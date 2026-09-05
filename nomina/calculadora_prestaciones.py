"""Cálculo de provisiones de prestaciones sociales y bonificaciones institucionales."""

from __future__ import annotations

from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modelo_datos import Contrato, Profesor
    from nomina.calculadora_deducciones import CalculadoraDeducciones


class CalculadoraPrestaciones:
    """Calcula cesantías, primas, vacaciones y bonificaciones especiales."""

    CERO = Decimal("0")
    DOS = Decimal("2")
    DIAS_ANIO = Decimal("360")

    def __init__(self, calculadora_deducciones: CalculadoraDeducciones) -> None:
        self.calc_ded = calculadora_deducciones

    @staticmethod
    def redondear(valor: Decimal) -> Decimal:
        return valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def calcular_auxilio_transporte(
        self,
        contrato: Contrato,
        salario: Decimal,
        smmlv: Decimal,
        fecha: date | None = None,
        codigos_utilizados: dict[str, str] | None = None,
    ) -> Decimal:
        if contrato.aplicaAuxilioTransporte and salario <= self.DOS * smmlv:
            valor = self.calc_ded.obtener_parametro_decimal("VALOR_AUXILIO_TRANSPORTE_VIGENTE", fecha)
            if codigos_utilizados is not None:
                codigos_utilizados["VALOR_AUXILIO_TRANSPORTE_VIGENTE"] = str(valor) if valor is not None else str(self.CERO)
            return valor or self.CERO
        return self.CERO

    def calcular_bonificacion_posgrado(
        self,
        profesor: Profesor,
        smmlv: Decimal,
        contrato: Contrato,
        horas: Decimal | None,
        incluir_bonificaciones: bool,
        codigos_utilizados: dict[str, str] | None = None,
    ) -> Decimal:
        if contrato.permiteBonificacionPosgrado is False or not incluir_bonificaciones:
            return self.CERO
        factores = {
            "ESPECIALIZACION": Decimal("0.10"),
            "MAESTRIA": Decimal("0.45"),
            "DOCTORADO": Decimal("0.90"),
            "POSTDOCTORADO": self.CERO,
        }
        factor = factores.get(str(profesor.nivelPosgradoReconocido or "").upper(), self.CERO)
        if codigos_utilizados is not None:
            codigos_utilizados["BONIFICACION_POSGRADO"] = str(factor)
        return self._bonificacion_proporcional(smmlv * factor, contrato, horas)

    def calcular_bonificacion_investigacion(
        self,
        profesor: Profesor,
        smmlv: Decimal,
        contrato: Contrato,
        horas: Decimal | None,
        incluir_bonificaciones: bool,
        codigos_utilizados: dict[str, str] | None = None,
    ) -> Decimal:
        if contrato.permiteBonificacionInvestigacion is False or not incluir_bonificaciones:
            return self.CERO
        grupo = str(profesor.categoriaGrupoInvestigacion or "").upper()
        factores = {
            "GRUPO_A1": Decimal("0.56"), "A1": Decimal("0.56"),
            "GRUPO_A": Decimal("0.47"), "A": Decimal("0.47"),
            "GRUPO_B": Decimal("0.42"), "B": Decimal("0.42"),
            "GRUPO_C": Decimal("0.38"), "C": Decimal("0.38"),
            "GRUPO_RECONOCIDO": Decimal("0.33"), "SEMILLERO": Decimal("0.20"),
        }
        factor = factores.get(grupo, self.CERO)
        acreditada = bool(profesor.productividadInvestigativaVigente or profesor.participaProyectoInvestigacionVigente) and bool(profesor.certificacionVicerrectoriaInvestigacion)
        if codigos_utilizados is not None:
            codigos_utilizados["BONIFICACION_INVESTIGACION"] = str(factor) if factor else str(self.CERO)
        return self._bonificacion_proporcional(smmlv * factor if acreditada else self.CERO, contrato, horas)

    def _bonificacion_proporcional(self, valor: Decimal, contrato: Contrato, horas: Decimal | None) -> Decimal:
        if horas is None or contrato.horasMensualesAsignadas in (None, 0):
            return valor
        return valor * horas / Decimal(contrato.horasMensualesAsignadas)

    def calcular_provisiones(
        self,
        base_prestacional: Decimal,
        ibc: Decimal,
        dias: Decimal,
        *,
        regimen_especial: bool = False,
    ) -> dict[str, Decimal]:
        provisiones = {
            "cesantias": self.redondear(base_prestacional * dias / self.DIAS_ANIO),
            "intereses": self.redondear(base_prestacional * dias * Decimal("0.12") / self.DIAS_ANIO),
            "prima_servicios": self.redondear(base_prestacional * dias / self.DIAS_ANIO),
            "prima_navidad": self.redondear(base_prestacional * dias / self.DIAS_ANIO),
            "vacaciones": self.redondear(ibc * dias / Decimal("720")),
            "prima_vacaciones": self.CERO,
            "bonificacion_servicios": self.CERO,
        }
        if not regimen_especial:
            return provisiones

        # Bases especiales de los arts. 33, 39 y 46 del Decreto 1279
        tope = self.calc_ded.obtener_parametro_decimal("TOPE_BONIFICACION_SERVICIOS") or Decimal("756411")
        porcentaje = (
            self.calc_ded.obtener_porcentaje("PORCENTAJE_BONIFICACION_SERVICIOS_HASTA_TOPE", Decimal("0.50"))
            if ibc <= tope
            else self.calc_ded.obtener_porcentaje("PORCENTAJE_BONIFICACION_SERVICIOS_SOBRE_TOPE", Decimal("0.35"))
        )
        provisiones["bonificacion_servicios"] = self.redondear(ibc * porcentaje * dias / self.DIAS_ANIO)

        base_vacaciones = ibc + provisiones["prima_servicios"] / Decimal("12") + provisiones["bonificacion_servicios"] / Decimal("12")
        base_prima_vacaciones = (ibc * Decimal("2") / Decimal("3")) + provisiones["prima_servicios"] / Decimal("12") + provisiones["bonificacion_servicios"] / Decimal("12")

        provisiones["vacaciones"] = self.redondear(base_vacaciones * dias / Decimal("720"))
        provisiones["prima_vacaciones"] = self.redondear(base_prima_vacaciones * dias / Decimal("540"))

        base_prima_navidad = (
            ibc
            + provisiones["prima_servicios"] / Decimal("12")
            + provisiones["prima_vacaciones"] / Decimal("12")
            + provisiones["bonificacion_servicios"] / Decimal("12")
        )
        provisiones["prima_navidad"] = self.redondear(base_prima_navidad * dias / self.DIAS_ANIO)
        return provisiones
