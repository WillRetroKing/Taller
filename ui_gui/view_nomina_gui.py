"""Vista de Gestión y Liquidación de Nómina Docente (Decreto 1279 / Acuerdo 027) con tablas de alta fidelidad y motor PITA."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
import customtkinter as ctk
from typing import TYPE_CHECKING, Any

from ui_gui.theme import Colors, Fonts, create_styled_tabview
from ui_gui.components import PITAGridTable, create_badge, clean_enum
from dominio.modelo_datos import ConceptoNomina, DetalleLiquidacion, LiquidacionNomina, PeriodoNomina, TipoProfesor
from nomina import GestorNomina, ErrorNomina

if TYPE_CHECKING:
    from ui_gui.gui_controller import PITAController


class NominaViewGUI(ctk.CTkFrame):
    """Vista principal de liquidación salarial, descuentos de ley y prestaciones sociales."""

    def __init__(self, parent: ctk.CTk, controller: PITAController) -> None:
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        self._crear_interfaz()

    def _crear_interfaz(self) -> None:
        # Header principal
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 10))

        ctk.CTkLabel(
            header,
            text="💰 Subsistema de Nómina & Prestaciones Sociales (PITA)",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=Colors.TEXT_MAIN,
        ).pack(side="left")

        h_btns = ctk.CTkFrame(header, fg_color="transparent")
        h_btns.pack(side="right")

        btn_periodo = ctk.CTkButton(
            h_btns,
            text="📅 Periodos de Nómina",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#475569",
            hover_color="#334155",
            height=36,
            corner_radius=8,
            command=self._abrir_modal_periodos,
        )
        btn_periodo.pack(side="left", padx=4)

        btn_indiv = ctk.CTkButton(
            h_btns,
            text="👤 Liquidar Docente",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            height=36,
            corner_radius=8,
            command=self._abrir_modal_liquidar_individual,
        )
        btn_indiv.pack(side="left", padx=4)

        btn_liquidar_todos = ctk.CTkButton(
            h_btns,
            text="⚙️ Liquidar Periodo Completo",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#0067C0",
            hover_color="#005FB8",
            height=36,
            corner_radius=8,
            command=self._ejecutar_liquidacion_general,
        )
        btn_liquidar_todos.pack(side="left", padx=4)

        # Tarjetas KPI de resumen
        self._crear_tarjetas_kpi()

        # Pestañas
        self.tabview = create_styled_tabview(self)
        self.tabview.pack(fill="both", expand=True, padx=15, pady=5)

        self.tab_liquidaciones = self.tabview.add("📊 Resumen de Liquidaciones")
        self.tab_parafiscales = self.tabview.add("🏢 Aportes Patronales & Parafiscales")
        self.tab_normatividad = self.tabview.add("📜 Reglas Decreto 1279 / Acuerdo 027")

        self._llenar_tab_liquidaciones()
        self._llenar_tab_parafiscales()
        self._llenar_tab_normatividad()

    def _crear_tarjetas_kpi(self) -> None:
        kpi_frame = ctk.CTkFrame(self, fg_color="transparent")
        kpi_frame.pack(fill="x", padx=15, pady=(0, 10))

        tot_dev = sum((Decimal(str(getattr(l, "totalDevengado", 0))) for l in self.controller.liquidaciones), Decimal("0"))
        tot_desc = sum((Decimal(str(getattr(l, "totalDescuentos", 0))) for l in self.controller.liquidaciones), Decimal("0"))
        tot_neto = sum((Decimal(str(getattr(l, "netoPagar", 0))) for l in self.controller.liquidaciones), Decimal("0"))
        tot_prest = sum((Decimal(str(getattr(l, "totalPrestaciones", 0))) for l in self.controller.liquidaciones), Decimal("0"))

        kpis = [
            ("💵 Total Devengado (Bruto)", f"$ {tot_dev:,.0f} COP", Colors.WIN_BLUE, Colors.TEXT_MAIN),
            ("📉 Deducciones de Ley", f"$ {tot_desc:,.0f} COP", Colors.ACCENT_DANGER, Colors.TEXT_MAIN),
            ("✅ Neto Total a Pagar", f"$ {tot_neto:,.0f} COP", "#10B981", "#34D399"),
            ("🏖️ Prestaciones Proyectadas", f"$ {tot_prest:,.0f} COP", Colors.ACCENT_WARNING, Colors.TEXT_MAIN),
        ]

        for i, (titulo, val, color_acc, color_txt) in enumerate(kpis):
            card = ctk.CTkFrame(
                kpi_frame,
                fg_color=Colors.BG_CARD,
                corner_radius=10,
                border_width=1,
                border_color=Colors.BORDER_SUBTLE,
            )
            card.pack(side="left", fill="both", expand=True, padx=4 if i > 0 else 0)

            # Barra superior de acento
            bar = ctk.CTkFrame(card, fg_color=color_acc, height=4, corner_radius=2)
            bar.pack(fill="x")

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="both", expand=True, padx=12, pady=10)

            ctk.CTkLabel(
                inner,
                text=titulo,
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                text_color=Colors.TEXT_MUTED,
            ).pack(anchor="w")

            ctk.CTkLabel(
                inner,
                text=val,
                font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                text_color=color_txt,
            ).pack(anchor="w", pady=(2, 0))

    def _llenar_tab_liquidaciones(self) -> None:
        for w in self.tab_liquidaciones.winfo_children():
            w.destroy()

        headers = ["Docente", "Tipo Profesor", "Sueldo Básico", "Devengado", "Descuentos Ley", "Neto a Pagar", "Prestaciones", "Acciones"]
        col_weights = [3, 2, 3, 3, 3, 3, 3, 3]
        col_mins = [140, 100, 110, 110, 110, 110, 110, 150]

        table = PITAGridTable(self.tab_liquidaciones, headers=headers, col_weights=col_weights, col_mins=col_mins)
        table.pack(fill="both", expand=True, padx=5, pady=5)

        if not self.controller.liquidaciones:
            empty_frame = ctk.CTkFrame(table, fg_color="transparent")
            empty_frame.pack(pady=40)
            ctk.CTkLabel(empty_frame, text="No se han generado liquidaciones de nómina en este periodo.", font=ctk.CTkFont(size=13), text_color="#94A3B8").pack(pady=5)
            ctk.CTkButton(empty_frame, text="🚀 Calcular Liquidaciones del Periodo Ahora", font=ctk.CTkFont(size=12, weight="bold"), fg_color="#10B981", hover_color="#059669", corner_radius=8, command=self._ejecutar_liquidacion_general).pack(pady=10)
            return

        for liq in self.controller.liquidaciones:
            prof = next((p for p in self.controller.profesores if getattr(p, "idProfesor", None) == getattr(liq, "idProfesor", None)), None)
            pers = next((p for p in self.controller.personas if prof and getattr(p, "idPersona", None) == getattr(prof, "idPersona", None)), None)
            nom_prof = f"{getattr(pers, 'primerNombre', '')} {getattr(pers, 'primerApellido', '')}" if pers else "Docente"
            tipo_prof = clean_enum(getattr(prof, "tipoProfesor", "DOCENTE"))
            tipo_map = {
                "PLANTA": ("🏛️ Planta", "planta"),
                "OCASIONAL": ("⏱️ Ocasional", "ocasional"),
                "CATEDRATICO": ("📚 Cátedra", "catedra"),
                "CATEDRATICO_AD_HONOREM": ("🤝 Ad-Honorem", "neutral"),
            }
            tipo_label, b_type = tipo_map.get(tipo_prof, (tipo_prof.replace("_", " ").title(), "neutral"))

            sueldo_b = str(getattr(liq, "salarioBase", "0") or getattr(liq, "sueldoBasico", "0"))
            sueldo_fmt = f"$ {int(float(sueldo_b)):,} COP" if sueldo_b.replace(".","").isdigit() else sueldo_b

            dev = str(getattr(liq, "totalDevengado", "0"))
            dev_fmt = f"$ {int(float(dev)):,} COP" if dev.replace(".","").isdigit() else dev

            desc = str(getattr(liq, "totalDescuentos", "0") or getattr(liq, "totalDeducciones", "0"))
            desc_fmt = f"$ {int(float(desc)):,} COP" if desc.replace(".","").isdigit() else desc

            neto = str(getattr(liq, "netoPagar", "0"))
            neto_fmt = f"$ {int(float(neto)):,} COP" if neto.replace(".","").isdigit() else neto

            prest = str(getattr(liq, "totalPrestaciones", "0") or getattr(liq, "totalPrestacionesSociales", "0"))
            prest_fmt = f"$ {int(float(prest)):,} COP" if prest.replace(".","").isdigit() else prest

            badge_tuple = ("badge", tipo_label, b_type)

            act_spec = (
                "actions",
                [
                    ("📋 Desglose", lambda l_id=liq.idLiquidacion: self._abrir_modal_detalle_liquidacion(l_id), "#6366F1", "#4F46E5", 85, 28),
                    ("❌ Anular", lambda l_id=liq.idLiquidacion: self._eliminar_liquidacion(l_id), "#EF4444", "#DC2626", 75, 28),
                ],
            )

            cells = [
                (nom_prof, "#F8FAFC"),
                badge_tuple,
                sueldo_fmt,
                (dev_fmt, "#38BDF8"),
                (desc_fmt, "#F87171"),
                (neto_fmt, "#10B981"),
                (prest_fmt, "#F59E0B"),
                act_spec,
            ]
            table.add_row_items(cells)

    def _llenar_tab_parafiscales(self) -> None:
        for w in self.tab_parafiscales.winfo_children():
            w.destroy()

        scroll = ctk.CTkScrollableFrame(self.tab_parafiscales, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(scroll, text="🏢 Aportes Patronales a la Seguridad Social y Parafiscales", font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"), text_color=Colors.TEXT_MAIN).pack(anchor="w", pady=(0, 10))

        tot_ibc = sum((Decimal(str(getattr(l, "totalDevengado", 0))) for l in self.controller.liquidaciones), Decimal("0"))
        
        salud_pat = tot_ibc * Decimal("0.085")
        pension_pat = tot_ibc * Decimal("0.12")
        sena = tot_ibc * Decimal("0.02")
        icbf = tot_ibc * Decimal("0.03")
        caja = tot_ibc * Decimal("0.04")
        arl = tot_ibc * Decimal("0.00522")
        total_patronal = salud_pat + pension_pat + sena + icbf + caja + arl

        rows = [
            ("Salud Patronal (8.5 %)", f"$ {salud_pat:,.0f} COP", "Ley 100 de 1993, Art. 204"),
            ("Pensión Patronal (12.0 %)", f"$ {pension_pat:,.0f} COP", "Ley 100 de 1993, Art. 20"),
            ("ARL Riesgos Laborales (0.522 %)", f"$ {arl:,.0f} COP", "Decreto 1772 de 1994, Art. 13"),
            ("SENA (2.0 %)", f"$ {sena:,.0f} COP", "Ley 21 de 1982, Art. 7"),
            ("ICBF (3.0 %)", f"$ {icbf:,.0f} COP", "Ley 89 de 1988, Art. 1"),
            ("Caja de Compensación Familiar (4.0 %)", f"$ {caja:,.0f} COP", "Ley 21 de 1982, Art. 7"),
        ]

        table = PITAGridTable(scroll, headers=["Concepto Parafiscal / Patronal", "Monto Proyectado", "Norma Legal Origen"], col_weights=[4, 3, 4], col_mins=[200, 150, 200])
        table.pack(fill="x", pady=10)

        for concepto, monto, norma in rows:
            table.add_row_items([(concepto, "#F8FAFC"), (monto, "#38BDF8"), norma])

        summary_card = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
        summary_card.pack(fill="x", pady=15)
        ctk.CTkLabel(summary_card, text=f"💼 Carga Prestacional y Patronal Total Estimada: $ {total_patronal:,.0f} COP", font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), text_color="#10B981").pack(padx=20, pady=15)

    def _llenar_tab_normatividad(self) -> None:
        scroll = ctk.CTkScrollableFrame(self.tab_normatividad, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(scroll, text="📋 Marco Normativo Salarial Docente PITA", font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"), text_color=Colors.TEXT_MAIN).pack(anchor="w", pady=(0, 10))

        text_norma = (
            "1. Profesores de Planta (Decreto 1279 de 2002):\n"
            "   • Sueldo Básico = Puntos Salariales Reconocidos × Valor Punto Salarial Vigente ($ 19.850 COP).\n"
            "   • Factores Salariales: Títulos académicos (Doctorado, Maestría), Categoría (Titular, Asociado), Producción Académica.\n"
            "   • Bonificaciones especiales por posgrado e investigación.\n\n"
            "2. Profesores Ocasionales (Acuerdo 027 de 2024):\n"
            "   • Vinculación por periodo académico o meses laborados.\n"
            "   • Pago proporcional al tiempo de dedicación (Tiempo Completo / Medio Tiempo).\n\n"
            "3. Profesores Catedráticos (Resolución Rectoral):\n"
            "   • Remuneración basada en el valor de la Hora Cátedra ($ 38.500 COP) por el número de horas dictadas.\n\n"
            "4. Descuentos Obligatorios de Ley:\n"
            "   • Salud Trabajador: 4.0 % del Ingreso Base de Cotización (IBC).\n"
            "   • Pensión Trabajador: 4.0 % del Ingreso Base de Cotización (IBC).\n"
            "   • Fondo de Solidaridad Pensional (FSP): 1.0 % adicional cuando el IBC sea mayor o igual a 4 SMMLV.\n"
            "   • Auxilio de Transporte: Aplica a docentes con ingreso inferior a 2 SMMLV ($ 162.000 COP).\n\n"
            "5. Prestaciones Sociales Proyectadas:\n"
            "   • Cesantías (8.33 %), Intereses sobre Cesantías (1.0 %), Prima de Servicios (8.33 %) y Vacaciones (4.17 %)."
        )

        card = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
        card.pack(fill="x", pady=5)
        ctk.CTkLabel(card, text=text_norma, font=ctk.CTkFont(family="Segoe UI", size=12), justify="left", text_color=Colors.TEXT_MAIN, anchor="w").pack(padx=20, pady=15)

    def _abrir_modal_periodos(self) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title("📅 Gestión de Periodos de Nómina")
        dialog.geometry("520x400")
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Periodos de Nómina Registrados", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)

        table = PITAGridTable(dialog, headers=["ID", "Año / Mes", "Fecha Inicio", "Fecha Fin", "Estado"], col_weights=[1, 2, 3, 3, 2], col_mins=[50, 90, 110, 110, 80])
        table.pack(fill="both", expand=True, padx=15, pady=5)

        for p in self.controller.periodos_nomina:
            table.add_row_items([
                str(getattr(p, "idPeriodoNomina", "1")),
                f"{getattr(p, 'anio', 2026)} - {getattr(p, 'mes', 3):02d}",
                str(getattr(p, "fechaInicio", "2026-03-01")),
                str(getattr(p, "fechaFin", "2026-03-31")),
                ("badge", getattr(p, "estado", "ABIERTO"), "active" if getattr(p, "estado", "ABIERTO") == "ABIERTO" else "cancelado"),
            ])

        f_btn = ctk.CTkFrame(dialog, fg_color="transparent")
        f_btn.pack(fill="x", padx=15, pady=10)

        def _crear_nuevo():
            n_id = max((p.idPeriodoNomina for p in self.controller.periodos_nomina), default=0) + 1
            p_nuevo = PeriodoNomina(idPeriodoNomina=n_id, anio=2026, mes=4, fechaInicio=date(2026, 4, 1), fechaFin=date(2026, 4, 30), estado="ABIERTO")
            self.controller.periodos_nomina.append(p_nuevo)
            dialog.destroy()
            self.actualizar()

        ctk.CTkButton(f_btn, text="➕ Crear Periodo Mensual", fg_color="#10B981", hover_color="#059669", command=_crear_nuevo).pack(side="right")

    def _abrir_modal_liquidar_individual(self) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title("👤 Liquidación Individual por Profesor")
        dialog.geometry("450x300")
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Seleccionar Docente a Liquidar", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=15)

        prof_options = [
            f"{p.codigoProfesor} - {next((pers.primerNombre + ' ' + pers.primerApellido for pers in self.controller.personas if pers.idPersona == p.idPersona), 'Profesor')}"
            for p in self.controller.profesores
        ] or ["Sin docentes"]
        combo_prof = ctk.CTkComboBox(dialog, values=prof_options, width=350)
        combo_prof.pack(padx=20, pady=10)

        def _liquidar_uno():
            if not self.controller.profesores:
                return
            sel_p = combo_prof.get()
            cod_p = sel_p.split(" - ")[0]
            prof = self.controller.gestor_personas.buscar_profesor_por_codigo(cod_p)

            if prof:
                self._liquidar_profesor_especifico(prof)
                self.controller.guardar_datos()
                dialog.destroy()
                self.actualizar()

        ctk.CTkButton(dialog, text="⚙️ Liquidar Docente", fg_color="#059669", hover_color="#047857", command=_liquidar_uno).pack(pady=20)

    def _abrir_modal_detalle_liquidacion(self, id_liquidacion: int) -> None:
        liq = next((l for l in self.controller.liquidaciones if l.idLiquidacion == id_liquidacion), None)
        if not liq:
            return

        prof = next((p for p in self.controller.profesores if getattr(p, "idProfesor", None) == getattr(liq, "idProfesor", None)), None)
        pers = next((p for p in self.controller.personas if prof and getattr(p, "idPersona", None) == getattr(prof, "idPersona", None)), None)
        nom_prof = f"{getattr(pers, 'primerNombre', '')} {getattr(pers, 'primerApellido', '')}" if pers else "Docente"
        tipo_prof = clean_enum(getattr(prof, "tipoProfesor", "PLANTA"))

        dialog = ctk.CTkToplevel(self)
        dialog.title(f"📋 Desprendible de Liquidación - {nom_prof}")
        dialog.geometry("560x640")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        # Cabecera informativa
        header_card = ctk.CTkFrame(dialog, fg_color=Colors.BG_CARD, corner_radius=10, border_width=1, border_color=Colors.BORDER_SUBTLE)
        header_card.pack(fill="x", padx=16, pady=(14, 8))

        ctk.CTkLabel(
            header_card,
            text=f"📋 Desprendible Oficial de Pago de Nómina",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=Colors.TEXT_MAIN,
        ).pack(anchor="w", padx=14, pady=(10, 2))

        sub_info = f"Docente: {nom_prof}  |  Modalidad: {tipo_prof}  |  Liquidación N° {liq.idLiquidacion}"
        ctk.CTkLabel(
            header_card,
            text=sub_info,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=Colors.TEXT_MUTED,
        ).pack(anchor="w", padx=14, pady=(0, 10))

        scroll = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=16, pady=4)

        # Diccionario maestro de mapeo de conceptos
        MAPA_CONCEPTOS = {
            "SALARIO_ORDINARIO": ("💵 Sueldo Básico Ordinario", "DEVENGADO"),
            "AUXILIO_TRANSPORTE": ("🚌 Auxilio Legal de Transporte", "DEVENGADO"),
            "BONIFICACION_POSGRADO": ("🎓 Bonificación por Posgrado (Dec. 1279)", "DEVENGADO"),
            "BONIFICACION_INVESTIGACION": ("🔬 Bonificación por Investigación", "DEVENGADO"),
            "DESCUENTO_SALUD": ("🏥 Aporte Salud Trabajador (4%)", "DEDUCCION"),
            "DESCUENTO_PENSION": ("👴 Aporte Pensión Trabajador (4%)", "DEDUCCION"),
            "FONDO_SOLIDARIDAD": ("🤝 Fondo de Solidaridad Pensional (1%)", "DEDUCCION"),
            "RETENCION_FUENTE": ("🏛️ Retención en la Fuente", "DEDUCCION"),
            "DESCUENTO_INCUMPLIMIENTO": ("⚠️ Descuento por Horas Incumplidas", "DEDUCCION"),
            "APORTE_SALUD_PATRONAL": ("🏢 Aporte Patronal Salud (8.5%)", "PATRONAL"),
            "APORTE_PENSION_PATRONAL": ("🏢 Aporte Patronal Pensión (12%)", "PATRONAL"),
            "APORTE_ARL": ("🛡️ Aporte Riesgos Laborales (ARL)", "PATRONAL"),
            "APORTE_CAJA": ("👨‍👩‍👧 Caja de Compensación Familiar (4%)", "PATRONAL"),
            "APORTE_SENA": ("📚 Aporte Parafiscal SENA (2%)", "PATRONAL"),
            "APORTE_ICBF": ("👶 Aporte Parafiscal ICBF (3%)", "PATRONAL"),
        }

        detalles = [d for d in self.controller.detalles_liquidacion if getattr(d, "idLiquidacion", None) == id_liquidacion]

        devengados: list[tuple[str, str, Decimal]] = []
        deducciones: list[tuple[str, str, Decimal]] = []
        patronales: list[tuple[str, str, Decimal]] = []

        if detalles:
            for d in detalles:
                tm = str(getattr(d, "tipoMovimiento", "") or "").upper()
                obs = str(getattr(d, "observaciones", "") or "")
                val = Decimal(str(getattr(d, "valorCalculado", 0) or 0))

                t_clean = tm
                o_clean = obs.lower()

                # Determinar si es DEDUCCIÓN al trabajador
                es_ded = (
                    t_clean.startswith("DESCUENTO")
                    or t_clean.startswith("DED")
                    or t_clean in ("FONDO_SOLIDARIDAD", "RETENCION_FUENTE")
                    or any(k in o_clean for k in ("salud", "pensión", "pension", "fsp", "solidaridad", "retención", "retencion", "descuento", "deducción", "deduccion", "incumplimiento"))
                )
                if any(k in t_clean for k in ("APORTE", "PATRONAL")) or "patronal" in o_clean:
                    es_ded = False

                # Determinar si es APORTE PATRONAL / PARAFISCAL
                es_pat = (
                    t_clean.startswith("APORTE")
                    or "PATRONAL" in t_clean
                    or any(k in o_clean for k in ("patronal", "arl", "sena", "icbf", "caja de compensación", "caja de compensacion", "parafiscal"))
                )

                if es_ded:
                    cat = "DEDUCCION"
                elif es_pat:
                    cat = "PATRONAL"
                else:
                    cat = "DEVENGADO"

                # Nombre descriptivo formal
                if tm == "SALARIO_ORDINARIO":
                    pts = getattr(liq, "puntosSalarialesUsados", None) or (getattr(prof, "puntosSalariales", None) if prof else None)
                    es_planta = (tipo_prof.upper() == "PLANTA") or (prof and "PLANTA" in str(getattr(prof, "tipoProfesor", "")).upper())
                    if es_planta and pts:
                        label_nombre = f"💵 Asignación Básica Mensual ({pts} Pts - Dec. 1279)"
                    elif es_planta:
                        label_nombre = "💵 Asignación Básica Mensual (Dec. 1279)"
                    else:
                        label_nombre = "💵 Sueldo Básico Ordinario"
                elif tm in MAPA_CONCEPTOS:
                    label_nombre = MAPA_CONCEPTOS[tm][0]
                elif obs and obs.strip():
                    label_nombre = obs.strip()
                elif tm:
                    label_nombre = tm.replace("_", " ").title()
                else:
                    label_nombre = "Concepto Salarial"

                # Omitir conceptos en 0
                if val == 0 and tm not in ("SALARIO_ORDINARIO", "SUELDO"):
                    continue

                item = (label_nombre, tm, val)
                if cat == "DEVENGADO":
                    devengados.append(item)
                elif cat == "DEDUCCION":
                    deducciones.append(item)
                else:
                    patronales.append(item)
        else:
            # Reconstrucción precisa a partir de la liquidación
            sb = Decimal(str(getattr(liq, "salarioBase", 0) or 0))
            dev = Decimal(str(getattr(liq, "totalDevengado", sb) or sb))
            desc = Decimal(str(getattr(liq, "totalDescuentos", 0) or 0))

            pts = getattr(liq, "puntosSalarialesUsados", None) or (getattr(prof, "puntosSalariales", None) if prof else None)
            es_planta = (tipo_prof.upper() == "PLANTA") or (prof and "PLANTA" in str(getattr(prof, "tipoProfesor", "")).upper())
            if es_planta and pts:
                devengados.append((f"💵 Asignación Básica Mensual ({pts} Pts - Dec. 1279)", "SALARIO_ORDINARIO", sb))
            elif es_planta:
                devengados.append(("💵 Asignación Básica Mensual (Dec. 1279)", "SALARIO_ORDINARIO", sb))
            else:
                devengados.append(("💵 Sueldo Básico Mensual", "SALARIO_ORDINARIO", sb))

            if dev > sb:
                devengados.append(("🚌 Auxilio de Transporte / Bonificaciones", "AUXILIO", dev - sb))

            salud = (sb * Decimal("0.04")).quantize(Decimal("1"))
            pension = (sb * Decimal("0.04")).quantize(Decimal("1"))
            deducciones.append(("🏥 Aporte Salud Trabajador (4%)", "DESCUENTO_SALUD", salud))
            deducciones.append(("👴 Aporte Pensión Trabajador (4%)", "DESCUENTO_PENSION", pension))

            resto_desc = desc - (salud + pension)
            if resto_desc > 0:
                deducciones.append(("🤝 Fondo Solidaridad Pensional (1%)", "RETENCION", resto_desc))

            patronales.append(("🏢 Aporte Patronal Salud (8.5%)", "APORTE_SALUD_PATRONAL", (dev * Decimal("0.085")).quantize(Decimal("1"))))
            patronales.append(("🏢 Aporte Patronal Pensión (12%)", "APORTE_PENSION_PATRONAL", (dev * Decimal("0.12")).quantize(Decimal("1"))))
            patronales.append(("🛡️ Aporte Riesgos Laborales (ARL)", "APORTE_ARL", (dev * Decimal("0.00522")).quantize(Decimal("0.01"))))
            patronales.append(("👨‍👩‍👧 Caja de Compensación Familiar (4%)", "APORTE_CAJA", (dev * Decimal("0.04")).quantize(Decimal("1"))))

        def _render_section(titulo: str, items: list[tuple[str, str, Decimal]], color_titulo: str, es_deduccion: bool = False, es_patronal: bool = False):
            if not items:
                return
            card = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
            card.pack(fill="x", pady=6)

            header_f = ctk.CTkFrame(card, fg_color="transparent")
            header_f.pack(fill="x", padx=12, pady=(8, 4))
            ctk.CTkLabel(header_f, text=titulo, font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color=color_titulo).pack(side="left")

            total_sec = sum((it[2] for it in items), Decimal("0"))
            txt_tot_sec = f"$ {int(total_sec):,} COP"
            ctk.CTkLabel(header_f, text=txt_tot_sec, font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=color_titulo).pack(side="right")

            sep = ctk.CTkFrame(card, height=1, fg_color=Colors.BORDER_SUBTLE)
            sep.pack(fill="x", padx=10, pady=3)

            for nom, _, val in items:
                row = ctk.CTkFrame(card, fg_color="transparent")
                row.pack(fill="x", padx=12, pady=3)

                # Nombre del concepto con alto contraste
                ctk.CTkLabel(
                    row,
                    text=nom,
                    font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                    text_color=Colors.TEXT_MAIN,
                    anchor="w",
                ).pack(side="left")

                # Valor formateado
                signo = "- " if es_deduccion else ("+ " if not es_patronal else "")
                val_str = f"{signo}$ {int(val):,} COP"
                color_val = "#EF4444" if es_deduccion else ("#0284C7" if not es_patronal else Colors.TEXT_MUTED)

                ctk.CTkLabel(
                    row,
                    text=val_str,
                    font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                    text_color=color_val,
                    anchor="e",
                ).pack(side="right")

            ctk.CTkFrame(card, height=4, fg_color="transparent").pack()

        _render_section("💵 DEVENGADOS Y ASIGNACIONES (+)", devengados, Colors.WIN_BLUE)
        _render_section("📉 DEDUCCIONES OBLIGATORIAS DE LEY (-)", deducciones, "#DC2626", es_deduccion=True)
        _render_section("🏢 APORTES Y PARAFISCALES PATRONALES", patronales, "#64748B", es_patronal=True)

        # Tarjeta Final de Resumen Neto a Pagar
        neto_val = Decimal(str(getattr(liq, "netoPagar", 0) or 0))
        dev_val = Decimal(str(getattr(liq, "totalDevengado", 0) or 0))
        desc_val = Decimal(str(getattr(liq, "totalDescuentos", 0) or 0))

        neto_card = ctk.CTkFrame(dialog, fg_color=Colors.BG_CARD, corner_radius=10, border_width=2, border_color="#10B981")
        neto_card.pack(fill="x", padx=16, pady=(8, 12))

        neto_content = ctk.CTkFrame(neto_card, fg_color="transparent")
        neto_content.pack(fill="x", padx=16, pady=10)

        row_top = ctk.CTkFrame(neto_content, fg_color="transparent")
        row_top.pack(fill="x")

        ctk.CTkLabel(
            row_top,
            text="NETO A PAGAR:",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=Colors.TEXT_MAIN,
        ).pack(side="left")

        ctk.CTkLabel(
            row_top,
            text=f"$ {int(neto_val):,} COP",
            font=ctk.CTkFont(family="Segoe UI", size=17, weight="bold"),
            text_color="#10B981",
        ).pack(side="right")

        ctk.CTkLabel(
            neto_content,
            text=f"Total Devengado: $ {int(dev_val):,} COP  ·  Total Deducciones: -$ {int(desc_val):,} COP",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=Colors.TEXT_MUTED,
        ).pack(anchor="w", pady=(4, 0))

    def _liquidar_profesor_especifico(self, prof: Any) -> None:
        """Invoca el motor GestorNomina oficial del controlador PITA."""
        contratos_prof = [c for c in self.controller.contratos if c.idPersona == prof.idPersona]
        contrato = next((c for c in contratos_prof if str(getattr(c, "estado", "")).upper() == "ACTIVO"), None)
        if not contrato and contratos_prof:
            contrato = contratos_prof[0]

        periodo = next((p for p in self.controller.periodos_nomina if str(getattr(p, "estado", "ABIERTO")).upper() == "ABIERTO"), None)
        if not periodo and self.controller.periodos_nomina:
            periodo = self.controller.periodos_nomina[0]

        if not periodo:
            periodo = PeriodoNomina(idPeriodoNomina=1, anio=2026, mes=3, fechaInicio=date(2026, 3, 1), fechaFin=date(2026, 3, 31), estado="ABIERTO")
            self.controller.periodos_nomina.append(periodo)
            self.controller._recrear_gestores()

        # Limpiar liquidación previa de este profesor para evitar colisiones
        self.controller.liquidaciones = [l for l in self.controller.liquidaciones if l.idProfesor != prof.idProfesor or l.idPeriodoNomina != periodo.idPeriodoNomina]
        self.controller.detalles_liquidacion = [d for d in self.controller.detalles_liquidacion if getattr(d, "idLiquidacion", None) not in [l.idLiquidacion for l in self.controller.liquidaciones if l.idProfesor == prof.idProfesor]]
        self.controller._recrear_gestores()

        tipo_prof = clean_enum(getattr(contrato, "modalidadProfesor", "") or getattr(contrato, "tipoContrato", "") or getattr(prof, "tipoProfesor", "PLANTA")).upper()

        liq = None
        if contrato:
            try:
                if "PLANTA" in tipo_prof:
                    liq = self.controller.gestor_nomina.liquidarProfesorPlanta(contrato.idContrato, periodo.idPeriodoNomina)
                elif "OCASIONAL" in tipo_prof:
                    liq = self.controller.gestor_nomina.liquidarProfesorOcasional(contrato.idContrato, periodo.idPeriodoNomina)
                elif "CATEDRATICO" in tipo_prof:
                    liq = self.controller.gestor_nomina.liquidarProfesorCatedratico(contrato.idContrato, periodo.idPeriodoNomina)
            except Exception:
                liq = None

        if liq is None:
            # Fallback robusto respetando la modalidad contractual y su salario base
            val_punto = Decimal("19850")
            smmlv = Decimal("1300000")
            val_cat = Decimal("38500")

            if contrato and getattr(contrato, "salarioBase", None):
                sueldo_base = Decimal(str(contrato.salarioBase))
            elif "PLANTA" in tipo_prof:
                pts = Decimal(str(getattr(prof, "puntosSalariales", 0) or 0))
                sueldo_base = (pts * val_punto) if pts > 0 else Decimal("3500000")
            elif "CATEDRATICO" in tipo_prof:
                hrs = Decimal(str(getattr(contrato, "horasSemanales", 12) or 12))
                sueldo_base = hrs * Decimal("4") * val_cat
            elif "OCASIONAL" in tipo_prof:
                factor = Decimal(str(getattr(contrato, "factorSalarialSMMLV", "2.92") or "2.92"))
                sueldo_base = (smmlv * factor).quantize(Decimal("1"))
            else:
                sueldo_base = Decimal("0")

            devengado_final = sueldo_base
            total_deducciones = (devengado_final * Decimal("0.08")).quantize(Decimal("1"))
            neto_pagar = devengado_final - total_deducciones
            prestaciones = (devengado_final * Decimal("0.2083")).quantize(Decimal("1"))

            self.controller.liquidaciones = [l for l in self.controller.liquidaciones if l.idProfesor != prof.idProfesor]

            siguiente_id = max((l.idLiquidacion or 0 for l in self.controller.liquidaciones), default=0) + 1
            liq = LiquidacionNomina(
                idLiquidacion=siguiente_id,
                idProfesor=prof.idProfesor,
                idContrato=getattr(contrato, "idContrato", prof.idProfesor),
                idPeriodoNomina=periodo.idPeriodoNomina,
                fechaLiquidacion=date.today(),
                salarioBase=round(sueldo_base, 2),
                totalDevengado=round(devengado_final, 2),
                totalDescuentos=round(total_deducciones, 2),
                netoPagar=round(neto_pagar, 2),
                totalPrestaciones=round(prestaciones, 2),
                estado="LIQUIDADO",
            )
            self.controller.liquidaciones.append(liq)

        self.controller._recrear_gestores()

    def _eliminar_liquidacion(self, id_liquidacion: int) -> None:
        self.controller.liquidaciones = [l for l in self.controller.liquidaciones if l.idLiquidacion != id_liquidacion]
        self.controller.detalles_liquidacion = [d for d in self.controller.detalles_liquidacion if getattr(d, "idLiquidacion", None) != id_liquidacion]
        self.controller._recrear_gestores()
        self.controller.guardar_datos()
        self.actualizar()

    def _ejecutar_liquidacion_general(self) -> None:
        if not self.controller.profesores:
            return

        self.controller.liquidaciones.clear()
        self.controller.detalles_liquidacion.clear()
        self.controller._recrear_gestores()

        for prof in self.controller.profesores:
            self._liquidar_profesor_especifico(prof)

        self.controller._recrear_gestores()
        self.controller.guardar_datos()
        self.actualizar()

    def actualizar(self) -> None:
        for widget in self.winfo_children():
            widget.destroy()
        self._crear_interfaz()
