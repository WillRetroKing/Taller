#define _CRT_SECURE_NO_WARNINGS
#include <cstring>
#include "gui_app.h"
#include "tema.h"

#include "imgui.h"
#include "imgui_impl_glfw.h"
#include "imgui_impl_opengl3.h"

#include <GLFW/glfw3.h>
#include <cstdio>
#include <string>
#include <cmath>

namespace pita {

// ======================================================================
// CONSTRUCTOR / DESTRUCTOR
// ======================================================================

PITAApp::PITAApp(const std::string& dirDatos)
    : ctrl(dirDatos) {}

PITAApp::~PITAApp() {
    destruir();
}

// ======================================================================
// SETUP GLFW
// ======================================================================

static void glfw_error_callback(int error, const char* description) {
    fprintf(stderr, "GLFW Error %d: %s\n", error, description);
}

bool PITAApp::inicializarGLFW() {
    glfwSetErrorCallback(glfw_error_callback);
    if (!glfwInit()) return false;

    // GL 3.0 + GLSL 130 (compatible con la mayoría)
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 0);

    ventana = glfwCreateWindow(1400, 850,
        "PITA v2.0 - Sistema Integrado de Transacciones Academicas | Universidad Popular del Cesar",
        nullptr, nullptr);
    if (!ventana) return false;

    glfwMakeContextCurrent(ventana);
    glfwSwapInterval(1); // VSync
    return true;
}

// ======================================================================
// SETUP IMGUI
// ======================================================================

bool PITAApp::inicializarImGui() {
    IMGUI_CHECKVERSION();
    ImGui::CreateContext();
    ImGuiIO& io = ImGui::GetIO();

    io.ConfigFlags |= ImGuiConfigFlags_NavEnableKeyboard;

    // Fonts — usar Segoe UI si disponible, sino usar la default
    fuenteNormal = io.Fonts->AddFontFromFileTTF("C:\\Windows\\Fonts\\segoeui.ttf", 16.0f);
    if (!fuenteNormal) fuenteNormal = io.Fonts->AddFontDefault();

    fuenteTitulo = io.Fonts->AddFontFromFileTTF("C:\\Windows\\Fonts\\segoeuib.ttf", 22.0f);
    if (!fuenteTitulo) fuenteTitulo = fuenteNormal;

    fuentePequena = io.Fonts->AddFontFromFileTTF("C:\\Windows\\Fonts\\segoeui.ttf", 13.0f);
    if (!fuentePequena) fuentePequena = fuenteNormal;

    // Aplicar tema Windows 11 Light
    tema::aplicarTema();

    // Setup Platform/Renderer backends
    ImGui_ImplGlfw_InitForOpenGL(ventana, true);
    ImGui_ImplOpenGL3_Init("#version 130");

    return true;
}

void PITAApp::destruir() {
    if (ventana) {
        ImGui_ImplOpenGL3_Shutdown();
        ImGui_ImplGlfw_Shutdown();
        ImGui::DestroyContext();
        glfwDestroyWindow(ventana);
        glfwTerminate();
        ventana = nullptr;
    }
}

// ======================================================================
// LOOP PRINCIPAL
// ======================================================================

int PITAApp::ejecutar() {
    if (!inicializarGLFW()) return 1;
    if (!inicializarImGui()) return 1;

    while (!glfwWindowShouldClose(ventana)) {
        glfwPollEvents();
        renderFrame();
    }

    destruir();
    return 0;
}

