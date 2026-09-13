from __future__ import annotations
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Callable
import customtkinter as ctk

from ui_gui.theme import Colors
from ui_gui.components import clean_enum
from ui_gui.personas.persona_form_card import PersonaFormCard
from dominio.modelo_datos import (
    Dedicacion,
    EstadoAcademico,
    TipoProfesor,
)

if TYPE_CHECKING:
    from ui_gui.gui_controller import PITAController
    from ui_gui.personas.personas_service import PersonasService
    from dominio.modelo_datos import Persona, Estudiante, Profesor, Administrativo

class DialogFormPersona(ctk.CTkToplevel):
    """Modal unificado para registrar o editar una Persona y su Rol institucional."""

    def __init__(
        self,
        parent: ctk.CTkBaseClass,
        controller: 'PITAController',
        service: 'PersonasService',
        on_success: Callable[[], None],
        persona: 'Persona' = None,
        rol_obj: Any = None,
        tipo_rol: str = "ESTUDIANTE"
    ) -> None:
        super().__init__(parent)
        self.controller = controller
        self.service = service
        self.on_success = on_success
        self.persona = persona
        self.rol_obj = rol_obj
        self.is_edit = persona is not None
        self.tipo_rol = tipo_rol if self.is_edit else "ESTUDIANTE"

        titulo = f"✏️ Editar {self.tipo_rol.capitalize()}: {getattr(self.rol_obj, 'codigo'+self.tipo_rol.capitalize(), getattr(self.rol_obj, 'codigoEmpleado', ''))}" if self.is_edit else "➕ Registrar Persona y Asignar Rol en PITA"
        self.title(titulo)
        self.geometry("640x760")
        self.minsize(580, 620)
        self.grab_set()

        self.widgets_rol: dict[str, ctk.CTkBaseClass] = {}
        self._construir_ui()

    def _construir_ui(self) -> None:
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(15, 10))

        ctk.CTkLabel(
            header_frame,
            text=f"✏️ Modificar {self.tipo_rol.capitalize()}" if self.is_edit else "➕ Registrar Nueva Persona y Asignar Rol",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#F8FAFC",
        ).pack(anchor="w")
        ctk.CTkLabel(
            header_frame,
            text="Actualice la información personal, de contacto y los datos del rol." if self.is_edit else "Complete los datos de identificación, contacto y la información del rol académico o laboral.",
            font=ctk.CTkFont(size=11),
            text_color="#94A3B8",
        ).pack(anchor="w", pady=(2, 0))

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        self.card_personal = PersonaFormCard(scroll, incluir_documento=not self.is_edit)
        if self.is_edit and self.persona:
            self.card_personal.poblar_desde_persona(self.persona)

        card_r = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
        card_r.pack(fill="x", pady=6)

        ctk.CTkLabel(
            card_r,
            text="🎓 2. Rol y Vinculación en PITA" if not self.is_edit else "🎓 2. Información Académica/Laboral",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#A78BFA",
        ).pack(anchor="w", padx=15, pady=(12, 6))

        row_rol = ctk.CTkFrame(card_r, fg_color="transparent")
        row_rol.pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkLabel(row_rol, text="Rol Institucional:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(side="left", padx=(0, 10))
        self.combo_rol = ctk.CTkComboBox(row_rol, values=["ESTUDIANTE", "PROFESOR", "ADMINISTRATIVO"], width=200)
        self.combo_rol.set(self.tipo_rol)
        self.combo_rol.pack(side="left")

        if self.is_edit:
            self.combo_rol.configure(state="disabled")

        self.sub_rol = ctk.CTkFrame(card_r, fg_color="transparent")
        self.sub_rol.pack(fill="x", padx=15, pady=(0, 15))
        self.sub_rol.columnconfigure(0, weight=1)
        self.sub_rol.columnconfigure(1, weight=1)

        self.combo_rol.configure(command=self._cambiar_rol)
        self._cambiar_rol(self.tipo_rol)

        self.lbl_error = ctk.CTkLabel(scroll, text="", text_color="#EF4444", font=ctk.CTkFont(size=12, weight="bold"))
        self.lbl_error.pack(pady=(5, 2))

        btn_box = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_box.pack(fill="x", pady=(5, 10))

        ctk.CTkButton(
            btn_box,
            text="💾 Guardar Cambios" if self.is_edit else "➕ Registrar en Sistema",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#10B981",
            hover_color="#059669",
            height=42,
            command=self._guardar,
        ).pack(side="left", expand=True, fill="x", padx=(0, 8))

        ctk.CTkButton(
            btn_box,
            text="Cancelar",
            font=ctk.CTkFont(size=12),
            fg_color="#334155",
            hover_color="#475569",
            height=42,
            command=self.destroy,
        ).pack(side="right", padx=(8, 0))

    def _cambiar_rol(self, rol: str) -> None:
        for w in self.sub_rol.winfo_children():
            w.destroy()
        self.widgets_rol.clear()

        def add_campo(lbl: str, row: int, col: int, default: str = "", cmb_vals: list[str] = None):
            ctk.CTkLabel(self.sub_rol, text=lbl, font=ctk.CTkFont(size=11, weight="bold"), text_color="#CBD5E1").grid(row=row, column=col, sticky="w", padx=5, pady=(2, 0))
            if cmb_vals:
                w = ctk.CTkComboBox(self.sub_rol, values=cmb_vals)
                w.set(default if default in cmb_vals else cmb_vals[0])
            else:
                w = ctk.CTkEntry(self.sub_rol)
                if default:
                    w.insert(0, default)
            w.grid(row=row+1, column=col, sticky="ew", padx=5, pady=(2, 8))
            return w

        if rol == "ESTUDIANTE":
            prog_vals = [f"{p.idPrograma} - {p.nombre}" for p in self.controller.programas] or ["1 - Programa General"]
            plan_vals = [f"{pl.idPlanEstudio} - {pl.nombre}" for pl in self.controller.planes] or ["1 - Plan General"]
            
            sel_prog = prog_vals[0]
            sel_plan = plan_vals[0]
            if self.is_edit and self.rol_obj:
                sel_prog = next((pv for pv in prog_vals if pv.startswith(f"{self.rol_obj.idPrograma} - ")), prog_vals[0])
                sel_plan = next((pv for pv in plan_vals if pv.startswith(f"{self.rol_obj.idPlanEstudio} - ")), plan_vals[0])

            self.widgets_rol["programa"] = add_campo("Programa Académico *", 0, 0, sel_prog, prog_vals)
            self.widgets_rol["plan"] = add_campo("Plan de Estudio *", 0, 1, sel_plan, plan_vals)
            
            if self.is_edit:
                estados = [e.name for e in EstadoAcademico]
                self.widgets_rol["estado"] = add_campo("Estado Académico *", 2, 0, getattr(self.rol_obj, "estadoAcademico", "MATRICULADO"), estados)
                self.widgets_rol["ingreso"] = add_campo("Semestre Ingreso", 2, 1, getattr(self.rol_obj, "semestreIngreso", ""))

        elif rol == "PROFESOR":
            prog_vals = [f"{p.idPrograma} - {p.nombre}" for p in self.controller.programas] or ["1 - Programa General"]
            sel_prog = prog_vals[0]
            if self.is_edit and self.rol_obj:
                sel_prog = next((pv for pv in prog_vals if pv.startswith(f"{self.rol_obj.idProgramaPrincipal} - ")), prog_vals[0])

            self.widgets_rol["programa"] = add_campo("Programa Principal *", 0, 0, sel_prog, prog_vals)
            self.widgets_rol["tipo"] = add_campo("Categoría Docente *", 0, 1, getattr(self.rol_obj, "categoriaDocente", "AUXILIAR") if self.is_edit else "AUXILIAR", [e.name for e in TipoProfesor])
            self.widgets_rol["area"] = add_campo("Área de Especialidad", 2, 0, getattr(self.rol_obj, "areaEspecialidad", "") if self.is_edit else "")
            if self.is_edit:
                self.widgets_rol["estado"] = add_campo("Estado *", 2, 1, getattr(self.rol_obj, "estado", "ACTIVO"), ["ACTIVO", "INACTIVO", "SABATICO"])

        elif rol == "ADMINISTRATIVO":
            self.widgets_rol["cargo"] = add_campo("Cargo / Denominación *", 0, 0, getattr(self.rol_obj, "cargo", "") if self.is_edit else "")
            self.widgets_rol["dependencia"] = add_campo("Dependencia / Área *", 0, 1, getattr(self.rol_obj, "dependencia", "") if self.is_edit else "")
            if self.is_edit:
                self.widgets_rol["estado"] = add_campo("Estado *", 2, 0, getattr(self.rol_obj, "estado", "ACTIVO"), ["ACTIVO", "INACTIVO"])

    def _guardar(self) -> None:
        datos_per = self.card_personal.obtener_datos()
        
        if not self.is_edit:
            if not datos_per.get("documentoIdentidad"):
                self.lbl_error.configure(text="⚠️ Documento de identidad es obligatorio.")
                return

        if not datos_per.get("primerNombre") or not datos_per.get("primerApellido"):
            self.lbl_error.configure(text="⚠️ Nombres y apellidos primarios son obligatorios.")
            return

        if self.is_edit:
            try:
                for k, v in datos_per.items():
                    if hasattr(self.persona, k):
                        setattr(self.persona, k, v)
                
                rol = self.tipo_rol
                if rol == "ESTUDIANTE":
                    sp = self.widgets_rol["programa"].get()
                    self.rol_obj.idPrograma = int(sp.split(" - ")[0]) if " - " in sp else 1
                    spl = self.widgets_rol["plan"].get()
                    self.rol_obj.idPlanEstudio = int(spl.split(" - ")[0]) if " - " in spl else 1
                    self.rol_obj.estadoAcademico = self.widgets_rol["estado"].get()
                    self.rol_obj.semestreIngreso = self.widgets_rol["ingreso"].get().strip() or None
                elif rol == "PROFESOR":
                    sp = self.widgets_rol["programa"].get()
                    self.rol_obj.idProgramaPrincipal = int(sp.split(" - ")[0]) if " - " in sp else 1
                    self.rol_obj.categoriaDocente = self.widgets_rol["tipo"].get()
                    self.rol_obj.areaEspecialidad = self.widgets_rol["area"].get().strip() or None
                    self.rol_obj.estado = self.widgets_rol["estado"].get()
                elif rol == "ADMINISTRATIVO":
                    self.rol_obj.cargo = self.widgets_rol["cargo"].get().strip()
                    self.rol_obj.dependencia = self.widgets_rol["dependencia"].get().strip()
                    self.rol_obj.estado = self.widgets_rol["estado"].get()
                
                self.controller.guardar_datos()
                self.destroy()
                self.on_success()
            except Exception as e:
                self.lbl_error.configure(text=f"⚠️ Error: {e}")
        else:
            try:
                rol = self.combo_rol.get()
                kwargs_rol = {}
                if rol == "ESTUDIANTE":
                    sp = self.widgets_rol["programa"].get()
                    kwargs_rol["id_programa"] = int(sp.split(" - ")[0]) if " - " in sp else 1
                    spl = self.widgets_rol["plan"].get()
                    kwargs_rol["id_plan"] = int(spl.split(" - ")[0]) if " - " in spl else 1
                elif rol == "PROFESOR":
                    sp = self.widgets_rol["programa"].get()
                    kwargs_rol["id_programa_principal"] = int(sp.split(" - ")[0]) if " - " in sp else 1
                    kwargs_rol["categoria_docente"] = self.widgets_rol["tipo"].get()
                    kwargs_rol["area_especialidad"] = self.widgets_rol["area"].get().strip() or None
                elif rol == "ADMINISTRATIVO":
                    kwargs_rol["cargo"] = self.widgets_rol["cargo"].get().strip()
                    kwargs_rol["dependencia"] = self.widgets_rol["dependencia"].get().strip()

                self.service.registrar_persona_con_rol(datos_per, rol, **kwargs_rol)
                self.destroy()
                self.on_success()
            except Exception as e:
                self.lbl_error.configure(text=f"⚠️ Error al registrar: {e}")
