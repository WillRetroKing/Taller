"""Paquete de gestión de Contratación Docente y Factores Salariales."""

from __future__ import annotations

from ui_gui.contratos.contratos_service import ContratosService
from ui_gui.contratos.contratos_kpis import ContratosKPIs
from ui_gui.contratos.contratos_tabs import ContratosTabsRenderer

__all__ = ["ContratosService", "ContratosKPIs", "ContratosTabsRenderer"]
