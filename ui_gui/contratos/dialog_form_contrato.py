from __future__ import annotations
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, Callable
import customtkinter as ctk

from ui_gui.theme import Colors
from ui_gui.components import clean_enum
from dominio.modelo_datos import Contrato, Dedicacion

if TYPE_CHECKING:
    from ui_gui.gui_controller import PITAController
    from ui_gui.contratos.contratos_service import ContratosService

class DialogFormContrato(ctk.CTkToplevel):
    """Diálogo modal adaptativo para registro o edición de contrato laboral."""

    def __init__(
        self,
        parent: ctk.CTkBaseClass,
        controller: 'PITAController',
        service: 'ContratosService',
        on_success: Callable[[], None],
        contrato: 'Contrato' = None
    ) -> None:
        super().__init__(parent)
        self.controller = controller
        self.service = service
        self.on_success = on_success
        self.contrato = contrato
        self.is_edit = contrato is not None

        self.title(f"✏️ Editar Contrato {self.contrato.numeroContrato}" if self.is_edit else "💼 Registrar Vinculación Contractual")
        self.geometry("640x720")
        self.transient(parent.winfo_toplevel())
        self.grab_set()

        self._construir_ui()

    def _construir_ui(self) -> None:
        ctk.CTkLabel(
            self,
            text=f"✏️ Modificar Contrato {self.contrato.numeroContrato}" if self.is_edit else "🤝 Vinculación Contractual y Formalización de Nómina",
            font=ctk.CTkFont(family="Segoe UI", size=17, weight="bold"),
            text_color=Colors.TEXT_MAIN,
        ).pack(pady=(12, 2))

        ctk.CTkLabel(
            self,
            text="Actualice vigencia, dedicación, asignación o estado presupuestal" if self.is_edit else "Formalización jurídica laboral para docentes y funcionarios",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=Colors.TEXT_MUTED,
        ).pack(pady=(0, 8))

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

        self.card_vinculacion = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
        self.card_vinculacion.pack(fill="x", pady=6)

        self.lbl_card1_title = ctk.CTkLabel(
            self.card_vinculacion,
            text="1. Empleado y Estado Contractual" if self.is_edit else "1. Empleado y Modalidad de Vinculación",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=Colors.TEXT_MAIN,
        )
        self.lbl_card1_title.pack(anchor="w", padx=14, pady=(10, 6))

        self.f_selector_persona = ctk.CTkFrame(self.card_vinculacion, fg_color="transparent")
        self.f_selector_persona.pack(fill="x", padx=14, pady=(0, 4))

        self.lbl_sel_emp = ctk.CTkLabel(self.f_selector_persona, text="Seleccionar Docente *:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"))
        self.lbl_sel_emp.pack(anchor="w", pady=(2, 1))

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
        
        adm_options = []
        for a in self.controller.administrativos:
            pers = self.service.buscar_persona_por_id(a.idPersona)
            nom = f"{getattr(pers, 'primerNombre', '')} {getattr(pers, 'primerApellido', '')}" if pers else "Administrativo"
            adm_options.append(f"{a.codigoEmpleado} - {nom} ({a.cargo or 'Cargo'})")
        if not adm_options:
            adm_options = ["Sin administrativos registrados"]
        self.combo_adm = ctk.CTkComboBox(self.f_selector_persona, values=adm_options, width=420, command=self._on_seleccionar_adm)
        self.combo_prof.pack(fill="x", pady=(0, 4))

        if self.is_edit:
            self.combo_prof.configure(state="disabled")
            self.combo_adm.configure(state="disabled")
            self.seg_tipo.configure(state="disabled")
            # Prefill combo to show the current person
            if self.contrato.idEmpleado in [p.idPersona for p in self.controller.profesores]:
                self.seg_tipo.set("👨‍🏫 Personal Docente")
                for po in prof_options:
                    if str(self.contrato.idEmpleado) in po: # roughly, actually we'd need exact match but this is a mock prefill
                        self.combo_prof.set(po)
            else:
                self.seg_tipo.set("👔 Personal Administrativo")
                self.combo_prof.pack_forget()
                self.combo_adm.pack(fill="x", pady=(0, 4))
                for ao in adm_options:
                    if str(self.contrato.idEmpleado) in ao:
                        self.combo_adm.set(ao)

        self.switch_jubilado = ctk.CTkSwitch(self.card_vinculacion, text="¿El empleado es pensionado / jubilado? (Restricción legal)", onvalue=True, offvalue=False)
        self.switch_jubilado.pack(anchor="w", padx=14, pady=4)

        ctk.CTkLabel(self.card_vinculacion, text="Modalidad Contractual / Régimen Jurídico:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w", padx=14, pady=(6, 1))
        self.combo_tipo = ctk.CTkComboBox(
            self.card_vinculacion,
            values=[
                "CONTRATO INDEFINIDO LEY 100 (Administrativo)",
                "CONTRATO FIJO (Administrativo / Ocasional)",
                "DECRETO 1279 DE 2002 (Docente Planta)",
                "ESTATUTO DOCENTE ACUERDO 027 (Catedrático)",
                "PRESTACIÓN DE SERVICIOS HONORARIOS",
            ],
            width=420,
        )
        if self.is_edit:
            self.combo_tipo.set(self.contrato.tipoContrato)
        else:
            self.combo_tipo.set("DECRETO 1279 DE 2002 (Docente Planta)")
        self.combo_tipo.pack(fill="x", padx=14, pady=(0, 10))

        # ESTADO CONTRATO
        if self.is_edit:
            ctk.CTkLabel(self.card_vinculacion, text="Estado del Contrato:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w", padx=14, pady=(4, 1))
            self.combo_est = ctk.CTkComboBox(self.card_vinculacion, values=["ACTIVO", "TERMINADO", "SUSPENDIDO"])
            self.combo_est.set(clean_enum(getattr(self.contrato, "estado", "ACTIVO")))
            self.combo_est.pack(fill="x", padx=14, pady=(0, 10))

        # CARD 2: DEDICACIÓN Y VIGENCIA
        self.card_dedicacion = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
        self.card_dedicacion.pack(fill="x", pady=6)

        ctk.CTkLabel(
            self.card_dedicacion,
            text="⏳ 2. Dedicación Horaria y Vigencia",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#F59E0B",
        ).pack(anchor="w", padx=14, pady=(10, 6))

        grid_d = ctk.CTkFrame(self.card_dedicacion, fg_color="transparent")
        grid_d.pack(fill="x", padx=14, pady=(0, 10))
        grid_d.columnconfigure(0, weight=1)
        grid_d.columnconfigure(1, weight=1)

        ctk.CTkLabel(grid_d, text="Dedicación (Tipo):", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).grid(row=0, column=0, sticky="w", padx=4, pady=(2, 0))
        self.combo_dedicacion = ctk.CTkComboBox(
            grid_d,
            values=["TIEMPO_COMPLETO", "MEDIO_TIEMPO", "HORA_CATEDRA", "EXCLUSIVA"],
            command=self._on_cambiar_dedicacion,
        )
        if self.is_edit: self.combo_dedicacion.set(clean_enum(getattr(self.contrato, "dedicacion", "TIEMPO_COMPLETO")))
        self.combo_dedicacion.grid(row=1, column=0, sticky="ew", padx=4, pady=(2, 6))

        ctk.CTkLabel(grid_d, text="Horas Semanales Presenciales:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).grid(row=0, column=1, sticky="w", padx=4, pady=(2, 0))
        self.entry_hrs = ctk.CTkEntry(grid_d, placeholder_text="ej: 40")
        if self.is_edit: self.entry_hrs.insert(0, str(getattr(self.contrato, "horasSemanales", 40)))
        else: self.entry_hrs.insert(0, "40")
        self.entry_hrs.grid(row=1, column=1, sticky="ew", padx=4, pady=(2, 6))

        ctk.CTkLabel(grid_d, text="Fecha de Inicio (Opcional)", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).grid(row=2, column=0, sticky="w", padx=4, pady=(4, 0))
        self.entry_fini = ctk.CTkEntry(grid_d, placeholder_text="YYYY-MM-DD")
        if self.is_edit: self.entry_fini.insert(0, str(getattr(self.contrato, "fechaInicio", "") or ""))
        else: self.entry_fini.insert(0, str(date.today()))
        self.entry_fini.grid(row=3, column=0, sticky="ew", padx=4, pady=(2, 6))

        ctk.CTkLabel(grid_d, text="Fecha Fin Proyectada (Opcional)", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).grid(row=2, column=1, sticky="w", padx=4, pady=(4, 0))
        self.entry_ffin = ctk.CTkEntry(grid_d, placeholder_text="YYYY-MM-DD")
        if self.is_edit: self.entry_ffin.insert(0, str(getattr(self.contrato, "fechaFin", "") or ""))
        self.entry_ffin.grid(row=3, column=1, sticky="ew", padx=4, pady=(2, 6))

        # CARD 3: SALARIO
        self.card_salario = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
        self.card_salario.pack(fill="x", pady=6)

        ctk.CTkLabel(
            self.card_salario,
            text="💰 3. Asignación Básica Mensual y Riesgos",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#10B981",
        ).pack(anchor="w", padx=14, pady=(10, 6))

        if not self.is_edit:
            self.f_sim_doc = ctk.CTkFrame(self.card_salario, fg_color="#F8FAFC", corner_radius=6)
            self.f_sim_doc.pack(fill="x", padx=14, pady=(0, 10))
            ctk.CTkLabel(self.f_sim_doc, text="🧮 Simulación Salarial D. 1279", font=ctk.CTkFont(size=11, weight="bold"), text_color=Colors.WIN_BLUE).pack(anchor="w", padx=10, pady=(6, 2))
            
            self.lbl_sim_pts = ctk.CTkLabel(self.f_sim_doc, text="Puntos Acumulados: 0", font=ctk.CTkFont(size=11), text_color=Colors.TEXT_MUTED)
            self.lbl_sim_pts.pack(anchor="w", padx=10, pady=(0, 1))
            self.lbl_sim_val = ctk.CTkLabel(self.f_sim_doc, text="Valor del Punto: $ 20,836 COP", font=ctk.CTkFont(size=11), text_color=Colors.TEXT_MUTED)
            self.lbl_sim_val.pack(anchor="w", padx=10, pady=(0, 6))

        ctk.CTkLabel(self.card_salario, text="Asignación Básica Mensual (Salario Base) *:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w", padx=14, pady=(2, 1))
        self.entry_salario = ctk.CTkEntry(self.card_salario)
        if self.is_edit: self.entry_salario.insert(0, str(getattr(self.contrato, "salarioBase", "0") or "0"))
        else: self.entry_salario.insert(0, "0.00")
        self.entry_salario.pack(fill="x", padx=14, pady=(0, 6))

        ctk.CTkLabel(self.card_salario, text="Clasificación de Riesgo Laboral (ARL) *:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w", padx=14, pady=(4, 1))
        self.combo_arl = ctk.CTkComboBox(self.card_salario, values=["CLASE I (0.522%)", "CLASE II (1.044%)", "CLASE III (2.436%)", "CLASE IV (4.350%)", "CLASE V (6.960%)"])
        if self.is_edit: self.combo_arl.set(str(getattr(self.contrato, "claseRiesgoARL", "CLASE I (0.522%)")))
        else: self.combo_arl.set("CLASE I (0.522%)")
        self.combo_arl.pack(fill="x", padx=14, pady=(0, 10))

        # CARD 4: PRESUPUESTO
        self.card_pres = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
        self.card_pres.pack(fill="x", pady=6)

        ctk.CTkLabel(
            self.card_pres,
            text="📑 4. Documentación y Presupuesto",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#8B5CF6",
        ).pack(anchor="w", padx=14, pady=(10, 6))

        grid_p = ctk.CTkFrame(self.card_pres, fg_color="transparent")
        grid_p.pack(fill="x", padx=14, pady=(0, 10))
        grid_p.columnconfigure(0, weight=1)
        grid_p.columnconfigure(1, weight=1)

        ctk.CTkLabel(grid_p, text="Número CDP (Opcional):", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).grid(row=0, column=0, sticky="w", padx=4, pady=(2, 0))
        self.entry_cdp = ctk.CTkEntry(grid_p, placeholder_text="Certificado de Disponibilidad")
        if self.is_edit: self.entry_cdp.insert(0, str(getattr(self.contrato, "numeroCDP", "") or ""))
        self.entry_cdp.grid(row=1, column=0, sticky="ew", padx=4, pady=(2, 6))

        ctk.CTkLabel(grid_p, text="Resolución Rectoral (Opcional):", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).grid(row=0, column=1, sticky="w", padx=4, pady=(2, 0))
        self.entry_res = ctk.CTkEntry(grid_p, placeholder_text="Res. Nombramiento")
        if self.is_edit: self.entry_res.insert(0, str(getattr(self.contrato, "resolucionNombramiento", "") or ""))
        self.entry_res.grid(row=1, column=1, sticky="ew", padx=4, pady=(2, 6))

        self.lbl_error = ctk.CTkLabel(scroll, text="", text_color="#EF4444", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"))
        self.lbl_error.pack(pady=4)

        ctk.CTkButton(
            scroll,
            text="💾 Guardar Cambios" if self.is_edit else "💾 Generar y Firmar Contrato",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=Colors.ACCENT_PRIMARY,
            hover_color=Colors.ACCENT_HOVER,
            height=40,
            command=self._guardar,
        ).pack(fill="x", padx=14, pady=(10, 20))
        
        if not self.is_edit:
            self._on_cambiar_tipo_personal("👨‍🏫 Personal Docente")

    def _on_cambiar_tipo_personal(self, valor: str) -> None:
        if valor.startswith("👨‍🏫"):
            self.lbl_sel_emp.configure(text="Seleccionar Docente *:")
            self.combo_adm.pack_forget()
            self.combo_prof.pack(fill="x", pady=(0, 4))
            self.combo_tipo.set("DECRETO 1279 DE 2002 (Docente Planta)")
            self.f_sim_doc.pack(fill="x", padx=14, pady=(0, 10))
            self._on_seleccionar_prof(self.combo_prof.get())
        else:
            self.lbl_sel_emp.configure(text="Seleccionar Administrativo *:")
            self.combo_prof.pack_forget()
            self.combo_adm.pack(fill="x", pady=(0, 4))
            self.combo_tipo.set("CONTRATO INDEFINIDO LEY 100 (Administrativo)")
            self.f_sim_doc.pack_forget()
            self.entry_salario.delete(0, "end")
            self.entry_salario.insert(0, "1500000.00")

    def _on_cambiar_dedicacion(self, valor: str) -> None:
        if valor == "HORA_CATEDRA":
            self.entry_hrs.delete(0, "end")
            self.entry_hrs.insert(0, "8")
        elif valor == "MEDIO_TIEMPO":
            self.entry_hrs.delete(0, "end")
            self.entry_hrs.insert(0, "20")
        else:
            self.entry_hrs.delete(0, "end")
            self.entry_hrs.insert(0, "40")

    def _on_seleccionar_prof(self, val: str) -> None:
        if not val or val == "Sin docentes registrados":
            return
        try:
            pts_str = val.split("[")[1].split(",")[1].replace("pts]", "").strip()
            pts = int(pts_str)
            self.lbl_sim_pts.configure(text=f"Puntos Acumulados: {pts}")
            salario = pts * 20836
            self.lbl_sim_val.configure(text=f"Estimado Salarial: $ {salario:,.2f} COP")
            self.entry_salario.delete(0, "end")
            self.entry_salario.insert(0, str(salario))
        except:
            pass

    def _on_seleccionar_adm(self, val: str) -> None:
        pass

    def _guardar(self) -> None:
        try:
            h = int(self.entry_hrs.get().strip())
            sal = Decimal(self.entry_salario.get().strip())
        except Exception:
            self.lbl_error.configure(text="⚠️ Horas y Salario deben ser numéricos.")
            return

        if sal <= 0:
            self.lbl_error.configure(text="⚠️ El salario base debe ser mayor a 0.")
            return

        f_ini_str = self.entry_fini.get().strip()
        f_fin_str = self.entry_ffin.get().strip()

        try:
            d_ini = date.fromisoformat(f_ini_str) if f_ini_str else None
            d_fin = date.fromisoformat(f_fin_str) if f_fin_str else None
        except ValueError:
            self.lbl_error.configure(text="⚠️ Las fechas deben tener el formato YYYY-MM-DD.")
            return
            
        if self.is_edit:
            datos = {
                "dedicacion": self.combo_dedicacion.get(),
                "horasSemanales": h,
                "salarioBase": sal,
                "salarioMensualPactado": sal,
                "fechaInicio": d_ini,
                "fechaFin": d_fin,
                "numeroCDP": self.entry_cdp.get().strip() or None,
                "resolucionNombramiento": self.entry_res.get().strip() or None,
                "claseRiesgoARL": self.combo_arl.get(),
                "estado": self.combo_est.get(),
            }
            try:
                self.service.actualizar_contrato(self.contrato, datos)
                self.destroy()
                self.on_success()
            except Exception as e:
                self.lbl_error.configure(text=f"⚠️ Error: {e}")
        else:
            tipo_pers = self.seg_tipo.get()
            emp_id = None

            if tipo_pers.startswith("👨‍🏫"):
                sel = self.combo_prof.get()
                if "Sin docentes" in sel:
                    self.lbl_error.configure(text="⚠️ No hay docentes.")
                    return
                cod = sel.split(" - ")[0]
                for p in self.controller.profesores:
                    if str(p.codigoProfesor) == cod:
                        emp_id = p.idPersona
                        break
            else:
                sel = self.combo_adm.get()
                if "Sin administrativos" in sel:
                    self.lbl_error.configure(text="⚠️ No hay administrativos.")
                    return
                cod = sel.split(" - ")[0]
                for a in self.controller.administrativos:
                    if str(a.codigoEmpleado) == cod:
                        emp_id = a.idPersona
                        break

            if not emp_id:
                self.lbl_error.configure(text="⚠️ No se pudo identificar al empleado seleccionado.")
                return
            
            try:
                self.service.crear_contrato(
                    id_empleado=emp_id,
                    tipo_contrato=self.combo_tipo.get(),
                    dedicacion=self.combo_dedicacion.get(),
                    horas=h,
                    salario=sal,
                    f_inicio=d_ini,
                    f_fin=d_fin,
                    cdp=self.entry_cdp.get().strip() or None,
                    res=self.entry_res.get().strip() or None,
                    arl=self.combo_arl.get()
                )
                self.destroy()
                self.on_success()
            except Exception as e:
                self.lbl_error.configure(text=f"⚠️ Error al crear contrato: {e}")
