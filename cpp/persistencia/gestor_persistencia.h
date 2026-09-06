#ifndef GESTOR_PERSISTENCIA_H
#define GESTOR_PERSISTENCIA_H

#include <string>
#include <vector>
#include <unordered_set>
#include <sstream>
#include <fstream>
#include <iostream>
#include <iomanip>
#include "../dominio/lista_enlazada.h"
#include "../dominio/modelo_datos.h"

namespace pita {

struct DatosSistema {
    ListaEnlazada<Universidad> universidades;
    ListaEnlazada<Facultad> facultades;
    ListaEnlazada<ProgramaAcademico> programas;
    ListaEnlazada<PlanEstudio> planesEstudio;
    ListaEnlazada<DetallePlanEstudio> detallesPlanEstudio;
    ListaEnlazada<Curso> cursos;
    ListaEnlazada<Prerrequisito> prerrequisitos;
    ListaEnlazada<Persona> personas;
    ListaEnlazada<Estudiante> estudiantes;
    ListaEnlazada<Profesor> profesores;
    ListaEnlazada<Administrativo> administrativos;
    ListaEnlazada<PeriodoAcademico> periodosAcademicos;
    ListaEnlazada<OfertaCurso> ofertasCurso;
    ListaEnlazada<AsignacionDocente> asignacionesDocentes;
    ListaEnlazada<Horario> horarios;
    ListaEnlazada<MatriculaAcademica> matriculas;
    ListaEnlazada<DetalleMatricula> detallesMatricula;
    ListaEnlazada<Evaluacion> evaluaciones;
    ListaEnlazada<Calificacion> calificaciones;
    ListaEnlazada<AlertaAcademica> alertasAcademicas;
    ListaEnlazada<Contrato> contratos;
    ListaEnlazada<CategoriaDocente> categoriasDocentes;
    ListaEnlazada<FactorSalarial> factoresSalariales;
    ListaEnlazada<ProduccionAcademica> produccionesAcademicas;
    ListaEnlazada<PeriodoNomina> periodosNomina;
    ListaEnlazada<LiquidacionNomina> liquidacionesNomina;
    ListaEnlazada<ConceptoNomina> conceptosNomina;
    ListaEnlazada<DetalleLiquidacion> detallesLiquidacion;
    ListaEnlazada<ParametroNormativo> parametrosNormativos;
    ListaEnlazada<ArchivoPersistencia> archivosPersistencia;
};

class GestorPersistencia {
public:
    static const char DELIMITADOR = '|';
    std::string directorio;

    explicit GestorPersistencia(const std::string& rutaDirectorio = "datos");

    DatosSistema cargarTodosLosDatos();
    void guardarTodosLosDatos(const DatosSistema& datos);
    static void validarIntegridadDatos(const DatosSistema& datos);

