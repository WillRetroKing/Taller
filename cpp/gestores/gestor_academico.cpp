#include "gestor_academico.h"
#include <ctime>
#include <iomanip>
#include <sstream>

namespace pita {

static std::string fecha_hoy() {
    std::time_t t = std::time(nullptr);
    std::tm tm = *std::localtime(&t);
    std::ostringstream oss;
    oss << std::put_time(&tm, "%Y-%m-%d");
    return oss.str();
}

GestorAcademico::GestorAcademico(
    ListaEnlazada<PlanEstudio>& planes,
    ListaEnlazada<DetallePlanEstudio>& detallesPlanes,
    ListaEnlazada<Curso>& cursos,
    ListaEnlazada<Prerrequisito>& prerrequisitos,
    ListaEnlazada<ProgramaAcademico>& programas,
    ListaEnlazada<Horario>& horarios,
    ListaEnlazada<AsignacionDocente>& asignaciones,
    ListaEnlazada<Profesor>& profesores,
    ListaEnlazada<OfertaCurso>& ofertas
) : planes(planes),
    detallesPlanes(detallesPlanes),
    cursos(cursos),
    prerrequisitos(prerrequisitos),
    programas(programas),
    horarios(horarios),
    asignaciones(asignaciones),
    profesores(profesores),
    ofertas(ofertas) {}

int GestorAcademico::siguienteIdPlan() {
    int maxId = 0;
    for (const auto& p : planes) {
        if (p.idPlanEstudio.has_value() && *p.idPlanEstudio > maxId) {
            maxId = *p.idPlanEstudio;
        }
    }
    return maxId + 1;
}

int GestorAcademico::siguienteIdDetallePlan() {
    int maxId = 0;
    for (const auto& d : detallesPlanes) {
        if (d.idDetallePlan.has_value() && *d.idDetallePlan > maxId) {
            maxId = *d.idDetallePlan;
        }
    }
    return maxId + 1;
}

int GestorAcademico::siguienteIdPrerrequisito() {
    int maxId = 0;
    for (const auto& p : prerrequisitos) {
        if (p.idPrerrequisito.has_value() && *p.idPrerrequisito > maxId) {
            maxId = *p.idPrerrequisito;
        }
    }
    return maxId + 1;
}

int GestorAcademico::siguienteIdAsignacion() {
    int maxId = 0;
    for (const auto& a : asignaciones) {
        if (a.idAsignacion.has_value() && *a.idAsignacion > maxId) {
            maxId = *a.idAsignacion;
        }
    }
    return maxId + 1;
}

int GestorAcademico::siguienteIdHorario() {
    int maxId = 0;
    for (const auto& h : horarios) {
        if (h.idHorario.has_value() && *h.idHorario > maxId) {
            maxId = *h.idHorario;
        }
    }
    return maxId + 1;
}

bool GestorAcademico::seCruzan(const Horario& primero, const Horario& segundo) {
    if (!primero.diaSemana.has_value() || !segundo.diaSemana.has_value()) return false;
    if (*primero.diaSemana != *segundo.diaSemana) return false;
    if (!primero.horaInicio.has_value() || !primero.horaFin.has_value()) return false;
    if (!segundo.horaInicio.has_value() || !segundo.horaFin.has_value()) return false;
    return (*primero.horaInicio < *segundo.horaFin && *segundo.horaInicio < *primero.horaFin);
}

PlanEstudio& GestorAcademico::crearPlan(PlanEstudio plan) {
    if (!plan.idPlanEstudio.has_value()) {
        plan.idPlanEstudio = siguienteIdPlan();
    } else {
        for (const auto& p : planes) {
            if (p.idPlanEstudio.has_value() && *p.idPlanEstudio == *plan.idPlanEstudio) {
                throw ErrorAcademico("Ya existe un plan de estudio con ID " + std::to_string(*plan.idPlanEstudio));
            }
        }
    }

    if (plan.idPrograma.has_value()) {
        bool existeProg = false;
        for (const auto& pr : programas) {
            if (pr.idPrograma.has_value() && *pr.idPrograma == *plan.idPrograma) {
                existeProg = true;
                break;
            }
        }
        if (!existeProg) {
            throw ErrorAcademico("No existe el programa con ID " + std::to_string(*plan.idPrograma));
        }
    }

    if (plan.fechaFinVigencia.has_value() && plan.fechaInicioVigencia.has_value()) {
        if (*plan.fechaFinVigencia < *plan.fechaInicioVigencia) {
            throw ErrorAcademico("La vigencia final del plan no puede preceder a la inicial");
        }
    }

    if (!plan.estado.has_value() || plan.estado->empty()) {
        plan.estado = "ACTIVO";
    }

    planes.push_back(std::move(plan));
    return planes.back();
}

DetallePlanEstudio& GestorAcademico::incluirCurso(int idPlan, int idCurso, int semestreSugerido, bool esObligatorio) {
    PlanEstudio* plan = nullptr;
    for (auto& p : planes) {
        if (p.idPlanEstudio.has_value() && *p.idPlanEstudio == idPlan) {
            plan = &p;
            break;
        }
    }
    if (!plan) {
        throw ErrorAcademico("No existe el plan de estudio con ID " + std::to_string(idPlan));
    }

    Curso* curso = nullptr;
    for (auto& c : cursos) {
        if (c.idCurso.has_value() && *c.idCurso == idCurso) {
            curso = &c;
            break;
        }
    }
    if (!curso) {
        throw ErrorAcademico("No existe el curso con ID " + std::to_string(idCurso));
    }

    if (semestreSugerido < 1) {
        throw ErrorAcademico("El semestre sugerido debe ser positivo");
    }

    for (const auto& d : detallesPlanes) {
        if (d.idPlanEstudio.has_value() && *d.idPlanEstudio == idPlan &&
            d.idCurso.has_value() && *d.idCurso == idCurso) {
            throw ErrorAcademico("El curso ya pertenece a este plan");
        }
    }

    DetallePlanEstudio detalle;
    detalle.idDetallePlan = siguienteIdDetallePlan();
    detalle.idPlanEstudio = idPlan;
    detalle.idCurso = idCurso;
    detalle.semestreSugerido = semestreSugerido;
    detalle.numeroCreditos = curso->numeroCreditos;
    detalle.esObligatorio = esObligatorio;
    detalle.estado = "ACTIVO";

    detallesPlanes.push_back(std::move(detalle));

    int totalCred = 0;
    for (const auto& d : detallesPlanes) {
        if (d.idPlanEstudio.has_value() && *d.idPlanEstudio == idPlan &&
            (!d.estado.has_value() || *d.estado != "INACTIVO")) {
            totalCred += d.numeroCreditos.value_or(0);
        }
    }
    plan->totalCreditos = totalCred;

    return detallesPlanes.back();
}

Prerrequisito& GestorAcademico::registrarPrerrequisito(Prerrequisito prerrequisito) {
    bool cursoExiste = false;
    bool reqExiste = false;
    for (const auto& c : cursos) {
        if (c.idCurso.has_value()) {
            if (prerrequisito.idCurso.has_value() && *c.idCurso == *prerrequisito.idCurso) cursoExiste = true;
            if (prerrequisito.idCursoRequerido.has_value() && *c.idCurso == *prerrequisito.idCursoRequerido) reqExiste = true;
        }
    }
    if (!cursoExiste) {
        throw ErrorAcademico("No existe el curso con ID " + (prerrequisito.idCurso.has_value() ? std::to_string(*prerrequisito.idCurso) : ""));
    }
    if (!reqExiste) {
        throw ErrorAcademico("No existe el curso prerrequisito con ID " + (prerrequisito.idCursoRequerido.has_value() ? std::to_string(*prerrequisito.idCursoRequerido) : ""));
    }

    if (prerrequisito.idCurso == prerrequisito.idCursoRequerido) {
        throw ErrorAcademico("Un curso no puede ser prerrequisito de si mismo");
    }

    for (const auto& p : prerrequisitos) {
        if (p.idCurso == prerrequisito.idCurso && p.idCursoRequerido == prerrequisito.idCursoRequerido) {
            throw ErrorAcademico("El prerrequisito ya esta registrado");
        }
    }

    if (!prerrequisito.idPrerrequisito.has_value()) {
        prerrequisito.idPrerrequisito = siguienteIdPrerrequisito();
    } else {
        for (const auto& p : prerrequisitos) {
            if (p.idPrerrequisito.has_value() && *p.idPrerrequisito == *prerrequisito.idPrerrequisito) {
                throw ErrorAcademico("Ya existe un prerrequisito con ID " + std::to_string(*prerrequisito.idPrerrequisito));
            }
        }
    }

    if (!prerrequisito.estado.has_value() || prerrequisito.estado->empty()) {
        prerrequisito.estado = "ACTIVO";
    }

    prerrequisitos.push_back(std::move(prerrequisito));
    return prerrequisitos.back();
}

std::pair<PlanEstudio*, ListaEnlazada<DetallePlanEstudio>> GestorAcademico::consultarPlan(int idPlan) {
    PlanEstudio* plan = nullptr;
    for (auto& p : planes) {
        if (p.idPlanEstudio.has_value() && *p.idPlanEstudio == idPlan) {
            plan = &p;
            break;
        }
    }
    if (!plan) {
        throw ErrorAcademico("No existe el plan de estudio con ID " + std::to_string(idPlan));
    }

    ListaEnlazada<DetallePlanEstudio> detalles;
    for (const auto& d : detallesPlanes) {
        if (d.idPlanEstudio.has_value() && *d.idPlanEstudio == idPlan) {
            detalles.push_back(d);
        }
    }
    return {plan, detalles};
}

AsignacionDocente& GestorAcademico::asignarProfesor(int idProfesor, int idOferta, double numeroHoras) {
    bool profExiste = false;
    for (const auto& p : profesores) {
        if (p.idProfesor.has_value() && *p.idProfesor == idProfesor) {
            profExiste = true;
            break;
        }
    }
    if (!profExiste) {
        throw ErrorAcademico("No existe el profesor con ID " + std::to_string(idProfesor));
    }

    bool ofertaExiste = false;
    for (const auto& o : ofertas) {
        if (o.idOfertaCurso.has_value() && *o.idOfertaCurso == idOferta) {
            ofertaExiste = true;
            break;
        }
    }
    if (!ofertaExiste) {
        throw ErrorAcademico("No existe la oferta con ID " + std::to_string(idOferta));
    }

    for (const auto& a : asignaciones) {
        if (a.idProfesor.has_value() && *a.idProfesor == idProfesor &&
            a.idOfertaCurso.has_value() && *a.idOfertaCurso == idOferta) {
            throw ErrorAcademico("El profesor ya esta asignado a esta oferta");
        }
    }

    if (numeroHoras <= 0) {
        throw ErrorAcademico("El numero de horas debe ser positivo");
    }

    AsignacionDocente asig;
    asig.idAsignacion = siguienteIdAsignacion();
    asig.idProfesor = idProfesor;
    asig.idOfertaCurso = idOferta;
    asig.numeroHoras = numeroHoras;
    asig.fechaAsignacion = fecha_hoy();
    asig.estado = "ACTIVO";

    asignaciones.push_back(std::move(asig));
    return asignaciones.back();
}

Horario& GestorAcademico::agregarHorario(Horario horario) {
    if (!horario.horaInicio.has_value() || !horario.horaFin.has_value() || *horario.horaInicio >= *horario.horaFin) {
        throw ErrorAcademico("El horario debe tener horas validas y consecutivas");
    }

    for (const auto& existente : horarios) {
        if (existente.idOfertaCurso.has_value() && horario.idOfertaCurso.has_value() &&
            *existente.idOfertaCurso == *horario.idOfertaCurso) {
            if (seCruzan(horario, existente)) {
                throw ErrorAcademico("El horario se cruza con otro horario de la oferta");
            }
        }
    }

    if (!horario.idHorario.has_value()) {
        horario.idHorario = siguienteIdHorario();
    } else {
        for (const auto& h : horarios) {
            if (h.idHorario.has_value() && *h.idHorario == *horario.idHorario) {
                throw ErrorAcademico("Ya existe un horario con ID " + std::to_string(*horario.idHorario));
            }
        }
    }

    horarios.push_back(std::move(horario));
    return horarios.back();
}

PlanEstudio& GestorAcademico::desactivarPlan(int idPlan) {
    for (auto& p : planes) {
        if (p.idPlanEstudio.has_value() && *p.idPlanEstudio == idPlan) {
            p.estado = "INACTIVO";
            return p;
        }
    }
    throw ErrorAcademico("No existe el plan de estudio con ID " + std::to_string(idPlan));
}

} // namespace pita
