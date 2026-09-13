# Experimento: Modificabilidad / Configurabilidad

## Objetivo
Agregar un nuevo partner B2B2C (`partner-demo`) sin impactar Work Orchestration.

## Hipótesis
El nuevo partner puede incorporarse modificando como máximo Partner Integration y Partner Rules.

## Medidas
- <= 2 bounded contexts modificados
- 0 cambios en Work Orchestration
- `partner-demo` procesado correctamente

## Ejecución

```bash
python experiments/modifiability/run_experiment.py
```

## Resultados

`experiments/modifiability/results/`
