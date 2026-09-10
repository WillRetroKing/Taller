from datetime import date, time
from decimal import Decimal
from tempfile import TemporaryDirectory
import unittest
import subprocess
import sys

from gestores.gestor_academico import ErrorAcademico, GestorAcademico
from gestores.gestor_contratos import ErrorContrato, GestorContratos
from persistencia.gestor_crud import ErrorCRUD, GestorCRUD
from nomina import ErrorNomina, GestorNomina
from gestores.gestor_parametros import ErrorParametro, GestorParametros
from gestores.gestor_periodos import ErrorPeriodo, GestorPeriodosAcademicos
from persistencia.gestor_persistencia import GestorPersistencia
from gestores.gestores_academicos import ErrorCalificacion, ErrorMatricula, GestorCalificaciones, GestorMatriculas
from dominio.modelo_datos import (
    Administrativo, Calificacion, Contrato, Curso, DetalleMatricula, DetallePlanEstudio,
    Dedicacion, Estudiante, EstadoAcademico, EstadoCurso, Evaluacion, Facultad,
    Horario, LiquidacionNomina, MatriculaAcademica, OfertaCurso,
    ParametroNormativo, ParametroNormativoCodigo, PeriodoAcademico,
    PeriodoNomina, Persona, PlanEstudio, Profesor, Prerrequisito,
    ProgramaAcademico, TipoProfesor,
)


class TestCRUD(unittest.TestCase):
    def test_crud_y_codigo_unico(self):
        registros = []
        gestor = GestorCRUD(registros, campo_id="idFacultad", campo_codigo="codigoFacultad")
        facultad = gestor.crear(Facultad(codigoFacultad="F-01", nombre="Ingenieria"))
        with self.assertRaises(ErrorCRUD):
            gestor.crear(Facultad(codigoFacultad="F-01", nombre="Duplicada"))
        gestor.modificar(facultad.idFacultad, nombre="Ciencias")
        gestor.desactivar(facultad.idFacultad)
        self.assertEqual(gestor.listar(incluir_inactivos=False), [])
        gestor.reactivar(facultad.idFacultad)
        self.assertEqual(facultad.nombre, "Ciencias")


class TestPersistencia(unittest.TestCase):
    def test_guardar_cargar_y_referencia(self):
        with TemporaryDirectory() as directory:
            gestor = GestorPersistencia(directory)
            gestor.guardar_todos_los_datos({
                Facultad: [Facultad(1, nombre="Ingenieria")],
                ProgramaAcademico: [ProgramaAcademico(2, idFacultad=1, fechaCreacion=date(2026, 9, 3))],
            })
            datos = gestor.cargar_todos_los_datos()
            self.assertEqual(datos[ProgramaAcademico][0].fechaCreacion, date(2026, 9, 3))
            gestor.guardar_entidad([ProgramaAcademico(3, idFacultad=99)], ProgramaAcademico)
            with self.assertRaises(ValueError):
                gestor.cargar_todos_los_datos()

    def test_flujo_integral_guardar_y_cargar_relaciones(self):
        with TemporaryDirectory() as directory:
            datos = {
                Facultad: [Facultad(1, codigoFacultad="F-01", nombre="Ingenieria")],
                ProgramaAcademico: [ProgramaAcademico(1, codigoPrograma="P-01", nombre="Sistemas", idFacultad=1)],
                Curso: [Curso(1, codigoCurso="CUR-01", nombre="Algoritmos", numeroCreditos=3)],
                PeriodoAcademico: [PeriodoAcademico(1, codigo="2026-1", estado="ACTIVO")],
                OfertaCurso: [OfertaCurso(1, idCurso=1, idPeriodo=1, grupo="A", cupoDisponible=20, estado="ACTIVO")],
            }
            gestor = GestorPersistencia(directory)
            gestor.guardar_todos_los_datos(datos)
            cargados = gestor.cargar_todos_los_datos()
            relaciones = gestor.reconstruir_relaciones(cargados)
            self.assertIs(relaciones["facultad_por_programa"][1], cargados[Facultad][0])
            self.assertIs(relaciones["curso_por_oferta"][1], cargados[Curso][0])

    def test_cli_inicia_sin_datos_y_sale(self):
        resultado = subprocess.run(
            [sys.executable, "main.py"], input="N\n15\nN\n", text=True,
            capture_output=True, check=False,
        )
        self.assertEqual(resultado.returncode, 0)
        self.assertIn("¡Gracias por usar PITA!", resultado.stdout)


