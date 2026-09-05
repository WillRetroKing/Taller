"""Aplicación Principal de Interfaz Gráfica (GUI) para PITA con diseño y paleta de colores de alta fidelidad."""

from __future__ import annotations

import customtkinter as ctk

from ui_gui.gui_controller import PITAController
from ui_gui.view_academica_gui import AcademicaViewGUI
from ui_gui.view_contratos_gui import ContratosViewGUI
from ui_gui.view_dashboard_gui import DashboardViewGUI
from ui_gui.view_facultades_gui import FacultadesViewGUI
from ui_gui.view_nomina_gui import NominaViewGUI
from ui_gui.view_parametros_gui import ParametrosViewGUI
from ui_gui.view_personas_gui import PersonasViewGUI


class PITAApplication(ctk.CTk):
    """Ventana raíz y contenedora de la GUI PITA con estética moderna."""

    def __init__(self, directorio_datos: str = "datos") -> None:
        super().__init__()

        # Configuración de la ventana principal
        self.title("PITA v2.0 - Programa Integrado de Transacciones Académicas | Universidad Popular del Cesar")
        self.geometry("1340x800")
        self.minsize(1100, 700)

        # Configuración del tema visual (Dark Mode Premium Slate & Emerald)
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("green")

        # Inicializar controlador y gestores
        self.controller = PITAController(directorio_datos)

        self._crear_layout_base()
        self._inicializar_vistas()
        self.mostrar_vista("dashboard")

    def _crear_layout_base(self) -> None:
        # Configuración grid principal: Header arriba, Sidebar izquierda, Contenedor derecha
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ------------------------------------------------------------------
        # Header Superior Institucional (Gradiente Visual / Verde Emerald UPC)
        # ------------------------------------------------------------------
        self.header_frame = ctk.CTkFrame(self, height=56, corner_radius=0, fg_color="#064E3B", border_width=0)
        self.header_frame.grid(row=0, column=0, columnspan=2, sticky="ew")

        # Marca / Título
        header_brand = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        header_brand.pack(side="left", padx=20, pady=10)

        ctk.CTkLabel(
            header_brand,
            text="🏛️ UNIVERSIDAD POPULAR DEL CESAR",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#6EE7B7",
        ).pack(anchor="w")

        ctk.CTkLabel(
            header_brand,
            text="PITA • Sistema Integrado de Transacciones Académicas y Nómina Docente",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#FFFFFF",
        ).pack(anchor="w")

        # Indicador de estado de conexión/persistencia
        self.status_pill = ctk.CTkFrame(self.header_frame, fg_color="#022C22", corner_radius=12, border_width=1, border_color="#059669")
        self.status_pill.pack(side="right", padx=20, pady=12)

        self.lbl_status = ctk.CTkLabel(
            self.status_pill,
            text="🟢 Persistencia Conectada (datos/)",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#34D399",
        )
        self.lbl_status.pack(padx=12, pady=4)

        # ------------------------------------------------------------------
        # Sidebar (Navegación Lateral en Slate Oscuro #0F172A)
        # ------------------------------------------------------------------
        self.sidebar_frame = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color="#0F172A", border_width=0)
        self.sidebar_frame.grid(row=1, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(8, weight=1)

        # Menú Secciones
        ctk.CTkLabel(
            self.sidebar_frame,
            text="MENÚ PRINCIPAL",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#64748B",
        ).grid(row=0, column=0, padx=20, pady=(15, 10), sticky="w")

        self.btn_dashboard = self._crear_sidebar_button("📊  Panel de Control", lambda: self.mostrar_vista("dashboard"))
        self.btn_dashboard.grid(row=1, column=0, padx=12, pady=2, sticky="ew")

        self.btn_facultades = self._crear_sidebar_button("🏛️  Facultades & Programas", lambda: self.mostrar_vista("facultades"))
        self.btn_facultades.grid(row=2, column=0, padx=12, pady=2, sticky="ew")

        self.btn_personas = self._crear_sidebar_button("👥  Gestión de Personas", lambda: self.mostrar_vista("personas"))
        self.btn_personas.grid(row=3, column=0, padx=12, pady=2, sticky="ew")

        self.btn_academica = self._crear_sidebar_button("🎓  Académico & EBRA", lambda: self.mostrar_vista("academica"))
        self.btn_academica.grid(row=4, column=0, padx=12, pady=2, sticky="ew")

        self.btn_contratos = self._crear_sidebar_button("📝  Contratación Docente", lambda: self.mostrar_vista("contratos"))
        self.btn_contratos.grid(row=5, column=0, padx=12, pady=2, sticky="ew")

        self.btn_nomina = self._crear_sidebar_button("💰  Nómina & Liquidación", lambda: self.mostrar_vista("nomina"))
        self.btn_nomina.grid(row=6, column=0, padx=12, pady=2, sticky="ew")

        self.btn_parametros = self._crear_sidebar_button("⚙️  Parámetros Legal", lambda: self.mostrar_vista("parametros"))
        self.btn_parametros.grid(row=7, column=0, padx=12, pady=2, sticky="ew")

        # Botón Guardar Rápido en Sidebar
        btn_quick_save = ctk.CTkButton(
            self.sidebar_frame,
            text="💾 Guardar Cambios en Disco",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#10B981",
            hover_color="#059669",
            height=38,
            corner_radius=8,
            command=self._guardar_datos_rapido,
        )
        btn_quick_save.grid(row=8, column=0, padx=15, pady=(5, 10), sticky="ew")

        # Selector de Tema
        combo_tema = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=["Modo Oscuro (Dark Slate)", "Modo Claro (Light)"],
            font=ctk.CTkFont(size=11),
            fg_color="#1E293B",
            button_color="#334155",
            command=self._cambiar_tema,
        )
        combo_tema.grid(row=9, column=0, padx=15, pady=(0, 15), sticky="ew")

        # ------------------------------------------------------------------
        # Contenedor de Vistas Dinámicas (Fondo Slate Obsidian #161E2E)
        # ------------------------------------------------------------------
        self.container_frame = ctk.CTkFrame(self, fg_color="#161E2E", corner_radius=12)
        self.container_frame.grid(row=1, column=1, sticky="nsew", padx=15, pady=15)
        self.container_frame.grid_rowconfigure(0, weight=1)
        self.container_frame.grid_columnconfigure(0, weight=1)

    def _crear_sidebar_button(self, text: str, command) -> ctk.CTkButton:
        return ctk.CTkButton(
            self.sidebar_frame,
            text=text,
            anchor="w",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="transparent",
            text_color="#94A3B8",
            hover_color="#1E293B",
            height=42,
            corner_radius=8,
            command=command,
        )

    def _inicializar_vistas(self) -> None:
        self.vistas = {
            "dashboard": DashboardViewGUI(self.container_frame, self.controller),
            "facultades": FacultadesViewGUI(self.container_frame, self.controller),
            "personas": PersonasViewGUI(self.container_frame, self.controller),
            "academica": AcademicaViewGUI(self.container_frame, self.controller),
            "contratos": ContratosViewGUI(self.container_frame, self.controller),
            "nomina": NominaViewGUI(self.container_frame, self.controller),
            "parametros": ParametrosViewGUI(self.container_frame, self.controller),
        }

        for vista in self.vistas.values():
            vista.grid(row=0, column=0, sticky="nsew")

    def mostrar_vista(self, nombre_vista: str) -> None:
        """Muestra la vista solicitada y oculta las demás."""
        if nombre_vista in self.vistas:
            target = self.vistas[nombre_vista]
            if hasattr(target, "actualizar"):
                target.actualizar()
            target.tkraise()

            # Resaltar botón activo
            btn_map = {
                "dashboard": self.btn_dashboard,
                "facultades": self.btn_facultades,
                "personas": self.btn_personas,
                "academica": self.btn_academica,
                "contratos": self.btn_contratos,
                "nomina": self.btn_nomina,
                "parametros": self.btn_parametros,
            }
            for key, btn in btn_map.items():
                if key == nombre_vista:
                    btn.configure(fg_color="#10B981", text_color="#FFFFFF")
                else:
                    btn.configure(fg_color="transparent", text_color="#94A3B8")

    def _guardar_datos_rapido(self) -> None:
        self.controller.guardar_datos()
        self.lbl_status.configure(text="✅ Persistencia Guardada en 'datos/'")

    def _cambiar_tema(self, seleccion: str) -> None:
        mode = "Dark" if "Oscuro" in seleccion else "Light"
        ctk.set_appearance_mode(mode)
