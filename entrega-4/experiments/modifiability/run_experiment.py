#!/usr/bin/env python
"""Driver del experimento de modificabilidad: nuevo partner-demo."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT_DIR = Path(__file__).resolve().parent
RESULTS_DIR = EXPERIMENT_DIR / 'results'
BASELINE_FILE = EXPERIMENT_DIR / 'baseline_commit.txt'

BOUNDED_CONTEXTS = (
    'partner_integration',
    'partner_rules',
    'work_orchestration',
    'provider_matching',
)

PARTNER_ID = 'partner-demo'
EXTERNAL_PAYLOAD = {
    'reference': 'EXT-DEMO-001',
    'municipality': 'Bogota',
    'country_code': 'CO',
    'service_type': 'HOME_REPAIR',
}


def _ensure_pythonpath() -> None:
    src = str(ROOT / 'src')
    if src not in sys.path:
        sys.path.insert(0, src)


def _run_git(*args: str) -> str:
    completed = subprocess.run(
        ['git', *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _load_baseline_commit() -> str:
    return BASELINE_FILE.read_text(encoding='utf-8').strip()


def _changed_files(baseline: str) -> list[str]:
    tracked = _run_git('diff', '--name-only', baseline)
    untracked = _run_git('ls-files', '--others', '--exclude-standard')
    files: list[str] = []
    for block in (tracked, untracked):
        if block:
            files.extend(line.replace('\\', '/') for line in block.splitlines() if line.strip())
    # Deduplicate preserving order
    seen: set[str] = set()
    ordered: list[str] = []
    for path in files:
        if path not in seen:
            seen.add(path)
            ordered.append(path)
    return ordered


def _normalize_path(path: str) -> str:
    normalized = path.replace('\\', '/')
    if normalized.startswith('entrega-4/'):
        normalized = normalized[len('entrega-4/') :]
    return normalized


def _affected_bounded_contexts(changed_files: list[str]) -> list[str]:
    affected: list[str] = []
    for bc in BOUNDED_CONTEXTS:
        marker = f'src/{bc}/'
        if any(marker in _normalize_path(path) for path in changed_files):
            affected.append(bc)
    return affected


def _run_functional_checks() -> dict:
    _ensure_pythonpath()

    from partner_integration.aplicacion.comandos.normalize_partner_request import (
        NormalizePartnerRequest,
    )
    from partner_integration.config.container import get_normalize_partner_request_handler
    from partner_rules.aplicacion.comandos.evaluate_partner_rules import EvaluatePartnerRules
    from partner_rules.config.container import get_evaluate_partner_rules_handler

    normalize_handler = get_normalize_partner_request_handler()
    partner_request = normalize_handler.handle(
        NormalizePartnerRequest(
            partner_id=PARTNER_ID,
            payload=EXTERNAL_PAYLOAD,
        )
    )

    data = (partner_request.normalized_payload or {}).get('data', {})
    normalization_successful = (
        partner_request.external_reference is not None
        and partner_request.external_reference.valor == 'EXT-DEMO-001'
        and data.get('city') == 'Bogota'
        and data.get('country') == 'CO'
        and data.get('service_type') == 'HOME_REPAIR'
    )

    rules_handler = get_evaluate_partner_rules_handler()
    evaluation = rules_handler.handle(
        EvaluatePartnerRules(
            partner_id=PARTNER_ID,
            service_type='HOME_REPAIR',
        )
    )
    rules_successful = bool(evaluation.allowed) and len(evaluation.applicable_rule_ids) >= 1
    new_partner_supported = normalization_successful and rules_successful

    return {
        'normalization_successful': normalization_successful,
        'rules_successful': rules_successful,
        'new_partner_supported': new_partner_supported,
        'normalized_external_reference': (
            partner_request.external_reference.valor
            if partner_request.external_reference
            else None
        ),
        'normalized_city': data.get('city'),
        'normalized_country': data.get('country'),
        'rules_summary': evaluation.summary,
    }


def _write_summary(
    *,
    affected_count: int,
    work_changes: int,
    supported: bool,
    result: str,
) -> str:
    bc_status = 'PASS' if affected_count <= 2 else 'FAIL'
    work_status = 'PASS' if work_changes == 0 else 'FAIL'
    partner_status = 'PASS' if supported else 'FAIL'
    supported_label = 'Sí' if supported else 'No'

    lines = [
        '| Medida | Objetivo | Resultado | Estado |',
        '|---|---:|---:|---|',
        f'| Bounded Contexts modificados | <= 2 | {affected_count} | {bc_status} |',
        f'| Cambios en Work Orchestration | 0 | {work_changes} | {work_status} |',
        f'| Nuevo partner soportado | Sí | {supported_label} | {partner_status} |',
        '',
        f'Resultado general: {result}',
        '',
    ]
    if result == 'PASS':
        lines.append(
            'Conclusión: el escenario de modificabilidad fue validado; '
            'partner-demo se incorporó sin tocar Work Orchestration.'
        )
    else:
        lines.append(
            'Conclusión: el escenario de modificabilidad NO fue validado '
            'según los umbrales definidos.'
        )
    return '\n'.join(lines) + '\n'


def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    baseline = _load_baseline_commit()
    functional = _run_functional_checks()

    changed_files = _changed_files(baseline)
    (RESULTS_DIR / 'changed-files.txt').write_text(
        '\n'.join(changed_files) + ('\n' if changed_files else ''),
        encoding='utf-8',
    )

    affected = _affected_bounded_contexts(changed_files)
    work_changes = sum(
        1
        for path in changed_files
        if 'src/work_orchestration/' in _normalize_path(path)
    )

    result = (
        'PASS'
        if (
            len(affected) <= 2
            and work_changes == 0
            and functional['new_partner_supported']
        )
        else 'FAIL'
    )

    payload = {
        'experiment': 'modifiability_new_partner',
        'partner': PARTNER_ID,
        'baseline_commit': baseline,
        'affected_bounded_contexts': len(affected),
        'affected_bounded_context_names': affected,
        'max_allowed_bounded_contexts': 2,
        'work_orchestration_files_changed': work_changes,
        'max_allowed_work_changes': 0,
        'new_partner_supported': functional['new_partner_supported'],
        'normalization_successful': functional['normalization_successful'],
        'rules_successful': functional['rules_successful'],
        'result': result,
    }

    (RESULTS_DIR / 'results.json').write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + '\n',
        encoding='utf-8',
    )
    (RESULTS_DIR / 'summary.md').write_text(
        _write_summary(
            affected_count=len(affected),
            work_changes=work_changes,
            supported=functional['new_partner_supported'],
            result=result,
        ),
        encoding='utf-8',
    )

    print(json.dumps(payload, indent=2, ensure_ascii=False))
    print(f'\nResultado general: {result}')
    return 0 if result == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
