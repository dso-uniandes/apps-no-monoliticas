# Resultado del experimento de desplegabilidad

| Medida | Objetivo | Resultado | Estado |
|---|---:|---:|---|
| Eventos V1 procesados por consumidor V1 | 100 | 100 | PASS |
| Eventos V2 procesados por consumidor V1 | 100 | 100 | PASS |
| Errores de deserialización/procesamiento | 0 | 0 | PASS |
| Cambios al consumidor V1 durante el despliegue | 0 | 0 | PASS |

Resultado general: **PASS**

La revisión V2 conserva el nombre lógico del registro Avro, mantiene los campos de V1 y agrega `region` y `priority` con valores predeterminados. El mismo consumidor V1 procesa ambas revisiones.
