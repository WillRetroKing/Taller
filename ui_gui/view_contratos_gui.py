"""Vista de Contratación Docente y Factores Salariales (Fachada Orquestadora)."""

from __future__ import annotations

from typing import TYPE_CHECKING
import customtkinter as ctk

from ui_gui.theme import Colors, create_styled_tabview
from ui_gui.contratos.contratos_service import ContratosService
from ui_gui.contratos.contratos_kpis import ContratosKPIs
from ui_gui.contratos.contratos_tabs import ContratosTabsRenderer
from ui_gui.contratos.dialog_nuevo_contrato import DialogNuevoContrato
from ui_gui.contratos.dialog_reconocer_puntos import DialogReconocerPuntos
from ui_gui.contratos.dialog_contrato_acciones import (
    DialogDetalleContrato,
    DialogEditarContrato,
    DialogTerminarContrato,
)

if TYPE_CHECKING:
    from ui_gui.gui_controller import PITAController
    from dominio.modelo_datos import Contrato


class ContratosViewGUI(ctk.CTkFrame):
    """Vista de gestión integral de vinculación docente, contratos y factores salariales."""

    def __init__(self, parent: ctk.CTk, controller: PITAController) -> None:
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.service = ContratosService(controller)
        self.kpis = ContratosKPIs(controller, self.service)

        self.tabs_renderer = ContratosTabsRenderer(
            controller=self.controller,
            service=self.service,
            on_ver_contrato=self._abrir_modal_detalle_contrato,
            on_editar_contrato=self._abrir_modal_editar_contrato,
            on_terminar_contrato=self._abrir_modal_terminar_contrato,
        )

        self._crear_interfaz()

    def _crear_interfaz(self) -> None:
        # Cabecera principal
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=14, pady=(0, 10))

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left")

        ctk.CTkLabel(
            title_box,
            text="📝 Gestión de Contratación y Factores Salariales",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=Colors.TEXT_MAIN,
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_box,
            text="Régimen de Carrera (Dec. 1279/2002) y Profesores Transitorios (Acuerdo 027/2024)",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=Colors.TEXT_MUTED,
        ).pack(anchor="w")

        h_buttons = ctk.CTkFrame(header, fg_color="transparent")
        h_buttons.pack(side="right")

        btn_nuevo_contrato = ctk.CTkButton(
            h_buttons,
            text="➕ Registrar Contrato Docente",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=Colors.WIN_BLUE,
            hover_color=Colors.WIN_BLUE_HOVER,
            corner_radius=8,
            height=36,
            command=self._abrir_modal_nuevo_contrato,
        )
        btn_nuevo_contrato.pack(side="left", padx=5)

        btn_reconocer_puntos = ctk.CTkButton(
            h_buttons,
            text="⭐ Reconocer Puntos / Productividad",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#006837",
            hover_color="#004D28",
            corner_radius=8,
            height=36,
            command=self._abrir_modal_reconocer_puntos,
        )
        btn_reconocer_puntos.pack(side="left", padx=5)

        # Barra de KPIs Ejecutivos
        self.kpi_container = ctk.CTkFrame(self, fg_color="transparent")
        self.kpi_container.pack(fill="x", padx=14, pady=(0, 10))
        self.kpis.renderizar(self.kpi_container)

        # Tabview principal
        self.tabview = create_styled_tabview(self)
        self.tabview.pack(fill="both", expand=True, padx=14, pady=5)

        self.tab_contratos = self.tabview.add("📜 Contratos Docentes Vigentes")
        self.tab_factores = self.tabview.add("⭐ Factores Salariales y Escalafón (Dec. 1279)")

        self.actualizar()

    def actualizar(self) -> None:
        self.kpis.renderizar(self.kpi_container)
        self.tabs_renderer.llenar_tab_contratos(self.tab_contratos)
        self.tabs_renderer.llenar_tab_factores(self.tab_factores)

    # -------------------------------------------------------------------------
    # MODALES
    # -------------------------------------------------------------------------
    def _abrir_modal_nuevo_contrato(self) -> None:
        DialogNuevoContrato(self, self.controller, self.service, self.actualizar)

    def _abrir_modal_reconocer_puntos(self) -> None:
        DialogReconocerPuntos(self, self.controller, self.service, self.actualizar)

    def _abrir_modal_detalle_contrato(self, contrato: Contrato) -> None:
        DialogDetalleContrato(self, contrato, self.controller, self.service)

    def _abrir_modal_editar_contrato(self, contrato: Contrato) -> None:
        DialogEditarContrato(self, contrato, self.controller, self.service, self.actualizar)

    def _abrir_modal_terminar_contrato(self, contrato: Contrato) -> None:
        DialogTerminarContrato(self, contrato, self.controller, self.service, self.actualizar)
