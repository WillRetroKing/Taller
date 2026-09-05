"""Paquete de gestión de Personas (Estudiantes, Profesores, Administrativos) para la GUI."""

from __future__ import annotations

from ui_gui.personas.personas_service import PersonasService
from ui_gui.personas.persona_form_card import PersonaFormCard
from ui_gui.personas.personas_tabs import PersonasTabsRenderer

__all__ = ["PersonasService", "PersonaFormCard", "PersonasTabsRenderer"]