void PITAApp::renderFrame() {
    ImGui_ImplOpenGL3_NewFrame();
    ImGui_ImplGlfw_NewFrame();
    ImGui::NewFrame();

    // Crear ventana fullscreen sin decoración
    ImGuiViewport* viewport = ImGui::GetMainViewport();
    ImGui::SetNextWindowPos(viewport->WorkPos);
    ImGui::SetNextWindowSize(viewport->WorkSize);

    ImGuiWindowFlags flags =
        ImGuiWindowFlags_NoTitleBar | ImGuiWindowFlags_NoCollapse |
        ImGuiWindowFlags_NoResize | ImGuiWindowFlags_NoMove |
        ImGuiWindowFlags_NoBringToFrontOnFocus | ImGuiWindowFlags_NoNavFocus |
        ImGuiWindowFlags_NoScrollbar | ImGuiWindowFlags_NoScrollWithMouse;

    ImGui::PushStyleVar(ImGuiStyleVar_WindowPadding, ImVec2(0, 0));
    ImGui::PushStyleVar(ImGuiStyleVar_WindowRounding, 0.0f);
    ImGui::PushStyleVar(ImGuiStyleVar_WindowBorderSize, 0.0f);

    ImGui::Begin("##MainWindow", nullptr, flags);
    ImGui::PopStyleVar(3);

    renderHeader();

    // Cuerpo: Sidebar + Contenido
    float sidebarWidth = 250.0f;
    float headerHeight = 62.0f;
    ImVec2 bodyPos = ImVec2(viewport->WorkPos.x, viewport->WorkPos.y + headerHeight);
    ImVec2 bodySize = ImVec2(viewport->WorkSize.x, viewport->WorkSize.y - headerHeight);

    // Sidebar
    ImGui::SetCursorPos(ImVec2(0, headerHeight));
    ImGui::PushStyleColor(ImGuiCol_ChildBg, tema::BG_SIDEBAR());
    ImGui::BeginChild("##Sidebar", ImVec2(sidebarWidth, bodySize.y), ImGuiChildFlags_Borders);
    renderSidebar();
    ImGui::EndChild();
    ImGui::PopStyleColor();

    // Contenido principal
    ImGui::SetCursorPos(ImVec2(sidebarWidth, headerHeight));
    ImGui::PushStyleColor(ImGuiCol_ChildBg, tema::BG_WINDOW());
    ImGui::BeginChild("##Content", ImVec2(viewport->WorkSize.x - sidebarWidth, bodySize.y), ImGuiChildFlags_None);
    ImGui::PushStyleVar(ImGuiStyleVar_WindowPadding, ImVec2(20, 15));
    renderContenido();
    ImGui::PopStyleVar();
    ImGui::EndChild();
    ImGui::PopStyleColor();

    // Barra de estado
    renderBarraEstado();

    // Modales interactivos CRUD
    renderModales();

    ImGui::End();

    // Render
    ImGui::Render();
    int display_w, display_h;
    glfwGetFramebufferSize(ventana, &display_w, &display_h);
    glViewport(0, 0, display_w, display_h);
    ImVec4 clear = tema::BG_WINDOW();
    glClearColor(clear.x, clear.y, clear.z, clear.w);
    glClear(GL_COLOR_BUFFER_BIT);
    ImGui_ImplOpenGL3_RenderDrawData(ImGui::GetDrawData());
    glfwSwapBuffers(ventana);
}

// ======================================================================
// HEADER INSTITUCIONAL
// ======================================================================

void PITAApp::renderHeader() {
    ImGui::PushStyleColor(ImGuiCol_ChildBg, tema::BG_HEADER());
    ImGui::SetCursorPos(ImVec2(0, 0));
    ImGui::BeginChild("##Header", ImVec2(ImGui::GetWindowWidth(), 62), ImGuiChildFlags_Borders);

    ImGui::SetCursorPos(ImVec2(20, 8));

    if (fuentePequena) ImGui::PushFont(fuentePequena);
    ImGui::TextColored(tema::TEXT_ACCENT(), "UNIVERSIDAD POPULAR DEL CESAR");
    if (fuentePequena) ImGui::PopFont();

    ImGui::SetCursorPosX(20);
    if (fuenteNormal) ImGui::PushFont(fuenteNormal);
    ImGui::TextColored(tema::TEXT_MAIN(), "PITA  -  Sistema Integrado de Transacciones Academicas y Nomina Docente");
    if (fuenteNormal) ImGui::PopFont();

    // Status pill (derecha)
    float pillWidth = 240.0f;
    ImGui::SameLine(ImGui::GetWindowWidth() - pillWidth - 20.0f);
    ImGui::SetCursorPosY(18.0f);

    ImVec4 statusColor = ctrl.datosDisponibles ? tema::ACCENT_SUCCESS() : tema::ACCENT_DANGER();
    const char* statusText = ctrl.datosDisponibles ? "Persistencia Conectada (datos/)" : "Sin Datos Cargados";

    ImGui::PushStyleColor(ImGuiCol_Button, tema::withAlpha(statusColor, 0.15f));
    ImGui::PushStyleColor(ImGuiCol_ButtonHovered, tema::withAlpha(statusColor, 0.25f));
    ImGui::PushStyleColor(ImGuiCol_Text, statusColor);
    ImGui::PushStyleVar(ImGuiStyleVar_FrameRounding, 12.0f);
    ImGui::SmallButton(statusText);
    ImGui::PopStyleVar();
    ImGui::PopStyleColor(3);

    ImGui::EndChild();
    ImGui::PopStyleColor();
}

