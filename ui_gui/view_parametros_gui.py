"""Vista de Parámetros Normativos y Gestión de Persistencia en Disco con diseño Clean Windows 11 Light UI."""

from __future__ import annotations

import customtkinter as ctk
from typing import Any, TYPE_CHECKING

from ui_gui.components import PITAGridTable, create_badge
from ui_gui.theme import Colors, Fonts

if TYPE_CHECKING:
    from ui_gui.gui_controller import PITAController


class ParametrosViewGUI(ctk.CTkFrame):
    """Vista para administrar parámetros legales y controlar la persistencia de datos."""

    def __init__(self, parent: ctk.CTk, controller: PITAController) -> None:
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        self._crear_interfaz()

    def _crear_interfaz(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(
            header,
            text="⚙️ Parámetros Normativos & Persistencia",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=Colors.TEXT_MAIN,
        ).pack(side="left")

        # Botones de Acción de Persistencia
        p_frame = ctk.CTkFrame(header, fg_color="transparent")
        p_frame.pack(side="right")

        btn_guardar = ctk.CTkButton(
            p_frame,
            text="💾 Guardar en Disco (datos/)",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=Colors.WIN_BLUE,
            hover_color=Colors.WIN_BLUE_HOVER,
            text_color="#FFFFFF",
            corner_radius=8,
            command=self._guardar_persistencia,
        )
        btn_guardar.pack(side="left", padx=5)

        btn_cargar = ctk.CTkButton(
            p_frame,
            text="🔄 Recargar desde Disco",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=Colors.ACCENT_PRIMARY,
            hover_color=Colors.ACCENT_PRIMARY_HOVER,
            text_color="#FFFFFF",
            corner_radius=8,
            command=self._recargar_persistencia,
        )
        btn_cargar.pack(side="left", padx=5)

        # Contenido de Parámetros
        headers = ["Código Parámetro", "Nombre Descripción", "Valor Vigente", "Unidad", "Norma Origen", "Aplica A", "Acción"]
        col_weights = [2, 3, 2, 1, 2, 1, 1]
        col_mins = [110, 150, 90, 60, 110, 80, 80]

        table = PITAGridTable(self, headers=headers, col_weights=col_weights, col_mins=col_mins)
        table.pack(fill="both", expand=True, padx=10, pady=5)

        if not self.controller.parametros:
            ctk.CTkLabel(table, text="No hay parámetros cargados.", text_color=Colors.TEXT_MUTED).pack(pady=20)
            return

        for p in self.controller.parametros:
            val_str = str(getattr(p, "valor", "0"))
            val_fmt = f"$ {int(float(val_str)):,}" if val_str.replace(".","").isdigit() and getattr(p, "tipoDato", "") == "MONETARIO" else val_str

            codigo_raw = str(getattr(p, "codigo", "N/A"))
            codigo_clean = codigo_raw.split(".")[-1] if "." in codigo_raw else codigo_raw

            act_spec = (
                "actions",
                [
                    ("✏️ Editar", lambda par=p: self._editar_parametro(par), Colors.WIN_BLUE, Colors.WIN_BLUE_HOVER, 74, 28, 10),
                ],
            )

            cells = [
                (codigo_clean, Colors.TEXT_ACCENT),
                (getattr(p, "nombre", "N/A"), Colors.TEXT_MAIN),
                (val_fmt, Colors.BADGE_ACTIVE_TXT),
                getattr(p, "unidad", ""),
                getattr(p, "normaOrigen", "Acuerdo 027"),
                ("badge", getattr(p, "aplicaA", "TODOS"), "info"),
                act_spec,
            ]
            table.add_row_items(cells)

    def _editar_parametro(self, param: Any) -> None:
        dialog = ctk.CTkToplevel(self)
        codigo_raw = str(param.codigo)
        codigo_clean = codigo_raw.split(".")[-1] if "." in codigo_raw else codigo_raw
        dialog.title(f"✏️ Editar Parámetro {codigo_clean}")
        dialog.geometry("450x380")
        dialog.grab_set()

        ctk.CTkLabel(
            dialog,
            text=f"Modificar Parámetro: {param.nombre}",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=Colors.TEXT_MAIN,
        ).pack(pady=15)

        entry_val = ctk.CTkEntry(
            dialog,
            width=360,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            fg_color=Colors.BG_WINDOW,
            border_color=Colors.BORDER_SUBTLE,
            text_color=Colors.TEXT_MAIN,
        )
        entry_val.insert(0, str(param.valor))
        entry_val.pack(padx=20, pady=10)

        def _guardar():
            val = entry_val.get().strip()
            if val:
                param.valor = val
                self.controller._recrear_gestores()
                dialog.destroy()
                self.actualizar()

        ctk.CTkButton(
            dialog,
            text="💾 Actualizar Parámetro",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=Colors.WIN_BLUE,
            hover_color=Colors.WIN_BLUE_HOVER,
            text_color="#FFFFFF",
            height=36,
            command=_guardar,
        ).pack(pady=20)

    def _guardar_persistencia(self) -> None:
        try:
            self.controller.guardar_datos()
            msg = ctk.CTkToplevel(self)
            msg.title("Éxito")
            msg.geometry("320x130")
            ctk.CTkLabel(
                msg,
                text="✅ Todos los datos fueron guardados\nexitosamente en 'datos/'.",
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                text_color=Colors.TEXT_MAIN,
            ).pack(pady=20)
        except Exception as e:
            print(f"Error guardando: {e}")

    def _recargar_persistencia(self) -> None:
        self.controller.cargar_datos()
        self.actualizar()

    def actualizar(self) -> None:
        for widget in self.winfo_children():
            widget.destroy()
        self._crear_interfaz()
