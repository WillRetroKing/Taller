"""Vista de Gestión de Personas (Estudiantes, Profesores, Administrativos) para la GUI con tablas y badges estilizados."""

from __future__ import annotations

from datetime import date
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
        col_weights = [2, 2, 4, 2, 2, 3, 2]
        col_mins = [90, 100, 180, 90, 80, 110, 100]

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
                    ("👁️", lambda p=pers: self._ver_detalle_persona(p), "#6366F1", "#4F46E5", 30, 28),
                    ("✏️", lambda e=est, p=pers: self._editar_estudiante(e, p), "#334155", "#475569", 30, 28),
                    ("❌", lambda e_id=getattr(est, "idEstudiante", 0): self._desactivar_estudiante(e_id), "#EF4444", "#DC2626", 30, 28),
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
        col_weights = [2, 2, 4, 3, 2, 2, 3]
        col_mins = [90, 100, 180, 110, 100, 90, 120]

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
                    ("👁️", lambda p=pers: self._ver_detalle_persona(p), "#6366F1", "#4F46E5", 30, 28),
                    ("✏️", lambda pr=prof, p=pers: self._editar_profesor(pr, p), "#334155", "#475569", 30, 28),
                    ("❌", lambda p_id=getattr(prof, "idProfesor", 0): self._desactivar_profesor(p_id), "#EF4444", "#DC2626", 30, 28),
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
        col_weights = [2, 2, 4, 3, 3, 3, 3]
        col_mins = [90, 100, 180, 120, 120, 120, 120]

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
                    ("👁️", lambda p=pers: self._ver_detalle_persona(p), "#6366F1", "#4F46E5", 30, 28),
                    ("✏️", lambda a=adm, p=pers: self._editar_administrativo(a, p), "#334155", "#475569", 30, 28),
                    ("❌", lambda a_id=getattr(adm, "idAdministrativo", 0): self._desactivar_administrativo(a_id), "#EF4444", "#DC2626", 30, 28),
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
        dialog.title("➕ Registrar Persona y Asignar Rol")
        dialog.geometry("500x650")
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Datos Básicos de la Persona", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        entry_doc = ctk.CTkEntry(dialog, placeholder_text="Número de Documento (Cédula)")
        entry_doc.pack(fill="x", padx=20, pady=5)

        entry_nom1 = ctk.CTkEntry(dialog, placeholder_text="Primer Nombre")
        entry_nom1.pack(fill="x", padx=20, pady=5)

        entry_ape1 = ctk.CTkEntry(dialog, placeholder_text="Primer Apellido")
        entry_ape1.pack(fill="x", padx=20, pady=5)

        entry_correo = ctk.CTkEntry(dialog, placeholder_text="Correo Institucional (@unicesar.edu.co)")
        entry_correo.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(dialog, text="Rol a Asignar en PITA", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(15, 5))
        combo_rol = ctk.CTkComboBox(dialog, values=["ESTUDIANTE", "PROFESOR", "ADMINISTRATIVO"])
        combo_rol.pack(fill="x", padx=20, pady=5)

        entry_codigo = ctk.CTkEntry(dialog, placeholder_text="Código (ej: EST-2026-99 / PROF-99)")
        entry_codigo.pack(fill="x", padx=20, pady=5)

        def _guardar():
            doc = entry_doc.get().strip()
            nom = entry_nom1.get().strip()
            ape = entry_ape1.get().strip()
            correo = entry_correo.get().strip()
            rol = combo_rol.get()
            cod = entry_codigo.get().strip()

            if not doc or not nom or not ape or not cod:
                return

            new_id_p = len(self.controller.personas) + 1
            nueva_p = Persona(
                idPersona=new_id_p,
                tipoDocumento="CC",
                numeroDocumento=doc,
                primerNombre=nom,
                primerApellido=ape,
                correoInstitucional=correo or f"{nom.lower()}@unicesar.edu.co",
                fechaRegistro=date.today(),
                estado="ACTIVO",
            )
            self.controller.personas.append(nueva_p)

            if rol == "ESTUDIANTE":
                new_e = Estudiante(
                    idEstudiante=len(self.controller.estudiantes) + 1,
                    idPersona=new_id_p,
                    codigoEstudiante=cod,
                    idPrograma=1,
                    idPlanEstudio=1,
                    fechaIngreso=date.today(),
                    semestreActual=1,
                    creditosAprobados=0,
                    promedioAcumulado="5.0",
                    estadoAcademico=EstadoAcademico.ACTIVO,
                    estado="ACTIVO",
                )
                self.controller.estudiantes.append(new_e)
            elif rol == "PROFESOR":
                new_prof = Profesor(
                    idProfesor=len(self.controller.profesores) + 1,
                    idPersona=new_id_p,
                    codigoProfesor=cod,
                    idProgramaPrincipal=1,
                    fechaVinculacion=date.today(),
                    tipoProfesor=TipoProfesor.PLANTA,
                    categoriaDocente="ASISTENTE",
                    dedicacion=Dedicacion.TIEMPO_COMPLETO,
                    numeroHorasSemanales=40,
                    puntosSalariales="350",
                    estado="ACTIVO",
                )
                self.controller.profesores.append(new_prof)
            elif rol == "ADMINISTRATIVO":
                new_adm = Administrativo(
                    idAdministrativo=len(self.controller.administrativos) + 1,
                    idPersona=new_id_p,
                    codigoEmpleado=cod,
                    cargo="Analista",
                    dependencia="Académica",
                    salarioBase="2500000",
                    estado="ACTIVO",
                )
                self.controller.administrativos.append(new_adm)

            self.controller._recrear_gestores()
            dialog.destroy()
            self.actualizar()

        ctk.CTkButton(
            dialog, text="💾 Registrar Persona", fg_color="#059669", hover_color="#047857", command=_guardar
        ).pack(pady=20)

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
        dialog.geometry("450x420")
        dialog.grab_set()

        ctk.CTkLabel(dialog, text=f"👤 {persona.primerNombre} {persona.primerApellido}", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=12)

        info_frame = ctk.CTkFrame(dialog, fg_color=Colors.BG_CARD_HOVER, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
        info_frame.pack(fill="both", expand=True, padx=20, pady=10)

        detalles = [
            ("📄 Documento Identidad:", f"{persona.tipoDocumento} {persona.numeroDocumento}"),
            ("📧 Correo Institucional:", persona.correoInstitucional or "N/A"),
            ("📧 Correo Personal:", persona.correoPersonal or "N/A"),
            ("📱 Teléfono Contacto:", persona.telefono or "N/A"),
            ("🏠 Dirección / Ciudad:", f"{persona.direccion or ''} ({persona.ciudadResidencia or ''})"),
            ("📅 Fecha Registro:", str(persona.fechaRegistro)),
            ("🟢 Estado Sistema:", persona.estado),
        ]

        for lbl, val in detalles:
            r = ctk.CTkFrame(info_frame, fg_color="transparent")
            r.pack(fill="x", padx=15, pady=4)
            ctk.CTkLabel(r, text=lbl, font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(side="left")
            ctk.CTkLabel(r, text=val, font=ctk.CTkFont(size=11), text_color="#F8FAFC").pack(side="right")

    def _editar_estudiante(self, est: Estudiante, pers: Persona | None) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"✏️ Editar Estudiante {est.codigoEstudiante}")
        dialog.geometry("460x520")
        dialog.grab_set()

        ctk.CTkLabel(dialog, text=f"Modificar Datos Estudiante: {est.codigoEstudiante}", font=ctk.CTkFont(size=15, weight="bold")).pack(pady=12)

        entry_nom = ctk.CTkEntry(dialog)
        if pers:
            entry_nom.insert(0, pers.primerNombre)
        entry_nom.pack(fill="x", padx=20, pady=5)

        entry_ape = ctk.CTkEntry(dialog)
        if pers:
            entry_ape.insert(0, pers.primerApellido)
        entry_ape.pack(fill="x", padx=20, pady=5)

        entry_sem = ctk.CTkEntry(dialog)
        entry_sem.insert(0, str(getattr(est, "semestreActual", "1")))
        entry_sem.pack(fill="x", padx=20, pady=5)

        entry_prom = ctk.CTkEntry(dialog)
        entry_prom.insert(0, str(getattr(est, "promedioAcumulado", "0.0")))
        entry_prom.pack(fill="x", padx=20, pady=5)

        def _guardar():
            if pers:
                pers.primerNombre = entry_nom.get().strip() or pers.primerNombre
                pers.primerApellido = entry_ape.get().strip() or pers.primerApellido
            if entry_sem.get().strip().isdigit():
                est.semestreActual = int(entry_sem.get().strip())
            try:
                val_p = float(entry_prom.get().strip())
                est.promedioAcumulado = val_p
                if val_p < 3.0:
                    est.estadoAcademico = EstadoAcademico.EBRA
                else:
                    est.estadoAcademico = EstadoAcademico.ACTIVO
            except ValueError:
                pass
            self.controller._recrear_gestores()
            self.actualizar_tablas()
            dialog.destroy()

        ctk.CTkButton(dialog, text="💾 Guardar Cambios", font=ctk.CTkFont(size=12, weight="bold"), fg_color="#10B981", hover_color="#059669", height=36, command=_guardar).pack(pady=20)

    def _editar_profesor(self, prof: Profesor, pers: Persona | None) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"✏️ Editar Profesor {prof.codigoProfesor}")
        dialog.geometry("460x520")
        dialog.grab_set()

        ctk.CTkLabel(dialog, text=f"Modificar Datos Profesor: {prof.codigoProfesor}", font=ctk.CTkFont(size=15, weight="bold")).pack(pady=12)

        entry_nom = ctk.CTkEntry(dialog)
        if pers:
            entry_nom.insert(0, pers.primerNombre)
        entry_nom.pack(fill="x", padx=20, pady=5)

        entry_ape = ctk.CTkEntry(dialog)
        if pers:
            entry_ape.insert(0, pers.primerApellido)
        entry_ape.pack(fill="x", padx=20, pady=5)

        combo_cat = ctk.CTkComboBox(dialog, values=["TITULAR", "ASOCIADO", "ASISTENTE", "INSTRUCTOR"])
        combo_cat.set(str(getattr(prof, "categoriaDocente", "TITULAR")))
        combo_cat.pack(fill="x", padx=20, pady=5)

        entry_horas = ctk.CTkEntry(dialog)
        entry_horas.insert(0, str(getattr(prof, "numeroHorasSemanales", "40")))
        entry_horas.pack(fill="x", padx=20, pady=5)

        def _guardar():
            if pers:
                pers.primerNombre = entry_nom.get().strip() or pers.primerNombre
                pers.primerApellido = entry_ape.get().strip() or pers.primerApellido
            prof.categoriaDocente = combo_cat.get()
            if entry_horas.get().strip().isdigit():
                prof.numeroHorasSemanales = int(entry_horas.get().strip())
            self.controller._recrear_gestores()
            self.actualizar_tablas()
            dialog.destroy()

        ctk.CTkButton(dialog, text="💾 Guardar Cambios", font=ctk.CTkFont(size=12, weight="bold"), fg_color="#10B981", hover_color="#059669", height=36, command=_guardar).pack(pady=20)

    def _editar_administrativo(self, adm: Administrativo, pers: Persona | None) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"✏️ Editar Administrativo {adm.codigoEmpleado}")
        dialog.geometry("460x520")
        dialog.grab_set()

        ctk.CTkLabel(dialog, text=f"Modificar Datos Empleado: {adm.codigoEmpleado}", font=ctk.CTkFont(size=15, weight="bold")).pack(pady=12)

        entry_nom = ctk.CTkEntry(dialog)
        if pers:
            entry_nom.insert(0, pers.primerNombre)
        entry_nom.pack(fill="x", padx=20, pady=5)

        entry_cargo = ctk.CTkEntry(dialog)
        entry_cargo.insert(0, getattr(adm, "cargo", ""))
        entry_cargo.pack(fill="x", padx=20, pady=5)

        entry_sal = ctk.CTkEntry(dialog)
        entry_sal.insert(0, str(getattr(adm, "salarioBase", "0")))
        entry_sal.pack(fill="x", padx=20, pady=5)

        def _guardar():
            if pers:
                pers.primerNombre = entry_nom.get().strip() or pers.primerNombre
            adm.cargo = entry_cargo.get().strip() or adm.cargo
            adm.salarioBase = entry_sal.get().strip() or adm.salarioBase
            self.controller._recrear_gestores()
            self.actualizar_tablas()
            dialog.destroy()

        ctk.CTkButton(dialog, text="💾 Guardar Cambios", font=ctk.CTkFont(size=12, weight="bold"), fg_color="#10B981", hover_color="#059669", height=36, command=_guardar).pack(pady=20)

    def _desactivar_administrativo(self, id_administrativo: int) -> None:
        adm = next((a for a in self.controller.administrativos if getattr(a, "idAdministrativo", 0) == id_administrativo), None)
        if adm:
            adm.estado = "INACTIVO"
            self.controller._recrear_gestores()
            self.actualizar_tablas()

    def actualizar(self) -> None:
        self.actualizar_tablas()
