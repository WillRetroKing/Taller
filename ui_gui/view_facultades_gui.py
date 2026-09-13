"""Vista de Gestión de Facultades y Programas Académicos (Taller 1 Requisitos 24 y 25)."""

from __future__ import annotations

from datetime import date
import customtkinter as ctk
from typing import TYPE_CHECKING, Callable

from ui_gui.theme import Colors, Fonts, create_styled_tabview
from ui_gui.components import PITAGridTable, create_badge
from dominio.modelo_datos import Facultad, ProgramaAcademico

if TYPE_CHECKING:
    from ui_gui.gui_controller import PITAController


class FacultadesViewGUI(ctk.CTkFrame):
    """Vista para administrar Facultades y Programas Académicos con CRUD completo."""

    def __init__(self, parent: ctk.CTk, controller: PITAController) -> None:
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        self._crear_interfaz()

    def _crear_interfaz(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 10))

        ctk.CTkLabel(
            header,
            text="🏛️ Gestión de Facultades & Programas Académicos",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=Colors.TEXT_MAIN,
        ).pack(side="left")

        h_btns = ctk.CTkFrame(header, fg_color="transparent")
        h_btns.pack(side="right")

        btn_fac = ctk.CTkButton(
            h_btns,
            text="➕ Nueva Facultad",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#0067C0",
            hover_color="#005FB8",
            height=36,
            corner_radius=8,
            command=self._abrir_modal_nueva_facultad,
        )
        btn_fac.pack(side="left", padx=5)

        btn_prog = ctk.CTkButton(
            h_btns,
            text="➕ Nuevo Programa",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            height=36,
            corner_radius=8,
            command=self._abrir_modal_nuevo_programa,
        )
        btn_prog.pack(side="left", padx=5)

        # Tabs
        self.tabview = create_styled_tabview(self)
        self.tabview.pack(fill="both", expand=True, padx=15, pady=5)

        self.tab_facultades = self.tabview.add("🏛️ Facultades Instucional")
        self.tab_programas = self.tabview.add("🎓 Programas Académicos")

        self.actualizar_tablas()

    def actualizar(self) -> None:
        self.actualizar_tablas()

    def actualizar_tablas(self) -> None:
        self._llenar_tab_facultades()
        self._llenar_tab_programas()

    # ------------------------------------------------------------------
    # TAB FACULTADES
    # ------------------------------------------------------------------
    def _llenar_tab_facultades(self) -> None:
        for w in self.tab_facultades.winfo_children():
            w.destroy()

        headers = ["Código", "Nombre de Facultad", "Decano / Responsable", "Ubicación", "Teléfono", "Correo", "Estado", "Acciones"]
        col_weights = [2, 4, 3, 3, 2, 3, 2, 3]
        col_mins = [90, 170, 150, 110, 90, 140, 90, 150]

        table = PITAGridTable(self.tab_facultades, headers=headers, col_weights=col_weights, col_mins=col_mins)
        table.pack(fill="both", expand=True, padx=5, pady=5)

        if not self.controller.facultades:
            ctk.CTkLabel(table, text="No hay facultades registradas.", text_color="#94A3B8").pack(pady=30)
            return

        def _get_nombre_decano(id_decano: int | None) -> str:
            if not id_decano:
                return "Sin Asignar"
            prof = next((p for p in self.controller.profesores if getattr(p, "idProfesor", None) == id_decano), None)
            if not prof:
                return f"Docente #{id_decano}"
            pers = next((per for per in self.controller.personas if getattr(per, "idPersona", None) == getattr(prof, "idPersona", None)), None)
            if pers:
                nom = f"{getattr(pers, 'primerNombre', '')} {getattr(pers, 'primerApellido', '')}".strip()
                cod = getattr(prof, "codigoProfesor", "")
                return f"{nom} ({cod})" if cod else nom
            return getattr(prof, "codigoProfesor", f"Docente #{id_decano}")

        for fac in self.controller.facultades:
            act_spec = (
                "actions",
                [
                    ("✏️ Editar", lambda f=fac: self._abrir_modal_editar_facultad(f), "#334155", "#475569", 70, 28, 10),
                    ("❌ Eliminar", lambda f_id=fac.idFacultad: self._eliminar_facultad(f_id), "#EF4444", "#DC2626", 74, 28, 10),
                ],
            )

            nom_dec = _get_nombre_decano(getattr(fac, "idDecano", None))

            correo_fac = getattr(fac, "correo", None) or getattr(fac, "correoInstitucional", None) or getattr(fac, "email", "N/A")

            cells = [
                (getattr(fac, "codigoFacultad", "N/A"), "#F59E0B"),
                (getattr(fac, "nombre", "N/A"), "#F8FAFC"),
                (nom_dec, "#38BDF8" if nom_dec != "Sin Asignar" else "#94A3B8"),
                getattr(fac, "ubicacion", "N/A"),
                getattr(fac, "telefono", "N/A"),
                (str(correo_fac), "#38BDF8" if "@" in str(correo_fac) else "#94A3B8"),
                ("badge", getattr(fac, "estado", "ACTIVO"), "active"),
                act_spec,
            ]
            table.add_row_items(cells)

    # ------------------------------------------------------------------
    # TAB PROGRAMAS
    # ------------------------------------------------------------------
    def _llenar_tab_programas(self) -> None:
        for w in self.tab_programas.winfo_children():
            w.destroy()

        headers = ["Código", "Programa Académico", "Nivel", "Modalidad", "Semestres", "Créditos", "Facultad", "Estado", "Acciones"]
        col_weights = [2, 4, 2, 2, 2, 2, 3, 2, 3]
        col_mins = [90, 170, 85, 95, 75, 75, 130, 80, 150]

        table = PITAGridTable(self.tab_programas, headers=headers, col_weights=col_weights, col_mins=col_mins)
        table.pack(fill="both", expand=True, padx=5, pady=5)

        if not self.controller.programas:
            ctk.CTkLabel(table, text="No hay programas académicos registrados.", text_color="#94A3B8").pack(pady=30)
            return

        for prog in self.controller.programas:
            fac = next((f for f in self.controller.facultades if f.idFacultad == prog.idFacultad), None)
            nom_fac = fac.nombre if fac else "N/A"

            act_spec = (
                "actions",
                [
                    ("✏️ Editar", lambda p=prog: self._abrir_modal_editar_programa(p), "#334155", "#475569", 70, 28, 10),
                    ("❌ Eliminar", lambda p_id=prog.idPrograma: self._eliminar_programa(p_id), "#EF4444", "#DC2626", 74, 28, 10),
                ],
            )

            est_estado = getattr(prog, "estado", "ACTIVO") or "ACTIVO"
            badge_type = "active" if est_estado.upper() == "ACTIVO" else "danger"

            cells = [
                (getattr(prog, "codigoPrograma", "N/A"), "#38BDF8"),
                (getattr(prog, "nombre", "N/A"), "#F8FAFC"),
                getattr(prog, "nivelFormacion", "PREGRADO"),
                getattr(prog, "modalidad", "PRESENCIAL"),
                f"{getattr(prog, 'numeroSemestres', 10)} Sem",
                f"{getattr(prog, 'totalCreditos', 160)} Cred",
                nom_fac,
                ("badge", est_estado, badge_type),
                act_spec,
            ]
            table.add_row_items(cells)

    # ------------------------------------------------------------------
    # MODALES CRUD FACULTAD
    # ------------------------------------------------------------------
    def _abrir_modal_nueva_facultad(self) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title("➕ Registrar Nueva Facultad")
        dialog.geometry("460x570")
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Crear Unidad Académica / Facultad", font=ctk.CTkFont(size=15, weight="bold")).pack(pady=12)

        entry_cod = ctk.CTkEntry(dialog, placeholder_text="Código Facultad (ej: FAC-ING)")
        entry_cod.pack(fill="x", padx=20, pady=6)

        entry_nom = ctk.CTkEntry(dialog, placeholder_text="Nombre de la Facultad")
        entry_nom.pack(fill="x", padx=20, pady=6)

        entry_ubi = ctk.CTkEntry(dialog, placeholder_text="Ubicación / Sede")
        entry_ubi.pack(fill="x", padx=20, pady=6)

        entry_tel = ctk.CTkEntry(dialog, placeholder_text="Teléfono de Contacto")
        entry_tel.pack(fill="x", padx=20, pady=6)

        entry_cor = ctk.CTkEntry(dialog, placeholder_text="Correo Institucional")
        entry_cor.pack(fill="x", padx=20, pady=6)

        # Opciones de Decano basadas en Profesores registrados
        profs_opciones = ["(Sin Decano Asignado)"]
        profs_map: dict[str, int | None] = {"(Sin Decano Asignado)": None}
        for p in self.controller.profesores:
            pers = next((per for per in self.controller.personas if getattr(per, "idPersona", None) == getattr(p, "idPersona", None)), None)
            nom = f"{getattr(pers, 'primerNombre', '')} {getattr(pers, 'primerApellido', '')}".strip() or f"Docente #{p.idProfesor}"
            cod = getattr(p, "codigoProfesor", "")
            lbl = f"{nom} ({cod})" if cod else nom
            profs_opciones.append(lbl)
            profs_map[lbl] = p.idProfesor

        lbl_dec = ctk.CTkLabel(dialog, text="Decano / Autoridad Académica:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=Colors.TEXT_MUTED)
        lbl_dec.pack(anchor="w", padx=20, pady=(6, 2))

        combo_dec = ctk.CTkOptionMenu(dialog, values=profs_opciones)
        combo_dec.set(profs_opciones[0])
        combo_dec.pack(fill="x", padx=20, pady=(0, 6))

        def _guardar():
            cod = entry_cod.get().strip()
            nom = entry_nom.get().strip()
            if cod and nom:
                id_dec_sel = profs_map.get(combo_dec.get(), None)
                f = Facultad(
                    idFacultad=len(self.controller.facultades) + 1,
                    codigoFacultad=cod,
                    nombre=nom,
                    descripcion="Facultad institucional UPC",
                    ubicacion=entry_ubi.get().strip() or "Sede Sabanas",
                    telefono=entry_tel.get().strip() or "5842000",
                    correo=entry_cor.get().strip() or "facultad@unicesar.edu.co",
                    idDecano=id_dec_sel,
                    fechaCreacion=date.today(),
                    estado="ACTIVO",
                )
                self.controller.facultades.append(f)
                self.controller._recrear_gestores()
                self.controller.guardar_datos()
                self.actualizar_tablas()
                dialog.destroy()

        ctk.CTkButton(dialog, text="💾 Guardar Facultad", font=ctk.CTkFont(size=12, weight="bold"), fg_color="#10B981", hover_color="#059669", height=36, command=_guardar).pack(pady=16)

    def _abrir_modal_editar_facultad(self, fac: Facultad) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"✏️ Editar Facultad {fac.codigoFacultad}")
        dialog.geometry("460x570")
        dialog.grab_set()

        ctk.CTkLabel(dialog, text=f"Modificar Facultad: {fac.nombre}", font=ctk.CTkFont(size=15, weight="bold")).pack(pady=12)

        entry_nom = ctk.CTkEntry(dialog)
        entry_nom.insert(0, fac.nombre)
        entry_nom.pack(fill="x", padx=20, pady=6)

        entry_ubi = ctk.CTkEntry(dialog)
        entry_ubi.insert(0, fac.ubicacion)
        entry_ubi.pack(fill="x", padx=20, pady=6)

        entry_tel = ctk.CTkEntry(dialog)
        entry_tel.insert(0, fac.telefono)
        entry_tel.pack(fill="x", padx=20, pady=6)

        entry_cor = ctk.CTkEntry(dialog)
        entry_cor.insert(0, fac.correo)
        entry_cor.pack(fill="x", padx=20, pady=6)

        # Opciones de Decano
        profs_opciones = ["(Sin Decano Asignado)"]
        profs_map: dict[str, int | None] = {"(Sin Decano Asignado)": None}
        for p in self.controller.profesores:
            pers = next((per for per in self.controller.personas if getattr(per, "idPersona", None) == getattr(p, "idPersona", None)), None)
            nom = f"{getattr(pers, 'primerNombre', '')} {getattr(pers, 'primerApellido', '')}".strip() or f"Docente #{p.idProfesor}"
            cod = getattr(p, "codigoProfesor", "")
            lbl = f"{nom} ({cod})" if cod else nom
            profs_opciones.append(lbl)
            profs_map[lbl] = p.idProfesor

        sel_val = profs_opciones[0]
        if getattr(fac, "idDecano", None):
            for lbl, pid in profs_map.items():
                if pid == fac.idDecano:
                    sel_val = lbl
                    break

        lbl_dec = ctk.CTkLabel(dialog, text="Decano / Autoridad Académica:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=Colors.TEXT_MUTED)
        lbl_dec.pack(anchor="w", padx=20, pady=(6, 2))

        combo_dec = ctk.CTkOptionMenu(dialog, values=profs_opciones)
        combo_dec.set(sel_val)
        combo_dec.pack(fill="x", padx=20, pady=(0, 6))

        def _guardar():
            fac.nombre = entry_nom.get().strip() or fac.nombre
            fac.ubicacion = entry_ubi.get().strip() or fac.ubicacion
            fac.telefono = entry_tel.get().strip() or fac.telefono
            fac.correo = entry_cor.get().strip() or fac.correo
            fac.idDecano = profs_map.get(combo_dec.get(), None)
            self.controller._recrear_gestores()
            self.controller.guardar_datos()
            self.actualizar_tablas()
            dialog.destroy()

        ctk.CTkButton(dialog, text="💾 Guardar Cambios", font=ctk.CTkFont(size=12, weight="bold"), fg_color="#10B981", hover_color="#059669", height=36, command=_guardar).pack(pady=16)

    def _eliminar_facultad(self, f_id: int) -> None:
        self.controller.facultades = [f for f in self.controller.facultades if f.idFacultad != f_id]
        self.controller._recrear_gestores()
        self.controller.guardar_datos()
        self.actualizar_tablas()

    # ------------------------------------------------------------------
    # MODALES CRUD PROGRAMA
    # ------------------------------------------------------------------
    def _abrir_modal_nuevo_programa(self) -> None:
        DialogFormPrograma(self, self.controller, on_success=self.actualizar_tablas)

    def _abrir_modal_editar_programa(self, prog: ProgramaAcademico) -> None:
        DialogFormPrograma(self, self.controller, on_success=self.actualizar_tablas, prog=prog)

    def _eliminar_programa(self, p_id: int) -> None:
        prog = next((p for p in self.controller.programas if p.idPrograma == p_id), None)
        if not prog:
            return

        cant_est = len([e for e in self.controller.estudiantes if getattr(e, "idPrograma", None) == p_id])
        cant_plan = len([p for p in self.controller.planes if getattr(p, "idPrograma", None) == p_id])

        if cant_est > 0 or cant_plan > 0:
            self._mostrar_aviso_no_eliminar_programa(prog, cant_est, cant_plan)
            return

        self.controller.programas = [p for p in self.controller.programas if p.idPrograma != p_id]
        self.controller._recrear_gestores()
        self.controller.guardar_datos()
        self.actualizar_tablas()

    def _mostrar_aviso_no_eliminar_programa(self, prog: ProgramaAcademico, cant_est: int, cant_plan: int) -> None:
        aviso = ctk.CTkToplevel(self)
        aviso.title("⚠️ Bloqueo de Integridad Referencial")
        aviso.geometry("480x300")
        aviso.grab_set()

        ctk.CTkLabel(
            aviso,
            text="⚠️ No es posible eliminar el Programa Académico",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color="#EF4444",
        ).pack(pady=(22, 10))

        nom = getattr(prog, "nombre", "Programa")
        cod = getattr(prog, "codigoPrograma", "N/A")
        msg = (
            f"El programa '{nom}' ({cod}) no puede eliminarse de la base de datos\n"
            f"porque cuenta con registros institucionales vinculados:\n\n"
            f"• {cant_est} Estudiante(s) matriculado(s)\n"
            f"• {cant_plan} Plan(es) de estudio registrado(s)\n\n"
            "Para retirar el programa sin comprometer la integridad histórica,\n"
            "edítelo y cambie su estado a 'INACTIVO'."
        )
        ctk.CTkLabel(aviso, text=msg, font=ctk.CTkFont(family="Segoe UI", size=12), justify="center").pack(padx=20, pady=8)

        ctk.CTkButton(
            aviso,
            text="Entendido",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=Colors.WIN_BLUE,
            hover_color=Colors.WIN_BLUE_HOVER,
            width=130,
            height=34,
            corner_radius=8,
            command=aviso.destroy,
        ).pack(pady=(12, 16))


class DialogFormPrograma(ctk.CTkToplevel):
    """Modal unificado para Creación y Edición de un Programa Académico."""

    def __init__(
        self,
        parent: ctk.CTkBaseClass,
        controller: 'PITAController',
        on_success: 'Callable[[], None]',
        prog: 'ProgramaAcademico' = None
    ) -> None:
        super().__init__(parent)
        self.prog = prog
        self.is_edit = prog is not None
        self.controller = controller
        self.on_success = on_success

        titulo = f"✏️ Editar Programa Académico — {prog.codigoPrograma or f'Prog #{prog.idPrograma}'}" if self.is_edit else "➕ Registrar Nuevo Programa Académico"
        self.title(titulo)
        self.geometry("600x750" if self.is_edit else "600x740")
        self.minsize(540, 620 if self.is_edit else 600)
        self.grab_set()

        self._construir_ui()

    def _construir_ui(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(16, 8))

        ctk.CTkLabel(
            header,
            text=f"✏️ Modificar Programa: {self.prog.nombre or 'Programa'}" if self.is_edit else "➕ Registrar Nuevo Programa Académico",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=Colors.TEXT_MAIN,
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Actualice la configuración curricular, directiva y el estado operativo del programa." if self.is_edit else "Ingrese los datos requeridos para aperturar una nueva oferta académica en la institución.",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=Colors.TEXT_MUTED,
        ).pack(anchor="w", pady=(2, 0))

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=16, pady=(0, 8))

        if self.is_edit:
            from datetime import date
            cant_estudiantes = len([e for e in self.controller.estudiantes if getattr(e, "idPrograma", None) == self.prog.idPrograma])
            cant_planes = len([p for p in self.controller.planes if getattr(p, "idPrograma", None) == self.prog.idPrograma])
            cant_docentes = len([d for d in self.controller.profesores if getattr(d, "idProgramaPrincipal", None) == self.prog.idPrograma])
            f_creacion_str = self.prog.fechaCreacion.strftime("%d/%m/%Y") if isinstance(self.prog.fechaCreacion, date) else str(self.prog.fechaCreacion or "Histórico")

            card_audit = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD, corner_radius=10, border_width=1, border_color=Colors.BORDER_SUBTLE)
            card_audit.pack(fill="x", pady=(0, 10))

            top_audit = ctk.CTkFrame(card_audit, fg_color="transparent")
            top_audit.pack(fill="x", padx=14, pady=(10, 6))

            badge_id = ctk.CTkFrame(top_audit, fg_color="#F1F5F9", corner_radius=6)
            badge_id.pack(side="left")
            ctk.CTkLabel(badge_id, text=f"🆔 ID: #{self.prog.idPrograma}", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=Colors.TEXT_MAIN).pack(padx=8, pady=2)

            is_act = (getattr(self.prog, "estado", "ACTIVO") or "ACTIVO").upper() == "ACTIVO"
            badge_estado_top = ctk.CTkFrame(top_audit, fg_color=Colors.BADGE_ACTIVE_BG if is_act else Colors.BADGE_EBRA_BG, corner_radius=6)
            badge_estado_top.pack(side="left", padx=8)
            self.lbl_badge_estado = ctk.CTkLabel(
                badge_estado_top,
                text="🟢 ACTIVO" if is_act else "🔴 INACTIVO",
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                text_color=Colors.BADGE_ACTIVE_TXT if is_act else Colors.BADGE_EBRA_TXT,
            )
            self.lbl_badge_estado.pack(padx=8, pady=2)
            self.badge_estado_top = badge_estado_top

            ctk.CTkLabel(top_audit, text=f"📅 Registro: {f_creacion_str}", font=ctk.CTkFont(family="Segoe UI", size=11), text_color=Colors.TEXT_MUTED).pack(side="right")

            kpis_frame = ctk.CTkFrame(card_audit, fg_color="#F8FAFC", corner_radius=8)
            kpis_frame.pack(fill="x", padx=12, pady=(0, 10))
            kpis_frame.columnconfigure((0, 1, 2), weight=1)

            def _hacer_kpi(col: int, icono: str, valor: int, rotulo: str, color_val: str) -> None:
                f = ctk.CTkFrame(kpis_frame, fg_color="transparent")
                f.grid(row=0, column=col, padx=6, pady=8, sticky="ew")
                ctk.CTkLabel(f, text=f"{icono} {valor}", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), text_color=color_val).pack()
                ctk.CTkLabel(f, text=rotulo, font=ctk.CTkFont(family="Segoe UI", size=10), text_color=Colors.TEXT_MUTED).pack()

            _hacer_kpi(0, "👨‍🎓", cant_estudiantes, "Estudiantes", Colors.ACCENT_PRIMARY)
            _hacer_kpi(1, "📑", cant_planes, "Planes de Estudio", "#10B981")
            _hacer_kpi(2, "👨‍🏫", cant_docentes, "Docentes", "#8B5CF6")
        else:
            from datetime import date
            card_banner = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD, corner_radius=10, border_width=1, border_color=Colors.BORDER_SUBTLE)
            card_banner.pack(fill="x", pady=(0, 10))

            b_content = ctk.CTkFrame(card_banner, fg_color="transparent")
            b_content.pack(fill="x", padx=14, pady=10)

            badge_new = ctk.CTkFrame(b_content, fg_color="#E0F2FE", corner_radius=6)
            badge_new.pack(side="left")
            ctk.CTkLabel(badge_new, text="🆕 Alta Institucional", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color="#0369A1").pack(padx=8, pady=2)

            badge_act = ctk.CTkFrame(b_content, fg_color=Colors.BADGE_ACTIVE_BG, corner_radius=6)
            badge_act.pack(side="left", padx=8)
            ctk.CTkLabel(badge_act, text="🟢 Estado Inicial: ACTIVO", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=Colors.BADGE_ACTIVE_TXT).pack(padx=8, pady=2)

            ctk.CTkLabel(b_content, text=f"📅 Fecha: {date.today().strftime('%d/%m/%Y')}", font=ctk.CTkFont(family="Segoe UI", size=11), text_color=Colors.TEXT_MUTED).pack(side="right")


        card_id = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD, corner_radius=10, border_width=1, border_color=Colors.BORDER_SUBTLE)
        card_id.pack(fill="x", pady=6)

        ctk.CTkLabel(
            card_id,
            text="🏷️ 1. Identificación y Estado Operativo" if self.is_edit else "🏷️ 1. Identificación del Programa",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=Colors.WIN_BLUE,
        ).pack(anchor="w", padx=14, pady=(10, 8))

        ctk.CTkLabel(card_id, text="Nombre del Programa Académico *", font=ctk.CTkFont(size=11, weight="bold"), text_color=Colors.TEXT_MAIN).pack(anchor="w", padx=14, pady=(2, 1))
        self.entry_nom = ctk.CTkEntry(card_id, height=32, placeholder_text="ej: Ingeniería de Sistemas / Derecho", fg_color=Colors.BG_INPUT, border_color=Colors.BORDER_SUBTLE)
        if self.is_edit: self.entry_nom.insert(0, self.prog.nombre or "")
        self.entry_nom.pack(fill="x", padx=14, pady=(0, 8))

        grid_id = ctk.CTkFrame(card_id, fg_color="transparent")
        grid_id.pack(fill="x", padx=14, pady=(0, 10))
        grid_id.columnconfigure(0, weight=3)
        grid_id.columnconfigure(1, weight=2)

        ctk.CTkLabel(grid_id, text="Código Institucional *", font=ctk.CTkFont(size=11, weight="bold"), text_color=Colors.TEXT_MAIN).grid(row=0, column=0, sticky="w", padx=(0, 6), pady=(0, 1))
        self.entry_cod = ctk.CTkEntry(grid_id, height=32, placeholder_text="ej: PROG-ING-SIST", fg_color=Colors.BG_INPUT, border_color=Colors.BORDER_SUBTLE)
        if self.is_edit: self.entry_cod.insert(0, self.prog.codigoPrograma or "")
        self.entry_cod.grid(row=1, column=0, sticky="ew", padx=(0, 6), pady=(0, 2))
        ctk.CTkLabel(grid_id, text="ℹ️ Clave oficial institucional (ej: PROG-ING-SIST)", font=ctk.CTkFont(size=10), text_color=Colors.TEXT_MUTED).grid(row=2, column=0, sticky="w", padx=(0, 6))

        if self.is_edit:
            ctk.CTkLabel(grid_id, text="Estado Operativo *", font=ctk.CTkFont(size=11, weight="bold"), text_color=Colors.TEXT_MAIN).grid(row=0, column=1, sticky="w", padx=(6, 0), pady=(0, 1))
            self.combo_estado = ctk.CTkComboBox(grid_id, values=["ACTIVO", "INACTIVO"], height=32, state="readonly", command=self._on_cambio_estado)
            self.combo_estado.set(getattr(self.prog, "estado", "ACTIVO") or "ACTIVO")
            self.combo_estado.grid(row=1, column=1, sticky="ew", padx=(6, 0), pady=(0, 2))

            self.lbl_alerta_inactivo = ctk.CTkLabel(
                card_id,
                text=f"⚠️ Advertencia: Este programa tiene {cant_estudiantes} estudiante(s) matriculado(s). Inactivarlo impedirá nuevas admisiones y aperturas de cursos.",
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color="#D97706",
                wraplength=480,
                justify="left",
            )
            self.cant_estudiantes = cant_estudiantes
            if not is_act and cant_estudiantes > 0:
                self.lbl_alerta_inactivo.pack(anchor="w", padx=14, pady=(0, 8))

        card_ads = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD, corner_radius=10, border_width=1, border_color=Colors.BORDER_SUBTLE)
        card_ads.pack(fill="x", pady=6)

        ctk.CTkLabel(
            card_ads,
            text="🏛️ 2. Adscripción y Dirección Académica",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=Colors.WIN_BLUE,
        ).pack(anchor="w", padx=14, pady=(10, 8))

        fac_opts = [f"{f.idFacultad} - {f.nombre}" for f in self.controller.facultades] or ["1 - Facultad General"]
        ctk.CTkLabel(card_ads, text="Facultad de Adscripción *", font=ctk.CTkFont(size=11, weight="bold"), text_color=Colors.TEXT_MAIN).pack(anchor="w", padx=14, pady=(2, 1))
        self.combo_fac = ctk.CTkComboBox(card_ads, values=fac_opts, height=32, state="readonly")
        sel_fac = fac_opts[0]
        if self.is_edit:
            sel_fac = next((fo for fo in fac_opts if fo.startswith(f"{self.prog.idFacultad} - ")), fac_opts[0])
        self.combo_fac.set(sel_fac)
        self.combo_fac.pack(fill="x", padx=14, pady=(0, 10))

        profs_opciones, profs_map = self._obtener_catalogo_profesores()
        self.profs_map = profs_map

        ctk.CTkLabel(card_ads, text="Director de Programa (Docente a Cargo)", font=ctk.CTkFont(size=11, weight="bold"), text_color=Colors.TEXT_MAIN).pack(anchor="w", padx=14, pady=(2, 1))
        self.combo_dir = ctk.CTkComboBox(card_ads, values=profs_opciones, height=32, state="readonly")
        sel_dir = profs_opciones[0]
        if self.is_edit and self.prog.idDirector:
            for lbl, pid in profs_map.items():
                if pid == self.prog.idDirector:
                    sel_dir = lbl
                    break
        self.combo_dir.set(sel_dir)
        self.combo_dir.pack(fill="x", padx=14, pady=(0, 10))

        card_reg = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD, corner_radius=10, border_width=1, border_color=Colors.BORDER_SUBTLE)
        card_reg.pack(fill="x", pady=6)

        ctk.CTkLabel(
            card_reg,
            text="📜 3. Regulación y Formación Académica",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=Colors.WIN_BLUE,
        ).pack(anchor="w", padx=14, pady=(10, 8))

        grid_reg = ctk.CTkFrame(card_reg, fg_color="transparent")
        grid_reg.pack(fill="x", padx=14, pady=(0, 8))
        grid_reg.columnconfigure(0, weight=1)
        grid_reg.columnconfigure(1, weight=1)

        niveles = ["PREGRADO", "POSGRADO", "ESPECIALIZACIÓN", "MAESTRÍA", "DOCTORADO", "TECNOLOGÍA"]
        ctk.CTkLabel(grid_reg, text="Nivel de Formación *", font=ctk.CTkFont(size=11, weight="bold"), text_color=Colors.TEXT_MAIN).grid(row=0, column=0, sticky="w", padx=(0, 6), pady=(0, 1))
        self.combo_nivel = ctk.CTkComboBox(grid_reg, values=niveles, height=32, state="readonly")
        act_nivel = (self.prog.nivelFormacion or "PREGRADO").upper() if self.is_edit else "PREGRADO"
        self.combo_nivel.set(act_nivel if act_nivel in niveles else "PREGRADO")
        self.combo_nivel.grid(row=1, column=0, sticky="ew", padx=(0, 6), pady=(0, 6))

        modalidades = ["PRESENCIAL", "VIRTUAL", "A DISTANCIA", "DUAL", "HÍBRIDA / SEMIPRESENCIAL"]
        ctk.CTkLabel(grid_reg, text="Modalidad *", font=ctk.CTkFont(size=11, weight="bold"), text_color=Colors.TEXT_MAIN).grid(row=0, column=1, sticky="w", padx=(6, 0), pady=(0, 1))
        self.combo_mod = ctk.CTkComboBox(grid_reg, values=modalidades, height=32, state="readonly")
        act_mod = (self.prog.modalidad or "PRESENCIAL").upper() if self.is_edit else "PRESENCIAL"
        self.combo_mod.set(act_mod if act_mod in modalidades else "PRESENCIAL")
        self.combo_mod.grid(row=1, column=1, sticky="ew", padx=(6, 0), pady=(0, 6))

        ctk.CTkLabel(card_reg, text="Registro Calificado / Resolución MEN", font=ctk.CTkFont(size=11, weight="bold"), text_color=Colors.TEXT_MAIN).pack(anchor="w", padx=14, pady=(4, 1))
        self.entry_rc = ctk.CTkEntry(card_reg, height=32, placeholder_text="ej: RC-2026-V1 / Res. 014526 MEN", fg_color=Colors.BG_INPUT, border_color=Colors.BORDER_SUBTLE)
        if self.is_edit: self.entry_rc.insert(0, self.prog.registroCalificado or "")
        self.entry_rc.pack(fill="x", padx=14, pady=(0, 10))

        card_cur = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD, corner_radius=10, border_width=1, border_color=Colors.BORDER_SUBTLE)
        card_cur.pack(fill="x", pady=6)

        ctk.CTkLabel(
            card_cur,
            text="📊 4. Duración y Estructura Curricular",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=Colors.WIN_BLUE,
        ).pack(anchor="w", padx=14, pady=(10, 8))

        grid_cur = ctk.CTkFrame(card_cur, fg_color="transparent")
        grid_cur.pack(fill="x", padx=14, pady=(0, 10))
        grid_cur.columnconfigure(0, weight=1)
        grid_cur.columnconfigure(1, weight=1)

        ctk.CTkLabel(grid_cur, text="Número de Semestres *", font=ctk.CTkFont(size=11, weight="bold"), text_color=Colors.TEXT_MAIN).grid(row=0, column=0, sticky="w", padx=(0, 6), pady=(0, 1))
        self.entry_sem = ctk.CTkEntry(grid_cur, height=32, placeholder_text="ej: 10", fg_color=Colors.BG_INPUT, border_color=Colors.BORDER_SUBTLE)
        if self.is_edit: self.entry_sem.insert(0, str(self.prog.numeroSemestres or 10))
        self.entry_sem.grid(row=1, column=0, sticky="ew", padx=(0, 6), pady=(0, 2))

        ctk.CTkLabel(grid_cur, text="Total Créditos Académicos *", font=ctk.CTkFont(size=11, weight="bold"), text_color=Colors.TEXT_MAIN).grid(row=0, column=1, sticky="w", padx=(6, 0), pady=(0, 1))
        self.entry_cred = ctk.CTkEntry(grid_cur, height=32, placeholder_text="ej: 160", fg_color=Colors.BG_INPUT, border_color=Colors.BORDER_SUBTLE)
        if self.is_edit: self.entry_cred.insert(0, str(self.prog.totalCreditos or 160))
        self.entry_cred.grid(row=1, column=1, sticky="ew", padx=(6, 0), pady=(0, 2))

        self.lbl_error = ctk.CTkLabel(scroll, text="", font=ctk.CTkFont(size=11, weight="bold"), text_color=Colors.BADGE_EBRA_TXT)
        self.lbl_error.pack(padx=14, pady=(6, 0))

        btn_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_frame.pack(fill="x", padx=14, pady=16)

        btn_cancel = ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="transparent",
            text_color=Colors.TEXT_MAIN,
            border_width=1,
            border_color=Colors.BORDER_SUBTLE,
            hover_color=Colors.BG_HOVER,
            command=self.destroy,
            width=120,
            height=36,
        )
        btn_cancel.pack(side="left", expand=True, padx=(0, 6))

        btn_guardar = ctk.CTkButton(
            btn_frame,
            text="💾 Guardar Cambios" if self.is_edit else "💾 Registrar Programa",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=Colors.ACCENT_PRIMARY,
            text_color="#FFFFFF",
            hover_color=Colors.ACCENT_HOVER,
            command=self._guardar,
            width=120,
            height=36,
        )
        btn_guardar.pack(side="right", expand=True, padx=(6, 0))

    def _on_cambio_estado(self, val: str) -> None:
        if not self.is_edit: return
        if val == "INACTIVO" and self.cant_estudiantes > 0:
            self.lbl_alerta_inactivo.pack(anchor="w", padx=14, pady=(0, 8), before=self.combo_fac.master)
            self.badge_estado_top.configure(fg_color=Colors.BADGE_EBRA_BG)
            self.lbl_badge_estado.configure(text="🔴 INACTIVO", text_color=Colors.BADGE_EBRA_TXT)
        else:
            self.lbl_alerta_inactivo.pack_forget()
            if val == "ACTIVO":
                self.badge_estado_top.configure(fg_color=Colors.BADGE_ACTIVE_BG)
                self.lbl_badge_estado.configure(text="🟢 ACTIVO", text_color=Colors.BADGE_ACTIVE_TXT)
            else:
                self.badge_estado_top.configure(fg_color=Colors.BADGE_EBRA_BG)
                self.lbl_badge_estado.configure(text="🔴 INACTIVO", text_color=Colors.BADGE_EBRA_TXT)

    def _obtener_catalogo_profesores(self):
        profs_opc = ["-- Sin Director Asignado --"]
        profs_map = {"-- Sin Director Asignado --": None}
        for prof in self.controller.profesores:
            if getattr(prof, "estado", "ACTIVO") == "ACTIVO":
                pers = next((p for p in self.controller.personas if getattr(p, "idPersona", None) == getattr(prof, "idPersona", None)), None)
                if pers:
                    doc = getattr(pers, "documentoIdentidad", getattr(prof, "codigoProfesor", "N/A"))
                    nom = f"{getattr(pers, 'primerNombre', '')} {getattr(pers, 'primerApellido', '')}".strip()
                    lbl = f"{doc} - {nom}"
                else:
                    lbl = f"Docente #{getattr(prof, 'idProfesor', 'N/A')}"
                profs_opc.append(lbl)
                profs_map[lbl] = prof.idPersona
        return profs_opc, profs_map

    def _guardar(self) -> None:
        nom = self.entry_nom.get().strip()
        cod = self.entry_cod.get().strip()
        sem = self.entry_sem.get().strip()
        cred = self.entry_cred.get().strip()
        rc = self.entry_rc.get().strip()
        estado = self.combo_estado.get() if self.is_edit else "ACTIVO"

        if not nom or not cod or not sem or not cred:
            self.lbl_error.configure(text="⚠️ Error: Los campos marcados con (*) son obligatorios.")
            return

        sel_fac = self.combo_fac.get()
        fac_id = None
        if sel_fac and " - " in sel_fac:
            try:
                fac_id = int(sel_fac.split(" - ")[0])
            except ValueError:
                pass
        if fac_id is None:
            self.lbl_error.configure(text="⚠️ Error: Debe seleccionar una facultad válida.")
            return

        sel_dir_lbl = self.combo_dir.get()
        dir_id = self.profs_map.get(sel_dir_lbl)

        try:
            n_sem = int(sem)
            n_cred = int(cred)
        except ValueError:
            self.lbl_error.configure(text="⚠️ Error: Semestres y Créditos deben ser números enteros.")
            return

        if self.is_edit:
            self.prog.nombre = nom
            self.prog.codigoPrograma = cod
            self.prog.estado = estado
            self.prog.idFacultad = fac_id
            self.prog.idDirector = dir_id
            self.prog.nivelFormacion = self.combo_nivel.get()
            self.prog.modalidad = self.combo_mod.get()
            self.prog.registroCalificado = rc
            self.prog.numeroSemestres = n_sem
            self.prog.totalCreditos = n_cred

            try:
                self.controller.servicios.facultades.actualizar_programa(self.prog)
                self.on_success()
                self.destroy()
            except Exception as e:
                self.lbl_error.configure(text=f"⚠️ Error al guardar: {e}")
        else:
            try:
                self.controller.servicios.facultades.crear_programa(
                    id_facultad=fac_id,
                    codigo=cod,
                    nombre=nom,
                    nivel=self.combo_nivel.get(),
                    modalidad=self.combo_mod.get(),
                    registro=rc,
                    semestres=n_sem,
                    creditos=n_cred,
                    director_id=dir_id,
                )
                self.on_success()
                self.destroy()
            except Exception as e:
                self.lbl_error.configure(text=f"⚠️ Error al registrar: {e}")
