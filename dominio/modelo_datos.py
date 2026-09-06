from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time
from decimal import Decimal
from enum import Enum


class EstadoAcademico(str, Enum):
    ASPIRANTE = "ASPIRANTE"
    ADMITIDO = "ADMITIDO"
    MATRICULADO = "MATRICULADO"
    ACTIVO = "ACTIVO"
    INACTIVO = "INACTIVO"
    RESERVA_CUPO = "RESERVA_CUPO"
    EBRA = "EBRA"
    GRADUADO = "GRADUADO"
    RETIRADO = "RETIRADO"
    SUSPENDIDO = "SUSPENDIDO"


class TipoProfesor(str, Enum):
    PLANTA = "PLANTA"
    OCASIONAL = "OCASIONAL"
    CATEDRATICO = "CATEDRATICO"
    CATEDRATICO_AD_HONOREM = "CATEDRATICO_AD_HONOREM"


class Dedicacion(str, Enum):
    TIEMPO_COMPLETO = "TIEMPO_COMPLETO"
    MEDIO_TIEMPO = "MEDIO_TIEMPO"
    HORA_CATEDRA = "HORA_CATEDRA"


class EstadoCurso(str, Enum):
    MATRICULADO = "MATRICULADO"
    EN_CURSO = "EN_CURSO"
    CANCELADO = "CANCELADO"
    APROBADO = "APROBADO"
    REPROBADO = "REPROBADO"
    RETIRADO = "RETIRADO"
    HOMOLOGADO = "HOMOLOGADO"
    VALIDADO = "VALIDADO"


class CategoriaDocenteCodigo(str, Enum):
    AUXILIAR = "AUXILIAR"
    ASISTENTE = "ASISTENTE"
    ASOCIADO = "ASOCIADO"
    TITULAR = "TITULAR"
    NO_CATEGORIZADO = "NO_CATEGORIZADO"


class TipoFactor(str, Enum):
    TITULO_ACADEMICO = "TITULO_ACADEMICO"
    CATEGORIA_DOCENTE = "CATEGORIA_DOCENTE"
    EXPERIENCIA = "EXPERIENCIA"
    PRODUCTIVIDAD_ACADEMICA = "PRODUCTIVIDAD_ACADEMICA"
    DIRECCION_ACADEMICO_ADMINISTRATIVA = "DIRECCION_ACADEMICO_ADMINISTRATIVA"
    DESEMPENO_DESTACADO = "DESEMPENO_DESTACADO"
    POSGRADO = "POSGRADO"
    GRUPO_INVESTIGACION = "GRUPO_INVESTIGACION"
    SEMILLERO = "SEMILLERO"


