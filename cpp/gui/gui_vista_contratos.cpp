#define _CRT_SECURE_NO_WARNINGS
#include "gui_app.h"
#include "tema.h"
#include "imgui.h"

#include <cstring>
#include <string>
#include <algorithm>
#include <cctype>

namespace pita {

// ======================================================================
// HELPERS DE RESOLUCIÓN DE NOMBRES
// ======================================================================

static std::string getNombreDocente(const GUIController& ctrl, int idPersona) {
    for (int j = 0; j < ctrl.datos.personas.tamano(); j++) {
        auto& p = ctrl.datos.personas.obtener(j);
        if (p.idPersona && *p.idPersona == idPersona) {
            std::string n = (p.primerNombre ? *p.primerNombre : "") + " " + (p.primerApellido ? *p.primerApellido : "");
            std::string doc = (p.numeroDocumento ? " (" + *p.numeroDocumento + ")" : "");
            return n + doc;
        }
    }
    return "Persona #" + std::to_string(idPersona);
}

static std::string getNombreDocentePorIdProfesor(const GUIController& ctrl, int idProfesor) {
    for (int i = 0; i < ctrl.datos.profesores.tamano(); i++) {
        auto& prof = ctrl.datos.profesores.obtener(i);
        if (prof.idProfesor && *prof.idProfesor == idProfesor && prof.idPersona) {
            std::string cod = prof.codigoProfesor ? *prof.codigoProfesor : "";
            std::string nom = getNombreDocente(ctrl, *prof.idPersona);
            if (!cod.empty()) return cod + " - " + nom;
            return nom;
        }
    }
    return "Profesor #" + std::to_string(idProfesor);
}

// ======================================================================
// VISTA: CONTRATOS Y FACTORES SALARIALES
// ======================================================================

void PITAApp::renderContratos() {
    // Encabezado
    if (fuenteTitulo) ImGui::PushFont(fuenteTitulo);
    ImGui::TextColored(tema::TEXT_MAIN(), "Gestion de Contratacion y Factores Salariales");
    if (fuenteTitulo) ImGui::PopFont();

    if (fuentePequena) ImGui::PushFont(fuentePequena);
    ImGui::TextColored(tema::TEXT_MUTED(), "Regimen de Carrera (Dec. 1279/2002) y Profesores Transitorios (Acuerdo 027/2024)");
    if (fuentePequena) ImGui::PopFont();

    ImGui::Spacing();

    // Botones de acción principales en cabecera
    if (ImGui::Button("+ Registrar Contrato Docente", ImVec2(210, 32))) {
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
    ImGui::SameLine();
    ImGui::PushStyleColor(ImGuiCol_Button, ImVec4(0.0f, 0.41f, 0.22f, 1.0f));
    ImGui::PushStyleColor(ImGuiCol_ButtonHovered, ImVec4(0.0f, 0.32f, 0.17f, 1.0f));
    if (ImGui::Button("Reconocer Puntos / Productividad", ImVec2(240, 32))) {
        if (ctrl.datos.profesores.tamano() > 0) {
            recProfesorId = ctrl.datos.profesores.obtener(0).idProfesor.value_or(1);
        }
        recTipoReconocimientoIdx = 0;
        mensajeModal[0] = '\0';
        errorModal = false;
        modalReconocerPuntosAbierto = true;
    }
    ImGui::PopStyleColor(2);

    ImGui::Spacing(); ImGui::Spacing();

    // ------------------------------------------------------------------
    // KPI CARDS SUPERIORES (4 columnas proporcionales)
    // ------------------------------------------------------------------
    int totalContratos = static_cast<int>(ctrl.datos.contratos.tamano());
    int contratosActivos = 0;
    int plantaCount = 0, transitorioCount = 0, catedraCount = 0, adHonoremCount = 0;
    double totalNominaMensual = 0.0;

    for (int i = 0; i < ctrl.datos.contratos.tamano(); i++) {
        auto& c = ctrl.datos.contratos.obtener(i);
        bool activo = (c.estado && *c.estado == "ACTIVO");
        if (activo) {
            contratosActivos++;
            totalNominaMensual += c.salarioBase.value_or(0.0);

            std::string tipo = c.tipoContrato ? *c.tipoContrato : "";
            std::string mod = c.modalidadProfesor ? *c.modalidadProfesor : "";
            std::string fullType = tipo + " " + mod;
            for (auto& ch : fullType) ch = (char)toupper(ch);

            if (fullType.find("PLANTA") != std::string::npos) plantaCount++;
            else if (fullType.find("OCASIONAL") != std::string::npos) transitorioCount++;
            else if (fullType.find("CATEDRA") != std::string::npos || fullType.find("CATEDRATICO") != std::string::npos) {
                transitorioCount++;
                catedraCount++;
            }
            if (c.esAdHonorem.value_or(false) || fullType.find("AD_HONOREM") != std::string::npos) {
                adHonoremCount++;
            }
        }
    }

    double totalPuntosDocentes = 0.0;
    for (int i = 0; i < ctrl.datos.profesores.tamano(); i++) {
        auto& pr = ctrl.datos.profesores.obtener(i);
        totalPuntosDocentes += pr.puntosSalariales.value_or(0.0);
    }

    char bufActivos[32], bufSubActivos[64];
    snprintf(bufActivos, sizeof(bufActivos), "%d Activos", contratosActivos);
    snprintf(bufSubActivos, sizeof(bufSubActivos), "%d vinculaciones totales", totalContratos);

    char bufDist[48], bufSubDist[64];
    snprintf(bufDist, sizeof(bufDist), "%d Planta | %d Trans.", plantaCount, transitorioCount);
    snprintf(bufSubDist, sizeof(bufSubDist), "%d Catedra - %d Ad-Honorem", catedraCount, adHonoremCount);

    char bufPts[32], bufSubPts[64];
    snprintf(bufPts, sizeof(bufPts), "%.0f Pts", totalPuntosDocentes);
    snprintf(bufSubPts, sizeof(bufSubPts), "Valor punto: $23.924 COP");

    char bufNomina[48];
    snprintf(bufNomina, sizeof(bufNomina), "$%.0f COP", totalNominaMensual);

    if (ImGui::BeginTable("##GridKPIContratos", 4, ImGuiTableFlags_SizingStretchSame)) {
        ImGui::TableNextColumn();
        tarjetaKPI("CONTRATOS ACTIVOS", bufActivos, tema::WIN_BLUE(), bufSubActivos);

        ImGui::TableNextColumn();
        tarjetaKPI("DISTRIBUCION DOCENTE", bufDist, tema::ACCENT_INDIGO(), bufSubDist);

        ImGui::TableNextColumn();
        tarjetaKPI("PUNTOS SALARIALES TOTALES", bufPts, tema::ACCENT_WARNING(), bufSubPts);

        ImGui::TableNextColumn();
        tarjetaKPI("MASA SALARIAL MENSUAL", bufNomina, tema::ACCENT_SUCCESS(), "Asignacion basica consolidada");

        ImGui::EndTable();
    }

    ImGui::Spacing(); ImGui::Spacing();

    // ------------------------------------------------------------------
    // TABBAR PRINCIPAL DE CONTRATACIÓN
    // ------------------------------------------------------------------
    if (ImGui::BeginTabBar("##TabsContratosPrincipal")) {

        // TAB 1: CONTRATOS DOCENTES VIGENTES
        if (ImGui::BeginTabItem("Contratos Docentes Vigentes")) {
            ImGui::Spacing();

            // Barra de Filtros
            ImGui::PushStyleColor(ImGuiCol_ChildBg, tema::BG_CARD());
            ImGui::PushStyleVar(ImGuiStyleVar_ChildRounding, 8.0f);
            ImGui::BeginChild("##BarraFiltrosContratos", ImVec2(0, 48), ImGuiChildFlags_Borders);
            ImGui::SetCursorPosY(8);
            ImGui::SetCursorPosX(12);

            ImGui::AlignTextToFramePadding();
            ImGui::TextColored(tema::TEXT_MUTED(), "Filtrar:");
            ImGui::SameLine(0, 10);

            const char* opcionesModalidad[] = {
                "TODAS LAS MODALIDADES",
                "PLANTA",
                "OCASIONAL",
                "CATEDRA",
                "AD_HONOREM"
            };
            ImGui::SetNextItemWidth(190);
            ImGui::Combo("##FiltroModalidad", &conFiltroModalidadIdx, opcionesModalidad, IM_ARRAYSIZE(opcionesModalidad));
            ImGui::SameLine(0, 10);

            const char* opcionesEstado[] = {
                "TODOS LOS ESTADOS",
                "ACTIVO",
                "TERMINADO"
            };
            ImGui::SetNextItemWidth(150);
            ImGui::Combo("##FiltroEstado", &conFiltroEstadoIdx, opcionesEstado, IM_ARRAYSIZE(opcionesEstado));
            ImGui::SameLine(0, 10);

            ImGui::SetNextItemWidth(240);
            ImGui::InputTextWithHint("##BuscarContrato", "Buscar docente o No. contrato...", conFiltroBusqueda, sizeof(conFiltroBusqueda));
            ImGui::SameLine(0, 10);

            if (ImGui::Button("Restablecer", ImVec2(90, 0))) {
                conFiltroModalidadIdx = 0;
                conFiltroEstadoIdx = 0;
                conFiltroBusqueda[0] = '\0';
            }

            ImGui::EndChild();
            ImGui::PopStyleVar();
            ImGui::PopStyleColor();

            ImGui::Spacing();

            // Tabla de Contratos
            if (ImGui::BeginTable("##TablaContratosVigentes", 8,
                ImGuiTableFlags_RowBg | ImGuiTableFlags_BordersOuter | ImGuiTableFlags_BordersInnerH |
                ImGuiTableFlags_Resizable | ImGuiTableFlags_ScrollY, ImVec2(0, 0))) {

                ImGui::TableSetupColumn("No. Contrato", ImGuiTableColumnFlags_WidthFixed, 105);
                ImGui::TableSetupColumn("Docente", ImGuiTableColumnFlags_WidthStretch);
                ImGui::TableSetupColumn("Modalidad / Regimen", ImGuiTableColumnFlags_WidthFixed, 150);
                ImGui::TableSetupColumn("Dedicacion / Horas", ImGuiTableColumnFlags_WidthFixed, 125);
                ImGui::TableSetupColumn("Asignacion Basica", ImGuiTableColumnFlags_WidthFixed, 130);
                ImGui::TableSetupColumn("Vigencia", ImGuiTableColumnFlags_WidthFixed, 160);
                ImGui::TableSetupColumn("Estado", ImGuiTableColumnFlags_WidthFixed, 85);
                ImGui::TableSetupColumn("Acciones", ImGuiTableColumnFlags_WidthFixed, 90);
                ImGui::TableHeadersRow();

                std::string busq = conFiltroBusqueda;
                for (auto& ch : busq) ch = (char)tolower(ch);

                for (int i = 0; i < ctrl.datos.contratos.tamano(); i++) {
                    auto& c = ctrl.datos.contratos.obtener(i);

                    // Filtrado por estado
                    std::string est = c.estado ? *c.estado : "ACTIVO";
                    if (conFiltroEstadoIdx == 1 && est != "ACTIVO") continue;
                    if (conFiltroEstadoIdx == 2 && est == "ACTIVO") continue;

                    // Filtrado por modalidad
                    std::string tipoStr = c.tipoContrato ? *c.tipoContrato : "";
                    std::string modStr = c.modalidadProfesor ? *c.modalidadProfesor : "";
                    std::string fullType = tipoStr + " " + modStr;
                    for (auto& ch : fullType) ch = (char)toupper(ch);

                    if (conFiltroModalidadIdx == 1 && fullType.find("PLANTA") == std::string::npos) continue;
                    if (conFiltroModalidadIdx == 2 && fullType.find("OCASIONAL") == std::string::npos) continue;
                    if (conFiltroModalidadIdx == 3 && fullType.find("CATEDRA") == std::string::npos) continue;
                    if (conFiltroModalidadIdx == 4 && (!c.esAdHonorem.value_or(false) && fullType.find("AD_HONOREM") == std::string::npos)) continue;

                    // Nombre docente
                    std::string nomDocente = getNombreDocente(ctrl, c.idPersona.value_or(0));
                    std::string numContrato = c.numeroContrato ? *c.numeroContrato : ("CNT-" + std::to_string(c.idContrato.value_or(i + 1)));

                    // Filtrado por búsqueda de texto
                    if (!busq.empty()) {
                        std::string nomLower = nomDocente;
                        std::string numLower = numContrato;
                        for (auto& ch : nomLower) ch = (char)tolower(ch);
                        for (auto& ch : numLower) ch = (char)tolower(ch);
                        if (nomLower.find(busq) == std::string::npos && numLower.find(busq) == std::string::npos) {
                            continue;
                        }
                    }

                    ImGui::TableNextRow();

                    // No. Contrato
                    ImGui::TableNextColumn();
                    ImGui::TextColored(tema::ACCENT_WARNING(), "%s", numContrato.c_str());

                    // Docente
                    ImGui::TableNextColumn();
                    ImGui::Text("%s", nomDocente.c_str());

                    // Modalidad / Régimen
                    ImGui::TableNextColumn();
                    if (fullType.find("PLANTA") != std::string::npos) {
                        ImGui::TextColored(tema::WIN_BLUE(), "Planta (D.1279)");
                    } else if (fullType.find("OCASIONAL") != std::string::npos) {
                        ImGui::TextColored(tema::ACCENT_INDIGO(), "Ocasional (Ac.027)");
                    } else if (fullType.find("CATEDRA") != std::string::npos) {
                        ImGui::TextColored(tema::ACCENT_WARNING(), "Catedra (Ac.027)");
                    } else {
                        ImGui::TextColored(tema::TEXT_MUTED(), "Ad-Honorem");
                    }

                    // Dedicación / Horas
                    ImGui::TableNextColumn();
                    std::string ded = c.dedicacion ? to_string(*c.dedicacion) : "TIEMPO_COMPLETO";
                    double h = c.horasSemanales.value_or(40.0);
                    if (ded.find("COMPLETO") != std::string::npos) {
                        ImGui::Text("TC (%.0fh)", h);
                    } else if (ded.find("MEDIO") != std::string::npos) {
                        ImGui::Text("MT (%.0fh)", h);
                    } else {
                        ImGui::Text("HC (%.0fh)", h);
                    }

                    // Asignación Básica
                    ImGui::TableNextColumn();
                    char bufSal[48];
                    snprintf(bufSal, sizeof(bufSal), "$%.0f", c.salarioBase.value_or(0.0));
                    ImGui::TextColored(tema::ACCENT_SUCCESS(), "%s", bufSal);

                    // Vigencia
                    ImGui::TableNextColumn();
                    std::string fIni = c.fechaInicio ? *c.fechaInicio : "N/D";
                    std::string fFin = c.fechaFin ? *c.fechaFin : "Indefinido";
                    ImGui::Text("%s al %s", fIni.c_str(), fFin.c_str());

                    // Estado
                    ImGui::TableNextColumn();
                    if (est == "ACTIVO") {
                        ImGui::PushStyleColor(ImGuiCol_Button, tema::BADGE_ACTIVE_BG());
                        ImGui::PushStyleColor(ImGuiCol_Text, tema::BADGE_ACTIVE_TXT());
                        ImGui::SmallButton("ACTIVO");
                        ImGui::PopStyleColor(2);
                    } else {
                        ImGui::TextColored(tema::TEXT_MUTED(), "%s", est.c_str());
                    }

                    // Acciones
                    ImGui::TableNextColumn();
                    ImGui::PushID(i);
                    if (est == "ACTIVO") {
                        ImGui::PushStyleColor(ImGuiCol_Button, tema::ACCENT_DANGER());
                        ImGui::PushStyleColor(ImGuiCol_ButtonHovered, tema::ACCENT_DANGER_H());
                        if (ImGui::SmallButton("Terminar")) {
                            idContratoTerminando = c.idContrato ? *c.idContrato : 0;
                            mensajeModal[0] = '\0';
                            errorModal = false;
                            modalTerminarContratoAbierto = true;
                        }
                        ImGui::PopStyleColor(2);
                    } else {
                        ImGui::TextDisabled("Cerrado");
                    }
                    ImGui::PopID();
                }
                ImGui::EndTable();
            }
            ImGui::EndTabItem();
        }

        // TAB 2: FACTORES SALARIALES Y ESCALAFÓN (DEC. 1279)
        if (ImGui::BeginTabItem("Factores Salariales y Escalafon (Dec. 1279)")) {
            ImGui::Spacing();

            if (ImGui::BeginTabBar("##SubTabsFactores")) {

                // Sub-tab A: Factores Salariales Reconocidos
                if (ImGui::BeginTabItem("Factores Salariales Reconocidos")) {
                    ImGui::Spacing();
                    if (ctrl.datos.factoresSalariales.tamano() == 0) {
                        ImGui::TextColored(tema::TEXT_MUTED(), "No hay factores salariales registrados.");
                    } else {
                        if (ImGui::BeginTable("##TablaFactoresSalariales", 7,
                            ImGuiTableFlags_RowBg | ImGuiTableFlags_BordersOuter | ImGuiTableFlags_BordersInnerH |
                            ImGuiTableFlags_Resizable | ImGuiTableFlags_ScrollY, ImVec2(0, 0))) {

                            ImGui::TableSetupColumn("Docente", ImGuiTableColumnFlags_WidthStretch);
                            ImGui::TableSetupColumn("Tipo de Factor", ImGuiTableColumnFlags_WidthFixed, 150);
                            ImGui::TableSetupColumn("Concepto / Denominacion", ImGuiTableColumnFlags_WidthStretch);
                            ImGui::TableSetupColumn("Puntos Reconocidos", ImGuiTableColumnFlags_WidthFixed, 130);
                            ImGui::TableSetupColumn("Acto Administrativo", ImGuiTableColumnFlags_WidthFixed, 140);
                            ImGui::TableSetupColumn("Fecha Reconocimiento", ImGuiTableColumnFlags_WidthFixed, 130);
                            ImGui::TableSetupColumn("Estado", ImGuiTableColumnFlags_WidthFixed, 90);
                            ImGui::TableHeadersRow();

                            for (int i = 0; i < ctrl.datos.factoresSalariales.tamano(); i++) {
                                auto& f = ctrl.datos.factoresSalariales.obtener(i);
                                ImGui::TableNextRow();

                                ImGui::TableNextColumn();
                                ImGui::Text("%s", getNombreDocentePorIdProfesor(ctrl, f.idProfesor.value_or(0)).c_str());

                                ImGui::TableNextColumn();
                                std::string tf = f.tipoFactor ? to_string(*f.tipoFactor) : "TITULO_ACADEMICO";
                                ImGui::Text("%s", tf.c_str());

                                ImGui::TableNextColumn();
                                ImGui::Text("%s", f.nombre ? f.nombre->c_str() : "Factor");

                                ImGui::TableNextColumn();
                                double pts = f.puntosReconocidos.value_or(f.puntosAprobados.value_or(0.0));
                                ImGui::TextColored(tema::ACCENT_WARNING(), "+%.0f pts", pts);

                                ImGui::TableNextColumn();
                                ImGui::Text("%s", f.actoAdministrativo ? f.actoAdministrativo->c_str() : "N/A");

                                ImGui::TableNextColumn();
                                ImGui::Text("%s", f.fechaReconocimiento ? f.fechaReconocimiento->c_str() : "N/D");

                                ImGui::TableNextColumn();
                                ImGui::PushStyleColor(ImGuiCol_Button, tema::BADGE_ACTIVE_BG());
                                ImGui::PushStyleColor(ImGuiCol_Text, tema::BADGE_ACTIVE_TXT());
                                ImGui::SmallButton("APROBADO");
                                ImGui::PopStyleColor(2);
                            }
                            ImGui::EndTable();
                        }
                    }
                    ImGui::EndTabItem();
                }

                // Sub-tab B: Producción Intelectual / Obras
                if (ImGui::BeginTabItem("Produccion Intelectual / Obras")) {
                    ImGui::Spacing();
                    if (ctrl.datos.produccionesAcademicas.tamano() == 0) {
                        ImGui::TextColored(tema::TEXT_MUTED(), "No hay produccion intelectual registrada bajo Decreto 1279.");
                    } else {
                        if (ImGui::BeginTable("##TablaProduccionesAcademicas", 7,
                            ImGuiTableFlags_RowBg | ImGuiTableFlags_BordersOuter | ImGuiTableFlags_BordersInnerH |
                            ImGuiTableFlags_Resizable | ImGuiTableFlags_ScrollY, ImVec2(0, 0))) {

                            ImGui::TableSetupColumn("Docente", ImGuiTableColumnFlags_WidthStretch);
                            ImGui::TableSetupColumn("Tipo de Obra", ImGuiTableColumnFlags_WidthFixed, 130);
                            ImGui::TableSetupColumn("Titulo de la Produccion", ImGuiTableColumnFlags_WidthStretch);
                            ImGui::TableSetupColumn("Medio / Editorial", ImGuiTableColumnFlags_WidthFixed, 150);
                            ImGui::TableSetupColumn("Autores / Coautoria", ImGuiTableColumnFlags_WidthFixed, 130);
                            ImGui::TableSetupColumn("Puntos Docente", ImGuiTableColumnFlags_WidthFixed, 120);
                            ImGui::TableSetupColumn("Estado", ImGuiTableColumnFlags_WidthFixed, 90);
                            ImGui::TableHeadersRow();

                            for (int i = 0; i < ctrl.datos.produccionesAcademicas.tamano(); i++) {
                                auto& p = ctrl.datos.produccionesAcademicas.obtener(i);
                                ImGui::TableNextRow();

                                ImGui::TableNextColumn();
                                ImGui::Text("%s", getNombreDocentePorIdProfesor(ctrl, p.idProfesor.value_or(0)).c_str());

                                ImGui::TableNextColumn();
                                ImGui::Text("%s", p.tipoProduccion ? p.tipoProduccion->c_str() : "ARTICULO");

                                ImGui::TableNextColumn();
                                ImGui::TextColored(tema::WIN_BLUE(), "%s", p.titulo ? p.titulo->c_str() : "Obra");

                                ImGui::TableNextColumn();
                                ImGui::Text("%s", p.entidadPublicadora ? p.entidadPublicadora->c_str() : "N/A");

                                ImGui::TableNextColumn();
                                int nAut = p.numeroAutores.value_or(1);
                                double coaut = p.factorCoautoria.value_or(1.0);
                                ImGui::Text("%d aut. (%.0f%%)", nAut, coaut * 100.0);

                                ImGui::TableNextColumn();
                                double pts = p.puntosReconocidos.value_or(p.puntosSolicitados.value_or(0.0));
                                ImGui::TextColored(tema::ACCENT_WARNING(), "+%.1f pts", pts);

                                ImGui::TableNextColumn();
                                ImGui::PushStyleColor(ImGuiCol_Button, tema::BADGE_ACTIVE_BG());
                                ImGui::PushStyleColor(ImGuiCol_Text, tema::BADGE_ACTIVE_TXT());
                                ImGui::SmallButton("VALIDADO");
                                ImGui::PopStyleColor(2);
                            }
                            ImGui::EndTable();
                        }
                    }
                    ImGui::EndTabItem();
                }

                ImGui::EndTabBar();
            }
            ImGui::EndTabItem();
        }

        ImGui::EndTabBar();
    }
}

// ======================================================================
// MODAL: NUEVO CONTRATO DOCENTE
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
                previewProf = getNombreDocente(ctrl, conPersonaId);
                break;
            }
        }
        if (ImGui::BeginCombo("Docente *", previewProf.c_str())) {
            for (int i = 0; i < ctrl.datos.profesores.tamano(); i++) {
                auto& pr = ctrl.datos.profesores.obtener(i);
                bool isSelected = (pr.idPersona && *pr.idPersona == conPersonaId);
                std::string label = getNombreDocente(ctrl, pr.idPersona.value_or(0));
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

// ======================================================================
// MODAL: TERMINAR CONTRATO
// ======================================================================

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

// ======================================================================
// MODAL: RECONOCER PUNTOS / PRODUCTIVIDAD (DEC. 1279)
// ======================================================================

void PITAApp::renderModalReconocerPuntos() {
    if (modalReconocerPuntosAbierto) {
        ImGui::OpenPopup("Reconocer Factores y Productividad Academica");
    }

    ImVec2 center = ImGui::GetMainViewport()->GetCenter();
    ImGui::SetNextWindowPos(center, ImGuiCond_Appearing, ImVec2(0.5f, 0.5f));
    ImGui::SetNextWindowSize(ImVec2(620, 0), ImGuiCond_Always);

    if (ImGui::BeginPopupModal("Reconocer Factores y Productividad Academica", &modalReconocerPuntosAbierto, ImGuiWindowFlags_AlwaysAutoResize)) {
        if (strlen(mensajeModal) > 0) {
            ImGui::TextColored(errorModal ? tema::ACCENT_DANGER() : tema::ACCENT_SUCCESS(), "%s", mensajeModal);
            ImGui::Separator();
        }

        ImGui::TextColored(tema::TEXT_MAIN(), "Comite de Puntaje Salarial (Decreto 1279 de 2002)");
        ImGui::TextColored(tema::TEXT_MUTED(), "Reconocimiento oficial de puntos salariales por titulos, escalafon o produccion intelectual.");
        ImGui::Spacing();

        // Selector Docente Beneficiario
        std::string previewProf = "Seleccione Docente";
        for (int i = 0; i < ctrl.datos.profesores.tamano(); i++) {
            auto& pr = ctrl.datos.profesores.obtener(i);
            if (pr.idProfesor && *pr.idProfesor == recProfesorId) {
                previewProf = getNombreDocentePorIdProfesor(ctrl, recProfesorId) + " [" + std::to_string((int)pr.puntosSalariales.value_or(0.0)) + " pts actual]";
                break;
            }
        }

        if (ImGui::BeginCombo("Docente Beneficiario *", previewProf.c_str())) {
            for (int i = 0; i < ctrl.datos.profesores.tamano(); i++) {
                auto& pr = ctrl.datos.profesores.obtener(i);
                int pId = pr.idProfesor.value_or(i + 1);
                bool isSelected = (pId == recProfesorId);
                std::string label = getNombreDocentePorIdProfesor(ctrl, pId) + " [" + std::to_string((int)pr.puntosSalariales.value_or(0.0)) + " pts]";
                if (ImGui::Selectable(label.c_str(), isSelected)) {
                    recProfesorId = pId;
                }
                if (isSelected) ImGui::SetItemDefaultFocus();
            }
            ImGui::EndCombo();
        }

        ImGui::Spacing();

        // SubTabs de Reconocimiento
        if (ImGui::BeginTabBar("##TabsReconocerPuntos")) {

            // Tab Factores Salariales
            if (ImGui::BeginTabItem("Titulos y Escalafon")) {
                recTipoReconocimientoIdx = 0;

                const char* tiposFac[] = {
                    "TITULO_ACADEMICO",
                    "CATEGORIA_DOCENTE",
                    "EXPERIENCIA_CALIFICADA",
                    "CARGO_DIRECCION_ACADEMICA"
                };
                ImGui::Combo("Tipo de Factor Salarial *", &recTipoFactorIdx, tiposFac, IM_ARRAYSIZE(tiposFac));

                ImGui::InputText("Concepto / Denominacion *", recNombreFactor, sizeof(recNombreFactor));
                ImGui::InputDouble("Puntos Salariales a Asignar (+)", &recPuntosFactor, 1.0, 10.0, "%.1f");
                ImGui::InputText("Acto Administrativo *", recActoAdmin, sizeof(recActoAdmin));
                ImGui::InputText("Fecha Reconocimiento (YYYY-MM-DD)", recFechaReconocimiento, sizeof(recFechaReconocimiento));

                ImGui::EndTabItem();
            }

            // Tab Producción Intelectual
            if (ImGui::BeginTabItem("Produccion Intelectual")) {
                recTipoReconocimientoIdx = 1;

                const char* tiposProd[] = {
                    "ARTICULO",
                    "LIBRO",
                    "CAPITULO_LIBRO",
                    "PATENTE",
                    "SOFTWARE_REGISTRADO"
                };
                ImGui::Combo("Tipo de Obra / Producto *", &recTipoProduccionIdx, tiposProd, IM_ARRAYSIZE(tiposProd));

                ImGui::InputText("Titulo de la Obra *", recTituloProduccion, sizeof(recTituloProduccion));
                ImGui::InputText("Editorial / Medio de Publicacion", recEditorial, sizeof(recEditorial));
                ImGui::InputInt("Numero de Autores", &recNumAutores);
                if (recNumAutores < 1) recNumAutores = 1;

                double factorCoautoria = (recNumAutores == 1) ? 1.0 : (recNumAutores == 2 ? 0.8 : (recNumAutores == 3 ? 0.6 : 0.4));
                ImGui::TextColored(tema::TEXT_MUTED(), "Factor de Coautoria aplicado: %.0f%%", factorCoautoria * 100.0);

                ImGui::InputDouble("Puntos para el Docente (+)", &recPuntosProduccion, 1.0, 5.0, "%.1f");

                ImGui::EndTabItem();
            }

            ImGui::EndTabBar();
        }

        ImGui::Spacing();
        ImGui::Separator();

        if (ImGui::Button("Asignar Puntos", ImVec2(160, 32))) {
            try {
                // Actualizar puntos en el profesor
                Profesor* profTarget = nullptr;
                for (int i = 0; i < ctrl.datos.profesores.tamano(); i++) {
                    auto& pr = ctrl.datos.profesores.obtener(i);
                    if (pr.idProfesor && *pr.idProfesor == recProfesorId) {
                        profTarget = &pr;
                        break;
                    }
                }

                if (!profTarget) {
                    throw std::runtime_error("Profesor no encontrado para la asignacion de puntos.");
                }

                if (recTipoReconocimientoIdx == 0) {
                    // Factor Salarial
                    FactorSalarial fs;
                    fs.idFactor = static_cast<int>(ctrl.datos.factoresSalariales.tamano()) + 1;
                    fs.idProfesor = recProfesorId;
                    fs.nombre = recNombreFactor;
                    fs.tipoFactor = (recTipoFactorIdx == 0) ? TipoFactor::TITULO_ACADEMICO :
                                    (recTipoFactorIdx == 1) ? TipoFactor::CATEGORIA_DOCENTE :
                                    (recTipoFactorIdx == 2) ? TipoFactor::EXPERIENCIA :
                                                              TipoFactor::DIRECCION_ACADEMICO_ADMINISTRATIVA;
                    fs.puntosReconocidos = recPuntosFactor;
                    fs.puntosAprobados = recPuntosFactor;
                    fs.actoAdministrativo = recActoAdmin;
                    fs.fechaReconocimiento = recFechaReconocimiento;
                    fs.estado = "APROBADO";

                    ctrl.datos.factoresSalariales.push_back(fs);
                    double ptsActuales = profTarget->puntosSalariales.value_or(0.0);
                    profTarget->puntosSalariales = ptsActuales + recPuntosFactor;
                } else {
                    // Producción Intelectual
                    const char* tiposProd[] = { "ARTICULO", "LIBRO", "CAPITULO_LIBRO", "PATENTE", "SOFTWARE_REGISTRADO" };
                    ProduccionAcademica pa;
                    pa.idProduccion = static_cast<int>(ctrl.datos.produccionesAcademicas.tamano()) + 1;
                    pa.idProfesor = recProfesorId;
                    pa.tipoProduccion = tiposProd[recTipoProduccionIdx];
                    pa.titulo = recTituloProduccion;
                    pa.entidadPublicadora = recEditorial;
                    pa.numeroAutores = recNumAutores;
                    pa.factorCoautoria = (recNumAutores == 1) ? 1.0 : (recNumAutores == 2 ? 0.8 : (recNumAutores == 3 ? 0.6 : 0.4));
                    pa.puntosReconocidos = recPuntosProduccion;
                    pa.estadoValidacion = "VALIDADO";

                    ctrl.datos.produccionesAcademicas.push_back(pa);
                    double ptsActuales = profTarget->puntosSalariales.value_or(0.0);
                    profTarget->puntosSalariales = ptsActuales + recPuntosProduccion;
                }

                ctrl.guardarDatos();
                ctrl.setMensaje("Puntos salariales y factores reconocidos formalmente.");
                modalReconocerPuntosAbierto = false;
                ImGui::CloseCurrentPopup();
            } catch (const std::exception& e) {
                strncpy(mensajeModal, e.what(), sizeof(mensajeModal) - 1);
                errorModal = true;
            }
        }

        ImGui::SameLine();
        if (ImGui::Button("Cancelar", ImVec2(120, 32))) {
            modalReconocerPuntosAbierto = false;
            ImGui::CloseCurrentPopup();
        }

        ImGui::EndPopup();
    }
}

} // namespace pita
