#ifndef GUI_APP_H
#define GUI_APP_H

#include "gui_controller.h"
#include "imgui.h"
#include <string>

struct GLFWwindow;

namespace pita {

enum class VistaActiva {
    DASHBOARD,
    FACULTADES,
    PERSONAS,
    ACADEMICA,
    CONTRATOS,
    NOMINA,
    PARAMETROS
};

/**
 * Aplicación principal PITA con Dear ImGui.
 * Maneja la ventana GLFW, el loop de renderizado,
 * la sidebar de navegación, el routing de vistas y operaciones CRUD.
 */
class PITAApp {
public:
    explicit PITAApp(const std::string& dirDatos = "datos");
    ~PITAApp();

    // Ejecutar el loop principal (bloquea hasta cerrar)
    int ejecutar();

private:
    GLFWwindow* ventana = nullptr;
    GUIController ctrl;
    VistaActiva vistaActiva = VistaActiva::DASHBOARD;
    ImFont* fuenteNormal = nullptr;
    ImFont* fuenteTitulo = nullptr;
    ImFont* fuentePequena = nullptr;

    // Setup & teardown
    bool inicializarGLFW();
    bool inicializarImGui();
    void destruir();

    // Render loop
    void renderFrame();
    void renderHeader();
    void renderSidebar();
    void renderContenido();

    // Vistas
    void renderDashboard();
    void renderFacultades();
    void renderPersonas();
    void renderAcademica();
    void renderContratos();
    void renderNomina();
    void renderParametros();

    // Helpers UI
    void renderBarraEstado();
    bool sidebarButton(const char* label, bool activo);
    void tarjetaKPI(const char* titulo, const char* valor, ImVec4 color, const char* subtitulo, float cardWidth = 0.0f);

    // ==================================================================
    // ESTADO Y MODALES CRUD
    // ==================================================================
    char mensajeModal[256] = "";
    bool errorModal = false;

    // 1. Modal Persona (Crear / Editar)
    bool modalPersonaAbierto = false;
    bool modoEditarPersona = false;
    int idPersonaEditando = 0;
    char pTipoDoc[16] = "CC";
    char pNumDoc[32] = "";
    char pPrimerNombre[64] = "";
    char pSegundoNombre[64] = "";
    char pPrimerApellido[64] = "";
    char pSegundoApellido[64] = "";
    char pEmail[128] = "";
    char pTelefono[32] = "";
    char pDireccion[128] = "";
    int pRolSeleccionado = 0; // 0: Ninguno, 1: Estudiante, 2: Profesor, 3: Administrativo
    // Campos Estudiante
    char estCodigo[32] = "";
    int estProgramaId = 0;
    int estSemestre = 1;
    // Campos Profesor
    char profCodigo[32] = "";
    int profTipoIdx = 0; // 0: PLANTA, 1: OCASIONAL, 2: CATEDRA
    int profDedicacionIdx = 0; // 0: TIEMPO_COMPLETO, 1: MEDIO_TIEMPO, 2: HORA_CATEDRA
    double profHoras = 40.0;
    char profCategoria[64] = "ASISTENTE";
    double profPuntos = 0.0;
    // Campos Administrativo
    char admCodigo[32] = "";
    char admCargo[64] = "";
    char admDependencia[64] = "";
    int admCategoriaIdx = 0; // 0: PROFESIONAL, 1: DIRECTIVO, 2: ASESOR, 3: TECNICO, 4: ASISTENCIAL
    int admTipoContratacionIdx = 0; // 0: PLANTA, 1: CARRERA_ADMINISTRATIVA, 2: LIBRE_NOMBRAMIENTO, 3: PROVISIONALIDAD, 4: PRESTACION_SERVICIOS
    double admSalarioBase = 2800000.0;
    char admFechaVinculacion[32] = "2026-03-01";

    // Modal Detalle Persona
    bool modalDetallePersonaAbierto = false;
    int idPersonaDetalle = 0;

    // Modal Editar Estudiante
    bool modalEditarEstudianteAbierto = false;
    int idEstudianteEditando = 0;
    char editEstCodigo[32] = "";
    int editEstProgramaId = 0;
    int editEstSemestre = 1;
    int editEstCreditos = 0;
    float editEstPromedio = 4.0f;
    int editEstEstadoAcadIdx = 0; // 0: MATRICULADO, 1: EBRA, 2: GRADUADO, 3: RETIRADO, 4: CANCELADO
    int editEstEstadoIdx = 0; // 0: ACTIVO, 1: INACTIVO