class ParametroNormativoCodigo(str, Enum):
    SALARIO_MINIMO = "SALARIO_MINIMO"
    VALOR_PUNTO_SALARIAL = "VALOR_PUNTO_SALARIAL"
    VALOR_AUXILIO_TRANSPORTE_VIGENTE = "VALOR_AUXILIO_TRANSPORTE_VIGENTE"
    PORCENTAJE_ARL_CLASE_I = "PORCENTAJE_ARL_CLASE_I"
    PORCENTAJE_ARL_CLASE_II = "PORCENTAJE_ARL_CLASE_II"
    PORCENTAJE_SENA = "PORCENTAJE_SENA"
    PORCENTAJE_ICBF = "PORCENTAJE_ICBF"
    VALOR_HORA_CATEDRA = "VALOR_HORA_CATEDRA"
    PORCENTAJE_SALUD_TRABAJADOR = "PORCENTAJE_SALUD_TRABAJADOR"
    PORCENTAJE_SALUD_EMPLEADOR = "PORCENTAJE_SALUD_EMPLEADOR"
    PORCENTAJE_PENSION_TRABAJADOR = "PORCENTAJE_PENSION_TRABAJADOR"
    PORCENTAJE_PENSION_EMPLEADOR = "PORCENTAJE_PENSION_EMPLEADOR"
    PORCENTAJE_FONDO_SOLIDARIDAD = "PORCENTAJE_FONDO_SOLIDARIDAD"
    PORCENTAJE_RIESGOS_LABORALES = "PORCENTAJE_RIESGOS_LABORALES"
    PORCENTAJE_CAJA_COMPENSACION = "PORCENTAJE_CAJA_COMPENSACION"
    TOPE_BONIFICACION_SERVICIOS = "TOPE_BONIFICACION_SERVICIOS"
    PORCENTAJE_BONIFICACION_SERVICIOS_HASTA_TOPE = "PORCENTAJE_BONIFICACION_SERVICIOS_HASTA_TOPE"
    PORCENTAJE_BONIFICACION_SERVICIOS_SOBRE_TOPE = "PORCENTAJE_BONIFICACION_SERVICIOS_SOBRE_TOPE"
    PORCENTAJE_RETENCION_FUENTE = "PORCENTAJE_RETENCION_FUENTE"
    BASE_MINIMA_RETENCION_FUENTE = "BASE_MINIMA_RETENCION_FUENTE"
    NOTA_MINIMA_APROBATORIA = "NOTA_MINIMA_APROBATORIA"
    PROMEDIO_MINIMO_EBRA = "PROMEDIO_MINIMO_EBRA"
    MAXIMO_CREDITOS_PERIODO = "MAXIMO_CREDITOS_PERIODO"


@dataclass
class Universidad:
    idUniversidad: int | None = None
    nombre: str | None = None
    nit: str | None = None
    codigoInstitucional: str | None = None
    direccion: str | None = None
    ciudad: str | None = None
    departamento: str | None = None
    telefono: str | None = None
    correoInstitucional: str | None = None
    sitioWeb: str | None = None
    estado: str | None = None


@dataclass
class Facultad:
    idFacultad: int | None = None
    codigoFacultad: str | None = None
    nombre: str | None = None
    descripcion: str | None = None
    ubicacion: str | None = None
    telefono: str | None = None
    correo: str | None = None
    idDecano: int | None = None
    fechaCreacion: date | None = None
    estado: str | None = None


@dataclass
class ProgramaAcademico:
    idPrograma: int | None = None
    codigoPrograma: str | None = None
    nombre: str | None = None
    nivelFormacion: str | None = None
    modalidad: str | None = None
    numeroSemestres: int | None = None
    totalCreditos: int | None = None
    registroCalificado: str | None = None
    fechaCreacion: date | None = None
    idDirector: int | None = None
    idFacultad: int | None = None
    estado: str | None = None


@dataclass
class PlanEstudio:
    idPlanEstudio: int | None = None
    codigo: str | None = None
    nombre: str | None = None
    version: str | None = None
    fechaInicioVigencia: date | None = None
    fechaFinVigencia: date | None = None
    totalCreditos: int | None = None
    idPrograma: int | None = None
    estado: str | None = None


@dataclass
class DetallePlanEstudio:
    idDetallePlan: int | None = None
    idPlanEstudio: int | None = None
    idCurso: int | None = None
    semestreSugerido: int | None = None
    tipoCurso: str | None = None
    numeroCreditos: int | None = None
    esObligatorio: bool | None = None
    estado: str | None = None


@dataclass
class Curso:
    idCurso: int | None = None
    codigoCurso: str | None = None
    nombre: str | None = None
    descripcion: str | None = None
    numeroCreditos: int | None = None
    horasTeoricas: int | None = None
    horasPracticas: int | None = None
    horasTrabajoIndependiente: int | None = None
    cupoSugerido: int | None = None
    notaMinimaAprobatoria: Decimal | None = None
    estado: str | None = None


@dataclass
class Prerrequisito:
    idPrerrequisito: int | None = None
    idCurso: int | None = None
    idCursoRequerido: int | None = None
    tipoRequisito: str | None = None
    notaMinima: Decimal | None = None
    creditosMinimos: int | None = None
    estado: str | None = None


