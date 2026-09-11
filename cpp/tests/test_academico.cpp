#include <gtest/gtest.h>
#include <filesystem>
#include "../dominio/modelo_datos.h"
#include "../dominio/lista_enlazada.h"
#include "../gestores/gestores_academicos.h"
#include "../gestores/gestor_academico.h"
#include "../gestores/gestor_periodos.h"
#include "../gui/gui_controller.h"

using namespace pita;

class TestAcademico : public ::testing::Test {
protected:
    ListaEnlazada<Estudiante> estudiantes;
    ListaEnlazada<PeriodoAcademico> periodos;
    ListaEnlazada<OfertaCurso> ofertas;
    ListaEnlazada<Curso> cursos;
    ListaEnlazada<MatriculaAcademica> matriculas;
    ListaEnlazada<DetalleMatricula> detalles;
    ListaEnlazada<Horario> horarios;
    ListaEnlazada<ParametroNormativo> parametros;
    ListaEnlazada<Prerrequisito> prerrequisitos;
    ListaEnlazada<AlertaAcademica> alertas;
    ListaEnlazada<Evaluacion> evaluaciones;
    ListaEnlazada<Calificacion> calificaciones;

    void SetUp() override {
        Estudiante est;
        est.idEstudiante = 1;
        est.estadoAcademico = EstadoAcademico::ACTIVO;
        est.estado = "ACTIVO";
        estudiantes.push_back(est);

        PeriodoAcademico per;
        per.idPeriodo = 1;
        per.codigo = "2026-1";
        per.estado = "ACTIVO";
        per.fechaInicioMatricula = "2026-01-01";
        per.fechaFinMatricula = "2026-12-31";
        periodos.push_back(per);

        Curso c1;
        c1.idCurso = 1;
        c1.codigoCurso = "CUR-01";
        c1.numeroCreditos = 3;
        c1.estado = "ACTIVO";
        cursos.push_back(c1);

        Curso c2;
        c2.idCurso = 2;
        c2.codigoCurso = "CUR-02";
        c2.numeroCreditos = 3;
        c2.estado = "ACTIVO";
        cursos.push_back(c2);

        OfertaCurso of1;
        of1.idOfertaCurso = 1;
        of1.idCurso = 1;
        of1.idPeriodo = 1;
        of1.cupoDisponible = 1;
        of1.cupoMaximo = 1;
        of1.estado = "ACTIVO";
        ofertas.push_back(of1);

        OfertaCurso of2;
        of2.idOfertaCurso = 2;
        of2.idCurso = 2;
        of2.idPeriodo = 1;
        of2.cupoDisponible = 1;
        of2.cupoMaximo = 1;
        of2.estado = "ACTIVO";
        ofertas.push_back(of2);
    }
};

TEST_F(TestAcademico, MatriculaCancelacionCupoYCruce) {
    // Horario 1: LUNES 08:00 - 10:00
    Horario h1;
    h1.idHorario = 1;
    h1.idOfertaCurso = 1;
    h1.diaSemana = "LUNES";
    h1.horaInicio = "08:00";
    h1.horaFin = "10:00";
    horarios.push_back(h1);

    // Horario 2: LUNES 09:00 - 11:00 (Cruce con Horario 1)
    Horario h2;
    h2.idHorario = 2;
    h2.idOfertaCurso = 2;
    h2.diaSemana = "LUNES";
    h2.horaInicio = "09:00";
    h2.horaFin = "11:00";
    horarios.push_back(h2);

    GestorMatriculas gestor(
        estudiantes, periodos, ofertas, cursos,
        matriculas, detalles, horarios, parametros,
        prerrequisitos, alertas
    );

    // Matricular Oferta 1 exitosamente
    DetalleMatricula& dm1 = gestor.matricularCurso(1, 1, "2026-02-01");
    EXPECT_EQ(*dm1.idOfertaCurso, 1);
    EXPECT_EQ(ofertas.front().cupoDisponible.value_or(0), 0);

    // Intentar matricular Oferta 2 (Debe fallar por cruce de horario)
    EXPECT_THROW(gestor.matricularCurso(1, 2, "2026-02-01"), ErrorMatricula);

    // Cancelar curso 1 y validar que se restablezca el cupo
    gestor.cancelarCurso(1, 1, "Horario laboral", "2026-02-02");
    EXPECT_EQ(ofertas.front().cupoDisponible.value_or(0), 1);
}

TEST_F(TestAcademico, CalificacionPonderadaYEbra) {
    GestorMatriculas gestorMatr(
        estudiantes, periodos, ofertas, cursos,
        matriculas, detalles, horarios, parametros,
        prerrequisitos, alertas
    );

    // Crear matrícula y detalle
    MatriculaAcademica matr;
    matr.idMatricula = 1;
    matr.idEstudiante = 1;
    matr.idPeriodo = 1;
    matriculas.push_back(matr);

    DetalleMatricula det;
    det.idDetalleMatricula = 1;
    det.idMatricula = 1;
    det.idOfertaCurso = 1;
    det.estadoCurso = EstadoCurso::MATRICULADO;
    detalles.push_back(det);

    Evaluacion ev1; ev1.idEvaluacion = 1; ev1.idOfertaCurso = 1; ev1.porcentaje = 30.0; ev1.estado = "ACTIVO";
    Evaluacion ev2; ev2.idEvaluacion = 2; ev2.idOfertaCurso = 1; ev2.porcentaje = 30.0; ev2.estado = "ACTIVO";
    Evaluacion ev3; ev3.idEvaluacion = 3; ev3.idOfertaCurso = 1; ev3.porcentaje = 40.0; ev3.estado = "ACTIVO";
    evaluaciones.push_back(ev1);
    evaluaciones.push_back(ev2);
    evaluaciones.push_back(ev3);

    ParametroNormativo pMinEbra;
    pMinEbra.codigo = ParametroNormativoCodigo::PROMEDIO_MINIMO_EBRA;
    pMinEbra.valor = "3.0";
    parametros.push_back(pMinEbra);

    GestorCalificaciones gestorCalif(
        evaluaciones, calificaciones, detalles,
        matriculas, estudiantes, ofertas,
        cursos, gestorMatr
    );

    gestorCalif.registrarCalificacion(1, 1, 2.0);
    gestorCalif.registrarCalificacion(2, 1, 2.0);
    gestorCalif.registrarCalificacion(3, 1, 2.0);

    EXPECT_NEAR(detalles.front().notaFinal.value_or(0.0), 2.00, 0.01);

    AlertaAcademica* alerta = gestorMatr.evaluarEbra(1);
    ASSERT_NE(alerta, nullptr);
    EXPECT_EQ(estudiantes.front().estadoAcademico, EstadoAcademico::EBRA);
}

