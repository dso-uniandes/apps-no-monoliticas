# Resultados cualitativos de la experimentación

Acá interpretamos los resultados finales de los tres escenarios de calidad
que corrimos en la POC: modificabilidad / configurabilidad, escalabilidad y
desplegabilidad / evolución compatible del contrato.

Los números crudos y la evidencia de cada corrida siguen en
`experiments/*/results`. Este documento no los vuelve a copiar uno a uno:
lo que hace es decir qué leímos en esos resultados, qué hipótesis se sostuvo
y hasta dónde llega la conclusión.

---

## 1. Modificabilidad / configurabilidad

### Resultado observado

- Se agregó `partner-demo`.
- Se modificaron exactamente 2 bounded contexts:
  - `partner_integration`
  - `partner_rules`
- Work Orchestration tuvo 0 archivos modificados.
- El nuevo partner pudo normalizarse y sus reglas pudieron procesarse.
- Resultado del experimento: **PASS**.

Evidencia:

- [`experiments/modifiability/results/results.json`](../experiments/modifiability/results/results.json)
- [`experiments/modifiability/results/changed-files.txt`](../experiments/modifiability/results/changed-files.txt)
- [`experiments/modifiability/results/summary.md`](../experiments/modifiability/results/summary.md)

### Análisis cualitativo

En este experimento la hipótesis sí se sostuvo. Para agregar `partner-demo` tuvimos que tocar Partner Integration y Partner Rules, que eran precisamente los dos bounded contexts donde esperábamos absorber el cambio, mientras que Work Orchestration quedó intacto.

Para nosotros ese es el punto importante del resultado: el cambio no se regó por el resto del flujo. La lógica específica del partner quedó contenida donde correspondía y no fue necesario modificar el bounded context que maneja el `Work`.

Tampoco queremos llevar la conclusión más allá de lo que realmente probamos. Esto no significa que cualquier cambio futuro de un partner vaya a afectar siempre máximo dos contextos. Lo que sí podemos decir es que, para el escenario que definimos y ejecutamos, la separación propuesta funcionó como esperábamos.

### Estado de la hipótesis

**Sostenida para el escenario probado.**

---

## 2. Escalabilidad

### Resultado observado

- 10.000 mensajes.
- Ventana de 60 segundos.
- Umbral requerido: 95 %.
- Con 1 consumidor: 10.000 / 10.000 procesados = 100 %.
- Con 4 consumidores: 10.000 / 10.000 procesados = 100 %.
- Resultado: **PASS** en ambas configuraciones.

Evidencia:

- [`experiments/scalability/results/consumers-1.json`](../experiments/scalability/results/consumers-1.json)
- [`experiments/scalability/results/consumers-4.json`](../experiments/scalability/results/consumers-4.json)
- [`experiments/scalability/results/summary.md`](../experiments/scalability/results/summary.md)

### Análisis cualitativo

El escenario también cumplió lo que habíamos definido: tanto con un consumidor como con cuatro consumidores se procesaron los 10.000 mensajes dentro de la ventana de 60 segundos, superando el umbral mínimo del 95 %.

Hay una precisión importante acá. Con estos resultados no podemos afirmar que cuatro consumidores hayan sido más rápidos que uno, porque el experimento actual mide cuántos mensajes alcanzaron a procesarse dentro de una ventana fija y ambas configuraciones llegaron al 100 %. No tenemos una medición suficientemente detallada de tiempo total o throughput que permita comparar la ganancia de rendimiento entre 1 y 4 consumidores.

Lo que sí comprobamos es que Provider Matching soportó por completo la carga definida y que puede ejecutarse con varios consumidores usando la suscripción `Shared` de Pulsar sin impedir el procesamiento completo de los mensajes. Para la hipótesis y el umbral que definimos inicialmente, el escenario quedó satisfecho.

### Estado de la hipótesis

**Sostenida para la carga y ventana definidas.**

---

## 3. Desplegabilidad / evolución compatible del contrato

### Resultado observado

- 100 eventos V1 publicados.
- 100 eventos V1 procesados por el consumidor V1.
- 100 eventos V2 publicados.
- 100 eventos V2 procesados por el mismo consumidor V1.
- Backlog final: 0.
- Errores de deserialización/procesamiento: 0.
- Checksum del consumidor antes y después: idéntico.
- Cambios al consumidor: 0.
- Resultado: **PASS**.

La V2 agregó `region` y `priority` con valores por defecto en Avro.

Evidencia:

- [`experiments/deployability/results/results.json`](../experiments/deployability/results/results.json)
- [`experiments/deployability/results/summary.md`](../experiments/deployability/results/summary.md)

### Análisis cualitativo

La hipótesis también se sostuvo para el cambio de contrato que probamos. El consumidor V1 pudo procesar tanto los eventos V1 como los V2 sin errores, terminó sin backlog y su código no tuvo que modificarse durante la prueba.

En este caso lo que nos interesaba era comprobar que el productor pudiera evolucionar `WorkCreated` agregando `region` y `priority`, ambos con valores por defecto, sin obligarnos a cambiar y desplegar al mismo tiempo el consumidor existente. Para ese cambio concreto, la compatibilidad del esquema funcionó.

Igual que en los otros experimentos, la conclusión tiene un alcance específico. No sería correcto decir que cualquier modificación futura del contrato va a ser compatible automáticamente. Lo que validamos fue esta evolución particular del esquema y las condiciones definidas en el experimento.

### Estado de la hipótesis

**Sostenida para la evolución de esquema probada.**

---

## Conclusión general

Viendo los tres experimentos en conjunto, los escenarios de calidad que definimos para la POC quedaron satisfechos, pero cada resultado tiene que leerse dentro del alcance que realmente probamos.

En modificabilidad logramos incorporar un nuevo partner sin llevar el cambio hasta Work Orchestration. En escalabilidad procesamos completamente la carga definida tanto con uno como con cuatro consumidores. Y en desplegabilidad pudimos evolucionar el evento `WorkCreated` manteniendo operativo al consumidor V1 sin modificar su código.

Más que tomar estos resultados como una garantía general sobre todo el sistema, los usamos para validar decisiones concretas de la arquitectura: separar la lógica de integración del partner, permitir el consumo compartido en Provider Matching y mantener contratos de eventos versionados y compatibles. Para los escenarios que planteamos en esta POC, esas decisiones respondieron como esperábamos.