// ======================================================================
// SIDEBAR NAVIGATION
// ======================================================================

bool PITAApp::sidebarButton(const char* label, bool activo) {
    ImVec4 bg = activo ? tema::withAlpha(tema::WIN_BLUE(), 0.12f) : ImVec4(0, 0, 0, 0);
    ImVec4 bgHover = activo ? tema::withAlpha(tema::WIN_BLUE(), 0.18f) : tema::BG_CARD_HOVER();
    ImVec4 textColor = activo ? tema::WIN_BLUE() : tema::TEXT_MAIN();

    ImGui::PushStyleColor(ImGuiCol_Button, bg);
    ImGui::PushStyleColor(ImGuiCol_ButtonHovered, bgHover);
    ImGui::PushStyleColor(ImGuiCol_ButtonActive, tema::withAlpha(tema::WIN_BLUE(), 0.22f));
    ImGui::PushStyleColor(ImGuiCol_Text, textColor);
    ImGui::PushStyleVar(ImGuiStyleVar_FrameRounding, 8.0f);
    ImGui::PushStyleVar(ImGuiStyleVar_ButtonTextAlign, ImVec2(0.0f, 0.5f));

    bool clicked = ImGui::Button(label, ImVec2(ImGui::GetContentRegionAvail().x, 36));

    ImGui::PopStyleVar(2);
    ImGui::PopStyleColor(4);
    return clicked;
}

void PITAApp::renderSidebar() {
    ImGui::SetCursorPosY(15);

    // Sección NAVEGACIÓN
    if (fuentePequena) ImGui::PushFont(fuentePequena);
    ImGui::SetCursorPosX(20);
    ImGui::TextColored(tema::TEXT_MUTED(), "NAVEGACION");
    if (fuentePequena) ImGui::PopFont();

    ImGui::Spacing();

    ImGui::SetCursorPosX(10);
    ImGui::BeginGroup();

    if (sidebarButton("  Panel de Control",    vistaActiva == VistaActiva::DASHBOARD))  vistaActiva = VistaActiva::DASHBOARD;
    if (sidebarButton("  Facultades & Prog.",   vistaActiva == VistaActiva::FACULTADES)) vistaActiva = VistaActiva::FACULTADES;
    if (sidebarButton("  Gestion de Personas",  vistaActiva == VistaActiva::PERSONAS))   vistaActiva = VistaActiva::PERSONAS;
    if (sidebarButton("  Academico & EBRA",     vistaActiva == VistaActiva::ACADEMICA))  vistaActiva = VistaActiva::ACADEMICA;
    if (sidebarButton("  Contratacion Docente", vistaActiva == VistaActiva::CONTRATOS))  vistaActiva = VistaActiva::CONTRATOS;
    if (sidebarButton("  Nomina & Liquidacion", vistaActiva == VistaActiva::NOMINA))     vistaActiva = VistaActiva::NOMINA;
    if (sidebarButton("  Parametros Legal",     vistaActiva == VistaActiva::PARAMETROS)) vistaActiva = VistaActiva::PARAMETROS;

    ImGui::EndGroup();

    ImGui::Spacing();
    ImGui::Separator();
    ImGui::Spacing();

    // Sección CONTROL DE DATOS
    if (fuentePequena) ImGui::PushFont(fuentePequena);
    ImGui::SetCursorPosX(20);
    ImGui::TextColored(tema::TEXT_MUTED(), "CONTROL DE DATOS");
    if (fuentePequena) ImGui::PopFont();

    ImGui::Spacing();
    ImGui::SetCursorPosX(10);
    ImGui::BeginGroup();

    // Botón Iniciar Sin Datos (Requerimiento #59 Taller PITA)
    ImGui::PushStyleColor(ImGuiCol_Button, tema::withAlpha(tema::TEXT_MUTED(), 0.25f));
    ImGui::PushStyleColor(ImGuiCol_ButtonHovered, tema::withAlpha(tema::TEXT_MUTED(), 0.45f));
    ImGui::PushStyleColor(ImGuiCol_Text, tema::TEXT_MAIN());
    if (ImGui::Button("Iniciar Sin Datos (0 datos)", ImVec2(ImGui::GetContentRegionAvail().x, 30))) {
        ctrl.iniciarSinDatos();
    }
    ImGui::PopStyleColor(3);

    ImGui::Spacing();

    // Botón Recargar Datos
    ImGui::PushStyleColor(ImGuiCol_Button, tema::ACCENT_SUCCESS());
    ImGui::PushStyleColor(ImGuiCol_ButtonHovered, tema::ACCENT_SUCCESS_H());
    ImGui::PushStyleColor(ImGuiCol_Text, tema::TEXT_WHITE());
    if (ImGui::Button("Recargar Datos", ImVec2(ImGui::GetContentRegionAvail().x, 32))) {
        ctrl.cargarDatos();
    }
    ImGui::PopStyleColor(3);

    ImGui::Spacing();

    // Botón Guardar
    ImGui::PushStyleColor(ImGuiCol_Button, tema::WIN_BLUE());
    ImGui::PushStyleColor(ImGuiCol_ButtonHovered, tema::WIN_BLUE_HOVER());
    ImGui::PushStyleColor(ImGuiCol_Text, tema::TEXT_WHITE());
    if (ImGui::Button("Guardar Cambios", ImVec2(ImGui::GetContentRegionAvail().x, 36))) {
        ctrl.guardarDatos();
    }
    ImGui::PopStyleColor(3);

    ImGui::EndGroup();
}