class TestAcademico(unittest.TestCase):
    def setUp(self):
        self.estudiante = Estudiante(1, estadoAcademico=EstadoAcademico.ACTIVO)
        self.periodo = PeriodoAcademico(1, estado="ACTIVO", fechaInicioMatricula=date(2026, 1, 1), fechaFinMatricula=date(2026, 12, 31))
        self.cursos = [Curso(1, numeroCreditos=3), Curso(2, numeroCreditos=3)]
        self.ofertas = [OfertaCurso(1, 1, 1, cupoDisponible=1, estado="ACTIVO"), OfertaCurso(2, 2, 1, cupoDisponible=1, estado="ACTIVO")]
        self.matriculas, self.detalles = [], []

    def test_matricula_cancelacion_cupo_y_cruce(self):
        gestor = GestorMatriculas([self.estudiante], [self.periodo], self.ofertas, self.cursos, self.matriculas, self.detalles, [Horario(1, 1, "LUNES", time(8), time(10)), Horario(2, 2, "LUNES", time(9), time(11))])
        gestor.matricular_curso(1, 1, date(2026, 2, 1))
        with self.assertRaises(ErrorMatricula):
            gestor.matricular_curso(1, 2, date(2026, 2, 1))
        gestor.cancelar_curso(1, 1, "Horario laboral", date(2026, 2, 2))
        self.assertEqual(self.ofertas[0].cupoDisponible, 1)

    def test_calificacion_ponderada_y_ebra(self):
        detalle = DetalleMatricula(1, 1, 1)
        matricula = MatriculaAcademica(1, 1, 1)
        evaluaciones = [Evaluacion(1, 1, porcentaje=Decimal("30"), estado="ACTIVO"), Evaluacion(2, 1, porcentaje=Decimal("30"), estado="ACTIVO"), Evaluacion(3, 1, porcentaje=Decimal("40"), estado="ACTIVO")]
        parametros = [ParametroNormativo(codigo=ParametroNormativoCodigo.PROMEDIO_MINIMO_EBRA, valor="3.0")]
        gestor = GestorCalificaciones(evaluaciones, [], [detalle], [matricula], [self.estudiante], self.ofertas, self.cursos, parametros, [])
        for evaluacion, nota in ((1, "2"), (2, "2"), (3, "2")):
            gestor.registrar_calificacion(evaluacion, 1, Decimal(nota))
        self.assertEqual(detalle.notaFinal, Decimal("2.00"))
        self.assertEqual(self.estudiante.estadoAcademico, EstadoAcademico.EBRA)


