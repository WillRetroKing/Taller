from __future__ import annotations

from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Iterable

from modelo_datos import (
    CategoriaDocente,
    Contrato,
    Dedicacion,
    DetalleLiquidacion,
    FactorSalarial,
    LiquidacionNomina,
    ParametroNormativo,
    PeriodoNomina,
    ProduccionAcademica,
    Profesor,
    TipoProfesor,
)


class ErrorNomina(ValueError):
    """Error en una liquidación de nómina."""


class GestorNomina:
    """Liquida docentes ocasionales y catedráticos según el modelo PITA."""

    CERO = Decimal("0")
    DIEZ = Decimal("10")
    DOS = Decimal("2")
    CUATRO = Decimal("4")
    DIAS_MES = Decimal("30")
    DIAS_ANIO = Decimal("360")

    def __init__(
        self,
        contratos: list[Contrato],
        profesores: list[Profesor],
        periodos_nomina: list[PeriodoNomina],
        liquidaciones: list[LiquidacionNomina] | None = None,
        parametros: list[ParametroNormativo] | None = None,
        detalles_liquidacion: list[DetalleLiquidacion] | None = None,
        categorias: list[CategoriaDocente] | None = None,
        factores: list[FactorSalarial] | None = None,
        producciones: list[ProduccionAcademica] | None = None,
    ) -> None:
        self.contratos = contratos
        self.profesores = profesores
        self.periodos_nomina = periodos_nomina
        self.liquidaciones = liquidaciones if liquidaciones is not None else []
        self.parametros = parametros if parametros is not None else []
        self.detalles_liquidacion = detalles_liquidacion if detalles_liquidacion is not None else []
        self.categorias = categorias if categorias is not None else []
        self.factores = factores if factores is not None else []
        self.producciones = producciones if producciones is not None else []

    def liquidarProfesorOcasional(
        self,
        id_contrato: int,
        id_periodo_nomina: int,
        *,
        horas_incumplidas: Decimal | None = None,
        fecha_liquidacion: date | None = None,
    ) -> LiquidacionNomina:
        contrato = self._contrato(id_contrato)
        periodo = self._periodo(id_periodo_nomina)
        self._validar_periodo_abierto(periodo)
        self._evitar_liquidacion_duplicada(id_contrato, id_periodo_nomina)
        profesor = self._profesor(contrato.idPersona)
        self._validar_contrato(contrato, TipoProfesor.OCASIONAL, periodo)

        salario_minimo = self._salario_minimo(contrato, periodo)
        factor = self._decimal(contrato.factorSalarialSMMLV, "factor salarial del contrato")
        salario_base = salario_minimo * factor
        horas_no_cumplidas = self._decimal(
            (contrato.horasIncumplidas if horas_incumplidas is None else horas_incumplidas) or self.CERO,
            "horas incumplidas",
        )
        self._validar_horas_incumplidas(contrato, horas_no_cumplidas)
        valor_hora_incumplida = self._decimal(contrato.valorHoraIncumplida or self.CERO, "valor de hora incumplida")
        descuento_incumplimiento = horas_no_cumplidas * valor_hora_incumplida
        salario_ordinario = salario_base
        ibc = salario_ordinario - descuento_incumplimiento
        return self._crear_liquidacion(
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

    def liquidarProfesorPlanta(
        self,
        id_contrato: int,
        id_periodo_nomina: int,
        *,
        fecha_liquidacion: date | None = None,
    ) -> LiquidacionNomina:
        contrato = self._contrato(id_contrato)
        periodo = self._periodo(id_periodo_nomina)
        self._validar_periodo_abierto(periodo)
        self._evitar_liquidacion_duplicada(id_contrato, id_periodo_nomina)
        profesor = self._profesor(contrato.idPersona)
        self._validar_contrato(contrato, TipoProfesor.PLANTA, periodo)

        puntos = self._puntos_planta(profesor, periodo)
        valor_punto = self._decimal(
            periodo.valorPuntoSalarialVigente or self._parametro_decimal("VALOR_PUNTO_SALARIAL"),
            "valor del punto salarial vigente",
        )
        factor_dedicacion = {
            Dedicacion.TIEMPO_COMPLETO.value: Decimal("1"),
            Dedicacion.MEDIO_TIEMPO.value: Decimal("0.5"),
        }.get(self._valor_enum(contrato.dedicacion or contrato.tipoDedicacion), None)
        if factor_dedicacion is None:
            raise ErrorNomina("La dedicación de planta debe ser tiempo completo o medio tiempo")
        salario_base = puntos * valor_punto * factor_dedicacion
        liquidacion = self._crear_liquidacion(
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

    def liquidarProfesorCatedratico(
        self,
        id_contrato: int,
        id_periodo_nomina: int,
        *,
        fecha_liquidacion: date | None = None,
    ) -> LiquidacionNomina:
        contrato = self._contrato(id_contrato)
        periodo = self._periodo(id_periodo_nomina)
        self._validar_periodo_abierto(periodo)
        self._evitar_liquidacion_duplicada(id_contrato, id_periodo_nomina)
        profesor = self._profesor(contrato.idPersona)
        self._validar_contrato(contrato, TipoProfesor.CATEDRATICO, periodo)

        horas_asignadas = self._decimal(contrato.horasMensualesAsignadas, "horas mensuales asignadas")
        horas_cumplidas = self._decimal(contrato.horasMensualesCumplidas, "horas mensuales cumplidas")
        horas_pagables = min(horas_asignadas, horas_cumplidas)
        valor_hora = self._decimal(
            contrato.valorHoraCatedraVigente,
            "valor vigente de la hora cátedra",
        )
        modalidad = getattr(contrato.modalidadProfesor, "value", contrato.modalidadProfesor)
        es_ad_honorem = contrato.esAdHonorem is True or modalidad == TipoProfesor.CATEDRATICO_AD_HONOREM.value
        salario_base = self.CERO if es_ad_honorem else horas_pagables * valor_hora
        return self._crear_liquidacion(
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

    def _crear_liquidacion(
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
        fecha_parametros = periodo.fechaFin or periodo.fechaInicio or date.today()

        # Registrar códigos de parámetros utilizados (para auditoría y trazabilidad)
        codigos_utilizados: dict[str, str] = {}

        salario_minimo = self._salario_minimo(contrato, periodo, fecha_parametros, codigos_utilizados)
        auxilio = self._auxilio_transporte(contrato, salario_ordinario, salario_minimo, fecha_parametros, codigos_utilizados)
        base_prestacional = ibc + auxilio
        bonificacion_posgrado = self._bonificacion_posgrado(profesor, salario_minimo, contrato, horas_pagables, incluir_bonificaciones, codigos_utilizados) if incluir_bonificaciones else self.CERO
        bonificacion_investigacion = self._bonificacion_investigacion(profesor, salario_minimo, contrato, horas_pagables, incluir_bonificaciones, codigos_utilizados) if incluir_bonificaciones else self.CERO
        salud_trabajador = self._porcentaje("PORCENTAJE_SALUD_TRABAJADOR", Decimal("0.04"), fecha_parametros, codigos_utilizados)
        pension_trabajador = self._porcentaje("PORCENTAJE_PENSION_TRABAJADOR", Decimal("0.04"), fecha_parametros, codigos_utilizados)
        salud_empleador = self._porcentaje("PORCENTAJE_SALUD_EMPLEADOR", Decimal("0.085"), fecha_parametros, codigos_utilizados)
        pension_empleador = self._porcentaje("PORCENTAJE_PENSION_EMPLEADOR", Decimal("0.12"), fecha_parametros, codigos_utilizados)
        sena = self._porcentaje("PORCENTAJE_SENA", Decimal("0.02"), fecha_parametros, codigos_utilizados)
        icbf = self._porcentaje("PORCENTAJE_ICBF", Decimal("0.03"), fecha_parametros, codigos_utilizados)
        arl = self._porcentaje(f"PORCENTAJE_ARL_CLASE_{str(contrato.claseARL or 'I').upper()}", Decimal("0.00522"), fecha_parametros, codigos_utilizados)
        caja = self._porcentaje("PORCENTAJE_CAJA_COMPENSACION", Decimal("0.04"), fecha_parametros, codigos_utilizados)
        descuento_salud = self._redondear(ibc * salud_trabajador)
        descuento_pension = self._redondear(ibc * pension_trabajador)
        exonerado = ibc < self.DIEZ * salario_minimo
        aporte_salud = self.CERO if exonerado else self._redondear(ibc * salud_empleador)
        aporte_sena = self.CERO if exonerado else self._redondear(ibc * sena)
        aporte_icbf = self.CERO if exonerado else self._redondear(ibc * icbf)
        aporte_pension = self._redondear(ibc * pension_empleador)
        aporte_arl = self._redondear(ibc * arl)
        aporte_caja = self._redondear(ibc * caja)
        fondo_solidaridad = self._redondear(
            ibc * self._porcentaje("PORCENTAJE_FONDO_SOLIDARIDAD", self.CERO, fecha_parametros, codigos_utilizados)
        ) if ibc >= self.CUATRO * salario_minimo else self.CERO
        # Retención con configuración personalizable (puede recibir parámetros desde la UI o configuración)
        parametros_retencion = None  # Aquí podrían pasar valores personalizados desde la configuración
        retencion = self._retencion_fuente(ibc, fecha_parametros, codigos_utilizados=codigos_utilizados, parametros_personalizados=parametros_retencion)
        dias = self._decimal(periodo.diasBaseLiquidacion or 30, "días base de liquidación")
        regimen_especial = tipo == TipoProfesor.PLANTA and self._es_regimen_1279(contrato.regimenAplicable)
        provisiones = self._provisiones(base_prestacional, ibc, dias, regimen_especial=regimen_especial)
        bonificaciones = bonificacion_posgrado + bonificacion_investigacion
        total_descuentos = descuento_salud + descuento_pension + fondo_solidaridad + retencion + descuento_incumplimiento
        total_devengado = salario_ordinario + auxilio + bonificaciones
        total_prestaciones = sum(provisiones.values(), self.CERO)
        neto = total_devengado - total_descuentos
        liquidacion = LiquidacionNomina(
            idLiquidacion=self._siguiente_id(), idProfesor=profesor.idProfesor,
            idContrato=contrato.idContrato, idPeriodoNomina=periodo.idPeriodoNomina,
            fechaLiquidacion=fecha_liquidacion or date.today(), salarioBase=salario_base,
            totalDevengado=self._redondear(total_devengado), totalDescuentos=self._redondear(total_descuentos),
            totalPrestaciones=self._redondear(total_prestaciones), baseLiquidacionPrestaciones=self._redondear(base_prestacional),
            baseCotizacionSeguridadSocial=self._redondear(ibc), valorAuxilioTransporteCotizado=self._redondear(auxilio),
            aportePatronalSENA=self._redondear(aporte_sena), aportePatronalICBF=self._redondear(aporte_icbf),
            netoPagar=self._redondear(neto), estado="PROCESADA", tipoProfesorLiquidado=tipo,
            regimenLiquidado=contrato.regimenAplicable, dedicacionLiquidada=contrato.dedicacion,
            diasTrabajados=dias, horasAsignadas=horas_asignadas, horasCumplidas=horas_cumplidas,
            horasIncumplidas=horas_incumplidas, salarioMinimoUsado=salario_minimo,
            valorHoraCatedraUsado=contrato.valorHoraCatedraVigente, factorCategoriaUsado=contrato.factorSalarialSMMLV,
            salarioOrdinario=self._redondear(salario_ordinario), baseSalarialPrestacional=self._redondear(base_prestacional),
            baseSeguridadSocial=self._redondear(ibc), bonificacionPosgrado=self._redondear(bonificacion_posgrado),
            bonificacionInvestigacion=self._redondear(bonificacion_investigacion), bonificacionesNoSalariales=self._redondear(bonificaciones),
            descuentoSalud=descuento_salud, descuentoPension=descuento_pension,
            fondoSolidaridadPensional=fondo_solidaridad, retencionFuente=retencion,
            descuentoHorasIncumplidas=self._redondear(descuento_incumplimiento),
            provisionCesantias=provisiones["cesantias"], provisionInteresesCesantias=provisiones["intereses"],
            provisionPrimaServicios=provisiones["prima_servicios"], provisionPrimaNavidad=provisiones["prima_navidad"],
            provisionVacaciones=provisiones["vacaciones"], provisionPrimaVacaciones=provisiones["prima_vacaciones"],
            bonificacionServiciosPrestados=provisiones["bonificacion_servicios"], aportePatronalSalud=self._redondear(aporte_salud),
            aportePatronalPension=aporte_pension, aporteRiesgosLaborales=aporte_arl,
            aporteCajaCompensacion=aporte_caja,
            costoTotalEmpleador=self._redondear(total_devengado + total_prestaciones + aporte_salud + aporte_pension + aporte_arl + aporte_sena + aporte_icbf + aporte_caja),
            parametros_utilizados=codigos_utilizados if codigos_utilizados else None,
        )
        self.liquidaciones.append(liquidacion)
        self._crear_detalles(liquidacion, periodo, ibc, salario_ordinario, auxilio, bonificacion_posgrado, bonificacion_investigacion, descuento_salud, descuento_pension, fondo_solidaridad, retencion, descuento_incumplimiento, aporte_salud, aporte_pension, aporte_arl, aporte_caja, aporte_sena, aporte_icbf, codigos_utilizados)
        return liquidacion

    def _crear_detalles(
        self, liquidacion: LiquidacionNomina, periodo: PeriodoNomina, ibc: Decimal,
        salario_ordinario: Decimal, auxilio: Decimal, bonificacion_posgrado: Decimal,
        bonificacion_investigacion: Decimal, descuento_salud: Decimal,
        descuento_pension: Decimal, fondo_solidaridad: Decimal, retencion: Decimal,
        descuento_incumplimiento: Decimal, aporte_salud: Decimal,
        aporte_pension: Decimal, aporte_arl: Decimal, aporte_caja: Decimal,
        aporte_sena: Decimal, aporte_icbf: Decimal, codigos_utilizados: dict | None = None,
    ) -> None:
        conceptos = (
            ("SALARIO_ORDINARIO", salario_ordinario, ibc, None, "salarioOrdinario = IBC"),
            ("AUXILIO_TRANSPORTE", auxilio, self.CERO, None, "auxilio según salario y SMMLV"),
            ("BONIFICACION_POSGRADO", bonificacion_posgrado, self.CERO, None, "SMMLV * factorPosgrado"),
            ("BONIFICACION_INVESTIGACION", bonificacion_investigacion, self.CERO, None, "SMMLV * factorInvestigacion"),
            ("DESCUENTO_SALUD", descuento_salud, ibc, self._porcentaje("PORCENTAJE_SALUD_TRABAJADOR", self.CERO, codigos_utilizados=codigos_utilizados), "IBC * porcentajeSaludTrabajador"),
            ("DESCUENTO_PENSION", descuento_pension, ibc, self._porcentaje("PORCENTAJE_PENSION_TRABAJADOR", self.CERO), "IBC * porcentajePensionTrabajador"),
            ("FONDO_SOLIDARIDAD", fondo_solidaridad, ibc, self._porcentaje("PORCENTAJE_FONDO_SOLIDARIDAD", self.CERO), "IBC * porcentajeFondoSolidaridad"),
            ("RETENCION_FUENTE", retencion, ibc, self._porcentaje("PORCENTAJE_RETENCION_FUENTE", self.CERO), "IBC * porcentajeRetencionFuente"),
            ("DESCUENTO_INCUMPLIMIENTO", descuento_incumplimiento, descuento_incumplimiento, None, "horasIncumplidas * valorHoraIncumplida"),
            ("APORTE_SALUD_PATRONAL", aporte_salud, ibc, self._porcentaje("PORCENTAJE_SALUD_EMPLEADOR", self.CERO), "IBC * porcentajeSaludEmpleador"),
            ("APORTE_PENSION_PATRONAL", aporte_pension, ibc, self._porcentaje("PORCENTAJE_PENSION_EMPLEADOR", self.CERO), "IBC * porcentajePensionEmpleador"),
            ("APORTE_ARL", aporte_arl, ibc, None, "IBC * porcentajeARL"),
            ("APORTE_CAJA", aporte_caja, ibc, self._porcentaje("PORCENTAJE_CAJA_COMPENSACION", self.CERO), "IBC * porcentajeCajaCompensacion"),
            ("APORTE_SENA", aporte_sena, ibc, self._porcentaje("PORCENTAJE_SENA", self.CERO), "IBC * porcentajeSENA"),
            ("APORTE_ICBF", aporte_icbf, ibc, self._porcentaje("PORCENTAJE_ICBF", self.CERO), "IBC * porcentajeICBF"),
        )
        for codigo, valor, base, porcentaje, formula in conceptos:
            self.detalles_liquidacion.append(DetalleLiquidacion(
                idDetalleLiquidacion=max((item.idDetalleLiquidacion or 0 for item in self.detalles_liquidacion), default=0) + 1,
                idLiquidacion=liquidacion.idLiquidacion,
                cantidad=Decimal("1"), baseCalculo=self._redondear(base),
                porcentajeAplicado=porcentaje, valorCalculado=self._redondear(valor),
                valorDefinitivo=self._redondear(valor), tipoMovimiento=codigo,
                periodoCausacion=str(periodo.idPeriodoNomina), formulaAplicada=formula,
                fechaRegistro=date.today(), esSalarial=codigo == "SALARIO_ORDINARIO",
                integraSeguridadSocial=codigo in {"SALARIO_ORDINARIO"},
                integraPrestaciones=codigo in {"SALARIO_ORDINARIO", "AUXILIO_TRANSPORTE"},
                integraParafiscales=codigo == "SALARIO_ORDINARIO",
            ))

    def crear_periodo_nomina(self, periodo: PeriodoNomina) -> PeriodoNomina:
        if periodo.idPeriodoNomina is None:
            periodo.idPeriodoNomina = max(
                (item.idPeriodoNomina or 0 for item in self.periodos_nomina), default=0
            ) + 1
        if any(item.idPeriodoNomina == periodo.idPeriodoNomina for item in self.periodos_nomina):
            raise ErrorNomina(f"Ya existe el periodo de nómina {periodo.idPeriodoNomina}")
        if periodo.fechaInicio and periodo.fechaFin and periodo.fechaFin < periodo.fechaInicio:
            raise ErrorNomina("La fecha final no puede preceder a la fecha inicial")
        periodo.estaCerrado = False
        periodo.estado = periodo.estado or "ABIERTO"
        self.periodos_nomina.append(periodo)
        return periodo

    def abrir_periodo_nomina(self, id_periodo_nomina: int) -> PeriodoNomina:
        periodo = self._periodo(id_periodo_nomina)
        if periodo.estaCerrado:
            raise ErrorNomina("Un periodo cerrado no puede reabrirse")
        periodo.estado = "ABIERTO"
        return periodo

    def cerrar_periodo_nomina(self, id_periodo_nomina: int) -> PeriodoNomina:
        periodo = self._periodo(id_periodo_nomina)
        if periodo.estaCerrado:
            raise ErrorNomina("El periodo ya está cerrado")
        periodo.totalDevengadoPeriodo = self._total_periodo(periodo.idPeriodoNomina, "totalDevengado")
        periodo.totalDescuentosPeriodo = self._total_periodo(periodo.idPeriodoNomina, "totalDescuentos")
        periodo.totalPrestacionesPeriodo = self._total_periodo(periodo.idPeriodoNomina, "totalPrestaciones")
        periodo.totalAportesPatronalesPeriodo = sum(
            (self._aportes(liquidacion) for liquidacion in self._liquidaciones_periodo(periodo.idPeriodoNomina)),
            self.CERO,
        )
        periodo.costoTotalPeriodo = self._total_periodo(periodo.idPeriodoNomina, "costoTotalEmpleador")
        periodo.estaCerrado = True
        periodo.estado = "CERRADO"
        return periodo

    def aprobar_liquidacion(self, id_liquidacion: int, usuario: str) -> LiquidacionNomina:
        liquidacion = self._liquidacion(id_liquidacion)
        periodo = self._periodo(liquidacion.idPeriodoNomina)
        if periodo.estaCerrado:
            raise ErrorNomina("No se puede aprobar una liquidación de un periodo cerrado")
        if not usuario.strip():
            raise ErrorNomina("El usuario aprobador es obligatorio")
        liquidacion.aprobada = True
        liquidacion.fechaAprobacion = date.today()
        liquidacion.usuarioAprobador = usuario.strip()
        liquidacion.estado = "APROBADA"
        return liquidacion

    def pagar_liquidacion(self, id_liquidacion: int, medio_pago: str, referencia: str) -> LiquidacionNomina:
        liquidacion = self._liquidacion(id_liquidacion)
        periodo = self._periodo(liquidacion.idPeriodoNomina)
        self._validar_periodo_abierto(periodo)
        if not liquidacion.aprobada:
            raise ErrorNomina("Solo se puede pagar una liquidación aprobada")
        if not medio_pago.strip() or not referencia.strip():
            raise ErrorNomina("Medio y referencia de pago son obligatorios")
        liquidacion.pagada = True
        liquidacion.fechaPago = date.today()
        liquidacion.medioPago = medio_pago.strip()
        liquidacion.referenciaPago = referencia.strip()
        liquidacion.estado = "PAGADA"
        return liquidacion

    def consultar_liquidaciones(self, id_profesor: int | None = None, id_periodo_nomina: int | None = None) -> list[LiquidacionNomina]:
        return [
            liquidacion for liquidacion in self.liquidaciones
            if (id_profesor is None or liquidacion.idProfesor == id_profesor)
            and (id_periodo_nomina is None or liquidacion.idPeriodoNomina == id_periodo_nomina)
        ]

    def crear_liquidacion(self, liquidacion: LiquidacionNomina) -> LiquidacionNomina:
        """Crear una nueva liquidación con validación de duplicados.

        Valida que no exista una liquidación activa para el mismo contrato y periodo.
        Si la liquidación ya fue pagada o está en historial, se levanta error.
        """
        # Validar que el contrato y periodo existan
        contrato = self._contrato(liquidacion.idContrato)
        periodo = self._periodo(liquidacion.idPeriodoNomina)
        self._validar_periodo_abierto(periodo)
        self._evitar_liquidacion_duplicada(liquidacion.idContrato, liquidacion.idPeriodoNomina)

        # Validar que el profesor exista en el contrato
        profesor = self._profesor(contrato.idPersona)

        # Ejecutar la liquidación (usar el método apropiado según el tipo de profesor)
        tipo = getattr(contrato, "modalidadProfesor", None)
        tipo = str(getattr(tipo, "value", tipo or "")).upper()

        if tipo == "OCASIONAL" or (tipo and "OCASIONAL" in tipo):
            resultado = self.liquidarProfesorOcasional(
                liquidacion.idContrato, liquidacion.idPeriodoNomina,
                horas_incumplidas=liquidacion.horasIncumplidas or Decimal("0"),
            )
        elif tipo == "PLANTA" or (tipo and "PLANTA" in tipo):
            resultado = self.liquidarProfesorPlanta(
                liquidacion.idContrato, liquidacion.idPeriodoNomina,
            )
        elif tipo == "CATEDRATICO" or (tipo and "CATEDRATICO" in tipo):
            resultado = self.liquidarProfesorCatedratico(
                liquidacion.idContrato, liquidacion.idPeriodoNomina,
            )
        else:
            # Default: intentar liquidar según el tipo de contrato detectado
            resultado = self.liquidarProfesorOcasional(
                liquidacion.idContrato, liquidacion.idPeriodoNomina,
                horas_incumplidas=liquidacion.horasIncumplidas or Decimal("0"),
            )

        # Copiar los campos de la liquidación solicitada a la resultado
        resultado.fechaLiquidacion = liquidacion.fechaLiquidacion or date.today()
        resultado.estado = liquidacion.estado or "PROCESADA"

        self.liquidaciones.append(resultado)
        return resultado

    def modificar_liquidacion(self, id_liquidacion: int, **cambios: Any) -> LiquidacionNomina:
        """Modificar una liquidación existente.

        No permite modificar liquidaciones que ya fueron pagadas o tienen historial.
        Solo permite cambiar campos que no afecten el historial contable.
        """
        liquidacion = self._liquidacion(id_liquidacion)

        # Verificar si la liquidación tiene historial (fue reliquidada o pagada)
        if liquidacion.pagada:
            raise ErrorNomina("No se puede modificar una liquidación ya pagada")
        if liquidacion.requiereReliquidacion:
            raise ErrorNomina("No se puede modificar una liquidación que fue reliquidada")

        # Verificar si tiene historial (fue versionada)
        if self.tiene_historial_liquidacion(liquidacion):
            raise ErrorNomina("No se puede modificar directamente una liquidación con historial")

        # Campos permitidos para modificación
        campos_permitidos = {
            "fechaLiquidacion", "observaciones", "usuarioAprobador",
            "aprobada", "requiereReliquidacion", "motivoReliquidacion",
        }

        # Validar que los campos solicitados sean permitidos
        desconocidos = set(cambios) - campos_permitidos
        if desconocidos:
            raise ErrorNomina(f"Campos no válidos para modificación: {', '.join(sorted(desconocidos))}")

        # Aplicar los cambios
        for campo, valor in cambios.items():
            setattr(liquidacion, campo, valor)

        return liquidacion

    def desactivar_liquidacion(self, id_liquidacion: int) -> LiquidacionNomina:
        """Eliminación lógica: marcar liquidación como INACTIVA.

        En lugar de borrar la liquidación del historial, la marca como inactiva
        para mantener el registro contable y auditoría.
        """
        liquidacion = self._liquidacion(id_liquidacion)
        liquidacion.estado = "INACTIVO"
        liquidacion.fechaGeneracion = date.today()
        return liquidacion

    def reactivar_liquidacion(self, id_liquidacion: int) -> LiquidacionNomina:
        """Reactivar una liquidación previamente inactivada."""
        liquidacion = self._liquidacion(id_liquidacion)
        liquidacion.estado = "PROCESADA"
        return liquidacion

    def eliminar_liquidacion(self, id_liquidacion: int) -> LiquidacionNomina:
        """Eliminar físicamente una liquidación.

        Solo permite eliminación si la liquidación no tiene historial (no fue
        reliquidada, pagada o versionada). Si tiene historial, usa eliminación lógica.
        """
        liquidacion = self._liquidacion(id_liquidacion)

        # Verificar si la liquidación tiene historial que la protege de eliminación
        if self.tiene_historial_liquidacion(liquidacion):
            # Usar eliminación lógica en lugar de física
            return self.desactivar_liquidacion(id_liquidacion)

        # Eliminación física: remover de la lista
        self.liquidaciones.remove(liquidacion)
        return liquidacion

    def tiene_historial_liquidacion(self, liquidacion: LiquidacionNomina) -> bool:
        """Verificar si una liquidación tiene historial que la protege de modificaciones."""
        # Tiene historial si fue reliquidada, pagada o versionada
        return (
            liquidacion.pagada
            or liquidacion.requiereReliquidacion
            or (liquidacion.version is not None and liquidacion.version > 0)
            or liquidacion.estado == "RELIQUIDADA"
        )

    def _porcentaje(self, codigo: str, defecto: Decimal, fecha: date | None = None, codigos_utilizados: dict | None = None) -> Decimal:
        if periodo.estaCerrado or str(periodo.estado or "").upper() == "CERRADO":
            raise ErrorNomina("El periodo de nómina está cerrado")

    def _validar_periodo_abierto(self, periodo: PeriodoNomina) -> None:
        if periodo.estaCerrado or str(periodo.estado or "").upper() == "CERRADO":
            raise ErrorNomina("El periodo de nómina está cerrado")

    def _evitar_liquidacion_duplicada(self, id_contrato: int, id_periodo_nomina: int) -> None:
        if any(
            item.idContrato == id_contrato and item.idPeriodoNomina == id_periodo_nomina
            and item.estado != "RELIQUIDADA"
            for item in self.liquidaciones
        ):
            raise ErrorNomina("Ya existe una liquidación para ese contrato y periodo")

    def _liquidacion(self, id_liquidacion: int) -> LiquidacionNomina:
        return self._buscar(self.liquidaciones, "idLiquidacion", id_liquidacion, "liquidación")

    def _liquidaciones_periodo(self, id_periodo_nomina: int | None) -> list[LiquidacionNomina]:
        return [item for item in self.liquidaciones if item.idPeriodoNomina == id_periodo_nomina]

    def _total_periodo(self, id_periodo_nomina: int | None, campo: str) -> Decimal:
        return self._redondear(sum((getattr(item, campo) or self.CERO for item in self._liquidaciones_periodo(id_periodo_nomina)), self.CERO))

    @staticmethod
    def _aportes(liquidacion: LiquidacionNomina) -> Decimal:
        campos = ("aportePatronalSalud", "aportePatronalPension", "aporteRiesgosLaborales", "aporteCajaCompensacion", "aportePatronalSENA", "aportePatronalICBF")
        return sum((getattr(liquidacion, campo) or Decimal("0") for campo in campos), Decimal("0"))

    def _bonificacion_posgrado(self, profesor: Profesor, smmlv: Decimal, contrato: Contrato, horas: Decimal | None, incluir_bonificaciones: bool, codigos_utilizados: dict | None = None) -> Decimal:
        if contrato.permiteBonificacionPosgrado is False:
            return self.CERO
        factores = {"ESPECIALIZACION": Decimal("0.10"), "MAESTRIA": Decimal("0.45"), "DOCTORADO": Decimal("0.90"), "POSTDOCTORADO": self.CERO}
        factor = factores.get(str(profesor.nivelPosgradoReconocido or "").upper(), self.CERO)
        if codigos_utilizados is not None:
            codigos_utilizados["BONIFICACION_POSGRADO"] = str(factor)
        return self._bonificacion_proporcional(smmlv * factor, contrato, horas) if incluir_bonificaciones else self.CERO

    def _bonificacion_investigacion(self, profesor: Profesor, smmlv: Decimal, contrato: Contrato, horas: Decimal | None, incluir_bonificaciones: bool, codigos_utilizados: dict | None = None) -> Decimal:
        if contrato.permiteBonificacionInvestigacion is False:
            return self.CERO
        grupo = str(profesor.categoriaGrupoInvestigacion or "").upper()
        factores = {"GRUPO_A1": Decimal("0.56"), "A1": Decimal("0.56"), "GRUPO_A": Decimal("0.47"), "A": Decimal("0.47"), "GRUPO_B": Decimal("0.42"), "B": Decimal("0.42"), "GRUPO_C": Decimal("0.38"), "C": Decimal("0.38"), "GRUPO_RECONOCIDO": Decimal("0.33"), "SEMILLERO": Decimal("0.20")}
        factor = factores.get(grupo, self.CERO)
        acreditada = bool(profesor.productividadInvestigativaVigente or profesor.participaProyectoInvestigacionVigente) and bool(profesor.certificacionVicerrectoriaInvestigacion)
        if codigos_utilizados is not None:
            codigos_utilizados["BONIFICACION_INVESTIGACION"] = str(factor) if factor else str(self.CERO)
        return self._bonificacion_proporcional(smmlv * factor if acreditada else self.CERO, contrato, horas) if incluir_bonificaciones else self.CERO

    def _bonificacion_proporcional(self, valor: Decimal, contrato: Contrato, horas: Decimal | None) -> Decimal:
        if horas is None or contrato.horasMensualesAsignadas in (None, 0):
            return valor
        return valor * horas / Decimal(contrato.horasMensualesAsignadas)

    def _puntos_planta(self, profesor: Profesor, periodo: PeriodoNomina) -> Decimal:
        """Obtiene puntos vigentes y conserva el dato histórico sin fuentes configuradas."""
        codigos_categoria = {str(profesor.categoriaDocente or "").upper(), str(profesor.categoriaReconocida or "").upper()}
        tiene_categoria = any(categoria.idCategoria == profesor.idCategoriaDocente or str(getattr(categoria.codigo, "value", categoria.codigo or "")).upper() in codigos_categoria for categoria in self.categorias)
        tiene_fuentes = tiene_categoria or any(factor.idProfesor == profesor.idProfesor for factor in self.factores) or any(produccion.idProfesor == profesor.idProfesor for produccion in self.producciones)
        if tiene_fuentes:
            from gestor_factores import GestorFactores
            fecha = periodo.fechaFin or periodo.fechaInicio or date.today()
            return GestorFactores(self.categorias, self.factores, self.producciones, self.profesores).calcular_puntos_profesor(profesor.idProfesor, fecha)
        return self._decimal(profesor.puntosSalariales, "puntos salariales del profesor")

    @staticmethod
    def _es_regimen_1279(regimen: str | None) -> bool:
        return "1279" in str(regimen or "").upper().replace(" ", "")

    def _provisiones(self, base_prestacional: Decimal, ibc: Decimal, dias: Decimal, *, regimen_especial: bool = False) -> dict[str, Decimal]:
        provisiones = {
            "cesantias": self._redondear(base_prestacional * dias / self.DIAS_ANIO),
            "intereses": self._redondear(base_prestacional * dias * Decimal("0.12") / self.DIAS_ANIO),
            "prima_servicios": self._redondear(base_prestacional * dias / self.DIAS_ANIO),
            "prima_navidad": self._redondear(base_prestacional * dias / self.DIAS_ANIO),
            "vacaciones": self._redondear(ibc * dias / Decimal("720")),
            "prima_vacaciones": self.CERO,
            "bonificacion_servicios": self.CERO,
        }
        if not regimen_especial:
            return provisiones
        # Bases especiales de los arts. 33, 39 y 46 del Decreto 1279.
        tope = self._parametro_decimal("TOPE_BONIFICACION_SERVICIOS") or Decimal("756411")
        porcentaje = self._porcentaje("PORCENTAJE_BONIFICACION_SERVICIOS_HASTA_TOPE", Decimal("0.50")) if ibc <= tope else self._porcentaje("PORCENTAJE_BONIFICACION_SERVICIOS_SOBRE_TOPE", Decimal("0.35"))
        provisiones["bonificacion_servicios"] = self._redondear(ibc * porcentaje * dias / self.DIAS_ANIO)
        base_vacaciones = ibc + provisiones["prima_servicios"] / Decimal("12") + provisiones["bonificacion_servicios"] / Decimal("12")
        base_prima_vacaciones = (ibc * Decimal("2") / Decimal("3")) + provisiones["prima_servicios"] / Decimal("12") + provisiones["bonificacion_servicios"] / Decimal("12")
        provisiones["vacaciones"] = self._redondear(base_vacaciones * dias / Decimal("720"))
        provisiones["prima_vacaciones"] = self._redondear(base_prima_vacaciones * dias / Decimal("540"))
        base_prima_navidad = ibc + provisiones["prima_servicios"] / Decimal("12") + provisiones["prima_vacaciones"] / Decimal("12") + provisiones["bonificacion_servicios"] / Decimal("12")
        provisiones["prima_navidad"] = self._redondear(base_prima_navidad * dias / self.DIAS_ANIO)
        return provisiones
    def _auxilio_transporte(self, contrato: Contrato, salario: Decimal, smmlv: Decimal, fecha: date | None = None, codigos_utilizados: dict | None = None) -> Decimal:
        if contrato.aplicaAuxilioTransporte and salario <= self.DOS * smmlv:
            valor = self._parametro_decimal("VALOR_AUXILIO_TRANSPORTE_VIGENTE", fecha)
            # Registrar código utilizado para trazabilidad si hay diccionario
            if codigos_utilizados is not None:
                codigos_utilizados["VALOR_AUXILIO_TRANSPORTE_VIGENTE"] = str(valor) if valor is not None else str(self.CERO)
            return valor or self.CERO
        return self.CERO

    def _salario_minimo(self, contrato: Contrato, periodo: PeriodoNomina, fecha: date | None = None, codigos_utilizados: dict | None = None) -> Decimal:
        # Registrar código utilizado para trazabilidad si se proporciona el diccionario
        if codigos_utilizados is not None:
            pass  # El código SALARIO_MINIMO se registra en el caller (_crear_liquidacion)
        return self._decimal(contrato.salarioMinimoVigente or periodo.salarioMinimoVigente or self._parametro_decimal("SALARIO_MINIMO", fecha), "salario mínimo vigente")

    def _porcentaje(self, codigo: str, defecto: Decimal, fecha: date | None = None, codigos_utilizados: dict | None = None) -> Decimal:
        valor = self._parametro_decimal(codigo, fecha)
        # Registrar el código utilizado para trazabilidad (si hay diccionario para llenar)
        if codigos_utilizados is not None:
            codigos_utilizados[codigo] = str(valor) if valor is not None else str(defecto)
        return valor if valor is not None else defecto

    def _retencion_fuente(self, ibc: Decimal, fecha: date, *, parametros_personalizados: dict | None = None, codigos_utilizados: dict | None = None) -> Decimal:
        """Calcular retención fuente con configuración personalizable.

        Args:
            ibc: Base de cotización sobre la cual se calcula la retención
            fecha: Fecha para consultar los parámetros vigentes
            parametros_personalizados: Diccionario opcional con claves 'base_minima' y 'porcentaje'
                para sobreescribir los parámetros consultados del sistema
            codigos_utilizados: Diccionario opcional para registrar códigos utilizados en trazabilidad

        La retención aplica cuando el IBC supera un mínimo exento. Si el IBC está por debajo,
        la retención es cero. El porcentaje se aplica sobre el IBC completo cuando supera el mínimo.
        """
        # Usar parámetros personalizados si se proporcionan
        if parametros_personalizados:
            base_minima = Decimal(parametros_personalizados.get('base_minima', self._parametro_decimal("BASE_MINIMA_RETENCION_FUENTE", fecha) or self.CERO))
            porcentaje = Decimal(parametros_personalizados.get('porcentaje', self._porcentaje("PORCENTAJE_RETENCION_FUENTE", self.CERO, fecha, codigos_utilizados)))
        else:
            base_minima = self._parametro_decimal("BASE_MINIMA_RETENCION_FUENTE", fecha) or self.CERO
            porcentaje = self._porcentaje("PORCENTAJE_RETENCION_FUENTE", self.CERO, fecha, codigos_utilizados)

        if ibc < base_minima:
            return self.CERO
        return self._redondear(ibc * porcentaje)

    @staticmethod
    def _valor_enum(valor: Any) -> str:
        return str(getattr(valor, "value", valor or "")).upper()

    def _parametro_decimal(self, codigo: str, fecha: date | None = None) -> Decimal | None:
        fecha_consulta = fecha or date.today()
        parametro = next((item for item in self.parametros if str(getattr(item.codigo, "value", item.codigo)) == codigo and self._parametro_activo(item, fecha_consulta)), None)
        return Decimal(parametro.valor) if parametro and parametro.valor else None

    @staticmethod
    def _parametro_activo(parametro: ParametroNormativo, fecha: date) -> bool:
        estado = str(getattr(parametro.estado, "value", parametro.estado or "ACTIVO")).upper()
        return estado == "ACTIVO" and (parametro.fechaInicioVigencia is None or parametro.fechaInicioVigencia <= fecha) and (parametro.fechaFinVigencia is None or fecha <= parametro.fechaFinVigencia)

    def _descuento_salud(self, ibc: Decimal) -> Decimal:
        """Calcular descuento salud trabajador (4% sobre IBC)."""
        return self._redondear(ibc * self._porcentaje("PORCENTAJE_SALUD_TRABAJADOR", Decimal("0.04")))

    def _descuento_pension(self, ibc: Decimal) -> Decimal:
        """Calcular descuento pension trabajador (4% sobre IBC)."""
        return self._redondear(ibc * self._porcentaje("PORCENTAJE_PENSION_TRABAJADOR", Decimal("0.04")))

    def _fondo_solidaridad(self, ibc: Decimal) -> Decimal:
        """Calcular fondo solidaridad pensional."""
        return self._redondear(
            ibc * self._porcentaje("PORCENTAJE_FONDO_SOLIDARIDAD", self.CERO)
        )

    def _aporte_salud_patronal(self, ibc: Decimal) -> Decimal:
        """Calcular aporte salud patronal (8.5% sobre IBC)."""
        return self._redondear(ibc * self._porcentaje("PORCENTAJE_SALUD_EMPLEADOR", Decimal("0.085")))

    def _aporte_pension_patronal(self, ibc: Decimal) -> Decimal:
        """Calcular aporte pension patronal (12% sobre IBC)."""
        return self._redondear(ibc * self._porcentaje("PORCENTAJE_PENSION_EMPLEADOR", Decimal("0.12")))

    def _aporte_arl(self, ibc: Decimal) -> Decimal:
        """Calcular aporte ARL (0.522% sobre IBC)."""
        return self._redondear(ibc * self._porcentaje("PORCENTAJE_ARL_CLASE_I", Decimal("0.00522")))

    def _aporte_caja_compensacion(self, ibc: Decimal) -> Decimal:
        """Calcular aporte caja compensación (4% sobre IBC)."""
        return self._redondear(ibc * self._porcentaje("PORCENTAJE_CAJA_COMPENSACION", Decimal("0.04")))

    def _aporte_sena_patronal(self, ibc: Decimal) -> Decimal:
        """Calcular aporte SENA patronal (2% sobre IBC)."""
        return self._redondear(ibc * self._porcentaje("PORCENTAJE_SENA", Decimal("0.02")))

    def _aporte_icbf_patronal(self, ibc: Decimal) -> Decimal:
        """Calcular aporte ICBF patronal (3% sobre IBC)."""
        return self._redondear(ibc * self._porcentaje("PORCENTAJE_ICBF", Decimal("0.03")))

    def _validar_contrato(self, contrato: Contrato, tipo: TipoProfesor, periodo: PeriodoNomina) -> None:
        actual = getattr(contrato.modalidadProfesor or contrato.tipoContrato or "", "value", contrato.modalidadProfesor or contrato.tipoContrato or "")
        actual = str(actual).upper()
        esperado = tipo.value
        if actual not in {esperado, TipoProfesor.CATEDRATICO_AD_HONOREM.value if tipo == TipoProfesor.CATEDRATICO else esperado}:
            raise ErrorNomina(f"El contrato no es de tipo {esperado}")
        if not self._activo(contrato.estado):
            raise ErrorNomina("El contrato no está activo")
        inicio_periodo = periodo.fechaInicio or periodo.fechaFin or date.today()
        fin_periodo = periodo.fechaFin or inicio_periodo
        if contrato.fechaInicio and contrato.fechaInicio > fin_periodo:
            raise ErrorNomina("El contrato inicia después del período de liquidación")
        if contrato.fechaFin and contrato.fechaFin < inicio_periodo:
            raise ErrorNomina("El contrato terminó antes del período de liquidación")

    def _validar_horas_incumplidas(self, contrato: Contrato, horas_incumplidas: Decimal) -> None:
        """Validar horas incumplidas con reglas basadas en el tipo de contrato.

        - Si requiere certificación y no tiene, error
        - Las horas incumplidas no pueden superar las horas mensuales asignadas
        - Para contratos de planta, se considera el tope semanal
        - Para ocasionales, se valida contra horas mensuales
        """
        if horas_incumplidas == self.CERO:
            return

        # Verificar certificación requerida
        if contrato.requiereCertificacionCumplimiento and not contrato.certificacionCumplimiento:
            raise ErrorNomina(
                "Las horas incumplidas requieren certificación de cumplimiento "
                "según el art. 87 del decreto sustantivo de la materia"
            )

        # Obtener horas asignadas (preferir semanales, luego mensuales)
        horas_semanales = contrato.horasSemanalesAsignadas or contrato.horasSemanales
        horas_mensuales_estimadas = (horas_semanales or self.CERO) * self.DIAS_MES / Decimal("7")

        # Validar que haya horas asignadas
        if horas_semanales is None or horas_semanales <= 0:
            raise ErrorNomina(
                "Se requieren horas asignadas para descontar incumplimientos "
                "en el contrato"
            )

        # Las horas incumplidas no pueden superar las horas mensuales asignadas/estimadas
        if horas_incumplidas > horas_mensuales_estimadas:
            raise ErrorNomina(
                f"Las horas incumplidas ({horas_incumplidas}) no pueden superar "
                f"las horas mensuales estimadas ({horas_mensuales_estimadas}) "
                f"basadas en {horas_semanales} horas semanales asignadas"
            )

    def _contrato(self, id_contrato: int) -> Contrato:
        return self._buscar(self.contratos, "idContrato", id_contrato, "contrato")

    def _periodo(self, id_periodo: int) -> PeriodoNomina:
        return self._buscar(self.periodos_nomina, "idPeriodoNomina", id_periodo, "periodo de nómina")

    def _profesor(self, id_persona: int | None) -> Profesor:
        return self._buscar(self.profesores, "idPersona", id_persona, "profesor")

    @staticmethod
    def _buscar(elementos: Iterable[Any], campo: str, valor: Any, nombre: str) -> Any:
        elemento = next((item for item in elementos if getattr(item, campo, None) == valor), None)
        if elemento is None:
            raise ErrorNomina(f"No existe el {nombre} con ID {valor}")
        return elemento

    def _siguiente_id(self) -> int:
        return max((item.idLiquidacion or 0 for item in self.liquidaciones), default=0) + 1

    @staticmethod
    def _activo(estado: Any) -> bool:
        return str(getattr(estado, "value", estado)).upper() == "ACTIVO"

    @staticmethod
    def _decimal(valor: Any, nombre: str) -> Decimal:
        if valor is None:
            raise ErrorNomina(f"Falta {nombre}")
        resultado = Decimal(valor)
        if resultado < 0:
            raise ErrorNomina(f"{nombre.capitalize()} no puede ser negativo")
        return resultado

    @staticmethod
    def _redondear(valor: Decimal) -> Decimal:
        return valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def consultar_detalles_liquidacion(self, id_liquidacion: int) -> list[DetalleLiquidacion]:
        """Consultar los detalles de una liquidación específica."""
        return [d for d in self.detalles_liquidacion if d.idLiquidacion == id_liquidacion]

    def reliquidar(self, id_liquidacion: int) -> LiquidacionNomina:
        """Recalcular una liquidación existente preservando el historial versionado.

        En lugar de borrar la liquidación original, crea una nueva versión con
        un número de versión incrementado. La liquidación original permanece en
        el historial y la nueva se agrega a la lista.
        """
        liquidacion_original = self._liquidacion(id_liquidacion)
        if liquidacion_original.pagada:
            raise ErrorNomina("No se puede reliquidar una liquidación ya pagada")

        # Determinar el número de versión de la nueva versión
        nueva_version = (liquidacion_original.version or 0) + 1

        # Crear la nueva liquidación versión con los mismos parámetros base
        contrato = self._contrato(liquidacion_original.idContrato)
        profesor = self._profesor(contrato.idPersona)
        periodo = self._periodo(liquidacion_original.idPeriodoNomina)
        self._validar_periodo_abierto(periodo)
        self._evitar_liquidacion_duplicada_version(liquidacion_original.idContrato, liquidacion_original.idPeriodoNomina, id_liquidacion)

        tipo = liquidacion_original.tipoProfesorLiquidado

        # Parámetros comunes para la nueva versión
        fecha_liquidacion = liquidacion_original.fechaLiquidacion

        # Crear la nueva liquidación versión usando el método apropiado según el tipo
        if tipo == TipoProfesor.PLANTA:
            nueva_liquidacion = self.liquidarProfesorPlanta(
                liquidacion_original.idContrato, liquidacion_original.idPeriodoNomina,
                fecha_liquidacion=fecha_liquidacion,
            )
        elif tipo == TipoProfesor.OCASIONAL:
            horas_incumplidas = liquidacion_original.horasIncumplidas or self.CERO
            nueva_liquidacion = self.liquidarProfesorOcasional(
                liquidacion_original.idContrato, liquidacion_original.idPeriodoNomina,
                horas_incumplidas=horas_incumplidas,
                fecha_liquidacion=fecha_liquidacion,
            )
        elif tipo == TipoProfesor.CATEDRATICO:
            nueva_liquidacion = self.liquidarProfesorCatedratico(
                liquidacion_original.idContrato, liquidacion_original.idPeriodoNomina,
                fecha_liquidacion=fecha_liquidacion,
            )
        else:
            raise ErrorNomina("Tipo de profesor no soportado para reliquidación")

        # Asignar el número de versión a la nueva liquidación
        nueva_liquidacion.version = nueva_version
        nueva_liquidacion.liquidacionOrigen = id_liquidacion

        # Marcar la original como versión anterior (opcional, para rastreo)
        liquidacion_original.requiereReliquidacion = True
        liquidacion_original.motivoReliquidacion = f"Reliquidación version {nueva_version} solicitada"

        # Agregar la nueva versión a la lista (la original se conserva en el historial)
        self.liquidaciones.append(nueva_liquidacion)

        # Crear los detalles de la nueva versión (eliminar detalles antiguos de esta versión específica)
        self._eliminar_detalles_version(id_liquidacion)
        self._crear_detalles(nueva_liquidacion, periodo,
            ibc=nueva_liquidacion.baseCotizacionSeguridadSocial,
            salario_ordinario=nueva_liquidacion.salarioOrdinario,
            auxilio=self._auxilio_transporte(contrato, nueva_liquidacion.salarioBase, self._salario_minimo(contrato, periodo), fecha_liquidacion),
            bonificacion_posgrado=self._bonificacion_posgrado(profesor, self._salario_minimo(contrato, periodo), contrato, nueva_liquidacion.horasAsignadas),
            bonificacion_investigacion=self._bonificacion_investigacion(profesor, self._salario_minimo(contrato, periodo), contrato, nueva_liquidacion.horasAsignadas),
            descuento_salud=self._descuento_salud(nueva_liquidacion.baseCotizacionSeguridadSocial),
            descuento_pension=self._descuento_pension(nueva_liquidacion.baseCotizacionSeguridadSocial),
            fondo_solidaridad=self._fondo_solidaridad(nueva_liquidacion.baseCotizacionSeguridadSocial),
            retencion=self._retencion_fuente(nueva_liquidacion.baseCotizacionSeguridadSocial, fecha_liquidacion),
            descuento_incumplimiento=nueva_liquidacion.descuentoHorasIncumplidas or self.CERO,
            aporte_salud=self._aporte_salud_patronal(nueva_liquidacion.baseCotizacionSeguridadSocial),
            aporte_pension=self._aporte_pension_patronal(nueva_liquidacion.baseCotizacionSeguridadSocial),
            aporte_arl=self._aporte_arl(nueva_liquidacion.baseCotizacionSeguridadSocial),
            aporte_caja=self._aporte_caja_compensacion(nueva_liquidacion.baseCotizacionSeguridadSocial),
            aporte_sena=self._aporte_sena_patronal(nueva_liquidacion.baseCotizacionSeguridadSocial),
            aporte_icbf=self._aporte_icbf_patronal(nueva_liquidacion.baseCotizacionSeguridadSocial),
        )

        return nueva_liquidacion

    def _eliminar_detalles(self, id_liquidacion: int) -> None:
        self.detalles_liquidacion = [d for d in self.detalles_liquidacion if d.idLiquidacion != id_liquidacion]

    def _eliminar_detalles_version(self, id_liquidacion_original: int) -> None:
        """Eliminar solo los detalles de la versión anterior, manteniendo otros."""
        self.detalles_liquidacion = [d for d in self.detalles_liquidacion if d.idLiquidacion != id_liquidacion_original]

    def _evitar_liquidacion_duplicada_version(self, id_contrato: int, id_periodo_nomina: int, id_liquidacion_origen: int) -> None:
        """Evitar liquidación duplicada versión: no permite una nueva versión si existe una versión RELIQUIDADA activa para el mismo contrato y periodo."""
        for item in self.liquidaciones:
            if (item.idContrato == id_contrato and item.idPeriodoNomina == id_periodo_nomina
                    and item.version is not None
                    and item.estado != "RELIQUIDADA"
                    and item.idLiquidacion != id_liquidacion_origen):
                raise ErrorNomina("Ya existe una versión de liquidación para ese contrato y periodo")

    def resumen_nomina_periodo(self, id_periodo_nomina: int) -> dict[str, Decimal]:
        """Generar resumen de nómina para un periodo."""
        liquidaciones = self._liquidaciones_periodo(id_periodo_nomina)
        if not liquidaciones:
            return {
                "total_liquidaciones": Decimal("0"),
                "total_devengado": Decimal("0"),
                "total_descuentos": Decimal("0"),
                "total_prestaciones": Decimal("0"),
                "total_aportes": Decimal("0"),
                "costo_total": Decimal("0"),
            }
        return {
            "total_liquidaciones": Decimal(len(liquidaciones)),
            "total_devengado": self._total_periodo(id_periodo_nomina, "totalDevengado"),
            "total_descuentos": self._total_periodo(id_periodo_nomina, "totalDescuentos"),
            "total_prestaciones": self._total_periodo(id_periodo_nomina, "totalPrestaciones"),
            "total_aportes": sum((self._aportes(l) for l in liquidaciones), self.CERO),
            "costo_total": self._total_periodo(id_periodo_nomina, "costoTotalEmpleador"),
        }

    def totales_por_tipo_profesor(self, id_periodo_nomina: int) -> dict[str, dict[str, Decimal]]:
        """Resumen de totales por tipo de profesor."""
        liquidaciones = self._liquidaciones_periodo(id_periodo_nomina)
        resultado: dict[str, dict[str, Decimal]] = {}
        for liq in liquidaciones:
            tipo = str(liq.tipoProfesorLiquidado or "DESCONOCIDO")
            if tipo not in resultado:
                resultado[tipo] = {
                    "cantidad": self.CERO,
                    "total_devengado": self.CERO,
                    "total_descuentos": self.CERO,
                    "neto": self.CERO,
                }
            resultado[tipo]["cantidad"] += Decimal("1")
            resultado[tipo]["total_devengado"] += liq.totalDevengado or self.CERO
            resultado[tipo]["total_descuentos"] += liq.totalDescuentos or self.CERO
            resultado[tipo]["neto"] += liq.netoPagar or self.CERO
        for tipo in resultado:
            for campo in resultado[tipo]:
                resultado[tipo][campo] = self._redondear(resultado[tipo][campo])
        return resultado

    def crear_periodo_nomina_mensual(self, anio: int, mes: int) -> PeriodoNomina:
        """Crear un periodo de nómina para un mes específico."""
        from calendar import monthrange
        _, ultimo_dia = monthrange(anio, mes)
        periodo = PeriodoNomina(
            idPeriodoNomina=max((p.idPeriodoNomina or 0 for p in self.periodos_nomina), default=0) + 1,
            anio=anio,
            mes=mes,
            fechaInicio=date(anio, mes, 1),
            fechaFin=date(anio, mes, ultimo_dia),
            fechaPago=date(anio, mes, ultimo_dia),
            tipoPeriodicidad="MENSUAL",
            diasBaseLiquidacion=30,
            estado="ABIERTO",
        )
        return self.crear_periodo_nomina(periodo)