@dataclass
class PeriodoAcademico:
    idPeriodo: int | None = None
    codigo: str | None = None
    nombre: str | None = None
    anio: int | None = None
    numeroPeriodo: int | None = None
    fechaInicio: date | None = None
    fechaFin: date | None = None
    fechaInicioMatricula: date | None = None
    fechaFinMatricula: date | None = None
    fechaLimiteCancelacion: date | None = None
    estado: str | None = None


@dataclass
class Persona:
    idPersona: int | None = None
    tipoDocumento: str | None = None
    numeroDocumento: str | None = None
    primerNombre: str | None = None
    segundoNombre: str | None = None
    primerApellido: str | None = None
    segundoApellido: str | None = None
    fechaNacimiento: date | None = None
    direccion: str | None = None
    telefono: str | None = None
    correoPersonal: str | None = None
    correoInstitucional: str | None = None
    ciudadResidencia: str | None = None
    fechaRegistro: date | None = None
    estado: str | None = None


@dataclass
class Estudiante:
    idEstudiante: int | None = None
    idPersona: int | None = None
    codigoEstudiante: str | None = None
    idPrograma: int | None = None
    idPlanEstudio: int | None = None
    fechaIngreso: date | None = None
    semestreActual: int | None = None
    creditosAprobados: int | None = None
    promedioAcumulado: Decimal | None = None
    estadoAcademico: EstadoAcademico | None = None
    estado: str | None = None


@dataclass
class Profesor:
    idProfesor: int | None = None
    idPersona: int | None = None
    codigoProfesor: str | None = None
    idProgramaPrincipal: int | None = None
    fechaVinculacion: date | None = None
    tipoProfesor: TipoProfesor | None = None
    categoriaDocente: str | None = None
    dedicacion: Dedicacion | None = None
    maximoNivelEstudio: str | None = None
    tituloProfesional: str | None = None
    areaConocimiento: str | None = None
    numeroHorasSemanales: Decimal | None = None
    puntosSalariales: Decimal | None = None
    estado: str | None = None
    regimenSalarial: str | None = None
    modalidadVinculacion: str | None = None
    perteneceCarreraDocente: bool | None = None
    fechaIngresoCarreraDocente: date | None = None
    fechaPosesion: date | None = None
    fechaUltimaVinculacion: date | None = None
    fechaRetiro: date | None = None
    motivoRetiro: str | None = None
    actoAdministrativoIngreso: str | None = None
    actoAdministrativoRetiro: str | None = None
    evaluacionDesempenoAnterior: Decimal | None = None
    puedeSerVinculadoSiguientePeriodo: bool | None = None
    idCategoriaDocente: int | None = None
    categoriaReconocida: str | None = None
    categoriaInstitucionOrigen: str | None = None
    fechaReconocimientoCategoria: date | None = None
    actoReconocimientoCategoria: str | None = None
    categoriaComoInvestigador: str | None = None
    grupoInvestigacion: str | None = None
    categoriaGrupoInvestigacion: str | None = None
    perteneceSemillero: bool | None = None
    semilleroInvestigacion: str | None = None
    productividadInvestigativaVigente: bool | None = None
    participaProyectoInvestigacionVigente: bool | None = None
    certificacionVicerrectoriaInvestigacion: str | None = None
    nivelPosgradoReconocido: str | None = None
    tituloPosgradoReconocido: str | None = None
    fechaObtencionPosgrado: date | None = None
    tituloConvalidado: bool | None = None
    numeroResolucionConvalidacion: str | None = None
    esEspecializacionClinica: bool | None = None
    posgradoRelacionadoConAreaDesempeno: bool | None = None
    factorBonificacionPosgrado: Decimal | None = None
    fechaInicioReconocimientoPosgrado: date | None = None
    fechaFinReconocimientoPosgrado: date | None = None
    aniosExperienciaDocenteUniversitaria: Decimal | None = None
    periodosExperienciaDocenteUniversitaria: int | None = None
    aniosExperienciaInvestigacion: Decimal | None = None
    aniosExperienciaProfesional: Decimal | None = None
    aniosExperienciaDireccionAcademica: Decimal | None = None
    experienciaEquivalenteTiempoCompleto: Decimal | None = None
    experienciaCertificada: bool | None = None
    fechaCorteExperiencia: date | None = None
    puntosExperienciaReconocidos: Decimal | None = None