// ======================================================================
// ROUTER DE CONTENIDO
// ======================================================================

void PITAApp::renderContenido() {
    ImGui::SetCursorPos(ImVec2(20, 15));

    switch (vistaActiva) {
        case VistaActiva::DASHBOARD:  renderDashboard();  break;
        case VistaActiva::FACULTADES: renderFacultades(); break;
        case VistaActiva::PERSONAS:   renderPersonas();   break;
        case VistaActiva::ACADEMICA:  renderAcademica();  break;
        case VistaActiva::CONTRATOS:  renderContratos();  break;
        case VistaActiva::NOMINA:     renderNomina();     break;
        case VistaActiva::PARAMETROS: renderParametros(); break;
    }
}

// ======================================================================
// BARRA DE ESTADO (Bottom)
// ======================================================================

void PITAApp::renderBarraEstado() {
    if (ctrl.ultimoMensaje.empty()) return;

    // Mostrar como overlay en la parte inferior
    ImGuiViewport* viewport = ImGui::GetMainViewport();
    ImVec2 msgPos(viewport->WorkPos.x + 260, viewport->WorkPos.y + viewport->WorkSize.y - 32);
    ImVec2 msgSize(viewport->WorkSize.x - 260, 32);

    ImGui::SetNextWindowPos(msgPos);
    ImGui::SetNextWindowSize(msgSize);
    ImGui::PushStyleVar(ImGuiStyleVar_WindowPadding, ImVec2(15, 6));

    ImVec4 bgColor = ctrl.hayError ?
        tema::withAlpha(tema::ACCENT_DANGER(), 0.12f) :
        tema::withAlpha(tema::ACCENT_SUCCESS(), 0.12f);

    ImGui::PushStyleColor(ImGuiCol_WindowBg, bgColor);
    ImGui::Begin("##StatusBar", nullptr,
        ImGuiWindowFlags_NoTitleBar | ImGuiWindowFlags_NoResize |
        ImGuiWindowFlags_NoMove | ImGuiWindowFlags_NoScrollbar |
        ImGuiWindowFlags_NoFocusOnAppearing | ImGuiWindowFlags_NoBringToFrontOnFocus);

    ImVec4 txtColor = ctrl.hayError ? tema::ACCENT_DANGER() : tema::ACCENT_SUCCESS();
    if (fuentePequena) ImGui::PushFont(fuentePequena);
    ImGui::TextColored(txtColor, "%s", ctrl.ultimoMensaje.c_str());
    if (fuentePequena) ImGui::PopFont();

    ImGui::End();
    ImGui::PopStyleColor();
    ImGui::PopStyleVar();
}

// ======================================================================
// HELPER: TARJETA KPI
// ======================================================================

