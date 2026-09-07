"""Vista de Gestión de Facultades y Programas Académicos (Taller 1 Requisitos 24 y 25)."""

from __future__ import annotations

from datetime import date
import customtkinter as ctk
from typing import TYPE_CHECKING

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

            cells = [
                (getattr(fac, "codigoFacultad", "N/A"), "#F59E0B"),
                (getattr(fac, "nombre", "N/A"), "#F8FAFC"),
                (nom_dec, "#38BDF8" if nom_dec != "Sin Asignar" else "#94A3B8"),
                getattr(fac, "ubicacion", "N/A"),
                getattr(fac, "telefono", "N/A"),
                getattr(fac, "correo", "N/A"),
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

        headers = ["Código", "Programa Académico", "Nivel", "Modalidad", "Semestres", "Créditos", "Facultad", "Acciones"]
        col_weights = [2, 4, 2, 2, 2, 2, 3, 3]
        col_mins = [90, 180, 90, 100, 80, 80, 140, 160]

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

            cells = [
                (getattr(prog, "codigoPrograma", "N/A"), "#38BDF8"),
                (getattr(prog, "nombre", "N/A"), "#F8FAFC"),
                getattr(prog, "nivelFormacion", "PREGRADO"),
                getattr(prog, "modalidad", "PRESENCIAL"),
                f"{getattr(prog, 'numeroSemestres', 10)} Sem",
                f"{getattr(prog, 'totalCreditos', 160)} Cred",
                nom_fac,
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
        dialog = ctk.CTkToplevel(self)
        dialog.title("➕ Registrar Nuevo Programa Académico")
        dialog.geometry("480x560")
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Crear Programa Académico de Pregrado/Posgrado", font=ctk.CTkFont(size=15, weight="bold")).pack(pady=12)

        entry_cod = ctk.CTkEntry(dialog, placeholder_text="Código Programa (ej: PROG-ING-SIST)")
        entry_cod.pack(fill="x", padx=20, pady=6)

        entry_nom = ctk.CTkEntry(dialog, placeholder_text="Nombre del Programa")
        entry_nom.pack(fill="x", padx=20, pady=6)

        fac_opts = [f"{f.idFacultad} - {f.nombre}" for f in self.controller.facultades] or ["1 - Facultad General"]
        combo_fac = ctk.CTkComboBox(dialog, values=fac_opts)
        combo_fac.pack(fill="x", padx=20, pady=6)

        entry_sem = ctk.CTkEntry(dialog, placeholder_text="Número de Semestres (ej: 10)")
        entry_sem.pack(fill="x", padx=20, pady=6)

        entry_cred = ctk.CTkEntry(dialog, placeholder_text="Total Créditos (ej: 165)")
        entry_cred.pack(fill="x", padx=20, pady=6)

        def _guardar():
            cod = entry_cod.get().strip()
            nom = entry_nom.get().strip()
            sel_fac = combo_fac.get()
            fac_id = int(sel_fac.split(" - ")[0]) if " - " in sel_fac else 1

            if cod and nom:
                p = ProgramaAcademico(
                    idPrograma=len(self.controller.programas) + 1,
                    codigoPrograma=cod,
                    nombre=nom,
                    nivelFormacion="PREGRADO",
                    modalidad="PRESENCIAL",
                    numeroSemestres=int(entry_sem.get().strip()) if entry_sem.get().strip().isdigit() else 10,
                    totalCreditos=int(entry_cred.get().strip()) if entry_cred.get().strip().isdigit() else 165,
                    registroCalificado="RC-2026-V1",
                    fechaCreacion=date.today(),
                    idDirector=1,
                    idFacultad=fac_id,
                    estado="ACTIVO",
                )
                self.controller.programas.append(p)
                self.controller._recrear_gestores()
                self.actualizar_tablas()
                dialog.destroy()

        ctk.CTkButton(dialog, text="💾 Guardar Programa", font=ctk.CTkFont(size=12, weight="bold"), fg_color="#10B981", hover_color="#059669", height=36, command=_guardar).pack(pady=20)

    def _abrir_modal_editar_programa(self, prog: ProgramaAcademico) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"✏️ Editar Programa {prog.codigoPrograma}")
        dialog.geometry("480x520")
        dialog.grab_set()

        ctk.CTkLabel(dialog, text=f"Modificar Programa: {prog.nombre}", font=ctk.CTkFont(size=15, weight="bold")).pack(pady=12)

        entry_nom = ctk.CTkEntry(dialog)
        entry_nom.insert(0, prog.nombre)
        entry_nom.pack(fill="x", padx=20, pady=6)

        entry_sem = ctk.CTkEntry(dialog)
        entry_sem.insert(0, str(prog.numeroSemestres))
        entry_sem.pack(fill="x", padx=20, pady=6)

        entry_cred = ctk.CTkEntry(dialog)
        entry_cred.insert(0, str(prog.totalCreditos))
        entry_cred.pack(fill="x", padx=20, pady=6)

        def _guardar():
            prog.nombre = entry_nom.get().strip() or prog.nombre
            if entry_sem.get().strip().isdigit():
                prog.numeroSemestres = int(entry_sem.get().strip())
            if entry_cred.get().strip().isdigit():
                prog.totalCreditos = int(entry_cred.get().strip())
            self.controller._recrear_gestores()
            self.actualizar_tablas()
            dialog.destroy()

        ctk.CTkButton(dialog, text="💾 Guardar Cambios", font=ctk.CTkFont(size=12, weight="bold"), fg_color="#10B981", hover_color="#059669", height=36, command=_guardar).pack(pady=20)

    def _eliminar_programa(self, p_id: int) -> None:
        self.controller.programas = [p for p in self.controller.programas if p.idPrograma != p_id]
        self.controller._recrear_gestores()
        self.actualizar_tablas()
