#define _CRT_SECURE_NO_WARNINGS
#include "gui_app.h"
#include "tema.h"
#include "imgui.h"

#include <cstring>
#include <string>

namespace pita {

// ======================================================================
// VISTA: CONTRATOS
// ======================================================================

void PITAApp::renderContratos() {
    if (fuenteTitulo) ImGui::PushFont(fuenteTitulo);
    ImGui::TextColored(tema::TEXT_MAIN(), "Contratacion Docente");
    if (fuenteTitulo) ImGui::PopFont();

    if (fuentePequena) ImGui::PushFont(fuentePequena);
    ImGui::TextColored(tema::TEXT_MUTED(), "Contratos de vinculacion docente (Planta, Ocasional, Catedra)");
    if (fuentePequena) ImGui::PopFont();

    ImGui::Spacing();
    if (ImGui::Button("+ Nuevo Contrato Docente", ImVec2(200, 32))) {
        if (ctrl.datos.profesores.tamano() > 0) {
            conPersonaId = ctrl.datos.profesores.obtener(0).idPersona.value_or(1);
        }
        conTipoIdx = 0;
        conSalarioBase = 3500000.0;
        conHoras = 16.0;
        mensajeModal[0] = '\0';
        errorModal = false;
        modalContratoAbierto = true;
    }
    ImGui::Spacing();

    if (ImGui::BeginTable("##TablaContratos", 10,
        ImGuiTableFlags_RowBg | ImGuiTableFlags_BordersOuter | ImGuiTableFlags_BordersInnerH |
        ImGuiTableFlags_Resizable | ImGuiTableFlags_ScrollY, ImVec2(0, 0))) {

        ImGui::TableSetupColumn("ID");
        ImGui::TableSetupColumn("Profesor");
        ImGui::TableSetupColumn("Tipo");
        ImGui::TableSetupColumn("Dedicacion");
        ImGui::TableSetupColumn("Horas");
        ImGui::TableSetupColumn("Fecha Inicio");
        ImGui::TableSetupColumn("Fecha Fin");
        ImGui::TableSetupColumn("Salario Base");
        ImGui::TableSetupColumn("Estado");
        ImGui::TableSetupColumn("Acciones");
        ImGui::TableHeadersRow();

        for (int i = 0; i < ctrl.datos.contratos.tamano(); i++) {
            auto& c = ctrl.datos.contratos.obtener(i);

            // Buscar nombre del profesor
            std::string nombre = "---";
            if (c.idPersona) {
                for (int j = 0; j < ctrl.datos.personas.tamano(); j++) {
                    auto& p = ctrl.datos.personas.obtener(j);
                    if (p.idPersona && *p.idPersona == *c.idPersona) {
                        nombre = (p.primerNombre ? *p.primerNombre : "") + " " + (p.primerApellido ? *p.primerApellido : "");
                        break;
                    }
                }
            }

            ImGui::TableNextRow();
            ImGui::TableNextColumn(); ImGui::Text("%d", c.idContrato ? *c.idContrato : 0);
            ImGui::TableNextColumn(); ImGui::Text("%s", nombre.c_str());
            ImGui::TableNextColumn(); ImGui::Text("%s", c.tipoContrato ? c.tipoContrato->c_str() : "---");
            ImGui::TableNextColumn(); ImGui::Text("%s", c.dedicacion ? to_string(*c.dedicacion).c_str() : "---");
            ImGui::TableNextColumn(); ImGui::Text("%.1f", c.horasSemanales ? *c.horasSemanales : 0.0);
            ImGui::TableNextColumn(); ImGui::Text("%s", c.fechaInicio ? c.fechaInicio->c_str() : "---");
            ImGui::TableNextColumn(); ImGui::Text("%s", c.fechaFin ? c.fechaFin->c_str() : "---");
            ImGui::TableNextColumn(); ImGui::Text("$%.0f", c.salarioBase ? *c.salarioBase : 0.0);
            ImGui::TableNextColumn();
            if (c.estado && *c.estado == "ACTIVO") {
                ImGui::PushStyleColor(ImGuiCol_Button, tema::BADGE_ACTIVE_BG());
                ImGui::PushStyleColor(ImGuiCol_Text, tema::BADGE_ACTIVE_TXT());
                ImGui::SmallButton("ACTIVO");
                ImGui::PopStyleColor(2);
            } else {
                ImGui::Text("%s", c.estado ? c.estado->c_str() : "---");
            }
            ImGui::TableNextColumn();
            ImGui::PushID(i);
            if (c.estado && *c.estado == "ACTIVO") {
                if (ImGui::SmallButton("Terminar")) {
                    idContratoTerminando = c.idContrato ? *c.idContrato : 0;
                    mensajeModal[0] = '\0';
                    errorModal = false;
                    modalTerminarContratoAbierto = true;
                }
            } else {
                ImGui::TextDisabled("Cerrado");
            }
            ImGui::PopID();
        }
        ImGui::EndTable();
    }
}

// ======================================================================
// MODALES CONTRATO & TERMINAR CONTRATO
// ======================================================================

void PITAApp::renderModalContrato() {
    if (modalContratoAbierto) {
        ImGui::OpenPopup("Nuevo Contrato Docente");
    }

    ImVec2 center = ImGui::GetMainViewport()->GetCenter();
    ImGui::SetNextWindowPos(center, ImGuiCond_Appearing, ImVec2(0.5f, 0.5f));
    ImGui::SetNextWindowSize(ImVec2(520, 0), ImGuiCond_Always);

    if (ImGui::BeginPopupModal("Nuevo Contrato Docente", &modalContratoAbierto, ImGuiWindowFlags_AlwaysAutoResize)) {
        if (strlen(mensajeModal) > 0) {
            ImGui::TextColored(errorModal ? tema::ACCENT_DANGER() : tema::ACCENT_SUCCESS(), "%s", mensajeModal);
            ImGui::Separator();
        }

        // Selector Profesor
        std::string previewProf = "Seleccione Profesor";
        for (int i = 0; i < ctrl.datos.profesores.tamano(); i++) {
            auto& pr = ctrl.datos.profesores.obtener(i);
            if (pr.idPersona && *pr.idPersona == conPersonaId) {
                previewProf = pr.codigoProfesor ? *pr.codigoProfesor : ("Profesor #" + std::to_string(pr.idProfesor.value_or(0)));
                break;
            }
        }
        if (ImGui::BeginCombo("Docente *", previewProf.c_str())) {
            for (int i = 0; i < ctrl.datos.profesores.tamano(); i++) {
                auto& pr = ctrl.datos.profesores.obtener(i);
                bool isSelected = (pr.idPersona && *pr.idPersona == conPersonaId);
                std::string label = pr.codigoProfesor ? *pr.codigoProfesor : ("Profesor ID " + std::to_string(pr.idPersona.value_or(0)));
                if (ImGui::Selectable(label.c_str(), isSelected)) {
                    conPersonaId = pr.idPersona.value_or(1);
                }
                if (isSelected) ImGui::SetItemDefaultFocus();
            }
            ImGui::EndCombo();
        }

        const char* tipos[] = { "DOCENTE_PLANTA", "DOCENTE_OCASIONAL", "DOCENTE_CATEDRA" };
        ImGui::Combo("Tipo de Contrato *", &conTipoIdx, tipos, IM_ARRAYSIZE(tipos));

        ImGui::InputDouble("Horas Semanales", &conHoras, 1.0, 4.0, "%.1f");
        if (conTipoIdx == 2 && conHoras > 18.0) {
            ImGui::TextColored(tema::ACCENT_DANGER(), "Advertencia legal: Catedraticos maximo 18h/semana.");
        }

        ImGui::InputDouble("Salario Base / Asignacion *", &conSalarioBase, 50000.0, 500000.0, "%.0f");
        ImGui::InputText("Fecha Inicio (YYYY-MM-DD)", conFechaInicio, sizeof(conFechaInicio));
        ImGui::InputText("Fecha Fin (YYYY-MM-DD)", conFechaFin, sizeof(conFechaFin));

        ImGui::Spacing();
        ImGui::Separator();

        if (ImGui::Button("Crear Contrato", ImVec2(140, 0))) {
            try {
                Contrato c;
                c.idPersona = conPersonaId;
                c.tipoContrato = tipos[conTipoIdx];
                c.horasSemanales = conHoras;
                c.salarioBase = conSalarioBase;
                c.fechaInicio = conFechaInicio;
                c.fechaFin = conFechaFin;
                c.estado = "ACTIVO";

                ctrl.gestorContratos->crearContrato(c);
                ctrl.guardarDatos();
                ctrl.setMensaje("Contrato creado y validado legalmente.");
                modalContratoAbierto = false;
                ImGui::CloseCurrentPopup();
            } catch (const std::exception& e) {
                strncpy(mensajeModal, e.what(), sizeof(mensajeModal) - 1);
                errorModal = true;
            }
        }

        ImGui::SameLine();
        if (ImGui::Button("Cancelar", ImVec2(120, 0))) {
            modalContratoAbierto = false;
            ImGui::CloseCurrentPopup();
        }

        ImGui::EndPopup();
    }
}

void PITAApp::renderModalTerminarContrato() {
    if (modalTerminarContratoAbierto) {
        ImGui::OpenPopup("Terminar Contrato");
    }

    ImVec2 center = ImGui::GetMainViewport()->GetCenter();
    ImGui::SetNextWindowPos(center, ImGuiCond_Appearing, ImVec2(0.5f, 0.5f));
    ImGui::SetNextWindowSize(ImVec2(480, 0), ImGuiCond_Always);

    if (ImGui::BeginPopupModal("Terminar Contrato", &modalTerminarContratoAbierto, ImGuiWindowFlags_AlwaysAutoResize)) {
        if (strlen(mensajeModal) > 0) {
            ImGui::TextColored(errorModal ? tema::ACCENT_DANGER() : tema::ACCENT_SUCCESS(), "%s", mensajeModal);
            ImGui::Separator();
        }

        ImGui::Text("Terminando Contrato ID: %d", idContratoTerminando);
        ImGui::Spacing();

        ImGui::InputText("Causal de Terminacion *", conCausal, sizeof(conCausal));
        ImGui::InputText("Acto Administrativo *", conDocumento, sizeof(conDocumento));

        ImGui::Spacing();
        ImGui::Separator();

        if (ImGui::Button("Confirmar Terminacion", ImVec2(170, 0))) {
            try {
                ctrl.gestorContratos->terminarContrato(idContratoTerminando, conCausal, conDocumento);
                ctrl.guardarDatos();
                ctrl.setMensaje("Contrato terminado conforme a la norma.");
                modalTerminarContratoAbierto = false;
                ImGui::CloseCurrentPopup();
            } catch (const std::exception& e) {
                strncpy(mensajeModal, e.what(), sizeof(mensajeModal) - 1);
                errorModal = true;
            }
        }

        ImGui::SameLine();
        if (ImGui::Button("Cancelar", ImVec2(120, 0))) {
            modalTerminarContratoAbierto = false;
            ImGui::CloseCurrentPopup();
        }

        ImGui::EndPopup();
    }
}

} // namespace pita
