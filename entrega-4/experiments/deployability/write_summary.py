#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> None:
    result = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
    lines = [
        '# Resultado del experimento de desplegabilidad',
        '',
        '| Medida | Objetivo | Resultado | Estado |',
        '|---|---:|---:|---|',
        f"| Eventos V1 procesados por consumidor V1 | {result['v1_published']} | {result['v1_processed_by_v1_consumer']} | {'PASS' if result['v1_processed_by_v1_consumer'] == result['v1_published'] else 'FAIL'} |",
        f"| Eventos V2 procesados por consumidor V1 | {result['v2_published']} | {result['v2_processed_by_v1_consumer']} | {'PASS' if result['v2_processed_by_v1_consumer'] == result['v2_published'] else 'FAIL'} |",
        f"| Errores de deserialización/procesamiento | 0 | {result['deserialization_or_processing_errors']} | {'PASS' if result['deserialization_or_processing_errors'] == 0 else 'FAIL'} |",
        f"| Cambios al consumidor V1 durante el despliegue | 0 | {result['consumer_code_changes']} | {'PASS' if result['consumer_code_changes'] == 0 else 'FAIL'} |",
        '',
        f"Resultado general: **{result['result']}**",
        '',
        'La revisión V2 conserva el nombre lógico del registro Avro, mantiene los campos de V1 y agrega `region` y `priority` con valores predeterminados. El mismo consumidor V1 procesa ambas revisiones.',
        '',
    ]
    Path(sys.argv[2]).write_text('\n'.join(lines), encoding='utf-8')


if __name__ == '__main__':
    main()