class TestOperacionesAcademicas(unittest.TestCase):
    def test_periodos_y_ofertas_consultables_y_modificables(self):
        periodo = PeriodoAcademico(1, codigo="2026-1", nombre="2026-1", estado="ABIERTO")
        oferta = OfertaCurso(1, idCurso=1, idPeriodo=1, grupo="A", cupoMaximo=30, cupoDisponible=20, estado="ACTIVO")
        gestor = GestorPeriodosAcademicos([periodo], [oferta])

        self.assertEqual(gestor.consultar_periodo(1), periodo)
        self.assertEqual(gestor.consultar_ofertas_periodo(1), [oferta])
        modificada = gestor.modificar_oferta(1, 1, grupo="B", cupoMaximo=25, cupoDisponible=15)
        self.assertEqual((modificada.grupo, modificada.cupoDisponible), ("B", 15))
        with self.assertRaises(ErrorPeriodo):
            gestor.modificar_oferta(1, 1, cupoDisponible=26)
        self.assertEqual(oferta.cupoDisponible, 15)

        gestor.cerrar_periodo(1)
        with self.assertRaises(ErrorPeriodo):
            gestor.abrir_periodo(1)

    def test_calificaciones_rechazan_registros_inactivos_o_cancelados(self):
        estudiante = Estudiante(1, estadoAcademico=EstadoAcademico.ACTIVO)
        oferta = OfertaCurso(1, idCurso=1, idPeriodo=1, estado="ACTIVO")
        curso = Curso(1, numeroCreditos=3)
        detalle_cancelado = DetalleMatricula(1, 1, 1, estadoCurso=EstadoCurso.CANCELADO)
        evaluacion = Evaluacion(1, 1, nombre="Parcial", tipo="PARCIAL", porcentaje=Decimal("100"), estado="ACTIVO")
        gestor = GestorCalificaciones([evaluacion], [], [detalle_cancelado], [MatriculaAcademica(1, 1, 1)], [estudiante], [oferta], [curso])
        with self.assertRaises(ErrorCalificacion):
            gestor.registrar_calificacion(1, 1, Decimal("4"))

        oferta.estado = "INACTIVO"
        with self.assertRaises(ErrorCalificacion):
            gestor.crear_evaluacion(1, "Quiz", "QUIZ", Decimal("10"))


