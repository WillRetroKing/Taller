#define _CRT_SECURE_NO_WARNINGS
#include "gui_app.h"
#include "tema.h"
#include "imgui.h"

#include <cstring>
#include <string>

namespace pita {

// ======================================================================
// VISTA: PERSONAS
// ======================================================================

void PITAApp::renderPersonas() {
    if (fuenteTitulo) ImGui::PushFont(fuenteTitulo);
    ImGui::TextColored(tema::TEXT_MAIN(), "Gestion de Personas");
    if (fuenteTitulo) ImGui::PopFont();

    if (fuentePequena) ImGui::PushFont(fuentePequena);
    ImGui::TextColored(tema::TEXT_MUTED(), "Personas, Estudiantes, Profesores y Administrativos");
    if (fuentePequena) ImGui::PopFont();

    ImGui::Spacing();
    if (ImGui::Button("+ Registrar Persona / Rol", ImVec2(210, 32))) {
        abrirModalPersona(false, 0);
    }
    ImGui::Spacing();

    if (ImGui::BeginTabBar("##TabsPersonas")) {

        // Tab Personas
        if (ImGui::BeginTabItem("Personas")) {
            ImGui::Spacing();

            // Buscador dinámico
            ImGui::SetNextItemWidth(320);
            ImGui::InputTextWithHint("##BuscarPersona", "Buscar persona por nombre, documento o correo...", perFiltroBusqueda, sizeof(perFiltroBusqueda));
            ImGui::SameLine();
            if (ImGui::Button("Limpiar##Per")) {
                perFiltroBusqueda[0] = '\0';
            }
            ImGui::SameLine();
            ImGui::TextColored(tema::TEXT_MUTED(), "(%d registradas)", ctrl.datos.personas.tamano());

            ImGui::Spacing();

            if (ImGui::BeginTable("##TablaPersonas", 8,
                ImGuiTableFlags_RowBg | ImGuiTableFlags_BordersOuter | ImGuiTableFlags_BordersInnerH |
                ImGuiTableFlags_Resizable | ImGuiTableFlags_ScrollY, ImVec2(0, 0))) {

                ImGui::TableSetupColumn("ID", ImGuiTableColumnFlags_WidthFixed, 50);
                ImGui::TableSetupColumn("Tipo Doc.", ImGuiTableColumnFlags_WidthFixed, 80);
                ImGui::TableSetupColumn("No. Documento", ImGuiTableColumnFlags_WidthFixed, 120);
                ImGui::TableSetupColumn("Nombre Completo", ImGuiTableColumnFlags_WidthStretch);
                ImGui::TableSetupColumn("Correo", ImGuiTableColumnFlags_WidthStretch);
                ImGui::TableSetupColumn("Ciudad", ImGuiTableColumnFlags_WidthFixed, 110);
                ImGui::TableSetupColumn("Estado", ImGuiTableColumnFlags_WidthFixed, 80);
                ImGui::TableSetupColumn("Acciones", ImGuiTableColumnFlags_WidthFixed, 140);
                ImGui::TableHeadersRow();

                std::string busqPer = perFiltroBusqueda;
                for (auto& ch : busqPer) ch = (char)tolower(ch);

                for (int i = 0; i < ctrl.datos.personas.tamano(); i++) {
                    auto& p = ctrl.datos.personas.obtener(i);
                    std::string nombre = (p.primerNombre ? *p.primerNombre : "") + " " +
                                         (p.segundoNombre ? *p.segundoNombre : "") + " " +
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
                    ImGui::TableNextColumn(); ImGui::Text("%d", p.idPersona ? *p.idPersona : 0);
                    ImGui::TableNextColumn(); ImGui::Text("%s", p.tipoDocumento ? p.tipoDocumento->c_str() : "---");
                    ImGui::TableNextColumn(); ImGui::TextColored(tema::ACCENT_WARNING(), "%s", p.numeroDocumento ? p.numeroDocumento->c_str() : "---");
                    ImGui::TableNextColumn(); ImGui::Text("%s", nombre.c_str());
                    ImGui::TableNextColumn(); ImGui::Text("%s", p.correoPersonal ? p.correoPersonal->c_str() : "---");
                    ImGui::TableNextColumn(); ImGui::Text("%s", p.ciudadResidencia ? p.ciudadResidencia->c_str() : "---");
                    ImGui::TableNextColumn();
                    if (p.estado && *p.estado == "ACTIVO") {
                        ImGui::PushStyleColor(ImGuiCol_Button, tema::BADGE_ACTIVE_BG());
                        ImGui::PushStyleColor(ImGuiCol_Text, tema::BADGE_ACTIVE_TXT());
                        ImGui::SmallButton("ACTIVO");
                        ImGui::PopStyleColor(2);
                    } else {
                        ImGui::Text("%s", p.estado ? p.estado->c_str() : "---");
                    }
                    ImGui::TableNextColumn();
                    ImGui::PushID(i);
                    if (ImGui::SmallButton("Editar")) {
                        abrirModalPersona(true, p.idPersona ? *p.idPersona : 0);
                    }
                    ImGui::SameLine();
                    if (p.estado && *p.estado == "ACTIVO") {
                        if (ImGui::SmallButton("Desactivar")) {
                            p.estado = "INACTIVO";
                            ctrl.guardarDatos();
                            ctrl.setMensaje("Persona desactivada.");
                        }
                    } else {
                        if (ImGui::SmallButton("Activar")) {
                            p.estado = "ACTIVO";
                            ctrl.guardarDatos();
                            ctrl.setMensaje("Persona activada.");
                        }
                    }
                    ImGui::PopID();
                }
                ImGui::EndTable();
            }
            ImGui::EndTabItem();
        }

        // Tab Estudiantes
        if (ImGui::BeginTabItem("Estudiantes")) {
            ImGui::Spacing();

            ImGui::SetNextItemWidth(300);
            ImGui::InputTextWithHint("##BuscarEstudiante", "Buscar por nombre o codigo de estudiante...", estFiltroBusqueda, sizeof(estFiltroBusqueda));
            ImGui::SameLine();
            if (ImGui::Button("Limpiar##Est")) {
                estFiltroBusqueda[0] = '\0';
            }
            ImGui::SameLine();
            ImGui::TextColored(tema::TEXT_MUTED(), "(%d matriculados)", ctrl.datos.estudiantes.tamano());

            ImGui::Spacing();

            if (ImGui::BeginTable("##TablaEstudiantes", 7,
                ImGuiTableFlags_RowBg | ImGuiTableFlags_BordersOuter | ImGuiTableFlags_BordersInnerH |
                ImGuiTableFlags_Resizable | ImGuiTableFlags_ScrollY, ImVec2(0, 0))) {

                ImGui::TableSetupColumn("ID", ImGuiTableColumnFlags_WidthFixed, 50);
                ImGui::TableSetupColumn("Codigo", ImGuiTableColumnFlags_WidthFixed, 105);
                ImGui::TableSetupColumn("Nombre", ImGuiTableColumnFlags_WidthStretch);
                ImGui::TableSetupColumn("Semestre", ImGuiTableColumnFlags_WidthFixed, 80);
                ImGui::TableSetupColumn("Creditos Apr.", ImGuiTableColumnFlags_WidthFixed, 100);
                ImGui::TableSetupColumn("Promedio", ImGuiTableColumnFlags_WidthFixed, 80);
                ImGui::TableSetupColumn("Estado Acad.", ImGuiTableColumnFlags_WidthFixed, 100);
                ImGui::TableHeadersRow();

                std::string busqEst = estFiltroBusqueda;
                for (auto& ch : busqEst) ch = (char)tolower(ch);

                for (int i = 0; i < ctrl.datos.estudiantes.tamano(); i++) {
                    auto& e = ctrl.datos.estudiantes.obtener(i);
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

                    if (!busqEst.empty()) {
                        std::string nLower = nombre;
                        for (auto& ch : nLower) ch = (char)tolower(ch);
                        std::string codLower = e.codigoEstudiante ? *e.codigoEstudiante : "";
                        for (auto& ch : codLower) ch = (char)tolower(ch);

                        if (nLower.find(busqEst) == std::string::npos && codLower.find(busqEst) == std::string::npos) {
                            continue;
                        }
                    }

                    ImGui::TableNextRow();
                    ImGui::TableNextColumn(); ImGui::Text("%d", e.idEstudiante ? *e.idEstudiante : 0);
                    ImGui::TableNextColumn(); ImGui::TextColored(tema::WIN_BLUE(), "%s", e.codigoEstudiante ? e.codigoEstudiante->c_str() : "---");
                    ImGui::TableNextColumn(); ImGui::Text("%s", nombre.c_str());
                    ImGui::TableNextColumn(); ImGui::Text("Sem. %d", e.semestreActual ? *e.semestreActual : 0);
                    ImGui::TableNextColumn(); ImGui::Text("%d cr.", e.creditosAprobados ? *e.creditosAprobados : 0);
                    ImGui::TableNextColumn();
                    if (e.promedioAcumulado && *e.promedioAcumulado < 3.0) {
                        ImGui::TextColored(tema::ACCENT_DANGER(), "%.2f", *e.promedioAcumulado);
                    } else {
                        ImGui::Text("%.2f", e.promedioAcumulado ? *e.promedioAcumulado : 0.0);
                    }
                    ImGui::TableNextColumn();
                    if (e.estadoAcademico) {
                        std::string ea = to_string(*e.estadoAcademico);
                        if (*e.estadoAcademico == EstadoAcademico::EBRA) {
                            ImGui::PushStyleColor(ImGuiCol_Button, tema::BADGE_EBRA_BG());
                            ImGui::PushStyleColor(ImGuiCol_Text, tema::BADGE_EBRA_TXT());
                            ImGui::SmallButton("EBRA");
                            ImGui::PopStyleColor(2);
                        } else {
                            ImGui::Text("%s", ea.c_str());
                        }
                    } else {
                        ImGui::Text("---");
                    }
                }
                ImGui::EndTable();
            }
            ImGui::EndTabItem();
        }

        // Tab Profesores
        if (ImGui::BeginTabItem("Profesores")) {
            ImGui::Spacing();

            ImGui::SetNextItemWidth(300);
            ImGui::InputTextWithHint("##BuscarProfesor", "Buscar por nombre o codigo de docente...", profFiltroBusqueda, sizeof(profFiltroBusqueda));
            ImGui::SameLine();
            if (ImGui::Button("Limpiar##Prof")) {
                profFiltroBusqueda[0] = '\0';
            }
            ImGui::SameLine();
            ImGui::TextColored(tema::TEXT_MUTED(), "(%d vinculados)", ctrl.datos.profesores.tamano());

            ImGui::Spacing();

            if (ImGui::BeginTable("##TablaProfesores", 7,
                ImGuiTableFlags_RowBg | ImGuiTableFlags_BordersOuter | ImGuiTableFlags_BordersInnerH |
                ImGuiTableFlags_Resizable | ImGuiTableFlags_ScrollY, ImVec2(0, 0))) {

                ImGui::TableSetupColumn("ID", ImGuiTableColumnFlags_WidthFixed, 50);
                ImGui::TableSetupColumn("Codigo", ImGuiTableColumnFlags_WidthFixed, 105);
                ImGui::TableSetupColumn("Nombre Docente", ImGuiTableColumnFlags_WidthStretch);
                ImGui::TableSetupColumn("Tipo / Modalidad", ImGuiTableColumnFlags_WidthFixed, 140);
                ImGui::TableSetupColumn("Dedicacion", ImGuiTableColumnFlags_WidthFixed, 130);
                ImGui::TableSetupColumn("Horas/Sem", ImGuiTableColumnFlags_WidthFixed, 90);
                ImGui::TableSetupColumn("Puntos Dec. 1279", ImGuiTableColumnFlags_WidthFixed, 120);
                ImGui::TableHeadersRow();

                std::string busqProf = profFiltroBusqueda;
                for (auto& ch : busqProf) ch = (char)tolower(ch);

                for (int i = 0; i < ctrl.datos.profesores.tamano(); i++) {
                    auto& prof = ctrl.datos.profesores.obtener(i);
                    std::string nombre = "---";
                    if (prof.idPersona) {
                        for (int j = 0; j < ctrl.datos.personas.tamano(); j++) {
                            auto& p = ctrl.datos.personas.obtener(j);
                            if (p.idPersona && *p.idPersona == *prof.idPersona) {
                                nombre = (p.primerNombre ? *p.primerNombre : "") + " " + (p.primerApellido ? *p.primerApellido : "");
                                break;
                            }
                        }
                    }

                    if (!busqProf.empty()) {
                        std::string nLower = nombre;
                        for (auto& ch : nLower) ch = (char)tolower(ch);
                        std::string codLower = prof.codigoProfesor ? *prof.codigoProfesor : "";
                        for (auto& ch : codLower) ch = (char)tolower(ch);

                        if (nLower.find(busqProf) == std::string::npos && codLower.find(busqProf) == std::string::npos) {
                            continue;
                        }
                    }

                    ImGui::TableNextRow();
                    ImGui::TableNextColumn(); ImGui::Text("%d", prof.idProfesor ? *prof.idProfesor : 0);
                    ImGui::TableNextColumn(); ImGui::TextColored(tema::ACCENT_INDIGO(), "%s", prof.codigoProfesor ? prof.codigoProfesor->c_str() : "---");
                    ImGui::TableNextColumn(); ImGui::Text("%s", nombre.c_str());
                    ImGui::TableNextColumn(); ImGui::Text("%s", prof.tipoProfesor ? to_string(*prof.tipoProfesor).c_str() : "---");
                    ImGui::TableNextColumn(); ImGui::Text("%s", prof.dedicacion ? to_string(*prof.dedicacion).c_str() : "---");
                    ImGui::TableNextColumn(); ImGui::Text("%.1f h", prof.numeroHorasSemanales ? *prof.numeroHorasSemanales : 0.0);
                    ImGui::TableNextColumn();
                    double pts = prof.puntosSalariales.value_or(0.0);
                    ImGui::TextColored(tema::ACCENT_WARNING(), "%.0f pts", pts);
                }
                ImGui::EndTable();
            }
            ImGui::EndTabItem();
        }

        // Tab Administrativos
        if (ImGui::BeginTabItem("Administrativos")) {
            ImGui::Spacing();
            if (ImGui::BeginTable("##TablaAdmin", 6,
                ImGuiTableFlags_RowBg | ImGuiTableFlags_BordersOuter | ImGuiTableFlags_BordersInnerH |
                ImGuiTableFlags_Resizable | ImGuiTableFlags_ScrollY, ImVec2(0, 0))) {

                ImGui::TableSetupColumn("ID");
                ImGui::TableSetupColumn("Codigo");
                ImGui::TableSetupColumn("Nombre");
                ImGui::TableSetupColumn("Cargo");
                ImGui::TableSetupColumn("Dependencia");
                ImGui::TableSetupColumn("Estado");
                ImGui::TableHeadersRow();

                for (int i = 0; i < ctrl.datos.administrativos.tamano(); i++) {
                    auto& a = ctrl.datos.administrativos.obtener(i);
                    std::string nombre = "---";
                    if (a.idPersona) {
                        for (int j = 0; j < ctrl.datos.personas.tamano(); j++) {
                            auto& p = ctrl.datos.personas.obtener(j);
                            if (p.idPersona && *p.idPersona == *a.idPersona) {
                                nombre = (p.primerNombre ? *p.primerNombre : "") + " " + (p.primerApellido ? *p.primerApellido : "");
                                break;
                            }
                        }
                    }
                    ImGui::TableNextRow();
                    ImGui::TableNextColumn(); ImGui::Text("%d", a.idAdministrativo ? *a.idAdministrativo : 0);
                    ImGui::TableNextColumn(); ImGui::Text("%s", a.codigoEmpleado ? a.codigoEmpleado->c_str() : "---");
                    ImGui::TableNextColumn(); ImGui::Text("%s", nombre.c_str());
                    ImGui::TableNextColumn(); ImGui::Text("%s", a.cargo ? a.cargo->c_str() : "---");
                    ImGui::TableNextColumn(); ImGui::Text("%s", a.dependencia ? a.dependencia->c_str() : "---");
                    ImGui::TableNextColumn();
                    if (a.estado && *a.estado == "ACTIVO") {
                        ImGui::PushStyleColor(ImGuiCol_Button, tema::BADGE_ACTIVE_BG());
                        ImGui::PushStyleColor(ImGuiCol_Text, tema::BADGE_ACTIVE_TXT());
                        ImGui::SmallButton("ACTIVO");
                        ImGui::PopStyleColor(2);
                    } else {
                        ImGui::Text("%s", a.estado ? a.estado->c_str() : "---");
                    }
                }
                ImGui::EndTable();
            }
            ImGui::EndTabItem();
        }

        ImGui::EndTabBar();
    }
}

// ======================================================================
// HELPER APERTURA MODAL PERSONA
// ======================================================================

void PITAApp::abrirModalPersona(bool editar, int idPersona) {
    modoEditarPersona = editar;
    idPersonaEditando = idPersona;
    mensajeModal[0] = '\0';
    errorModal = false;

    if (editar && idPersona > 0) {
        for (int i = 0; i < ctrl.datos.personas.tamano(); i++) {
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

                // Selector de Programa Académico
                if (ctrl.datos.programas.tamano() > 0) {
                    std::string previewProg = "Seleccione Programa";
                    for (int i = 0; i < ctrl.datos.programas.tamano(); i++) {
                        auto& pr = ctrl.datos.programas.obtener(i);
                        if (pr.idPrograma && *pr.idPrograma == estProgramaId) {
                            previewProg = pr.nombre ? *pr.nombre : "---";
                            break;
                        }
                    }
                    if (ImGui::BeginCombo("Programa *", previewProg.c_str())) {
                        for (int i = 0; i < ctrl.datos.programas.tamano(); i++) {
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
                ImGui::InputText("Cargo *", admCargo, sizeof(admCargo));
                ImGui::InputText("Dependencia *", admDependencia, sizeof(admDependencia));
            }
        }

        ImGui::Spacing();
        ImGui::Separator();
        ImGui::Spacing();

        if (ImGui::Button("Guardar", ImVec2(120, 0))) {
            if (strlen(pNumDoc) == 0 || strlen(pPrimerNombre) == 0 || strlen(pPrimerApellido) == 0) {
                strncpy(mensajeModal, "Documento, Primer Nombre y Primer Apellido son obligatorios.", sizeof(mensajeModal) - 1);
                errorModal = true;
            } else {
                try {
                    int idPersFinal = idPersonaEditando;

                    if (modoEditarPersona) {
                        for (int i = 0; i < ctrl.datos.personas.tamano(); i++) {
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
                        for (int i = 0; i < ctrl.datos.personas.tamano(); i++) {
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
                            for (int i = 0; i < ctrl.datos.estudiantes.tamano(); i++) {
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
                            for (int i = 0; i < ctrl.datos.profesores.tamano(); i++) {
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
                            for (int i = 0; i < ctrl.datos.administrativos.tamano(); i++) {
                                auto& a = ctrl.datos.administrativos.obtener(i);
                                if (a.idAdministrativo && *a.idAdministrativo > maxAdmId) maxAdmId = *a.idAdministrativo;
                            }
                            adm.idAdministrativo = maxAdmId + 1;
                            adm.idPersona = idPersFinal;
                            adm.codigoEmpleado = admCodigo;
                            adm.cargo = admCargo;
                            adm.dependencia = admDependencia;
                            adm.estado = "ACTIVO";
                            ctrl.datos.administrativos.push_back(adm);
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
        if (ImGui::Button("Cancelar", ImVec2(120, 0))) {
            modalPersonaAbierto = false;
            ImGui::CloseCurrentPopup();
        }

        ImGui::EndPopup();
    }
}

} // namespace pita
