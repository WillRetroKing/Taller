#ifndef GESTORES_ACADEMICOS_H
#define GESTORES_ACADEMICOS_H

#include <string>
#include <stdexcept>
#include <optional>
#include <utility>
#include "../dominio/lista_enlazada.h"
#include "../dominio/modelo_datos.h"

namespace pita {

class ErrorMatricula : public std::runtime_error {
public:
    explicit ErrorMatricula(const std::string& mensaje) : std::runtime_error(mensaje) {}
};

class ErrorCalificacion : public std::runtime_error {
public:
    explicit ErrorCalificacion(const std::string& mensaje) : std::runtime_error(mensaje) {}
};

class GestorMatriculas {
public:
    ListaEnlazada<Estudiante>& estudiantes;
    ListaEnlazada<PeriodoAcademico>& periodos;
    ListaEnlazada<OfertaCurso>& ofertas;
    ListaEnlazada<Curso>& cursos;
    ListaEnlazada<MatriculaAcademica>& matriculas;
    ListaEnlazada<DetalleMatricula>& detalles;
    ListaEnlazada<Horario>& horarios;
    ListaEnlazada<ParametroNormativo>& parametros;
    ListaEnlazada<Prerrequisito>& prerrequisitos;
    ListaEnlazada<AlertaAcademica>& alertas;

    GestorMatriculas(
        ListaEnlazada<Estudiante>& estudiantes,
        ListaEnlazada<PeriodoAcademico>& periodos,
        ListaEnlazada<OfertaCurso>& ofertas,
        ListaEnlazada<Curso>& cursos,
        ListaEnlazada<MatriculaAcademica>& matriculas,
        ListaEnlazada<DetalleMatricula>& detalles,
        ListaEnlazada<Horario>& horarios,
        ListaEnlazada<ParametroNormativo>& parametros,
        ListaEnlazada<Prerrequisito>& prerrequisitos,
        ListaEnlazada<AlertaAcademica>& alertas
    );

    DetalleMatricula& matricularCurso(int idEstudiante, int idOferta, const std::string& fechaMatricula = "");
    double calcularPromedioPeriodo(int idMatricula);
    DetalleMatricula& cancelarCurso(int idEstudiante, int idOferta, const std::string& motivo, const std::string& fechaCancelacion = "");
    double calcularPromedioAcumulado(int idEstudiante);
    AlertaAcademica* evaluarEbra(int idEstudiante);
    ListaEnlazada<AlertaAcademica> evaluarAlertasPeriodo(int idPeriodo);

    ListaEnlazada<MatriculaAcademica> consultarMatriculas(
        std::optional<int> idEstudiante = std::nullopt,
        std::optional<int> idPeriodo = std::nullopt,
        const std::string& estado = ""
    ) const;

    ListaEnlazada<DetalleMatricula> consultarDetalleMatricula(int idMatricula) const;
    MatriculaAcademica* consultarMatriculaEstudiantePeriodo(int idEstudiante, int idPeriodo);
    ListaEnlazada<OfertaCurso> listarOfertasDisponibles(int idPeriodo) const;

    static bool esPeriodoAbierto(const PeriodoAcademico& periodo, const std::string& fecha);
    static bool esActivo(const std::optional<std::string>& estado);
    static bool seCruzan(const Horario& primero, const Horario& segundo);

    Curso* cursoDeOferta(int idOferta);

private:
    MatriculaAcademica& obtenerOCrearMatricula(Estudiante& est, PeriodoAcademico& per, const std::string& fecha);
    bool cumplePrerrequisitos(int idEstudiante, int idCurso);
    bool tieneCruceHorario(int idEstudiante, int idOferta, int idPeriodo);
    std::optional<double> parametroDecimal(ParametroNormativoCodigo codigo);
    std::optional<int> ultimoPeriodoDelEstudiante(int idEstudiante);
    int siguienteIdMatricula();
    int siguienteIdDetalle();
    int siguienteIdAlerta();
};

class GestorCalificaciones {
public:
    ListaEnlazada<Evaluacion>& evaluaciones;
    ListaEnlazada<Calificacion>& calificaciones;
    ListaEnlazada<DetalleMatricula>& detalles;
    ListaEnlazada<MatriculaAcademica>& matriculas;
    ListaEnlazada<Estudiante>& estudiantes;
    ListaEnlazada<OfertaCurso>& ofertas;
    ListaEnlazada<Curso>& cursos;
    GestorMatriculas& gestorMatriculas;

    GestorCalificaciones(
        ListaEnlazada<Evaluacion>& evaluaciones,
        ListaEnlazada<Calificacion>& calificaciones,
        ListaEnlazada<DetalleMatricula>& detalles,
        ListaEnlazada<MatriculaAcademica>& matriculas,
        ListaEnlazada<Estudiante>& estudiantes,
        ListaEnlazada<OfertaCurso>& ofertas,
        ListaEnlazada<Curso>& cursos,
        GestorMatriculas& gestorMatriculas
    );

    Calificacion& registrarCalificacion(int idEvaluacion, int idDetalle, double nota, const std::string& fechaRegistro = "");
    double recalcularNotaFinal(int idDetalle);
    Evaluacion& crearEvaluacion(int idOferta, const std::string& nombre, const std::string& tipo, double porcentaje, const std::string& fechaProgramada = "");
    ListaEnlazada<Evaluacion> consultarEvaluacionesOferta(int idOferta) const;
    double porcentajeTotalEvaluaciones(int idOferta) const;
    std::pair<bool, std::string> validarEvaluacionesParaFinal(int idOferta) const;
    Evaluacion& modificarEvaluacion(int idEvaluacion, const std::optional<std::string>& nombre = std::nullopt, const std::optional<double>& porcentaje = std::nullopt, const std::optional<std::string>& fechaProgramada = std::nullopt);

private:
    int siguienteIdCalificacion();
    int siguienteIdEvaluacion();
};

} // namespace pita

#endif // GESTORES_ACADEMICOS_H
