"""Vista de Gestión y Liquidación de Nómina Docente (Decreto 1279 / Acuerdo 027) con tablas de alta fidelidad."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
import customtkinter as ctk
from typing import TYPE_CHECKING

from ui_gui.components import PITAGridTable, create_badge
from modelo_datos import ConceptoNomina, DetalleLiquidacion, LiquidacionNomina, PeriodoNomina

if TYPE_CHECKING:
    from ui_gui.gui_controller import PITAController


class NominaViewGUI(ctk.CTkFrame):
    """Vista principal de liquidación salarial, descuentos de ley y prestaciones sociales."""

    def __init__(self, parent: ctk.CTk, controller: PITAController) -> None:
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        self._crear_interfaz()

    def _crear_interfaz(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 10))

        ctk.CTkLabel(
            header,
            text="💰 Liquidación de Nómina & Prestaciones Sociales",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#F8FAFC",
        ).pack(side="left")

        h_btns = ctk.CTkFrame(header, fg_color="transparent")
        h_btns.pack(side="right")

        btn_indiv = ctk.CTkButton(
            h_btns,
            text="👤 Liquidación Individual",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#6366F1",
            hover_color="#4F46E5",
            height=36,
            corner_radius=8,
            command=self._abrir_modal_liquidar_individual,
        )
        btn_indiv.pack(side="left", padx=5)

        btn_liquidar_todos = ctk.CTkButton(
            h_btns,
            text="⚙️ Liquidar Nómina del Periodo",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#10B981",
            hover_color="#059669",
            height=36,
            corner_radius=8,
            command=self._ejecutar_liquidacion_general,
        )
        btn_liquidar_todos.pack(side="left", padx=5)

        # Pestañas
        self.tabview = ctk.CTkTabview(self, fg_color="transparent")
        self.tabview.pack(fill="both", expand=True, padx=15, pady=5)

        self.tab_liquidaciones = self.tabview.add("📊 Resumen de Liquidaciones")
        self.tab_normatividad = self.tabview.add("📜 Reglas Decreto 1279 / Acuerdo 027")

        self._llenar_tab_liquidaciones()
        self._llenar_tab_normatividad()

    def _llenar_tab_liquidaciones(self) -> None:
        for w in self.tab_liquidaciones.winfo_children():
            w.destroy()

        headers = ["Docente", "Tipo Profesor", "Sueldo Básico", "Devengado", "Descuentos Ley", "Neto a Pagar", "Prestaciones", "Acción"]
        col_weights = [3, 2, 3, 3, 3, 3, 2, 2]
        col_mins = [160, 110, 120, 120, 130, 130, 110, 90]

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
            tipo_prof = str(getattr(prof, "tipoProfesor", "DOCENTE"))

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

            badge_tuple = ("badge", tipo_prof, tipo_prof.lower())

            act_spec = (
                "actions",
                [
                    ("📋 Desglose", lambda l_id=liq.idLiquidacion: self._abrir_modal_detalle_liquidacion(l_id), "#6366F1", "#4F46E5", 80, 28, 10),
                    ("❌", lambda l_id=liq.idLiquidacion: self._eliminar_liquidacion(l_id), "#EF4444", "#DC2626", 30, 28, 10),
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

    def _llenar_tab_normatividad(self) -> None:
        scroll = ctk.CTkScrollableFrame(self.tab_normatividad, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(scroll, text="📋 Marco Normativo Salarial Docente PITA", font=ctk.CTkFont(size=16, weight="bold"), text_color="#F8FAFC").pack(anchor="w", pady=(0, 10))

        text_norma = (
            "1. Profesores de Planta (Decreto 1279 de 2002):\n"
            "   • Sueldo Básico = Puntos Salariales Reconocidos × Valor Punto Salarial Vigente ($ 19.850).\n"
            "   • Factores Salariales: Títulos académicos (Doctorado, Maestría), Categoría (Titular, Asociado), Producción Académica.\n"
            "   • Bonificaciones especiales por posgrado e investigación.\n\n"
            "2. Profesores Ocasionales (Acuerdo 027 de 2024):\n"
            "   • Vinculación por periodo académico o meses laborados.\n"
            "   • Pago proporcional al tiempo de dedicación (Tiempo Completo / Medio Tiempo).\n\n"
            "3. Profesores Catedráticos (Resolución Rectoral):\n"
            "   • Remuneración basada en el valor de la Hora Cátedra ($ 38.500) por el número de horas dictadas.\n\n"
            "4. Descuentos Obligatorios de Ley:\n"
            "   • Salud Trabajador: 4.0 % del Ingreso Base de Cotización (IBC).\n"
            "   • Pensión Trabajador: 4.0 % del Ingreso Base de Cotización (IBC).\n"
            "   • Fondo de Solidaridad Pensional (FSP): 1.0 % adicional cuando el IBC sea mayor o igual a 4 SMMLV.\n"
            "   • Auxilio de Transporte: Aplica a docentes con ingreso inferior a 2 SMMLV ($ 162.000 COP).\n\n"
            "5. Prestaciones Sociales Proyectadas:\n"
            "   • Cesantías (8.33 %), Intereses sobre Cesantías (1.0 %), Prima de Servicios (8.33 %) y Vacaciones (4.17 %)."
        )

        card = ctk.CTkFrame(scroll, fg_color="#0F172A", corner_radius=8, border_width=1, border_color="#334155")
        card.pack(fill="x", pady=5)
        ctk.CTkLabel(card, text=text_norma, font=ctk.CTkFont(size=12), justify="left", text_color="#E2E8F0", anchor="w").pack(padx=20, pady=15)

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

        dialog = ctk.CTkToplevel(self)
        dialog.title(f"📋 Desprendible de Liquidación - {nom_prof}")
        dialog.geometry("500x450")
        dialog.grab_set()

        ctk.CTkLabel(dialog, text=f"Detalle de Liquidación - {nom_prof}", font=ctk.CTkFont(size=15, weight="bold")).pack(pady=10)

        scroll = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=15, pady=10)

        detalles = [d for d in self.controller.detalles_liquidacion if getattr(d, "idLiquidacion", None) == id_liquidacion]
        if not detalles:
            sb = float(getattr(liq, "salarioBase", 0))
            dev = float(getattr(liq, "totalDevengado", sb))
            desc = float(getattr(liq, "totalDescuentos", 0))

            detalles_info = [
                ("DEVENGADO", "Sueldo Básico Mensual", f"$ {int(sb):,} COP"),
                ("DEDUCCION", "Descuento Salud (4%)", f"$ {int(sb * 0.04):,} COP"),
                ("DEDUCCION", "Descuento Pensión (4%)", f"$ {int(sb * 0.04):,} COP"),
            ]
            if desc > (sb * 0.08):
                detalles_info.append(("DEDUCCION", "Fondo Solidaridad Pensional (1%)", f"$ {int(sb * 0.01):,} COP"))

            for tipo, desc_c, val in detalles_info:
                r = ctk.CTkFrame(scroll, fg_color="#1E293B", corner_radius=6)
                r.pack(fill="x", pady=3, padx=5)
                color_t = "#38BDF8" if tipo == "DEVENGADO" else "#F87171"
                ctk.CTkLabel(r, text=desc_c, font=ctk.CTkFont(size=11, weight="bold"), text_color="#F8FAFC").pack(side="left", padx=10, pady=6)
                ctk.CTkLabel(r, text=val, font=ctk.CTkFont(size=11, weight="bold"), text_color=color_t).pack(side="right", padx=10, pady=6)
        else:
            for d in detalles:
                r = ctk.CTkFrame(scroll, fg_color="#1E293B", corner_radius=6)
                r.pack(fill="x", pady=3, padx=5)
                val_c = getattr(d, "valorCalculado", 0)
                ctk.CTkLabel(r, text=getattr(d, "observaciones", "Concepto"), font=ctk.CTkFont(size=11, weight="bold"), text_color="#F8FAFC").pack(side="left", padx=10, pady=6)
                ctk.CTkLabel(r, text=f"$ {val_c}", font=ctk.CTkFont(size=11, weight="bold"), text_color="#34D399").pack(side="right", padx=10, pady=6)

        ctk.CTkLabel(dialog, text=f"NETO A PAGAR: $ {getattr(liq, 'netoPagar', '0')}", font=ctk.CTkFont(size=14, weight="bold"), text_color="#34D399").pack(pady=10)

    def _liquidar_profesor_especifico(self, prof) -> None:
        val_punto = Decimal("19850")
        smmlv = Decimal("1423500")
        val_hora_cat = Decimal("38500")

        tipo = str(getattr(prof, "tipoProfesor", "PLANTA"))
        puntos = Decimal(str(getattr(prof, "puntosSalariales", "300")))
        horas = int(getattr(prof, "numeroHorasSemanales", 40))

        if tipo == "PLANTA":
            sueldo_base = puntos * val_punto
        elif tipo == "CATEDRATICO":
            sueldo_base = Decimal(horas * 4) * val_hora_cat
        else:
            sueldo_base = Decimal("3500000")

        bonif = sueldo_base * Decimal("0.10") if getattr(prof, "maximoNivelEstudio", "") in ["DOCTORADO", "MAESTRIA"] else Decimal("0")
        total_devengado = sueldo_base + bonif
        salud = total_devengado * Decimal("0.04")
        pension = total_devengado * Decimal("0.04")
        fsp = total_devengado * Decimal("0.01") if total_devengado >= (smmlv * 4) else Decimal("0")
        aux_trans = Decimal("162000") if total_devengado <= (smmlv * 2) and tipo != "PLANTA" else Decimal("0")

        devengado_final = total_devengado + aux_trans
        total_deducciones = salud + pension + fsp
        neto_pagar = devengado_final - total_deducciones
        prestaciones = devengado_final * Decimal("0.2083")

        self.controller.liquidaciones = [l for l in self.controller.liquidaciones if l.idProfesor != prof.idProfesor]

        liq = LiquidacionNomina(
            idLiquidacion=len(self.controller.liquidaciones) + 1,
            idProfesor=prof.idProfesor,
            idContrato=prof.idProfesor,
            idPeriodoNomina=1,
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

    def _ejecutar_liquidacion_general(self) -> None:
        if not self.controller.profesores:
            return

        self.controller.liquidaciones.clear()
        for prof in self.controller.profesores:
            self._liquidar_profesor_especifico(prof)

        self.actualizar()

    def actualizar(self) -> None:
        for widget in self.winfo_children():
            widget.destroy()
        self._crear_interfaz()
