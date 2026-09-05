"""Componentes visuales reutilizables para la GUI PITA.

Incluye la tabla basada en Grid con alineación perfecta, insignias de estado (badges)
y tarjetas de métricas KPI estilizadas.
"""

from __future__ import annotations

import customtkinter as ctk
from typing import Callable, List, Optional, Sequence, Tuple, Union


def create_badge(
    parent: Optional[ctk.CTkFrame],
    text: str,
    badge_type: str = "success",
) -> ctk.CTkFrame:
    """Crea una insignia estilizada (Status Badge Pill) con bordes suaves."""
    styles = {
        "success": {"bg": "#064E3B", "text": "#34D399", "border": "#059669"},
        "active": {"bg": "#064E3B", "text": "#34D399", "border": "#059669"},
        "liquidado": {"bg": "#064E3B", "text": "#34D399", "border": "#059669"},
        "danger": {"bg": "#451A1D", "text": "#F87171", "border": "#7F1D1D"},
        "ebra": {"bg": "#451A1D", "text": "#F87171", "border": "#7F1D1D"},
        "cancelado": {"bg": "#451A1D", "text": "#F87171", "border": "#7F1D1D"},
        "warning": {"bg": "#451E03", "text": "#FBBF24", "border": "#D97706"},
        "info": {"bg": "#1E1B4B", "text": "#A5B4FC", "border": "#4338CA"},
        "planta": {"bg": "#1E1B4B", "text": "#A5B4FC", "border": "#4338CA"},
        "ocasional": {"bg": "#083344", "text": "#67E8F9", "border": "#0891B2"},
        "catedra": {"bg": "#2E1065", "text": "#DDD6FE", "border": "#7C3AED"},
        "neutral": {"bg": "#1E293B", "text": "#94A3B8", "border": "#334155"},
    }

    style = styles.get(badge_type.lower(), styles["neutral"])

    pill = ctk.CTkFrame(
        parent,
        fg_color=style["bg"],
        corner_radius=12,
        border_width=1,
        border_color=style["border"],
    )

    label = ctk.CTkLabel(
        pill,
        text=text,
        font=ctk.CTkFont(size=11, weight="bold"),
        text_color=style["text"],
    )
    label.pack(padx=10, pady=3)
    return pill


def create_stat_card(
    parent: ctk.CTkFrame,
    row: int,
    col: int,
    title: str,
    value: str,
    accent_color: str = "#10B981",
    subtitle: str = "",
) -> ctk.CTkFrame:
    """Crea una tarjeta KPI elevada con barra superior de color y tipografía limpia."""
    card = ctk.CTkFrame(
        parent,
        corner_radius=10,
        fg_color="#0F172A",
        border_width=1,
        border_color="#334155",
    )
    card.grid(row=row, column=col, sticky="nsew", padx=6, pady=6)

    # Barra acentuada superior
    top_strip = ctk.CTkFrame(card, height=4, corner_radius=0, fg_color=accent_color)
    top_strip.pack(fill="x", side="top")

    content = ctk.CTkFrame(card, fg_color="transparent")
    content.pack(fill="both", expand=True, padx=14, pady=12)

    ctk.CTkLabel(
        content,
        text=title,
        font=ctk.CTkFont(size=12, weight="bold"),
        text_color="#94A3B8",
        anchor="w",
    ).pack(anchor="w")

    ctk.CTkLabel(
        content,
        text=value,
        font=ctk.CTkFont(size=26, weight="bold"),
        text_color="#F8FAFC",
        anchor="w",
    ).pack(anchor="w", pady=(4, 2))

    if subtitle:
        ctk.CTkLabel(
            content,
            text=subtitle,
            font=ctk.CTkFont(size=11),
            text_color="#64748B",
            anchor="w",
        ).pack(anchor="w")

    return card


