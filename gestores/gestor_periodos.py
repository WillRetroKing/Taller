from __future__ import annotations

from datetime import date
from dataclasses import fields
from typing import Any

from dominio.modelo_datos import PeriodoAcademico


class ErrorPeriodo(ValueError):
    """Error de un periodo académico."""


class GestorPeriodosAcademicos:
    def __init__(self, periodos: list[PeriodoAcademico], ofertas: list[Any] | None = None) -> None:
        self.periodos = periodos
        self._ofertas = ofertas if ofertas is not None else []

    def crear_periodo(self, periodo: PeriodoAcademico) -> PeriodoAcademico:
        self._validar_fechas(periodo)
        periodo.idPeriodo = periodo.idPeriodo or self._siguiente_id()
        if any(item.idPeriodo == periodo.idPeriodo for item in self.periodos):
            raise ErrorPeriodo(f"Ya existe el periodo {periodo.idPeriodo}")
        if periodo.estado is None:
            periodo.estado = "ABIERTO"
        self.periodos.append(periodo)
        return periodo

    def cerrar_periodo(self, id_periodo: int) -> PeriodoAcademico:
        periodo = self._buscar(id_periodo)
        periodo.estado = "CERRADO"
        return periodo

    def consultar_periodo(self, id_periodo: int) -> PeriodoAcademico:
        return self._buscar(id_periodo)

    def listar_periodos(self, *, incluir_cerrados: bool = True) -> list[PeriodoAcademico]:
        if incluir_cerrados:
            return list(self.periodos)
        return [item for item in self.periodos if str(item.estado).upper() != "CERRADO"]

    def modificar_periodo(self, id_periodo: int, **cambios: Any) -> PeriodoAcademico:
        periodo = self._buscar(id_periodo)
        campos = set(getattr(periodo, "__dataclass_fields__", {}))
        desconocidos = set(cambios) - campos
        if desconocidos:
            raise ErrorPeriodo(f"Campos no válidos: {', '.join(sorted(desconocidos))}")
        anteriores = {campo: getattr(periodo, campo) for campo in cambios}
        for campo, valor in cambios.items():
            setattr(periodo, campo, valor)
        try:
            self._validar_fechas(periodo)
        except ErrorPeriodo:
            for campo, valor in anteriores.items():
                setattr(periodo, campo, valor)
            raise
        return periodo

    @staticmethod
    def _validar_fechas(periodo: PeriodoAcademico) -> None:
        if periodo.fechaInicio and periodo.fechaFin and periodo.fechaFin < periodo.fechaInicio:
            raise ErrorPeriodo("La fecha final no puede preceder a la fecha inicial")
        if periodo.fechaInicioMatricula and periodo.fechaFinMatricula and periodo.fechaFinMatricula < periodo.fechaInicioMatricula:
            raise ErrorPeriodo("La ventana de matrícula tiene fechas inválidas")
        if periodo.fechaLimiteCancelacion and periodo.fechaFin and periodo.fechaLimiteCancelacion > periodo.fechaFin:
            raise ErrorPeriodo("La fecha límite de cancelación no puede superar el fin del periodo")

    def _buscar(self, id_periodo: int) -> PeriodoAcademico:
        periodo = next((item for item in self.periodos if item.idPeriodo == id_periodo), None)
        if periodo is None:
            raise ErrorPeriodo(f"No existe el periodo con ID {id_periodo}")
        return periodo

    def consultar_periodos(self, *, estado: str | None = None) -> list[PeriodoAcademico]:
        """Consultar periodos con filtro opcional por estado."""
        if estado is None:
            return list(self.periodos)
        return [p for p in self.periodos if str(p.estado or "").upper() == estado.upper()]

    def consultar_ofertas_periodo(self, id_periodo: int) -> list[Any]:
        """Devuelve las ofertas completas de un período existente."""
        self._buscar(id_periodo)
        return list(self._ofertas_por_periodo(id_periodo))

    def modificar_oferta(self, id_oferta: int, id_periodo: int, **cambios: Any) -> Any:
        """Modifica una oferta del período sin permitir inconsistencias de cupo."""
        oferta = next((o for o in self._ofertas if o.idOfertaCurso == id_oferta), None)
        if oferta is None:
            raise ErrorPeriodo(f"No existe la oferta con ID {id_oferta}")
        if oferta.idPeriodo != id_periodo:
            raise ErrorPeriodo("La oferta no pertenece a ese periodo")
        permitidos = {campo.name for campo in fields(oferta)} - {"idOfertaCurso", "idPeriodo", "idCurso"}
        desconocidos = set(cambios) - permitidos
        if desconocidos:
            raise ErrorPeriodo(f"Campos de oferta no válidos: {', '.join(sorted(desconocidos))}")
        anteriores = {campo: getattr(oferta, campo) for campo in cambios}
        for campo, valor in cambios.items():
            setattr(oferta, campo, valor)
        try:
            if oferta.cupoMaximo is not None and oferta.cupoMaximo < 0:
                raise ErrorPeriodo("El cupo máximo no puede ser negativo")
            if oferta.cupoDisponible is not None and oferta.cupoDisponible < 0:
                raise ErrorPeriodo("El cupo disponible no puede ser negativo")
            if (oferta.cupoMaximo is not None and oferta.cupoDisponible is not None
                    and oferta.cupoDisponible > oferta.cupoMaximo):
                raise ErrorPeriodo("El cupo disponible no puede superar el cupo máximo")
        except ErrorPeriodo:
            for campo, valor in anteriores.items():
                setattr(oferta, campo, valor)
            raise
        return oferta

    def abrir_periodo(self, id_periodo: int) -> PeriodoAcademico:
        """Abrir un periodo académico para permitir operaciones."""
        periodo = self._buscar(id_periodo)
        if str(periodo.estado or "").upper() == "CERRADO":
            raise ErrorPeriodo("No se puede abrir un periodo cerrado")
        periodo.estado = "ABIERTO"
        return periodo

    def _ofertas_por_periodo(self, id_periodo: int) -> list:
        if self._ofertas is None:
            return []
        return [o for o in self._ofertas if o.idPeriodo == id_periodo]

    def _siguiente_id(self) -> int:
        return max((item.idPeriodo or 0 for item in self.periodos), default=0) + 1
