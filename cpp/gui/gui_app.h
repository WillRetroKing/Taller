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

    // 2. Modal Facultad & Programa
    bool modalFacultadAbierto = false;
    char facCodigo[32] = "";
    char facNombre[128] = "";
    char facUbicacion[128] = "";
    char facDecano[128] = "";

    bool modalProgramaAbierto = false;
    char progCodigo[32] = "";
    char progNombre[128] = "";
    int progFacultadId = 0;
    int progNivelIdx = 0; // 0: PREGRADO, 1: POSGRADO
    int progCreditos = 160;

    // 3. Modal Curso & Matrícula & Calificación
    bool modalCursoAbierto = false;
    char curCodigo[32] = "";
    char curNombre[128] = "";
    int curCreditos = 3;
    int curSemestre = 1;

    bool modalMatriculaAbierto = false;
    int matEstudianteId = 0;
    int matOfertaId = 0;

    bool modalNotaAbierto = false;
    int notaEvaluacionId = 0;
    int notaDetalleMatriculaId = 0;
    float notaValor = 4.0f;

    // 4. Modal Contrato
    bool modalContratoAbierto = false;
    int conPersonaId = 0;
    int conTipoIdx = 0; // 0: DOCENTE_PLANTA, 1: DOCENTE_OCASIONAL, 2: DOCENTE_CATEDRA
    double conSalarioBase = 3500000.0;
    double conHoras = 16.0;
    char conFechaInicio[32] = "2025-02-01";
    char conFechaFin[32] = "2025-11-30";

    bool modalTerminarContratoAbierto = false;
    int idContratoTerminando = 0;
    char conCausal[128] = "Cumplimiento del termino pactado";
    char conDocumento[128] = "Resolucion No. 042-2025";

    // 5. Modal Periodo Nómina & Liquidación
    bool modalPeriodoNominaAbierto = false;
    int perAnio = 2025;
    int perMes = 1;

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
    int idProfesorLiquidarIndividual = 0;

    // 6. Modal Editar Parámetro
    bool modalParametroAbierto = false;
    int idParametroEditando = 0;
    char paramCodigo[64] = "";
    char paramDescripcion[128] = "";
    char paramValor[64] = "";

    // Métodos de Renderizado de Modales
    void renderModales();
    void renderModalPersona();
    void renderModalFacultad();
    void renderModalPrograma();
    void renderModalCurso();
    void renderModalMatricula();
    void renderModalNota();
    void renderModalContrato();
    void renderModalTerminarContrato();
    void renderModalPeriodoNomina();
    void renderModalLiquidar();
    void renderModalPagarNomina();
    void renderModalDesprendible();
    void renderModalLiquidarIndividual();
    void renderModalParametro();

    // Acciones de Nómina (alineadas con Python view_nomina_gui)
    void ejecutarLiquidacionGeneral();
    void liquidarProfesorEspecifico(int idProfesor);
    void eliminarLiquidacion(int idLiquidacion);

    // Helpers de apertura de modales con datos prellenados
    void abrirModalPersona(bool editar = false, int idPersona = 0);
    void abrirModalParametro(int idParametro);
};

} // namespace pita

#endif // GUI_APP_H
