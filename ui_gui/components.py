"""Componentes visuales reutilizables para la GUI PITA con diseño Clean Windows 11 Light UI (Filas Compactas).

Incluye la tabla basada en Grid con alineación perfecta, insignias de estado (badges compactas)
y tarjetas de métricas KPI estilizadas.
"""

from __future__ import annotations

import customtkinter as ctk
from typing import Any, Callable, List, Optional, Sequence, Tuple, Union

from ui_gui.theme import Colors, Fonts


def clean_enum(val: Any, default: str = "") -> str:
    """Extrae el nombre o valor limpio de una instancia de Enum o string de Enum.
    
    Evita que cadenas como 'TipoProfesor.PLANTA' o 'EstadoAcademico.EBRA'
    se muestren directamente en la interfaz.
    """
    if val is None:
        return default
    if hasattr(val, "value"):
        s = str(val.value)
    elif hasattr(val, "name"):
        s = str(val.name)
    else:
        s = str(val)
    if "." in s:
        s = s.split(".")[-1]
    return s


def format_title_enum(val: Any, default: str = "") -> str:
    """Limpia el enum y lo formatea como Title Case reemplazando guiones bajos."""
    cleaned = clean_enum(val, default)
    return cleaned.replace("_", " ").title()


def create_badge(
    parent: Optional[ctk.CTkFrame],
    text: Any,
    badge_type: Any = "success",
) -> ctk.CTkFrame:
    """Crea una insignia estilizada compacta (Status Badge Pill) estilo Windows Fluent."""
    text_clean = clean_enum(text)
    type_clean = clean_enum(badge_type).lower()

    styles = {
        "success": {"bg": Colors.BADGE_ACTIVE_BG, "text": Colors.BADGE_ACTIVE_TXT, "border": Colors.BADGE_ACTIVE_BORDER},
        "active": {"bg": Colors.BADGE_ACTIVE_BG, "text": Colors.BADGE_ACTIVE_TXT, "border": Colors.BADGE_ACTIVE_BORDER},
        "activo": {"bg": Colors.BADGE_ACTIVE_BG, "text": Colors.BADGE_ACTIVE_TXT, "border": Colors.BADGE_ACTIVE_BORDER},
        "matriculado": {"bg": Colors.BADGE_INFO_BG, "text": Colors.BADGE_INFO_TXT, "border": Colors.BADGE_INFO_BORDER},
        "aprobado": {"bg": Colors.BADGE_ACTIVE_BG, "text": Colors.BADGE_ACTIVE_TXT, "border": Colors.BADGE_ACTIVE_BORDER},
        "liquidado": {"bg": Colors.BADGE_ACTIVE_BG, "text": Colors.BADGE_ACTIVE_TXT, "border": Colors.BADGE_ACTIVE_BORDER},
        "danger": {"bg": Colors.BADGE_EBRA_BG, "text": Colors.BADGE_EBRA_TXT, "border": Colors.BADGE_EBRA_BORDER},
        "ebra": {"bg": Colors.BADGE_EBRA_BG, "text": Colors.BADGE_EBRA_TXT, "border": Colors.BADGE_EBRA_BORDER},
        "cancelado": {"bg": Colors.BADGE_EBRA_BG, "text": Colors.BADGE_EBRA_TXT, "border": Colors.BADGE_EBRA_BORDER},
        "reprobado": {"bg": Colors.BADGE_EBRA_BG, "text": Colors.BADGE_EBRA_TXT, "border": Colors.BADGE_EBRA_BORDER},
        "warning": {"bg": "#FEF3C7", "text": "#D97706", "border": "#FCD34D"},
        "info": {"bg": Colors.BADGE_INFO_BG, "text": Colors.BADGE_INFO_TXT, "border": Colors.BADGE_INFO_BORDER},
        "en_curso": {"bg": "#E0E7FF", "text": "#4338CA", "border": "#A5B4FC"},
        "planta": {"bg": Colors.BADGE_INFO_BG, "text": Colors.BADGE_INFO_TXT, "border": Colors.BADGE_INFO_BORDER},
        "ocasional": {"bg": "#E0F2FE", "text": "#0369A1", "border": "#7DD3FC"},
        "catedra": {"bg": "#F3E8FF", "text": "#7E22CE", "border": "#D8B4FE"},
        "catedratico": {"bg": "#F3E8FF", "text": "#7E22CE", "border": "#D8B4FE"},
        "neutral": {"bg": "#F1F5F9", "text": Colors.TEXT_MUTED, "border": Colors.BORDER_SUBTLE},
    }

    style = styles.get(type_clean, styles["neutral"])

    pill = ctk.CTkFrame(
        parent,
        fg_color=style["bg"],
        corner_radius=6,
        border_width=1,
        border_color=style["border"],
    )

    label = ctk.CTkLabel(
        pill,
        text=text_clean,
        font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
        text_color=style["text"],
    )
    label.pack(padx=6, pady=1)
    return pill


