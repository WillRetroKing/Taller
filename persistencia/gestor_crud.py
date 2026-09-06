from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any, Generic, TypeVar


Entidad = TypeVar("Entidad")


class ErrorCRUD(ValueError):
    """Error de una operación CRUD."""


class GestorCRUD(Generic[Entidad]):
    def __init__(
        self,
        registros: list[Entidad],
        *,
        campo_id: str,
        campo_codigo: str | None = None,
        campo_estado: str = "estado",
        validador: Callable[[Entidad], None] | None = None,
        tiene_historial: Callable[[Entidad], bool] | None = None,
    ) -> None:
        self.registros = registros
        self.campo_id = campo_id
        self.campo_codigo = campo_codigo
        self.campo_estado = campo_estado
        self.validador = validador
        self.tiene_historial = tiene_historial or (lambda _: False)

    def crear(self, registro: Entidad) -> Entidad:
        self.validar(registro)
        identificador = getattr(registro, self.campo_id, None)
        if identificador is None:
            setattr(registro, self.campo_id, self._siguiente_id())
        elif self.buscar_por_id(identificador) is not None:
            raise ErrorCRUD(f"Ya existe un registro con ID {identificador}")
        if self.campo_codigo is not None:
            codigo = getattr(registro, self.campo_codigo, None)
            if codigo is not None and self.buscar_por_codigo(codigo) is not None:
                raise ErrorCRUD(f"Ya existe el código {codigo}")
        self.registros.append(registro)
        return registro

    def agregar(self, registro: Entidad) -> Entidad:
        return self.crear(registro)

    def buscar_por_id(self, identificador: Any) -> Entidad | None:
        return next(
            (registro for registro in self.registros if getattr(registro, self.campo_id, None) == identificador),
            None,
        )

    def buscar_por_codigo(self, codigo: Any) -> Entidad | None:
        if self.campo_codigo is None:
            raise ErrorCRUD("Esta entidad no tiene campo de código configurado")
        return next(
            (registro for registro in self.registros if getattr(registro, self.campo_codigo, None) == codigo),
            None,
        )

    def listar(self, *, incluir_inactivos: bool = True) -> list[Entidad]:
        if incluir_inactivos:
            return list(self.registros)
        return [registro for registro in self.registros if self._estado(registro) != "INACTIVO"]

    def modificar(self, identificador: Any, **cambios: Any) -> Entidad:
        registro = self._requerir(identificador)
        if self.tiene_historial(registro):
            raise ErrorCRUD("No se puede modificar directamente un registro histórico")
        campos = set(getattr(registro, "__dataclass_fields__", {}))
        desconocidos = set(cambios) - campos
        if desconocidos:
            raise ErrorCRUD(f"Campos no válidos: {', '.join(sorted(desconocidos))}")
        copia = self._copia_con_cambios(registro, cambios)
        self.validar(copia)
        if self.campo_codigo and self.campo_codigo in cambios:
            existente = self.buscar_por_codigo(cambios[self.campo_codigo])
            if existente is not None and existente is not registro:
                raise ErrorCRUD(f"Ya existe el código {cambios[self.campo_codigo]}")
        for campo, valor in cambios.items():
            setattr(registro, campo, valor)
        return registro

    def desactivar(self, identificador: Any) -> Entidad:
        registro = self._requerir(identificador)
        setattr(registro, self.campo_estado, "INACTIVO")
        return registro

    def reactivar(self, identificador: Any) -> Entidad:
        registro = self._requerir(identificador)
        setattr(registro, self.campo_estado, "ACTIVO")
        self.validar(registro)
        return registro

    def eliminar(self, identificador: Any) -> Entidad:
        registro = self._requerir(identificador)
        if self.tiene_historial(registro):
            setattr(registro, self.campo_estado, "INACTIVO")
            return registro
        self.registros.remove(registro)
        return registro

    def validar(self, registro: Entidad) -> None:
        if getattr(registro, self.campo_id, None) is not None and getattr(registro, self.campo_id) < 0:
            raise ErrorCRUD("El ID no puede ser negativo")
        if self.campo_codigo is not None:
            codigo = getattr(registro, self.campo_codigo, None)
            if codigo is not None and not str(codigo).strip():
                raise ErrorCRUD("El código no puede estar vacío")
        if self.validador is not None:
            self.validador(registro)

    def _requerir(self, identificador: Any) -> Entidad:
        registro = self.buscar_por_id(identificador)
        if registro is None:
            raise ErrorCRUD(f"No existe un registro con ID {identificador}")
        return registro

    def _siguiente_id(self) -> int:
        return max((getattr(registro, self.campo_id) or 0 for registro in self.registros), default=0) + 1

    def _estado(self, registro: Entidad) -> str:
        return str(getattr(getattr(registro, self.campo_estado, ""), "value", getattr(registro, self.campo_estado, ""))).upper()

    @staticmethod
    def _copia_con_cambios(registro: Entidad, cambios: dict[str, Any]) -> Entidad:
        import copy
        copia = copy.copy(registro)
        for campo, valor in cambios.items():
            setattr(copia, campo, valor)
        return copia
