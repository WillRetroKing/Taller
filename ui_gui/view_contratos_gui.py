"""Vista de Contratación Docente (Planta, Ocasional, Catedrático, Ad Honorem) y Factores Salariales (Decreto 1279 / Acuerdo 027)."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
import customtkinter as ctk
from typing import TYPE_CHECKING, Any

from ui_gui.theme import Colors, Fonts, create_styled_tabview
from ui_gui.components import PITAGridTable, create_badge, create_stat_card
from modelo_datos import (
    CategoriaDocente,
    Contrato,
    Dedicacion,
    FactorSalarial,
    ProduccionAcademica,
    TipoFactor,
)
from gestor_contratos import ErrorContrato
from gestor_factores import ErrorFactor

if TYPE_CHECKING:
    from ui_gui.gui_controller import PITAController


class ContratosViewGUI(ctk.CTkFrame):
    """Vista de gestión integral de vinculación docente, contratos y factores salariales."""

    def __init__(self, parent: ctk.CTk, controller: PITAController) -> None:
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        self.filtro_modalidad = "TODAS"
        self.filtro_estado = "TODOS"
        self.busqueda_texto = ""

        self._crear_interfaz()

    def _crear_interfaz(self) -> None:
        # Cabecera principal
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=14, pady=(0, 10))

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left")

        ctk.CTkLabel(
            title_box,
            text="📝 Gestión de Contratación y Factores Salariales",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=Colors.TEXT_MAIN,
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_box,
            text="Régimen de Carrera (Dec. 1279/2002) y Profesores Transitorios (Acuerdo 027/2024)",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=Colors.TEXT_MUTED,
        ).pack(anchor="w")

        h_buttons = ctk.CTkFrame(header, fg_color="transparent")
        h_buttons.pack(side="right")

        btn_nuevo_contrato = ctk.CTkButton(
            h_buttons,
            text="➕ Registrar Contrato Docente",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=Colors.WIN_BLUE,
            hover_color=Colors.WIN_BLUE_HOVER,
            corner_radius=8,
            height=36,
            command=self._abrir_modal_nuevo_contrato,
        )
        btn_nuevo_contrato.pack(side="left", padx=5)

        btn_reconocer_puntos = ctk.CTkButton(
            h_buttons,
            text="⭐ Reconocer Puntos / Productividad",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#006837",
            hover_color="#004D28",
            corner_radius=8,
            height=36,
            command=self._abrir_modal_reconocer_puntos,
        )
        btn_reconocer_puntos.pack(side="left", padx=5)

        # Barra de KPIs Ejecutivos
        self._crear_kpis()

        # Tabview principal
        self.tabview = create_styled_tabview(self)
        self.tabview.pack(fill="both", expand=True, padx=14, pady=5)

        self.tab_contratos = self.tabview.add("📜 Contratos Docentes Vigentes")
        self.tab_factores = self.tabview.add("⭐ Factores Salariales y Escalafón (Dec. 1279)")

        self._llenar_tab_contratos()
        self._llenar_tab_factores()

    def _crear_kpis(self) -> None:
        kpi_frame = ctk.CTkFrame(self, fg_color="transparent")
        kpi_frame.pack(fill="x", padx=14, pady=(0, 10))
        kpi_frame.columnconfigure((0, 1, 2, 3), weight=1)

        contratos = self.controller.contratos
        activos = [c for c in contratos if str(getattr(c, "estado", "ACTIVO")).upper() == "ACTIVO"]
        total_activos = len(activos)

        # Distribución de modalidades
        planta = sum(1 for c in activos if "PLANTA" in str(getattr(c, "modalidadProfesor", "") or getattr(c, "tipoContrato", "")).upper())
        ocasional = sum(1 for c in activos if "OCASIONAL" in str(getattr(c, "modalidadProfesor", "") or getattr(c, "tipoContrato", "")).upper())
        catedra = sum(1 for c in activos if "CATEDRATICO" in str(getattr(c, "modalidadProfesor", "") or getattr(c, "tipoContrato", "")).upper())
        ad_honorem = sum(1 for c in activos if getattr(c, "esAdHonorem", False) or "AD_HONOREM" in str(getattr(c, "tipoContrato", "")).upper())

        # Total de puntos salariales reconocidos a docentes de planta
        profesores = self.controller.profesores
        total_puntos = sum(
            Decimal(str(getattr(p, "puntosSalariales", "0") or "0"))
            for p in profesores
        )

        val_punto = self._obtener_parametro_decimal("VALOR_PUNTO_SALARIAL", Decimal("19850"))

        # Presupuesto mensual estimado de nómina
        total_nomina = sum(
            Decimal(str(getattr(c, "salarioBase", "0") or getattr(c, "salarioMensualPactado", "0") or "0"))
            for c in activos
        )

        create_stat_card(
            kpi_frame,
            row=0,
            col=0,
            title="CONTRATOS ACTIVOS",
            value=f"{total_activos} Activos",
            accent_color=Colors.WIN_BLUE,
            subtitle=f"{len(contratos)} vinculaciones totales",
        )

        create_stat_card(
            kpi_frame,
            row=0,
            col=1,
            title="DISTRIBUCIÓN DOCENTE",
            value=f"{planta} Planta | {ocasional+catedra} Trans.",
            accent_color="#8B5CF6",
            subtitle=f"{catedra} Cátedra · {ad_honorem} Ad-Honorem",
        )

        create_stat_card(
            kpi_frame,
            row=0,
            col=2,
            title="PUNTOS SALARIALES TOTALES",
            value=f"{int(total_puntos):,} Pts",
            accent_color="#F59E0B",
            subtitle=f"Valor punto: ${int(val_punto):,} COP",
        )

        create_stat_card(
            kpi_frame,
            row=0,
            col=3,
            title="MASA SALARIAL MENSUAL",
            value=f"$ {int(total_nomina):,} COP",
            accent_color="#10B981",
            subtitle="Asignación básica consolidada",
        )

    # -------------------------------------------------------------------------
    # TAB 1: CONTRATOS DOCENTES
    # -------------------------------------------------------------------------

    def _llenar_tab_contratos(self) -> None:
        for w in self.tab_contratos.winfo_children():
            w.destroy()

        # Barra de Filtros y Búsqueda
        filter_bar = ctk.CTkFrame(self.tab_contratos, fg_color=Colors.BG_CARD, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
        filter_bar.pack(fill="x", padx=6, pady=(4, 8))

        ctk.CTkLabel(filter_bar, text="🔍 Filtrar:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=Colors.TEXT_MUTED).pack(side="left", padx=(12, 6), pady=8)

        combo_mod = ctk.CTkComboBox(
            filter_bar,
            values=["TODAS LAS MODALIDADES", "PLANTA", "OCASIONAL", "CATEDRATICO", "AD_HONOREM"],
            width=180,
            command=self._on_filtro_modalidad_change,
        )
        combo_mod.set(self.filtro_modalidad)
        combo_mod.pack(side="left", padx=4, pady=8)

        combo_est = ctk.CTkComboBox(
            filter_bar,
            values=["TODOS LOS ESTADOS", "ACTIVO", "TERMINADO"],
            width=150,
            command=self._on_filtro_estado_change,
        )
        combo_est.set(self.filtro_estado)
        combo_est.pack(side="left", padx=4, pady=8)

        entry_buscar = ctk.CTkEntry(
            filter_bar,
            placeholder_text="Buscar docente o número de contrato...",
            width=240,
        )
        if self.busqueda_texto:
            entry_buscar.insert(0, self.busqueda_texto)
        entry_buscar.pack(side="left", padx=6, pady=8)

        def _buscar():
            self.busqueda_texto = entry_buscar.get().strip().lower()
            self._llenar_tab_contratos()

        ctk.CTkButton(
            filter_bar,
            text="Buscar",
            width=70,
            fg_color=Colors.WIN_BLUE,
            hover_color=Colors.WIN_BLUE_HOVER,
            command=_buscar,
        ).pack(side="left", padx=4, pady=8)

        def _limpiar():
            self.filtro_modalidad = "TODAS LAS MODALIDADES"
            self.filtro_estado = "TODOS LOS ESTADOS"
            self.busqueda_texto = ""
            self._llenar_tab_contratos()

        ctk.CTkButton(
            filter_bar,
            text="Restablecer",
            width=85,
            fg_color="#64748B",
            hover_color="#475569",
            command=_limpiar,
        ).pack(side="left", padx=4, pady=8)

        headers = ["N° Contrato", "Docente", "Modalidad / Régimen", "Dedicación / Horas", "Asignación Básica", "Vigencia", "Estado", "Acciones"]
        col_weights = [2, 3, 3, 2, 2, 3, 2, 3]
        col_mins = [110, 160, 140, 90, 120, 130, 90, 170]

        table = PITAGridTable(self.tab_contratos, headers=headers, col_weights=col_weights, col_mins=col_mins)
        table.pack(fill="both", expand=True, padx=4, pady=4)

        contratos = self.controller.contratos
        if not contratos:
            ctk.CTkLabel(table, text="No hay contratos vigentes registrados.", text_color="#94A3B8").pack(pady=25)
            return

        # Aplicar filtros
        filtrados = []
        for cont in contratos:
            mod = str(getattr(cont, "modalidadProfesor", "") or getattr(cont, "tipoContrato", "")).upper()
            est = str(getattr(cont, "estado", "ACTIVO")).upper()

            # Filtro modalidad
            if self.filtro_modalidad != "TODAS LAS MODALIDADES" and self.filtro_modalidad != "TODAS":
                if self.filtro_modalidad == "AD_HONOREM" and not (getattr(cont, "esAdHonorem", False) or "AD_HONOREM" in mod):
                    continue
                elif self.filtro_modalidad != "AD_HONOREM" and self.filtro_modalidad not in mod:
                    continue

            # Filtro estado
            if self.filtro_estado != "TODOS LOS ESTADOS" and self.filtro_estado != "TODOS":
                if self.filtro_estado == "ACTIVO" and est != "ACTIVO":
                    continue
                if self.filtro_estado == "TERMINADO" and est not in ("TERMINADO", "INACTIVO"):
                    continue

            # Búsqueda
            if self.busqueda_texto:
                prof = self._buscar_profesor_por_id_persona(cont.idPersona)
                pers = self._buscar_persona_por_id(cont.idPersona)
                nom = f"{getattr(pers, 'primerNombre', '')} {getattr(pers, 'primerApellido', '')}".lower()
                num = str(getattr(cont, "numeroContrato", "")).lower()
                if self.busqueda_texto not in nom and self.busqueda_texto not in num:
                    continue

            filtrados.append(cont)

        if not filtrados:
            ctk.CTkLabel(table, text="No se encontraron contratos con los filtros aplicados.", text_color="#94A3B8").pack(pady=25)
            return

        for cont in filtrados:
            pers = self._buscar_persona_por_id(cont.idPersona)
            nom_prof = f"{getattr(pers, 'primerNombre', '')} {getattr(pers, 'primerApellido', '')}" if pers else f"Persona #{cont.idPersona}"

            asig = str(getattr(cont, "salarioBase", "0") or getattr(cont, "salarioMensualPactado", "0") or "0")
            try:
                asig_fmt = f"$ {int(float(asig)):,} COP"
            except Exception:
                asig_fmt = f"$ {asig}"

            est = str(getattr(cont, "estado", "ACTIVO")).upper()
            badge_est = "cancelado" if est in ("TERMINADO", "INACTIVO") else "active"

            mod = str(getattr(cont, "modalidadProfesor", "") or getattr(cont, "tipoContrato", "DOCENTE")).upper()
            if "PLANTA" in mod:
                badge_mod_type = "planta"
                mod_desc = "🏛️ Planta (D.1279)"
            elif "OCASIONAL" in mod:
                badge_mod_type = "ocasional"
                mod_desc = "⏱️ Ocasional (Ac.027)"
            elif "CATEDRATICO" in mod:
                badge_mod_type = "catedra"
                mod_desc = "📚 Cátedra (Ac.027)"
            else:
                badge_mod_type = "neutral"
                mod_desc = "🤝 Ad-Honorem"

            horas = getattr(cont, "horasSemanales", 40)
            ded = str(getattr(cont, "dedicacion", "TC"))
            ded_fmt = "TC (40h)" if "COMPLETO" in ded else ("MT (20h)" if "MEDIO" in ded else f"HC ({horas}h)")

            f_ini = getattr(cont, "fechaInicio", "") or "N/D"
            f_fin = getattr(cont, "fechaFin", "") or "Indefinido"
            vigencia = f"{f_ini} al {f_fin}"

            btn_list = [
                ("👁️ Ver", lambda c=cont: self._abrir_modal_detalle_contrato(c), "#334155", "#475569", 55, 26),
                ("✏️ Editar", lambda c=cont: self._abrir_modal_editar_contrato(c), Colors.WIN_BLUE, Colors.WIN_BLUE_HOVER, 60, 26),
            ]
            if est == "ACTIVO":
                btn_list.append(("🚫 Terminar", lambda c=cont: self._abrir_modal_terminar_contrato(c), "#EF4444", "#DC2626", 75, 26))

            cells = [
                (getattr(cont, "numeroContrato", "N/A"), "#F59E0B"),
                (nom_prof, "#F8FAFC"),
                ("badge", mod_desc, badge_mod_type),
                ded_fmt,
                (asig_fmt, "#10B981"),
                vigencia,
                ("badge", est, badge_est),
                ("actions", btn_list),
            ]
            table.add_row_items(cells, is_highlighted=(est in ("TERMINADO", "INACTIVO")))

    def _on_filtro_modalidad_change(self, val: str) -> None:
        self.filtro_modalidad = val
        self._llenar_tab_contratos()

    def _on_filtro_estado_change(self, val: str) -> None:
        self.filtro_estado = val
        self._llenar_tab_contratos()

    # -------------------------------------------------------------------------
    # TAB 2: FACTORES SALARIALES Y ESCALAFÓN (DEC. 1279)
    # -------------------------------------------------------------------------

    def _llenar_tab_factores(self) -> None:
        for w in self.tab_factores.winfo_children():
            w.destroy()

        sub_tabview = create_styled_tabview(self.tab_factores)
        sub_tabview.pack(fill="both", expand=True, padx=4, pady=4)

        tab_fac_base = sub_tabview.add("📜 Factores Salariales Reconocidos")
        tab_prod_acad = sub_tabview.add("🔬 Producción Intelectual / Obras")

        # Sub-tab A: Factores Salariales
        headers_fac = ["Docente", "Tipo de Factor", "Concepto / Descripción", "Puntos Reconocidos", "Acto Administrativo", "Fecha Reconocimiento", "Estado"]
        col_w_fac = [3, 2, 4, 2, 3, 2, 2]
        col_m_fac = [160, 130, 200, 110, 140, 100, 80]

        table_fac = PITAGridTable(tab_fac_base, headers=headers_fac, col_weights=col_w_fac, col_mins=col_m_fac)
        table_fac.pack(fill="both", expand=True, padx=4, pady=4)

        if not self.controller.factores:
            ctk.CTkLabel(table_fac, text="No hay factores salariales registrados.", text_color="#94A3B8").pack(pady=25)
        else:
            for fac in self.controller.factores:
                prof = self._buscar_profesor_por_id(fac.idProfesor)
                pers = self._buscar_persona_por_id(getattr(prof, "idPersona", None))
                nom_prof = f"{getattr(pers, 'primerNombre', '')} {getattr(pers, 'primerApellido', '')}" if pers else f"Profesor #{fac.idProfesor}"

                t_fac = str(getattr(fac, "tipoFactor", "TITULO_ACADEMICO"))
                pts = getattr(fac, "puntosReconocidos", None) or getattr(fac, "puntosAprobados", 0)

                cells = [
                    (nom_prof, "#F8FAFC"),
                    t_fac.replace("_", " ").title(),
                    getattr(fac, "nombre", "Factor"),
                    (f"+{pts} pts", "#F59E0B"),
                    getattr(fac, "actoAdministrativo", "N/A"),
                    str(getattr(fac, "fechaReconocimiento", "") or "N/D"),
                    ("badge", "APROBADO", "active"),
                ]
                table_fac.add_row_items(cells)

        # Sub-tab B: Producción Académica
        headers_prod = ["Docente", "Tipo de Obra", "Título de la Producción", "Medio / Editorial", "Autores / Coautoría", "Puntos Docente", "Estado"]
        col_w_prod = [3, 2, 4, 3, 2, 2, 2]
        col_m_prod = [160, 120, 200, 140, 120, 110, 90]

        table_prod = PITAGridTable(tab_prod_acad, headers=headers_prod, col_weights=col_w_prod, col_mins=col_m_prod)
        table_prod.pack(fill="both", expand=True, padx=4, pady=4)

        if not self.controller.producciones:
            ctk.CTkLabel(table_prod, text="No hay producción intelectual registrada bajo Decreto 1279.", text_color="#94A3B8").pack(pady=25)
        else:
            for prod in self.controller.producciones:
                prof = self._buscar_profesor_por_id(prod.idProfesor)
                pers = self._buscar_persona_por_id(getattr(prof, "idPersona", None))
                nom_prof = f"{getattr(pers, 'primerNombre', '')} {getattr(pers, 'primerApellido', '')}" if pers else f"Profesor #{prod.idProfesor}"

                n_aut = getattr(prod, "numeroAutores", 1) or 1
                coaut = getattr(prod, "factorCoautoria", Decimal("1.0")) or Decimal("1.0")
                coaut_pct = f"{n_aut} aut. ({int(coaut * 100)}%)"

                pts_prof = getattr(prod, "puntosReconocidosProfesor", None) or getattr(prod, "puntosReconocidos", 0)

                cells = [
                    (nom_prof, "#F8FAFC"),
                    str(getattr(prod, "tipoProduccion", "ARTICULO")).replace("_", " ").title(),
                    getattr(prod, "titulo", "Obra"),
                    getattr(prod, "entidadPublicadora", "") or getattr(prod, "identificadorProducto", "N/A"),
                    coaut_pct,
                    (f"+{pts_prof} pts", "#F59E0B"),
                    ("badge", "VALIDADO", "active"),
                ]
                table_prod.add_row_items(cells)

    # -------------------------------------------------------------------------
    # MODAL 1: REGISTRAR CONTRATO DOCENTE
    # -------------------------------------------------------------------------

    def _abrir_modal_nuevo_contrato(self) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title("➕ Registrar Contrato Docente")
        dialog.geometry("640x680")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        ctk.CTkLabel(
            dialog,
            text="📝 Vinculación Contractual Docente",
            font=ctk.CTkFont(family="Segoe UI", size=17, weight="bold"),
            text_color=Colors.TEXT_MAIN,
        ).pack(pady=(12, 4))

        ctk.CTkLabel(
            dialog,
            text="Verificación automática de topes de horas, incompatibilidad de jubilados y cálculo salarial",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=Colors.TEXT_MUTED,
        ).pack(pady=(0, 10))

        scroll = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=16, pady=4)

        # CARD 1: DOCENTE Y MODALIDAD
        card_docente = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
        card_docente.pack(fill="x", pady=6)

        ctk.CTkLabel(card_docente, text="1. Docente y Modalidad de Vinculación", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), text_color=Colors.TEXT_MAIN).pack(anchor="w", padx=14, pady=(10, 6))

        ctk.CTkLabel(card_docente, text="Seleccionar Docente:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w", padx=14, pady=(4, 1))

        prof_options = []
        for p in self.controller.profesores:
            pers = self._buscar_persona_por_id(p.idPersona)
            nom = f"{getattr(pers, 'primerNombre', '')} {getattr(pers, 'primerApellido', '')}" if pers else "Profesor"
            cat = getattr(p, "categoriaDocente", "AUXILIAR") or "DOCENTE"
            pts = getattr(p, "puntosSalariales", 0) or 0
            prof_options.append(f"{p.codigoProfesor} - {nom} [{cat}, {pts} pts]")

        if not prof_options:
            prof_options = ["Sin docentes registrados"]

        combo_prof = ctk.CTkComboBox(card_docente, values=prof_options, width=420)
        combo_prof.pack(fill="x", padx=14, pady=(0, 8))

        switch_jubilado = ctk.CTkSwitch(card_docente, text="¿El docente es pensionado / jubilado? (Aplica restricción legal)", onvalue=True, offvalue=False)
        switch_jubilado.pack(anchor="w", padx=14, pady=4)

        ctk.CTkLabel(card_docente, text="Modalidad de Vinculación:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w", padx=14, pady=(6, 1))
        combo_tipo = ctk.CTkComboBox(
            card_docente,
            values=[
                "DOCENTE_PLANTA (Dec. 1279)",
                "DOCENTE_OCASIONAL (Ac. 027/2024)",
                "DOCENTE_CATEDRATICO (Ac. 027/2024)",
                "DOCENTE_AD_HONOREM",
            ],
            width=420,
        )
        combo_tipo.pack(fill="x", padx=14, pady=(0, 8))

        row_ded = ctk.CTkFrame(card_docente, fg_color="transparent")
        row_ded.pack(fill="x", padx=14, pady=4)
        row_ded.columnconfigure((0, 1), weight=1)

        f_ded = ctk.CTkFrame(row_ded, fg_color="transparent")
        f_ded.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkLabel(f_ded, text="Dedicación:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w")
        combo_ded = ctk.CTkComboBox(f_ded, values=["TIEMPO_COMPLETO", "MEDIO_TIEMPO", "HORA_CATEDRA"])
        combo_ded.pack(fill="x", pady=2)

        f_hrs = ctk.CTkFrame(row_ded, fg_color="transparent")
        f_hrs.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        ctk.CTkLabel(f_hrs, text="Horas Semanales (máx 18h cátedra):", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w")
        entry_horas = ctk.CTkEntry(f_hrs, placeholder_text="40")
        entry_horas.insert(0, "40")
        entry_horas.pack(fill="x", pady=2)

        row_arl = ctk.CTkFrame(card_docente, fg_color="transparent")
        row_arl.pack(fill="x", padx=14, pady=(4, 12))
        row_arl.columnconfigure((0, 1), weight=1)

        f_arl = ctk.CTkFrame(row_arl, fg_color="transparent")
        f_arl.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkLabel(f_arl, text="Clase de Riesgo ARL:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w")
        combo_arl = ctk.CTkComboBox(f_arl, values=["CLASE I (0.522%)", "CLASE II (1.044%)", "CLASE III (2.436%)"])
        combo_arl.pack(fill="x", pady=2)

        # CARD 2: VIGENCIA Y COMPENSACIÓN
        card_eco = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
        card_eco.pack(fill="x", pady=6)

        ctk.CTkLabel(card_eco, text="2. Vigencia, Presupuesto y Asignación Básica", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), text_color=Colors.TEXT_MAIN).pack(anchor="w", padx=14, pady=(10, 6))

        siguiente_id = max((c.idContrato or 0 for c in self.controller.contratos), default=0) + 1
        num_sugerido = f"CONT-2026-{siguiente_id:03d}"

        row_num_cdp = ctk.CTkFrame(card_eco, fg_color="transparent")
        row_num_cdp.pack(fill="x", padx=14, pady=4)
        row_num_cdp.columnconfigure((0, 1), weight=1)

        f_num = ctk.CTkFrame(row_num_cdp, fg_color="transparent")
        f_num.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkLabel(f_num, text="Número de Contrato:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w")
        entry_num = ctk.CTkEntry(f_num)
        entry_num.insert(0, num_sugerido)
        entry_num.pack(fill="x", pady=2)

        f_cdp = ctk.CTkFrame(row_num_cdp, fg_color="transparent")
        f_cdp.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        ctk.CTkLabel(f_cdp, text="Certificado Presupuestal (CDP):", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w")
        entry_cdp = ctk.CTkEntry(f_cdp, placeholder_text="ej: CDP-2026-085")
        entry_cdp.insert(0, f"CDP-2026-{siguiente_id:03d}")
        entry_cdp.pack(fill="x", pady=2)

        row_fechas = ctk.CTkFrame(card_eco, fg_color="transparent")
        row_fechas.pack(fill="x", padx=14, pady=4)
        row_fechas.columnconfigure((0, 1), weight=1)

        f_ini = ctk.CTkFrame(row_fechas, fg_color="transparent")
        f_ini.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkLabel(f_ini, text="Fecha de Inicio (YYYY-MM-DD):", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w")
        entry_ini = ctk.CTkEntry(f_ini)
        entry_ini.insert(0, date.today().isoformat())
        entry_ini.pack(fill="x", pady=2)

        f_fin = ctk.CTkFrame(row_fechas, fg_color="transparent")
        f_fin.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        ctk.CTkLabel(f_fin, text="Fecha de Terminación (YYYY-MM-DD):", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w")
        entry_fin = ctk.CTkEntry(f_fin)
        entry_fin.insert(0, "2026-12-31")
        entry_fin.pack(fill="x", pady=2)

        ctk.CTkLabel(card_eco, text="Resolución Rectoral de Vinculación:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w", padx=14, pady=(6, 1))
        entry_res = ctk.CTkEntry(card_eco, placeholder_text="ej: Resolución Rectoral N° 124 de 2026")
        entry_res.insert(0, f"Res. Rectoral 2026-{siguiente_id:03d}")
        entry_res.pack(fill="x", padx=14, pady=(0, 8))

        row_sal = ctk.CTkFrame(card_eco, fg_color="transparent")
        row_sal.pack(fill="x", padx=14, pady=(4, 12))
        row_sal.columnconfigure((0, 1), weight=1)

        f_monto = ctk.CTkFrame(row_sal, fg_color="transparent")
        f_monto.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkLabel(f_monto, text="Asignación Básica Mensual ($ COP):", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w")
        entry_monto = ctk.CTkEntry(f_monto, placeholder_text="ej: 3500000")
        entry_monto.insert(0, "3500000")
        entry_monto.pack(fill="x", pady=2)

        f_calc = ctk.CTkFrame(row_sal, fg_color="transparent")
        f_calc.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        ctk.CTkLabel(f_calc, text="Asistente de Cálculo:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w")

        def _calcular_sugerido():
            sel_p = combo_prof.get()
            t_sel = combo_tipo.get()
            if not sel_p or sel_p == "Sin docentes registrados":
                return
            cod = sel_p.split(" - ")[0].strip()
            prof = self.controller.gestor_personas.buscar_profesor_por_codigo(cod)
            if not prof:
                return

            val_pto = self._obtener_parametro_decimal("VALOR_PUNTO_SALARIAL", Decimal("19850"))
            val_cat = self._obtener_parametro_decimal("VALOR_HORA_CATEDRA", Decimal("45000"))
            smmlv = self._obtener_parametro_decimal("SALARIO_MINIMO", Decimal("1300000"))

            try:
                hrs = Decimal(entry_horas.get().strip() or "40")
            except Exception:
                hrs = Decimal("40")

            if "AD_HONOREM" in t_sel:
                sug = Decimal("0")
            elif "PLANTA" in t_sel:
                pts = Decimal(str(getattr(prof, "puntosSalariales", 0) or 0))
                if pts == 0:
                    pts = Decimal("180")
                sug = (pts * val_pto).quantize(Decimal("1"))
            elif "CATEDRATICO" in t_sel:
                sug = (hrs * Decimal("4") * val_cat).quantize(Decimal("1"))
            else:  # OCASIONAL
                factor = Decimal("2.5") if hrs >= 40 else Decimal("1.25")
                sug = (smmlv * factor).quantize(Decimal("1"))

            entry_monto.delete(0, "end")
            entry_monto.insert(0, str(int(sug)))

        btn_sugerir = ctk.CTkButton(
            f_calc,
            text="💡 Calcular Sugerido",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#334155",
            hover_color="#475569",
            height=30,
            command=_calcular_sugerido,
        )
        btn_sugerir.pack(fill="x", pady=2)

        # Label de alerta / error
        lbl_error = ctk.CTkLabel(dialog, text="", text_color="#EF4444", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"))
        lbl_error.pack(pady=(4, 0))

        def _guardar():
            lbl_error.configure(text="")
            num = entry_num.get().strip()
            sel_p = combo_prof.get()
            t_sel = combo_tipo.get()
            ded_sel = combo_ded.get()
            hrs_str = entry_horas.get().strip()
            monto_str = entry_monto.get().strip()
            ini_str = entry_ini.get().strip()
            fin_str = entry_fin.get().strip()
            cdp = entry_cdp.get().strip()
            res = entry_res.get().strip()
            es_jub = switch_jubilado.get()

            if not num:
                lbl_error.configure(text="El número de contrato es obligatorio.")
                return

            if not sel_p or sel_p == "Sin docentes registrados":
                lbl_error.configure(text="Debe seleccionar un docente registrado.")
                return

            cod_p = sel_p.split(" - ")[0].strip()
            prof = self.controller.gestor_personas.buscar_profesor_por_codigo(cod_p)
            if not prof:
                lbl_error.configure(text="No se encontró el docente especificado.")
                return

            try:
                f_inicio = datetime.strptime(ini_str, "%Y-%m-%d").date()
                f_termina = datetime.strptime(fin_str, "%Y-%m-%d").date()
            except ValueError:
                lbl_error.configure(text="Las fechas deben tener el formato válido YYYY-MM-DD.")
                return

            try:
                hrs_val = Decimal(hrs_str)
            except Exception:
                lbl_error.configure(text="Las horas semanales deben ser un número válido.")
                return

            try:
                monto_val = Decimal(monto_str)
            except Exception:
                lbl_error.configure(text="La asignación básica debe ser un monto numérico válido.")
                return

            # Mapeo de modalidad
            if "PLANTA" in t_sel:
                mod = "PLANTA"
                regimen = "Decreto 1279 de 2002"
                tipo_c = "DOCENTE_PLANTA"
                es_ad = False
                val_hora_cat = Decimal("0")
                factor_smmlv = Decimal("0")
            elif "OCASIONAL" in t_sel:
                mod = "OCASIONAL"
                regimen = "Acuerdo 027 de 2024"
                tipo_c = "DOCENTE_OCASIONAL"
                es_ad = False
                val_hora_cat = Decimal("0")
                smmlv = self._obtener_parametro_decimal("SALARIO_MINIMO", Decimal("1300000"))
                factor_smmlv = (monto_val / smmlv).quantize(Decimal("0.01"))
            elif "CATEDRATICO" in t_sel:
                mod = "CATEDRATICO"
                regimen = "Acuerdo 027 de 2024"
                tipo_c = "DOCENTE_CATEDRATICO"
                es_ad = False
                val_hora_cat = self._obtener_parametro_decimal("VALOR_HORA_CATEDRA", Decimal("45000"))
                factor_smmlv = Decimal("0")
            else:  # AD_HONOREM
                mod = "CATEDRATICO_AD_HONOREM"
                regimen = "Acuerdo 027 de 2024"
                tipo_c = "DOCENTE_AD_HONOREM"
                es_ad = True
                val_hora_cat = Decimal("0")
                factor_smmlv = Decimal("0")
                monto_val = Decimal("0")

            dedicacion_enum = Dedicacion.TIEMPO_COMPLETO if ded_sel == "TIEMPO_COMPLETO" else (
                Dedicacion.MEDIO_TIEMPO if ded_sel == "MEDIO_TIEMPO" else Dedicacion.HORA_CATEDRA
            )

            arl_sel = combo_arl.get()
            clase_arl = "I" if "I " in arl_sel else ("II" if "II " in arl_sel else "III")

            nuevo_contrato = Contrato(
                idContrato=siguiente_id,
                idPersona=prof.idPersona,
                numeroContrato=num,
                tipoContrato=tipo_c,
                modalidadProfesor=mod,
                regimenAplicable=regimen,
                fechaInicio=f_inicio,
                fechaFin=f_termina,
                dedicacion=dedicacion_enum,
                horasSemanales=hrs_val,
                horasSemanalesAsignadas=hrs_val,
                horasMensualesAsignadas=hrs_val * Decimal("4"),
                horasMensualesCumplidas=hrs_val * Decimal("4"),
                horasIncumplidas=Decimal("0"),
                salarioBase=monto_val,
                salarioMensualPactado=monto_val,
                factorSalarialSMMLV=factor_smmlv,
                valorHoraCatedraVigente=val_hora_cat,
                esAdHonorem=es_ad,
                claseARL=clase_arl,
                numeroCDP=cdp,
                resolucionRectoral=res,
                actoAdministrativo=res,
                estado="ACTIVO",
            )

            # Validar con el gestor institucional
            try:
                self.controller.gestor_contratos.crear_contrato(nuevo_contrato, jubilado=es_jub)
            except ErrorContrato as err:
                lbl_error.configure(text=f"⚠️ {str(err)}")
                return
            except Exception as err:
                lbl_error.configure(text=f"Error inesperado: {str(err)}")
                return

            self.controller._recrear_gestores()
            self.controller.guardar_datos()
            dialog.destroy()
            self.actualizar()

        btn_guardar = ctk.CTkButton(
            dialog,
            text="💾 Registrar Contrato",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color="#006837",
            hover_color="#004D28",
            height=38,
            command=_guardar,
        )
        btn_guardar.pack(fill="x", padx=16, pady=(10, 14))

    # -------------------------------------------------------------------------
    # MODAL 2: RECONOCER PUNTOS / FACTOR / PRODUCTIVIDAD
    # -------------------------------------------------------------------------

    def _abrir_modal_reconocer_puntos(self) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title("⭐ Reconocer Factor / Productividad Decreto 1279")
        dialog.geometry("620x680")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        ctk.CTkLabel(
            dialog,
            text="⭐ Reconocimiento Salarial Decreto 1279 de 2002",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=Colors.TEXT_MAIN,
        ).pack(pady=(12, 2))

        ctk.CTkLabel(
            dialog,
            text="Títulos, Categorías, Experiencia y Producción Intelectual con cálculo de coautoría",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=Colors.TEXT_MUTED,
        ).pack(pady=(0, 10))

        scroll = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=16, pady=4)

        # 1. Docente
        card_p = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
        card_p.pack(fill="x", pady=4)

        ctk.CTkLabel(card_p, text="Docente Beneficiario:", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")).pack(anchor="w", padx=12, pady=(10, 2))
        prof_options = []
        for p in self.controller.profesores:
            pers = self._buscar_persona_por_id(p.idPersona)
            nom = f"{getattr(pers, 'primerNombre', '')} {getattr(pers, 'primerApellido', '')}" if pers else "Profesor"
            prof_options.append(f"{p.codigoProfesor} - {nom} [Puntos actuales: {getattr(p, 'puntosSalariales', 0)}]")

        if not prof_options:
            prof_options = ["Sin docentes registrados"]

        combo_prof = ctk.CTkComboBox(card_p, values=prof_options, width=420)
        combo_prof.pack(fill="x", padx=12, pady=(0, 10))

        # 2. Tipo de Reconocimiento
        card_tipo = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
        card_tipo.pack(fill="x", pady=6)

        ctk.CTkLabel(card_tipo, text="Dimensión del Decreto 1279:", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")).pack(anchor="w", padx=12, pady=(10, 2))

        seg_tipo = ctk.CTkSegmentedButton(
            card_tipo,
            values=["Título Académico", "Categoría Docente", "Experiencia Calificada", "Producción Intelectual", "Cargo Académico"],
        )
        seg_tipo.set("Título Académico")
        seg_tipo.pack(fill="x", padx=12, pady=6)

        # 3. Contenedor de Campos dinámicos
        card_fields = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
        card_fields.pack(fill="x", pady=6)

        ctk.CTkLabel(card_fields, text="Detalle de la Solicitud y Soportes:", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")).pack(anchor="w", padx=12, pady=(10, 6))

        lbl_desc = ctk.CTkLabel(card_fields, text="Descripción o Título:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"))
        lbl_desc.pack(anchor="w", padx=12, pady=(4, 1))
        entry_desc = ctk.CTkEntry(card_fields, placeholder_text="ej: Maestría en Ciencias de la Computación")
        entry_desc.pack(fill="x", padx=12, pady=(0, 6))

        # Campos específicos de Producción Académica (Ocultables)
        frame_prod = ctk.CTkFrame(card_fields, fg_color="transparent")

        ctk.CTkLabel(frame_prod, text="Revista / Editorial / Entidad Publicadora:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w", pady=(2, 1))
        entry_editorial = ctk.CTkEntry(frame_prod, placeholder_text="ej: IEEE Transactions on Software Engineering")
        entry_editorial.pack(fill="x", pady=(0, 6))

        row_prod_meta = ctk.CTkFrame(frame_prod, fg_color="transparent")
        row_prod_meta.pack(fill="x", pady=4)
        row_prod_meta.columnconfigure((0, 1), weight=1)

        f_id_prod = ctk.CTkFrame(row_prod_meta, fg_color="transparent")
        f_id_prod.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        ctk.CTkLabel(f_id_prod, text="DOI / ISSN / ISBN:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w")
        entry_ident = ctk.CTkEntry(f_id_prod, placeholder_text="ej: 10.1109/TSE.2025.123456")
        entry_ident.pack(fill="x", pady=2)

        f_autores = ctk.CTkFrame(row_prod_meta, fg_color="transparent")
        f_autores.grid(row=0, column=1, sticky="ew", padx=(4, 0))
        ctk.CTkLabel(f_autores, text="Número de Autores:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w")
        entry_autores = ctk.CTkEntry(f_autores)
        entry_autores.insert(0, "1")
        entry_autores.pack(fill="x", pady=2)

        lbl_coautoria_info = ctk.CTkLabel(frame_prod, text="Factor coautoría estimado: 100% de los puntos", text_color="#10B981", font=ctk.CTkFont(size=11, weight="bold"))
        lbl_coautoria_info.pack(anchor="w", pady=2)

        def _actualizar_coautoria(*_):
            try:
                n = int(entry_autores.get().strip() or "1")
                if n <= 3:
                    f = Decimal("1.0")
                elif n <= 5:
                    f = Decimal("0.5")
                else:
                    f = (Decimal("2") / Decimal(n)).quantize(Decimal("0.01"))
                lbl_coautoria_info.configure(text=f"Factor coautoría Dec. 1279: {int(f*100)}% de los puntos")
            except Exception:
                lbl_coautoria_info.configure(text="Factor coautoría: N/D")

        entry_autores.bind("<KeyRelease>", _actualizar_coautoria)

        # Campos comunes de Puntos y Acto Administrativo
        row_pts_acto = ctk.CTkFrame(card_fields, fg_color="transparent")
        row_pts_acto.pack(fill="x", padx=12, pady=6)
        row_pts_acto.columnconfigure((0, 1), weight=1)

        f_pts = ctk.CTkFrame(row_pts_acto, fg_color="transparent")
        f_pts.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        ctk.CTkLabel(f_pts, text="Puntos Base a Otorgar:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w")
        entry_pts = ctk.CTkEntry(f_pts, placeholder_text="ej: 40")
        entry_pts.insert(0, "40")
        entry_pts.pack(fill="x", pady=2)

        f_acto = ctk.CTkFrame(row_pts_acto, fg_color="transparent")
        f_acto.grid(row=0, column=1, sticky="ew", padx=(4, 0))
        ctk.CTkLabel(f_acto, text="Acto Administrativo / CIARP:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w")
        entry_acto = ctk.CTkEntry(f_acto, placeholder_text="ej: Res. Rectoral 104")
        entry_acto.insert(0, "Res. Rectoral 2026-CIARP")
        entry_acto.pack(fill="x", pady=2)

        # Manejador dinámico del segmented button
        def _on_seg_change(val: str) -> None:
            if val == "Producción Intelectual":
                frame_prod.pack(fill="x", padx=12, pady=4, before=row_pts_acto)
                lbl_desc.configure(text="Título del Artículo o Libro:")
                entry_desc.configure(placeholder_text="ej: Machine Learning Applications in Medicine")
                entry_pts.delete(0, "end")
                entry_pts.insert(0, "15")
            else:
                frame_prod.pack_forget()
                if val == "Título Académico":
                    lbl_desc.configure(text="Denominación del Título:")
                    entry_desc.configure(placeholder_text="ej: Doctorado en Ingeniería de Software")
                    entry_pts.delete(0, "end")
                    entry_pts.insert(0, "80")
                elif val == "Categoría Docente":
                    lbl_desc.configure(text="Ascenso de Categoría:")
                    entry_desc.configure(placeholder_text="ej: Ascenso a Profesor Titular")
                    entry_pts.delete(0, "end")
                    entry_pts.insert(0, "38")
                elif val == "Experiencia Calificada":
                    lbl_desc.configure(text="Detalle de Experiencia:")
                    entry_desc.configure(placeholder_text="ej: 4 años Docencia Universitaria")
                    entry_pts.delete(0, "end")
                    entry_pts.insert(0, "16")
                else:
                    lbl_desc.configure(text="Cargo o Función Administrativa:")
                    entry_desc.configure(placeholder_text="ej: Decanatura de Facultad")
                    entry_pts.delete(0, "end")
                    entry_pts.insert(0, "20")

        seg_tipo.configure(command=_on_seg_change)

        lbl_error = ctk.CTkLabel(dialog, text="", text_color="#EF4444", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"))
        lbl_error.pack(pady=(4, 0))

        def _guardar_reconocimiento():
            lbl_error.configure(text="")
            sel_p = combo_prof.get()
            t_dim = seg_tipo.get()
            desc = entry_desc.get().strip()
            pts_str = entry_pts.get().strip()
            acto = entry_acto.get().strip()

            if not desc:
                lbl_error.configure(text="Debe ingresar la descripción o título del reconocimiento.")
                return

            try:
                pts_val = Decimal(pts_str)
                if pts_val <= 0:
                    lbl_error.configure(text="Los puntos a otorgar deben ser mayores a cero.")
                    return
            except Exception:
                lbl_error.configure(text="Los puntos deben ser un valor numérico válido.")
                return

            if not sel_p or sel_p == "Sin docentes registrados":
                lbl_error.configure(text="Debe seleccionar un docente registrado.")
                return

            cod_p = sel_p.split(" - ")[0].strip()
            prof = self.controller.gestor_personas.buscar_profesor_por_codigo(cod_p)
            if not prof:
                lbl_error.configure(text="Docente no encontrado.")
                return

            if t_dim == "Producción Intelectual":
                editorial = entry_editorial.get().strip() or "Revista Universitaria"
                ident = entry_ident.get().strip() or f"DOI-2026-{len(self.controller.producciones)+1}"
                try:
                    num_aut = int(entry_autores.get().strip() or "1")
                    if num_aut <= 0:
                        num_aut = 1
                except Exception:
                    num_aut = 1

                prod = ProduccionAcademica(
                    idProduccion=len(self.controller.producciones) + 1,
                    idProfesor=prof.idProfesor,
                    tipoProduccion="ARTICULO",
                    titulo=desc,
                    fechaPublicacion=date.today(),
                    entidadPublicadora=editorial,
                    identificadorProducto=ident,
                    numeroAutores=num_aut,
                    puntosSolicitados=pts_val,
                    actoAdministrativo=acto or "Acta CIARP",
                )

                try:
                    self.controller.gestor_factores.registrar_produccion(prod)
                    self.controller.gestor_factores.reconocer_puntos(prod.idProduccion, pts_val)
                except ErrorFactor as err:
                    lbl_error.configure(text=f"⚠️ {str(err)}")
                    return
                except Exception as err:
                    lbl_error.configure(text=f"Error al registrar producción: {str(err)}")
                    return
            else:
                # Factor Salarial
                tipo_enum = (
                    TipoFactor.TITULO_ACADEMICO if t_dim == "Título Académico" else (
                        TipoFactor.CATEGORIA_DOCENTE if t_dim == "Categoría Docente" else (
                            TipoFactor.EXPERIENCIA if t_dim == "Experiencia Calificada" else TipoFactor.DIRECCION_ACADEMICO_ADMINISTRATIVA
                        )
                    )
                )

                fac = FactorSalarial(
                    idFactor=len(self.controller.factores) + 1,
                    idProfesor=prof.idProfesor,
                    tipoFactor=tipo_enum,
                    nombre=desc,
                    puntosSolicitados=pts_val,
                    puntosReconocidos=pts_val,
                    puntosAprobados=pts_val,
                    fechaReconocimiento=date.today(),
                    actoAdministrativo=acto or "Resolución Rectoral",
                    estado="APROBADO",
                )

                try:
                    self.controller.gestor_factores.registrar_factor(fac)
                    self.controller.gestor_factores.aprobar_factor(fac.idFactor, pts_val)
                except ErrorFactor as err:
                    lbl_error.configure(text=f"⚠️ {str(err)}")
                    return
                except Exception as err:
                    lbl_error.configure(text=f"Error al registrar factor: {str(err)}")
                    return

            self.controller._recrear_gestores()
            self.controller.guardar_datos()
            dialog.destroy()
            self.actualizar()

        btn_guardar = ctk.CTkButton(
            dialog,
            text="💾 Otorgar Reconocimiento y Actualizar Puntos",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color="#006837",
            hover_color="#004D28",
            height=38,
            command=_guardar_reconocimiento,
        )
        btn_guardar.pack(fill="x", padx=16, pady=(10, 14))

    # -------------------------------------------------------------------------
    # MODAL 3: TERMINAR CONTRATO (CON CAUSAL Y SOPORTE LEGAL)
    # -------------------------------------------------------------------------

    def _abrir_modal_terminar_contrato(self, cont: Contrato) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"🚫 Terminar Contrato {cont.numeroContrato}")
        dialog.geometry("480x420")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        pers = self._buscar_persona_por_id(cont.idPersona)
        nom_prof = f"{getattr(pers, 'primerNombre', '')} {getattr(pers, 'primerApellido', '')}" if pers else "Docente"

        ctk.CTkLabel(
            dialog,
            text="🚫 Terminación Contractual Formal",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color="#EF4444",
        ).pack(pady=(14, 4))

        ctk.CTkLabel(
            dialog,
            text=f"Contrato N° {cont.numeroContrato} · {nom_prof}",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=Colors.TEXT_MAIN,
        ).pack(pady=(0, 10))

        content = ctk.CTkFrame(dialog, fg_color=Colors.BG_CARD, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
        content.pack(fill="x", padx=16, pady=4)

        ctk.CTkLabel(content, text="Causal de Terminación (Obligatoria):", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w", padx=12, pady=(10, 2))
        combo_causal = ctk.CTkComboBox(
            content,
            values=[
                "Vencimiento del término pactado",
                "Renuncia regularmente aceptada",
                "Mutuo acuerdo entre las partes",
                "Destitución o sanción disciplinaria",
                "Incapacidad total o fuerza mayor",
            ],
            width=400,
        )
        combo_causal.pack(fill="x", padx=12, pady=(0, 8))

        ctk.CTkLabel(content, text="Documento Soporte / Acto Administrativo:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w", padx=12, pady=(4, 2))
        entry_doc = ctk.CTkEntry(content, placeholder_text="ej: Resolución Rectoral N° 340 de 2026")
        entry_doc.insert(0, f"Res. Liquidacion-{cont.numeroContrato}")
        entry_doc.pack(fill="x", padx=12, pady=(0, 8))

        ctk.CTkLabel(content, text="Fecha de Retiro Efectiva (YYYY-MM-DD):", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w", padx=12, pady=(4, 2))
        entry_f_ret = ctk.CTkEntry(content)
        entry_f_ret.insert(0, date.today().isoformat())
        entry_f_ret.pack(fill="x", padx=12, pady=(0, 12))

        lbl_error = ctk.CTkLabel(dialog, text="", text_color="#EF4444", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"))
        lbl_error.pack(pady=4)

        def _confirmar():
            causal = combo_causal.get().strip()
            doc = entry_doc.get().strip()
            f_str = entry_f_ret.get().strip()

            if not causal or not doc:
                lbl_error.configure(text="La causal y el documento soporte son estrictamente obligatorios.")
                return

            try:
                f_ret = datetime.strptime(f_str, "%Y-%m-%d").date()
            except Exception:
                lbl_error.configure(text="Formato de fecha inválido. Utilice YYYY-MM-DD.")
                return

            try:
                self.controller.gestor_contratos.terminar_contrato(cont.idContrato, causal=causal, documento=doc, fecha=f_ret)
            except ErrorContrato as err:
                lbl_error.configure(text=f"⚠️ {str(err)}")
                return
            except Exception as err:
                lbl_error.configure(text=f"Error: {str(err)}")
                return

            self.controller._recrear_gestores()
            self.controller.guardar_datos()
            dialog.destroy()
            self.actualizar()

        btn_term = ctk.CTkButton(
            dialog,
            text="🚫 Confirmar Terminación de Contrato",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#EF4444",
            hover_color="#DC2626",
            height=36,
            command=_confirmar,
        )
        btn_term.pack(fill="x", padx=16, pady=10)

    # -------------------------------------------------------------------------
    # MODAL 4: EDITAR CONTRATO
    # -------------------------------------------------------------------------

    def _abrir_modal_editar_contrato(self, cont: Contrato) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"✏️ Editar Contrato {cont.numeroContrato}")
        dialog.geometry("500x520")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        ctk.CTkLabel(
            dialog,
            text=f"✏️ Modificar Parámetros Contractuales",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=Colors.TEXT_MAIN,
        ).pack(pady=(14, 2))

        ctk.CTkLabel(
            dialog,
            text=f"Contrato {cont.numeroContrato} · {cont.tipoContrato}",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=Colors.TEXT_MUTED,
        ).pack(pady=(0, 8))

        content = ctk.CTkFrame(dialog, fg_color=Colors.BG_CARD, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
        content.pack(fill="both", expand=True, padx=16, pady=4)

        ctk.CTkLabel(content, text="Asignación Básica Mensual ($ COP):", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w", padx=12, pady=(10, 2))
        entry_sal = ctk.CTkEntry(content)
        entry_sal.insert(0, str(getattr(cont, "salarioBase", 0) or getattr(cont, "salarioMensualPactado", 0) or 0))
        entry_sal.pack(fill="x", padx=12, pady=(0, 6))

        ctk.CTkLabel(content, text="Horas Semanales Asignadas:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w", padx=12, pady=(4, 2))
        entry_hrs = ctk.CTkEntry(content)
        entry_hrs.insert(0, str(getattr(cont, "horasSemanales", 40) or 40))
        entry_hrs.pack(fill="x", padx=12, pady=(0, 6))

        ctk.CTkLabel(content, text="Fecha de Terminación / Prórroga (YYYY-MM-DD):", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w", padx=12, pady=(4, 2))
        entry_fin = ctk.CTkEntry(content)
        entry_fin.insert(0, str(getattr(cont, "fechaFin", "") or ""))
        entry_fin.pack(fill="x", padx=12, pady=(0, 6))

        ctk.CTkLabel(content, text="Certificado Presupuestal (CDP):", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w", padx=12, pady=(4, 2))
        entry_cdp = ctk.CTkEntry(content)
        entry_cdp.insert(0, str(getattr(cont, "numeroCDP", "") or ""))
        entry_cdp.pack(fill="x", padx=12, pady=(0, 6))

        ctk.CTkLabel(content, text="Observaciones / Modificaciones Contractuales:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w", padx=12, pady=(4, 2))
        entry_obs = ctk.CTkEntry(content)
        entry_obs.insert(0, str(getattr(cont, "observaciones", "") or ""))
        entry_obs.pack(fill="x", padx=12, pady=(0, 10))

        lbl_error = ctk.CTkLabel(dialog, text="", text_color="#EF4444", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"))
        lbl_error.pack(pady=4)

        def _guardar():
            lbl_error.configure(text="")
            sal_str = entry_sal.get().strip()
            hrs_str = entry_hrs.get().strip()
            fin_str = entry_fin.get().strip()

            try:
                sal_val = Decimal(sal_str)
                hrs_val = Decimal(hrs_str)
            except Exception:
                lbl_error.configure(text="El salario y las horas deben ser numéricos.")
                return

            f_fin = None
            if fin_str:
                try:
                    f_fin = datetime.strptime(fin_str, "%Y-%m-%d").date()
                except Exception:
                    lbl_error.configure(text="La fecha debe tener formato YYYY-MM-DD.")
                    return

            try:
                cambios: dict[str, Any] = {
                    "salarioBase": sal_val,
                    "salarioMensualPactado": sal_val,
                    "horasSemanales": hrs_val,
                    "horasSemanalesAsignadas": hrs_val,
                    "horasMensualesAsignadas": hrs_val * Decimal("4"),
                    "numeroCDP": entry_cdp.get().strip(),
                    "observaciones": entry_obs.get().strip(),
                }
                if f_fin:
                    cambios["fechaFin"] = f_fin

                self.controller.gestor_contratos.modificar_contrato(cont.idContrato, **cambios)
            except ErrorContrato as err:
                lbl_error.configure(text=f"⚠️ {str(err)}")
                return
            except Exception as err:
                lbl_error.configure(text=f"Error al modificar: {str(err)}")
                return

            self.controller._recrear_gestores()
            self.controller.guardar_datos()
            dialog.destroy()
            self.actualizar()

        btn_guardar = ctk.CTkButton(
            dialog,
            text="💾 Guardar Modificaciones",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=Colors.WIN_BLUE,
            hover_color=Colors.WIN_BLUE_HOVER,
            height=36,
            command=_guardar,
        )
        btn_guardar.pack(fill="x", padx=16, pady=10)

    # -------------------------------------------------------------------------
    # MODAL 5: DETALLE COMPLETO DEL CONTRATO
    # -------------------------------------------------------------------------

    def _abrir_modal_detalle_contrato(self, cont: Contrato) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"📄 Ficha Técnica del Contrato {cont.numeroContrato}")
        dialog.geometry("560x600")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        pers = self._buscar_persona_por_id(cont.idPersona)
        prof = self._buscar_profesor_por_id_persona(cont.idPersona)
        nom_prof = f"{getattr(pers, 'primerNombre', '')} {getattr(pers, 'primerApellido', '')}" if pers else "Docente"

        ctk.CTkLabel(
            dialog,
            text=f"📄 Ficha Técnica de Vinculación Docente",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=Colors.TEXT_MAIN,
        ).pack(pady=(14, 2))

        ctk.CTkLabel(
            dialog,
            text=f"Contrato N° {cont.numeroContrato} · Estado: {getattr(cont, 'estado', 'ACTIVO')}",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=Colors.TEXT_MUTED,
        ).pack(pady=(0, 10))

        scroll = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=16, pady=4)

        def _add_section(title: str, rows: list[tuple[str, str]]) -> None:
            card = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
            card.pack(fill="x", pady=6)
            ctk.CTkLabel(card, text=title, font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color=Colors.WIN_BLUE).pack(anchor="w", padx=12, pady=(8, 4))
            for k, v in rows:
                r = ctk.CTkFrame(card, fg_color="transparent")
                r.pack(fill="x", padx=12, pady=2)
                ctk.CTkLabel(r, text=f"{k}:", width=180, anchor="w", font=ctk.CTkFont(size=11, weight="bold"), text_color=Colors.TEXT_MUTED).pack(side="left")
                ctk.CTkLabel(r, text=str(v), anchor="w", font=ctk.CTkFont(size=11), text_color=Colors.TEXT_MAIN).pack(side="left", fill="x", expand=True)
            ctk.CTkFrame(card, height=4, fg_color="transparent").pack()

        _add_section("1. Datos Personales y Académicos", [
            ("Docente", nom_prof),
            ("Código Docente", getattr(prof, "codigoProfesor", "N/D")),
            ("Escalafón / Categoría", getattr(prof, "categoriaDocente", "AUXILIAR")),
            ("Puntos Salariales Dec. 1279", f"{getattr(prof, 'puntosSalariales', 0)} pts"),
        ])

        _add_section("2. Condiciones Contractuales y Jurídicas", [
            ("Modalidad", str(cont.modalidadProfesor or cont.tipoContrato)),
            ("Régimen Aplicable", str(cont.regimenAplicable or "N/D")),
            ("Dedicación", str(cont.dedicacion or "TC")),
            ("Horas Semanales", f"{cont.horasSemanales or 40} horas"),
            ("Clase de Riesgo ARL", f"Clase {cont.claseARL or 'I'}"),
            ("Es Ad-Honorem", "Sí" if cont.esAdHonorem else "No"),
        ])

        asig = cont.salarioBase or cont.salarioMensualPactado or 0
        asig_fmt = f"$ {int(float(asig)):,} COP" if str(asig).replace(".","").isdigit() else str(asig)

        _add_section("3. Presupuesto, Asignación y Vigencia", [
            ("Asignación Básica Mensual", asig_fmt),
            ("Disponibilidad (CDP)", str(cont.numeroCDP or "N/D")),
            ("Resolución de Nombramiento", str(cont.resolucionRectoral or cont.actoAdministrativo or "N/D")),
            ("Fecha de Inicio", str(cont.fechaInicio or "N/D")),
            ("Fecha de Terminación", str(cont.fechaFin or "N/D")),
            ("Estado Final", str(cont.estadoFinalContrato or cont.estado or "ACTIVO")),
            ("Causal de Retiro (si aplica)", str(cont.causalTerminacion or "N/A")),
        ])

        btn_cerrar = ctk.CTkButton(
            dialog,
            text="Cerrar",
            width=100,
            fg_color="#64748B",
            hover_color="#475569",
            command=dialog.destroy,
        )
        btn_cerrar.pack(pady=10)

    # -------------------------------------------------------------------------
    # HELPERS
    # -------------------------------------------------------------------------

    def _buscar_persona_por_id(self, id_persona: int | None) -> Any:
        if id_persona is None:
            return None
        return next((p for p in self.controller.personas if p.idPersona == id_persona), None)

    def _buscar_profesor_por_id(self, id_profesor: int | None) -> Any:
        if id_profesor is None:
            return None
        return next((p for p in self.controller.profesores if p.idProfesor == id_profesor), None)

    def _buscar_profesor_por_id_persona(self, id_persona: int | None) -> Any:
        if id_persona is None:
            return None
        return next((p for p in self.controller.profesores if p.idPersona == id_persona), None)

    def _obtener_parametro_decimal(self, codigo_str: str, defecto: Decimal) -> Decimal:
        for p in self.controller.parametros:
            cod = getattr(p.codigo, "value", str(p.codigo))
            if cod == codigo_str:
                try:
                    return Decimal(str(p.valor).replace(",", "."))
                except Exception:
                    return defecto
        return defecto

    def actualizar(self) -> None:
        for widget in self.winfo_children():
            widget.destroy()
        self._crear_interfaz()
