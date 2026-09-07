#define _CRT_SECURE_NO_WARNINGS
#include "gui_app.h"
#include "tema.h"
#include "imgui.h"

#include <cstring>
#include <string>

namespace pita {

// ======================================================================
// VISTA: FACULTADES
// ======================================================================

static std::string getNombreDocentePersona(const GUIController& ctrl, int idPersona) {
    for (size_t i = 0; i < ctrl.datos.personas.tamano(); ++i) {
        auto& p = ctrl.datos.personas.obtener(i);
        if (p.idPersona && *p.idPersona == idPersona) {
            std::string nom = p.primerNombre.value_or("");
            std::string ape = p.primerApellido.value_or("");
            return nom + " " + ape;
        }
    }
    return "Desconocido";
}

static std::string getNombreDecano(const GUIController& ctrl, std::optional<int> idDecano) {
    if (!idDecano || *idDecano <= 0) return "Sin Asignar";
    for (size_t i = 0; i < ctrl.datos.profesores.tamano(); ++i) {
        auto& prof = ctrl.datos.profesores.obtener(i);
        if (prof.idProfesor && *prof.idProfesor == *idDecano) {
            std::string nom = getNombreDocentePersona(ctrl, prof.idPersona.value_or(0));
            std::string cod = prof.codigoProfesor.value_or("");
            return cod.empty() ? nom : (nom + " (" + cod + ")");
        }
    }
    return "Docente #" + std::to_string(*idDecano);
}

void PITAApp::renderFacultades() {
    if (fuenteTitulo) ImGui::PushFont(fuenteTitulo);
    ImGui::TextColored(tema::TEXT_MAIN(), "Facultades & Programas Academicos");
    if (fuenteTitulo) ImGui::PopFont();

    if (fuentePequena) ImGui::PushFont(fuentePequena);
    ImGui::TextColored(tema::TEXT_MUTED(), "Gestion de la estructura institucional");
    if (fuentePequena) ImGui::PopFont();

    ImGui::Spacing(); ImGui::Spacing();

    if (ImGui::BeginTabBar("##TabsFacultades")) {

        // Tab Universidad
        if (ImGui::BeginTabItem("Universidad")) {
            ImGui::Spacing();
            ImGui::PushStyleColor(ImGuiCol_ChildBg, tema::BG_CARD());
            ImGui::PushStyleVar(ImGuiStyleVar_ChildRounding, 10.0f);
            ImGui::BeginChild("##UniCard", ImVec2(0, 0), ImGuiChildFlags_Borders);

            if (ctrl.datos.universidades.tamano() > 0) {
                auto& u = ctrl.datos.universidades.obtener(0);
                ImGui::SetCursorPos(ImVec2(20, 20));
                if (fuenteNormal) ImGui::PushFont(fuenteNormal);
                ImGui::TextColored(tema::WIN_BLUE(), "Informacion Institucional");
                if (fuenteNormal) ImGui::PopFont();
                ImGui::Spacing();
                ImGui::SetCursorPosX(20);
                ImGui::Text("Nombre: %s", u.nombre ? u.nombre->c_str() : "---");
                ImGui::SetCursorPosX(20);
                ImGui::Text("NIT: %s", u.nit ? u.nit->c_str() : "---");
                ImGui::SetCursorPosX(20);
                ImGui::Text("Ciudad: %s, %s", u.ciudad ? u.ciudad->c_str() : "---", u.departamento ? u.departamento->c_str() : "---");
                ImGui::SetCursorPosX(20);
                ImGui::Text("Telefono: %s", u.telefono ? u.telefono->c_str() : "---");
                ImGui::SetCursorPosX(20);
                ImGui::Text("Correo: %s", u.correoInstitucional ? u.correoInstitucional->c_str() : "---");
                ImGui::SetCursorPosX(20);
                ImGui::Text("Web: %s", u.sitioWeb ? u.sitioWeb->c_str() : "---");
            } else {
                ImGui::SetCursorPos(ImVec2(20, 20));
                ImGui::TextColored(tema::TEXT_MUTED(), "No hay datos de universidad registrados.");
            }

            ImGui::EndChild();
            ImGui::PopStyleVar();
            ImGui::PopStyleColor();
            ImGui::EndTabItem();
        }

        // Tab Facultades
        if (ImGui::BeginTabItem("Facultades")) {
            ImGui::Spacing();
            if (ImGui::Button("+ Nueva Facultad", ImVec2(150, 30))) {
                facCodigo[0] = '\0';
                facNombre[0] = '\0';
                facUbicacion[0] = '\0';
                facDecano[0] = '\0';
                facDecanoId = 0;
                mensajeModal[0] = '\0';
                errorModal = false;
                modalFacultadAbierto = true;
            }
            ImGui::Spacing();
            if (ImGui::BeginTable("##TablaFacultades", 7,
                ImGuiTableFlags_RowBg | ImGuiTableFlags_BordersOuter | ImGuiTableFlags_BordersInnerH |
                ImGuiTableFlags_Resizable | ImGuiTableFlags_ScrollY, ImVec2(0, 0))) {

                ImGui::TableSetupColumn("ID");
                ImGui::TableSetupColumn("Codigo");
                ImGui::TableSetupColumn("Nombre");
                ImGui::TableSetupColumn("Decano / Responsable");
                ImGui::TableSetupColumn("Ubicacion");
                ImGui::TableSetupColumn("Correo");
                ImGui::TableSetupColumn("Estado");
                ImGui::TableHeadersRow();

                for (int i = 0; i < ctrl.datos.facultades.tamano(); i++) {
                    auto& f = ctrl.datos.facultades.obtener(i);
                    ImGui::TableNextRow();
                    ImGui::TableNextColumn(); ImGui::Text("%d", f.idFacultad ? *f.idFacultad : 0);
                    ImGui::TableNextColumn(); ImGui::Text("%s", f.codigoFacultad ? f.codigoFacultad->c_str() : "---");
                    ImGui::TableNextColumn(); ImGui::Text("%s", f.nombre ? f.nombre->c_str() : "---");
                    ImGui::TableNextColumn();
                    std::string nomDec = getNombreDecano(ctrl, f.idDecano);
                    if (f.idDecano && *f.idDecano > 0) {
                        ImGui::TextColored(tema::WIN_BLUE(), "%s", nomDec.c_str());
                    } else {
                        ImGui::TextColored(tema::TEXT_MUTED(), "%s", nomDec.c_str());
                    }
                    ImGui::TableNextColumn(); ImGui::Text("%s", f.ubicacion ? f.ubicacion->c_str() : "---");
                    ImGui::TableNextColumn(); ImGui::Text("%s", f.correo ? f.correo->c_str() : "---");
                    ImGui::TableNextColumn();
                    if (f.estado && *f.estado == "ACTIVO") {
                        ImGui::PushStyleColor(ImGuiCol_Button, tema::BADGE_ACTIVE_BG());
                        ImGui::PushStyleColor(ImGuiCol_Text, tema::BADGE_ACTIVE_TXT());
                        ImGui::SmallButton("ACTIVO");
                        ImGui::PopStyleColor(2);
                    } else {
                        ImGui::Text("%s", f.estado ? f.estado->c_str() : "---");
                    }
                }
                ImGui::EndTable();
            }
            ImGui::EndTabItem();
        }

        // Tab Programas
        if (ImGui::BeginTabItem("Programas")) {
            ImGui::Spacing();
            if (ImGui::Button("+ Nuevo Programa", ImVec2(160, 30))) {
                progCodigo[0] = '\0';
                progNombre[0] = '\0';
                if (ctrl.datos.facultades.tamano() > 0) {
                    progFacultadId = ctrl.datos.facultades.obtener(0).idFacultad.value_or(1);
                }
                progNivelIdx = 0;
                progCreditos = 160;
                mensajeModal[0] = '\0';
                errorModal = false;
                modalProgramaAbierto = true;
            }
            ImGui::Spacing();
            if (ImGui::BeginTable("##TablaProgramas", 7,
                ImGuiTableFlags_RowBg | ImGuiTableFlags_BordersOuter | ImGuiTableFlags_BordersInnerH |
                ImGuiTableFlags_Resizable | ImGuiTableFlags_ScrollY, ImVec2(0, 0))) {

                ImGui::TableSetupColumn("ID");
                ImGui::TableSetupColumn("Codigo");
                ImGui::TableSetupColumn("Nombre");
                ImGui::TableSetupColumn("Nivel");
                ImGui::TableSetupColumn("Creditos");
                ImGui::TableSetupColumn("Facultad");
                ImGui::TableSetupColumn("Estado");
                ImGui::TableHeadersRow();

                for (int i = 0; i < ctrl.datos.programas.tamano(); i++) {
                    auto& p = ctrl.datos.programas.obtener(i);
                    ImGui::TableNextRow();
                    ImGui::TableNextColumn(); ImGui::Text("%d", p.idPrograma ? *p.idPrograma : 0);
                    ImGui::TableNextColumn(); ImGui::Text("%s", p.codigoPrograma ? p.codigoPrograma->c_str() : "---");
                    ImGui::TableNextColumn(); ImGui::Text("%s", p.nombre ? p.nombre->c_str() : "---");
                    ImGui::TableNextColumn(); ImGui::Text("%s", p.nivelFormacion ? p.nivelFormacion->c_str() : "PREGRADO");
                    ImGui::TableNextColumn(); ImGui::Text("%d", p.totalCreditos ? *p.totalCreditos : 0);
                    ImGui::TableNextColumn();
                    std::string nomFac = "---";
                    if (p.idFacultad) {
                        for (int j = 0; j < ctrl.datos.facultades.tamano(); j++) {
                            auto& f = ctrl.datos.facultades.obtener(j);
                            if (f.idFacultad && *f.idFacultad == *p.idFacultad) {
                                nomFac = f.nombre ? *f.nombre : "---";
                                break;
                            }
                        }
                    }
                    ImGui::Text("%s", nomFac.c_str());
                    ImGui::TableNextColumn();
                    if (p.estado && *p.estado == "ACTIVO") {
                        ImGui::PushStyleColor(ImGuiCol_Button, tema::BADGE_ACTIVE_BG());
                        ImGui::PushStyleColor(ImGuiCol_Text, tema::BADGE_ACTIVE_TXT());
                        ImGui::SmallButton("ACTIVO");
                        ImGui::PopStyleColor(2);
                    } else {
                        ImGui::Text("%s", p.estado ? p.estado->c_str() : "---");
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
// MODALES FACULTAD & PROGRAMA
// ======================================================================

void PITAApp::renderModalFacultad() {
    if (modalFacultadAbierto) {
        ImGui::OpenPopup("Nueva Facultad");
    }

    ImVec2 center = ImGui::GetMainViewport()->GetCenter();
    ImGui::SetNextWindowPos(center, ImGuiCond_Appearing, ImVec2(0.5f, 0.5f));
    ImGui::SetNextWindowSize(ImVec2(480, 0), ImGuiCond_Always);

    if (ImGui::BeginPopupModal("Nueva Facultad", &modalFacultadAbierto, ImGuiWindowFlags_AlwaysAutoResize)) {
        if (strlen(mensajeModal) > 0) {
            ImGui::TextColored(errorModal ? tema::ACCENT_DANGER() : tema::ACCENT_SUCCESS(), "%s", mensajeModal);
            ImGui::Separator();
        }

        ImGui::InputText("Codigo *", facCodigo, sizeof(facCodigo));
        ImGui::InputText("Nombre *", facNombre, sizeof(facNombre));
        ImGui::InputText("Ubicacion", facUbicacion, sizeof(facUbicacion));

        // Combo Decano / Autoridad Académica
        std::string previewDecano = "(Sin Decano Asignado)";
        if (facDecanoId > 0) {
            previewDecano = getNombreDecano(ctrl, facDecanoId);
        }

        if (ImGui::BeginCombo("Decano / Responsable", previewDecano.c_str())) {
            bool selNinguno = (facDecanoId == 0);
            if (ImGui::Selectable("(Sin Decano Asignado)", selNinguno)) {
                facDecanoId = 0;
            }
            if (selNinguno) ImGui::SetItemDefaultFocus();

            for (size_t i = 0; i < ctrl.datos.profesores.tamano(); ++i) {
                auto& pr = ctrl.datos.profesores.obtener(i);
                int pId = pr.idProfesor.value_or(0);
                std::string label = getNombreDecano(ctrl, pId);
                bool sel = (facDecanoId == pId);
                if (ImGui::Selectable(label.c_str(), sel)) {
                    facDecanoId = pId;
                }
                if (sel) ImGui::SetItemDefaultFocus();
            }
            ImGui::EndCombo();
        }

        ImGui::Spacing();
        ImGui::Separator();

        if (ImGui::Button("Guardar", ImVec2(120, 0))) {
            if (strlen(facCodigo) == 0 || strlen(facNombre) == 0) {
                strncpy(mensajeModal, "Codigo y Nombre son obligatorios.", sizeof(mensajeModal) - 1);
                errorModal = true;
            } else {
                Facultad f;
                int maxId = 0;
                for (int i = 0; i < ctrl.datos.facultades.tamano(); i++) {
                    auto& fac = ctrl.datos.facultades.obtener(i);
                    if (fac.idFacultad && *fac.idFacultad > maxId) maxId = *fac.idFacultad;
                }
                f.idFacultad = maxId + 1;
                f.codigoFacultad = facCodigo;
                f.nombre = facNombre;
                if (strlen(facUbicacion) > 0) f.ubicacion = facUbicacion;
                if (facDecanoId > 0) {
                    f.idDecano = facDecanoId;
                } else {
                    f.idDecano = std::nullopt;
                }
                f.estado = "ACTIVO";

                ctrl.datos.facultades.push_back(f);
                ctrl.guardarDatos();
                ctrl.setMensaje("Facultad registrada con exito.");
                modalFacultadAbierto = false;
                ImGui::CloseCurrentPopup();
            }
        }

        ImGui::SameLine();
        if (ImGui::Button("Cancelar", ImVec2(120, 0))) {
            modalFacultadAbierto = false;
            ImGui::CloseCurrentPopup();
        }

        ImGui::EndPopup();
    }
}

void PITAApp::renderModalPrograma() {
    if (modalProgramaAbierto) {
        ImGui::OpenPopup("Nuevo Programa Academico");
    }

    ImVec2 center = ImGui::GetMainViewport()->GetCenter();
    ImGui::SetNextWindowPos(center, ImGuiCond_Appearing, ImVec2(0.5f, 0.5f));
    ImGui::SetNextWindowSize(ImVec2(480, 0), ImGuiCond_Always);

    if (ImGui::BeginPopupModal("Nuevo Programa Academico", &modalProgramaAbierto, ImGuiWindowFlags_AlwaysAutoResize)) {
        if (strlen(mensajeModal) > 0) {
            ImGui::TextColored(errorModal ? tema::ACCENT_DANGER() : tema::ACCENT_SUCCESS(), "%s", mensajeModal);
            ImGui::Separator();
        }

        ImGui::InputText("Codigo *", progCodigo, sizeof(progCodigo));
        ImGui::InputText("Nombre *", progNombre, sizeof(progNombre));

        if (ctrl.datos.facultades.tamano() > 0) {
            std::string previewFac = "Seleccione Facultad";
            for (int i = 0; i < ctrl.datos.facultades.tamano(); i++) {
                auto& f = ctrl.datos.facultades.obtener(i);
                if (f.idFacultad && *f.idFacultad == progFacultadId) {
                    previewFac = f.nombre ? *f.nombre : "---";
                    break;
                }
            }
            if (ImGui::BeginCombo("Facultad *", previewFac.c_str())) {
                for (int i = 0; i < ctrl.datos.facultades.tamano(); i++) {
                    auto& f = ctrl.datos.facultades.obtener(i);
                    bool isSelected = (f.idFacultad && *f.idFacultad == progFacultadId);
                    std::string label = f.nombre ? *f.nombre : "Facultad";
                    if (ImGui::Selectable(label.c_str(), isSelected)) {
                        progFacultadId = f.idFacultad.value_or(1);
                    }
                    if (isSelected) ImGui::SetItemDefaultFocus();
                }
                ImGui::EndCombo();
            }
        }

        const char* niveles[] = { "PREGRADO", "POSGRADO" };
        ImGui::Combo("Nivel de Formacion", &progNivelIdx, niveles, IM_ARRAYSIZE(niveles));
        ImGui::InputInt("Creditos Totales", &progCreditos);
        if (progCreditos < 1) progCreditos = 1;

        ImGui::Spacing();
        ImGui::Separator();

        if (ImGui::Button("Guardar", ImVec2(120, 0))) {
            if (strlen(progCodigo) == 0 || strlen(progNombre) == 0) {
                strncpy(mensajeModal, "Codigo y Nombre son obligatorios.", sizeof(mensajeModal) - 1);
                errorModal = true;
            } else {
                ProgramaAcademico p;
                int maxId = 0;
                for (int i = 0; i < ctrl.datos.programas.tamano(); i++) {
                    auto& pr = ctrl.datos.programas.obtener(i);
                    if (pr.idPrograma && *pr.idPrograma > maxId) maxId = *pr.idPrograma;
                }
                p.idPrograma = maxId + 1;
                p.codigoPrograma = progCodigo;
                p.nombre = progNombre;
                p.idFacultad = progFacultadId;
                p.nivelFormacion = (progNivelIdx == 0 ? "PREGRADO" : "POSGRADO");
                p.totalCreditos = progCreditos;
                p.estado = "ACTIVO";

                ctrl.datos.programas.push_back(p);
                ctrl.guardarDatos();
                ctrl.setMensaje("Programa academico registrado con exito.");
                modalProgramaAbierto = false;
                ImGui::CloseCurrentPopup();
            }
        }

        ImGui::SameLine();
        if (ImGui::Button("Cancelar", ImVec2(120, 0))) {
            modalProgramaAbierto = false;
            ImGui::CloseCurrentPopup();
        }

        ImGui::EndPopup();
    }
}

} // namespace pita