@dataclass
class Administrativo:
    idAdministrativo: int | None = None
    idPersona: int | None = None
    codigoEmpleado: str | None = None
    cargo: str | None = None
    dependencia: str | None = None
    categoria: str | None = None
    tipoContratacion: str | None = None
    fechaVinculacion: date | None = None
    salarioBase: Decimal | None = None
    estado: str | None = None


@dataclass
class OfertaCurso:
    idOfertaCurso: int | None = None
    idCurso: int | None = None
    idPeriodo: int | None = None
    grupo: str | None = None
    cupoMaximo: int | None = None
    cupoDisponible: int | None = None
    modalidad: str | None = None
    aula: str | None = None
    sede: str | None = None
    fechaInicio: date | None = None
    fechaFin: date | None = None
    estado: str | None = None


@dataclass
class AsignacionDocente:
    idAsignacion: int | None = None
    idProfesor: int | None = None
    idOfertaCurso: int | None = None
    rolDocente: str | None = None
    numeroHoras: Decimal | None = None
    porcentajeResponsabilidad: Decimal | None = None
    fechaAsignacion: date | None = None
    estado: str | None = None


@dataclass
class Horario:
    idHorario: int | None = None
    idOfertaCurso: int | None = None
    diaSemana: str | None = None
    horaInicio: time | None = None
    horaFin: time | None = None
    aula: str | None = None
    sede: str | None = None
    tipoSesion: str | None = None
    estado: str | None = None


@dataclass
class MatriculaAcademica:
    idMatricula: int | None = None
    idEstudiante: int | None = None
    idPeriodo: int | None = None
    fechaMatricula: date | None = None
    totalCreditos: int | None = None
    promedioPeriodo: Decimal | None = None
    estadoMatricula: str | None = None
    observaciones: str | None = None


@dataclass
class DetalleMatricula:
    idDetalleMatricula: int | None = None
    idMatricula: int | None = None
    idOfertaCurso: int | None = None
    fechaInscripcion: date | None = None
    estadoCurso: EstadoCurso | None = None
    notaFinal: Decimal | None = None
    numeroFallas: int | None = None
    fechaCancelacion: date | None = None
    motivoCancelacion: str | None = None


@dataclass
class Evaluacion:
    idEvaluacion: int | None = None
    idOfertaCurso: int | None = None
    nombre: str | None = None
    tipo: str | None = None
    porcentaje: Decimal | None = None
    fechaProgramada: date | None = None
    descripcion: str | None = None
    estado: str | None = None


@dataclass
class Calificacion:
    idCalificacion: int | None = None
    idEvaluacion: int | None = None
    idDetalleMatricula: int | None = None
    nota: Decimal | None = None
    fechaRegistro: date | None = None
    observacion: str | None = None
    estado: str | None = None


@dataclass
class AlertaAcademica:
    idAlerta: int | None = None
    idEstudiante: int | None = None
    idPeriodo: int | None = None
    tipoAlerta: str | None = None
    motivo: str | None = None
    valorObservado: Decimal | None = None
    valorLimite: Decimal | None = None
    fechaGeneracion: date | None = None
    atendida: bool | None = None
    observaciones: str | None = None
    estado: str | None = None


