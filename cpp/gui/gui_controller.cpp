#include "gui_controller.h"
#include <iostream>

namespace pita {

GUIController::GUIController(const std::string& dirDatos)
    : directorioDatos(dirDatos), persistencia(dirDatos) {
    cargarDatos();
}

void GUIController::cargarDatos() {
    try {
        datos = persistencia.cargarTodosLosDatos();
        inicializarGestores();
        datosDisponibles = true;
        setMensaje("Datos cargados correctamente desde " + directorioDatos);
    } catch (const std::exception& e) {
        datosDisponibles = false;
        setMensaje(std::string("Error al cargar datos: ") + e.what(), true);
    }
}

void GUIController::guardarDatos() {
    try {
        persistencia.guardarTodosLosDatos(datos);
        setMensaje("Datos guardados exitosamente.");
    } catch (const std::exception& e) {
        setMensaje(std::string("Error al guardar: ") + e.what(), true);
    }
}

void GUIController::iniciarSinDatos() {
    ListaEnlazada<ParametroNormativo> params = datos.parametrosNormativos;
    ListaEnlazada<ConceptoNomina> conceptos = datos.conceptosNomina;
    datos = DatosSistema();
    datos.parametrosNormativos = params;
    datos.conceptosNomina = conceptos;
    inicializarGestores();
    datosDisponibles = true;
    setMensaje("Sistema iniciado en limpio (0 datos operativos). Listo para ingresar datos desde cero.");
}

void GUIController::inicializarGestores() {
    gestorPersonas = std::make_unique<GestorPersonas>(
        datos.personas, datos.estudiantes, datos.profesores,
        datos.administrativos, datos.programas, datos.planesEstudio
    );

    gestorAcademico = std::make_unique<GestorAcademico>(
        datos.planesEstudio, datos.detallesPlanEstudio, datos.cursos,
        datos.prerrequisitos, datos.programas, datos.horarios,
        datos.asignacionesDocentes, datos.profesores, datos.ofertasCurso
    );

    gestorContratos = std::make_unique<GestorContratos>(
        datos.contratos, datos.profesores, datos.administrativos,
        datos.liquidacionesNomina
    );

    gestorParametros = std::make_unique<GestorParametros>(
        datos.parametrosNormativos, datos.liquidacionesNomina
    );

    gestorPeriodos = std::make_unique<GestorPeriodosAcademicos>(
        datos.periodosAcademicos, datos.ofertasCurso
    );

    gestorFactores = std::make_unique<GestorFactores>(
        datos.categoriasDocentes, datos.factoresSalariales,
        datos.produccionesAcademicas, datos.profesores
    );

    gestorMatriculas = std::make_unique<GestorMatriculas>(
        datos.estudiantes, datos.periodosAcademicos, datos.ofertasCurso,
        datos.cursos, datos.matriculas, datos.detallesMatricula,
        datos.horarios, datos.parametrosNormativos, datos.prerrequisitos,
        datos.alertasAcademicas
    );

    gestorCalificaciones = std::make_unique<GestorCalificaciones>(
        datos.evaluaciones, datos.calificaciones, datos.detallesMatricula,
        datos.matriculas, datos.estudiantes, datos.ofertasCurso,
        datos.cursos, *gestorMatriculas
    );

    gestorNomina = std::make_unique<GestorNomina>(
        datos.contratos, datos.profesores, datos.periodosNomina,
        datos.liquidacionesNomina, datos.parametrosNormativos,
        datos.detallesLiquidacion, datos.categoriasDocentes,
        datos.factoresSalariales, datos.produccionesAcademicas
    );
}

void GUIController::setMensaje(const std::string& msg, bool error) {
    ultimoMensaje = msg;
    hayError = error;
}

void GUIController::limpiarMensaje() {
    ultimoMensaje.clear();
    hayError = false;
}

} // namespace pita
