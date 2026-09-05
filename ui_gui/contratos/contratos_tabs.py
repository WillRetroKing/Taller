"""Renderizador de pestañas para Contratos Docentes y Factores Salariales."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Callable
import customtkinter as ctk

from ui_gui.theme import Colors, create_styled_tabview
from ui_gui.components import PITAGridTable

if TYPE_CHECKING:
    from ui_gui.gui_controller import PITAController
    from ui_gui.contratos.contratos_service import ContratosService
    from modelo_datos import Contrato


class ContratosTabsRenderer:
    """Renderiza las tablas de Contratos y Factores/Producción Académica."""

    def __init__(
        self,
        controller: PITAController,
        service: ContratosService,
        on_ver_contrato: Callable[[Contrato], None],
        on_editar_contrato: Callable[[Contrato], None],
        on_terminar_contrato: Callable[[Contrato], None],
    ) -> None:
        self.controller = controller
        self.service = service
        self.on_ver_contrato = on_ver_contrato
        self.on_editar_contrato = on_editar_contrato
        self.on_terminar_contrato = on_terminar_contrato

        self.filtro_modalidad = "TODAS LAS MODALIDADES"
        self.filtro_estado = "TODOS LOS ESTADOS"
        self.busqueda_texto = ""

    # -------------------------------------------------------------------------
    # TAB 1: CONTRATOS
    # -------------------------------------------------------------------------
    def llenar_tab_contratos(self, container: ctk.CTkFrame) -> None:
        for w in container.winfo_children():
            w.destroy()

        # Barra de Filtros y Búsqueda
        filter_bar = ctk.CTkFrame(container, fg_color=Colors.BG_CARD, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
        filter_bar.pack(fill="x", padx=6, pady=(4, 8))

        ctk.CTkLabel(filter_bar, text="🔍 Filtrar:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=Colors.TEXT_MUTED).pack(side="left", padx=(12, 6), pady=8)

        def _cambiar_mod(val: str) -> None:
            self.filtro_modalidad = val
            self.llenar_tab_contratos(container)

        combo_mod = ctk.CTkComboBox(
            filter_bar,
            values=["TODAS LAS MODALIDADES", "PLANTA", "OCASIONAL", "CATEDRATICO", "AD_HONOREM"],
            width=180,
            command=_cambiar_mod,
        )
        combo_mod.set(self.filtro_modalidad)
        combo_mod.pack(side="left", padx=4, pady=8)

        def _cambiar_est(val: str) -> None:
            self.filtro_estado = val
            self.llenar_tab_contratos(container)

        combo_est = ctk.CTkComboBox(
            filter_bar,
            values=["TODOS LOS ESTADOS", "ACTIVO", "TERMINADO"],
            width=150,
            command=_cambiar_est,
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

        def _buscar() -> None:
            self.busqueda_texto = entry_buscar.get().strip().lower()
            self.llenar_tab_contratos(container)

        entry_buscar.bind("<Return>", lambda e: _buscar())

        ctk.CTkButton(
            filter_bar,
            text="Buscar",
            width=70,
            fg_color=Colors.WIN_BLUE,
            hover_color=Colors.WIN_BLUE_HOVER,
            command=_buscar,
        ).pack(side="left", padx=4, pady=8)

        def _limpiar() -> None:
            self.filtro_modalidad = "TODAS LAS MODALIDADES"
            self.filtro_estado = "TODOS LOS ESTADOS"
            self.busqueda_texto = ""
            self.llenar_tab_contratos(container)

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

        table = PITAGridTable(container, headers=headers, col_weights=col_weights, col_mins=col_mins)
        table.pack(fill="both", expand=True, padx=4, pady=4)

        contratos = self.controller.contratos
        if not contratos:
            ctk.CTkLabel(table, text="No hay contratos vigentes registrados.", text_color="#94A3B8").pack(pady=25)
            return

        filtrados = []
        for cont in contratos:
            mod = str(getattr(cont, "modalidadProfesor", "") or getattr(cont, "tipoContrato", "")).upper()
            est = str(getattr(cont, "estado", "ACTIVO")).upper()

            if self.filtro_modalidad not in ("TODAS LAS MODALIDADES", "TODAS"):
                if self.filtro_modalidad == "AD_HONOREM" and not (getattr(cont, "esAdHonorem", False) or "AD_HONOREM" in mod):
                    continue
                elif self.filtro_modalidad != "AD_HONOREM" and self.filtro_modalidad not in mod:
                    continue

            if self.filtro_estado not in ("TODOS LOS ESTADOS", "TODOS"):
                if self.filtro_estado == "ACTIVO" and est != "ACTIVO":
                    continue
                if self.filtro_estado == "TERMINADO" and est not in ("TERMINADO", "INACTIVO"):
                    continue

            if self.busqueda_texto:
                pers = self.service.buscar_persona_por_id(cont.idPersona)
                nom = f"{getattr(pers, 'primerNombre', '')} {getattr(pers, 'primerApellido', '')}".lower()
                num = str(getattr(cont, "numeroContrato", "")).lower()
                if self.busqueda_texto not in nom and self.busqueda_texto not in num:
                    continue

            filtrados.append(cont)

        if not filtrados:
            ctk.CTkLabel(table, text="No se encontraron contratos con los filtros aplicados.", text_color="#94A3B8").pack(pady=25)
            return

        for cont in filtrados:
            pers = self.service.buscar_persona_por_id(cont.idPersona)
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
                ("👁️ Ver", lambda c=cont: self.on_ver_contrato(c), "#334155", "#475569", 55, 26),
                ("✏️ Editar", lambda c=cont: self.on_editar_contrato(c), Colors.WIN_BLUE, Colors.WIN_BLUE_HOVER, 60, 26),
            ]
            if est == "ACTIVO":
                btn_list.append(("🚫 Terminar", lambda c=cont: self.on_terminar_contrato(c), "#EF4444", "#DC2626", 75, 26))

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

    # -------------------------------------------------------------------------
    # TAB 2: FACTORES SALARIALES Y ESCALAFÓN
    # -------------------------------------------------------------------------
    def llenar_tab_factores(self, container: ctk.CTkFrame) -> None:
        for w in container.winfo_children():
            w.destroy()

        sub_tabview = create_styled_tabview(container)
        sub_tabview.pack(fill="both", expand=True, padx=4, pady=4)

        tab_fac_base = sub_tabview.add("📜 Factores Salariales Reconocidos")
        tab_prod_acad = sub_tabview.add("🔬 Producción Intelectual / Obras")

        # Sub-tab A: Factores
        headers_fac = ["Docente", "Tipo de Factor", "Concepto / Descripción", "Puntos Reconocidos", "Acto Administrativo", "Fecha Reconocimiento", "Estado"]
        col_w_fac = [3, 2, 4, 2, 3, 2, 2]
        col_m_fac = [160, 130, 200, 110, 140, 100, 80]

        table_fac = PITAGridTable(tab_fac_base, headers=headers_fac, col_weights=col_w_fac, col_mins=col_m_fac)
        table_fac.pack(fill="both", expand=True, padx=4, pady=4)

        if not self.controller.factores:
            ctk.CTkLabel(table_fac, text="No hay factores salariales registrados.", text_color="#94A3B8").pack(pady=25)
        else:
            for fac in self.controller.factores:
                prof = self.service.buscar_profesor_por_id(fac.idProfesor)
                pers = self.service.buscar_persona_por_id(getattr(prof, "idPersona", None))
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
                prof = self.service.buscar_profesor_por_id(prod.idProfesor)
                pers = self.service.buscar_persona_por_id(getattr(prof, "idPersona", None))
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
