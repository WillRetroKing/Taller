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
                        mensajeModal[0] = '\0';
                        errorModal = false;
                        modalCursoAbierto = true;
                    }
                    ImGui::Spacing();

                    if (ImGui::BeginTable("##TablaCursosCatalogo", 7,
                        ImGuiTableFlags_RowBg | ImGuiTableFlags_BordersOuter | ImGuiTableFlags_BordersInnerH |
                        ImGuiTableFlags_Resizable | ImGuiTableFlags_ScrollY, ImVec2(0, 0))) {

                        ImGui::TableSetupColumn("ID", ImGuiTableColumnFlags_WidthFixed, 50);
                        ImGui::TableSetupColumn("Codigo", ImGuiTableColumnFlags_WidthFixed, 90);
                        ImGui::TableSetupColumn("Nombre Asignatura", ImGuiTableColumnFlags_WidthStretch);
                        ImGui::TableSetupColumn("Creditos", ImGuiTableColumnFlags_WidthFixed, 80);
                        ImGui::TableSetupColumn("Horas T / P", ImGuiTableColumnFlags_WidthFixed, 100);
                        ImGui::TableSetupColumn("Nota Minima", ImGuiTableColumnFlags_WidthFixed, 95);
                        ImGui::TableSetupColumn("Cupo Sugerido", ImGuiTableColumnFlags_WidthFixed, 100);
                        ImGui::TableHeadersRow();

                        for (int i = 0; i < ctrl.datos.cursos.tamano(); i++) {
                            auto& c = ctrl.datos.cursos.obtener(i);
                            ImGui::TableNextRow();
                            ImGui::TableNextColumn(); ImGui::Text("%d", c.idCurso ? *c.idCurso : 0);
                            ImGui::TableNextColumn(); ImGui::TextColored(tema::WIN_BLUE(), "%s", c.codigoCurso ? c.codigoCurso->c_str() : "---");
                            ImGui::TableNextColumn(); ImGui::Text("%s", c.nombre ? c.nombre->c_str() : "---");
                            ImGui::TableNextColumn(); ImGui::Text("%d creditos", c.numeroCreditos ? *c.numeroCreditos : 3);
                            ImGui::TableNextColumn(); ImGui::Text("%dh T / %dh P", c.horasTeoricas ? *c.horasTeoricas : 3, c.horasPracticas ? *c.horasPracticas : 2);
                            ImGui::TableNextColumn(); ImGui::Text("%.1f", c.notaMinimaAprobatoria ? *c.notaMinimaAprobatoria : 3.0);
                            ImGui::TableNextColumn(); ImGui::Text("%d cupos", c.cupoSugerido ? *c.cupoSugerido : 30);
                        }
                        ImGui::EndTable();
                    }
                    ImGui::EndTabItem();
                }

                // Sub-tab 2: Ofertas y Grupos Abiertos
                if (ImGui::BeginTabItem("Ofertas y Grupos Abiertos")) {
                    ImGui::Spacing();
                    if (ctrl.datos.ofertasCurso.tamano() == 0) {
                        ImGui::TextColored(tema::TEXT_MUTED(), "No hay ofertas ni grupos abiertos registrados.");
                    } else {
                        if (ImGui::BeginTable("##TablaOfertasGrupos", 7,
                            ImGuiTableFlags_RowBg | ImGuiTableFlags_BordersOuter | ImGuiTableFlags_BordersInnerH |
                            ImGuiTableFlags_Resizable | ImGuiTableFlags_ScrollY, ImVec2(0, 0))) {

                            ImGui::TableSetupColumn("Codigo Oferta", ImGuiTableColumnFlags_WidthFixed, 110);
                            ImGui::TableSetupColumn("Asignatura", ImGuiTableColumnFlags_WidthStretch);
                            ImGui::TableSetupColumn("Periodo", ImGuiTableColumnFlags_WidthFixed, 90);
                            ImGui::TableSetupColumn("Grupo", ImGuiTableColumnFlags_WidthFixed, 70);
                            ImGui::TableSetupColumn("Aula / Sede", ImGuiTableColumnFlags_WidthFixed, 140);
                            ImGui::TableSetupColumn("Cupo Disp / Total", ImGuiTableColumnFlags_WidthFixed, 130);
                            ImGui::TableSetupColumn("Docente Asignado", ImGuiTableColumnFlags_WidthStretch);
                            ImGui::TableHeadersRow();

                            for (int i = 0; i < ctrl.datos.ofertasCurso.tamano(); i++) {
                                auto& of = ctrl.datos.ofertasCurso.obtener(i);
                                ImGui::TableNextRow();

                                // Código
                                ImGui::TableNextColumn();
                                ImGui::TextColored(tema::ACCENT_INDIGO(), "OFER-%d", of.idOfertaCurso ? *of.idOfertaCurso : (i + 1));

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
                        if (ImGui::BeginTable("##TablaCalificacionesDetalle", 6,
                            ImGuiTableFlags_RowBg | ImGuiTableFlags_BordersOuter | ImGuiTableFlags_BordersInnerH |
                            ImGuiTableFlags_Resizable | ImGuiTableFlags_ScrollY, ImVec2(0, 0))) {

                            ImGui::TableSetupColumn("ID", ImGuiTableColumnFlags_WidthFixed, 50);
                            ImGui::TableSetupColumn("Inscripcion / Estudiante", ImGuiTableColumnFlags_WidthStretch);
                            ImGui::TableSetupColumn("Evaluacion", ImGuiTableColumnFlags_WidthStretch);
                            ImGui::TableSetupColumn("Calificacion", ImGuiTableColumnFlags_WidthFixed, 100);
                            ImGui::TableSetupColumn("Fecha Registro", ImGuiTableColumnFlags_WidthFixed, 120);
                            ImGui::TableSetupColumn("Estado", ImGuiTableColumnFlags_WidthFixed, 90);
                            ImGui::TableHeadersRow();

                            for (int i = 0; i < ctrl.datos.calificaciones.tamano(); i++) {
                                auto& cal = ctrl.datos.calificaciones.obtener(i);
                                ImGui::TableNextRow();

                                ImGui::TableNextColumn();
                                ImGui::Text("%d", cal.idCalificacion.value_or(0));

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

} // namespace pita
