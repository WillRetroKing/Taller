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
    ImGui::TextColored(tema::TEXT_MAIN(), "Parametros Normativos & Persistencia");
    if (fuenteTitulo) ImGui::PopFont();

    if (fuentePequena) ImGui::PushFont(fuentePequena);
    ImGui::TextColored(tema::TEXT_MUTED(), "Parametros legales y normativos del sistema (SMMLV, tasas, porcentajes de ley y control de almacenamiento)");
    if (fuentePequena) ImGui::PopFont();

    ImGui::Spacing();

    // Botones de persistencia en header
    if (ImGui::Button("Guardar en Disco (datos/)", ImVec2(200, 32))) {
        ctrl.guardarDatos();
        ctrl.setMensaje("Todos los datos persistidos en disco exitosamente.");
    }
    ImGui::SameLine();
    if (ImGui::Button("Recargar desde Disco", ImVec2(180, 32))) {
        ctrl.cargarDatos();
        ctrl.inicializarGestores();
        ctrl.setMensaje("Datos recargados desde disco correctamente.");
    }

    ImGui::Spacing();
    ImGui::Separator();
    ImGui::Spacing();

    // Filtro de búsqueda
    static char busqParam[64] = "";
    ImGui::SetNextItemWidth(350);
    ImGui::InputTextWithHint("##BuscarParametro", "Buscar por codigo o descripcion...", busqParam, sizeof(busqParam));
    ImGui::SameLine();
    if (ImGui::Button("Limpiar", ImVec2(80, 0))) {
        busqParam[0] = '\0';
    }

    ImGui::Spacing();

    if (ImGui::BeginTable("##TablaParametros", 7,
        ImGuiTableFlags_RowBg | ImGuiTableFlags_BordersOuter | ImGuiTableFlags_BordersInnerH |
        ImGuiTableFlags_Resizable | ImGuiTableFlags_ScrollY, ImVec2(0, 0))) {

        ImGui::TableSetupColumn("ID", ImGuiTableColumnFlags_WidthFixed, 45);
        ImGui::TableSetupColumn("Codigo Parametro", ImGuiTableColumnFlags_WidthFixed, 230);
        ImGui::TableSetupColumn("Descripcion", ImGuiTableColumnFlags_WidthStretch);
        ImGui::TableSetupColumn("Valor Vigente", ImGuiTableColumnFlags_WidthFixed, 150);
        ImGui::TableSetupColumn("Unidad", ImGuiTableColumnFlags_WidthFixed, 80);
        ImGui::TableSetupColumn("Estado", ImGuiTableColumnFlags_WidthFixed, 80);
        ImGui::TableSetupColumn("Accion", ImGuiTableColumnFlags_WidthFixed, 80);
        ImGui::TableHeadersRow();

        std::string filtro = busqParam;
        for (auto& c : filtro) c = (char)tolower(c);

        for (int i = 0; i < ctrl.datos.parametrosNormativos.tamano(); i++) {
            auto& pn = ctrl.datos.parametrosNormativos.obtener(i);
            std::string codStr = pn.codigo ? to_string(*pn.codigo) : "";
            std::string descStr = pn.descripcion ? *pn.descripcion : "";

            std::string searchTarget = codStr + " " + descStr;
            for (auto& c : searchTarget) c = (char)tolower(c);

            if (!filtro.empty() && searchTarget.find(filtro) == std::string::npos) {
                continue;
            }

            ImGui::TableNextRow();
            ImGui::TableNextColumn(); ImGui::Text("%d", pn.idParametro ? *pn.idParametro : 0);
            ImGui::TableNextColumn();
            ImGui::TextColored(tema::TEXT_ACCENT(), "%s", codStr.c_str());

            ImGui::TableNextColumn(); ImGui::Text("%s", descStr.c_str());

            // Formateo inteligente del valor
            ImGui::TableNextColumn();
            std::string valStr = pn.valor ? *pn.valor : "0";
            std::string unidadStr = "---";

            if (codStr.find("SALARIO") != std::string::npos ||
                codStr.find("PUNTO") != std::string::npos ||
                codStr.find("TRANSPORTE") != std::string::npos ||
                codStr.find("CATEDRA") != std::string::npos ||
                codStr.find("TOPE") != std::string::npos ||
                codStr.find("BASE_MINIMA") != std::string::npos) {
                unidadStr = "COP";
                try {
                    double numVal = std::stod(valStr);
                    char bufM[64];
                    snprintf(bufM, sizeof(bufM), "$%.0f COP", numVal);
                    ImGui::TextColored(tema::WIN_BLUE(), "%s", bufM);
                } catch (...) {
                    ImGui::TextColored(tema::WIN_BLUE(), "%s", valStr.c_str());
                }
            } else if (codStr.find("PORCENTAJE") != std::string::npos) {
                unidadStr = "%";
                try {
                    double numVal = std::stod(valStr);
                    if (numVal <= 1.0 && numVal > 0.0) {
                        numVal *= 100.0;
                    }
                    char bufP[64];
                    snprintf(bufP, sizeof(bufP), "%.2f %%", numVal);
                    ImGui::TextColored(tema::ACCENT_WARNING(), "%s", bufP);
                } catch (...) {
                    ImGui::TextColored(tema::ACCENT_WARNING(), "%s", valStr.c_str());
                }
            } else {
                ImGui::TextColored(tema::TEXT_MAIN(), "%s", valStr.c_str());
            }

            ImGui::TableNextColumn(); ImGui::Text("%s", unidadStr.c_str());

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