    // Modal Editar Profesor
    bool modalEditarProfesorAbierto = false;
    int idProfesorEditando = 0;
    char editProfCodigo[32] = "";
    int editProfTipoIdx = 0; // 0: PLANTA, 1: OCASIONAL, 2: CATEDRA
    int editProfDedicacionIdx = 0; // 0: TIEMPO_COMPLETO, 1: MEDIO_TIEMPO, 2: HORA_CATEDRA
    double editProfHoras = 40.0;
    int editProfCategoriaIdx = 0; // 0: TITULAR, 1: ASOCIADO, 2: ASISTENTE, 3: AUXILIAR
    double editProfPuntos = 0.0;
    int editProfEstadoIdx = 0; // 0: ACTIVO, 1: INACTIVO

    // Modal Editar Administrativo
    bool modalEditarAdminAbierto = false;
    int idAdminEditando = 0;
    char editAdmCodigo[32] = "";
    char editAdmCargo[64] = "";
    char editAdmDependencia[64] = "";
    int editAdmCategoriaIdx = 0;
    int editAdmTipoContratacionIdx = 0;
    double editAdmSalarioBase = 2800000.0;

    // 2. Modal Facultad & Programa
    bool modalFacultadAbierto = false;
    char facCodigo[32] = "";
    char facNombre[128] = "";
    char facUbicacion[128] = "";
    char facTelefono[64] = "";
    char facCorreo[128] = "";
    char facDecano[128] = "";
    int facDecanoId = 0;

    bool modalEditarFacultadAbierto = false;
    int editFacId = 0;
    char editFacCodigo[32] = "";
    char editFacNombre[128] = "";
    char editFacUbicacion[128] = "";
    char editFacTelefono[64] = "";
    char editFacCorreo[128] = "";
    int editFacDecanoId = 0;
    int editFacEstadoIdx = 0; // 0: ACTIVO, 1: INACTIVO

    bool modalProgramaAbierto = false;
    char progCodigo[32] = "";
    char progNombre[128] = "";
    int progFacultadId = 0;
    int progDirectorId = 0;
    int progNivelIdx = 0; // 0: PREGRADO, 1: POSGRADO, 2: ESPECIALIZACION, 3: MAESTRIA, 4: DOCTORADO, 5: TECNOLOGIA
    int progModalidadIdx = 0; // 0: PRESENCIAL, 1: VIRTUAL, 2: A DISTANCIA, 3: DUAL, 4: HIBRIDA
    char progRegistroCalificado[64] = "RC-2026-V1";
    int progSemestres = 10;
    int progCreditos = 160;

    bool modalEditarProgramaAbierto = false;
    int editProgId = 0;
    char editProgCodigo[32] = "";
    char editProgNombre[128] = "";
    int editProgFacultadId = 0;
    int editProgDirectorId = 0;
    int editProgNivelIdx = 0;
    int editProgModalidadIdx = 0;
    char editProgRegistroCalificado[64] = "";
    int editProgSemestres = 10;
    int editProgCreditos = 160;
    int editProgEstadoIdx = 0; // 0: ACTIVO, 1: INACTIVO

    // Bloqueo de integridad referencial al eliminar programa
    bool modalAvisoIntegridadProgramaAbierto = false;
    int idProgBloqueado = 0;
    char nombreProgBloqueado[128] = "";
    char codigoProgBloqueado[32] = "";
    int cantEstudiantesProgBloqueado = 0;
    int cantPlanesProgBloqueado = 0;

    // 3. Modal Curso & Matrícula & Calificación
    bool modalCursoAbierto = false;
    char curCodigo[32] = "";
    char curNombre[128] = "";
    int curCreditos = 3;
    int curSemestre = 1;
    int curHorasTeoricas = 3;
    int curHorasPracticas = 2;
    float curNotaMinima = 3.0f;
    int curCupoSugerido = 30;

    // Modal Editar Curso
    bool modalEditarCursoAbierto = false;
    int editCurId = 0;
    char editCurCodigo[32] = "";
    char editCurNombre[128] = "";
    int editCurCreditos = 3;
    int editCurHorasTeoricas = 3;
    int editCurHorasPracticas = 2;
    float editCurNotaMinima = 3.0f;
    int editCurCupoSugerido = 30;

    // Modal Nueva Oferta / Grupo
    bool modalNuevaOfertaAbierto = false;
    int ofCursoId = 1;
    int ofPeriodoId = 1;
    char ofGrupo[16] = "01";
    char ofAula[32] = "Aula 204";
    char ofSede[32] = "Sabanas";
    int ofCupoMaximo = 35;
    int ofProfesorId = 1;

