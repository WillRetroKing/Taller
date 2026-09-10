"""Vista de Gestión y Liquidación de Nómina Docente (Decreto 1279 / Acuerdo 027) con tablas de alta fidelidad y motor PITA."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
import customtkinter as ctk
from typing import TYPE_CHECKING, Any

from ui_gui.theme import Colors, Fonts, create_styled_tabview
from ui_gui.components import PITAGridTable, create_badge, clean_enum
from dominio.modelo_datos import ConceptoNomina, Contrato, Dedicacion, DetalleLiquidacion, LiquidacionNomina, PeriodoNomina, TipoProfesor
from nomina import GestorNomina, ErrorNomina

if TYPE_CHECKING:
    from ui_gui.gui_controller import PITAController


class NominaViewGUI(ctk.CTkFrame):
    """Vista principal de liquidación salarial, descuentos de ley y prestaciones sociales."""

    def __init__(self, parent: ctk.CTk, controller: PITAController) -> None:
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.periodo_seleccionado_id: int | None = None

        self._crear_interfaz()

    def _crear_interfaz(self) -> None:
        # Header principal
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 6))

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
            text="👤 Liquidar Empleado",
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

        # Barra de Selección y Filtro de Período Activo
        filter_bar = ctk.CTkFrame(self, fg_color="transparent")
        filter_bar.pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkLabel(
            filter_bar,
            text="📅 Período de Nómina Activo:",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=Colors.TEXT_MUTED,
        ).pack(side="left", padx=(0, 8))

        self.combo_periodo_filtro = ctk.CTkComboBox(
            filter_bar,
            width=360,
            values=["Todos los Períodos"],
            command=self._cambiar_periodo_filtro,
        )
        self.combo_periodo_filtro.pack(side="left")

        self.lbl_estado_periodo = ctk.CTkLabel(
            filter_bar,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
        )
        self.lbl_estado_periodo.pack(side="left", padx=12)

        # Contenedor de Tarjetas KPI de resumen
        self.kpi_container = ctk.CTkFrame(self, fg_color="transparent")
        self.kpi_container.pack(fill="x", padx=15, pady=(0, 10))

        # Pestañas
        self.tabview = create_styled_tabview(self)
        self.tabview.pack(fill="both", expand=True, padx=15, pady=5)

        self.tab_liquidaciones = self.tabview.add("📊 Resumen de Liquidaciones")
        self.tab_parafiscales = self.tabview.add("🏢 Aportes Patronales & Parafiscales")
        self.tab_anual = self.tabview.add("📅 Desglose de Nómina Anual")
        self.tab_normatividad = self.tabview.add("📜 Reglas Decreto 1279 / Acuerdo 027")

        self.scroll_parafiscales = ctk.CTkScrollableFrame(self.tab_parafiscales, fg_color="transparent")
        self.scroll_parafiscales.pack(fill="both", expand=True, padx=10, pady=10)

        self.scroll_anual = ctk.CTkScrollableFrame(self.tab_anual, fg_color="transparent")
        self.scroll_anual.pack(fill="both", expand=True, padx=10, pady=10)

        self._llenar_tab_normatividad()
        self.actualizar()

    def _obtener_liquidaciones_filtradas(self) -> list[Any]:
        if not self.periodo_seleccionado_id or self.periodo_seleccionado_id == 0:
            return self.controller.liquidaciones
        return [l for l in self.controller.liquidaciones if getattr(l, "idPeriodoNomina", None) == self.periodo_seleccionado_id]

    def _cambiar_periodo_filtro(self, seleccion: str) -> None:
        if seleccion == "Todos los Períodos" or not seleccion:
            self.periodo_seleccionado_id = None
            if hasattr(self, "lbl_estado_periodo"):
                self.lbl_estado_periodo.configure(text="")
        else:
            try:
                p_id = int(seleccion.split(" - ")[0].replace("#", "").strip())
                self.periodo_seleccionado_id = p_id
                per = next((p for p in self.controller.periodos_nomina if p.idPeriodoNomina == p_id), None)
                if per and hasattr(self, "lbl_estado_periodo"):
                    est = str(getattr(per, "estado", "ABIERTO")).upper()
                    if est == "ABIERTO":
                        self.lbl_estado_periodo.configure(text="● PERÍODO EN PROCESO (ABIERTO)", text_color="#10B981")
                    else:
                        self.lbl_estado_periodo.configure(text="🔒 PERÍODO CERRADO / AUDITADO", text_color="#EF4444")
            except Exception:
                self.periodo_seleccionado_id = None
                if hasattr(self, "lbl_estado_periodo"):
                    self.lbl_estado_periodo.configure(text="")

        self._crear_tarjetas_kpi()
        self._llenar_tab_liquidaciones()
        self._llenar_tab_parafiscales()

    def _crear_tarjetas_kpi(self) -> None:
        if not hasattr(self, "kpi_container"):
            return
        for w in self.kpi_container.winfo_children():
            w.destroy()

        liq_list = self._obtener_liquidaciones_filtradas()
        tot_dev = sum((Decimal(str(getattr(l, "totalDevengado", 0))) for l in liq_list), Decimal("0"))
        tot_desc = sum((Decimal(str(getattr(l, "totalDescuentos", 0))) for l in liq_list), Decimal("0"))
        tot_neto = sum((Decimal(str(getattr(l, "netoPagar", 0))) for l in liq_list), Decimal("0"))
        tot_prest = sum((Decimal(str(getattr(l, "totalPrestaciones", 0))) for l in liq_list), Decimal("0"))

        kpis = [
            ("💵 Total Devengado (Bruto)", f"$ {tot_dev:,.0f} COP", Colors.WIN_BLUE, Colors.TEXT_MAIN),
            ("📉 Deducciones de Ley", f"$ {tot_desc:,.0f} COP", Colors.ACCENT_DANGER, Colors.TEXT_MAIN),
            ("✅ Neto Total a Pagar", f"$ {tot_neto:,.0f} COP", "#10B981", "#34D399"),
            ("🏖️ Prestaciones Proyectadas", f"$ {tot_prest:,.0f} COP", Colors.ACCENT_WARNING, Colors.TEXT_MAIN),
        ]

        for i, (titulo, val, color_acc, color_txt) in enumerate(kpis):
            card = ctk.CTkFrame(
                self.kpi_container,
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

        headers = ["Empleado / Funcionario", "Tipo / Cargo", "Sueldo Básico", "Devengado", "Descuentos Ley", "Neto a Pagar", "Prestaciones", "Acciones"]
        col_weights = [3, 2, 3, 3, 3, 3, 3, 4]
        col_mins = [140, 110, 110, 110, 110, 110, 110, 240]

        table = PITAGridTable(self.tab_liquidaciones, headers=headers, col_weights=col_weights, col_mins=col_mins)
        table.pack(fill="both", expand=True, padx=5, pady=5)

        liq_list = self._obtener_liquidaciones_filtradas()

        if not liq_list:
            empty_frame = ctk.CTkFrame(table, fg_color="transparent")
            empty_frame.pack(pady=40)
            txt_vacio = "No se han generado liquidaciones de nómina en este período." if self.periodo_seleccionado_id else "No se han generado liquidaciones de nómina."
            ctk.CTkLabel(empty_frame, text=txt_vacio, font=ctk.CTkFont(size=13), text_color="#94A3B8").pack(pady=5)
            ctk.CTkButton(empty_frame, text="🚀 Calcular Liquidaciones del Periodo Ahora", font=ctk.CTkFont(size=12, weight="bold"), fg_color="#10B981", hover_color="#059669", corner_radius=8, command=self._ejecutar_liquidacion_general).pack(pady=10)
            return

        for liq in liq_list:
            prof = next((p for p in self.controller.profesores if getattr(p, "idProfesor", None) == getattr(liq, "idProfesor", None)), None)
            if prof:
                pers = next((p for p in self.controller.personas if getattr(p, "idPersona", None) == getattr(prof, "idPersona", None)), None)
                nom_prof = f"{getattr(pers, 'primerNombre', '')} {getattr(pers, 'primerApellido', '')}" if pers else "Docente"
                tipo_prof = clean_enum(getattr(prof, "tipoProfesor", "DOCENTE"))
                tipo_map = {
                    "PLANTA": ("🏛️ Planta", "planta"),
                    "OCASIONAL": ("⏱️ Ocasional", "ocasional"),
                    "CATEDRATICO": ("📚 Cátedra", "catedra"),
                    "CATEDRATICO_AD_HONOREM": ("🤝 Ad-Honorem", "neutral"),
                }
                tipo_label, b_type = tipo_map.get(tipo_prof, (tipo_prof.replace("_", " ").title(), "neutral"))
            else:
                con = next((c for c in self.controller.contratos if c.idContrato == getattr(liq, "idContrato", None)), None)
                pers = next((p for p in self.controller.personas if con and p.idPersona == con.idPersona), None)
                adm = next((a for a in self.controller.administrativos if con and a.idPersona == con.idPersona), None)
                nom_prof = f"{getattr(pers, 'primerNombre', '')} {getattr(pers, 'primerApellido', '')}" if pers else "Administrativo"
                cargo_label = getattr(adm, "cargo", None) or getattr(liq, "categoriaLiquidada", "Administrativo")
                tipo_label = f"👔 {cargo_label}"
                b_type = "info"

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

            per_liq = next((p for p in self.controller.periodos_nomina if p.idPeriodoNomina == getattr(liq, "idPeriodoNomina", None)), None)
            es_cerrado = bool(per_liq and (getattr(per_liq, "estaCerrado", False) or str(getattr(per_liq, "estado", "")).upper() == "CERRADO"))

            acciones_list: list[tuple[Any, ...]] = [
                ("📋 Desglose", lambda l_id=liq.idLiquidacion: self._abrir_modal_detalle_liquidacion(l_id), "#6366F1", "#4F46E5", 85, 28),
            ]
            if not es_cerrado and not getattr(liq, "pagada", False) and str(getattr(liq, "estadoLiquidacion", "")).upper() != "PAGADA":
                acciones_list.append(("🔄 Reliquidar", lambda l_id=liq.idLiquidacion: self._reliquidar_accion(l_id), "#D97706", "#B45309", 85, 28))
            if not es_cerrado:
                acciones_list.append(("❌ Anular", lambda l_id=liq.idLiquidacion: self._eliminar_liquidacion(l_id), "#EF4444", "#DC2626", 75, 28))

            act_spec = ("actions", acciones_list)

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
        if not hasattr(self, "scroll_parafiscales") or not self.scroll_parafiscales.winfo_exists():
            self.scroll_parafiscales = ctk.CTkScrollableFrame(self.tab_parafiscales, fg_color="transparent")
            self.scroll_parafiscales.pack(fill="both", expand=True, padx=10, pady=10)

        scroll = self.scroll_parafiscales
        for w in scroll.winfo_children():
            w.destroy()

        ctk.CTkLabel(scroll, text="🏢 Aportes Patronales a la Seguridad Social y Parafiscales", font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"), text_color=Colors.TEXT_MAIN).pack(anchor="w", pady=(0, 10))

        liq_list = self._obtener_liquidaciones_filtradas()
        tot_ibc = sum((Decimal(str(getattr(l, "totalDevengado", 0))) for l in liq_list), Decimal("0"))
        
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
        txt_costo_titulo = f"💼 Carga Prestacional y Patronal Estimada ({'Período Activo' if self.periodo_seleccionado_id else 'Total Registrado'}): $ {total_patronal:,.0f} COP"
        ctk.CTkLabel(summary_card, text=txt_costo_titulo, font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), text_color="#10B981").pack(padx=20, pady=15)

    def _llenar_tab_normatividad(self) -> None:
        if self.tab_normatividad.winfo_children():
            return

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

    def _cerrar_periodo(self, id_periodo: int, dialog: ctk.CTkToplevel | None = None) -> None:
        try:
            self.controller.gestor_nomina.ciclo_vida.cerrar_periodo_nomina(id_periodo)
            self.controller.guardar_datos()
            if dialog and dialog.winfo_exists():
                dialog.destroy()
                self._abrir_modal_periodos()
            self.actualizar()
        except Exception:
            pass

    def _abrir_modal_periodos(self) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title("📅 Gestión de Periodos de Nómina y Cierre Contable")
        dialog.geometry("740x550")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        hdr = ctk.CTkFrame(dialog, fg_color=Colors.BG_CARD, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
        hdr.pack(fill="x", padx=16, pady=(14, 8))

        ctk.CTkLabel(
            hdr,
            text="📅 Períodos de Nómina y Ciclo Contable PITA",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=Colors.TEXT_MAIN,
        ).pack(anchor="w", padx=14, pady=(10, 2))

        ctk.CTkLabel(
            hdr,
            text="Administración de cortes mensuales, estado de auditoría contable y consolidación de costos.",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=Colors.TEXT_MUTED,
        ).pack(anchor="w", padx=14, pady=(0, 10))

        # Tabla de periodos
        f_tabla = ctk.CTkFrame(dialog, fg_color="transparent")
        f_tabla.pack(fill="both", expand=True, padx=16, pady=4)

        headers = ["ID", "Período", "Rango de Fechas", "Estado", "Costo Total", "Acción Cierre"]
        col_weights = [1, 2, 3, 2, 3, 3]
        col_mins = [40, 90, 140, 90, 120, 130]

        table = PITAGridTable(f_tabla, headers=headers, col_weights=col_weights, col_mins=col_mins)
        table.pack(fill="both", expand=True)

        MESES = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

        for p in self.controller.periodos_nomina:
            pid = p.idPeriodoNomina
            m_idx = getattr(p, "mes", 1) or 1
            m_nom = MESES[m_idx] if 1 <= m_idx <= 12 else f"Mes {m_idx}"
            txt_per = f"{getattr(p, 'anio', 2026)} - {m_nom}"
            fi = str(getattr(p, "fechaInicio", ""))
            ff = str(getattr(p, "fechaFin", ""))
            rango = f"{fi} al {ff}" if (fi and ff) else "Mensual"
            est = str(getattr(p, "estado", "ABIERTO")).upper()

            # Costo acumulado
            costo = getattr(p, "costoTotalPeriodo", None)
            if costo is None:
                liqs_p = [l for l in self.controller.liquidaciones if getattr(l, "idPeriodoNomina", None) == pid]
                costo = sum((Decimal(str(getattr(l, "costoTotalEmpleador", None) or getattr(l, "totalDevengado", 0))) for l in liqs_p), Decimal("0"))
            costo_fmt = f"$ {int(Decimal(str(costo))):,} COP".replace(",", ".")

            if est == "ABIERTO":
                badge_tup = ("badge", "ABIERTO", "active")
                act_col = (
                    "actions",
                    [("🔒 Cerrar Período", lambda p_id=pid: self._cerrar_periodo(p_id, dialog), "#DC2626", "#B91C1C", 115, 26)]
                )
            else:
                badge_tup = ("badge", "CERRADO", "cancelado")
                act_col = ("Auditado / Cerrado", "#94A3B8")

            table.add_row_items([
                str(pid),
                txt_per,
                rango,
                badge_tup,
                (costo_fmt, "#38BDF8"),
                act_col,
            ])

        # Sección inferior: Formulario de Creación de Período Mensual
        f_new = ctk.CTkFrame(dialog, fg_color=Colors.BG_CARD, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
        f_new.pack(fill="x", padx=16, pady=(6, 14))

        f_new_inner = ctk.CTkFrame(f_new, fg_color="transparent")
        f_new_inner.pack(fill="x", padx=14, pady=10)

        ctk.CTkLabel(f_new_inner, text="➕ Crear Nuevo Período:", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color=Colors.TEXT_MAIN).pack(side="left", padx=(0, 15))

        ctk.CTkLabel(f_new_inner, text="Año:", font=ctk.CTkFont(size=11), text_color=Colors.TEXT_MUTED).pack(side="left", padx=(0, 4))
        entry_anio = ctk.CTkEntry(f_new_inner, width=70)
        entry_anio.pack(side="left", padx=(0, 12))
        entry_anio.insert(0, "2026")

        ctk.CTkLabel(f_new_inner, text="Mes:", font=ctk.CTkFont(size=11), text_color=Colors.TEXT_MUTED).pack(side="left", padx=(0, 4))
        mes_opts = [f"{i:02d} - {MESES[i]}" for i in range(1, 13)]
        meses_existentes = [getattr(p, "mes", 0) for p in self.controller.periodos_nomina if getattr(p, "anio", 0) == 2026]
        next_m = 1
        for m in range(1, 13):
            if m not in meses_existentes:
                next_m = m
                break
        combo_mes = ctk.CTkComboBox(f_new_inner, values=mes_opts, width=150)
        combo_mes.pack(side="left", padx=(0, 15))
        combo_mes.set(mes_opts[next_m - 1])

        def _crear_periodo_accion():
            try:
                a_val = int(entry_anio.get().strip())
                m_val = int(combo_mes.get().split(" - ")[0].strip())
                self.controller.gestor_nomina.ciclo_vida.crear_periodo_nomina_mensual(a_val, m_val)
                self.controller.guardar_datos()
                dialog.destroy()
                self._abrir_modal_periodos()
                self.actualizar()
            except Exception:
                dialog.destroy()
                self.actualizar()

        ctk.CTkButton(
            f_new_inner,
            text="➕ Registrar Período",
            font=ctk.CTkFont(weight="bold"),
            fg_color="#10B981",
            hover_color="#059669",
            command=_crear_periodo_accion,
        ).pack(side="right")

    def _abrir_modal_liquidar_individual(self) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title("👤 Liquidación Individual de Nómina")
        dialog.geometry("520x480")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Liquidación Individual de Empleado", font=ctk.CTkFont(size=15, weight="bold")).pack(pady=(15, 8))

        tipo_var = ctk.StringVar(value="Docente")

        def _doc_info(p):
            pers = next((pe for pe in self.controller.personas if pe.idPersona == p.idPersona), None)
            nom = f"{pers.primerNombre} {pers.primerApellido}" if pers else "Profesor"
            has_con = any(c.idPersona == p.idPersona and str(getattr(c, "estado", "")).upper() == "ACTIVO" for c in self.controller.contratos)
            tag = "✅ Contrato Activo" if has_con else "⚠️ Sin Contrato"
            return f"{p.codigoProfesor} - {nom} [{tag}]"

        def _adm_info(a):
            pers = next((pe for pe in self.controller.personas if pe.idPersona == a.idPersona), None)
            nom = f"{pers.primerNombre} {pers.primerApellido}" if pers else "Administrativo"
            has_con = any(c.idPersona == a.idPersona and str(getattr(c, "estado", "")).upper() == "ACTIVO" for c in self.controller.contratos)
            tag = "✅ Contrato Activo" if has_con else "⚠️ Sin Contrato"
            return f"{a.codigoEmpleado or f'ADM-{a.idAdministrativo}'} - {nom} ({a.cargo or 'Cargo'}) [{tag}]"

        prof_options = [_doc_info(p) for p in self.controller.profesores] or ["Sin docentes"]
        adm_options = [_adm_info(a) for a in self.controller.administrativos] or ["Sin administrativos"]

        # Selector de Periodo de Nómina destino
        lbl_per = ctk.CTkLabel(dialog, text="Seleccionar Período de Nómina (Abierto):", font=ctk.CTkFont(size=12, weight="bold"), text_color=Colors.TEXT_MUTED)
        lbl_per.pack(anchor="w", padx=25, pady=(5, 2))

        MESES = ["", "Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        periodos_abiertos = [p for p in self.controller.periodos_nomina if str(getattr(p, "estado", "ABIERTO")).upper() == "ABIERTO"]
        per_options = [f"#{p.idPeriodoNomina} - {getattr(p, 'anio', 2026)} {MESES[getattr(p, 'mes', 1)] if 1 <= getattr(p, 'mes', 1) <= 12 else ''} (Abierto)" for p in periodos_abiertos] or ["Sin periodos abiertos"]

        combo_per = ctk.CTkComboBox(dialog, values=per_options, width=470)
        combo_per.pack(padx=25, pady=(0, 8))
        if self.periodo_seleccionado_id:
            for opt in per_options:
                if opt.startswith(f"#{self.periodo_seleccionado_id} "):
                    combo_per.set(opt)
                    break

        lbl_sel = ctk.CTkLabel(dialog, text="Seleccionar Docente a Liquidar:", font=ctk.CTkFont(size=12, weight="bold"), text_color=Colors.TEXT_MUTED)
        lbl_sel.pack(anchor="w", padx=25, pady=(5, 2))

        lbl_alerta = ctk.CTkLabel(dialog, text="", font=ctk.CTkFont(size=11, weight="bold"), wraplength=460)

        btn_ejecutar = ctk.CTkButton(
            dialog,
            text="⚙️ Ejecutar Liquidación",
            fg_color="#059669",
            hover_color="#047857",
            font=ctk.CTkFont(weight="bold"),
            command=lambda: _liquidar_uno(),
        )

        def _verificar_contrato_seleccionado(seleccion: str):
            if not seleccion or "Sin " in seleccion:
                lbl_alerta.configure(text="", text_color=Colors.TEXT_MUTED)
                btn_ejecutar.configure(state="disabled", fg_color="#475569")
                return

            cod = seleccion.split(" - ")[0].strip()
            tiene_contrato = False
            if tipo_var.get() == "Docente":
                prof = next((p for p in self.controller.profesores if str(p.codigoProfesor) == cod), None)
                if prof:
                    tiene_contrato = any(c.idPersona == prof.idPersona and str(getattr(c, "estado", "")).upper() == "ACTIVO" for c in self.controller.contratos)
            else:
                adm = next((a for a in self.controller.administrativos if str(a.codigoEmpleado) == cod or f"ADM-{a.idAdministrativo}" == cod), None)
                if adm:
                    tiene_contrato = any(c.idPersona == adm.idPersona and str(getattr(c, "estado", "")).upper() == "ACTIVO" for c in self.controller.contratos)

            if tiene_contrato:
                lbl_alerta.configure(
                    text="✅ Contrato laboral vigente confirmado. Cumple requisitos para liquidación.",
                    text_color="#10B981"
                )
                btn_ejecutar.configure(state="normal", fg_color="#059669")
            else:
                lbl_alerta.configure(
                    text="⚠️ Este empleado NO cuenta con un contrato activo registrado.\nDebe formalizar su vinculación en el módulo de Contratos antes de liquidar.",
                    text_color="#EF4444"
                )
                btn_ejecutar.configure(state="disabled", fg_color="#475569")

        combo_emp = ctk.CTkComboBox(dialog, values=prof_options, width=470, command=_verificar_contrato_seleccionado)
        combo_emp.pack(padx=25, pady=(0, 6))

        def _cambiar_tipo(seleccion):
            if seleccion == "Docente":
                lbl_sel.configure(text="Seleccionar Docente a Liquidar:")
                combo_emp.configure(values=prof_options)
                combo_emp.set(prof_options[0] if prof_options else "")
                _verificar_contrato_seleccionado(prof_options[0] if prof_options else "")
            else:
                lbl_sel.configure(text="Seleccionar Administrativo a Liquidar:")
                combo_emp.configure(values=adm_options)
                combo_emp.set(adm_options[0] if adm_options else "")
                _verificar_contrato_seleccionado(adm_options[0] if adm_options else "")

        seg = ctk.CTkSegmentedButton(dialog, values=["Docente", "Administrativo"], variable=tipo_var, command=_cambiar_tipo)
        seg.pack(padx=25, pady=6)

        lbl_alerta.pack(padx=25, pady=(4, 10))

        def _liquidar_uno():
            sel_p = combo_per.get()
            target_pid = None
            if sel_p and sel_p.startswith("#"):
                try:
                    target_pid = int(sel_p.split(" - ")[0].replace("#", "").strip())
                except Exception:
                    pass

            sel = combo_emp.get()
            cod = sel.split(" - ")[0].strip()
            ok = False
            msg = ""
            if tipo_var.get() == "Docente":
                prof = self.controller.gestor_personas.buscar_profesor_por_codigo(cod)
                if not prof:
                    prof = next((p for p in self.controller.profesores if str(p.codigoProfesor) == cod), None)
                if prof:
                    ok, msg = self._liquidar_profesor_especifico(prof, target_pid)
            else:
                adm = next((a for a in self.controller.administrativos if str(a.codigoEmpleado) == cod or f"ADM-{a.idAdministrativo}" == cod), None)
                if adm:
                    ok, msg = self._liquidar_administrativo_especifico(adm, target_pid)

            if ok:
                self.controller.guardar_datos()
                dialog.destroy()
                self.actualizar()
            else:
                lbl_alerta.configure(text=f"❌ No se pudo liquidar: {msg}", text_color="#EF4444")

        btn_ejecutar.pack(pady=10)
        _verificar_contrato_seleccionado(prof_options[0] if prof_options else "")

    def _abrir_modal_detalle_liquidacion(self, id_liquidacion: int) -> None:
        liq = next((l for l in self.controller.liquidaciones if l.idLiquidacion == id_liquidacion), None)
        if not liq:
            return

        prof = next((p for p in self.controller.profesores if getattr(p, "idProfesor", None) is not None and getattr(p, "idProfesor", None) == getattr(liq, "idProfesor", None)), None) if getattr(liq, "idProfesor", None) is not None else None
        con = next((c for c in self.controller.contratos if c.idContrato == getattr(liq, "idContrato", None)), None)
        adm = None
        pers = None

        if prof:
            pers = next((p for p in self.controller.personas if getattr(p, "idPersona", None) == getattr(prof, "idPersona", None)), None)
            nom_empleado = f"{getattr(pers, 'primerNombre', '')} {getattr(pers, 'primerApellido', '')}" if pers else "Docente"
            tipo_prof = clean_enum(getattr(prof, "tipoProfesor", "PLANTA"))
            sub_info = f"Docente: {nom_empleado}  |  Modalidad: {tipo_prof}  |  Liquidación N° {liq.idLiquidacion}"
        else:
            tipo_prof = "ADMINISTRATIVO"
            if con:
                adm = next((a for a in self.controller.administrativos if a.idPersona == con.idPersona), None)
                pers = next((p for p in self.controller.personas if p.idPersona == con.idPersona), None)
            if not adm and getattr(liq, "categoriaLiquidada", None):
                adm = next((a for a in self.controller.administrativos if getattr(a, "cargo", None) == getattr(liq, "categoriaLiquidada", None)), None)
                if adm and not pers:
                    pers = next((p for p in self.controller.personas if p.idPersona == adm.idPersona), None)
            if not adm and self.controller.administrativos:
                adm = self.controller.administrativos[0]
                if not pers:
                    pers = next((p for p in self.controller.personas if p.idPersona == adm.idPersona), None)
            nom_empleado = f"{getattr(pers, 'primerNombre', '')} {getattr(pers, 'primerApellido', '')}" if pers else "Funcionario Administrativo"
            cargo_txt = getattr(adm, "cargo", None) or getattr(liq, "categoriaLiquidada", "Administrativo")
            sub_info = f"Funcionario: {nom_empleado}  |  Cargo: {cargo_txt}  |  Liquidación N° {liq.idLiquidacion}"

        # 1. Resolver período de nómina liquidado
        id_periodo = getattr(liq, "idPeriodoNomina", None)
        periodo_obj = next((p for p in self.controller.periodos_nomina if getattr(p, "idPeriodoNomina", None) == id_periodo), None)

        MESES = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

        if periodo_obj and getattr(periodo_obj, "mes", None) and getattr(periodo_obj, "anio", None):
            mes_idx = int(periodo_obj.mes)
            mes_nom = MESES[mes_idx] if 1 <= mes_idx <= 12 else f"Mes {mes_idx}"
            txt_periodo = f"{mes_nom} {periodo_obj.anio}"
            fi = getattr(periodo_obj, "fechaInicio", None)
            ff = getattr(periodo_obj, "fechaFin", None)
            if fi and ff:
                try:
                    fi_str = str(fi).split()[0]
                    ff_str = str(ff).split()[0]
                    fi_p = fi_str.split("-")
                    ff_p = ff_str.split("-")
                    if len(fi_p) == 3 and len(ff_p) == 3:
                        txt_rango = f"{fi_p[2]}/{fi_p[1]}/{fi_p[0]} - {ff_p[2]}/{ff_p[1]}/{ff_p[0]}"
                    else:
                        txt_rango = f"{fi_str} - {ff_str}"
                    txt_periodo_full = f"{txt_periodo}  ·  {txt_rango}"
                except Exception:
                    txt_periodo_full = f"{txt_periodo}  ·  {fi} - {ff}"
            else:
                txt_periodo_full = txt_periodo
        else:
            txt_periodo_full = f"Periodo N° {id_periodo or 1}"

        # 2. Información Salarial y Base de Cotización (IBC)
        categoria_doc = getattr(liq, "categoriaLiquidada", None) or (getattr(prof, "categoriaDocente", None) if prof else None) or "Titular"
        pts_doc = getattr(liq, "puntosSalarialesUsados", None) or (getattr(prof, "puntosSalariales", None) if prof else None) or 450
        valor_pto = getattr(liq, "valorPuntoUsado", None) or 23924
        ibc_val = Decimal(str(getattr(liq, "baseCotizacionSeguridadSocial", None) or getattr(liq, "salarioBase", None) or getattr(liq, "totalDevengado", 0) or 0))

        pts_int = int(float(pts_doc)) if pts_doc else 0
        val_pto_int = int(float(valor_pto)) if valor_pto else 0

        dialog = ctk.CTkToplevel(self)
        dialog.title(f"📋 Desprendible de Liquidación - {nom_empleado}")
        dialog.geometry("580x680")
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

        ctk.CTkLabel(
            header_card,
            text=sub_info,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=Colors.TEXT_MUTED,
        ).pack(anchor="w", padx=14, pady=(0, 2))

        ctk.CTkLabel(
            header_card,
            text=f"📅 Período Liquidado: {txt_periodo_full}",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=Colors.WIN_BLUE,
        ).pack(anchor="w", padx=14, pady=(0, 10))

        scroll = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=16, pady=4)

        # Diccionario maestro de mapeo de conceptos
        MAPA_CONCEPTOS = {
            "SALARIO_ORDINARIO": ("Asignación Básica Mensual", "DEVENGADO"),
            "AUXILIO_TRANSPORTE": ("Auxilio Legal de Transporte", "DEVENGADO"),
            "BONIFICACION_POSGRADO": ("Bonificación por Posgrado (Dec. 1279)", "DEVENGADO"),
            "BONIFICACION_INVESTIGACION": ("Bonificación por Investigación", "DEVENGADO"),
            "DESCUENTO_SALUD": ("Aporte Salud Trabajador (4%)", "DEDUCCION"),
            "DESCUENTO_PENSION": ("Aporte Pensión Trabajador (4%)", "DEDUCCION"),
            "FONDO_SOLIDARIDAD": ("Fondo de Solidaridad Pensional (1%)", "DEDUCCION"),
            "RETENCION_FUENTE": ("Retención en la Fuente", "DEDUCCION"),
            "DESCUENTO_ESTAMPILLA": ("Descuento Estampilla", "DEDUCCION"),
            "DESCUENTO_INCUMPLIMIENTO": ("Descuento por Horas Incumplidas", "DEDUCCION"),
            "APORTE_SALUD_PATRONAL": ("Salud Patronal (8.5%)", "PATRONAL"),
            "APORTE_PENSION_PATRONAL": ("Pensión Patronal (12%)", "PATRONAL"),
            "APORTE_ARL": ("Aporte Riesgos Laborales (ARL)", "PATRONAL"),
            "APORTE_CAJA": ("Caja de Compensación Familiar (4%)", "PATRONAL"),
            "APORTE_SENA": ("Aporte Parafiscal SENA (2%)", "PATRONAL"),
            "APORTE_ICBF": ("Aporte Parafiscal ICBF (3%)", "PATRONAL"),
        }

        detalles = [d for d in self.controller.detalles_liquidacion if getattr(d, "idLiquidacion", None) == id_liquidacion]

        devengados: list[tuple[str, str, Decimal]] = []
        deducciones: list[tuple[str, str, Decimal]] = []
        patronales: list[tuple[str, str, Decimal]] = []

        es_planta = bool(prof and (tipo_prof.upper() == "PLANTA" or "PLANTA" in str(getattr(prof, "tipoProfesor", "")).upper()))
        val_pto_str = f"${val_pto_int:,}".replace(",", ".")
        label_asignacion_basica = f"Asignación Básica Mensual ({pts_int} pts × {val_pto_str})" if (es_planta and pts_int > 0) else ("Asignación Básica Mensual (Dec. 1279)" if es_planta else "Sueldo Básico Ordinario")

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
                    label_nombre = label_asignacion_basica
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

            devengados.append((label_asignacion_basica, "SALARIO_ORDINARIO", sb))

            aux_transporte = getattr(liq, "valorAuxilioTransporteCotizado", 0) or (dev - sb if dev > sb else 0)
            if Decimal(str(aux_transporte)) > 0:
                devengados.append(("Auxilio Legal de Transporte", "AUXILIO_TRANSPORTE", Decimal(str(aux_transporte))))
            elif dev > sb:
                devengados.append(("Bonificaciones / Devengados Adicionales", "BONIFICACION", dev - sb))

            salud = Decimal(str(getattr(liq, "descuentoSalud", None) or (ibc_val * Decimal("0.04")).quantize(Decimal("1"))))
            pension = Decimal(str(getattr(liq, "descuentoPension", None) or (ibc_val * Decimal("0.04")).quantize(Decimal("1"))))
            deducciones.append(("Aporte Salud Trabajador (4%)", "DESCUENTO_SALUD", salud))
            deducciones.append(("Aporte Pensión Trabajador (4%)", "DESCUENTO_PENSION", pension))

            fsp = getattr(liq, "fondoSolidaridadPensional", None)
            if fsp and Decimal(str(fsp)) > 0:
                deducciones.append(("Fondo de Solidaridad Pensional (1%)", "FONDO_SOLIDARIDAD", Decimal(str(fsp))))
            
            ret = getattr(liq, "retencionFuente", None)
            if ret and Decimal(str(ret)) > 0:
                deducciones.append(("Retención en la Fuente", "RETENCION_FUENTE", Decimal(str(ret))))

            est = getattr(liq, "otrosDescuentos", None)
            if est and Decimal(str(est)) > 0:
                deducciones.append(("Descuento Estampilla", "DESCUENTO_ESTAMPILLA", Decimal(str(est))))
            else:
                resto_desc = desc - (salud + pension + (Decimal(str(fsp)) if fsp else Decimal("0")) + (Decimal(str(ret)) if ret else Decimal("0")))
                if resto_desc > 0:
                    deducciones.append(("Descuento Estampilla", "DESCUENTO_ESTAMPILLA", resto_desc))

            # Aportes patronales
            ap_salud = getattr(liq, "aportePatronalSalud", None)
            if ap_salud is not None and Decimal(str(ap_salud)) > 0:
                patronales.append(("Salud Patronal (8.5%)", "APORTE_SALUD_PATRONAL", Decimal(str(ap_salud))))
            elif prof:
                patronales.append(("Salud Patronal (8.5%)", "APORTE_SALUD_PATRONAL", (dev * Decimal("0.085")).quantize(Decimal("1"))))

            ap_pension = getattr(liq, "aportePatronalPension", None) or (ibc_val * Decimal("0.12")).quantize(Decimal("1"))
            patronales.append(("Pensión Patronal (12%)", "APORTE_PENSION_PATRONAL", Decimal(str(ap_pension))))

            ap_arl = getattr(liq, "aporteRiesgosLaborales", None) or (ibc_val * Decimal("0.00522")).quantize(Decimal("0.01"))
            patronales.append(("Aporte Riesgos Laborales (ARL)", "APORTE_ARL", Decimal(str(ap_arl))))

            ap_caja = getattr(liq, "aporteCajaCompensacion", None) or (ibc_val * Decimal("0.04")).quantize(Decimal("1"))
            patronales.append(("Caja de Compensación Familiar (4%)", "APORTE_CAJA", Decimal(str(ap_caja))))

            ap_sena = getattr(liq, "aportePatronalSENA", None)
            if ap_sena and Decimal(str(ap_sena)) > 0:
                patronales.append(("Aporte Parafiscal SENA (2%)", "APORTE_SENA", Decimal(str(ap_sena))))

            ap_icbf = getattr(liq, "aportePatronalICBF", None)
            if ap_icbf and Decimal(str(ap_icbf)) > 0:
                patronales.append(("Aporte Parafiscal ICBF (3%)", "APORTE_ICBF", Decimal(str(ap_icbf))))

        def _render_section(titulo: str, items: list[tuple[str, str, Decimal]], color_titulo: str, es_deduccion: bool = False, es_patronal: bool = False, base_ibc: Decimal | None = None):
            if not items:
                return
            card = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
            card.pack(fill="x", pady=6)

            header_f = ctk.CTkFrame(card, fg_color="transparent")
            header_f.pack(fill="x", padx=12, pady=(8, 4))
            ctk.CTkLabel(header_f, text=titulo, font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color=color_titulo).pack(side="left")

            total_sec = sum((it[2] for it in items), Decimal("0"))
            txt_tot_sec = f"$ {int(round(total_sec)):,} COP".replace(",", ".")
            ctk.CTkLabel(header_f, text=txt_tot_sec, font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=color_titulo).pack(side="right")

            sep = ctk.CTkFrame(card, height=1, fg_color=Colors.BORDER_SUBTLE)
            sep.pack(fill="x", padx=10, pady=3)

            # Si es sección de deducciones y se provee IBC, mostrarlo destacado para auditoría
            if es_deduccion and base_ibc is not None:
                row_ibc = ctk.CTkFrame(card, fg_color="transparent")
                row_ibc.pack(fill="x", padx=12, pady=2)
                ctk.CTkLabel(row_ibc, text="IBC Seguridad Social (Base Cotización):", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=Colors.TEXT_MUTED).pack(side="left")
                ctk.CTkLabel(row_ibc, text=f"$ {int(round(base_ibc)):,} COP".replace(",", "."), font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=Colors.TEXT_MAIN).pack(side="right")
                ctk.CTkFrame(card, height=1, fg_color=Colors.BORDER_SUBTLE).pack(fill="x", padx=10, pady=3)

            for nom, _, val in items:
                row = ctk.CTkFrame(card, fg_color="transparent")
                row.pack(fill="x", padx=12, pady=3)

                ctk.CTkLabel(
                    row,
                    text=nom,
                    font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                    text_color=Colors.TEXT_MAIN,
                    anchor="w",
                ).pack(side="left")

                signo = "- " if es_deduccion else ("+ " if not es_patronal else "")
                val_str = f"{signo}$ {int(round(val)):,} COP".replace(",", ".")
                color_val = "#EF4444" if es_deduccion else ("#0284C7" if not es_patronal else Colors.TEXT_MUTED)

                ctk.CTkLabel(
                    row,
                    text=val_str,
                    font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                    text_color=color_val,
                    anchor="e",
                ).pack(side="right")

            ctk.CTkFrame(card, height=4, fg_color="transparent").pack()

        # 1. Devengados y 2. Deducciones
        _render_section("DEVENGADOS Y ASIGNACIONES (+)", devengados, Colors.WIN_BLUE)
        _render_section("DEDUCCIONES OBLIGATORIAS DE LEY (-)", deducciones, "#DC2626", es_deduccion=True, base_ibc=ibc_val)

        # 3. Costo Total Empleador (UPC)
        asig_basica_val = Decimal(str(getattr(liq, "totalDevengado", None) or getattr(liq, "salarioBase", 0) or 0))
        tot_patronal = sum((it[2] for it in patronales), Decimal("0"))
        prest_val = Decimal(str(getattr(liq, "totalPrestaciones", 0) or 0))
        tot_costo_upc = getattr(liq, "costoTotalEmpleador", None)
        if tot_costo_upc is not None:
            tot_costo_upc = Decimal(str(tot_costo_upc))
        else:
            tot_costo_upc = asig_basica_val + tot_patronal + prest_val

        card_costo = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
        card_costo.pack(fill="x", pady=6)

        hdr_costo = ctk.CTkFrame(card_costo, fg_color="transparent")
        hdr_costo.pack(fill="x", padx=12, pady=(8, 4))
        ctk.CTkLabel(hdr_costo, text="COSTO TOTAL EMPLEADOR (UPC)", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color="#D97706").pack(side="left")
        ctk.CTkLabel(hdr_costo, text=f"$ {int(tot_costo_upc):,} COP".replace(",", "."), font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color="#D97706").pack(side="right")

        ctk.CTkFrame(card_costo, height=1, fg_color=Colors.BORDER_SUBTLE).pack(fill="x", padx=10, pady=3)

        # Fila Asignación Básica / Devengados
        row_ab = ctk.CTkFrame(card_costo, fg_color="transparent")
        row_ab.pack(fill="x", padx=12, pady=3)
        lbl_costo_dev = "Asignación Básica Devengada" if prof else "Sueldo y Devengados del Empleado"
        ctk.CTkLabel(row_ab, text=lbl_costo_dev, font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=Colors.TEXT_MAIN).pack(side="left")
        ctk.CTkLabel(row_ab, text=f"$ {int(asig_basica_val):,} COP".replace(",", "."), font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=Colors.WIN_BLUE).pack(side="right")

        for nom, _, val in patronales:
            row_p = ctk.CTkFrame(card_costo, fg_color="transparent")
            row_p.pack(fill="x", padx=12, pady=3)
            ctk.CTkLabel(row_p, text=nom, font=ctk.CTkFont(family="Segoe UI", size=11), text_color=Colors.TEXT_MUTED).pack(side="left")
            ctk.CTkLabel(row_p, text=f"$ {int(val):,} COP".replace(",", "."), font=ctk.CTkFont(family="Segoe UI", size=11), text_color=Colors.TEXT_MUTED).pack(side="right")

        if prest_val > 0:
            row_pr = ctk.CTkFrame(card_costo, fg_color="transparent")
            row_pr.pack(fill="x", padx=12, pady=3)
            ctk.CTkLabel(row_pr, text="Provisión Prestaciones Sociales (Cesantías, Primas, Vac.)", font=ctk.CTkFont(family="Segoe UI", size=11), text_color=Colors.TEXT_MUTED).pack(side="left")
            ctk.CTkLabel(row_pr, text=f"$ {int(prest_val):,} COP".replace(",", "."), font=ctk.CTkFont(family="Segoe UI", size=11), text_color=Colors.TEXT_MUTED).pack(side="right")

        ctk.CTkFrame(card_costo, height=1, fg_color=Colors.BORDER_SUBTLE).pack(fill="x", padx=10, pady=3)

        row_tot = ctk.CTkFrame(card_costo, fg_color="transparent")
        row_tot.pack(fill="x", padx=12, pady=(3, 6))
        ctk.CTkLabel(row_tot, text="TOTAL COSTO UPC", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=Colors.TEXT_MAIN).pack(side="left")
        ctk.CTkLabel(row_tot, text=f"$ {int(tot_costo_upc):,} COP".replace(",", "."), font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color=Colors.WIN_BLUE).pack(side="right")

        # 4. Información Salarial y Normativa (Docente Dec. 1279 vs Administrativo CST)
        card_escalafon = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
        card_escalafon.pack(fill="x", pady=6)

        hdr_esc = ctk.CTkFrame(card_escalafon, fg_color="transparent")
        hdr_esc.pack(fill="x", padx=12, pady=(8, 4))
        if prof:
            ctk.CTkLabel(hdr_esc, text="INFORMACIÓN SALARIAL DOCENTE (DECRETO 1279)", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color=Colors.WIN_BLUE).pack(side="left")
            ctk.CTkFrame(card_escalafon, height=1, fg_color=Colors.BORDER_SUBTLE).pack(fill="x", padx=10, pady=3)

            calc_str = f"{pts_int} pts × ${val_pto_int:,} COP".replace(",", ".") if (pts_int > 0 and val_pto_int > 0) else "N/A"

            rows_info = [
                ("Categoría Docente:", str(categoria_doc)),
                ("Total Puntos Salariales:", f"{pts_int} pts" if pts_int > 0 else "N/A"),
                ("Valor Punto Salarial:", f"$ {val_pto_int:,} COP".replace(",", ".") if val_pto_int > 0 else "N/A"),
                ("Cálculo Asignación Básica:", calc_str),
                ("IBC Seguridad Social:", f"$ {int(ibc_val):,} COP".replace(",", ".")),
            ]
        else:
            ctk.CTkLabel(hdr_esc, text="INFORMACIÓN LABORAL Y SALARIAL (CST / LEY 100)", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color="#10B981").pack(side="left")
            ctk.CTkFrame(card_escalafon, height=1, fg_color=Colors.BORDER_SUBTLE).pack(fill="x", padx=10, pady=3)

            sueldo_adm = getattr(liq, "salarioBase", None) or (getattr(adm, "salarioBase", None) if adm else None) or 0
            aux_adm = getattr(liq, "valorAuxilioTransporteCotizado", 0) or 0
            sueldo_int = int(float(sueldo_adm)) if sueldo_adm else 0
            aux_int = int(float(aux_adm)) if aux_adm else 0
            aux_str = f"$ {aux_int:,} COP".replace(",", ".") if aux_int > 0 else "No Aplica (> 2 SMMLV)"

            rows_info = [
                ("Cargo Institucional:", str(getattr(adm, "cargo", None) or getattr(liq, "categoriaLiquidada", "Administrativo"))),
                ("Dependencia Adscrita:", str(getattr(adm, "dependencia", "Administración Central") if adm else "Administración Central")),
                ("Régimen y Tipo Vinculación:", f"CST / {getattr(adm, 'tipoContratacion', 'Contrato Laboral') if adm else 'Contrato'}"),
                ("Sueldo Básico Ordinario:", f"$ {sueldo_int:,} COP".replace(",", ".")),
                ("Auxilio Legal Transporte:", aux_str),
                ("IBC Seguridad Social:", f"$ {int(float(ibc_val)):,} COP".replace(",", ".")),
            ]

        for lbl, val_txt in rows_info:
            r = ctk.CTkFrame(card_escalafon, fg_color="transparent")
            r.pack(fill="x", padx=12, pady=2)
            ctk.CTkLabel(r, text=lbl, font=ctk.CTkFont(family="Segoe UI", size=11), text_color=Colors.TEXT_MUTED).pack(side="left")
            ctk.CTkLabel(r, text=val_txt, font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=Colors.TEXT_MAIN).pack(side="right")
        ctk.CTkFrame(card_escalafon, height=4, fg_color="transparent").pack()

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

        footer_modal = ctk.CTkFrame(dialog, fg_color="transparent")
        footer_modal.pack(fill="x", padx=16, pady=(0, 12))

        per_obj = next((p for p in self.controller.periodos_nomina if p.idPeriodoNomina == getattr(liq, "idPeriodoNomina", None)), None)
        es_cerr = bool(per_obj and (getattr(per_obj, "estaCerrado", False) or str(getattr(per_obj, "estado", "")).upper() == "CERRADO"))
        if not es_cerr and not getattr(liq, "pagada", False) and str(getattr(liq, "estadoLiquidacion", "")).upper() != "PAGADA":
            def _hacer_reliquidacion():
                dialog.destroy()
                self._reliquidar_accion(id_liquidacion)

            ctk.CTkButton(
                footer_modal,
                text="🔄 Reliquidar Nómina",
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                fg_color="#D97706",
                hover_color="#B45309",
                command=_hacer_reliquidacion,
            ).pack(side="left")

        ctk.CTkButton(
            footer_modal,
            text="Cerrar",
            fg_color="#475569",
            hover_color="#334155",
            width=90,
            command=dialog.destroy,
        ).pack(side="right")

    def _liquidar_profesor_especifico(self, prof: Any, id_periodo: int | None = None) -> tuple[bool, str]:
        """Invoca el motor GestorNomina oficial para un profesor con contrato activo."""
        contratos_prof = [c for c in self.controller.contratos if c.idPersona == prof.idPersona]
        contrato = next((c for c in contratos_prof if str(getattr(c, "estado", "")).upper() == "ACTIVO"), None)
        if not contrato:
            return False, "El docente no cuenta con un contrato activo registrado en el sistema."

        periodo = None
        if id_periodo:
            periodo = next((p for p in self.controller.periodos_nomina if p.idPeriodoNomina == id_periodo), None)
        if not periodo:
            periodo = next((p for p in self.controller.periodos_nomina if str(getattr(p, "estado", "ABIERTO")).upper() == "ABIERTO"), None)
        if not periodo and self.controller.periodos_nomina:
            periodo = self.controller.periodos_nomina[0]

        if not periodo:
            periodo = PeriodoNomina(idPeriodoNomina=1, anio=2026, mes=3, fechaInicio=date(2026, 3, 1), fechaFin=date(2026, 3, 31), estado="ABIERTO")
            self.controller.periodos_nomina.append(periodo)
            self.controller._recrear_gestores()

        # Limpiar liquidación previa de este profesor para evitar colisiones
        ids_previos = [l.idLiquidacion for l in self.controller.liquidaciones if l.idProfesor == prof.idProfesor and l.idPeriodoNomina == periodo.idPeriodoNomina]
        if ids_previos:
            self.controller.liquidaciones = [l for l in self.controller.liquidaciones if l.idLiquidacion not in ids_previos]
            self.controller.detalles_liquidacion = [d for d in self.controller.detalles_liquidacion if getattr(d, "idLiquidacion", None) not in ids_previos]
            self.controller._recrear_gestores()

        tipo_prof = clean_enum(getattr(contrato, "modalidadProfesor", "") or getattr(contrato, "tipoContrato", "") or getattr(prof, "tipoProfesor", "PLANTA")).upper()

        liq = None
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
            # Fallback respetando estrictamente el contrato activo existente
            val_punto = Decimal("19850")
            smmlv = Decimal("1300000")
            val_cat = Decimal("38500")

            if getattr(contrato, "salarioBase", None):
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

            self.controller.liquidaciones = [l for l in self.controller.liquidaciones if l.idProfesor != prof.idProfesor or l.idPeriodoNomina != periodo.idPeriodoNomina]

            siguiente_id = max((l.idLiquidacion or 0 for l in self.controller.liquidaciones), default=0) + 1
            liq = LiquidacionNomina(
                idLiquidacion=siguiente_id,
                idProfesor=prof.idProfesor,
                idContrato=contrato.idContrato,
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
        return True, "Docente liquidado exitosamente."

    def _liquidar_administrativo_especifico(self, adm: Any, id_periodo: int | None = None) -> tuple[bool, str]:
        """Invoca el motor GestorNomina para personal administrativo con contrato activo."""
        contratos_adm = [c for c in self.controller.contratos if c.idPersona == adm.idPersona]
        contrato = next((c for c in contratos_adm if str(getattr(c, "estado", "")).upper() == "ACTIVO"), None)
        if not contrato:
            return False, "El funcionario administrativo no cuenta con un contrato activo registrado en el sistema."

        periodo = None
        if id_periodo:
            periodo = next((p for p in self.controller.periodos_nomina if p.idPeriodoNomina == id_periodo), None)
        if not periodo:
            periodo = next((p for p in self.controller.periodos_nomina if str(getattr(p, "estado", "ABIERTO")).upper() == "ABIERTO"), None)
        if not periodo and self.controller.periodos_nomina:
            periodo = self.controller.periodos_nomina[0]

        if not periodo:
            periodo = PeriodoNomina(idPeriodoNomina=1, anio=2026, mes=3, fechaInicio=date(2026, 3, 1), fechaFin=date(2026, 3, 31), estado="ABIERTO")
            self.controller.periodos_nomina.append(periodo)
            self.controller._recrear_gestores()

        # Limpiar liquidación previa de este contrato
        ids_previos = [l.idLiquidacion for l in self.controller.liquidaciones if l.idContrato == contrato.idContrato and l.idPeriodoNomina == periodo.idPeriodoNomina]
        if ids_previos:
            self.controller.liquidaciones = [l for l in self.controller.liquidaciones if l.idLiquidacion not in ids_previos]
            self.controller.detalles_liquidacion = [d for d in self.controller.detalles_liquidacion if getattr(d, "idLiquidacion", None) not in ids_previos]
            self.controller._recrear_gestores()

        liq = None
        try:
            liq = self.controller.gestor_nomina.liquidarAdministrativo(contrato.idContrato, periodo.idPeriodoNomina)
        except Exception:
            liq = None

        if liq is None:
            sueldo_base = Decimal(str(contrato.salarioBase or adm.salarioBase or 2800000))
            smmlv = Decimal("1750905")
            auxilio = Decimal("249095") if sueldo_base <= Decimal("2") * smmlv else Decimal("0")
            devengado = sueldo_base + auxilio
            ibc = sueldo_base
            salud = (ibc * Decimal("0.04")).quantize(Decimal("1"))
            pension = (ibc * Decimal("0.04")).quantize(Decimal("1"))
            deducciones = salud + pension
            neto = devengado - deducciones
            prestaciones = (devengado * Decimal("0.2183")).quantize(Decimal("1"))

            siguiente_id = max((l.idLiquidacion or 0 for l in self.controller.liquidaciones), default=0) + 1
            liq = LiquidacionNomina(
                idLiquidacion=siguiente_id,
                idProfesor=None,
                idContrato=contrato.idContrato,
                idPeriodoNomina=periodo.idPeriodoNomina,
                fechaLiquidacion=date.today(),
                salarioBase=round(sueldo_base, 2),
                totalDevengado=round(devengado, 2),
                totalDescuentos=round(deducciones, 2),
                netoPagar=round(neto, 2),
                totalPrestaciones=round(prestaciones, 2),
                baseCotizacionSeguridadSocial=round(ibc, 2),
                valorAuxilioTransporteCotizado=round(auxilio, 2),
                estado="PROCESADA",
                regimenLiquidado="LEY_100_CST",
                categoriaLiquidada=adm.cargo or "ADMINISTRATIVO",
            )
            self.controller.liquidaciones.append(liq)

        self.controller._recrear_gestores()
        return True, "Administrativo liquidado exitosamente."

    def _eliminar_liquidacion(self, id_liquidacion: int) -> None:
        liq = next((l for l in self.controller.liquidaciones if l.idLiquidacion == id_liquidacion), None)
        if liq:
            per = next((p for p in self.controller.periodos_nomina if p.idPeriodoNomina == liq.idPeriodoNomina), None)
            if per and (getattr(per, "estaCerrado", False) or str(getattr(per, "estado", "")).upper() == "CERRADO"):
                # No se puede anular una liquidación de un período cerrado contablemente
                return
        self.controller.liquidaciones = [l for l in self.controller.liquidaciones if l.idLiquidacion != id_liquidacion]
        self.controller.detalles_liquidacion = [d for d in self.controller.detalles_liquidacion if getattr(d, "idLiquidacion", None) != id_liquidacion]
        self.controller._recrear_gestores()
        self.controller.guardar_datos()
        self.actualizar()

    def _reliquidar_accion(self, id_liquidacion: int) -> None:
        try:
            self.controller.gestor_nomina.ciclo_vida.reliquidar(id_liquidacion)
            self.controller._recrear_gestores()
            self.controller.guardar_datos()
            self.actualizar()
        except Exception as err:
            from tkinter import messagebox
            messagebox.showerror("Error al reliquidar", f"No se pudo reliquidar: {err}")

    def _mostrar_resumen_liquidacion(self, liq_doc: int, liq_adm: int, omit_doc: int, omit_adm: int) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title("⚙️ Balance de Liquidación General")
        dialog.geometry("450x300")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        card = ctk.CTkFrame(dialog, fg_color=Colors.BG_CARD, corner_radius=10, border_width=1, border_color=Colors.BORDER_SUBTLE)
        card.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            card,
            text="⚙️ Liquidación General Procesada",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=Colors.TEXT_MAIN,
        ).pack(anchor="w", padx=15, pady=(15, 6))

        ctk.CTkLabel(
            card,
            text=f"✅ Docentes Liquidados (Con Contrato Activo): {liq_doc}\n✅ Administrativos Liquidados (Con Contrato Activo): {liq_adm}",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#10B981",
            justify="left",
        ).pack(anchor="w", padx=15, pady=4)

        if omit_doc > 0 or omit_adm > 0:
            sep = ctk.CTkFrame(card, height=1, fg_color=Colors.BORDER_SUBTLE)
            sep.pack(fill="x", padx=15, pady=8)

            ctk.CTkLabel(
                card,
                text=f"⚠️ Personal Omitido (Sin Contrato Activo):\n"
                     f"   • {omit_doc} docente(s) omitido(s)\n"
                     f"   • {omit_adm} administrativo(s) omitido(s)\n\n"
                     f"💡 Nota: Para incluir a estas personas en la nómina, debe registrar y formalizar previamente su vinculación en el módulo de Contratos.",
                font=ctk.CTkFont(family="Segoe UI", size=11),
                text_color="#EF4444",
                justify="left",
                wraplength=380,
            ).pack(anchor="w", padx=15, pady=(2, 10))

        ctk.CTkButton(
            card,
            text="Aceptar",
            fg_color="#0067C0",
            hover_color="#005FB8",
            width=100,
            command=dialog.destroy,
        ).pack(pady=(0, 10))

    def _ejecutar_liquidacion_general(self) -> None:
        if not self.controller.profesores and not self.controller.administrativos:
            return

        target_pid = self.periodo_seleccionado_id
        if target_pid:
            # Limpiar solo las de este periodo
            self.controller.liquidaciones = [l for l in self.controller.liquidaciones if l.idPeriodoNomina != target_pid]
            self.controller.detalles_liquidacion = [d for d in self.controller.detalles_liquidacion if getattr(d, "idLiquidacion", None) in [l.idLiquidacion for l in self.controller.liquidaciones]]
        else:
            self.controller.liquidaciones.clear()
            self.controller.detalles_liquidacion.clear()
        self.controller._recrear_gestores()

        liq_doc = 0
        omit_doc = 0
        for prof in self.controller.profesores:
            ok, _ = self._liquidar_profesor_especifico(prof, target_pid)
            if ok:
                liq_doc += 1
            else:
                omit_doc += 1

        liq_adm = 0
        omit_adm = 0
        for adm in self.controller.administrativos:
            ok, _ = self._liquidar_administrativo_especifico(adm, target_pid)
            if ok:
                liq_adm += 1
            else:
                omit_adm += 1

        self.controller._recrear_gestores()
        self.controller.guardar_datos()
        self.actualizar()

        if omit_doc > 0 or omit_adm > 0:
            self._mostrar_resumen_liquidacion(liq_doc, liq_adm, omit_doc, omit_adm)

    def actualizar(self) -> None:
        MESES = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        opciones = ["Todos los Períodos"]
        val_actual = "Todos los Períodos"
        for p in self.controller.periodos_nomina:
            m_idx = getattr(p, "mes", 1) or 1
            m_nom = MESES[m_idx] if (1 <= m_idx <= 12) else f"Mes {m_idx}"
            opt = f"#{p.idPeriodoNomina} - {getattr(p, 'anio', 2026)} {m_nom} [{getattr(p, 'estado', 'ABIERTO')}]"
            opciones.append(opt)
            if self.periodo_seleccionado_id == p.idPeriodoNomina:
                val_actual = opt

        if hasattr(self, "combo_periodo_filtro"):
            self.combo_periodo_filtro.configure(values=opciones)
            self.combo_periodo_filtro.set(val_actual)
            if self.periodo_seleccionado_id:
                per = next((p for p in self.controller.periodos_nomina if p.idPeriodoNomina == self.periodo_seleccionado_id), None)
                if per and hasattr(self, "lbl_estado_periodo"):
                    est = str(getattr(per, "estado", "ABIERTO")).upper()
                    if est == "ABIERTO":
                        self.lbl_estado_periodo.configure(text="● PERÍODO EN PROCESO (ABIERTO)", text_color="#10B981")
                    else:
                        self.lbl_estado_periodo.configure(text="🔒 PERÍODO CERRADO / AUDITADO", text_color="#EF4444")
            else:
                if hasattr(self, "lbl_estado_periodo"):
                    self.lbl_estado_periodo.configure(text="")

        self._crear_tarjetas_kpi()
        self._llenar_tab_liquidaciones()
        self._llenar_tab_parafiscales()
        self._llenar_tab_anual()

    def _llenar_tab_anual(self) -> None:
        if not hasattr(self, "scroll_anual"):
            return
        for w in self.scroll_anual.winfo_children():
            w.destroy()

        from pathlib import Path
        from nomina.desglose_anual import CalculadorDesgloseAnual
        setattr(self.controller.gestor_nomina, "personas", self.controller.personas)
        calculador = CalculadorDesgloseAnual(self.controller.gestor_nomina)
        institucional = calculador.generar_desglose_institucional(2026)

        # Header con botón de exportar
        top_bar = ctk.CTkFrame(self.scroll_anual, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            top_bar,
            text="📅 Consolidado Anual de Nómina y Prestaciones Sociales (Cierre 360 Días)",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=Colors.TEXT_MAIN,
        ).pack(side="left")

        def _exportar_reporte():
            txt = calculador.generar_reporte_texto(2026)
            p = Path("docs/DESGLOSE_NOMINA_ANUAL_2026.md")
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(txt, encoding="utf-8")
            btn_exp.configure(text="✅ Exportado a docs/DESGLOSE_NOMINA_ANUAL_2026.md", fg_color="#059669")

        btn_exp = ctk.CTkButton(
            top_bar,
            text="📥 Exportar Reporte Anual (.md)",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color="#0067C0",
            hover_color="#005FB8",
            command=_exportar_reporte,
            height=32,
            corner_radius=6,
        )
        btn_exp.pack(side="right")

        # KPIs Anuales
        kpi_frame = ctk.CTkFrame(self.scroll_anual, fg_color="transparent")
        kpi_frame.pack(fill="x", pady=(0, 15))

        kpis = [
            ("💵 Devengado Anual", f"$ {institucional['total_devengado_anual']:,.0f} COP", Colors.WIN_BLUE),
            ("📉 Deducciones Anuales", f"$ {institucional['total_descuentos_anual']:,.0f} COP", Colors.ACCENT_DANGER),
            ("✅ Neto Anual Docentes", f"$ {institucional['total_neto_anual']:,.0f} COP", "#10B981"),
            ("🏖️ Prestaciones Anuales", f"$ {institucional['total_prestaciones_anual']:,.0f} COP", Colors.ACCENT_WARNING),
            ("🏢 Costo Total Empleador", f"$ {institucional['costo_total_institucional_anual']:,.0f} COP", "#8B5CF6"),
        ]

        for tit, val, col in kpis:
            card = ctk.CTkFrame(kpi_frame, fg_color=Colors.BG_CARD, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
            card.pack(side="left", fill="both", expand=True, padx=4)
            ctk.CTkLabel(card, text=tit, font=ctk.CTkFont(size=10, weight="bold"), text_color=Colors.TEXT_MUTED).pack(anchor="w", padx=10, pady=(8, 2))
            ctk.CTkLabel(card, text=val, font=ctk.CTkFont(size=12, weight="bold"), text_color=col).pack(anchor="w", padx=10, pady=(0, 8))

        # Tarjetas detalladas por contrato
        for d in institucional["desgloses_individuales"]:
            c_card = ctk.CTkFrame(self.scroll_anual, fg_color=Colors.BG_CARD, corner_radius=10, border_width=1, border_color=Colors.BORDER_SUBTLE)
            c_card.pack(fill="x", pady=8)

            c_hdr = ctk.CTkFrame(c_card, fg_color="transparent")
            c_hdr.pack(fill="x", padx=14, pady=(10, 6))

            ctk.CTkLabel(
                c_hdr,
                text=f"👤 {d.nombre_completo} — Contrato #{d.id_contrato} ({d.tipo_personal} | {d.regimen})",
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                text_color=Colors.TEXT_MAIN,
            ).pack(side="left")

            ctk.CTkLabel(
                c_hdr,
                text=f"Vigencia: {d.meses_considerados} meses ({d.dias_trabajados_anio} días)  |  Costo Total: $ {d.costo_total_empleador_anual:,.0f} COP",
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                text_color=Colors.WIN_BLUE,
            ).pack(side="right")

            headers = ["Concepto Salarial / Prestacional", "Categoría", "Factor / %", "Valor Mensual", "Valor Anual Consolidado"]
            col_weights = [4, 2, 3, 3, 3]
            col_mins = [180, 100, 120, 110, 120]

            t = PITAGridTable(c_card, headers=headers, col_weights=col_weights, col_mins=col_mins)
            t.pack(fill="x", padx=10, pady=(0, 10))

            for it in d.items:
                cat_color = {
                    "DEVENGADO": "#10B981",
                    "DEDUCCION": "#EF4444",
                    "PRESTACION": "#F59E0B",
                    "APORTE_PATRONAL": "#6366F1",
                }.get(it.categoria, "#94A3B8")

                t.add_row_items([
                    it.concepto,
                    ("badge", it.categoria, "active" if it.categoria == "DEVENGADO" else "neutral"),
                    it.porcentaje_o_factor,
                    f"$ {it.valor_mensual_promedio:,.2f}",
                    (f"$ {it.valor_anual_consolidado:,.2f}", cat_color),
                ])