@dataclass
class Contrato:
    idContrato: int | None = None
    idPersona: int | None = None
    numeroContrato: str | None = None
    tipoContrato: str | None = None
    fechaInicio: date | None = None
    fechaFin: date | None = None
    dedicacion: Dedicacion | None = None
    horasSemanales: Decimal | None = None
    horasCatedra: Decimal | None = None
    valorHora: Decimal | None = None
    aplicaAuxilioTransporte: bool | None = None
    salarioBase: Decimal | None = None
    claseARL: str | None = None
    actoAdministrativo: str | None = None
    observaciones: str | None = None
    estado: str | None = None
    regimenAplicable: str | None = None
    normaVinculacion: str | None = None
    articuloNormativo: str | None = None
    modalidadProfesor: str | None = None
    esEmpleadoPublicoDocente: bool | None = None
    perteneceCarreraProfesoral: bool | None = None
    esTransitorio: bool | None = None
    esRemunerado: bool | None = None
    esAdHonorem: bool | None = None
    tipoDedicacion: str | None = None
    porcentajeDedicacion: Decimal | None = None
    duracionEnMeses: int | None = None
    periodoAcademicoInicial: int | None = None
    periodoAcademicoFinal: int | None = None
    tipoActoVinculacion: str | None = None
    numeroActoVinculacion: str | None = None
    fechaActoVinculacion: date | None = None
    fechaPosesion: date | None = None
    certificadoDisponibilidadPresupuestal: str | None = None
    numeroCDP: str | None = None
    fechaCDP: date | None = None
    valorDisponibilidadPresupuestal: Decimal | None = None
    resolucionRectoral: str | None = None
    fechaResolucionRectoral: date | None = None
    estadoFormalizacion: str | None = None
    fechaInicioEfectiva: date | None = None
    fechaTerminacionEfectiva: date | None = None
    horasSemanalesAsignadas: Decimal | None = None
    horasMensualesAsignadas: Decimal | None = None
    horasDocenciaDirecta: Decimal | None = None
    horasActividadesComplementarias: Decimal | None = None
    horasMensualesReconocidas: Decimal | None = None
    horasMensualesCumplidas: Decimal | None = None
    horasIncumplidas: Decimal | None = None
    valorHoraIncumplida: Decimal | None = None
    valorDescuentoIncumplimiento: Decimal | None = None
    limiteHorasSemanales: Decimal | None = None
    requiereCertificacionCumplimiento: bool | None = None
    certificacionCumplimiento: str | None = None
    fechaCertificacionCumplimiento: date | None = None
    categoriaDocenteAlVincular: str | None = None
    nivelPosgradoAlVincular: str | None = None
    grupoInvestigacionAlVincular: str | None = None
    categoriaGrupoAlVincular: str | None = None
    semilleroAlVincular: str | None = None
    salarioMinimoVigente: Decimal | None = None
    factorSalarialSMMLV: Decimal | None = None
    valorHoraCatedraVigente: Decimal | None = None
    resolucionValorHoraCatedra: str | None = None
    fechaVigenciaValorHora: date | None = None
    salarioMensualPactado: Decimal | None = None
    permiteBonificacionPosgrado: bool | None = None
    permiteBonificacionInvestigacion: bool | None = None
    permitePrestacionesSociales: bool | None = None
    permiteAportesParafiscales: bool | None = None
    causalTerminacion: str | None = None
    fechaNovedadTerminacion: date | None = None
    actoTerminacion: str | None = None
    renunciaPresentada: bool | None = None
    renunciaAceptada: bool | None = None
    necesidadServicioVigente: bool | None = None
    incumplimientoComprobado: bool | None = None
    decisionJudicialOAdministrativa: str | None = None
    documentoSoporteTerminacion: str | None = None
    estadoFinalContrato: str | None = None