    ListaEnlazada<Universidad> cargarUniversidad();
    void guardarUniversidad(const ListaEnlazada<Universidad>& lista);
    static std::string serializarUniversidad(const Universidad& e);
    static Universidad deserializarUniversidad(const std::string& linea);
    ListaEnlazada<Facultad> cargarFacultad();
    void guardarFacultad(const ListaEnlazada<Facultad>& lista);
    static std::string serializarFacultad(const Facultad& e);
    static Facultad deserializarFacultad(const std::string& linea);
    ListaEnlazada<ProgramaAcademico> cargarProgramaAcademico();
    void guardarProgramaAcademico(const ListaEnlazada<ProgramaAcademico>& lista);
    static std::string serializarProgramaAcademico(const ProgramaAcademico& e);
    static ProgramaAcademico deserializarProgramaAcademico(const std::string& linea);
    ListaEnlazada<PlanEstudio> cargarPlanEstudio();
    void guardarPlanEstudio(const ListaEnlazada<PlanEstudio>& lista);
    static std::string serializarPlanEstudio(const PlanEstudio& e);
    static PlanEstudio deserializarPlanEstudio(const std::string& linea);
    ListaEnlazada<DetallePlanEstudio> cargarDetallePlanEstudio();
    void guardarDetallePlanEstudio(const ListaEnlazada<DetallePlanEstudio>& lista);
    static std::string serializarDetallePlanEstudio(const DetallePlanEstudio& e);
    static DetallePlanEstudio deserializarDetallePlanEstudio(const std::string& linea);
    ListaEnlazada<Curso> cargarCurso();
    void guardarCurso(const ListaEnlazada<Curso>& lista);
    static std::string serializarCurso(const Curso& e);
    static Curso deserializarCurso(const std::string& linea);
    ListaEnlazada<Prerrequisito> cargarPrerrequisito();
    void guardarPrerrequisito(const ListaEnlazada<Prerrequisito>& lista);
    static std::string serializarPrerrequisito(const Prerrequisito& e);
    static Prerrequisito deserializarPrerrequisito(const std::string& linea);
    ListaEnlazada<Persona> cargarPersona();
    void guardarPersona(const ListaEnlazada<Persona>& lista);
    static std::string serializarPersona(const Persona& e);
    static Persona deserializarPersona(const std::string& linea);
    ListaEnlazada<Estudiante> cargarEstudiante();
    void guardarEstudiante(const ListaEnlazada<Estudiante>& lista);
    static std::string serializarEstudiante(const Estudiante& e);
    static Estudiante deserializarEstudiante(const std::string& linea);
    ListaEnlazada<Profesor> cargarProfesor();
    void guardarProfesor(const ListaEnlazada<Profesor>& lista);
    static std::string serializarProfesor(const Profesor& e);
    static Profesor deserializarProfesor(const std::string& linea);
    ListaEnlazada<Administrativo> cargarAdministrativo();
    void guardarAdministrativo(const ListaEnlazada<Administrativo>& lista);
    static std::string serializarAdministrativo(const Administrativo& e);
    static Administrativo deserializarAdministrativo(const std::string& linea);
    ListaEnlazada<PeriodoAcademico> cargarPeriodoAcademico();
    void guardarPeriodoAcademico(const ListaEnlazada<PeriodoAcademico>& lista);
    static std::string serializarPeriodoAcademico(const PeriodoAcademico& e);
    static PeriodoAcademico deserializarPeriodoAcademico(const std::string& linea);
    ListaEnlazada<OfertaCurso> cargarOfertaCurso();
    void guardarOfertaCurso(const ListaEnlazada<OfertaCurso>& lista);
    static std::string serializarOfertaCurso(const OfertaCurso& e);
    static OfertaCurso deserializarOfertaCurso(const std::string& linea);
    ListaEnlazada<AsignacionDocente> cargarAsignacionDocente();
    void guardarAsignacionDocente(const ListaEnlazada<AsignacionDocente>& lista);
    static std::string serializarAsignacionDocente(const AsignacionDocente& e);
    static AsignacionDocente deserializarAsignacionDocente(const std::string& linea);
    ListaEnlazada<Horario> cargarHorario();
    void guardarHorario(const ListaEnlazada<Horario>& lista);
    static std::string serializarHorario(const Horario& e);
    static Horario deserializarHorario(const std::string& linea);
    ListaEnlazada<MatriculaAcademica> cargarMatriculaAcademica();
    void guardarMatriculaAcademica(const ListaEnlazada<MatriculaAcademica>& lista);
    static std::string serializarMatriculaAcademica(const MatriculaAcademica& e);
    static MatriculaAcademica deserializarMatriculaAcademica(const std::string& linea);
    ListaEnlazada<DetalleMatricula> cargarDetalleMatricula();
    void guardarDetalleMatricula(const ListaEnlazada<DetalleMatricula>& lista);
    static std::string serializarDetalleMatricula(const DetalleMatricula& e);
    static DetalleMatricula deserializarDetalleMatricula(const std::string& linea);
    ListaEnlazada<Evaluacion> cargarEvaluacion();
    void guardarEvaluacion(const ListaEnlazada<Evaluacion>& lista);
    static std::string serializarEvaluacion(const Evaluacion& e);
    static Evaluacion deserializarEvaluacion(const std::string& linea);
    ListaEnlazada<Calificacion> cargarCalificacion();
    void guardarCalificacion(const ListaEnlazada<Calificacion>& lista);
    static std::string serializarCalificacion(const Calificacion& e);
    static Calificacion deserializarCalificacion(const std::string& linea);
    ListaEnlazada<AlertaAcademica> cargarAlertaAcademica();
    void guardarAlertaAcademica(const ListaEnlazada<AlertaAcademica>& lista);
    static std::string serializarAlertaAcademica(const AlertaAcademica& e);
    static AlertaAcademica deserializarAlertaAcademica(const std::string& linea);
    ListaEnlazada<Contrato> cargarContrato();
    void guardarContrato(const ListaEnlazada<Contrato>& lista);
    static std::string serializarContrato(const Contrato& e);
    static Contrato deserializarContrato(const std::string& linea);
    ListaEnlazada<CategoriaDocente> cargarCategoriaDocente();
    void guardarCategoriaDocente(const ListaEnlazada<CategoriaDocente>& lista);
    static std::string serializarCategoriaDocente(const CategoriaDocente& e);
    static CategoriaDocente deserializarCategoriaDocente(const std::string& linea);
    ListaEnlazada<FactorSalarial> cargarFactorSalarial();
    void guardarFactorSalarial(const ListaEnlazada<FactorSalarial>& lista);
    static std::string serializarFactorSalarial(const FactorSalarial& e);
    static FactorSalarial deserializarFactorSalarial(const std::string& linea);
    ListaEnlazada<ProduccionAcademica> cargarProduccionAcademica();
    void guardarProduccionAcademica(const ListaEnlazada<ProduccionAcademica>& lista);
    static std::string serializarProduccionAcademica(const ProduccionAcademica& e);
    static ProduccionAcademica deserializarProduccionAcademica(const std::string& linea);
    ListaEnlazada<PeriodoNomina> cargarPeriodoNomina();
    void guardarPeriodoNomina(const ListaEnlazada<PeriodoNomina>& lista);
    static std::string serializarPeriodoNomina(const PeriodoNomina& e);
    static PeriodoNomina deserializarPeriodoNomina(const std::string& linea);
    ListaEnlazada<LiquidacionNomina> cargarLiquidacionNomina();
    void guardarLiquidacionNomina(const ListaEnlazada<LiquidacionNomina>& lista);
    static std::string serializarLiquidacionNomina(const LiquidacionNomina& e);
    static LiquidacionNomina deserializarLiquidacionNomina(const std::string& linea);
    ListaEnlazada<ConceptoNomina> cargarConceptoNomina();
    void guardarConceptoNomina(const ListaEnlazada<ConceptoNomina>& lista);
    static std::string serializarConceptoNomina(const ConceptoNomina& e);
    static ConceptoNomina deserializarConceptoNomina(const std::string& linea);
    ListaEnlazada<DetalleLiquidacion> cargarDetalleLiquidacion();
    void guardarDetalleLiquidacion(const ListaEnlazada<DetalleLiquidacion>& lista);
    static std::string serializarDetalleLiquidacion(const DetalleLiquidacion& e);
    static DetalleLiquidacion deserializarDetalleLiquidacion(const std::string& linea);
    ListaEnlazada<ParametroNormativo> cargarParametroNormativo();
    void guardarParametroNormativo(const ListaEnlazada<ParametroNormativo>& lista);
    static std::string serializarParametroNormativo(const ParametroNormativo& e);
    static ParametroNormativo deserializarParametroNormativo(const std::string& linea);
    ListaEnlazada<ArchivoPersistencia> cargarArchivoPersistencia();
    void guardarArchivoPersistencia(const ListaEnlazada<ArchivoPersistencia>& lista);
    static std::string serializarArchivoPersistencia(const ArchivoPersistencia& e);
    static ArchivoPersistencia deserializarArchivoPersistencia(const std::string& linea);

    // Helpers
    static std::vector<std::string> split(const std::string& s, char delim);
    static std::string doubleToString(double val);
    static std::optional<int> parseOptionalInt(const std::string& s);
    static std::optional<double> parseOptionalDouble(const std::string& s);
    static std::optional<bool> parseOptionalBool(const std::string& s);
    static std::optional<std::string> parseOptionalString(const std::string& s);
    static std::optional<EstadoAcademico> parseOptionalEstadoAcademico(const std::string& s);
    static std::optional<TipoProfesor> parseOptionalTipoProfesor(const std::string& s);
    static std::optional<Dedicacion> parseOptionalDedicacion(const std::string& s);
    static std::optional<EstadoCurso> parseOptionalEstadoCurso(const std::string& s);
    static std::optional<CategoriaDocenteCodigo> parseOptionalCategoriaDocente(const std::string& s);
    static std::optional<TipoFactor> parseOptionalTipoFactor(const std::string& s);
    static std::optional<ParametroNormativoCodigo> parseOptionalParametroNormativo(const std::string& s);
};

} // namespace pita

#endif // GESTOR_PERSISTENCIA_H
