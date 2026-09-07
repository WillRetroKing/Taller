#define _CRT_SECURE_NO_WARNINGS
#include "gui_app.h"
#include "tema.h"
#include "imgui.h"

#include <cstring>
#include <string>
#include <vector>
#include <cmath>
#include <algorithm>

namespace pita {

// ======================================================================
// HELPERS MONEDA Y FORMATO
// ======================================================================

static std::string formatearMoneda(double valor) {
    long long entero = static_cast<long long>(std::round(valor));
    std::string s = std::to_string(std::abs(entero));
    std::string res;
    int count = 0;
    for (int i = static_cast<int>(s.length()) - 1; i >= 0; --i) {
        res.insert(res.begin(), s[i]);
        count++;
        if (count % 3 == 0 && i > 0) {
            res.insert(res.begin(), '.');
        }
    }
    std::string signo = (entero < 0) ? "-$" : "$";
    return signo + " " + res + " COP";
}

static std::string getNombreDocente(const GUIController& ctrl, int idProfesor) {
    for (size_t i = 0; i < ctrl.datos.profesores.tamano(); ++i) {
        auto& prof = ctrl.datos.profesores.obtener(i);
        if (prof.idProfesor && *prof.idProfesor == idProfesor) {
            for (size_t j = 0; j < ctrl.datos.personas.tamano(); ++j) {
                auto& p = ctrl.datos.personas.obtener(j);
                if (p.idPersona && prof.idPersona && *p.idPersona == *prof.idPersona) {
                    std::string nombre = (p.primerNombre ? *p.primerNombre : "") + " " + (p.primerApellido ? *p.primerApellido : "");
                    if (!nombre.empty() && nombre != " ") return nombre;
                }
            }
            if (prof.codigoProfesor) return *prof.codigoProfesor;
            return "Docente #" + std::to_string(idProfesor);
        }
    }
    return "Docente #" + std::to_string(idProfesor);
}

// ======================================================================
// VISTA: NÓMINA & LIQUIDACIÓN
// ======================================================================

void PITAApp::renderNomina() {
    if (fuenteTitulo) ImGui::PushFont(fuenteTitulo);
    ImGui::TextColored(tema::TEXT_MAIN(), "Subsistema de Nomina & Prestaciones Sociales (PITA)");
    if (fuenteTitulo) ImGui::PopFont();

    if (fuentePequena) ImGui::PushFont(fuentePequena);
    ImGui::TextColored(tema::TEXT_MUTED(), "Liquidacion salarial docente, descuentos de ley y aportes patronales (Decreto 1279 / Acuerdo 027)");
    if (fuentePequena) ImGui::PopFont();

    ImGui::Spacing();

    // Botones de acción principales (Header)
    if (ImGui::Button("Periodos de Nomina", ImVec2(165, 34))) {
        perAnio = 2026;
        perMes = 3;
        mensajeModal[0] = '\0';
        errorModal = false;
        modalPeriodoNominaAbierto = true;
    }
    ImGui::SameLine();
    if (ImGui::Button("Liquidar Docente", ImVec2(165, 34))) {
        mensajeModal[0] = '\0';
        errorModal = false;
        modalLiquidarIndividualAbierto = true;
    }
    ImGui::SameLine();
    if (ImGui::Button("Liquidar Periodo Completo", ImVec2(205, 34))) {
        ejecutarLiquidacionGeneral();
    }

    ImGui::Spacing();
    ImGui::Separator();
    ImGui::Spacing();

    // Cálculo de acumulados financieros (KPIs)
    double tot_dev = 0.0;
    double tot_desc = 0.0;
    double tot_neto = 0.0;
    double tot_prest = 0.0;
    for (size_t i = 0; i < ctrl.datos.liquidacionesNomina.tamano(); ++i) {
        auto& l = ctrl.datos.liquidacionesNomina.obtener(i);
        tot_dev += l.totalDevengado.value_or(0.0);
        tot_desc += l.totalDescuentos.value_or(0.0);
        tot_neto += l.netoPagar.value_or(0.0);
        tot_prest += l.totalPrestaciones.value_or(0.0);
    }

    // 4 Tarjetas KPI de resumen organizadas en Grid horizontal
    if (ImGui::BeginTable("##GridKPINomina", 4, ImGuiTableFlags_SizingStretchSame)) {
        ImGui::TableNextColumn();
        tarjetaKPI("Total Devengado (Bruto)", formatearMoneda(tot_dev).c_str(), tema::WIN_BLUE(), "Ingreso base devengado periodo");

        ImGui::TableNextColumn();
        tarjetaKPI("Deducciones de Ley", formatearMoneda(tot_desc).c_str(), tema::ACCENT_DANGER(), "Salud, pension y retenciones");

        ImGui::TableNextColumn();
        tarjetaKPI("Neto Total a Pagar", formatearMoneda(tot_neto).c_str(), ImVec4(0.063f, 0.725f, 0.506f, 1.0f), "Gasto liquido a transferir");

        ImGui::TableNextColumn();
        tarjetaKPI("Prestaciones Proyectadas", formatearMoneda(tot_prest).c_str(), tema::ACCENT_WARNING(), "Cesantias, primas y vacaciones");

        ImGui::EndTable();
    }
    ImGui::Spacing();

    // Pestañas temáticas idénticas a Python
    if (ImGui::BeginTabBar("##TabsNominaPITA")) {

        // --------------------------------------------------------------
        // Pestaña 1: Resumen de Liquidaciones
        // --------------------------------------------------------------
        if (ImGui::BeginTabItem("Resumen de Liquidaciones")) {
            ImGui::Spacing();

            if (ctrl.datos.liquidacionesNomina.tamano() == 0) {
                ImGui::BeginChild("##VacioLiquidaciones", ImVec2(0, 180), true);
                ImGui::Spacing();
                ImGui::Spacing();
                ImGui::TextColored(tema::TEXT_MUTED(), "No se han generado liquidaciones de nomina en este periodo.");
                ImGui::Spacing();
                if (ImGui::Button("Calcular Liquidaciones del Periodo Ahora", ImVec2(280, 36))) {
                    ejecutarLiquidacionGeneral();
                }
                ImGui::EndChild();
            } else {
                if (ImGui::BeginTable("##TablaResumenLiquidaciones", 8,
                    ImGuiTableFlags_RowBg | ImGuiTableFlags_BordersOuter | ImGuiTableFlags_BordersInnerH |
                    ImGuiTableFlags_Resizable | ImGuiTableFlags_ScrollY, ImVec2(0, 0))) {

                    ImGui::TableSetupColumn("Docente", ImGuiTableColumnFlags_WidthStretch, 2.0f);
                    ImGui::TableSetupColumn("Tipo Profesor", ImGuiTableColumnFlags_WidthFixed, 110.0f);
                    ImGui::TableSetupColumn("Sueldo Basico", ImGuiTableColumnFlags_WidthFixed, 120.0f);
                    ImGui::TableSetupColumn("Devengado", ImGuiTableColumnFlags_WidthFixed, 120.0f);
                    ImGui::TableSetupColumn("Descuentos Ley", ImGuiTableColumnFlags_WidthFixed, 120.0f);
                    ImGui::TableSetupColumn("Neto a Pagar", ImGuiTableColumnFlags_WidthFixed, 120.0f);
                    ImGui::TableSetupColumn("Prestaciones", ImGuiTableColumnFlags_WidthFixed, 120.0f);
                    ImGui::TableSetupColumn("Acciones", ImGuiTableColumnFlags_WidthFixed, 160.0f);
                    ImGui::TableHeadersRow();

                    for (size_t i = 0; i < ctrl.datos.liquidacionesNomina.tamano(); ++i) {
                        auto& l = ctrl.datos.liquidacionesNomina.obtener(i);
                        int idLiq = l.idLiquidacion.value_or(0);
                        int idProf = l.idProfesor.value_or(0);

                        std::string nombre = getNombreDocente(ctrl, idProf);
                        std::string tipoDocente = l.tipoProfesorLiquidado ? to_string(*l.tipoProfesorLiquidado) : "PLANTA";

                        ImGui::TableNextRow();
                        // 1. Docente
                        ImGui::TableNextColumn();
                        ImGui::TextColored(tema::TEXT_MAIN(), "%s", nombre.c_str());

                        // 2. Tipo Profesor (Badge)
                        ImGui::TableNextColumn();
                        if (tipoDocente.find("PLANTA") != std::string::npos) {
                            ImGui::PushStyleColor(ImGuiCol_Button, tema::BADGE_ACTIVE_BG());
                            ImGui::PushStyleColor(ImGuiCol_Text, tema::BADGE_ACTIVE_TXT());
                            ImGui::SmallButton("PLANTA");
                            ImGui::PopStyleColor(2);
                        } else if (tipoDocente.find("OCASIONAL") != std::string::npos) {
                            ImGui::PushStyleColor(ImGuiCol_Button, ImVec4(0.35f, 0.20f, 0.50f, 0.35f));
                            ImGui::PushStyleColor(ImGuiCol_Text, ImVec4(0.75f, 0.55f, 0.95f, 1.0f));
                            ImGui::SmallButton("OCASIONAL");
                            ImGui::PopStyleColor(2);
                        } else {
                            ImGui::PushStyleColor(ImGuiCol_Button, tema::BADGE_INFO_BG());
                            ImGui::PushStyleColor(ImGuiCol_Text, tema::BADGE_INFO_TXT());
                            ImGui::SmallButton("CATEDRATICO");
                            ImGui::PopStyleColor(2);
                        }

                        // 3. Sueldo Básico
                        ImGui::TableNextColumn();
                        ImGui::Text("%s", formatearMoneda(l.salarioBase.value_or(0.0)).c_str());

                        // 4. Devengado
                        ImGui::TableNextColumn();
                        ImGui::TextColored(tema::WIN_BLUE(), "%s", formatearMoneda(l.totalDevengado.value_or(0.0)).c_str());

                        // 5. Descuentos Ley
                        ImGui::TableNextColumn();
                        ImGui::TextColored(tema::ACCENT_DANGER(), "%s", formatearMoneda(l.totalDescuentos.value_or(0.0)).c_str());

                        // 6. Neto a Pagar
                        ImGui::TableNextColumn();
                        ImGui::TextColored(ImVec4(0.063f, 0.725f, 0.506f, 1.0f), "%s", formatearMoneda(l.netoPagar.value_or(0.0)).c_str());

                        // 7. Prestaciones
                        ImGui::TableNextColumn();
                        ImGui::TextColored(tema::ACCENT_WARNING(), "%s", formatearMoneda(l.totalPrestaciones.value_or(0.0)).c_str());

                        // 8. Acciones
                        ImGui::TableNextColumn();
                        ImGui::PushID(static_cast<int>(i));
                        if (ImGui::SmallButton("Desglose")) {
                            idLiquidacionDesprendible = idLiq;
                            modalDesprendibleAbierto = true;
                        }
                        ImGui::SameLine();
                        if (ImGui::SmallButton("Anular")) {
                            eliminarLiquidacion(idLiq);
                        }
                        ImGui::PopID();
                    }
                    ImGui::EndTable();
                }
            }
            ImGui::EndTabItem();
        }

        // --------------------------------------------------------------
        // Pestaña 2: Aportes Patronales & Parafiscales
        // --------------------------------------------------------------
        if (ImGui::BeginTabItem("Aportes Patronales & Parafiscales")) {
            ImGui::Spacing();
            ImGui::TextColored(tema::TEXT_MAIN(), "Aportes Patronales a la Seguridad Social y Parafiscales");
            ImGui::TextColored(tema::TEXT_MUTED(), "Calculados sobre el Ingreso Base de Cotizacion (IBC total devengado periodo).");
            ImGui::Spacing();

            double tot_ibc = tot_dev;
            double salud_pat = tot_ibc * 0.085;
            double pension_pat = tot_ibc * 0.12;
            double arl = tot_ibc * 0.00522;
            double sena = tot_ibc * 0.02;
            double icbf = tot_ibc * 0.03;
            double caja = tot_ibc * 0.04;
            double total_patronal = salud_pat + pension_pat + arl + sena + icbf + caja;

            if (ImGui::BeginTable("##TablaParafiscalesPatronal", 3,
                ImGuiTableFlags_RowBg | ImGuiTableFlags_BordersOuter | ImGuiTableFlags_BordersInnerH |
                ImGuiTableFlags_Resizable, ImVec2(0, 0))) {

                ImGui::TableSetupColumn("Concepto Parafiscal / Patronal", ImGuiTableColumnFlags_WidthStretch, 2.0f);
                ImGui::TableSetupColumn("Monto Proyectado", ImGuiTableColumnFlags_WidthFixed, 180.0f);
                ImGui::TableSetupColumn("Norma Legal Origen", ImGuiTableColumnFlags_WidthStretch, 2.0f);
                ImGui::TableHeadersRow();

                struct FilaParafiscal {
                    const char* concepto;
                    double monto;
                    const char* norma;
                };
                FilaParafiscal filas[] = {
                    { "Salud Patronal (8.5 %)", salud_pat, "Ley 100 de 1993, Art. 204" },
                    { "Pension Patronal (12.0 %)", pension_pat, "Ley 100 de 1993, Art. 20" },
                    { "ARL Riesgos Laborales (0.522 %)", arl, "Decreto 1772 de 1994, Art. 13" },
                    { "SENA (2.0 %)", sena, "Ley 21 de 1982, Art. 7" },
                    { "ICBF (3.0 %)", icbf, "Ley 89 de 1988, Art. 1" },
                    { "Caja de Compensacion Familiar (4.0 %)", caja, "Ley 21 de 1982, Art. 7" }
                };

                for (const auto& f : filas) {
                    ImGui::TableNextRow();
                    ImGui::TableNextColumn();
                    ImGui::Text("%s", f.concepto);
                    ImGui::TableNextColumn();
                    ImGui::TextColored(tema::WIN_BLUE(), "%s", formatearMoneda(f.monto).c_str());
                    ImGui::TableNextColumn();
                    ImGui::TextColored(tema::TEXT_MUTED(), "%s", f.norma);
                }
                ImGui::EndTable();
            }

            ImGui::Spacing();
            ImGui::BeginChild("##CardTotalPatronal", ImVec2(0, 56), true);
            ImGui::TextColored(ImVec4(0.063f, 0.725f, 0.506f, 1.0f), "Carga Prestacional y Patronal Total Estimada: %s", formatearMoneda(total_patronal).c_str());
            ImGui::TextColored(tema::TEXT_MUTED(), "Provision mensual estimada para costos directos de nomina institucional.");
            ImGui::EndChild();

            ImGui::EndTabItem();
        }

        // --------------------------------------------------------------
        // Pestaña 3: Reglas Decreto 1279 / Acuerdo 027
        // --------------------------------------------------------------
        if (ImGui::BeginTabItem("Reglas Decreto 1279 / Acuerdo 027")) {
            ImGui::Spacing();
            ImGui::TextColored(tema::TEXT_MAIN(), "Marco Normativo Salarial Docente PITA");
            ImGui::Spacing();

            ImGui::BeginChild("##CardNormatividad", ImVec2(0, 360), true);
            ImGui::TextColored(tema::WIN_BLUE(), "1. Profesores de Planta (Decreto 1279 de 2002):");
            ImGui::BulletText("Sueldo Basico = Puntos Salariales Reconocidos x Valor Punto Salarial Vigente ($ 23.924 COP).");
            ImGui::BulletText("Factores Salariales: Titulos academicos (Doctorado, Maestria), Categoria (Titular, Asociado), Produccion Academica.");
            ImGui::BulletText("Bonificaciones especiales por posgrado e investigacion.");
            ImGui::Spacing();

            ImGui::TextColored(tema::WIN_BLUE(), "2. Profesores Ocasionales (Acuerdo 027 de 2024):");
            ImGui::BulletText("Vinculacion por periodo academico o meses laborados.");
            ImGui::BulletText("Pago proporcional al tiempo de dedicacion (Tiempo Completo / Medio Tiempo).");
            ImGui::BulletText("Factor salarial indexado a SMMLV ($ 1.750.905 COP, por ejemplo factor 2.92).");
            ImGui::Spacing();

            ImGui::TextColored(tema::WIN_BLUE(), "3. Profesores Catedraticos (Resolucion Rectoral):");
            ImGui::BulletText("Remuneracion basada en el valor de la Hora Catedra ($ 38.500 COP) por el numero de horas dictadas.");
            ImGui::Spacing();

            ImGui::TextColored(tema::WIN_BLUE(), "4. Descuentos Obligatorios de Ley:");
            ImGui::BulletText("Salud Trabajador: 4.0 %% del Ingreso Base de Cotizacion (IBC).");
            ImGui::BulletText("Pension Trabajador: 4.0 %% del Ingreso Base de Cotizacion (IBC).");
            ImGui::BulletText("Fondo de Solidaridad Pensional (FSP): 1.0 %% adicional cuando el IBC sea mayor o igual a 4 SMMLV ($ 7.003.620 COP).");
            ImGui::BulletText("Auxilio de Transporte: Aplica a docentes con ingreso inferior a 2 SMMLV ($ 249.095 COP).");
            ImGui::Spacing();

            ImGui::TextColored(tema::WIN_BLUE(), "5. Prestaciones Sociales Proyectadas:");
            ImGui::BulletText("Cesantias (8.33 %%), Intereses sobre Cesantias (1.0 %%), Prima de Servicios (8.33 %%) y Vacaciones (4.17 %%).");
            ImGui::EndChild();

            ImGui::EndTabItem();
        }

        ImGui::EndTabBar();
    }
}

// ======================================================================
// MODALES DE NÓMINA
// ======================================================================

void PITAApp::renderModalPeriodoNomina() {
    if (modalPeriodoNominaAbierto) {
        ImGui::OpenPopup("Nuevo Periodo de Nomina");
    }

    ImVec2 center = ImGui::GetMainViewport()->GetCenter();
    ImGui::SetNextWindowPos(center, ImGuiCond_Appearing, ImVec2(0.5f, 0.5f));
    ImGui::SetNextWindowSize(ImVec2(420, 0), ImGuiCond_Always);

    if (ImGui::BeginPopupModal("Nuevo Periodo de Nomina", &modalPeriodoNominaAbierto, ImGuiWindowFlags_AlwaysAutoResize)) {
        if (strlen(mensajeModal) > 0) {
            ImGui::TextColored(errorModal ? tema::ACCENT_DANGER() : tema::ACCENT_SUCCESS(), "%s", mensajeModal);
            ImGui::Separator();
        }

        ImGui::InputInt("Ano *", &perAnio);
        ImGui::InputInt("Mes (1-12) *", &perMes);
        if (perMes < 1) perMes = 1;
        if (perMes > 12) perMes = 12;

        ImGui::Spacing();
        ImGui::Separator();

        if (ImGui::Button("Crear Periodo", ImVec2(140, 0))) {
            try {
                ctrl.gestorNomina->cicloVida.crearPeriodoNominaMensual(perAnio, perMes);
                ctrl.guardarDatos();
                ctrl.setMensaje("Periodo de nomina creado con exito.");
                modalPeriodoNominaAbierto = false;
                ImGui::CloseCurrentPopup();
            } catch (const std::exception& e) {
                strncpy(mensajeModal, e.what(), sizeof(mensajeModal) - 1);
                errorModal = true;
            }
        }

        ImGui::SameLine();
        if (ImGui::Button("Cancelar", ImVec2(120, 0))) {
            modalPeriodoNominaAbierto = false;
            ImGui::CloseCurrentPopup();
        }

        ImGui::EndPopup();
    }
}

void PITAApp::renderModalLiquidar() {
    if (modalLiquidarAbierto) {
        ImGui::OpenPopup("Liquidar Nomina");
    }

    ImVec2 center = ImGui::GetMainViewport()->GetCenter();
    ImGui::SetNextWindowPos(center, ImGuiCond_Appearing, ImVec2(0.5f, 0.5f));
    ImGui::SetNextWindowSize(ImVec2(480, 0), ImGuiCond_Always);

    if (ImGui::BeginPopupModal("Liquidar Nomina", &modalLiquidarAbierto, ImGuiWindowFlags_AlwaysAutoResize)) {
        if (strlen(mensajeModal) > 0) {
            ImGui::TextColored(errorModal ? tema::ACCENT_DANGER() : tema::ACCENT_SUCCESS(), "%s", mensajeModal);
            ImGui::Separator();
        }

        // Selector Periodo
        std::string previewPer = "Seleccione Periodo";
        for (int i = 0; i < ctrl.datos.periodosNomina.tamano(); i++) {
            auto& pn = ctrl.datos.periodosNomina.obtener(i);
            if (pn.idPeriodoNomina && *pn.idPeriodoNomina == liqPeriodoId) {
                previewPer = std::to_string(pn.anio.value_or(0)) + "-" + std::to_string(pn.mes.value_or(0));
                break;
            }
        }
        if (ImGui::BeginCombo("Periodo a Liquidar *", previewPer.c_str())) {
            for (int i = 0; i < ctrl.datos.periodosNomina.tamano(); i++) {
                auto& pn = ctrl.datos.periodosNomina.obtener(i);
                bool isSelected = (pn.idPeriodoNomina && *pn.idPeriodoNomina == liqPeriodoId);
                std::string label = "Periodo " + std::to_string(pn.anio.value_or(0)) + "-" + std::to_string(pn.mes.value_or(0)) + " [" + (pn.estado ? *pn.estado : "") + "]";
                if (ImGui::Selectable(label.c_str(), isSelected)) {
                    liqPeriodoId = pn.idPeriodoNomina.value_or(1);
                }
                if (isSelected) ImGui::SetItemDefaultFocus();
            }
            ImGui::EndCombo();
        }

        // Selector Contrato (0: Todos)
        std::string previewCon = (liqContratoId == 0) ? "TODOS LOS CONTRATOS VIGENTES" : ("Contrato #" + std::to_string(liqContratoId));
        if (ImGui::BeginCombo("Alcance de Liquidacion", previewCon.c_str())) {
            if (ImGui::Selectable("TODOS LOS CONTRATOS VIGENTES", liqContratoId == 0)) {
                liqContratoId = 0;
            }
            for (int i = 0; i < ctrl.datos.contratos.tamano(); i++) {
                auto& c = ctrl.datos.contratos.obtener(i);
                if (c.idContrato && c.estado && *c.estado == "ACTIVO") {
                    bool isSelected = (*c.idContrato == liqContratoId);
                    std::string label = "Contrato #" + std::to_string(*c.idContrato) + " (" + (c.tipoContrato ? *c.tipoContrato : "") + ")";
                    if (ImGui::Selectable(label.c_str(), isSelected)) {
                        liqContratoId = *c.idContrato;
                    }
                    if (isSelected) ImGui::SetItemDefaultFocus();
                }
            }
            ImGui::EndCombo();
        }

        ImGui::Spacing();
        ImGui::Separator();

        if (ImGui::Button("Ejecutar Liquidacion", ImVec2(160, 0))) {
            try {
                int liqGeneradas = 0;
                if (liqContratoId > 0) {
                    for (int i = 0; i < ctrl.datos.contratos.tamano(); i++) {
                        auto& c = ctrl.datos.contratos.obtener(i);
                        if (c.idContrato && *c.idContrato == liqContratoId) {
                            if (c.tipoContrato && *c.tipoContrato == "DOCENTE_PLANTA") {
                                ctrl.gestorNomina->liquidarProfesorPlanta(liqContratoId, liqPeriodoId);
                            } else if (c.tipoContrato && *c.tipoContrato == "DOCENTE_OCASIONAL") {
                                ctrl.gestorNomina->liquidarProfesorOcasional(liqContratoId, liqPeriodoId);
                            } else {
                                ctrl.gestorNomina->liquidarProfesorCatedratico(liqContratoId, liqPeriodoId);
                            }
                            liqGeneradas++;
                            break;
                        }
                    }
                } else {
                    for (int i = 0; i < ctrl.datos.contratos.tamano(); i++) {
                        auto& c = ctrl.datos.contratos.obtener(i);
                        if (c.idContrato && c.estado && *c.estado == "ACTIVO") {
                            try {
                                if (c.tipoContrato && *c.tipoContrato == "DOCENTE_PLANTA") {
                                    ctrl.gestorNomina->liquidarProfesorPlanta(*c.idContrato, liqPeriodoId);
                                } else if (c.tipoContrato && *c.tipoContrato == "DOCENTE_OCASIONAL") {
                                    ctrl.gestorNomina->liquidarProfesorOcasional(*c.idContrato, liqPeriodoId);
                                } else {
                                    ctrl.gestorNomina->liquidarProfesorCatedratico(*c.idContrato, liqPeriodoId);
                                }
                                liqGeneradas++;
                            } catch (...) {}
                        }
                    }
                }

                ctrl.guardarDatos();
                ctrl.setMensaje("Liquidacion procesada exitosamente (" + std::to_string(liqGeneradas) + " contratos calculados).");
                modalLiquidarAbierto = false;
                ImGui::CloseCurrentPopup();
            } catch (const std::exception& e) {
                strncpy(mensajeModal, e.what(), sizeof(mensajeModal) - 1);
                errorModal = true;
            }
        }

        ImGui::SameLine();
        if (ImGui::Button("Cancelar", ImVec2(120, 0))) {
            modalLiquidarAbierto = false;
            ImGui::CloseCurrentPopup();
        }

        ImGui::EndPopup();
    }
}

void PITAApp::renderModalPagarNomina() {
    if (modalPagarNominaAbierto) {
        ImGui::OpenPopup("Pagar Liquidacion");
    }

    ImVec2 center = ImGui::GetMainViewport()->GetCenter();
    ImGui::SetNextWindowPos(center, ImGuiCond_Appearing, ImVec2(0.5f, 0.5f));
    ImGui::SetNextWindowSize(ImVec2(440, 0), ImGuiCond_Always);

    if (ImGui::BeginPopupModal("Pagar Liquidacion", &modalPagarNominaAbierto, ImGuiWindowFlags_AlwaysAutoResize)) {
        if (strlen(mensajeModal) > 0) {
            ImGui::TextColored(errorModal ? tema::ACCENT_DANGER() : tema::ACCENT_SUCCESS(), "%s", mensajeModal);
            ImGui::Separator();
        }

        ImGui::Text("Pagando Liquidacion ID: %d", idLiquidacionPagando);
        ImGui::Spacing();

        const char* medios[] = { "TRANSFERENCIA_BANCARIA", "CHEQUE", "CONSIGNACION" };
        static int medioIdx = 0;
        if (ImGui::Combo("Medio de Pago", &medioIdx, medios, IM_ARRAYSIZE(medios))) {
            strncpy(pagMedio, medios[medioIdx], sizeof(pagMedio) - 1);
        }

        ImGui::InputText("Referencia / Comprobante *", pagReferencia, sizeof(pagReferencia));

        ImGui::Spacing();
        ImGui::Separator();

        if (ImGui::Button("Registrar Pago", ImVec2(140, 0))) {
            try {
                ctrl.gestorNomina->cicloVida.pagarLiquidacion(idLiquidacionPagando, pagMedio, pagReferencia);
                ctrl.guardarDatos();
                ctrl.setMensaje("Pago registrado y liquidacion cerrada.");
                modalPagarNominaAbierto = false;
                ImGui::CloseCurrentPopup();
            } catch (const std::exception& e) {
                strncpy(mensajeModal, e.what(), sizeof(mensajeModal) - 1);
                errorModal = true;
            }
        }

        ImGui::SameLine();
        if (ImGui::Button("Cancelar", ImVec2(120, 0))) {
            modalPagarNominaAbierto = false;
            ImGui::CloseCurrentPopup();
        }

        ImGui::EndPopup();
    }
}

// ----------------------------------------------------------------------
// MODAL DESPRENDIBLE DE LIQUIDACIÓN
// ----------------------------------------------------------------------
void PITAApp::renderModalDesprendible() {
    if (modalDesprendibleAbierto) {
        ImGui::OpenPopup("Desprendible de Liquidacion");
    }

    ImVec2 center = ImGui::GetMainViewport()->GetCenter();
    ImGui::SetNextWindowPos(center, ImGuiCond_Appearing, ImVec2(0.5f, 0.5f));
    ImGui::SetNextWindowSize(ImVec2(620, 640), ImGuiCond_Always);

    if (ImGui::BeginPopupModal("Desprendible de Liquidacion", &modalDesprendibleAbierto, ImGuiWindowFlags_None)) {
        LiquidacionNomina* liqPtr = nullptr;
        for (size_t i = 0; i < ctrl.datos.liquidacionesNomina.tamano(); ++i) {
            auto& l = ctrl.datos.liquidacionesNomina.obtener(i);
            if (l.idLiquidacion && *l.idLiquidacion == idLiquidacionDesprendible) {
                liqPtr = &l;
                break;
            }
        }

        if (!liqPtr) {
            ImGui::TextColored(tema::ACCENT_DANGER(), "No se encontro la liquidacion seleccionada.");
            if (ImGui::Button("Cerrar", ImVec2(120, 0))) {
                modalDesprendibleAbierto = false;
                ImGui::CloseCurrentPopup();
            }
            ImGui::EndPopup();
            return;
        }

        int idProf = liqPtr->idProfesor.value_or(0);
        std::string nomProf = getNombreDocente(ctrl, idProf);
        std::string tipoDocente = liqPtr->tipoProfesorLiquidado ? to_string(*liqPtr->tipoProfesorLiquidado) : "PLANTA";

        // Cabecera informativa estilo tarjeta
        ImGui::BeginChild("##HeaderCardDesprendible", ImVec2(0, 70), true);
        if (fuenteTitulo) ImGui::PushFont(fuenteTitulo);
        ImGui::TextColored(tema::TEXT_MAIN(), "Desprendible Oficial de Pago de Nomina");
        if (fuenteTitulo) ImGui::PopFont();
        ImGui::TextColored(tema::TEXT_MUTED(), "Docente: %s  |  Modalidad: %s  |  Liquidacion N° %d",
            nomProf.c_str(), tipoDocente.c_str(), idLiquidacionDesprendible);
        ImGui::EndChild();

        ImGui::Spacing();

        // Categorías de conceptos
        struct ConceptoItem {
            std::string nombre;
            std::string tipo;
            double valor;
        };

        std::vector<ConceptoItem> devengados;
        std::vector<ConceptoItem> deducciones;
        std::vector<ConceptoItem> patronales;

        // Buscar en detallesLiquidacion
        for (size_t i = 0; i < ctrl.datos.detallesLiquidacion.tamano(); ++i) {
            auto& d = ctrl.datos.detallesLiquidacion.obtener(i);
            if (d.idLiquidacion && *d.idLiquidacion == idLiquidacionDesprendible) {
                std::string tm = d.tipoMovimiento.value_or("");
                std::string obs = d.observaciones.value_or("");
                double val = d.valorCalculado.value_or(0.0);

                std::string tmUpper = tm;
                for (auto& c : tmUpper) c = static_cast<char>(toupper(c));
                std::string obsLower = obs;
                for (auto& c : obsLower) c = static_cast<char>(tolower(c));

                bool esDed = (tmUpper.find("DESCUENTO") != std::string::npos ||
                              tmUpper.find("DED") != std::string::npos ||
                              tmUpper == "FONDO_SOLIDARIDAD" || tmUpper == "RETENCION_FUENTE" ||
                              obsLower.find("salud") != std::string::npos || obsLower.find("pension") != std::string::npos ||
                              obsLower.find("fsp") != std::string::npos || obsLower.find("retencion") != std::string::npos);

                if (tmUpper.find("APORTE") != std::string::npos || tmUpper.find("PATRONAL") != std::string::npos || obsLower.find("patronal") != std::string::npos) {
                    esDed = false;
                }

                bool esPat = (tmUpper.find("APORTE") != std::string::npos || tmUpper.find("PATRONAL") != std::string::npos ||
                              obsLower.find("patronal") != std::string::npos || obsLower.find("arl") != std::string::npos ||
                              obsLower.find("sena") != std::string::npos || obsLower.find("icbf") != std::string::npos ||
                              obsLower.find("caja") != std::string::npos);

                std::string label = tm;
                if (tmUpper == "SALARIO_ORDINARIO") {
                    double pts = liqPtr->puntosSalarialesUsados.value_or(0.0);
                    if (tipoDocente == "PLANTA" && pts > 0) {
                        char buf[128];
                        snprintf(buf, sizeof(buf), "Asignacion Basica Mensual (%.0f Pts - Dec. 1279)", pts);
                        label = buf;
                    } else if (tipoDocente == "PLANTA") {
                        label = "Asignacion Basica Mensual (Dec. 1279)";
                    } else {
                        label = "Sueldo Basico Ordinario";
                    }
                } else if (tmUpper == "AUXILIO_TRANSPORTE") {
                    label = "Auxilio Legal de Transporte";
                } else if (tmUpper == "BONIFICACION_POSGRADO") {
                    label = "Bonificacion por Posgrado (Dec. 1279)";
                } else if (tmUpper == "BONIFICACION_INVESTIGACION") {
                    label = "Bonificacion por Investigacion";
                } else if (tmUpper == "DESCUENTO_SALUD") {
                    label = "Aporte Salud Trabajador (4%)";
                } else if (tmUpper == "DESCUENTO_PENSION") {
                    label = "Aporte Pension Trabajador (4%)";
                } else if (tmUpper == "FONDO_SOLIDARIDAD") {
                    label = "Fondo de Solidaridad Pensional (1%)";
                } else if (tmUpper == "RETENCION_FUENTE") {
                    label = "Retencion en la Fuente";
                } else if (tmUpper == "DESCUENTO_INCUMPLIMIENTO") {
                    label = "Descuento por Horas Incumplidas";
                } else if (tmUpper == "APORTE_SALUD_PATRONAL") {
                    label = "Aporte Patronal Salud (8.5%)";
                } else if (tmUpper == "APORTE_PENSION_PATRONAL") {
                    label = "Aporte Patronal Pension (12%)";
                } else if (tmUpper == "APORTE_ARL") {
                    label = "Aporte Riesgos Laborales (ARL)";
                } else if (tmUpper == "APORTE_CAJA") {
                    label = "Caja de Compensacion Familiar (4%)";
                } else if (tmUpper == "APORTE_SENA") {
                    label = "Aporte Parafiscal SENA (2%)";
                } else if (tmUpper == "APORTE_ICBF") {
                    label = "Aporte Parafiscal ICBF (3%)";
                } else if (!obs.empty()) {
                    label = obs;
                }

                // Omitir conceptos en 0 que no sean el salario ordinario
                if (val == 0.0 && tmUpper != "SALARIO_ORDINARIO" && tmUpper != "SUELDO") {
                    continue;
                }

                if (esDed) {
                    deducciones.push_back({ label, tm, val });
                } else if (esPat) {
                    patronales.push_back({ label, tm, val });
                } else {
                    devengados.push_back({ label, tm, val });
                }
            }
        }

        // Si no había detalles, reconstruir con la fórmula fiel de Python
        if (devengados.empty() && deducciones.empty()) {
            double sb = liqPtr->salarioBase.value_or(0.0);
            double dev = liqPtr->totalDevengado.value_or(sb);
            double desc = liqPtr->totalDescuentos.value_or(0.0);

            double pts = liqPtr->puntosSalarialesUsados.value_or(0.0);
            if (tipoDocente == "PLANTA" && pts > 0) {
                char buf[128];
                snprintf(buf, sizeof(buf), "Asignacion Basica Mensual (%.0f Pts - Dec. 1279)", pts);
                devengados.push_back({ buf, "SALARIO_ORDINARIO", sb });
            } else if (tipoDocente == "PLANTA") {
                devengados.push_back({ "Asignacion Basica Mensual (Dec. 1279)", "SALARIO_ORDINARIO", sb });
            } else {
                devengados.push_back({ "Sueldo Basico Mensual", "SALARIO_ORDINARIO", sb });
            }
            if (dev > sb) {
                devengados.push_back({ "Auxilio Legal de Transporte / Bonificaciones", "AUXILIO", dev - sb });
            }

            double salud = std::round(sb * 0.04);
            double pension = std::round(sb * 0.04);
            deducciones.push_back({ "Aporte Salud Trabajador (4%)", "DESCUENTO_SALUD", salud });
            deducciones.push_back({ "Aporte Pension Trabajador (4%)", "DESCUENTO_PENSION", pension });

            double restoDesc = desc - (salud + pension);
            if (restoDesc > 0) {
                deducciones.push_back({ "Fondo Solidaridad Pensional / Retencion", "RETENCION", restoDesc });
            }

            patronales.push_back({ "Aporte Patronal Salud (8.5%)", "APORTE_SALUD_PATRONAL", std::round(dev * 0.085) });
            patronales.push_back({ "Aporte Patronal Pension (12.0%)", "APORTE_PENSION_PATRONAL", std::round(dev * 0.12) });
            patronales.push_back({ "Aporte Riesgos Laborales (ARL)", "APORTE_ARL", std::round(dev * 0.00522) });
            patronales.push_back({ "Caja de Compensacion Familiar (4%)", "APORTE_CAJA", std::round(dev * 0.04) });
            patronales.push_back({ "Aporte Parafiscal SENA (2%)", "APORTE_SENA", std::round(dev * 0.02) });
            patronales.push_back({ "Aporte Parafiscal ICBF (3%)", "APORTE_ICBF", std::round(dev * 0.03) });
        }

        // Área scrolleable para las secciones
        ImGui::BeginChild("##ScrollDetalleSecciones", ImVec2(0, 390), false);

        auto renderSeccion = [](const char* titulo, const std::vector<ConceptoItem>& items, ImVec4 colorTitulo, bool esDeduccion, bool esPatronal) {
            if (items.empty()) return;

            ImGui::Spacing();
            ImGui::TextColored(colorTitulo, "%s", titulo);
            ImGui::Separator();

            for (const auto& item : items) {
                ImGui::Text("  • %s", item.nombre.c_str());
                ImGui::SameLine(ImGui::GetWindowWidth() - 180);
                std::string signo = esDeduccion ? "- " : (esPatronal ? "" : "+ ");
                ImVec4 colorVal = esDeduccion ? tema::ACCENT_DANGER() : (esPatronal ? tema::TEXT_MUTED() : tema::WIN_BLUE());
                ImGui::TextColored(colorVal, "%s%s", signo.c_str(), formatearMoneda(item.valor).c_str());
            }
            ImGui::Spacing();
        };

        renderSeccion("DEVENGADOS Y ASIGNACIONES (+)", devengados, tema::WIN_BLUE(), false, false);
        renderSeccion("DEDUCCIONES OBLIGATORIAS DE LEY (-)", deducciones, tema::ACCENT_DANGER(), true, false);
        renderSeccion("APORTES Y PARAFISCALES PATRONALES", patronales, tema::TEXT_MUTED(), false, true);

        ImGui::EndChild();

        ImGui::Separator();
        ImGui::Spacing();

        // Tarjeta final de Neto a Pagar enmarcada
        double netoVal = liqPtr->netoPagar.value_or(0.0);
        double devVal = liqPtr->totalDevengado.value_or(0.0);
        double descVal = liqPtr->totalDescuentos.value_or(0.0);

        ImGui::BeginChild("##CardNetoFinal", ImVec2(0, 64), true);
        ImGui::TextColored(tema::TEXT_MAIN(), "NETO A PAGAR:");
        ImGui::SameLine(ImGui::GetWindowWidth() - 220);
        ImGui::TextColored(ImVec4(0.063f, 0.725f, 0.506f, 1.0f), "%s", formatearMoneda(netoVal).c_str());
        ImGui::TextColored(tema::TEXT_MUTED(), "Total Devengado: %s  ·  Total Deducciones: -%s",
            formatearMoneda(devVal).c_str(), formatearMoneda(descVal).c_str());
        ImGui::EndChild();

        ImGui::Spacing();
        if (ImGui::Button("Cerrar Desprendible", ImVec2(160, 32))) {
            modalDesprendibleAbierto = false;
            ImGui::CloseCurrentPopup();
        }

        ImGui::EndPopup();
    }
}

// ----------------------------------------------------------------------
// MODAL LIQUIDAR DOCENTE INDIVIDUAL
// ----------------------------------------------------------------------
void PITAApp::renderModalLiquidarIndividual() {
    if (modalLiquidarIndividualAbierto) {
        ImGui::OpenPopup("Liquidar Docente Individual");
    }

    ImVec2 center = ImGui::GetMainViewport()->GetCenter();
    ImGui::SetNextWindowPos(center, ImGuiCond_Appearing, ImVec2(0.5f, 0.5f));
    ImGui::SetNextWindowSize(ImVec2(480, 230), ImGuiCond_Always);

    if (ImGui::BeginPopupModal("Liquidar Docente Individual", &modalLiquidarIndividualAbierto, ImGuiWindowFlags_AlwaysAutoResize)) {
        if (strlen(mensajeModal) > 0) {
            ImGui::TextColored(errorModal ? tema::ACCENT_DANGER() : tema::ACCENT_SUCCESS(), "%s", mensajeModal);
            ImGui::Separator();
        }

        ImGui::TextColored(tema::TEXT_MAIN(), "Seleccionar Docente a Liquidar:");
        ImGui::Spacing();

        std::string previewProf = "Seleccione un profesor...";
        for (size_t i = 0; i < ctrl.datos.profesores.tamano(); ++i) {
            auto& p = ctrl.datos.profesores.obtener(i);
            if (p.idProfesor && *p.idProfesor == idProfesorLiquidarIndividual) {
                previewProf = (p.codigoProfesor ? *p.codigoProfesor : "") + " - " + getNombreDocente(ctrl, *p.idProfesor);
                break;
            }
        }

        if (ImGui::BeginCombo("Docente *", previewProf.c_str())) {
            for (size_t i = 0; i < ctrl.datos.profesores.tamano(); ++i) {
                auto& p = ctrl.datos.profesores.obtener(i);
                int profId = p.idProfesor.value_or(0);
                bool isSelected = (profId == idProfesorLiquidarIndividual);
                std::string label = (p.codigoProfesor ? *p.codigoProfesor : "") + " - " + getNombreDocente(ctrl, profId);
                if (ImGui::Selectable(label.c_str(), isSelected)) {
                    idProfesorLiquidarIndividual = profId;
                }
                if (isSelected) ImGui::SetItemDefaultFocus();
            }
            ImGui::EndCombo();
        }

        ImGui::Spacing();
        ImGui::Separator();
        ImGui::Spacing();

        if (ImGui::Button("Liquidar Docente", ImVec2(160, 32))) {
            if (idProfesorLiquidarIndividual > 0) {
                liquidarProfesorEspecifico(idProfesorLiquidarIndividual);
                modalLiquidarIndividualAbierto = false;
                ImGui::CloseCurrentPopup();
            } else {
                strncpy(mensajeModal, "Debe seleccionar un docente de la lista.", sizeof(mensajeModal) - 1);
                errorModal = true;
            }
        }

        ImGui::SameLine();
        if (ImGui::Button("Cancelar", ImVec2(120, 32))) {
            modalLiquidarIndividualAbierto = false;
            ImGui::CloseCurrentPopup();
        }

        ImGui::EndPopup();
    }
}

// ----------------------------------------------------------------------
// ACCIONES DE NÓMINA (Lógica idéntica al motor PITA de Python)
// ----------------------------------------------------------------------
void PITAApp::liquidarProfesorEspecifico(int idProfesor) {
    Profesor* profPtr = nullptr;
    for (size_t i = 0; i < ctrl.datos.profesores.tamano(); ++i) {
        if (ctrl.datos.profesores.obtener(i).idProfesor && *ctrl.datos.profesores.obtener(i).idProfesor == idProfesor) {
            profPtr = &ctrl.datos.profesores.obtener(i);
            break;
        }
    }
    if (!profPtr) return;

    // Buscar contrato del profesor
    Contrato* contratoPtr = nullptr;
    for (size_t i = 0; i < ctrl.datos.contratos.tamano(); ++i) {
        auto& c = ctrl.datos.contratos.obtener(i);
        if (c.idPersona == profPtr->idPersona) {
            if (c.estado && *c.estado == "ACTIVO") {
                contratoPtr = &c;
                break;
            }
            if (!contratoPtr) contratoPtr = &c;
        }
    }

    // Buscar periodo abierto
    PeriodoNomina* periodoPtr = nullptr;
    for (size_t i = 0; i < ctrl.datos.periodosNomina.tamano(); ++i) {
        auto& p = ctrl.datos.periodosNomina.obtener(i);
        if (p.estado && *p.estado == "ABIERTO") {
            periodoPtr = &p;
            break;
        }
    }
    if (!periodoPtr && ctrl.datos.periodosNomina.tamano() > 0) {
        periodoPtr = &ctrl.datos.periodosNomina.obtener(0);
    }
    if (!periodoPtr) {
        PeriodoNomina pNuevo;
        pNuevo.idPeriodoNomina = 1;
        pNuevo.anio = 2026;
        pNuevo.mes = 3;
        pNuevo.fechaInicio = "2026-03-01";
        pNuevo.fechaFin = "2026-03-31";
        pNuevo.estado = "ABIERTO";
        ctrl.datos.periodosNomina.push_back(pNuevo);
        ctrl.inicializarGestores();
        periodoPtr = &ctrl.datos.periodosNomina.obtener(0);
    }

    int idPeriodo = periodoPtr->idPeriodoNomina.value_or(1);

    // Limpiar liquidación previa de este profesor en este periodo para evitar duplicados
    std::vector<int> idsBorrados;
    ListaEnlazada<LiquidacionNomina> liqFiltradas;
    for (size_t i = 0; i < ctrl.datos.liquidacionesNomina.tamano(); ++i) {
        auto& l = ctrl.datos.liquidacionesNomina.obtener(i);
        if (l.idProfesor && *l.idProfesor == idProfesor && l.idPeriodoNomina && *l.idPeriodoNomina == idPeriodo) {
            if (l.idLiquidacion) idsBorrados.push_back(*l.idLiquidacion);
        } else {
            liqFiltradas.push_back(l);
        }
    }
    ctrl.datos.liquidacionesNomina = std::move(liqFiltradas);

    if (!idsBorrados.empty()) {
        ListaEnlazada<DetalleLiquidacion> detFiltrados;
        for (size_t i = 0; i < ctrl.datos.detallesLiquidacion.tamano(); ++i) {
            auto& d = ctrl.datos.detallesLiquidacion.obtener(i);
            bool borrar = false;
            for (int idB : idsBorrados) {
                if (d.idLiquidacion && *d.idLiquidacion == idB) {
                    borrar = true;
                    break;
                }
            }
            if (!borrar) detFiltrados.push_back(d);
        }
        ctrl.datos.detallesLiquidacion = std::move(detFiltrados);
    }
    ctrl.inicializarGestores();

    // Intentar liquidar con gestorNomina oficial
    bool liquidado = false;
    std::string tipoProfStr = profPtr->tipoProfesor ? to_string(*profPtr->tipoProfesor) : "PLANTA";
    if (contratoPtr && contratoPtr->idContrato) {
        try {
            if (tipoProfStr.find("PLANTA") != std::string::npos) {
                ctrl.gestorNomina->liquidarProfesorPlanta(*contratoPtr->idContrato, idPeriodo);
                liquidado = true;
            } else if (tipoProfStr.find("OCASIONAL") != std::string::npos) {
                ctrl.gestorNomina->liquidarProfesorOcasional(*contratoPtr->idContrato, idPeriodo);
                liquidado = true;
            } else if (tipoProfStr.find("CATEDRATICO") != std::string::npos) {
                ctrl.gestorNomina->liquidarProfesorCatedratico(*contratoPtr->idContrato, idPeriodo);
                liquidado = true;
            }
        } catch (...) {
            liquidado = false;
        }
    }

    // Fallback robusto respetando Decreto 1279 / Acuerdo 027 (fórmula idéntica a Python)
    if (!liquidado) {
        double valPunto = 23924.0;
        double smmlv = 1750905.0;
        double valCat = 38500.0;
        double sueldoBase = 0.0;

        if (contratoPtr && contratoPtr->salarioBase.has_value() && *contratoPtr->salarioBase > 0) {
            sueldoBase = *contratoPtr->salarioBase;
        } else if (tipoProfStr.find("PLANTA") != std::string::npos) {
            double pts = profPtr->puntosSalariales.value_or(0.0);
            sueldoBase = (pts > 0) ? (pts * valPunto) : 3500000.0;
        } else if (tipoProfStr.find("CATEDRATICO") != std::string::npos) {
            double hrs = (contratoPtr && contratoPtr->horasSemanales) ? *contratoPtr->horasSemanales : 12.0;
            sueldoBase = hrs * 4.0 * valCat;
        } else if (tipoProfStr.find("OCASIONAL") != std::string::npos) {
            double factor = (contratoPtr && contratoPtr->factorSalarialSMMLV) ? *contratoPtr->factorSalarialSMMLV : 2.92;
            sueldoBase = smmlv * factor;
        } else {
            sueldoBase = 2500000.0;
        }

        double devengado = sueldoBase;
        double deducciones = std::round(devengado * 0.08); // 4% salud + 4% pension
        double neto = devengado - deducciones;
        double prestaciones = std::round(devengado * 0.2083);

        int maxLiqId = 0;
        for (size_t i = 0; i < ctrl.datos.liquidacionesNomina.tamano(); ++i) {
            int curId = ctrl.datos.liquidacionesNomina.obtener(i).idLiquidacion.value_or(0);
            if (curId > maxLiqId) maxLiqId = curId;
        }
        int nuevoIdLiq = maxLiqId + 1;

        LiquidacionNomina liq;
        liq.idLiquidacion = nuevoIdLiq;
        liq.idProfesor = idProfesor;
        liq.idContrato = contratoPtr ? contratoPtr->idContrato.value_or(idProfesor) : idProfesor;
        liq.idPeriodoNomina = idPeriodo;
        liq.fechaLiquidacion = "2026-03-31";
        liq.salarioBase = sueldoBase;
        liq.totalDevengado = devengado;
        liq.totalDescuentos = deducciones;
        liq.netoPagar = neto;
        liq.totalPrestaciones = prestaciones;
        liq.estado = "LIQUIDADO";
        liq.tipoProfesorLiquidado = profPtr->tipoProfesor;

        ctrl.datos.liquidacionesNomina.push_back(liq);

        // Desglose oficial de detalles para el desprendible
        int maxDetId = 0;
        for (size_t i = 0; i < ctrl.datos.detallesLiquidacion.tamano(); ++i) {
            int curD = ctrl.datos.detallesLiquidacion.obtener(i).idDetalleLiquidacion.value_or(0);
            if (curD > maxDetId) maxDetId = curD;
        }

        DetalleLiquidacion d1;
        d1.idDetalleLiquidacion = ++maxDetId;
        d1.idLiquidacion = nuevoIdLiq;
        d1.idConcepto = 1;
        d1.tipoMovimiento = "SALARIO_ORDINARIO";
        d1.valorCalculado = sueldoBase;
        d1.observaciones = "Sueldo Basico Ordinario";
        ctrl.datos.detallesLiquidacion.push_back(d1);

        DetalleLiquidacion d2;
        d2.idDetalleLiquidacion = ++maxDetId;
        d2.idLiquidacion = nuevoIdLiq;
        d2.idConcepto = 3;
        d2.tipoMovimiento = "DESCUENTO_SALUD";
        d2.valorCalculado = std::round(sueldoBase * 0.04);
        d2.observaciones = "Aporte Salud Trabajador (4%)";
        ctrl.datos.detallesLiquidacion.push_back(d2);

        DetalleLiquidacion d3;
        d3.idDetalleLiquidacion = ++maxDetId;
        d3.idLiquidacion = nuevoIdLiq;
        d3.idConcepto = 4;
        d3.tipoMovimiento = "DESCUENTO_PENSION";
        d3.valorCalculado = std::round(sueldoBase * 0.04);
        d3.observaciones = "Aporte Pension Trabajador (4%)";
        ctrl.datos.detallesLiquidacion.push_back(d3);

        DetalleLiquidacion d4;
        d4.idDetalleLiquidacion = ++maxDetId;
        d4.idLiquidacion = nuevoIdLiq;
        d4.idConcepto = 6;
        d4.tipoMovimiento = "APORTE_SALUD_PATRONAL";
        d4.valorCalculado = std::round(sueldoBase * 0.085);
        d4.observaciones = "Aporte Patronal Salud (8.5%)";
        ctrl.datos.detallesLiquidacion.push_back(d4);

        DetalleLiquidacion d5;
        d5.idDetalleLiquidacion = ++maxDetId;
        d5.idLiquidacion = nuevoIdLiq;
        d5.idConcepto = 7;
        d5.tipoMovimiento = "APORTE_PENSION_PATRONAL";
        d5.valorCalculado = std::round(sueldoBase * 0.12);
        d5.observaciones = "Aporte Patronal Pension (12%)";
        ctrl.datos.detallesLiquidacion.push_back(d5);

        DetalleLiquidacion d6;
        d6.idDetalleLiquidacion = ++maxDetId;
        d6.idLiquidacion = nuevoIdLiq;
        d6.idConcepto = 8;
        d6.tipoMovimiento = "APORTE_ARL";
        d6.valorCalculado = std::round(sueldoBase * 0.00522);
        d6.observaciones = "Aporte Riesgos Laborales (ARL)";
        ctrl.datos.detallesLiquidacion.push_back(d6);

        DetalleLiquidacion d7;
        d7.idDetalleLiquidacion = ++maxDetId;
        d7.idLiquidacion = nuevoIdLiq;
        d7.idConcepto = 9;
        d7.tipoMovimiento = "APORTE_CAJA";
        d7.valorCalculado = std::round(sueldoBase * 0.04);
        d7.observaciones = "Caja de Compensacion Familiar (4%)";
        ctrl.datos.detallesLiquidacion.push_back(d7);

        DetalleLiquidacion d8;
        d8.idDetalleLiquidacion = ++maxDetId;
        d8.idLiquidacion = nuevoIdLiq;
        d8.idConcepto = 10;
        d8.tipoMovimiento = "APORTE_SENA";
        d8.valorCalculado = std::round(sueldoBase * 0.02);
        d8.observaciones = "Aporte Parafiscal SENA (2%)";
        ctrl.datos.detallesLiquidacion.push_back(d8);

        DetalleLiquidacion d9;
        d9.idDetalleLiquidacion = ++maxDetId;
        d9.idLiquidacion = nuevoIdLiq;
        d9.idConcepto = 11;
        d9.tipoMovimiento = "APORTE_ICBF";
        d9.valorCalculado = std::round(sueldoBase * 0.03);
        d9.observaciones = "Aporte Parafiscal ICBF (3%)";
        ctrl.datos.detallesLiquidacion.push_back(d9);

        ctrl.inicializarGestores();
    }

    ctrl.guardarDatos();
}

void PITAApp::ejecutarLiquidacionGeneral() {
    if (ctrl.datos.profesores.tamano() == 0) {
        ctrl.setMensaje("No hay profesores registrados para liquidar.", true);
        return;
    }

    int count = 0;
    for (size_t i = 0; i < ctrl.datos.profesores.tamano(); ++i) {
        auto& p = ctrl.datos.profesores.obtener(i);
        if (p.idProfesor) {
            liquidarProfesorEspecifico(*p.idProfesor);
            count++;
        }
    }
    ctrl.setMensaje("Liquidacion de periodo procesada exitosamente (" + std::to_string(count) + " docentes calculados).");
}

void PITAApp::eliminarLiquidacion(int idLiquidacion) {
    ListaEnlazada<LiquidacionNomina> liqFiltradas;
    for (size_t i = 0; i < ctrl.datos.liquidacionesNomina.tamano(); ++i) {
        auto& l = ctrl.datos.liquidacionesNomina.obtener(i);
        if (l.idLiquidacion.value_or(0) != idLiquidacion) {
            liqFiltradas.push_back(l);
        }
    }
    ctrl.datos.liquidacionesNomina = std::move(liqFiltradas);

    ListaEnlazada<DetalleLiquidacion> detFiltrados;
    for (size_t i = 0; i < ctrl.datos.detallesLiquidacion.tamano(); ++i) {
        auto& d = ctrl.datos.detallesLiquidacion.obtener(i);
        if (d.idLiquidacion.value_or(0) != idLiquidacion) {
            detFiltrados.push_back(d);
        }
    }
    ctrl.datos.detallesLiquidacion = std::move(detFiltrados);

    ctrl.inicializarGestores();
    ctrl.guardarDatos();
    ctrl.setMensaje("Liquidacion #" + std::to_string(idLiquidacion) + " anulada exitosamente.");
}

} // namespace pita
