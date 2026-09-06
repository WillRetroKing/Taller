#include "gestor_personas.h"
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

GestorPersonas::GestorPersonas(
    ListaEnlazada<Persona>& personas,
    ListaEnlazada<Estudiante>& estudiantes,
    ListaEnlazada<Profesor>& profesores,
    ListaEnlazada<Administrativo>& administrativos,
    ListaEnlazada<ProgramaAcademico>& programas,
    ListaEnlazada<PlanEstudio>& planesEstudio
) : personas(personas),
    estudiantes(estudiantes),
    profesores(profesores),
    administrativos(administrativos),
    programas(programas),
    planesEstudio(planesEstudio) {}

int GestorPersonas::siguienteIdPersona() {
    int maxId = 0;
    for (const auto& p : personas) {
        if (p.idPersona.has_value() && *p.idPersona > maxId) {
            maxId = *p.idPersona;
        }
    }
    return maxId + 1;
}

int GestorPersonas::siguienteIdEstudiante() {
    int maxId = 0;
    for (const auto& e : estudiantes) {
        if (e.idEstudiante.has_value() && *e.idEstudiante > maxId) {
            maxId = *e.idEstudiante;
        }
    }
    return maxId + 1;
}

int GestorPersonas::siguienteIdProfesor() {
    int maxId = 0;
    for (const auto& p : profesores) {
        if (p.idProfesor.has_value() && *p.idProfesor > maxId) {
            maxId = *p.idProfesor;
        }
    }
    return maxId + 1;
}

int GestorPersonas::siguienteIdAdministrativo() {
    int maxId = 0;
    for (const auto& a : administrativos) {
        if (a.idAdministrativo.has_value() && *a.idAdministrativo > maxId) {
            maxId = *a.idAdministrativo;
        }
    }
    return maxId + 1;
}

void GestorPersonas::verificarPersonaExistente(std::optional<int> idPersona) {
    if (!idPersona.has_value()) {
        throw ErrorPersona("El rol debe estar asociado a una persona");
    }
    for (const auto& p : personas) {
        if (p.idPersona.has_value() && *p.idPersona == *idPersona) {
            return;
        }
    }
    throw ErrorPersona("No existe la persona con ID " + std::to_string(*idPersona));
}

Persona& GestorPersonas::crearPersona(Persona persona) {
    if (!persona.idPersona.has_value()) {
        persona.idPersona = siguienteIdPersona();
    } else {
        for (const auto& p : personas) {
            if (p.idPersona.has_value() && *p.idPersona == *persona.idPersona) {
                throw ErrorPersona("Ya existe una persona con ID " + std::to_string(*persona.idPersona));
            }
        }
    }

    if (!persona.numeroDocumento.has_value() || persona.numeroDocumento->empty()) {
        throw ErrorPersona("El numero de documento es obligatorio");
    }

    for (const auto& p : personas) {
        if (p.numeroDocumento.has_value() && *p.numeroDocumento == *persona.numeroDocumento) {
            throw ErrorPersona("Ya existe el documento " + *persona.numeroDocumento);
        }
    }

    if (!persona.fechaRegistro.has_value() || persona.fechaRegistro->empty()) {
        persona.fechaRegistro = fecha_hoy();
    }
    if (!persona.estado.has_value() || persona.estado->empty()) {
        persona.estado = "ACTIVO";
    }

    personas.push_back(std::move(persona));
    return personas.back();
}

Estudiante& GestorPersonas::crearEstudiante(Estudiante estudiante) {
    verificarPersonaExistente(estudiante.idPersona);

    if (!estudiante.idEstudiante.has_value()) {
        estudiante.idEstudiante = siguienteIdEstudiante();
    } else {
        for (const auto& e : estudiantes) {
            if (e.idEstudiante.has_value() && *e.idEstudiante == *estudiante.idEstudiante) {
                throw ErrorPersona("Ya existe un estudiante con ID " + std::to_string(*estudiante.idEstudiante));
            }
        }
    }

    if (estudiante.codigoEstudiante.has_value() && !estudiante.codigoEstudiante->empty()) {
        for (const auto& e : estudiantes) {
            if (e.codigoEstudiante.has_value() && *e.codigoEstudiante == *estudiante.codigoEstudiante) {
                throw ErrorPersona("Ya existe el codigo de estudiante " + *estudiante.codigoEstudiante);
            }
        }
    }

    if (estudiante.idPrograma.has_value()) {
        bool existeProg = false;
        for (const auto& pr : programas) {
            if (pr.idPrograma.has_value() && *pr.idPrograma == *estudiante.idPrograma) {
                existeProg = true;
                break;
            }
        }
        if (!existeProg) {
            throw ErrorPersona("No existe el programa con ID " + std::to_string(*estudiante.idPrograma));
        }
    }

    if (estudiante.idPlanEstudio.has_value()) {
        bool existePlan = false;
        for (const auto& pl : planesEstudio) {
            if (pl.idPlanEstudio.has_value() && *pl.idPlanEstudio == *estudiante.idPlanEstudio) {
                existePlan = true;
                break;
            }
        }
        if (!existePlan) {
            throw ErrorPersona("No existe el plan de estudio con ID " + std::to_string(*estudiante.idPlanEstudio));
        }
    }

    if (!estudiante.estadoAcademico.has_value()) {
        estudiante.estadoAcademico = EstadoAcademico::ACTIVO;
    }
    if (!estudiante.estado.has_value() || estudiante.estado->empty()) {
        estudiante.estado = "ACTIVO";
    }

    estudiantes.push_back(std::move(estudiante));
    return estudiantes.back();
}

