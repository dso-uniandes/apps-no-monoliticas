# Referencia: patrón Saga (Tutorial 8 - MISW4406)

Esta carpeta **no forma parte de la ejecución** de la aplicación. Es únicamente material de estudio preservado antes de eliminar `src/aeroalpes/`.

## Origen de los archivos

| Archivo en esta carpeta | Origen original |
|---|---|
| `seedwork/aplicacion/sagas.py` | `src/aeroalpes/seedwork/aplicacion/sagas.py` |
| `modulos/sagas/aplicacion/coordinadores/saga_reservas.py` | `src/aeroalpes/modulos/sagas/aplicacion/coordinadores/saga_reservas.py` |
| `modulos/sagas/aplicacion/comandos/*.py` | `src/aeroalpes/modulos/sagas/aplicacion/comandos/` |
| `modulos/sagas/dominio/eventos/*.py` | `src/aeroalpes/modulos/sagas/dominio/eventos/` |
| `modulos/sagas/dominio/repositorios.py` | `src/aeroalpes/modulos/sagas/dominio/repositorios.py` |
| `modulos/sagas/infraestructura/dto.py` | `src/aeroalpes/modulos/sagas/infraestructura/dto.py` |
| `modulos/sagas/infraestructura/repositorios.py` | `src/aeroalpes/modulos/sagas/infraestructura/repositorios.py` |

## Qué estudiar aquí

- **`sagas.py`**: interfaces genéricas (`CoordinadorSaga`, `CoordinadorOrquestacion`, `Paso`, `Transaccion`, `Inicio`, `Fin`) y lógica de avance/compensación.
- **`saga_reservas.py`**: ejemplo concreto de orquestación (pasos, comandos, eventos de error y compensaciones).
- **Comandos / eventos**: stubs y eventos usados por la saga del tutorial.
- **Repositorios / DTO de saga log**: persistencia del log de transacciones largas.

## Dependencias no copiadas a propósito

`saga_reservas.py` importaba también comandos/eventos del módulo de vuelos (`src/aeroalpes/modulos/vuelos/...`), que no se preservaron aquí para no arrastrar todo AeroAlpes. Esos imports quedarán rotos: úsalos solo como referencia de lectura.
