"""Diálogos modales para creación y edición de cursos y ofertas académicas."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Callable
import customtkinter as ctk

from ui_gui.theme import Colors
from dominio.modelo_datos import Curso

if TYPE_CHECKING:
    from ui_gui.academica.academica_service import AcademicaService
    from ui_gui.gui_controller import PITAController


class DialogNuevoCurso(ctk.CTkToplevel):
    """Modal para dar de alta una nueva asignatura en el catálogo."""

    def __init__(self, parent: ctk.CTkBaseClass, service: AcademicaService, on_success: Callable[[], None]) -> None:
        super().__init__(parent)
        self.service = service
        self.on_success = on_success

        self.title("➕ Crear Nueva Asignatura")
        self.geometry("520x680")
        self.minsize(480, 600)
        self.grab_set()

        self._crear_interfaz()

    def _crear_interfaz(self) -> None:
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=15, pady=10)

        ctk.CTkLabel(
            scroll,
            text="Crear Asignatura en el Catálogo",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#F8FAFC",
        ).pack(anchor="w", padx=10, pady=(5, 2))
        ctk.CTkLabel(
            scroll,
            text="Defina los parámetros académicos, créditos y nota mínima aprobatoria.",
            font=ctk.CTkFont(size=11),
            text_color="#94A3B8",
        ).pack(anchor="w", padx=10, pady=(0, 15))

        def _agregar_campo(label_text: str, default_val: str = "", placeholder: str = "") -> ctk.CTkEntry:
            ctk.CTkLabel(
                scroll,
                text=label_text,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#CBD5E1",
            ).pack(anchor="w", padx=10, pady=(6, 2))
            entry = ctk.CTkEntry(scroll, placeholder_text=placeholder, height=36)
            if default_val:
                entry.insert(0, default_val)
            entry.pack(fill="x", padx=10, pady=(0, 4))
            return entry

        entry_cod = _agregar_campo("Código de la Asignatura *", placeholder="ej: INF-201")
        entry_nom = _agregar_campo("Nombre de la Asignatura *", placeholder="ej: Inteligencia Artificial")
        entry_cred = _agregar_campo("Número de Créditos *", default_val="3", placeholder="ej: 3")
        entry_ht = _agregar_campo("Horas Teóricas Semanales", default_val="3", placeholder="ej: 3")
        entry_hp = _agregar_campo("Horas Prácticas Semanales", default_val="2", placeholder="ej: 2")
        entry_nota = _agregar_campo("Nota Mínima Aprobatoria * (Reglamento Art. 45)", default_val="3.0", placeholder="ej: 3.0")
        entry_cupo = _agregar_campo("Cupo Sugerido de Estudiantes", default_val="30", placeholder="ej: 30")

        lbl_error = ctk.CTkLabel(scroll, text="", font=ctk.CTkFont(size=11, weight="bold"), text_color="#EF4444")
        lbl_error.pack(padx=10, pady=(6, 0))

        def _guardar():
            cod = entry_cod.get().strip()
            nom = entry_nom.get().strip()
            cred = entry_cred.get().strip()
            ht = entry_ht.get().strip()
            hp = entry_hp.get().strip()
            nota = entry_nota.get().strip().replace(",", ".")
            cupo = entry_cupo.get().strip()

            if not cod or not nom:
                lbl_error.configure(text="⚠️ El código y el nombre son obligatorios.")
                return

            c_cred = int(cred) if cred.isdigit() else 3
            c_ht = int(ht) if ht.isdigit() else 3
            c_hp = int(hp) if hp.isdigit() else 2
            c_cupo = int(cupo) if cupo.isdigit() else 30

            try:
                c_nota = Decimal(nota)
                if c_nota <= Decimal("0"):
                    c_nota = Decimal("3.0")
            except Exception:
                c_nota = Decimal("3.0")

            self.service.crear_curso(cod, nom, c_cred, c_ht, c_hp, c_cupo, c_nota)
            self.destroy()
            self.on_success()

        btn_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=(15, 10))

        ctk.CTkButton(
            btn_frame,
            text="💾 Guardar Asignatura",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#0067C0",
            hover_color="#005FB8",
            height=38,
            command=_guardar,
        ).pack(side="left", expand=True, fill="x", padx=(0, 6))

        ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            font=ctk.CTkFont(size=12),
            fg_color="#334155",
            hover_color="#475569",
            height=38,
            command=self.destroy,
        ).pack(side="right", padx=(6, 0))


class DialogEditarCurso(ctk.CTkToplevel):
    """Modal para editar una asignatura existente."""

    def __init__(self, parent: ctk.CTkBaseClass, curso: Curso, service: AcademicaService, on_success: Callable[[], None]) -> None:
        super().__init__(parent)
        self.curso = curso
        self.service = service
        self.on_success = on_success

        self.title(f"✏️ Editar Asignatura {curso.codigoCurso}")
        self.geometry("520x680")
        self.minsize(480, 600)
        self.grab_set()

        self._crear_interfaz()

    def _crear_interfaz(self) -> None:
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=15, pady=10)

        ctk.CTkLabel(
            scroll,
            text=f"✏️ Modificar Asignatura: {self.curso.codigoCurso}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#F8FAFC",
        ).pack(anchor="w", padx=10, pady=(5, 2))
        ctk.CTkLabel(
            scroll,
            text="Ajuste los créditos, intensidades horarias y la nota mínima requerida.",
            font=ctk.CTkFont(size=11),
            text_color="#94A3B8",
        ).pack(anchor="w", padx=10, pady=(0, 15))

        def _agregar_campo(label_text: str, default_val: str = "", disabled: bool = False) -> ctk.CTkEntry:
            ctk.CTkLabel(
                scroll,
                text=label_text,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#CBD5E1",
            ).pack(anchor="w", padx=10, pady=(6, 2))
            entry = ctk.CTkEntry(scroll, height=36)
            if default_val:
                entry.insert(0, default_val)
            if disabled:
                entry.configure(state="disabled", text_color="#94A3B8")
            entry.pack(fill="x", padx=10, pady=(0, 4))
            return entry

        _agregar_campo("Código del Curso (Identificador)", default_val=self.curso.codigoCurso or "N/A", disabled=True)
        entry_nom = _agregar_campo("Nombre de la Asignatura *", default_val=self.curso.nombre or "")
        entry_cred = _agregar_campo("Número de Créditos *", default_val=str(self.curso.numeroCreditos or 3))
        entry_ht = _agregar_campo("Horas Teóricas Semanales", default_val=str(getattr(self.curso, "horasTeoricas", 3) or 3))
        entry_hp = _agregar_campo("Horas Prácticas Semanales", default_val=str(getattr(self.curso, "horasPracticas", 2) or 2))

        # Nota mínima aprobatoria actual con fallback seguro
        curr_nota = getattr(self.curso, "notaMinimaAprobatoria", None)
        try:
            nota_str = f"{float(curr_nota):.1f}" if (curr_nota is not None and float(curr_nota) > 0) else "3.0"
        except Exception:
            nota_str = "3.0"
        entry_nota = _agregar_campo("Nota Mínima Aprobatoria * (Reglamento Art. 45)", default_val=nota_str)

        entry_cupo = _agregar_campo("Cupo Sugerido de Estudiantes", default_val=str(getattr(self.curso, "cupoSugerido", 30) or 30))

        lbl_error = ctk.CTkLabel(scroll, text="", font=ctk.CTkFont(size=11, weight="bold"), text_color="#EF4444")
        lbl_error.pack(padx=10, pady=(6, 0))

        def _guardar():
            nom = entry_nom.get().strip()
            cred = entry_cred.get().strip()
            ht = entry_ht.get().strip()
            hp = entry_hp.get().strip()
            nota = entry_nota.get().strip().replace(",", ".")
            cupo = entry_cupo.get().strip()

            if not nom:
                lbl_error.configure(text="⚠️ El nombre de la asignatura no puede estar vacío.")
                return

            self.curso.nombre = nom
            if cred.isdigit():
                self.curso.numeroCreditos = int(cred)
            if ht.isdigit():
                self.curso.horasTeoricas = int(ht)
            if hp.isdigit():
                self.curso.horasPracticas = int(hp)
            if cupo.isdigit():
                self.curso.cupoSugerido = int(cupo)

            try:
                val_nota = Decimal(nota)
                if val_nota > Decimal("0"):
                    self.curso.notaMinimaAprobatoria = val_nota
                else:
                    self.curso.notaMinimaAprobatoria = Decimal("3.0")
            except Exception:
                self.curso.notaMinimaAprobatoria = Decimal("3.0")

            self.service.controller._recrear_gestores()
            self.service.controller.guardar_datos()
            self.destroy()
            self.on_success()

        btn_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=(15, 10))

        ctk.CTkButton(
            btn_frame,
            text="💾 Guardar Cambios",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#10B981",
            hover_color="#059669",
            height=38,
            command=_guardar,
        ).pack(side="left", expand=True, fill="x", padx=(0, 6))

        ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            font=ctk.CTkFont(size=12),
            fg_color="#334155",
            hover_color="#475569",
            height=38,
            command=self.destroy,
        ).pack(side="right", padx=(6, 0))


class DialogNuevaOferta(ctk.CTkToplevel):
    """Modal para abrir una nueva oferta académica / grupo."""

    def __init__(self, parent: ctk.CTkBaseClass, controller: PITAController, service: AcademicaService, on_success: Callable[[], None]) -> None:
        super().__init__(parent)
        self.controller = controller
        self.service = service
        self.on_success = on_success

        self.title("🏫 Abrir Oferta de Asignatura (Grupo)")
        self.geometry("520x620")
        self.grab_set()

        self._crear_interfaz()

    def _crear_interfaz(self) -> None:
        ctk.CTkLabel(self, text="Abrir Oferta de Curso / Grupo", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 5))
        ctk.CTkLabel(self, text="Configure el grupo, periodo, cupo y docente asignado.", font=ctk.CTkFont(size=11), text_color="#94A3B8").pack(pady=(0, 15))

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        # Asignatura
        ctk.CTkLabel(scroll, text="Asignatura a Ofertar *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(anchor="w", padx=10, pady=(2, 0))
        curso_vals = [f"{c.idCurso} - {c.codigoCurso} | {c.nombre}" for c in self.controller.cursos] or ["1 - Sin Cursos"]
        combo_curso = ctk.CTkComboBox(scroll, values=curso_vals)
        combo_curso.pack(fill="x", padx=10, pady=(2, 8))

        # Periodo
        ctk.CTkLabel(scroll, text="Periodo Académico *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(anchor="w", padx=10, pady=(2, 0))
        per_vals = [f"{p.idPeriodo} - {p.codigo} | {p.nombre}" for p in self.controller.periodos_academicos] or ["1 - 2026-1"]
        combo_per = ctk.CTkComboBox(scroll, values=per_vals)
        combo_per.pack(fill="x", padx=10, pady=(2, 8))

        # Grupo y Cupo
        row_gc = ctk.CTkFrame(scroll, fg_color="transparent")
        row_gc.pack(fill="x", padx=10, pady=(2, 8))
        row_gc.columnconfigure(0, weight=1)
        row_gc.columnconfigure(1, weight=1)

        ctk.CTkLabel(row_gc, text="Grupo *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=0, column=0, sticky="w", padx=5)
        ctk.CTkLabel(row_gc, text="Cupo Máximo *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=0, column=1, sticky="w", padx=5)

        entry_grupo = ctk.CTkEntry(row_gc)
        entry_grupo.insert(0, "01")
        entry_grupo.grid(row=1, column=0, sticky="ew", padx=5, pady=2)

        entry_cupo = ctk.CTkEntry(row_gc)
        entry_cupo.insert(0, "35")
        entry_cupo.grid(row=1, column=1, sticky="ew", padx=5, pady=2)

        # Aula y Sede
        row_as = ctk.CTkFrame(scroll, fg_color="transparent")
        row_as.pack(fill="x", padx=10, pady=(2, 8))
        row_as.columnconfigure(0, weight=1)
        row_as.columnconfigure(1, weight=1)

        ctk.CTkLabel(row_as, text="Aula", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=0, column=0, sticky="w", padx=5)
        ctk.CTkLabel(row_as, text="Sede", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=0, column=1, sticky="w", padx=5)

        entry_aula = ctk.CTkEntry(row_as)
        entry_aula.insert(0, "Aula 201")
        entry_aula.grid(row=1, column=0, sticky="ew", padx=5, pady=2)

        entry_sede = ctk.CTkEntry(row_as)
        entry_sede.insert(0, "Sede Sabanas")
        entry_sede.grid(row=1, column=1, sticky="ew", padx=5, pady=2)

        # Modalidad
        ctk.CTkLabel(scroll, text="Modalidad", font=ctk.CTkFont(size=11), text_color="#94A3B8").pack(anchor="w", padx=10, pady=(2, 0))
        combo_mod = ctk.CTkComboBox(scroll, values=["PRESENCIAL", "VIRTUAL", "HIBRIDA"])
        combo_mod.set("PRESENCIAL")
        combo_mod.pack(fill="x", padx=10, pady=(2, 8))

        # Docente a Asignar
        ctk.CTkLabel(scroll, text="Profesor Asignado (Opcional)", font=ctk.CTkFont(size=11, weight="bold"), text_color="#38BDF8").pack(anchor="w", padx=10, pady=(2, 0))
        prof_options = ["Sin Asignar"]
        for pr in self.controller.profesores:
            pe = next((p for p in self.controller.personas if p.idPersona == pr.idPersona), None)
            nom = f"{pe.primerNombre} {pe.primerApellido}" if pe else "Profesor"
            prof_options.append(f"{pr.idProfesor} - {pr.codigoProfesor} | {nom}")

        combo_prof = ctk.CTkComboBox(scroll, values=prof_options)
        combo_prof.set(prof_options[0])
        combo_prof.pack(fill="x", padx=10, pady=(2, 8))

        def _guardar_oferta():
            c_sel = combo_curso.get().split(" - ")[0].strip()
            id_curso = int(c_sel) if c_sel.isdigit() else 1

            p_sel = combo_per.get().split(" - ")[0].strip()
            id_per = int(p_sel) if p_sel.isdigit() else 1

            gr = entry_grupo.get().strip() or "01"
            cupo_str = entry_cupo.get().strip()
            cupo = int(cupo_str) if cupo_str.isdigit() else 35

            aula = entry_aula.get().strip() or "Aula General"
            sede = entry_sede.get().strip() or "Sede Principal"
            mod = combo_mod.get()

            id_prof = None
            pr_sel = combo_prof.get()
            if pr_sel != "Sin Asignar" and " - " in pr_sel:
                p_id_str = pr_sel.split(" - ")[0].strip()
                if p_id_str.isdigit():
                    id_prof = int(p_id_str)

            self.service.crear_oferta(id_curso, id_per, gr, cupo, aula, sede, mod, id_prof)
            self.destroy()
            self.on_success()

        ctk.CTkButton(self, text="🚀 Publicar Oferta", font=ctk.CTkFont(size=12, weight="bold"), fg_color="#059669", hover_color="#047857", height=38, command=_guardar_oferta).pack(pady=15)
