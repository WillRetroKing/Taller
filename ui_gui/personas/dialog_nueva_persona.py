from __future__ import annotations

"""Modal para registrar una nueva Persona y asignarle un Rol institucional en PITA."""

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


class DialogNuevaPersona(ctk.CTkToplevel):
    """Diálogo modal para registrar Persona y vincularle un Rol."""

    def __init__(
        self,
        parent: ctk.CTkBaseClass,
        controller: PITAController,
        service: PersonasService,
        on_success: Callable[[], None],
    ) -> None:
        super().__init__(parent)
        self.controller = controller
        self.service = service
        self.on_success = on_success

        self.title("➕ Registrar Persona y Asignar Rol en PITA")
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
            text="➕ Registrar Nueva Persona y Asignar Rol",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#F8FAFC",
        ).pack(anchor="w")
        ctk.CTkLabel(
            header_frame,
            text="Complete los datos de identificación, contacto y la información del rol académico o laboral.",
            font=ctk.CTkFont(size=11),
            text_color="#94A3B8",
        ).pack(anchor="w", pady=(2, 0))

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        # Tarjeta 1: Información Personal (Reutilizable)
        self.card_personal = PersonaFormCard(scroll, incluir_documento=True)

        # Tarjeta 2: Rol Institucional
        card_r = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
        card_r.pack(fill="x", pady=6)

        ctk.CTkLabel(
            card_r,
            text="🎓 2. Rol y Vinculación en PITA",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#A78BFA",
        ).pack(anchor="w", padx=15, pady=(12, 6))

        row_rol = ctk.CTkFrame(card_r, fg_color="transparent")
        row_rol.pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkLabel(row_rol, text="Rol Institucional a Asignar:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(side="left", padx=(0, 10))
        self.combo_rol = ctk.CTkComboBox(row_rol, values=["ESTUDIANTE", "PROFESOR", "ADMINISTRATIVO"], width=200)
        self.combo_rol.set("ESTUDIANTE")
        self.combo_rol.pack(side="left")

        self.sub_rol = ctk.CTkFrame(card_r, fg_color="transparent")
        self.sub_rol.pack(fill="x", padx=15, pady=(0, 15))
        self.sub_rol.columnconfigure(0, weight=1)
        self.sub_rol.columnconfigure(1, weight=1)

        self.combo_rol.configure(command=self._cambiar_rol)
        self._cambiar_rol("ESTUDIANTE")

        # Label de error
        self.lbl_error = ctk.CTkLabel(scroll, text="", text_color="#EF4444", font=ctk.CTkFont(size=12, weight="bold"))
        self.lbl_error.pack(pady=(5, 2))

        # Botón Guardar
        btn_save = ctk.CTkButton(
            scroll,
            text="💾 Registrar Persona y Guardar Rol",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#059669",
            hover_color="#047857",
            height=40,
            command=self._guardar,
        )
        btn_save.pack(fill="x", padx=15, pady=(10, 20))

    def _cambiar_rol(self, nuevo_rol: str) -> None:
        for w in self.sub_rol.winfo_children():
            w.destroy()
        self.widgets_rol.clear()

        prog_vals = [f"{p.idPrograma} - {p.nombre}" for p in self.controller.programas] if self.controller.programas else ["1 - Programa General"]
        plan_vals = [f"{pl.idPlanEstudio} - {pl.nombre}" for pl in self.controller.planes] if self.controller.planes else ["1 - Plan General"]

        if nuevo_rol == "ESTUDIANTE":
            ctk.CTkLabel(self.sub_rol, text="Código Estudiante *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=0, column=0, sticky="w", padx=5, pady=(2, 0))
            ctk.CTkLabel(self.sub_rol, text="Semestre Actual", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=0, column=1, sticky="w", padx=5, pady=(2, 0))

            entry_cod = ctk.CTkEntry(self.sub_rol, placeholder_text="ej: EST-2026-01")
            entry_cod.grid(row=1, column=0, sticky="ew", padx=5, pady=(2, 8))
            self.widgets_rol["codigo"] = entry_cod

            combo_sem = ctk.CTkComboBox(self.sub_rol, values=[str(i) for i in range(1, 11)])
            combo_sem.set("1")
            combo_sem.grid(row=1, column=1, sticky="ew", padx=5, pady=(2, 8))
            self.widgets_rol["semestre"] = combo_sem

            ctk.CTkLabel(self.sub_rol, text="Programa Académico *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=2, column=0, sticky="w", padx=5, pady=(2, 0))
            ctk.CTkLabel(self.sub_rol, text="Plan de Estudio *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=2, column=1, sticky="w", padx=5, pady=(2, 0))

            combo_prog = ctk.CTkComboBox(self.sub_rol, values=prog_vals)
            combo_prog.set(prog_vals[0])
            combo_prog.grid(row=3, column=0, sticky="ew", padx=5, pady=(2, 8))
            self.widgets_rol["programa"] = combo_prog

            combo_plan = ctk.CTkComboBox(self.sub_rol, values=plan_vals)
            combo_plan.set(plan_vals[0])
            combo_plan.grid(row=3, column=1, sticky="ew", padx=5, pady=(2, 8))
            self.widgets_rol["plan"] = combo_plan

            ctk.CTkLabel(self.sub_rol, text="Estado Académico", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=4, column=0, sticky="w", padx=5, pady=(2, 0))
            ctk.CTkLabel(self.sub_rol, text="Fecha Ingreso (AAAA-MM-DD)", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=4, column=1, sticky="w", padx=5, pady=(2, 0))

            combo_est_acad = ctk.CTkComboBox(self.sub_rol, values=["ACTIVO", "ASPIRANTE", "ADMITIDO", "MATRICULADO"])
            combo_est_acad.set("ACTIVO")
            combo_est_acad.grid(row=5, column=0, sticky="ew", padx=5, pady=(2, 4))
            self.widgets_rol["estado_academico"] = combo_est_acad

            entry_fing = ctk.CTkEntry(self.sub_rol)
            entry_fing.insert(0, date.today().strftime("%Y-%m-%d"))
            entry_fing.grid(row=5, column=1, sticky="ew", padx=5, pady=(2, 4))
            self.widgets_rol["fecha_ingreso"] = entry_fing

        elif nuevo_rol == "PROFESOR":
            ctk.CTkLabel(self.sub_rol, text="Código Profesor *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=0, column=0, sticky="w", padx=5, pady=(2, 0))
            ctk.CTkLabel(self.sub_rol, text="Programa Principal *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=0, column=1, sticky="w", padx=5, pady=(2, 0))

            entry_cod = ctk.CTkEntry(self.sub_rol, placeholder_text="ej: PROF-2026-01")
            entry_cod.grid(row=1, column=0, sticky="ew", padx=5, pady=(2, 8))
            self.widgets_rol["codigo"] = entry_cod

            combo_prog = ctk.CTkComboBox(self.sub_rol, values=prog_vals)
            combo_prog.set(prog_vals[0])
            combo_prog.grid(row=1, column=1, sticky="ew", padx=5, pady=(2, 8))
            self.widgets_rol["programa"] = combo_prog

            ctk.CTkLabel(self.sub_rol, text="Tipo de Profesor / Vinculación *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=2, column=0, sticky="w", padx=5, pady=(2, 0))
            ctk.CTkLabel(self.sub_rol, text="Categoría Docente *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=2, column=1, sticky="w", padx=5, pady=(2, 0))

            combo_tipo = ctk.CTkComboBox(self.sub_rol, values=["PLANTA", "OCASIONAL", "CATEDRATICO", "CATEDRATICO_AD_HONOREM"])
            combo_tipo.set("PLANTA")
            combo_tipo.grid(row=3, column=0, sticky="ew", padx=5, pady=(2, 8))
            self.widgets_rol["tipo_profesor"] = combo_tipo

            combo_cat = ctk.CTkComboBox(self.sub_rol, values=["AUXILIAR", "ASISTENTE", "ASOCIADO", "TITULAR", "NO_CATEGORIZADO"])
            combo_cat.set("ASISTENTE")
            combo_cat.grid(row=3, column=1, sticky="ew", padx=5, pady=(2, 8))
            self.widgets_rol["categoria_docente"] = combo_cat

            ctk.CTkLabel(self.sub_rol, text="Dedicación *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=4, column=0, sticky="w", padx=5, pady=(2, 0))
            ctk.CTkLabel(self.sub_rol, text="Horas Semanales", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=4, column=1, sticky="w", padx=5, pady=(2, 0))

            combo_ded = ctk.CTkComboBox(self.sub_rol, values=["TIEMPO_COMPLETO", "MEDIO_TIEMPO", "HORA_CATEDRA"])
            combo_ded.set("TIEMPO_COMPLETO")
            combo_ded.grid(row=5, column=0, sticky="ew", padx=5, pady=(2, 8))
            self.widgets_rol["dedicacion"] = combo_ded

            entry_horas = ctk.CTkEntry(self.sub_rol)
            entry_horas.insert(0, "40")
            entry_horas.grid(row=5, column=1, sticky="ew", padx=5, pady=(2, 8))
            self.widgets_rol["horas"] = entry_horas

            ctk.CTkLabel(self.sub_rol, text="Máximo Nivel de Estudio", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=6, column=0, sticky="w", padx=5, pady=(2, 0))
            ctk.CTkLabel(self.sub_rol, text="Puntos Salariales (Dec. 1279)", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=6, column=1, sticky="w", padx=5, pady=(2, 0))

            combo_nivel = ctk.CTkComboBox(self.sub_rol, values=["PREGRADO", "ESPECIALIZACION", "MAESTRIA", "DOCTORADO"])
            combo_nivel.set("MAESTRIA")
            combo_nivel.grid(row=7, column=0, sticky="ew", padx=5, pady=(2, 8))
            self.widgets_rol["nivel_estudio"] = combo_nivel

            entry_puntos = ctk.CTkEntry(self.sub_rol)
            entry_puntos.insert(0, "350")
            entry_puntos.grid(row=7, column=1, sticky="ew", padx=5, pady=(2, 8))
            self.widgets_rol["puntos"] = entry_puntos

            ctk.CTkLabel(self.sub_rol, text="Título Profesional", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=8, column=0, sticky="w", padx=5, pady=(2, 0))
            ctk.CTkLabel(self.sub_rol, text="Área de Conocimiento", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=8, column=1, sticky="w", padx=5, pady=(2, 0))

            entry_tit = ctk.CTkEntry(self.sub_rol, placeholder_text="ej: Ingeniero de Sistemas")
            entry_tit.grid(row=9, column=0, sticky="ew", padx=5, pady=(2, 4))
            self.widgets_rol["titulo"] = entry_tit

            entry_area = ctk.CTkEntry(self.sub_rol, placeholder_text="ej: Computación y Software")
            entry_area.grid(row=9, column=1, sticky="ew", padx=5, pady=(2, 4))
            self.widgets_rol["area"] = entry_area

        elif nuevo_rol == "ADMINISTRATIVO":
            ctk.CTkLabel(self.sub_rol, text="Código Empleado *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=0, column=0, sticky="w", padx=5, pady=(2, 0))
            ctk.CTkLabel(self.sub_rol, text="Cargo Institucional *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=0, column=1, sticky="w", padx=5, pady=(2, 0))

            entry_cod = ctk.CTkEntry(self.sub_rol, placeholder_text="ej: ADM-2026-01")
            entry_cod.grid(row=1, column=0, sticky="ew", padx=5, pady=(2, 8))
            self.widgets_rol["codigo"] = entry_cod

            entry_cargo = ctk.CTkEntry(self.sub_rol, placeholder_text="ej: Profesional Universitario")
            entry_cargo.insert(0, "Profesional Universitario")
            entry_cargo.grid(row=1, column=1, sticky="ew", padx=5, pady=(2, 8))
            self.widgets_rol["cargo"] = entry_cargo

            ctk.CTkLabel(self.sub_rol, text="Dependencia *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=2, column=0, sticky="w", padx=5, pady=(2, 0))
            ctk.CTkLabel(self.sub_rol, text="Nivel / Categoría *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=2, column=1, sticky="w", padx=5, pady=(2, 0))

            entry_dep = ctk.CTkEntry(self.sub_rol, placeholder_text="ej: Vicerrectoría Académica")
            entry_dep.insert(0, "Vicerrectoría Académica")
            entry_dep.grid(row=3, column=0, sticky="ew", padx=5, pady=(2, 8))
            self.widgets_rol["dependencia"] = entry_dep

            combo_cat = ctk.CTkComboBox(self.sub_rol, values=["PROFESIONAL", "DIRECTIVO", "ASESOR", "TECNICO", "ASISTENCIAL"])
            combo_cat.set("PROFESIONAL")
            combo_cat.grid(row=3, column=1, sticky="ew", padx=5, pady=(2, 8))
            self.widgets_rol["categoria"] = combo_cat

            ctk.CTkLabel(self.sub_rol, text="Tipo Contratación", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=4, column=0, sticky="w", padx=5, pady=(2, 0))
            ctk.CTkLabel(self.sub_rol, text="Salario Base Mensual ($) *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=4, column=1, sticky="w", padx=5, pady=(2, 0))

            combo_tcont = ctk.CTkComboBox(self.sub_rol, values=["PLANTA", "CARRERA_ADMINISTRATIVA", "LIBRE_NOMBRAMIENTO", "PROVISIONALIDAD", "PRESTACION_SERVICIOS"])
            combo_tcont.set("PLANTA")
            combo_tcont.grid(row=5, column=0, sticky="ew", padx=5, pady=(2, 8))
            self.widgets_rol["tipo_contratacion"] = combo_tcont

            entry_sal = ctk.CTkEntry(self.sub_rol)
            entry_sal.insert(0, "2800000")
            entry_sal.grid(row=5, column=1, sticky="ew", padx=5, pady=(2, 8))
            self.widgets_rol["salario"] = entry_sal

            ctk.CTkLabel(self.sub_rol, text="Fecha Vinculación (AAAA-MM-DD)", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=6, column=0, sticky="w", padx=5, pady=(2, 0))
            entry_fvin = ctk.CTkEntry(self.sub_rol)
            entry_fvin.insert(0, date.today().strftime("%Y-%m-%d"))
            entry_fvin.grid(row=7, column=0, sticky="ew", padx=5, pady=(2, 4))
            self.widgets_rol["fecha_vinculacion"] = entry_fvin

    def _guardar(self) -> None:
        datos_p, error_p = self.card_personal.extraer_datos()
        if error_p:
            self.lbl_error.configure(text=f"⚠️ {error_p}")
            return

        rol = self.combo_rol.get()
        cod_widget = self.widgets_rol.get("codigo")
        cod = cod_widget.get().strip() if cod_widget else ""

        # Validaciones de unicidad vía Service
        ok_doc, msg_doc = self.service.validar_documento_unico(datos_p["numeroDocumento"])
        if not ok_doc:
            self.lbl_error.configure(text=f"⚠️ {msg_doc}")
            return

        ok_cod, msg_cod = self.service.validar_codigo_unico(rol, cod)
        if not ok_cod:
            self.lbl_error.configure(text=f"⚠️ {msg_cod}")
            return

        # Construir datos específicos del rol
        datos_rol: dict[str, Any] = {"codigo": cod}

        if rol == "ESTUDIANTE":
            sem_str = self.widgets_rol["semestre"].get().strip() if "semestre" in self.widgets_rol else "1"
            datos_rol["semestreActual"] = int(sem_str) if sem_str.isdigit() else 1

            prog_sel = self.widgets_rol["programa"].get().split(" - ")[0] if "programa" in self.widgets_rol else "1"
            datos_rol["idPrograma"] = int(prog_sel) if prog_sel.isdigit() else 1

            plan_sel = self.widgets_rol["plan"].get().split(" - ")[0] if "plan" in self.widgets_rol else "1"
            datos_rol["idPlanEstudio"] = int(plan_sel) if plan_sel.isdigit() else 1

            est_acad_str = clean_enum(self.widgets_rol["estado_academico"].get() if "estado_academico" in self.widgets_rol else "ACTIVO")
            try:
                datos_rol["estadoAcademico"] = EstadoAcademico[est_acad_str]
            except KeyError:
                datos_rol["estadoAcademico"] = EstadoAcademico.ACTIVO

            fing_str = self.widgets_rol["fecha_ingreso"].get().strip() if "fecha_ingreso" in self.widgets_rol else ""
            try:
                datos_rol["fechaIngreso"] = datetime.strptime(fing_str, "%Y-%m-%d").date() if fing_str else date.today()
            except ValueError:
                datos_rol["fechaIngreso"] = date.today()

        elif rol == "PROFESOR":
            prog_sel = self.widgets_rol["programa"].get().split(" - ")[0] if "programa" in self.widgets_rol else "1"
            datos_rol["idProgramaPrincipal"] = int(prog_sel) if prog_sel.isdigit() else 1

            tipo_str = clean_enum(self.widgets_rol["tipo_profesor"].get() if "tipo_profesor" in self.widgets_rol else "PLANTA")
            try:
                datos_rol["tipoProfesor"] = TipoProfesor[tipo_str]
            except KeyError:
                datos_rol["tipoProfesor"] = TipoProfesor.PLANTA

            ded_str = clean_enum(self.widgets_rol["dedicacion"].get() if "dedicacion" in self.widgets_rol else "TIEMPO_COMPLETO")
            try:
                datos_rol["dedicacion"] = Dedicacion[ded_str]
            except KeyError:
                datos_rol["dedicacion"] = Dedicacion.TIEMPO_COMPLETO

            datos_rol["categoriaDocente"] = self.widgets_rol["categoria_docente"].get() if "categoria_docente" in self.widgets_rol else "ASISTENTE"
            datos_rol["maximoNivelEstudio"] = self.widgets_rol["nivel_estudio"].get() if "nivel_estudio" in self.widgets_rol else "MAESTRIA"
            datos_rol["tituloProfesional"] = self.widgets_rol["titulo"].get().strip() if "titulo" in self.widgets_rol else ""
            datos_rol["areaConocimiento"] = self.widgets_rol["area"].get().strip() if "area" in self.widgets_rol else ""

            horas_str = self.widgets_rol["horas"].get().strip() if "horas" in self.widgets_rol else "40"
            datos_rol["numeroHorasSemanales"] = Decimal(horas_str) if horas_str.replace(".", "", 1).isdigit() else Decimal("40")

            puntos_str = self.widgets_rol["puntos"].get().strip() if "puntos" in self.widgets_rol else "350"
            datos_rol["puntosSalariales"] = Decimal(puntos_str) if puntos_str.replace(".", "", 1).isdigit() else Decimal("350")

        elif rol == "ADMINISTRATIVO":
            datos_rol["cargo"] = self.widgets_rol["cargo"].get().strip() if "cargo" in self.widgets_rol else "Profesional Universitario"
            datos_rol["dependencia"] = self.widgets_rol["dependencia"].get().strip() if "dependencia" in self.widgets_rol else "Vicerrectoría Académica"
            datos_rol["categoria"] = self.widgets_rol["categoria"].get().strip() if "categoria" in self.widgets_rol else "PROFESIONAL"
            datos_rol["tipoContratacion"] = self.widgets_rol["tipo_contratacion"].get() if "tipo_contratacion" in self.widgets_rol else "PLANTA"

            sal_str = self.widgets_rol["salario"].get().strip() if "salario" in self.widgets_rol else "2800000"
            datos_rol["salarioBase"] = Decimal(sal_str) if sal_str.replace(".", "", 1).isdigit() else Decimal("2800000")

            fvin_str = self.widgets_rol["fecha_vinculacion"].get().strip() if "fecha_vinculacion" in self.widgets_rol else ""
            try:
                datos_rol["fechaVinculacion"] = datetime.strptime(fvin_str, "%Y-%m-%d").date() if fvin_str else date.today()
            except ValueError:
                datos_rol["fechaVinculacion"] = date.today()

        self.service.registrar_persona_con_rol(datos_p, rol, datos_rol)
        self.destroy()
        self.on_success()
