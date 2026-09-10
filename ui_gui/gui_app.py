"""Aplicación Principal de Interfaz Gráfica (GUI) para PITA con diseño Clean Windows 11 Light UI."""

from __future__ import annotations

import customtkinter as ctk

from ui_gui.gui_controller import PITAController
from ui_gui.theme import Colors, Fonts, aplicar_configuracion_tema
from ui_gui.view_academica_gui import AcademicaViewGUI
from ui_gui.view_contratos_gui import ContratosViewGUI
from ui_gui.view_dashboard_gui import DashboardViewGUI
from ui_gui.view_facultades_gui import FacultadesViewGUI
from ui_gui.view_nomina_gui import NominaViewGUI
from ui_gui.view_parametros_gui import ParametrosViewGUI
from ui_gui.view_personas_gui import PersonasViewGUI


class PITAApplication(ctk.CTk):
    """Ventana raíz y contenedora de la GUI PITA con estética Clean Windows 11 Light UI."""

    def __init__(self, directorio_datos: str = "datos") -> None:
        super().__init__()

        # Configuración de la ventana principal
        self.title("PITA v2.0 - Programa Integrado de Transacciones Académicas | Universidad Popular del Cesar")
        self.geometry("1360x820")
        self.minsize(1100, 700)

        # Configuración global del tema visual (Light Clean Por Defecto)
        aplicar_configuracion_tema()

        # Inicializar controlador y gestores
        self.controller = PITAController(directorio_datos)
        self.vista_actual = "dashboard"

        self._crear_layout_base()
        self._inicializar_vistas()
        self.mostrar_vista("dashboard")

        # Comprobar si la persistencia está vacía para preguntar al usuario (Requerimiento #59 Taller PITA)
        self.after(300, self._comprobar_datos_iniciales)

    def _crear_layout_base(self) -> None:
        # Configuración grid principal: Header arriba, Sidebar izquierda, Contenedor derecha
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ------------------------------------------------------------------
        # Header Superior Institucional (Estilo Clean Windows 11 Light App Bar)
        # ------------------------------------------------------------------
        self.header_frame = ctk.CTkFrame(
            self,
            height=56,
            corner_radius=0,
            fg_color=Colors.BG_HEADER,
            border_width=1,
            border_color=Colors.BORDER_SUBTLE,
        )
        self.header_frame.grid(row=0, column=0, columnspan=2, sticky="ew")

        # Marca / Título
        header_brand = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        header_brand.pack(side="left", padx=20, pady=10)

        nombre_univ_act = (
            self.controller.universidad_activa.nombre.upper()
            if self.controller.universidad_activa and self.controller.universidad_activa.nombre
            else "SISTEMA MULTI-UNIVERSITARIO"
        )
        self.lbl_univ = ctk.CTkLabel(
            header_brand,
            text=f"🏛️ {nombre_univ_act}",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=Colors.TEXT_ACCENT,
        )
        self.lbl_univ.pack(anchor="w")

        ctk.CTkLabel(
            header_brand,
            text="PITA • Sistema Integrado de Transacciones Académicas y Nómina Docente",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=Colors.TEXT_MAIN,
        ).pack(anchor="w")

        # Indicador de estado de conexión/persistencia
        self.status_pill = ctk.CTkFrame(
            self.header_frame,
            fg_color="#F1F5F9",
            corner_radius=12,
            border_width=1,
            border_color=Colors.BORDER_SUBTLE,
        )
        self.status_pill.pack(side="right", padx=20, pady=12)

        self.lbl_status = ctk.CTkLabel(
            self.status_pill,
            text="🟢 Persistencia Conectada (datos/)",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=Colors.BADGE_ACTIVE_TXT,
        )
        self.lbl_status.pack(padx=12, pady=4)

        # Selector de Universidad Activa (Multi-Tenancy por Directorio)
        nombres_univ = (
            [t.nombre for t in self.controller.tenants if t.nombre]
            if getattr(self.controller, "tenants", None)
            else ([u.nombre for u in self.controller.universidades if u.nombre] or ["Universidad Popular del Cesar"])
        )
        val_inicial = (
            self.controller.tenant_activo.nombre
            if getattr(self.controller, "tenant_activo", None)
            else (self.controller.universidad_activa.nombre if self.controller.universidad_activa else nombres_univ[0])
        )
        self.selector_univ = ctk.CTkOptionMenu(
            self.header_frame,
            values=nombres_univ,
            command=self._on_cambiar_universidad,
            width=260,
            height=30,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            fg_color="#F8FAFC",
            button_color=Colors.ACCENT_PRIMARY,
            text_color=Colors.TEXT_MAIN,
        )
        self.selector_univ.set(val_inicial)
        self.selector_univ.pack(side="right", padx=(6, 10), pady=12)

        self.btn_nueva_univ = ctk.CTkButton(
            self.header_frame,
            text="➕ Nueva Univ.",
            command=self._abrir_modal_nueva_universidad,
            width=110,
            height=30,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=Colors.BG_CARD,
            hover_color=Colors.BORDER_SUBTLE,
            text_color=Colors.ACCENT_PRIMARY,
            border_width=1,
            border_color=Colors.BORDER_SUBTLE,
        )
        self.btn_nueva_univ.pack(side="right", padx=(0, 6), pady=12)

        # ------------------------------------------------------------------
        # Sidebar (Navegación Lateral Estilo Windows 11 NavigationRail Limpio)
        # ------------------------------------------------------------------
        self.sidebar_frame = ctk.CTkFrame(
            self,
            width=240,
            corner_radius=0,
            fg_color=Colors.BG_SIDEBAR,
            border_width=1,
            border_color=Colors.BORDER_SUBTLE,
        )
        self.sidebar_frame.grid(row=1, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(14, weight=1)

        # Menú Secciones
        ctk.CTkLabel(
            self.sidebar_frame,
            text="NAVEGACIÓN",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=Colors.TEXT_MUTED,
        ).grid(row=0, column=0, padx=20, pady=(15, 6), sticky="w")

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

        # Separador / Gestión de Datos (Requerimiento #59 Taller PITA)
        ctk.CTkLabel(
            self.sidebar_frame,
            text="CONTROL DE DATOS (#59)",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=Colors.TEXT_MUTED,
        ).grid(row=8, column=0, padx=20, pady=(15, 6), sticky="w")

        btn_demo = ctk.CTkButton(
            self.sidebar_frame,
            text="🌱 Cargar Datos Demo",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color="#10B981",
            hover_color="#059669",
            text_color="#FFFFFF",
            height=32,
            corner_radius=8,
            command=self._cargar_demo_accion,
        )
        btn_demo.grid(row=9, column=0, padx=12, pady=3, sticky="ew")

        btn_sin_datos = ctk.CTkButton(
            self.sidebar_frame,
            text="🧹 Iniciar Sin Datos",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color="#64748B",
            hover_color="#475569",
            text_color="#FFFFFF",
            height=32,
            corner_radius=8,
            command=self._confirmar_iniciar_sin_datos,
        )
        btn_sin_datos.grid(row=10, column=0, padx=12, pady=3, sticky="ew")

        # Botón Guardar Rápido en Sidebar
        btn_quick_save = ctk.CTkButton(
            self.sidebar_frame,
            text="💾 Guardar Cambios",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=Colors.WIN_BLUE,
            hover_color=Colors.WIN_BLUE_HOVER,
            text_color="#FFFFFF",
            height=36,
            corner_radius=8,
            command=self._guardar_datos_rapido,
        )
        btn_quick_save.grid(row=11, column=0, padx=12, pady=(10, 6), sticky="ew")

        # Selector de Tema
        combo_tema = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=["Modo Claro (Windows Light)", "Modo Oscuro (Windows Dark)"],
            font=ctk.CTkFont(family="Segoe UI", size=11),
            fg_color=Colors.BG_CARD,
            button_color=Colors.BORDER_SUBTLE,
            text_color=Colors.TEXT_MAIN,
            command=self._cambiar_tema,
        )
        combo_tema.grid(row=12, column=0, padx=12, pady=(4, 15), sticky="ew")

        # ------------------------------------------------------------------
        # Contenedor de Vistas Dinámicas
        # ------------------------------------------------------------------
        self.container_frame = ctk.CTkFrame(self, fg_color=Colors.BG_WINDOW, corner_radius=12)
        self.container_frame.grid(row=1, column=1, sticky="nsew", padx=15, pady=15)
        self.container_frame.grid_rowconfigure(0, weight=1)
        self.container_frame.grid_columnconfigure(0, weight=1)

    def _crear_sidebar_button(self, text: str, command) -> ctk.CTkButton:
        return ctk.CTkButton(
            self.sidebar_frame,
            text=text,
            anchor="w",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color="transparent",
            text_color=Colors.TEXT_MUTED,
            hover_color="#E2E8F0",
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
            self.vista_actual = nombre_vista
            target = self.vistas[nombre_vista]
            if hasattr(target, "actualizar"):
                target.actualizar()
            target.tkraise()

            # Resaltar botón activo con el azul Accent de Windows 11
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
                    btn.configure(fg_color=Colors.WIN_BLUE, text_color="#FFFFFF")
                else:
                    btn.configure(fg_color="transparent", text_color=Colors.TEXT_MUTED)

    def _guardar_datos_rapido(self) -> None:
        self.controller.guardar_datos()
        self.lbl_status.configure(text="✅ Persistencia Guardada en 'datos/'")

    def _cambiar_tema(self, seleccion: str) -> None:
        mode = "Dark" if "Oscuro" in seleccion else "Light"
        ctk.set_appearance_mode(mode)

    def _on_cambiar_universidad(self, nombre_seleccionado: str) -> None:
        if self.controller.seleccionar_universidad(nombre_seleccionado):
            univ = self.controller.universidad_activa
            nom = univ.nombre if univ and univ.nombre else nombre_seleccionado
            if hasattr(self, "lbl_univ"):
                self.lbl_univ.configure(text=f"🏛️ {nom.upper()}")
            if hasattr(self, "lbl_status") and hasattr(self.controller, "directorio_datos"):
                dir_label = self.controller.directorio_datos.name
                self.lbl_status.configure(text=f"🟢 Conectado: datos/{dir_label}/")
            self.title(f"PITA v2.0 - Programa Integrado de Transacciones Académicas | {nom}")
            if hasattr(self, "vista_actual") and self.vista_actual in self.vistas:
                self.mostrar_vista(self.vista_actual)

    def _abrir_modal_nueva_universidad(self) -> None:
        """Modal para registrar una nueva universidad con código único institucional y almacenamiento aislado."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("🏛️ Registrar Nueva Universidad - PITA v2.0")
        dialog.geometry("540x560")
        dialog.resizable(False, False)
        dialog.grab_set()

        card = ctk.CTkFrame(dialog, fg_color=Colors.BG_CARD, corner_radius=12, border_width=1, border_color=Colors.BORDER_SUBTLE)
        card.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            card,
            text="🏛️ Registrar Nueva Universidad",
            font=ctk.CTkFont(family="Segoe UI", size=17, weight="bold"),
            text_color=Colors.TEXT_MAIN,
        ).pack(pady=(15, 2))

        ctk.CTkLabel(
            card,
            text="Se creará un espacio de datos aislado con código único institucional.",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=Colors.TEXT_MUTED,
        ).pack(pady=(0, 15))

        # Formulario
        form_frame = ctk.CTkFrame(card, fg_color="transparent")
        form_frame.pack(fill="x", padx=25)

        # 1. Nombre Institucional
        ctk.CTkLabel(form_frame, text="Nombre Institución *", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=Colors.TEXT_MAIN).grid(row=0, column=0, sticky="w", pady=(4, 2))
        entry_nombre = ctk.CTkEntry(form_frame, placeholder_text="ej: Universidad de Antioquia", width=420)
        entry_nombre.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 8))

        # 2. Código Único + Botón Sugerir
        ctk.CTkLabel(form_frame, text="Código Único Institucional *", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=Colors.TEXT_MAIN).grid(row=2, column=0, sticky="w", pady=(4, 2))
        code_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        code_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        entry_codigo = ctk.CTkEntry(code_frame, placeholder_text="ej: UDEA", width=290)
        entry_codigo.pack(side="left", fill="x", expand=True, padx=(0, 8))

        def _auto_sugerir():
            nom = entry_nombre.get().strip()
            if nom and hasattr(self.controller, "gestor_multi_tenancy"):
                sug = self.controller.gestor_multi_tenancy.generar_codigo_sugerido(nom)
                entry_codigo.delete(0, "end")
                entry_codigo.insert(0, sug)

        btn_sugerir = ctk.CTkButton(
            code_frame,
            text="✨ Sugerir Código",
            width=120,
            command=_auto_sugerir,
            fg_color=Colors.BG_SIDEBAR,
            hover_color=Colors.BORDER_SUBTLE,
            text_color=Colors.TEXT_MAIN,
            border_width=1,
            border_color=Colors.BORDER_SUBTLE,
        )
        btn_sugerir.pack(side="right")

        def _on_nombre_key(event):
            if not entry_codigo.get().strip():
                _auto_sugerir()
        entry_nombre.bind("<KeyRelease>", _on_nombre_key)

        # 3. NIT y Ciudad
        row_nit_ciu = ctk.CTkFrame(form_frame, fg_color="transparent")
        row_nit_ciu.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(0, 8))

        f_nit = ctk.CTkFrame(row_nit_ciu, fg_color="transparent")
        f_nit.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(f_nit, text="NIT", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=Colors.TEXT_MAIN).pack(anchor="w", pady=(0, 2))
        entry_nit = ctk.CTkEntry(f_nit, placeholder_text="890980040-8")
        entry_nit.pack(fill="x")

        f_ciu = ctk.CTkFrame(row_nit_ciu, fg_color="transparent")
        f_ciu.pack(side="right", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(f_ciu, text="Ciudad Sede", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=Colors.TEXT_MAIN).pack(anchor="w", pady=(0, 2))
        entry_ciudad = ctk.CTkEntry(f_ciu, placeholder_text="Medellín")
        entry_ciudad.pack(fill="x")

        # 4. Caja Compensación y ARL
        row_caja_arl = ctk.CTkFrame(form_frame, fg_color="transparent")
        row_caja_arl.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(0, 8))

        f_caja = ctk.CTkFrame(row_caja_arl, fg_color="transparent")
        f_caja.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(f_caja, text="Caja Compensación", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=Colors.TEXT_MAIN).pack(anchor="w", pady=(0, 2))
        entry_caja = ctk.CTkEntry(f_caja, placeholder_text="Comfenalco")
        entry_caja.pack(fill="x")

        f_arl = ctk.CTkFrame(row_caja_arl, fg_color="transparent")
        f_arl.pack(side="right", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(f_arl, text="ARL", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=Colors.TEXT_MAIN).pack(anchor="w", pady=(0, 2))
        entry_arl = ctk.CTkEntry(f_arl, placeholder_text="Positiva")
        entry_arl.pack(fill="x")

        # Etiqueta de validación/error
        lbl_error = ctk.CTkLabel(card, text="", font=ctk.CTkFont(family="Segoe UI", size=11), text_color="#EF4444")
        lbl_error.pack(pady=(4, 8))

        # Botones de Acción
        btn_box = ctk.CTkFrame(card, fg_color="transparent")
        btn_box.pack(pady=(0, 10))

        def _cancelar():
            dialog.destroy()

        def _guardar_nueva_universidad():
            nombre = entry_nombre.get().strip()
            codigo = entry_codigo.get().strip().upper()
            nit = entry_nit.get().strip()
            ciudad = entry_ciudad.get().strip()
            caja = entry_caja.get().strip()
            arl = entry_arl.get().strip()

            if not nombre:
                lbl_error.configure(text="⚠️ Ingrese el nombre de la universidad.")
                return

            if not codigo:
                codigo = self.controller.gestor_multi_tenancy.generar_codigo_sugerido(nombre)

            # Validar unicidad del código
            if not self.controller.gestor_multi_tenancy.validar_codigo_disponible(codigo):
                lbl_error.configure(text=f"⚠️ El código '{codigo}' ya existe. Debe ser único.")
                return

            try:
                tenant = self.controller.agregar_universidad(
                    nombre=nombre,
                    codigo=codigo,
                    nit=nit,
                    ciudad=ciudad,
                    caja_compensacion=caja,
                    arl=arl,
                )
                # Actualizar selector del header
                nombres_actualizados = [t.nombre for t in self.controller.tenants if t.nombre]
                self.selector_univ.configure(values=nombres_actualizados)
                self.selector_univ.set(tenant.nombre)
                self._on_cambiar_universidad(tenant.nombre)
                dialog.destroy()
            except Exception as e:
                lbl_error.configure(text=f"❌ Error al guardar: {e}")

        ctk.CTkButton(
            btn_box,
            text="Cancelar",
            width=110,
            command=_cancelar,
            fg_color="transparent",
            border_width=1,
            border_color=Colors.BORDER_SUBTLE,
            text_color=Colors.TEXT_MUTED,
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            btn_box,
            text="💾 Guardar y Activar",
            width=170,
            command=_guardar_nueva_universidad,
            fg_color=Colors.ACCENT_PRIMARY,
            hover_color=Colors.ACCENT_PRIMARY_HOVER,
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
        ).pack(side="left", padx=8)

    # ------------------------------------------------------------------
    # Gestión de Inicio Con / Sin Datos (Requerimiento #59 Taller PITA)
    # ------------------------------------------------------------------
    def _comprobar_datos_iniciales(self) -> None:
        """Si la aplicación arranca sin facultades ni personas, ofrece la decisión al usuario."""
        if not self.controller.facultades and not self.controller.personas:
            self._mostrar_modal_bienvenida_datos()

    def _mostrar_modal_bienvenida_datos(self) -> None:
        """Modal de bienvenida para decidir arranque con datos demo o en limpio."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("👋 Configuración Inicial de Datos - PITA v2.0")
        dialog.geometry("560x380")
        dialog.resizable(False, False)
        dialog.grab_set()

        card = ctk.CTkFrame(dialog, fg_color=Colors.BG_CARD, corner_radius=12, border_width=1, border_color=Colors.BORDER_SUBTLE)
        card.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            card,
            text="👋 Bienvenido a PITA v2.0 (UPC)",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=Colors.TEXT_MAIN,
        ).pack(pady=(20, 5))

        ctk.CTkLabel(
            card,
            text="No se encontraron registros académicos previos en la carpeta 'datos/'.\nSegún el Requerimiento #59 del Taller, ¿cómo desea iniciar el sistema?",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=Colors.TEXT_MUTED,
            justify="center",
        ).pack(pady=(0, 20))

        def _elegir_demo():
            self.controller.cargar_datos_demo()
            dialog.destroy()
            self._refrescar_despues_de_cambio("🌱 Datos de Demostración Cargados con Éxito")

        def _elegir_sin_datos():
            self.controller.iniciar_sin_datos(crear_parametros_defecto=True)
            dialog.destroy()
            self._refrescar_despues_de_cambio("🧹 Sistema Iniciado Sin Datos (Solo Parámetros Normativos)")

        btn_demo = ctk.CTkButton(
            card,
            text="🌱 Cargar Datos de Demostración (Recomendado para video)",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#10B981",
            hover_color="#059669",
            height=40,
            corner_radius=8,
            command=_elegir_demo,
        )
        btn_demo.pack(fill="x", padx=40, pady=(0, 10))

        btn_vacio = ctk.CTkButton(
            card,
            text="🧹 Comenzar Sin Datos (Solo Parámetros por Defecto)",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#475569",
            hover_color="#334155",
            height=40,
            corner_radius=8,
            command=_elegir_sin_datos,
        )
        btn_vacio.pack(fill="x", padx=40, pady=(0, 15))

        ctk.CTkLabel(
            card,
            text="💡 Nota: Podrá alternar entre Modo Demo y Modo Sin Datos en cualquier momento\ndesde los botones del menú lateral izquierdo.",
            font=ctk.CTkFont(family="Segoe UI", size=10, slant="italic"),
            text_color=Colors.TEXT_MUTED,
            justify="center",
        ).pack(pady=(0, 10))

    def _cargar_demo_accion(self) -> None:
        """Carga la base de datos de ejemplo completa."""
        self.controller.cargar_datos_demo()
        self._refrescar_despues_de_cambio("🌱 Datos Demo Restaurados en 'datos/'")

    def _confirmar_iniciar_sin_datos(self) -> None:
        """Solicita confirmación antes de limpiar las entidades y comenzar sin datos."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("⚠️ Confirmar Modo Sin Datos")
        dialog.geometry("450x230")
        dialog.resizable(False, False)
        dialog.grab_set()

        ctk.CTkLabel(
            dialog,
            text="¿Desea limpiar los datos y comenzar sin registros?",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=Colors.TEXT_MAIN,
        ).pack(pady=(20, 10))

        ctk.CTkLabel(
            dialog,
            text="Se vaciarán facultades, programas, cursos, personas y contratos.\nLos 20 parámetros normativos legales se mantendrán activos\npara permitir registros desde cero.",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=Colors.TEXT_MUTED,
            justify="center",
        ).pack(pady=(0, 20))

        f_btns = ctk.CTkFrame(dialog, fg_color="transparent")
        f_btns.pack(fill="x", padx=20, pady=10)

        def _confirmar():
            self.controller.iniciar_sin_datos(crear_parametros_defecto=True)
            dialog.destroy()
            self._refrescar_despues_de_cambio("🧹 Modo Sin Datos Activo (Solo Parámetros)")

        ctk.CTkButton(f_btns, text="Cancelar", fg_color="#94A3B8", hover_color="#64748B", command=dialog.destroy).pack(side="left", expand=True, padx=5)
        ctk.CTkButton(f_btns, text="Sí, Iniciar Sin Datos", fg_color="#EF4444", hover_color="#DC2626", command=_confirmar).pack(side="right", expand=True, padx=5)

    def _refrescar_despues_de_cambio(self, mensaje_estado: str) -> None:
        """Actualiza el estado de la barra y refresca todas las vistas cargadas."""
        self.lbl_status.configure(text=f"🟢 {mensaje_estado}")
        for vista in self.vistas.values():
            if hasattr(vista, "actualizar"):
                try:
                    vista.actualizar()
                except Exception as err:
                    print(f"Error al refrescar vista: {err}")
        self.mostrar_vista(self.vista_actual or "dashboard")