class TestContratosParametrosNomina(unittest.TestCase):
    def test_restricciones_contrato(self):
        gestor = GestorContratos([])
        with self.assertRaises(ErrorContrato):
            gestor.crear_contrato(Contrato(idPersona=1, modalidadProfesor="OCASIONAL", dedicacion=Dedicacion.HORA_CATEDRA, duracionEnMeses=6))
        contrato = gestor.crear_contrato(Contrato(idPersona=2, modalidadProfesor="OCASIONAL", dedicacion=Dedicacion.MEDIO_TIEMPO, duracionEnMeses=11))
        self.assertEqual(contrato.idContrato, 1)

    def test_parametros_y_nomina(self):
        parametros = []
        gestor_parametros = GestorParametros(parametros)
        gestor_parametros.crear_parametro(ParametroNormativo(codigo="SALARIO_MINIMO", valor="1000", fechaInicioVigencia=date(2026, 1, 1)))
        with self.assertRaises(ErrorParametro):
            gestor_parametros.crear_parametro(ParametroNormativo(codigo="SALARIO_MINIMO", valor="1100", fechaInicioVigencia=date(2026, 1, 1)))
        profesor = Profesor(1, 1, puntosSalariales=Decimal("100"))
        contrato = Contrato(1, 1, modalidadProfesor=TipoProfesor.PLANTA, dedicacion=Dedicacion.MEDIO_TIEMPO, estado="ACTIVO")
        periodo = PeriodoNomina(1, valorPuntoSalarialVigente=Decimal("50"), salarioMinimoVigente=Decimal("1000"))
        liquidacion = GestorNomina([contrato], [profesor], [periodo]).liquidarProfesorPlanta(1, 1)
        self.assertEqual(liquidacion.salarioBase, Decimal("2500"))

    def test_nomina_ocasional_exoneracion_y_bonificaciones_exentas(self):
        profesor = Profesor(
            idProfesor=1,
            idPersona=10,
            nivelPosgradoReconocido="MAESTRIA",
            categoriaGrupoInvestigacion="GRUPO_A",
            productividadInvestigativaVigente=True,
            certificacionVicerrectoriaInvestigacion="CERT",
        )
        contrato = Contrato(
            idContrato=1,
            idPersona=10,
            modalidadProfesor="OCASIONAL",
            factorSalarialSMMLV=Decimal("2"),
            horasIncumplidas=Decimal("2"),
            valorHoraIncumplida=Decimal("10"),
            horasSemanalesAsignadas=Decimal("24"),  # Añadido: requiere validación horas incumplidas
            estado="ACTIVO",
        )
        periodo = PeriodoNomina(1, salarioMinimoVigente=Decimal("1000"), diasBaseLiquidacion=30)
        liquidacion = GestorNomina([contrato], [profesor], [periodo]).liquidarProfesorOcasional(1, 1)
        self.assertEqual(liquidacion.baseSeguridadSocial, Decimal("1980.00"))
        self.assertEqual(liquidacion.baseLiquidacionPrestaciones, Decimal("1980.00"))
        self.assertEqual(liquidacion.bonificacionesNoSalariales, Decimal("920.00"))
        self.assertEqual(liquidacion.aportePatronalSalud, Decimal("0.00"))
        self.assertEqual(liquidacion.aportePatronalSENA, Decimal("0.00"))
        self.assertEqual(liquidacion.aportePatronalICBF, Decimal("0.00"))

    def test_nomina_catedratico_prorratea_horas(self):
        profesor = Profesor(idProfesor=1, idPersona=10, nivelPosgradoReconocido="ESPECIALIZACION")
        contrato = Contrato(
            idContrato=1,
            idPersona=10,
            modalidadProfesor="CATEDRATICO",
            horasMensualesAsignadas=Decimal("100"),
            horasMensualesCumplidas=Decimal("80"),
            valorHoraCatedraVigente=Decimal("20"),
            estado="ACTIVO",
        )
        periodo = PeriodoNomina(1, salarioMinimoVigente=Decimal("1000"))
        liquidacion = GestorNomina([contrato], [profesor], [periodo]).liquidarProfesorCatedratico(1, 1)
        self.assertEqual(liquidacion.salarioOrdinario, Decimal("1600.00"))
        self.assertEqual(liquidacion.bonificacionPosgrado, Decimal("80.00"))
        self.assertEqual(liquidacion.baseSeguridadSocial, Decimal("1600.00"))

    def test_nomina_usa_parametro_vigente_del_periodo(self):
        profesor = Profesor(idProfesor=1, idPersona=10)
        contrato = Contrato(idContrato=1, idPersona=10, modalidadProfesor="OCASIONAL", factorSalarialSMMLV=Decimal("1"), estado="ACTIVO")
        periodo = PeriodoNomina(1, fechaInicio=date(2026, 6, 1), fechaFin=date(2026, 6, 30), salarioMinimoVigente=None)
        parametros = [
            ParametroNormativo(codigo="SALARIO_MINIMO", valor="1000", fechaInicioVigencia=date(2025, 1, 1), fechaFinVigencia=date(2025, 12, 31), estado="ACTIVO"),
            ParametroNormativo(codigo="SALARIO_MINIMO", valor="2000", fechaInicioVigencia=date(2026, 1, 1), estado="ACTIVO"),
        ]
        liquidacion = GestorNomina([contrato], [profesor], [periodo], parametros=parametros).liquidarProfesorOcasional(1, 1)
        self.assertEqual(liquidacion.salarioMinimoUsado, Decimal("2000"))
        self.assertEqual(liquidacion.salarioBase, Decimal("2000"))

    def test_auxilio_entra_en_neto_y_fondo_solidaridad_es_parametrico(self):
        profesor = Profesor(idProfesor=1, idPersona=10)
        periodo = PeriodoNomina(1, salarioMinimoVigente=Decimal("1000"))
        parametros = [ParametroNormativo(codigo="VALOR_AUXILIO_TRANSPORTE_VIGENTE", valor="100", fechaInicioVigencia=date(2026, 1, 1))]
        contrato_auxilio = Contrato(idContrato=1, idPersona=10, modalidadProfesor="OCASIONAL", factorSalarialSMMLV=Decimal("1"), aplicaAuxilioTransporte=True, estado="ACTIVO")
        liquidacion_auxilio = GestorNomina([contrato_auxilio], [profesor], [periodo], parametros=parametros).liquidarProfesorOcasional(1, 1)
        self.assertEqual(liquidacion_auxilio.valorAuxilioTransporteCotizado, Decimal("100.00"))
        self.assertEqual(liquidacion_auxilio.totalDevengado, Decimal("1100.00"))
        self.assertEqual(liquidacion_auxilio.netoPagar, Decimal("1020.00"))

        parametros.append(ParametroNormativo(codigo="PORCENTAJE_FONDO_SOLIDARIDAD", valor="0.01", fechaInicioVigencia=date(2026, 1, 1)))
        contrato_fsp = Contrato(idContrato=2, idPersona=10, modalidadProfesor="OCASIONAL", factorSalarialSMMLV=Decimal("4"), estado="ACTIVO")
        liquidacion_fsp = GestorNomina([contrato_fsp], [profesor], [periodo], parametros=parametros).liquidarProfesorOcasional(2, 1)
        self.assertEqual(liquidacion_fsp.fondoSolidaridadPensional, Decimal("40.00"))

    def test_ciclo_nomina_y_bloqueo_periodo_cerrado(self):
        periodo = PeriodoNomina(1, estado="ABIERTO")
        liquidacion = LiquidacionNomina(1, idPeriodoNomina=1, totalDevengado=Decimal("100"), totalDescuentos=Decimal("10"), totalPrestaciones=Decimal("5"), costoTotalEmpleador=Decimal("130"))
        gestor = GestorNomina([], [], [periodo], [liquidacion])
        gestor.aprobar_liquidacion(1, "admin")
        gestor.pagar_liquidacion(1, "TRANSFERENCIA", "REF-1")
        gestor.cerrar_periodo_nomina(1)
        with self.assertRaises(ErrorNomina):
            gestor._validar_periodo_abierto(periodo)

    def test_liquidacion_conserva_detalles_y_excluye_bonificaciones(self):
        profesor = Profesor(idProfesor=1, idPersona=10, nivelPosgradoReconocido="DOCTORADO")
        contrato = Contrato(idContrato=1, idPersona=10, modalidadProfesor="CATEDRATICO", horasMensualesAsignadas=Decimal("100"), horasMensualesCumplidas=Decimal("100"), valorHoraCatedraVigente=Decimal("20"), estado="ACTIVO")
        periodo = PeriodoNomina(1, salarioMinimoVigente=Decimal("1000"))
        detalles = []
        liquidacion = GestorNomina([contrato], [profesor], [periodo], detalles_liquidacion=detalles).liquidarProfesorCatedratico(1, 1)
        bonificacion = next(item for item in detalles if item.tipoMovimiento == "BONIFICACION_POSGRADO")
        salario = next(item for item in detalles if item.tipoMovimiento == "SALARIO_ORDINARIO")
        self.assertEqual(liquidacion.idLiquidacion, bonificacion.idLiquidacion)
        self.assertFalse(bonificacion.esSalarial)
        self.assertFalse(bonificacion.integraSeguridadSocial)
        self.assertFalse(bonificacion.integraPrestaciones)
        self.assertFalse(bonificacion.integraParafiscales)
        self.assertTrue(salario.integraSeguridadSocial)

    def test_liquidacion_administrativo(self):
        adm = Administrativo(idAdministrativo=1, idPersona=7, cargo="Director Admisiones", salarioBase=Decimal("3800000"))
        contrato = Contrato(idContrato=4, idPersona=7, tipoContrato="ADMINISTRATIVO", salarioBase=Decimal("3800000"), estado="ACTIVO", regimenAplicable="LEY_100_CST")
        periodo = PeriodoNomina(1, salarioMinimoVigente=Decimal("1750905"), diasBaseLiquidacion=30)
        detalles = []
        gestor = GestorNomina([contrato], [], [periodo], detalles_liquidacion=detalles, administrativos=[adm])
        liq = gestor.liquidarAdministrativo(4, 1)

        self.assertIsNone(liq.idProfesor)
        self.assertEqual(liq.regimenLiquidado, "LEY_100_CST")
        self.assertEqual(liq.categoriaLiquidada, "Director Admisiones")
        self.assertEqual(liq.baseCotizacionSeguridadSocial, Decimal("3800000.00"))
        self.assertEqual(liq.descuentoSalud, Decimal("152000.00"))
        self.assertEqual(liq.descuentoPension, Decimal("152000.00"))
        self.assertEqual(liq.totalDescuentos, Decimal("304000.00"))
        self.assertEqual(liq.netoPagar, Decimal("3496000.00"))
        self.assertTrue(any(d.tipoMovimiento == "SALARIO_ORDINARIO" for d in detalles))
        self.assertTrue(any(d.tipoMovimiento == "DESCUENTO_SALUD" for d in detalles))

    def test_desglose_nomina_anual(self):
        profesor = Profesor(idProfesor=1, idPersona=10, puntosSalariales=Decimal("500"))
        contrato = Contrato(idContrato=1, idPersona=10, modalidadProfesor="PLANTA", dedicacion=Dedicacion.TIEMPO_COMPLETO, salarioBase=Decimal("10000000"), estado="ACTIVO")
        periodo = PeriodoNomina(1, anio=2026, mes=1, salarioMinimoVigente=Decimal("1750905"), valorPuntoSalarialVigente=Decimal("20000"))
        gestor = GestorNomina([contrato], [profesor], [periodo])
        desglose = gestor.desglose_nomina_anual(1, anio=2026)

        self.assertEqual(desglose.meses_considerados, 12)
        self.assertEqual(desglose.dias_trabajados_anio, 360)
        self.assertEqual(desglose.salario_ordinario_anual, Decimal("120000000.00"))
        self.assertEqual(desglose.cesantias_anuales, Decimal("10000000.00"))
        self.assertEqual(desglose.intereses_cesantias_anuales, Decimal("1200000.00"))
        self.assertEqual(desglose.prima_servicios_anual, Decimal("10000000.00"))
        self.assertEqual(desglose.descuento_salud_anual, Decimal("4800000.00"))
        self.assertEqual(desglose.descuento_pension_anual, Decimal("4800000.00"))
        self.assertEqual(desglose.neto_anual_trabajador, Decimal("110400000.00"))


