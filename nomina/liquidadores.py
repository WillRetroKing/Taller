"""Motores de liquidación especializados por régimen docente (Planta, Ocasional y Cátedra)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from dominio.modelo_datos import (
    Contrato,
    Dedicacion,
    DetalleLiquidacion,
    LiquidacionNomina,
    PeriodoNomina,
    Profesor,
    TipoProfesor,
)
from nomina.excepciones import ErrorNomina

if TYPE_CHECKING:
    from nomina.gestor_nomina import GestorNomina


class MotorLiquidacionBase:
    """Clase base para liquidadores con lógica compartida de liquidación y detalles."""

    CERO = Decimal("0")
    CUATRO = Decimal("4")
    DIEZ = Decimal("10")

    def __init__(self, gestor: GestorNomina) -> None:
        self.gestor = gestor

    def _ensamblar_liquidacion(
        self,
        *,
        contrato: Contrato,
        profesor: Profesor,
        periodo: PeriodoNomina,
        fecha_liquidacion: date | None,
        salario_base: Decimal,
        salario_ordinario: Decimal,
        ibc: Decimal,
        horas_asignadas: Decimal | None,
        horas_cumplidas: Decimal | None,
        horas_incumplidas: Decimal,
        descuento_incumplimiento: Decimal,
        tipo: TipoProfesor,
        horas_pagables: Decimal | None = None,
        es_ad_honorem: bool = False,
        incluir_bonificaciones: bool = True,
    ) -> LiquidacionNomina:
        if ibc < self.CERO:
            raise ErrorNomina("El IBC no puede ser negativo")

        fecha_param = periodo.fechaFin or periodo.fechaInicio or date.today()
        codigos_utilizados: dict[str, str] = {}

        salario_minimo = self.gestor._salario_minimo(contrato, periodo, fecha_param, codigos_utilizados)
        auxilio = self.gestor.calc_prestaciones.calcular_auxilio_transporte(contrato, salario_ordinario, salario_minimo, fecha_param, codigos_utilizados)
        base_prestacional = ibc + auxilio

        bonif_posgrado = self.gestor.calc_prestaciones.calcular_bonificacion_posgrado(profesor, salario_minimo, contrato, horas_pagables, incluir_bonificaciones, codigos_utilizados)
        bonif_investigacion = self.gestor.calc_prestaciones.calcular_bonificacion_investigacion(profesor, salario_minimo, contrato, horas_pagables, incluir_bonificaciones, codigos_utilizados)

        calc_ded = self.gestor.calc_deducciones
        descuento_salud = calc_ded.calcular_descuento_salud(ibc, fecha_param, codigos_utilizados)
        descuento_pension = calc_ded.calcular_descuento_pension(ibc, fecha_param, codigos_utilizados)
        fondo_solidaridad = calc_ded.calcular_fondo_solidaridad(ibc, salario_minimo, fecha_param, codigos_utilizados)
        retencion = calc_ded.calcular_retencion_fuente(ibc, fecha_param, codigos_utilizados=codigos_utilizados)

        aporte_salud = calc_ded.calcular_aporte_salud_patronal(ibc, salario_minimo, fecha_param, codigos_utilizados)
        aporte_pension = calc_ded.calcular_aporte_pension_patronal(ibc, fecha_param, codigos_utilizados)
        aporte_arl = calc_ded.calcular_aporte_arl(ibc, contrato.claseARL, fecha_param, codigos_utilizados)
        aporte_caja = calc_ded.calcular_aporte_caja(ibc, fecha_param, codigos_utilizados)
        aporte_sena = calc_ded.calcular_aporte_sena(ibc, salario_minimo, fecha_param, codigos_utilizados)
        aporte_icbf = calc_ded.calcular_aporte_icbf(ibc, salario_minimo, fecha_param, codigos_utilizados)

        dias = self.gestor._decimal(periodo.diasBaseLiquidacion or 30, "días base de liquidación")
        regimen_especial = tipo == TipoProfesor.PLANTA and self.gestor._es_regimen_1279(contrato.regimenAplicable)
        provisiones = self.gestor.calc_prestaciones.calcular_provisiones(base_prestacional, ibc, dias, regimen_especial=regimen_especial)

        bonificaciones = bonif_posgrado + bonif_investigacion
        total_descuentos = descuento_salud + descuento_pension + fondo_solidaridad + retencion + descuento_incumplimiento
        total_devengado = salario_ordinario + auxilio + bonificaciones
        total_prestaciones = sum(provisiones.values(), self.CERO)
        neto = total_devengado - total_descuentos

        liquidacion = LiquidacionNomina(
            idLiquidacion=self.gestor._siguiente_id(),
            idProfesor=profesor.idProfesor,
            idContrato=contrato.idContrato,
            idPeriodoNomina=periodo.idPeriodoNomina,
            fechaLiquidacion=fecha_liquidacion or date.today(),
            salarioBase=salario_base,
            totalDevengado=self.gestor._redondear(total_devengado),
            totalDescuentos=self.gestor._redondear(total_descuentos),
            totalPrestaciones=self.gestor._redondear(total_prestaciones),
            baseLiquidacionPrestaciones=self.gestor._redondear(base_prestacional),
            baseCotizacionSeguridadSocial=self.gestor._redondear(ibc),
            valorAuxilioTransporteCotizado=self.gestor._redondear(auxilio),
            aportePatronalSENA=self.gestor._redondear(aporte_sena),
            aportePatronalICBF=self.gestor._redondear(aporte_icbf),
            netoPagar=self.gestor._redondear(neto),
            estado="PROCESADA",
            tipoProfesorLiquidado=tipo,
            regimenLiquidado=contrato.regimenAplicable,
            dedicacionLiquidada=contrato.dedicacion,
            diasTrabajados=dias,
            horasAsignadas=horas_asignadas,
            horasCumplidas=horas_cumplidas,
            horasIncumplidas=horas_incumplidas,
            salarioMinimoUsado=salario_minimo,
            valorHoraCatedraUsado=contrato.valorHoraCatedraVigente,
            factorCategoriaUsado=contrato.factorSalarialSMMLV,
            salarioOrdinario=self.gestor._redondear(salario_ordinario),
            baseSalarialPrestacional=self.gestor._redondear(base_prestacional),
            baseSeguridadSocial=self.gestor._redondear(ibc),
            bonificacionPosgrado=self.gestor._redondear(bonif_posgrado),
            bonificacionInvestigacion=self.gestor._redondear(bonif_investigacion),
            bonificacionesNoSalariales=self.gestor._redondear(bonificaciones),
            descuentoSalud=descuento_salud,
            descuentoPension=descuento_pension,
            fondoSolidaridadPensional=fondo_solidaridad,
            retencionFuente=retencion,
            descuentoHorasIncumplidas=self.gestor._redondear(descuento_incumplimiento),
            provisionCesantias=provisiones["cesantias"],
            provisionInteresesCesantias=provisiones["intereses"],
            provisionPrimaServicios=provisiones["prima_servicios"],
            provisionPrimaNavidad=provisiones["prima_navidad"],
            provisionVacaciones=provisiones["vacaciones"],
            provisionPrimaVacaciones=provisiones["prima_vacaciones"],
            bonificacionServiciosPrestados=provisiones["bonificacion_servicios"],
            aportePatronalSalud=self.gestor._redondear(aporte_salud),
            aportePatronalPension=aporte_pension,
            aporteRiesgosLaborales=aporte_arl,
            aporteCajaCompensacion=aporte_caja,
            costoTotalEmpleador=self.gestor._redondear(
                total_devengado + total_prestaciones + aporte_salud + aporte_pension + aporte_arl + aporte_sena + aporte_icbf + aporte_caja
            ),
            parametros_utilizados=codigos_utilizados if codigos_utilizados else None,
        )
        self.gestor.liquidaciones.append(liquidacion)
        self._crear_detalles(
            liquidacion, periodo, ibc, salario_ordinario, auxilio,
            bonif_posgrado, bonif_investigacion, descuento_salud, descuento_pension,
            fondo_solidaridad, retencion, descuento_incumplimiento, aporte_salud,
            aporte_pension, aporte_arl, aporte_caja, aporte_sena, aporte_icbf, codigos_utilizados
        )
        return liquidacion

    def _crear_detalles(
        self, liquidacion: LiquidacionNomina, periodo: PeriodoNomina, ibc: Decimal,
        salario_ordinario: Decimal, auxilio: Decimal, bonificacion_posgrado: Decimal,
        bonificacion_investigacion: Decimal, descuento_salud: Decimal,
        descuento_pension: Decimal, fondo_solidaridad: Decimal, retencion: Decimal,
        descuento_incumplimiento: Decimal, aporte_salud: Decimal,
        aporte_pension: Decimal, aporte_arl: Decimal, aporte_caja: Decimal,
        aporte_sena: Decimal, aporte_icbf: Decimal, codigos_utilizados: dict[str, str] | None = None,
    ) -> None:
        calc_ded = self.gestor.calc_deducciones
        conceptos = (
            ("SALARIO_ORDINARIO", salario_ordinario, ibc, None, "salarioOrdinario = IBC"),
            ("AUXILIO_TRANSPORTE", auxilio, self.CERO, None, "auxilio según salario y SMMLV"),
            ("BONIFICACION_POSGRADO", bonificacion_posgrado, self.CERO, None, "SMMLV * factorPosgrado"),
            ("BONIFICACION_INVESTIGACION", bonificacion_investigacion, self.CERO, None, "SMMLV * factorInvestigacion"),
            ("DESCUENTO_SALUD", descuento_salud, ibc, calc_ded.obtener_porcentaje("PORCENTAJE_SALUD_TRABAJADOR", self.CERO, codigos_utilizados=codigos_utilizados), "IBC * porcentajeSaludTrabajador"),
            ("DESCUENTO_PENSION", descuento_pension, ibc, calc_ded.obtener_porcentaje("PORCENTAJE_PENSION_TRABAJADOR", self.CERO), "IBC * porcentajePensionTrabajador"),
            ("FONDO_SOLIDARIDAD", fondo_solidaridad, ibc, calc_ded.obtener_porcentaje("PORCENTAJE_FONDO_SOLIDARIDAD", self.CERO), "IBC * porcentajeFondoSolidaridad"),
            ("RETENCION_FUENTE", retencion, ibc, calc_ded.obtener_porcentaje("PORCENTAJE_RETENCION_FUENTE", self.CERO), "IBC * porcentajeRetencionFuente"),
            ("DESCUENTO_INCUMPLIMIENTO", descuento_incumplimiento, descuento_incumplimiento, None, "horasIncumplidas * valorHoraIncumplida"),
            ("APORTE_SALUD_PATRONAL", aporte_salud, ibc, calc_ded.obtener_porcentaje("PORCENTAJE_SALUD_EMPLEADOR", self.CERO), "IBC * porcentajeSaludEmpleador"),
            ("APORTE_PENSION_PATRONAL", aporte_pension, ibc, calc_ded.obtener_porcentaje("PORCENTAJE_PENSION_EMPLEADOR", self.CERO), "IBC * porcentajePensionEmpleador"),
            ("APORTE_ARL", aporte_arl, ibc, None, "IBC * porcentajeARL"),
            ("APORTE_CAJA", aporte_caja, ibc, calc_ded.obtener_porcentaje("PORCENTAJE_CAJA_COMPENSACION", self.CERO), "IBC * porcentajeCajaCompensacion"),
            ("APORTE_SENA", aporte_sena, ibc, calc_ded.obtener_porcentaje("PORCENTAJE_SENA", self.CERO), "IBC * porcentajeSENA"),
            ("APORTE_ICBF", aporte_icbf, ibc, calc_ded.obtener_porcentaje("PORCENTAJE_ICBF", self.CERO), "IBC * porcentajeICBF"),
        )
        for codigo, valor, base, porcentaje, formula in conceptos:
            self.gestor.detalles_liquidacion.append(DetalleLiquidacion(
                idDetalleLiquidacion=max((item.idDetalleLiquidacion or 0 for item in self.gestor.detalles_liquidacion), default=0) + 1,
                idLiquidacion=liquidacion.idLiquidacion,
                cantidad=Decimal("1"), baseCalculo=self.gestor._redondear(base),
                porcentajeAplicado=porcentaje, valorCalculado=self.gestor._redondear(valor),
                valorDefinitivo=self.gestor._redondear(valor), tipoMovimiento=codigo,
                observaciones=codigo.replace("_", " ").title(),
                periodoCausacion=str(periodo.idPeriodoNomina), formulaAplicada=formula,
                fechaRegistro=date.today(), esSalarial=codigo == "SALARIO_ORDINARIO",
                integraSeguridadSocial=codigo in {"SALARIO_ORDINARIO"},
                integraPrestaciones=codigo in {"SALARIO_ORDINARIO", "AUXILIO_TRANSPORTE"},
                integraParafiscales=codigo == "SALARIO_ORDINARIO",
            ))


class LiquidadorOcasional(MotorLiquidacionBase):
    """Liquidación de profesores ocasionales según Acuerdo 027/2024."""

    def liquidar(
        self,
        id_contrato: int,
        id_periodo_nomina: int,
        *,
        horas_incumplidas: Decimal | None = None,
        fecha_liquidacion: date | None = None,
    ) -> LiquidacionNomina:
        contrato = self.gestor._contrato(id_contrato)
        periodo = self.gestor._periodo(id_periodo_nomina)
        self.gestor._validar_periodo_abierto(periodo)
        self.gestor._evitar_liquidacion_duplicada(id_contrato, id_periodo_nomina)
        profesor = self.gestor._profesor(contrato.idPersona)
        self.gestor._validar_contrato(contrato, TipoProfesor.OCASIONAL, periodo)

        salario_minimo = self.gestor._salario_minimo(contrato, periodo)
        factor = contrato.factorSalarialSMMLV
        if factor is None or factor == self.CERO:
            if contrato.salarioBase and salario_minimo > self.CERO:
                factor = (self.gestor._decimal(contrato.salarioBase, "salario base") / salario_minimo).quantize(Decimal("0.01"))
            else:
                factor = Decimal("2.5")
        factor = self.gestor._decimal(factor, "factor salarial del contrato")
        salario_base = contrato.salarioBase or (salario_minimo * factor)
        horas_no_cumplidas = self.gestor._decimal(
            (contrato.horasIncumplidas if horas_incumplidas is None else horas_incumplidas) or self.CERO,
            "horas incumplidas",
        )
        self.gestor._validar_horas_incumplidas(contrato, horas_no_cumplidas)
        valor_hora_incumplida = self.gestor._decimal(contrato.valorHoraIncumplida or self.CERO, "valor de hora incumplida")
        descuento_incumplimiento = horas_no_cumplidas * valor_hora_incumplida
        salario_ordinario = salario_base
        ibc = salario_ordinario - descuento_incumplimiento

        return self._ensamblar_liquidacion(
            contrato=contrato,
            profesor=profesor,
            periodo=periodo,
            fecha_liquidacion=fecha_liquidacion,
            salario_base=salario_base,
            salario_ordinario=salario_ordinario,
            ibc=ibc,
            horas_asignadas=contrato.horasSemanalesAsignadas,
            horas_cumplidas=None,
            horas_incumplidas=horas_no_cumplidas,
            descuento_incumplimiento=descuento_incumplimiento,
            tipo=TipoProfesor.OCASIONAL,
        )


class LiquidadorPlanta(MotorLiquidacionBase):
    """Liquidación de profesores de planta según Decreto 1279/2002."""

    def liquidar(
        self,
        id_contrato: int,
        id_periodo_nomina: int,
        *,
        fecha_liquidacion: date | None = None,
    ) -> LiquidacionNomina:
        contrato = self.gestor._contrato(id_contrato)
        periodo = self.gestor._periodo(id_periodo_nomina)
        self.gestor._validar_periodo_abierto(periodo)
        self.gestor._evitar_liquidacion_duplicada(id_contrato, id_periodo_nomina)
        profesor = self.gestor._profesor(contrato.idPersona)
        self.gestor._validar_contrato(contrato, TipoProfesor.PLANTA, periodo)

        puntos = self.gestor._puntos_planta(profesor, periodo)
        valor_punto = self.gestor._decimal(
            periodo.valorPuntoSalarialVigente or self.gestor._parametro_decimal("VALOR_PUNTO_SALARIAL"),
            "valor del punto salarial vigente",
        )
        factor_dedicacion = {
            Dedicacion.TIEMPO_COMPLETO.value: Decimal("1"),
            Dedicacion.MEDIO_TIEMPO.value: Decimal("0.5"),
        }.get(self.gestor._valor_enum(contrato.dedicacion or contrato.tipoDedicacion), None)
        if factor_dedicacion is None:
            raise ErrorNomina("La dedicación de planta debe ser tiempo completo o medio tiempo")

        salario_base = puntos * valor_punto * factor_dedicacion
        liquidacion = self._ensamblar_liquidacion(
            contrato=contrato,
            profesor=profesor,
            periodo=periodo,
            fecha_liquidacion=fecha_liquidacion,
            salario_base=salario_base,
            salario_ordinario=salario_base,
            ibc=salario_base,
            horas_asignadas=contrato.horasSemanalesAsignadas,
            horas_cumplidas=None,
            horas_incumplidas=self.CERO,
            descuento_incumplimiento=self.CERO,
            tipo=TipoProfesor.PLANTA,
            incluir_bonificaciones=False,
        )
        liquidacion.valorPuntoUsado = valor_punto
        liquidacion.puntosSalarialesUsados = puntos
        return liquidacion


class LiquidadorCatedratico(MotorLiquidacionBase):
    """Liquidación de profesores catedráticos según Acuerdo 027/2024."""

    def liquidar(
        self,
        id_contrato: int,
        id_periodo_nomina: int,
        *,
        fecha_liquidacion: date | None = None,
    ) -> LiquidacionNomina:
        contrato = self.gestor._contrato(id_contrato)
        periodo = self.gestor._periodo(id_periodo_nomina)
        self.gestor._validar_periodo_abierto(periodo)
        self.gestor._evitar_liquidacion_duplicada(id_contrato, id_periodo_nomina)
        profesor = self.gestor._profesor(contrato.idPersona)
        self.gestor._validar_contrato(contrato, TipoProfesor.CATEDRATICO, periodo)

        horas_semanales = contrato.horasSemanales or contrato.horasSemanalesAsignadas or Decimal("12")
        horas_asignadas = self.gestor._decimal(
            contrato.horasMensualesAsignadas or (horas_semanales * Decimal("4")),
            "horas mensuales asignadas",
        )
        horas_cumplidas = self.gestor._decimal(
            contrato.horasMensualesCumplidas or horas_asignadas,
            "horas mensuales cumplidas",
        )
        horas_pagables = min(horas_asignadas, horas_cumplidas)
        valor_hora = contrato.valorHoraCatedraVigente or contrato.valorHora
        if valor_hora is None or valor_hora == self.CERO:
            if contrato.salarioBase and horas_pagables > self.CERO:
                valor_hora = (self.gestor._decimal(contrato.salarioBase, "salario base") / horas_pagables).quantize(Decimal("1"))
            else:
                valor_hora = self.gestor._parametro_decimal("VALOR_HORA_CATEDRA") or Decimal("38500")
        valor_hora = self.gestor._decimal(valor_hora, "valor vigente de la hora cátedra")

        modalidad = str(getattr(contrato.modalidadProfesor or contrato.tipoContrato or "", "value", contrato.modalidadProfesor or contrato.tipoContrato or "")).upper()
        es_ad_honorem = contrato.esAdHonorem is True or "AD_HONOREM" in modalidad
        salario_base = self.CERO if es_ad_honorem else (contrato.salarioBase or (horas_pagables * valor_hora))

        return self._ensamblar_liquidacion(
            contrato=contrato,
            profesor=profesor,
            periodo=periodo,
            fecha_liquidacion=fecha_liquidacion,
            salario_base=salario_base,
            salario_ordinario=salario_base,
            ibc=salario_base,
            horas_asignadas=horas_asignadas,
            horas_cumplidas=horas_cumplidas,
            horas_incumplidas=self.CERO,
            descuento_incumplimiento=self.CERO,
            tipo=TipoProfesor.CATEDRATICO,
            horas_pagables=horas_pagables,
            es_ad_honorem=es_ad_honorem,
        )
