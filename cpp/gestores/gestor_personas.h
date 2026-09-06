#ifndef GESTOR_PERSONAS_H
#define GESTOR_PERSONAS_H

#include <string>
#include <stdexcept>
#include <optional>
#include "../dominio/lista_enlazada.h"
#include "../dominio/modelo_datos.h"

namespace pita {

class ErrorPersona : public std::runtime_error {
public:
    explicit ErrorPersona(const std::string& mensaje) : std::runtime_error(mensaje) {}
};

class GestorPersonas {
public:
    ListaEnlazada<Persona>& personas;
    ListaEnlazada<Estudiante>& estudiantes;
    ListaEnlazada<Profesor>& profesores;
    ListaEnlazada<Administrativo>& administrativos;
    ListaEnlazada<ProgramaAcademico>& programas;
    ListaEnlazada<PlanEstudio>& planesEstudio;

    GestorPersonas(
        ListaEnlazada<Persona>& personas,
        ListaEnlazada<Estudiante>& estudiantes,
        ListaEnlazada<Profesor>& profesores,
        ListaEnlazada<Administrativo>& administrativos,
        ListaEnlazada<ProgramaAcademico>& programas,
        ListaEnlazada<PlanEstudio>& planesEstudio
    );

    Persona& crearPersona(Persona persona);
    Estudiante& crearEstudiante(Estudiante estudiante);
    Profesor& crearProfesor(Profesor profesor);
    Administrativo& crearAdministrativo(Administrativo administrativo);

    Persona* buscarPersonaPorDocumento(const std::string& numeroDocumento);
    Estudiante* buscarEstudiantePorCodigo(const std::string& codigo);
    Profesor* buscarProfesorPorCodigo(const std::string& codigo);

    ListaEnlazada<Estudiante> listarEstudiantesPorPrograma(int idPrograma) const;
    ListaEnlazada<Profesor> listarProfesoresPorPrograma(int idPrograma) const;

    Persona& desactivarPersona(int idPersona);
    Estudiante& desactivarEstudiante(int idEstudiante);
    Profesor& desactivarProfesor(int idProfesor);
    Administrativo& desactivarAdministrativo(int idAdministrativo);

private:
    void verificarPersonaExistente(std::optional<int> idPersona);
    int siguienteIdPersona();
    int siguienteIdEstudiante();
    int siguienteIdProfesor();
    int siguienteIdAdministrativo();
};

} // namespace pita

#endif // GESTOR_PERSONAS_H
