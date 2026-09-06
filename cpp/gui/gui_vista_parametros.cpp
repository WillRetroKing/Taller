#define _CRT_SECURE_NO_WARNINGS
#include "gui_app.h"
#include "tema.h"
#include "imgui.h"

#include <cstring>
#include <string>

namespace pita {

// ======================================================================
// VISTA: PARÁMETROS NORMATIVOS
// ======================================================================

void PITAApp::renderParametros() {
    if (fuenteTitulo) ImGui::PushFont(fuenteTitulo);
    ImGui::TextColored(tema::TEXT_MAIN(), "Parametros Normativos");
    if (fuenteTitulo) ImGui::PopFont();

    if (fuentePequena) ImGui::PushFont(fuentePequena);
    ImGui::TextColored(tema::TEXT_MUTED(), "Parametros legales y normativos del sistema (SMLMV, tasas, porcentajes)");
    if (fuentePequena) ImGui::PopFont();

    ImGui::Spacing(); ImGui::Spacing();

    if (ImGui::BeginTable("##TablaParametros", 6,
        ImGuiTableFlags_RowBg | ImGuiTableFlags_BordersOuter | ImGuiTableFlags_BordersInnerH |
        ImGuiTableFlags_Resizable | ImGuiTableFlags_ScrollY, ImVec2(0, 0))) {

        ImGui::TableSetupColumn("ID");
        ImGui::TableSetupColumn("Codigo");
        ImGui::TableSetupColumn("Descripcion");
        ImGui::TableSetupColumn("Valor");
        ImGui::TableSetupColumn("Estado");
        ImGui::TableSetupColumn("Accion");
        ImGui::TableHeadersRow();

        for (int i = 0; i < ctrl.datos.parametrosNormativos.tamano(); i++) {
            auto& pn = ctrl.datos.parametrosNormativos.obtener(i);
            ImGui::TableNextRow();
            ImGui::TableNextColumn(); ImGui::Text("%d", pn.idParametro ? *pn.idParametro : 0);
            ImGui::TableNextColumn();
            if (pn.codigo) {
                ImGui::TextColored(tema::TEXT_ACCENT(), "%s", to_string(*pn.codigo).c_str());
            } else {
                ImGui::Text("---");
            }
            ImGui::TableNextColumn(); ImGui::Text("%s", pn.descripcion ? pn.descripcion->c_str() : "---");
            ImGui::TableNextColumn(); ImGui::TextColored(tema::WIN_BLUE(), "%s", pn.valor ? pn.valor->c_str() : "---");
            ImGui::TableNextColumn();
            if (pn.estado && *pn.estado == "ACTIVO") {
                ImGui::PushStyleColor(ImGuiCol_Button, tema::BADGE_ACTIVE_BG());
                ImGui::PushStyleColor(ImGuiCol_Text, tema::BADGE_ACTIVE_TXT());
                ImGui::SmallButton("ACTIVO");
                ImGui::PopStyleColor(2);
            } else {
                ImGui::Text("%s", pn.estado ? pn.estado->c_str() : "---");
            }
            ImGui::TableNextColumn();
            ImGui::PushID(i);
            if (ImGui::SmallButton("Editar")) {
                abrirModalParametro(pn.idParametro ? *pn.idParametro : 0);
            }
            ImGui::PopID();
        }
        ImGui::EndTable();
    }
}

// ======================================================================
// HELPER APERTURA MODAL PARÁMETRO
// ======================================================================

void PITAApp::abrirModalParametro(int idParametro) {
    idParametroEditando = idParametro;
    mensajeModal[0] = '\0';
    errorModal = false;
    for (int i = 0; i < ctrl.datos.parametrosNormativos.tamano(); i++) {
        auto& pn = ctrl.datos.parametrosNormativos.obtener(i);
        if (pn.idParametro && *pn.idParametro == idParametro) {
            strncpy(paramCodigo, pn.codigo ? to_string(*pn.codigo).c_str() : "", sizeof(paramCodigo) - 1);
            strncpy(paramDescripcion, pn.descripcion ? pn.descripcion->c_str() : "", sizeof(paramDescripcion) - 1);
            strncpy(paramValor, pn.valor ? pn.valor->c_str() : "", sizeof(paramValor) - 1);
            break;
        }
    }
    modalParametroAbierto = true;
}

// ======================================================================
// MODAL EDITAR PARÁMETRO
// ======================================================================

void PITAApp::renderModalParametro() {
    if (modalParametroAbierto) {
        ImGui::OpenPopup("Editar Parametro Normativo");
    }

    ImVec2 center = ImGui::GetMainViewport()->GetCenter();
    ImGui::SetNextWindowPos(center, ImGuiCond_Appearing, ImVec2(0.5f, 0.5f));
    ImGui::SetNextWindowSize(ImVec2(480, 0), ImGuiCond_Always);

    if (ImGui::BeginPopupModal("Editar Parametro Normativo", &modalParametroAbierto, ImGuiWindowFlags_AlwaysAutoResize)) {
        if (strlen(mensajeModal) > 0) {
            ImGui::TextColored(errorModal ? tema::ACCENT_DANGER() : tema::ACCENT_SUCCESS(), "%s", mensajeModal);
            ImGui::Separator();
        }

        ImGui::TextColored(tema::WIN_BLUE(), "Parametro: %s", paramCodigo);
        ImGui::Spacing();
        ImGui::InputText("Descripcion", paramDescripcion, sizeof(paramDescripcion));
        ImGui::InputText("Valor Normativo *", paramValor, sizeof(paramValor));

        ImGui::Spacing();
        ImGui::Separator();

        if (ImGui::Button("Guardar Parametro", ImVec2(160, 0))) {
            try {
                ParametroNormativo act;
                act.valor = paramValor;
                act.descripcion = paramDescripcion;
                ctrl.gestorParametros->modificarParametro(idParametroEditando, act);
                ctrl.guardarDatos();
                ctrl.setMensaje("Parametro normativo actualizado y persistido.");
                modalParametroAbierto = false;
                ImGui::CloseCurrentPopup();
            } catch (const std::exception& e) {
                strncpy(mensajeModal, e.what(), sizeof(mensajeModal) - 1);
                errorModal = true;
            }
        }

        ImGui::SameLine();
        if (ImGui::Button("Cancelar", ImVec2(120, 0))) {
            modalParametroAbierto = false;
            ImGui::CloseCurrentPopup();
        }

        ImGui::EndPopup();
    }
}

} // namespace pita