void PITAApp::tarjetaKPI(const char* titulo, const char* valor, ImVec4 color, const char* subtitulo, float cardWidth) {
    ImGui::PushStyleColor(ImGuiCol_ChildBg, tema::BG_CARD());
    ImGui::PushStyleColor(ImGuiCol_Border, tema::BORDER_SUBTLE());
    ImGui::PushStyleVar(ImGuiStyleVar_ChildRounding, 8.0f);
    ImGui::PushStyleVar(ImGuiStyleVar_ChildBorderSize, 1.0f);

    ImGui::BeginChild(titulo, ImVec2(cardWidth, 105), ImGuiChildFlags_Borders);

    // Barra de color superior estética
    ImDrawList* dl = ImGui::GetWindowDrawList();
    ImVec2 minPos = ImGui::GetWindowPos();
    float winWidth = ImGui::GetWindowWidth();
    dl->AddRectFilled(minPos, ImVec2(minPos.x + winWidth, minPos.y + 4.0f),
                      tema::toU32(color), 8.0f, ImDrawFlags_RoundCornersTop);

    ImGui::SetCursorPosY(12);
    ImGui::SetCursorPosX(14);
    if (fuentePequena) ImGui::PushFont(fuentePequena);
    ImGui::TextColored(tema::TEXT_MUTED(), "%s", titulo);
    if (fuentePequena) ImGui::PopFont();

    ImGui::SetCursorPosX(14);
    if (fuenteTitulo) ImGui::PushFont(fuenteTitulo);
    ImGui::TextColored(color, "%s", valor);
    if (fuenteTitulo) ImGui::PopFont();

    ImGui::SetCursorPosX(14);
    if (fuentePequena) ImGui::PushFont(fuentePequena);
    ImGui::TextColored(tema::TEXT_MUTED(), "%s", subtitulo);
    if (fuentePequena) ImGui::PopFont();

    ImGui::EndChild();
    ImGui::PopStyleVar(2);
    ImGui::PopStyleColor(2);
}

// ======================================================================
// VISTA: DASHBOARD
// ======================================================================

