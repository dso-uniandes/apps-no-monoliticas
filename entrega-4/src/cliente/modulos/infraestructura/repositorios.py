from uuid import UUID

from cliente.modulos.dominio.entidades import Usuario
from cliente.modulos.dominio.repositorios import RepositorioUsuarios


class RepositorioUsuariosSQLAlchemy(RepositorioUsuarios):

    def obtener_por_id(self, id: UUID) -> Usuario:
        raise NotImplementedError

    def obtener_todos(self) -> list[Usuario]:
        raise NotImplementedError

    def agregar(self, entity: Usuario):
        raise NotImplementedError

    def actualizar(self, entity: Usuario):
        raise NotImplementedError

    def eliminar(self, entity_id: UUID):
        raise NotImplementedError
