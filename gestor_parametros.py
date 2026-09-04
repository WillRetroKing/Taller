from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Iterable

from modelo_datos import LiquidacionNomina, ParametroNormativo


class ErrorParametro(ValueError):
    """Error de validación o vigencia de un parámetro normativo."""


class GestorParametros:
    PARAMETROS_PORCENTUALES = {
        "PORCENTAJE_ARL_CLASE_I",
        "PORCENTAJE_ARL_CLASE_II",
        "PORCENTAJE_SENA",
        "PORCENTAJE_ICBF",
        "PORCENTAJE_SALUD_TRABAJADOR",
        "PORCENTAJE_SALUD_EMPLEADOR",
        "PORCENTAJE_PENSION_TRABAJADOR",
        "PORCENTAJE_PENSION_EMPLEADOR",
        "PORCENTAJE_FONDO_SOLIDARIDAD",
        "PORCENTAJE_RIESGOS_LABORALES",
        "PORCENTAJE_CAJA_COMPENSACION",
        "PORCENTAJE_BONIFICACION_SERVICIOS_HASTA_TOPE",
        "PORCENTAJE_BONIFICACION_SERVICIOS_SOBRE_TOPE",
        "PORCENTAJE_RETENCION_FUENTE",
    }
    PARAMETROS_MONETARIOS = {
        "SALARIO_MINIMO",
        "VALOR_PUNTO_SALARIAL",
        "VALOR_AUXILIO_TRANSPORTE_VIGENTE",
        "VALOR_HORA_CATEDRA",
        "TOPE_BONIFICACION_SERVICIOS",
        "BASE_MINIMA_RETENCION_FUENTE",
    }

    def __init__(
        self,
        parametros: list[ParametroNormativo],
        liquidaciones: Iterable[LiquidacionNomina] | None = None,
    ) -> None:
        self.parametros = parametros
        self.liquidaciones = list(liquidaciones or [])

    def crear_parametro(self, parametro: ParametroNormativo) -> ParametroNormativo:
        self._validar(parametro)
        if parametro.idParametro is None:
            parametro.idParametro = self._siguiente_id()
        if any(item.idParametro == parametro.idParametro for item in self.parametros):
            raise ErrorParametro(f"Ya existe un parámetro con ID {parametro.idParametro}")
        self._validar_no_solapamiento(parametro)
        parametro.estado = "ACTIVO"
        self.parametros.append(parametro)
        return parametro

    def buscar_parametro_vigente(self, codigo: str, fecha: date | None = None) -> ParametroNormativo | None:
        fecha_consulta = fecha or date.today()
        codigo = self._codigo(codigo)
        candidatos = [
            parametro for parametro in self.parametros
            if self._codigo(parametro.codigo) == codigo
            and self._activo(parametro.estado)
            and self._vigente_en(parametro, fecha_consulta)
        ]
        return max(candidatos, key=lambda parametro: parametro.fechaInicioVigencia or date.min, default=None)

    def modificar_parametro(self, id_parametro: int, **cambios) -> ParametroNormativo:
        actual = self._buscar(id_parametro)
        if self._esta_usado_en_liquidacion(actual):
            raise ErrorParametro("No se puede modificar un parámetro utilizado en una liquidación")
        actualizado = ParametroNormativo(**{campo: cambios.get(campo, getattr(actual, campo)) for campo in actual.__dataclass_fields__})
        actualizado.idParametro = actual.idParametro
        self._validar(actualizado)
        self._validar_no_solapamiento(actualizado, excluir=actual)
        for campo in actual.__dataclass_fields__:
            setattr(actual, campo, getattr(actualizado, campo))
        return actual

    def desactivar_parametro(self, id_parametro: int) -> ParametroNormativo:
        parametro = self._buscar(id_parametro)
        if self._esta_usado_en_liquidacion(parametro):
            raise ErrorParametro("No se puede desactivar un parámetro utilizado en una liquidación")
        parametro.estado = "INACTIVO"
        return parametro

    def listar_parametros_por_tipo(self, tipo_dato: str) -> list[ParametroNormativo]:
        return [item for item in self.parametros if item.tipoDato == tipo_dato]

    def _validar(self, parametro: ParametroNormativo) -> None:
        if not parametro.codigo:
            raise ErrorParametro("El código del parámetro es obligatorio")
        inicio = parametro.fechaInicioVigencia
        fin = parametro.fechaFinVigencia
        if inicio is None:
            raise ErrorParametro("La fecha de inicio de vigencia es obligatoria")
        if fin is not None and fin <= inicio:
            raise ErrorParametro("La fecha de fin debe ser posterior a la fecha de inicio")
        if parametro.valor is None or parametro.valor == "":
            raise ErrorParametro("El valor del parámetro es obligatorio")
        codigo = self._codigo(parametro.codigo)
        try:
            valor = Decimal(parametro.valor)
        except (InvalidOperation, ValueError):
            raise ErrorParametro("El valor del parámetro debe ser numérico") from None
        if codigo in self.PARAMETROS_PORCENTUALES and not Decimal("0") <= valor <= Decimal("1"):
            raise ErrorParametro("Los porcentajes deben estar entre 0 y 1")
        if codigo in self.PARAMETROS_MONETARIOS and valor <= 0:
            raise ErrorParametro("Los montos monetarios deben ser mayores que cero")

    def _validar_no_solapamiento(self, nuevo: ParametroNormativo, excluir: ParametroNormativo | None = None) -> None:
        for actual in self.parametros:
            if actual is excluir or not self._activo(actual.estado) or self._codigo(actual.codigo) != self._codigo(nuevo.codigo):
                continue
            if self._intervalos_se_cruzan(nuevo, actual):
                raise ErrorParametro(f"La vigencia se solapa para el parámetro {self._codigo(nuevo.codigo)}")

    @staticmethod
    def _intervalos_se_cruzan(primero: ParametroNormativo, segundo: ParametroNormativo) -> bool:
        primero_fin = primero.fechaFinVigencia or date.max
        segundo_fin = segundo.fechaFinVigencia or date.max
        return (primero.fechaInicioVigencia or date.min) <= segundo_fin and (segundo.fechaInicioVigencia or date.min) <= primero_fin

    def _esta_usado_en_liquidacion(self, parametro: ParametroNormativo) -> bool:
        codigo = self._codigo(parametro.codigo)
        return any(
            liquidacion.aprobada
            and any(codigo in str(valor or "") for valor in (liquidacion.regimenLiquidado, liquidacion.medioPago, liquidacion.referenciaPago))
            for liquidacion in self.liquidaciones
        )

    def _buscar(self, id_parametro: int) -> ParametroNormativo:
        parametro = next((item for item in self.parametros if item.idParametro == id_parametro), None)
        if parametro is None:
            raise ErrorParametro(f"No existe el parámetro con ID {id_parametro}")
        return parametro

    def _siguiente_id(self) -> int:
        return max((item.idParametro or 0 for item in self.parametros), default=0) + 1

    @staticmethod
    def _codigo(codigo) -> str:
        return str(getattr(codigo, "value", codigo or "")).upper()

    @staticmethod
    def _activo(estado) -> bool:
        return str(getattr(estado, "value", estado)).upper() == "ACTIVO"

    @staticmethod
    def _vigente_en(parametro: ParametroNormativo, fecha: date) -> bool:
        return (parametro.fechaInicioVigencia or date.min) <= fecha and (
            parametro.fechaFinVigencia is None or fecha <= parametro.fechaFinVigencia
        )
