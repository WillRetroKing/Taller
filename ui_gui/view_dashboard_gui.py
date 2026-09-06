"""Vista de Panel de Control (Dashboard) para la GUI del Sistema PITA con diseño Windows 11."""

from __future__ import annotations

import customtkinter as ctk
from typing import TYPE_CHECKING

from ui_gui.components import create_badge, create_stat_card
from ui_gui.theme import Colors, Fonts

if TYPE_CHECKING:
    from ui_gui.gui_controller import PITAController


class DashboardViewGUI(ctk.CTkFrame):
    """Vista principal con resumen KPI, métricas académicas y de nómina."""

    def __init__(self, parent: ctk.CTk, controller: PITAController) -> None:
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        self._crear_interfaz()

    def actualizar(self) -> None:
        """Refresca todos los KPIs, alertas y resúmenes con los datos vigentes del controlador."""
        for child in self.winfo_children():
            child.destroy()
        self._crear_interfaz()

    def _crear_interfaz(self) -> None:
        # Título y Subtítulo
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", padx=15, pady=(15, 15))

        ctk.CTkLabel(
            title_frame,
            text="📊 Panel de Control General",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=Colors.TEXT_MAIN,
            anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_frame,
            text="Sistema Integrado de Transacciones Académicas y Nómina Docente • Universidad Popular del Cesar",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=Colors.TEXT_MUTED,
            anchor="w",
        ).pack(anchor="w")

        # ------------------------------------------------------------------
        # Tarjetas KPI (Métricas Principales)
        # ------------------------------------------------------------------
        kpi_frame = ctk.CTkFrame(self, fg_color="transparent")
        kpi_frame.pack(fill="x", padx=15, pady=(0, 15))
        kpi_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="kpi")

        total_estudiantes = len(self.controller.estudiantes)
        estudiantes_ebra = sum(
            1 for e in self.controller.estudiantes
            if str(getattr(e, "estadoAcademico", "")) == "EBRA" or (e.promedioAcumulado and e.promedioAcumulado < 3.0)
        )
        total_profesores = len(self.controller.profesores)
        total_contratos = sum(1 for c in self.controller.contratos if str(getattr(c, "estado", "")) == "ACTIVO")

        create_stat_card(
            kpi_frame, 0, 0, "👨‍🎓 Estudiantes Registrados", str(total_estudiantes), Colors.WIN_BLUE, "Activos en programas PITA"
        )
        create_stat_card(
            kpi_frame, 0, 1, "⚠️ Alertas EBRA Activas", str(estudiantes_ebra), Colors.ACCENT_DANGER if estudiantes_ebra > 0 else Colors.ACCENT_SUCCESS, "Riesgo académico (< 3.0)"
        )
        create_stat_card(
            kpi_frame, 0, 2, "👨‍🏫 Cuerpo Docente", str(total_profesores), Colors.ACCENT_INDIGO, "Planta, Ocasional y Cátedra"
        )
        create_stat_card(
            kpi_frame, 0, 3, "📝 Contratos Docentes", str(total_contratos), Colors.ACCENT_WARNING, "Vinculaciones vigentes"
        )

        # ------------------------------------------------------------------
        # Sección Central (Alertas EBRA y Resumen de Nómina)
        # ------------------------------------------------------------------
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=15, pady=5)
        content_frame.grid_columnconfigure((0, 1), weight=1, uniform="content")
        content_frame.grid_rowconfigure(0, weight=1)

        # Panel Izquierdo: Alertas EBRA Destacadas
        ebra_card = ctk.CTkFrame(content_frame, corner_radius=10, fg_color=Colors.BG_CARD, border_width=1, border_color=Colors.ACCENT_DANGER)
        ebra_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=5)

        header_eb = ctk.CTkFrame(ebra_card, fg_color="transparent")
        header_eb.pack(fill="x", padx=15, pady=(15, 5))

        ctk.CTkLabel(
            header_eb,
            text="⚠️ Estudiantes en Alerta EBRA",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=Colors.ACCENT_DANGER,
        ).pack(side="left")

        # Badge total
        ctk.CTkLabel(
            header_eb,
            text=f"{estudiantes_ebra} casos",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=Colors.ACCENT_DANGER,
        ).pack(side="right")

        ctk.CTkLabel(
            ebra_card,
            text="Estudiantes cuyo promedio acumulado está por debajo de 3.0",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=Colors.TEXT_MUTED,
        ).pack(anchor="w", padx=15, pady=(0, 10))

        ebra_scroll = ctk.CTkScrollableFrame(ebra_card, fg_color="transparent")
        ebra_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        estud_ebra_list = [
            e for e in self.controller.estudiantes
            if str(getattr(e, "estadoAcademico", "")) == "EBRA" or (e.promedioAcumulado and e.promedioAcumulado < 3.0)
        ]

        if not estud_ebra_list:
            ctk.CTkLabel(
                ebra_scroll,
                text="✅ Sin alertas registradas. Todos los estudiantes cumplen el promedio.",
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                text_color=Colors.ACCENT_SUCCESS,
            ).pack(pady=30)
        else:
            for est in estud_ebra_list:
                item = ctk.CTkFrame(ebra_scroll, fg_color=Colors.BADGE_EBRA_BG, corner_radius=6, border_width=1, border_color=Colors.BADGE_EBRA_BORDER)
                item.pack(fill="x", pady=4, padx=5)

                pers = next((p for p in self.controller.personas if getattr(p, "idPersona", None) == getattr(est, "idPersona", None)), None)
                nombre_est = f"{getattr(pers, 'primerNombre', '')} {getattr(pers, 'primerApellido', '')}" if pers else "Estudiante"

                ctk.CTkLabel(
                    item,
                    text=f"{getattr(est, 'codigoEstudiante', 'N/A')} — {nombre_est}",
                    font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                    text_color=Colors.TEXT_MAIN,
                ).pack(side="left", padx=12, pady=8)

                ctk.CTkLabel(
                    item,
                    text=f"Promedio: {getattr(est, 'promedioAcumulado', '0.0')}",
                    font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                    text_color=Colors.BADGE_EBRA_TXT,
                ).pack(side="right", padx=12, pady=8)

        # Panel Derecho: Estado de Nómina y Normatividad
        payroll_card = ctk.CTkFrame(content_frame, corner_radius=10, fg_color=Colors.BG_CARD, border_width=1, border_color=Colors.BORDER_SUBTLE)
        payroll_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=5)

        ctk.CTkLabel(
            payroll_card,
            text="💰 Parámetros Salariales y Normatividad",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=Colors.TEXT_MAIN,
        ).pack(anchor="w", padx=15, pady=(15, 5))

        ctk.CTkLabel(
            payroll_card,
            text="Decreto 1279 de 2002 / Acuerdo 027 del 31 de octubre de 2024",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=Colors.TEXT_MUTED,
        ).pack(anchor="w", padx=15, pady=(0, 10))

        pay_info_frame = ctk.CTkFrame(payroll_card, fg_color="transparent")
        pay_info_frame.pack(fill="both", expand=True, padx=15, pady=5)

        smmlv = next((p.valor for p in self.controller.parametros if p.codigo == "SALARIO_MINIMO"), "1750905")
        punto = next((p.valor for p in self.controller.parametros if p.codigo == "VALOR_PUNTO_SALARIAL"), "23924")
        aux_trans = next((p.valor for p in self.controller.parametros if p.codigo == "VALOR_AUXILIO_TRANSPORTE_VIGENTE"), "249095")

        rows = [
            ("💵 SMMLV Vigente:", f"$ {int(float(smmlv)):,} COP" if str(smmlv).replace(".","").isdigit() else smmlv),
            ("📍 Punto Salarial (Dec. 1279):", f"$ {int(float(punto)):,} COP" if str(punto).replace(".","").isdigit() else punto),
            ("🚌 Auxilio Transporte:", f"$ {int(float(aux_trans)):,} COP" if str(aux_trans).replace(".","").isdigit() else aux_trans),
            ("🏥 Salud Trabajador:", "4.0 % (Ingreso Base Cotización)"),
            ("👴 Pensión Trabajador:", "4.0 % (Ingreso Base Cotización)"),
            ("⚖️ Fondo Solidaridad Pensional:", "1.0 % (si IBC ≥ 4 SMMLV)"),
        ]

        for label, val in rows:
            r = ctk.CTkFrame(pay_info_frame, fg_color=Colors.BG_CARD_HOVER, corner_radius=6)
            r.pack(fill="x", pady=4)

            ctk.CTkLabel(
                r,
                text=label,
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                text_color=Colors.TEXT_MUTED,
            ).pack(side="left", padx=12, pady=6)

            ctk.CTkLabel(
                r,
                text=val,
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                text_color=Colors.TEXT_MAIN,
            ).pack(side="right", padx=12, pady=6)
