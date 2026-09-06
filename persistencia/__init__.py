"""Capa de Persistencia y Acceso a Datos (Archivos Planos y CRUD)."""

from persistencia.gestor_persistencia import GestorPersistencia
from persistencia.gestor_crud import GestorCRUD, ErrorCRUD

__all__ = ["GestorPersistencia", "GestorCRUD", "ErrorCRUD"]
