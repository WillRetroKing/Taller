"""Vista de Parámetros Normativos y Gestión de Persistencia en Disco."""

from __future__ import annotations

import customtkinter as ctk
from typing import TYPE_CHECKING

from ui_gui.components import PITAGridTable, create_badge


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
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#F8FAFC",
        ).pack(side="left")

        # Botones de Acción de Persistencia
        p_frame = ctk.CTkFrame(header, fg_color="transparent")
        p_frame.pack(side="right")

        btn_guardar = ctk.CTkButton(
            p_frame,
            text="💾 Guardar en Disco (datos/)",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#10B981",
            hover_color="#059669",
            corner_radius=8,
            command=self._guardar_persistencia,
        )
        btn_guardar.pack(side="left", padx=5)

        btn_cargar = ctk.CTkButton(
            p_frame,
            text="🔄 Recargar desde Disco",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#6366F1",
            hover_color="#4F46E5",
            corner_radius=8,
            command=self._recargar_persistencia,
        )
        btn_cargar.pack(side="left", padx=5)

        # Contenido de Parámetros
        headers = ["Código Parámetro", "Nombre Descripción", "Valor Vigente", "Unidad", "Norma Origen", "Aplica A", "Acción"]
        col_weights = [2, 4, 3, 2, 3, 2, 2]
        col_mins = [120, 200, 120, 80, 130, 90, 80]

        table = PITAGridTable(self, headers=headers, col_weights=col_weights, col_mins=col_mins)
        table.pack(fill="both", expand=True, padx=10, pady=5)

        if not self.controller.parametros:
            ctk.CTkLabel(table, text="No hay parámetros cargados.", text_color="#94A3B8").pack(pady=20)
            return

        for p in self.controller.parametros:
            val_str = str(getattr(p, "valor", "0"))
            val_fmt = f"$ {int(float(val_str)):,}" if val_str.replace(".","").isdigit() and getattr(p, "tipoDato", "") == "MONETARIO" else val_str

            btn_e = ("button", "✏️ Editar", lambda par=p: self._editar_parametro(par), "#334155", "#475569", 74, 28)

            cells = [
                (str(getattr(p, "codigo", "N/A")), "#F59E0B"),
                (getattr(p, "nombre", "N/A"), "#F8FAFC"),
                (val_fmt, "#10B981"),
                getattr(p, "unidad", ""),
                getattr(p, "normaOrigen", "Acuerdo 027"),
                ("badge", getattr(p, "aplicaA", "TODOS"), "info"),
                btn_e,
            ]
            table.add_row_items(cells)

    def _editar_parametro(self, param: Any) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"✏️ Editar Parámetro {param.codigo}")
        dialog.geometry("450x420")
        dialog.grab_set()

        ctk.CTkLabel(dialog, text=f"Modificar Parámetro: {param.nombre}", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=12)

        entry_val = ctk.CTkEntry(dialog)
        entry_val.insert(0, str(param.valor))
        entry_val.pack(fill="x", padx=20, pady=8)

        def _guardar():
            val = entry_val.get().strip()
            if val:
                param.valor = val
                self.controller._recrear_gestores()
                dialog.destroy()
                self.actualizar()

        ctk.CTkButton(dialog, text="💾 Actualizar Parámetro", font=ctk.CTkFont(size=12, weight="bold"), fg_color="#10B981", hover_color="#059669", height=36, command=_guardar).pack(pady=20)

    def _guardar_persistencia(self) -> None:
        try:
            self.controller.guardar_datos()
            msg = ctk.CTkToplevel(self)
            msg.title("Éxito")
            msg.geometry("300x120")
            ctk.CTkLabel(msg, text="✅ Todos los datos fueron guardados\nexitosamente en 'datos/'.", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=20)
        except Exception as e:
            print(f"Error guardando: {e}")

    def _recargar_persistencia(self) -> None:
        self.controller.cargar_datos()
        self.actualizar()

    def actualizar(self) -> None:
        for widget in self.winfo_children():
            widget.destroy()
        self._crear_interfaz()
