"""Vista de Panel de Control (Dashboard) para la GUI del Sistema PITA."""

from __future__ import annotations

import customtkinter as ctk
from typing import TYPE_CHECKING

from ui_gui.components import create_badge, create_stat_card

if TYPE_CHECKING:
    from ui_gui.gui_controller import PITAController


class DashboardViewGUI(ctk.CTkFrame):
    """Vista principal con resumen KPI, métricas académicas y de nómina."""

    def __init__(self, parent: ctk.CTk, controller: PITAController) -> None:
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        self._crear_interfaz()

    def _crear_interfaz(self) -> None:
        # Título y Subtítulo
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", padx=15, pady=(15, 15))

        ctk.CTkLabel(
            title_frame,
            text="📊 Panel de Control General",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#F8FAFC",
            anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_frame,
            text="Sistema Integrado de Transacciones Académicas y Nómina Docente • Universidad Popular del Cesar",
            font=ctk.CTkFont(size=12),
            text_color="#94A3B8",
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
            kpi_frame, 0, 0, "👨‍🎓 Estudiantes Registrados", str(total_estudiantes), "#3B82F6", "Activos en programas PITA"
        )
        create_stat_card(
            kpi_frame, 0, 1, "⚠️ Alertas EBRA Activas", str(estudiantes_ebra), "#EF4444" if estudiantes_ebra > 0 else "#10B981", "Riesgo académico (< 3.0)"
        )
        create_stat_card(
            kpi_frame, 0, 2, "👨‍🏫 Cuerpo Docente", str(total_profesores), "#8B5CF6", "Planta, Ocasional y Cátedra"
        )
        create_stat_card(
            kpi_frame, 0, 3, "📝 Contratos Docentes", str(total_contratos), "#F59E0B", "Vinculaciones vigentes"
        )

        # ------------------------------------------------------------------
        # Sección Central (Alertas EBRA y Resumen de Nómina)
        # ------------------------------------------------------------------
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=15, pady=5)
        content_frame.grid_columnconfigure((0, 1), weight=1, uniform="content")
        content_frame.grid_rowconfigure(0, weight=1)

        # Panel Izquierdo: Alertas EBRA Destacadas
        ebra_card = ctk.CTkFrame(content_frame, corner_radius=10, fg_color="#0F172A", border_width=1, border_color="#EF4444")
        ebra_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=5)

        header_eb = ctk.CTkFrame(ebra_card, fg_color="transparent")
        header_eb.pack(fill="x", padx=15, pady=(15, 5))

        ctk.CTkLabel(
            header_eb,
            text="⚠️ Estudiantes en Alerta EBRA",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#F87171",
        ).pack(side="left")

        # Badge total
        ctk.CTkLabel(
            header_eb,
            text=f"{estudiantes_ebra} casos",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#EF4444",
        ).pack(side="right")

        ctk.CTkLabel(
            ebra_card,
            text="Estudiantes cuyo promedio acumulado está por debajo de 3.0",
            font=ctk.CTkFont(size=11),
            text_color="#94A3B8",
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
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#34D399",
            ).pack(pady=30)
        else:
            for est in estud_ebra_list:
                item = ctk.CTkFrame(ebra_scroll, fg_color="#451A1D", corner_radius=6, border_width=1, border_color="#7F1D1D")
                item.pack(fill="x", pady=4, padx=5)

                pers = next((p for p in self.controller.personas if getattr(p, "idPersona", None) == getattr(est, "idPersona", None)), None)
                nombre_est = f"{getattr(pers, 'primerNombre', '')} {getattr(pers, 'primerApellido', '')}" if pers else "Estudiante"

                ctk.CTkLabel(
                    item,
                    text=f"{getattr(est, 'codigoEstudiante', 'N/A')} — {nombre_est}",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="#F8FAFC",
                ).pack(side="left", padx=12, pady=8)

                ctk.CTkLabel(
                    item,
                    text=f"Promedio: {getattr(est, 'promedioAcumulado', '0.0')}",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="#F87171",
                ).pack(side="right", padx=12, pady=8)

        # Panel Derecho: Estado de Nómina y Normatividad
        payroll_card = ctk.CTkFrame(content_frame, corner_radius=10, fg_color="#0F172A", border_width=1, border_color="#334155")
        payroll_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=5)

        ctk.CTkLabel(
            payroll_card,
            text="💰 Parámetros Salariales y Normatividad",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#F8FAFC",
        ).pack(anchor="w", padx=15, pady=(15, 5))

        ctk.CTkLabel(
            payroll_card,
            text="Decreto 1279 de 2002 / Acuerdo 027 del 31 de octubre de 2024",
            font=ctk.CTkFont(size=11),
            text_color="#94A3B8",
        ).pack(anchor="w", padx=15, pady=(0, 10))

        pay_info_frame = ctk.CTkFrame(payroll_card, fg_color="transparent")
        pay_info_frame.pack(fill="both", expand=True, padx=15, pady=5)

        smmlv = next((p.valor for p in self.controller.parametros if p.codigo == "SALARIO_MINIMO"), "1423500")
        punto = next((p.valor for p in self.controller.parametros if p.codigo == "VALOR_PUNTO_SALARIAL"), "19850")
        aux_trans = next((p.valor for p in self.controller.parametros if p.codigo == "VALOR_AUXILIO_TRANSPORTE_VIGENTE"), "162000")

        rows = [
            ("💵 SMMLV Vigente:", f"$ {int(float(smmlv)):,} COP" if str(smmlv).replace(".","").isdigit() else smmlv),
            ("📍 Punto Salarial (Dec. 1279):", f"$ {int(float(punto)):,} COP" if str(punto).replace(".","").isdigit() else punto),
            ("🚌 Auxilio Transporte:", f"$ {int(float(aux_trans)):,} COP" if str(aux_trans).replace(".","").isdigit() else aux_trans),
            ("🏥 Salud Trabajador:", "4.0 % (Ingreso Base Cotización)"),
            ("👴 Pensión Trabajador:", "4.0 % (Ingreso Base Cotización)"),
            ("⚖️ Fondo Solidaridad Pensional:", "1.0 % (si IBC ≥ 4 SMMLV)"),
        ]

        for label, val in rows:
            r = ctk.CTkFrame(pay_info_frame, fg_color="#1E293B", corner_radius=6)
            r.pack(fill="x", pady=4, padx=2)
            ctk.CTkLabel(r, text=label, font=ctk.CTkFont(size=11), text_color="#94A3B8").pack(side="left", padx=10, pady=6)
            ctk.CTkLabel(r, text=val, font=ctk.CTkFont(size=11, weight="bold"), text_color="#34D399").pack(side="right", padx=10, pady=6)

    def _crear_kpi_card(
        self, parent: ctk.CTkFrame, row: int, col: int, title: str, value: str, color: str, subtext: str
    ) -> None:
        card = ctk.CTkFrame(parent, corner_radius=10, fg_color="#0F172A", border_width=1, border_color="#334155")
        card.grid(row=row, column=col, sticky="nsew", padx=4, pady=4)

        bar = ctk.CTkFrame(card, fg_color=color, height=4, corner_radius=2)
        bar.pack(fill="x", side="top")

        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#94A3B8",
        ).pack(anchor="w", padx=14, pady=(12, 2))

        ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=color,
        ).pack(anchor="w", padx=14, pady=0)

        ctk.CTkLabel(
            card,
            text=subtext,
            font=ctk.CTkFont(size=10),
            text_color="#64748B",
        ).pack(anchor="w", padx=14, pady=(2, 12))

    def actualizar(self) -> None:
        """Refresca la vista recreando sus componentes."""
        for widget in self.winfo_children():
            widget.destroy()
        self._crear_interfaz()
