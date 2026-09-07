"""Cálculo de deducciones de ley al empleado y aportes patronales de seguridad social y parafiscales."""

from __future__ import annotations

from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from dominio.modelo_datos import ParametroNormativo


class CalculadoraDeducciones:
    """Calcula retenciones, aportes a salud/pensión, fondo de solidaridad y parafiscales."""

    CERO = Decimal("0")
    CUATRO = Decimal("4")
    DIEZ = Decimal("10")

    def __init__(self, parametros: list[ParametroNormativo]) -> None:
        self.parametros = parametros

    @staticmethod
    def redondear(valor: Decimal) -> Decimal:
        return valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def obtener_parametro_decimal(self, codigo: str, fecha: date | None = None) -> Decimal | None:
        fecha_consulta = fecha or date.today()
        for p in self.parametros:
            p_cod = str(getattr(p.codigo, "value", p.codigo))
            if p_cod == codigo:
                estado = str(getattr(p.estado, "value", p.estado or "ACTIVO")).upper()
                if estado == "ACTIVO":
                    f_ini_ok = p.fechaInicioVigencia is None or p.fechaInicioVigencia <= fecha_consulta
                    f_fin_ok = p.fechaFinVigencia is None or fecha_consulta <= p.fechaFinVigencia
                    if f_ini_ok and f_fin_ok and p.valor is not None:
                        return Decimal(str(p.valor))
        return None

    def obtener_porcentaje(self, codigo: str, defecto: Decimal, fecha: date | None = None, codigos_utilizados: dict[str, str] | None = None) -> Decimal:
        valor = self.obtener_parametro_decimal(codigo, fecha)
        if codigos_utilizados is not None:
            codigos_utilizados[codigo] = str(valor) if valor is not None else str(defecto)
        return valor if valor is not None else defecto

    # ------------------------------------------------------------------
    # DEDUCCIONES AL TRABAJADOR
    # ------------------------------------------------------------------
    def calcular_descuento_salud(self, ibc: Decimal, fecha: date | None = None, codigos_utilizados: dict[str, str] | None = None) -> Decimal:
        pct = self.obtener_porcentaje("PORCENTAJE_SALUD_TRABAJADOR", Decimal("0.04"), fecha, codigos_utilizados)
        return self.redondear(ibc * pct)

    def calcular_descuento_pension(self, ibc: Decimal, fecha: date | None = None, codigos_utilizados: dict[str, str] | None = None) -> Decimal:
        pct = self.obtener_porcentaje("PORCENTAJE_PENSION_TRABAJADOR", Decimal("0.04"), fecha, codigos_utilizados)
        return self.redondear(ibc * pct)

    def calcular_fondo_solidaridad(self, ibc: Decimal, salario_minimo: Decimal, fecha: date | None = None, codigos_utilizados: dict[str, str] | None = None) -> Decimal:
        if ibc >= self.CUATRO * salario_minimo:
            pct = self.obtener_porcentaje("PORCENTAJE_FONDO_SOLIDARIDAD", self.CERO, fecha, codigos_utilizados)
            return self.redondear(ibc * pct)
        return self.CERO

    def calcular_retencion_fuente(
        self,
        ibc: Decimal,
        fecha: date,
        parametros_personalizados: dict[str, Any] | None = None,
        codigos_utilizados: dict[str, str] | None = None,
    ) -> Decimal:
        if parametros_personalizados:
            base_minima = Decimal(parametros_personalizados.get('base_minima', self.obtener_parametro_decimal("BASE_MINIMA_RETENCION_FUENTE", fecha) or self.CERO))
            pct = Decimal(parametros_personalizados.get('porcentaje', self.obtener_porcentaje("PORCENTAJE_RETENCION_FUENTE", self.CERO, fecha, codigos_utilizados)))
        else:
            base_minima = self.obtener_parametro_decimal("BASE_MINIMA_RETENCION_FUENTE", fecha) or self.CERO
            pct = self.obtener_porcentaje("PORCENTAJE_RETENCION_FUENTE", self.CERO, fecha, codigos_utilizados)

        if ibc < base_minima:
            return self.CERO
        return self.redondear(ibc * pct)

    # ------------------------------------------------------------------
    # APORTES PATRONALES
    # ------------------------------------------------------------------
    def calcular_aporte_salud_patronal(
        self,
        ibc: Decimal,
        salario_minimo: Decimal,
        fecha: date | None = None,
        codigos_utilizados: dict[str, str] | None = None,
        exonerado: bool = False,
    ) -> Decimal:
        """
        Calcula el aporte patronal a salud (8.5%).
        Nota: Según el Art. 114-1 Parágrafo 2 del Estatuto Tributario, las entidades de derecho
        público (como universidades públicas del Estado, e.g. Universidad Popular del Cesar - UPC)
        no son beneficiarias de la exoneración de aportes patronales. Por defecto exonerado=False.
        """
        if exonerado and ibc < self.DIEZ * salario_minimo:
            return self.CERO  # Exoneración tributaria sólo para entidades privadas beneficiarias
        pct = self.obtener_porcentaje("PORCENTAJE_SALUD_EMPLEADOR", Decimal("0.085"), fecha, codigos_utilizados)
        return self.redondear(ibc * pct)

    def calcular_aporte_pension_patronal(self, ibc: Decimal, fecha: date | None = None, codigos_utilizados: dict[str, str] | None = None) -> Decimal:
        pct = self.obtener_porcentaje("PORCENTAJE_PENSION_EMPLEADOR", Decimal("0.12"), fecha, codigos_utilizados)
        return self.redondear(ibc * pct)

    def calcular_aporte_arl(self, ibc: Decimal, clase_arl: str | None, fecha: date | None = None, codigos_utilizados: dict[str, str] | None = None) -> Decimal:
        clase = str(clase_arl or "I").upper().replace("CLASE ", "").strip()
        pct = self.obtener_porcentaje(f"PORCENTAJE_ARL_CLASE_{clase}", Decimal("0.00522"), fecha, codigos_utilizados)
        return self.redondear(ibc * pct)

    def calcular_aporte_caja(self, ibc: Decimal, fecha: date | None = None, codigos_utilizados: dict[str, str] | None = None) -> Decimal:
        pct = self.obtener_porcentaje("PORCENTAJE_CAJA_COMPENSACION", Decimal("0.04"), fecha, codigos_utilizados)
        return self.redondear(ibc * pct)

    def calcular_aporte_sena(self, ibc: Decimal, salario_minimo: Decimal, fecha: date | None = None, codigos_utilizados: dict[str, str] | None = None) -> Decimal:
        if ibc < self.DIEZ * salario_minimo:
            return self.CERO  # Exoneración tributaria
        pct = self.obtener_porcentaje("PORCENTAJE_SENA", Decimal("0.02"), fecha, codigos_utilizados)
        return self.redondear(ibc * pct)

    def calcular_aporte_icbf(self, ibc: Decimal, salario_minimo: Decimal, fecha: date | None = None, codigos_utilizados: dict[str, str] | None = None) -> Decimal:
        if ibc < self.DIEZ * salario_minimo:
            return self.CERO  # Exoneración tributaria
        pct = self.obtener_porcentaje("PORCENTAJE_ICBF", Decimal("0.03"), fecha, codigos_utilizados)
        return self.redondear(ibc * pct)