@dataclass
class CategoriaDocente:
    idCategoria: int | None = None
    codigo: CategoriaDocenteCodigo | None = None
    nombre: str | None = None
    descripcion: str | None = None
    puntosBase: Decimal | None = None
    valorHoraBase: Decimal | None = None
    nivelJerarquico: str | None = None
    normaOrigen: str | None = None
    fechaInicioVigencia: date | None = None
    fechaFinVigencia: date | None = None
    estado: str | None = None
    tipoRegimen: str | None = None
    puntosCategoria: Decimal | None = None
    factorSalarialTiempoCompleto: Decimal | None = None
    factorSalarialMedioTiempo: Decimal | None = None
    unidadFactorSalarial: str | None = None
    requiereActoReconocimiento: bool | None = None
    actoReconocimiento: str | None = None
    fechaReconocimiento: date | None = None
    categoriaAnterior: str | None = None
    fechaAscenso: date | None = None
    esCategoriaPorDefecto: bool | None = None
    permiteReconocimientoCategoriaOrigen: bool | None = None
    evaluacionSatisfactoriaInstitucionOrigen: bool | None = None


@dataclass
class FactorSalarial:
    idFactor: int | None = None
    nombre: str | None = None
    tipoFactor: TipoFactor | None = None
    cantidad: Decimal | None = None
    puntosReconocidos: Decimal | None = None
    valorReconocido: Decimal | None = None
    fechaReconocimiento: date | None = None
    actoAdministrativo: str | None = None
    idProfesor: int | None = None
    estado: str | None = None
    regimenAplicable: str | None = None
    factorGenerador: str | None = None
    tipoReconocimiento: str | None = None
    puntosSolicitados: Decimal | None = None
    puntosAprobados: Decimal | None = None
    puntosAcumulables: Decimal | None = None
    topeIndividual: Decimal | None = None
    topePorCategoria: Decimal | None = None
    topeAnual: Decimal | None = None
    numeroAutores: int | None = None
    factorCoautoria: Decimal | None = None
    requiereEvaluacionPares: bool | None = None
    resultadoEvaluacionPares: str | None = None
    requiereAprobacionComite: bool | None = None
    fechaAprobacionComite: date | None = None
    actoReconocimiento: str | None = None
    fechaEfectoSalarial: date | None = None
    esConstitutivoSalario: bool | None = None
    integraBasePrestacional: bool | None = None
    integraBaseParafiscal: bool | None = None
    vigenciaDesde: date | None = None
    vigenciaHasta: date | None = None


@dataclass
class ProduccionAcademica:
    idProduccion: int | None = None
    idProfesor: int | None = None
    tipoProduccion: str | None = None
    titulo: str | None = None
    fechaPublicacion: date | None = None
    entidadPublicadora: str | None = None
    identificadorProducto: str | None = None
    puntosSolicitados: Decimal | None = None
    puntosReconocidos: Decimal | None = None
    fechaReconocimiento: date | None = None
    actoAdministrativo: str | None = None
    estadoValidacion: str | None = None
    modalidadProducto: str | None = None
    subtipoProducto: str | None = None
    nivelImpacto: str | None = None
    clasificacionRevista: str | None = None
    isbn: str | None = None
    issn: str | None = None
    registroDerechoAutor: str | None = None
    numeroPatente: str | None = None
    entidadIndexadora: str | None = None
    numeroAutores: int | None = None
    posicionAutor: int | None = None
    porcentajeParticipacion: Decimal | None = None
    creditoInstitucional: bool | None = None
    evaluadoPorPares: bool | None = None
    cantidadPares: int | None = None
    resultadoEvaluacion: str | None = None
    puntosTotalesProducto: Decimal | None = None
    factorCoautoria: Decimal | None = None
    puntosReconocidosProfesor: Decimal | None = None
    tipoReconocimiento: str | None = None
    fechaActoReconocimiento: date | None = None
    yaReconocidoOtroConcepto: bool | None = None
    productoReclasificado: bool | None = None
    puntosAdicionalesReclasificacion: Decimal | None = None
    fechaLimiteReclasificacion: date | None = None