    bool modalMatriculaAbierto = false;
    int matEstudianteId = 0;
    int matOfertaId = 0;

    bool modalNotaAbierto = false;
    int notaEvaluacionId = 0;
    int notaDetalleMatriculaId = 0;
    float notaValor = 4.0f;

    // Modal Editar Nota
    bool modalEditarNotaAbierto = false;
    int editNotaIdCalificacion = 0;
    float editNotaNuevoValor = 4.0f;
    char editNotaDescripcion[128] = "";

    // 3b. Modales Periodo Academico & Plan de Estudio / Malla Curricular
    bool modalPeriodoAcademicoAbierto = false;
    char perAcadCodigo[32] = "2026-1";
    char perAcadNombre[64] = "Periodo Academico 2026-1";
    char perAcadFechaInicio[32] = "2026-02-02";
    char perAcadFechaFin[32] = "2026-06-19";
    int perAcadEstadoIdx = 0; // 0: PLANIFICACION, 1: MATRICULAS, 2: EN_CURSO, 3: FINALIZADO

    bool modalPlanEstudioAbierto = false;
    char planCodigo[32] = "PLAN-SIS-2026";
    char planNombre[128] = "Plan de Estudios Ingenieria de Sistemas 2026";
    char planVersion[32] = "2026.1";
    int planTotalCreditos = 160;
    int planProgramaId = 1;

    bool modalMallaCurricularAbierto = false;
    int planSeleccionadoId = 1;
    bool modalAsignarCursoPlanAbierto = false;
    int planCursoId = 1;
    int planCursoSemestre = 1;
    int planCursoTipoIdx = 0; // 0: OBLIGATORIA, 1: ELECTIVA

    // 4. Modal Contrato
    bool modalContratoAbierto = false;
    int conTipoPersonalIdx = 0; // 0: Docente, 1: Administrativo
    int conPersonaId = 0;
    int conTipoIdx = 0; // 0: DOCENTE_PLANTA, 1: DOCENTE_OCASIONAL, 2: DOCENTE_CATEDRA / 0: TERMINO_INDEFINIDO, etc.
    double conSalarioBase = 3500000.0;
    double conHoras = 40.0;
    int conDedicacionIdx = 0; // 0: TIEMPO_COMPLETO, 1: MEDIO_TIEMPO, 2: HORA_CATEDRA
    char conFechaInicio[32] = "2026-02-01";
    char conFechaFin[32] = "2026-11-30";

    // Modal Editar Contrato
    bool modalEditarContratoAbierto = false;
    int idContratoEditando = 0;
    char editConNumero[32] = "";
    int editConDedicacionIdx = 0; // 0: TIEMPO_COMPLETO, 1: MEDIO_TIEMPO, 2: HORA_CATEDRA
    double editConHoras = 40.0;
    double editConSalarioBase = 3500000.0;
    char editConFechaFin[32] = "2026-11-30";
    char editConCDP[64] = "";
    char editConResolucion[64] = "";
    int editConClaseARLIdx = 0; // 0: CLASE I (0.522%), 1: CLASE II (1.044%), 2: CLASE III (2.436%)
    int editConEstadoIdx = 0;   // 0: ACTIVO, 1: TERMINADO, 2: SUSPENDIDO

    bool modalTerminarContratoAbierto = false;
    int idContratoTerminando = 0;
    char conCausal[128] = "Cumplimiento del termino pactado";
    char conDocumento[128] = "Resolucion No. 042-2025";

    bool modalDetalleContratoAbierto = false;
    int idContratoDetalle = 0;

    // 5. Modal Periodo Nómina & Liquidación
    bool modalPeriodoNominaAbierto = false;
    int perAnio = 2026;
    int perMes = 1;
    int nomFiltroPeriodoId = 0; // 0: Todos los períodos, >0: idPeriodoNomina específico

    bool modalLiquidarAbierto = false;
    int liqPeriodoId = 0;
    int liqContratoId = 0; // 0: Todos los contratos, >0: contrato específico

    bool modalPagarNominaAbierto = false;
    int idLiquidacionPagando = 0;
    char pagMedio[64] = "TRANSFERENCIA_BANCARIA";
    char pagReferencia[64] = "TRX-202501-001";

    // Modales Nómina estilo Python
    bool modalDesprendibleAbierto = false;
    int idLiquidacionDesprendible = 0;

    bool modalLiquidarIndividualAbierto = false;
    int liqIndTipoPersonalIdx = 0; // 0: Docente, 1: Administrativo
    int idProfesorLiquidarIndividual = 0;
    int idAdminLiquidarIndividual = 0;
    int idPeriodoLiquidarIndividual = 0;

