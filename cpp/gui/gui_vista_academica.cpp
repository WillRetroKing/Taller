#define _CRT_SECURE_NO_WARNINGS
#include "gui_app.h"
#include "tema.h"
#include "imgui.h"

#include <cstring>
#include <string>

namespace pita {

// ======================================================================
// HELPERS DE FORMATO Y RESOLUCIÓN DE ENTIDADES ACADÉMICAS
// ======================================================================

static std::string getNombreEstudiante(const GUIController& ctrl, int idEstudiante) {
    for (size_t i = 0; i < ctrl.datos.estudiantes.tamano(); ++i) {
        auto& est = ctrl.datos.estudiantes.obtener(i);
        if (est.idEstudiante && *est.idEstudiante == idEstudiante) {
            std::string cod = est.codigoEstudiante ? *est.codigoEstudiante : ("EST-" + std::to_string(idEstudiante));
            if (est.idPersona) {
                for (size_t j = 0; j < ctrl.datos.personas.tamano(); ++j) {
                    auto& p = ctrl.datos.personas.obtener(j);
                    if (p.idPersona && *p.idPersona == *est.idPersona) {
                        std::string nombre = (p.primerNombre ? *p.primerNombre : "") + " " + (p.primerApellido ? *p.primerApellido : "");
                        return cod + " - " + nombre;
                    }
                }
            }
            return cod;
        }
    }
    return "Estudiante #" + std::to_string(idEstudiante);
}

static std::string getNombreEstudianteConCodigo(const GUIController& ctrl, int idEstudiante) {
    for (size_t i = 0; i < ctrl.datos.estudiantes.tamano(); ++i) {
        auto& est = ctrl.datos.estudiantes.obtener(i);
        if (est.idEstudiante && *est.idEstudiante == idEstudiante) {
            std::string cod = est.codigoEstudiante ? *est.codigoEstudiante : ("EST-" + std::to_string(idEstudiante));
            if (est.idPersona) {
                for (size_t j = 0; j < ctrl.datos.personas.tamano(); ++j) {
                    auto& p = ctrl.datos.personas.obtener(j);
                    if (p.idPersona && *p.idPersona == *est.idPersona) {
                        std::string nombre = (p.primerNombre ? *p.primerNombre : "") + " " + (p.primerApellido ? *p.primerApellido : "");
                        return nombre + " (" + cod + ")";
                    }
                }
            }
            return cod;
        }
    }
    return "Estudiante #" + std::to_string(idEstudiante);
}

static std::string getDescripcionOferta(const GUIController& ctrl, int idOfertaCurso) {
    for (size_t i = 0; i < ctrl.datos.ofertasCurso.tamano(); ++i) {
        auto& of = ctrl.datos.ofertasCurso.obtener(i);
        if (of.idOfertaCurso && *of.idOfertaCurso == idOfertaCurso) {
            std::string gr = of.grupo ? *of.grupo : "01";
            std::string nomCurso = "Asignatura #" + std::to_string(of.idCurso.value_or(0));
            std::string codCurso = "";
            if (of.idCurso) {
                for (size_t j = 0; j < ctrl.datos.cursos.tamano(); ++j) {
                    auto& c = ctrl.datos.cursos.obtener(j);
                    if (c.idCurso && *c.idCurso == *of.idCurso) {
                        nomCurso = c.nombre ? *c.nombre : nomCurso;
                        codCurso = c.codigoCurso ? *c.codigoCurso : "";
                        break;
                    }
                }
            }
            std::string cupos = "";
            if (of.cupoDisponible && of.cupoMaximo) {
                cupos = " - Cupos: " + std::to_string(*of.cupoDisponible) + "/" + std::to_string(*of.cupoMaximo);
            }
            if (!codCurso.empty()) {
                return "[" + codCurso + "] " + nomCurso + " (Gr. " + gr + ")" + cupos;
            }
            return nomCurso + " (Gr. " + gr + ")" + cupos;
        }
    }
    return "Oferta #" + std::to_string(idOfertaCurso);
}

static std::string getDescripcionDetalleMatricula(const GUIController& ctrl, int idDetalleMatricula) {
    for (size_t i = 0; i < ctrl.datos.detallesMatricula.tamano(); ++i) {
        auto& dm = ctrl.datos.detallesMatricula.obtener(i);
        if (dm.idDetalleMatricula && *dm.idDetalleMatricula == idDetalleMatricula) {
            // Estudiante
            std::string alumno = "Alumno";
            if (dm.idMatricula) {
                for (size_t j = 0; j < ctrl.datos.matriculas.tamano(); ++j) {
                    auto& m = ctrl.datos.matriculas.obtener(j);
                    if (m.idMatricula && *m.idMatricula == *dm.idMatricula && m.idEstudiante) {
                        alumno = getNombreEstudiante(ctrl, *m.idEstudiante);
                        break;
                    }
                }
            }
            // Curso / Oferta
            std::string curso = "Curso";
            std::string gr = "01";
            if (dm.idOfertaCurso) {
                for (size_t k = 0; k < ctrl.datos.ofertasCurso.tamano(); ++k) {
                    auto& of = ctrl.datos.ofertasCurso.obtener(k);
                    if (of.idOfertaCurso && *of.idOfertaCurso == *dm.idOfertaCurso) {
                        gr = of.grupo ? *of.grupo : "01";
                        if (of.idCurso) {
                            for (size_t cIdx = 0; cIdx < ctrl.datos.cursos.tamano(); ++cIdx) {
                                auto& c = ctrl.datos.cursos.obtener(cIdx);
                                if (c.idCurso && *c.idCurso == *of.idCurso) {
                                    curso = c.nombre ? *c.nombre : curso;
                                    break;
                                }
                            }
                        }
                        break;
                    }
                }
            }
            char notaBuf[32];
            if (dm.notaFinal) {
                snprintf(notaBuf, sizeof(notaBuf), " [Nota: %.2f]", *dm.notaFinal);
            } else {
                snprintf(notaBuf, sizeof(notaBuf), " [Sin nota]");
            }
            return "INS-" + std::to_string(idDetalleMatricula) + " | " + alumno + " — " + curso + " (Gr. " + gr + ")" + notaBuf;
        }
    }
    return "Inscripcion #" + std::to_string(idDetalleMatricula);
}

static std::string getDescripcionEvaluacion(const GUIController& ctrl, int idEvaluacion) {
    for (size_t i = 0; i < ctrl.datos.evaluaciones.tamano(); ++i) {
        auto& ev = ctrl.datos.evaluaciones.obtener(i);
        if (ev.idEvaluacion && *ev.idEvaluacion == idEvaluacion) {
            std::string nom = ev.nombre ? *ev.nombre : ("Evaluacion #" + std::to_string(idEvaluacion));
            char porcBuf[32] = "";
            if (ev.porcentaje) {
                snprintf(porcBuf, sizeof(porcBuf), " (%.1f%%)", *ev.porcentaje);
            }
            std::string curso = "";
            if (ev.idOfertaCurso) {
                for (size_t k = 0; k < ctrl.datos.ofertasCurso.tamano(); ++k) {
                    auto& of = ctrl.datos.ofertasCurso.obtener(k);
                    if (of.idOfertaCurso && *of.idOfertaCurso == *ev.idOfertaCurso && of.idCurso) {
                        for (size_t cIdx = 0; cIdx < ctrl.datos.cursos.tamano(); ++cIdx) {
                            auto& c = ctrl.datos.cursos.obtener(cIdx);
                            if (c.idCurso && *c.idCurso == *of.idCurso) {
                                curso = c.nombre ? (" — " + *c.nombre) : "";
                                break;
                            }
                        }
                        break;
                    }
                }
            }
            return nom + porcBuf + curso;
        }
    }
    return "Evaluacion #" + std::to_string(idEvaluacion);
}

static std::string getDocenteAsignadoOferta(const GUIController& ctrl, int idOfertaCurso) {
    for (size_t aIdx = 0; aIdx < ctrl.datos.asignacionesDocentes.tamano(); ++aIdx) {
        auto& asig = ctrl.datos.asignacionesDocentes.obtener(aIdx);
        if (asig.idOfertaCurso && *asig.idOfertaCurso == idOfertaCurso) {
            if (asig.estado && *asig.estado == "INACTIVO") continue;
            if (asig.idProfesor) {
                for (size_t pIdx = 0; pIdx < ctrl.datos.profesores.tamano(); ++pIdx) {
                    auto& pr = ctrl.datos.profesores.obtener(pIdx);
                    if (pr.idProfesor && *pr.idProfesor == *asig.idProfesor && pr.idPersona) {
                        for (size_t perIdx = 0; perIdx < ctrl.datos.personas.tamano(); ++perIdx) {
                            auto& per = ctrl.datos.personas.obtener(perIdx);
                            if (per.idPersona && *per.idPersona == *pr.idPersona) {
                                return (per.primerNombre ? *per.primerNombre : "") + " " + (per.primerApellido ? *per.primerApellido : "");
                            }
                        }
                    }
                }
            }
        }
    }
    return "Sin asignar";
}

static std::string getNombreCursoPorId(const GUIController& ctrl, int idCurso) {
    for (size_t i = 0; i < ctrl.datos.cursos.tamano(); ++i) {
        auto& c = ctrl.datos.cursos.obtener(i);
        if (c.idCurso && *c.idCurso == idCurso) {
            return c.nombre ? *c.nombre : ("Curso #" + std::to_string(idCurso));
        }
    }
    return "Curso #" + std::to_string(idCurso);
}

static std::string getCodigoPeriodoPorId(const GUIController& ctrl, int idPeriodo) {
    for (size_t i = 0; i < ctrl.datos.periodosAcademicos.tamano(); ++i) {
        auto& per = ctrl.datos.periodosAcademicos.obtener(i);
        if (per.idPeriodo && *per.idPeriodo == idPeriodo) {
            return per.codigo ? *per.codigo : ("Per #" + std::to_string(idPeriodo));
        }
    }
    return "Per #" + std::to_string(idPeriodo);
}

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
            if (ImGui::Button("+ Aperturar Periodo", ImVec2(170, 30))) {
                snprintf(perAcadCodigo, sizeof(perAcadCodigo), "2026-1");
                snprintf(perAcadNombre, sizeof(perAcadNombre), "Periodo Academico 2026-1");
                snprintf(perAcadFechaInicio, sizeof(perAcadFechaInicio), "2026-02-02");
                snprintf(perAcadFechaFin, sizeof(perAcadFechaFin), "2026-06-19");
                perAcadEstadoIdx = 0;
                mensajeModal[0] = '\0';
                errorModal = false;
                modalPeriodoAcademicoAbierto = true;
            }
            ImGui::SameLine();
            if (ImGui::Button("Apertura Rapida 2026-1", ImVec2(180, 30))) {
                bool yaExiste = false;
                for (size_t i = 0; i < ctrl.datos.periodosAcademicos.tamano(); ++i) {
                    auto& p = ctrl.datos.periodosAcademicos.obtener(i);
                    if (p.codigo && *p.codigo == "2026-1") { yaExiste = true; break; }
                }
                if (!yaExiste) {
                    int maxId = 0;
                    for (size_t i = 0; i < ctrl.datos.periodosAcademicos.tamano(); ++i) {
                        auto& p = ctrl.datos.periodosAcademicos.obtener(i);
                        if (p.idPeriodo && *p.idPeriodo > maxId) maxId = *p.idPeriodo;
                    }
                    PeriodoAcademico nuevoP;
                    nuevoP.idPeriodo = maxId + 1;
                    nuevoP.codigo = "2026-1";
                    nuevoP.nombre = "Periodo Academico 2026-1";
                    nuevoP.fechaInicio = "2026-02-02";
                    nuevoP.fechaFin = "2026-06-19";
                    nuevoP.estado = "MATRICULAS";
                    ctrl.datos.periodosAcademicos.push_back(nuevoP);
                    ctrl.guardarDatos();
                    ctrl.setMensaje("Periodo 2026-1 aperturado exitosamente.");
                }
            }
            ImGui::Spacing();

