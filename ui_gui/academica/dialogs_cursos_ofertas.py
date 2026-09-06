"""Diálogos modales para creación y edición de cursos y ofertas académicas."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Callable
import customtkinter as ctk

from ui_gui.theme import Colors
from modelo_datos import Curso

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
        self.geometry("500x560")
        self.grab_set()

        self._crear_interfaz()

    def _crear_interfaz(self) -> None:
        ctk.CTkLabel(self, text="Crear Asignatura en el Catálogo", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 5))
        ctk.CTkLabel(self, text="Defina los parámetros base de la asignatura académica.", font=ctk.CTkFont(size=11), text_color="#94A3B8").pack(pady=(0, 15))

        entry_cod = ctk.CTkEntry(self, placeholder_text="Código del Curso (ej: INF-201)")
        entry_cod.pack(fill="x", padx=25, pady=6)

        entry_nom = ctk.CTkEntry(self, placeholder_text="Nombre de la Asignatura")
        entry_nom.pack(fill="x", padx=25, pady=6)

        entry_cred = ctk.CTkEntry(self, placeholder_text="Número de Créditos (ej: 3)")
        entry_cred.insert(0, "3")
        entry_cred.pack(fill="x", padx=25, pady=6)

        entry_ht = ctk.CTkEntry(self, placeholder_text="Horas Teóricas Semanales (ej: 3)")
        entry_ht.insert(0, "3")
        entry_ht.pack(fill="x", padx=25, pady=6)

        entry_hp = ctk.CTkEntry(self, placeholder_text="Horas Prácticas Semanales (ej: 2)")
        entry_hp.insert(0, "2")
        entry_hp.pack(fill="x", padx=25, pady=6)

        entry_cupo = ctk.CTkEntry(self, placeholder_text="Cupo Sugerido (ej: 30)")
        entry_cupo.insert(0, "30")
        entry_cupo.pack(fill="x", padx=25, pady=6)

        lbl_error = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=11, weight="bold"), text_color="#EF4444")
        lbl_error.pack(pady=(4, 0))

        def _guardar():
            cod = entry_cod.get().strip()
            nom = entry_nom.get().strip()
            cred = entry_cred.get().strip()
            ht = entry_ht.get().strip()
            hp = entry_hp.get().strip()
            cupo = entry_cupo.get().strip()

            if not cod or not nom:
                lbl_error.configure(text="⚠️ El código y el nombre son obligatorios.")
                return

            c_cred = int(cred) if cred.isdigit() else 3
            c_ht = int(ht) if ht.isdigit() else 3
            c_hp = int(hp) if hp.isdigit() else 2
            c_cupo = int(cupo) if cupo.isdigit() else 30

            self.service.crear_curso(cod, nom, c_cred, c_ht, c_hp, c_cupo)
            self.destroy()
            self.on_success()

        ctk.CTkButton(self, text="💾 Guardar Asignatura", font=ctk.CTkFont(size=12, weight="bold"), fg_color="#0067C0", hover_color="#005FB8", height=38, command=_guardar).pack(pady=20)


class DialogEditarCurso(ctk.CTkToplevel):
    """Modal para editar una asignatura existente."""

    def __init__(self, parent: ctk.CTkBaseClass, curso: Curso, service: AcademicaService, on_success: Callable[[], None]) -> None:
        super().__init__(parent)
        self.curso = curso
        self.service = service
        self.on_success = on_success

        self.title(f"✏️ Editar Asignatura {curso.codigoCurso}")
        self.geometry("460x520")
        self.grab_set()

        self._crear_interfaz()

    def _crear_interfaz(self) -> None:
        ctk.CTkLabel(self, text=f"Modificar Asignatura: {self.curso.nombre}", font=ctk.CTkFont(size=15, weight="bold")).pack(pady=(15, 10))

        entry_nom = ctk.CTkEntry(self)
        entry_nom.insert(0, self.curso.nombre)
        entry_nom.pack(fill="x", padx=20, pady=6)

        entry_cred = ctk.CTkEntry(self)
        entry_cred.insert(0, str(self.curso.numeroCreditos or 3))
        entry_cred.pack(fill="x", padx=20, pady=6)

        entry_ht = ctk.CTkEntry(self)
        entry_ht.insert(0, str(getattr(self.curso, "horasTeoricas", 3)))
        entry_ht.pack(fill="x", padx=20, pady=6)

        entry_hp = ctk.CTkEntry(self)
        entry_hp.insert(0, str(getattr(self.curso, "horasPracticas", 2)))
        entry_hp.pack(fill="x", padx=20, pady=6)

        entry_nota = ctk.CTkEntry(self)
        entry_nota.insert(0, str(getattr(self.curso, "notaMinimaAprobatoria", Decimal("3.0"))))
        entry_nota.pack(fill="x", padx=20, pady=6)

        def _guardar():
            self.curso.nombre = entry_nom.get().strip() or self.curso.nombre
            if entry_cred.get().strip().isdigit():
                self.curso.numeroCreditos = int(entry_cred.get().strip())
            if entry_ht.get().strip().isdigit():
                self.curso.horasTeoricas = int(entry_ht.get().strip())
            if entry_hp.get().strip().isdigit():
                self.curso.horasPracticas = int(entry_hp.get().strip())
            try:
                self.curso.notaMinimaAprobatoria = Decimal(entry_nota.get().strip())
            except Exception:
                pass

            self.service.controller._recrear_gestores()
            self.destroy()
            self.on_success()

        ctk.CTkButton(self, text="💾 Guardar Cambios", font=ctk.CTkFont(size=12, weight="bold"), fg_color="#10B981", hover_color="#059669", height=36, command=_guardar).pack(pady=20)


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
