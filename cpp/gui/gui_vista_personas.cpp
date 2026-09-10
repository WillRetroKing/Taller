#define _CRT_SECURE_NO_WARNINGS
#include "gui_app.h"
#include "tema.h"
#include "imgui.h"

#include <cstring>
#include <string>
#include <cmath>
#include <algorithm>

namespace pita {

static std::string formatearMoneda(double valor) {
    long long entero = static_cast<long long>(std::round(valor));
    std::string s = std::to_string(entero);
    std::string res = "";
    int cont = 0;
    for (int i = static_cast<int>(s.length()) - 1; i >= 0; i--) {
        res = s[i] + res;
        cont++;
        if (cont == 3 && i > 0) {
            res = "." + res;
            cont = 0;
        }
    }
    return "$" + res + " COP";
}

// ======================================================================
// HELPERS DE APERTURA DE MODALES
// ======================================================================

void PITAApp::abrirModalDetallePersona(int idPersona) {
    idPersonaDetalle = idPersona;
    modalDetallePersonaAbierto = true;
}

void PITAApp::abrirModalEditarEstudiante(int idEstudiante) {
    idEstudianteEditando = idEstudiante;
    mensajeModal[0] = '\0';
    errorModal = false;

    for (size_t i = 0; i < ctrl.datos.estudiantes.tamano(); ++i) {
        auto& e = ctrl.datos.estudiantes.obtener(i);
        if (e.idEstudiante && *e.idEstudiante == idEstudiante) {
            strncpy(editEstCodigo, e.codigoEstudiante ? e.codigoEstudiante->c_str() : "", sizeof(editEstCodigo) - 1);
            editEstCodigo[sizeof(editEstCodigo) - 1] = '\0';

            editEstProgramaId = e.idPrograma.value_or(1);
            editEstSemestre = e.semestreActual.value_or(1);
            editEstCreditos = e.creditosAprobados.value_or(0);
            editEstPromedio = static_cast<float>(e.promedioAcumulado.value_or(4.0));

            // Estado académico
            editEstEstadoAcadIdx = 0;
            if (e.estadoAcademico) {
                switch (*e.estadoAcademico) {
                    case EstadoAcademico::MATRICULADO: editEstEstadoAcadIdx = 0; break;
                    case EstadoAcademico::EBRA: editEstEstadoAcadIdx = 1; break;
                    case EstadoAcademico::ACTIVO: editEstEstadoAcadIdx = 2; break;
                    case EstadoAcademico::GRADUADO: editEstEstadoAcadIdx = 3; break;
                    case EstadoAcademico::RETIRADO: editEstEstadoAcadIdx = 4; break;
                    case EstadoAcademico::SUSPENDIDO: editEstEstadoAcadIdx = 5; break;
                    default: editEstEstadoAcadIdx = 0; break;
                }
            }

            editEstEstadoIdx = (e.estado && *e.estado == "INACTIVO") ? 1 : 0;
            break;
        }
    }

    modalEditarEstudianteAbierto = true;
}

void PITAApp::abrirModalEditarProfesor(int idProfesor) {
    idProfesorEditando = idProfesor;
    mensajeModal[0] = '\0';
    errorModal = false;

    for (size_t i = 0; i < ctrl.datos.profesores.tamano(); ++i) {
        auto& prof = ctrl.datos.profesores.obtener(i);
        if (prof.idProfesor && *prof.idProfesor == idProfesor) {
            strncpy(editProfCodigo, prof.codigoProfesor ? prof.codigoProfesor->c_str() : "", sizeof(editProfCodigo) - 1);
            editProfCodigo[sizeof(editProfCodigo) - 1] = '\0';

            // Tipo profesor
            editProfTipoIdx = 0;
            if (prof.tipoProfesor) {
                if (*prof.tipoProfesor == TipoProfesor::OCASIONAL) editProfTipoIdx = 1;
                else if (*prof.tipoProfesor == TipoProfesor::CATEDRATICO) editProfTipoIdx = 2;
                else editProfTipoIdx = 0;
            }

            // Dedicación
            editProfDedicacionIdx = 0;
            if (prof.dedicacion) {
                if (*prof.dedicacion == Dedicacion::MEDIO_TIEMPO) editProfDedicacionIdx = 1;
                else if (*prof.dedicacion == Dedicacion::HORA_CATEDRA) editProfDedicacionIdx = 2;
                else editProfDedicacionIdx = 0;
            }

            editProfHoras = prof.numeroHorasSemanales.value_or(40.0);
            editProfPuntos = prof.puntosSalariales.value_or(0.0);

            // Categoría
            std::string cat = prof.categoriaDocente.value_or("TITULAR");
            if (cat == "ASOCIADO") editProfCategoriaIdx = 1;
            else if (cat == "ASISTENTE") editProfCategoriaIdx = 2;
            else if (cat == "AUXILIAR") editProfCategoriaIdx = 3;
            else editProfCategoriaIdx = 0;

            editProfEstadoIdx = (prof.estado && *prof.estado == "INACTIVO") ? 1 : 0;
            break;
        }
    }

    modalEditarProfesorAbierto = true;
}

// ======================================================================
// VISTA: PERSONAS
// ======================================================================

void PITAApp::renderPersonas() {
    float btnWidth = 240.0f;
    float availW = ImGui::GetContentRegionAvail().x;

    if (fuenteTitulo) ImGui::PushFont(fuenteTitulo);
    ImGui::TextColored(tema::TEXT_MAIN(), "Gestion de Personas e Identificacion");
    if (fuenteTitulo) ImGui::PopFont();

    if (fuentePequena) ImGui::PushFont(fuentePequena);
    ImGui::TextColored(tema::TEXT_MUTED(), "Directorio maestro de Personas, Estudiantes, Profesores y Administrativos de la UPC");
    if (fuentePequena) ImGui::PopFont();

    ImGui::SameLine(availW - btnWidth);
    ImGui::SetCursorPosY(ImGui::GetCursorPosY() - 6.0f);

    ImGui::PushStyleColor(ImGuiCol_Button, tema::WIN_BLUE());
    ImGui::PushStyleColor(ImGuiCol_ButtonHovered, tema::WIN_BLUE_HOVER());
    if (ImGui::Button("+ Registrar Persona / Asignar Rol", ImVec2(btnWidth, 32))) {
        abrirModalPersona(false, 0);
    }
    ImGui::PopStyleColor(2);

    ImGui::Spacing();
    ImGui::Spacing();

    if (ImGui::BeginTabBar("##TabsPersonas")) {

        // ==============================================================
        // TAB 1: PERSONAS (DIRECTORIO MAESTRO)
        // ==============================================================
        if (ImGui::BeginTabItem("Personas Maestro")) {
            ImGui::Spacing();

            // Buscador dinámico
            ImGui::SetNextItemWidth(340);
            ImGui::InputTextWithHint("##BuscarPersona", "Filtrar por documento, nombre o correo...", perFiltroBusqueda, sizeof(perFiltroBusqueda));
            ImGui::SameLine();
            if (ImGui::Button("Limpiar##Per")) {
                perFiltroBusqueda[0] = '\0';
            }
            ImGui::SameLine();
            ImGui::TextColored(tema::TEXT_MUTED(), "(%d personas registradas)", ctrl.datos.personas.tamano());

            ImGui::Spacing();

            if (ImGui::BeginTable("##TablaPersonas", 8,
                ImGuiTableFlags_RowBg | ImGuiTableFlags_BordersOuter | ImGuiTableFlags_BordersInnerH |
                ImGuiTableFlags_Resizable | ImGuiTableFlags_ScrollY, ImVec2(0, 0))) {

                ImGui::TableSetupColumn("ID", ImGuiTableColumnFlags_WidthFixed, 45);
                ImGui::TableSetupColumn("Tipo Doc.", ImGuiTableColumnFlags_WidthFixed, 80);
                ImGui::TableSetupColumn("No. Documento", ImGuiTableColumnFlags_WidthFixed, 115);
                ImGui::TableSetupColumn("Nombre Completo", ImGuiTableColumnFlags_WidthStretch);
                ImGui::TableSetupColumn("Correo Electronico", ImGuiTableColumnFlags_WidthStretch);
                ImGui::TableSetupColumn("Ciudad Residencia", ImGuiTableColumnFlags_WidthFixed, 115);
                ImGui::TableSetupColumn("Estado", ImGuiTableColumnFlags_WidthFixed, 80);
                ImGui::TableSetupColumn("Acciones", ImGuiTableColumnFlags_WidthFixed, 190);
                ImGui::TableHeadersRow();

                std::string busqPer = perFiltroBusqueda;
                for (auto& ch : busqPer) ch = (char)tolower(ch);

                for (size_t i = 0; i < ctrl.datos.personas.tamano(); i++) {
                    auto& p = ctrl.datos.personas.obtener(i);
                    int pId = p.idPersona.value_or(0);

                    std::string nombre = (p.primerNombre ? *p.primerNombre : "") + " " +
                                         (p.segundoNombre ? *p.segundoNombre + " " : "") +
                                         (p.primerApellido ? *p.primerApellido : "") + " " +
                                         (p.segundoApellido ? *p.segundoApellido : "");

                    if (!busqPer.empty()) {
                        std::string nLower = nombre;
                        for (auto& ch : nLower) ch = (char)tolower(ch);
                        std::string docLower = p.numeroDocumento ? *p.numeroDocumento : "";
                        for (auto& ch : docLower) ch = (char)tolower(ch);
                        std::string mailLower = p.correoPersonal ? *p.correoPersonal : "";
                        for (auto& ch : mailLower) ch = (char)tolower(ch);

                        if (nLower.find(busqPer) == std::string::npos &&
                            docLower.find(busqPer) == std::string::npos &&
                            mailLower.find(busqPer) == std::string::npos) {
                            continue;
                        }
                    }

                    ImGui::TableNextRow();
                    ImGui::TableNextColumn(); ImGui::Text("%d", pId);
                    ImGui::TableNextColumn(); ImGui::Text("%s", p.tipoDocumento ? p.tipoDocumento->c_str() : "CC");
                    ImGui::TableNextColumn(); ImGui::TextColored(tema::ACCENT_WARNING(), "%s", p.numeroDocumento ? p.numeroDocumento->c_str() : "---");
                    ImGui::TableNextColumn(); ImGui::Text("%s", nombre.c_str());
                    ImGui::TableNextColumn(); ImGui::Text("%s", p.correoPersonal ? p.correoPersonal->c_str() : "---");
                    ImGui::TableNextColumn(); ImGui::Text("%s", p.ciudadResidencia ? p.ciudadResidencia->c_str() : "---");

                    ImGui::TableNextColumn();
                    bool esActivo = (!p.estado || *p.estado == "ACTIVO");
                    if (esActivo) {
                        ImGui::PushStyleColor(ImGuiCol_Button, tema::BADGE_ACTIVE_BG());
                        ImGui::PushStyleColor(ImGuiCol_Text, tema::BADGE_ACTIVE_TXT());
                        ImGui::SmallButton("ACTIVO");
                        ImGui::PopStyleColor(2);
                    } else {
                        ImGui::PushStyleColor(ImGuiCol_Button, tema::withAlpha(tema::ACCENT_DANGER(), 0.15f));
                        ImGui::PushStyleColor(ImGuiCol_Text, tema::ACCENT_DANGER());
                        ImGui::SmallButton("INACTIVO");
                        ImGui::PopStyleColor(2);
                    }

                    ImGui::TableNextColumn();
                    ImGui::PushID(static_cast<int>(i));

                    ImGui::PushStyleColor(ImGuiCol_Button, tema::withAlpha(tema::ACCENT_INDIGO(), 0.18f));
                    ImGui::PushStyleColor(ImGuiCol_Text, tema::ACCENT_INDIGO());
                    if (ImGui::SmallButton("Ver")) {
                        abrirModalDetallePersona(pId);
                    }
                    ImGui::PopStyleColor(2);

                    ImGui::SameLine();
                    ImGui::PushStyleColor(ImGuiCol_Button, tema::withAlpha(tema::WIN_BLUE(), 0.18f));
                    ImGui::PushStyleColor(ImGuiCol_Text, tema::WIN_BLUE());
                    if (ImGui::SmallButton("Editar")) {
                        abrirModalPersona(true, pId);
                    }
                    ImGui::PopStyleColor(2);

                    ImGui::SameLine();
                    if (esActivo) {
                        ImGui::PushStyleColor(ImGuiCol_Button, tema::withAlpha(tema::ACCENT_DANGER(), 0.18f));
                        ImGui::PushStyleColor(ImGuiCol_Text, tema::ACCENT_DANGER());
                        if (ImGui::SmallButton("Desactivar")) {
                            p.estado = "INACTIVO";
                            ctrl.guardarDatos();
                            ctrl.setMensaje("Persona desactivada en el sistema.");
                        }
                        ImGui::PopStyleColor(2);
                    } else {
                        ImGui::PushStyleColor(ImGuiCol_Button, tema::withAlpha(tema::ACCENT_SUCCESS(), 0.18f));
                        ImGui::PushStyleColor(ImGuiCol_Text, tema::ACCENT_SUCCESS());
                        if (ImGui::SmallButton("Activar")) {
                            p.estado = "ACTIVO";
                            ctrl.guardarDatos();
                            ctrl.setMensaje("Persona activada en el sistema.");
                        }
                        ImGui::PopStyleColor(2);
                    }

                    ImGui::PopID();
                }
                ImGui::EndTable();
            }
            ImGui::EndTabItem();
        }

        // ==============================================================
        // TAB 2: ESTUDIANTES
        // ==============================================================
        if (ImGui::BeginTabItem("Estudiantes")) {
            ImGui::Spacing();

            ImGui::SetNextItemWidth(340);
            ImGui::InputTextWithHint("##BuscarEstudiante", "Buscar por nombre, documento o codigo estudiantil...", estFiltroBusqueda, sizeof(estFiltroBusqueda));
            ImGui::SameLine();
            if (ImGui::Button("Limpiar##Est")) {
                estFiltroBusqueda[0] = '\0';
            }
            ImGui::SameLine();
            ImGui::TextColored(tema::TEXT_MUTED(), "(%d estudiantes matriculados)", ctrl.datos.estudiantes.tamano());

            ImGui::Spacing();

            if (ImGui::BeginTable("##TablaEstudiantes", 9,
                ImGuiTableFlags_RowBg | ImGuiTableFlags_BordersOuter | ImGuiTableFlags_BordersInnerH |
                ImGuiTableFlags_Resizable | ImGuiTableFlags_ScrollY, ImVec2(0, 0))) {

                ImGui::TableSetupColumn("Codigo", ImGuiTableColumnFlags_WidthFixed, 105);
                ImGui::TableSetupColumn("Documento", ImGuiTableColumnFlags_WidthFixed, 100);
                ImGui::TableSetupColumn("Nombre Completo", ImGuiTableColumnFlags_WidthStretch);
                ImGui::TableSetupColumn("Sem.", ImGuiTableColumnFlags_WidthFixed, 55);
                ImGui::TableSetupColumn("Cred.", ImGuiTableColumnFlags_WidthFixed, 55);
                ImGui::TableSetupColumn("Promedio", ImGuiTableColumnFlags_WidthFixed, 75);
                ImGui::TableSetupColumn("Condicion", ImGuiTableColumnFlags_WidthFixed, 85);
                ImGui::TableSetupColumn("Estado", ImGuiTableColumnFlags_WidthFixed, 80);
                ImGui::TableSetupColumn("Acciones", ImGuiTableColumnFlags_WidthFixed, 190);
                ImGui::TableHeadersRow();

                std::string busqEst = estFiltroBusqueda;
                for (auto& ch : busqEst) ch = (char)tolower(ch);

                for (size_t i = 0; i < ctrl.datos.estudiantes.tamano(); i++) {
                    auto& e = ctrl.datos.estudiantes.obtener(i);
                    int eId = e.idEstudiante.value_or(0);
                    int pId = e.idPersona.value_or(0);

                    std::string doc = "N/A";
                    std::string nombre = "Sin Persona";

                    for (size_t j = 0; j < ctrl.datos.personas.tamano(); j++) {
                        auto& p = ctrl.datos.personas.obtener(j);
                        if (p.idPersona && *p.idPersona == pId) {
                            doc = p.numeroDocumento.value_or("N/A");
                            nombre = (p.primerNombre ? *p.primerNombre : "") + " " + (p.primerApellido ? *p.primerApellido : "");
                            break;
                        }
                    }

                    if (!busqEst.empty()) {
                        std::string nLower = nombre;
                        for (auto& ch : nLower) ch = (char)tolower(ch);
                        std::string codLower = e.codigoEstudiante ? *e.codigoEstudiante : "";
                        for (auto& ch : codLower) ch = (char)tolower(ch);
                        std::string docLower = doc;
                        for (auto& ch : docLower) ch = (char)tolower(ch);

                        if (nLower.find(busqEst) == std::string::npos &&
                            codLower.find(busqEst) == std::string::npos &&
                            docLower.find(busqEst) == std::string::npos) {
                            continue;
                        }
                    }

                    double prom = e.promedioAcumulado.value_or(0.0);
                    bool esEbra = (e.estadoAcademico && *e.estadoAcademico == EstadoAcademico::EBRA) || (prom < 3.0);
                    bool esActivo = (!e.estado || *e.estado == "ACTIVO");

                    ImGui::TableNextRow();
                    ImGui::TableNextColumn();
                    ImGui::TextColored(tema::WIN_BLUE(), "%s", e.codigoEstudiante ? e.codigoEstudiante->c_str() : "---");

                    ImGui::TableNextColumn();
                    ImGui::Text("%s", doc.c_str());

                    ImGui::TableNextColumn();
                    ImGui::Text("%s", nombre.c_str());

                    ImGui::TableNextColumn();
                    ImGui::Text("%d", e.semestreActual ? *e.semestreActual : 1);

                    ImGui::TableNextColumn();
                    ImGui::Text("%d", e.creditosAprobados ? *e.creditosAprobados : 0);

                    ImGui::TableNextColumn();
                    if (prom < 3.0) {
                        ImGui::TextColored(tema::ACCENT_DANGER(), "%.2f", prom);
                    } else {
                        ImGui::TextColored(tema::ACCENT_SUCCESS(), "%.2f", prom);
                    }

                    ImGui::TableNextColumn();
                    if (esEbra) {
                        ImGui::PushStyleColor(ImGuiCol_Button, tema::BADGE_EBRA_BG());
                        ImGui::PushStyleColor(ImGuiCol_Text, tema::BADGE_EBRA_TXT());
                        ImGui::SmallButton("EBRA");
                        ImGui::PopStyleColor(2);
                    } else {
                        ImGui::PushStyleColor(ImGuiCol_Button, tema::withAlpha(tema::TEXT_MUTED(), 0.15f));
                        ImGui::PushStyleColor(ImGuiCol_Text, tema::TEXT_MUTED());
                        ImGui::SmallButton("Regular");
                        ImGui::PopStyleColor(2);
                    }

                    ImGui::TableNextColumn();
                    if (esActivo) {
                        ImGui::PushStyleColor(ImGuiCol_Button, tema::BADGE_ACTIVE_BG());
                        ImGui::PushStyleColor(ImGuiCol_Text, tema::BADGE_ACTIVE_TXT());
                        ImGui::SmallButton("ACTIVO");
                        ImGui::PopStyleColor(2);
                    } else {
                        ImGui::PushStyleColor(ImGuiCol_Button, tema::withAlpha(tema::ACCENT_DANGER(), 0.15f));
                        ImGui::PushStyleColor(ImGuiCol_Text, tema::ACCENT_DANGER());
                        ImGui::SmallButton("INACTIVO");
                        ImGui::PopStyleColor(2);
                    }

                    ImGui::TableNextColumn();
                    ImGui::PushID(static_cast<int>(1000 + i));

                    ImGui::PushStyleColor(ImGuiCol_Button, tema::withAlpha(tema::ACCENT_INDIGO(), 0.18f));
                    ImGui::PushStyleColor(ImGuiCol_Text, tema::ACCENT_INDIGO());
                    if (ImGui::SmallButton("Ver")) {
                        abrirModalDetallePersona(pId);
                    }
                    ImGui::PopStyleColor(2);

                    ImGui::SameLine();
                    ImGui::PushStyleColor(ImGuiCol_Button, tema::withAlpha(tema::WIN_BLUE(), 0.18f));
                    ImGui::PushStyleColor(ImGuiCol_Text, tema::WIN_BLUE());
                    if (ImGui::SmallButton("Editar")) {
                        abrirModalEditarEstudiante(eId);
                    }
                    ImGui::PopStyleColor(2);

                    ImGui::SameLine();
                    if (esActivo) {
                        ImGui::PushStyleColor(ImGuiCol_Button, tema::withAlpha(tema::ACCENT_DANGER(), 0.18f));
                        ImGui::PushStyleColor(ImGuiCol_Text, tema::ACCENT_DANGER());
                        if (ImGui::SmallButton("Desactivar")) {
                            e.estado = "INACTIVO";
                            ctrl.guardarDatos();
                            ctrl.setMensaje("Estudiante desactivado.");
                        }
                        ImGui::PopStyleColor(2);
                    } else {
                        ImGui::PushStyleColor(ImGuiCol_Button, tema::withAlpha(tema::ACCENT_SUCCESS(), 0.18f));
                        ImGui::PushStyleColor(ImGuiCol_Text, tema::ACCENT_SUCCESS());
                        if (ImGui::SmallButton("Activar")) {
                            e.estado = "ACTIVO";
                            ctrl.guardarDatos();
                            ctrl.setMensaje("Estudiante activado.");
                        }
                        ImGui::PopStyleColor(2);
                    }

                    ImGui::PopID();
                }
                ImGui::EndTable();
            }
            ImGui::EndTabItem();
        }

        // ==============================================================
        // TAB 3: PROFESORES
        // ==============================================================
        if (ImGui::BeginTabItem("Profesores")) {
            ImGui::Spacing();

            ImGui::SetNextItemWidth(340);
            ImGui::InputTextWithHint("##BuscarProfesor", "Buscar por nombre, documento o codigo docente...", profFiltroBusqueda, sizeof(profFiltroBusqueda));
            ImGui::SameLine();
            if (ImGui::Button("Limpiar##Prof")) {
                profFiltroBusqueda[0] = '\0';
            }
            ImGui::SameLine();
            ImGui::TextColored(tema::TEXT_MUTED(), "(%d docentes vinculados)", ctrl.datos.profesores.tamano());

            ImGui::Spacing();

            if (ImGui::BeginTable("##TablaProfesores", 9,
                ImGuiTableFlags_RowBg | ImGuiTableFlags_BordersOuter | ImGuiTableFlags_BordersInnerH |
                ImGuiTableFlags_Resizable | ImGuiTableFlags_ScrollY, ImVec2(0, 0))) {

                ImGui::TableSetupColumn("Codigo", ImGuiTableColumnFlags_WidthFixed, 105);
                ImGui::TableSetupColumn("Documento", ImGuiTableColumnFlags_WidthFixed, 100);
                ImGui::TableSetupColumn("Nombre Docente", ImGuiTableColumnFlags_WidthStretch);
                ImGui::TableSetupColumn("Tipo / Modalidad", ImGuiTableColumnFlags_WidthFixed, 130);
                ImGui::TableSetupColumn("Categoria", ImGuiTableColumnFlags_WidthFixed, 100);
                ImGui::TableSetupColumn("Dedicacion", ImGuiTableColumnFlags_WidthFixed, 120);
                ImGui::TableSetupColumn("Puntos Dec. 1279", ImGuiTableColumnFlags_WidthFixed, 115);
                ImGui::TableSetupColumn("Estado", ImGuiTableColumnFlags_WidthFixed, 80);
                ImGui::TableSetupColumn("Acciones", ImGuiTableColumnFlags_WidthFixed, 190);
                ImGui::TableHeadersRow();

                std::string busqProf = profFiltroBusqueda;
                for (auto& ch : busqProf) ch = (char)tolower(ch);

                for (size_t i = 0; i < ctrl.datos.profesores.tamano(); i++) {
                    auto& prof = ctrl.datos.profesores.obtener(i);
                    int profId = prof.idProfesor.value_or(0);
                    int pId = prof.idPersona.value_or(0);

                    std::string doc = "N/A";
                    std::string nombre = "Sin Persona";

                    for (size_t j = 0; j < ctrl.datos.personas.tamano(); j++) {
                        auto& p = ctrl.datos.personas.obtener(j);
                        if (p.idPersona && *p.idPersona == pId) {
                            doc = p.numeroDocumento.value_or("N/A");
                            nombre = (p.primerNombre ? *p.primerNombre : "") + " " + (p.primerApellido ? *p.primerApellido : "");
                            break;
                        }
                    }

                    if (!busqProf.empty()) {
                        std::string nLower = nombre;
                        for (auto& ch : nLower) ch = (char)tolower(ch);
                        std::string codLower = prof.codigoProfesor ? *prof.codigoProfesor : "";
                        for (auto& ch : codLower) ch = (char)tolower(ch);
                        std::string docLower = doc;
                        for (auto& ch : docLower) ch = (char)tolower(ch);

                        if (nLower.find(busqProf) == std::string::npos &&
                            codLower.find(busqProf) == std::string::npos &&
                            docLower.find(busqProf) == std::string::npos) {
                            continue;
                        }
                    }

                    bool esActivo = (!prof.estado || *prof.estado == "ACTIVO");

                    ImGui::TableNextRow();
                    ImGui::TableNextColumn();
                    ImGui::TextColored(tema::ACCENT_INDIGO(), "%s", prof.codigoProfesor ? prof.codigoProfesor->c_str() : "---");

                    ImGui::TableNextColumn();
                    ImGui::Text("%s", doc.c_str());

                    ImGui::TableNextColumn();
                    ImGui::Text("%s", nombre.c_str());

                    ImGui::TableNextColumn();
                    ImGui::Text("%s", prof.tipoProfesor ? to_string(*prof.tipoProfesor).c_str() : "---");

                    ImGui::TableNextColumn();
                    ImGui::Text("%s", prof.categoriaDocente ? prof.categoriaDocente->c_str() : "TITULAR");

                    ImGui::TableNextColumn();
                    ImGui::Text("%s", prof.dedicacion ? to_string(*prof.dedicacion).c_str() : "---");

                    ImGui::TableNextColumn();
                    double pts = prof.puntosSalariales.value_or(0.0);
                    ImGui::TextColored(tema::ACCENT_WARNING(), "%.0f pts", pts);

                    ImGui::TableNextColumn();
                    if (esActivo) {
                        ImGui::PushStyleColor(ImGuiCol_Button, tema::BADGE_ACTIVE_BG());
                        ImGui::PushStyleColor(ImGuiCol_Text, tema::BADGE_ACTIVE_TXT());
                        ImGui::SmallButton("ACTIVO");
                        ImGui::PopStyleColor(2);
                    } else {
                        ImGui::PushStyleColor(ImGuiCol_Button, tema::withAlpha(tema::ACCENT_DANGER(), 0.15f));
                        ImGui::PushStyleColor(ImGuiCol_Text, tema::ACCENT_DANGER());
                        ImGui::SmallButton("INACTIVO");
                        ImGui::PopStyleColor(2);
                    }

                    ImGui::TableNextColumn();
                    ImGui::PushID(static_cast<int>(3000 + i));

                    ImGui::PushStyleColor(ImGuiCol_Button, tema::withAlpha(tema::ACCENT_INDIGO(), 0.18f));
                    ImGui::PushStyleColor(ImGuiCol_Text, tema::ACCENT_INDIGO());
                    if (ImGui::SmallButton("Ver")) {
                        abrirModalDetallePersona(pId);
                    }
                    ImGui::PopStyleColor(2);

                    ImGui::SameLine();
                    ImGui::PushStyleColor(ImGuiCol_Button, tema::withAlpha(tema::WIN_BLUE(), 0.18f));
                    ImGui::PushStyleColor(ImGuiCol_Text, tema::WIN_BLUE());
                    if (ImGui::SmallButton("Editar")) {
                        abrirModalEditarProfesor(profId);
                    }
                    ImGui::PopStyleColor(2);

                    ImGui::SameLine();
                    if (esActivo) {
                        ImGui::PushStyleColor(ImGuiCol_Button, tema::withAlpha(tema::ACCENT_DANGER(), 0.18f));
                        ImGui::PushStyleColor(ImGuiCol_Text, tema::ACCENT_DANGER());
                        if (ImGui::SmallButton("Desactivar")) {
                            prof.estado = "INACTIVO";
                            ctrl.guardarDatos();
                            ctrl.setMensaje("Profesor desactivado.");
                        }
                        ImGui::PopStyleColor(2);
                    } else {
                        ImGui::PushStyleColor(ImGuiCol_Button, tema::withAlpha(tema::ACCENT_SUCCESS(), 0.18f));
                        ImGui::PushStyleColor(ImGuiCol_Text, tema::ACCENT_SUCCESS());
                        if (ImGui::SmallButton("Activar")) {
                            prof.estado = "ACTIVO";
                            ctrl.guardarDatos();
                            ctrl.setMensaje("Profesor activado.");
                        }
                        ImGui::PopStyleColor(2);
                    }

                    ImGui::PopID();
                }
                ImGui::EndTable();
            }
            ImGui::EndTabItem();
        }

        // ==============================================================
        // TAB 4: ADMINISTRATIVOS
        // ==============================================================
        if (ImGui::BeginTabItem("Administrativos")) {
            ImGui::Spacing();

            if (ImGui::BeginTable("##TablaAdmin", 9,
                ImGuiTableFlags_RowBg | ImGuiTableFlags_BordersOuter | ImGuiTableFlags_BordersInnerH |
                ImGuiTableFlags_Resizable | ImGuiTableFlags_ScrollY, ImVec2(0, 0))) {

                ImGui::TableSetupColumn("Codigo", ImGuiTableColumnFlags_WidthFixed, 95);
                ImGui::TableSetupColumn("Documento", ImGuiTableColumnFlags_WidthFixed, 100);
                ImGui::TableSetupColumn("Nombre Completo", ImGuiTableColumnFlags_WidthStretch);
                ImGui::TableSetupColumn("Cargo", ImGuiTableColumnFlags_WidthStretch);
                ImGui::TableSetupColumn("Dependencia", ImGuiTableColumnFlags_WidthStretch);
                ImGui::TableSetupColumn("Nivel", ImGuiTableColumnFlags_WidthFixed, 100);
                ImGui::TableSetupColumn("Salario Base", ImGuiTableColumnFlags_WidthFixed, 120);
                ImGui::TableSetupColumn("Estado", ImGuiTableColumnFlags_WidthFixed, 80);
                ImGui::TableSetupColumn("Acciones", ImGuiTableColumnFlags_WidthFixed, 190);
                ImGui::TableHeadersRow();

                for (size_t i = 0; i < ctrl.datos.administrativos.tamano(); i++) {
                    auto& a = ctrl.datos.administrativos.obtener(i);
                    int admId = a.idAdministrativo.value_or(0);
                    int pId = a.idPersona.value_or(0);

                    std::string doc = "N/A";
                    std::string nombre = "Sin Persona";

                    for (size_t j = 0; j < ctrl.datos.personas.tamano(); j++) {
                        auto& p = ctrl.datos.personas.obtener(j);
                        if (p.idPersona && *p.idPersona == pId) {
                            doc = p.numeroDocumento.value_or("N/A");
                            nombre = (p.primerNombre ? *p.primerNombre : "") + " " + (p.primerApellido ? *p.primerApellido : "");
                            break;
                        }
                    }

                    bool esActivo = (!a.estado || *a.estado == "ACTIVO");

                    ImGui::TableNextRow();
                    ImGui::TableNextColumn();
                    ImGui::TextColored(tema::ACCENT_WARNING(), "%s", a.codigoEmpleado ? a.codigoEmpleado->c_str() : "---");

                    ImGui::TableNextColumn();
                    ImGui::Text("%s", doc.c_str());

                    ImGui::TableNextColumn();
                    ImGui::Text("%s", nombre.c_str());

                    ImGui::TableNextColumn();
                    ImGui::Text("%s", a.cargo ? a.cargo->c_str() : "---");

                    ImGui::TableNextColumn();
                    ImGui::Text("%s", a.dependencia ? a.dependencia->c_str() : "---");

                    ImGui::TableNextColumn();
                    ImGui::Text("%s", a.categoria ? a.categoria->c_str() : "PROFESIONAL");

                    ImGui::TableNextColumn();
                    double salVal = a.salarioBase.value_or(0.0);
                    ImGui::TextColored(tema::ACCENT_SUCCESS(), "%s", formatearMoneda(salVal).c_str());

                    ImGui::TableNextColumn();
                    if (esActivo) {
                        ImGui::PushStyleColor(ImGuiCol_Button, tema::BADGE_ACTIVE_BG());
                        ImGui::PushStyleColor(ImGuiCol_Text, tema::BADGE_ACTIVE_TXT());
                        ImGui::SmallButton("ACTIVO");
                        ImGui::PopStyleColor(2);
                    } else {
                        ImGui::PushStyleColor(ImGuiCol_Button, tema::withAlpha(tema::ACCENT_DANGER(), 0.15f));
                        ImGui::PushStyleColor(ImGuiCol_Text, tema::ACCENT_DANGER());
                        ImGui::SmallButton("INACTIVO");
                        ImGui::PopStyleColor(2);
                    }

                    ImGui::TableNextColumn();
                    ImGui::PushID(static_cast<int>(5000 + i));

                    ImGui::PushStyleColor(ImGuiCol_Button, tema::withAlpha(tema::ACCENT_INDIGO(), 0.18f));
                    ImGui::PushStyleColor(ImGuiCol_Text, tema::ACCENT_INDIGO());
                    if (ImGui::SmallButton("Ver")) {
                        abrirModalDetallePersona(pId);
                    }
                    ImGui::PopStyleColor(2);

                    ImGui::SameLine();
                    ImGui::PushStyleColor(ImGuiCol_Button, tema::withAlpha(tema::WIN_BLUE(), 0.18f));
                    ImGui::PushStyleColor(ImGuiCol_Text, tema::WIN_BLUE());
                    if (ImGui::SmallButton("Editar")) {
                        abrirModalEditarAdministrativo(admId);
                    }
                    ImGui::PopStyleColor(2);

                    ImGui::SameLine();
                    if (esActivo) {
                        ImGui::PushStyleColor(ImGuiCol_Button, tema::withAlpha(tema::ACCENT_DANGER(), 0.18f));
                        ImGui::PushStyleColor(ImGuiCol_Text, tema::ACCENT_DANGER());
                        if (ImGui::SmallButton("Desactivar")) {
                            a.estado = "INACTIVO";
                            if (a.idPersona) {
                                for (size_t cIdx = 0; cIdx < ctrl.datos.contratos.tamano(); ++cIdx) {
                                    auto& c = ctrl.datos.contratos.obtener(cIdx);
                                    if (c.idPersona == a.idPersona && c.estado && *c.estado == "ACTIVO") {
                                        c.estado = "INACTIVO";
                                    }
                                }
                            }
                            ctrl.guardarDatos();
                            ctrl.setMensaje("Administrativo y contrato desactivados.");
                        }
                        ImGui::PopStyleColor(2);
                    } else {
                        ImGui::PushStyleColor(ImGuiCol_Button, tema::withAlpha(tema::ACCENT_SUCCESS(), 0.18f));
                        ImGui::PushStyleColor(ImGuiCol_Text, tema::ACCENT_SUCCESS());
                        if (ImGui::SmallButton("Activar")) {
                            a.estado = "ACTIVO";
                            if (a.idPersona) {
                                for (size_t cIdx = 0; cIdx < ctrl.datos.contratos.tamano(); ++cIdx) {
                                    auto& c = ctrl.datos.contratos.obtener(cIdx);
                                    if (c.idPersona == a.idPersona) {
                                        c.estado = "ACTIVO";
                                    }
                                }
                            }
                            ctrl.guardarDatos();
                            ctrl.setMensaje("Administrativo y contrato activados.");
                        }
                        ImGui::PopStyleColor(2);
                    }

                    ImGui::PopID();
                }
                ImGui::EndTable();
            }
            ImGui::EndTabItem();
        }

        ImGui::EndTabBar();
    }
}

// ======================================================================
// MODAL: FICHA DETALLADA INTEGRAL DE PERSONA (DialogDetallePersona)
// ======================================================================

void PITAApp::renderModalDetallePersona() {
    if (modalDetallePersonaAbierto) {
        ImGui::OpenPopup("Ficha Detallada de Persona");
    }

    ImVec2 center = ImGui::GetMainViewport()->GetCenter();
    ImGui::SetNextWindowPos(center, ImGuiCond_Appearing, ImVec2(0.5f, 0.5f));
    ImGui::SetNextWindowSize(ImVec2(650, 680), ImGuiCond_Always);

    if (ImGui::BeginPopupModal("Ficha Detallada de Persona", &modalDetallePersonaAbierto, ImGuiWindowFlags_None)) {
        // Buscar persona
        Persona* pPers = nullptr;
        for (size_t i = 0; i < ctrl.datos.personas.tamano(); ++i) {
            auto& p = ctrl.datos.personas.obtener(i);
            if (p.idPersona && *p.idPersona == idPersonaDetalle) {
                pPers = &p;
                break;
            }
        }

        if (!pPers) {
            ImGui::TextColored(tema::ACCENT_DANGER(), "Persona no encontrada en el sistema.");
            if (ImGui::Button("Cerrar", ImVec2(100, 30))) {
                modalDetallePersonaAbierto = false;
                ImGui::CloseCurrentPopup();
            }
            ImGui::EndPopup();
            return;
        }

        std::string nomCompleto = (pPers->primerNombre ? *pPers->primerNombre : "") + " " +
                                  (pPers->segundoNombre ? *pPers->segundoNombre + " " : "") +
                                  (pPers->primerApellido ? *pPers->primerApellido : "") + " " +
                                  (pPers->segundoApellido ? *pPers->segundoApellido : "");

        ImGui::TextColored(tema::WIN_BLUE(), "FICHA INTEGRAL DE PERSONA Y ROLES INSTITUCIONALES");
        if (fuenteTitulo) ImGui::PushFont(fuenteTitulo);
        ImGui::TextColored(tema::TEXT_MAIN(), "%s", nomCompleto.c_str());
        if (fuenteTitulo) ImGui::PopFont();
        ImGui::Separator();
        ImGui::Spacing();

        ImGui::BeginChild("##ScrollDetallePersona", ImVec2(0, -45), ImGuiChildFlags_None);

        // 1. Datos Personales
        ImGui::PushStyleColor(ImGuiCol_ChildBg, tema::BG_CARD());
        ImGui::BeginChild("##CardDatosPersonales", ImVec2(0, 160), ImGuiChildFlags_Borders);
        ImGui::SetCursorPos(ImVec2(12, 8));
        ImGui::TextColored(tema::WIN_BLUE(), "Datos Personales y de Contacto");
        ImGui::Separator();
        ImGui::SetCursorPos(ImVec2(14, 34));
        ImGui::Text("Documento Identidad: %s %s", pPers->tipoDocumento ? pPers->tipoDocumento->c_str() : "CC",
                    pPers->numeroDocumento ? pPers->numeroDocumento->c_str() : "---");
        ImGui::SetCursorPos(ImVec2(14, 56));
        ImGui::Text("Correo Personal:     %s", pPers->correoPersonal ? pPers->correoPersonal->c_str() : "No registrado");
        ImGui::SetCursorPos(ImVec2(14, 78));
        ImGui::Text("Telefono Contacto:   %s", pPers->telefono ? pPers->telefono->c_str() : "No registrado");
        ImGui::SetCursorPos(ImVec2(14, 100));
        ImGui::Text("Direccion:           %s (%s)", pPers->direccion ? pPers->direccion->c_str() : "---",
                    pPers->ciudadResidencia ? pPers->ciudadResidencia->c_str() : "Valledupar");
        ImGui::SetCursorPos(ImVec2(14, 122));
        ImGui::Text("Estado en Sistema:   %s", pPers->estado ? pPers->estado->c_str() : "ACTIVO");
        ImGui::EndChild();
        ImGui::PopStyleColor();

        ImGui::Spacing();

        // 2. Roles Institucionales
        // Buscar si es Estudiante
        Estudiante* pEst = nullptr;
        for (size_t i = 0; i < ctrl.datos.estudiantes.tamano(); ++i) {
            auto& e = ctrl.datos.estudiantes.obtener(i);
            if (e.idPersona && *e.idPersona == idPersonaDetalle) {
                pEst = &e;
                break;
            }
        }

        if (pEst) {
            std::string nomProg = "---";
            if (pEst->idPrograma) {
                for (size_t k = 0; k < ctrl.datos.programas.tamano(); ++k) {
                    auto& pr = ctrl.datos.programas.obtener(k);
                    if (pr.idPrograma && *pr.idPrograma == *pEst->idPrograma) {
                        nomProg = pr.nombre ? *pr.nombre : "---";
                        break;
                    }
                }
            }

            ImGui::PushStyleColor(ImGuiCol_ChildBg, tema::BG_CARD());
            ImGui::BeginChild("##CardRolEstudiante", ImVec2(0, 130), ImGuiChildFlags_Borders);
            ImGui::SetCursorPos(ImVec2(12, 8));
            ImGui::TextColored(tema::ACCENT_SUCCESS(), "Rol Institucional: Estudiante de Pregrado/Posgrado");
            ImGui::Separator();
            ImGui::SetCursorPos(ImVec2(14, 34));
            ImGui::Text("Codigo Estudiante:   %s", pEst->codigoEstudiante ? pEst->codigoEstudiante->c_str() : "---");
            ImGui::SetCursorPos(ImVec2(14, 56));
            ImGui::Text("Programa Academico:  %s", nomProg.c_str());
            ImGui::SetCursorPos(ImVec2(14, 78));
            ImGui::Text("Semestre Actual:     Semestre %d (%d creditos aprobados)",
                        pEst->semestreActual ? *pEst->semestreActual : 1,
                        pEst->creditosAprobados ? *pEst->creditosAprobados : 0);
            ImGui::SetCursorPos(ImVec2(14, 100));
            double prom = pEst->promedioAcumulado.value_or(0.0);
            ImGui::Text("Promedio Acumulado:  %.2f", prom);
            ImGui::SameLine(250);
            if (prom < 3.0 || (pEst->estadoAcademico && *pEst->estadoAcademico == EstadoAcademico::EBRA)) {
                ImGui::TextColored(tema::ACCENT_DANGER(), "[ALERTA TEMPRANA EBRA]");
            } else {
                ImGui::TextColored(tema::ACCENT_SUCCESS(), "[ESTADO REGULAR]");
            }
            ImGui::EndChild();
            ImGui::PopStyleColor();
            ImGui::Spacing();
        }

        // Buscar si es Profesor
        Profesor* pProf = nullptr;
        for (size_t i = 0; i < ctrl.datos.profesores.tamano(); ++i) {
            auto& prof = ctrl.datos.profesores.obtener(i);
            if (prof.idPersona && *prof.idPersona == idPersonaDetalle) {
                pProf = &prof;
                break;
            }
        }

        if (pProf) {
            ImGui::PushStyleColor(ImGuiCol_ChildBg, tema::BG_CARD());
            ImGui::BeginChild("##CardRolProfesor", ImVec2(0, 130), ImGuiChildFlags_Borders);
            ImGui::SetCursorPos(ImVec2(12, 8));
            ImGui::TextColored(tema::ACCENT_INDIGO(), "Rol Institucional: Docente Universitario");
            ImGui::Separator();
            ImGui::SetCursorPos(ImVec2(14, 34));
            ImGui::Text("Codigo Profesor:     %s", pProf->codigoProfesor ? pProf->codigoProfesor->c_str() : "---");
            ImGui::SetCursorPos(ImVec2(14, 56));
            ImGui::Text("Tipo / Regimen:      %s", pProf->tipoProfesor ? to_string(*pProf->tipoProfesor).c_str() : "---");
            ImGui::SetCursorPos(ImVec2(14, 78));
            ImGui::Text("Dedicacion:          %s (%.1f h/semana)",
                        pProf->dedicacion ? to_string(*pProf->dedicacion).c_str() : "---",
                        pProf->numeroHorasSemanales ? *pProf->numeroHorasSemanales : 40.0);
            ImGui::SetCursorPos(ImVec2(14, 100));
            ImGui::Text("Puntos Dec. 1279:    %.0f pts (Remuneracion Estatutaria)",
                        pProf->puntosSalariales ? *pProf->puntosSalariales : 0.0);
            ImGui::EndChild();
            ImGui::PopStyleColor();
            ImGui::Spacing();
        }

        // Buscar si es Administrativo
        Administrativo* pAdm = nullptr;
        for (size_t i = 0; i < ctrl.datos.administrativos.tamano(); ++i) {
            auto& a = ctrl.datos.administrativos.obtener(i);
            if (a.idPersona && *a.idPersona == idPersonaDetalle) {
                pAdm = &a;
                break;
            }
        }

        if (pAdm) {
            ImGui::PushStyleColor(ImGuiCol_ChildBg, tema::BG_CARD());
            ImGui::BeginChild("##CardRolAdmin", ImVec2(0, 130), ImGuiChildFlags_Borders);
            ImGui::SetCursorPos(ImVec2(12, 8));
            ImGui::TextColored(tema::ACCENT_WARNING(), "Rol Institucional: Funcionario Administrativo");
            ImGui::Separator();
            ImGui::SetCursorPos(ImVec2(14, 34));
            ImGui::Text("Codigo Empleado:     %s", pAdm->codigoEmpleado ? pAdm->codigoEmpleado->c_str() : "---");
            ImGui::SetCursorPos(ImVec2(14, 56));
            ImGui::Text("Cargo:               %s (%s)", pAdm->cargo ? pAdm->cargo->c_str() : "---",
                        pAdm->categoria ? pAdm->categoria->c_str() : "PROFESIONAL");
            ImGui::SetCursorPos(ImVec2(14, 78));
            ImGui::Text("Dependencia:         %s", pAdm->dependencia ? pAdm->dependencia->c_str() : "---");
            ImGui::SetCursorPos(ImVec2(14, 100));
            ImGui::Text("Salario Base:        %s", formatearMoneda(pAdm->salarioBase.value_or(0.0)).c_str());
            ImGui::EndChild();
            ImGui::PopStyleColor();
            ImGui::Spacing();
        }

        // 3. Contratos Laborales Asociados
        bool tieneContratos = false;
        for (size_t i = 0; i < ctrl.datos.contratos.tamano(); ++i) {
            auto& c = ctrl.datos.contratos.obtener(i);
            if (c.idPersona && *c.idPersona == idPersonaDetalle) {
                if (!tieneContratos) {
                    ImGui::TextColored(tema::TEXT_MUTED(), "Contratos Laborales Asociados:");
                    tieneContratos = true;
                }
                ImGui::BulletText("Contrato #%d (%s): Salario Base %s - Estado: %s",
                                  c.idContrato ? *c.idContrato : 0,
                                  c.tipoContrato ? c.tipoContrato->c_str() : "LABORAL",
                                  formatearMoneda(c.salarioBase.value_or(0.0)).c_str(),
                                  c.estado ? c.estado->c_str() : "ACTIVO");
            }
        }

        ImGui::EndChild();

        ImGui::Separator();
        ImGui::Spacing();
        ImGui::SetCursorPosX((ImGui::GetWindowWidth() - 120) / 2.0f);
        if (ImGui::Button("Cerrar Ficha", ImVec2(120, 32))) {
            modalDetallePersonaAbierto = false;
            ImGui::CloseCurrentPopup();
        }

        ImGui::EndPopup();
    }
}

// ======================================================================
// MODAL: EDITAR ESTUDIANTE (DialogEditarEstudiante)
// ======================================================================

void PITAApp::renderModalEditarEstudiante() {
    if (modalEditarEstudianteAbierto) {
        ImGui::OpenPopup("Modificar Datos Estudiante");
    }

    ImVec2 center = ImGui::GetMainViewport()->GetCenter();
    ImGui::SetNextWindowPos(center, ImGuiCond_Appearing, ImVec2(0.5f, 0.5f));
    ImGui::SetNextWindowSize(ImVec2(520, 0), ImGuiCond_Always);

    if (ImGui::BeginPopupModal("Modificar Datos Estudiante", &modalEditarEstudianteAbierto, ImGuiWindowFlags_AlwaysAutoResize)) {
        if (strlen(mensajeModal) > 0) {
            ImGui::TextColored(errorModal ? tema::ACCENT_DANGER() : tema::ACCENT_SUCCESS(), "%s", mensajeModal);
            ImGui::Separator();
        }

        ImGui::TextColored(tema::WIN_BLUE(), "Actualizar Ficha Academica: %s", editEstCodigo);
        ImGui::Spacing();

        ImGui::InputInt("Semestre Actual *", &editEstSemestre);
        if (editEstSemestre < 1) editEstSemestre = 1;
        if (editEstSemestre > 14) editEstSemestre = 14;

        ImGui::InputInt("Creditos Aprobados *", &editEstCreditos);
        if (editEstCreditos < 0) editEstCreditos = 0;

        ImGui::InputFloat("Promedio Acumulado *", &editEstPromedio, 0.1f, 0.5f, "%.2f");
        if (editEstPromedio < 0.0f) editEstPromedio = 0.0f;
        if (editEstPromedio > 5.0f) editEstPromedio = 5.0f;

        // Selector de Programa Académico
        if (ctrl.datos.programas.tamano() > 0) {
            std::string previewProg = "Seleccione Programa";
            for (size_t i = 0; i < ctrl.datos.programas.tamano(); i++) {
                auto& pr = ctrl.datos.programas.obtener(i);
                if (pr.idPrograma && *pr.idPrograma == editEstProgramaId) {
                    previewProg = pr.nombre ? *pr.nombre : "---";
                    break;
                }
            }
            if (ImGui::BeginCombo("Programa Academico *", previewProg.c_str())) {
                for (size_t i = 0; i < ctrl.datos.programas.tamano(); i++) {
                    auto& pr = ctrl.datos.programas.obtener(i);
                    bool isSelected = (pr.idPrograma && *pr.idPrograma == editEstProgramaId);
                    std::string label = pr.nombre ? *pr.nombre : "Programa";
                    if (ImGui::Selectable(label.c_str(), isSelected)) {
                        editEstProgramaId = pr.idPrograma.value_or(1);
                    }
                    if (isSelected) ImGui::SetItemDefaultFocus();
                }
                ImGui::EndCombo();
            }
        }

        const char* estadosAcad[] = { "MATRICULADO", "EBRA", "ACTIVO", "GRADUADO", "RETIRADO", "SUSPENDIDO" };
        ImGui::Combo("Estado Academico", &editEstEstadoAcadIdx, estadosAcad, IM_ARRAYSIZE(estadosAcad));

        const char* estadosGen[] = { "ACTIVO", "INACTIVO" };
        ImGui::Combo("Estado Operativo", &editEstEstadoIdx, estadosGen, IM_ARRAYSIZE(estadosGen));

        if (editEstPromedio < 3.0f) {
            ImGui::TextColored(tema::ACCENT_DANGER(), "Nota: Promedio inferior a 3.0 situara al estudiante en condicion EBRA.");
        }

        ImGui::Spacing();
        ImGui::Separator();
        ImGui::Spacing();

        if (ImGui::Button("Guardar Cambios", ImVec2(150, 32))) {
            for (size_t i = 0; i < ctrl.datos.estudiantes.tamano(); ++i) {
                auto& e = ctrl.datos.estudiantes.obtener(i);
                if (e.idEstudiante && *e.idEstudiante == idEstudianteEditando) {
                    e.semestreActual = editEstSemestre;
                    e.creditosAprobados = editEstCreditos;
                    e.promedioAcumulado = editEstPromedio;
                    e.idPrograma = editEstProgramaId;

                    if (editEstPromedio < 3.0f) {
                        e.estadoAcademico = EstadoAcademico::EBRA;
                    } else {
                        switch (editEstEstadoAcadIdx) {
                            case 0: e.estadoAcademico = EstadoAcademico::MATRICULADO; break;
                            case 1: e.estadoAcademico = EstadoAcademico::EBRA; break;
                            case 2: e.estadoAcademico = EstadoAcademico::ACTIVO; break;
                            case 3: e.estadoAcademico = EstadoAcademico::GRADUADO; break;
                            case 4: e.estadoAcademico = EstadoAcademico::RETIRADO; break;
                            default: e.estadoAcademico = EstadoAcademico::SUSPENDIDO; break;
                        }
                    }

                    e.estado = (editEstEstadoIdx == 0 ? "ACTIVO" : "INACTIVO");
                    break;
                }
            }

            ctrl.guardarDatos();
            ctrl.setMensaje("Estudiante actualizado exitosamente.");
            modalEditarEstudianteAbierto = false;
            ImGui::CloseCurrentPopup();
        }

        ImGui::SameLine();
        if (ImGui::Button("Cancelar", ImVec2(120, 32))) {
            modalEditarEstudianteAbierto = false;
            ImGui::CloseCurrentPopup();
        }

        ImGui::EndPopup();
    }
}

// ======================================================================
// MODAL: EDITAR PROFESOR (DialogEditarProfesor)
// ======================================================================

void PITAApp::renderModalEditarProfesor() {
    if (modalEditarProfesorAbierto) {
        ImGui::OpenPopup("Modificar Datos Docente");
    }

    ImVec2 center = ImGui::GetMainViewport()->GetCenter();
    ImGui::SetNextWindowPos(center, ImGuiCond_Appearing, ImVec2(0.5f, 0.5f));
    ImGui::SetNextWindowSize(ImVec2(540, 0), ImGuiCond_Always);

    if (ImGui::BeginPopupModal("Modificar Datos Docente", &modalEditarProfesorAbierto, ImGuiWindowFlags_AlwaysAutoResize)) {
        if (strlen(mensajeModal) > 0) {
            ImGui::TextColored(errorModal ? tema::ACCENT_DANGER() : tema::ACCENT_SUCCESS(), "%s", mensajeModal);
            ImGui::Separator();
        }

        ImGui::TextColored(tema::WIN_BLUE(), "Actualizar Ficha Docente: %s", editProfCodigo);
        ImGui::Spacing();

        const char* tiposProf[] = { "PLANTA", "OCASIONAL", "CATEDRATICO" };
        ImGui::Combo("Tipo / Regimen Salarial *", &editProfTipoIdx, tiposProf, IM_ARRAYSIZE(tiposProf));

        const char* catsDoc[] = { "TITULAR", "ASOCIADO", "ASISTENTE", "AUXILIAR" };
        ImGui::Combo("Categoria en Escalafon *", &editProfCategoriaIdx, catsDoc, IM_ARRAYSIZE(catsDoc));

        const char* dedics[] = { "TIEMPO_COMPLETO", "MEDIO_TIEMPO", "HORA_CATEDRA" };
        ImGui::Combo("Dedicacion *", &editProfDedicacionIdx, dedics, IM_ARRAYSIZE(dedics));

        ImGui::InputDouble("Horas Semanales *", &editProfHoras, 1.0, 5.0, "%.1f h");
        if (editProfHoras < 1.0) editProfHoras = 1.0;

        ImGui::InputDouble("Puntos Salariales Dec. 1279", &editProfPuntos, 10.0, 50.0, "%.1f pts");
        if (editProfPuntos < 0.0) editProfPuntos = 0.0;

        const char* estadosGen[] = { "ACTIVO", "INACTIVO" };
        ImGui::Combo("Estado General", &editProfEstadoIdx, estadosGen, IM_ARRAYSIZE(estadosGen));

        ImGui::Spacing();
        ImGui::Separator();
        ImGui::Spacing();

        if (ImGui::Button("Guardar Cambios", ImVec2(150, 32))) {
            for (size_t i = 0; i < ctrl.datos.profesores.tamano(); ++i) {
                auto& prof = ctrl.datos.profesores.obtener(i);
                if (prof.idProfesor && *prof.idProfesor == idProfesorEditando) {
                    prof.tipoProfesor = (editProfTipoIdx == 0 ? TipoProfesor::PLANTA : (editProfTipoIdx == 1 ? TipoProfesor::OCASIONAL : TipoProfesor::CATEDRATICO));
                    prof.categoriaDocente = catsDoc[editProfCategoriaIdx];
                    prof.dedicacion = (editProfDedicacionIdx == 0 ? Dedicacion::TIEMPO_COMPLETO : (editProfDedicacionIdx == 1 ? Dedicacion::MEDIO_TIEMPO : Dedicacion::HORA_CATEDRA));
                    prof.numeroHorasSemanales = editProfHoras;
                    prof.puntosSalariales = editProfPuntos;
                    prof.estado = (editProfEstadoIdx == 0 ? "ACTIVO" : "INACTIVO");
                    break;
                }
            }

            ctrl.inicializarGestores();
            ctrl.guardarDatos();
            ctrl.setMensaje("Docente actualizado exitosamente.");
            modalEditarProfesorAbierto = false;
            ImGui::CloseCurrentPopup();
        }

        ImGui::SameLine();
        if (ImGui::Button("Cancelar", ImVec2(120, 32))) {
            modalEditarProfesorAbierto = false;
            ImGui::CloseCurrentPopup();
        }

        ImGui::EndPopup();
    }
}

// ======================================================================
// HELPER APERTURA MODAL PERSONA (CREAR / EDITAR)
// ======================================================================

void PITAApp::abrirModalPersona(bool editar, int idPersona) {
    modoEditarPersona = editar;
    idPersonaEditando = idPersona;
    mensajeModal[0] = '\0';
    errorModal = false;

    if (editar && idPersona > 0) {
        for (size_t i = 0; i < ctrl.datos.personas.tamano(); i++) {
            auto& p = ctrl.datos.personas.obtener(i);
            if (p.idPersona && *p.idPersona == idPersona) {
                strncpy(pTipoDoc, p.tipoDocumento ? p.tipoDocumento->c_str() : "CC", sizeof(pTipoDoc) - 1);
                strncpy(pNumDoc, p.numeroDocumento ? p.numeroDocumento->c_str() : "", sizeof(pNumDoc) - 1);
                strncpy(pPrimerNombre, p.primerNombre ? p.primerNombre->c_str() : "", sizeof(pPrimerNombre) - 1);
                strncpy(pSegundoNombre, p.segundoNombre ? p.segundoNombre->c_str() : "", sizeof(pSegundoNombre) - 1);
                strncpy(pPrimerApellido, p.primerApellido ? p.primerApellido->c_str() : "", sizeof(pPrimerApellido) - 1);
                strncpy(pSegundoApellido, p.segundoApellido ? p.segundoApellido->c_str() : "", sizeof(pSegundoApellido) - 1);
                strncpy(pEmail, p.correoPersonal ? p.correoPersonal->c_str() : "", sizeof(pEmail) - 1);
                strncpy(pTelefono, p.telefono ? p.telefono->c_str() : "", sizeof(pTelefono) - 1);
                strncpy(pDireccion, p.direccion ? p.direccion->c_str() : "", sizeof(pDireccion) - 1);
                pRolSeleccionado = 0;
                break;
            }
        }
    } else {
        pNumDoc[0] = '\0';
        pPrimerNombre[0] = '\0';
        pSegundoNombre[0] = '\0';
        pPrimerApellido[0] = '\0';
        pSegundoApellido[0] = '\0';
        pEmail[0] = '\0';
        pTelefono[0] = '\0';
        pDireccion[0] = '\0';
        estCodigo[0] = '\0';
        profCodigo[0] = '\0';
        profDedicacionIdx = 0;
        profHoras = 40.0;
        admCodigo[0] = '\0';
        pRolSeleccionado = 1; // Default Estudiante
        if (ctrl.datos.programas.tamano() > 0) {
            estProgramaId = ctrl.datos.programas.obtener(0).idPrograma.value_or(1);
        }
    }
    modalPersonaAbierto = true;
}

// ======================================================================
// MODAL PERSONA (Crear / Editar)
// ======================================================================

void PITAApp::renderModalPersona() {
    if (modalPersonaAbierto) {
        ImGui::OpenPopup(modoEditarPersona ? "Editar Persona" : "Registrar Persona");
    }

    ImVec2 center = ImGui::GetMainViewport()->GetCenter();
    ImGui::SetNextWindowPos(center, ImGuiCond_Appearing, ImVec2(0.5f, 0.5f));
    ImGui::SetNextWindowSize(ImVec2(550, 0), ImGuiCond_Always);

    if (ImGui::BeginPopupModal(modoEditarPersona ? "Editar Persona" : "Registrar Persona", &modalPersonaAbierto, ImGuiWindowFlags_AlwaysAutoResize)) {
        if (strlen(mensajeModal) > 0) {
            ImGui::TextColored(errorModal ? tema::ACCENT_DANGER() : tema::ACCENT_SUCCESS(), "%s", mensajeModal);
            ImGui::Separator();
        }

        ImGui::TextColored(tema::WIN_BLUE(), "Datos Basicos de Identificacion");
        ImGui::Spacing();

        const char* tiposDoc[] = { "CC", "TI", "CE", "PASAPORTE" };
        static int tipoDocIdx = 0;
        if (ImGui::Combo("Tipo Documento", &tipoDocIdx, tiposDoc, IM_ARRAYSIZE(tiposDoc))) {
            strncpy(pTipoDoc, tiposDoc[tipoDocIdx], sizeof(pTipoDoc) - 1);
        }

        ImGui::InputText("No. Documento *", pNumDoc, sizeof(pNumDoc));
        ImGui::InputText("Primer Nombre *", pPrimerNombre, sizeof(pPrimerNombre));
        ImGui::InputText("Segundo Nombre", pSegundoNombre, sizeof(pSegundoNombre));
        ImGui::InputText("Primer Apellido *", pPrimerApellido, sizeof(pPrimerApellido));
        ImGui::InputText("Segundo Apellido", pSegundoApellido, sizeof(pSegundoApellido));
        ImGui::InputText("Correo Electronico", pEmail, sizeof(pEmail));
        ImGui::InputText("Telefono", pTelefono, sizeof(pTelefono));
        ImGui::InputText("Direccion", pDireccion, sizeof(pDireccion));

        if (!modoEditarPersona) {
            ImGui::Spacing();
            ImGui::Separator();
            ImGui::TextColored(tema::ACCENT_INDIGO(), "Asignacion de Rol Institucional");
            ImGui::Spacing();

            const char* roles[] = { "Sin Rol Adicional", "Estudiante", "Profesor", "Administrativo" };
            ImGui::Combo("Rol Principal", &pRolSeleccionado, roles, IM_ARRAYSIZE(roles));

            if (pRolSeleccionado == 1) {
                // Estudiante
                ImGui::InputText("Codigo Estudiantil *", estCodigo, sizeof(estCodigo));

                if (ctrl.datos.programas.tamano() > 0) {
                    std::string previewProg = "Seleccione Programa";
                    for (size_t i = 0; i < ctrl.datos.programas.tamano(); i++) {
                        auto& pr = ctrl.datos.programas.obtener(i);
                        if (pr.idPrograma && *pr.idPrograma == estProgramaId) {
                            previewProg = pr.nombre ? *pr.nombre : "---";
                            break;
                        }
                    }
                    if (ImGui::BeginCombo("Programa *", previewProg.c_str())) {
                        for (size_t i = 0; i < ctrl.datos.programas.tamano(); i++) {
                            auto& pr = ctrl.datos.programas.obtener(i);
                            bool isSelected = (pr.idPrograma && *pr.idPrograma == estProgramaId);
                            std::string label = pr.nombre ? *pr.nombre : "Programa";
                            if (ImGui::Selectable(label.c_str(), isSelected)) {
                                estProgramaId = pr.idPrograma.value_or(1);
                            }
                            if (isSelected) ImGui::SetItemDefaultFocus();
                        }
                        ImGui::EndCombo();
                    }
                }
            } else if (pRolSeleccionado == 2) {
                // Profesor
                ImGui::InputText("Codigo Profesor *", profCodigo, sizeof(profCodigo));
                const char* tiposProf[] = { "PLANTA", "OCASIONAL", "CATEDRATICO" };
                ImGui::Combo("Tipo Profesor", &profTipoIdx, tiposProf, IM_ARRAYSIZE(tiposProf));

                const char* dedics[] = { "TIEMPO_COMPLETO", "MEDIO_TIEMPO", "HORA_CATEDRA" };
                ImGui::Combo("Dedicacion", &profDedicacionIdx, dedics, IM_ARRAYSIZE(dedics));

                ImGui::InputDouble("Horas Semanales", &profHoras, 1.0, 5.0, "%.1f");
                ImGui::InputDouble("Puntos Salariales", &profPuntos, 10.0, 50.0, "%.1f");
            } else if (pRolSeleccionado == 3) {
                // Administrativo
                ImGui::InputText("Codigo Empleado *", admCodigo, sizeof(admCodigo));
                ImGui::InputText("Cargo Institucional *", admCargo, sizeof(admCargo));
                ImGui::InputText("Dependencia *", admDependencia, sizeof(admDependencia));

                const char* catsAdm[] = { "PROFESIONAL", "DIRECTIVO", "ASESOR", "TECNICO", "ASISTENCIAL" };
                ImGui::Combo("Nivel / Categoria *", &admCategoriaIdx, catsAdm, IM_ARRAYSIZE(catsAdm));

                const char* tiposContAdm[] = { "PLANTA", "CARRERA_ADMINISTRATIVA", "LIBRE_NOMBRAMIENTO", "PROVISIONALIDAD", "PRESTACION_SERVICIOS" };
                ImGui::Combo("Tipo Contratacion *", &admTipoContratacionIdx, tiposContAdm, IM_ARRAYSIZE(tiposContAdm));

                ImGui::InputDouble("Salario Base Mensual ($) *", &admSalarioBase, 100000.0, 500000.0, "$ %.0f");
                ImGui::InputText("Fecha Vinculacion (AAAA-MM-DD)", admFechaVinculacion, sizeof(admFechaVinculacion));
            }
        }

        ImGui::Spacing();
        ImGui::Separator();
        ImGui::Spacing();

        if (ImGui::Button("Guardar", ImVec2(120, 32))) {
            if (strlen(pNumDoc) == 0 || strlen(pPrimerNombre) == 0 || strlen(pPrimerApellido) == 0) {
                strncpy(mensajeModal, "Documento, Primer Nombre y Primer Apellido son obligatorios.", sizeof(mensajeModal) - 1);
                errorModal = true;
            } else {
                try {
                    int idPersFinal = idPersonaEditando;

                    if (modoEditarPersona) {
                        for (size_t i = 0; i < ctrl.datos.personas.tamano(); i++) {
                            auto& p = ctrl.datos.personas.obtener(i);
                            if (p.idPersona && *p.idPersona == idPersonaEditando) {
                                p.tipoDocumento = pTipoDoc;
                                p.numeroDocumento = pNumDoc;
                                p.primerNombre = pPrimerNombre;
                                p.segundoNombre = strlen(pSegundoNombre) > 0 ? std::make_optional(std::string(pSegundoNombre)) : std::nullopt;
                                p.primerApellido = pPrimerApellido;
                                p.segundoApellido = strlen(pSegundoApellido) > 0 ? std::make_optional(std::string(pSegundoApellido)) : std::nullopt;
                                p.correoPersonal = strlen(pEmail) > 0 ? std::make_optional(std::string(pEmail)) : std::nullopt;
                                p.telefono = strlen(pTelefono) > 0 ? std::make_optional(std::string(pTelefono)) : std::nullopt;
                                p.direccion = strlen(pDireccion) > 0 ? std::make_optional(std::string(pDireccion)) : std::nullopt;
                                break;
                            }
                        }
                    } else {
                        Persona p;
                        int maxId = 0;
                        for (size_t i = 0; i < ctrl.datos.personas.tamano(); i++) {
                            auto& per = ctrl.datos.personas.obtener(i);
                            if (per.idPersona && *per.idPersona > maxId) maxId = *per.idPersona;
                        }
                        idPersFinal = maxId + 1;
                        p.idPersona = idPersFinal;
                        p.tipoDocumento = pTipoDoc;
                        p.numeroDocumento = pNumDoc;
                        p.primerNombre = pPrimerNombre;
                        if (strlen(pSegundoNombre) > 0) p.segundoNombre = pSegundoNombre;
                        p.primerApellido = pPrimerApellido;
                        if (strlen(pSegundoApellido) > 0) p.segundoApellido = pSegundoApellido;
                        if (strlen(pEmail) > 0) p.correoPersonal = pEmail;
                        if (strlen(pTelefono) > 0) p.telefono = pTelefono;
                        if (strlen(pDireccion) > 0) p.direccion = pDireccion;
                        p.estado = "ACTIVO";

                        ctrl.datos.personas.push_back(p);

                        // Crear Rol si corresponde
                        if (pRolSeleccionado == 1 && strlen(estCodigo) > 0) {
                            Estudiante est;
                            int maxEstId = 0;
                            for (size_t i = 0; i < ctrl.datos.estudiantes.tamano(); i++) {
                                auto& e = ctrl.datos.estudiantes.obtener(i);
                                if (e.idEstudiante && *e.idEstudiante > maxEstId) maxEstId = *e.idEstudiante;
                            }
                            est.idEstudiante = maxEstId + 1;
                            est.idPersona = idPersFinal;
                            est.codigoEstudiante = estCodigo;
                            est.idPrograma = estProgramaId;
                            est.semestreActual = 1;
                            est.creditosAprobados = 0;
                            est.promedioAcumulado = 4.0;
                            est.estadoAcademico = EstadoAcademico::MATRICULADO;
                            est.estado = "ACTIVO";
                            ctrl.datos.estudiantes.push_back(est);
                        } else if (pRolSeleccionado == 2 && strlen(profCodigo) > 0) {
                            Profesor prof;
                            int maxProfId = 0;
                            for (size_t i = 0; i < ctrl.datos.profesores.tamano(); i++) {
                                auto& pr = ctrl.datos.profesores.obtener(i);
                                if (pr.idProfesor && *pr.idProfesor > maxProfId) maxProfId = *pr.idProfesor;
                            }
                            prof.idProfesor = maxProfId + 1;
                            prof.idPersona = idPersFinal;
                            prof.codigoProfesor = profCodigo;
                            prof.tipoProfesor = (profTipoIdx == 0 ? TipoProfesor::PLANTA : (profTipoIdx == 1 ? TipoProfesor::OCASIONAL : TipoProfesor::CATEDRATICO));
                            prof.dedicacion = (profDedicacionIdx == 0 ? Dedicacion::TIEMPO_COMPLETO : (profDedicacionIdx == 1 ? Dedicacion::MEDIO_TIEMPO : Dedicacion::HORA_CATEDRA));
                            prof.numeroHorasSemanales = profHoras;
                            prof.puntosSalariales = profPuntos;
                            prof.estado = "ACTIVO";
                            ctrl.datos.profesores.push_back(prof);
                        } else if (pRolSeleccionado == 3 && strlen(admCodigo) > 0) {
                            Administrativo adm;
                            int maxAdmId = 0;
                            for (size_t i = 0; i < ctrl.datos.administrativos.tamano(); i++) {
                                auto& a = ctrl.datos.administrativos.obtener(i);
                                if (a.idAdministrativo && *a.idAdministrativo > maxAdmId) maxAdmId = *a.idAdministrativo;
                            }
                            adm.idAdministrativo = maxAdmId + 1;
                            adm.idPersona = idPersFinal;
                            adm.codigoEmpleado = admCodigo;
                            adm.cargo = admCargo;
                            adm.dependencia = admDependencia;
                            const char* catsAdm[] = { "PROFESIONAL", "DIRECTIVO", "ASESOR", "TECNICO", "ASISTENCIAL" };
                            adm.categoria = catsAdm[admCategoriaIdx];
                            const char* tiposContAdm[] = { "PLANTA", "CARRERA_ADMINISTRATIVA", "LIBRE_NOMBRAMIENTO", "PROVISIONALIDAD", "PRESTACION_SERVICIOS" };
                            adm.tipoContratacion = tiposContAdm[admTipoContratacionIdx];
                            adm.fechaVinculacion = strlen(admFechaVinculacion) > 0 ? std::string(admFechaVinculacion) : "2026-03-01";
                            adm.salarioBase = admSalarioBase;
                            adm.estado = "ACTIVO";
                            ctrl.datos.administrativos.push_back(adm);

                            // Generar inmediatamente su contrato laboral activo enlazado a la persona
                            int maxConId = 0;
                            for (size_t i = 0; i < ctrl.datos.contratos.tamano(); ++i) {
                                auto& c = ctrl.datos.contratos.obtener(i);
                                if (c.idContrato && *c.idContrato > maxConId) maxConId = *c.idContrato;
                            }
                            Contrato con;
                            con.idContrato = maxConId + 1;
                            con.idPersona = idPersFinal;
                            con.numeroContrato = "ADM-CONTRATO-" + std::to_string(*con.idContrato);
                            con.tipoContrato = "TERMINO_INDEFINIDO";
                            con.fechaInicio = strlen(admFechaVinculacion) > 0 ? std::string(admFechaVinculacion) : "2026-03-01";
                            con.salarioBase = admSalarioBase;
                            con.aplicaAuxilioTransporte = (admSalarioBase <= 3501810.0);
                            con.estado = "ACTIVO";
                            con.regimenAplicable = "CST_LEY100_ADMINISTRATIVO";
                            con.esRemunerado = true;
                            con.esEmpleadoPublicoDocente = false;
                            con.perteneceCarreraProfesoral = false;
                            con.esTransitorio = false;
                            con.esAdHonorem = false;
                            ctrl.datos.contratos.push_back(con);
                        }
                    }

                    ctrl.guardarDatos();
                    ctrl.setMensaje("Persona y roles guardados con exito.");
                    modalPersonaAbierto = false;
                    ImGui::CloseCurrentPopup();
                } catch (const std::exception& e) {
                    strncpy(mensajeModal, e.what(), sizeof(mensajeModal) - 1);
                    errorModal = true;
                }
            }
        }

        ImGui::SameLine();
        if (ImGui::Button("Cancelar", ImVec2(120, 32))) {
            modalPersonaAbierto = false;
            ImGui::CloseCurrentPopup();
        }

        ImGui::EndPopup();
    }
}

// ======================================================================
// MODAL: EDITAR ADMINISTRATIVO
// ======================================================================

void PITAApp::abrirModalEditarAdministrativo(int idAdministrativo) {
    idAdminEditando = idAdministrativo;
    mensajeModal[0] = '\0';
    errorModal = false;

    for (size_t i = 0; i < ctrl.datos.administrativos.tamano(); ++i) {
        auto& a = ctrl.datos.administrativos.obtener(i);
        if (a.idAdministrativo && *a.idAdministrativo == idAdministrativo) {
            strncpy(editAdmCodigo, a.codigoEmpleado ? a.codigoEmpleado->c_str() : "", sizeof(editAdmCodigo) - 1);
            strncpy(editAdmCargo, a.cargo ? a.cargo->c_str() : "", sizeof(editAdmCargo) - 1);
            strncpy(editAdmDependencia, a.dependencia ? a.dependencia->c_str() : "", sizeof(editAdmDependencia) - 1);
            editAdmSalarioBase = a.salarioBase.value_or(2500000.0);

            std::string cat = a.categoria.value_or("PROFESIONAL");
            if (cat == "DIRECTIVO") editAdmCategoriaIdx = 1;
            else if (cat == "ASESOR") editAdmCategoriaIdx = 2;
            else if (cat == "TECNICO") editAdmCategoriaIdx = 3;
            else if (cat == "ASISTENCIAL") editAdmCategoriaIdx = 4;
            else editAdmCategoriaIdx = 0;

            std::string tc = a.tipoContratacion.value_or("PLANTA");
            if (tc == "CARRERA_ADMINISTRATIVA") editAdmTipoContratacionIdx = 1;
            else if (tc == "LIBRE_NOMBRAMIENTO") editAdmTipoContratacionIdx = 2;
            else if (tc == "PROVISIONALIDAD") editAdmTipoContratacionIdx = 3;
            else if (tc == "PRESTACION_SERVICIOS") editAdmTipoContratacionIdx = 4;
            else editAdmTipoContratacionIdx = 0;

            break;
        }
    }
    modalEditarAdminAbierto = true;
}

void PITAApp::renderModalEditarAdministrativo() {
    if (modalEditarAdminAbierto) {
        ImGui::OpenPopup("Modificar Datos Administrativo");
    }

    ImVec2 center = ImGui::GetMainViewport()->GetCenter();
    ImGui::SetNextWindowPos(center, ImGuiCond_Appearing, ImVec2(0.5f, 0.5f));
    ImGui::SetNextWindowSize(ImVec2(520, 0), ImGuiCond_Always);

    if (ImGui::BeginPopupModal("Modificar Datos Administrativo", &modalEditarAdminAbierto, ImGuiWindowFlags_AlwaysAutoResize)) {
        if (strlen(mensajeModal) > 0) {
            ImGui::TextColored(errorModal ? tema::ACCENT_DANGER() : tema::ACCENT_SUCCESS(), "%s", mensajeModal);
            ImGui::Separator();
        }

        ImGui::TextColored(tema::WIN_BLUE(), "Parametros Laborales del Funcionario");
        ImGui::Spacing();

        ImGui::TextColored(tema::TEXT_MUTED(), "Codigo Empleado: %s", editAdmCodigo);
        ImGui::Spacing();

        ImGui::InputText("Cargo Institucional *", editAdmCargo, sizeof(editAdmCargo));
        ImGui::InputText("Dependencia Adscrita *", editAdmDependencia, sizeof(editAdmDependencia));

        const char* catsAdm[] = { "PROFESIONAL", "DIRECTIVO", "ASESOR", "TECNICO", "ASISTENCIAL" };
        ImGui::Combo("Nivel / Categoria *", &editAdmCategoriaIdx, catsAdm, IM_ARRAYSIZE(catsAdm));

        const char* tiposContAdm[] = { "PLANTA", "CARRERA_ADMINISTRATIVA", "LIBRE_NOMBRAMIENTO", "PROVISIONALIDAD", "PRESTACION_SERVICIOS" };
        ImGui::Combo("Tipo Contratacion *", &editAdmTipoContratacionIdx, tiposContAdm, IM_ARRAYSIZE(tiposContAdm));

        ImGui::InputDouble("Salario Base Mensual ($) *", &editAdmSalarioBase, 100000.0, 500000.0, "$ %.0f");

        ImGui::Spacing();
        ImGui::Separator();
        ImGui::Spacing();

        if (ImGui::Button("Guardar Cambios", ImVec2(140, 32))) {
            if (strlen(editAdmCargo) == 0 || strlen(editAdmDependencia) == 0 || editAdmSalarioBase <= 0) {
                strncpy(mensajeModal, "Cargo, Dependencia y Salario Base positivo son obligatorios.", sizeof(mensajeModal) - 1);
                errorModal = true;
            } else {
                try {
                    int idPers = 0;
                    for (size_t i = 0; i < ctrl.datos.administrativos.tamano(); ++i) {
                        auto& a = ctrl.datos.administrativos.obtener(i);
                        if (a.idAdministrativo && *a.idAdministrativo == idAdminEditando) {
                            a.cargo = editAdmCargo;
                            a.dependencia = editAdmDependencia;
                            const char* catsAdmArr[] = { "PROFESIONAL", "DIRECTIVO", "ASESOR", "TECNICO", "ASISTENCIAL" };
                            a.categoria = catsAdmArr[editAdmCategoriaIdx];
                            const char* tiposContAdmArr[] = { "PLANTA", "CARRERA_ADMINISTRATIVA", "LIBRE_NOMBRAMIENTO", "PROVISIONALIDAD", "PRESTACION_SERVICIOS" };
                            a.tipoContratacion = tiposContAdmArr[editAdmTipoContratacionIdx];
                            a.salarioBase = editAdmSalarioBase;
                            idPers = a.idPersona.value_or(0);
                            break;
                        }
                    }

                    // Sincronizar contrato laboral activo
                    if (idPers > 0) {
                        for (size_t i = 0; i < ctrl.datos.contratos.tamano(); ++i) {
                            auto& c = ctrl.datos.contratos.obtener(i);
                            if (c.idPersona && *c.idPersona == idPers && c.estado && *c.estado == "ACTIVO") {
                                c.salarioBase = editAdmSalarioBase;
                                c.aplicaAuxilioTransporte = (editAdmSalarioBase <= 3501810.0);
                                break;
                            }
                        }
                    }

                    ctrl.inicializarGestores();
                    ctrl.guardarDatos();
                    ctrl.setMensaje("Administrativo y contrato laboral actualizados exitosamente.");
                    modalEditarAdminAbierto = false;
                    ImGui::CloseCurrentPopup();
                } catch (const std::exception& e) {
                    strncpy(mensajeModal, e.what(), sizeof(mensajeModal) - 1);
                    errorModal = true;
                }
            }
        }

        ImGui::SameLine();
        if (ImGui::Button("Cancelar", ImVec2(120, 32))) {
            modalEditarAdminAbierto = false;
            ImGui::CloseCurrentPopup();
        }

        ImGui::EndPopup();
    }
}

} // namespace pita