            if (ImGui::BeginTable("##TablaPeriodos", 7,
                ImGuiTableFlags_RowBg | ImGuiTableFlags_BordersOuter | ImGuiTableFlags_BordersInnerH |
                ImGuiTableFlags_Resizable | ImGuiTableFlags_ScrollY, ImVec2(0, 0))) {

                ImGui::TableSetupColumn("ID", ImGuiTableColumnFlags_WidthFixed, 45);
                ImGui::TableSetupColumn("Codigo", ImGuiTableColumnFlags_WidthFixed, 90);
                ImGui::TableSetupColumn("Nombre", ImGuiTableColumnFlags_WidthStretch);
                ImGui::TableSetupColumn("Fecha Inicio", ImGuiTableColumnFlags_WidthFixed, 105);
                ImGui::TableSetupColumn("Fecha Fin", ImGuiTableColumnFlags_WidthFixed, 105);
                ImGui::TableSetupColumn("Estado", ImGuiTableColumnFlags_WidthFixed, 120);
                ImGui::TableSetupColumn("Acciones Ciclo de Vida", ImGuiTableColumnFlags_WidthFixed, 200);
                ImGui::TableHeadersRow();

                for (int i = 0; i < ctrl.datos.periodosAcademicos.tamano(); i++) {
                    auto& per = ctrl.datos.periodosAcademicos.obtener(i);
                    int idPer = per.idPeriodo ? *per.idPeriodo : 0;
                    ImGui::TableNextRow();
                    ImGui::TableNextColumn(); ImGui::Text("%d", idPer);
                    ImGui::TableNextColumn(); ImGui::TextColored(tema::WIN_BLUE(), "%s", per.codigo ? per.codigo->c_str() : "---");
                    ImGui::TableNextColumn(); ImGui::Text("%s", per.nombre ? per.nombre->c_str() : "---");
                    ImGui::TableNextColumn(); ImGui::Text("%s", per.fechaInicio ? per.fechaInicio->c_str() : "---");
                    ImGui::TableNextColumn(); ImGui::Text("%s", per.fechaFin ? per.fechaFin->c_str() : "---");
                    ImGui::TableNextColumn();
                    std::string est = per.estado ? *per.estado : "PLANIFICACION";
                    if (est == "EN_CURSO" || est == "ABIERTO" || est == "MATRICULAS") {
                        ImGui::PushStyleColor(ImGuiCol_Button, tema::BADGE_ACTIVE_BG());
                        ImGui::PushStyleColor(ImGuiCol_Text, tema::BADGE_ACTIVE_TXT());
                        ImGui::SmallButton(est.c_str());
                        ImGui::PopStyleColor(2);
                    } else if (est == "FINALIZADO" || est == "CERRADO") {
                        ImGui::TextColored(tema::ACCENT_DANGER(), "%s", est.c_str());
                    } else {
                        ImGui::Text("%s", est.c_str());
                    }

                    ImGui::TableNextColumn();
                    ImGui::PushID(idPer);
                    if (est == "PLANIFICACION") {
                        if (ImGui::SmallButton("-> Abrir Matriculas")) {
                            per.estado = "MATRICULAS";
                            ctrl.guardarDatos();
                        }
                    } else if (est == "MATRICULAS") {
                        if (ImGui::SmallButton("-> Iniciar Clases")) {
                            per.estado = "EN_CURSO";
                            ctrl.guardarDatos();
                        }
                    } else if (est == "EN_CURSO" || est == "ABIERTO") {
                        if (ImGui::SmallButton("-> Finalizar")) {
                            per.estado = "FINALIZADO";
                            ctrl.guardarDatos();
                        }
                    } else {
                        if (ImGui::SmallButton("Reabrir")) {
                            per.estado = "PLANIFICACION";
                            ctrl.guardarDatos();
                        }
                    }
                    ImGui::SameLine();
                    if (ImGui::SmallButton("Ciclar")) {
                        if (est == "PLANIFICACION") per.estado = "MATRICULAS";
                        else if (est == "MATRICULAS") per.estado = "EN_CURSO";
                        else if (est == "EN_CURSO") per.estado = "FINALIZADO";
                        else per.estado = "PLANIFICACION";
                        ctrl.guardarDatos();
                    }
                    ImGui::PopID();
                }
                ImGui::EndTable();
            }
            ImGui::EndTabItem();
        }

        // Tab Planes de Estudio & Malla Curricular
        if (ImGui::BeginTabItem("Planes de Estudio & Malla Curricular")) {
            ImGui::Spacing();
            if (ImGui::Button("+ Nuevo Plan de Estudio", ImVec2(190, 30))) {
                snprintf(planCodigo, sizeof(planCodigo), "PLAN-SIS-2026");
                snprintf(planNombre, sizeof(planNombre), "Plan de Estudios Ingenieria de Sistemas 2026");
                snprintf(planVersion, sizeof(planVersion), "2026.1");
                planTotalCreditos = 160;
                planProgramaId = 1;
                mensajeModal[0] = '\0';
                errorModal = false;
                modalPlanEstudioAbierto = true;
            }
            ImGui::Spacing();

            if (ImGui::BeginTable("##TablaPlanesEstudio", 8,
                ImGuiTableFlags_RowBg | ImGuiTableFlags_BordersOuter | ImGuiTableFlags_BordersInnerH |
                ImGuiTableFlags_Resizable | ImGuiTableFlags_ScrollY, ImVec2(0, 0))) {

                ImGui::TableSetupColumn("ID", ImGuiTableColumnFlags_WidthFixed, 45);
                ImGui::TableSetupColumn("Codigo", ImGuiTableColumnFlags_WidthFixed, 110);
                ImGui::TableSetupColumn("Nombre del Plan", ImGuiTableColumnFlags_WidthStretch);
                ImGui::TableSetupColumn("Programa", ImGuiTableColumnFlags_WidthFixed, 140);
                ImGui::TableSetupColumn("Version", ImGuiTableColumnFlags_WidthFixed, 75);
                ImGui::TableSetupColumn("Creditos", ImGuiTableColumnFlags_WidthFixed, 75);
                ImGui::TableSetupColumn("Estado", ImGuiTableColumnFlags_WidthFixed, 100);
                ImGui::TableSetupColumn("Acciones", ImGuiTableColumnFlags_WidthFixed, 230);
                ImGui::TableHeadersRow();

                for (int i = 0; i < ctrl.datos.planesEstudio.tamano(); ++i) {
                    auto& pl = ctrl.datos.planesEstudio.obtener(i);
                    int idPlan = pl.idPlanEstudio ? *pl.idPlanEstudio : 0;
                    ImGui::TableNextRow();
                    ImGui::TableNextColumn(); ImGui::Text("%d", idPlan);
                    ImGui::TableNextColumn(); ImGui::TextColored(tema::WIN_BLUE(), "%s", pl.codigo ? pl.codigo->c_str() : "---");
                    ImGui::TableNextColumn(); ImGui::Text("%s", pl.nombre ? pl.nombre->c_str() : "---");
                    std::string nomProg = "Programa #" + std::to_string(pl.idPrograma.value_or(0));
                    for (int j = 0; j < ctrl.datos.programas.tamano(); ++j) {
                        auto& prg = ctrl.datos.programas.obtener(j);
                        if (prg.idPrograma && pl.idPrograma && *prg.idPrograma == *pl.idPrograma) {
                            nomProg = prg.nombre ? *prg.nombre : nomProg;
                            break;
                        }
                    }
                    ImGui::TableNextColumn(); ImGui::Text("%s", nomProg.c_str());
                    ImGui::TableNextColumn(); ImGui::Text("%s", pl.version ? pl.version->c_str() : "1.0");
                    ImGui::TableNextColumn(); ImGui::Text("%d", pl.totalCreditos.value_or(0));
                    ImGui::TableNextColumn();
                    std::string est = pl.estado ? *pl.estado : "VIGENTE";
                    if (est == "VIGENTE") {
                        ImGui::PushStyleColor(ImGuiCol_Button, tema::BADGE_ACTIVE_BG());
                        ImGui::PushStyleColor(ImGuiCol_Text, tema::BADGE_ACTIVE_TXT());
                        ImGui::SmallButton("VIGENTE");
                        ImGui::PopStyleColor(2);
                    } else {
                        ImGui::Text("%s", est.c_str());
                    }

                    ImGui::TableNextColumn();
                    ImGui::PushID(idPlan);
                    ImGui::PushStyleColor(ImGuiCol_Button, tema::WIN_BLUE());
                    ImGui::PushStyleColor(ImGuiCol_Text, ImVec4(1,1,1,1));
                    if (ImGui::SmallButton("Malla Curricular")) {
                        planSeleccionadoId = idPlan;
                        modalMallaCurricularAbierto = true;
                    }
                    ImGui::PopStyleColor(2);
                    ImGui::SameLine();
                    if (ImGui::SmallButton("Alternar Estado")) {
                        if (pl.estado.has_value() && *pl.estado == "VIGENTE") {
                            pl.estado = "OBSOLETO";
                        } else {
                            pl.estado = "VIGENTE";
                        }
                        ctrl.guardarDatos();
                    }
                    ImGui::PopID();
                }
                ImGui::EndTable();
            }
            ImGui::EndTabItem();
        }

        // Tab Cursos & Ofertas
        if (ImGui::BeginTabItem("Cursos & Ofertas")) {
            ImGui::Spacing();

            if (ImGui::BeginTabBar("##SubTabsCursosOfertas")) {

                // Sub-tab 1: Catálogo de Asignaturas
                if (ImGui::BeginTabItem("Catalogo de Asignaturas")) {
                    ImGui::Spacing();
                    if (ImGui::Button("+ Nueva Asignatura", ImVec2(160, 30))) {
                        curCodigo[0] = '\0';
                        curNombre[0] = '\0';
                        curCreditos = 3;
                        curHorasTeoricas = 3;
                        curHorasPracticas = 2;
                        curNotaMinima = 3.0f;
                        curCupoSugerido = 30;
                        mensajeModal[0] = '\0';
                        errorModal = false;
                        modalCursoAbierto = true;
                    }
                    ImGui::Spacing();

                    if (ImGui::BeginTable("##TablaCursosCatalogo", 8,
                        ImGuiTableFlags_RowBg | ImGuiTableFlags_BordersOuter | ImGuiTableFlags_BordersInnerH |
                        ImGuiTableFlags_Resizable | ImGuiTableFlags_ScrollY, ImVec2(0, 0))) {

                        ImGui::TableSetupColumn("ID", ImGuiTableColumnFlags_WidthFixed, 45);
                        ImGui::TableSetupColumn("Codigo", ImGuiTableColumnFlags_WidthFixed, 90);
                        ImGui::TableSetupColumn("Nombre Asignatura", ImGuiTableColumnFlags_WidthStretch);
                        ImGui::TableSetupColumn("Creditos", ImGuiTableColumnFlags_WidthFixed, 80);
                        ImGui::TableSetupColumn("Horas T / P", ImGuiTableColumnFlags_WidthFixed, 100);
                        ImGui::TableSetupColumn("Nota Minima", ImGuiTableColumnFlags_WidthFixed, 95);
                        ImGui::TableSetupColumn("Cupo Sugerido", ImGuiTableColumnFlags_WidthFixed, 100);
                        ImGui::TableSetupColumn("Acciones", ImGuiTableColumnFlags_WidthFixed, 150);
                        ImGui::TableHeadersRow();

                        for (int i = 0; i < ctrl.datos.cursos.tamano(); i++) {
                            auto& c = ctrl.datos.cursos.obtener(i);
                            int idCur = c.idCurso ? *c.idCurso : 0;
                            ImGui::TableNextRow();
                            ImGui::TableNextColumn(); ImGui::Text("%d", idCur);
                            ImGui::TableNextColumn(); ImGui::TextColored(tema::WIN_BLUE(), "%s", c.codigoCurso ? c.codigoCurso->c_str() : "---");
                            ImGui::TableNextColumn(); ImGui::Text("%s", c.nombre ? c.nombre->c_str() : "---");
                            ImGui::TableNextColumn(); ImGui::Text("%d creditos", c.numeroCreditos ? *c.numeroCreditos : 3);
                            ImGui::TableNextColumn(); ImGui::Text("%dh T / %dh P", c.horasTeoricas ? *c.horasTeoricas : 3, c.horasPracticas ? *c.horasPracticas : 2);
                            double notaMin = (c.notaMinimaAprobatoria.has_value() && *c.notaMinimaAprobatoria > 0.0) ? *c.notaMinimaAprobatoria : 3.0;
                            ImGui::TableNextColumn(); ImGui::Text("%.1f", notaMin);
                            ImGui::TableNextColumn(); ImGui::Text("%d cupos", c.cupoSugerido ? *c.cupoSugerido : 30);
                            ImGui::TableNextColumn();
                            ImGui::PushID(idCur);
                            if (ImGui::SmallButton("Editar")) {
                                abrirModalEditarCurso(idCur);
                            }
                            ImGui::SameLine();
                            ImGui::PushStyleColor(ImGuiCol_Button, tema::ACCENT_DANGER());
                            ImGui::PushStyleColor(ImGuiCol_ButtonHovered, tema::ACCENT_DANGER_H());
                            if (ImGui::SmallButton("Eliminar")) {
                                eliminarCurso(idCur);
                            }
                            ImGui::PopStyleColor(2);
                            ImGui::PopID();
                        }
                        ImGui::EndTable();
                    }
                    ImGui::EndTabItem();
                }

                // Sub-tab 2: Ofertas y Grupos Abiertos
                if (ImGui::BeginTabItem("Ofertas y Grupos Abiertos")) {
                    ImGui::Spacing();
                    if (ImGui::Button("+ Abrir Oferta / Grupo", ImVec2(180, 30))) {
                        abrirModalNuevaOferta();
                    }
                    ImGui::Spacing();

                    if (ctrl.datos.ofertasCurso.tamano() == 0) {
                        ImGui::TextColored(tema::TEXT_MUTED(), "No hay ofertas ni grupos abiertos registrados.");
                    } else {
                        if (ImGui::BeginTable("##TablaOfertasGrupos", 8,
                            ImGuiTableFlags_RowBg | ImGuiTableFlags_BordersOuter | ImGuiTableFlags_BordersInnerH |
                            ImGuiTableFlags_Resizable | ImGuiTableFlags_ScrollY, ImVec2(0, 0))) {

                            ImGui::TableSetupColumn("Codigo Oferta", ImGuiTableColumnFlags_WidthFixed, 105);
                            ImGui::TableSetupColumn("Asignatura", ImGuiTableColumnFlags_WidthStretch);
                            ImGui::TableSetupColumn("Periodo", ImGuiTableColumnFlags_WidthFixed, 85);
                            ImGui::TableSetupColumn("Grupo", ImGuiTableColumnFlags_WidthFixed, 65);
                            ImGui::TableSetupColumn("Aula / Sede", ImGuiTableColumnFlags_WidthFixed, 130);
                            ImGui::TableSetupColumn("Cupo Disp / Total", ImGuiTableColumnFlags_WidthFixed, 125);
                            ImGui::TableSetupColumn("Docente Asignado", ImGuiTableColumnFlags_WidthStretch);
                            ImGui::TableSetupColumn("Acciones", ImGuiTableColumnFlags_WidthFixed, 90);
                            ImGui::TableHeadersRow();

                            for (int i = 0; i < ctrl.datos.ofertasCurso.tamano(); i++) {
                                auto& of = ctrl.datos.ofertasCurso.obtener(i);
                                int idOf = of.idOfertaCurso ? *of.idOfertaCurso : 0;
                                ImGui::TableNextRow();

                                // Código
                                ImGui::TableNextColumn();
                                ImGui::TextColored(tema::ACCENT_INDIGO(), "OFER-%d", idOf > 0 ? idOf : (i + 1));

                                // Asignatura
                                ImGui::TableNextColumn();
                                ImGui::Text("%s", getNombreCursoPorId(ctrl, of.idCurso.value_or(0)).c_str());

                                // Periodo
                                ImGui::TableNextColumn();
                                ImGui::Text("%s", getCodigoPeriodoPorId(ctrl, of.idPeriodo.value_or(0)).c_str());

                                // Grupo
                                ImGui::TableNextColumn();
                                ImGui::Text("Gr. %s", of.grupo ? of.grupo->c_str() : "01");

                                // Aula / Sede
                                ImGui::TableNextColumn();
                                std::string aula = of.aula ? *of.aula : "Aula";
                                std::string sede = of.sede ? *of.sede : "Sede";
                                ImGui::Text("%s (%s)", aula.c_str(), sede.c_str());

                                // Cupos con semáforo
                                ImGui::TableNextColumn();
                                int cDisp = of.cupoDisponible.value_or(0);
                                int cMax = of.cupoMaximo.value_or(35);
                                ImVec4 colorCupo = (cDisp > 5) ? tema::ACCENT_SUCCESS() : ((cDisp > 0) ? tema::ACCENT_WARNING() : tema::ACCENT_DANGER());
                                ImGui::TextColored(colorCupo, "%d / %d", cDisp, cMax);

                                // Docente
                                ImGui::TableNextColumn();
                                ImGui::TextColored(tema::WIN_BLUE(), "%s", getDocenteAsignadoOferta(ctrl, of.idOfertaCurso.value_or(0)).c_str());

                                // Acciones
                                ImGui::TableNextColumn();
                                ImGui::PushID(idOf);
                                ImGui::PushStyleColor(ImGuiCol_Button, tema::ACCENT_DANGER());
                                ImGui::PushStyleColor(ImGuiCol_ButtonHovered, tema::ACCENT_DANGER_H());
                                if (ImGui::SmallButton("Cerrar")) {
                                    eliminarOferta(idOf);
                                }
                                ImGui::PopStyleColor(2);
                                ImGui::PopID();
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

        // Tab Matriculas
        if (ImGui::BeginTabItem("Matriculas de Cursos")) {
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
            ImGui::Spacing();

            if (ImGui::BeginTable("##TablaInscripcionesMatricula", 7,
                ImGuiTableFlags_RowBg | ImGuiTableFlags_BordersOuter | ImGuiTableFlags_BordersInnerH |
                ImGuiTableFlags_Resizable | ImGuiTableFlags_ScrollY, ImVec2(0, 0))) {

                ImGui::TableSetupColumn("ID", ImGuiTableColumnFlags_WidthFixed, 65);
                ImGui::TableSetupColumn("Estudiante", ImGuiTableColumnFlags_WidthStretch);
                ImGui::TableSetupColumn("Asignatura / Oferta", ImGuiTableColumnFlags_WidthStretch);
                ImGui::TableSetupColumn("Creditos", ImGuiTableColumnFlags_WidthFixed, 65);
                ImGui::TableSetupColumn("Estado", ImGuiTableColumnFlags_WidthFixed, 95);
                ImGui::TableSetupColumn("Nota Final", ImGuiTableColumnFlags_WidthFixed, 85);
                ImGui::TableSetupColumn("Acciones", ImGuiTableColumnFlags_WidthFixed, 95);
                ImGui::TableHeadersRow();

                for (int i = 0; i < ctrl.datos.detallesMatricula.tamano(); i++) {
                    auto& dm = ctrl.datos.detallesMatricula.obtener(i);

                    // Buscar Estudiante
                    std::string nomEstudiante = "Estudiante";
                    int idEstudiante = 0;
                    if (dm.idMatricula) {
                        for (int j = 0; j < ctrl.datos.matriculas.tamano(); j++) {
                            auto& m = ctrl.datos.matriculas.obtener(j);
                            if (m.idMatricula && *m.idMatricula == *dm.idMatricula && m.idEstudiante) {
                                idEstudiante = *m.idEstudiante;
                                nomEstudiante = getNombreEstudianteConCodigo(ctrl, idEstudiante);
                                break;
                            }
                        }
                    }

                    // Buscar Curso y Oferta
                    std::string nomCurso = "Asignatura";
                    int creditos = 3;
                    std::string grupo = "01";
                    if (dm.idOfertaCurso) {
                        for (int k = 0; k < ctrl.datos.ofertasCurso.tamano(); k++) {
                            auto& of = ctrl.datos.ofertasCurso.obtener(k);
                            if (of.idOfertaCurso && *of.idOfertaCurso == *dm.idOfertaCurso) {
                                grupo = of.grupo ? *of.grupo : "01";
                                if (of.idCurso) {
                                    for (int cIdx = 0; cIdx < ctrl.datos.cursos.tamano(); cIdx++) {
                                        auto& c = ctrl.datos.cursos.obtener(cIdx);
                                        if (c.idCurso && *c.idCurso == *of.idCurso) {
                                            nomCurso = (c.nombre ? *c.nombre : "Asignatura") + " (Gr. " + grupo + ")";
                                            creditos = c.numeroCreditos ? *c.numeroCreditos : 3;
                                            break;
                                        }
                                    }
                                }
                                break;
                            }
                        }
                    }

                    std::string estStr = dm.estadoCurso ? to_string(*dm.estadoCurso) : "EN_CURSO";
                    bool cancelada = (dm.estadoCurso && *dm.estadoCurso == EstadoCurso::CANCELADO);

                    ImGui::TableNextRow();
                    ImGui::TableNextColumn();
                    ImGui::Text("INS-%d", dm.idDetalleMatricula.value_or(0));

                    ImGui::TableNextColumn();
                    ImGui::Text("%s", nomEstudiante.c_str());

                    ImGui::TableNextColumn();
                    ImGui::TextColored(tema::WIN_BLUE(), "%s", nomCurso.c_str());

                    ImGui::TableNextColumn();
                    ImGui::Text("%d cr.", creditos);

                    ImGui::TableNextColumn();
                    if (cancelada) {
                        ImGui::TextColored(tema::TEXT_MUTED(), "%s", estStr.c_str());
                    } else if (dm.estadoCurso && *dm.estadoCurso == EstadoCurso::APROBADO) {
                        ImGui::TextColored(tema::ACCENT_SUCCESS(), "%s", estStr.c_str());
                    } else if (dm.estadoCurso && *dm.estadoCurso == EstadoCurso::REPROBADO) {
                        ImGui::TextColored(tema::ACCENT_DANGER(), "%s", estStr.c_str());
                    } else {
                        ImGui::TextColored(tema::WIN_BLUE(), "%s", estStr.c_str());
                    }

                    ImGui::TableNextColumn();
                    if (dm.notaFinal) {
                        float nf = static_cast<float>(*dm.notaFinal);
                        ImVec4 colorNota = (nf < 3.0f) ? tema::ACCENT_DANGER() : tema::ACCENT_SUCCESS();
                        ImGui::TextColored(colorNota, "%.2f", nf);
                    } else {
                        ImGui::TextColored(tema::TEXT_MUTED(), "Sin nota");
                    }

                    ImGui::TableNextColumn();
                    if (!cancelada) {
                        ImGui::PushID(dm.idDetalleMatricula.value_or(i));
                        ImGui::PushStyleColor(ImGuiCol_Button, tema::ACCENT_DANGER());
                        ImGui::PushStyleColor(ImGuiCol_ButtonHovered, tema::ACCENT_DANGER_H());
                        if (ImGui::SmallButton("Cancelar")) {
                            try {
                                if (dm.idOfertaCurso) {
                                    ctrl.gestorMatriculas->cancelarCurso(idEstudiante, *dm.idOfertaCurso, "Cancelacion desde interfaz");
                                    ctrl.guardarDatos();
                                    ctrl.setMensaje("Asignatura cancelada correctamente.");
                                }
                            } catch (const std::exception& ex) {
                                ctrl.setMensaje(ex.what(), true);
                            }
                        }
                        ImGui::PopStyleColor(2);
                        ImGui::PopID();
                    } else {
                        ImGui::TextColored(tema::TEXT_MUTED(), "Cancelada");
                    }
                }
                ImGui::EndTable();
            }
            ImGui::EndTabItem();
        }

        // Tab Evaluaciones y Calificaciones
        if (ImGui::BeginTabItem("Evaluaciones y Calificaciones")) {
            ImGui::Spacing();

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

            if (ImGui::BeginTabBar("##SubTabsEvaluacionesCalificaciones")) {

                // Sub-tab A: Evaluaciones Programadas
                if (ImGui::BeginTabItem("Evaluaciones Programadas")) {
                    ImGui::Spacing();
                    if (ctrl.datos.evaluaciones.tamano() == 0) {
                        ImGui::TextColored(tema::TEXT_MUTED(), "No hay evaluaciones programadas registradas.");
                    } else {
                        if (ImGui::BeginTable("##TablaEvaluacionesProgramadas", 6,
                            ImGuiTableFlags_RowBg | ImGuiTableFlags_BordersOuter | ImGuiTableFlags_BordersInnerH |
                            ImGuiTableFlags_Resizable | ImGuiTableFlags_ScrollY, ImVec2(0, 0))) {

                            ImGui::TableSetupColumn("ID", ImGuiTableColumnFlags_WidthFixed, 50);
                            ImGui::TableSetupColumn("Nombre de Evaluacion", ImGuiTableColumnFlags_WidthStretch);
                            ImGui::TableSetupColumn("Porcentaje", ImGuiTableColumnFlags_WidthFixed, 90);
                            ImGui::TableSetupColumn("Curso / Oferta", ImGuiTableColumnFlags_WidthStretch);
                            ImGui::TableSetupColumn("Tipo", ImGuiTableColumnFlags_WidthFixed, 100);
                            ImGui::TableSetupColumn("Fecha Limite", ImGuiTableColumnFlags_WidthFixed, 110);
                            ImGui::TableHeadersRow();

                            for (int i = 0; i < ctrl.datos.evaluaciones.tamano(); i++) {
                                auto& ev = ctrl.datos.evaluaciones.obtener(i);
                                ImGui::TableNextRow();

                                ImGui::TableNextColumn();
                                ImGui::Text("%d", ev.idEvaluacion.value_or(0));

                                ImGui::TableNextColumn();
                                ImGui::TextColored(tema::TEXT_MAIN(), "%s", ev.nombre ? ev.nombre->c_str() : "---");

                                ImGui::TableNextColumn();
                                ImGui::TextColored(tema::ACCENT_WARNING(), "%.1f%%", ev.porcentaje.value_or(0.0));

                                ImGui::TableNextColumn();
                                ImGui::Text("%s", getDescripcionOferta(ctrl, ev.idOfertaCurso.value_or(0)).c_str());

                                ImGui::TableNextColumn();
                                ImGui::Text("%s", ev.tipo ? ev.tipo->c_str() : "---");

                                ImGui::TableNextColumn();
                                ImGui::Text("%s", ev.fechaProgramada ? ev.fechaProgramada->c_str() : "N/D");
                            }
                            ImGui::EndTable();
                        }
                    }
                    ImGui::EndTabItem();
                }

                // Sub-tab B: Calificaciones Registradas
                if (ImGui::BeginTabItem("Calificaciones Registradas")) {
                    ImGui::Spacing();
                    if (ctrl.datos.calificaciones.tamano() == 0) {
                        ImGui::TextColored(tema::TEXT_MUTED(), "No hay calificaciones registradas aun.");
                    } else {
                        if (ImGui::BeginTable("##TablaCalificacionesDetalle", 7,
                            ImGuiTableFlags_RowBg | ImGuiTableFlags_BordersOuter | ImGuiTableFlags_BordersInnerH |
                            ImGuiTableFlags_Resizable | ImGuiTableFlags_ScrollY, ImVec2(0, 0))) {

                            ImGui::TableSetupColumn("ID", ImGuiTableColumnFlags_WidthFixed, 45);
                            ImGui::TableSetupColumn("Inscripcion / Estudiante", ImGuiTableColumnFlags_WidthStretch);
                            ImGui::TableSetupColumn("Evaluacion", ImGuiTableColumnFlags_WidthStretch);
                            ImGui::TableSetupColumn("Calificacion", ImGuiTableColumnFlags_WidthFixed, 95);
                            ImGui::TableSetupColumn("Fecha Registro", ImGuiTableColumnFlags_WidthFixed, 110);
                            ImGui::TableSetupColumn("Estado", ImGuiTableColumnFlags_WidthFixed, 90);
                            ImGui::TableSetupColumn("Acciones", ImGuiTableColumnFlags_WidthFixed, 160);
                            ImGui::TableHeadersRow();

                            for (int i = 0; i < ctrl.datos.calificaciones.tamano(); i++) {
                                auto& cal = ctrl.datos.calificaciones.obtener(i);
                                int idCal = cal.idCalificacion.value_or(0);
                                ImGui::TableNextRow();

                                ImGui::TableNextColumn();
                                ImGui::Text("%d", idCal);

                                ImGui::TableNextColumn();
                                ImGui::Text("%s", getDescripcionDetalleMatricula(ctrl, cal.idDetalleMatricula.value_or(0)).c_str());

                                ImGui::TableNextColumn();
                                ImGui::Text("%s", getDescripcionEvaluacion(ctrl, cal.idEvaluacion.value_or(0)).c_str());

                                ImGui::TableNextColumn();
                                double valNota = cal.nota.value_or(0.0);
                                ImVec4 cNota = (valNota < 3.0) ? tema::ACCENT_DANGER() : tema::ACCENT_SUCCESS();
                                ImGui::TextColored(cNota, "%.2f", valNota);

                                ImGui::TableNextColumn();
                                ImGui::Text("%s", cal.fechaRegistro ? cal.fechaRegistro->c_str() : "---");

                                ImGui::TableNextColumn();
                                if (valNota >= 3.0) {
                                    ImGui::PushStyleColor(ImGuiCol_Button, tema::BADGE_ACTIVE_BG());
                                    ImGui::PushStyleColor(ImGuiCol_Text, tema::BADGE_ACTIVE_TXT());
                                    ImGui::SmallButton("APROBADO");
                                    ImGui::PopStyleColor(2);
                                } else {
                                    ImGui::PushStyleColor(ImGuiCol_Button, tema::BADGE_EBRA_BG());
                                    ImGui::PushStyleColor(ImGuiCol_Text, tema::BADGE_EBRA_TXT());
                                    ImGui::SmallButton("REPROBADO");
                                    ImGui::PopStyleColor(2);
                                }

                                // Acciones: Editar Nota y Limpiar / Eliminar Nota
                                ImGui::TableNextColumn();
                                ImGui::PushID(idCal);
                                if (ImGui::SmallButton("Editar")) {
                                    abrirModalEditarNota(idCal);
                                }
                                ImGui::SameLine();
                                ImGui::PushStyleColor(ImGuiCol_Button, tema::ACCENT_DANGER());
                                ImGui::PushStyleColor(ImGuiCol_ButtonHovered, tema::ACCENT_DANGER_H());
                                if (ImGui::SmallButton("Limpiar")) {
                                    eliminarCalificacion(idCal);
                                }
                                ImGui::PopStyleColor(2);
                                ImGui::PopID();
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

        // Tab Alertas EBRA
        if (ImGui::BeginTabItem("Alertas EBRA")) {
            ImGui::Spacing();

            // KPIs EBRA
            int totalEst = static_cast<int>(ctrl.datos.estudiantes.tamano());
            int enRiesgoEbra = 0;
            double sumaPromedios = 0.0;
            int estConPromedio = 0;

            for (int i = 0; i < totalEst; i++) {
                auto& e = ctrl.datos.estudiantes.obtener(i);
                double prom = e.promedioAcumulado.value_or(0.0);
                if (prom > 0.0) {
                    sumaPromedios += prom;
                    estConPromedio++;
                }
                if ((e.estadoAcademico && *e.estadoAcademico == EstadoAcademico::EBRA) || (prom > 0.0 && prom < 3.0)) {
                    enRiesgoEbra++;
                }
            }
            int normales = totalEst - enRiesgoEbra;
            double promGlobal = (estConPromedio > 0) ? (sumaPromedios / estConPromedio) : 0.0;

            char bufTot[32], bufNorm[32], bufSubNorm[48], bufEbra[32], bufSubEbra[48], bufProm[32];
            snprintf(bufTot, sizeof(bufTot), "%d", totalEst);
            snprintf(bufNorm, sizeof(bufNorm), "%d", normales);
            snprintf(bufSubNorm, sizeof(bufSubNorm), "%.1f%% del total", totalEst > 0 ? (normales * 100.0 / totalEst) : 100.0);
            snprintf(bufEbra, sizeof(bufEbra), "%d", enRiesgoEbra);
            snprintf(bufSubEbra, sizeof(bufSubEbra), "%.1f%% en riesgo critico", totalEst > 0 ? (enRiesgoEbra * 100.0 / totalEst) : 0.0);
            snprintf(bufProm, sizeof(bufProm), "%.2f / 5.0", promGlobal);

            if (ImGui::BeginTable("##GridKPIEBRA", 4, ImGuiTableFlags_SizingStretchSame)) {
                ImGui::TableNextColumn();
                tarjetaKPI("TOTAL ESTUDIANTES", bufTot, tema::WIN_BLUE(), "Estudiantes inscritos");

                ImGui::TableNextColumn();
                tarjetaKPI("NORMALIDAD ACADEMICA", bufNorm, tema::ACCENT_SUCCESS(), bufSubNorm);

                ImGui::TableNextColumn();
                tarjetaKPI("EN RIESGO EBRA", bufEbra, enRiesgoEbra > 0 ? tema::ACCENT_DANGER() : tema::ACCENT_SUCCESS(), bufSubEbra);

                ImGui::TableNextColumn();
                tarjetaKPI("PROMEDIO GENERAL", bufProm, tema::ACCENT_WARNING(), "Promedio institucional");

                ImGui::EndTable();
            }

            ImGui::Spacing(); ImGui::Spacing();

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

            if (ImGui::BeginTable("##TablaAlertas", 6,
                ImGuiTableFlags_RowBg | ImGuiTableFlags_BordersOuter | ImGuiTableFlags_BordersInnerH |
                ImGuiTableFlags_Resizable | ImGuiTableFlags_ScrollY, ImVec2(0, 0))) {

                ImGui::TableSetupColumn("ID", ImGuiTableColumnFlags_WidthFixed, 50);
                ImGui::TableSetupColumn("Estudiante", ImGuiTableColumnFlags_WidthStretch);
                ImGui::TableSetupColumn("Tipo de Alerta", ImGuiTableColumnFlags_WidthFixed, 120);
                ImGui::TableSetupColumn("Motivo / Diagnostico", ImGuiTableColumnFlags_WidthStretch);
                ImGui::TableSetupColumn("Fecha Generacion", ImGuiTableColumnFlags_WidthFixed, 110);
                ImGui::TableSetupColumn("Accion Recomendada", ImGuiTableColumnFlags_WidthFixed, 160);
                ImGui::TableHeadersRow();

                for (int i = 0; i < ctrl.datos.alertasAcademicas.tamano(); i++) {
                    auto& a = ctrl.datos.alertasAcademicas.obtener(i);
                    ImGui::TableNextRow();
                    ImGui::TableNextColumn(); ImGui::Text("%d", a.idAlerta ? *a.idAlerta : 0);
                    ImGui::TableNextColumn();
                    ImGui::Text("%s", getNombreEstudianteConCodigo(ctrl, a.idEstudiante.value_or(0)).c_str());
                    ImGui::TableNextColumn();
                    ImGui::TextColored(tema::ACCENT_DANGER(), "%s", a.tipoAlerta ? a.tipoAlerta->c_str() : "EBRA");
                    ImGui::TableNextColumn(); ImGui::Text("%s", a.motivo ? a.motivo->c_str() : "Bajo Rendimiento");
                    ImGui::TableNextColumn(); ImGui::Text("%s", a.fechaGeneracion ? a.fechaGeneracion->c_str() : "---");
                    ImGui::TableNextColumn();
                    ImGui::TextColored(tema::ACCENT_WARNING(), "Plan Tutoria UPC");
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
        ImGui::InputInt("Horas Teoricas Semanales", &curHorasTeoricas);
        if (curHorasTeoricas < 0) curHorasTeoricas = 0;
        ImGui::InputInt("Horas Practicas Semanales", &curHorasPracticas);
        if (curHorasPracticas < 0) curHorasPracticas = 0;
        ImGui::InputFloat("Nota Minima Aprobatoria", &curNotaMinima, 0.1f, 0.5f, "%.1f");
        if (curNotaMinima < 0.0f) curNotaMinima = 3.0f;
        ImGui::InputInt("Cupo Sugerido", &curCupoSugerido);
        if (curCupoSugerido < 1) curCupoSugerido = 30;

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
                c.horasTeoricas = curHorasTeoricas;
                c.horasPracticas = curHorasPracticas;
                c.cupoSugerido = curCupoSugerido;
                c.notaMinimaAprobatoria = curNotaMinima > 0.0f ? curNotaMinima : 3.0;
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
    ImGui::SetNextWindowSize(ImVec2(620, 0), ImGuiCond_Always);

    if (ImGui::BeginPopupModal("Matricular Curso", &modalMatriculaAbierto, ImGuiWindowFlags_AlwaysAutoResize)) {
        if (strlen(mensajeModal) > 0) {
            ImGui::TextColored(errorModal ? tema::ACCENT_DANGER() : tema::ACCENT_SUCCESS(), "%s", mensajeModal);
            ImGui::Separator();
        }

        // Selector Estudiante
        std::string previewEst = getNombreEstudiante(ctrl, matEstudianteId);
        if (ImGui::BeginCombo("Estudiante *", previewEst.c_str())) {
            for (int i = 0; i < ctrl.datos.estudiantes.tamano(); i++) {
                auto& est = ctrl.datos.estudiantes.obtener(i);
                if (est.estado && *est.estado == "INACTIVO") continue;
                bool isSelected = (est.idEstudiante && *est.idEstudiante == matEstudianteId);
                std::string label = getNombreEstudiante(ctrl, est.idEstudiante.value_or(0));
                if (ImGui::Selectable(label.c_str(), isSelected)) {
                    matEstudianteId = est.idEstudiante.value_or(1);
                }
                if (isSelected) ImGui::SetItemDefaultFocus();
            }
            ImGui::EndCombo();
        }

        // Selector Oferta
        std::string previewOf = getDescripcionOferta(ctrl, matOfertaId);
        if (ImGui::BeginCombo("Oferta de Asignatura *", previewOf.c_str())) {
            for (int i = 0; i < ctrl.datos.ofertasCurso.tamano(); i++) {
                auto& of = ctrl.datos.ofertasCurso.obtener(i);
                bool isSelected = (of.idOfertaCurso && *of.idOfertaCurso == matOfertaId);
                std::string label = getDescripcionOferta(ctrl, of.idOfertaCurso.value_or(0));
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
    ImGui::SetNextWindowSize(ImVec2(680, 0), ImGuiCond_Always);

    if (ImGui::BeginPopupModal("Registrar Calificacion", &modalNotaAbierto, ImGuiWindowFlags_AlwaysAutoResize)) {
        if (strlen(mensajeModal) > 0) {
            ImGui::TextColored(errorModal ? tema::ACCENT_DANGER() : tema::ACCENT_SUCCESS(), "%s", mensajeModal);
            ImGui::Separator();
        }

        // Selector Detalle Matricula
        std::string previewDet = getDescripcionDetalleMatricula(ctrl, notaDetalleMatriculaId);
        if (ImGui::BeginCombo("Inscripcion / Alumno *", previewDet.c_str())) {
            for (int i = 0; i < ctrl.datos.detallesMatricula.tamano(); i++) {
                auto& dm = ctrl.datos.detallesMatricula.obtener(i);
                if (dm.estadoCurso && *dm.estadoCurso == EstadoCurso::CANCELADO) continue;
                bool isSelected = (dm.idDetalleMatricula && *dm.idDetalleMatricula == notaDetalleMatriculaId);
                std::string label = getDescripcionDetalleMatricula(ctrl, dm.idDetalleMatricula.value_or(0));
                if (ImGui::Selectable(label.c_str(), isSelected)) {
                    notaDetalleMatriculaId = dm.idDetalleMatricula.value_or(1);
                    // Preseleccionar evaluacion correspondiente si existe
                    if (dm.idOfertaCurso) {
                        for (int k = 0; k < ctrl.datos.evaluaciones.tamano(); k++) {
                            auto& ev = ctrl.datos.evaluaciones.obtener(k);
                            if (ev.idOfertaCurso && *ev.idOfertaCurso == *dm.idOfertaCurso) {
                                notaEvaluacionId = ev.idEvaluacion.value_or(notaEvaluacionId);
                                break;
                            }
                        }
                    }
                }
                if (isSelected) ImGui::SetItemDefaultFocus();
            }
            ImGui::EndCombo();
        }

        // Selector Evaluacion
        std::string previewEv = getDescripcionEvaluacion(ctrl, notaEvaluacionId);
        if (ImGui::BeginCombo("Evaluacion *", previewEv.c_str())) {
            for (int i = 0; i < ctrl.datos.evaluaciones.tamano(); i++) {
                auto& ev = ctrl.datos.evaluaciones.obtener(i);
                bool isSelected = (ev.idEvaluacion && *ev.idEvaluacion == notaEvaluacionId);
                std::string label = getDescripcionEvaluacion(ctrl, ev.idEvaluacion.value_or(0));
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
            try {
                if (ctrl.gestorCalificaciones) {
                    ctrl.gestorCalificaciones->registrarCalificacion(notaEvaluacionId, notaDetalleMatriculaId, notaValor);
                    ctrl.gestorCalificaciones->recalcularNotaFinal(notaDetalleMatriculaId);
                } else {
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
                }
                ctrl.guardarDatos();
                ctrl.setMensaje("Calificacion registrada correctamente.");
                modalNotaAbierto = false;
                ImGui::CloseCurrentPopup();
            } catch (const std::exception& e) {
                strncpy(mensajeModal, e.what(), sizeof(mensajeModal) - 1);
                errorModal = true;
            }
        }

        ImGui::SameLine();
        if (ImGui::Button("Cancelar", ImVec2(120, 0))) {
            modalNotaAbierto = false;
            ImGui::CloseCurrentPopup();
        }

        ImGui::EndPopup();
    }
}

void PITAApp::renderModalPeriodoAcademico() {
    if (modalPeriodoAcademicoAbierto) {
        ImGui::OpenPopup("Aperturar Periodo Academico");
    }

    ImVec2 center = ImGui::GetMainViewport()->GetCenter();
    ImGui::SetNextWindowPos(center, ImGuiCond_Appearing, ImVec2(0.5f, 0.5f));
    ImGui::SetNextWindowSize(ImVec2(520, 0), ImGuiCond_Always);

    if (ImGui::BeginPopupModal("Aperturar Periodo Academico", &modalPeriodoAcademicoAbierto, ImGuiWindowFlags_AlwaysAutoResize)) {
        if (strlen(mensajeModal) > 0) {
            ImGui::TextColored(errorModal ? tema::ACCENT_DANGER() : tema::ACCENT_SUCCESS(), "%s", mensajeModal);
            ImGui::Separator();
        }

        ImGui::InputText("Codigo Periodo *", perAcadCodigo, sizeof(perAcadCodigo));
        ImGui::InputText("Nombre Descriptivo *", perAcadNombre, sizeof(perAcadNombre));
        ImGui::InputText("Fecha Inicio (YYYY-MM-DD) *", perAcadFechaInicio, sizeof(perAcadFechaInicio));
        ImGui::InputText("Fecha Fin (YYYY-MM-DD) *", perAcadFechaFin, sizeof(perAcadFechaFin));

        const char* estadosPer[] = { "PLANIFICACION", "MATRICULAS", "EN_CURSO", "FINALIZADO" };
        ImGui::Combo("Estado Inicial", &perAcadEstadoIdx, estadosPer, IM_ARRAYSIZE(estadosPer));

        ImGui::Spacing();
        ImGui::Separator();

        if (ImGui::Button("Crear Periodo", ImVec2(140, 0))) {
            if (strlen(perAcadCodigo) == 0 || strlen(perAcadNombre) == 0) {
                strncpy(mensajeModal, "Debe ingresar codigo y nombre del periodo.", sizeof(mensajeModal) - 1);
                errorModal = true;
            } else {
                int maxId = 0;
                for (size_t i = 0; i < ctrl.datos.periodosAcademicos.tamano(); ++i) {
                    auto& p = ctrl.datos.periodosAcademicos.obtener(i);
                    if (p.idPeriodo && *p.idPeriodo > maxId) maxId = *p.idPeriodo;
                }
                PeriodoAcademico np;
                np.idPeriodo = maxId + 1;
                np.codigo = std::string(perAcadCodigo);
                np.nombre = std::string(perAcadNombre);
                np.fechaInicio = std::string(perAcadFechaInicio);
                np.fechaFin = std::string(perAcadFechaFin);
                np.estado = std::string(estadosPer[perAcadEstadoIdx]);

                ctrl.datos.periodosAcademicos.push_back(np);
                ctrl.guardarDatos();
                ctrl.setMensaje("Periodo academico creado exitosamente.");
                modalPeriodoAcademicoAbierto = false;
                ImGui::CloseCurrentPopup();
            }
        }

        ImGui::SameLine();
        if (ImGui::Button("Cancelar", ImVec2(120, 0))) {
            modalPeriodoAcademicoAbierto = false;
            ImGui::CloseCurrentPopup();
        }

        ImGui::EndPopup();
    }
}

void PITAApp::renderModalPlanEstudio() {
    if (modalPlanEstudioAbierto) {
        ImGui::OpenPopup("Crear Plan de Estudio");
    }

    ImVec2 center = ImGui::GetMainViewport()->GetCenter();
    ImGui::SetNextWindowPos(center, ImGuiCond_Appearing, ImVec2(0.5f, 0.5f));
    ImGui::SetNextWindowSize(ImVec2(600, 0), ImGuiCond_Always);

    if (ImGui::BeginPopupModal("Crear Plan de Estudio", &modalPlanEstudioAbierto, ImGuiWindowFlags_AlwaysAutoResize)) {
        if (strlen(mensajeModal) > 0) {
            ImGui::TextColored(errorModal ? tema::ACCENT_DANGER() : tema::ACCENT_SUCCESS(), "%s", mensajeModal);
            ImGui::Separator();
        }

        ImGui::InputText("Codigo Plan *", planCodigo, sizeof(planCodigo));
        ImGui::InputText("Nombre del Plan *", planNombre, sizeof(planNombre));
        ImGui::InputText("Version *", planVersion, sizeof(planVersion));
        ImGui::InputInt("Total Creditos Exigidos *", &planTotalCreditos);

        // Selector de Programa
        std::string previewProg = "Seleccionar Programa";
        for (size_t i = 0; i < ctrl.datos.programas.tamano(); ++i) {
            auto& prg = ctrl.datos.programas.obtener(i);
            if (prg.idPrograma && *prg.idPrograma == planProgramaId) {
                previewProg = prg.nombre ? *prg.nombre : ("Prog #" + std::to_string(planProgramaId));
                break;
            }
        }

        if (ImGui::BeginCombo("Programa Academico *", previewProg.c_str())) {
            for (size_t i = 0; i < ctrl.datos.programas.tamano(); ++i) {
                auto& prg = ctrl.datos.programas.obtener(i);
                int idPrg = prg.idPrograma ? *prg.idPrograma : 0;
                bool isSel = (idPrg == planProgramaId);
                std::string lbl = prg.nombre ? *prg.nombre : ("Programa #" + std::to_string(idPrg));
                if (ImGui::Selectable(lbl.c_str(), isSel)) {
                    planProgramaId = idPrg;
                }
                if (isSel) ImGui::SetItemDefaultFocus();
            }
            ImGui::EndCombo();
        }

        ImGui::Spacing();
        ImGui::Separator();

        if (ImGui::Button("Crear Plan", ImVec2(140, 0))) {
            if (strlen(planCodigo) == 0 || strlen(planNombre) == 0) {
                strncpy(mensajeModal, "Debe ingresar codigo y nombre del plan.", sizeof(mensajeModal) - 1);
                errorModal = true;
            } else {
                int maxId = 0;
                for (size_t i = 0; i < ctrl.datos.planesEstudio.tamano(); ++i) {
                    auto& p = ctrl.datos.planesEstudio.obtener(i);
                    if (p.idPlanEstudio && *p.idPlanEstudio > maxId) maxId = *p.idPlanEstudio;
                }
                PlanEstudio np;
                np.idPlanEstudio = maxId + 1;
                np.codigo = std::string(planCodigo);
                np.nombre = std::string(planNombre);
                np.version = std::string(planVersion);
                np.totalCreditos = planTotalCreditos;
                np.idPrograma = planProgramaId;
                np.estado = "VIGENTE";

                ctrl.datos.planesEstudio.push_back(np);
                ctrl.guardarDatos();
                ctrl.setMensaje("Plan de estudio creado exitosamente.");
                modalPlanEstudioAbierto = false;
                ImGui::CloseCurrentPopup();
            }
        }

        ImGui::SameLine();
        if (ImGui::Button("Cancelar", ImVec2(120, 0))) {
            modalPlanEstudioAbierto = false;
            ImGui::CloseCurrentPopup();
        }

        ImGui::EndPopup();
    }
}

void PITAApp::renderModalMallaCurricular() {
    if (modalMallaCurricularAbierto) {
        ImGui::OpenPopup("Malla Curricular - Plan de Estudios");
    }

    ImVec2 center = ImGui::GetMainViewport()->GetCenter();
    ImGui::SetNextWindowPos(center, ImGuiCond_Appearing, ImVec2(0.5f, 0.5f));
    ImGui::SetNextWindowSize(ImVec2(850, 620), ImGuiCond_Always);

    if (ImGui::BeginPopupModal("Malla Curricular - Plan de Estudios", &modalMallaCurricularAbierto)) {
        PlanEstudio* plan = nullptr;
        for (size_t i = 0; i < ctrl.datos.planesEstudio.tamano(); ++i) {
            auto& p = ctrl.datos.planesEstudio.obtener(i);
            if (p.idPlanEstudio && *p.idPlanEstudio == planSeleccionadoId) {
                plan = &p;
                break;
            }
        }

        if (!plan) {
            ImGui::TextColored(tema::ACCENT_DANGER(), "No se encontro el plan de estudio seleccionado.");
            if (ImGui::Button("Cerrar", ImVec2(120, 0))) {
                modalMallaCurricularAbierto = false;
                ImGui::CloseCurrentPopup();
            }
            ImGui::EndPopup();
            return;
        }

        // Encabezado del Plan
        std::string codPlan = plan->codigo.value_or("PLAN");
        std::string nomPlan = plan->nombre.value_or("Plan de Estudio");
        int totCredPlan = plan->totalCreditos.value_or(160);

        ImGui::TextColored(tema::TEXT_MAIN(), "%s [%s]", nomPlan.c_str(), codPlan.c_str());
        ImGui::TextColored(tema::TEXT_MUTED(), "Version: %s | Creditos Totales Requeridos: %d",
                           plan->version.value_or("1.0").c_str(), totCredPlan);
        ImGui::Spacing();

        if (ImGui::Button("+ Asignar Asignatura a Semestre", ImVec2(240, 30))) {
            planCursoSemestre = 1;
            planCursoTipoIdx = 0;
            if (ctrl.datos.cursos.tamano() > 0) {
                planCursoId = ctrl.datos.cursos.obtener(0).idCurso.value_or(1);
            }
            modalAsignarCursoPlanAbierto = true;
        }
        ImGui::Spacing();
        ImGui::Separator();
        ImGui::Spacing();

        // Malla dividida por semestres (1 a 10)
        int creditosAcumulados = 0;
        int totalAsignaturas = 0;

        ImGui::BeginChild("##ScrollMallaCurricular", ImVec2(0, 430), true);

        for (int sem = 1; sem <= 10; ++sem) {
            std::vector<DetallePlanEstudio*> cursosSemestre;
            int creditosSemestre = 0;

            for (size_t i = 0; i < ctrl.datos.detallesPlanEstudio.tamano(); ++i) {
                auto& d = ctrl.datos.detallesPlanEstudio.obtener(i);
                if (d.idPlanEstudio && *d.idPlanEstudio == planSeleccionadoId &&
                    d.semestreSugerido && *d.semestreSugerido == sem) {
                    cursosSemestre.push_back(&d);
                    creditosSemestre += d.numeroCreditos.value_or(3);
                }
            }

            if (cursosSemestre.empty() && sem > 2) {
                // Solo mostrar semestres vacíos hasta el 2 para no saturar si es un plan corto
                continue;
            }

            creditosAcumulados += creditosSemestre;
            totalAsignaturas += static_cast<int>(cursosSemestre.size());

            std::string headerLabel = "Semestre " + std::to_string(sem) +
                                      " (" + std::to_string(cursosSemestre.size()) + " asignaturas, " +
                                      std::to_string(creditosSemestre) + " creditos)";

            if (ImGui::CollapsingHeader(headerLabel.c_str(), ImGuiTreeNodeFlags_DefaultOpen)) {
                if (cursosSemestre.empty()) {
                    ImGui::TextColored(tema::TEXT_MUTED(), "   No hay asignaturas registradas en este semestre.");
                } else {
                    std::string idTabla = "##TablaSemestre" + std::to_string(sem);
                    if (ImGui::BeginTable(idTabla.c_str(), 6,
                        ImGuiTableFlags_RowBg | ImGuiTableFlags_BordersOuter | ImGuiTableFlags_BordersInnerH |
                        ImGuiTableFlags_Resizable)) {

                        ImGui::TableSetupColumn("Codigo", ImGuiTableColumnFlags_WidthFixed, 90);
                        ImGui::TableSetupColumn("Asignatura", ImGuiTableColumnFlags_WidthStretch);
                        ImGui::TableSetupColumn("Creditos", ImGuiTableColumnFlags_WidthFixed, 75);
                        ImGui::TableSetupColumn("Tipo", ImGuiTableColumnFlags_WidthFixed, 100);
                        ImGui::TableSetupColumn("Prerrequisitos", ImGuiTableColumnFlags_WidthStretch);
                        ImGui::TableSetupColumn("Accion", ImGuiTableColumnFlags_WidthFixed, 80);
                        ImGui::TableHeadersRow();

                        for (auto* det : cursosSemestre) {
                            int idCur = det->idCurso.value_or(0);
                            std::string codCurso = "---";
                            std::string nomCurso = "Curso #" + std::to_string(idCur);
                            int cred = det->numeroCreditos.value_or(3);

                            for (size_t cIdx = 0; cIdx < ctrl.datos.cursos.tamano(); ++cIdx) {
                                auto& cur = ctrl.datos.cursos.obtener(cIdx);
                                if (cur.idCurso && *cur.idCurso == idCur) {
                                    codCurso = cur.codigoCurso.value_or("---");
                                    nomCurso = cur.nombre.value_or(nomCurso);
                                    cred = cur.numeroCreditos.value_or(cred);
                                    break;
                                }
                            }

                            // Prerrequisitos de este curso
                            std::string prerreqStr = "Ninguno";
                            for (size_t prIdx = 0; prIdx < ctrl.datos.prerrequisitos.tamano(); ++prIdx) {
                                auto& pr = ctrl.datos.prerrequisitos.obtener(prIdx);
                                if (pr.idCurso && *pr.idCurso == idCur && pr.idCursoRequerido) {
                                    for (size_t c2 = 0; c2 < ctrl.datos.cursos.tamano(); ++c2) {
                                        auto& cur2 = ctrl.datos.cursos.obtener(c2);
                                        if (cur2.idCurso && *cur2.idCurso == *pr.idCursoRequerido) {
                                            if (prerreqStr == "Ninguno") prerreqStr = cur2.codigoCurso.value_or("Req");
                                            else prerreqStr += ", " + cur2.codigoCurso.value_or("Req");
                                            break;
                                        }
                                    }
                                }
                            }

                            ImGui::TableNextRow();
                            ImGui::TableNextColumn(); ImGui::TextColored(tema::WIN_BLUE(), "%s", codCurso.c_str());
                            ImGui::TableNextColumn(); ImGui::Text("%s", nomCurso.c_str());
                            ImGui::TableNextColumn(); ImGui::Text("%d cr.", cred);
                            ImGui::TableNextColumn();
                            std::string tipoC = det->tipoCurso.value_or("OBLIGATORIA");
                            if (tipoC == "OBLIGATORIA") {
                                ImGui::TextColored(tema::ACCENT_WARNING(), "OBLIGATORIA");
                            } else {
                                ImGui::TextColored(tema::WIN_BLUE(), "ELECTIVA");
                            }
                            ImGui::TableNextColumn(); ImGui::TextColored(tema::TEXT_MUTED(), "%s", prerreqStr.c_str());
                            ImGui::TableNextColumn();
                            ImGui::PushID(det->idDetallePlan.value_or(0));
                            if (ImGui::SmallButton("Quitar")) {
                                int idDel = det->idDetallePlan.value_or(0);
                                ctrl.datos.detallesPlanEstudio.remove_if([idDel](const DetallePlanEstudio& dpe) {
                                    return dpe.idDetallePlan.has_value() && *dpe.idDetallePlan == idDel;
                                });
                                ctrl.guardarDatos();
                            }
                            ImGui::PopID();
                        }
                        ImGui::EndTable();
                    }
                }
                ImGui::Spacing();
            }
        }

        ImGui::EndChild();

        ImGui::Spacing();
        ImGui::Separator();
        ImGui::Spacing();

        // Resumen pie de página
        ImGui::TextColored(tema::WIN_BLUE(), "Resumen Malla: %d asignaturas registradas | %d / %d creditos configurados (%.1f%%)",
                           totalAsignaturas, creditosAcumulados, totCredPlan,
                           totCredPlan > 0 ? (creditosAcumulados * 100.0 / totCredPlan) : 0.0);
        ImGui::SameLine();
        ImGui::SetCursorPosX(ImGui::GetWindowWidth() - 130);
        if (ImGui::Button("Cerrar", ImVec2(120, 0))) {
            modalMallaCurricularAbierto = false;
            ImGui::CloseCurrentPopup();
        }

        ImGui::EndPopup();
    }
}

void PITAApp::renderModalAsignarCursoPlan() {
    if (modalAsignarCursoPlanAbierto) {
        ImGui::OpenPopup("Asignar Asignatura a Semestre");
    }

    ImVec2 center = ImGui::GetMainViewport()->GetCenter();
    ImGui::SetNextWindowPos(center, ImGuiCond_Appearing, ImVec2(0.5f, 0.5f));
    ImGui::SetNextWindowSize(ImVec2(550, 0), ImGuiCond_Always);

    if (ImGui::BeginPopupModal("Asignar Asignatura a Semestre", &modalAsignarCursoPlanAbierto, ImGuiWindowFlags_AlwaysAutoResize)) {
        if (strlen(mensajeModal) > 0) {
            ImGui::TextColored(errorModal ? tema::ACCENT_DANGER() : tema::ACCENT_SUCCESS(), "%s", mensajeModal);
            ImGui::Separator();
        }

        // Selector Curso
        std::string previewCur = "Seleccionar Asignatura";
        for (size_t i = 0; i < ctrl.datos.cursos.tamano(); ++i) {
            auto& c = ctrl.datos.cursos.obtener(i);
            if (c.idCurso && *c.idCurso == planCursoId) {
                previewCur = "[" + c.codigoCurso.value_or("---") + "] " + c.nombre.value_or("Curso");
                break;
            }
        }

        if (ImGui::BeginCombo("Asignatura *", previewCur.c_str())) {
            for (size_t i = 0; i < ctrl.datos.cursos.tamano(); ++i) {
                auto& c = ctrl.datos.cursos.obtener(i);
                int idC = c.idCurso.value_or(0);
                bool isSel = (idC == planCursoId);
                std::string lbl = "[" + c.codigoCurso.value_or("---") + "] " + c.nombre.value_or("Curso");
                if (ImGui::Selectable(lbl.c_str(), isSel)) {
                    planCursoId = idC;
                }
                if (isSel) ImGui::SetItemDefaultFocus();
            }
            ImGui::EndCombo();
        }

        ImGui::SliderInt("Semestre Sugerido (1 - 10) *", &planCursoSemestre, 1, 10);

        const char* tiposCurso[] = { "OBLIGATORIA", "ELECTIVA" };
        ImGui::Combo("Tipo de Asignatura", &planCursoTipoIdx, tiposCurso, IM_ARRAYSIZE(tiposCurso));

        ImGui::Spacing();
        ImGui::Separator();

        if (ImGui::Button("Asignar al Plan", ImVec2(140, 0))) {
            int maxId = 0;
            for (size_t i = 0; i < ctrl.datos.detallesPlanEstudio.tamano(); ++i) {
                auto& d = ctrl.datos.detallesPlanEstudio.obtener(i);
                if (d.idDetallePlan && *d.idDetallePlan > maxId) maxId = *d.idDetallePlan;
            }

            int creds = 3;
            for (size_t i = 0; i < ctrl.datos.cursos.tamano(); ++i) {
                auto& c = ctrl.datos.cursos.obtener(i);
                if (c.idCurso && *c.idCurso == planCursoId) {
                    creds = c.numeroCreditos.value_or(3);
                    break;
                }
            }

            DetallePlanEstudio nd;
            nd.idDetallePlan = maxId + 1;
            nd.idPlanEstudio = planSeleccionadoId;
            nd.idCurso = planCursoId;
            nd.semestreSugerido = planCursoSemestre;
            nd.tipoCurso = std::string(tiposCurso[planCursoTipoIdx]);
            nd.numeroCreditos = creds;
            nd.esObligatorio = (planCursoTipoIdx == 0);
            nd.estado = "ACTIVO";

            ctrl.datos.detallesPlanEstudio.push_back(nd);
            ctrl.guardarDatos();
            modalAsignarCursoPlanAbierto = false;
            ImGui::CloseCurrentPopup();
        }

        ImGui::SameLine();
        if (ImGui::Button("Cancelar", ImVec2(120, 0))) {
            modalAsignarCursoPlanAbierto = false;
            ImGui::CloseCurrentPopup();
        }

        ImGui::EndPopup();
    }
}

// ======================================================================
// HELPERS Y ACCIONES ACADÉMICAS (CURSOS, OFERTAS Y CALIFICACIONES)
// ======================================================================

void PITAApp::abrirModalEditarCurso(int idCurso) {
    editCurId = idCurso;
    mensajeModal[0] = '\0';
    errorModal = false;

    for (size_t i = 0; i < ctrl.datos.cursos.tamano(); ++i) {
        auto& c = ctrl.datos.cursos.obtener(i);
        if (c.idCurso && *c.idCurso == idCurso) {
            strncpy(editCurCodigo, c.codigoCurso ? c.codigoCurso->c_str() : "", sizeof(editCurCodigo) - 1);
            editCurCodigo[sizeof(editCurCodigo) - 1] = '\0';

            strncpy(editCurNombre, c.nombre ? c.nombre->c_str() : "", sizeof(editCurNombre) - 1);
            editCurNombre[sizeof(editCurNombre) - 1] = '\0';

            editCurCreditos = c.numeroCreditos.value_or(3);
            editCurHorasTeoricas = c.horasTeoricas.value_or(3);
            editCurHorasPracticas = c.horasPracticas.value_or(2);
            editCurNotaMinima = static_cast<float>(c.notaMinimaAprobatoria.value_or(3.0));
            editCurCupoSugerido = c.cupoSugerido.value_or(30);
            break;
        }
    }
    modalEditarCursoAbierto = true;
}

void PITAApp::eliminarCurso(int idCurso) {
    // Validar si tiene ofertas vigentes
    for (size_t i = 0; i < ctrl.datos.ofertasCurso.tamano(); ++i) {
        auto& of = ctrl.datos.ofertasCurso.obtener(i);
        if (of.idCurso && *of.idCurso == idCurso) {
            ctrl.setMensaje("No se puede eliminar la asignatura porque tiene grupos y ofertas abiertas.", true);
            return;
        }
    }
    // Validar si está en planes de estudio
    for (size_t i = 0; i < ctrl.datos.detallesPlanEstudio.tamano(); ++i) {
        auto& d = ctrl.datos.detallesPlanEstudio.obtener(i);
        if (d.idCurso && *d.idCurso == idCurso) {
            ctrl.setMensaje("No se puede eliminar la asignatura porque esta adscrita a un plan de estudios.", true);
            return;
        }
    }

    ctrl.datos.cursos.remove_if([idCurso](const Curso& c) {
        return c.idCurso.has_value() && *c.idCurso == idCurso;
    });
    ctrl.guardarDatos();
    ctrl.setMensaje("Asignatura eliminada del catalogo correctamente.");
}

void PITAApp::abrirModalNuevaOferta() {
    mensajeModal[0] = '\0';
    errorModal = false;
    if (ctrl.datos.cursos.tamano() > 0) {
        ofCursoId = ctrl.datos.cursos.obtener(0).idCurso.value_or(1);
    }
    if (ctrl.datos.periodosAcademicos.tamano() > 0) {
        ofPeriodoId = ctrl.datos.periodosAcademicos.obtener(0).idPeriodo.value_or(1);
    }
    if (ctrl.datos.profesores.tamano() > 0) {
        ofProfesorId = ctrl.datos.profesores.obtener(0).idProfesor.value_or(1);
    }
    snprintf(ofGrupo, sizeof(ofGrupo), "01");
    snprintf(ofAula, sizeof(ofAula), "Aula 204");
    snprintf(ofSede, sizeof(ofSede), "Sabanas");
    ofCupoMaximo = 35;
    modalNuevaOfertaAbierto = true;
}

void PITAApp::eliminarOferta(int idOfertaCurso) {
    // Validar si tiene inscripciones de estudiantes
    for (size_t i = 0; i < ctrl.datos.detallesMatricula.tamano(); ++i) {
        auto& dm = ctrl.datos.detallesMatricula.obtener(i);
        if (dm.idOfertaCurso && *dm.idOfertaCurso == idOfertaCurso &&
            (!dm.estadoCurso || *dm.estadoCurso != EstadoCurso::CANCELADO)) {
            ctrl.setMensaje("No se puede cerrar la oferta porque tiene estudiantes inscritos.", true);
            return;
        }
    }

    // Remover asignaciones docentes vinculadas
    ctrl.datos.asignacionesDocentes.remove_if([idOfertaCurso](const AsignacionDocente& ad) {
        return ad.idOfertaCurso.has_value() && *ad.idOfertaCurso == idOfertaCurso;
    });

    // Remover la oferta
    ctrl.datos.ofertasCurso.remove_if([idOfertaCurso](const OfertaCurso& oc) {
        return oc.idOfertaCurso.has_value() && *oc.idOfertaCurso == idOfertaCurso;
    });

    ctrl.guardarDatos();
    ctrl.setMensaje("Oferta academica cerrada y eliminada exitosamente.");
}

void PITAApp::abrirModalEditarNota(int idCalificacion) {
    editNotaIdCalificacion = idCalificacion;
    mensajeModal[0] = '\0';
    errorModal = false;

    for (size_t i = 0; i < ctrl.datos.calificaciones.tamano(); ++i) {
        auto& cal = ctrl.datos.calificaciones.obtener(i);
        if (cal.idCalificacion && *cal.idCalificacion == idCalificacion) {
            editNotaNuevoValor = static_cast<float>(cal.nota.value_or(4.0));
            std::string desc = getDescripcionDetalleMatricula(ctrl, cal.idDetalleMatricula.value_or(0));
            strncpy(editNotaDescripcion, desc.c_str(), sizeof(editNotaDescripcion) - 1);
            editNotaDescripcion[sizeof(editNotaDescripcion) - 1] = '\0';
            break;
        }
    }
    modalEditarNotaAbierto = true;
}

void PITAApp::eliminarCalificacion(int idCalificacion) {
    int idDetalle = 0;
    for (size_t i = 0; i < ctrl.datos.calificaciones.tamano(); ++i) {
        auto& c = ctrl.datos.calificaciones.obtener(i);
        if (c.idCalificacion && *c.idCalificacion == idCalificacion) {
            idDetalle = c.idDetalleMatricula.value_or(0);
            break;
        }
    }

    ctrl.datos.calificaciones.remove_if([idCalificacion](const Calificacion& c) {
        return c.idCalificacion.has_value() && *c.idCalificacion == idCalificacion;
    });

    // Actualizar DetalleMatricula correspondiente
    if (idDetalle > 0) {
        for (size_t i = 0; i < ctrl.datos.detallesMatricula.tamano(); ++i) {
            auto& dm = ctrl.datos.detallesMatricula.obtener(i);
            if (dm.idDetalleMatricula && *dm.idDetalleMatricula == idDetalle) {
                dm.notaFinal = std::nullopt;
                dm.estadoCurso = EstadoCurso::EN_CURSO;

                // Recalcular promedio y EBRA del estudiante
                if (dm.idMatricula) {
                    for (size_t j = 0; j < ctrl.datos.matriculas.tamano(); ++j) {
                        auto& m = ctrl.datos.matriculas.obtener(j);
                        if (m.idMatricula && *m.idMatricula == *dm.idMatricula && m.idEstudiante) {
                            int idEst = *m.idEstudiante;
                            if (ctrl.gestorMatriculas) {
                                ctrl.gestorMatriculas->calcularPromedioAcumulado(idEst);
                                ctrl.gestorMatriculas->evaluarEbra(idEst);
                            }
                            break;
                        }
                    }
                }
                break;
            }
        }
    }

    ctrl.guardarDatos();
    ctrl.setMensaje("Calificacion eliminada / restablecida a EN_CURSO.");
}

// ======================================================================
// MODALES EDITAR CURSO, NUEVA OFERTA Y EDITAR NOTA
// ======================================================================

void PITAApp::renderModalEditarCurso() {
    if (modalEditarCursoAbierto) {
        ImGui::OpenPopup("Editar Asignatura");
    }

    ImVec2 center = ImGui::GetMainViewport()->GetCenter();
    ImGui::SetNextWindowPos(center, ImGuiCond_Appearing, ImVec2(0.5f, 0.5f));
    ImGui::SetNextWindowSize(ImVec2(520, 0), ImGuiCond_Always);

    if (ImGui::BeginPopupModal("Editar Asignatura", &modalEditarCursoAbierto, ImGuiWindowFlags_AlwaysAutoResize)) {
        if (strlen(mensajeModal) > 0) {
            ImGui::TextColored(errorModal ? tema::ACCENT_DANGER() : tema::ACCENT_SUCCESS(), "%s", mensajeModal);
            ImGui::Separator();
        }

        ImGui::BeginDisabled(true);
        ImGui::InputText("Codigo de Curso (Identificador)", editCurCodigo, sizeof(editCurCodigo));
        ImGui::EndDisabled();

        ImGui::InputText("Nombre de Asignatura *", editCurNombre, sizeof(editCurNombre));
        ImGui::InputInt("Creditos Academicos *", &editCurCreditos);
        if (editCurCreditos < 1) editCurCreditos = 1;

        ImGui::InputInt("Horas Teoricas Semanales", &editCurHorasTeoricas);
        if (editCurHorasTeoricas < 0) editCurHorasTeoricas = 0;

        ImGui::InputInt("Horas Practicas Semanales", &editCurHorasPracticas);
        if (editCurHorasPracticas < 0) editCurHorasPracticas = 0;

        ImGui::InputFloat("Nota Minima Aprobatoria *", &editCurNotaMinima, 0.1f, 0.5f, "%.1f");
        if (editCurNotaMinima < 0.0f) editCurNotaMinima = 3.0f;

        ImGui::InputInt("Cupo Sugerido de Estudiantes", &editCurCupoSugerido);
        if (editCurCupoSugerido < 1) editCurCupoSugerido = 30;

        ImGui::Spacing();
        ImGui::Separator();

        if (ImGui::Button("Guardar Cambios", ImVec2(150, 0))) {
            if (strlen(editCurNombre) == 0) {
                strncpy(mensajeModal, "El nombre de la asignatura no puede estar vacio.", sizeof(mensajeModal) - 1);
                errorModal = true;
            } else {
                for (size_t i = 0; i < ctrl.datos.cursos.tamano(); ++i) {
                    auto& c = ctrl.datos.cursos.obtener(i);
                    if (c.idCurso && *c.idCurso == editCurId) {
                        c.nombre = std::string(editCurNombre);
                        c.numeroCreditos = editCurCreditos;
                        c.horasTeoricas = editCurHorasTeoricas;
                        c.horasPracticas = editCurHorasPracticas;
                        c.notaMinimaAprobatoria = editCurNotaMinima > 0.0f ? editCurNotaMinima : 3.0;
                        c.cupoSugerido = editCurCupoSugerido;
                        break;
                    }
                }
                ctrl.guardarDatos();
                ctrl.setMensaje("Asignatura actualizada exitosamente.");
                modalEditarCursoAbierto = false;
                ImGui::CloseCurrentPopup();
            }
        }

        ImGui::SameLine();
        if (ImGui::Button("Cancelar", ImVec2(120, 0))) {
            modalEditarCursoAbierto = false;
            ImGui::CloseCurrentPopup();
        }

        ImGui::EndPopup();
    }
}

void PITAApp::renderModalNuevaOferta() {
    if (modalNuevaOfertaAbierto) {
        ImGui::OpenPopup("Abrir Oferta de Asignatura (Grupo)");
    }

    ImVec2 center = ImGui::GetMainViewport()->GetCenter();
    ImGui::SetNextWindowPos(center, ImGuiCond_Appearing, ImVec2(0.5f, 0.5f));
    ImGui::SetNextWindowSize(ImVec2(560, 0), ImGuiCond_Always);

    if (ImGui::BeginPopupModal("Abrir Oferta de Asignatura (Grupo)", &modalNuevaOfertaAbierto, ImGuiWindowFlags_AlwaysAutoResize)) {
        if (strlen(mensajeModal) > 0) {
            ImGui::TextColored(errorModal ? tema::ACCENT_DANGER() : tema::ACCENT_SUCCESS(), "%s", mensajeModal);
            ImGui::Separator();
        }

        // Selector Curso
        std::string previewCur = "Seleccionar Asignatura";
        for (size_t i = 0; i < ctrl.datos.cursos.tamano(); ++i) {
            auto& c = ctrl.datos.cursos.obtener(i);
            if (c.idCurso && *c.idCurso == ofCursoId) {
                previewCur = "[" + c.codigoCurso.value_or("---") + "] " + c.nombre.value_or("Curso");
                break;
            }
        }
        if (ImGui::BeginCombo("Asignatura a Ofertar *", previewCur.c_str())) {
            for (size_t i = 0; i < ctrl.datos.cursos.tamano(); ++i) {
                auto& c = ctrl.datos.cursos.obtener(i);
                int idC = c.idCurso.value_or(0);
                bool isSel = (idC == ofCursoId);
                std::string lbl = "[" + c.codigoCurso.value_or("---") + "] " + c.nombre.value_or("Curso");
                if (ImGui::Selectable(lbl.c_str(), isSel)) {
                    ofCursoId = idC;
                }
                if (isSel) ImGui::SetItemDefaultFocus();
            }
            ImGui::EndCombo();
        }

        // Selector Periodo
        std::string previewPer = "Seleccionar Periodo";
        for (size_t i = 0; i < ctrl.datos.periodosAcademicos.tamano(); ++i) {
            auto& p = ctrl.datos.periodosAcademicos.obtener(i);
            if (p.idPeriodo && *p.idPeriodo == ofPeriodoId) {
                previewPer = p.codigo.value_or("Per") + " (" + p.nombre.value_or("Periodo") + ")";
                break;
            }
        }
        if (ImGui::BeginCombo("Periodo Academico *", previewPer.c_str())) {
            for (size_t i = 0; i < ctrl.datos.periodosAcademicos.tamano(); ++i) {
                auto& p = ctrl.datos.periodosAcademicos.obtener(i);
                int idP = p.idPeriodo.value_or(0);
                bool isSel = (idP == ofPeriodoId);
                std::string lbl = p.codigo.value_or("Per") + " (" + p.nombre.value_or("Periodo") + ")";
                if (ImGui::Selectable(lbl.c_str(), isSel)) {
                    ofPeriodoId = idP;
                }
                if (isSel) ImGui::SetItemDefaultFocus();
            }
            ImGui::EndCombo();
        }

        ImGui::InputText("Grupo *", ofGrupo, sizeof(ofGrupo));
        ImGui::InputInt("Cupo Maximo *", &ofCupoMaximo);
        if (ofCupoMaximo < 1) ofCupoMaximo = 35;

        ImGui::InputText("Aula", ofAula, sizeof(ofAula));
        ImGui::InputText("Sede", ofSede, sizeof(ofSede));

        // Selector Docente asignado
        std::string previewProf = "Sin Asignar";
        for (size_t i = 0; i < ctrl.datos.profesores.tamano(); ++i) {
            auto& pr = ctrl.datos.profesores.obtener(i);
            if (pr.idProfesor && *pr.idProfesor == ofProfesorId) {
                std::string nomP = "Docente";
                if (pr.idPersona) {
                    for (size_t j = 0; j < ctrl.datos.personas.tamano(); ++j) {
                        auto& per = ctrl.datos.personas.obtener(j);
                        if (per.idPersona && *per.idPersona == *pr.idPersona) {
                            nomP = (per.primerNombre ? *per.primerNombre : "") + " " + (per.primerApellido ? *per.primerApellido : "");
                            break;
                        }
                    }
                }
                previewProf = "[" + pr.codigoProfesor.value_or("DOC") + "] " + nomP;
                break;
            }
        }

        if (ImGui::BeginCombo("Profesor Asignado", previewProf.c_str())) {
            if (ImGui::Selectable("Sin Asignar", ofProfesorId == 0)) {
                ofProfesorId = 0;
            }
            for (size_t i = 0; i < ctrl.datos.profesores.tamano(); ++i) {
                auto& pr = ctrl.datos.profesores.obtener(i);
                int idPr = pr.idProfesor.value_or(0);
                std::string nomP = "Docente";
                if (pr.idPersona) {
                    for (size_t j = 0; j < ctrl.datos.personas.tamano(); ++j) {
                        auto& per = ctrl.datos.personas.obtener(j);
                        if (per.idPersona && *per.idPersona == *pr.idPersona) {
                            nomP = (per.primerNombre ? *per.primerNombre : "") + " " + (per.primerApellido ? *per.primerApellido : "");
                            break;
                        }
                    }
                }
                std::string lbl = "[" + pr.codigoProfesor.value_or("DOC") + "] " + nomP;
                bool isSel = (idPr == ofProfesorId);
                if (ImGui::Selectable(lbl.c_str(), isSel)) {
                    ofProfesorId = idPr;
                }
                if (isSel) ImGui::SetItemDefaultFocus();
            }
            ImGui::EndCombo();
        }

        ImGui::Spacing();
        ImGui::Separator();

        if (ImGui::Button("Crear Oferta", ImVec2(140, 0))) {
            if (ofCursoId <= 0 || ofPeriodoId <= 0 || strlen(ofGrupo) == 0) {
                strncpy(mensajeModal, "Debe seleccionar asignatura, periodo e indicar un grupo.", sizeof(mensajeModal) - 1);
                errorModal = true;
            } else {
                int maxIdOf = 0;
                for (size_t i = 0; i < ctrl.datos.ofertasCurso.tamano(); ++i) {
                    auto& o = ctrl.datos.ofertasCurso.obtener(i);
                    if (o.idOfertaCurso && *o.idOfertaCurso > maxIdOf) maxIdOf = *o.idOfertaCurso;
                }

                OfertaCurso nof;
                nof.idOfertaCurso = maxIdOf + 1;
                nof.idCurso = ofCursoId;
                nof.idPeriodo = ofPeriodoId;
                nof.grupo = std::string(ofGrupo);
                nof.cupoMaximo = ofCupoMaximo;
                nof.cupoDisponible = ofCupoMaximo;
                nof.aula = std::string(ofAula);
                nof.sede = std::string(ofSede);
                nof.modalidad = "PRESENCIAL";
                nof.estado = "ACTIVO";

                ctrl.datos.ofertasCurso.push_back(nof);

                // Si seleccionó docente, crear asignación docente
                if (ofProfesorId > 0) {
                    int maxIdAsig = 0;
                    for (size_t i = 0; i < ctrl.datos.asignacionesDocentes.tamano(); ++i) {
                        auto& a = ctrl.datos.asignacionesDocentes.obtener(i);
                        if (a.idAsignacion && *a.idAsignacion > maxIdAsig) maxIdAsig = *a.idAsignacion;
                    }
                    AsignacionDocente nasig;
                    nasig.idAsignacion = maxIdAsig + 1;
                    nasig.idProfesor = ofProfesorId;
                    nasig.idOfertaCurso = nof.idOfertaCurso;
                    nasig.rolDocente = "TITULAR";
                    nasig.numeroHoras = 4.0;
                    nasig.porcentajeResponsabilidad = 100.0;
                    nasig.fechaAsignacion = "2026-02-01";
                    nasig.estado = "ACTIVO";
                    ctrl.datos.asignacionesDocentes.push_back(nasig);
                }

                ctrl.guardarDatos();
                ctrl.setMensaje("Oferta academica y grupo creados exitosamente.");
                modalNuevaOfertaAbierto = false;
                ImGui::CloseCurrentPopup();
            }
        }

        ImGui::SameLine();
        if (ImGui::Button("Cancelar", ImVec2(120, 0))) {
            modalNuevaOfertaAbierto = false;
            ImGui::CloseCurrentPopup();
        }

        ImGui::EndPopup();
    }
}

void PITAApp::renderModalEditarNota() {
    if (modalEditarNotaAbierto) {
        ImGui::OpenPopup("Editar Calificacion");
    }

    ImVec2 center = ImGui::GetMainViewport()->GetCenter();
    ImGui::SetNextWindowPos(center, ImGuiCond_Appearing, ImVec2(0.5f, 0.5f));
    ImGui::SetNextWindowSize(ImVec2(520, 0), ImGuiCond_Always);

    if (ImGui::BeginPopupModal("Editar Calificacion", &modalEditarNotaAbierto, ImGuiWindowFlags_AlwaysAutoResize)) {
        if (strlen(mensajeModal) > 0) {
            ImGui::TextColored(errorModal ? tema::ACCENT_DANGER() : tema::ACCENT_SUCCESS(), "%s", mensajeModal);
            ImGui::Separator();
        }

        ImGui::TextColored(tema::TEXT_MUTED(), "Inscripcion: %s", editNotaDescripcion);
        ImGui::Spacing();

        ImGui::SliderFloat("Nueva Calificacion (0.0 - 5.0) *", &editNotaNuevoValor, 0.0f, 5.0f, "%.2f");

        ImGui::Spacing();
        ImGui::Separator();

        if (ImGui::Button("Guardar Calificacion", ImVec2(160, 0))) {
            int idDetalle = 0;
            for (size_t i = 0; i < ctrl.datos.calificaciones.tamano(); ++i) {
                auto& cal = ctrl.datos.calificaciones.obtener(i);
                if (cal.idCalificacion && *cal.idCalificacion == editNotaIdCalificacion) {
                    cal.nota = static_cast<double>(editNotaNuevoValor);
                    idDetalle = cal.idDetalleMatricula.value_or(0);
                    break;
                }
            }

            // Recalcular nota final del detalle de matrícula y actualizar estado
            if (idDetalle > 0) {
                if (ctrl.gestorCalificaciones) {
                    ctrl.gestorCalificaciones->recalcularNotaFinal(idDetalle);
                } else {
                    for (size_t i = 0; i < ctrl.datos.detallesMatricula.tamano(); ++i) {
                        auto& dm = ctrl.datos.detallesMatricula.obtener(i);
                        if (dm.idDetalleMatricula && *dm.idDetalleMatricula == idDetalle) {
                            dm.notaFinal = static_cast<double>(editNotaNuevoValor);
                            dm.estadoCurso = (editNotaNuevoValor >= 3.0f) ? EstadoCurso::APROBADO : EstadoCurso::REPROBADO;

                            // Actualizar promedio y EBRA del estudiante
                            if (dm.idMatricula) {
                                for (size_t j = 0; j < ctrl.datos.matriculas.tamano(); ++j) {
                                    auto& m = ctrl.datos.matriculas.obtener(j);
                                    if (m.idMatricula && *m.idMatricula == *dm.idMatricula && m.idEstudiante) {
                                        int idEst = *m.idEstudiante;
                                        if (ctrl.gestorMatriculas) {
                                            ctrl.gestorMatriculas->calcularPromedioAcumulado(idEst);
                                            ctrl.gestorMatriculas->evaluarEbra(idEst);
                                        }
                                        break;
                                    }
                                }
                            }
                            break;
                        }
                    }
                }
            }

            ctrl.guardarDatos();
            ctrl.setMensaje("Calificacion actualizada exitosamente.");
            modalEditarNotaAbierto = false;
            ImGui::CloseCurrentPopup();
        }

        ImGui::SameLine();
        if (ImGui::Button("Cancelar", ImVec2(120, 0))) {
            modalEditarNotaAbierto = false;
            ImGui::CloseCurrentPopup();
        }

        ImGui::EndPopup();
    }
}

} // namespace pita
