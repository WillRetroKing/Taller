#define _CRT_SECURE_NO_WARNINGS
#include "gui_app.h"
#include "tema.h"
#include "imgui.h"

#include <cstring>
#include <string>

namespace pita {

// ======================================================================
// VISTA: ACADÉMICA
// ======================================================================

void PITAApp::renderAcademica() {
    if (fuenteTitulo) ImGui::PushFont(fuenteTitulo);
    ImGui::TextColored(tema::TEXT_MAIN(), "Gestion Academica & EBRA");
    if (fuenteTitulo) ImGui::PopFont();

    if (fuentePequena) ImGui::PushFont(fuentePequena);
    ImGui::TextColored(tema::TEXT_MUTED(), "Planes de estudio, cursos, matriculas, calificaciones y alertas academicas");
    if (fuentePequena) ImGui::PopFont();

    ImGui::Spacing(); ImGui::Spacing();

    if (ImGui::BeginTabBar("##TabsAcademica")) {

        // Tab Periodos
        if (ImGui::BeginTabItem("Periodos")) {
            ImGui::Spacing();
            if (ImGui::BeginTable("##TablaPeriodos", 6,
                ImGuiTableFlags_RowBg | ImGuiTableFlags_BordersOuter | ImGuiTableFlags_BordersInnerH |
                ImGuiTableFlags_Resizable | ImGuiTableFlags_ScrollY, ImVec2(0, 0))) {

                ImGui::TableSetupColumn("ID");
                ImGui::TableSetupColumn("Codigo");
                ImGui::TableSetupColumn("Nombre");
                ImGui::TableSetupColumn("Fecha Inicio");
                ImGui::TableSetupColumn("Fecha Fin");
                ImGui::TableSetupColumn("Estado");
                ImGui::TableHeadersRow();

                for (int i = 0; i < ctrl.datos.periodosAcademicos.tamano(); i++) {
                    auto& per = ctrl.datos.periodosAcademicos.obtener(i);
                    ImGui::TableNextRow();
                    ImGui::TableNextColumn(); ImGui::Text("%d", per.idPeriodo ? *per.idPeriodo : 0);
                    ImGui::TableNextColumn(); ImGui::Text("%s", per.codigo ? per.codigo->c_str() : "---");
                    ImGui::TableNextColumn(); ImGui::Text("%s", per.nombre ? per.nombre->c_str() : "---");
                    ImGui::TableNextColumn(); ImGui::Text("%s", per.fechaInicio ? per.fechaInicio->c_str() : "---");
                    ImGui::TableNextColumn(); ImGui::Text("%s", per.fechaFin ? per.fechaFin->c_str() : "---");
                    ImGui::TableNextColumn();
                    if (per.estado && *per.estado == "ABIERTO") {
                        ImGui::PushStyleColor(ImGuiCol_Button, tema::BADGE_ACTIVE_BG());
                        ImGui::PushStyleColor(ImGuiCol_Text, tema::BADGE_ACTIVE_TXT());
                        ImGui::SmallButton("ABIERTO");
                        ImGui::PopStyleColor(2);
                    } else {
                        ImGui::Text("%s", per.estado ? per.estado->c_str() : "---");
                    }
                }
                ImGui::EndTable();
            }
            ImGui::EndTabItem();
        }

        // Tab Cursos
        if (ImGui::BeginTabItem("Cursos")) {
            ImGui::Spacing();
            if (ImGui::Button("+ Nuevo Curso", ImVec2(140, 30))) {
                curCodigo[0] = '\0';
                curNombre[0] = '\0';
                curCreditos = 3;
                mensajeModal[0] = '\0';
                errorModal = false;
                modalCursoAbierto = true;
            }
            ImGui::Spacing();
            if (ImGui::BeginTable("##TablaCursos", 6,
                ImGuiTableFlags_RowBg | ImGuiTableFlags_BordersOuter | ImGuiTableFlags_BordersInnerH |
                ImGuiTableFlags_Resizable | ImGuiTableFlags_ScrollY, ImVec2(0, 0))) {

                ImGui::TableSetupColumn("ID");
                ImGui::TableSetupColumn("Codigo");
                ImGui::TableSetupColumn("Nombre");
                ImGui::TableSetupColumn("Creditos");
                ImGui::TableSetupColumn("Hrs Teoricas");
                ImGui::TableSetupColumn("Hrs Practicas");
                ImGui::TableHeadersRow();

                for (int i = 0; i < ctrl.datos.cursos.tamano(); i++) {
                    auto& c = ctrl.datos.cursos.obtener(i);
                    ImGui::TableNextRow();
                    ImGui::TableNextColumn(); ImGui::Text("%d", c.idCurso ? *c.idCurso : 0);
                    ImGui::TableNextColumn(); ImGui::Text("%s", c.codigoCurso ? c.codigoCurso->c_str() : "---");
                    ImGui::TableNextColumn(); ImGui::Text("%s", c.nombre ? c.nombre->c_str() : "---");
                    ImGui::TableNextColumn(); ImGui::Text("%d", c.numeroCreditos ? *c.numeroCreditos : 0);
                    ImGui::TableNextColumn(); ImGui::Text("%d", c.horasTeoricas ? *c.horasTeoricas : 0);
                    ImGui::TableNextColumn(); ImGui::Text("%d", c.horasPracticas ? *c.horasPracticas : 0);
                }
                ImGui::EndTable();
            }
            ImGui::EndTabItem();
        }

        // Tab Matriculas
        if (ImGui::BeginTabItem("Matriculas")) {
            ImGui::Spacing();
            if (ImGui::Button("+ Matricular Estudiante", ImVec2(180, 30))) {
                if (ctrl.datos.estudiantes.tamano() > 0) {
                    matEstudianteId = ctrl.datos.estudiantes.obtener(0).idEstudiante.value_or(1);
                }
                if (ctrl.datos.ofertasCurso.tamano() > 0) {
                    matOfertaId = ctrl.datos.ofertasCurso.obtener(0).idOfertaCurso.value_or(1);
                }
                mensajeModal[0] = '\0';
                errorModal = false;
                modalMatriculaAbierto = true;
            }
            ImGui::SameLine();
            if (ImGui::Button("+ Registrar Calificacion", ImVec2(190, 30))) {
                if (ctrl.datos.detallesMatricula.tamano() > 0) {
                    notaDetalleMatriculaId = ctrl.datos.detallesMatricula.obtener(0).idDetalleMatricula.value_or(1);
                }
                if (ctrl.datos.evaluaciones.tamano() > 0) {
                    notaEvaluacionId = ctrl.datos.evaluaciones.obtener(0).idEvaluacion.value_or(1);
                }
                notaValor = 4.0f;
                mensajeModal[0] = '\0';
                errorModal = false;
                modalNotaAbierto = true;
            }
            ImGui::Spacing();
            if (ImGui::BeginTable("##TablaMatriculas", 5,
                ImGuiTableFlags_RowBg | ImGuiTableFlags_BordersOuter | ImGuiTableFlags_BordersInnerH |
                ImGuiTableFlags_Resizable | ImGuiTableFlags_ScrollY, ImVec2(0, 0))) {

                ImGui::TableSetupColumn("ID");
                ImGui::TableSetupColumn("Estudiante");
                ImGui::TableSetupColumn("Periodo");
                ImGui::TableSetupColumn("Fecha");
                ImGui::TableSetupColumn("Estado");
                ImGui::TableHeadersRow();

                for (int i = 0; i < ctrl.datos.matriculas.tamano(); i++) {
                    auto& m = ctrl.datos.matriculas.obtener(i);
                    ImGui::TableNextRow();
                    ImGui::TableNextColumn(); ImGui::Text("%d", m.idMatricula ? *m.idMatricula : 0);
                    ImGui::TableNextColumn(); ImGui::Text("%d", m.idEstudiante ? *m.idEstudiante : 0);
                    ImGui::TableNextColumn(); ImGui::Text("%d", m.idPeriodo ? *m.idPeriodo : 0);
                    ImGui::TableNextColumn(); ImGui::Text("%s", m.fechaMatricula ? m.fechaMatricula->c_str() : "---");
                    ImGui::TableNextColumn(); ImGui::Text("%s", m.estadoMatricula ? m.estadoMatricula->c_str() : "---");
                }
                ImGui::EndTable();
            }
            ImGui::EndTabItem();
        }

        // Tab Alertas EBRA
        if (ImGui::BeginTabItem("Alertas EBRA")) {
            ImGui::Spacing();
            if (ImGui::Button("⚡ Ejecutar Deteccion EBRA Masiva", ImVec2(250, 30))) {
                int totalGeneradas = 0;
                for (int i = 0; i < ctrl.datos.estudiantes.tamano(); i++) {
                    auto& est = ctrl.datos.estudiantes.obtener(i);
                    if (est.idEstudiante) {
                        try {
                            auto* alerta = ctrl.gestorMatriculas->evaluarEbra(*est.idEstudiante);
                            if (alerta) totalGeneradas++;
                        } catch (...) {}
                    }
                }
                ctrl.guardarDatos();
                ctrl.setMensaje("Evaluacion EBRA finalizada (" + std::to_string(totalGeneradas) + " alertas generadas/actualizadas).");
            }
            ImGui::Spacing();
            if (ImGui::BeginTable("##TablaAlertas", 5,
                ImGuiTableFlags_RowBg | ImGuiTableFlags_BordersOuter | ImGuiTableFlags_BordersInnerH |
                ImGuiTableFlags_Resizable | ImGuiTableFlags_ScrollY, ImVec2(0, 0))) {

                ImGui::TableSetupColumn("ID");
                ImGui::TableSetupColumn("Estudiante");
                ImGui::TableSetupColumn("Tipo");
                ImGui::TableSetupColumn("Motivo");
                ImGui::TableSetupColumn("Fecha");
                ImGui::TableHeadersRow();

                for (int i = 0; i < ctrl.datos.alertasAcademicas.tamano(); i++) {
                    auto& a = ctrl.datos.alertasAcademicas.obtener(i);
                    ImGui::TableNextRow();
                    ImGui::TableNextColumn(); ImGui::Text("%d", a.idAlerta ? *a.idAlerta : 0);
                    ImGui::TableNextColumn(); ImGui::Text("%d", a.idEstudiante ? *a.idEstudiante : 0);
                    ImGui::TableNextColumn();
                    ImGui::TextColored(tema::ACCENT_DANGER(), "%s", a.tipoAlerta ? a.tipoAlerta->c_str() : "---");
                    ImGui::TableNextColumn(); ImGui::Text("%s", a.motivo ? a.motivo->c_str() : "---");
                    ImGui::TableNextColumn(); ImGui::Text("%s", a.fechaGeneracion ? a.fechaGeneracion->c_str() : "---");
                }
                ImGui::EndTable();
            }
            ImGui::EndTabItem();
        }

        ImGui::EndTabBar();
    }
}

// ======================================================================
// MODALES CURSO, MATRÍCULA Y CALIFICACIÓN
// ======================================================================

void PITAApp::renderModalCurso() {
    if (modalCursoAbierto) {
        ImGui::OpenPopup("Nuevo Curso");
    }

    ImVec2 center = ImGui::GetMainViewport()->GetCenter();
    ImGui::SetNextWindowPos(center, ImGuiCond_Appearing, ImVec2(0.5f, 0.5f));
    ImGui::SetNextWindowSize(ImVec2(450, 0), ImGuiCond_Always);

    if (ImGui::BeginPopupModal("Nuevo Curso", &modalCursoAbierto, ImGuiWindowFlags_AlwaysAutoResize)) {
        if (strlen(mensajeModal) > 0) {
            ImGui::TextColored(errorModal ? tema::ACCENT_DANGER() : tema::ACCENT_SUCCESS(), "%s", mensajeModal);
            ImGui::Separator();
        }

        ImGui::InputText("Codigo de Curso *", curCodigo, sizeof(curCodigo));
        ImGui::InputText("Nombre de Asignatura *", curNombre, sizeof(curNombre));
        ImGui::InputInt("Creditos Academicos", &curCreditos);
        if (curCreditos < 1) curCreditos = 1;

        ImGui::Spacing();
        ImGui::Separator();

        if (ImGui::Button("Guardar", ImVec2(120, 0))) {
            if (strlen(curCodigo) == 0 || strlen(curNombre) == 0) {
                strncpy(mensajeModal, "Codigo y Nombre son obligatorios.", sizeof(mensajeModal) - 1);
                errorModal = true;
            } else {
                Curso c;
                int maxId = 0;
                for (int i = 0; i < ctrl.datos.cursos.tamano(); i++) {
                    auto& cur = ctrl.datos.cursos.obtener(i);
                    if (cur.idCurso && *cur.idCurso > maxId) maxId = *cur.idCurso;
                }
                c.idCurso = maxId + 1;
                c.codigoCurso = curCodigo;
                c.nombre = curNombre;
                c.numeroCreditos = curCreditos;
                c.estado = "ACTIVO";

                ctrl.datos.cursos.push_back(c);
                ctrl.guardarDatos();
                ctrl.setMensaje("Curso registrado exitosamente.");
                modalCursoAbierto = false;
                ImGui::CloseCurrentPopup();
            }
        }

        ImGui::SameLine();
        if (ImGui::Button("Cancelar", ImVec2(120, 0))) {
            modalCursoAbierto = false;
            ImGui::CloseCurrentPopup();
        }

        ImGui::EndPopup();
    }
}

void PITAApp::renderModalMatricula() {
    if (modalMatriculaAbierto) {
        ImGui::OpenPopup("Matricular Curso");
    }

    ImVec2 center = ImGui::GetMainViewport()->GetCenter();
    ImGui::SetNextWindowPos(center, ImGuiCond_Appearing, ImVec2(0.5f, 0.5f));
    ImGui::SetNextWindowSize(ImVec2(500, 0), ImGuiCond_Always);

    if (ImGui::BeginPopupModal("Matricular Curso", &modalMatriculaAbierto, ImGuiWindowFlags_AlwaysAutoResize)) {
        if (strlen(mensajeModal) > 0) {
            ImGui::TextColored(errorModal ? tema::ACCENT_DANGER() : tema::ACCENT_SUCCESS(), "%s", mensajeModal);
            ImGui::Separator();
        }

        // Selector Estudiante
        std::string previewEst = "Seleccione Estudiante";
        for (int i = 0; i < ctrl.datos.estudiantes.tamano(); i++) {
            auto& est = ctrl.datos.estudiantes.obtener(i);
            if (est.idEstudiante && *est.idEstudiante == matEstudianteId) {
                previewEst = est.codigoEstudiante ? *est.codigoEstudiante : ("ID " + std::to_string(*est.idEstudiante));
                break;
            }
        }
        if (ImGui::BeginCombo("Estudiante *", previewEst.c_str())) {
            for (int i = 0; i < ctrl.datos.estudiantes.tamano(); i++) {
                auto& est = ctrl.datos.estudiantes.obtener(i);
                bool isSelected = (est.idEstudiante && *est.idEstudiante == matEstudianteId);
                std::string label = est.codigoEstudiante ? *est.codigoEstudiante : ("Estudiante #" + std::to_string(est.idEstudiante.value_or(0)));
                if (ImGui::Selectable(label.c_str(), isSelected)) {
                    matEstudianteId = est.idEstudiante.value_or(1);
                }
                if (isSelected) ImGui::SetItemDefaultFocus();
            }
            ImGui::EndCombo();
        }

        // Selector Oferta
        std::string previewOf = "Seleccione Oferta de Curso";
        for (int i = 0; i < ctrl.datos.ofertasCurso.tamano(); i++) {
            auto& of = ctrl.datos.ofertasCurso.obtener(i);
            if (of.idOfertaCurso && *of.idOfertaCurso == matOfertaId) {
                previewOf = "Oferta #" + std::to_string(*of.idOfertaCurso);
                break;
            }
        }
        if (ImGui::BeginCombo("Oferta de Asignatura *", previewOf.c_str())) {
            for (int i = 0; i < ctrl.datos.ofertasCurso.tamano(); i++) {
                auto& of = ctrl.datos.ofertasCurso.obtener(i);
                bool isSelected = (of.idOfertaCurso && *of.idOfertaCurso == matOfertaId);
                std::string label = "Oferta #" + std::to_string(of.idOfertaCurso.value_or(0)) + " (Grupo " + (of.grupo ? *of.grupo : "A") + ")";
                if (ImGui::Selectable(label.c_str(), isSelected)) {
                    matOfertaId = of.idOfertaCurso.value_or(1);
                }
                if (isSelected) ImGui::SetItemDefaultFocus();
            }
            ImGui::EndCombo();
        }

        ImGui::Spacing();
        ImGui::Separator();

        if (ImGui::Button("Confirmar Matricula", ImVec2(160, 0))) {
            try {
                ctrl.gestorMatriculas->matricularCurso(matEstudianteId, matOfertaId);
                ctrl.guardarDatos();
                ctrl.setMensaje("Matricula inscrita exitosamente.");
                modalMatriculaAbierto = false;
                ImGui::CloseCurrentPopup();
            } catch (const std::exception& e) {
                strncpy(mensajeModal, e.what(), sizeof(mensajeModal) - 1);
                errorModal = true;
            }
        }

        ImGui::SameLine();
        if (ImGui::Button("Cancelar", ImVec2(120, 0))) {
            modalMatriculaAbierto = false;
            ImGui::CloseCurrentPopup();
        }

        ImGui::EndPopup();
    }
}

void PITAApp::renderModalNota() {
    if (modalNotaAbierto) {
        ImGui::OpenPopup("Registrar Calificacion");
    }

    ImVec2 center = ImGui::GetMainViewport()->GetCenter();
    ImGui::SetNextWindowPos(center, ImGuiCond_Appearing, ImVec2(0.5f, 0.5f));
    ImGui::SetNextWindowSize(ImVec2(460, 0), ImGuiCond_Always);

    if (ImGui::BeginPopupModal("Registrar Calificacion", &modalNotaAbierto, ImGuiWindowFlags_AlwaysAutoResize)) {
        if (strlen(mensajeModal) > 0) {
            ImGui::TextColored(errorModal ? tema::ACCENT_DANGER() : tema::ACCENT_SUCCESS(), "%s", mensajeModal);
            ImGui::Separator();
        }

        // Selector Detalle Matricula
        std::string previewDet = "Detalle Matricula #" + std::to_string(notaDetalleMatriculaId);
        if (ImGui::BeginCombo("Inscripcion / Alumno *", previewDet.c_str())) {
            for (int i = 0; i < ctrl.datos.detallesMatricula.tamano(); i++) {
                auto& dm = ctrl.datos.detallesMatricula.obtener(i);
                bool isSelected = (dm.idDetalleMatricula && *dm.idDetalleMatricula == notaDetalleMatriculaId);
                std::string label = "Inscripcion #" + std::to_string(dm.idDetalleMatricula.value_or(0));
                if (ImGui::Selectable(label.c_str(), isSelected)) {
                    notaDetalleMatriculaId = dm.idDetalleMatricula.value_or(1);
                }
                if (isSelected) ImGui::SetItemDefaultFocus();
            }
            ImGui::EndCombo();
        }

        // Selector Evaluacion
        std::string previewEv = "Evaluacion #" + std::to_string(notaEvaluacionId);
        if (ImGui::BeginCombo("Evaluacion *", previewEv.c_str())) {
            for (int i = 0; i < ctrl.datos.evaluaciones.tamano(); i++) {
                auto& ev = ctrl.datos.evaluaciones.obtener(i);
                bool isSelected = (ev.idEvaluacion && *ev.idEvaluacion == notaEvaluacionId);
                std::string label = ev.nombre ? *ev.nombre : ("Eval #" + std::to_string(ev.idEvaluacion.value_or(0)));
                if (ImGui::Selectable(label.c_str(), isSelected)) {
                    notaEvaluacionId = ev.idEvaluacion.value_or(1);
                }
                if (isSelected) ImGui::SetItemDefaultFocus();
            }
            ImGui::EndCombo();
        }

        ImGui::SliderFloat("Calificacion (0.0 - 5.0) *", &notaValor, 0.0f, 5.0f, "%.2f");

        ImGui::Spacing();
        ImGui::Separator();

        if (ImGui::Button("Registrar Nota", ImVec2(140, 0))) {
            Calificacion cal;
            int maxId = 0;
            for (int i = 0; i < ctrl.datos.calificaciones.tamano(); i++) {
                auto& c = ctrl.datos.calificaciones.obtener(i);
                if (c.idCalificacion && *c.idCalificacion > maxId) maxId = *c.idCalificacion;
            }
            cal.idCalificacion = maxId + 1;
            cal.idDetalleMatricula = notaDetalleMatriculaId;
            cal.idEvaluacion = notaEvaluacionId;
            cal.nota = notaValor;
            cal.estado = "REGISTRADA";

            ctrl.datos.calificaciones.push_back(cal);
            ctrl.guardarDatos();
            ctrl.setMensaje("Calificacion registrada correctamente.");
            modalNotaAbierto = false;
            ImGui::CloseCurrentPopup();
        }

        ImGui::SameLine();
        if (ImGui::Button("Cancelar", ImVec2(120, 0))) {
            modalNotaAbierto = false;
            ImGui::CloseCurrentPopup();
        }

        ImGui::EndPopup();
    }
}

} // namespace pita
