from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any, Iterable

from modelo_datos import Administrativo, Contrato, Dedicacion, Profesor, TipoProfesor


class ErrorContrato(ValueError):
    """Incumplimiento de una regla de vinculación contractual."""


class GestorContratos:
    HORAS_MAXIMAS_CATEDRATICO = Decimal("18")
    HORAS_MAXIMAS_ADMINISTRATIVO_AD_HONOREM = Decimal("8")

    def __init__(
        self,
        contratos: list[Contrato],
        profesores: list[Profesor] | None = None,
        administrativos: list[Administrativo] | None = None,
        liquidaciones: Iterable[Any] | None = None,
    ) -> None:
        self.contratos = contratos
        self.profesores = profesores or []
        self.administrativos = administrativos or []
        self.liquidaciones = list(liquidaciones or [])

    def crear_contrato(
        self,
        contrato: Contrato,
        *,
        jubilado: bool | None = None,
    ) -> Contrato:
        """Valida y agrega un contrato; si falla, las listas permanecen sin cambios."""
        if contrato.idContrato is None:
            contrato.idContrato = self._siguiente_id()
        if any(item.idContrato == contrato.idContrato for item in self.contratos):
            raise ErrorContrato(f"Ya existe un contrato con ID {contrato.idContrato}")

        self.validar_contrato(contrato, jubilado=jubilado)
        self.contratos.append(contrato)
        return contrato

    def buscar_contrato_vigente(self, id_persona: int, fecha: date | None = None) -> Contrato | None:
        momento = fecha or date.today()
        return next(
            (
                contrato for contrato in self.contratos
                if contrato.idPersona == id_persona and self._es_activo(contrato.estado)
                and (contrato.fechaInicio is None or contrato.fechaInicio <= momento)
                and (contrato.fechaFin is None or momento <= contrato.fechaFin)
            ),
            None,
        )

    def listar_contratos_profesor(self, id_persona: int) -> list[Contrato]:
        return [contrato for contrato in self.contratos if contrato.idPersona == id_persona]

    def modificar_contrato(self, id_contrato: int, **cambios: Any) -> Contrato:
        contrato = self._buscar(id_contrato)
        if any(getattr(liquidacion, "idContrato", None) == id_contrato for liquidacion in self.liquidaciones):
            raise ErrorContrato("No se puede modificar un contrato con liquidaciones históricas")
        campos = set(getattr(contrato, "__dataclass_fields__", {}))
        desconocidos = set(cambios) - campos
        if desconocidos:
            raise ErrorContrato(f"Campos no válidos: {', '.join(sorted(desconocidos))}")
        copia = Contrato(**{campo: cambios.get(campo, getattr(contrato, campo)) for campo in campos})
        self.validar_contrato(copia)
        for campo, valor in cambios.items():
            setattr(contrato, campo, valor)
        return contrato

    def terminar_contrato(self, id_contrato: int, causal: str, documento: str, fecha: date | None = None) -> Contrato:
        contrato = self._buscar(id_contrato)
        if not causal.strip() or not documento.strip():
            raise ErrorContrato("La causal y el documento de terminación son obligatorios")
        contrato.causalTerminacion = causal.strip()
        contrato.documentoSoporteTerminacion = documento.strip()
        contrato.fechaTerminacionEfectiva = fecha or date.today()
        contrato.estadoFinalContrato = "TERMINADO"
        contrato.estado = "INACTIVO"
        return contrato

    def desactivar_contrato(self, id_contrato: int) -> Contrato:
        contrato = self._buscar(id_contrato)
        contrato.estado = "INACTIVO"
        return contrato

    def validar_contrato(
        self,
        contrato: Contrato,
        *,
        jubilado: bool | None = None,
    ) -> None:
        tipo = self._tipo(contrato)
        dedicacion = self._dedicacion(contrato)
        horas = self._horas_semanales(contrato)

        if horas < 0:
            raise ErrorContrato("Las horas semanales no pueden ser negativas")
        if contrato.fechaInicio and contrato.fechaFin and contrato.fechaFin < contrato.fechaInicio:
            raise ErrorContrato("La fecha de terminación no puede preceder a la fecha de inicio")

        if tipo in {"CATEDRATICO", "CATEDRATICO_AD_HONOREM"}:
            total_horas = self._horas_activas(contrato.idPersona, "CATEDRATICO") + horas
            if total_horas > self.HORAS_MAXIMAS_CATEDRATICO:
                raise ErrorContrato(
                    f"Los catedráticos no pueden superar {self.HORAS_MAXIMAS_CATEDRATICO} horas semanales"
                )

        if self._es_catedratico_ad_honorem(contrato) and self._es_administrativo(contrato.idPersona):
            total_horas = self._horas_activas(contrato.idPersona, "CATEDRATICO_AD_HONOREM") + horas
            if total_horas > self.HORAS_MAXIMAS_ADMINISTRATIVO_AD_HONOREM:
                raise ErrorContrato(
                    "Los administrativos catedráticos ad-honorem no pueden superar 8 horas semanales"
                )

        if tipo == "OCASIONAL":
            if dedicacion not in {Dedicacion.TIEMPO_COMPLETO.value, Dedicacion.MEDIO_TIEMPO.value}:
                raise ErrorContrato("Los profesores ocasionales solo pueden ser de tiempo completo o medio tiempo")
            if self._duracion_en_meses(contrato) >= 12:
                raise ErrorContrato("La vinculación ocasional debe durar menos de un año")

        if tipo in {"OCASIONAL", "PLANTA"} and self._es_jubilado(contrato.idPersona, jubilado):
            raise ErrorContrato("No se pueden vincular docentes jubilados en modalidad ocasional o planta")

    def _horas_activas(self, id_persona: int | None, tipo: str) -> Decimal:
        return sum(
            (self._horas_semanales(item) for item in self.contratos
             if item.idPersona == id_persona and self._es_activo(item.estado)
             and self._tipo(item) in ({"CATEDRATICO", "CATEDRATICO_AD_HONOREM"} if tipo == "CATEDRATICO" else {tipo})),
            Decimal("0"),
        )

    def _duracion_en_meses(self, contrato: Contrato) -> int:
        if contrato.duracionEnMeses is not None:
            return contrato.duracionEnMeses
        if contrato.fechaInicio is None or contrato.fechaFin is None:
            raise ErrorContrato("La vinculación ocasional requiere duración o fechas de inicio y fin")
        return (contrato.fechaFin.year - contrato.fechaInicio.year) * 12 + contrato.fechaFin.month - contrato.fechaInicio.month + (
            1 if contrato.fechaFin.day >= contrato.fechaInicio.day else 0
        )

    def _es_jubilado(self, id_persona: int | None, jubilado: bool | None) -> bool:
        if jubilado is not None:
            return jubilado
        profesor = next((item for item in self.profesores if item.idPersona == id_persona), None)
        if profesor is None:
            return False
        for nombre in ("esJubilado", "jubilado", "esPensionado"):
            valor = getattr(profesor, nombre, None)
            if valor is not None:
                return bool(valor)
        estado = str(getattr(profesor, "estado", "")).upper()
        return estado in {"JUBILADO", "PENSIONADO"}

    def _es_administrativo(self, id_persona: int | None) -> bool:
        return any(item.idPersona == id_persona for item in self.administrativos)

    @staticmethod
    def _es_catedratico_ad_honorem(contrato: Contrato) -> bool:
        tipo = GestorContratos._tipo(contrato)
        modalidad = str(contrato.modalidadProfesor or "").upper()
        return tipo == "CATEDRATICO_AD_HONOREM" or (
            tipo == "CATEDRATICO" and (contrato.esAdHonorem is True or modalidad == "CATEDRATICO_AD_HONOREM")
        )

    @staticmethod
    def _tipo(contrato: Contrato) -> str:
        valor = contrato.modalidadProfesor or contrato.tipoContrato or ""
        valor = getattr(valor, "value", valor)
        return str(valor).upper().replace("Á", "A").replace("É", "E").replace("Í", "I").replace("Ó", "O").replace("Ú", "U")

    @staticmethod
    def _dedicacion(contrato: Contrato) -> str:
        valor = contrato.dedicacion or contrato.tipoDedicacion or ""
        valor = getattr(valor, "value", valor)
        return str(valor).upper()

    @staticmethod
    def _horas_semanales(contrato: Contrato) -> Decimal:
        valor = contrato.horasSemanales
        if valor is None:
            valor = contrato.horasSemanalesAsignadas
        return Decimal(valor or 0)

    @staticmethod
    def _es_activo(estado: Any) -> bool:
        valor = getattr(estado, "value", estado)
        return str(valor).upper() == "ACTIVO"

    def _siguiente_id(self) -> int:
        return max((item.idContrato or 0 for item in self.contratos), default=0) + 1

    def _buscar(self, identificador: int) -> Contrato:
        contrato = next((item for item in self.contratos if item.idContrato == identificador), None)
        if contrato is None:
            raise ErrorContrato(f"No existe el contrato con ID {identificador}")
        return contrato
