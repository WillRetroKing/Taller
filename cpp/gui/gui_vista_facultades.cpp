#define _CRT_SECURE_NO_WARNINGS
#include "gui_app.h"
#include "tema.h"
#include "imgui.h"

#include <cstring>
#include <string>
#include <vector>
#include <algorithm>

namespace pita {

// ======================================================================
// HELPERS DOCENTES Y AUTORIDADES
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

static std::string getNombreDirector(const GUIController& ctrl, std::optional<int> idDirector) {
    if (!idDirector || *idDirector <= 0) return "Sin Director Asignado";
    for (size_t i = 0; i < ctrl.datos.profesores.tamano(); ++i) {
        auto& prof = ctrl.datos.profesores.obtener(i);
        if (prof.idProfesor && *prof.idProfesor == *idDirector) {
            std::string nom = getNombreDocentePersona(ctrl, prof.idPersona.value_or(0));
            std::string cod = prof.codigoProfesor.value_or("");
            return cod.empty() ? nom : (nom + " (" + cod + ")");
        }
    }
    return "Docente #" + std::to_string(*idDirector);
}

static const char* NIVELES_FORMACION[] = {
    "PREGRADO", "POSGRADO", "ESPECIALIZACION", "MAESTRIA", "DOCTORADO", "TECNOLOGIA"
};
static const int TOTAL_NIVELES = IM_ARRAYSIZE(NIVELES_FORMACION);

static const char* MODALIDADES_PROGRAMA[] = {
    "PRESENCIAL", "VIRTUAL", "A DISTANCIA", "DUAL", "HIBRIDA / SEMIPRESENCIAL"
};
static const int TOTAL_MODALIDADES = IM_ARRAYSIZE(MODALIDADES_PROGRAMA);

static const char* ESTADOS_REGISTRO[] = {
    "ACTIVO", "INACTIVO"
};

// ======================================================================
// METODOS AUXILIARES Y GESTION CRUD
// ======================================================================

void PITAApp::abrirModalEditarFacultad(int idFacultad) {
    for (size_t i = 0; i < ctrl.datos.facultades.tamano(); ++i) {
        auto& f = ctrl.datos.facultades.obtener(i);
        if (f.idFacultad && *f.idFacultad == idFacultad) {
            editFacId = idFacultad;
            strncpy(editFacCodigo, f.codigoFacultad ? f.codigoFacultad->c_str() : "", sizeof(editFacCodigo) - 1);
            editFacCodigo[sizeof(editFacCodigo) - 1] = '\0';

            strncpy(editFacNombre, f.nombre ? f.nombre->c_str() : "", sizeof(editFacNombre) - 1);
            editFacNombre[sizeof(editFacNombre) - 1] = '\0';

            strncpy(editFacUbicacion, f.ubicacion ? f.ubicacion->c_str() : "Sede Sabanas", sizeof(editFacUbicacion) - 1);
            editFacUbicacion[sizeof(editFacUbicacion) - 1] = '\0';

            strncpy(editFacTelefono, f.telefono ? f.telefono->c_str() : "5842000", sizeof(editFacTelefono) - 1);
            editFacTelefono[sizeof(editFacTelefono) - 1] = '\0';

            strncpy(editFacCorreo, f.correo ? f.correo->c_str() : "facultad@unicesar.edu.co", sizeof(editFacCorreo) - 1);
            editFacCorreo[sizeof(editFacCorreo) - 1] = '\0';

            editFacDecanoId = f.idDecano.value_or(0);
            editFacEstadoIdx = (f.estado && *f.estado == "INACTIVO") ? 1 : 0;

            mensajeModal[0] = '\0';
            errorModal = false;
            modalEditarFacultadAbierto = true;
            return;
        }
    }
}

void PITAApp::eliminarFacultad(int idFacultad) {
    // Verificar si tiene programas vinculados
    int cantProgs = 0;
    for (size_t i = 0; i < ctrl.datos.programas.tamano(); ++i) {
        auto& p = ctrl.datos.programas.obtener(i);
        if (p.idFacultad && *p.idFacultad == idFacultad) {
            cantProgs++;
        }
    }

    if (cantProgs > 0) {
        ctrl.setMensaje("No es posible eliminar la facultad: tiene programas academicos vinculados. Reasigne o retire primero los programas.", true);
        return;
    }

    bool borrado = ctrl.datos.facultades.remove_if([idFacultad](const Facultad& f) {
        return f.idFacultad && *f.idFacultad == idFacultad;
    });

    if (borrado) {
        ctrl.guardarDatos();
        ctrl.setMensaje("Facultad eliminada correctamente de la base de datos.");
    }
}

void PITAApp::abrirModalEditarPrograma(int idPrograma) {
    for (size_t i = 0; i < ctrl.datos.programas.tamano(); ++i) {
        auto& p = ctrl.datos.programas.obtener(i);
        if (p.idPrograma && *p.idPrograma == idPrograma) {
            editProgId = idPrograma;

            strncpy(editProgCodigo, p.codigoPrograma ? p.codigoPrograma->c_str() : "", sizeof(editProgCodigo) - 1);
            editProgCodigo[sizeof(editProgCodigo) - 1] = '\0';

            strncpy(editProgNombre, p.nombre ? p.nombre->c_str() : "", sizeof(editProgNombre) - 1);
            editProgNombre[sizeof(editProgNombre) - 1] = '\0';

            editProgFacultadId = p.idFacultad.value_or(1);
            editProgDirectorId = p.idDirector.value_or(0);

            // Buscar nivel
            std::string niv = p.nivelFormacion.value_or("PREGRADO");
            editProgNivelIdx = 0;
            for (int k = 0; k < TOTAL_NIVELES; ++k) {
                if (niv == NIVELES_FORMACION[k]) {
                    editProgNivelIdx = k;
                    break;
                }
            }

            // Buscar modalidad
            std::string mod = p.modalidad.value_or("PRESENCIAL");
            editProgModalidadIdx = 0;
            for (int k = 0; k < TOTAL_MODALIDADES; ++k) {
                if (mod.rfind(MODALIDADES_PROGRAMA[k], 0) == 0 || mod == MODALIDADES_PROGRAMA[k]) {
                    editProgModalidadIdx = k;
                    break;
                }
            }

            strncpy(editProgRegistroCalificado, p.registroCalificado ? p.registroCalificado->c_str() : "RC-2026-V1", sizeof(editProgRegistroCalificado) - 1);
            editProgRegistroCalificado[sizeof(editProgRegistroCalificado) - 1] = '\0';

            editProgSemestres = p.numeroSemestres.value_or(10);
            editProgCreditos = p.totalCreditos.value_or(160);
            editProgEstadoIdx = (p.estado && *p.estado == "INACTIVO") ? 1 : 0;

            mensajeModal[0] = '\0';
            errorModal = false;
            modalEditarProgramaAbierto = true;
            return;
        }
    }
}

void PITAApp::intentarEliminarPrograma(int idPrograma) {
    int cantEst = 0;
    for (size_t i = 0; i < ctrl.datos.estudiantes.tamano(); ++i) {
        auto& e = ctrl.datos.estudiantes.obtener(i);
        if (e.idPrograma && *e.idPrograma == idPrograma) {
            cantEst++;
        }
    }

    int cantPlan = 0;
    for (size_t i = 0; i < ctrl.datos.planesEstudio.tamano(); ++i) {
        auto& pl = ctrl.datos.planesEstudio.obtener(i);
        if (pl.idPrograma && *pl.idPrograma == idPrograma) {
            cantPlan++;
        }
    }

    if (cantEst > 0 || cantPlan > 0) {
        idProgBloqueado = idPrograma;
        cantEstudiantesProgBloqueado = cantEst;
        cantPlanesProgBloqueado = cantPlan;

        nombreProgBloqueado[0] = '\0';
        codigoProgBloqueado[0] = '\0';
        for (size_t i = 0; i < ctrl.datos.programas.tamano(); ++i) {
            auto& pr = ctrl.datos.programas.obtener(i);
            if (pr.idPrograma && *pr.idPrograma == idPrograma) {
                strncpy(nombreProgBloqueado, pr.nombre ? pr.nombre->c_str() : "Programa", sizeof(nombreProgBloqueado) - 1);
                strncpy(codigoProgBloqueado, pr.codigoPrograma ? pr.codigoPrograma->c_str() : "N/A", sizeof(codigoProgBloqueado) - 1);
                break;
            }
        }

        modalAvisoIntegridadProgramaAbierto = true;
        return;
    }

    bool borrado = ctrl.datos.programas.remove_if([idPrograma](const ProgramaAcademico& p) {
        return p.idPrograma && *p.idPrograma == idPrograma;
    });

    if (borrado) {
        ctrl.guardarDatos();
        ctrl.setMensaje("Programa academico eliminado correctamente.");
    }
}

// ======================================================================
// VISTA PRINCIPAL: FACULTADES Y PROGRAMAS
// ======================================================================

void PITAApp::renderFacultades() {
    // Cabecera con título y botones de acción rápida
    float btnWidth = 160.0f;
    float availW = ImGui::GetContentRegionAvail().x;

    if (fuenteTitulo) ImGui::PushFont(fuenteTitulo);
    ImGui::TextColored(tema::TEXT_MAIN(), "Gestion de Facultades & Programas Academicos");
    if (fuenteTitulo) ImGui::PopFont();

    if (fuentePequena) ImGui::PushFont(fuentePequena);
    ImGui::TextColored(tema::TEXT_MUTED(), "Administracion de unidades academicas, gobierno directivo y programas curriculares de la UPC");
    if (fuentePequena) ImGui::PopFont();

    ImGui::SameLine(availW - (btnWidth * 2.0f + 15.0f));
    ImGui::SetCursorPosY(ImGui::GetCursorPosY() - 6.0f);

    ImGui::PushStyleColor(ImGuiCol_Button, tema::WIN_BLUE());
    ImGui::PushStyleColor(ImGuiCol_ButtonHovered, tema::WIN_BLUE_HOVER());
    if (ImGui::Button("+ Nueva Facultad", ImVec2(btnWidth, 32))) {
        facCodigo[0] = '\0';
        facNombre[0] = '\0';
        facUbicacion[0] = '\0';
        strncpy(facTelefono, "5842000", sizeof(facTelefono) - 1);
        strncpy(facCorreo, "facultad@unicesar.edu.co", sizeof(facCorreo) - 1);
        facDecanoId = 0;
        mensajeModal[0] = '\0';
        errorModal = false;
        modalFacultadAbierto = true;
    }
    ImGui::PopStyleColor(2);

    ImGui::SameLine();
    ImGui::PushStyleColor(ImGuiCol_Button, tema::ACCENT_INDIGO());
    ImGui::PushStyleColor(ImGuiCol_ButtonHovered, tema::withAlpha(tema::ACCENT_INDIGO(), 0.8f));
    if (ImGui::Button("+ Nuevo Programa", ImVec2(btnWidth, 32))) {
        progCodigo[0] = '\0';
        progNombre[0] = '\0';
        if (ctrl.datos.facultades.tamano() > 0) {
            progFacultadId = ctrl.datos.facultades.obtener(0).idFacultad.value_or(1);
        } else {
            progFacultadId = 1;
        }
        progDirectorId = 0;
        progNivelIdx = 0;
        progModalidadIdx = 0;
        strncpy(progRegistroCalificado, "RC-2026-V1", sizeof(progRegistroCalificado) - 1);
        progSemestres = 10;
        progCreditos = 160;
        mensajeModal[0] = '\0';
        errorModal = false;
        modalProgramaAbierto = true;
    }
    ImGui::PopStyleColor(2);

    ImGui::Spacing();
    ImGui::Spacing();

    if (ImGui::BeginTabBar("##TabsFacultades")) {

        // --------------------------------------------------------------
        // TAB 1: FACULTADES INSTITUCIONAL
        // --------------------------------------------------------------
        if (ImGui::BeginTabItem("Facultades Institucional")) {
            ImGui::Spacing();

            if (ctrl.datos.facultades.tamano() == 0) {
                ImGui::TextColored(tema::TEXT_MUTED(), "No hay facultades registradas en el sistema.");
            } else {
                if (ImGui::BeginTable("##TablaFacultades", 8,
                    ImGuiTableFlags_RowBg | ImGuiTableFlags_BordersOuter | ImGuiTableFlags_BordersInnerH |
                    ImGuiTableFlags_Resizable | ImGuiTableFlags_ScrollY, ImVec2(0, 0))) {

                    ImGui::TableSetupColumn("Codigo", ImGuiTableColumnFlags_WidthFixed, 95);
                    ImGui::TableSetupColumn("Nombre de Facultad", ImGuiTableColumnFlags_WidthStretch);
                    ImGui::TableSetupColumn("Decano / Responsable", ImGuiTableColumnFlags_WidthStretch);
                    ImGui::TableSetupColumn("Ubicacion", ImGuiTableColumnFlags_WidthStretch);
                    ImGui::TableSetupColumn("Telefono", ImGuiTableColumnFlags_WidthFixed, 100);
                    ImGui::TableSetupColumn("Correo", ImGuiTableColumnFlags_WidthStretch);
                    ImGui::TableSetupColumn("Estado", ImGuiTableColumnFlags_WidthFixed, 85);
                    ImGui::TableSetupColumn("Acciones", ImGuiTableColumnFlags_WidthFixed, 145);
                    ImGui::TableHeadersRow();

                    for (size_t i = 0; i < ctrl.datos.facultades.tamano(); i++) {
                        auto& f = ctrl.datos.facultades.obtener(i);
                        int fId = f.idFacultad.value_or(0);

                        ImGui::TableNextRow();
                        ImGui::TableNextColumn();
                        ImGui::TextColored(tema::ACCENT_WARNING(), "%s", f.codigoFacultad ? f.codigoFacultad->c_str() : "---");

                        ImGui::TableNextColumn();
                        ImGui::Text("%s", f.nombre ? f.nombre->c_str() : "---");

                        ImGui::TableNextColumn();
                        std::string nomDec = getNombreDecano(ctrl, f.idDecano);
                        if (f.idDecano && *f.idDecano > 0) {
                            ImGui::TextColored(tema::WIN_BLUE(), "%s", nomDec.c_str());
                        } else {
                            ImGui::TextColored(tema::TEXT_MUTED(), "%s", nomDec.c_str());
                        }

                        ImGui::TableNextColumn();
                        ImGui::Text("%s", f.ubicacion ? f.ubicacion->c_str() : "---");

                        ImGui::TableNextColumn();
                        ImGui::Text("%s", f.telefono ? f.telefono->c_str() : "---");

                        ImGui::TableNextColumn();
                        ImGui::TextColored(tema::TEXT_MUTED(), "%s", f.correo ? f.correo->c_str() : "---");

                        ImGui::TableNextColumn();
                        bool esActivo = (!f.estado || *f.estado == "ACTIVO");
                        if (esActivo) {
                            ImGui::PushStyleColor(ImGuiCol_Button, tema::BADGE_ACTIVE_BG());
                            ImGui::PushStyleColor(ImGuiCol_Text, tema::BADGE_ACTIVE_TXT());
                            ImGui::SmallButton("ACTIVO");
                            ImGui::PopStyleColor(2);
                        } else {
                            ImGui::PushStyleColor(ImGuiCol_Button, tema::withAlpha(tema::ACCENT_DANGER(), 0.15f));
                            ImGui::PushStyleColor(ImGuiCol_Text, tema::ACCENT_DANGER());
                            ImGui::SmallButton("INACTIVO");
                            ImGui::PopStyleColor(2);
                        }

                        ImGui::TableNextColumn();
                        ImGui::PushID(fId);

                        ImGui::PushStyleColor(ImGuiCol_Button, tema::withAlpha(tema::WIN_BLUE(), 0.18f));
                        ImGui::PushStyleColor(ImGuiCol_Text, tema::WIN_BLUE());
                        if (ImGui::SmallButton("Editar")) {
                            abrirModalEditarFacultad(fId);
                        }
                        ImGui::PopStyleColor(2);

                        ImGui::SameLine();

                        ImGui::PushStyleColor(ImGuiCol_Button, tema::withAlpha(tema::ACCENT_DANGER(), 0.18f));
                        ImGui::PushStyleColor(ImGuiCol_Text, tema::ACCENT_DANGER());
                        if (ImGui::SmallButton("Eliminar")) {
                            eliminarFacultad(fId);
                        }
                        ImGui::PopStyleColor(2);

                        ImGui::PopID();
                    }
                    ImGui::EndTable();
                }
            }
            ImGui::EndTabItem();
        }

        // --------------------------------------------------------------
        // TAB 2: PROGRAMAS ACADEMICOS
        // --------------------------------------------------------------
        if (ImGui::BeginTabItem("Programas Academicos")) {
            ImGui::Spacing();

            if (ctrl.datos.programas.tamano() == 0) {
                ImGui::TextColored(tema::TEXT_MUTED(), "No hay programas academicos registrados en el sistema.");
            } else {
                if (ImGui::BeginTable("##TablaProgramas", 10,
                    ImGuiTableFlags_RowBg | ImGuiTableFlags_BordersOuter | ImGuiTableFlags_BordersInnerH |
                    ImGuiTableFlags_Resizable | ImGuiTableFlags_ScrollY, ImVec2(0, 0))) {

                    ImGui::TableSetupColumn("Codigo", ImGuiTableColumnFlags_WidthFixed, 110);
                    ImGui::TableSetupColumn("Programa Academico", ImGuiTableColumnFlags_WidthStretch);
                    ImGui::TableSetupColumn("Director a Cargo", ImGuiTableColumnFlags_WidthStretch);
                    ImGui::TableSetupColumn("Nivel", ImGuiTableColumnFlags_WidthFixed, 95);
                    ImGui::TableSetupColumn("Modalidad", ImGuiTableColumnFlags_WidthFixed, 95);
                    ImGui::TableSetupColumn("Sem.", ImGuiTableColumnFlags_WidthFixed, 55);
                    ImGui::TableSetupColumn("Cred.", ImGuiTableColumnFlags_WidthFixed, 55);
                    ImGui::TableSetupColumn("Facultad", ImGuiTableColumnFlags_WidthStretch);
                    ImGui::TableSetupColumn("Estado", ImGuiTableColumnFlags_WidthFixed, 85);
                    ImGui::TableSetupColumn("Acciones", ImGuiTableColumnFlags_WidthFixed, 145);
                    ImGui::TableHeadersRow();

                    for (size_t i = 0; i < ctrl.datos.programas.tamano(); i++) {
                        auto& p = ctrl.datos.programas.obtener(i);
                        int pId = p.idPrograma.value_or(0);

                        ImGui::TableNextRow();
                        ImGui::TableNextColumn();
                        ImGui::TextColored(tema::WIN_BLUE(), "%s", p.codigoPrograma ? p.codigoPrograma->c_str() : "---");

                        ImGui::TableNextColumn();
                        ImGui::Text("%s", p.nombre ? p.nombre->c_str() : "---");

                        ImGui::TableNextColumn();
                        std::string nomDir = getNombreDirector(ctrl, p.idDirector);
                        if (p.idDirector && *p.idDirector > 0) {
                            ImGui::TextColored(tema::WIN_BLUE(), "%s", nomDir.c_str());
                        } else {
                            ImGui::TextColored(tema::TEXT_MUTED(), "%s", nomDir.c_str());
                        }

                        ImGui::TableNextColumn();
                        ImGui::Text("%s", p.nivelFormacion ? p.nivelFormacion->c_str() : "PREGRADO");

                        ImGui::TableNextColumn();
                        ImGui::Text("%s", p.modalidad ? p.modalidad->c_str() : "PRESENCIAL");

                        ImGui::TableNextColumn();
                        ImGui::Text("%d Sem", p.numeroSemestres ? *p.numeroSemestres : 10);

                        ImGui::TableNextColumn();
                        ImGui::Text("%d", p.totalCreditos ? *p.totalCreditos : 160);

                        ImGui::TableNextColumn();
                        std::string nomFac = "---";
                        if (p.idFacultad) {
                            for (size_t j = 0; j < ctrl.datos.facultades.tamano(); j++) {
                                auto& f = ctrl.datos.facultades.obtener(j);
                                if (f.idFacultad && *f.idFacultad == *p.idFacultad) {
                                    nomFac = f.nombre ? *f.nombre : "---";
                                    break;
                                }
                            }
                        }
                        ImGui::Text("%s", nomFac.c_str());

                        ImGui::TableNextColumn();
                        bool esActivo = (!p.estado || *p.estado == "ACTIVO");
                        if (esActivo) {
                            ImGui::PushStyleColor(ImGuiCol_Button, tema::BADGE_ACTIVE_BG());
                            ImGui::PushStyleColor(ImGuiCol_Text, tema::BADGE_ACTIVE_TXT());
                            ImGui::SmallButton("ACTIVO");
                            ImGui::PopStyleColor(2);
                        } else {
                            ImGui::PushStyleColor(ImGuiCol_Button, tema::withAlpha(tema::ACCENT_DANGER(), 0.15f));
                            ImGui::PushStyleColor(ImGuiCol_Text, tema::ACCENT_DANGER());
                            ImGui::SmallButton("INACTIVO");
                            ImGui::PopStyleColor(2);
                        }

                        ImGui::TableNextColumn();
                        ImGui::PushID(pId);

                        ImGui::PushStyleColor(ImGuiCol_Button, tema::withAlpha(tema::WIN_BLUE(), 0.18f));
                        ImGui::PushStyleColor(ImGuiCol_Text, tema::WIN_BLUE());
                        if (ImGui::SmallButton("Editar")) {
                            abrirModalEditarPrograma(pId);
                        }
                        ImGui::PopStyleColor(2);

                        ImGui::SameLine();

                        ImGui::PushStyleColor(ImGuiCol_Button, tema::withAlpha(tema::ACCENT_DANGER(), 0.18f));
                        ImGui::PushStyleColor(ImGuiCol_Text, tema::ACCENT_DANGER());
                        if (ImGui::SmallButton("Eliminar")) {
                            intentarEliminarPrograma(pId);
                        }
                        ImGui::PopStyleColor(2);

                        ImGui::PopID();
                    }
                    ImGui::EndTable();
                }
            }
            ImGui::EndTabItem();
        }

        // --------------------------------------------------------------
        // TAB 3: UNIVERSIDAD POPULAR DEL CESAR
        // --------------------------------------------------------------
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

        ImGui::EndTabBar();
    }
}

// ======================================================================
// MODAL: NUEVA FACULTAD
// ======================================================================

void PITAApp::renderModalFacultad() {
    if (modalFacultadAbierto) {
        ImGui::OpenPopup("Nueva Facultad");
    }

    ImVec2 center = ImGui::GetMainViewport()->GetCenter();
    ImGui::SetNextWindowPos(center, ImGuiCond_Appearing, ImVec2(0.5f, 0.5f));
    ImGui::SetNextWindowSize(ImVec2(500, 0), ImGuiCond_Always);

    if (ImGui::BeginPopupModal("Nueva Facultad", &modalFacultadAbierto, ImGuiWindowFlags_AlwaysAutoResize)) {
        if (strlen(mensajeModal) > 0) {
            ImGui::TextColored(errorModal ? tema::ACCENT_DANGER() : tema::ACCENT_SUCCESS(), "%s", mensajeModal);
            ImGui::Separator();
        }

        ImGui::TextColored(tema::WIN_BLUE(), "Crear Unidad Academica / Facultad");
        ImGui::Spacing();

        ImGui::InputText("Codigo *", facCodigo, sizeof(facCodigo));
        ImGui::InputText("Nombre *", facNombre, sizeof(facNombre));
        ImGui::InputText("Ubicacion / Sede", facUbicacion, sizeof(facUbicacion));
        ImGui::InputText("Telefono", facTelefono, sizeof(facTelefono));
        ImGui::InputText("Correo Institucional", facCorreo, sizeof(facCorreo));

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
        ImGui::Spacing();

        if (ImGui::Button("Guardar Facultad", ImVec2(150, 32))) {
            if (strlen(facCodigo) == 0 || strlen(facNombre) == 0) {
                strncpy(mensajeModal, "Codigo y Nombre son obligatorios.", sizeof(mensajeModal) - 1);
                errorModal = true;
            } else {
                Facultad f;
                int maxId = 0;
                for (size_t i = 0; i < ctrl.datos.facultades.tamano(); i++) {
                    auto& fac = ctrl.datos.facultades.obtener(i);
                    if (fac.idFacultad && *fac.idFacultad > maxId) maxId = *fac.idFacultad;
                }
                f.idFacultad = maxId + 1;
                f.codigoFacultad = facCodigo;
                f.nombre = facNombre;
                if (strlen(facUbicacion) > 0) f.ubicacion = facUbicacion;
                if (strlen(facTelefono) > 0) f.telefono = facTelefono;
                if (strlen(facCorreo) > 0) f.correo = facCorreo;
                if (facDecanoId > 0) {
                    f.idDecano = facDecanoId;
                } else {
                    f.idDecano = std::nullopt;
                }
                f.fechaCreacion = "2026-03-01";
                f.estado = "ACTIVO";

                ctrl.datos.facultades.push_back(f);
                ctrl.guardarDatos();
                ctrl.setMensaje("Facultad registrada con exito.");
                modalFacultadAbierto = false;
                ImGui::CloseCurrentPopup();
            }
        }

        ImGui::SameLine();
        if (ImGui::Button("Cancelar", ImVec2(120, 32))) {
            modalFacultadAbierto = false;
            ImGui::CloseCurrentPopup();
        }

        ImGui::EndPopup();
    }
}

// ======================================================================
// MODAL: EDITAR FACULTAD
// ======================================================================

void PITAApp::renderModalEditarFacultad() {
    if (modalEditarFacultadAbierto) {
        ImGui::OpenPopup("Editar Facultad");
    }

    ImVec2 center = ImGui::GetMainViewport()->GetCenter();
    ImGui::SetNextWindowPos(center, ImGuiCond_Appearing, ImVec2(0.5f, 0.5f));
    ImGui::SetNextWindowSize(ImVec2(500, 0), ImGuiCond_Always);

    if (ImGui::BeginPopupModal("Editar Facultad", &modalEditarFacultadAbierto, ImGuiWindowFlags_AlwaysAutoResize)) {
        if (strlen(mensajeModal) > 0) {
            ImGui::TextColored(errorModal ? tema::ACCENT_DANGER() : tema::ACCENT_SUCCESS(), "%s", mensajeModal);
            ImGui::Separator();
        }

        ImGui::TextColored(tema::WIN_BLUE(), "Modificar Facultad: %s", editFacNombre);
        ImGui::Spacing();

        ImGui::InputText("Codigo *", editFacCodigo, sizeof(editFacCodigo));
        ImGui::InputText("Nombre *", editFacNombre, sizeof(editFacNombre));
        ImGui::InputText("Ubicacion / Sede", editFacUbicacion, sizeof(editFacUbicacion));
        ImGui::InputText("Telefono", editFacTelefono, sizeof(editFacTelefono));
        ImGui::InputText("Correo Institucional", editFacCorreo, sizeof(editFacCorreo));

        // Combo Decano
        std::string previewDecano = "(Sin Decano Asignado)";
        if (editFacDecanoId > 0) {
            previewDecano = getNombreDecano(ctrl, editFacDecanoId);
        }

        if (ImGui::BeginCombo("Decano / Responsable", previewDecano.c_str())) {
            bool selNinguno = (editFacDecanoId == 0);
            if (ImGui::Selectable("(Sin Decano Asignado)", selNinguno)) {
                editFacDecanoId = 0;
            }
            if (selNinguno) ImGui::SetItemDefaultFocus();

            for (size_t i = 0; i < ctrl.datos.profesores.tamano(); ++i) {
                auto& pr = ctrl.datos.profesores.obtener(i);
                int pId = pr.idProfesor.value_or(0);
                std::string label = getNombreDecano(ctrl, pId);
                bool sel = (editFacDecanoId == pId);
                if (ImGui::Selectable(label.c_str(), sel)) {
                    editFacDecanoId = pId;
                }
                if (sel) ImGui::SetItemDefaultFocus();
            }
            ImGui::EndCombo();
        }

        ImGui::Combo("Estado", &editFacEstadoIdx, ESTADOS_REGISTRO, IM_ARRAYSIZE(ESTADOS_REGISTRO));

        ImGui::Spacing();
        ImGui::Separator();
        ImGui::Spacing();

        if (ImGui::Button("Guardar Cambios", ImVec2(150, 32))) {
            if (strlen(editFacCodigo) == 0 || strlen(editFacNombre) == 0) {
                strncpy(mensajeModal, "Codigo y Nombre son obligatorios.", sizeof(mensajeModal) - 1);
                errorModal = true;
            } else {
                for (size_t i = 0; i < ctrl.datos.facultades.tamano(); ++i) {
                    auto& f = ctrl.datos.facultades.obtener(i);
                    if (f.idFacultad && *f.idFacultad == editFacId) {
                        f.codigoFacultad = editFacCodigo;
                        f.nombre = editFacNombre;
                        f.ubicacion = editFacUbicacion;
                        f.telefono = editFacTelefono;
                        f.correo = editFacCorreo;
                        f.idDecano = editFacDecanoId > 0 ? std::optional<int>(editFacDecanoId) : std::nullopt;
                        f.estado = (editFacEstadoIdx == 0 ? "ACTIVO" : "INACTIVO");
                        break;
                    }
                }
                ctrl.guardarDatos();
                ctrl.setMensaje("Facultad actualizada con exito.");
                modalEditarFacultadAbierto = false;
                ImGui::CloseCurrentPopup();
            }
        }

        ImGui::SameLine();
        if (ImGui::Button("Cancelar", ImVec2(120, 32))) {
            modalEditarFacultadAbierto = false;
            ImGui::CloseCurrentPopup();
        }

        ImGui::EndPopup();
    }
}

// ======================================================================
// MODAL: NUEVO PROGRAMA ACADEMICO
// ======================================================================

void PITAApp::renderModalPrograma() {
    if (modalProgramaAbierto) {
        ImGui::OpenPopup("Nuevo Programa Academico");
    }

    ImVec2 center = ImGui::GetMainViewport()->GetCenter();
    ImGui::SetNextWindowPos(center, ImGuiCond_Appearing, ImVec2(0.5f, 0.5f));
    ImGui::SetNextWindowSize(ImVec2(560, 0), ImGuiCond_Always);

    if (ImGui::BeginPopupModal("Nuevo Programa Academico", &modalProgramaAbierto, ImGuiWindowFlags_AlwaysAutoResize)) {
        if (strlen(mensajeModal) > 0) {
            ImGui::TextColored(errorModal ? tema::ACCENT_DANGER() : tema::ACCENT_SUCCESS(), "%s", mensajeModal);
            ImGui::Separator();
        }

        ImGui::TextColored(tema::WIN_BLUE(), "Registrar Nueva Oferta Academica UPC");
        ImGui::Spacing();

        ImGui::InputText("Nombre del Programa *", progNombre, sizeof(progNombre));
        ImGui::InputText("Codigo Institucional *", progCodigo, sizeof(progCodigo));

        // Combo Facultad
        if (ctrl.datos.facultades.tamano() > 0) {
            std::string previewFac = "Seleccione Facultad";
            for (size_t i = 0; i < ctrl.datos.facultades.tamano(); i++) {
                auto& f = ctrl.datos.facultades.obtener(i);
                if (f.idFacultad && *f.idFacultad == progFacultadId) {
                    previewFac = f.nombre ? *f.nombre : "---";
                    break;
                }
            }
            if (ImGui::BeginCombo("Facultad de Adscripcion *", previewFac.c_str())) {
                for (size_t i = 0; i < ctrl.datos.facultades.tamano(); i++) {
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

        // Combo Director de Programa (Profesores)
        std::string previewDir = "(Sin Director Asignado)";
        if (progDirectorId > 0) {
            previewDir = getNombreDirector(ctrl, progDirectorId);
        }

        if (ImGui::BeginCombo("Director de Programa (Docente a Cargo)", previewDir.c_str())) {
            bool selNinguno = (progDirectorId == 0);
            if (ImGui::Selectable("(Sin Director Asignado)", selNinguno)) {
                progDirectorId = 0;
            }
            if (selNinguno) ImGui::SetItemDefaultFocus();

            for (size_t i = 0; i < ctrl.datos.profesores.tamano(); ++i) {
                auto& pr = ctrl.datos.profesores.obtener(i);
                int pId = pr.idProfesor.value_or(0);
                std::string label = getNombreDirector(ctrl, pId);
                bool sel = (progDirectorId == pId);
                if (ImGui::Selectable(label.c_str(), sel)) {
                    progDirectorId = pId;
                }
                if (sel) ImGui::SetItemDefaultFocus();
            }
            ImGui::EndCombo();
        }

        ImGui::Combo("Nivel de Formacion", &progNivelIdx, NIVELES_FORMACION, TOTAL_NIVELES);
        ImGui::Combo("Modalidad", &progModalidadIdx, MODALIDADES_PROGRAMA, TOTAL_MODALIDADES);
        ImGui::InputText("Registro Calificado / Res. MEN", progRegistroCalificado, sizeof(progRegistroCalificado));

        ImGui::InputInt("Numero de Semestres *", &progSemestres);
        if (progSemestres < 1) progSemestres = 1;

        ImGui::InputInt("Total Creditos Academicos *", &progCreditos);
        if (progCreditos < 1) progCreditos = 1;

        ImGui::Spacing();
        ImGui::Separator();
        ImGui::Spacing();

        if (ImGui::Button("Registrar Programa", ImVec2(160, 32))) {
            if (strlen(progCodigo) == 0 || strlen(progNombre) == 0) {
                strncpy(mensajeModal, "Codigo y Nombre del programa son obligatorios.", sizeof(mensajeModal) - 1);
                errorModal = true;
            } else {
                // Verificar colisión de código
                bool colision = false;
                for (size_t i = 0; i < ctrl.datos.programas.tamano(); ++i) {
                    auto& pr = ctrl.datos.programas.obtener(i);
                    if (pr.codigoPrograma && *pr.codigoPrograma == progCodigo) {
                        colision = true;
                        break;
                    }
                }

                if (colision) {
                    strncpy(mensajeModal, "El codigo ya esta asignado a otro programa academico.", sizeof(mensajeModal) - 1);
                    errorModal = true;
                } else {
                    ProgramaAcademico p;
                    int maxId = 0;
                    for (size_t i = 0; i < ctrl.datos.programas.tamano(); i++) {
                        auto& pr = ctrl.datos.programas.obtener(i);
                        if (pr.idPrograma && *pr.idPrograma > maxId) maxId = *pr.idPrograma;
                    }
                    p.idPrograma = maxId + 1;
                    p.codigoPrograma = progCodigo;
                    p.nombre = progNombre;
                    p.idFacultad = progFacultadId;
                    p.idDirector = progDirectorId > 0 ? std::optional<int>(progDirectorId) : std::nullopt;
                    p.nivelFormacion = NIVELES_FORMACION[progNivelIdx];
                    p.modalidad = MODALIDADES_PROGRAMA[progModalidadIdx];
                    p.registroCalificado = progRegistroCalificado;
                    p.numeroSemestres = progSemestres;
                    p.totalCreditos = progCreditos;
                    p.fechaCreacion = "2026-03-01";
                    p.estado = "ACTIVO";

                    ctrl.datos.programas.push_back(p);
                    ctrl.guardarDatos();
                    ctrl.setMensaje("Programa academico registrado con exito.");
                    modalProgramaAbierto = false;
                    ImGui::CloseCurrentPopup();
                }
            }
        }

        ImGui::SameLine();
        if (ImGui::Button("Cancelar", ImVec2(120, 32))) {
            modalProgramaAbierto = false;
            ImGui::CloseCurrentPopup();
        }

        ImGui::EndPopup();
    }
}

// ======================================================================
// MODAL: EDITAR PROGRAMA ACADEMICO (EQUIVALENTE A DialogEditarPrograma)
// ======================================================================

void PITAApp::renderModalEditarPrograma() {
    if (modalEditarProgramaAbierto) {
        ImGui::OpenPopup("Editar Programa Academico");
    }

    ImVec2 center = ImGui::GetMainViewport()->GetCenter();
    ImGui::SetNextWindowPos(center, ImGuiCond_Appearing, ImVec2(0.5f, 0.5f));
    ImGui::SetNextWindowSize(ImVec2(600, 0), ImGuiCond_Always);

    if (ImGui::BeginPopupModal("Editar Programa Academico", &modalEditarProgramaAbierto, ImGuiWindowFlags_AlwaysAutoResize)) {
        if (strlen(mensajeModal) > 0) {
            ImGui::TextColored(errorModal ? tema::ACCENT_DANGER() : tema::ACCENT_SUCCESS(), "%s", mensajeModal);
            ImGui::Separator();
        }

        ImGui::TextColored(tema::WIN_BLUE(), "Modificar Programa: %s", editProgNombre);
        ImGui::TextColored(tema::TEXT_MUTED(), "Actualice la configuracion curricular, directiva y el estado operativo.");
        ImGui::Spacing();

        // --------------------------------------------------------------
        // BANNER DE CONTEXTO INSTITUCIONAL Y METRICAS DE IMPACTO
        // --------------------------------------------------------------
        int cantEst = 0;
        for (size_t i = 0; i < ctrl.datos.estudiantes.tamano(); ++i) {
            auto& e = ctrl.datos.estudiantes.obtener(i);
            if (e.idPrograma && *e.idPrograma == editProgId) cantEst++;
        }

        int cantPlanes = 0;
        for (size_t i = 0; i < ctrl.datos.planesEstudio.tamano(); ++i) {
            auto& pl = ctrl.datos.planesEstudio.obtener(i);
            if (pl.idPrograma && *pl.idPrograma == editProgId) cantPlanes++;
        }

        int cantDocentes = 0;
        for (size_t i = 0; i < ctrl.datos.profesores.tamano(); ++i) {
            auto& pr = ctrl.datos.profesores.obtener(i);
            if (pr.idProgramaPrincipal && *pr.idProgramaPrincipal == editProgId) cantDocentes++;
        }

        ImGui::PushStyleColor(ImGuiCol_ChildBg, tema::BG_CARD());
        ImGui::BeginChild("##ImpactoProg", ImVec2(0, 60), ImGuiChildFlags_Borders);
        ImGui::SetCursorPos(ImVec2(12, 10));
        ImGui::TextColored(tema::TEXT_MUTED(), "Impacto Academico en Vivo:");
        ImGui::SetCursorPos(ImVec2(12, 32));
        ImGui::TextColored(tema::WIN_BLUE(), "%d Estudiantes Matriculados", cantEst);
        ImGui::SameLine(220);
        ImGui::TextColored(tema::ACCENT_WARNING(), "%d Planes de Estudio", cantPlanes);
        ImGui::SameLine(400);
        ImGui::TextColored(tema::ACCENT_SUCCESS(), "%d Docentes Adscritos", cantDocentes);
        ImGui::EndChild();
        ImGui::PopStyleColor();

        ImGui::Spacing();

        ImGui::InputText("Nombre del Programa *", editProgNombre, sizeof(editProgNombre));
        ImGui::InputText("Codigo Institucional *", editProgCodigo, sizeof(editProgCodigo));

        // Combo Facultad
        if (ctrl.datos.facultades.tamano() > 0) {
            std::string previewFac = "Seleccione Facultad";
            for (size_t i = 0; i < ctrl.datos.facultades.tamano(); i++) {
                auto& f = ctrl.datos.facultades.obtener(i);
                if (f.idFacultad && *f.idFacultad == editProgFacultadId) {
                    previewFac = f.nombre ? *f.nombre : "---";
                    break;
                }
            }
            if (ImGui::BeginCombo("Facultad de Adscripcion *", previewFac.c_str())) {
                for (size_t i = 0; i < ctrl.datos.facultades.tamano(); i++) {
                    auto& f = ctrl.datos.facultades.obtener(i);
                    bool isSelected = (f.idFacultad && *f.idFacultad == editProgFacultadId);
                    std::string label = f.nombre ? *f.nombre : "Facultad";
                    if (ImGui::Selectable(label.c_str(), isSelected)) {
                        editProgFacultadId = f.idFacultad.value_or(1);
                    }
                    if (isSelected) ImGui::SetItemDefaultFocus();
                }
                ImGui::EndCombo();
            }
        }

        // Combo Director
        std::string previewDir = "(Sin Director Asignado)";
        if (editProgDirectorId > 0) {
            previewDir = getNombreDirector(ctrl, editProgDirectorId);
        }

        if (ImGui::BeginCombo("Director de Programa (Docente a Cargo)", previewDir.c_str())) {
            bool selNinguno = (editProgDirectorId == 0);
            if (ImGui::Selectable("(Sin Director Asignado)", selNinguno)) {
                editProgDirectorId = 0;
            }
            if (selNinguno) ImGui::SetItemDefaultFocus();

            for (size_t i = 0; i < ctrl.datos.profesores.tamano(); ++i) {
                auto& pr = ctrl.datos.profesores.obtener(i);
                int pId = pr.idProfesor.value_or(0);
                std::string label = getNombreDirector(ctrl, pId);
                bool sel = (editProgDirectorId == pId);
                if (ImGui::Selectable(label.c_str(), sel)) {
                    editProgDirectorId = pId;
                }
                if (sel) ImGui::SetItemDefaultFocus();
            }
            ImGui::EndCombo();
        }

        ImGui::Combo("Nivel de Formacion", &editProgNivelIdx, NIVELES_FORMACION, TOTAL_NIVELES);
        ImGui::Combo("Modalidad", &editProgModalidadIdx, MODALIDADES_PROGRAMA, TOTAL_MODALIDADES);
        ImGui::InputText("Registro Calificado / Res. MEN", editProgRegistroCalificado, sizeof(editProgRegistroCalificado));

        ImGui::InputInt("Numero de Semestres *", &editProgSemestres);
        if (editProgSemestres < 1) editProgSemestres = 1;

        ImGui::InputInt("Total Creditos Academicos *", &editProgCreditos);
        if (editProgCreditos < 1) editProgCreditos = 1;

        ImGui::Combo("Estado Operativo", &editProgEstadoIdx, ESTADOS_REGISTRO, IM_ARRAYSIZE(ESTADOS_REGISTRO));
        if (editProgEstadoIdx == 1 && cantEst > 0) {
            ImGui::TextColored(tema::ACCENT_DANGER(), "Atencion: Hay %d estudiante(s) activo(s) en este programa.", cantEst);
        }

        ImGui::Spacing();
        ImGui::Separator();
        ImGui::Spacing();

        if (ImGui::Button("Guardar Cambios", ImVec2(160, 32))) {
            if (strlen(editProgCodigo) == 0 || strlen(editProgNombre) == 0) {
                strncpy(mensajeModal, "Codigo y Nombre del programa son obligatorios.", sizeof(mensajeModal) - 1);
                errorModal = true;
            } else {
                // Verificar colisión con otro programa
                bool colision = false;
                for (size_t i = 0; i < ctrl.datos.programas.tamano(); ++i) {
                    auto& pr = ctrl.datos.programas.obtener(i);
                    if (pr.idPrograma && *pr.idPrograma != editProgId &&
                        pr.codigoPrograma && *pr.codigoPrograma == editProgCodigo) {
                        colision = true;
                        break;
                    }
                }

                if (colision) {
                    strncpy(mensajeModal, "El codigo ya esta asignado a otro programa academico.", sizeof(mensajeModal) - 1);
                    errorModal = true;
                } else {
                    for (size_t i = 0; i < ctrl.datos.programas.tamano(); ++i) {
                        auto& pr = ctrl.datos.programas.obtener(i);
                        if (pr.idPrograma && *pr.idPrograma == editProgId) {
                            pr.codigoPrograma = editProgCodigo;
                            pr.nombre = editProgNombre;
                            pr.idFacultad = editProgFacultadId;
                            pr.idDirector = editProgDirectorId > 0 ? std::optional<int>(editProgDirectorId) : std::nullopt;
                            pr.nivelFormacion = NIVELES_FORMACION[editProgNivelIdx];
                            pr.modalidad = MODALIDADES_PROGRAMA[editProgModalidadIdx];
                            pr.registroCalificado = editProgRegistroCalificado;
                            pr.numeroSemestres = editProgSemestres;
                            pr.totalCreditos = editProgCreditos;
                            pr.estado = (editProgEstadoIdx == 0 ? "ACTIVO" : "INACTIVO");
                            break;
                        }
                    }
                    ctrl.guardarDatos();
                    ctrl.setMensaje("Programa academico actualizado con exito.");
                    modalEditarProgramaAbierto = false;
                    ImGui::CloseCurrentPopup();
                }
            }
        }

        ImGui::SameLine();
        if (ImGui::Button("Cancelar", ImVec2(120, 32))) {
            modalEditarProgramaAbierto = false;
            ImGui::CloseCurrentPopup();
        }

        ImGui::EndPopup();
    }
}

// ======================================================================
// MODAL: AVISO DE INTEGRIDAD REFERENCIAL AL ELIMINAR PROGRAMA
// ======================================================================

void PITAApp::renderModalAvisoIntegridadPrograma() {
    if (modalAvisoIntegridadProgramaAbierto) {
        ImGui::OpenPopup("Bloqueo de Integridad Referencial");
    }

    ImVec2 center = ImGui::GetMainViewport()->GetCenter();
    ImGui::SetNextWindowPos(center, ImGuiCond_Appearing, ImVec2(0.5f, 0.5f));
    ImGui::SetNextWindowSize(ImVec2(520, 0), ImGuiCond_Always);

    if (ImGui::BeginPopupModal("Bloqueo de Integridad Referencial", &modalAvisoIntegridadProgramaAbierto, ImGuiWindowFlags_AlwaysAutoResize)) {
        ImGui::Spacing();
        if (fuenteNormal) ImGui::PushFont(fuenteNormal);
        ImGui::TextColored(tema::ACCENT_DANGER(), "No es posible eliminar el Programa Academico");
        if (fuenteNormal) ImGui::PopFont();
        ImGui::Spacing();

        ImGui::TextWrapped("El programa '%s' (%s) no puede eliminarse de la base de datos porque cuenta con registros institucionales vinculados:",
                           nombreProgBloqueado, codigoProgBloqueado);
        ImGui::Spacing();

        ImGui::BulletText("%d Estudiante(s) matriculado(s)", cantEstudiantesProgBloqueado);
        ImGui::BulletText("%d Plan(es) de estudio registrado(s)", cantPlanesProgBloqueado);

        ImGui::Spacing();
        ImGui::TextWrapped("Para retirar el programa sin comprometer la integridad historica, edítelo y cambie su estado operativo a 'INACTIVO'.");
        ImGui::Spacing();
        ImGui::Separator();
        ImGui::Spacing();

        ImGui::SetCursorPosX((ImGui::GetWindowWidth() - 130) / 2.0f);
        if (ImGui::Button("Entendido", ImVec2(130, 32))) {
            modalAvisoIntegridadProgramaAbierto = false;
            ImGui::CloseCurrentPopup();
        }

        ImGui::EndPopup();
    }
}

} // namespace pita
