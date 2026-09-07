"""Componente de barra de KPIs ejecutivos para la vista de Contratación Docente."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING
import customtkinter as ctk

from ui_gui.theme import Colors
from ui_gui.components import create_stat_card

if TYPE_CHECKING:
    from ui_gui.gui_controller import PITAController
    from ui_gui.contratos.contratos_service import ContratosService


class ContratosKPIs:
    """Calcula y dibuja los 4 indicadores KPI superiores."""

    def __init__(self, controller: PITAController, service: ContratosService) -> None:
        self.controller = controller
        self.service = service

    def renderizar(self, container: ctk.CTkFrame) -> None:
        for w in container.winfo_children():
            w.destroy()

        container.columnconfigure((0, 1, 2, 3), weight=1)

        contratos = self.controller.contratos
        activos = [c for c in contratos if str(getattr(c, "estado", "ACTIVO")).upper() == "ACTIVO"]
        total_activos = len(activos)

        # Distribución de personal
        admin_count = sum(1 for c in activos if ("ADMIN" in str(getattr(c, "tipoContrato", "")).upper() or getattr(c, "regimenAplicable", "") == "CST_LEY100_ADMINISTRATIVO" or self.service.buscar_administrativo_por_id_persona(c.idPersona) is not None))
        docente_count = total_activos - admin_count
        planta = sum(1 for c in activos if "PLANTA" in str(getattr(c, "modalidadProfesor", "") or getattr(c, "tipoContrato", "")).upper() and self.service.buscar_administrativo_por_id_persona(c.idPersona) is None)
        transitorios = docente_count - planta

        # Total de puntos salariales reconocidos
        profesores = self.controller.profesores
        total_puntos = sum(
            Decimal(str(getattr(p, "puntosSalariales", "0") or "0"))
            for p in profesores
        )

        val_punto = self.service.obtener_parametro_decimal("VALOR_PUNTO_SALARIAL", Decimal("19850"))

        # Presupuesto mensual estimado
        total_nomina = sum(
            Decimal(str(getattr(c, "salarioBase", "0") or getattr(c, "salarioMensualPactado", "0") or "0"))
            for c in activos
        )

        create_stat_card(
            container,
            row=0,
            col=0,
            title="CONTRATOS ACTIVOS",
            value=f"{total_activos} Activos",
            accent_color=Colors.WIN_BLUE,
            subtitle=f"{len(contratos)} vinculaciones totales",
        )

        create_stat_card(
            container,
            row=0,
            col=1,
            title="DISTRIBUCIÓN PERSONAL",
            value=f"{docente_count} Docentes | {admin_count} Adm.",
            accent_color="#8B5CF6",
            subtitle=f"{planta} Planta Doc. · {transitorios} Trans. Doc.",
        )

        create_stat_card(
            container,
            row=0,
            col=2,
            title="PUNTOS SALARIALES TOTALES",
            value=f"{int(total_puntos):,} Pts",
            accent_color="#F59E0B",
            subtitle=f"Valor punto: ${int(val_punto):,} COP",
        )

        create_stat_card(
            container,
            row=0,
            col=3,
            title="MASA SALARIAL MENSUAL",
            value=f"$ {int(total_nomina):,} COP",
            accent_color="#10B981",
            subtitle="Asignación básica consolidada",
        )
