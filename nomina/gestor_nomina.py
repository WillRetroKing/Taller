"""Motor de liquidación de nómina docente y prestaciones PITA (Fachada Orquestadora)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Iterable

from dominio.modelo_datos import (
    Administrativo,
    CategoriaDocente,
    Contrato,
    Dedicacion,
    DetalleLiquidacion,
    Facultad,
    FactorSalarial,
    LiquidacionNomina,
    ParametroNormativo,
    PeriodoNomina,
    ProduccionAcademica,
    Profesor,
    ProgramaAcademico,
    TipoProfesor,
    Universidad,
)
from nomina.excepciones import ErrorNomina
from nomina.calculadora_deducciones import CalculadoraDeducciones
from nomina.calculadora_prestaciones import CalculadoraPrestaciones
from nomina.liquidadores import (
    LiquidadorPlanta,
    LiquidadorOcasional,
    LiquidadorCatedratico,
    LiquidadorAdministrativo,
)
from nomina.ciclo_vida_nomina import CicloVidaNomina


class GestorNomina:
    """Liquida docentes de planta, ocasionales y catedráticos según el modelo PITA."""

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
        administrativos: list[Administrativo] | None = None,
        universidades: list[Universidad] | None = None,
        facultades: list[Facultad] | None = None,
        programas: list[ProgramaAcademico] | None = None,
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
        self.administrativos = administrativos if administrativos is not None else []
        self.universidades = universidades if universidades is not None else []
        self.facultades = facultades if facultades is not None else []
        self.programas = programas if programas is not None else []

        # Inicializar submódulos especializados
        self.calc_deducciones = CalculadoraDeducciones(self.parametros)
        self.calc_prestaciones = CalculadoraPrestaciones(self.calc_deducciones)
        self.liquidador_planta = LiquidadorPlanta(self)
        self.liquidador_ocasional = LiquidadorOcasional(self)
        self.liquidador_catedratico = LiquidadorCatedratico(self)
        self.liquidador_administrativo = LiquidadorAdministrativo(self)
        self.ciclo_vida = CicloVidaNomina(self)

    # ------------------------------------------------------------------
    # LIQUIDACIONES PRINCIPALES POR RÉGIMEN
    # ------------------------------------------------------------------
    def liquidarProfesorOcasional(
        self,
        id_contrato: int,
        id_periodo_nomina: int,
        *,
        horas_incumplidas: Decimal | None = None,
        fecha_liquidacion: date | None = None,
    ) -> LiquidacionNomina:
        return self.liquidador_ocasional.liquidar(
            id_contrato, id_periodo_nomina, horas_incumplidas=horas_incumplidas, fecha_liquidacion=fecha_liquidacion
        )

    def liquidarProfesorPlanta(
        self,
        id_contrato: int,
        id_periodo_nomina: int,
        *,
        fecha_liquidacion: date | None = None,
    ) -> LiquidacionNomina:
        return self.liquidador_planta.liquidar(id_contrato, id_periodo_nomina, fecha_liquidacion=fecha_liquidacion)

    def liquidarProfesorCatedratico(
        self,
        id_contrato: int,
        id_periodo_nomina: int,
        *,
        fecha_liquidacion: date | None = None,
    ) -> LiquidacionNomina:
        return self.liquidador_catedratico.liquidar(id_contrato, id_periodo_nomina, fecha_liquidacion=fecha_liquidacion)

    def liquidarAdministrativo(
        self,
        id_contrato: int,
        id_periodo_nomina: int,
        *,
        fecha_liquidacion: date | None = None,
    ) -> LiquidacionNomina:
        return self.liquidador_administrativo.liquidar(id_contrato, id_periodo_nomina, fecha_liquidacion=fecha_liquidacion)

    def crear_liquidacion(self, liquidacion: LiquidacionNomina) -> LiquidacionNomina:
        contrato = self._contrato(liquidacion.idContrato)
        periodo = self._periodo(liquidacion.idPeriodoNomina)
        self._validar_periodo_abierto(periodo)
        self._evitar_liquidacion_duplicada(liquidacion.idContrato, liquidacion.idPeriodoNomina)

        tipo = getattr(contrato, "modalidadProfesor", None) or getattr(contrato, "tipoContrato", None)
        tipo = str(getattr(tipo, "value", tipo or "")).upper()

        if "ADMINISTRATIVO" in tipo:
            resultado = self.liquidarAdministrativo(liquidacion.idContrato, liquidacion.idPeriodoNomina)
        elif "OCASIONAL" in tipo:
            resultado = self.liquidarProfesorOcasional(
                liquidacion.idContrato, liquidacion.idPeriodoNomina,
                horas_incumplidas=liquidacion.horasIncumplidas or self.CERO,
            )
        elif "PLANTA" in tipo:
            resultado = self.liquidarProfesorPlanta(liquidacion.idContrato, liquidacion.idPeriodoNomina)
        elif "CATEDRATICO" in tipo:
            resultado = self.liquidarProfesorCatedratico(liquidacion.idContrato, liquidacion.idPeriodoNomina)
        else:
            resultado = self.liquidarProfesorOcasional(
                liquidacion.idContrato, liquidacion.idPeriodoNomina,
                horas_incumplidas=liquidacion.horasIncumplidas or self.CERO,
            )

        resultado.fechaLiquidacion = liquidacion.fechaLiquidacion or date.today()
        resultado.estado = liquidacion.estado or "PROCESADA"
        return resultado

    # ------------------------------------------------------------------
    # GESTIÓN DE PERIODOS Y CICLO CONTABLE
    # ------------------------------------------------------------------
    def crear_periodo_nomina(self, periodo: PeriodoNomina) -> PeriodoNomina:
        return self.ciclo_vida.crear_periodo_nomina(periodo)

    def abrir_periodo_nomina(self, id_periodo_nomina: int) -> PeriodoNomina:
        return self.ciclo_vida.abrir_periodo_nomina(id_periodo_nomina)

    def cerrar_periodo_nomina(self, id_periodo_nomina: int) -> PeriodoNomina:
        return self.ciclo_vida.cerrar_periodo_nomina(id_periodo_nomina)

    def crear_periodo_nomina_mensual(self, anio: int, mes: int) -> PeriodoNomina:
        return self.ciclo_vida.crear_periodo_nomina_mensual(anio, mes)

    def aprobar_liquidacion(self, id_liquidacion: int, usuario: str) -> LiquidacionNomina:
        return self.ciclo_vida.aprobar_liquidacion(id_liquidacion, usuario)

    def pagar_liquidacion(self, id_liquidacion: int, medio_pago: str, referencia: str) -> LiquidacionNomina:
        return self.ciclo_vida.pagar_liquidacion(id_liquidacion, medio_pago, referencia)

    def reliquidar(self, id_liquidacion: int) -> LiquidacionNomina:
        return self.ciclo_vida.reliquidar(id_liquidacion)

    def tiene_historial_liquidacion(self, liquidacion: LiquidacionNomina) -> bool:
        return self.ciclo_vida.tiene_historial_liquidacion(liquidacion)

    def modificar_liquidacion(self, id_liquidacion: int, **cambios: Any) -> LiquidacionNomina:
        return self.ciclo_vida.modificar_liquidacion(id_liquidacion, **cambios)

    def desactivar_liquidacion(self, id_liquidacion: int) -> LiquidacionNomina:
        return self.ciclo_vida.desactivar_liquidacion(id_liquidacion)

    def reactivar_liquidacion(self, id_liquidacion: int) -> LiquidacionNomina:
        return self.ciclo_vida.reactivar_liquidacion(id_liquidacion)

    def eliminar_liquidacion(self, id_liquidacion: int) -> LiquidacionNomina:
        return self.ciclo_vida.eliminar_liquidacion(id_liquidacion)

    def consultar_liquidaciones(self, id_profesor: int | None = None, id_periodo_nomina: int | None = None) -> list[LiquidacionNomina]:
        return [
            liq for liq in self.liquidaciones
            if (id_profesor is None or liq.idProfesor == id_profesor)
            and (id_periodo_nomina is None or liq.idPeriodoNomina == id_periodo_nomina)
        ]

    def consultar_detalles_liquidacion(self, id_liquidacion: int) -> list[DetalleLiquidacion]:
        return [d for d in self.detalles_liquidacion if d.idLiquidacion == id_liquidacion]

    def resumen_nomina_periodo(self, id_periodo_nomina: int) -> dict[str, Decimal]:
        return self.ciclo_vida.resumen_nomina_periodo(id_periodo_nomina)

    def totales_por_tipo_profesor(self, id_periodo_nomina: int) -> dict[str, dict[str, Decimal]]:
        return self.ciclo_vida.totales_por_tipo_profesor(id_periodo_nomina)

    def desglose_nomina_anual(self, id_contrato: int, anio: int = 2026) -> Any:
        from nomina.desglose_anual import CalculadorDesgloseAnual
        calculador = CalculadorDesgloseAnual(self)
        return calculador.generar_desglose_por_contrato(id_contrato, anio=anio)

    def resumen_nomina_anual(self, anio: int = 2026) -> dict[str, Any]:
        from nomina.desglose_anual import CalculadorDesgloseAnual
        calculador = CalculadorDesgloseAnual(self)
        return calculador.generar_desglose_institucional(anio=anio)

    # ------------------------------------------------------------------
    # HELPERS Y CONSULTAS INTERNAS
    # ------------------------------------------------------------------
    def _contrato(self, id_contrato: int) -> Contrato:
        return self._buscar(self.contratos, "idContrato", id_contrato, "contrato")

    def obtener_contratos_por_universidad(self, id_universidad: int) -> list[Contrato]:
        """Retorna todos los contratos asociados directa o indirectamente a una universidad."""
        resultado: list[Contrato] = []
        for c in self.contratos:
            if getattr(c, "idUniversidad", None) == id_universidad:
                resultado.append(c)
                continue
            prof = next((p for p in self.profesores if p.idPersona == c.idPersona), None)
            if prof and prof.idProgramaPrincipal and self.programas and self.facultades:
                prog = next((pr for pr in self.programas if pr.idPrograma == prof.idProgramaPrincipal), None)
                if prog and prog.idFacultad:
                    fac = next((f for f in self.facultades if f.idFacultad == prog.idFacultad), None)
                    if fac and fac.idUniversidad == id_universidad:
                        resultado.append(c)
        return resultado

    def _periodo(self, id_periodo: int) -> PeriodoNomina:
        return self._buscar(self.periodos_nomina, "idPeriodoNomina", id_periodo, "periodo de nómina")

    def _profesor(self, id_persona: int | None) -> Profesor:
        return self._buscar(self.profesores, "idPersona", id_persona, "profesor")

    def _administrativo(self, id_persona: int | None) -> Administrativo | None:
        if not self.administrativos or id_persona is None:
            return None
        return next((item for item in self.administrativos if item.idPersona == id_persona), None)

    def _liquidacion(self, id_liquidacion: int) -> LiquidacionNomina:
        return self._buscar(self.liquidaciones, "idLiquidacion", id_liquidacion, "liquidación")

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
        resultado = Decimal(str(valor))
        if resultado < 0:
            raise ErrorNomina(f"{nombre.capitalize()} no puede ser negativo")
        return resultado

    @staticmethod
    def _redondear(valor: Decimal) -> Decimal:
        return valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def _valor_enum(valor: Any) -> str:
        return str(getattr(valor, "value", valor or "")).upper()

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

    def _evitar_liquidacion_duplicada_version(self, id_contrato: int, id_periodo_nomina: int, id_liquidacion_origen: int) -> None:
        for item in self.liquidaciones:
            if (item.idContrato == id_contrato and item.idPeriodoNomina == id_periodo_nomina
                    and item.version is not None
                    and item.estado != "RELIQUIDADA"
                    and item.idLiquidacion != id_liquidacion_origen):
                raise ErrorNomina("Ya existe una versión de liquidación para ese contrato y periodo")

    def _liquidaciones_periodo(self, id_periodo_nomina: int | None) -> list[LiquidacionNomina]:
        return [item for item in self.liquidaciones if item.idPeriodoNomina == id_periodo_nomina]

    def _total_periodo(self, id_periodo_nomina: int | None, campo: str) -> Decimal:
        return self._redondear(sum((getattr(item, campo) or self.CERO for item in self._liquidaciones_periodo(id_periodo_nomina)), self.CERO))

    @staticmethod
    def _aportes(liquidacion: LiquidacionNomina) -> Decimal:
        campos = ("aportePatronalSalud", "aportePatronalPension", "aporteRiesgosLaborales", "aporteCajaCompensacion", "aportePatronalSENA", "aportePatronalICBF")
        return sum((getattr(liquidacion, campo) or Decimal("0") for campo in campos), Decimal("0"))

    @staticmethod
    def _es_regimen_1279(regimen: str | None) -> bool:
        if not regimen:
            return True
        r = str(regimen).upper().replace(" ", "")
        return "1279" in r or "PLANTA" in r

    def _puntos_planta(self, profesor: Profesor, periodo: PeriodoNomina) -> Decimal:
        tipo_str = str(getattr(profesor.tipoProfesor, "value", profesor.tipoProfesor or "")).upper()
        if tipo_str in ("OCASIONAL", "CATEDRATICO", "CATEDRATICO_AD_HONOREM", "AD_HONOREM"):
            return self.CERO

        pts_guardados = Decimal(str(profesor.puntosSalariales or self.CERO))
        if pts_guardados > self.CERO:
            return pts_guardados

        cat_str = str(profesor.categoriaDocente or profesor.categoriaReconocida or "").upper()
        pts_escalafon = {"AUXILIAR": Decimal("180"), "ASISTENTE": Decimal("250"), "ASOCIADO": Decimal("350"), "TITULAR": Decimal("450")}.get(
            cat_str,
            {"AUXILIAR": Decimal("37"), "ASISTENTE": Decimal("58"), "ASOCIADO": Decimal("74"), "TITULAR": Decimal("96")}.get(cat_str, Decimal("0")),
        )

        codigos_categoria = {str(profesor.categoriaDocente or "").upper(), str(profesor.categoriaReconocida or "").upper()}
        tiene_categoria = any(categoria.idCategoria == profesor.idCategoriaDocente or str(getattr(categoria.codigo, "value", categoria.codigo or "")).upper() in codigos_categoria for categoria in self.categorias)
        tiene_posgrado = bool(profesor.nivelPosgradoReconocido or profesor.maximoNivelEstudio)
        tiene_fuentes = tiene_categoria or tiene_posgrado or any(factor.idProfesor == profesor.idProfesor for factor in self.factores) or any(produccion.idProfesor == profesor.idProfesor for produccion in self.producciones)
        pts_calculados = self.CERO
        if tiene_fuentes:
            from gestores.gestor_factores import GestorFactores
            fecha = periodo.fechaFin or periodo.fechaInicio or date.today()
            pts_calculados = GestorFactores(self.categorias, self.factores, self.producciones, self.profesores).calcular_puntos_profesor(profesor.idProfesor, fecha)

        return max(pts_escalafon, pts_calculados)

    def _parametro_decimal(self, codigo: str, fecha: date | None = None) -> Decimal | None:
        return self.calc_deducciones.obtener_parametro_decimal(codigo, fecha)

    def _porcentaje(self, codigo: str, defecto: Decimal, fecha: date | None = None, codigos_utilizados: dict | None = None) -> Decimal:
        return self.calc_deducciones.obtener_porcentaje(codigo, defecto, fecha, codigos_utilizados)

    def _salario_minimo(self, contrato: Contrato, periodo: PeriodoNomina, fecha: date | None = None, codigos_utilizados: dict | None = None) -> Decimal:
        # Priorizar la variable activa de SALARIO_MINIMO parametrizada en tiempo de ejecución
        param_smmlv = self._parametro_decimal("SALARIO_MINIMO", fecha)
        if param_smmlv is not None and param_smmlv > self.CERO:
            if codigos_utilizados is not None:
                codigos_utilizados["SALARIO_MINIMO"] = str(param_smmlv)
            return self._decimal(param_smmlv, "salario mínimo vigente")
        periodo_smmlv = getattr(periodo, "salarioMinimoVigente", None)
        if periodo_smmlv is not None and periodo_smmlv > self.CERO:
            if codigos_utilizados is not None:
                codigos_utilizados["SALARIO_MINIMO"] = str(periodo_smmlv)
            return self._decimal(periodo_smmlv, "salario mínimo vigente")
        contra_smmlv = getattr(contrato, "salarioMinimoVigente", None)
        if contra_smmlv is not None and contra_smmlv > self.CERO:
            if codigos_utilizados is not None:
                codigos_utilizados["SALARIO_MINIMO"] = str(contra_smmlv)
            return self._decimal(contra_smmlv, "salario mínimo vigente")
        return Decimal("1750905")

    def _validar_contrato(self, contrato: Contrato, tipo: TipoProfesor, periodo: PeriodoNomina) -> None:
        actual = getattr(contrato.modalidadProfesor or contrato.tipoContrato or "", "value", contrato.modalidadProfesor or contrato.tipoContrato or "")
        actual = str(actual).upper().replace("DOCENTE_", "")
        esperado = tipo.value.replace("DOCENTE_", "")
        permitidos = {esperado}
        if tipo == TipoProfesor.CATEDRATICO:
            permitidos.add(TipoProfesor.CATEDRATICO_AD_HONOREM.value)
            permitidos.add("CATEDRATICO_AD_HONOREM")
            permitidos.add("AD_HONOREM")
        if actual not in permitidos:
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
        if horas_incumplidas == self.CERO:
            return
        if contrato.requiereCertificacionCumplimiento and not contrato.certificacionCumplimiento:
            raise ErrorNomina("Las horas incumplidas requieren certificación de cumplimiento según el art. 87 del decreto sustantivo de la materia")
        horas_semanales = contrato.horasSemanalesAsignadas or contrato.horasSemanales
        horas_mensuales_estimadas = (horas_semanales or self.CERO) * self.DIAS_MES / Decimal("7")
        if horas_semanales is None or horas_semanales <= 0:
            raise ErrorNomina("Se requieren horas asignadas para descontar incumplimientos en el contrato")
        if horas_incumplidas > horas_mensuales_estimadas:
            raise ErrorNomina(
                f"Las horas incumplidas ({horas_incumplidas}) no pueden superar las horas mensuales estimadas ({horas_mensuales_estimadas}) basadas en {horas_semanales} horas semanales asignadas"
            )

    def _eliminar_detalles_version(self, id_liquidacion_original: int) -> None:
        self.detalles_liquidacion = [d for d in self.detalles_liquidacion if d.idLiquidacion != id_liquidacion_original]