class TestAcademicoEstructura(unittest.TestCase):
    def test_plan_y_prerrequisito(self):
        gestor = GestorAcademico([], [], [Curso(1, numeroCreditos=3), Curso(2, numeroCreditos=4)], [], [ProgramaAcademico(1)])
        plan = gestor.crear_plan(PlanEstudio(idPrograma=1))
        gestor.incluir_curso(plan.idPlanEstudio, 1, 1)
        requisito = gestor.registrar_prerrequisito(Prerrequisito(idCurso=2, idCursoRequerido=1))
        self.assertEqual(plan.totalCreditos, 3)
        self.assertEqual(requisito.idPrerrequisito, 1)

    def test_gestion_periodos_academicos_y_estados(self):
        """Valida el ciclo de vida, fechas y estados del período académico."""
        p = PeriodoAcademico(
            idPeriodo=1,
            codigo="2026-1",
            nombre="Primer Período Académico 2026",
            anio=2026,
            numeroPeriodo=1,
            fechaInicio=date(2026, 2, 1),
            fechaFin=date(2026, 6, 30),
            fechaInicioMatricula=date(2026, 1, 15),
            fechaFinMatricula=date(2026, 2, 10),
            fechaLimiteCancelacion=date(2026, 4, 15),
            estado="ABIERTO",
        )
        self.assertEqual(p.codigo, "2026-1")
        self.assertEqual(p.estado, "ABIERTO")

        # Transición de estado: cerrar y reabrir
        p.estado = "CERRADO"
        self.assertEqual(p.estado, "CERRADO")
        p.estado = "ABIERTO"
        self.assertEqual(p.estado, "ABIERTO")

        # Persistencia en archivo plano estructurado
        with TemporaryDirectory() as tmpdir:
            gp = GestorPersistencia(tmpdir)
            gp.guardar_entidad([p], PeriodoAcademico)
            cargados = gp.cargar_entidad(PeriodoAcademico)
            self.assertEqual(len(cargados), 1)
            self.assertEqual(cargados[0].codigo, "2026-1")
            self.assertEqual(cargados[0].estado, "ABIERTO")
            self.assertEqual(cargados[0].anio, 2026)

    def test_plan_estudio_malla_curricular_completa(self):
        """Valida creación de plan de estudio, inclusión de asignaturas en malla, créditos y versiones."""
        c1 = Curso(1, codigoCurso="SIS-301", nombre="Estructuras de Datos", numeroCreditos=3)
        c2 = Curso(2, codigoCurso="SIS-401", nombre="Sistemas Operativos", numeroCreditos=4)
        prog = ProgramaAcademico(1, codigoPrograma="SIS", nombre="Ingeniería de Sistemas")
        gestor = GestorAcademico([], [], [c1, c2], [], [prog])

        # Crear Plan
        plan = gestor.crear_plan(PlanEstudio(
            codigo="PLAN-SIS-2026",
            nombre="Plan de Estudios Sistemas 2026",
            version="V1",
            idPrograma=1,
            fechaInicioVigencia=date(2026, 1, 1),
            totalCreditos=0,
            estado="ACTIVO",
        ))
        self.assertEqual(plan.codigo, "PLAN-SIS-2026")
        self.assertEqual(plan.estado, "ACTIVO")

        # Incluir Asignaturas a la Malla Curricular
        det1 = gestor.incluir_curso(plan.idPlanEstudio, c1.idCurso, semestre_sugerido=3, es_obligatorio=True)
        det2 = gestor.incluir_curso(plan.idPlanEstudio, c2.idCurso, semestre_sugerido=4, es_obligatorio=True)
        self.assertEqual(plan.totalCreditos, 7)
        self.assertEqual(len(gestor.detalles_planes), 2)
        self.assertEqual(det1.semestreSugerido, 3)
        self.assertEqual(det2.semestreSugerido, 4)

        # Desactivación / Reactivación de versión del plan
        gestor.desactivar_plan(plan.idPlanEstudio)
        self.assertEqual(plan.estado, "INACTIVO")
        plan.estado = "ACTIVO"
        self.assertEqual(plan.estado, "ACTIVO")

        # Persistencia y verificación de integridad referencial
        with TemporaryDirectory() as tmpdir:
            gp = GestorPersistencia(tmpdir)
            gp.guardar_todos_los_datos({
                Facultad: [Facultad(1, codigoFacultad="FIT", nombre="Ingenierias")],
                ProgramaAcademico: [prog],
                Curso: [c1, c2],
                PlanEstudio: [plan],
                DetallePlanEstudio: gestor.detalles_planes,
            })
            cargados = gp.cargar_todos_los_datos()
            self.assertEqual(len(cargados[PlanEstudio]), 1)
            self.assertEqual(len(cargados[DetallePlanEstudio]), 2)
            self.assertEqual(cargados[PlanEstudio][0].totalCreditos, 7)

    def test_integracion_controller_periodos_y_planes(self):
        """Valida que PITAController cargue adecuadamente períodos y planes de estudio."""
        from ui_gui.gui_controller import PITAController
        ctrl = PITAController()
        self.assertTrue(len(ctrl.periodos_academicos) >= 1)
        periodo_actual = next((p for p in ctrl.periodos_academicos if p.codigo == "2026-1"), None)
        self.assertIsNotNone(periodo_actual)
        self.assertIn(periodo_actual.estado, ["ABIERTO", "ACTIVO"])

        self.assertTrue(len(ctrl.planes) >= 1)
        plan_actual = next((pl for pl in ctrl.planes if "SIS" in (pl.codigo or "")), None)
        self.assertIsNotNone(plan_actual)
        self.assertEqual(plan_actual.estado, "ACTIVO")

    def test_gui_pestanas_periodos_y_planes(self):
        """Valida la presencia e inicialización de las pestañas de Períodos y Planes en AcademicaViewGUI."""
        import customtkinter as ctk
        from ui_gui.gui_controller import PITAController
        from ui_gui.view_academica_gui import AcademicaViewGUI
        app = ctk.CTk()
        ctrl = PITAController()
        view = AcademicaViewGUI(app, ctrl)
        self.assertTrue(hasattr(view, "tab_periodos"))
        self.assertTrue(hasattr(view, "tab_planes"))
        app.destroy()


if __name__ == "__main__":
    unittest.main(verbosity=2)
