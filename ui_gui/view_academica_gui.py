"""Vista de Gestión Académica (Cursos, Ofertas, Matrículas, Calificaciones y Alertas EBRA).

Fachada principal desacoplada que delega responsabilidades a:
- ui_gui.academica.academica_service: Lógica de negocio, matrículas, promedios y EBRA.
- ui_gui.academica.academica_tabs: Componentes de presentación para cada pestaña.
- ui_gui.academica.dialogs_cursos_ofertas: Diálogos para asignaturas y ofertas.
- ui_gui.academica.dialogs_notas: Diálogos para edición y eliminación de calificaciones.
"""

from __future__ import annotations

import customtkinter as ctk
from typing import TYPE_CHECKING

from ui_gui.theme import Colors, create_styled_tabview
from ui_gui.components import clean_enum
from ui_gui.academica.academica_service import AcademicaService
from ui_gui.academica.academica_tabs import AcademicaTabs
from ui_gui.academica.dialogs_cursos_ofertas import (
    DialogNuevoCurso,
    DialogEditarCurso,
    DialogNuevaOferta,
)
from ui_gui.academica.dialogs_notas import (
    DialogEditarNota,
    DialogLimpiarNota,
)
from ui_gui.academica.dialogs_planes_periodos import (
    DialogNuevoPeriodo,
    DialogEditarPeriodo,
    DialogNuevoPlanEstudio,
    DialogMallaCurricular,
)

if TYPE_CHECKING:
    from ui_gui.gui_controller import PITAController
    from dominio.modelo_datos import Curso, DetalleMatricula, PeriodoAcademico, PlanEstudio


