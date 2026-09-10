"""Diálogos modales para gestión de Períodos Académicos y Planes de Estudio (Malla Curricular)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from tkinter import messagebox
from typing import TYPE_CHECKING, Callable
import customtkinter as ctk

from ui_gui.theme import Colors, Fonts, create_styled_tabview
from ui_gui.components import PITAGridTable, clean_enum, create_badge
from dominio.modelo_datos import DetallePlanEstudio, PeriodoAcademico, PlanEstudio

if TYPE_CHECKING:
    from ui_gui.academica.academica_service import AcademicaService
    from ui_gui.gui_controller import PITAController


def _parse_fecha(texto: str) -> date | None:
    texto = texto.strip()
    if not texto:
        return None
    try:
        partes = [int(p) for p in texto.split("-")]
        if len(partes) == 3:
            return date(partes[0], partes[1], partes[2])
    except Exception:
        pass
    return None


# ======================================================================
# DIÁLOGOS DE PERÍODOS ACADÉMICOS
# ======================================================================

class DialogNuevoPeriodo(ctk.CTkToplevel):
    """Modal para aperturar / registrar un nuevo período académico."""

    def __init__(self, parent: ctk.CTkBaseClass, service: AcademicaService, on_success: Callable[[], None]) -> None:
        super().__init__(parent)
        self.service = service
        self.on_success = on_success

        self.title("📅 Aperturar Período Académico")
        self.geometry("540x660")
        self.minsize(500, 580)
        self.grab_set()

        self._crear_interfaz()

    def _crear_interfaz(self) -> None:
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=15)

        ctk.CTkLabel(
            scroll,
            text="Apertura de Período Académico",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color="#F8FAFC",
        ).pack(anchor="w", pady=(0, 2))

        ctk.CTkLabel(
            scroll,
            text="Configure el calendario académico, períodos de matrícula y cancelaciones.",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#94A3B8",
        ).pack(anchor="w", pady=(0, 15))

        def _campo(label: str, default: str = "", placeholder: str = "") -> ctk.CTkEntry:
            ctk.CTkLabel(
                scroll,
                text=label,
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                text_color="#CBD5E1",
            ).pack(anchor="w", pady=(6, 2))
            e = ctk.CTkEntry(scroll, height=36, placeholder_text=placeholder)
            if default:
                e.insert(0, default)
            e.pack(fill="x", pady=(0, 4))
            return e

        self.entry_codigo = _campo("Código del Período *", default="2026-1", placeholder="ej: 2026-1")
        self.entry_nombre = _campo("Nombre Descriptivo *", default="Primer Período Académico 2026", placeholder="ej: Primer Semestre 2026")

        row_num = ctk.CTkFrame(scroll, fg_color="transparent")
        row_num.pack(fill="x", pady=(4, 4))
        row_num.columnconfigure(0, weight=1)
        row_num.columnconfigure(1, weight=1)

        ctk.CTkLabel(row_num, text="Año *", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color="#CBD5E1").grid(row=0, column=0, sticky="w", padx=(0, 5))
        ctk.CTkLabel(row_num, text="Número Período (Semestre) *", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color="#CBD5E1").grid(row=0, column=1, sticky="w", padx=(5, 0))

        self.entry_anio = ctk.CTkEntry(row_num, height=36)
        self.entry_anio.insert(0, "2026")
        self.entry_anio.grid(row=1, column=0, sticky="ew", padx=(0, 5), pady=(2, 0))

        self.entry_num = ctk.CTkEntry(row_num, height=36)
        self.entry_num.insert(0, "1")
        self.entry_num.grid(row=1, column=1, sticky="ew", padx=(5, 0), pady=(2, 0))

        self.entry_finicio = _campo("Fecha Inicio Clases (YYYY-MM-DD)", default="2026-02-01")
        self.entry_ffin = _campo("Fecha Fin Clases (YYYY-MM-DD)", default="2026-06-30")
        self.entry_fmat_ini = _campo("Fecha Inicio Matrícula (YYYY-MM-DD)", default="2026-01-15")
        self.entry_fmat_fin = _campo("Fecha Fin Matrícula (YYYY-MM-DD)", default="2026-02-10")
        self.entry_fcanc = _campo("Fecha Límite Cancelación (YYYY-MM-DD)", default="2026-04-15")

        ctk.CTkLabel(
            scroll,
            text="Estado Inicial del Período *",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color="#CBD5E1",
        ).pack(anchor="w", pady=(8, 2))

        self.combo_estado = ctk.CTkComboBox(
            scroll,
            values=["ABIERTO", "EN_CURSO", "PLANIFICACION", "CERRADO"],
            height=36,
        )
        self.combo_estado.set("ABIERTO")
        self.combo_estado.pack(fill="x", pady=(0, 10))

        self.lbl_error = ctk.CTkLabel(scroll, text="", font=ctk.CTkFont(size=12, weight="bold"), text_color="#EF4444")
        self.lbl_error.pack(anchor="w", pady=(2, 8))

        btn_box = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_box.pack(fill="x", pady=(10, 10))

        ctk.CTkButton(
            btn_box,
            text="💾 Aperturar Período",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color="#059669",
            hover_color="#047857",
            height=40,
            command=self._guardar,
        ).pack(side="left", expand=True, fill="x", padx=(0, 6))

        ctk.CTkButton(
            btn_box,
            text="Cancelar",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color="#334155",
            hover_color="#475569",
            height=40,
            command=self.destroy,
        ).pack(side="right", padx=(6, 0))

    def _guardar(self) -> None:
        cod = self.entry_codigo.get().strip()
        nom = self.entry_nombre.get().strip()
        anio_str = self.entry_anio.get().strip()
        num_str = self.entry_num.get().strip()

        if not cod or not nom:
            self.lbl_error.configure(text="⚠️ El código y el nombre son obligatorios.")
            return

        try:
            anio = int(anio_str)
            num = int(num_str)
        except ValueError:
            self.lbl_error.configure(text="⚠️ Año y Número de período deben ser números enteros.")
            return

        f_ini = _parse_fecha(self.entry_finicio.get())
        f_fin = _parse_fecha(self.entry_ffin.get())
        f_mat_ini = _parse_fecha(self.entry_fmat_ini.get())
        f_mat_fin = _parse_fecha(self.entry_fmat_fin.get())
        f_canc = _parse_fecha(self.entry_fcanc.get())

        estado = self.combo_estado.get().strip() or "ABIERTO"

        ctrl = self.service.controller
        nuevo_id = max((p.idPeriodo or 0 for p in ctrl.periodos_academicos), default=0) + 1

        periodo = PeriodoAcademico(
            idPeriodo=nuevo_id,
            codigo=cod,
            nombre=nom,
            anio=anio,
            numeroPeriodo=num,
            fechaInicio=f_ini,
            fechaFin=f_fin,
            fechaInicioMatricula=f_mat_ini,
            fechaFinMatricula=f_mat_fin,
            fechaLimiteCancelacion=f_canc,
            estado=estado,
        )

        ctrl.periodos_academicos.append(periodo)
        ctrl.guardar_datos()
        self.destroy()
        self.on_success()


class DialogEditarPeriodo(ctk.CTkToplevel):
    """Modal para editar fechas y estado de un período académico existente."""

    def __init__(self, parent: ctk.CTkBaseClass, service: AcademicaService, periodo: PeriodoAcademico, on_success: Callable[[], None]) -> None:
        super().__init__(parent)
        self.service = service
        self.periodo = periodo
        self.on_success = on_success

        self.title(f"✏️ Editar Período: {periodo.codigo}")
        self.geometry("540x620")
        self.minsize(500, 550)
        self.grab_set()

        self._crear_interfaz()

    def _crear_interfaz(self) -> None:
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=15)

        ctk.CTkLabel(
            scroll,
            text=f"Modificar Período Académico {self.periodo.codigo}",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color="#F8FAFC",
        ).pack(anchor="w", pady=(0, 15))

        def _campo(label: str, val: str) -> ctk.CTkEntry:
            ctk.CTkLabel(scroll, text=label, font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color="#CBD5E1").pack(anchor="w", pady=(6, 2))
            e = ctk.CTkEntry(scroll, height=36)
            e.insert(0, val)
            e.pack(fill="x", pady=(0, 4))
            return e

        self.entry_nom = _campo("Nombre Descriptivo *", self.periodo.nombre or "")
        self.entry_finicio = _campo("Fecha Inicio Clases (YYYY-MM-DD)", str(self.periodo.fechaInicio or ""))
        self.entry_ffin = _campo("Fecha Fin Clases (YYYY-MM-DD)", str(self.periodo.fechaFin or ""))
        self.entry_fmat_ini = _campo("Fecha Inicio Matrícula (YYYY-MM-DD)", str(self.periodo.fechaInicioMatricula or ""))
        self.entry_fmat_fin = _campo("Fecha Fin Matrícula (YYYY-MM-DD)", str(self.periodo.fechaFinMatricula or ""))
        self.entry_fcanc = _campo("Fecha Límite Cancelación (YYYY-MM-DD)", str(self.periodo.fechaLimiteCancelacion or ""))

        ctk.CTkLabel(scroll, text="Estado del Período *", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color="#CBD5E1").pack(anchor="w", pady=(8, 2))
        self.combo_estado = ctk.CTkComboBox(scroll, values=["ABIERTO", "EN_CURSO", "PLANIFICACION", "CERRADO"], height=36)
        self.combo_estado.set(self.periodo.estado or "ABIERTO")
        self.combo_estado.pack(fill="x", pady=(0, 10))

        self.lbl_error = ctk.CTkLabel(scroll, text="", font=ctk.CTkFont(size=12, weight="bold"), text_color="#EF4444")
        self.lbl_error.pack(anchor="w", pady=(2, 8))

        btn_box = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_box.pack(fill="x", pady=(10, 10))

        ctk.CTkButton(
            btn_box,
            text="💾 Guardar Cambios",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color="#10B981",
            hover_color="#059669",
            height=40,
            command=self._guardar,
        ).pack(side="left", expand=True, fill="x", padx=(0, 6))

        ctk.CTkButton(btn_box, text="Cancelar", font=ctk.CTkFont(size=12), fg_color="#334155", hover_color="#475569", height=40, command=self.destroy).pack(side="right", padx=(6, 0))

    def _guardar(self) -> None:
        nom = self.entry_nom.get().strip()
        if not nom:
            self.lbl_error.configure(text="⚠️ El nombre es obligatorio.")
            return

        self.periodo.nombre = nom
        self.periodo.fechaInicio = _parse_fecha(self.entry_finicio.get())
        self.periodo.fechaFin = _parse_fecha(self.entry_ffin.get())
        self.periodo.fechaInicioMatricula = _parse_fecha(self.entry_fmat_ini.get())
        self.periodo.fechaFinMatricula = _parse_fecha(self.entry_fmat_fin.get())
        self.periodo.fechaLimiteCancelacion = _parse_fecha(self.entry_fcanc.get())
        self.periodo.estado = self.combo_estado.get().strip() or "ABIERTO"

        self.service.controller.guardar_datos()
        self.destroy()
        self.on_success()


# ======================================================================
# DIÁLOGOS DE PLANES DE ESTUDIO
# ======================================================================

class DialogNuevoPlanEstudio(ctk.CTkToplevel):
    """Modal para crear un nuevo Plan de Estudio curricular."""

    def __init__(self, parent: ctk.CTkBaseClass, service: AcademicaService, on_success: Callable[[], None]) -> None:
        super().__init__(parent)
        self.service = service
        self.on_success = on_success

        self.title("📋 Crear Plan de Estudio")
        self.geometry("540x640")
        self.minsize(500, 580)
        self.grab_set()

        self._crear_interfaz()

    def _crear_interfaz(self) -> None:
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=15)

        ctk.CTkLabel(
            scroll,
            text="Nuevo Plan de Estudio Curricular",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color="#F8FAFC",
        ).pack(anchor="w", pady=(0, 2))

        ctk.CTkLabel(
            scroll,
            text="Especifique el programa académico, versión y total de créditos de la malla.",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#94A3B8",
        ).pack(anchor="w", pady=(0, 15))

        def _campo(label: str, default: str = "", placeholder: str = "") -> ctk.CTkEntry:
            ctk.CTkLabel(scroll, text=label, font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color="#CBD5E1").pack(anchor="w", pady=(6, 2))
            e = ctk.CTkEntry(scroll, height=36, placeholder_text=placeholder)
            if default:
                e.insert(0, default)
            e.pack(fill="x", pady=(0, 4))
            return e

        self.entry_codigo = _campo("Código del Plan *", default="PLAN-SIS-2026", placeholder="ej: PLAN-SIS-2026")
        self.entry_nombre = _campo("Nombre del Plan *", default="Plan de Estudios Ingeniería de Sistemas 2026", placeholder="ej: Plan Curricular 2026")

        # Programa
        ctk.CTkLabel(scroll, text="Programa Académico *", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color="#CBD5E1").pack(anchor="w", pady=(6, 2))
        ctrl = self.service.controller
        prog_vals = [f"{p.idPrograma} - {getattr(p, 'codigoPrograma', getattr(p, 'codigo', 'N/A'))} | {p.nombre}" for p in ctrl.programas] or ["1 - SIS | Ingeniería de Sistemas"]
        self.combo_programa = ctk.CTkComboBox(scroll, values=prog_vals, height=36)
        self.combo_programa.pack(fill="x", pady=(0, 4))

        row_v = ctk.CTkFrame(scroll, fg_color="transparent")
        row_v.pack(fill="x", pady=(4, 4))
        row_v.columnconfigure(0, weight=1)
        row_v.columnconfigure(1, weight=1)

        ctk.CTkLabel(row_v, text="Versión *", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color="#CBD5E1").grid(row=0, column=0, sticky="w", padx=(0, 5))
        ctk.CTkLabel(row_v, text="Total Créditos Previstos *", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color="#CBD5E1").grid(row=0, column=1, sticky="w", padx=(5, 0))

        self.entry_version = ctk.CTkEntry(row_v, height=36)
        self.entry_version.insert(0, "V1")
        self.entry_version.grid(row=1, column=0, sticky="ew", padx=(0, 5), pady=(2, 0))

        self.entry_creditos = ctk.CTkEntry(row_v, height=36)
        self.entry_creditos.insert(0, "160")
        self.entry_creditos.grid(row=1, column=1, sticky="ew", padx=(5, 0), pady=(2, 0))

        self.entry_fini = _campo("Fecha Inicio Vigencia (YYYY-MM-DD)", default=str(date.today()))
        self.entry_ffin = _campo("Fecha Fin Vigencia (YYYY-MM-DD - Opcional)", default="")

        ctk.CTkLabel(scroll, text="Estado Inicial *", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color="#CBD5E1").pack(anchor="w", pady=(8, 2))
        self.combo_estado = ctk.CTkComboBox(scroll, values=["ACTIVO", "INACTIVO"], height=36)
        self.combo_estado.set("ACTIVO")
        self.combo_estado.pack(fill="x", pady=(0, 10))

        self.lbl_error = ctk.CTkLabel(scroll, text="", font=ctk.CTkFont(size=12, weight="bold"), text_color="#EF4444")
        self.lbl_error.pack(anchor="w", pady=(2, 8))

        btn_box = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_box.pack(fill="x", pady=(10, 10))

        ctk.CTkButton(
            btn_box,
            text="💾 Guardar Plan de Estudio",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            height=40,
            command=self._guardar,
        ).pack(side="left", expand=True, fill="x", padx=(0, 6))

        ctk.CTkButton(btn_box, text="Cancelar", font=ctk.CTkFont(size=12), fg_color="#334155", hover_color="#475569", height=40, command=self.destroy).pack(side="right", padx=(6, 0))

    def _guardar(self) -> None:
        cod = self.entry_codigo.get().strip()
        nom = self.entry_nombre.get().strip()
        ver = self.entry_version.get().strip() or "V1"
        cred_str = self.entry_creditos.get().strip()

        if not cod or not nom:
            self.lbl_error.configure(text="⚠️ El código y el nombre del plan son obligatorios.")
            return

        try:
            total_cred = int(cred_str)
        except ValueError:
            self.lbl_error.configure(text="⚠️ El total de créditos debe ser un entero.")
            return

        prog_sel = self.combo_programa.get().split(" - ")[0].strip()
        id_prog = int(prog_sel) if prog_sel.isdigit() else 1

        f_ini = _parse_fecha(self.entry_fini.get()) or date.today()
        f_fin = _parse_fecha(self.entry_ffin.get())
        estado = self.combo_estado.get().strip() or "ACTIVO"

        ctrl = self.service.controller
        nuevo_id = max((p.idPlanEstudio or 0 for p in ctrl.planes), default=0) + 1

        nuevo_plan = PlanEstudio(
            idPlanEstudio=nuevo_id,
            codigo=cod,
            nombre=nom,
            version=ver,
            fechaInicioVigencia=f_ini,
            fechaFinVigencia=f_fin,
            totalCreditos=total_cred,
            idPrograma=id_prog,
            estado=estado,
        )

        ctrl.planes.append(nuevo_plan)
        ctrl.guardar_datos()
        self.destroy()
        self.on_success()


# ======================================================================
# DIÁLOGO MALLA CURRICULAR (DETALLE DEL PLAN)
# ======================================================================

class DialogMallaCurricular(ctk.CTkToplevel):
    """Modal para gestionar la malla curricular: agregar y remover asignaturas del plan de estudio."""

    def __init__(self, parent: ctk.CTkBaseClass, service: AcademicaService, plan: PlanEstudio, on_success: Callable[[], None]) -> None:
        super().__init__(parent)
        self.service = service
        self.plan = plan
        self.on_success = on_success

        self.title(f"📜 Malla Curricular: {plan.codigo} - {plan.nombre}")
        self.geometry("880x680")
        self.minsize(800, 600)
        self.grab_set()

        self._crear_interfaz()

    def _crear_interfaz(self) -> None:
        # Cabecera informativa
        header = ctk.CTkFrame(self, fg_color="#1E293B", corner_radius=10)
        header.pack(fill="x", padx=15, pady=(15, 10))

        ctrl = self.service.controller
        prog = next((pr for pr in ctrl.programas if pr.idPrograma == self.plan.idPrograma), None)
        cod_prog = getattr(prog, "codigoPrograma", getattr(prog, "codigo", "N/A")) if prog else "N/A"
        nom_prog = f"{cod_prog} - {prog.nombre}" if prog else f"Programa #{self.plan.idPrograma}"

        ctk.CTkLabel(
            header,
            text=f"📜 {self.plan.codigo} — {self.plan.nombre}",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color="#38BDF8",
        ).pack(anchor="w", padx=15, pady=(10, 2))

        detalles_actuales = [d for d in ctrl.detalles_plan if d.idPlanEstudio == self.plan.idPlanEstudio and d.estado != "INACTIVO"]
        creditos_malla = sum(d.numeroCreditos or 0 for d in detalles_actuales)

        ctk.CTkLabel(
            header,
            text=f"Programa: {nom_prog}  |  Versión: {self.plan.version}  |  Créditos en Malla: {creditos_malla} / {self.plan.totalCreditos or 160}  |  Estado: {self.plan.estado}",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#94A3B8",
        ).pack(anchor="w", padx=15, pady=(0, 10))

        # Panel para agregar asignatura a la malla
        card_add = ctk.CTkFrame(self, fg_color="#0F172A", corner_radius=10)
        card_add.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(
            card_add,
            text="➕ Incluir Asignatura a la Malla Curricular",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#F8FAFC",
        ).pack(anchor="w", padx=12, pady=(10, 6))

        row_inputs = ctk.CTkFrame(card_add, fg_color="transparent")
        row_inputs.pack(fill="x", padx=12, pady=(0, 10))
        row_inputs.columnconfigure(0, weight=3)
        row_inputs.columnconfigure(1, weight=1)
        row_inputs.columnconfigure(2, weight=1)
        row_inputs.columnconfigure(3, weight=1)
        row_inputs.columnconfigure(4, weight=1)

        ctk.CTkLabel(row_inputs, text="Asignatura Catálogo *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=0, column=0, sticky="w", padx=4)
        ctk.CTkLabel(row_inputs, text="Semestre Sugerido *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=0, column=1, sticky="w", padx=4)
        ctk.CTkLabel(row_inputs, text="Tipo Curso *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=0, column=2, sticky="w", padx=4)
        ctk.CTkLabel(row_inputs, text="Obligatoria?", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=0, column=3, sticky="w", padx=4)

        cursos_vals = [f"{c.idCurso} - {c.codigoCurso} | {c.nombre} ({c.numeroCreditos} cr)" for c in ctrl.cursos] or ["1 - Sin asignaturas registradas"]
        self.combo_curso = ctk.CTkComboBox(row_inputs, values=cursos_vals, height=34)
        self.combo_curso.grid(row=1, column=0, sticky="ew", padx=4, pady=2)

        self.combo_semestre = ctk.CTkComboBox(row_inputs, values=[str(s) for s in range(1, 11)], height=34)
        self.combo_semestre.set("1")
        self.combo_semestre.grid(row=1, column=1, sticky="ew", padx=4, pady=2)

        self.combo_tipo = ctk.CTkComboBox(row_inputs, values=["OBLIGATORIA", "ELECTIVA", "OPTATIVA"], height=34)
        self.combo_tipo.set("OBLIGATORIA")
        self.combo_tipo.grid(row=1, column=2, sticky="ew", padx=4, pady=2)

        self.combo_obliga = ctk.CTkComboBox(row_inputs, values=["SI", "NO"], height=34)
        self.combo_obliga.set("SI")
        self.combo_obliga.grid(row=1, column=3, sticky="ew", padx=4, pady=2)

        btn_incluir = ctk.CTkButton(
            row_inputs,
            text="➕ Incluir",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#059669",
            hover_color="#047857",
            height=34,
            command=self._incluir_asignatura,
        )
        btn_incluir.grid(row=1, column=4, sticky="ew", padx=4, pady=2)

        # Tabla de asignaturas incluidas
        self.frame_tabla = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_tabla.pack(fill="both", expand=True, padx=15, pady=(10, 15))

        self._render_tabla()

    def _render_tabla(self) -> None:
        for w in self.frame_tabla.winfo_children():
            w.destroy()

        ctrl = self.service.controller
        detalles = [d for d in ctrl.detalles_plan if d.idPlanEstudio == self.plan.idPlanEstudio and d.estado != "INACTIVO"]
        detalles.sort(key=lambda x: (x.semestreSugerido or 0, x.idDetallePlan or 0))

        headers = ["Semestre", "Código Asignatura", "Nombre Asignatura", "Créditos", "Tipo Curso", "Obligatoria", "Acciones"]
        col_weights = [1, 2, 4, 1, 2, 1, 2]
        col_mins = [60, 90, 160, 60, 90, 70, 90]

        table = PITAGridTable(self.frame_tabla, headers=headers, col_weights=col_weights, col_mins=col_mins)
        table.pack(fill="both", expand=True)

        if not detalles:
            ctk.CTkLabel(table, text="Este plan de estudio aún no tiene asignaturas en su malla.", text_color="#94A3B8").pack(pady=30)
            return

        for d in detalles:
            cur = next((c for c in ctrl.cursos if c.idCurso == d.idCurso), None)
            nom_c = cur.nombre if cur else f"Curso #{d.idCurso}"
            cod_c = cur.codigoCurso if cur else f"ID-{d.idCurso}"
            cred_c = d.numeroCreditos or (cur.numeroCreditos if cur else 3)

            act_spec = (
                "actions",
                [
                    ("❌ Quitar", lambda det_id=d.idDetallePlan: self._quitar_asignatura(det_id), "#EF4444", "#DC2626"),
                ],
            )

            cells = [
                f"Semestre {d.semestreSugerido or 1}",
                (cod_c, "#38BDF8"),
                nom_c,
                f"{cred_c} créditos",
                d.tipoCurso or "OBLIGATORIA",
                "Sí" if d.esObligatorio else "No",
                act_spec,
            ]
            table.add_row_items(cells)

    def _incluir_asignatura(self) -> None:
        ctrl = self.service.controller
        if not ctrl.cursos:
            messagebox.showwarning("Sin Asignaturas", "Primero debe registrar asignaturas en el catálogo.")
            return

        sel_val = self.combo_curso.get().split(" - ")[0].strip()
        if not sel_val.isdigit():
            messagebox.showwarning("Selección Inválida", "Seleccione una asignatura válida.")
            return

        id_curso = int(sel_val)
        cur = next((c for c in ctrl.cursos if c.idCurso == id_curso), None)
        if not cur:
            messagebox.showerror("Error", "Asignatura no encontrada.")
            return

        # Verificar si ya está en la malla
        ya_existe = any(d.idPlanEstudio == self.plan.idPlanEstudio and d.idCurso == id_curso and d.estado != "INACTIVO" for d in ctrl.detalles_plan)
        if ya_existe:
            messagebox.showwarning("Asignatura Existente", f"La asignatura {cur.nombre} ya está incluida en este plan de estudios.")
            return

        sem_sug = int(self.combo_semestre.get()) if self.combo_semestre.get().isdigit() else 1
        tipo_c = self.combo_tipo.get().strip() or "OBLIGATORIA"
        es_obliga = (self.combo_obliga.get().strip() == "SI")
        creditos = cur.numeroCreditos or 3

        nuevo_id = max((d.idDetallePlan or 0 for d in ctrl.detalles_plan), default=0) + 1
        nuevo_detalle = DetallePlanEstudio(
            idDetallePlan=nuevo_id,
            idPlanEstudio=self.plan.idPlanEstudio,
            idCurso=id_curso,
            semestreSugerido=sem_sug,
            tipoCurso=tipo_c,
            numeroCreditos=creditos,
            esObligatorio=es_obliga,
            estado="ACTIVO",
        )

        ctrl.detalles_plan.append(nuevo_detalle)
        self.plan.totalCreditos = sum(d.numeroCreditos or 0 for d in ctrl.detalles_plan if d.idPlanEstudio == self.plan.idPlanEstudio and d.estado != "INACTIVO")
        ctrl.guardar_datos()

        self._render_tabla()
        self.on_success()

    def _quitar_asignatura(self, id_detalle: int) -> None:
        ctrl = self.service.controller
        det = next((d for d in ctrl.detalles_plan if d.idDetallePlan == id_detalle), None)
        if not det:
            return

        det.estado = "INACTIVO"
        self.plan.totalCreditos = sum(d.numeroCreditos or 0 for d in ctrl.detalles_plan if d.idPlanEstudio == self.plan.idPlanEstudio and d.estado != "INACTIVO")
        ctrl.guardar_datos()

        self._render_tabla()
        self.on_success()
