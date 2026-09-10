"""Módulo de Consolidación y Desglose de Nómina Anual para PITA.

Permite tomar la nómina liquidada mes a mes (o proyectar los 12 meses de vigencia
contractual) y generar el desglose anual detallado conforme a la normatividad colombiana,
el Decreto 1279 de 2002, el Acuerdo 027 de 2024 y las directrices de Mi Calculadora (Mintrabajo).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from dominio.modelo_datos import Contrato, LiquidacionNomina, Persona, Profesor
    from nomina.gestor_nomina import GestorNomina


def redondear(valor: Decimal | float | int | None) -> Decimal:
    """Redondea a 2 decimales estándar monetario."""
    if valor is None:
        return Decimal("0.00")
    return Decimal(str(valor)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@dataclass
class ItemDesgloseAnual:
    """Detalle de un concepto salarial o prestacional en el desglose anual."""
    concepto: str
    categoria: str  # DEVENGADO, DEDUCCION, PRESTACION, APORTE_PATRONAL
    base_calculo: Decimal = Decimal("0.00")
    porcentaje_o_factor: str = ""
    valor_mensual_promedio: Decimal = Decimal("0.00")
    valor_anual_consolidado: Decimal = Decimal("0.00")
    observaciones: str = ""


@dataclass
class DesgloseNominaAnual:
    """Consolidado completo de nómina anual para un empleado o contrato."""
    id_contrato: int
    id_persona: int | None = None
    nombre_completo: str = ""
    identificacion: str = ""
    tipo_personal: str = ""  # PLANTA, OCASIONAL, CATEDRATICO, ADMINISTRATIVO
    regimen: str = ""        # DECRETO_1279, ACUERDO_027, LEY_100_CST
    anio: int = 2026
    meses_considerados: int = 12
    dias_trabajados_anio: int = 360

    # 1. Devengados Anuales
    salario_ordinario_anual: Decimal = Decimal("0.00")
    bonificaciones_posgrado_anual: Decimal = Decimal("0.00")
    bonificaciones_investigacion_anual: Decimal = Decimal("0.00")
    otras_bonificaciones_anual: Decimal = Decimal("0.00")
    auxilio_transporte_anual: Decimal = Decimal("0.00")
    total_devengado_anual: Decimal = Decimal("0.00")

    # 2. Deducciones Anuales (Trabajador)
    descuento_salud_anual: Decimal = Decimal("0.00")
    descuento_pension_anual: Decimal = Decimal("0.00")
    fondo_solidaridad_anual: Decimal = Decimal("0.00")
    retencion_fuente_anual: Decimal = Decimal("0.00")
    estampillas_anual: Decimal = Decimal("0.00")
    otros_descuentos_anual: Decimal = Decimal("0.00")
    total_descuentos_anual: Decimal = Decimal("0.00")

    # 3. Neto Anual Pagado al Trabajador
    neto_anual_trabajador: Decimal = Decimal("0.00")

    # 4. Prestaciones Sociales Anuales (Consolidadas / Causadas)
    cesantias_anuales: Decimal = Decimal("0.00")
    intereses_cesantias_anuales: Decimal = Decimal("0.00")
    prima_servicios_anual: Decimal = Decimal("0.00")
    vacaciones_anuales: Decimal = Decimal("0.00")
    prima_navidad_anual: Decimal = Decimal("0.00")
    prima_vacaciones_anual: Decimal = Decimal("0.00")
    bonificacion_servicios_anual: Decimal = Decimal("0.00")
    total_prestaciones_anuales: Decimal = Decimal("0.00")

    # 5. Aportes Patronales y Parafiscales Anuales (Costo UPC)
    salud_patronal_anual: Decimal = Decimal("0.00")
    pension_patronal_anual: Decimal = Decimal("0.00")
    arl_patronal_anual: Decimal = Decimal("0.00")
    caja_compensacion_anual: Decimal = Decimal("0.00")
    sena_anual: Decimal = Decimal("0.00")
    icbf_anual: Decimal = Decimal("0.00")
    total_aportes_patronales_anual: Decimal = Decimal("0.00")

    # 6. Costo Total Institucional Anual (Presupuesto Empleador)
    costo_total_empleador_anual: Decimal = Decimal("0.00")

    # Detalle concepto a concepto
    items: list[ItemDesgloseAnual] = field(default_factory=list)


class CalculadorDesgloseAnual:
    """Servicio de cálculo y consolidación de nómina anual."""

    def __init__(self, gestor: GestorNomina) -> None:
        self.gestor = gestor

    def generar_desglose_por_contrato(
        self,
        id_contrato: int,
        anio: int = 2026,
        *,
        proyectar_12_meses: bool = True,
    ) -> DesgloseNominaAnual:
        """Genera el desglose anual para un contrato específico.

        Si proyectar_12_meses es True, toma la liquidación tipo y la multiplica
        por los meses de vigencia en el año (12 para planta, meses del contrato para ocasionales).
        Si es False, acumula estrictamente los periodos registrados en ese año.
        """
        contrato = self.gestor._contrato(id_contrato)
        profesor = self._obtener_profesor(contrato.idPersona)
        persona = self._obtener_persona(contrato.idPersona)
        if persona:
            partes_nom = [persona.primerNombre or "", persona.segundoNombre or "", persona.primerApellido or "", persona.segundoApellido or ""]
            nombre = " ".join(p for p in partes_nom if p).strip() or f"Empleado #{id_contrato}"
            identificacion = persona.numeroDocumento or ""
        else:
            nombre = f"Empleado #{id_contrato}"
            identificacion = ""

        tipo_personal = str(getattr(contrato, "modalidadProfesor", None) or getattr(contrato, "tipoContrato", "PLANTA")).upper()
        if hasattr(contrato.modalidadProfesor, "name"):
            tipo_personal = contrato.modalidadProfesor.name

        regimen = str(getattr(contrato, "regimenAplicable", "GENERAL")).upper()

        es_adm = (
            "ADMINISTRATIVO" in tipo_personal
            or "ADMINISTRATIVO" in regimen
            or any(getattr(a, "idPersona", None) == contrato.idPersona for a in getattr(self.gestor, "administrativos", []))
            or (self._obtener_profesor(contrato.idPersona) is None)
        )
        if es_adm:
            tipo_personal = "ADMINISTRATIVO"

        # Determinar meses y días de vigencia en el año
        meses_vigencia = 12
        if tipo_personal in ("PLANTA", "ADMINISTRATIVO"):
            meses_vigencia = 12
        elif contrato.fechaInicio and contrato.fechaFin:
            # Calcular meses calendario entre inicio y fin limitados al año
            f_ini = contrato.fechaInicio
            f_fin = contrato.fechaFin
            if f_ini.year == anio and f_fin.year == anio:
                meses_vigencia = max(1, (f_fin.year - f_ini.year) * 12 + f_fin.month - f_ini.month + 1)
            elif f_ini.year == anio:
                meses_vigencia = max(1, 12 - f_ini.month + 1)
            elif f_fin.year == anio:
                meses_vigencia = max(1, f_fin.month)

        dias_anio = meses_vigencia * 30

        # Buscar liquidaciones existentes para este contrato
        liqs_existentes = [l for l in self.gestor.liquidaciones if l.idContrato == id_contrato]

        # Si no hay liquidaciones, realizamos una liquidación mensual simulada
        if not liqs_existentes:
            periodo_ref = next((p for p in self.gestor.periodos_nomina if not contrato.fechaInicio or not p.fechaFin or contrato.fechaInicio <= p.fechaFin), None)
            temp_agregado = False
            if periodo_ref is None:
                from calendar import monthrange
                from datetime import date
                from dominio.modelo_datos import PeriodoNomina
                y_ini = contrato.fechaInicio.year if contrato.fechaInicio else anio
                m_ini = contrato.fechaInicio.month if contrato.fechaInicio else 1
                _, u_dia = monthrange(y_ini, m_ini)
                p_orig = self.gestor.periodos_nomina[0] if self.gestor.periodos_nomina else None
                periodo_ref = PeriodoNomina(
                    idPeriodoNomina=9999,
                    anio=y_ini,
                    mes=m_ini,
                    fechaInicio=contrato.fechaInicio or date(y_ini, m_ini, 1),
                    fechaFin=date(y_ini, m_ini, u_dia),
                    fechaPago=date(y_ini, m_ini, u_dia),
                    salarioMinimoVigente=getattr(p_orig, "salarioMinimoVigente", None) or Decimal("1750905"),
                    valorPuntoSalarialVigente=getattr(p_orig, "valorPuntoSalarialVigente", None) or Decimal("23924"),
                    diasBaseLiquidacion=30,
                    estado="ABIERTO",
                )
                self.gestor.periodos_nomina.append(periodo_ref)
                temp_agregado = True

            id_per = periodo_ref.idPeriodoNomina
            try:
                if es_adm or "ADMINISTRATIVO" in tipo_personal:
                    liq_base = self.gestor.liquidarAdministrativo(id_contrato, id_per)
                elif "PLANTA" in tipo_personal:
                    liq_base = self.gestor.liquidarProfesorPlanta(id_contrato, id_per)
                elif "CATEDRATICO" in tipo_personal:
                    liq_base = self.gestor.liquidarProfesorCatedratico(id_contrato, id_per)
                else:
                    liq_base = self.gestor.liquidarProfesorOcasional(id_contrato, id_per)
            finally:
                if temp_agregado and periodo_ref in self.gestor.periodos_nomina:
                    self.gestor.periodos_nomina.remove(periodo_ref)
        else:
            liq_base = liqs_existentes[0]

        # Factores multiplicadores
        meses_mult = Decimal(str(meses_vigencia))

        desglose = DesgloseNominaAnual(
            id_contrato=id_contrato,
            id_persona=contrato.idPersona,
            nombre_completo=nombre,
            identificacion=identificacion,
            tipo_personal=tipo_personal,
            regimen=regimen,
            anio=anio,
            meses_considerados=meses_vigencia,
            dias_trabajados_anio=dias_anio,
        )

        # 1. Devengados Anuales
        sal_ord = redondear(liq_base.salarioOrdinario or liq_base.salarioBase or Decimal("0"))
        bon_pos = redondear(liq_base.bonificacionPosgrado or Decimal("0"))
        bon_inv = redondear(liq_base.bonificacionInvestigacion or Decimal("0"))
        otras_bon = redondear(
            (liq_base.bonificacionesSalariales or Decimal("0"))
            + (liq_base.bonificacionesNoSalariales or Decimal("0"))
            - bon_pos - bon_inv
        )
        aux_trans = redondear(liq_base.valorAuxilioTransporteCotizado or Decimal("0"))

        desglose.salario_ordinario_anual = redondear(sal_ord * meses_mult)
        desglose.bonificaciones_posgrado_anual = redondear(bon_pos * meses_mult)
        desglose.bonificaciones_investigacion_anual = redondear(bon_inv * meses_mult)
        desglose.otras_bonificaciones_anual = redondear(otras_bon * meses_mult)
        desglose.auxilio_transporte_anual = redondear(aux_trans * meses_mult)

        desglose.total_devengado_anual = redondear(
            desglose.salario_ordinario_anual
            + desglose.bonificaciones_posgrado_anual
            + desglose.bonificaciones_investigacion_anual
            + desglose.otras_bonificaciones_anual
            + desglose.auxilio_transporte_anual
        )

        # 2. Deducciones Anuales
        desc_salud = redondear(liq_base.descuentoSalud or Decimal("0"))
        desc_pension = redondear(liq_base.descuentoPension or Decimal("0"))
        fsp = redondear(liq_base.fondoSolidaridadPensional or Decimal("0"))
        retefuente = redondear(liq_base.retencionFuente or Decimal("0"))
        estampillas = redondear(liq_base.otrosDescuentos or Decimal("0"))

        desglose.descuento_salud_anual = redondear(desc_salud * meses_mult)
        desglose.descuento_pension_anual = redondear(desc_pension * meses_mult)
        desglose.fondo_solidaridad_anual = redondear(fsp * meses_mult)
        desglose.retencion_fuente_anual = redondear(retefuente * meses_mult)
        desglose.estampillas_anual = redondear(estampillas * meses_mult)

        desglose.total_descuentos_anual = redondear(
            desglose.descuento_salud_anual
            + desglose.descuento_pension_anual
            + desglose.fondo_solidaridad_anual
            + desglose.retencion_fuente_anual
            + desglose.estampillas_anual
        )

        # 3. Neto Anual Trabajador
        desglose.neto_anual_trabajador = redondear(desglose.total_devengado_anual - desglose.total_descuentos_anual)

        # 4. Prestaciones Sociales Consolidadas Anuales
        # Se liquidan sobre los días totales trabajados en el año (cierre definitivo a 31 de diciembre)
        dias_dec = Decimal(str(dias_anio))
        base_prest = redondear(liq_base.baseLiquidacionPrestaciones or liq_base.salarioOrdinario or sal_ord)
        base_ibc = redondear(liq_base.baseSeguridadSocial or sal_ord)

        desglose.cesantias_anuales = redondear(base_prest * dias_dec / Decimal("360"))
        desglose.intereses_cesantias_anuales = redondear(desglose.cesantias_anuales * Decimal("0.12") * dias_dec / Decimal("360"))
        desglose.prima_servicios_anual = redondear(base_prest * dias_dec / Decimal("360"))

        if "PLANTA" in tipo_personal and ("1279" in regimen or regimen == "NONE" or not regimen):
            tope = Decimal("756411")
            pct_bon = Decimal("0.50") if base_ibc <= tope else Decimal("0.35")
            desglose.bonificacion_servicios_anual = redondear(base_ibc * pct_bon * dias_dec / Decimal("360"))

            base_p_vac = (base_ibc * Decimal("2") / Decimal("3")) + (desglose.prima_servicios_anual / Decimal("12")) + (desglose.bonificacion_servicios_anual / Decimal("12"))
            desglose.prima_vacaciones_anual = redondear(base_p_vac * dias_dec / Decimal("540"))

            base_vac = base_ibc + (desglose.prima_servicios_anual / Decimal("12")) + (desglose.bonificacion_servicios_anual / Decimal("12"))
            desglose.vacaciones_anuales = redondear(base_vac * dias_dec / Decimal("720"))

            base_nav = base_ibc + (desglose.prima_servicios_anual / Decimal("12")) + (desglose.prima_vacaciones_anual / Decimal("12")) + (desglose.bonificacion_servicios_anual / Decimal("12"))
            desglose.prima_navidad_anual = redondear(base_nav * dias_dec / Decimal("360"))
        else:
            desglose.vacaciones_anuales = redondear(base_ibc * dias_dec / Decimal("720"))
            desglose.prima_navidad_anual = redondear(base_prest * dias_dec / Decimal("360"))
            desglose.prima_vacaciones_anual = Decimal("0.00")
            desglose.bonificacion_servicios_anual = Decimal("0.00")

        desglose.total_prestaciones_anuales = redondear(
            desglose.cesantias_anuales
            + desglose.intereses_cesantias_anuales
            + desglose.prima_servicios_anual
            + desglose.prima_navidad_anual
            + desglose.vacaciones_anuales
            + desglose.prima_vacaciones_anual
            + desglose.bonificacion_servicios_anual
        )

        # 5. Aportes Patronales Anuales
        salud_pat = redondear(liq_base.aportePatronalSalud or Decimal("0"))
        pens_pat = redondear(liq_base.aportePatronalPension or Decimal("0"))
        arl_pat = redondear(liq_base.aporteRiesgosLaborales or Decimal("0"))
        caja_pat = redondear(liq_base.aporteCajaCompensacion or Decimal("0"))
        sena_pat = redondear(liq_base.aportePatronalSENA or Decimal("0"))
        icbf_pat = redondear(liq_base.aportePatronalICBF or Decimal("0"))

        desglose.salud_patronal_anual = redondear(salud_pat * meses_mult)
        desglose.pension_patronal_anual = redondear(pens_pat * meses_mult)
        desglose.arl_patronal_anual = redondear(arl_pat * meses_mult)
        desglose.caja_compensacion_anual = redondear(caja_pat * meses_mult)
        desglose.sena_anual = redondear(sena_pat * meses_mult)
        desglose.icbf_anual = redondear(icbf_pat * meses_mult)

        desglose.total_aportes_patronales_anual = redondear(
            desglose.salud_patronal_anual
            + desglose.pension_patronal_anual
            + desglose.arl_patronal_anual
            + desglose.caja_compensacion_anual
            + desglose.sena_anual
            + desglose.icbf_anual
        )

        # 6. Costo Total Institucional Anual
        desglose.costo_total_empleador_anual = redondear(
            desglose.total_devengado_anual
            + desglose.total_prestaciones_anuales
            + desglose.total_aportes_patronales_anual
        )

        # Crear lista detallada de items
        desglose.items = self._construir_items_detalle(desglose, liq_base)
        return desglose

    def _construir_items_detalle(self, d: DesgloseNominaAnual, liq: LiquidacionNomina) -> list[ItemDesgloseAnual]:
        items: list[ItemDesgloseAnual] = []

        # DEVENGADOS
        items.append(ItemDesgloseAnual(
            concepto="Salario Básico / Asignación Ordinaria",
            categoria="DEVENGADO",
            porcentaje_o_factor="100%",
            valor_mensual_promedio=redondear(liq.salarioOrdinario),
            valor_anual_consolidado=d.salario_ordinario_anual,
            observaciones=f"{d.meses_considerados} meses laborados ({d.dias_trabajados_anio} días)",
        ))
        if d.bonificaciones_posgrado_anual > 0:
            items.append(ItemDesgloseAnual(
                concepto="Bonificación por Posgrado (Acuerdo 027)",
                categoria="DEVENGADO",
                porcentaje_o_factor="Factor s/SMMLV",
                valor_mensual_promedio=redondear(liq.bonificacionPosgrado),
                valor_anual_consolidado=d.bonificaciones_posgrado_anual,
                observaciones="No constitutivo de salario",
            ))
        if d.bonificaciones_investigacion_anual > 0:
            items.append(ItemDesgloseAnual(
                concepto="Bonificación por Grupo de Investigación",
                categoria="DEVENGADO",
                porcentaje_o_factor="Factor s/SMMLV",
                valor_mensual_promedio=redondear(liq.bonificacionInvestigacion),
                valor_anual_consolidado=d.bonificaciones_investigacion_anual,
                observaciones="Acreditado MinCiencias",
            ))
        if d.auxilio_transporte_anual > 0:
            items.append(ItemDesgloseAnual(
                concepto="Auxilio de Transporte Legal",
                categoria="DEVENGADO",
                porcentaje_o_factor="Ley",
                valor_mensual_promedio=redondear(liq.valorAuxilioTransporteCotizado),
                valor_anual_consolidado=d.auxilio_transporte_anual,
                observaciones="Aplica para salarios <= 2 SMMLV",
            ))

        # DEDUCCIONES
        items.append(ItemDesgloseAnual(
            concepto="Aporte a Salud (Empleado)",
            categoria="DEDUCCION",
            porcentaje_o_factor="4.00%",
            valor_mensual_promedio=redondear(liq.descuentoSalud),
            valor_anual_consolidado=d.descuento_salud_anual,
            observaciones="Ley 100 de 1993",
        ))
        items.append(ItemDesgloseAnual(
            concepto="Aporte a Pensión (Empleado)",
            categoria="DEDUCCION",
            porcentaje_o_factor="4.00%",
            valor_mensual_promedio=redondear(liq.descuentoPension),
            valor_anual_consolidado=d.descuento_pension_anual,
            observaciones="Ley 100 de 1993",
        ))
        if d.fondo_solidaridad_anual > 0:
            items.append(ItemDesgloseAnual(
                concepto="Fondo de Solidaridad Pensional",
                categoria="DEDUCCION",
                porcentaje_o_factor="1.00%",
                valor_mensual_promedio=redondear(liq.fondoSolidaridadPensional),
                valor_anual_consolidado=d.fondo_solidaridad_anual,
                observaciones="Salarios > 4 SMMLV",
            ))
        if d.retencion_fuente_anual > 0:
            items.append(ItemDesgloseAnual(
                concepto="Retención en la Fuente",
                categoria="DEDUCCION",
                porcentaje_o_factor="Estatuto Tributario",
                valor_mensual_promedio=redondear(liq.retencionFuente),
                valor_anual_consolidado=d.retencion_fuente_anual,
                observaciones="Retención sobre salarios",
            ))

        # PRESTACIONES SOCIALES
        items.append(ItemDesgloseAnual(
            concepto="Cesantías Anuales",
            categoria="PRESTACION",
            porcentaje_o_factor="8.33% (1 mes/año)",
            valor_mensual_promedio=redondear(liq.provisionCesantias),
            valor_anual_consolidado=d.cesantias_anuales,
            observaciones="A consignar al fondo antes del 15 de febrero",
        ))
        items.append(ItemDesgloseAnual(
            concepto="Intereses sobre Cesantías",
            categoria="PRESTACION",
            porcentaje_o_factor="12.00% anual s/cesantías",
            valor_mensual_promedio=redondear(liq.provisionInteresesCesantias),
            valor_anual_consolidado=d.intereses_cesantias_anuales,
            observaciones="A pagar al empleado a más tardar el 31 de enero",
        ))
        items.append(ItemDesgloseAnual(
            concepto="Prima de Servicios",
            categoria="PRESTACION",
            porcentaje_o_factor="8.33% (1 mes/año)",
            valor_mensual_promedio=redondear(liq.provisionPrimaServicios),
            valor_anual_consolidado=d.prima_servicios_anual,
            observaciones="50% en junio y 50% en diciembre",
        ))
        items.append(ItemDesgloseAnual(
            concepto="Vacaciones",
            categoria="PRESTACION",
            porcentaje_o_factor="4.17% (15 días hábiles)",
            valor_mensual_promedio=redondear(liq.provisionVacaciones),
            valor_anual_consolidado=d.vacaciones_anuales,
            observaciones="Descanso anual remunerado",
        ))
        if d.prima_navidad_anual > 0:
            items.append(ItemDesgloseAnual(
                concepto="Prima de Navidad (Dec. 1279)",
                categoria="PRESTACION",
                porcentaje_o_factor="1 mes + doceavas",
                valor_mensual_promedio=redondear(liq.provisionPrimaNavidad),
                valor_anual_consolidado=d.prima_navidad_anual,
                observaciones="A pagar en primera quincena de diciembre",
            ))
        if d.prima_vacaciones_anual > 0:
            items.append(ItemDesgloseAnual(
                concepto="Prima de Vacaciones (Dec. 1279)",
                categoria="PRESTACION",
                porcentaje_o_factor="Art. 38 Dec. 1279",
                valor_mensual_promedio=redondear(liq.provisionPrimaVacaciones),
                valor_anual_consolidado=d.prima_vacaciones_anual,
                observaciones="Pago adicional en época de vacaciones",
            ))
        if d.bonificacion_servicios_anual > 0:
            items.append(ItemDesgloseAnual(
                concepto="Bonificación por Servicios Prestados",
                categoria="PRESTACION",
                porcentaje_o_factor="35% o 50% s/salario",
                valor_mensual_promedio=redondear(liq.bonificacionServiciosPrestados),
                valor_anual_consolidado=d.bonificacion_servicios_anual,
                observaciones="Al cumplir el año de servicio continuo",
            ))

        # APORTES PATRONALES
        if d.salud_patronal_anual > 0:
            items.append(ItemDesgloseAnual(
                concepto="Salud Patronal",
                categoria="APORTE_PATRONAL",
                porcentaje_o_factor="8.50%",
                valor_mensual_promedio=redondear(liq.aportePatronalSalud),
                valor_anual_consolidado=d.salud_patronal_anual,
                observaciones="Aporte UPC entidad promotora de salud",
            ))
        items.append(ItemDesgloseAnual(
            concepto="Pensión Patronal",
            categoria="APORTE_PATRONAL",
            porcentaje_o_factor="12.00%",
            valor_mensual_promedio=redondear(liq.aportePatronalPension),
            valor_anual_consolidado=d.pension_patronal_anual,
            observaciones="Aporte UPC fondo pensional",
        ))
        items.append(ItemDesgloseAnual(
            concepto="Riesgos Laborales (ARL)",
            categoria="APORTE_PATRONAL",
            porcentaje_o_factor="0.522% (Clase I)",
            valor_mensual_promedio=redondear(liq.aporteRiesgosLaborales),
            valor_anual_consolidado=d.arl_patronal_anual,
            observaciones="Cobertura ARL Positiva",
        ))
        items.append(ItemDesgloseAnual(
            concepto="Caja de Compensación Familiar",
            categoria="APORTE_PATRONAL",
            porcentaje_o_factor="4.00%",
            valor_mensual_promedio=redondear(liq.aporteCajaCompensacion),
            valor_anual_consolidado=d.caja_compensacion_anual,
            observaciones="Comfacesar / Caja de compensación",
        ))

        return items

    def generar_desglose_institucional(self, anio: int = 2026) -> dict[str, Any]:
        """Calcula el consolidado anual de toda la universidad para todos los contratos vigentes."""
        desgloses: list[DesgloseNominaAnual] = []
        for contrato in self.gestor.contratos:
            if getattr(contrato, "estado", "ACTIVO") == "ACTIVO":
                d = self.generar_desglose_por_contrato(contrato.idContrato, anio=anio)
                desgloses.append(d)

        # Sumatorias globales
        tot_dev = sum((d.total_devengado_anual for d in desgloses), Decimal("0"))
        tot_desc = sum((d.total_descuentos_anual for d in desgloses), Decimal("0"))
        tot_neto = sum((d.neto_anual_trabajador for d in desgloses), Decimal("0"))
        tot_prest = sum((d.total_prestaciones_anuales for d in desgloses), Decimal("0"))
        tot_aport = sum((d.total_aportes_patronales_anual for d in desgloses), Decimal("0"))
        tot_costo = sum((d.costo_total_empleador_anual for d in desgloses), Decimal("0"))

        return {
            "anio": anio,
            "total_contratos": len(desgloses),
            "desgloses_individuales": desgloses,
            "total_devengado_anual": redondear(tot_dev),
            "total_descuentos_anual": redondear(tot_desc),
            "total_neto_anual": redondear(tot_neto),
            "total_prestaciones_anual": redondear(tot_prest),
            "total_aportes_patronales_anual": redondear(tot_aport),
            "costo_total_institucional_anual": redondear(tot_costo),
        }

    def generar_reporte_texto(self, anio: int = 2026) -> str:
        """Construye un reporte en formato texto / Markdown presentable."""
        institucional = self.generar_desglose_institucional(anio=anio)
        lineas: list[str] = []

        lineas.append("=" * 88)
        lineas.append(f" UNIVERSIDAD POPULAR DEL CESAR (UPC) — CONSOLIDADO DE NÓMINA ANUAL {anio}")
        lineas.append(" Subsistema PITA de Gestión Académica y Nómina Docente (Decreto 1279 / CST)")
        lineas.append("=" * 88)
        lineas.append("")
        lineas.append(f"Total Contratos Analizados: {institucional['total_contratos']}")
        lineas.append(f"Presupuesto Total Empleador Anual: $ {institucional['costo_total_institucional_anual']:,.2f} COP")
        lineas.append(f"  -> Total Devengado Anual (Bruto):  $ {institucional['total_devengado_anual']:,.2f} COP")
        lineas.append(f"  -> Total Deducciones Anuales:      $ {institucional['total_descuentos_anual']:,.2f} COP")
        lineas.append(f"  -> Total Neto Pagado a Docentes:   $ {institucional['total_neto_anual']:,.2f} COP")
        lineas.append(f"  -> Total Prestaciones Sociales:    $ {institucional['total_prestaciones_anual']:,.2f} COP")
        lineas.append(f"  -> Total Aportes Patronales/Paraf: $ {institucional['total_aportes_patronales_anual']:,.2f} COP")
        lineas.append("")

        for d in institucional["desgloses_individuales"]:
            lineas.append("-" * 88)
            lineas.append(f"DOCENTE: {d.nombre_completo} (ID Contrato: #{d.id_contrato} | CC: {d.identificacion})")
            lineas.append(f"Régimen: {d.regimen} | Categoría: {d.tipo_personal} | Meses: {d.meses_considerados} ({d.dias_trabajados_anio} días)")
            lineas.append("-" * 88)
            lineas.append(f"{'CONCEPTO':<36} | {'FACTOR / %':<16} | {'VALOR MENSUAL':>14} | {'TOTAL ANUAL':>14}")
            lineas.append("-" * 88)
            for item in d.items:
                lineas.append(f"{item.concepto:<36} | {item.porcentaje_o_factor:<16} | ${item.valor_mensual_promedio:>13,.2f} | ${item.valor_anual_consolidado:>13,.2f}")
            lineas.append("." * 88)
            lineas.append(f"{'TOTAL DEVENGADO ANUAL':<36} | {'':<16} | {'':>14} | ${d.total_devengado_anual:>13,.2f}")
            lineas.append(f"{'TOTAL DEDUCCIONES ANUAL':<36} | {'':<16} | {'':>14} | ${d.total_descuentos_anual:>13,.2f}")
            lineas.append(f"{'NETO ANUAL A RECIBIR':<36} | {'':<16} | {'':>14} | ${d.neto_anual_trabajador:>13,.2f}")
            lineas.append(f"{'TOTAL PRESTACIONES ANUAL':<36} | {'':<16} | {'':>14} | ${d.total_prestaciones_anuales:>13,.2f}")
            lineas.append(f"{'TOTAL APORTES PATRONALES':<36} | {'':<16} | {'':>14} | ${d.total_aportes_patronales_anual:>13,.2f}")
            lineas.append(f"{'COSTO TOTAL EMPLEADOR ANUAL':<36} | {'':<16} | {'':>14} | ${d.costo_total_empleador_anual:>13,.2f}")
            lineas.append("")

        return "\n".join(lineas)

    def _obtener_profesor(self, id_persona: int | None) -> Profesor | None:
        if id_persona is None:
            return None
        return next((p for p in self.gestor.profesores if p.idPersona == id_persona), None)

    def _obtener_persona(self, id_persona: int | None) -> Persona | None:
        if id_persona is None:
            return None
        # Buscar en gestor_personas o atributos si están disponibles
        if hasattr(self.gestor, "personas") and self.gestor.personas:
            return next((p for p in self.gestor.personas if p.idPersona == id_persona), None)
        return None
