"""Gestión del ciclo de vida contable: periodos, aprobación, pagos, reliquidación y reportes."""

from __future__ import annotations

from calendar import monthrange
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from dominio.modelo_datos import LiquidacionNomina, PeriodoNomina, TipoProfesor
from nomina.excepciones import ErrorNomina

if TYPE_CHECKING:
    from nomina.gestor_nomina import GestorNomina


class CicloVidaNomina:
    """Administra el ciclo contable y la auditoría de periodos y liquidaciones."""

    CERO = Decimal("0")

    def __init__(self, gestor: GestorNomina) -> None:
        self.gestor = gestor

    # ------------------------------------------------------------------
    # PERIODOS DE NÓMINA
    # ------------------------------------------------------------------
    def crear_periodo_nomina(self, periodo: PeriodoNomina) -> PeriodoNomina:
        if periodo.idPeriodoNomina is None:
            periodo.idPeriodoNomina = max(
                (item.idPeriodoNomina or 0 for item in self.gestor.periodos_nomina), default=0
            ) + 1
        if any(item.idPeriodoNomina == periodo.idPeriodoNomina for item in self.gestor.periodos_nomina):
            raise ErrorNomina(f"Ya existe el periodo de nómina {periodo.idPeriodoNomina}")
        if periodo.fechaInicio and periodo.fechaFin and periodo.fechaFin < periodo.fechaInicio:
            raise ErrorNomina("La fecha final no puede preceder a la fecha inicial")
        periodo.estaCerrado = False
        periodo.estado = periodo.estado or "ABIERTO"
        self.gestor.periodos_nomina.append(periodo)
        return periodo

    def abrir_periodo_nomina(self, id_periodo_nomina: int) -> PeriodoNomina:
        periodo = self.gestor._periodo(id_periodo_nomina)
        if periodo.estaCerrado:
            raise ErrorNomina("Un periodo cerrado no puede reabrirse")
        periodo.estado = "ABIERTO"
        return periodo

    def cerrar_periodo_nomina(self, id_periodo_nomina: int) -> PeriodoNomina:
        periodo = self.gestor._periodo(id_periodo_nomina)
        if periodo.estaCerrado:
            raise ErrorNomina("El periodo ya está cerrado")
        periodo.totalDevengadoPeriodo = self.gestor._total_periodo(periodo.idPeriodoNomina, "totalDevengado")
        periodo.totalDescuentosPeriodo = self.gestor._total_periodo(periodo.idPeriodoNomina, "totalDescuentos")
        periodo.totalPrestacionesPeriodo = self.gestor._total_periodo(periodo.idPeriodoNomina, "totalPrestaciones")
        periodo.totalAportesPatronalesPeriodo = sum(
            (self.gestor._aportes(liq) for liq in self.gestor._liquidaciones_periodo(periodo.idPeriodoNomina)),
            self.CERO,
        )
        periodo.costoTotalPeriodo = self.gestor._total_periodo(periodo.idPeriodoNomina, "costoTotalEmpleador")
        periodo.estaCerrado = True
        periodo.estado = "CERRADO"
        return periodo

    def crear_periodo_nomina_mensual(self, anio: int, mes: int) -> PeriodoNomina:
        _, ultimo_dia = monthrange(anio, mes)
        periodo = PeriodoNomina(
            idPeriodoNomina=max((p.idPeriodoNomina or 0 for p in self.gestor.periodos_nomina), default=0) + 1,
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

    # ------------------------------------------------------------------
    # APROBACIÓN Y PAGO
    # ------------------------------------------------------------------
    def aprobar_liquidacion(self, id_liquidacion: int, usuario: str) -> LiquidacionNomina:
        liquidacion = self.gestor._liquidacion(id_liquidacion)
        periodo = self.gestor._periodo(liquidacion.idPeriodoNomina)
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
        liquidacion = self.gestor._liquidacion(id_liquidacion)
        periodo = self.gestor._periodo(liquidacion.idPeriodoNomina)
        self.gestor._validar_periodo_abierto(periodo)
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

    # ------------------------------------------------------------------
    # RELIQUIDACIÓN Y AUDITORÍA
    # ------------------------------------------------------------------
    def reliquidar(self, id_liquidacion: int) -> LiquidacionNomina:
        liquidacion_original = self.gestor._liquidacion(id_liquidacion)
        if liquidacion_original.pagada:
            raise ErrorNomina("No se puede reliquidar una liquidación ya pagada")

        nueva_version = (liquidacion_original.version or 0) + 1
        periodo = self.gestor._periodo(liquidacion_original.idPeriodoNomina)
        self.gestor._validar_periodo_abierto(periodo)
        self.gestor._evitar_liquidacion_duplicada_version(
            liquidacion_original.idContrato, liquidacion_original.idPeriodoNomina, id_liquidacion
        )

        tipo = liquidacion_original.tipoProfesorLiquidado
        fecha_liq = liquidacion_original.fechaLiquidacion

        if tipo == TipoProfesor.PLANTA:
            nueva = self.gestor.liquidador_planta.liquidar(
                liquidacion_original.idContrato, liquidacion_original.idPeriodoNomina, fecha_liquidacion=fecha_liq
            )
        elif tipo == TipoProfesor.OCASIONAL:
            horas_inc = liquidacion_original.horasIncumplidas or self.CERO
            nueva = self.gestor.liquidador_ocasional.liquidar(
                liquidacion_original.idContrato, liquidacion_original.idPeriodoNomina, horas_incumplidas=horas_inc, fecha_liquidacion=fecha_liq
            )
        elif tipo == TipoProfesor.CATEDRATICO:
            nueva = self.gestor.liquidador_catedratico.liquidar(
                liquidacion_original.idContrato, liquidacion_original.idPeriodoNomina, fecha_liquidacion=fecha_liq
            )
        else:
            raise ErrorNomina("Tipo de profesor no soportado para reliquidación")

        nueva.version = nueva_version
        nueva.liquidacionOrigen = id_liquidacion
        liquidacion_original.requiereReliquidacion = True
        liquidacion_original.motivoReliquidacion = f"Reliquidación version {nueva_version} solicitada"

        self.gestor._eliminar_detalles_version(id_liquidacion)
        return nueva

    def tiene_historial_liquidacion(self, liquidacion: LiquidacionNomina) -> bool:
        return (
            bool(liquidacion.pagada)
            or bool(liquidacion.requiereReliquidacion)
            or (liquidacion.version is not None and liquidacion.version > 0)
            or liquidacion.estado == "RELIQUIDADA"
        )

    def modificar_liquidacion(self, id_liquidacion: int, **cambios: Any) -> LiquidacionNomina:
        liquidacion = self.gestor._liquidacion(id_liquidacion)
        if liquidacion.pagada:
            raise ErrorNomina("No se puede modificar una liquidación ya pagada")
        if liquidacion.requiereReliquidacion:
            raise ErrorNomina("No se puede modificar una liquidación que fue reliquidada")
        if self.tiene_historial_liquidacion(liquidacion):
            raise ErrorNomina("No se puede modificar directamente una liquidación con historial")

        campos_permitidos = {
            "fechaLiquidacion", "observaciones", "usuarioAprobador",
            "aprobada", "requiereReliquidacion", "motivoReliquidacion",
        }
        desconocidos = set(cambios) - campos_permitidos
        if desconocidos:
            raise ErrorNomina(f"Campos no válidos para modificación: {', '.join(sorted(desconocidos))}")

        for campo, valor in cambios.items():
            setattr(liquidacion, campo, valor)
        return liquidacion

    def desactivar_liquidacion(self, id_liquidacion: int) -> LiquidacionNomina:
        liquidacion = self.gestor._liquidacion(id_liquidacion)
        liquidacion.estado = "INACTIVO"
        liquidacion.fechaGeneracion = date.today()
        return liquidacion

    def reactivar_liquidacion(self, id_liquidacion: int) -> LiquidacionNomina:
        liquidacion = self.gestor._liquidacion(id_liquidacion)
        liquidacion.estado = "PROCESADA"
        return liquidacion

    def eliminar_liquidacion(self, id_liquidacion: int) -> LiquidacionNomina:
        liquidacion = self.gestor._liquidacion(id_liquidacion)
        if self.tiene_historial_liquidacion(liquidacion):
            return self.desactivar_liquidacion(id_liquidacion)

        self.gestor.liquidaciones.remove(liquidacion)
        self.sincronizar_detalles_liquidacion(id_liquidacion)
        return liquidacion

    def sincronizar_detalles_liquidacion(self, id_liquidacion: int) -> None:
        if not hasattr(self.gestor, "detalles_liquidacion") or self.gestor.detalles_liquidacion is None:
            return
        self.gestor.detalles_liquidacion = [
            d for d in self.gestor.detalles_liquidacion
            if getattr(d, "idLiquidacion", None) != id_liquidacion
        ]

    # ------------------------------------------------------------------
    # REPORTES Y RESÚMENES
    # ------------------------------------------------------------------
    def resumen_nomina_periodo(self, id_periodo_nomina: int) -> dict[str, Decimal]:
        liquidaciones = self.gestor._liquidaciones_periodo(id_periodo_nomina)
        if not liquidaciones:
            return {
                "total_liquidaciones": self.CERO,
                "total_devengado": self.CERO,
                "total_descuentos": self.CERO,
                "total_prestaciones": self.CERO,
                "total_aportes": self.CERO,
                "costo_total": self.CERO,
            }
        return {
            "total_liquidaciones": Decimal(len(liquidaciones)),
            "total_devengado": self.gestor._total_periodo(id_periodo_nomina, "totalDevengado"),
            "total_descuentos": self.gestor._total_periodo(id_periodo_nomina, "totalDescuentos"),
            "total_prestaciones": self.gestor._total_periodo(id_periodo_nomina, "totalPrestaciones"),
            "total_aportes": sum((self.gestor._aportes(l) for l in liquidaciones), self.CERO),
            "costo_total": self.gestor._total_periodo(id_periodo_nomina, "costoTotalEmpleador"),
        }

    def totales_por_tipo_profesor(self, id_periodo_nomina: int) -> dict[str, dict[str, Decimal]]:
        liquidaciones = self.gestor._liquidaciones_periodo(id_periodo_nomina)
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
                resultado[tipo][campo] = self.gestor._redondear(resultado[tipo][campo])
        return resultado