TEST(TestOperacionesAcademicas, PeriodosYOfertasConsultablesYModificables) {
    ListaEnlazada<PeriodoAcademico> periodos;
    PeriodoAcademico p;
    p.idPeriodo = 1;
    p.codigo = "2026-1";
    p.nombre = "2026-1";
    p.estado = "ABIERTO";
    periodos.push_back(p);

    ListaEnlazada<OfertaCurso> ofertas;
    OfertaCurso of;
    of.idOfertaCurso = 1;
    of.idCurso = 1;
    of.idPeriodo = 1;
    of.grupo = "A";
    of.cupoMaximo = 30;
    of.cupoDisponible = 20;
    of.estado = "ACTIVO";
    ofertas.push_back(of);

    GestorPeriodosAcademicos gestor(periodos, ofertas);

    EXPECT_NE(gestor.consultarPeriodo(1), nullptr);
    EXPECT_EQ(gestor.consultarOfertasPeriodo(1).size(), 1u);

    OfertaCurso cambios;
    cambios.grupo = "B";
    cambios.cupoMaximo = 25;
    cambios.cupoDisponible = 15;
    OfertaCurso& mod = gestor.modificarOferta(1, 1, cambios);
    EXPECT_EQ(mod.grupo.value_or(""), "B");
    EXPECT_EQ(mod.cupoDisponible.value_or(0), 15);

    // Cupo disponible mayor que cupo máximo debe fallar
    OfertaCurso invalida;
    invalida.cupoDisponible = 26;
    invalida.cupoMaximo = 25;
    EXPECT_THROW(gestor.modificarOferta(1, 1, invalida), ErrorPeriodo);

    // Cerrar período bloquea reabrirlo directamente
    gestor.cerrarPeriodo(1);
    EXPECT_THROW(gestor.abrirPeriodo(1), ErrorPeriodo);
}

TEST(TestAcademicoEstructura, PlanYPrerrequisito) {
    ListaEnlazada<PlanEstudio> planes;
    ListaEnlazada<DetallePlanEstudio> detalles;
    ListaEnlazada<Curso> cursos;
    ListaEnlazada<Prerrequisito> prereqs;
    ListaEnlazada<ProgramaAcademico> programas;
    ListaEnlazada<Horario> horarios;
    ListaEnlazada<AsignacionDocente> asignaciones;
    ListaEnlazada<Profesor> profesores;
    ListaEnlazada<OfertaCurso> ofertas;

    Curso c1; c1.idCurso = 1; c1.numeroCreditos = 3; cursos.push_back(c1);
    Curso c2; c2.idCurso = 2; c2.numeroCreditos = 4; cursos.push_back(c2);

    ProgramaAcademico prog;
    prog.idPrograma = 1;
    prog.codigoPrograma = "SIS";
    prog.nombre = "Ingenieria de Sistemas";
    programas.push_back(prog);

    GestorAcademico gestor(
        planes, detalles, cursos, prereqs,
        programas, horarios, asignaciones, profesores, ofertas
    );

    PlanEstudio p;
    p.idPrograma = 1;
    p.codigo = "PLAN-SIS-2026";
    PlanEstudio& creado = gestor.crearPlan(p);
    int idPlan = *creado.idPlanEstudio;

    gestor.incluirCurso(idPlan, 1, 1, true);
    Prerrequisito pre;
    pre.idCurso = 2;
    pre.idCursoRequerido = 1;
    Prerrequisito& regPre = gestor.registrarPrerrequisito(pre);

    EXPECT_EQ(creado.totalCreditos.value_or(0), 3);
    EXPECT_EQ(*regPre.idPrerrequisito, 1);
}

static std::string resolverRutaDatos() {
    for (const auto& path : {"cpp/datos", "datos", "../datos", "../../datos", "../../cpp/datos"}) {
        if (std::filesystem::exists(path)) {
            return path;
        }
    }
    return "datos";
}

TEST(TestAcademicoEstructura, IntegracionControllerPeriodosYPlanes) {
    // Valida que GUIController cargue adecuadamente períodos y planes desde el almacén de datos
    std::string ruta = resolverRutaDatos();
    GUIController ctrl(ruta);
    EXPECT_TRUE(ctrl.datosDisponibles);
    EXPECT_GE(ctrl.datos.periodosAcademicos.size(), 1u);
    EXPECT_GE(ctrl.datos.planesEstudio.size(), 1u);
}