Profesor& GestorPersonas::crearProfesor(Profesor profesor) {
    verificarPersonaExistente(profesor.idPersona);

    if (!profesor.idProfesor.has_value()) {
        profesor.idProfesor = siguienteIdProfesor();
    } else {
        for (const auto& p : profesores) {
            if (p.idProfesor.has_value() && *p.idProfesor == *profesor.idProfesor) {
                throw ErrorPersona("Ya existe un profesor con ID " + std::to_string(*profesor.idProfesor));
            }
        }
    }

    if (profesor.codigoProfesor.has_value() && !profesor.codigoProfesor->empty()) {
        for (const auto& p : profesores) {
            if (p.codigoProfesor.has_value() && *p.codigoProfesor == *profesor.codigoProfesor) {
                throw ErrorPersona("Ya existe el codigo de profesor " + *profesor.codigoProfesor);
            }
        }
    }

    // Regla B5: Evitar registrar múltiples posgrados si ya tiene uno reconocido
    for (const auto& p : profesores) {
        if (p.idProfesor.has_value() && *p.idProfesor == *profesor.idProfesor) {
            if (p.nivelPosgradoReconocido.has_value() && !p.nivelPosgradoReconocido->empty()) {
                throw ErrorPersona("El profesor con ID " + std::to_string(*profesor.idProfesor) +
                                   " ya tiene un posgrado reconocido ('" + *p.nivelPosgradoReconocido +
                                   "'), no se pueden registrar multiples posgrados");
            }
        }
    }

    if (!profesor.estado.has_value() || profesor.estado->empty()) {
        profesor.estado = "ACTIVO";
    }

    profesores.push_back(std::move(profesor));
    return profesores.back();
}

Administrativo& GestorPersonas::crearAdministrativo(Administrativo administrativo) {
    verificarPersonaExistente(administrativo.idPersona);

    if (!administrativo.idAdministrativo.has_value()) {
        administrativo.idAdministrativo = siguienteIdAdministrativo();
    } else {
        for (const auto& a : administrativos) {
            if (a.idAdministrativo.has_value() && *a.idAdministrativo == *administrativo.idAdministrativo) {
                throw ErrorPersona("Ya existe un administrativo con ID " + std::to_string(*administrativo.idAdministrativo));
            }
        }
    }

    if (administrativo.codigoEmpleado.has_value() && !administrativo.codigoEmpleado->empty()) {
        for (const auto& a : administrativos) {
            if (a.codigoEmpleado.has_value() && *a.codigoEmpleado == *administrativo.codigoEmpleado) {
                throw ErrorPersona("Ya existe el codigo de empleado " + *administrativo.codigoEmpleado);
            }
        }
    }

    if (!administrativo.estado.has_value() || administrativo.estado->empty()) {
        administrativo.estado = "ACTIVO";
    }

    administrativos.push_back(std::move(administrativo));
    return administrativos.back();
}

Persona* GestorPersonas::buscarPersonaPorDocumento(const std::string& numeroDocumento) {
    for (auto& p : personas) {
        if (p.numeroDocumento.has_value() && *p.numeroDocumento == numeroDocumento) {
            return &p;
        }
    }
    return nullptr;
}

Estudiante* GestorPersonas::buscarEstudiantePorCodigo(const std::string& codigo) {
    for (auto& e : estudiantes) {
        if (e.codigoEstudiante.has_value() && *e.codigoEstudiante == codigo) {
            return &e;
        }
    }
    return nullptr;
}

Profesor* GestorPersonas::buscarProfesorPorCodigo(const std::string& codigo) {
    for (auto& p : profesores) {
        if (p.codigoProfesor.has_value() && *p.codigoProfesor == codigo) {
            return &p;
        }
    }
    return nullptr;
}

ListaEnlazada<Estudiante> GestorPersonas::listarEstudiantesPorPrograma(int idPrograma) const {
    ListaEnlazada<Estudiante> res;
    for (const auto& e : estudiantes) {
        if (e.idPrograma.has_value() && *e.idPrograma == idPrograma) {
            res.push_back(e);
        }
    }
    return res;
}

ListaEnlazada<Profesor> GestorPersonas::listarProfesoresPorPrograma(int idPrograma) const {
    ListaEnlazada<Profesor> res;
    for (const auto& p : profesores) {
        if (p.idProgramaPrincipal.has_value() && *p.idProgramaPrincipal == idPrograma) {
            res.push_back(p);
        }
    }
    return res;
}

Persona& GestorPersonas::desactivarPersona(int idPersona) {
    for (auto& p : personas) {
        if (p.idPersona.has_value() && *p.idPersona == idPersona) {
            p.estado = "INACTIVO";
            return p;
        }
    }
    throw ErrorPersona("No existe la persona con ID " + std::to_string(idPersona));
}

Estudiante& GestorPersonas::desactivarEstudiante(int idEstudiante) {
    for (auto& e : estudiantes) {
        if (e.idEstudiante.has_value() && *e.idEstudiante == idEstudiante) {
            e.estado = "INACTIVO";
            return e;
        }
    }
    throw ErrorPersona("No existe el estudiante con ID " + std::to_string(idEstudiante));
}

Profesor& GestorPersonas::desactivarProfesor(int idProfesor) {
    for (auto& p : profesores) {
        if (p.idProfesor.has_value() && *p.idProfesor == idProfesor) {
            p.estado = "INACTIVO";
            return p;
        }
    }
    throw ErrorPersona("No existe el profesor con ID " + std::to_string(idProfesor));
}

Administrativo& GestorPersonas::desactivarAdministrativo(int idAdministrativo) {
    for (auto& a : administrativos) {
        if (a.idAdministrativo.has_value() && *a.idAdministrativo == idAdministrativo) {
            a.estado = "INACTIVO";
            return a;
        }
    }
    throw ErrorPersona("No existe el administrativo con ID " + std::to_string(idAdministrativo));
}

} // namespace pita