@dataclass
class PeriodoNomina:
    idPeriodoNomina: int | None = None
    anio: int | None = None
    mes: int | None = None
    fechaInicio: date | None = None
    fechaFin: date | None = None
    fechaPago: date | None = None
    estado: str | None = None
    tipoPeriodicidad: str | None = None
    salarioMinimoVigente: Decimal | None = None
    valorPuntoSalarialVigente: Decimal | None = None
    fechaVigenciaValorPunto: date | None = None
    resolucionValorPunto: str | None = None
    diasBaseLiquidacion: int | None = None
    fechaCorteNovedades: date | None = None
    fechaCierreNomina: date | None = None
    fechaAprobacion: date | None = None
    usuarioAprobador: str | None = None
    totalDevengadoPeriodo: Decimal | None = None
    totalDescuentosPeriodo: Decimal | None = None
    totalPrestacionesPeriodo: Decimal | None = None
    totalAportesPatronalesPeriodo: Decimal | None = None
    costoTotalPeriodo: Decimal | None = None
    estaCerrado: bool | None = None
    permiteReliquidacion: bool | None = None
    versionLiquidacion: int | None = None


@dataclass
class LiquidacionNomina:
    idLiquidacion: int | None = None
    idProfesor: int | None = None
    idContrato: int | None = None
    idPeriodoNomina: int | None = None
    fechaLiquidacion: date | None = None
    salarioBase: Decimal | None = None
    totalDevengado: Decimal | None = None
    totalDescuentos: Decimal | None = None
    totalPrestaciones: Decimal | None = None
    baseLiquidacionPrestaciones: Decimal | None = None
    baseCotizacionSeguridadSocial: Decimal | None = None
    valorAuxilioTransporteCotizado: Decimal | None = None
    aportePatronalSENA: Decimal | None = None
    aportePatronalICBF: Decimal | None = None
    netoPagar: Decimal | None = None
    estado: str | None = None
    tipoProfesorLiquidado: TipoProfesor | None = None
    regimenLiquidado: str | None = None
    categoriaLiquidada: str | None = None
    dedicacionLiquidada: Dedicacion | None = None
    diasTrabajados: Decimal | None = None
    diasNoRemunerados: Decimal | None = None
    horasAsignadas: Decimal | None = None
    horasCumplidas: Decimal | None = None
    horasIncumplidas: Decimal | None = None
    salarioMinimoUsado: Decimal | None = None
    valorPuntoUsado: Decimal | None = None
    valorHoraCatedraUsado: Decimal | None = None
    factorCategoriaUsado: Decimal | None = None
    puntosSalarialesUsados: Decimal | None = None
    salarioOrdinario: Decimal | None = None
    baseSalarialPrestacional: Decimal | None = None
    baseSeguridadSocial: Decimal | None = None
    baseParafiscales: Decimal | None = None
    bonificacionPosgrado: Decimal | None = None
    bonificacionInvestigacion: Decimal | None = None
    bonificacionesSalariales: Decimal | None = None
    bonificacionesNoSalariales: Decimal | None = None
    otrosDevengadosSalariales: Decimal | None = None
    otrosDevengadosNoSalariales: Decimal | None = None
    ajustesDevengados: Decimal | None = None
    descuentoSalud: Decimal | None = None
    descuentoPension: Decimal | None = None
    fondoSolidaridadPensional: Decimal | None = None
    retencionFuente: Decimal | None = None
    descuentoHorasIncumplidas: Decimal | None = None
    descuentoLibranza: Decimal | None = None
    descuentoEmbargo: Decimal | None = None
    otrosDescuentos: Decimal | None = None
    ajustesDescuentos: Decimal | None = None
    provisionCesantias: Decimal | None = None
    provisionInteresesCesantias: Decimal | None = None
    provisionPrimaServicios: Decimal | None = None
    provisionPrimaNavidad: Decimal | None = None
    provisionVacaciones: Decimal | None = None
    provisionPrimaVacaciones: Decimal | None = None
    bonificacionServiciosPrestados: Decimal | None = None
    aportePatronalSalud: Decimal | None = None
    aportePatronalPension: Decimal | None = None
    aporteRiesgosLaborales: Decimal | None = None
    aporteCajaCompensacion: Decimal | None = None
    otrosAportesPatronales: Decimal | None = None
    costoTotalEmpleador: Decimal | None = None
    fechaGeneracion: date | None = None
    fechaAprobacion: date | None = None
    aprobada: bool | None = None
    pagada: bool | None = None
    fechaPago: date | None = None
    medioPago: str | None = None
    referenciaPago: str | None = None
    requiereReliquidacion: bool | None = None
    motivoReliquidacion: str | None = None
    liquidacionOrigen: int | None = None
    version: int | None = None
    usuarioLiquidador: str | None = None
    usuarioAprobador: str | None = None
    parametros_utilizados: dict[str, str] | None = None  # Código del parámetro -> valor aplicado


