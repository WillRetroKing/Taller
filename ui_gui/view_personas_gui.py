"""Vista de Gestión de Personas (Estudiantes, Profesores, Administrativos) para la GUI con tablas y badges estilizados."""

from __future__ import annotations

from typing import TYPE_CHECKING
import customtkinter as ctk

from ui_gui.theme import Colors, create_styled_tabview
from ui_gui.personas.personas_service import PersonasService
from ui_gui.personas.personas_tabs import PersonasTabsRenderer
from ui_gui.personas.dialog_detalle_persona import DialogDetallePersona
from ui_gui.personas.dialog_nueva_persona import DialogNuevaPersona
from ui_gui.personas.dialog_editar_persona import (
    DialogEditarEstudiante,
    DialogEditarProfesor,
    DialogEditarAdministrativo,
)

if TYPE_CHECKING:
    from ui_gui.gui_controller import PITAController
    from dominio.modelo_datos import Persona, Estudiante, Profesor, Administrativo


class PersonasViewGUI(ctk.CTkFrame):
    """Vista completa de gestión de Personas con tablas y badges estilizados."""

    def __init__(self, parent: ctk.CTk, controller: PITAController) -> None:
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.service = PersonasService(controller)
        self.busqueda_var = ctk.StringVar(value="")

        self.tabs_renderer = PersonasTabsRenderer(
            controller=self.controller,
            on_ver_persona=self._ver_detalle_persona,
            on_editar_estudiante=self._editar_estudiante,
            on_desactivar_estudiante=self._desactivar_estudiante,
            on_editar_profesor=self._editar_profesor,
            on_desactivar_profesor=self._desactivar_profesor,
            on_editar_administrativo=self._editar_administrativo,
            on_desactivar_administrativo=self._desactivar_administrativo,
        )

        self._crear_interfaz()

    def _crear_interfaz(self) -> None:
        # Header y Búsqueda
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 10))

        ctk.CTkLabel(
            header,
            text="👥 Gestión de Personas e Identificación",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=Colors.TEXT_MAIN,
        ).pack(side="left")

        btn_nueva = ctk.CTkButton(
            header,
            text="➕ Registrar Persona / Asignar Rol",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#0067C0",
            hover_color="#005FB8",
            height=36,
            corner_radius=8,
            command=self._abrir_modal_nueva_persona,
        )
        btn_nueva.pack(side="right")

        # Barra de Búsqueda (Estilo Clean Light Windows 11)
        search_frame = ctk.CTkFrame(
            self,
            fg_color=Colors.BG_CARD,
            corner_radius=8,
            border_width=1,
            border_color=Colors.BORDER_SUBTLE,
        )
        search_frame.pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkLabel(
            search_frame,
            text="🔍 Buscar Persona:",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=Colors.TEXT_MUTED,
        ).pack(side="left", padx=12, pady=10)

        entry_search = ctk.CTkEntry(
            search_frame,
            textvariable=self.busqueda_var,
            placeholder_text="Filtrar por documento, nombre o código...",
            width=320,
            fg_color=Colors.BG_WINDOW,
            border_color=Colors.BORDER_SUBTLE,
            text_color=Colors.TEXT_MAIN,
        )
        entry_search.pack(side="left", padx=5, pady=10)
        entry_search.bind("<KeyRelease>", lambda e: self.actualizar_tablas())

        btn_clear = ctk.CTkButton(
            search_frame,
            text="Limpiar",
            width=80,
            fg_color="#E2E8F0",
            hover_color="#CBD5E1",
            text_color=Colors.TEXT_MAIN,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            command=self._limpiar_busqueda,
        )
        btn_clear.pack(side="left", padx=5, pady=10)

        # Pestañas
        self.tabview = create_styled_tabview(self)
        self.tabview.pack(fill="both", expand=True, padx=15, pady=5)

        self.tab_estudiantes = self.tabview.add("👨‍🎓 Estudiantes")
        self.tab_profesores = self.tabview.add("👨‍🏫 Profesores")
        self.tab_administrativos = self.tabview.add("👔 Administrativos")

        self.actualizar_tablas()

    def _limpiar_busqueda(self) -> None:
        self.busqueda_var.set("")
        self.actualizar_tablas()

    def actualizar_tablas(self) -> None:
        q = self.busqueda_var.get().strip().lower()
        self.tabs_renderer.llenar_estudiantes(self.tab_estudiantes, q)
        self.tabs_renderer.llenar_profesores(self.tab_profesores, q)
        self.tabs_renderer.llenar_administrativos(self.tab_administrativos, q)

    def actualizar(self) -> None:
        self.actualizar_tablas()

    # ------------------------------------------------------------------
    # MODALES Y ACCIONES
    # ------------------------------------------------------------------
    def _abrir_modal_nueva_persona(self) -> None:
        DialogNuevaPersona(self, self.controller, self.service, self.actualizar)

    def _ver_detalle_persona(self, persona: Persona | None) -> None:
        if persona:
            DialogDetallePersona(self, persona, self.controller)

    def _editar_estudiante(self, est: Estudiante, pers: Persona | None) -> None:
        DialogEditarEstudiante(self, est, pers, self.controller, self.service, self.actualizar_tablas)

    def _desactivar_estudiante(self, id_estudiante: int) -> None:
        self.service.desactivar_estudiante(id_estudiante)
        self.actualizar_tablas()

    def _editar_profesor(self, prof: Profesor, pers: Persona | None) -> None:
        DialogEditarProfesor(self, prof, pers, self.controller, self.service, self.actualizar_tablas)

    def _desactivar_profesor(self, id_profesor: int) -> None:
        self.service.desactivar_profesor(id_profesor)
        self.actualizar_tablas()

    def _editar_administrativo(self, adm: Administrativo, pers: Persona | None) -> None:
        DialogEditarAdministrativo(self, adm, pers, self.controller, self.service, self.actualizar_tablas)

    def _desactivar_administrativo(self, id_administrativo: int) -> None:
        self.service.desactivar_administrativo(id_administrativo)
        self.actualizar_tablas()
