"""Modales de acciones sobre contratos: Ver Ficha Técnica, Editar y Terminar."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, Callable
import customtkinter as ctk

from ui_gui.theme import Colors

if TYPE_CHECKING:
    from ui_gui.gui_controller import PITAController
    from ui_gui.contratos.contratos_service import ContratosService
    from modelo_datos import Contrato


class DialogDetalleContrato(ctk.CTkToplevel):
    """Ficha Técnica consolidada de una vinculación contractual."""

    def __init__(
        self,
        parent: ctk.CTkBaseClass,
        contrato: Contrato,
        controller: PITAController,
        service: ContratosService,
    ) -> None:
        super().__init__(parent)
        self.contrato = contrato
        self.controller = controller
        self.service = service

        self.title(f"👁️ Ficha Contractual — {contrato.numeroContrato}")
        self.geometry("540x620")
        self.transient(parent.winfo_toplevel())
        self.grab_set()

        self._construir_ui()

    def _construir_ui(self) -> None:
        c = self.contrato
        pers = self.service.buscar_persona_por_id(c.idPersona)
        prof = self.service.buscar_profesor_por_id_persona(c.idPersona)
        nom_prof = f"{getattr(pers, 'primerNombre', '')} {getattr(pers, 'primerApellido', '')}" if pers else f"Persona #{c.idPersona}"

        ctk.CTkLabel(self, text=f"📜 Contrato: {c.numeroContrato}", font=ctk.CTkFont(family="Segoe UI", size=17, weight="bold"), text_color=Colors.TEXT_MAIN).pack(pady=(15, 2))
        ctk.CTkLabel(self, text=f"Docente: {nom_prof}", font=ctk.CTkFont(family="Segoe UI", size=13), text_color=Colors.WIN_BLUE).pack(pady=(0, 10))

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=16, pady=4)

        card = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
        card.pack(fill="x", pady=6)

        asig = str(getattr(c, "salarioBase", "0") or getattr(c, "salarioMensualPactado", "0") or "0")
        try:
            asig_fmt = f"$ {int(float(asig)):,} COP"
        except Exception:
            asig_fmt = f"$ {asig}"

        mod = str(getattr(c, "modalidadProfesor", "") or getattr(c, "tipoContrato", "DOCENTE")).upper()
        regimen = "Carrera Docente (Decreto 1279/2002)" if "PLANTA" in mod else "Docente Transitorio (Acuerdo 027/2024)"

        pts_sal = getattr(prof, "puntosSalariales", 0) or 0
        cat_doc = getattr(prof, "categoriaDocente", "N/A") or "N/A"

        items = [
            ("Docente Vinculado:", nom_prof),
            ("Documento de Identidad:", str(getattr(pers, "numeroDocumento", "N/D"))),
            ("Modalidad Contractual:", mod),
            ("Régimen Jurídico:", regimen),
            ("Categoría Docente:", str(cat_doc)),
            ("Puntos Salariales (Dec. 1279):", f"{pts_sal} puntos"),
            ("Dedicación:", str(getattr(c, "dedicacion", "TIEMPO_COMPLETO"))),
            ("Horas Semanales:", f"{getattr(c, 'horasSemanales', 40)} horas/semana"),
            ("Asignación Básica Mensual:", asig_fmt),
            ("Fecha de Inicio:", str(getattr(c, "fechaInicio", "N/D"))),
            ("Fecha de Terminación:", str(getattr(c, "fechaFin", "Indefinido"))),
            ("Estado:", str(getattr(c, "estado", "ACTIVO"))),
            ("Disponibilidad Presupuestal (CDP):", str(getattr(c, "numeroCDP", "N/A"))),
            ("Resolución de Nombramiento:", str(getattr(c, "resolucionNombramiento", "N/A"))),
            ("Clase de Riesgo ARL:", str(getattr(c, "claseRiesgoARL", "CLASE I"))),
            ("Supervisión / Decanatura:", "Decano de Facultad / Vicerrectoría"),
        ]

        for lbl, val in items:
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=14, pady=3)
            ctk.CTkLabel(row, text=lbl, font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=Colors.TEXT_MUTED).pack(side="left")
            ctk.CTkLabel(row, text=val, font=ctk.CTkFont(family="Segoe UI", size=11), text_color=Colors.TEXT_MAIN).pack(side="right")


class DialogEditarContrato(ctk.CTkToplevel):
    """Diálogo modal para editar parámetros de un contrato."""

    def __init__(
        self,
        parent: ctk.CTkBaseClass,
        contrato: Contrato,
        controller: PITAController,
        service: ContratosService,
        on_success: Callable[[], None],
    ) -> None:
        super().__init__(parent)
        self.contrato = contrato
        self.controller = controller
        self.service = service
        self.on_success = on_success

        self.title(f"✏️ Modificar Contrato {contrato.numeroContrato}")
        self.geometry("560x620")
        self.transient(parent.winfo_toplevel())
        self.grab_set()

        self._construir_ui()

    def _construir_ui(self) -> None:
        c = self.contrato
        ctk.CTkLabel(self, text=f"✏️ Editar Parámetros del Contrato {c.numeroContrato}", font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"), text_color=Colors.TEXT_MAIN).pack(pady=(14, 2))
        ctk.CTkLabel(self, text="Actualice vigencia, dedicación, asignación o estado presupuestal", font=ctk.CTkFont(family="Segoe UI", size=11), text_color=Colors.TEXT_MUTED).pack(pady=(0, 10))

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=16, pady=4)

        card = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
        card.pack(fill="x", pady=6)

        ctk.CTkLabel(card, text="Dedicación:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w", padx=14, pady=(10, 2))
        combo_ded = ctk.CTkComboBox(card, values=["TIEMPO_COMPLETO", "MEDIO_TIEMPO", "HORA_CATEDRA"])
        combo_ded.set(str(getattr(c, "dedicacion", "TIEMPO_COMPLETO")))
        combo_ded.pack(fill="x", padx=14, pady=(0, 6))

        ctk.CTkLabel(card, text="Horas Semanales:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w", padx=14, pady=(4, 2))
        entry_hrs = ctk.CTkEntry(card)
        entry_hrs.insert(0, str(getattr(c, "horasSemanales", 40)))
        entry_hrs.pack(fill="x", padx=14, pady=(0, 6))

        ctk.CTkLabel(card, text="Asignación Básica Mensual ($ COP):", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w", padx=14, pady=(4, 2))
        entry_sal = ctk.CTkEntry(card)
        entry_sal.insert(0, str(getattr(c, "salarioBase", "0") or "0"))
        entry_sal.pack(fill="x", padx=14, pady=(0, 6))

        ctk.CTkLabel(card, text="Fecha de Terminación (YYYY-MM-DD):", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w", padx=14, pady=(4, 2))
        entry_fin = ctk.CTkEntry(card)
        entry_fin.insert(0, str(getattr(c, "fechaFin", "") or ""))
        entry_fin.pack(fill="x", padx=14, pady=(0, 6))

        ctk.CTkLabel(card, text="Número CDP:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w", padx=14, pady=(4, 2))
        entry_cdp = ctk.CTkEntry(card)
        entry_cdp.insert(0, str(getattr(c, "numeroCDP", "") or ""))
        entry_cdp.pack(fill="x", padx=14, pady=(0, 6))

        ctk.CTkLabel(card, text="Resolución Rectoral:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w", padx=14, pady=(4, 2))
        entry_res = ctk.CTkEntry(card)
        entry_res.insert(0, str(getattr(c, "resolucionNombramiento", "") or ""))
        entry_res.pack(fill="x", padx=14, pady=(0, 6))

        ctk.CTkLabel(card, text="Clase de Riesgo ARL:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w", padx=14, pady=(4, 2))
        combo_arl = ctk.CTkComboBox(card, values=["CLASE I (0.522%)", "CLASE II (1.044%)", "CLASE III (2.436%)"])
        combo_arl.set(str(getattr(c, "claseRiesgoARL", "CLASE I (0.522%)")))
        combo_arl.pack(fill="x", padx=14, pady=(0, 6))

        ctk.CTkLabel(card, text="Estado del Contrato:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w", padx=14, pady=(4, 2))
        combo_est = ctk.CTkComboBox(card, values=["ACTIVO", "TERMINADO", "SUSPENDIDO"])
        combo_est.set(str(getattr(c, "estado", "ACTIVO")))
        combo_est.pack(fill="x", padx=14, pady=(0, 10))

        lbl_err = ctk.CTkLabel(scroll, text="", text_color="#EF4444", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"))
        lbl_err.pack(pady=4)

        def _guardar():
            try:
                h = int(entry_hrs.get().strip())
                sal = Decimal(entry_sal.get().strip())
            except Exception:
                lbl_err.configure(text="⚠️ Ingrese horas y salario válidos.")
                return

            f_fin_str = entry_fin.get().strip()
            f_fin = None
            if f_fin_str:
                try:
                    f_fin = date.fromisoformat(f_fin_str)
                except ValueError:
                    lbl_err.configure(text="⚠️ Formato de fecha de fin inválido.")
                    return

            datos = {
                "dedicacion": combo_ded.get(),
                "horasSemanales": h,
                "salarioBase": sal,
                "salarioMensualPactado": sal,
                "fechaFin": f_fin,
                "numeroCDP": entry_cdp.get().strip() or None,
                "resolucionNombramiento": entry_res.get().strip() or None,
                "claseRiesgoARL": combo_arl.get(),
                "estado": combo_est.get(),
            }

            self.service.actualizar_contrato(self.contrato, datos)
            self.destroy()
            self.on_success()

        ctk.CTkButton(
            scroll,
            text="💾 Guardar Modificaciones al Contrato",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=Colors.WIN_BLUE,
            hover_color=Colors.WIN_BLUE_HOVER,
            height=38,
            command=_guardar,
        ).pack(fill="x", padx=14, pady=(8, 16))


class DialogTerminarContrato(ctk.CTkToplevel):
    """Diálogo modal para terminar y liquidar una vinculación contractual."""

    def __init__(
        self,
        parent: ctk.CTkBaseClass,
        contrato: Contrato,
        controller: PITAController,
        service: ContratosService,
        on_success: Callable[[], None],
    ) -> None:
        super().__init__(parent)
        self.contrato = contrato
        self.controller = controller
        self.service = service
        self.on_success = on_success

        self.title(f"🚫 Terminar Contrato {contrato.numeroContrato}")
        self.geometry("480x420")
        self.transient(parent.winfo_toplevel())
        self.grab_set()

        self._construir_ui()

    def _construir_ui(self) -> None:
        c = self.contrato
        ctk.CTkLabel(self, text=f"🚫 Terminación de Contrato {c.numeroContrato}", font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"), text_color="#EF4444").pack(pady=(16, 2))
        ctk.CTkLabel(self, text="Esta acción finalizará la vinculación y habilitará la liquidación definitiva", font=ctk.CTkFont(family="Segoe UI", size=11), text_color=Colors.TEXT_MUTED).pack(pady=(0, 12))

        card = ctk.CTkFrame(self, fg_color=Colors.BG_CARD, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
        card.pack(fill="x", padx=20, pady=6)

        ctk.CTkLabel(card, text="Causal de Terminación:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w", padx=14, pady=(10, 2))
        combo_motivo = ctk.CTkComboBox(
            card,
            values=[
                "Cumplimiento del Plazo Pactado",
                "Renuncia Aceptada",
                "Mutuo Acuerdo de las Partes",
                "Despido Justificado / Incumplimiento",
                "Inhabilidad Sobreveniente",
            ],
            width=380,
        )
        combo_motivo.pack(fill="x", padx=14, pady=(0, 8))

        ctk.CTkLabel(card, text="Fecha Efectiva de Terminación (YYYY-MM-DD):", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w", padx=14, pady=(4, 2))
        entry_f_term = ctk.CTkEntry(card)
        entry_f_term.insert(0, date.today().isoformat())
        entry_f_term.pack(fill="x", padx=14, pady=(0, 8))

        chk_liq = ctk.CTkCheckBox(card, text="Confirmar Liquidación de Prestaciones Sociales y Cesantías")
        chk_liq.select()
        chk_liq.pack(anchor="w", padx=14, pady=(4, 12))

        lbl_err = ctk.CTkLabel(self, text="", text_color="#EF4444", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"))
        lbl_err.pack(pady=2)

        def _terminar():
            try:
                f_term = date.fromisoformat(entry_f_term.get().strip())
            except ValueError:
                lbl_err.configure(text="⚠️ Fecha de terminación inválida.")
                return

            motivo = combo_motivo.get()
            self.service.terminar_contrato(self.contrato, motivo, f_term)
            self.destroy()
            self.on_success()

        ctk.CTkButton(
            self,
            text="🚫 Confirmar y Terminar Vinculación",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#EF4444",
            hover_color="#DC2626",
            height=38,
            command=_terminar,
        ).pack(fill="x", padx=20, pady=(10, 16))
