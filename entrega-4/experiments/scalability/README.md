# Experimento de escalabilidad de Provider Matching

## Escenario

Con 10.000 trabajos acumulados en Pulsar, Provider Matching debe procesar al
menos el 95 % en 60 segundos. La prueba se ejecuta con una y cuatro instancias
del consumidor para comparar el escalado independiente.

## Preparación

Inicie Docker Desktop. El productor se ejecuta dentro de la imagen de Provider
Matching, por lo que no necesita instalar el cliente de Pulsar en el equipo.

## Ejecución

Desde `entrega-4`:

```bash
bash experiments/scalability/run_experiment.sh 1
bash experiments/scalability/run_experiment.sh 4
```

Cada ejecución crea un tópico y una suscripción exclusivos, publica 10.000
eventos antes de iniciar los consumidores y guarda el resultado en
`experiments/scalability/results/`.

El resultado es `PASS` cuando se procesan al menos 9.500 mensajes durante los
60 segundos. El tiempo necesario para iniciar los contenedores forma parte de
la medición.
