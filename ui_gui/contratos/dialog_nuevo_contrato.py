"""Modal para registrar contratos de vinculación docente en PITA."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Callable
import customtkinter as ctk

from ui_gui.theme import Colors

if TYPE_CHECKING:
    from ui_gui.gui_controller import PITAController
    from ui_gui.contratos.contratos_service import ContratosService


class DialogNuevoContrato(ctk.CTkToplevel):
    """Diálogo modal para registro de contrato docente."""

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

        self.title("➕ Registrar Contrato Docente")
        self.geometry("640x680")
        self.transient(parent.winfo_toplevel())
        self.grab_set()

        self._construir_ui()

    def _construir_ui(self) -> None:
        ctk.CTkLabel(
            self,
            text="📝 Vinculación Contractual Docente",
            font=ctk.CTkFont(family="Segoe UI", size=17, weight="bold"),
            text_color=Colors.TEXT_MAIN,
        ).pack(pady=(12, 4))

        ctk.CTkLabel(
            self,
            text="Verificación automática de topes de horas, incompatibilidad de jubilados y cálculo salarial",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=Colors.TEXT_MUTED,
        ).pack(pady=(0, 10))

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=16, pady=4)

        # CARD 1: DOCENTE Y MODALIDAD
        card_docente = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
        card_docente.pack(fill="x", pady=6)

        ctk.CTkLabel(card_docente, text="1. Docente y Modalidad de Vinculación", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), text_color=Colors.TEXT_MAIN).pack(anchor="w", padx=14, pady=(10, 6))

        ctk.CTkLabel(card_docente, text="Seleccionar Docente:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w", padx=14, pady=(4, 1))

        prof_options = []
        for p in self.controller.profesores:
            pers = self.service.buscar_persona_por_id(p.idPersona)
            nom = f"{getattr(pers, 'primerNombre', '')} {getattr(pers, 'primerApellido', '')}" if pers else "Profesor"
            cat = getattr(p, "categoriaDocente", "AUXILIAR") or "DOCENTE"
            pts = getattr(p, "puntosSalariales", 0) or 0
            prof_options.append(f"{p.codigoProfesor} - {nom} [{cat}, {pts} pts]")

        if not prof_options:
            prof_options = ["Sin docentes registrados"]

        self.combo_prof = ctk.CTkComboBox(card_docente, values=prof_options, width=420)
        self.combo_prof.pack(fill="x", padx=14, pady=(0, 8))

        self.switch_jubilado = ctk.CTkSwitch(card_docente, text="¿El docente es pensionado / jubilado? (Aplica restricción legal)", onvalue=True, offvalue=False)
        self.switch_jubilado.pack(anchor="w", padx=14, pady=4)

        ctk.CTkLabel(card_docente, text="Modalidad de Vinculación:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w", padx=14, pady=(6, 1))
        self.combo_tipo = ctk.CTkComboBox(
            card_docente,
            values=[
                "DOCENTE_PLANTA (Dec. 1279)",
                "DOCENTE_OCASIONAL (Ac. 027/2024)",
                "DOCENTE_CATEDRATICO (Ac. 027/2024)",
                "DOCENTE_AD_HONOREM",
            ],
            width=420,
        )
        self.combo_tipo.pack(fill="x", padx=14, pady=(0, 8))

        row_ded = ctk.CTkFrame(card_docente, fg_color="transparent")
        row_ded.pack(fill="x", padx=14, pady=4)
        row_ded.columnconfigure((0, 1), weight=1)

        f_ded = ctk.CTkFrame(row_ded, fg_color="transparent")
        f_ded.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkLabel(f_ded, text="Dedicación:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w")
        self.combo_ded = ctk.CTkComboBox(f_ded, values=["TIEMPO_COMPLETO", "MEDIO_TIEMPO", "HORA_CATEDRA"])
        self.combo_ded.pack(fill="x", pady=2)

        f_hrs = ctk.CTkFrame(row_ded, fg_color="transparent")
        f_hrs.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        ctk.CTkLabel(f_hrs, text="Horas Semanales (máx 18h cátedra):", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w")
        self.entry_horas = ctk.CTkEntry(f_hrs, placeholder_text="40")
        self.entry_horas.insert(0, "40")
        self.entry_horas.pack(fill="x", pady=2)

        row_arl = ctk.CTkFrame(card_docente, fg_color="transparent")
        row_arl.pack(fill="x", padx=14, pady=(4, 12))
        row_arl.columnconfigure((0, 1), weight=1)

        f_arl = ctk.CTkFrame(row_arl, fg_color="transparent")
        f_arl.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkLabel(f_arl, text="Clase de Riesgo ARL:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w")
        self.combo_arl = ctk.CTkComboBox(f_arl, values=["CLASE I (0.522%)", "CLASE II (1.044%)", "CLASE III (2.436%)"])
        self.combo_arl.pack(fill="x", pady=2)

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

        ctk.CTkLabel(card_eco, text="Resolución Rectoral de Vinculación:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w", padx=14, pady=(6, 1))
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

        btn_calc = ctk.CTkButton(
            f_calc,
            text="⚡ Calcular Según Régimen",
            fg_color="#475569",
            hover_color="#334155",
            command=self._calcular_sugerido,
        )
        btn_calc.pack(fill="x", pady=2)

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

    def _calcular_sugerido(self) -> None:
        sel_p = self.combo_prof.get()
        t_sel = self.combo_tipo.get()
        if not sel_p or sel_p == "Sin docentes registrados":
            return
        cod = sel_p.split(" - ")[0].strip()
        prof = self.controller.gestor_personas.buscar_profesor_por_codigo(cod)
        if not prof:
            return

        try:
            hrs = Decimal(self.entry_horas.get().strip() or "40")
        except Exception:
            hrs = Decimal("40")

        sug = self.service.calcular_asignacion_sugerida(t_sel, prof, self.combo_ded.get(), hrs)
        self.entry_monto.delete(0, "end")
        self.entry_monto.insert(0, str(int(sug)))

    def _guardar(self) -> None:
        sel_p = self.combo_prof.get()
        if not sel_p or sel_p == "Sin docentes registrados":
            self.lbl_error.configure(text="⚠️ Debe seleccionar un docente válido.")
            return

        cod = sel_p.split(" - ")[0].strip()
        prof = self.controller.gestor_personas.buscar_profesor_por_codigo(cod)
        if not prof:
            self.lbl_error.configure(text="⚠️ Docente no encontrado en la base de datos.")
            return

        num = self.entry_num.get().strip()
        t_sel = self.combo_tipo.get()

        try:
            hrs = Decimal(self.entry_horas.get().strip() or "40")
        except Exception:
            self.lbl_error.configure(text="⚠️ Ingrese un número de horas válido.")
            return

        es_jub = self.switch_jubilado.get()

        ok, msg = self.service.validar_contrato(num, prof.idPersona, t_sel, hrs, es_jub)
        if not ok:
            self.lbl_error.configure(text=f"⚠️ {msg}")
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

        tipo_clean = t_sel.split(" ")[0]
        modalidad = "PLANTA" if "PLANTA" in t_sel else ("OCASIONAL" if "OCASIONAL" in t_sel else ("CATEDRATICO" if "CATEDRATICO" in t_sel else "AD_HONOREM"))
        es_adh = "AD_HONOREM" in t_sel

        datos = {
            "numeroContrato": num,
            "idPersona": prof.idPersona,
            "tipoContrato": tipo_clean,
            "modalidadProfesor": modalidad,
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
