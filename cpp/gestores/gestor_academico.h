#ifndef GESTOR_ACADEMICO_H
#define GESTOR_ACADEMICO_H

#include <string>
#include <stdexcept>
#include <optional>
#include <utility>
#include "../dominio/lista_enlazada.h"
#include "../dominio/modelo_datos.h"

namespace pita {

class ErrorAcademico : public std::runtime_error {
public:
    explicit ErrorAcademico(const std::string& mensaje) : std::runtime_error(mensaje) {}
};

class GestorAcademico {
public:
    ListaEnlazada<PlanEstudio>& planes;
    ListaEnlazada<DetallePlanEstudio>& detallesPlanes;
    ListaEnlazada<Curso>& cursos;
    ListaEnlazada<Prerrequisito>& prerrequisitos;
    ListaEnlazada<ProgramaAcademico>& programas;
    ListaEnlazada<Horario>& horarios;
    ListaEnlazada<AsignacionDocente>& asignaciones;
    ListaEnlazada<Profesor>& profesores;
    ListaEnlazada<OfertaCurso>& ofertas;

    GestorAcademico(
        ListaEnlazada<PlanEstudio>& planes,
        ListaEnlazada<DetallePlanEstudio>& detallesPlanes,
        ListaEnlazada<Curso>& cursos,
        ListaEnlazada<Prerrequisito>& prerrequisitos,
        ListaEnlazada<ProgramaAcademico>& programas,
        ListaEnlazada<Horario>& horarios,
        ListaEnlazada<AsignacionDocente>& asignaciones,
        ListaEnlazada<Profesor>& profesores,
        ListaEnlazada<OfertaCurso>& ofertas
    );

    PlanEstudio& crearPlan(PlanEstudio plan);
    DetallePlanEstudio& incluirCurso(int idPlan, int idCurso, int semestreSugerido, bool esObligatorio = true);
    Prerrequisito& registrarPrerrequisito(Prerrequisito prerrequisito);
    std::pair<PlanEstudio*, ListaEnlazada<DetallePlanEstudio>> consultarPlan(int idPlan);
    AsignacionDocente& asignarProfesor(int idProfesor, int idOferta, double numeroHoras);
    Horario& agregarHorario(Horario horario);
    PlanEstudio& desactivarPlan(int idPlan);

    static bool seCruzan(const Horario& primero, const Horario& segundo);

private:
    int siguienteIdPlan();
    int siguienteIdDetallePlan();
    int siguienteIdPrerrequisito();
    int siguienteIdAsignacion();
    int siguienteIdHorario();
};

} // namespace pita

#endif // GESTOR_ACADEMICO_H
