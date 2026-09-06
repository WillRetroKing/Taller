"""Renderizadores de pestañas (Estudiantes, Profesores, Administrativos) para la vista de Personas."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable
import customtkinter as ctk

from ui_gui.components import PITAGridTable, clean_enum

if TYPE_CHECKING:
    from ui_gui.gui_controller import PITAController
    from dominio.modelo_datos import Persona, Estudiante, Profesor, Administrativo


class PersonasTabsRenderer:
    """Gestiona el llenado y renderizado dinámico de las tablas de cada pestaña."""

    def __init__(
        self,
        controller: PITAController,
        on_ver_persona: Callable[[Persona | None], None],
        on_editar_estudiante: Callable[[Estudiante, Persona | None], None],
        on_desactivar_estudiante: Callable[[int], None],
        on_editar_profesor: Callable[[Profesor, Persona | None], None],
        on_desactivar_profesor: Callable[[int], None],
        on_editar_administrativo: Callable[[Administrativo, Persona | None], None],
        on_desactivar_administrativo: Callable[[int], None],
    ) -> None:
        self.controller = controller
        self.on_ver_persona = on_ver_persona
        self.on_editar_estudiante = on_editar_estudiante
        self.on_desactivar_estudiante = on_desactivar_estudiante
        self.on_editar_profesor = on_editar_profesor
        self.on_desactivar_profesor = on_desactivar_profesor
        self.on_editar_administrativo = on_editar_administrativo
        self.on_desactivar_administrativo = on_desactivar_administrativo

    def llenar_estudiantes(self, container: ctk.CTkFrame, query: str = "") -> None:
        for w in container.winfo_children():
            w.destroy()

        headers = ["Código", "Documento", "Nombre Completo", "Semestre", "Promedio", "Estado Académico", "Acciones"]
        col_weights = [2, 2, 3, 1, 1, 1, 2]
        col_mins = [70, 80, 140, 60, 50, 70, 70]

        table = PITAGridTable(container, headers=headers, col_weights=col_weights, col_mins=col_mins)
        table.pack(fill="both", expand=True, padx=5, pady=5)

        estud_list = self.controller.estudiantes
        if query:
            estud_list = [
                e for e in estud_list
                if query in str(getattr(e, "codigoEstudiante", "")).lower()
                or query in clean_enum(getattr(e, "estadoAcademico", "")).lower()
                or any(
                    query in str(getattr(p, "numeroDocumento", "")).lower()
                    or query in str(getattr(p, "primerNombre", "")).lower()
                    or query in str(getattr(p, "primerApellido", "")).lower()
                    for p in self.controller.personas
                    if getattr(p, "idPersona", None) == getattr(e, "idPersona", None)
                )
            ]

        if not estud_list:
            ctk.CTkLabel(table, text="No hay estudiantes coincidentes.", text_color="#94A3B8").pack(pady=30)
            return

        for est in estud_list:
            pers = next((p for p in self.controller.personas if getattr(p, "idPersona", None) == getattr(est, "idPersona", None)), None)
            doc = getattr(pers, "numeroDocumento", "N/A") if pers else "N/A"
            nombre = f"{getattr(pers, 'primerNombre', '')} {getattr(pers, 'primerApellido', '')}" if pers else "Sin Persona"

            estado_acad = clean_enum(getattr(est, "estadoAcademico", "ACTIVO"))
            promedio = float(getattr(est, "promedioAcumulado", 0.0) or 0.0)

            badge_tuple = ("badge", "⚠️ EBRA", "ebra") if (estado_acad == "EBRA" or promedio < 3.0) else ("badge", "● ACTIVO", "active")

            act_spec = (
                "actions",
                [
                    ("👁️ Ver", lambda p=pers: self.on_ver_persona(p), "#6366F1", "#4F46E5"),
                    ("✏️ Editar", lambda e=est, p=pers: self.on_editar_estudiante(e, p), "#334155", "#475569"),
                    ("❌ Desactivar", lambda e_id=getattr(est, "idEstudiante", 0): self.on_desactivar_estudiante(e_id), "#EF4444", "#DC2626"),
                ],
            )

            color_prom = "#F87171" if promedio < 3.0 else "#34D399"
            cells = [
                (getattr(est, "codigoEstudiante", "N/A"), "#38BDF8"),
                doc,
                (nombre, "#F8FAFC"),
                f"Semestre {getattr(est, 'semestreActual', '1')}",
                (f"{promedio:.2f}", color_prom),
                badge_tuple,
                act_spec,
            ]
            table.add_row_items(cells, is_highlighted=(promedio < 3.0 or estado_acad == "EBRA"))

    def llenar_profesores(self, container: ctk.CTkFrame, query: str = "") -> None:
        for w in container.winfo_children():
            w.destroy()

        headers = ["Código", "Documento", "Nombre Completo", "Tipo Profesor", "Categoría", "Horas/Semana", "Acciones"]
        col_weights = [2, 2, 3, 1, 1, 1, 2]
        col_mins = [70, 80, 140, 50, 70, 70, 70]

        table = PITAGridTable(container, headers=headers, col_weights=col_weights, col_mins=col_mins)
        table.pack(fill="both", expand=True, padx=5, pady=5)

        prof_list = self.controller.profesores
        if query:
            prof_list = [
                p for p in prof_list
                if query in str(getattr(p, "codigoProfesor", "")).lower()
                or query in clean_enum(getattr(p, "tipoProfesor", "")).lower()
                or any(
                    query in str(getattr(pers, "numeroDocumento", "")).lower()
                    or query in str(getattr(pers, "primerNombre", "")).lower()
                    or query in str(getattr(pers, "primerApellido", "")).lower()
                    for pers in self.controller.personas
                    if getattr(pers, "idPersona", None) == getattr(p, "idPersona", None)
                )
            ]

        if not prof_list:
            ctk.CTkLabel(table, text="No hay profesores coincidentes.", text_color="#94A3B8").pack(pady=30)
            return

        for prof in prof_list:
            pers = next((p for p in self.controller.personas if getattr(p, "idPersona", None) == getattr(prof, "idPersona", None)), None)
            doc = getattr(pers, "numeroDocumento", "N/A") if pers else "N/A"
            nombre = f"{getattr(pers, 'primerNombre', '')} {getattr(pers, 'primerApellido', '')}" if pers else "Sin Persona"

            tipo_raw = clean_enum(getattr(prof, "tipoProfesor", "PLANTA"))
            tipo_map = {
                "PLANTA": ("🏛️ Planta", "planta"),
                "OCASIONAL": ("⏱️ Ocasional", "ocasional"),
                "CATEDRATICO": ("📚 Cátedra", "catedra"),
                "CATEDRATICO_AD_HONOREM": ("🤝 Ad-Honorem", "neutral"),
            }
            tipo_label, b_type = tipo_map.get(tipo_raw, (tipo_raw.replace("_", " ").title(), "neutral"))
            badge_tuple = ("badge", tipo_label, b_type)

            cat_raw = clean_enum(getattr(prof, "categoriaDocente", "TITULAR"))
            cat = cat_raw.replace("_", " ").title()

            act_spec = (
                "actions",
                [
                    ("👁️ Ver", lambda p=pers: self.on_ver_persona(p), "#6366F1", "#4F46E5"),
                    ("✏️ Editar", lambda pr=prof, p=pers: self.on_editar_profesor(pr, p), "#334155", "#475569"),
                    ("❌ Desactivar", lambda p_id=getattr(prof, "idProfesor", 0): self.on_desactivar_profesor(p_id), "#EF4444", "#DC2626"),
                ],
            )

            cells = [
                (getattr(prof, "codigoProfesor", "N/A"), "#C084FC"),
                doc,
                (nombre, "#F8FAFC"),
                badge_tuple,
                cat,
                f"{getattr(prof, 'numeroHorasSemanales', '40')} h/sem",
                act_spec,
            ]
            table.add_row_items(cells)

    def llenar_administrativos(self, container: ctk.CTkFrame, query: str = "") -> None:
        for w in container.winfo_children():
            w.destroy()

        headers = ["Código", "Documento", "Nombre Completo", "Cargo", "Dependencia", "Salario Base", "Acciones"]
        col_weights = [2, 2, 3, 2, 2, 1, 2]
        col_mins = [70, 80, 140, 80, 80, 70, 70]

        table = PITAGridTable(container, headers=headers, col_weights=col_weights, col_mins=col_mins)
        table.pack(fill="both", expand=True, padx=5, pady=5)

        adm_list = self.controller.administrativos
        if query:
            adm_list = [
                a for a in adm_list
                if query in str(getattr(a, "codigoEmpleado", "")).lower()
                or query in str(getattr(a, "cargo", "")).lower()
                or any(
                    query in str(getattr(pers, "numeroDocumento", "")).lower()
                    or query in str(getattr(pers, "primerNombre", "")).lower()
                    or query in str(getattr(pers, "primerApellido", "")).lower()
                    for pers in self.controller.personas
                    if getattr(pers, "idPersona", None) == getattr(a, "idPersona", None)
                )
            ]

        if not adm_list:
            ctk.CTkLabel(table, text="No hay administrativos coincidentes.", text_color="#94A3B8").pack(pady=30)
            return

        for adm in adm_list:
            pers = next((p for p in self.controller.personas if getattr(p, "idPersona", None) == getattr(adm, "idPersona", None)), None)
            doc = getattr(pers, "numeroDocumento", "N/A") if pers else "N/A"
            nombre = f"{getattr(pers, 'primerNombre', '')} {getattr(pers, 'primerApellido', '')}" if pers else "Sin Persona"

            sal = str(getattr(adm, "salarioBase", "0"))
            sal_fmt = f"$ {int(float(sal)):,} COP" if sal.replace(".", "").isdigit() else sal

            act_spec = (
                "actions",
                [
                    ("👁️ Ver", lambda p=pers: self.on_ver_persona(p), "#6366F1", "#4F46E5"),
                    ("✏️ Editar", lambda a=adm, p=pers: self.on_editar_administrativo(a, p), "#334155", "#475569"),
                    ("❌ Desactivar", lambda a_id=getattr(adm, "idAdministrativo", 0): self.on_desactivar_administrativo(a_id), "#EF4444", "#DC2626"),
                ],
            )

            cells = [
                (getattr(adm, "codigoEmpleado", "N/A"), "#F59E0B"),
                doc,
                (nombre, "#F8FAFC"),
                getattr(adm, "cargo", "N/A"),
                getattr(adm, "dependencia", "N/A"),
                (sal_fmt, "#10B981"),
                act_spec,
            ]
            table.add_row_items(cells)