class PITAGridTable(ctk.CTkScrollableFrame):
    """Tabla de datos estilizada con alineación estricta por columnas, zebra striping y headers."""

    def __init__(
        self,
        parent: ctk.CTkFrame,
        headers: List[str],
        col_weights: Optional[List[int]] = None,
        col_mins: Optional[List[int]] = None,
        **kwargs,
    ) -> None:
        super().__init__(parent, fg_color="transparent", **kwargs)

        self.headers = headers
        self.num_cols = len(headers)
        self.col_weights = col_weights or [1] * self.num_cols
        self.col_mins = col_mins or [80] * self.num_cols
        self.row_counter = 0

        self._crear_header()

    def _crear_header(self) -> None:
        """Construye la fila fijada de cabecera."""
        h_frame = ctk.CTkFrame(
            self,
            fg_color="#0F172A",
            corner_radius=8,
            border_width=1,
            border_color="#334155",
        )
        h_frame.pack(fill="x", pady=(0, 6))

        for col_idx, (text, w, m) in enumerate(zip(self.headers, self.col_weights, self.col_mins)):
            h_frame.grid_columnconfigure(col_idx, weight=w, minsize=m)
            lbl = ctk.CTkLabel(
                h_frame,
                text=text.upper(),
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#94A3B8",
                anchor="w",
            )
            lbl.grid(row=0, column=col_idx, padx=12, pady=10, sticky="ew")

    def add_row_items(
        self,
        cells: List[Union[str, Tuple[str, ...], ctk.CTkButton, ctk.CTkFrame, ctk.CTkLabel]],
        is_highlighted: bool = False,
        custom_bg: Optional[str] = None,
    ) -> ctk.CTkFrame:
        """Añade una fila con alineación estricta y alternado de color (zebra striping).

        Soporta:
        - Cadenas directas: "Texto"
        - Tuplas con color: ("Texto", "#10B981")
        - Tuplas badge: ("badge", "Texto", "active")
        - Tuplas botón: ("button", "Texto", comando_fn, "#EF4444", "#DC2626")
        - Widgets (CTkButton, CTkFrame, CTkLabel)
        """
        self.row_counter += 1
        if custom_bg:
            bg_color = custom_bg
        elif is_highlighted:
            bg_color = "#2D1A1E"
        else:
            bg_color = "#1E293B" if self.row_counter % 2 == 0 else "#141E2E"

        row_frame = ctk.CTkFrame(
            self,
            fg_color=bg_color,
            corner_radius=6,
            border_width=1,
            border_color="#1E293B" if bg_color == "#141E2E" else "#334155",
        )
        row_frame.pack(fill="x", pady=2)

        for col_idx, (item, w, m) in enumerate(zip(cells, self.col_weights, self.col_mins)):
            row_frame.grid_columnconfigure(col_idx, weight=w, minsize=m)

            if isinstance(item, tuple) and len(item) >= 2 and item[0] == "badge":
                b_text = item[1]
                b_type = item[2] if len(item) > 2 else "neutral"
                badge_w = create_badge(row_frame, b_text, b_type)
                badge_w.grid(row=0, column=col_idx, padx=8, pady=6, sticky="w")
            elif isinstance(item, tuple) and len(item) >= 3 and item[0] == "button":
                b_text = item[1]
                b_cmd = item[2]
                fg = item[3] if len(item) > 3 else "#334155"
                hvr = item[4] if len(item) > 4 else "#475569"
                w_val = item[5] if len(item) > 5 else 84
                h_val = item[6] if len(item) > 6 else 28
                btn = ctk.CTkButton(
                    row_frame,
                    text=b_text,
                    command=b_cmd,
                    fg_color=fg,
                    hover_color=hvr,
                    width=w_val,
                    height=h_val,
                    font=ctk.CTkFont(size=10, weight="bold"),
                )
                btn.grid(row=0, column=col_idx, padx=8, pady=6, sticky="w")
            elif isinstance(item, tuple) and item[0] == "actions":
                action_container = ctk.CTkFrame(row_frame, fg_color="transparent")
                for btn_spec in item[1]:
                    b_text = btn_spec[0]
                    b_cmd = btn_spec[1]
                    fg = btn_spec[2] if len(btn_spec) > 2 else "#334155"
                    hvr = btn_spec[3] if len(btn_spec) > 3 else "#475569"
                    w_val = btn_spec[4] if len(btn_spec) > 4 else 32
                    h_val = btn_spec[5] if len(btn_spec) > 5 else 28
                    b_font_sz = btn_spec[6] if len(btn_spec) > 6 else 10
                    btn = ctk.CTkButton(
                        action_container,
                        text=b_text,
                        command=b_cmd,
                        fg_color=fg,
                        hover_color=hvr,
                        width=w_val,
                        height=h_val,
                        font=ctk.CTkFont(size=b_font_sz, weight="bold"),
                    )
                    btn.pack(side="left", padx=2)
                action_container.grid(row=0, column=col_idx, padx=8, pady=6, sticky="w")
            elif isinstance(item, tuple):
                text, color = item[0], item[1]
                lbl = ctk.CTkLabel(
                    row_frame,
                    text=str(text),
                    font=ctk.CTkFont(size=11, weight="bold"),
                    text_color=color,
                    anchor="w",
                )
                lbl.grid(row=0, column=col_idx, padx=12, pady=8, sticky="ew")
            elif isinstance(item, (ctk.CTkButton, ctk.CTkFrame, ctk.CTkLabel)):
                # Si el widget ya fue creado con parent=row_frame o sin parent, lo posicionamos con grid
                item.grid(row=0, column=col_idx, padx=8, pady=6, sticky="w")
            else:
                lbl = ctk.CTkLabel(
                    row_frame,
                    text=str(item),
                    font=ctk.CTkFont(size=11),
                    text_color="#E2E8F0",
                    anchor="w",
                )
                lbl.grid(row=0, column=col_idx, padx=12, pady=8, sticky="ew")

        return row_frame

    def clear_rows(self) -> None:
        """Limpia las filas manteniendo el header."""
        for child in self.winfo_children():
            if child.winfo_class() == "Frame" and child != self.winfo_children()[0]:
                child.destroy()
        self.row_counter = 0
