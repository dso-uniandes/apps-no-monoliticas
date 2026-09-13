# Resultado del experimento de escalabilidad

| Consumidores | Mensajes | Procesados en 60 s | Porcentaje | Resultado |
|---:|---:|---:|---:|---|
| 1 | 10.000 | 10.000 | 100 % | PASS |
| 4 | 10.000 | 10.000 | 100 % | PASS |

El escenario exige procesar al menos el 95 % de 10.000 trabajos acumulados en
60 segundos. Las dos configuraciones cumplieron el umbral. La prueba demuestra
que Provider Matching soporta la carga definida y que puede ejecutarse con
varios consumidores mediante la suscripción `Shared` de Pulsar.
