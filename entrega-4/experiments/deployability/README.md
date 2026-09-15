# Experimento de desplegabilidad y evolución de esquema

## Escenario

Al desplegar un productor que publica la revisión V2 de `WorkCreated`, el
consumidor V1 existente de Provider Matching debe continuar operando sin
cambios y sin errores de deserialización.

V2 conserva el nombre lógico y todos los campos Avro de V1. Solo agrega
`region` y `priority`, ambos con valores predeterminados. Un lector V1 ignora
estos campos nuevos y un lector V2 puede leer mensajes históricos V1 usando
los valores predeterminados.

El entorno configura la estrategia `FULL` de Pulsar. Por ello, el broker debe
aceptar el nuevo esquema como compatible hacia adelante y hacia atrás antes de
permitir que el productor V2 publique.

## Criterios de aceptación

- 100 eventos V1 procesados por el consumidor V1.
- 100 eventos V2 procesados por el mismo consumidor V1.
- Backlog final igual a cero.
- Cero errores de deserialización o procesamiento.
- El checksum del código del consumidor no cambia durante la prueba.

## Ejecución

Inicie Docker Desktop y ejecute desde `entrega-4`:

```bash
bash experiments/deployability/run_experiment.sh
```

Puede cambiar la cantidad de eventos por versión pasando un número:

```bash
bash experiments/deployability/run_experiment.sh 200
```

El experimento usa un proyecto Docker aislado, un tópico exclusivo y los
contratos/consumidor reales. Los resultados quedan en
`experiments/deployability/results/`. Al finalizar elimina únicamente los
contenedores y volúmenes temporales del proyecto `hda-deployability`.