    // 5b. Desglose Anual de Nomina (12 Meses)
    int desgloseContratoSeleccionadoId = 0; // 0: Consolidado Institucional UPC, >0: idContrato especifico
    int desgloseAnio = 2026;
    bool modalReporteAnualAbierto = false;
    std::string reporteAnualTexto = "";

    // 6. Modal Editar Parámetro
    bool modalParametroAbierto = false;
    int idParametroEditando = 0;
    char paramCodigo[64] = "";
    char paramDescripcion[128] = "";
    char paramValor[64] = "";

    // Filtros de vistas
    int conFiltroModalidadIdx = 0; // 0: Todas, 1: Planta, 2: Ocasional, 3: Catedra, 4: Ad-Honorem
    int conFiltroEstadoIdx = 0;    // 0: Todos, 1: Activo, 2: Terminado
    char conFiltroBusqueda[64] = "";
    char perFiltroBusqueda[64] = "";
    char estFiltroBusqueda[64] = "";
    char profFiltroBusqueda[64] = "";

    // 4b. Modal Reconocer Puntos (Dec. 1279)
    bool modalReconocerPuntosAbierto = false;
    int recProfesorId = 0;
    int recTipoReconocimientoIdx = 0; // 0: Factores Salariales, 1: Produccion Intelectual
    int recTipoFactorIdx = 0;
    char recNombreFactor[128] = "Titulo de Doctorado en Computacion";
    double recPuntosFactor = 120.0;
    char recActoAdmin[64] = "Resolucion No. 015-2025";
    char recFechaReconocimiento[32] = "2025-02-01";
    int recTipoProduccionIdx = 0;
    char recTituloProduccion[128] = "Publicacion en Revista Indexada Q1";
    char recEditorial[128] = "IEEE Transactions on Software";
    int recNumAutores = 1;
    double recPuntosProduccion = 15.0;

    // Métodos de Renderizado de Modales
    void renderModales();
    void renderModalPersona();
    void renderModalDetallePersona();
    void renderModalEditarEstudiante();
    void renderModalEditarProfesor();
    void renderModalEditarAdministrativo();
    void renderModalFacultad();
    void renderModalEditarFacultad();
    void renderModalPrograma();
    void renderModalEditarPrograma();
    void renderModalAvisoIntegridadPrograma();
    void renderModalCurso();
    void renderModalEditarCurso();
    void renderModalNuevaOferta();
    void renderModalMatricula();
    void renderModalNota();
    void renderModalEditarNota();
    void renderModalContrato();
    void renderModalEditarContrato();
    void renderModalTerminarContrato();
    void renderModalDetalleContrato();
    void renderModalReconocerPuntos();
    void renderModalPeriodoNomina();
    void renderModalLiquidar();
    void renderModalPagarNomina();
    void renderModalDesprendible();
    void renderModalLiquidarIndividual();
    void renderModalParametro();
    void renderModalPeriodoAcademico();
    void renderModalPlanEstudio();
    void renderModalMallaCurricular();
    void renderModalAsignarCursoPlan();
    void renderModalReporteAnual();

    // Acciones de Nómina (alineadas con Python view_nomina_gui)
    void ejecutarLiquidacionGeneral();
    void liquidarProfesorEspecifico(int idProfesor, int idPeriodoForzado = 0);
    void liquidarAdministrativoEspecifico(int idAdministrativo, int idPeriodoForzado = 0);
    void eliminarLiquidacion(int idLiquidacion);

    // Helpers de apertura de modales con datos prellenados
    void abrirModalPersona(bool editar = false, int idPersona = 0);
    void abrirModalDetallePersona(int idPersona);
    void abrirModalEditarEstudiante(int idEstudiante);
    void abrirModalEditarProfesor(int idProfesor);
    void abrirModalEditarAdministrativo(int idAdministrativo);
    void abrirModalEditarFacultad(int idFacultad);
    void abrirModalEditarPrograma(int idPrograma);
    void intentarEliminarPrograma(int idPrograma);
    void eliminarFacultad(int idFacultad);
    void abrirModalEditarCurso(int idCurso);
    void abrirModalNuevaOferta();
    void abrirModalEditarNota(int idCalificacion);
    void eliminarCalificacion(int idCalificacion);
    void eliminarCurso(int idCurso);
    void eliminarOferta(int idOfertaCurso);
    void abrirModalEditarContrato(int idContrato);
    void abrirModalParametro(int idParametro);
};

} // namespace pita

#endif // GUI_APP_H