class AcademicaViewGUI(ctk.CTkFrame):
    """Vista académica completa: Períodos, Planes de Estudio, Cursos, Ofertas, Matrículas, Notas y Alertas EBRA."""

    def __init__(self, parent: ctk.CTk, controller: PITAController) -> None:
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.service = AcademicaService(controller)

        self._crear_interfaz()

    def _crear_interfaz(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(
            header,
            text="🎓 Gestión Académica, Matrícula y Alertas EBRA",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=Colors.TEXT_MAIN,
        ).pack(side="left")

        btn_box = ctk.CTkFrame(header, fg_color="transparent")
        btn_box.pack(side="right")

        btn_nueva_oferta = ctk.CTkButton(
            btn_box,
            text="🏫 Abrir Oferta / Grupo",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#059669",
            hover_color="#047857",
            corner_radius=8,
            command=self._abrir_modal_nueva_oferta,
        )
        btn_nueva_oferta.pack(side="right", padx=(6, 0))

        btn_nuevo_curso = ctk.CTkButton(
            btn_box,
            text="➕ Crear Asignatura",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#0067C0",
            hover_color="#005FB8",
            corner_radius=8,
            command=self._abrir_modal_nuevo_curso,
        )
        btn_nuevo_curso.pack(side="right", padx=(6, 0))

        btn_nuevo_plan = ctk.CTkButton(
            btn_box,
            text="📋 + Nuevo Plan",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            corner_radius=8,
            command=self._abrir_modal_nuevo_plan,
        )
        btn_nuevo_plan.pack(side="right", padx=(6, 0))

        btn_nuevo_periodo = ctk.CTkButton(
            btn_box,
            text="📅 + Aperturar Período",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#7C3AED",
            hover_color="#6D28D9",
            corner_radius=8,
            command=self._abrir_modal_nuevo_periodo,
        )
        btn_nuevo_periodo.pack(side="right")

        # Pestañas Principales
        self.tabview = create_styled_tabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=5)

        self.tab_periodos = self.tabview.add("📅 Períodos Académicos")
        self.tab_planes = self.tabview.add("📋 Planes de Estudio")
        self.tab_oferta = self.tabview.add("📚 Cursos & Ofertas")
        self.tab_matricula = self.tabview.add("✍️ Matrícula de Cursos")
        self.tab_evaluaciones = self.tabview.add("📝 Evaluaciones y Notas")
        self.tab_ebra = self.tabview.add("⚠️ Informe Alertas EBRA")

        self._llenar_tab_periodos()
        self._llenar_tab_planes()
        self._llenar_tab_oferta()
        self._llenar_tab_matricula()
        self._llenar_tab_evaluaciones()
        self._llenar_tab_ebra()

    # ------------------------------------------------------------------
    # LLENADO DE PESTAÑAS (DELEGACIÓN MODULAR)
    # ------------------------------------------------------------------
    def _llenar_tab_periodos(self) -> None:
        AcademicaTabs.render_tab_periodos(
            self.tab_periodos,
            self.controller,
            on_aperturar_periodo=self._abrir_modal_nuevo_periodo,
            on_editar_periodo=self._editar_periodo,
            on_cambiar_estado_periodo=self._cambiar_estado_periodo,
            on_apertura_rapida_2026_1=self._apertura_rapida_2026_1,
        )

    def _llenar_tab_planes(self) -> None:
        AcademicaTabs.render_tab_planes(
            self.tab_planes,
            self.controller,
            on_nuevo_plan=self._abrir_modal_nuevo_plan,
            on_ver_malla=self._ver_malla_plan,
            on_cambiar_estado_plan=self._cambiar_estado_plan,
        )

    def _llenar_tab_oferta(self) -> None:
        AcademicaTabs.render_tab_oferta(
            self.tab_oferta,
            self.controller,
            on_editar_curso=self._editar_curso,
            on_eliminar_curso=self._eliminar_curso,
            on_eliminar_oferta=self._eliminar_oferta,
        )

    def _llenar_tab_matricula(self) -> None:
        AcademicaTabs.render_tab_matricula(
            self.tab_matricula,
            self.controller,
            self.service,
            on_refresh=self.actualizar,
            on_cancelar_curso=self._cancelar_curso_estudiante,
        )

    def _llenar_tab_evaluaciones(self) -> None:
        AcademicaTabs.render_tab_evaluaciones(
            self.tab_evaluaciones,
            self.controller,
            self.service,
            on_refresh=self.actualizar,
            on_editar_nota=self._abrir_modal_editar_nota,
            on_limpiar_nota=self._limpiar_nota,
        )

    def _llenar_tab_ebra(self) -> None:
        AcademicaTabs.render_tab_ebra(
            self.tab_ebra,
            self.controller,
            self.service,
        )

    # ------------------------------------------------------------------
    # MODALES Y ACCIONES (RETROCOMPATIBILIDAD TOTAL)
    # ------------------------------------------------------------------
    def _abrir_modal_nuevo_periodo(self) -> None:
        DialogNuevoPeriodo(self, self.service, on_success=self.actualizar)

    def _editar_periodo(self, periodo: PeriodoAcademico) -> None:
        DialogEditarPeriodo(self, self.service, periodo, on_success=self.actualizar)

    def _cambiar_estado_periodo(self, periodo: PeriodoAcademico) -> None:
        nuevo = "CERRADO" if clean_enum(getattr(periodo, "estado", "")) == "ABIERTO" else "ABIERTO"
        periodo.estado = nuevo
        self.controller.guardar_datos()
        self.actualizar()

    def _apertura_rapida_2026_1(self) -> None:
        from datetime import date
        from dominio.modelo_datos import PeriodoAcademico
        nuevo_id = max((p.idPeriodo or 0 for p in self.controller.periodos_academicos), default=0) + 1
        per = PeriodoAcademico(
            idPeriodo=nuevo_id,
            codigo="2026-1",
            nombre="Primer Período Académico 2026",
            anio=2026,
            numeroPeriodo=1,
            fechaInicio=date(2026, 2, 1),
            fechaFin=date(2026, 6, 30),
            fechaInicioMatricula=date(2026, 1, 15),
            fechaFinMatricula=date(2026, 2, 10),
            fechaLimiteCancelacion=date(2026, 4, 15),
            estado="ABIERTO",
        )
        self.controller.periodos_academicos.append(per)
        self.controller.guardar_datos()
        self.actualizar()

    def _abrir_modal_nuevo_plan(self) -> None:
        DialogNuevoPlanEstudio(self, self.service, on_success=self.actualizar)

    def _ver_malla_plan(self, plan: PlanEstudio) -> None:
        DialogMallaCurricular(self, self.service, plan, on_success=self.actualizar)

    def _cambiar_estado_plan(self, plan: PlanEstudio) -> None:
        nuevo = "INACTIVO" if clean_enum(getattr(plan, "estado", "")) == "ACTIVO" else "ACTIVO"
        plan.estado = nuevo
        self.controller.guardar_datos()
        self.actualizar()

    def _abrir_modal_nuevo_curso(self) -> None:
        DialogNuevoCurso(self, self.service, on_success=self.actualizar)

    def _editar_curso(self, curso: Curso) -> None:
        DialogEditarCurso(self, curso, self.service, on_success=self.actualizar)

    def _eliminar_curso(self, id_curso: int) -> None:
        self.service.eliminar_curso(id_curso)
        self.actualizar()

    def _abrir_modal_nueva_oferta(self) -> None:
        DialogNuevaOferta(self, self.controller, self.service, on_success=self.actualizar)

    def _eliminar_oferta(self, id_oferta: int) -> None:
        self.service.eliminar_oferta(id_oferta)
        self.actualizar()

    def _cancelar_curso_estudiante(self, id_detalle: int) -> None:
        self.service.cancelar_curso_estudiante(id_detalle)
        self.actualizar()

    def _abrir_modal_editar_nota(self, det: DetalleMatricula) -> None:
        DialogEditarNota(self, det, self.service, on_success=self.actualizar)

    def _limpiar_nota(self, det: DetalleMatricula) -> None:
        DialogLimpiarNota(self, det, self.service, on_success=self.actualizar)

    def _actualizar_promedio_estudiante(self, id_estudiante: int) -> None:
        self.service.actualizar_promedio_estudiante(id_estudiante)

    def actualizar(self) -> None:
        """Refresca toda la vista académica reconstruyendo los elementos."""
        for widget in self.winfo_children():
            widget.destroy()
        self._crear_interfaz()