void PITAApp::renderDashboard() {
    if (fuenteTitulo) ImGui::PushFont(fuenteTitulo);
    ImGui::TextColored(tema::TEXT_MAIN(), "Panel de Control General");
    if (fuenteTitulo) ImGui::PopFont();

    if (fuentePequena) ImGui::PushFont(fuentePequena);
    ImGui::TextColored(tema::TEXT_MUTED(), "Sistema Integrado de Transacciones Academicas y Nomina Docente - Universidad Popular del Cesar");
    if (fuentePequena) ImGui::PopFont();

    ImGui::Spacing(); ImGui::Spacing();

    // KPIs
    int totalEstudiantes = 0, estudiantesEbra = 0, totalProfesores = 0, contratosActivos = 0;

    for (int i = 0; i < ctrl.datos.estudiantes.tamano(); i++) {
        totalEstudiantes++;
        auto& e = ctrl.datos.estudiantes.obtener(i);
        if (e.estadoAcademico && *e.estadoAcademico == EstadoAcademico::EBRA) estudiantesEbra++;
        else if (e.promedioAcumulado && *e.promedioAcumulado < 3.0) estudiantesEbra++;
    }
    totalProfesores = static_cast<int>(ctrl.datos.profesores.tamano());
    for (int i = 0; i < ctrl.datos.contratos.tamano(); i++) {
        auto& c = ctrl.datos.contratos.obtener(i);
        if (c.estado && *c.estado == "ACTIVO") contratosActivos++;
    }

    char bufEst[32], bufEbra[32], bufProf[32], bufCont[32];
    snprintf(bufEst, sizeof(bufEst), "%d", totalEstudiantes);
    snprintf(bufEbra, sizeof(bufEbra), "%d", estudiantesEbra);
    snprintf(bufProf, sizeof(bufProf), "%d", totalProfesores);
    snprintf(bufCont, sizeof(bufCont), "%d", contratosActivos);

    if (ImGui::BeginTable("##GridKPIDashboard", 4, ImGuiTableFlags_SizingStretchSame)) {
        ImGui::TableNextColumn();
        tarjetaKPI("Estudiantes Registrados", bufEst, tema::WIN_BLUE(), "Activos en programas PITA");

        ImGui::TableNextColumn();
        tarjetaKPI("Alertas EBRA Activas", bufEbra,
                   estudiantesEbra > 0 ? tema::ACCENT_DANGER() : tema::ACCENT_SUCCESS(),
                   "Riesgo academico (< 3.0)");

        ImGui::TableNextColumn();
        tarjetaKPI("Cuerpo Docente", bufProf, tema::ACCENT_INDIGO(), "Planta, Ocasional y Catedra");

        ImGui::TableNextColumn();
        tarjetaKPI("Contratos Docentes", bufCont, tema::ACCENT_WARNING(), "Vinculaciones vigentes");

        ImGui::EndTable();
    }

    ImGui::Spacing(); ImGui::Spacing();

    // Panel de Alertas EBRA y Resumen
    float totalW = ImGui::GetContentRegionAvail().x;
    float halfW = (totalW - 10) / 2.0f;

    // Panel EBRA
    ImGui::PushStyleColor(ImGuiCol_ChildBg, tema::BG_CARD());
    ImGui::PushStyleVar(ImGuiStyleVar_ChildRounding, 10.0f);
    ImGui::BeginChild("##PanelEBRA", ImVec2(halfW, 350), ImGuiChildFlags_Borders);

    ImGui::SetCursorPos(ImVec2(15, 15));
    if (fuenteNormal) ImGui::PushFont(fuenteNormal);
    ImGui::TextColored(tema::ACCENT_DANGER(), "Alertas Tempranas EBRA");
    if (fuenteNormal) ImGui::PopFont();

    ImGui::SetCursorPosX(15);
    if (fuentePequena) ImGui::PushFont(fuentePequena);
    ImGui::TextColored(tema::TEXT_MUTED(), "Estudiantes con promedio acumulado inferior a 3.0");
    if (fuentePequena) ImGui::PopFont();

    ImGui::Spacing();

    if (ImGui::BeginTable("##TablaEBRA", 4, ImGuiTableFlags_RowBg | ImGuiTableFlags_BordersInnerH, ImVec2(halfW - 30, 0))) {
        ImGui::TableSetupColumn("Codigo", ImGuiTableColumnFlags_WidthFixed, 90);
        ImGui::TableSetupColumn("Estudiante", ImGuiTableColumnFlags_WidthStretch);
        ImGui::TableSetupColumn("Prom.", ImGuiTableColumnFlags_WidthFixed, 55);
        ImGui::TableSetupColumn("Estado", ImGuiTableColumnFlags_WidthFixed, 70);
        ImGui::TableHeadersRow();

        for (int i = 0; i < ctrl.datos.estudiantes.tamano(); i++) {
            auto& e = ctrl.datos.estudiantes.obtener(i);
            bool esEbra = (e.estadoAcademico && *e.estadoAcademico == EstadoAcademico::EBRA) ||
                          (e.promedioAcumulado && *e.promedioAcumulado < 3.0);
            if (!esEbra) continue;

            std::string nombre = "---";
            if (e.idPersona) {
                for (int j = 0; j < ctrl.datos.personas.tamano(); j++) {
                    auto& p = ctrl.datos.personas.obtener(j);
                    if (p.idPersona && *p.idPersona == *e.idPersona) {
                        nombre = (p.primerNombre ? *p.primerNombre : "") + " " + (p.primerApellido ? *p.primerApellido : "");
                        break;
                    }
                }
            }

            ImGui::TableNextRow();
            ImGui::TableNextColumn();
            ImGui::Text("%s", e.codigoEstudiante ? e.codigoEstudiante->c_str() : "---");
            ImGui::TableNextColumn();
            ImGui::Text("%s", nombre.c_str());
            ImGui::TableNextColumn();
            ImGui::TextColored(tema::ACCENT_DANGER(), "%.2f", e.promedioAcumulado ? *e.promedioAcumulado : 0.0);
            ImGui::TableNextColumn();

            ImGui::PushStyleColor(ImGuiCol_Button, tema::BADGE_EBRA_BG());
            ImGui::PushStyleColor(ImGuiCol_Text, tema::BADGE_EBRA_TXT());
            ImGui::SmallButton("EBRA");
            ImGui::PopStyleColor(2);
        }
        ImGui::EndTable();
    }

    ImGui::EndChild();
    ImGui::PopStyleVar();
    ImGui::PopStyleColor();

    ImGui::SameLine(0, 10);

    // Panel Resumen Nómina
    ImGui::PushStyleColor(ImGuiCol_ChildBg, tema::BG_CARD());
    ImGui::PushStyleVar(ImGuiStyleVar_ChildRounding, 10.0f);
    ImGui::BeginChild("##PanelNomina", ImVec2(halfW, 350), ImGuiChildFlags_Borders);

    ImGui::SetCursorPos(ImVec2(15, 15));
    if (fuenteNormal) ImGui::PushFont(fuenteNormal);
    ImGui::TextColored(tema::ACCENT_INDIGO(), "Parametros Salariales y Normatividad");
    if (fuenteNormal) ImGui::PopFont();

    ImGui::SetCursorPosX(15);
    if (fuentePequena) ImGui::PushFont(fuentePequena);
    ImGui::TextColored(tema::TEXT_MUTED(), "Decreto 1279 de 2002 / Acuerdo 027 del 31 de octubre de 2024");
    if (fuentePequena) ImGui::PopFont();

    ImGui::Spacing();
    ImGui::SetCursorPosX(15);

    // Estadísticas de nómina
    int totalLiq = static_cast<int>(ctrl.datos.liquidacionesNomina.tamano());
    double totalNeto = 0;
    int liqAprobadas = 0, liqPendientes = 0;

    for (int i = 0; i < ctrl.datos.liquidacionesNomina.tamano(); i++) {
        auto& l = ctrl.datos.liquidacionesNomina.obtener(i);
        if (l.netoPagar) totalNeto += *l.netoPagar;
        if (l.estado && *l.estado == "APROBADA") liqAprobadas++;
        else if (l.estado && *l.estado == "GENERADA") liqPendientes++;
    }

    if (ImGui::BeginTable("##ResumenNomina", 2, ImGuiTableFlags_RowBg | ImGuiTableFlags_BordersInnerH, ImVec2(halfW - 30, 0))) {
        ImGui::TableSetupColumn("Parametro / Metrica", ImGuiTableColumnFlags_WidthStretch);
        ImGui::TableSetupColumn("Valor Institucional", ImGuiTableColumnFlags_WidthFixed, 175);
        ImGui::TableHeadersRow();

        ImGui::TableNextRow();
        ImGui::TableNextColumn(); ImGui::Text("SMMLV Vigente");
        ImGui::TableNextColumn(); ImGui::TextColored(tema::WIN_BLUE(), "$1.750.905 COP");

        ImGui::TableNextRow();
        ImGui::TableNextColumn(); ImGui::Text("Punto Salarial (Dec. 1279)");
        ImGui::TableNextColumn(); ImGui::TextColored(tema::ACCENT_WARNING(), "$23.924 COP");

        ImGui::TableNextRow();
        ImGui::TableNextColumn(); ImGui::Text("Auxilio de Transporte");
        ImGui::TableNextColumn(); ImGui::TextColored(tema::WIN_BLUE(), "$249.095 COP");

        ImGui::TableNextRow();
        ImGui::TableNextColumn(); ImGui::Text("Salud / Pension Trabajador");
        ImGui::TableNextColumn(); ImGui::Text("4.0 %% c/u (IBC)");

        ImGui::TableNextRow();
        ImGui::TableNextColumn(); ImGui::Text("Fondo Solidaridad Pensional");
        ImGui::TableNextColumn(); ImGui::Text("1.0 %% (si IBC >= 4 SMMLV)");

        ImGui::TableNextRow();
        ImGui::TableNextColumn(); ImGui::Text("Liquidaciones Registradas");
        ImGui::TableNextColumn(); ImGui::Text("%d (Aprob: %d, Pend: %d)", totalLiq, liqAprobadas, liqPendientes);

        ImGui::TableNextRow();
        ImGui::TableNextColumn(); ImGui::Text("Masa Pagada Consolidada");
        ImGui::TableNextColumn();
        char buf[64];
        snprintf(buf, sizeof(buf), "$%.0f COP", totalNeto);
        ImGui::TextColored(tema::ACCENT_SUCCESS(), "%s", buf);

        ImGui::EndTable();
    }

    ImGui::EndChild();
    ImGui::PopStyleVar();
    ImGui::PopStyleColor();
}

// ======================================================================
// DISPATCHER DE MODALES
// ======================================================================

void PITAApp::renderModales() {
    renderModalPersona();
    renderModalEditarAdministrativo();
    renderModalFacultad();
    renderModalPrograma();
    renderModalCurso();
    renderModalMatricula();
    renderModalNota();
    renderModalContrato();
    renderModalTerminarContrato();
    renderModalReconocerPuntos();
    renderModalPeriodoNomina();
    renderModalLiquidar();
    renderModalPagarNomina();
    renderModalDesprendible();
    renderModalLiquidarIndividual();
    renderModalParametro();
}

} // namespace pita