def create_stat_card(
    parent: ctk.CTkFrame,
    row: int,
    col: int,
    title: str,
    value: str,
    accent_color: str = Colors.WIN_BLUE,
    subtitle: str = "",
) -> ctk.CTkFrame:
    """Crea una tarjeta KPI limpia elevada en blanco puro."""
    card = ctk.CTkFrame(
        parent,
        corner_radius=10,
        fg_color=Colors.BG_CARD,
        border_width=1,
        border_color=Colors.BORDER_SUBTLE,
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
        font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
        text_color=Colors.TEXT_MUTED,
        anchor="w",
    ).pack(anchor="w")

    ctk.CTkLabel(
        content,
        text=value,
        font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
        text_color=Colors.TEXT_MAIN,
        anchor="w",
    ).pack(anchor="w", pady=(4, 2))

    if subtitle:
        ctk.CTkLabel(
            content,
            text=subtitle,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=Colors.TEXT_MUTED,
            anchor="w",
        ).pack(anchor="w")

    return card


class PITATreeviewTable(ctk.CTkFrame):
    """Tabla de datos limpia y nativa basada en ttk.Treeview con estilo Windows 11 Light,
    encabezados fijos, selección de fila nativa, scrollbar fluido y soporte completo de acciones.
    """

    def __init__(
        self,
        parent: ctk.CTkFrame,
        headers: List[str],
        col_weights: Optional[List[int]] = None,
        col_mins: Optional[List[int]] = None,
        **kwargs,
    ) -> None:
        super().__init__(
            parent,
            fg_color=Colors.BG_CARD,
            border_width=1,
            border_color=Colors.BORDER_SUBTLE,
            corner_radius=8,
            **kwargs,
        )

        self.headers = headers
        self.num_cols = len(headers)
        self.col_weights = col_weights or [1] * self.num_cols
        self.col_mins = col_mins or [90] * self.num_cols
        self.row_counter = 0
        self.row_actions = {}  # Map row_id -> list of action tuples: (label, callback)

        # Configurar Estilos de ttk.Treeview
        self._setup_style()

        # Generar identificadores de columna
        self.col_ids = [f"col_{i}" for i in range(self.num_cols)]

        # Contenedor para Treeview + Scrollbars
        self.tree_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.tree_frame.pack(fill="both", expand=True, padx=4, pady=4)

        # Scrollbars
        import tkinter as tk
        from tkinter import ttk

        self.vsb = ttk.Scrollbar(self.tree_frame, orient="vertical")
        self.hsb = ttk.Scrollbar(self.tree_frame, orient="horizontal")

        self.tree = ttk.Treeview(
            self.tree_frame,
            columns=self.col_ids,
            show="headings",
            style="PITA.Treeview",
            selectmode="browse",
            yscrollcommand=self.vsb.set,
            xscrollcommand=self.hsb.set,
        )

        self.vsb.config(command=self.tree.yview)
        self.hsb.config(command=self.tree.xview)

        # Empaquetado
        self.vsb.pack(side="right", fill="y")
        self.hsb.pack(side="bottom", fill="x")
        self.tree.pack(side="left", fill="both", expand=True)

        # Configurar columnas y encabezados
        for i, (col_id, text, min_w, w_ratio) in enumerate(
            zip(self.col_ids, self.headers, self.col_mins, self.col_weights)
        ):
            anchor = (
                "center"
                if text.lower() in ("acciones", "acción", "estado", "código", "id", "semestre", "créditos", "unidad")
                else "w"
            )
            self.tree.heading(col_id, text=text, anchor=anchor)
            calc_w = max(min_w, min_w * w_ratio // 2)
            self.tree.column(col_id, width=calc_w, minwidth=min_w, stretch=True, anchor=anchor)

        # Configurar Tags para alternancia de filas (Zebra Striping)
        self.tree.tag_configure("even", background="#FFFFFF")
        self.tree.tag_configure("odd", background="#F8FAFC")
        self.tree.tag_configure("highlight", background="#FEF2F2")

        # Bindings para doble clic y clic en celda
        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<ButtonRelease-1>", self._on_click)

    def _setup_style(self) -> None:
        import tkinter as tk
        from tkinter import ttk

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure(
            "PITA.Treeview",
            background="#FFFFFF",
            fieldbackground="#FFFFFF",
            foreground=Colors.TEXT_MAIN,
            rowheight=32,
            font=("Segoe UI", 10),
            bordercolor=Colors.BORDER_SUBTLE,
            borderwidth=1,
        )
        style.configure(
            "PITA.Treeview.Heading",
            background="#F1F5F9",
            foreground=Colors.TEXT_MAIN,
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padding=(8, 6),
        )
        style.map(
            "PITA.Treeview.Heading",
            background=[("active", "#E2E8F0")],
        )
        style.map(
            "PITA.Treeview",
            background=[("selected", Colors.WIN_BLUE)],
            foreground=[("selected", "#FFFFFF")],
        )

    def add_row_items(
        self,
        cells: List[Union[str, Tuple[str, ...], ctk.CTkButton, ctk.CTkFrame, ctk.CTkLabel]],
        is_highlighted: bool = False,
        custom_bg: Optional[str] = None,
    ) -> str:
        """Añade una fila a la Treeview procesando celdas simples, badges y acciones."""
        self.row_counter += 1
        row_id = str(self.row_counter)

        row_values = []
        row_action_list = []

        for item in cells:
            if isinstance(item, tuple) and len(item) >= 2 and item[0] == "badge":
                b_text = clean_enum(item[1])
                b_type = clean_enum(item[2]).lower() if len(item) > 2 else "neutral"
                prefix = {
                    "success": "🟢 ",
                    "active": "🟢 ",
                    "activo": "🟢 ",
                    "matriculado": "🟢 ",
                    "aprobado": "🟢 ",
                    "liquidado": "🟢 ",
                    "danger": "🔴 ",
                    "ebra": "🔴 ",
                    "cancelado": "🔴 ",
                    "reprobado": "🔴 ",
                    "warning": "⚠️ ",
                    "info": "🔵 ",
                    "en_curso": "🔵 ",
                    "planta": "🔵 ",
                    "ocasional": "🟣 ",
                    "catedra": "🟣 ",
                    "catedratico": "🟣 ",
                }.get(b_type, "")
                row_values.append(f"{prefix}{b_text}")
            elif isinstance(item, tuple) and item[0] == "actions":
                action_strs = []
                for spec in item[1]:
                    btn_text = spec[0]
                    btn_cmd = spec[1]
                    action_strs.append(btn_text)
                    row_action_list.append((btn_text, btn_cmd))
                row_values.append("  ".join(action_strs))
            elif isinstance(item, tuple) and len(item) >= 3 and item[0] == "button":
                btn_text, btn_cmd = item[1], item[2]
                row_values.append(btn_text)
                row_action_list.append((btn_text, btn_cmd))
            elif isinstance(item, tuple):
                row_values.append(clean_enum(item[0]))
            else:
                row_values.append(clean_enum(item))

        tag = "highlight" if is_highlighted else ("even" if self.row_counter % 2 == 0 else "odd")
        self.tree.insert("", "end", iid=row_id, values=row_values, tags=(tag,))

        if row_action_list:
            self.row_actions[row_id] = row_action_list

        return row_id

    def _on_double_click(self, event) -> None:
        """Al hacer doble clic en una fila, ejecuta la primera acción asociada si existe."""
        item_id = self.tree.focus()
        if item_id in self.row_actions and self.row_actions[item_id]:
            first_action_cmd = self.row_actions[item_id][0][1]
            if callable(first_action_cmd):
                first_action_cmd()

    def _on_click(self, event) -> None:
        """Al hacer clic en una celda de acción, activa el comando correspondiente."""
        import tkinter as tk

        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            col = self.tree.identify_column(event.x)
            try:
                col_index = int(col.replace("#", "")) - 1
            except ValueError:
                return

            if 0 <= col_index < len(self.headers):
                header_name = self.headers[col_index].lower()
                if "acción" in header_name or "acciones" in header_name:
                    item_id = self.tree.identify_row(event.y)
                    if item_id in self.row_actions:
                        actions = self.row_actions[item_id]
                        if len(actions) == 1:
                            if callable(actions[0][1]):
                                actions[0][1]()
                        elif len(actions) > 1:
                            menu = tk.Menu(self, tearoff=0)
                            for label, cmd in actions:
                                menu.add_command(label=label, command=cmd)
                            try:
                                menu.tk_popup(event.x_root, event.y_root)
                            finally:
                                menu.grab_release()

    def clear_rows(self) -> None:
        """Limpia todas las filas de la tabla."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.row_counter = 0
        self.row_actions.clear()


# Alias de compatibilidad
PITAGridTable = PITATreeviewTable

