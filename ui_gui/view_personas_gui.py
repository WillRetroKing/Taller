"""Vista de Gestión de Personas (Estudiantes, Profesores, Administrativos) para la GUI con tablas y badges estilizados."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
import customtkinter as ctk
from typing import TYPE_CHECKING

from ui_gui.theme import Colors, create_styled_tabview
from ui_gui.components import PITAGridTable, create_badge
from modelo_datos import (
    Administrativo,
    CategoriaDocente,
    Dedicacion,
    EstadoAcademico,
    Estudiante,
    Persona,
    Profesor,
    TipoProfesor,
)

if TYPE_CHECKING:
    from ui_gui.gui_controller import PITAController


class PersonasViewGUI(ctk.CTkFrame):
    """Vista completa de gestión de Personas con tablas y badges estilizados."""

    def __init__(self, parent: ctk.CTk, controller: PITAController) -> None:
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.busqueda_var = ctk.StringVar(value="")

        self._crear_interfaz()

    def _crear_interfaz(self) -> None:
        # Header y Búsqueda
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 10))

        ctk.CTkLabel(
            header,
            text="👥 Gestión de Personas e Identificación",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=Colors.TEXT_MAIN,
        ).pack(side="left")

        btn_nueva = ctk.CTkButton(
            header,
            text="➕ Registrar Persona / Asignar Rol",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#0067C0",
            hover_color="#005FB8",
            height=36,
            corner_radius=8,
            command=self._abrir_modal_nueva_persona,
        )
        btn_nueva.pack(side="right")

        # Barra de Búsqueda (Estilo Clean Light Windows 11)
        search_frame = ctk.CTkFrame(
            self,
            fg_color=Colors.BG_CARD,
            corner_radius=8,
            border_width=1,
            border_color=Colors.BORDER_SUBTLE,
        )
        search_frame.pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkLabel(
            search_frame,
            text="🔍 Buscar Persona:",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=Colors.TEXT_MUTED,
        ).pack(side="left", padx=12, pady=10)

        entry_search = ctk.CTkEntry(
            search_frame,
            textvariable=self.busqueda_var,
            placeholder_text="Filtrar por documento, nombre o código...",
            width=320,
            fg_color=Colors.BG_WINDOW,
            border_color=Colors.BORDER_SUBTLE,
            text_color=Colors.TEXT_MAIN,
        )
        entry_search.pack(side="left", padx=5, pady=10)
        entry_search.bind("<KeyRelease>", lambda e: self.actualizar_tablas())

        btn_clear = ctk.CTkButton(
            search_frame,
            text="Limpiar",
            width=80,
            fg_color="#E2E8F0",
            hover_color="#CBD5E1",
            text_color=Colors.TEXT_MAIN,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            command=self._limpiar_busqueda,
        )
        btn_clear.pack(side="left", padx=5, pady=10)

        # Pestañas
        self.tabview = create_styled_tabview(self)
        self.tabview.pack(fill="both", expand=True, padx=15, pady=5)

        self.tab_estudiantes = self.tabview.add("👨‍🎓 Estudiantes")
        self.tab_profesores = self.tabview.add("👨‍🏫 Profesores")
        self.tab_administrativos = self.tabview.add("👔 Administrativos")

        self.actualizar_tablas()

    def _limpiar_busqueda(self) -> None:
        self.busqueda_var.set("")
        self.actualizar_tablas()

    def actualizar_tablas(self) -> None:
        q = self.busqueda_var.get().strip().lower()
        self._llenar_tab_estudiantes(q)
        self._llenar_tab_profesores(q)
        self._llenar_tab_administrativos(q)

    # ------------------------------------------------------------------
    # TAB ESTUDIANTES
    # ------------------------------------------------------------------
    def _llenar_tab_estudiantes(self, query: str = "") -> None:
        for w in self.tab_estudiantes.winfo_children():
            w.destroy()

        headers = ["Código", "Documento", "Nombre Completo", "Semestre", "Promedio", "Estado Académico", "Acciones"]
        col_weights = [2, 2, 3, 1, 1, 1, 2]
        col_mins = [70, 80, 140, 60, 50, 70, 70]

        table = PITAGridTable(self.tab_estudiantes, headers=headers, col_weights=col_weights, col_mins=col_mins)
        table.pack(fill="both", expand=True, padx=5, pady=5)

        estud_list = self.controller.estudiantes
        if query:
            estud_list = [
                e for e in estud_list
                if query in str(getattr(e, "codigoEstudiante", "")).lower()
                or query in str(getattr(e, "estadoAcademico", "")).lower()
                or any(query in str(getattr(p, "numeroDocumento", "")).lower() or query in str(getattr(p, "primerNombre", "")).lower() or query in str(getattr(p, "primerApellido", "")).lower() for p in self.controller.personas if getattr(p, "idPersona", None) == getattr(e, "idPersona", None))
            ]

        if not estud_list:
            ctk.CTkLabel(table, text="No hay estudiantes coincidentes.", text_color="#94A3B8").pack(pady=30)
            return

        for est in estud_list:
            pers = next((p for p in self.controller.personas if getattr(p, "idPersona", None) == getattr(est, "idPersona", None)), None)
            doc = getattr(pers, "numeroDocumento", "N/A") if pers else "N/A"
            nombre = f"{getattr(pers, 'primerNombre', '')} {getattr(pers, 'primerApellido', '')}" if pers else "Sin Persona"

            estado_acad = str(getattr(est, "estadoAcademico", "ACTIVO"))
            promedio = float(getattr(est, "promedioAcumulado", 0.0) or 0.0)

            # Badge Status Pill
            if estado_acad == "EBRA" or promedio < 3.0:
                badge_tuple = ("badge", "⚠️ EBRA", "ebra")
            else:
                badge_tuple = ("badge", "● ACTIVO", "active")

            act_spec = (
                "actions",
                [
                    ("👁️ Ver", lambda p=pers: self._ver_detalle_persona(p), "#6366F1", "#4F46E5"),
                    ("✏️ Editar", lambda e=est, p=pers: self._editar_estudiante(e, p), "#334155", "#475569"),
                    ("❌ Desactivar", lambda e_id=getattr(est, "idEstudiante", 0): self._desactivar_estudiante(e_id), "#EF4444", "#DC2626"),
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

    # ------------------------------------------------------------------
    # TAB PROFESORES
    # ------------------------------------------------------------------
    def _llenar_tab_profesores(self, query: str = "") -> None:
        for w in self.tab_profesores.winfo_children():
            w.destroy()

        headers = ["Código", "Documento", "Nombre Completo", "Tipo Profesor", "Categoría", "Horas/Semana", "Acciones"]
        col_weights = [2, 2, 3, 1, 1, 1, 2]
        col_mins = [70, 80, 140, 50, 70, 70, 70]

        table = PITAGridTable(self.tab_profesores, headers=headers, col_weights=col_weights, col_mins=col_mins)
        table.pack(fill="both", expand=True, padx=5, pady=5)

        prof_list = self.controller.profesores
        if query:
            prof_list = [
                p for p in prof_list
                if query in str(getattr(p, "codigoProfesor", "")).lower()
                or query in str(getattr(p, "tipoProfesor", "")).lower()
                or any(query in str(getattr(pers, "numeroDocumento", "")).lower() or query in str(getattr(pers, "primerNombre", "")).lower() or query in str(getattr(pers, "primerApellido", "")).lower() for pers in self.controller.personas if getattr(pers, "idPersona", None) == getattr(p, "idPersona", None))
            ]

        if not prof_list:
            ctk.CTkLabel(table, text="No hay profesores coincidentes.", text_color="#94A3B8").pack(pady=30)
            return

        for prof in prof_list:
            pers = next((p for p in self.controller.personas if getattr(p, "idPersona", None) == getattr(prof, "idPersona", None)), None)
            doc = getattr(pers, "numeroDocumento", "N/A") if pers else "N/A"
            nombre = f"{getattr(pers, 'primerNombre', '')} {getattr(pers, 'primerApellido', '')}" if pers else "Sin Persona"

            tipo = str(getattr(prof, "tipoProfesor", "PLANTA"))
            cat = str(getattr(prof, "categoriaDocente", "TITULAR"))

            badge_tuple = ("badge", tipo, tipo.lower())

            act_spec = (
                "actions",
                [
                    ("👁️ Ver", lambda p=pers: self._ver_detalle_persona(p), "#6366F1", "#4F46E5"),
                    ("✏️ Editar", lambda pr=prof, p=pers: self._editar_profesor(pr, p), "#334155", "#475569"),
                    ("❌ Desactivar", lambda p_id=getattr(prof, "idProfesor", 0): self._desactivar_profesor(p_id), "#EF4444", "#DC2626"),
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

    # ------------------------------------------------------------------
    # TAB ADMINISTRATIVOS
    # ------------------------------------------------------------------
    def _llenar_tab_administrativos(self, query: str = "") -> None:
        for w in self.tab_administrativos.winfo_children():
            w.destroy()

        headers = ["Código", "Documento", "Nombre Completo", "Cargo", "Dependencia", "Salario Base", "Acciones"]
        col_weights = [2, 2, 3, 2, 2, 1, 2]
        col_mins = [70, 80, 140, 80, 80, 70, 70]

        table = PITAGridTable(self.tab_administrativos, headers=headers, col_weights=col_weights, col_mins=col_mins)
        table.pack(fill="both", expand=True, padx=5, pady=5)

        adm_list = self.controller.administrativos
        if query:
            adm_list = [
                a for a in adm_list
                if query in str(getattr(a, "codigoEmpleado", "")).lower()
                or query in str(getattr(a, "cargo", "")).lower()
                or any(query in str(getattr(pers, "numeroDocumento", "")).lower() or query in str(getattr(pers, "primerNombre", "")).lower() or query in str(getattr(pers, "primerApellido", "")).lower() for pers in self.controller.personas if getattr(pers, "idPersona", None) == getattr(a, "idPersona", None))
            ]

        if not adm_list:
            ctk.CTkLabel(table, text="No hay administrativos coincidentes.", text_color="#94A3B8").pack(pady=30)
            return

        for adm in adm_list:
            pers = next((p for p in self.controller.personas if getattr(p, "idPersona", None) == getattr(adm, "idPersona", None)), None)
            doc = getattr(pers, "numeroDocumento", "N/A") if pers else "N/A"
            nombre = f"{getattr(pers, 'primerNombre', '')} {getattr(pers, 'primerApellido', '')}" if pers else "Sin Persona"

            sal = str(getattr(adm, 'salarioBase', '0'))
            sal_fmt = f"$ {int(float(sal)):,} COP" if sal.replace(".","").isdigit() else sal

            act_spec = (
                "actions",
                [
                    ("👁️ Ver", lambda p=pers: self._ver_detalle_persona(p), "#6366F1", "#4F46E5"),
                    ("✏️ Editar", lambda a=adm, p=pers: self._editar_administrativo(a, p), "#334155", "#475569"),
                    ("❌ Desactivar", lambda a_id=getattr(adm, "idAdministrativo", 0): self._desactivar_administrativo(a_id), "#EF4444", "#DC2626"),
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

    def _crear_badge(self, parent: ctk.CTkFrame, text: str, bg_color: str, text_color: str, border_color: str) -> None:
        pill = ctk.CTkFrame(parent, fg_color=bg_color, corner_radius=12, border_width=1, border_color=border_color)
        pill.pack(side="left", padx=10, pady=6)
        ctk.CTkLabel(pill, text=text, font=ctk.CTkFont(size=10, weight="bold"), text_color=text_color).pack(padx=8, pady=2)

    def _abrir_modal_nueva_persona(self) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title("➕ Registrar Persona y Asignar Rol en PITA")
        dialog.geometry("640x760")
        dialog.minsize(580, 620)
        dialog.grab_set()

        # Header
        header_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(15, 10))

        ctk.CTkLabel(
            header_frame,
            text="➕ Registrar Nueva Persona y Asignar Rol",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#F8FAFC",
        ).pack(anchor="w")
        ctk.CTkLabel(
            header_frame,
            text="Complete los datos de identificación, contacto y la información del rol académico o laboral.",
            font=ctk.CTkFont(size=11),
            text_color="#94A3B8",
        ).pack(anchor="w", pady=(2, 0))

        scroll = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        # -------------------------------------------------------------
        # SECCIÓN 1: IDENTIFICACIÓN Y CONTACTO
        # -------------------------------------------------------------
        card_p = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
        card_p.pack(fill="x", pady=6)

        ctk.CTkLabel(
            card_p,
            text="👤 1. Identificación y Contacto Personal",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#38BDF8",
        ).pack(anchor="w", padx=15, pady=(12, 8))

        grid_p = ctk.CTkFrame(card_p, fg_color="transparent")
        grid_p.pack(fill="x", padx=15, pady=(0, 12))
        grid_p.columnconfigure(0, weight=1)
        grid_p.columnconfigure(1, weight=1)

        # Fila 0: Tipo doc + Documento
        ctk.CTkLabel(grid_p, text="Tipo Documento *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=0, column=0, sticky="w", padx=5, pady=(2, 0))
        ctk.CTkLabel(grid_p, text="Número de Documento *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=0, column=1, sticky="w", padx=5, pady=(2, 0))

        combo_tdoc = ctk.CTkComboBox(grid_p, values=["CC", "TI", "CE", "PASAPORTE"])
        combo_tdoc.set("CC")
        combo_tdoc.grid(row=1, column=0, sticky="ew", padx=5, pady=(2, 8))

        entry_doc = ctk.CTkEntry(grid_p, placeholder_text="ej: 1065890123")
        entry_doc.grid(row=1, column=1, sticky="ew", padx=5, pady=(2, 8))

        # Fila 2: Primer nombre + Segundo nombre
        ctk.CTkLabel(grid_p, text="Primer Nombre *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=2, column=0, sticky="w", padx=5, pady=(2, 0))
        ctk.CTkLabel(grid_p, text="Segundo Nombre", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=2, column=1, sticky="w", padx=5, pady=(2, 0))

        entry_nom1 = ctk.CTkEntry(grid_p, placeholder_text="ej: Juan")
        entry_nom1.grid(row=3, column=0, sticky="ew", padx=5, pady=(2, 8))

        entry_nom2 = ctk.CTkEntry(grid_p, placeholder_text="ej: Carlos (opcional)")
        entry_nom2.grid(row=3, column=1, sticky="ew", padx=5, pady=(2, 8))

        # Fila 4: Primer apellido + Segundo apellido
        ctk.CTkLabel(grid_p, text="Primer Apellido *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=4, column=0, sticky="w", padx=5, pady=(2, 0))
        ctk.CTkLabel(grid_p, text="Segundo Apellido", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=4, column=1, sticky="w", padx=5, pady=(2, 0))

        entry_ape1 = ctk.CTkEntry(grid_p, placeholder_text="ej: Pérez")
        entry_ape1.grid(row=5, column=0, sticky="ew", padx=5, pady=(2, 8))

        entry_ape2 = ctk.CTkEntry(grid_p, placeholder_text="ej: Gómez (opcional)")
        entry_ape2.grid(row=5, column=1, sticky="ew", padx=5, pady=(2, 8))

        # Fila 6: Fecha Nacimiento + Teléfono
        ctk.CTkLabel(grid_p, text="Fecha Nacimiento (AAAA-MM-DD)", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=6, column=0, sticky="w", padx=5, pady=(2, 0))
        ctk.CTkLabel(grid_p, text="Teléfono / Celular", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=6, column=1, sticky="w", padx=5, pady=(2, 0))

        entry_fnac = ctk.CTkEntry(grid_p, placeholder_text="ej: 1998-05-15")
        entry_fnac.grid(row=7, column=0, sticky="ew", padx=5, pady=(2, 8))

        entry_tel = ctk.CTkEntry(grid_p, placeholder_text="ej: 3001234567")
        entry_tel.grid(row=7, column=1, sticky="ew", padx=5, pady=(2, 8))

        # Fila 8: Correo Institucional + Correo Personal
        ctk.CTkLabel(grid_p, text="Correo Institucional", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=8, column=0, sticky="w", padx=5, pady=(2, 0))
        ctk.CTkLabel(grid_p, text="Correo Personal", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=8, column=1, sticky="w", padx=5, pady=(2, 0))

        entry_correo_inst = ctk.CTkEntry(grid_p, placeholder_text="ej: jperez@unicesar.edu.co")
        entry_correo_inst.grid(row=9, column=0, sticky="ew", padx=5, pady=(2, 8))

        entry_correo_pers = ctk.CTkEntry(grid_p, placeholder_text="ej: jperez@gmail.com")
        entry_correo_pers.grid(row=9, column=1, sticky="ew", padx=5, pady=(2, 8))

        # Fila 10: Dirección + Ciudad Residencia
        ctk.CTkLabel(grid_p, text="Dirección", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=10, column=0, sticky="w", padx=5, pady=(2, 0))
        ctk.CTkLabel(grid_p, text="Ciudad de Residencia", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=10, column=1, sticky="w", padx=5, pady=(2, 0))

        entry_dir = ctk.CTkEntry(grid_p, placeholder_text="ej: Calle 16 # 14-25")
        entry_dir.grid(row=11, column=0, sticky="ew", padx=5, pady=(2, 4))

        entry_ciudad = ctk.CTkEntry(grid_p, placeholder_text="ej: Valledupar")
        entry_ciudad.grid(row=11, column=1, sticky="ew", padx=5, pady=(2, 4))

        # -------------------------------------------------------------
        # SECCIÓN 2: ROL Y VINCULACIÓN EN PITA
        # -------------------------------------------------------------
        card_r = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
        card_r.pack(fill="x", pady=6)

        ctk.CTkLabel(
            card_r,
            text="🎓 2. Rol y Vinculación en PITA",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#A78BFA",
        ).pack(anchor="w", padx=15, pady=(12, 6))

        row_rol = ctk.CTkFrame(card_r, fg_color="transparent")
        row_rol.pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkLabel(row_rol, text="Rol Institucional a Asignar:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(side="left", padx=(0, 10))
        combo_rol = ctk.CTkComboBox(row_rol, values=["ESTUDIANTE", "PROFESOR", "ADMINISTRATIVO"], width=200)
        combo_rol.set("ESTUDIANTE")
        combo_rol.pack(side="left")

        # Contenedor dinámico según el rol
        sub_rol = ctk.CTkFrame(card_r, fg_color="transparent")
        sub_rol.pack(fill="x", padx=15, pady=(0, 15))
        sub_rol.columnconfigure(0, weight=1)
        sub_rol.columnconfigure(1, weight=1)

        # Variables / widgets del sub-formulario
        widgets_rol: dict[str, ctk.CTkBaseClass] = {}

        def _cambiar_rol(nuevo_rol: str) -> None:
            for w in sub_rol.winfo_children():
                w.destroy()
            widgets_rol.clear()

            # Opciones de programas y planes disponibles
            prog_vals = [f"{p.idPrograma} - {p.nombre}" for p in self.controller.programas] if self.controller.programas else ["1 - Programa General"]
            plan_vals = [f"{pl.idPlanEstudio} - {pl.nombre}" for pl in self.controller.planes] if self.controller.planes else ["1 - Plan General"]

            if nuevo_rol == "ESTUDIANTE":
                ctk.CTkLabel(sub_rol, text="Código Estudiante *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=0, column=0, sticky="w", padx=5, pady=(2, 0))
                ctk.CTkLabel(sub_rol, text="Semestre Actual", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=0, column=1, sticky="w", padx=5, pady=(2, 0))

                entry_cod = ctk.CTkEntry(sub_rol, placeholder_text="ej: EST-2026-01")
                entry_cod.grid(row=1, column=0, sticky="ew", padx=5, pady=(2, 8))
                widgets_rol["codigo"] = entry_cod

                combo_sem = ctk.CTkComboBox(sub_rol, values=[str(i) for i in range(1, 11)])
                combo_sem.set("1")
                combo_sem.grid(row=1, column=1, sticky="ew", padx=5, pady=(2, 8))
                widgets_rol["semestre"] = combo_sem

                ctk.CTkLabel(sub_rol, text="Programa Académico *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=2, column=0, sticky="w", padx=5, pady=(2, 0))
                ctk.CTkLabel(sub_rol, text="Plan de Estudio *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=2, column=1, sticky="w", padx=5, pady=(2, 0))

                combo_prog = ctk.CTkComboBox(sub_rol, values=prog_vals)
                combo_prog.set(prog_vals[0])
                combo_prog.grid(row=3, column=0, sticky="ew", padx=5, pady=(2, 8))
                widgets_rol["programa"] = combo_prog

                combo_plan = ctk.CTkComboBox(sub_rol, values=plan_vals)
                combo_plan.set(plan_vals[0])
                combo_plan.grid(row=3, column=1, sticky="ew", padx=5, pady=(2, 8))
                widgets_rol["plan"] = combo_plan

                ctk.CTkLabel(sub_rol, text="Estado Académico", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=4, column=0, sticky="w", padx=5, pady=(2, 0))
                ctk.CTkLabel(sub_rol, text="Fecha Ingreso (AAAA-MM-DD)", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=4, column=1, sticky="w", padx=5, pady=(2, 0))

                combo_est_acad = ctk.CTkComboBox(sub_rol, values=["ACTIVO", "ASPIRANTE", "ADMITIDO", "MATRICULADO"])
                combo_est_acad.set("ACTIVO")
                combo_est_acad.grid(row=5, column=0, sticky="ew", padx=5, pady=(2, 4))
                widgets_rol["estado_academico"] = combo_est_acad

                entry_fing = ctk.CTkEntry(sub_rol)
                entry_fing.insert(0, date.today().strftime("%Y-%m-%d"))
                entry_fing.grid(row=5, column=1, sticky="ew", padx=5, pady=(2, 4))
                widgets_rol["fecha_ingreso"] = entry_fing

            elif nuevo_rol == "PROFESOR":
                ctk.CTkLabel(sub_rol, text="Código Profesor *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=0, column=0, sticky="w", padx=5, pady=(2, 0))
                ctk.CTkLabel(sub_rol, text="Programa Principal *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=0, column=1, sticky="w", padx=5, pady=(2, 0))

                entry_cod = ctk.CTkEntry(sub_rol, placeholder_text="ej: PROF-2026-01")
                entry_cod.grid(row=1, column=0, sticky="ew", padx=5, pady=(2, 8))
                widgets_rol["codigo"] = entry_cod

                combo_prog = ctk.CTkComboBox(sub_rol, values=prog_vals)
                combo_prog.set(prog_vals[0])
                combo_prog.grid(row=1, column=1, sticky="ew", padx=5, pady=(2, 8))
                widgets_rol["programa"] = combo_prog

                ctk.CTkLabel(sub_rol, text="Tipo de Profesor / Vinculación *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=2, column=0, sticky="w", padx=5, pady=(2, 0))
                ctk.CTkLabel(sub_rol, text="Categoría Docente *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=2, column=1, sticky="w", padx=5, pady=(2, 0))

                combo_tipo = ctk.CTkComboBox(sub_rol, values=["PLANTA", "OCASIONAL_TC", "OCASIONAL_MT", "CATEDRA"])
                combo_tipo.set("PLANTA")
                combo_tipo.grid(row=3, column=0, sticky="ew", padx=5, pady=(2, 8))
                widgets_rol["tipo_profesor"] = combo_tipo

                combo_cat = ctk.CTkComboBox(sub_rol, values=["AUXILIAR", "ASISTENTE", "ASOCIADO", "TITULAR", "NO_CATEGORIZADO"])
                combo_cat.set("ASISTENTE")
                combo_cat.grid(row=3, column=1, sticky="ew", padx=5, pady=(2, 8))
                widgets_rol["categoria_docente"] = combo_cat

                ctk.CTkLabel(sub_rol, text="Dedicación *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=4, column=0, sticky="w", padx=5, pady=(2, 0))
                ctk.CTkLabel(sub_rol, text="Horas Semanales", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=4, column=1, sticky="w", padx=5, pady=(2, 0))

                combo_ded = ctk.CTkComboBox(sub_rol, values=["TIEMPO_COMPLETO", "MEDIO_TIEMPO", "CATEDRA"])
                combo_ded.set("TIEMPO_COMPLETO")
                combo_ded.grid(row=5, column=0, sticky="ew", padx=5, pady=(2, 8))
                widgets_rol["dedicacion"] = combo_ded

                entry_horas = ctk.CTkEntry(sub_rol)
                entry_horas.insert(0, "40")
                entry_horas.grid(row=5, column=1, sticky="ew", padx=5, pady=(2, 8))
                widgets_rol["horas"] = entry_horas

                ctk.CTkLabel(sub_rol, text="Máximo Nivel de Estudio", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=6, column=0, sticky="w", padx=5, pady=(2, 0))
                ctk.CTkLabel(sub_rol, text="Puntos Salariales (Dec. 1279)", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=6, column=1, sticky="w", padx=5, pady=(2, 0))

                combo_nivel = ctk.CTkComboBox(sub_rol, values=["PREGRADO", "ESPECIALIZACION", "MAESTRIA", "DOCTORADO"])
                combo_nivel.set("MAESTRIA")
                combo_nivel.grid(row=7, column=0, sticky="ew", padx=5, pady=(2, 8))
                widgets_rol["nivel_estudio"] = combo_nivel

                entry_puntos = ctk.CTkEntry(sub_rol)
                entry_puntos.insert(0, "350")
                entry_puntos.grid(row=7, column=1, sticky="ew", padx=5, pady=(2, 8))
                widgets_rol["puntos"] = entry_puntos

                ctk.CTkLabel(sub_rol, text="Título Profesional", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=8, column=0, sticky="w", padx=5, pady=(2, 0))
                ctk.CTkLabel(sub_rol, text="Área de Conocimiento", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=8, column=1, sticky="w", padx=5, pady=(2, 0))

                entry_tit = ctk.CTkEntry(sub_rol, placeholder_text="ej: Ingeniero de Sistemas")
                entry_tit.grid(row=9, column=0, sticky="ew", padx=5, pady=(2, 4))
                widgets_rol["titulo"] = entry_tit

                entry_area = ctk.CTkEntry(sub_rol, placeholder_text="ej: Computación y Software")
                entry_area.grid(row=9, column=1, sticky="ew", padx=5, pady=(2, 4))
                widgets_rol["area"] = entry_area

            elif nuevo_rol == "ADMINISTRATIVO":
                ctk.CTkLabel(sub_rol, text="Código Empleado *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=0, column=0, sticky="w", padx=5, pady=(2, 0))
                ctk.CTkLabel(sub_rol, text="Cargo Institucional *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=0, column=1, sticky="w", padx=5, pady=(2, 0))

                entry_cod = ctk.CTkEntry(sub_rol, placeholder_text="ej: ADM-2026-01")
                entry_cod.grid(row=1, column=0, sticky="ew", padx=5, pady=(2, 8))
                widgets_rol["codigo"] = entry_cod

                entry_cargo = ctk.CTkEntry(sub_rol, placeholder_text="ej: Profesional Universitario")
                entry_cargo.insert(0, "Profesional Universitario")
                entry_cargo.grid(row=1, column=1, sticky="ew", padx=5, pady=(2, 8))
                widgets_rol["cargo"] = entry_cargo

                ctk.CTkLabel(sub_rol, text="Dependencia *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=2, column=0, sticky="w", padx=5, pady=(2, 0))
                ctk.CTkLabel(sub_rol, text="Tipo Contratación", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=2, column=1, sticky="w", padx=5, pady=(2, 0))

                entry_dep = ctk.CTkEntry(sub_rol, placeholder_text="ej: Vicerrectoría Académica")
                entry_dep.insert(0, "Vicerrectoría Académica")
                entry_dep.grid(row=3, column=0, sticky="ew", padx=5, pady=(2, 8))
                widgets_rol["dependencia"] = entry_dep

                combo_tcont = ctk.CTkComboBox(sub_rol, values=["PLANTA", "PROVISIONALIDAD", "PRESTACION_SERVICIOS"])
                combo_tcont.set("PLANTA")
                combo_tcont.grid(row=3, column=1, sticky="ew", padx=5, pady=(2, 8))
                widgets_rol["tipo_contratacion"] = combo_tcont

                ctk.CTkLabel(sub_rol, text="Salario Base Mensual ($) *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=4, column=0, sticky="w", padx=5, pady=(2, 0))
                ctk.CTkLabel(sub_rol, text="Fecha Vinculación (AAAA-MM-DD)", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=4, column=1, sticky="w", padx=5, pady=(2, 0))

                entry_sal = ctk.CTkEntry(sub_rol)
                entry_sal.insert(0, "2800000")
                entry_sal.grid(row=5, column=0, sticky="ew", padx=5, pady=(2, 4))
                widgets_rol["salario"] = entry_sal

                entry_fvin = ctk.CTkEntry(sub_rol)
                entry_fvin.insert(0, date.today().strftime("%Y-%m-%d"))
                entry_fvin.grid(row=5, column=1, sticky="ew", padx=5, pady=(2, 4))
                widgets_rol["fecha_vinculacion"] = entry_fvin

        combo_rol.configure(command=_cambiar_rol)
        _cambiar_rol("ESTUDIANTE")

        # Mensaje de error / estado
        lbl_error = ctk.CTkLabel(scroll, text="", text_color="#EF4444", font=ctk.CTkFont(size=12, weight="bold"))
        lbl_error.pack(pady=(5, 2))

        def _guardar():
            doc = entry_doc.get().strip()
            nom1 = entry_nom1.get().strip()
            nom2 = entry_nom2.get().strip()
            ape1 = entry_ape1.get().strip()
            ape2 = entry_ape2.get().strip()
            fnac_str = entry_fnac.get().strip()
            tel = entry_tel.get().strip()
            correo_inst = entry_correo_inst.get().strip()
            correo_pers = entry_correo_pers.get().strip()
            direccion = entry_dir.get().strip()
            ciudad = entry_ciudad.get().strip()

            rol = combo_rol.get()
            cod_widget = widgets_rol.get("codigo")
            cod = cod_widget.get().strip() if cod_widget else ""

            # Validaciones básicas de campos obligatorios
            if not doc:
                lbl_error.configure(text="⚠️ El número de documento es obligatorio.")
                return
            if not nom1 or not ape1:
                lbl_error.configure(text="⚠️ El primer nombre y el primer apellido son obligatorios.")
                return
            if not cod:
                lbl_error.configure(text=f"⚠️ El código de {rol.lower()} es obligatorio.")
                return

            # Validar unicidad de documento
            if any(str(getattr(p, "numeroDocumento", "")).strip() == doc for p in self.controller.personas):
                lbl_error.configure(text=f"⚠️ Ya existe una persona registrada con el documento {doc}.")
                return

            # Validar unicidad de código según rol
            if rol == "ESTUDIANTE" and any(str(getattr(e, "codigoEstudiante", "")).strip() == cod for e in self.controller.estudiantes):
                lbl_error.configure(text=f"⚠️ Ya existe un estudiante con el código {cod}.")
                return
            elif rol == "PROFESOR" and any(str(getattr(pr, "codigoProfesor", "")).strip() == cod for pr in self.controller.profesores):
                lbl_error.configure(text=f"⚠️ Ya existe un profesor con el código {cod}.")
                return
            elif rol == "ADMINISTRATIVO" and any(str(getattr(a, "codigoEmpleado", "")).strip() == cod for a in self.controller.administrativos):
                lbl_error.configure(text=f"⚠️ Ya existe un administrativo con el código {cod}.")
                return

            # Parsear fecha de nacimiento si se suministró
            f_nac = None
            if fnac_str:
                try:
                    f_nac = datetime.strptime(fnac_str, "%Y-%m-%d").date()
                except ValueError:
                    lbl_error.configure(text="⚠️ Formato de Fecha de Nacimiento inválido. Use AAAA-MM-DD (ej: 1995-05-15).")
                    return

            # Generar ID de persona y crear registro
            new_id_p = (max((getattr(p, "idPersona", 0) or 0 for p in self.controller.personas), default=0)) + 1
            nueva_p = Persona(
                idPersona=new_id_p,
                tipoDocumento=combo_tdoc.get(),
                numeroDocumento=doc,
                primerNombre=nom1,
                segundoNombre=nom2 or None,
                primerApellido=ape1,
                segundoApellido=ape2 or None,
                fechaNacimiento=f_nac,
                direccion=direccion or None,
                telefono=tel or None,
                correoPersonal=correo_pers or None,
                correoInstitucional=correo_inst or f"{nom1.lower()}.{ape1.lower()}@unicesar.edu.co",
                ciudadResidencia=ciudad or None,
                fechaRegistro=date.today(),
                estado="ACTIVO",
            )
            self.controller.personas.append(nueva_p)

            # Asignar Rol Específico
            if rol == "ESTUDIANTE":
                sem_str = widgets_rol["semestre"].get().strip() if "semestre" in widgets_rol else "1"
                sem_val = int(sem_str) if sem_str.isdigit() else 1

                prog_sel = widgets_rol["programa"].get().split(" - ")[0] if "programa" in widgets_rol else "1"
                id_prog = int(prog_sel) if prog_sel.isdigit() else 1

                plan_sel = widgets_rol["plan"].get().split(" - ")[0] if "plan" in widgets_rol else "1"
                id_plan = int(plan_sel) if plan_sel.isdigit() else 1

                est_acad_str = widgets_rol["estado_academico"].get() if "estado_academico" in widgets_rol else "ACTIVO"
                try:
                    est_acad = EstadoAcademico[est_acad_str]
                except KeyError:
                    est_acad = EstadoAcademico.ACTIVO

                fing_str = widgets_rol["fecha_ingreso"].get().strip() if "fecha_ingreso" in widgets_rol else ""
                try:
                    f_ing = datetime.strptime(fing_str, "%Y-%m-%d").date() if fing_str else date.today()
                except ValueError:
                    f_ing = date.today()

                new_e = Estudiante(
                    idEstudiante=(max((getattr(e, "idEstudiante", 0) or 0 for e in self.controller.estudiantes), default=0)) + 1,
                    idPersona=new_id_p,
                    codigoEstudiante=cod,
                    idPrograma=id_prog,
                    idPlanEstudio=id_plan,
                    fechaIngreso=f_ing,
                    semestreActual=sem_val,
                    creditosAprobados=0,
                    promedioAcumulado=Decimal("5.0"),
                    estadoAcademico=est_acad,
                    estado="ACTIVO",
                )
                self.controller.estudiantes.append(new_e)

            elif rol == "PROFESOR":
                prog_sel = widgets_rol["programa"].get().split(" - ")[0] if "programa" in widgets_rol else "1"
                id_prog = int(prog_sel) if prog_sel.isdigit() else 1

                tipo_str = widgets_rol["tipo_profesor"].get() if "tipo_profesor" in widgets_rol else "PLANTA"
                try:
                    tipo_prof = TipoProfesor[tipo_str]
                except KeyError:
                    tipo_prof = TipoProfesor.PLANTA

                ded_str = widgets_rol["dedicacion"].get() if "dedicacion" in widgets_rol else "TIEMPO_COMPLETO"
                try:
                    dedicacion = Dedicacion[ded_str]
                except KeyError:
                    dedicacion = Dedicacion.TIEMPO_COMPLETO

                cat_str = widgets_rol["categoria_docente"].get() if "categoria_docente" in widgets_rol else "ASISTENTE"
                nivel_est = widgets_rol["nivel_estudio"].get() if "nivel_estudio" in widgets_rol else "MAESTRIA"
                tit_prof = widgets_rol["titulo"].get().strip() if "titulo" in widgets_rol else ""
                area_c = widgets_rol["area"].get().strip() if "area" in widgets_rol else ""

                horas_str = widgets_rol["horas"].get().strip() if "horas" in widgets_rol else "40"
                horas_val = Decimal(horas_str) if horas_str.replace(".", "", 1).isdigit() else Decimal("40")

                puntos_str = widgets_rol["puntos"].get().strip() if "puntos" in widgets_rol else "350"
                puntos_val = Decimal(puntos_str) if puntos_str.replace(".", "", 1).isdigit() else Decimal("350")

                new_prof = Profesor(
                    idProfesor=(max((getattr(p, "idProfesor", 0) or 0 for p in self.controller.profesores), default=0)) + 1,
                    idPersona=new_id_p,
                    codigoProfesor=cod,
                    idProgramaPrincipal=id_prog,
                    fechaVinculacion=date.today(),
                    tipoProfesor=tipo_prof,
                    categoriaDocente=cat_str,
                    dedicacion=dedicacion,
                    maximoNivelEstudio=nivel_est,
                    tituloProfesional=tit_prof or None,
                    areaConocimiento=area_c or None,
                    numeroHorasSemanales=horas_val,
                    puntosSalariales=puntos_val,
                    estado="ACTIVO",
                )
                self.controller.profesores.append(new_prof)

            elif rol == "ADMINISTRATIVO":
                cargo_val = widgets_rol["cargo"].get().strip() if "cargo" in widgets_rol else "Profesional Universitario"
                dep_val = widgets_rol["dependencia"].get().strip() if "dependencia" in widgets_rol else "Vicerrectoría Académica"
                tcont_val = widgets_rol["tipo_contratacion"].get() if "tipo_contratacion" in widgets_rol else "PLANTA"

                sal_str = widgets_rol["salario"].get().strip() if "salario" in widgets_rol else "2800000"
                sal_val = Decimal(sal_str) if sal_str.replace(".", "", 1).isdigit() else Decimal("2800000")

                fvin_str = widgets_rol["fecha_vinculacion"].get().strip() if "fecha_vinculacion" in widgets_rol else ""
                try:
                    f_vin = datetime.strptime(fvin_str, "%Y-%m-%d").date() if fvin_str else date.today()
                except ValueError:
                    f_vin = date.today()

                new_adm = Administrativo(
                    idAdministrativo=(max((getattr(a, "idAdministrativo", 0) or 0 for a in self.controller.administrativos), default=0)) + 1,
                    idPersona=new_id_p,
                    codigoEmpleado=cod,
                    cargo=cargo_val,
                    dependencia=dep_val,
                    tipoContratacion=tcont_val,
                    fechaVinculacion=f_vin,
                    salarioBase=sal_val,
                    estado="ACTIVO",
                )
                self.controller.administrativos.append(new_adm)

            self.controller._recrear_gestores()
            dialog.destroy()
            self.actualizar()

        # Botón Guardar
        btn_save = ctk.CTkButton(
            scroll,
            text="💾 Registrar Persona y Guardar Rol",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#059669",
            hover_color="#047857",
            height=40,
            command=_guardar,
        )
        btn_save.pack(fill="x", padx=15, pady=(10, 20))

    def _desactivar_estudiante(self, id_estudiante: int) -> None:
        est = next((e for e in self.controller.estudiantes if getattr(e, "idEstudiante", 0) == id_estudiante), None)
        if est:
            est.estado = "INACTIVO"
            self.controller._recrear_gestores()
            self.actualizar_tablas()

    def _desactivar_profesor(self, id_profesor: int) -> None:
        prof = next((p for p in self.controller.profesores if getattr(p, "idProfesor", 0) == id_profesor), None)
        if prof:
            prof.estado = "INACTIVO"
            self.controller._recrear_gestores()
            self.actualizar_tablas()

    def _desactivar_administrativo(self, id_administrativo: int) -> None:
        adm = next((a for a in self.controller.administrativos if getattr(a, "idAdministrativo", 0) == id_administrativo), None)
        if adm:
            adm.estado = "INACTIVO"
            self.controller._recrear_gestores()
            self.actualizar_tablas()

    # ------------------------------------------------------------------
    # MODALES DE DETALLE Y EDICIÓN (CRUD MODIFICACIÓN Y CONSULTA)
    # ------------------------------------------------------------------
    def _ver_detalle_persona(self, persona: Persona | None) -> None:
        if not persona:
            return
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"👁️ Ficha Técnica — {persona.primerNombre} {persona.primerApellido}")
        dialog.geometry("520x620")
        dialog.grab_set()

        nom_completo = f"{persona.primerNombre} {persona.segundoNombre or ''} {persona.primerApellido} {persona.segundoApellido or ''}".strip()
        ctk.CTkLabel(dialog, text=f"👤 {nom_completo}", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 5))
        ctk.CTkLabel(dialog, text="Ficha de Identificación, Contacto y Roles en PITA", font=ctk.CTkFont(size=11), text_color="#94A3B8").pack(pady=(0, 10))

        scroll_info = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        scroll_info.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        info_frame = ctk.CTkFrame(scroll_info, fg_color=Colors.BG_CARD_HOVER, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
        info_frame.pack(fill="x", pady=6)

        ctk.CTkLabel(info_frame, text="Datos Personales y Contacto", font=ctk.CTkFont(size=12, weight="bold"), text_color="#38BDF8").pack(anchor="w", padx=15, pady=(10, 6))

        detalles = [
            ("📄 Documento Identidad:", f"{persona.tipoDocumento or 'CC'} {persona.numeroDocumento}"),
            ("🎂 Fecha Nacimiento:", str(persona.fechaNacimiento or "No registrada")),
            ("📧 Correo Institucional:", persona.correoInstitucional or "N/A"),
            ("📧 Correo Personal:", persona.correoPersonal or "No registrado"),
            ("📱 Teléfono Contacto:", persona.telefono or "No registrado"),
            ("🏠 Dirección:", persona.direccion or "No registrada"),
            ("🏙️ Ciudad de Residencia:", persona.ciudadResidencia or "No registrada"),
            ("📅 Fecha Registro:", str(persona.fechaRegistro or "N/A")),
            ("🟢 Estado Sistema:", persona.estado or "ACTIVO"),
        ]

        for lbl, val in detalles:
            r = ctk.CTkFrame(info_frame, fg_color="transparent")
            r.pack(fill="x", padx=15, pady=3)
            ctk.CTkLabel(r, text=lbl, font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(side="left")
            ctk.CTkLabel(r, text=str(val), font=ctk.CTkFont(size=11), text_color="#F8FAFC").pack(side="right")

        ctk.CTkLabel(info_frame, text="").pack(pady=2)

        # Buscar roles asociados
        est_rel = next((e for e in self.controller.estudiantes if getattr(e, "idPersona", None) == persona.idPersona), None)
        prof_rel = next((p for p in self.controller.profesores if getattr(p, "idPersona", None) == persona.idPersona), None)
        adm_rel = next((a for a in self.controller.administrativos if getattr(a, "idPersona", None) == persona.idPersona), None)

        if est_rel:
            card_rol_info = ctk.CTkFrame(scroll_info, fg_color=Colors.BG_CARD_HOVER, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
            card_rol_info.pack(fill="x", pady=6)
            ctk.CTkLabel(card_rol_info, text="👨‍🎓 Rol: Estudiante", font=ctk.CTkFont(size=12, weight="bold"), text_color="#34D399").pack(anchor="w", padx=15, pady=(10, 6))

            prog_name = next((p.nombre for p in self.controller.programas if p.idPrograma == est_rel.idPrograma), f"Prog #{est_rel.idPrograma}")
            detalles_est = [
                ("Código Estudiante:", str(est_rel.codigoEstudiante)),
                ("Programa Académico:", str(prog_name)),
                ("Semestre Actual:", f"Semestre {est_rel.semestreActual}"),
                ("Promedio Acumulado:", f"{float(est_rel.promedioAcumulado or 0.0):.2f}"),
                ("Estado Académico:", str(est_rel.estadoAcademico)),
            ]
            for lbl, val in detalles_est:
                r = ctk.CTkFrame(card_rol_info, fg_color="transparent")
                r.pack(fill="x", padx=15, pady=3)
                ctk.CTkLabel(r, text=lbl, font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(side="left")
                ctk.CTkLabel(r, text=str(val), font=ctk.CTkFont(size=11), text_color="#F8FAFC").pack(side="right")
            ctk.CTkLabel(card_rol_info, text="").pack(pady=2)

        if prof_rel:
            card_rol_info = ctk.CTkFrame(scroll_info, fg_color=Colors.BG_CARD_HOVER, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
            card_rol_info.pack(fill="x", pady=6)
            ctk.CTkLabel(card_rol_info, text="👨‍🏫 Rol: Profesor", font=ctk.CTkFont(size=12, weight="bold"), text_color="#C084FC").pack(anchor="w", padx=15, pady=(10, 6))

            prog_name = next((p.nombre for p in self.controller.programas if p.idPrograma == prof_rel.idProgramaPrincipal), f"Prog #{prof_rel.idProgramaPrincipal}")
            detalles_prof = [
                ("Código Profesor:", str(prof_rel.codigoProfesor)),
                ("Programa Principal:", str(prog_name)),
                ("Tipo Profesor:", str(prof_rel.tipoProfesor)),
                ("Categoría:", str(prof_rel.categoriaDocente)),
                ("Dedicación:", str(prof_rel.dedicacion)),
                ("Horas Semanales:", f"{prof_rel.numeroHorasSemanales} h/sem"),
                ("Puntos Salariales:", str(prof_rel.puntosSalariales or "0")),
                ("Máximo Nivel Estudio:", str(prof_rel.maximoNivelEstudio or "N/A")),
                ("Título Profesional:", str(prof_rel.tituloProfesional or "N/A")),
            ]
            for lbl, val in detalles_prof:
                r = ctk.CTkFrame(card_rol_info, fg_color="transparent")
                r.pack(fill="x", padx=15, pady=3)
                ctk.CTkLabel(r, text=lbl, font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(side="left")
                ctk.CTkLabel(r, text=str(val), font=ctk.CTkFont(size=11), text_color="#F8FAFC").pack(side="right")
            ctk.CTkLabel(card_rol_info, text="").pack(pady=2)

        if adm_rel:
            card_rol_info = ctk.CTkFrame(scroll_info, fg_color=Colors.BG_CARD_HOVER, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
            card_rol_info.pack(fill="x", pady=6)
            ctk.CTkLabel(card_rol_info, text="👔 Rol: Administrativo", font=ctk.CTkFont(size=12, weight="bold"), text_color="#F59E0B").pack(anchor="w", padx=15, pady=(10, 6))

            detalles_adm = [
                ("Código Empleado:", str(adm_rel.codigoEmpleado)),
                ("Cargo:", str(adm_rel.cargo)),
                ("Dependencia:", str(adm_rel.dependencia)),
                ("Tipo Contratación:", str(getattr(adm_rel, "tipoContratacion", "PLANTA"))),
                ("Salario Base:", f"${float(adm_rel.salarioBase or 0):,.2f}"),
            ]
            for lbl, val in detalles_adm:
                r = ctk.CTkFrame(card_rol_info, fg_color="transparent")
                r.pack(fill="x", padx=15, pady=3)
                ctk.CTkLabel(r, text=lbl, font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(side="left")
                ctk.CTkLabel(r, text=str(val), font=ctk.CTkFont(size=11), text_color="#F8FAFC").pack(side="right")
            ctk.CTkLabel(card_rol_info, text="").pack(pady=2)

    def _editar_estudiante(self, est: Estudiante, pers: Persona | None) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"✏️ Editar Estudiante {est.codigoEstudiante}")
        dialog.geometry("620x720")
        dialog.minsize(560, 600)
        dialog.grab_set()

        # Header
        header_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(15, 10))

        ctk.CTkLabel(
            header_frame,
            text=f"✏️ Modificar Estudiante: {est.codigoEstudiante}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#F8FAFC",
        ).pack(anchor="w")
        ctk.CTkLabel(
            header_frame,
            text="Actualice la información personal, de contacto y los datos académicos del estudiante.",
            font=ctk.CTkFont(size=11),
            text_color="#94A3B8",
        ).pack(anchor="w", pady=(2, 0))

        scroll = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        # -------------------------------------------------------------
        # TARJETA 1: DATOS PERSONALES Y CONTACTO
        # -------------------------------------------------------------
        card_p = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
        card_p.pack(fill="x", pady=6)

        ctk.CTkLabel(
            card_p,
            text="👤 1. Información Personal y de Contacto",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#38BDF8",
        ).pack(anchor="w", padx=15, pady=(12, 8))

        grid_p = ctk.CTkFrame(card_p, fg_color="transparent")
        grid_p.pack(fill="x", padx=15, pady=(0, 12))
        grid_p.columnconfigure(0, weight=1)
        grid_p.columnconfigure(1, weight=1)

        # Nombres
        ctk.CTkLabel(grid_p, text="Primer Nombre *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=0, column=0, sticky="w", padx=5, pady=(2, 0))
        ctk.CTkLabel(grid_p, text="Segundo Nombre", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=0, column=1, sticky="w", padx=5, pady=(2, 0))

        entry_nom1 = ctk.CTkEntry(grid_p)
        if pers:
            entry_nom1.insert(0, pers.primerNombre or "")
        entry_nom1.grid(row=1, column=0, sticky="ew", padx=5, pady=(2, 8))

        entry_nom2 = ctk.CTkEntry(grid_p)
        if pers:
            entry_nom2.insert(0, pers.segundoNombre or "")
        entry_nom2.grid(row=1, column=1, sticky="ew", padx=5, pady=(2, 8))

        # Apellidos
        ctk.CTkLabel(grid_p, text="Primer Apellido *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=2, column=0, sticky="w", padx=5, pady=(2, 0))
        ctk.CTkLabel(grid_p, text="Segundo Apellido", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=2, column=1, sticky="w", padx=5, pady=(2, 0))

        entry_ape1 = ctk.CTkEntry(grid_p)
        if pers:
            entry_ape1.insert(0, pers.primerApellido or "")
        entry_ape1.grid(row=3, column=0, sticky="ew", padx=5, pady=(2, 8))

        entry_ape2 = ctk.CTkEntry(grid_p)
        if pers:
            entry_ape2.insert(0, pers.segundoApellido or "")
        entry_ape2.grid(row=3, column=1, sticky="ew", padx=5, pady=(2, 8))

        # Teléfono y Fecha Nacimiento
        ctk.CTkLabel(grid_p, text="Teléfono / Celular", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=4, column=0, sticky="w", padx=5, pady=(2, 0))
        ctk.CTkLabel(grid_p, text="Fecha Nacimiento (AAAA-MM-DD)", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=4, column=1, sticky="w", padx=5, pady=(2, 0))

        entry_tel = ctk.CTkEntry(grid_p)
        if pers:
            entry_tel.insert(0, pers.telefono or "")
        entry_tel.grid(row=5, column=0, sticky="ew", padx=5, pady=(2, 8))

        entry_fnac = ctk.CTkEntry(grid_p)
        if pers and pers.fechaNacimiento:
            entry_fnac.insert(0, str(pers.fechaNacimiento))
        entry_fnac.grid(row=5, column=1, sticky="ew", padx=5, pady=(2, 8))

        # Correos
        ctk.CTkLabel(grid_p, text="Correo Institucional", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=6, column=0, sticky="w", padx=5, pady=(2, 0))
        ctk.CTkLabel(grid_p, text="Correo Personal", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=6, column=1, sticky="w", padx=5, pady=(2, 0))

        entry_cinst = ctk.CTkEntry(grid_p)
        if pers:
            entry_cinst.insert(0, pers.correoInstitucional or "")
        entry_cinst.grid(row=7, column=0, sticky="ew", padx=5, pady=(2, 8))

        entry_cpers = ctk.CTkEntry(grid_p)
        if pers:
            entry_cpers.insert(0, pers.correoPersonal or "")
        entry_cpers.grid(row=7, column=1, sticky="ew", padx=5, pady=(2, 8))

        # Dirección y Ciudad
        ctk.CTkLabel(grid_p, text="Dirección", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=8, column=0, sticky="w", padx=5, pady=(2, 0))
        ctk.CTkLabel(grid_p, text="Ciudad de Residencia", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=8, column=1, sticky="w", padx=5, pady=(2, 0))

        entry_dir = ctk.CTkEntry(grid_p)
        if pers:
            entry_dir.insert(0, pers.direccion or "")
        entry_dir.grid(row=9, column=0, sticky="ew", padx=5, pady=(2, 4))

        entry_ciu = ctk.CTkEntry(grid_p)
        if pers:
            entry_ciu.insert(0, pers.ciudadResidencia or "")
        entry_ciu.grid(row=9, column=1, sticky="ew", padx=5, pady=(2, 4))

        # -------------------------------------------------------------
        # TARJETA 2: DATOS ACADÉMICOS
        # -------------------------------------------------------------
        card_a = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
        card_a.pack(fill="x", pady=6)

        ctk.CTkLabel(
            card_a,
            text="🎓 2. Información Académica",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#34D399",
        ).pack(anchor="w", padx=15, pady=(12, 8))

        grid_a = ctk.CTkFrame(card_a, fg_color="transparent")
        grid_a.pack(fill="x", padx=15, pady=(0, 12))
        grid_a.columnconfigure(0, weight=1)
        grid_a.columnconfigure(1, weight=1)

        prog_vals = [f"{p.idPrograma} - {p.nombre}" for p in self.controller.programas] if self.controller.programas else ["1 - Programa General"]
        plan_vals = [f"{pl.idPlanEstudio} - {pl.nombre}" for pl in self.controller.planes] if self.controller.planes else ["1 - Plan General"]

        # Programa y Plan
        ctk.CTkLabel(grid_a, text="Programa Académico *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=0, column=0, sticky="w", padx=5, pady=(2, 0))
        ctk.CTkLabel(grid_a, text="Plan de Estudio *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=0, column=1, sticky="w", padx=5, pady=(2, 0))

        combo_prog = ctk.CTkComboBox(grid_a, values=prog_vals)
        sel_prog = next((pv for pv in prog_vals if pv.startswith(f"{est.idPrograma} - ")), prog_vals[0])
        combo_prog.set(sel_prog)
        combo_prog.grid(row=1, column=0, sticky="ew", padx=5, pady=(2, 8))

        combo_plan = ctk.CTkComboBox(grid_a, values=plan_vals)
        sel_plan = next((pv for pv in plan_vals if pv.startswith(f"{est.idPlanEstudio} - ")), plan_vals[0])
        combo_plan.set(sel_plan)
        combo_plan.grid(row=1, column=1, sticky="ew", padx=5, pady=(2, 8))

        # Semestre y Estado Académico
        ctk.CTkLabel(grid_a, text="Semestre Actual", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=2, column=0, sticky="w", padx=5, pady=(2, 0))
        ctk.CTkLabel(grid_a, text="Estado Académico", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=2, column=1, sticky="w", padx=5, pady=(2, 0))

        combo_sem = ctk.CTkComboBox(grid_a, values=[str(i) for i in range(1, 11)])
        combo_sem.set(str(getattr(est, "semestreActual", 1) or 1))
        combo_sem.grid(row=3, column=0, sticky="ew", padx=5, pady=(2, 8))

        combo_est_acad = ctk.CTkComboBox(grid_a, values=["ACTIVO", "EBRA", "MATRICULADO", "ASPIRANTE", "ADMITIDO", "GRADUADO", "INACTIVO", "RETIRADO"])
        combo_est_acad.set(str(getattr(est, "estadoAcademico", "ACTIVO")))
        combo_est_acad.grid(row=3, column=1, sticky="ew", padx=5, pady=(2, 8))

        # Promedio y Créditos
        ctk.CTkLabel(grid_a, text="Promedio Acumulado (0.0 - 5.0)", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=4, column=0, sticky="w", padx=5, pady=(2, 0))
        ctk.CTkLabel(grid_a, text="Créditos Aprobados", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=4, column=1, sticky="w", padx=5, pady=(2, 0))

        entry_prom = ctk.CTkEntry(grid_a)
        entry_prom.insert(0, str(getattr(est, "promedioAcumulado", "0.0")))
        entry_prom.grid(row=5, column=0, sticky="ew", padx=5, pady=(2, 4))

        entry_cred = ctk.CTkEntry(grid_a)
        entry_cred.insert(0, str(getattr(est, "creditosAprobados", "0") or "0"))
        entry_cred.grid(row=5, column=1, sticky="ew", padx=5, pady=(2, 4))

        # Mensaje de error
        lbl_error = ctk.CTkLabel(scroll, text="", text_color="#EF4444", font=ctk.CTkFont(size=12, weight="bold"))
        lbl_error.pack(pady=(4, 2))

        def _guardar():
            nom1 = entry_nom1.get().strip()
            ape1 = entry_ape1.get().strip()
            if not nom1 or not ape1:
                lbl_error.configure(text="⚠️ Primer nombre y primer apellido son obligatorios.")
                return

            if pers:
                pers.primerNombre = nom1
                pers.segundoNombre = entry_nom2.get().strip() or None
                pers.primerApellido = ape1
                pers.segundoApellido = entry_ape2.get().strip() or None
                pers.telefono = entry_tel.get().strip() or None
                pers.correoInstitucional = entry_cinst.get().strip() or pers.correoInstitucional
                pers.correoPersonal = entry_cpers.get().strip() or None
                pers.direccion = entry_dir.get().strip() or None
                pers.ciudadResidencia = entry_ciu.get().strip() or None

                fnac_str = entry_fnac.get().strip()
                if fnac_str:
                    try:
                        pers.fechaNacimiento = datetime.strptime(fnac_str, "%Y-%m-%d").date()
                    except ValueError:
                        lbl_error.configure(text="⚠️ Formato de Fecha de Nacimiento debe ser AAAA-MM-DD.")
                        return

            # Actualizar datos de Estudiante
            prog_sel = combo_prog.get().split(" - ")[0]
            if prog_sel.isdigit():
                est.idPrograma = int(prog_sel)

            plan_sel = combo_plan.get().split(" - ")[0]
            if plan_sel.isdigit():
                est.idPlanEstudio = int(plan_sel)

            sem_str = combo_sem.get().strip()
            if sem_str.isdigit():
                est.semestreActual = int(sem_str)

            cred_str = entry_cred.get().strip()
            if cred_str.isdigit():
                est.creditosAprobados = int(cred_str)

            est_acad_str = combo_est_acad.get()
            try:
                est.estadoAcademico = EstadoAcademico[est_acad_str]
            except KeyError:
                pass

            try:
                val_p = Decimal(entry_prom.get().strip())
                est.promedioAcumulado = val_p
                # Si el usuario no forzó otro estado y el promedio es bajo, sugerir o aplicar EBRA
                if val_p < Decimal("3.0") and est.estadoAcademico == EstadoAcademico.ACTIVO:
                    est.estadoAcademico = EstadoAcademico.EBRA
            except Exception:
                pass

            self.controller._recrear_gestores()
            self.actualizar_tablas()
            dialog.destroy()

        ctk.CTkButton(scroll, text="💾 Guardar Cambios", font=ctk.CTkFont(size=13, weight="bold"), fg_color="#10B981", hover_color="#059669", height=40, command=_guardar).pack(fill="x", padx=15, pady=(10, 20))

    def _editar_profesor(self, prof: Profesor, pers: Persona | None) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"✏️ Editar Profesor {prof.codigoProfesor}")
        dialog.geometry("620x740")
        dialog.minsize(560, 600)
        dialog.grab_set()

        # Header
        header_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(15, 10))

        ctk.CTkLabel(
            header_frame,
            text=f"✏️ Modificar Profesor: {prof.codigoProfesor}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#F8FAFC",
        ).pack(anchor="w")
        ctk.CTkLabel(
            header_frame,
            text="Actualice la información personal, de contacto y los parámetros docentes y salariales.",
            font=ctk.CTkFont(size=11),
            text_color="#94A3B8",
        ).pack(anchor="w", pady=(2, 0))

        scroll = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        # -------------------------------------------------------------
        # TARJETA 1: DATOS PERSONALES Y CONTACTO
        # -------------------------------------------------------------
        card_p = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
        card_p.pack(fill="x", pady=6)

        ctk.CTkLabel(
            card_p,
            text="👤 1. Información Personal y de Contacto",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#38BDF8",
        ).pack(anchor="w", padx=15, pady=(12, 8))

        grid_p = ctk.CTkFrame(card_p, fg_color="transparent")
        grid_p.pack(fill="x", padx=15, pady=(0, 12))
        grid_p.columnconfigure(0, weight=1)
        grid_p.columnconfigure(1, weight=1)

        # Nombres
        ctk.CTkLabel(grid_p, text="Primer Nombre *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=0, column=0, sticky="w", padx=5, pady=(2, 0))
        ctk.CTkLabel(grid_p, text="Segundo Nombre", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=0, column=1, sticky="w", padx=5, pady=(2, 0))

        entry_nom1 = ctk.CTkEntry(grid_p)
        if pers:
            entry_nom1.insert(0, pers.primerNombre or "")
        entry_nom1.grid(row=1, column=0, sticky="ew", padx=5, pady=(2, 8))

        entry_nom2 = ctk.CTkEntry(grid_p)
        if pers:
            entry_nom2.insert(0, pers.segundoNombre or "")
        entry_nom2.grid(row=1, column=1, sticky="ew", padx=5, pady=(2, 8))

        # Apellidos
        ctk.CTkLabel(grid_p, text="Primer Apellido *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=2, column=0, sticky="w", padx=5, pady=(2, 0))
        ctk.CTkLabel(grid_p, text="Segundo Apellido", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=2, column=1, sticky="w", padx=5, pady=(2, 0))

        entry_ape1 = ctk.CTkEntry(grid_p)
        if pers:
            entry_ape1.insert(0, pers.primerApellido or "")
        entry_ape1.grid(row=3, column=0, sticky="ew", padx=5, pady=(2, 8))

        entry_ape2 = ctk.CTkEntry(grid_p)
        if pers:
            entry_ape2.insert(0, pers.segundoApellido or "")
        entry_ape2.grid(row=3, column=1, sticky="ew", padx=5, pady=(2, 8))

        # Teléfono y Fecha Nacimiento
        ctk.CTkLabel(grid_p, text="Teléfono / Celular", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=4, column=0, sticky="w", padx=5, pady=(2, 0))
        ctk.CTkLabel(grid_p, text="Fecha Nacimiento (AAAA-MM-DD)", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=4, column=1, sticky="w", padx=5, pady=(2, 0))

        entry_tel = ctk.CTkEntry(grid_p)
        if pers:
            entry_tel.insert(0, pers.telefono or "")
        entry_tel.grid(row=5, column=0, sticky="ew", padx=5, pady=(2, 8))

        entry_fnac = ctk.CTkEntry(grid_p)
        if pers and pers.fechaNacimiento:
            entry_fnac.insert(0, str(pers.fechaNacimiento))
        entry_fnac.grid(row=5, column=1, sticky="ew", padx=5, pady=(2, 8))

        # Correos
        ctk.CTkLabel(grid_p, text="Correo Institucional", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=6, column=0, sticky="w", padx=5, pady=(2, 0))
        ctk.CTkLabel(grid_p, text="Correo Personal", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=6, column=1, sticky="w", padx=5, pady=(2, 0))

        entry_cinst = ctk.CTkEntry(grid_p)
        if pers:
            entry_cinst.insert(0, pers.correoInstitucional or "")
        entry_cinst.grid(row=7, column=0, sticky="ew", padx=5, pady=(2, 8))

        entry_cpers = ctk.CTkEntry(grid_p)
        if pers:
            entry_cpers.insert(0, pers.correoPersonal or "")
        entry_cpers.grid(row=7, column=1, sticky="ew", padx=5, pady=(2, 8))

        # Dirección y Ciudad
        ctk.CTkLabel(grid_p, text="Dirección", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=8, column=0, sticky="w", padx=5, pady=(2, 0))
        ctk.CTkLabel(grid_p, text="Ciudad de Residencia", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=8, column=1, sticky="w", padx=5, pady=(2, 0))

        entry_dir = ctk.CTkEntry(grid_p)
        if pers:
            entry_dir.insert(0, pers.direccion or "")
        entry_dir.grid(row=9, column=0, sticky="ew", padx=5, pady=(2, 4))

        entry_ciu = ctk.CTkEntry(grid_p)
        if pers:
            entry_ciu.insert(0, pers.ciudadResidencia or "")
        entry_ciu.grid(row=9, column=1, sticky="ew", padx=5, pady=(2, 4))

        # -------------------------------------------------------------
        # TARJETA 2: PARÁMETROS DOCENTES Y SALARIALES
        # -------------------------------------------------------------
        card_d = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
        card_d.pack(fill="x", pady=6)

        ctk.CTkLabel(
            card_d,
            text="👨‍🏫 2. Parámetros Docentes y Salariales",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#C084FC",
        ).pack(anchor="w", padx=15, pady=(12, 8))

        grid_d = ctk.CTkFrame(card_d, fg_color="transparent")
        grid_d.pack(fill="x", padx=15, pady=(0, 12))
        grid_d.columnconfigure(0, weight=1)
        grid_d.columnconfigure(1, weight=1)

        prog_vals = [f"{p.idPrograma} - {p.nombre}" for p in self.controller.programas] if self.controller.programas else ["1 - Programa General"]

        # Programa Principal y Tipo Profesor
        ctk.CTkLabel(grid_d, text="Programa Principal *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=0, column=0, sticky="w", padx=5, pady=(2, 0))
        ctk.CTkLabel(grid_d, text="Tipo de Profesor / Vinculación *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=0, column=1, sticky="w", padx=5, pady=(2, 0))

        combo_prog = ctk.CTkComboBox(grid_d, values=prog_vals)
        sel_prog = next((pv for pv in prog_vals if pv.startswith(f"{prof.idProgramaPrincipal} - ")), prog_vals[0])
        combo_prog.set(sel_prog)
        combo_prog.grid(row=1, column=0, sticky="ew", padx=5, pady=(2, 8))

        combo_tipo = ctk.CTkComboBox(grid_d, values=["PLANTA", "OCASIONAL_TC", "OCASIONAL_MT", "CATEDRA"])
        combo_tipo.set(str(getattr(prof, "tipoProfesor", "PLANTA")))
        combo_tipo.grid(row=1, column=1, sticky="ew", padx=5, pady=(2, 8))

        # Categoría y Dedicación
        ctk.CTkLabel(grid_d, text="Categoría Docente *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=2, column=0, sticky="w", padx=5, pady=(2, 0))
        ctk.CTkLabel(grid_d, text="Dedicación *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=2, column=1, sticky="w", padx=5, pady=(2, 0))

        combo_cat = ctk.CTkComboBox(grid_d, values=["AUXILIAR", "ASISTENTE", "ASOCIADO", "TITULAR", "NO_CATEGORIZADO"])
        combo_cat.set(str(getattr(prof, "categoriaDocente", "TITULAR")))
        combo_cat.grid(row=3, column=0, sticky="ew", padx=5, pady=(2, 8))

        combo_ded = ctk.CTkComboBox(grid_d, values=["TIEMPO_COMPLETO", "MEDIO_TIEMPO", "CATEDRA"])
        combo_ded.set(str(getattr(prof, "dedicacion", "TIEMPO_COMPLETO")))
        combo_ded.grid(row=3, column=1, sticky="ew", padx=5, pady=(2, 8))

        # Horas Semanales y Puntos Salariales
        ctk.CTkLabel(grid_d, text="Horas Semanales", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=4, column=0, sticky="w", padx=5, pady=(2, 0))
        ctk.CTkLabel(grid_d, text="Puntos Salariales (Dec. 1279)", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=4, column=1, sticky="w", padx=5, pady=(2, 0))

        entry_horas = ctk.CTkEntry(grid_d)
        entry_horas.insert(0, str(getattr(prof, "numeroHorasSemanales", "40")))
        entry_horas.grid(row=5, column=0, sticky="ew", padx=5, pady=(2, 8))

        entry_puntos = ctk.CTkEntry(grid_d)
        entry_puntos.insert(0, str(getattr(prof, "puntosSalariales", "350") or "0"))
        entry_puntos.grid(row=5, column=1, sticky="ew", padx=5, pady=(2, 8))

        # Máximo Nivel de Estudio y Título
        ctk.CTkLabel(grid_d, text="Máximo Nivel de Estudio", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=6, column=0, sticky="w", padx=5, pady=(2, 0))
        ctk.CTkLabel(grid_d, text="Título Profesional", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=6, column=1, sticky="w", padx=5, pady=(2, 0))

        combo_nivel = ctk.CTkComboBox(grid_d, values=["PREGRADO", "ESPECIALIZACION", "MAESTRIA", "DOCTORADO"])
        combo_nivel.set(str(getattr(prof, "maximoNivelEstudio", "MAESTRIA") or "MAESTRIA"))
        combo_nivel.grid(row=7, column=0, sticky="ew", padx=5, pady=(2, 8))

        entry_tit = ctk.CTkEntry(grid_d)
        entry_tit.insert(0, str(getattr(prof, "tituloProfesional", "") or ""))
        entry_tit.grid(row=7, column=1, sticky="ew", padx=5, pady=(2, 8))

        # Área de Conocimiento
        ctk.CTkLabel(grid_d, text="Área de Conocimiento", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=8, column=0, sticky="w", padx=5, pady=(2, 0))

        entry_area = ctk.CTkEntry(grid_d)
        entry_area.insert(0, str(getattr(prof, "areaConocimiento", "") or ""))
        entry_area.grid(row=9, column=0, columnspan=2, sticky="ew", padx=5, pady=(2, 4))

        # Mensaje de error
        lbl_error = ctk.CTkLabel(scroll, text="", text_color="#EF4444", font=ctk.CTkFont(size=12, weight="bold"))
        lbl_error.pack(pady=(4, 2))

        def _guardar():
            nom1 = entry_nom1.get().strip()
            ape1 = entry_ape1.get().strip()
            if not nom1 or not ape1:
                lbl_error.configure(text="⚠️ Primer nombre y primer apellido son obligatorios.")
                return

            if pers:
                pers.primerNombre = nom1
                pers.segundoNombre = entry_nom2.get().strip() or None
                pers.primerApellido = ape1
                pers.segundoApellido = entry_ape2.get().strip() or None
                pers.telefono = entry_tel.get().strip() or None
                pers.correoInstitucional = entry_cinst.get().strip() or pers.correoInstitucional
                pers.correoPersonal = entry_cpers.get().strip() or None
                pers.direccion = entry_dir.get().strip() or None
                pers.ciudadResidencia = entry_ciu.get().strip() or None

                fnac_str = entry_fnac.get().strip()
                if fnac_str:
                    try:
                        pers.fechaNacimiento = datetime.strptime(fnac_str, "%Y-%m-%d").date()
                    except ValueError:
                        lbl_error.configure(text="⚠️ Formato de Fecha de Nacimiento debe ser AAAA-MM-DD.")
                        return

            # Actualizar datos de Profesor
            prog_sel = combo_prog.get().split(" - ")[0]
            if prog_sel.isdigit():
                prof.idProgramaPrincipal = int(prog_sel)

            try:
                prof.tipoProfesor = TipoProfesor[combo_tipo.get()]
            except KeyError:
                pass

            prof.categoriaDocente = combo_cat.get()

            try:
                prof.dedicacion = Dedicacion[combo_ded.get()]
            except KeyError:
                pass

            horas_str = entry_horas.get().strip()
            if horas_str.replace(".", "", 1).isdigit():
                prof.numeroHorasSemanales = Decimal(horas_str)

            puntos_str = entry_puntos.get().strip()
            if puntos_str.replace(".", "", 1).isdigit():
                prof.puntosSalariales = Decimal(puntos_str)

            prof.maximoNivelEstudio = combo_nivel.get()
            prof.tituloProfesional = entry_tit.get().strip() or None
            prof.areaConocimiento = entry_area.get().strip() or None

            self.controller._recrear_gestores()
            self.actualizar_tablas()
            dialog.destroy()

        ctk.CTkButton(scroll, text="💾 Guardar Cambios", font=ctk.CTkFont(size=13, weight="bold"), fg_color="#10B981", hover_color="#059669", height=40, command=_guardar).pack(fill="x", padx=15, pady=(10, 20))

    def _editar_administrativo(self, adm: Administrativo, pers: Persona | None) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"✏️ Editar Administrativo {adm.codigoEmpleado}")
        dialog.geometry("620x680")
        dialog.minsize(560, 580)
        dialog.grab_set()

        # Header
        header_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(15, 10))

        ctk.CTkLabel(
            header_frame,
            text=f"✏️ Modificar Administrativo: {adm.codigoEmpleado}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#F8FAFC",
        ).pack(anchor="w")
        ctk.CTkLabel(
            header_frame,
            text="Actualice la información personal, de contacto y los parámetros laborales del empleado.",
            font=ctk.CTkFont(size=11),
            text_color="#94A3B8",
        ).pack(anchor="w", pady=(2, 0))

        scroll = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        # -------------------------------------------------------------
        # TARJETA 1: DATOS PERSONALES Y CONTACTO
        # -------------------------------------------------------------
        card_p = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
        card_p.pack(fill="x", pady=6)

        ctk.CTkLabel(
            card_p,
            text="👤 1. Información Personal y de Contacto",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#38BDF8",
        ).pack(anchor="w", padx=15, pady=(12, 8))

        grid_p = ctk.CTkFrame(card_p, fg_color="transparent")
        grid_p.pack(fill="x", padx=15, pady=(0, 12))
        grid_p.columnconfigure(0, weight=1)
        grid_p.columnconfigure(1, weight=1)

        # Nombres
        ctk.CTkLabel(grid_p, text="Primer Nombre *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=0, column=0, sticky="w", padx=5, pady=(2, 0))
        ctk.CTkLabel(grid_p, text="Segundo Nombre", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=0, column=1, sticky="w", padx=5, pady=(2, 0))

        entry_nom1 = ctk.CTkEntry(grid_p)
        if pers:
            entry_nom1.insert(0, pers.primerNombre or "")
        entry_nom1.grid(row=1, column=0, sticky="ew", padx=5, pady=(2, 8))

        entry_nom2 = ctk.CTkEntry(grid_p)
        if pers:
            entry_nom2.insert(0, pers.segundoNombre or "")
        entry_nom2.grid(row=1, column=1, sticky="ew", padx=5, pady=(2, 8))

        # Apellidos
        ctk.CTkLabel(grid_p, text="Primer Apellido *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=2, column=0, sticky="w", padx=5, pady=(2, 0))
        ctk.CTkLabel(grid_p, text="Segundo Apellido", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=2, column=1, sticky="w", padx=5, pady=(2, 0))

        entry_ape1 = ctk.CTkEntry(grid_p)
        if pers:
            entry_ape1.insert(0, pers.primerApellido or "")
        entry_ape1.grid(row=3, column=0, sticky="ew", padx=5, pady=(2, 8))

        entry_ape2 = ctk.CTkEntry(grid_p)
        if pers:
            entry_ape2.insert(0, pers.segundoApellido or "")
        entry_ape2.grid(row=3, column=1, sticky="ew", padx=5, pady=(2, 8))

        # Teléfono y Fecha Nacimiento
        ctk.CTkLabel(grid_p, text="Teléfono / Celular", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=4, column=0, sticky="w", padx=5, pady=(2, 0))
        ctk.CTkLabel(grid_p, text="Fecha Nacimiento (AAAA-MM-DD)", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=4, column=1, sticky="w", padx=5, pady=(2, 0))

        entry_tel = ctk.CTkEntry(grid_p)
        if pers:
            entry_tel.insert(0, pers.telefono or "")
        entry_tel.grid(row=5, column=0, sticky="ew", padx=5, pady=(2, 8))

        entry_fnac = ctk.CTkEntry(grid_p)
        if pers and pers.fechaNacimiento:
            entry_fnac.insert(0, str(pers.fechaNacimiento))
        entry_fnac.grid(row=5, column=1, sticky="ew", padx=5, pady=(2, 8))

        # Correos
        ctk.CTkLabel(grid_p, text="Correo Institucional", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=6, column=0, sticky="w", padx=5, pady=(2, 0))
        ctk.CTkLabel(grid_p, text="Correo Personal", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=6, column=1, sticky="w", padx=5, pady=(2, 0))

        entry_cinst = ctk.CTkEntry(grid_p)
        if pers:
            entry_cinst.insert(0, pers.correoInstitucional or "")
        entry_cinst.grid(row=7, column=0, sticky="ew", padx=5, pady=(2, 8))

        entry_cpers = ctk.CTkEntry(grid_p)
        if pers:
            entry_cpers.insert(0, pers.correoPersonal or "")
        entry_cpers.grid(row=7, column=1, sticky="ew", padx=5, pady=(2, 8))

        # Dirección y Ciudad
        ctk.CTkLabel(grid_p, text="Dirección", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=8, column=0, sticky="w", padx=5, pady=(2, 0))
        ctk.CTkLabel(grid_p, text="Ciudad de Residencia", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=8, column=1, sticky="w", padx=5, pady=(2, 0))

        entry_dir = ctk.CTkEntry(grid_p)
        if pers:
            entry_dir.insert(0, pers.direccion or "")
        entry_dir.grid(row=9, column=0, sticky="ew", padx=5, pady=(2, 4))

        entry_ciu = ctk.CTkEntry(grid_p)
        if pers:
            entry_ciu.insert(0, pers.ciudadResidencia or "")
        entry_ciu.grid(row=9, column=1, sticky="ew", padx=5, pady=(2, 4))

        # -------------------------------------------------------------
        # TARJETA 2: DATOS LABORALES
        # -------------------------------------------------------------
        card_l = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
        card_l.pack(fill="x", pady=6)

        ctk.CTkLabel(
            card_l,
            text="👔 2. Información Laboral y Contractual",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#F59E0B",
        ).pack(anchor="w", padx=15, pady=(12, 8))

        grid_l = ctk.CTkFrame(card_l, fg_color="transparent")
        grid_l.pack(fill="x", padx=15, pady=(0, 12))
        grid_l.columnconfigure(0, weight=1)
        grid_l.columnconfigure(1, weight=1)

        # Cargo y Dependencia
        ctk.CTkLabel(grid_l, text="Cargo Institucional *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=0, column=0, sticky="w", padx=5, pady=(2, 0))
        ctk.CTkLabel(grid_l, text="Dependencia *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=0, column=1, sticky="w", padx=5, pady=(2, 0))

        entry_cargo = ctk.CTkEntry(grid_l)
        entry_cargo.insert(0, getattr(adm, "cargo", "") or "")
        entry_cargo.grid(row=1, column=0, sticky="ew", padx=5, pady=(2, 8))

        entry_dep = ctk.CTkEntry(grid_l)
        entry_dep.insert(0, getattr(adm, "dependencia", "") or "")
        entry_dep.grid(row=1, column=1, sticky="ew", padx=5, pady=(2, 8))

        # Tipo Contratación y Salario Base
        ctk.CTkLabel(grid_l, text="Tipo de Contratación", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=2, column=0, sticky="w", padx=5, pady=(2, 0))
        ctk.CTkLabel(grid_l, text="Salario Base Mensual ($) *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=2, column=1, sticky="w", padx=5, pady=(2, 0))

        combo_tcont = ctk.CTkComboBox(grid_l, values=["PLANTA", "PROVISIONALIDAD", "PRESTACION_SERVICIOS"])
        combo_tcont.set(str(getattr(adm, "tipoContratacion", "PLANTA") or "PLANTA"))
        combo_tcont.grid(row=3, column=0, sticky="ew", padx=5, pady=(2, 8))

        entry_sal = ctk.CTkEntry(grid_l)
        entry_sal.insert(0, str(getattr(adm, "salarioBase", "0") or "0"))
        entry_sal.grid(row=3, column=1, sticky="ew", padx=5, pady=(2, 8))

        # Mensaje de error
        lbl_error = ctk.CTkLabel(scroll, text="", text_color="#EF4444", font=ctk.CTkFont(size=12, weight="bold"))
        lbl_error.pack(pady=(4, 2))

        def _guardar():
            nom1 = entry_nom1.get().strip()
            ape1 = entry_ape1.get().strip()
            if not nom1 or not ape1:
                lbl_error.configure(text="⚠️ Primer nombre y primer apellido son obligatorios.")
                return

            if pers:
                pers.primerNombre = nom1
                pers.segundoNombre = entry_nom2.get().strip() or None
                pers.primerApellido = ape1
                pers.segundoApellido = entry_ape2.get().strip() or None
                pers.telefono = entry_tel.get().strip() or None
                pers.correoInstitucional = entry_cinst.get().strip() or pers.correoInstitucional
                pers.correoPersonal = entry_cpers.get().strip() or None
                pers.direccion = entry_dir.get().strip() or None
                pers.ciudadResidencia = entry_ciu.get().strip() or None

                fnac_str = entry_fnac.get().strip()
                if fnac_str:
                    try:
                        pers.fechaNacimiento = datetime.strptime(fnac_str, "%Y-%m-%d").date()
                    except ValueError:
                        lbl_error.configure(text="⚠️ Formato de Fecha de Nacimiento debe ser AAAA-MM-DD.")
                        return

            # Actualizar datos de Administrativo
            adm.cargo = entry_cargo.get().strip() or adm.cargo
            adm.dependencia = entry_dep.get().strip() or adm.dependencia
            adm.tipoContratacion = combo_tcont.get()

            sal_str = entry_sal.get().strip()
            if sal_str.replace(".", "", 1).isdigit():
                adm.salarioBase = Decimal(sal_str)

            self.controller._recrear_gestores()
            self.actualizar_tablas()
            dialog.destroy()

        ctk.CTkButton(scroll, text="💾 Guardar Cambios", font=ctk.CTkFont(size=13, weight="bold"), fg_color="#10B981", hover_color="#059669", height=40, command=_guardar).pack(fill="x", padx=15, pady=(10, 20))

    def _desactivar_administrativo(self, id_administrativo: int) -> None:
        adm = next((a for a in self.controller.administrativos if getattr(a, "idAdministrativo", 0) == id_administrativo), None)
        if adm:
            adm.estado = "INACTIVO"
            self.controller._recrear_gestores()
            self.actualizar_tablas()

    def actualizar(self) -> None:
        self.actualizar_tablas()
