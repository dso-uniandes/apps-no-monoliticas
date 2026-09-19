"""Derivacion del estado de la SAGA a partir de los pasos del Saga Log.

Es logica de presentacion: la SAGA es coreografiada y ningun servicio publica
un estado global, asi que el BFF lo infiere de la traza para responder una sola
pregunta del cliente: "como va mi solicitud".
"""

PENDING = 'PENDING'
IN_PROGRESS = 'IN_PROGRESS'
COMPLETED = 'COMPLETED'
COMPENSATING = 'COMPENSATING'
COMPENSATED = 'COMPENSATED'
REJECTED = 'REJECTED'

_TERMINAL = (COMPLETED, COMPENSATED, REJECTED)


def derive_status(steps: list[dict]) -> str:
    if not steps:
        return PENDING

    nombres = {step.get('step') for step in steps}

    if 'WORK_CANCELLED' in nombres:
        return COMPENSATED
    if 'WORK_COMPENSATION' in nombres:
        # La compensacion no encontro el Work: la SAGA no sigue avanzando.
        return COMPENSATED
    if 'MATCHING_FAILED' in nombres:
        return COMPENSATING
    if 'MATCHING_COMPLETED' in nombres:
        return COMPLETED

    for step in steps:
        if step.get('step') == 'PARTNER_RULES_EVALUATED' and step.get('status') == 'REJECTED':
            return REJECTED

    return IN_PROGRESS


def is_terminal(saga_status: str) -> bool:
    return saga_status in _TERMINAL
