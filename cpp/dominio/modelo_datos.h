#ifndef MODELO_DATOS_H
#define MODELO_DATOS_H

#include <string>
#include <optional>
#include <vector>
#include <map>

namespace pita {

// ==========================================
// ENUMS
// ==========================================

enum class EstadoAcademico {
    ASPIRANTE,
    ADMITIDO,
    MATRICULADO,
    ACTIVO,
    INACTIVO,
    RESERVA_CUPO,
    EBRA,
    GRADUADO,
    RETIRADO,
    SUSPENDIDO
};

inline std::string to_string(EstadoAcademico val) {
    switch (val) {
        case EstadoAcademico::ASPIRANTE: return "ASPIRANTE";
        case EstadoAcademico::ADMITIDO: return "ADMITIDO";
        case EstadoAcademico::MATRICULADO: return "MATRICULADO";
        case EstadoAcademico::ACTIVO: return "ACTIVO";
        case EstadoAcademico::INACTIVO: return "INACTIVO";
        case EstadoAcademico::RESERVA_CUPO: return "RESERVA_CUPO";
        case EstadoAcademico::EBRA: return "EBRA";
        case EstadoAcademico::GRADUADO: return "GRADUADO";
        case EstadoAcademico::RETIRADO: return "RETIRADO";
        case EstadoAcademico::SUSPENDIDO: return "SUSPENDIDO";
    }
    return "";
}

inline EstadoAcademico estado_academico_from_string(const std::string& s) {
    if (s == "ASPIRANTE") return EstadoAcademico::ASPIRANTE;
    if (s == "ADMITIDO") return EstadoAcademico::ADMITIDO;
    if (s == "MATRICULADO") return EstadoAcademico::MATRICULADO;
    if (s == "ACTIVO") return EstadoAcademico::ACTIVO;
    if (s == "INACTIVO") return EstadoAcademico::INACTIVO;
    if (s == "RESERVA_CUPO") return EstadoAcademico::RESERVA_CUPO;
    if (s == "EBRA") return EstadoAcademico::EBRA;
    if (s == "GRADUADO") return EstadoAcademico::GRADUADO;
    if (s == "RETIRADO") return EstadoAcademico::RETIRADO;
    return EstadoAcademico::SUSPENDIDO;
}

enum class TipoProfesor {
    PLANTA,
    OCASIONAL,
    CATEDRATICO,
    CATEDRATICO_AD_HONOREM
};

inline std::string to_string(TipoProfesor val) {
    switch (val) {
        case TipoProfesor::PLANTA: return "PLANTA";
        case TipoProfesor::OCASIONAL: return "OCASIONAL";
        case TipoProfesor::CATEDRATICO: return "CATEDRATICO";
        case TipoProfesor::CATEDRATICO_AD_HONOREM: return "CATEDRATICO_AD_HONOREM";
    }
    return "";
}

inline TipoProfesor tipo_profesor_from_string(const std::string& s) {
    if (s == "PLANTA") return TipoProfesor::PLANTA;
    if (s == "OCASIONAL") return TipoProfesor::OCASIONAL;
    if (s == "CATEDRATICO") return TipoProfesor::CATEDRATICO;
    return TipoProfesor::CATEDRATICO_AD_HONOREM;
}

enum class Dedicacion {
    TIEMPO_COMPLETO,
    MEDIO_TIEMPO,
    HORA_CATEDRA
};

inline std::string to_string(Dedicacion val) {
    switch (val) {
        case Dedicacion::TIEMPO_COMPLETO: return "TIEMPO_COMPLETO";
        case Dedicacion::MEDIO_TIEMPO: return "MEDIO_TIEMPO";
        case Dedicacion::HORA_CATEDRA: return "HORA_CATEDRA";
    }
    return "";
}

inline Dedicacion dedicacion_from_string(const std::string& s) {
    if (s == "TIEMPO_COMPLETO") return Dedicacion::TIEMPO_COMPLETO;
    if (s == "MEDIO_TIEMPO") return Dedicacion::MEDIO_TIEMPO;
    return Dedicacion::HORA_CATEDRA;
}

enum class EstadoCurso {
    MATRICULADO,
    EN_CURSO,
    CANCELADO,
    APROBADO,
    REPROBADO,
    RETIRADO,
    HOMOLOGADO,
    VALIDADO
};

inline std::string to_string(EstadoCurso val) {
    switch (val) {
        case EstadoCurso::MATRICULADO: return "MATRICULADO";
        case EstadoCurso::EN_CURSO: return "EN_CURSO";
        case EstadoCurso::CANCELADO: return "CANCELADO";
        case EstadoCurso::APROBADO: return "APROBADO";
        case EstadoCurso::REPROBADO: return "REPROBADO";
        case EstadoCurso::RETIRADO: return "RETIRADO";
        case EstadoCurso::HOMOLOGADO: return "HOMOLOGADO";
        case EstadoCurso::VALIDADO: return "VALIDADO";
    }
    return "";
}

inline EstadoCurso estado_curso_from_string(const std::string& s) {
    if (s == "MATRICULADO") return EstadoCurso::MATRICULADO;
    if (s == "EN_CURSO") return EstadoCurso::EN_CURSO;
    if (s == "CANCELADO") return EstadoCurso::CANCELADO;
    if (s == "APROBADO") return EstadoCurso::APROBADO;
    if (s == "REPROBADO") return EstadoCurso::REPROBADO;
    if (s == "RETIRADO") return EstadoCurso::RETIRADO;
    if (s == "HOMOLOGADO") return EstadoCurso::HOMOLOGADO;
    return EstadoCurso::VALIDADO;
}

enum class CategoriaDocenteCodigo {
    AUXILIAR,
    ASISTENTE,
    ASOCIADO,
    TITULAR,
    NO_CATEGORIZADO
};

inline std::string to_string(CategoriaDocenteCodigo val) {
    switch (val) {
        case CategoriaDocenteCodigo::AUXILIAR: return "AUXILIAR";
        case CategoriaDocenteCodigo::ASISTENTE: return "ASISTENTE";
        case CategoriaDocenteCodigo::ASOCIADO: return "ASOCIADO";
        case CategoriaDocenteCodigo::TITULAR: return "TITULAR";
        case CategoriaDocenteCodigo::NO_CATEGORIZADO: return "NO_CATEGORIZADO";
    }
    return "";
}

inline CategoriaDocenteCodigo categoria_docente_from_string(const std::string& s) {
    if (s == "AUXILIAR") return CategoriaDocenteCodigo::AUXILIAR;
    if (s == "ASISTENTE") return CategoriaDocenteCodigo::ASISTENTE;
    if (s == "ASOCIADO") return CategoriaDocenteCodigo::ASOCIADO;
    if (s == "TITULAR") return CategoriaDocenteCodigo::TITULAR;
    return CategoriaDocenteCodigo::NO_CATEGORIZADO;
}

enum class TipoFactor {
    TITULO_ACADEMICO,
    CATEGORIA_DOCENTE,
    EXPERIENCIA,
    PRODUCTIVIDAD_ACADEMICA,
    DIRECCION_ACADEMICO_ADMINISTRATIVA,
    DESEMPENO_DESTACADO,
    POSGRADO,
    GRUPO_INVESTIGACION,
    SEMILLERO
};

inline std::string to_string(TipoFactor val) {
    switch (val) {
        case TipoFactor::TITULO_ACADEMICO: return "TITULO_ACADEMICO";
        case TipoFactor::CATEGORIA_DOCENTE: return "CATEGORIA_DOCENTE";
        case TipoFactor::EXPERIENCIA: return "EXPERIENCIA";
        case TipoFactor::PRODUCTIVIDAD_ACADEMICA: return "PRODUCTIVIDAD_ACADEMICA";
        case TipoFactor::DIRECCION_ACADEMICO_ADMINISTRATIVA: return "DIRECCION_ACADEMICO_ADMINISTRATIVA";
        case TipoFactor::DESEMPENO_DESTACADO: return "DESEMPENO_DESTACADO";
        case TipoFactor::POSGRADO: return "POSGRADO";
        case TipoFactor::GRUPO_INVESTIGACION: return "GRUPO_INVESTIGACION";
        case TipoFactor::SEMILLERO: return "SEMILLERO";
    }
    return "";
}

inline TipoFactor tipo_factor_from_string(const std::string& s) {
    if (s == "TITULO_ACADEMICO") return TipoFactor::TITULO_ACADEMICO;
    if (s == "CATEGORIA_DOCENTE") return TipoFactor::CATEGORIA_DOCENTE;
    if (s == "EXPERIENCIA") return TipoFactor::EXPERIENCIA;
    if (s == "PRODUCTIVIDAD_ACADEMICA") return TipoFactor::PRODUCTIVIDAD_ACADEMICA;
    if (s == "DIRECCION_ACADEMICO_ADMINISTRATIVA") return TipoFactor::DIRECCION_ACADEMICO_ADMINISTRATIVA;
    if (s == "DESEMPENO_DESTACADO") return TipoFactor::DESEMPENO_DESTACADO;
    if (s == "POSGRADO") return TipoFactor::POSGRADO;
    if (s == "GRUPO_INVESTIGACION") return TipoFactor::GRUPO_INVESTIGACION;
    return TipoFactor::SEMILLERO;
}

enum class ParametroNormativoCodigo {
    SALARIO_MINIMO,
    VALOR_PUNTO_SALARIAL,
    VALOR_AUXILIO_TRANSPORTE_VIGENTE,
    PORCENTAJE_ARL_CLASE_I,
    PORCENTAJE_ARL_CLASE_II,
    PORCENTAJE_SENA,
    PORCENTAJE_ICBF,
    VALOR_HORA_CATEDRA,
    PORCENTAJE_SALUD_TRABAJADOR,
    PORCENTAJE_SALUD_EMPLEADOR,
    PORCENTAJE_PENSION_TRABAJADOR,
    PORCENTAJE_PENSION_EMPLEADOR,
    PORCENTAJE_FONDO_SOLIDARIDAD,
    PORCENTAJE_RIESGOS_LABORALES,
    PORCENTAJE_CAJA_COMPENSACION,
    TOPE_BONIFICACION_SERVICIOS,
    PORCENTAJE_BONIFICACION_SERVICIOS_HASTA_TOPE,
    PORCENTAJE_BONIFICACION_SERVICIOS_SOBRE_TOPE,
    PORCENTAJE_RETENCION_FUENTE,
    BASE_MINIMA_RETENCION_FUENTE,
    PORCENTAJE_ESTAMPILLA,
    RETENCION_FUENTE_SALARIO,
    NOTA_MINIMA_APROBATORIA,
    PROMEDIO_MINIMO_EBRA,
    MAXIMO_CREDITOS_PERIODO
};

inline std::string to_string(ParametroNormativoCodigo val) {
    switch (val) {
        case ParametroNormativoCodigo::SALARIO_MINIMO: return "SALARIO_MINIMO";
        case ParametroNormativoCodigo::VALOR_PUNTO_SALARIAL: return "VALOR_PUNTO_SALARIAL";
        case ParametroNormativoCodigo::VALOR_AUXILIO_TRANSPORTE_VIGENTE: return "VALOR_AUXILIO_TRANSPORTE_VIGENTE";
        case ParametroNormativoCodigo::PORCENTAJE_ARL_CLASE_I: return "PORCENTAJE_ARL_CLASE_I";
        case ParametroNormativoCodigo::PORCENTAJE_ARL_CLASE_II: return "PORCENTAJE_ARL_CLASE_II";
        case ParametroNormativoCodigo::PORCENTAJE_SENA: return "PORCENTAJE_SENA";
        case ParametroNormativoCodigo::PORCENTAJE_ICBF: return "PORCENTAJE_ICBF";
        case ParametroNormativoCodigo::VALOR_HORA_CATEDRA: return "VALOR_HORA_CATEDRA";
        case ParametroNormativoCodigo::PORCENTAJE_SALUD_TRABAJADOR: return "PORCENTAJE_SALUD_TRABAJADOR";
        case ParametroNormativoCodigo::PORCENTAJE_SALUD_EMPLEADOR: return "PORCENTAJE_SALUD_EMPLEADOR";
        case ParametroNormativoCodigo::PORCENTAJE_PENSION_TRABAJADOR: return "PORCENTAJE_PENSION_TRABAJADOR";
        case ParametroNormativoCodigo::PORCENTAJE_PENSION_EMPLEADOR: return "PORCENTAJE_PENSION_EMPLEADOR";
        case ParametroNormativoCodigo::PORCENTAJE_FONDO_SOLIDARIDAD: return "PORCENTAJE_FONDO_SOLIDARIDAD";
        case ParametroNormativoCodigo::PORCENTAJE_RIESGOS_LABORALES: return "PORCENTAJE_RIESGOS_LABORALES";
        case ParametroNormativoCodigo::PORCENTAJE_CAJA_COMPENSACION: return "PORCENTAJE_CAJA_COMPENSACION";
        case ParametroNormativoCodigo::TOPE_BONIFICACION_SERVICIOS: return "TOPE_BONIFICACION_SERVICIOS";
        case ParametroNormativoCodigo::PORCENTAJE_BONIFICACION_SERVICIOS_HASTA_TOPE: return "PORCENTAJE_BONIFICACION_SERVICIOS_HASTA_TOPE";
        case ParametroNormativoCodigo::PORCENTAJE_BONIFICACION_SERVICIOS_SOBRE_TOPE: return "PORCENTAJE_BONIFICACION_SERVICIOS_SOBRE_TOPE";
        case ParametroNormativoCodigo::PORCENTAJE_RETENCION_FUENTE: return "PORCENTAJE_RETENCION_FUENTE";
        case ParametroNormativoCodigo::BASE_MINIMA_RETENCION_FUENTE: return "BASE_MINIMA_RETENCION_FUENTE";
        case ParametroNormativoCodigo::PORCENTAJE_ESTAMPILLA: return "PORCENTAJE_ESTAMPILLA";
        case ParametroNormativoCodigo::RETENCION_FUENTE_SALARIO: return "RETENCION_FUENTE_SALARIO";
        case ParametroNormativoCodigo::NOTA_MINIMA_APROBATORIA: return "NOTA_MINIMA_APROBATORIA";
        case ParametroNormativoCodigo::PROMEDIO_MINIMO_EBRA: return "PROMEDIO_MINIMO_EBRA";
        case ParametroNormativoCodigo::MAXIMO_CREDITOS_PERIODO: return "MAXIMO_CREDITOS_PERIODO";
    }
    return "";
}

inline ParametroNormativoCodigo parametro_normativo_from_string(const std::string& s) {
    if (s == "SALARIO_MINIMO") return ParametroNormativoCodigo::SALARIO_MINIMO;
    if (s == "VALOR_PUNTO_SALARIAL") return ParametroNormativoCodigo::VALOR_PUNTO_SALARIAL;
    if (s == "VALOR_AUXILIO_TRANSPORTE_VIGENTE") return ParametroNormativoCodigo::VALOR_AUXILIO_TRANSPORTE_VIGENTE;
    if (s == "PORCENTAJE_ARL_CLASE_I") return ParametroNormativoCodigo::PORCENTAJE_ARL_CLASE_I;
    if (s == "PORCENTAJE_ARL_CLASE_II") return ParametroNormativoCodigo::PORCENTAJE_ARL_CLASE_II;
    if (s == "PORCENTAJE_SENA") return ParametroNormativoCodigo::PORCENTAJE_SENA;
    if (s == "PORCENTAJE_ICBF") return ParametroNormativoCodigo::PORCENTAJE_ICBF;
    if (s == "VALOR_HORA_CATEDRA") return ParametroNormativoCodigo::VALOR_HORA_CATEDRA;
    if (s == "PORCENTAJE_SALUD_TRABAJADOR") return ParametroNormativoCodigo::PORCENTAJE_SALUD_TRABAJADOR;
    if (s == "PORCENTAJE_SALUD_EMPLEADOR") return ParametroNormativoCodigo::PORCENTAJE_SALUD_EMPLEADOR;
    if (s == "PORCENTAJE_PENSION_TRABAJADOR") return ParametroNormativoCodigo::PORCENTAJE_PENSION_TRABAJADOR;
    if (s == "PORCENTAJE_PENSION_EMPLEADOR") return ParametroNormativoCodigo::PORCENTAJE_PENSION_EMPLEADOR;
    if (s == "PORCENTAJE_FONDO_SOLIDARIDAD") return ParametroNormativoCodigo::PORCENTAJE_FONDO_SOLIDARIDAD;
    if (s == "PORCENTAJE_RIESGOS_LABORALES") return ParametroNormativoCodigo::PORCENTAJE_RIESGOS_LABORALES;
    if (s == "PORCENTAJE_CAJA_COMPENSACION") return ParametroNormativoCodigo::PORCENTAJE_CAJA_COMPENSACION;
    if (s == "TOPE_BONIFICACION_SERVICIOS") return ParametroNormativoCodigo::TOPE_BONIFICACION_SERVICIOS;
    if (s == "PORCENTAJE_BONIFICACION_SERVICIOS_HASTA_TOPE") return ParametroNormativoCodigo::PORCENTAJE_BONIFICACION_SERVICIOS_HASTA_TOPE;
    if (s == "PORCENTAJE_BONIFICACION_SERVICIOS_SOBRE_TOPE") return ParametroNormativoCodigo::PORCENTAJE_BONIFICACION_SERVICIOS_SOBRE_TOPE;
    if (s == "PORCENTAJE_RETENCION_FUENTE") return ParametroNormativoCodigo::PORCENTAJE_RETENCION_FUENTE;
    if (s == "BASE_MINIMA_RETENCION_FUENTE") return ParametroNormativoCodigo::BASE_MINIMA_RETENCION_FUENTE;
    if (s == "PORCENTAJE_ESTAMPILLA") return ParametroNormativoCodigo::PORCENTAJE_ESTAMPILLA;
    if (s == "RETENCION_FUENTE_SALARIO") return ParametroNormativoCodigo::RETENCION_FUENTE_SALARIO;
    if (s == "NOTA_MINIMA_APROBATORIA") return ParametroNormativoCodigo::NOTA_MINIMA_APROBATORIA;
    if (s == "PROMEDIO_MINIMO_EBRA") return ParametroNormativoCodigo::PROMEDIO_MINIMO_EBRA;
    return ParametroNormativoCodigo::MAXIMO_CREDITOS_PERIODO;
}

// ==========================================
// ESTRUCTURAS DE DATOS (CAMPOS EN ORDEN EXACTO)
// ==========================================

struct Universidad {
    std::optional<int> idUniversidad;
    std::optional<std::string> nombre;
    std::optional<std::string> nit;
    std::optional<std::string> codigoInstitucional;
    std::optional<std::string> direccion;
    std::optional<std::string> ciudad;
    std::optional<std::string> departamento;
    std::optional<std::string> telefono;
    std::optional<std::string> correoInstitucional;
    std::optional<std::string> sitioWeb;
    std::optional<std::string> estado;
};

struct Facultad {
    std::optional<int> idFacultad;
    std::optional<std::string> codigoFacultad;
    std::optional<std::string> nombre;
    std::optional<std::string> descripcion;
    std::optional<std::string> ubicacion;
    std::optional<std::string> telefono;
    std::optional<std::string> correo;
    std::optional<int> idDecano;
    std::optional<std::string> fechaCreacion;
    std::optional<std::string> estado;
};

struct ProgramaAcademico {
    std::optional<int> idPrograma;
    std::optional<std::string> codigoPrograma;
    std::optional<std::string> nombre;
    std::optional<std::string> nivelFormacion;
    std::optional<std::string> modalidad;
    std::optional<int> numeroSemestres;
    std::optional<int> totalCreditos;
    std::optional<std::string> registroCalificado;
    std::optional<std::string> fechaCreacion;
    std::optional<int> idDirector;
    std::optional<int> idFacultad;
    std::optional<std::string> estado;
};

struct PlanEstudio {
    std::optional<int> idPlanEstudio;
    std::optional<std::string> codigo;
    std::optional<std::string> nombre;
    std::optional<std::string> version;
    std::optional<std::string> fechaInicioVigencia;
    std::optional<std::string> fechaFinVigencia;
    std::optional<int> totalCreditos;
    std::optional<int> idPrograma;
    std::optional<std::string> estado;
};

struct DetallePlanEstudio {
    std::optional<int> idDetallePlan;
    std::optional<int> idPlanEstudio;
    std::optional<int> idCurso;
    std::optional<int> semestreSugerido;
    std::optional<std::string> tipoCurso;
    std::optional<int> numeroCreditos;
    std::optional<bool> esObligatorio;
    std::optional<std::string> estado;
};

struct Curso {
    std::optional<int> idCurso;
    std::optional<std::string> codigoCurso;
    std::optional<std::string> nombre;
    std::optional<std::string> descripcion;
    std::optional<int> numeroCreditos;
    std::optional<int> horasTeoricas;
    std::optional<int> horasPracticas;
    std::optional<int> horasTrabajoIndependiente;
    std::optional<int> cupoSugerido;
    std::optional<double> notaMinimaAprobatoria;
    std::optional<std::string> estado;
};

struct Prerrequisito {
    std::optional<int> idPrerrequisito;
    std::optional<int> idCurso;
    std::optional<int> idCursoRequerido;
    std::optional<std::string> tipoRequisito;
    std::optional<double> notaMinima;
    std::optional<int> creditosMinimos;
    std::optional<std::string> estado;
};

struct PeriodoAcademico {
    std::optional<int> idPeriodo;
    std::optional<std::string> codigo;
    std::optional<std::string> nombre;
    std::optional<int> anio;
    std::optional<int> numeroPeriodo;
    std::optional<std::string> fechaInicio;
    std::optional<std::string> fechaFin;
    std::optional<std::string> fechaInicioMatricula;
    std::optional<std::string> fechaFinMatricula;
    std::optional<std::string> fechaLimiteCancelacion;
    std::optional<std::string> estado;
};

struct Persona {
    std::optional<int> idPersona;
    std::optional<std::string> tipoDocumento;
    std::optional<std::string> numeroDocumento;
    std::optional<std::string> primerNombre;
    std::optional<std::string> segundoNombre;
    std::optional<std::string> primerApellido;
    std::optional<std::string> segundoApellido;
    std::optional<std::string> fechaNacimiento;
    std::optional<std::string> direccion;
    std::optional<std::string> telefono;
    std::optional<std::string> correoPersonal;
    std::optional<std::string> correoInstitucional;
    std::optional<std::string> ciudadResidencia;
    std::optional<std::string> fechaRegistro;
    std::optional<std::string> estado;
};

struct Estudiante {
    std::optional<int> idEstudiante;
    std::optional<int> idPersona;
    std::optional<std::string> codigoEstudiante;
    std::optional<int> idPrograma;
    std::optional<int> idPlanEstudio;
    std::optional<std::string> fechaIngreso;
    std::optional<int> semestreActual;
    std::optional<int> creditosAprobados;
    std::optional<double> promedioAcumulado;
    std::optional<EstadoAcademico> estadoAcademico;
    std::optional<std::string> estado;
};

struct Profesor {
    std::optional<int> idProfesor;
    std::optional<int> idPersona;
    std::optional<std::string> codigoProfesor;
    std::optional<int> idProgramaPrincipal;
    std::optional<std::string> fechaVinculacion;
    std::optional<TipoProfesor> tipoProfesor;
    std::optional<std::string> categoriaDocente;
    std::optional<Dedicacion> dedicacion;
    std::optional<std::string> maximoNivelEstudio;
    std::optional<std::string> tituloProfesional;
    std::optional<std::string> areaConocimiento;
    std::optional<double> numeroHorasSemanales;
    std::optional<double> puntosSalariales;
    std::optional<std::string> estado;
    std::optional<std::string> regimenSalarial;
    std::optional<std::string> modalidadVinculacion;
    std::optional<bool> perteneceCarreraDocente;
    std::optional<std::string> fechaIngresoCarreraDocente;
    std::optional<std::string> fechaPosesion;
    std::optional<std::string> fechaUltimaVinculacion;
    std::optional<std::string> fechaRetiro;
    std::optional<std::string> motivoRetiro;
    std::optional<std::string> actoAdministrativoIngreso;
    std::optional<std::string> actoAdministrativoRetiro;
    std::optional<double> evaluacionDesempenoAnterior;
    std::optional<bool> puedeSerVinculadoSiguientePeriodo;
    std::optional<int> idCategoriaDocente;
    std::optional<std::string> categoriaReconocida;
    std::optional<std::string> categoriaInstitucionOrigen;
    std::optional<std::string> fechaReconocimientoCategoria;
    std::optional<std::string> actoReconocimientoCategoria;
    std::optional<std::string> categoriaComoInvestigador;
    std::optional<std::string> grupoInvestigacion;
    std::optional<std::string> categoriaGrupoInvestigacion;
    std::optional<bool> perteneceSemillero;
    std::optional<std::string> semilleroInvestigacion;
    std::optional<bool> productividadInvestigativaVigente;
    std::optional<bool> participaProyectoInvestigacionVigente;
    std::optional<std::string> certificacionVicerrectoriaInvestigacion;
    std::optional<std::string> nivelPosgradoReconocido;
    std::optional<std::string> tituloPosgradoReconocido;
    std::optional<std::string> fechaObtencionPosgrado;
    std::optional<bool> tituloConvalidado;
    std::optional<std::string> numeroResolucionConvalidacion;
    std::optional<bool> esEspecializacionClinica;
    std::optional<bool> posgradoRelacionadoConAreaDesempeno;
    std::optional<double> factorBonificacionPosgrado;
    std::optional<std::string> fechaInicioReconocimientoPosgrado;
    std::optional<std::string> fechaFinReconocimientoPosgrado;
    std::optional<double> aniosExperienciaDocenteUniversitaria;
    std::optional<int> periodosExperienciaDocenteUniversitaria;
    std::optional<double> aniosExperienciaInvestigacion;
    std::optional<double> aniosExperienciaProfesional;
    std::optional<double> aniosExperienciaDireccionAcademica;
    std::optional<double> experienciaEquivalenteTiempoCompleto;
    std::optional<bool> experienciaCertificada;
    std::optional<std::string> fechaCorteExperiencia;
    std::optional<double> puntosExperienciaReconocidos;
};

struct Administrativo {
    std::optional<int> idAdministrativo;
    std::optional<int> idPersona;
    std::optional<std::string> codigoEmpleado;
    std::optional<std::string> cargo;
    std::optional<std::string> dependencia;
    std::optional<std::string> categoria;
    std::optional<std::string> tipoContratacion;
    std::optional<std::string> fechaVinculacion;
    std::optional<double> salarioBase;
    std::optional<std::string> estado;
};

struct OfertaCurso {
    std::optional<int> idOfertaCurso;
    std::optional<int> idCurso;
    std::optional<int> idPeriodo;
    std::optional<std::string> grupo;
    std::optional<int> cupoMaximo;
    std::optional<int> cupoDisponible;
    std::optional<std::string> modalidad;
    std::optional<std::string> aula;
    std::optional<std::string> sede;
    std::optional<std::string> fechaInicio;
    std::optional<std::string> fechaFin;
    std::optional<std::string> estado;
};

struct AsignacionDocente {
    std::optional<int> idAsignacion;
    std::optional<int> idProfesor;
    std::optional<int> idOfertaCurso;
    std::optional<std::string> rolDocente;
    std::optional<double> numeroHoras;
    std::optional<double> porcentajeResponsabilidad;
    std::optional<std::string> fechaAsignacion;
    std::optional<std::string> estado;
};

struct Horario {
    std::optional<int> idHorario;
    std::optional<int> idOfertaCurso;
    std::optional<std::string> diaSemana;
    std::optional<std::string> horaInicio;
    std::optional<std::string> horaFin;
    std::optional<std::string> aula;
    std::optional<std::string> sede;
    std::optional<std::string> tipoSesion;
    std::optional<std::string> estado;
};

struct MatriculaAcademica {
    std::optional<int> idMatricula;
    std::optional<int> idEstudiante;
    std::optional<int> idPeriodo;
    std::optional<std::string> fechaMatricula;
    std::optional<int> totalCreditos;
    std::optional<double> promedioPeriodo;
    std::optional<std::string> estadoMatricula;
    std::optional<std::string> observaciones;
};

struct DetalleMatricula {
    std::optional<int> idDetalleMatricula;
    std::optional<int> idMatricula;
    std::optional<int> idOfertaCurso;
    std::optional<std::string> fechaInscripcion;
    std::optional<EstadoCurso> estadoCurso;
    std::optional<double> notaFinal;
    std::optional<int> numeroFallas;
    std::optional<std::string> fechaCancelacion;
    std::optional<std::string> motivoCancelacion;
};

struct Evaluacion {
    std::optional<int> idEvaluacion;
    std::optional<int> idOfertaCurso;
    std::optional<std::string> nombre;
    std::optional<std::string> tipo;
    std::optional<double> porcentaje;
    std::optional<std::string> fechaProgramada;
    std::optional<std::string> descripcion;
    std::optional<std::string> estado;
};

struct Calificacion {
    std::optional<int> idCalificacion;
    std::optional<int> idEvaluacion;
    std::optional<int> idDetalleMatricula;
    std::optional<double> nota;
    std::optional<std::string> fechaRegistro;
    std::optional<std::string> observacion;
    std::optional<std::string> estado;
};

struct AlertaAcademica {
    std::optional<int> idAlerta;
    std::optional<int> idEstudiante;
    std::optional<int> idPeriodo;
    std::optional<std::string> tipoAlerta;
    std::optional<std::string> motivo;
    std::optional<double> valorObservado;
    std::optional<double> valorLimite;
    std::optional<std::string> fechaGeneracion;
    std::optional<bool> atendida;
    std::optional<std::string> observaciones;
    std::optional<std::string> estado;
};

struct Contrato {
    std::optional<int> idContrato;
    std::optional<int> idPersona;
    std::optional<std::string> numeroContrato;
    std::optional<std::string> tipoContrato;
    std::optional<std::string> fechaInicio;
    std::optional<std::string> fechaFin;
    std::optional<Dedicacion> dedicacion;
    std::optional<double> horasSemanales;
    std::optional<double> horasCatedra;
    std::optional<double> valorHora;
    std::optional<bool> aplicaAuxilioTransporte;
    std::optional<double> salarioBase;
    std::optional<std::string> claseARL;
    std::optional<std::string> actoAdministrativo;
    std::optional<std::string> observaciones;
    std::optional<std::string> estado;
    std::optional<std::string> regimenAplicable;
    std::optional<std::string> normaVinculacion;
    std::optional<std::string> articuloNormativo;
    std::optional<std::string> modalidadProfesor;
    std::optional<bool> esEmpleadoPublicoDocente;
    std::optional<bool> perteneceCarreraProfesoral;
    std::optional<bool> esTransitorio;
    std::optional<bool> esRemunerado;
    std::optional<bool> esAdHonorem;
    std::optional<std::string> tipoDedicacion;
    std::optional<double> porcentajeDedicacion;
    std::optional<int> duracionEnMeses;
    std::optional<int> periodoAcademicoInicial;
    std::optional<int> periodoAcademicoFinal;
    std::optional<std::string> tipoActoVinculacion;
    std::optional<std::string> numeroActoVinculacion;
    std::optional<std::string> fechaActoVinculacion;
    std::optional<std::string> fechaPosesion;
    std::optional<std::string> certificadoDisponibilidadPresupuestal;
    std::optional<std::string> numeroCDP;
    std::optional<std::string> fechaCDP;
    std::optional<double> valorDisponibilidadPresupuestal;
    std::optional<std::string> resolucionRectoral;
    std::optional<std::string> fechaResolucionRectoral;
    std::optional<std::string> estadoFormalizacion;
    std::optional<std::string> fechaInicioEfectiva;
    std::optional<std::string> fechaTerminacionEfectiva;
    std::optional<double> horasSemanalesAsignadas;
    std::optional<double> horasMensualesAsignadas;
    std::optional<double> horasDocenciaDirecta;
    std::optional<double> horasActividadesComplementarias;
    std::optional<double> horasMensualesReconocidas;
    std::optional<double> horasMensualesCumplidas;
    std::optional<double> horasIncumplidas;
    std::optional<double> valorHoraIncumplida;
    std::optional<double> valorDescuentoIncumplimiento;
    std::optional<double> limiteHorasSemanales;
    std::optional<bool> requiereCertificacionCumplimiento;
    std::optional<std::string> certificacionCumplimiento;
    std::optional<std::string> fechaCertificacionCumplimiento;
    std::optional<std::string> categoriaDocenteAlVincular;
    std::optional<std::string> nivelPosgradoAlVincular;
    std::optional<std::string> grupoInvestigacionAlVincular;
    std::optional<std::string> categoriaGrupoAlVincular;
    std::optional<std::string> semilleroAlVincular;
    std::optional<double> salarioMinimoVigente;
    std::optional<double> factorSalarialSMMLV;
    std::optional<double> valorHoraCatedraVigente;
    std::optional<std::string> resolucionValorHoraCatedra;
    std::optional<std::string> fechaVigenciaValorHora;
    std::optional<double> salarioMensualPactado;
    std::optional<bool> permiteBonificacionPosgrado;
    std::optional<bool> permiteBonificacionInvestigacion;
    std::optional<bool> permitePrestacionesSociales;
    std::optional<bool> permiteAportesParafiscales;
    std::optional<std::string> causalTerminacion;
    std::optional<std::string> fechaNovedadTerminacion;
    std::optional<std::string> actoTerminacion;
    std::optional<bool> renunciaPresentada;
    std::optional<bool> renunciaAceptada;
    std::optional<bool> necesidadServicioVigente;
    std::optional<bool> incumplimientoComprobado;
    std::optional<std::string> decisionJudicialOAdministrativa;
    std::optional<std::string> documentoSoporteTerminacion;
    std::optional<std::string> estadoFinalContrato;
};

struct CategoriaDocente {
    std::optional<int> idCategoria;
    std::optional<CategoriaDocenteCodigo> codigo;
    std::optional<std::string> nombre;
    std::optional<std::string> descripcion;
    std::optional<double> puntosBase;
    std::optional<double> valorHoraBase;
    std::optional<std::string> nivelJerarquico;
    std::optional<std::string> normaOrigen;
    std::optional<std::string> fechaInicioVigencia;
    std::optional<std::string> fechaFinVigencia;
    std::optional<std::string> estado;
    std::optional<std::string> tipoRegimen;
    std::optional<double> puntosCategoria;
    std::optional<double> factorSalarialTiempoCompleto;
    std::optional<double> factorSalarialMedioTiempo;
    std::optional<std::string> unidadFactorSalarial;
    std::optional<bool> requiereActoReconocimiento;
    std::optional<std::string> actoReconocimiento;
    std::optional<std::string> fechaReconocimiento;
    std::optional<std::string> categoriaAnterior;
    std::optional<std::string> fechaAscenso;
    std::optional<bool> esCategoriaPorDefecto;
    std::optional<bool> permiteReconocimientoCategoriaOrigen;
    std::optional<bool> evaluacionSatisfactoriaInstitucionOrigen;
};

struct FactorSalarial {
    std::optional<int> idFactor;
    std::optional<std::string> nombre;
    std::optional<TipoFactor> tipoFactor;
    std::optional<double> cantidad;
    std::optional<double> puntosReconocidos;
    std::optional<double> valorReconocido;
    std::optional<std::string> fechaReconocimiento;
    std::optional<std::string> actoAdministrativo;
    std::optional<int> idProfesor;
    std::optional<std::string> estado;
    std::optional<std::string> regimenAplicable;
    std::optional<std::string> factorGenerador;
    std::optional<std::string> tipoReconocimiento;
    std::optional<double> puntosSolicitados;
    std::optional<double> puntosAprobados;
    std::optional<double> puntosAcumulables;
    std::optional<double> topeIndividual;
    std::optional<double> topePorCategoria;
    std::optional<double> topeAnual;
    std::optional<int> numeroAutores;
    std::optional<double> factorCoautoria;
    std::optional<bool> requiereEvaluacionPares;
    std::optional<std::string> resultadoEvaluacionPares;
    std::optional<bool> requiereAprobacionComite;
    std::optional<std::string> fechaAprobacionComite;
    std::optional<std::string> actoReconocimiento;
    std::optional<std::string> fechaEfectoSalarial;
    std::optional<bool> esConstitutivoSalario;
    std::optional<bool> integraBasePrestacional;
    std::optional<bool> integraBaseParafiscal;
    std::optional<std::string> vigenciaDesde;
    std::optional<std::string> vigenciaHasta;
};

struct ProduccionAcademica {
    std::optional<int> idProduccion;
    std::optional<int> idProfesor;
    std::optional<std::string> tipoProduccion;
    std::optional<std::string> titulo;
    std::optional<std::string> fechaPublicacion;
    std::optional<std::string> entidadPublicadora;
    std::optional<std::string> identificadorProducto;
    std::optional<double> puntosSolicitados;
    std::optional<double> puntosReconocidos;
    std::optional<std::string> fechaReconocimiento;
    std::optional<std::string> actoAdministrativo;
    std::optional<std::string> estadoValidacion;
    std::optional<std::string> modalidadProducto;
    std::optional<std::string> subtipoProducto;
    std::optional<std::string> nivelImpacto;
    std::optional<std::string> clasificacionRevista;
    std::optional<std::string> isbn;
    std::optional<std::string> issn;
    std::optional<std::string> registroDerechoAutor;
    std::optional<std::string> numeroPatente;
    std::optional<std::string> entidadIndexadora;
    std::optional<int> numeroAutores;
    std::optional<int> posicionAutor;
    std::optional<double> porcentajeParticipacion;
    std::optional<bool> creditoInstitucional;
    std::optional<bool> evaluadoPorPares;
    std::optional<int> cantidadPares;
    std::optional<std::string> resultadoEvaluacion;
    std::optional<double> puntosTotalesProducto;
    std::optional<double> factorCoautoria;
    std::optional<double> puntosReconocidosProfesor;
    std::optional<std::string> tipoReconocimiento;
    std::optional<std::string> fechaActoReconocimiento;
    std::optional<bool> yaReconocidoOtroConcepto;
    std::optional<bool> productoReclasificado;
    std::optional<double> puntosAdicionalesReclasificacion;
    std::optional<std::string> fechaLimiteReclasificacion;
};

struct PeriodoNomina {
    std::optional<int> idPeriodoNomina;
    std::optional<int> anio;
    std::optional<int> mes;
    std::optional<std::string> fechaInicio;
    std::optional<std::string> fechaFin;
    std::optional<std::string> fechaPago;
    std::optional<std::string> estado;
    std::optional<std::string> tipoPeriodicidad;
    std::optional<double> salarioMinimoVigente;
    std::optional<double> valorPuntoSalarialVigente;
    std::optional<std::string> fechaVigenciaValorPunto;
    std::optional<std::string> resolucionValorPunto;
    std::optional<int> diasBaseLiquidacion;
    std::optional<std::string> fechaCorteNovedades;
    std::optional<std::string> fechaCierreNomina;
    std::optional<std::string> fechaAprobacion;
    std::optional<std::string> usuarioAprobador;
    std::optional<double> totalDevengadoPeriodo;
    std::optional<double> totalDescuentosPeriodo;
    std::optional<double> totalPrestacionesPeriodo;
    std::optional<double> totalAportesPatronalesPeriodo;
    std::optional<double> costoTotalPeriodo;
    std::optional<bool> estaCerrado;
    std::optional<bool> permiteReliquidacion;
    std::optional<int> versionLiquidacion;
};

struct LiquidacionNomina {
    std::optional<int> idLiquidacion;
    std::optional<int> idProfesor;
    std::optional<int> idContrato;
    std::optional<int> idPeriodoNomina;
    std::optional<std::string> fechaLiquidacion;
    std::optional<double> salarioBase;
    std::optional<double> totalDevengado;
    std::optional<double> totalDescuentos;
    std::optional<double> totalPrestaciones;
    std::optional<double> baseLiquidacionPrestaciones;
    std::optional<double> baseCotizacionSeguridadSocial;
    std::optional<double> valorAuxilioTransporteCotizado;
    std::optional<double> aportePatronalSENA;
    std::optional<double> aportePatronalICBF;
    std::optional<double> netoPagar;
    std::optional<std::string> estado;
    std::optional<TipoProfesor> tipoProfesorLiquidado;
    std::optional<std::string> regimenLiquidado;
    std::optional<std::string> categoriaLiquidada;
    std::optional<Dedicacion> dedicacionLiquidada;
    std::optional<double> diasTrabajados;
    std::optional<double> diasNoRemunerados;
    std::optional<double> horasAsignadas;
    std::optional<double> horasCumplidas;
    std::optional<double> horasIncumplidas;
    std::optional<double> salarioMinimoUsado;
    std::optional<double> valorPuntoUsado;
    std::optional<double> valorHoraCatedraUsado;
    std::optional<double> factorCategoriaUsado;
    std::optional<double> puntosSalarialesUsados;
    std::optional<double> salarioOrdinario;
    std::optional<double> baseSalarialPrestacional;
    std::optional<double> baseSeguridadSocial;
    std::optional<double> baseParafiscales;
    std::optional<double> bonificacionPosgrado;
    std::optional<double> bonificacionInvestigacion;
    std::optional<double> bonificacionesSalariales;
    std::optional<double> bonificacionesNoSalariales;
    std::optional<double> otrosDevengadosSalariales;
    std::optional<double> otrosDevengadosNoSalariales;
    std::optional<double> ajustesDevengados;
    std::optional<double> descuentoSalud;
    std::optional<double> descuentoPension;
    std::optional<double> fondoSolidaridadPensional;
    std::optional<double> retencionFuente;
    std::optional<double> descuentoHorasIncumplidas;
    std::optional<double> descuentoLibranza;
    std::optional<double> descuentoEmbargo;
    std::optional<double> otrosDescuentos;
    std::optional<double> ajustesDescuentos;
    std::optional<double> provisionCesantias;
    std::optional<double> provisionInteresesCesantias;
    std::optional<double> provisionPrimaServicios;
    std::optional<double> provisionPrimaNavidad;
    std::optional<double> provisionVacaciones;
    std::optional<double> provisionPrimaVacaciones;
    std::optional<double> bonificacionServiciosPrestados;
    std::optional<double> aportePatronalSalud;
    std::optional<double> aportePatronalPension;
    std::optional<double> aporteRiesgosLaborales;
    std::optional<double> aporteCajaCompensacion;
    std::optional<double> otrosAportesPatronales;
    std::optional<double> costoTotalEmpleador;
    std::optional<std::string> fechaGeneracion;
    std::optional<std::string> fechaAprobacion;
    std::optional<bool> aprobada;
    std::optional<bool> pagada;
    std::optional<std::string> fechaPago;
    std::optional<std::string> medioPago;
    std::optional<std::string> referenciaPago;
    std::optional<bool> requiereReliquidacion;
    std::optional<std::string> motivoReliquidacion;
    std::optional<int> liquidacionOrigen;
    std::optional<int> version;
    std::optional<std::string> usuarioLiquidador;
    std::optional<std::string> usuarioAprobador;
    std::optional<std::string> parametros_utilizados;
};

struct ConceptoNomina {
    std::optional<int> idConcepto;
    std::optional<std::string> codigo;
    std::optional<std::string> nombre;
    std::optional<std::string> tipoConcepto;
    std::optional<std::string> naturaleza;
    std::optional<std::string> formaCalculo;
    std::optional<double> porcentaje;
    std::optional<double> valorFijo;
    std::optional<std::string> baseCalculo;
    std::optional<std::string> aplicaA;
    std::optional<std::string> normaOrigen;
    std::optional<std::string> fechaInicioVigencia;
    std::optional<std::string> fechaFinVigencia;
    std::optional<std::string> estado;
    std::optional<std::string> codigoContable;
    std::optional<std::string> regimenAplicable;
    std::optional<std::string> modalidadProfesorAplicable;
    std::optional<std::string> categoriaAplicable;
    std::optional<std::string> dedicacionAplicable;
    std::optional<std::string> periodicidad;
    std::optional<bool> esSalarial;
    std::optional<bool> esBonificacion;
    std::optional<bool> esDescuentoLey;
    std::optional<bool> esPrestacionSocial;
    std::optional<bool> esAportePatronal;
    std::optional<bool> integraBaseSalud;
    std::optional<bool> integraBasePension;
    std::optional<bool> integraBasePrestacional;
    std::optional<bool> integraBaseParafiscal;
    std::optional<bool> integraLiquidacionFinal;
    std::optional<bool> requiereActoAdministrativo;
    std::optional<std::string> articuloOrigen;
    std::optional<int> prioridadCalculo;
};

struct DetalleLiquidacion {
    std::optional<int> idDetalleLiquidacion;
    std::optional<int> idLiquidacion;
    std::optional<int> idConcepto;
    std::optional<double> cantidad;
    std::optional<double> baseCalculo;
    std::optional<double> porcentajeAplicado;
    std::optional<double> valorUnitario;
    std::optional<double> valorCalculado;
    std::optional<std::string> observaciones;
    std::optional<std::string> tipoMovimiento;
    std::optional<std::string> fechaCausacion;
    std::optional<std::string> periodoCausacion;
    std::optional<std::string> formulaAplicada;
    std::optional<std::string> parametrosAplicados;
    std::optional<double> valorAntesAjuste;
    std::optional<double> valorAjuste;
    std::optional<double> valorDefinitivo;
    std::optional<bool> esSalarial;
    std::optional<bool> integraSeguridadSocial;
    std::optional<bool> integraPrestaciones;
    std::optional<bool> integraParafiscales;
    std::optional<std::string> actoSoporte;
    std::optional<std::string> documentoSoporte;
    std::optional<std::string> usuarioRegistro;
    std::optional<std::string> fechaRegistro;
};

struct ParametroNormativo {
    std::optional<int> idParametro;
    std::optional<ParametroNormativoCodigo> codigo;
    std::optional<std::string> nombre;
    std::optional<std::string> descripcion;
    std::optional<std::string> tipoDato;
    std::optional<std::string> valor;
    std::optional<std::string> unidad;
    std::optional<std::string> normaOrigen;
    std::optional<std::string> articulo;
    std::optional<std::string> fechaInicioVigencia;
    std::optional<std::string> fechaFinVigencia;
    std::optional<std::string> aplicaA;
    std::optional<std::string> estado;
};

struct ArchivoPersistencia {
    std::optional<int> idArchivo;
    std::optional<std::string> nombreArchivo;
    std::optional<std::string> ruta;
    std::optional<std::string> formato;
    std::optional<std::string> fechaCreacion;
    std::optional<std::string> fechaUltimaCarga;
    std::optional<std::string> fechaUltimoGuardado;
    std::optional<std::string> versionEstructura;
    std::optional<int> cantidadRegistros;
    std::optional<std::string> estado;
};

} // namespace pita

#endif // MODELO_DATOS_H
