"""Diálogos modales para la gestión, edición y eliminación de calificaciones."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Callable
import customtkinter as ctk

from ui_gui.theme import Colors
from dominio.modelo_datos import DetalleMatricula, EstadoCurso

if TYPE_CHECKING:
    from ui_gui.academica.academica_service import AcademicaService


class DialogEditarNota(ctk.CTkToplevel):
    """Modal interactivo para editar o registrar la calificación de un estudiante."""

    def __init__(self, parent: ctk.CTkBaseClass, det: DetalleMatricula, service: AcademicaService, on_success: Callable[[], None]) -> None:
        super().__init__(parent)
        self.det = det
        self.service = service
        self.on_success = on_success

        self.title(f"✏️ Editar Calificación - INS-{det.idDetalleMatricula}")
        self.geometry("450x380")
        self.grab_set()

        self._crear_interfaz()

    def _crear_interfaz(self) -> None:
        mat = next((m for m in self.service.controller.matriculas if m.idMatricula == self.det.idMatricula), None)
        est = next((e for e in self.service.controller.estudiantes if mat and e.idEstudiante == mat.idEstudiante), None)
        pers = next((p for p in self.service.controller.personas if est and p.idPersona == est.idPersona), None)
        oferta = next((o for o in self.service.controller.ofertas if o.idOfertaCurso == self.det.idOfertaCurso), None)
        curso = next((c for c in self.service.controller.cursos if oferta and c.idCurso == oferta.idCurso), None)
        if not curso:
            curso = next((c for c in self.service.controller.cursos if c.idCurso == self.det.idOfertaCurso), None)

        nom_e = f"{pers.primerNombre} {pers.primerApellido}" if pers else "Estudiante"
        cod_e = est.codigoEstudiante if est else ""
        nom_c = curso.nombre if curso else "Curso"
        gr = oferta.grupo if oferta else "01"

        ctk.CTkLabel(self, text="✏️ Modificar Calificación Definitiva", font=ctk.CTkFont(size=16, weight="bold"), text_color=Colors.TEXT_MAIN).pack(pady=(15, 5))
        ctk.CTkLabel(self, text=f"{nom_e} ({cod_e})", font=ctk.CTkFont(size=12, weight="bold"), text_color="#38BDF8").pack(pady=(0, 2))
        ctk.CTkLabel(self, text=f"{nom_c} — Grupo {gr}", font=ctk.CTkFont(size=11), text_color="#94A3B8").pack(pady=(0, 15))

        f_input = ctk.CTkFrame(self, fg_color="transparent")
        f_input.pack(fill="x", padx=30, pady=10)

        ctk.CTkLabel(f_input, text="Nueva Nota Definitiva (0.0 a 5.0):", font=ctk.CTkFont(size=12, weight="bold"), text_color="#F8FAFC").pack(anchor="w", pady=(0, 5))
        entry_val = ctk.CTkEntry(f_input, placeholder_text="ej: 4.0", font=ctk.CTkFont(size=14))
        if self.det.notaFinal is not None:
            entry_val.insert(0, f"{float(self.det.notaFinal):.2f}")
        entry_val.pack(fill="x")

        lbl_error = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=11, weight="bold"), text_color="#EF4444")
        lbl_error.pack(pady=(5, 5))

        def _guardar():
            try:
                val = float(entry_val.get().strip())
                if val < 0.0 or val > 5.0:
                    lbl_error.configure(text="⚠️ La nota debe encontrarse entre 0.0 y 5.0.")
                    return
            except ValueError:
                lbl_error.configure(text="⚠️ Ingrese un valor numérico válido (ej: 3.8).")
                return

            nota_dec = Decimal(str(round(val, 2)))
            self.service.registrar_nota(self.det.idDetalleMatricula, nota_dec)
            self.destroy()
            self.on_success()

        btn_box = ctk.CTkFrame(self, fg_color="transparent")
        btn_box.pack(fill="x", padx=30, pady=15)

        ctk.CTkButton(btn_box, text="💾 Guardar Cambios", font=ctk.CTkFont(size=12, weight="bold"), fg_color="#10B981", hover_color="#059669", height=36, command=_guardar).pack(fill="x", pady=(0, 8))
        ctk.CTkButton(btn_box, text="Cancelar", font=ctk.CTkFont(size=12), fg_color="#334155", hover_color="#475569", height=32, command=self.destroy).pack(fill="x")


class DialogLimpiarNota(ctk.CTkToplevel):
    """Modal de confirmación para restablecer o eliminar una nota a estado pendiente (EN_CURSO)."""

    def __init__(self, parent: ctk.CTkBaseClass, det: DetalleMatricula, service: AcademicaService, on_success: Callable[[], None]) -> None:
        super().__init__(parent)
        self.det = det
        self.service = service
        self.on_success = on_success

        self.title("🗑️ Eliminar Calificación")
        self.geometry("420x290")
        self.grab_set()

        self._crear_interfaz()

    def _crear_interfaz(self) -> None:
        mat = next((m for m in self.service.controller.matriculas if m.idMatricula == self.det.idMatricula), None)
        est = next((e for e in self.service.controller.estudiantes if mat and e.idEstudiante == mat.idEstudiante), None)
        pers = next((p for p in self.service.controller.personas if est and p.idPersona == est.idPersona), None)
        oferta = next((o for o in self.service.controller.ofertas if o.idOfertaCurso == self.det.idOfertaCurso), None)
        curso = next((c for c in self.service.controller.cursos if oferta and c.idCurso == oferta.idCurso), None)
        if not curso:
            curso = next((c for c in self.service.controller.cursos if c.idCurso == self.det.idOfertaCurso), None)

        nom_e = f"{pers.primerNombre} {pers.primerApellido}" if pers else "Estudiante"
        nom_c = curso.nombre if curso else "Curso"

        ctk.CTkLabel(self, text="🗑️ ¿Eliminar Calificación?", font=ctk.CTkFont(size=16, weight="bold"), text_color="#EF4444").pack(pady=(15, 8))
        ctk.CTkLabel(self, text=f"Estudiante: {nom_e}", font=ctk.CTkFont(size=12, weight="bold"), text_color="#F8FAFC").pack(pady=(0, 2))
        ctk.CTkLabel(self, text=f"Asignatura: {nom_c}", font=ctk.CTkFont(size=11), text_color="#38BDF8").pack(pady=(0, 10))

        info_box = ctk.CTkFrame(self, fg_color="#1E293B", corner_radius=6)
        info_box.pack(fill="x", padx=25, pady=5)
        ctk.CTkLabel(
            info_box,
            text="ℹ️ La nota actual será eliminada.\nEl curso volverá a estado 'EN_CURSO' y el\npromedio del estudiante será recalculado.",
            font=ctk.CTkFont(size=11),
            text_color="#94A3B8",
            justify="center",
        ).pack(padx=10, pady=10)

        def _confirmar():
            self.service.limpiar_nota(self.det.idDetalleMatricula)
            self.destroy()
            self.on_success()

        btn_box = ctk.CTkFrame(self, fg_color="transparent")
        btn_box.pack(fill="x", padx=25, pady=15)

        ctk.CTkButton(btn_box, text="🗑️ Sí, Eliminar Calificación", font=ctk.CTkFont(size=12, weight="bold"), fg_color="#EF4444", hover_color="#DC2626", height=34, command=_confirmar).pack(fill="x", pady=(0, 6))
        ctk.CTkButton(btn_box, text="Cancelar", font=ctk.CTkFont(size=12), fg_color="#334155", hover_color="#475569", height=30, command=self.destroy).pack(fill="x")
