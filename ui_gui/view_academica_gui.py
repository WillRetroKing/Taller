"""Vista de Gestión Académica (Cursos, Ofertas, Matrículas, Calificaciones y Alertas EBRA)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
import customtkinter as ctk
from typing import TYPE_CHECKING

from ui_gui.theme import Colors, Fonts, create_styled_tabview
from ui_gui.components import PITAGridTable, create_badge
from modelo_datos import (
    Calificacion,
    Curso,
    DetalleMatricula,
    EstadoAcademico,
    EstadoCurso,
    Evaluacion,
    Facultad,
    MatriculaAcademica,
    OfertaCurso,
    PeriodoAcademico,
    ProgramaAcademico,
)

if TYPE_CHECKING:
    from ui_gui.gui_controller import PITAController


class AcademicaViewGUI(ctk.CTkFrame):
    """Vista académica completa: Oferta de cursos, matrícula de estudiantes, notas y alertas EBRA."""

    def __init__(self, parent: ctk.CTk, controller: PITAController) -> None:
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        self._crear_interfaz()

    def _crear_interfaz(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(
            header,
            text="🎓 Gestión Académica, Matrícula y Alertas EBRA",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=Colors.TEXT_MAIN,
        ).pack(side="left")

        btn_nuevo_curso = ctk.CTkButton(
            header,
            text="➕ Crear Nuevo Curso",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#0067C0",
            hover_color="#005FB8",
            corner_radius=8,
            command=self._abrir_modal_nuevo_curso,
        )
        btn_nuevo_curso.pack(side="right")

        # Pestañas
        self.tabview = create_styled_tabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=5)

        self.tab_oferta = self.tabview.add("📚 Cursos & Oferta")
        self.tab_matricula = self.tabview.add("✍️ Matrícula de Cursos")
        self.tab_evaluaciones = self.tabview.add("📝 Evaluaciones y Notas")
        self.tab_ebra = self.tabview.add("⚠️ Informe Alertas EBRA")

        self._llenar_tab_oferta()
        self._llenar_tab_matricula()
        self._llenar_tab_evaluaciones()
        self._llenar_tab_ebra()

    # ------------------------------------------------------------------
    # TAB OFERTA Y CURSOS
    # ------------------------------------------------------------------
    def _llenar_tab_oferta(self) -> None:
        for w in self.tab_oferta.winfo_children():
            w.destroy()

        headers = ["Código Curso", "Nombre de Asignatura", "Créditos", "Horas Teórica/Práctica", "Nota Mínima", "Estado", "Acciones"]
        col_weights = [2, 4, 2, 3, 2, 2, 3]
        col_mins = [100, 180, 90, 140, 100, 90, 140]

        table = PITAGridTable(self.tab_oferta, headers=headers, col_weights=col_weights, col_mins=col_mins)
        table.pack(fill="both", expand=True, padx=5, pady=5)

        if not self.controller.cursos:
            ctk.CTkLabel(table, text="No hay cursos configurados.", text_color="#94A3B8").pack(pady=20)
            return

        for c in self.controller.cursos:
            act_spec = (
                "actions",
                [
                    ("✏️ Editar", lambda cur=c: self._editar_curso(cur), "#334155", "#475569", 70, 28),
                    ("❌ Eliminar", lambda c_id=c.idCurso: self._eliminar_curso(c_id), "#EF4444", "#DC2626", 75, 28),
                ],
            )

            cells = [
                (getattr(c, "codigoCurso", "N/A"), "#38BDF8"),
                (getattr(c, "nombre", "N/A"), "#F8FAFC"),
                f"{getattr(c, 'numeroCreditos', 3)} créditos",
                f"{getattr(c, 'horasTeoricas', 3)}h Teóricas / {getattr(c, 'horasPracticas', 2)}h Prácticas",
                str(getattr(c, "notaMinimaAprobatoria", "3.0")),
                ("badge", "● ACTIVO", "active"),
                act_spec,
            ]
            table.add_row_items(cells)

    # ------------------------------------------------------------------
    # TAB MATRÍCULA
    # ------------------------------------------------------------------
    def _llenar_tab_matricula(self) -> None:
        container = ctk.CTkFrame(self.tab_matricula, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=5, pady=5)

        form = ctk.CTkFrame(container, corner_radius=8)
        form.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(form, text="Realizar Nueva Matrícula Académica", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(10, 5))

        f_row = ctk.CTkFrame(form, fg_color="transparent")
        f_row.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(f_row, text="Estudiante:").pack(side="left", padx=(0, 5))
        estud_options = [
            f"{e.codigoEstudiante} - {next((p.primerNombre + ' ' + p.primerApellido for p in self.controller.personas if p.idPersona == e.idPersona), 'Estudiante')}"
            for e in self.controller.estudiantes
        ] or ["Sin estudiantes"]
        combo_est = ctk.CTkComboBox(f_row, values=estud_options, width=300)
        combo_est.pack(side="left", padx=5)

        ctk.CTkLabel(f_row, text="Curso:").pack(side="left", padx=(15, 5))
        curso_options = [f"{c.codigoCurso} - {c.nombre}" for c in self.controller.cursos] or ["Sin cursos"]
        combo_cur = ctk.CTkComboBox(f_row, values=curso_options, width=250)
        combo_cur.pack(side="left", padx=5)

        def _matricular():
            if not self.controller.estudiantes or not self.controller.cursos:
                return
            sel_e = combo_est.get()
            sel_c = combo_cur.get()

            cod_e = sel_e.split(" - ")[0]
            cod_c = sel_c.split(" - ")[0]

            est = self.controller.gestor_personas.buscar_estudiante_por_codigo(cod_e)
            curso = next((c for c in self.controller.cursos if c.codigoCurso == cod_c), None)

            if est and curso:
                mat = next((m for m in self.controller.matriculas if m.idEstudiante == est.idEstudiante), None)
                if not mat:
                    mat = MatriculaAcademica(
                        idMatricula=len(self.controller.matriculas) + 1,
                        idEstudiante=est.idEstudiante,
                        idPeriodo=1,
                        fechaMatricula=date.today(),
                        totalCreditos=curso.numeroCreditos,
                        promedioPeriodo=Decimal("0.0"),
                        estadoMatricula="ACTIVO",
                    )
                    self.controller.matriculas.append(mat)

                det = DetalleMatricula(
                    idDetalleMatricula=len(self.controller.detalles_matricula) + 1,
                    idMatricula=mat.idMatricula,
                    idOfertaCurso=curso.idCurso,
                    fechaInscripcion=date.today(),
                    estadoCurso=EstadoCurso.EN_CURSO,
                    notaFinal=Decimal("0.0"),
                )
                self.controller.detalles_matricula.append(det)
                self.controller._recrear_gestores()
                self.actualizar()

        btn_mat = ctk.CTkButton(f_row, text="✍️ Registrar Matrícula", font=ctk.CTkFont(size=12, weight="bold"), fg_color="#10B981", hover_color="#059669", corner_radius=8, command=_matricular)
        btn_mat.pack(side="left", padx=15)

        headers = ["ID Inscripción", "Estudiante", "Asignatura", "Nota Definitiva", "Estado Curso", "Acciones"]
        col_weights = [2, 4, 4, 2, 3, 3]
        col_mins = [100, 180, 180, 100, 110, 120]

        table = PITAGridTable(container, headers=headers, col_weights=col_weights, col_mins=col_mins)
        table.pack(fill="both", expand=True, padx=5, pady=5)

        if not self.controller.detalles_matricula:
            ctk.CTkLabel(table, text="No hay inscripciones registradas aún.", text_color="#94A3B8").pack(pady=20)
            return

        for det in self.controller.detalles_matricula:
            mat = next((m for m in self.controller.matriculas if m.idMatricula == det.idMatricula), None)
            est = next((e for e in self.controller.estudiantes if mat and e.idEstudiante == mat.idEstudiante), None)
            pers = next((p for p in self.controller.personas if est and p.idPersona == est.idPersona), None)
            curso = next((c for c in self.controller.cursos if c.idCurso == det.idOfertaCurso), None)

            nom_e = f"{pers.primerNombre} {pers.primerApellido}" if pers else "Estudiante"
            nom_c = curso.nombre if curso else "Curso"
            est_c = str(getattr(det, "estadoCurso", "EN_CURSO"))
            nota_f = float(getattr(det, "notaFinal", 0.0) or 0.0)

            badge_tuple = ("badge", est_c, "cancelado" if est_c == "CANCELADO" else "active")

            if est_c != "CANCELADO":
                btn_canc = ("button", "🚫 Cancelar Curso", lambda d_id=det.idDetalleMatricula: self._cancelar_curso_estudiante(d_id), "#EF4444", "#DC2626", 110, 28)
            else:
                btn_canc = ("Cancelada", "#64748B")

            color_nota = "#F87171" if nota_f < 3.0 else "#34D399"

            cells = [
                f"INS-{det.idDetalleMatricula}",
                (nom_e, "#F8FAFC"),
                (nom_c, "#38BDF8"),
                (f"{nota_f:.2f}", color_nota),
                badge_tuple,
                btn_canc,
            ]
            table.add_row_items(cells, is_highlighted=(est_c == "CANCELADO"))

    # ------------------------------------------------------------------
    # TAB EVALUACIONES Y CALIFICACIONES
    # ------------------------------------------------------------------
    def _llenar_tab_evaluaciones(self) -> None:
        container = ctk.CTkFrame(self.tab_evaluaciones, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=5, pady=5)

        form = ctk.CTkFrame(container, corner_radius=8)
        form.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(form, text="Registrar Evaluaciones y Calificaciones", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(10, 5))

        f_row = ctk.CTkFrame(form, fg_color="transparent")
        f_row.pack(fill="x", padx=15, pady=5)

        det_options = [
            f"ID-{d.idDetalleMatricula} | Detalle Inscripción ID: {d.idDetalleMatricula}"
            for d in self.controller.detalles_matricula
            if str(getattr(d, "estadoCurso", "")) != "CANCELADO"
        ] or ["Sin inscripciones activas"]

        combo_det = ctk.CTkComboBox(f_row, values=det_options, width=300)
        combo_det.pack(side="left", padx=5)

        entry_nota = ctk.CTkEntry(f_row, placeholder_text="Nota (0.0 - 5.0)", width=120)
        entry_nota.pack(side="left", padx=10)

        def _guardar_nota():
            if not self.controller.detalles_matricula:
                return
            try:
                val_nota = float(entry_nota.get().strip())
                if val_nota < 0.0 or val_nota > 5.0:
                    return
            except ValueError:
                return

            sel_det_str = combo_det.get()
            if "ID-" not in sel_det_str:
                return
            det_id = int(sel_det_str.split("ID-")[1].split(" |")[0])
            det = next((d for d in self.controller.detalles_matricula if d.idDetalleMatricula == det_id), None)

            if det:
                det.notaFinal = Decimal(str(round(val_nota, 2)))
                det.estadoCurso = EstadoCurso.APROBADO if val_nota >= 3.0 else EstadoCurso.REPROBADO

                mat = next((m for m in self.controller.matriculas if m.idMatricula == det.idMatricula), None)
                if mat:
                    est = next((e for e in self.controller.estudiantes if e.idEstudiante == mat.idEstudiante), None)
                    if est:
                        notas_est = [
                            float(d.notaFinal) for d in self.controller.detalles_matricula
                            if any(m.idMatricula == d.idMatricula and m.idEstudiante == est.idEstudiante for m in self.controller.matriculas)
                            and d.notaFinal is not None
                        ]
                        if notas_est:
                            prom = sum(notas_est) / len(notas_est)
                            est.promedioAcumulado = Decimal(str(round(prom, 2)))
                            if prom < 3.0:
                                est.estadoAcademico = EstadoAcademico.EBRA
                            else:
                                est.estadoAcademico = EstadoAcademico.ACTIVO

                self.controller._recrear_gestores()
                self.actualizar()

        btn_nota = ctk.CTkButton(f_row, text="💾 Registrar Nota Definitiva", fg_color="#006837", hover_color="#004D28", command=_guardar_nota)
        btn_nota.pack(side="left", padx=10)

    # ------------------------------------------------------------------
    # TAB ALERTAS EBRA
    # ------------------------------------------------------------------
    def _llenar_tab_ebra(self) -> None:
        scroll = ctk.CTkScrollableFrame(self.tab_ebra, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=5, pady=5)

        ctk.CTkLabel(
            scroll,
            text="🚨 Informe Consolidado de Estudiantes en EBRA",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#E53935",
        ).pack(anchor="w", pady=(5, 5))

        ebras = [
            e for e in self.controller.estudiantes
            if str(getattr(e, "estadoAcademico", "")) == "EBRA" or (e.promedioAcumulado and e.promedioAcumulado < Decimal("3.0"))
        ]

        if not ebras:
            ctk.CTkLabel(
                scroll,
                text="🎉 ¡Excelente! No hay estudiantes en estado de alerta EBRA en la institución.",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#43A047",
            ).pack(pady=30)
            return

        for est in ebras:
            card = ctk.CTkFrame(scroll, fg_color="#33181C", border_width=1, border_color="#E53935", corner_radius=8)
            card.pack(fill="x", pady=6, padx=5)

            pers = next((p for p in self.controller.personas if p.idPersona == est.idPersona), None)
            nom = f"{pers.primerNombre} {pers.primerApellido}" if pers else "Estudiante"

            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=12, pady=8)

            ctk.CTkLabel(top, text=f"Estudiante: {nom} ({est.codigoEstudiante})", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left")
            ctk.CTkLabel(top, text="⚠️ RIESGO ACADÉMICO CRÍTICO", font=ctk.CTkFont(size=11, weight="bold"), text_color="#E53935").pack(side="right")

            bot = ctk.CTkFrame(card, fg_color="transparent")
            bot.pack(fill="x", padx=12, pady=(0, 8))

            ctk.CTkLabel(bot, text=f"Promedio Acumulado Actual: {est.promedioAcumulado} / 5.0", font=ctk.CTkFont(size=12, weight="bold"), text_color="#FF8A80").pack(side="left")
            ctk.CTkLabel(bot, text="Acción: Notificar a Tutoría y Registro Académico", font=ctk.CTkFont(size=11), text_color="gray").pack(side="right")

    def _abrir_modal_nuevo_curso(self) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title("➕ Crear Nuevo Curso")
        dialog.geometry("450x500")
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Crear Asignatura Académica", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        entry_cod = ctk.CTkEntry(dialog, placeholder_text="Código del Curso (ej: INF-201)")
        entry_cod.pack(fill="x", padx=20, pady=5)

        entry_nom = ctk.CTkEntry(dialog, placeholder_text="Nombre de la Asignatura")
        entry_nom.pack(fill="x", padx=20, pady=5)

        entry_cred = ctk.CTkEntry(dialog, placeholder_text="Número de Créditos (ej: 3)")
        entry_cred.pack(fill="x", padx=20, pady=5)

        def _guardar():
            cod = entry_cod.get().strip()
            nom = entry_nom.get().strip()
            cred = entry_cred.get().strip()

            if cod and nom:
                c = Curso(
                    idCurso=len(self.controller.cursos) + 1,
                    codigoCurso=cod,
                    nombre=nom,
                    descripcion="Asignatura institucional PITA",
                    numeroCreditos=int(cred) if cred.isdigit() else 3,
                    horasTeoricas=3,
                    horasPracticas=2,
                    horasTrabajoIndependiente=4,
                    cupoSugerido=30,
                    notaMinimaAprobatoria="3.0",
                    estado="ACTIVO",
                )
                self.controller.cursos.append(c)
                self.controller._recrear_gestores()
                dialog.destroy()
                self.actualizar()

        ctk.CTkButton(dialog, text="💾 Crear Curso", fg_color="#006837", hover_color="#004D28", command=_guardar).pack(pady=20)

    def _editar_curso(self, curso: Curso) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"✏️ Editar Curso {curso.codigoCurso}")
        dialog.geometry("450x450")
        dialog.grab_set()

        ctk.CTkLabel(dialog, text=f"Modificar Curso: {curso.nombre}", font=ctk.CTkFont(size=15, weight="bold")).pack(pady=12)

        entry_nom = ctk.CTkEntry(dialog)
        entry_nom.insert(0, curso.nombre)
        entry_nom.pack(fill="x", padx=20, pady=6)

        entry_cred = ctk.CTkEntry(dialog)
        entry_cred.insert(0, str(curso.numeroCreditos))
        entry_cred.pack(fill="x", padx=20, pady=6)

        entry_nota = ctk.CTkEntry(dialog)
        entry_nota.insert(0, str(curso.notaMinimaAprobatoria))
        entry_nota.pack(fill="x", padx=20, pady=6)

        def _guardar():
            curso.nombre = entry_nom.get().strip() or curso.nombre
            if entry_cred.get().strip().isdigit():
                curso.numeroCreditos = int(entry_cred.get().strip())
            curso.notaMinimaAprobatoria = entry_nota.get().strip() or curso.notaMinimaAprobatoria
            self.controller._recrear_gestores()
            dialog.destroy()
            self.actualizar()

        ctk.CTkButton(dialog, text="💾 Guardar Cambios", font=ctk.CTkFont(size=12, weight="bold"), fg_color="#10B981", hover_color="#059669", height=36, command=_guardar).pack(pady=20)

    def _eliminar_curso(self, id_curso: int) -> None:
        self.controller.cursos = [c for c in self.controller.cursos if c.idCurso != id_curso]
        self.controller._recrear_gestores()
        self.actualizar()

    def _cancelar_curso_estudiante(self, id_detalle: int) -> None:
        det = next((d for d in self.controller.detalles_matricula if d.idDetalleMatricula == id_detalle), None)
        if det:
            det.estadoCurso = EstadoCurso.CANCELADO
            det.fechaCancelacion = date.today()
            det.motivoCancelacion = "Cancelación a solicitud del estudiante"
            self.controller._recrear_gestores()
            self.actualizar()

    def actualizar(self) -> None:
        for widget in self.winfo_children():
            widget.destroy()
        self._crear_interfaz()