@dataclass
class ConceptoNomina:
    idConcepto: int | None = None
    codigo: str | None = None
    nombre: str | None = None
    tipoConcepto: str | None = None
    naturaleza: str | None = None
    formaCalculo: str | None = None
    porcentaje: Decimal | None = None
    valorFijo: Decimal | None = None
    baseCalculo: str | None = None
    aplicaA: str | None = None
    normaOrigen: str | None = None
    fechaInicioVigencia: date | None = None
    fechaFinVigencia: date | None = None
    estado: str | None = None
    codigoContable: str | None = None
    regimenAplicable: str | None = None
    modalidadProfesorAplicable: str | None = None
    categoriaAplicable: str | None = None
    dedicacionAplicable: str | None = None
    periodicidad: str | None = None
    esSalarial: bool | None = None
    esBonificacion: bool | None = None
    esDescuentoLey: bool | None = None
    esPrestacionSocial: bool | None = None
    esAportePatronal: bool | None = None
    integraBaseSalud: bool | None = None
    integraBasePension: bool | None = None
    integraBasePrestacional: bool | None = None
    integraBaseParafiscal: bool | None = None
    integraLiquidacionFinal: bool | None = None
    requiereActoAdministrativo: bool | None = None
    articuloOrigen: str | None = None
    prioridadCalculo: int | None = None


@dataclass
class DetalleLiquidacion:
    idDetalleLiquidacion: int | None = None
    idLiquidacion: int | None = None
    idConcepto: int | None = None
    cantidad: Decimal | None = None
    baseCalculo: Decimal | None = None
    porcentajeAplicado: Decimal | None = None
    valorUnitario: Decimal | None = None
    valorCalculado: Decimal | None = None
    observaciones: str | None = None
    tipoMovimiento: str | None = None
    fechaCausacion: date | None = None
    periodoCausacion: str | None = None
    formulaAplicada: str | None = None
    parametrosAplicados: str | None = None
    valorAntesAjuste: Decimal | None = None
    valorAjuste: Decimal | None = None
    valorDefinitivo: Decimal | None = None
    esSalarial: bool | None = None
    integraSeguridadSocial: bool | None = None
    integraPrestaciones: bool | None = None
    integraParafiscales: bool | None = None
    actoSoporte: str | None = None
    documentoSoporte: str | None = None
    usuarioRegistro: str | None = None
    fechaRegistro: date | None = None


@dataclass
class ParametroNormativo:
    idParametro: int | None = None
    codigo: ParametroNormativoCodigo | None = None
    nombre: str | None = None
    descripcion: str | None = None
    tipoDato: str | None = None
    valor: str | None = None
    unidad: str | None = None
    normaOrigen: str | None = None
    articulo: str | None = None
    fechaInicioVigencia: date | None = None
    fechaFinVigencia: date | None = None
    aplicaA: str | None = None
    estado: str | None = None


@dataclass
class ArchivoPersistencia:
    idArchivo: int | None = None
    nombreArchivo: str | None = None
    ruta: str | None = None
    formato: str | None = None
    fechaCreacion: date | None = None
    fechaUltimaCarga: date | None = None
    fechaUltimoGuardado: date | None = None
    versionEstructura: str | None = None
    cantidadRegistros: int | None = None
    estado: str | None = None
