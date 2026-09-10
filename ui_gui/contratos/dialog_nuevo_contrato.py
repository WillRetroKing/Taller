"""Modal para registrar contratos de vinculación docente y administrativa en PITA."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Callable
import customtkinter as ctk

from ui_gui.theme import Colors
from ui_gui.components import clean_enum

if TYPE_CHECKING:
    from ui_gui.gui_controller import PITAController
    from ui_gui.contratos.contratos_service import ContratosService


class DialogNuevoContrato(ctk.CTkToplevel):
    """Diálogo modal adaptativo para registro de contrato laboral (Docente o Administrativo)."""

    def __init__(
        self,
        parent: ctk.CTkBaseClass,
        controller: PITAController,
        service: ContratosService,
        on_success: Callable[[], None],
    ) -> None:
        super().__init__(parent)
        self.controller = controller
        self.service = service
        self.on_success = on_success

        self.title("➕ Registrar Vinculación Contractual")
        self.geometry("640x720")
        self.transient(parent.winfo_toplevel())
        self.grab_set()

        self._construir_ui()

    def _construir_ui(self) -> None:
        ctk.CTkLabel(
            self,
            text="📝 Vinculación Contractual y Formalización de Nómina",
            font=ctk.CTkFont(family="Segoe UI", size=17, weight="bold"),
            text_color=Colors.TEXT_MAIN,
        ).pack(pady=(12, 2))

        ctk.CTkLabel(
            self,
            text="Formalización jurídica laboral para docentes (D. 1279 / Ac. 027) y funcionarios administrativos (CST / L. 100)",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=Colors.TEXT_MUTED,
        ).pack(pady=(0, 8))

        # Selector de Tipo de Personal
        self.seg_tipo = ctk.CTkSegmentedButton(
            self,
            values=["👨‍🏫 Personal Docente", "👔 Personal Administrativo"],
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            selected_color=Colors.WIN_BLUE,
            command=self._on_cambiar_tipo_personal,
        )
        self.seg_tipo.set("👨‍🏫 Personal Docente")
        self.seg_tipo.pack(padx=16, pady=(0, 6), fill="x")

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=16, pady=4)

        # CARD 1: VINCULACIÓN Y EMPLEADO
        self.card_vinculacion = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
        self.card_vinculacion.pack(fill="x", pady=6)

        self.lbl_card1_title = ctk.CTkLabel(
            self.card_vinculacion,
            text="1. Empleado y Modalidad de Vinculación",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=Colors.TEXT_MAIN,
        )
        self.lbl_card1_title.pack(anchor="w", padx=14, pady=(10, 6))

        # Contenedor dinámico de selección de Empleado
        self.f_selector_persona = ctk.CTkFrame(self.card_vinculacion, fg_color="transparent")
        self.f_selector_persona.pack(fill="x", padx=14, pady=(0, 4))

        self.lbl_sel_emp = ctk.CTkLabel(self.f_selector_persona, text="Seleccionar Docente *:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"))
        self.lbl_sel_emp.pack(anchor="w", pady=(2, 1))

        # Combo Docentes
        prof_options = []
        for p in self.controller.profesores:
            pers = self.service.buscar_persona_por_id(p.idPersona)
            nombres = " ".join(part for part in [getattr(pers, 'primerNombre', ''), getattr(pers, 'segundoNombre', ''), getattr(pers, 'primerApellido', ''), getattr(pers, 'segundoApellido', '')] if part) if pers else "Profesor"
            cat = getattr(p, "categoriaDocente", "AUXILIAR") or "DOCENTE"
            pts = getattr(p, "puntosSalariales", 0) or 0
            prof_options.append(f"{p.codigoProfesor} - {nombres} [{cat}, {pts} pts]")
        if not prof_options:
            prof_options = ["Sin docentes registrados"]
        self.combo_prof = ctk.CTkComboBox(self.f_selector_persona, values=prof_options, width=420, command=self._on_seleccionar_prof)
        self.combo_prof.pack(fill="x", pady=(0, 4))

        # Combo Administrativos (inicialmente oculto o se intercambia)
        adm_options = []
        for a in self.controller.administrativos:
            pers = self.service.buscar_persona_por_id(a.idPersona)
            nom = f"{getattr(pers, 'primerNombre', '')} {getattr(pers, 'primerApellido', '')}" if pers else "Administrativo"
            adm_options.append(f"{a.codigoEmpleado} - {nom} ({a.cargo or 'Cargo'})")
        if not adm_options:
            adm_options = ["Sin administrativos registrados"]
        self.combo_adm = ctk.CTkComboBox(self.f_selector_persona, values=adm_options, width=420, command=self._on_seleccionar_adm)

        self.switch_jubilado = ctk.CTkSwitch(self.card_vinculacion, text="¿El empleado es pensionado / jubilado? (Restricción legal)", onvalue=True, offvalue=False)
        self.switch_jubilado.pack(anchor="w", padx=14, pady=4)

        ctk.CTkLabel(self.card_vinculacion, text="Modalidad Contractual / Régimen Jurídico:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w", padx=14, pady=(6, 1))
        self.combo_tipo = ctk.CTkComboBox(
            self.card_vinculacion,
            values=[
                "DOCENTE_PLANTA (Dec. 1279)",
                "DOCENTE_OCASIONAL (Ac. 027/2024)",
                "DOCENTE_CATEDRATICO (Ac. 027/2024)",
                "DOCENTE_AD_HONOREM",
            ],
            width=420,
            command=lambda _=None: self._on_cambiar_modalidad_docente(),
        )
        self.combo_tipo.pack(fill="x", padx=14, pady=(0, 8))

        row_ded = ctk.CTkFrame(self.card_vinculacion, fg_color="transparent")
        row_ded.pack(fill="x", padx=14, pady=4)
        row_ded.columnconfigure((0, 1), weight=1)

        f_ded = ctk.CTkFrame(row_ded, fg_color="transparent")
        f_ded.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.lbl_ded = ctk.CTkLabel(f_ded, text="Dedicación:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"))
        self.lbl_ded.pack(anchor="w")
        self.combo_ded = ctk.CTkComboBox(f_ded, values=["TIEMPO_COMPLETO", "MEDIO_TIEMPO", "HORA_CATEDRA"], command=lambda _=None: self._calcular_sugerido())
        self.combo_ded.pack(fill="x", pady=2)

        f_hrs = ctk.CTkFrame(row_ded, fg_color="transparent")
        f_hrs.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        self.lbl_hrs = ctk.CTkLabel(f_hrs, text="Horas Semanales (máx 18h cátedra):", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"))
        self.lbl_hrs.pack(anchor="w")
        self.entry_horas = ctk.CTkEntry(f_hrs, placeholder_text="40")
        self.entry_horas.insert(0, "40")
        self.entry_horas.pack(fill="x", pady=2)
        self.entry_horas.bind("<KeyRelease>", lambda _=None: self._calcular_sugerido())

        row_arl = ctk.CTkFrame(self.card_vinculacion, fg_color="transparent")
        row_arl.pack(fill="x", padx=14, pady=(4, 12))
        row_arl.columnconfigure((0, 1), weight=1)

        f_arl = ctk.CTkFrame(row_arl, fg_color="transparent")
        f_arl.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkLabel(f_arl, text="Clase de Riesgo ARL:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w")
        self.combo_arl = ctk.CTkComboBox(f_arl, values=["CLASE I (0.522%)", "CLASE II (1.044%)", "CLASE III (2.436%)"])
        self.combo_arl.pack(fill="x", pady=2)

        # Info de Auxilio de Transporte para administrativos
        f_aux = ctk.CTkFrame(row_arl, fg_color="transparent")
        f_aux.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        self.lbl_aux_info = ctk.CTkLabel(f_aux, text="Auxilio Legal de Transporte:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"))
        self.lbl_aux_info.pack(anchor="w")
        self.lbl_aux_status = ctk.CTkLabel(f_aux, text="No Aplica (Exclusivo Docente)", font=ctk.CTkFont(family="Segoe UI", size=11), text_color=Colors.TEXT_MUTED)
        self.lbl_aux_status.pack(anchor="w", pady=4)

        # CARD 2: VIGENCIA Y ASIGNACIÓN
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
        self.entry_num = ctk.CTkEntry(f_num)
        self.entry_num.insert(0, num_sugerido)
        self.entry_num.pack(fill="x", pady=2)

        f_cdp = ctk.CTkFrame(row_num_cdp, fg_color="transparent")
        f_cdp.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        ctk.CTkLabel(f_cdp, text="Certificado Presupuestal (CDP):", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w")
        self.entry_cdp = ctk.CTkEntry(f_cdp, placeholder_text="ej: CDP-2026-085")
        self.entry_cdp.insert(0, f"CDP-2026-{siguiente_id:03d}")
        self.entry_cdp.pack(fill="x", pady=2)

        row_fechas = ctk.CTkFrame(card_eco, fg_color="transparent")
        row_fechas.pack(fill="x", padx=14, pady=4)
        row_fechas.columnconfigure((0, 1), weight=1)

        f_ini = ctk.CTkFrame(row_fechas, fg_color="transparent")
        f_ini.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkLabel(f_ini, text="Fecha de Inicio (YYYY-MM-DD):", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w")
        self.entry_ini = ctk.CTkEntry(f_ini)
        self.entry_ini.insert(0, date.today().isoformat())
        self.entry_ini.pack(fill="x", pady=2)

        f_fin = ctk.CTkFrame(row_fechas, fg_color="transparent")
        f_fin.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        ctk.CTkLabel(f_fin, text="Fecha de Terminación (YYYY-MM-DD):", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w")
        self.entry_fin = ctk.CTkEntry(f_fin)
        self.entry_fin.insert(0, "2026-12-31")
        self.entry_fin.pack(fill="x", pady=2)

        ctk.CTkLabel(card_eco, text="Acto Administrativo / Resolución de Nombramiento:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w", padx=14, pady=(6, 1))
        self.entry_res = ctk.CTkEntry(card_eco, placeholder_text="ej: Resolución Rectoral N° 124 de 2026")
        self.entry_res.insert(0, f"Res. Rectoral 2026-{siguiente_id:03d}")
        self.entry_res.pack(fill="x", padx=14, pady=(0, 8))

        row_sal = ctk.CTkFrame(card_eco, fg_color="transparent")
        row_sal.pack(fill="x", padx=14, pady=(4, 12))
        row_sal.columnconfigure((0, 1), weight=1)

        f_monto = ctk.CTkFrame(row_sal, fg_color="transparent")
        f_monto.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkLabel(f_monto, text="Asignación Básica Mensual ($ COP):", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w")
        self.entry_monto = ctk.CTkEntry(f_monto, placeholder_text="ej: 3500000")
        self.entry_monto.insert(0, "3500000")
        self.entry_monto.pack(fill="x", pady=2)

        f_calc = ctk.CTkFrame(row_sal, fg_color="transparent")
        f_calc.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        ctk.CTkLabel(f_calc, text="Asistente de Cálculo:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w")

        self.btn_calc = ctk.CTkButton(
            f_calc,
            text="⚡ Calcular Según Régimen",
            fg_color="#0284C7",
            hover_color="#0369A1",
            command=self._calcular_sugerido,
        )
        self.btn_calc.pack(fill="x", pady=2)

        self.lbl_calc_info = ctk.CTkLabel(f_calc, text="", font=ctk.CTkFont(family="Segoe UI", size=10), text_color="#10B981")
        self.lbl_calc_info.pack(anchor="w", pady=(1, 0))

        self.lbl_error = ctk.CTkLabel(scroll, text="", text_color="#EF4444", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"))
        self.lbl_error.pack(pady=4)

        # Botón Guardar
        btn_guardar = ctk.CTkButton(
            scroll,
            text="💾 Formalizar y Registrar Vinculación Contractual",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color="#006837",
            hover_color="#004D28",
            height=40,
            command=self._guardar,
        )
        btn_guardar.pack(fill="x", padx=14, pady=(8, 16))

    def _on_cambiar_tipo_personal(self, val: str) -> None:
        siguiente_id = max((c.idContrato or 0 for c in self.controller.contratos), default=0) + 1
        if "Docente" in val:
            self.lbl_sel_emp.configure(text="Seleccionar Docente *:")
            self.combo_adm.pack_forget()
            self.combo_prof.pack(fill="x", pady=(0, 4))
            self.switch_jubilado.configure(state="normal")
            self.combo_tipo.configure(values=[
                "DOCENTE_PLANTA (Dec. 1279)",
                "DOCENTE_OCASIONAL (Ac. 027/2024)",
                "DOCENTE_CATEDRATICO (Ac. 027/2024)",
                "DOCENTE_AD_HONOREM",
            ])
            self.combo_tipo.set("DOCENTE_PLANTA (Dec. 1279)")
            self.combo_ded.configure(values=["TIEMPO_COMPLETO", "MEDIO_TIEMPO", "HORA_CATEDRA"])
            self.combo_ded.set("TIEMPO_COMPLETO")
            self.entry_horas.delete(0, "end")
            self.entry_horas.insert(0, "40")
            self.entry_num.delete(0, "end")
            self.entry_num.insert(0, f"CONT-2026-{siguiente_id:03d}")
            self.lbl_aux_status.configure(text="No Aplica (Exclusivo Docente)", text_color=Colors.TEXT_MUTED)
            self.btn_calc.configure(text="⚡ Calcular Según Régimen")
            self._calcular_sugerido()
        else:
            self.lbl_sel_emp.configure(text="Seleccionar Funcionario Administrativo *:")
            self.combo_prof.pack_forget()
            self.combo_adm.pack(fill="x", pady=(0, 4))
            self.switch_jubilado.configure(state="disabled")
            self.combo_tipo.configure(values=[
                "TERMINO_INDEFINIDO (CST)",
                "TERMINO_FIJO (CST)",
                "CARRERA_ADMINISTRATIVA",
                "LIBRE_NOMBRAMIENTO",
                "PROVISIONALIDAD",
            ])
            self.combo_tipo.set("TERMINO_INDEFINIDO (CST)")
            self.combo_ded.configure(values=["TIEMPO_COMPLETO"])
            self.combo_ded.set("TIEMPO_COMPLETO")
            self.entry_horas.delete(0, "end")
            self.entry_horas.insert(0, "40")
            self.entry_num.delete(0, "end")
            self.entry_num.insert(0, f"ADM-CONTRATO-{siguiente_id:03d}")
            self.btn_calc.configure(text="⚡ Asignar Salario del Cargo")
            self._on_seleccionar_adm()

    def _on_seleccionar_adm(self, *args) -> None:
        sel_a = self.combo_adm.get()
        if not sel_a or sel_a == "Sin administrativos registrados":
            return
        cod = sel_a.split(" - ")[0].strip()
        adm = next((a for a in self.controller.administrativos if str(a.codigoEmpleado).strip() == cod), None)
        if adm:
            sal = getattr(adm, "salarioBase", Decimal("2800000")) or Decimal("2800000")
            self.entry_monto.delete(0, "end")
            self.entry_monto.insert(0, str(int(sal)))
            if sal <= Decimal("3501810"):
                self.lbl_aux_status.configure(text="Aplica ($249.095 COP)", text_color="#10B981")
            else:
                self.lbl_aux_status.configure(text="No Aplica (> 2 SMMLV)", text_color=Colors.TEXT_MUTED)

    def _on_seleccionar_prof(self, *args) -> None:
        sel_p = self.combo_prof.get()
        if not sel_p or "Sin docentes" in sel_p:
            return
        cod = sel_p.split(" - ")[0].strip() if " - " in sel_p else sel_p.strip()
        prof = next((p for p in self.controller.profesores if str(getattr(p, "codigoProfesor", "")).strip() == cod), None)
        if not prof:
            prof = self.controller.gestor_personas.buscar_profesor_por_codigo(cod)
        if not prof:
            return

        tipo_p = clean_enum(getattr(prof, "tipoProfesor", "")).upper()
        if "CATEDRATICO" in tipo_p:
            self.combo_tipo.set("DOCENTE_CATEDRATICO (Ac. 027/2024)")
            self.combo_ded.set("HORA_CATEDRA")
            hrs_val = str(int(getattr(prof, "numeroHorasSemanales", 16) or 16))
            self.entry_horas.delete(0, "end")
            self.entry_horas.insert(0, hrs_val)
        elif "OCASIONAL" in tipo_p:
            self.combo_tipo.set("DOCENTE_OCASIONAL (Ac. 027/2024)")
            ded = clean_enum(getattr(prof, "dedicacion", "TIEMPO_COMPLETO"))
            self.combo_ded.set(ded if ded in ["TIEMPO_COMPLETO", "MEDIO_TIEMPO"] else "TIEMPO_COMPLETO")
            self.entry_horas.delete(0, "end")
            self.entry_horas.insert(0, "20" if "MEDIO" in ded else "40")
        else:
            self.combo_tipo.set("DOCENTE_PLANTA (Dec. 1279)")
            self.combo_ded.set("TIEMPO_COMPLETO")
            self.entry_horas.delete(0, "end")
            self.entry_horas.insert(0, "40")

        self._calcular_sugerido()

    def _on_cambiar_modalidad_docente(self, *args) -> None:
        m = self.combo_tipo.get().upper()
        if "CATEDRATICO" in m:
            self.combo_ded.set("HORA_CATEDRA")
            if self.entry_horas.get().strip() in ("40", ""):
                self.entry_horas.delete(0, "end")
                self.entry_horas.insert(0, "16")
        elif "PLANTA" in m:
            self.combo_ded.set("TIEMPO_COMPLETO")
            if self.entry_horas.get().strip() in ("16", ""):
                self.entry_horas.delete(0, "end")
                self.entry_horas.insert(0, "40")
        self._calcular_sugerido()

    def _calcular_sugerido(self) -> None:
        if "Administrativo" in self.seg_tipo.get():
            self._on_seleccionar_adm()
            return

        sel_p = self.combo_prof.get()
        t_sel = self.combo_tipo.get()
        if not sel_p or "Sin docentes" in sel_p:
            if hasattr(self, "lbl_calc_info"):
                self.lbl_calc_info.configure(text="⚠️ Seleccione un docente válido", text_color="#EF4444")
            return

        cod = sel_p.split(" - ")[0].strip() if " - " in sel_p else sel_p.strip()
        prof = next((p for p in self.controller.profesores if str(getattr(p, "codigoProfesor", "")).strip() == cod), None)
        if not prof:
            prof = self.controller.gestor_personas.buscar_profesor_por_codigo(cod)
        if not prof:
            prof = next((p for p in self.controller.profesores if cod in str(getattr(p, "codigoProfesor", ""))), None)
        if not prof:
            if hasattr(self, "lbl_calc_info"):
                self.lbl_calc_info.configure(text=f"⚠️ No se encontró al docente {cod}", text_color="#EF4444")
            return

        try:
            hrs = Decimal(self.entry_horas.get().strip() or "0")
        except Exception:
            hrs = Decimal("16") if ("CATEDRATICO" in t_sel.upper() or "CATEDRA" in self.combo_ded.get().upper()) else Decimal("40")

        sug, formula = self.service.calcular_asignacion_sugerida(t_sel, prof, self.combo_ded.get(), hrs)
        self.entry_monto.delete(0, "end")
        self.entry_monto.insert(0, str(int(sug)))

        if hasattr(self, "lbl_calc_info"):
            self.lbl_calc_info.configure(text=f"✅ {formula}", text_color="#10B981")

    def _guardar(self) -> None:
        num = self.entry_num.get().strip()
        t_sel = self.combo_tipo.get()
        es_admin = "Administrativo" in self.seg_tipo.get()

        try:
            hrs = Decimal(self.entry_horas.get().strip() or "40")
        except Exception:
            self.lbl_error.configure(text="⚠️ Ingrese un número de horas válido.")
            return

        try:
            f_ini = date.fromisoformat(self.entry_ini.get().strip())
            f_fin_str = self.entry_fin.get().strip()
            f_fin = date.fromisoformat(f_fin_str) if f_fin_str else None
        except ValueError:
            self.lbl_error.configure(text="⚠️ Formato de fechas inválido (use YYYY-MM-DD).")
            return

        try:
            monto = Decimal(self.entry_monto.get().strip() or "0")
        except Exception:
            self.lbl_error.configure(text="⚠️ Ingrese un valor de asignación válido.")
            return

        if es_admin:
            sel_a = self.combo_adm.get()
            if not sel_a or sel_a == "Sin administrativos registrados":
                self.lbl_error.configure(text="⚠️ Debe seleccionar un funcionario administrativo.")
                return
            cod = sel_a.split(" - ")[0].strip()
            adm = next((a for a in self.controller.administrativos if str(a.codigoEmpleado).strip() == cod), None)
            if not adm:
                self.lbl_error.configure(text="⚠️ Funcionario no encontrado.")
                return

            ok, msg = self.service.validar_contrato(num, adm.idPersona, t_sel, hrs, False)
            if not ok:
                self.lbl_error.configure(text=f"⚠️ {msg}")
                return

            tipo_clean = t_sel.split(" ")[0]
            datos = {
                "numeroContrato": num,
                "idPersona": adm.idPersona,
                "tipoContrato": tipo_clean,
                "modalidadProfesor": tipo_clean,
                "regimenAplicable": "CST_LEY100_ADMINISTRATIVO",
                "fechaInicio": f_ini,
                "fechaFin": f_fin,
                "dedicacion": "TIEMPO_COMPLETO",
                "horasSemanales": int(hrs),
                "salarioBase": monto,
                "salarioMensualPactado": monto,
                "aplicaAuxilioTransporte": bool(monto <= Decimal("3501810")),
                "esPensionado": False,
                "esAdHonorem": False,
                "numeroCDP": self.entry_cdp.get().strip(),
                "resolucionNombramiento": self.entry_res.get().strip(),
                "claseRiesgoARL": self.combo_arl.get(),
                "observaciones": f"Cargo: {adm.cargo} | Dependencia: {adm.dependencia}",
            }
        else:
            sel_p = self.combo_prof.get()
            if not sel_p or sel_p == "Sin docentes registrados":
                self.lbl_error.configure(text="⚠️ Debe seleccionar un docente válido.")
                return

            cod = sel_p.split(" - ")[0].strip() if " - " in sel_p else sel_p.strip()
            prof = next((p for p in self.controller.profesores if str(getattr(p, "codigoProfesor", "")).strip() == cod), None)
            if not prof:
                prof = self.controller.gestor_personas.buscar_profesor_por_codigo(cod)
            if not prof:
                self.lbl_error.configure(text="⚠️ Docente no encontrado en la base de datos.")
                return

            es_jub = self.switch_jubilado.get()
            ok, msg = self.service.validar_contrato(num, prof.idPersona, t_sel, hrs, es_jub)
            if not ok:
                self.lbl_error.configure(text=f"⚠️ {msg}")
                return

            tipo_clean = t_sel.split(" ")[0]
            modalidad = "PLANTA" if "PLANTA" in t_sel else ("OCASIONAL" if "OCASIONAL" in t_sel else ("CATEDRATICO" if "CATEDRATICO" in t_sel else "AD_HONOREM"))
            es_adh = "AD_HONOREM" in t_sel

            datos = {
                "numeroContrato": num,
                "idPersona": prof.idPersona,
                "tipoContrato": tipo_clean,
                "modalidadProfesor": modalidad,
                "regimenAplicable": "Decreto 1279 de 2002" if "PLANTA" in t_sel else "Acuerdo 027 de 2024",
                "fechaInicio": f_ini,
                "fechaFin": f_fin,
                "dedicacion": self.combo_ded.get(),
                "horasSemanales": int(hrs),
                "salarioBase": monto,
                "salarioMensualPactado": monto,
                "esPensionado": es_jub,
                "esAdHonorem": es_adh,
                "numeroCDP": self.entry_cdp.get().strip(),
                "resolucionNombramiento": self.entry_res.get().strip(),
                "claseRiesgoARL": self.combo_arl.get(),
            }

        self.service.registrar_contrato(datos)
        self.destroy()
        self.on_success()
