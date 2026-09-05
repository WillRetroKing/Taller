"""Vista de Gestión Académica (Cursos, Ofertas, Matrículas, Calificaciones y Alertas EBRA)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
import customtkinter as ctk
from typing import TYPE_CHECKING

from ui_gui.theme import Colors, Fonts, create_styled_tabview
from ui_gui.components import PITAGridTable, create_badge
from modelo_datos import (
    AsignacionDocente,
    Calificacion,
    Curso,
    DetalleMatricula,
    EstadoAcademico,
    EstadoCurso,
    Evaluacion,
    Facultad,
    Horario,
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

        btn_box = ctk.CTkFrame(header, fg_color="transparent")
        btn_box.pack(side="right")

        btn_nueva_oferta = ctk.CTkButton(
            btn_box,
            text="🏫 Abrir Oferta / Grupo",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#059669",
            hover_color="#047857",
            corner_radius=8,
            command=self._abrir_modal_nueva_oferta,
        )
        btn_nueva_oferta.pack(side="right", padx=(8, 0))

        btn_nuevo_curso = ctk.CTkButton(
            btn_box,
            text="➕ Crear Asignatura",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#0067C0",
            hover_color="#005FB8",
            corner_radius=8,
            command=self._abrir_modal_nuevo_curso,
        )
        btn_nuevo_curso.pack(side="right")

        # Pestañas Principales
        self.tabview = create_styled_tabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=5)

        self.tab_oferta = self.tabview.add("📚 Cursos & Ofertas")
        self.tab_matricula = self.tabview.add("✍️ Matrícula de Cursos")
        self.tab_evaluaciones = self.tabview.add("📝 Evaluaciones y Notas")
        self.tab_ebra = self.tabview.add("⚠️ Informe Alertas EBRA")

        self._llenar_tab_oferta()
        self._llenar_tab_matricula()
        self._llenar_tab_evaluaciones()
        self._llenar_tab_ebra()

    # ------------------------------------------------------------------
    # TAB 1: CURSOS Y OFERTA ACADÉMICA
    # ------------------------------------------------------------------
    def _llenar_tab_oferta(self) -> None:
        for w in self.tab_oferta.winfo_children():
            w.destroy()

        sub_tabview = create_styled_tabview(self.tab_oferta)
        sub_tabview.pack(fill="both", expand=True, padx=5, pady=5)

        sub_tab_cursos = sub_tabview.add("📖 Catálogo de Asignaturas")
        sub_tab_ofertas = sub_tabview.add("🏫 Ofertas y Grupos Abiertos")

        # 1. Catálogo de Asignaturas
        headers_c = ["Código Curso", "Nombre Asignatura", "Créditos", "Horas T / P", "Nota Mínima", "Cupo Sugerido", "Acciones"]
        col_w_c = [2, 4, 1, 2, 1, 1, 2]
        col_m_c = [80, 160, 60, 90, 70, 70, 80]

        table_c = PITAGridTable(sub_tab_cursos, headers=headers_c, col_weights=col_w_c, col_mins=col_m_c)
        table_c.pack(fill="both", expand=True, padx=5, pady=5)

        if not self.controller.cursos:
            ctk.CTkLabel(table_c, text="No hay asignaturas en el catálogo.", text_color="#94A3B8").pack(pady=30)
        else:
            for c in self.controller.cursos:
                act_spec = (
                    "actions",
                    [
                        ("✏️ Editar", lambda cur=c: self._editar_curso(cur), "#334155", "#475569"),
                        ("❌ Eliminar", lambda c_id=c.idCurso: self._eliminar_curso(c_id), "#EF4444", "#DC2626"),
                    ],
                )
                cells = [
                    (getattr(c, "codigoCurso", "N/A"), "#38BDF8"),
                    (getattr(c, "nombre", "N/A"), "#F8FAFC"),
                    f"{getattr(c, 'numeroCreditos', 3)} créditos",
                    f"{getattr(c, 'horasTeoricas', 3)}h T / {getattr(c, 'horasPracticas', 2)}h P",
                    str(getattr(c, "notaMinimaAprobatoria", "3.0")),
                    str(getattr(c, "cupoSugerido", 30)),
                    act_spec,
                ]
                table_c.add_row_items(cells)

        # 2. Ofertas de Cursos (Grupos)
        headers_o = ["Código Oferta", "Asignatura", "Periodo", "Grupo", "Aula / Sede", "Cupo Disp / Total", "Docente Asignado", "Acciones"]
        col_w_o = [2, 3, 2, 1, 2, 2, 3, 1]
        col_m_o = [80, 130, 70, 60, 100, 90, 120, 70]

        table_o = PITAGridTable(sub_tab_ofertas, headers=headers_o, col_weights=col_w_o, col_mins=col_m_o)
        table_o.pack(fill="both", expand=True, padx=5, pady=5)

        if not self.controller.ofertas:
            ctk.CTkLabel(table_o, text="No hay ofertas ni grupos abiertos para este periodo.", text_color="#94A3B8").pack(pady=30)
        else:
            for of in self.controller.ofertas:
                curso = next((c for c in self.controller.cursos if c.idCurso == of.idCurso), None)
                nom_curso = curso.nombre if curso else f"Curso #{of.idCurso}"

                periodo = next((p for p in self.controller.periodos_academicos if p.idPeriodo == of.idPeriodo), None)
                nom_per = periodo.codigo if periodo else f"Per #{of.idPeriodo}"

                asig = next((a for a in self.controller.asignaciones if a.idOfertaCurso == of.idOfertaCurso and a.estado != "INACTIVO"), None)
                prof = next((p for p in self.controller.profesores if asig and p.idProfesor == asig.idProfesor), None)
                pers_prof = next((pe for pe in self.controller.personas if prof and pe.idPersona == prof.idPersona), None)

                nom_prof = f"{pers_prof.primerNombre} {pers_prof.primerApellido}" if pers_prof else "Sin asignar"

                act_o = (
                    "actions",
                    [
                        ("❌ Cerrar", lambda of_id=of.idOfertaCurso: self._eliminar_oferta(of_id), "#EF4444", "#DC2626"),
                    ],
                )

                cupo_str = f"{of.cupoDisponible or 0} / {of.cupoMaximo or 35}"
                cupo_color = "#34D399" if (of.cupoDisponible or 0) > 5 else ("#F59E0B" if (of.cupoDisponible or 0) > 0 else "#EF4444")

                cells_o = [
                    (f"OFER-{of.idOfertaCurso}", "#A78BFA"),
                    (nom_curso, "#F8FAFC"),
                    nom_per,
                    f"Gr. {of.grupo or '01'}",
                    f"{of.aula or 'Aula'} ({of.sede or 'Sede'})",
                    (cupo_str, cupo_color),
                    (nom_prof, "#38BDF8"),
                    act_o,
                ]
                table_o.add_row_items(cells_o)

    # ------------------------------------------------------------------
    # TAB 2: MATRÍCULA ACADÉMICA
    # ------------------------------------------------------------------
    def _llenar_tab_matricula(self) -> None:
        container = ctk.CTkFrame(self.tab_matricula, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=5, pady=5)

        form = ctk.CTkFrame(container, fg_color=Colors.BG_CARD, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
        form.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(form, text="✍️ Registrar Matrícula en Oferta Académica", font=ctk.CTkFont(size=14, weight="bold"), text_color="#38BDF8").pack(anchor="w", padx=15, pady=(10, 5))

        f_row = ctk.CTkFrame(form, fg_color="transparent")
        f_row.pack(fill="x", padx=15, pady=5)

        # Opciones de estudiantes
        estud_options = [
            f"{e.codigoEstudiante} - {next((p.primerNombre + ' ' + p.primerApellido for p in self.controller.personas if p.idPersona == e.idPersona), 'Estudiante')}"
            for e in self.controller.estudiantes
            if e.estado != "INACTIVO"
        ] or ["Sin estudiantes disponibles"]

        ctk.CTkLabel(f_row, text="Estudiante:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(side="left", padx=(0, 5))
        combo_est = ctk.CTkComboBox(f_row, values=estud_options, width=270)
        combo_est.pack(side="left", padx=5)

        # Opciones de ofertas disponibles
        oferta_options = []
        for of in self.controller.ofertas:
            c = next((cur for cur in self.controller.cursos if cur.idCurso == of.idCurso), None)
            nom_c = c.nombre if c else f"Curso #{of.idCurso}"
            oferta_options.append(f"OFER-{of.idOfertaCurso} | {nom_c} (Gr. {of.grupo}) - Cupo: {of.cupoDisponible}/{of.cupoMaximo}")
        if not oferta_options:
            oferta_options = ["Sin ofertas de curso abiertas"]

        ctk.CTkLabel(f_row, text="Oferta / Asignatura:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(side="left", padx=(12, 5))
        combo_oferta = ctk.CTkComboBox(f_row, values=oferta_options, width=320)
        combo_oferta.pack(side="left", padx=5)

        lbl_msg = ctk.CTkLabel(form, text="", font=ctk.CTkFont(size=11, weight="bold"))
        lbl_msg.pack(anchor="w", padx=15, pady=(2, 4))

        def _matricular():
            sel_e = combo_est.get()
            sel_o = combo_oferta.get()

            if "Sin estudiantes" in sel_e or "Sin ofertas" in sel_o:
                lbl_msg.configure(text="⚠️ Seleccione un estudiante y una oferta válidos.", text_color="#EF4444")
                return

            cod_e = sel_e.split(" - ")[0].strip()
            est = next((e for e in self.controller.estudiantes if getattr(e, "codigoEstudiante", "") == cod_e), None)

            id_of_str = sel_o.split(" | ")[0].replace("OFER-", "").strip()
            oferta = next((o for o in self.controller.ofertas if str(o.idOfertaCurso) == id_of_str), None)

            if not est or not oferta:
                lbl_msg.configure(text="⚠️ Estudiante u oferta no encontrados.", text_color="#EF4444")
                return

            curso = next((c for c in self.controller.cursos if c.idCurso == oferta.idCurso), None)
            if not curso:
                lbl_msg.configure(text="⚠️ Asignatura asociada a la oferta no encontrada.", text_color="#EF4444")
                return

            # Validar cupo
            if (oferta.cupoDisponible or 0) <= 0:
                lbl_msg.configure(text=f"⚠️ No hay cupos disponibles en la oferta {oferta.idOfertaCurso} (Cupo 0).", text_color="#EF4444")
                return

            # Validar si ya está matriculado en este grupo o curso activo
            ya_inscrito = any(
                d.idOfertaCurso == oferta.idOfertaCurso and str(getattr(d, "estadoCurso", "")) != "CANCELADO"
                and any(m.idMatricula == d.idMatricula and m.idEstudiante == est.idEstudiante for m in self.controller.matriculas)
                for d in self.controller.detalles_matricula
            )
            if ya_inscrito:
                lbl_msg.configure(text=f"⚠️ El estudiante {cod_e} ya se encuentra matriculado en este curso/grupo.", text_color="#EF4444")
                return

            # Validar límite de créditos
            creditos_actuales = sum(
                (next((c.numeroCreditos for c in self.controller.cursos if c.idCurso == of.idCurso), 0) or 0)
                for d in self.controller.detalles_matricula
                if str(getattr(d, "estadoCurso", "")) != "CANCELADO"
                and any(m.idMatricula == d.idMatricula and m.idEstudiante == est.idEstudiante for m in self.controller.matriculas)
                for of in self.controller.ofertas if of.idOfertaCurso == d.idOfertaCurso
            )
            max_creditos = 20
            if hasattr(self.controller, "gestor_parametros") and self.controller.gestor_parametros:
                param = self.controller.gestor_parametros.obtener_parametro("MAXIMO_CREDITOS_PERIODO")
                if param and param.valor:
                    try:
                        max_creditos = int(param.valor)
                    except ValueError:
                        pass

            nuevo_cred = curso.numeroCreditos or 3
            if creditos_actuales + nuevo_cred > max_creditos:
                lbl_msg.configure(text=f"⚠️ Excede límite de créditos ({creditos_actuales} + {nuevo_cred} > {max_creditos} créditos máx).", text_color="#EF4444")
                return

            # Obtener o crear Matrícula para el periodo
            id_per = oferta.idPeriodo or 1
            mat = next((m for m in self.controller.matriculas if m.idEstudiante == est.idEstudiante and m.idPeriodo == id_per), None)
            if not mat:
                new_id_m = max((m.idMatricula or 0 for m in self.controller.matriculas), default=0) + 1
                mat = MatriculaAcademica(
                    idMatricula=new_id_m,
                    idEstudiante=est.idEstudiante,
                    idPeriodo=id_per,
                    fechaMatricula=date.today(),
                    totalCreditos=nuevo_cred,
                    promedioPeriodo=Decimal("0.0"),
                    estadoMatricula="ACTIVO",
                )
                self.controller.matriculas.append(mat)
            else:
                mat.totalCreditos = (mat.totalCreditos or 0) + nuevo_cred

            # Crear DetalleMatricula
            new_id_d = max((d.idDetalleMatricula or 0 for d in self.controller.detalles_matricula), default=0) + 1
            det = DetalleMatricula(
                idDetalleMatricula=new_id_d,
                idMatricula=mat.idMatricula,
                idOfertaCurso=oferta.idOfertaCurso,
                fechaInscripcion=date.today(),
                estadoCurso=EstadoCurso.EN_CURSO,
                notaFinal=None,
            )
            self.controller.detalles_matricula.append(det)

            # Descontar cupo
            oferta.cupoDisponible = max(0, (oferta.cupoDisponible or 1) - 1)

            self.controller._recrear_gestores()
            lbl_msg.configure(text=f"✅ Matrícula exitosa para {est.codigoEstudiante} en {curso.nombre} (Gr. {oferta.grupo}).", text_color="#10B981")
            self.actualizar()

        btn_mat = ctk.CTkButton(f_row, text="✍️ Matricular Estudiante", font=ctk.CTkFont(size=12, weight="bold"), fg_color="#10B981", hover_color="#059669", corner_radius=8, command=_matricular)
        btn_mat.pack(side="left", padx=15)

        # Tabla de Inscripciones
        headers = ["ID Inscripción", "Estudiante", "Asignatura & Grupo", "Créditos", "Estado Curso", "Nota Definitiva", "Acciones"]
        col_weights = [2, 3, 3, 1, 2, 2, 2]
        col_mins = [90, 150, 150, 70, 90, 90, 100]

        table = PITAGridTable(container, headers=headers, col_weights=col_weights, col_mins=col_mins)
        table.pack(fill="both", expand=True, padx=5, pady=5)

        if not self.controller.detalles_matricula:
            ctk.CTkLabel(table, text="No hay inscripciones registradas aún.", text_color="#94A3B8").pack(pady=20)
            return

        for det in self.controller.detalles_matricula:
            mat = next((m for m in self.controller.matriculas if m.idMatricula == det.idMatricula), None)
            est = next((e for e in self.controller.estudiantes if mat and e.idEstudiante == mat.idEstudiante), None)
            pers = next((p for p in self.controller.personas if est and p.idPersona == est.idPersona), None)

            oferta = next((o for o in self.controller.ofertas if o.idOfertaCurso == det.idOfertaCurso), None)
            curso = next((c for c in self.controller.cursos if oferta and c.idCurso == oferta.idCurso), None)
            if not curso:
                curso = next((c for c in self.controller.cursos if c.idCurso == det.idOfertaCurso), None)

            nom_e = f"{pers.primerNombre} {pers.primerApellido} ({est.codigoEstudiante})" if pers and est else "Estudiante"
            nom_c = f"{curso.nombre} (Gr. {oferta.grupo if oferta else '01'})" if curso else "Curso"
            cred_c = f"{curso.numeroCreditos or 3} cr." if curso else "3 cr."

            est_c = str(getattr(det, "estadoCurso", "EN_CURSO"))
            nota_f = getattr(det, "notaFinal", None)
            nota_str = f"{float(nota_f):.2f}" if nota_f is not None else "Sin nota"
            color_nota = "#F87171" if (nota_f is not None and float(nota_f) < 3.0) else ("#34D399" if nota_f is not None else "#94A3B8")

            badge_tuple = ("badge", est_c, "cancelado" if est_c == "CANCELADO" else ("active" if est_c == "APROBADO" else "ebra"))

            if est_c != "CANCELADO":
                btn_canc = ("button", "🚫 Cancelar", lambda d_id=det.idDetalleMatricula: self._cancelar_curso_estudiante(d_id), "#EF4444", "#DC2626", 90, 28)
            else:
                btn_canc = ("Cancelada", "#64748B")

            cells = [
                f"INS-{det.idDetalleMatricula}",
                (nom_e, "#F8FAFC"),
                (nom_c, "#38BDF8"),
                cred_c,
                badge_tuple,
                (nota_str, color_nota),
                btn_canc,
            ]
            table.add_row_items(cells, is_highlighted=(est_c == "CANCELADO"))

    # ------------------------------------------------------------------
    # TAB 3: EVALUACIONES Y NOTAS
    # ------------------------------------------------------------------
    def _llenar_tab_evaluaciones(self) -> None:
        container = ctk.CTkFrame(self.tab_evaluaciones, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=5, pady=5)

        form = ctk.CTkFrame(container, fg_color=Colors.BG_CARD, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
        form.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(form, text="📝 Asignación de Calificaciones y Evaluaciones", font=ctk.CTkFont(size=14, weight="bold"), text_color="#34D399").pack(anchor="w", padx=15, pady=(10, 5))

        f_row = ctk.CTkFrame(form, fg_color="transparent")
        f_row.pack(fill="x", padx=15, pady=5)

        # Opciones legibles de inscripciones activas
        det_options = []
        for d in self.controller.detalles_matricula:
            if str(getattr(d, "estadoCurso", "")) == "CANCELADO":
                continue
            mat = next((m for m in self.controller.matriculas if m.idMatricula == d.idMatricula), None)
            est = next((e for e in self.controller.estudiantes if mat and e.idEstudiante == mat.idEstudiante), None)
            pers = next((p for p in self.controller.personas if est and p.idPersona == est.idPersona), None)

            of = next((o for o in self.controller.ofertas if o.idOfertaCurso == d.idOfertaCurso), None)
            c = next((cur for cur in self.controller.cursos if of and cur.idCurso == of.idCurso), None)
            if not c:
                c = next((cur for cur in self.controller.cursos if cur.idCurso == d.idOfertaCurso), None)

            est_cod = est.codigoEstudiante if est else "EST"
            nom_p = f"{pers.primerNombre} {pers.primerApellido}" if pers else "Estudiante"
            nom_c = c.nombre if c else "Asignatura"
            gr = of.grupo if of else "01"
            nota_actual = f"Nota: {d.notaFinal}" if d.notaFinal is not None else "Sin nota"

            det_options.append(f"INS-{d.idDetalleMatricula} | {est_cod} - {nom_p} — {nom_c} (Gr. {gr}) [{nota_actual}]")

        if not det_options:
            det_options = ["Sin inscripciones activas"]

        ctk.CTkLabel(f_row, text="Inscripción Estudiante:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(side="left", padx=(0, 5))
        combo_det = ctk.CTkComboBox(f_row, values=det_options, width=420)
        combo_det.pack(side="left", padx=5)

        ctk.CTkLabel(f_row, text="Nota Definitiva (0.0 - 5.0):", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(side="left", padx=(10, 5))
        entry_nota = ctk.CTkEntry(f_row, placeholder_text="ej: 4.2", width=90)
        entry_nota.pack(side="left", padx=5)

        lbl_msg_nota = ctk.CTkLabel(form, text="", font=ctk.CTkFont(size=11, weight="bold"))
        lbl_msg_nota.pack(anchor="w", padx=15, pady=(2, 4))

        def _guardar_nota():
            sel = combo_det.get()
            if "Sin inscripciones" in sel or not sel.startswith("INS-"):
                lbl_msg_nota.configure(text="⚠️ Seleccione una inscripción válida.", text_color="#EF4444")
                return

            try:
                val_nota = float(entry_nota.get().strip())
                if val_nota < 0.0 or val_nota > 5.0:
                    lbl_msg_nota.configure(text="⚠️ La calificación debe encontrarse entre 0.0 y 5.0.", text_color="#EF4444")
                    return
            except ValueError:
                lbl_msg_nota.configure(text="⚠️ Ingrese un valor numérico válido (ej: 3.5).", text_color="#EF4444")
                return

            det_id = int(sel.split("INS-")[1].split(" |")[0])
            det = next((d for d in self.controller.detalles_matricula if d.idDetalleMatricula == det_id), None)

            if det:
                nota_dec = Decimal(str(round(val_nota, 2)))
                det.notaFinal = nota_dec
                det.estadoCurso = EstadoCurso.APROBADO if val_nota >= 3.0 else EstadoCurso.REPROBADO

                # Recalcular promedio de notas del estudiante
                mat = next((m for m in self.controller.matriculas if m.idMatricula == det.idMatricula), None)
                if mat:
                    est = next((e for e in self.controller.estudiantes if e.idEstudiante == mat.idEstudiante), None)
                    if est:
                        notas_est = [
                            float(d.notaFinal) for d in self.controller.detalles_matricula
                            if str(getattr(d, "estadoCurso", "")) != "CANCELADO"
                            and d.notaFinal is not None
                            and any(m.idMatricula == d.idMatricula and m.idEstudiante == est.idEstudiante for m in self.controller.matriculas)
                        ]
                        if notas_est:
                            prom = round(sum(notas_est) / len(notas_est), 2)
                            est.promedioAcumulado = Decimal(str(prom))
                            if prom < 3.0:
                                est.estadoAcademico = EstadoAcademico.EBRA
                            else:
                                est.estadoAcademico = EstadoAcademico.ACTIVO

                self.controller._recrear_gestores()
                lbl_msg_nota.configure(text=f"✅ Calificación de {val_nota:.2f} registrada exitosamente.", text_color="#10B981")
                self.actualizar()

        btn_nota = ctk.CTkButton(f_row, text="💾 Registrar Nota", font=ctk.CTkFont(size=12, weight="bold"), fg_color="#0067C0", hover_color="#005FB8", command=_guardar_nota)
        btn_nota.pack(side="left", padx=10)

        # Tabla de Calificaciones
        headers_n = ["ID Inscripción", "Estudiante", "Asignatura", "Nota Definitiva", "Estado Calificación", "Impacto EBRA"]
        col_w_n = [2, 3, 3, 2, 2, 2]
        col_m_n = [90, 150, 150, 90, 100, 100]

        table_n = PITAGridTable(container, headers=headers_n, col_weights=col_w_n, col_mins=col_m_n)
        table_n.pack(fill="both", expand=True, padx=5, pady=5)

        if not self.controller.detalles_matricula:
            ctk.CTkLabel(table_n, text="No hay registros de calificaciones.", text_color="#94A3B8").pack(pady=20)
            return

        for det in self.controller.detalles_matricula:
            if str(getattr(det, "estadoCurso", "")) == "CANCELADO":
                continue
            mat = next((m for m in self.controller.matriculas if m.idMatricula == det.idMatricula), None)
            est = next((e for e in self.controller.estudiantes if mat and e.idEstudiante == mat.idEstudiante), None)
            pers = next((p for p in self.controller.personas if est and p.idPersona == est.idPersona), None)

            oferta = next((o for o in self.controller.ofertas if o.idOfertaCurso == det.idOfertaCurso), None)
            curso = next((c for c in self.controller.cursos if oferta and c.idCurso == oferta.idCurso), None)
            if not curso:
                curso = next((c for c in self.controller.cursos if c.idCurso == det.idOfertaCurso), None)

            nom_e = f"{pers.primerNombre} {pers.primerApellido}" if pers else "Estudiante"
            nom_c = curso.nombre if curso else "Curso"

            nota_f = getattr(det, "notaFinal", None)
            nota_str = f"{float(nota_f):.2f}" if nota_f is not None else "Sin calificar"
            color_nota = "#F87171" if (nota_f is not None and float(nota_f) < 3.0) else ("#34D399" if nota_f is not None else "#94A3B8")

            est_c = str(getattr(det, "estadoCurso", "EN_CURSO"))
            badge_tuple = ("badge", est_c, "active" if est_c == "APROBADO" else ("ebra" if est_c == "REPROBADO" else "en_curso"))

            prom_est = float(getattr(est, "promedioAcumulado", 0.0) or 0.0) if est else 0.0
            if prom_est < 3.0 and prom_est > 0:
                ebra_badge = ("badge", f"⚠️ EBRA ({prom_est:.2f})", "ebra")
            else:
                ebra_badge = ("badge", f"● Normal ({prom_est:.2f})", "active")

            cells = [
                f"INS-{det.idDetalleMatricula}",
                (f"{nom_e} ({getattr(est, 'codigoEstudiante', '')})", "#F8FAFC"),
                (nom_c, "#38BDF8"),
                (nota_str, color_nota),
                badge_tuple,
                ebra_badge,
            ]
            table_n.add_row_items(cells, is_highlighted=(nota_f is not None and float(nota_f) < 3.0))

    # ------------------------------------------------------------------
    # TAB 4: TABLERO EBRA CON KPIS
    # ------------------------------------------------------------------
    def _llenar_tab_ebra(self) -> None:
        scroll = ctk.CTkScrollableFrame(self.tab_ebra, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=5, pady=5)

        ctk.CTkLabel(
            scroll,
            text="🚨 Tablero de Monitoreo y Alertas Académicas EBRA",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color="#F8FAFC",
        ).pack(anchor="w", pady=(5, 5))

        # KPI CARDS
        total_est = len(self.controller.estudiantes)
        ebras = [
            e for e in self.controller.estudiantes
            if str(getattr(e, "estadoAcademico", "")) == "EBRA" or (e.promedioAcumulado and float(e.promedioAcumulado) < 3.0 and float(e.promedioAcumulado) > 0)
        ]
        total_ebras = len(ebras)
        normales = total_est - total_ebras

        promedios = [float(e.promedioAcumulado) for e in self.controller.estudiantes if e.promedioAcumulado is not None and float(e.promedioAcumulado) > 0]
        prom_global = (sum(promedios) / len(promedios)) if promedios else 0.0

        kpi_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        kpi_frame.pack(fill="x", pady=(5, 15))
        kpi_frame.columnconfigure(0, weight=1)
        kpi_frame.columnconfigure(1, weight=1)
        kpi_frame.columnconfigure(2, weight=1)
        kpi_frame.columnconfigure(3, weight=1)

        kpis = [
            ("👥 Total Estudiantes", str(total_est), "#38BDF8", "Estudiantes inscritos"),
            ("🟢 Normalidad Académica", str(normales), "#34D399", f"{(normales/max(1, total_est))*100:.1f}% del total"),
            ("🚨 En Riesgo EBRA", str(total_ebras), "#EF4444", f"{(total_ebras/max(1, total_est))*100:.1f}% en riesgo crítico"),
            ("📊 Promedio General", f"{prom_global:.2f} / 5.0", "#F59E0B", "Promedio institucional"),
        ]

        for i, (titulo, val, color, subtitulo) in enumerate(kpis):
            card = ctk.CTkFrame(kpi_frame, fg_color=Colors.BG_CARD, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
            card.grid(row=0, column=i, padx=5, sticky="ew")

            ctk.CTkLabel(card, text=titulo, font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(anchor="w", padx=12, pady=(10, 2))
            ctk.CTkLabel(card, text=val, font=ctk.CTkFont(size=20, weight="bold"), text_color=color).pack(anchor="w", padx=12, pady=(0, 2))
            ctk.CTkLabel(card, text=subtitulo, font=ctk.CTkFont(size=10), text_color="#64748B").pack(anchor="w", padx=12, pady=(0, 10))

        if not ebras:
            no_ebra_card = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD, corner_radius=8, border_width=1, border_color="#10B981")
            no_ebra_card.pack(fill="x", padx=5, pady=20)
            ctk.CTkLabel(
                no_ebra_card,
                text="🎉 ¡Excelente! No se registran estudiantes en condición de Bajo Rendimiento Académico (EBRA).",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#34D399",
            ).pack(pady=25)
            return

        for est in ebras:
            card = ctk.CTkFrame(scroll, fg_color="#2A1417", border_width=1, border_color="#EF4444", corner_radius=8)
            card.pack(fill="x", pady=6, padx=5)

            pers = next((p for p in self.controller.personas if p.idPersona == est.idPersona), None)
            nom = f"{pers.primerNombre} {pers.primerApellido}" if pers else "Estudiante"
            doc = f"{pers.tipoDocumento} {pers.numeroDocumento}" if pers else "N/A"

            prog = next((pr.nombre for pr in self.controller.programas if pr.idPrograma == est.idPrograma), f"Prog #{est.idPrograma}")

            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=15, pady=(10, 4))

            ctk.CTkLabel(top, text=f"👨‍🎓 {nom} ({est.codigoEstudiante}) — Doc: {doc}", font=ctk.CTkFont(size=13, weight="bold"), text_color="#F8FAFC").pack(side="left")
            ctk.CTkLabel(top, text="⚠️ CONDICIÓN EBRA ACTIVA", font=ctk.CTkFont(size=11, weight="bold"), text_color="#EF4444").pack(side="right")

            bot = ctk.CTkFrame(card, fg_color="transparent")
            bot.pack(fill="x", padx=15, pady=(0, 10))

            ctk.CTkLabel(bot, text=f"Programa: {prog} | Semestre: {est.semestreActual} | Promedio: {est.promedioAcumulado} / 5.0", font=ctk.CTkFont(size=11), text_color="#FCA5A5").pack(side="left")
            ctk.CTkLabel(bot, text="📌 Acción: Remitir a Tutoría y Plan de Acompañamiento Académico", font=ctk.CTkFont(size=11, weight="bold"), text_color="#FBBF24").pack(side="right")

    # ------------------------------------------------------------------
    # MODAL 1: CREAR CURSO
    # ------------------------------------------------------------------
    def _abrir_modal_nuevo_curso(self) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title("➕ Crear Nueva Asignatura")
        dialog.geometry("500x560")
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Crear Asignatura en el Catálogo", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 5))
        ctk.CTkLabel(dialog, text="Defina los parámetros base de la asignatura académica.", font=ctk.CTkFont(size=11), text_color="#94A3B8").pack(pady=(0, 15))

        entry_cod = ctk.CTkEntry(dialog, placeholder_text="Código del Curso (ej: INF-201)")
        entry_cod.pack(fill="x", padx=25, pady=6)

        entry_nom = ctk.CTkEntry(dialog, placeholder_text="Nombre de la Asignatura")
        entry_nom.pack(fill="x", padx=25, pady=6)

        entry_cred = ctk.CTkEntry(dialog, placeholder_text="Número de Créditos (ej: 3)")
        entry_cred.insert(0, "3")
        entry_cred.pack(fill="x", padx=25, pady=6)

        entry_ht = ctk.CTkEntry(dialog, placeholder_text="Horas Teóricas Semanales (ej: 3)")
        entry_ht.insert(0, "3")
        entry_ht.pack(fill="x", padx=25, pady=6)

        entry_hp = ctk.CTkEntry(dialog, placeholder_text="Horas Prácticas Semanales (ej: 2)")
        entry_hp.insert(0, "2")
        entry_hp.pack(fill="x", padx=25, pady=6)

        entry_cupo = ctk.CTkEntry(dialog, placeholder_text="Cupo Sugerido (ej: 30)")
        entry_cupo.insert(0, "30")
        entry_cupo.pack(fill="x", padx=25, pady=6)

        def _guardar():
            cod = entry_cod.get().strip()
            nom = entry_nom.get().strip()
            cred = entry_cred.get().strip()
            ht = entry_ht.get().strip()
            hp = entry_hp.get().strip()
            cupo = entry_cupo.get().strip()

            if cod and nom:
                c = Curso(
                    idCurso=len(self.controller.cursos) + 1,
                    codigoCurso=cod,
                    nombre=nom,
                    descripcion="Asignatura institucional PITA",
                    numeroCreditos=int(cred) if cred.isdigit() else 3,
                    horasTeoricas=int(ht) if ht.isdigit() else 3,
                    horasPracticas=int(hp) if hp.isdigit() else 2,
                    horasTrabajoIndependiente=4,
                    cupoSugerido=int(cupo) if cupo.isdigit() else 30,
                    notaMinimaAprobatoria=Decimal("3.0"),
                    estado="ACTIVO",
                )
                self.controller.cursos.append(c)
                self.controller._recrear_gestores()
                dialog.destroy()
                self.actualizar()

        ctk.CTkButton(dialog, text="💾 Guardar Asignatura", font=ctk.CTkFont(size=12, weight="bold"), fg_color="#0067C0", hover_color="#005FB8", height=38, command=_guardar).pack(pady=20)

    # ------------------------------------------------------------------
    # MODAL 2: ABRIR OFERTA / GRUPO
    # ------------------------------------------------------------------
    def _abrir_modal_nueva_oferta(self) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title("🏫 Abrir Oferta de Asignatura (Grupo)")
        dialog.geometry("520x620")
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Abrir Oferta de Curso / Grupo", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 5))
        ctk.CTkLabel(dialog, text="Configure el grupo, periodo, cupo y docente asignado.", font=ctk.CTkFont(size=11), text_color="#94A3B8").pack(pady=(0, 15))

        scroll = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        # Asignatura
        ctk.CTkLabel(scroll, text="Asignatura a Ofertar *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(anchor="w", padx=10, pady=(2, 0))
        curso_vals = [f"{c.idCurso} - {c.codigoCurso} | {c.nombre}" for c in self.controller.cursos] or ["1 - Sin Cursos"]
        combo_curso = ctk.CTkComboBox(scroll, values=curso_vals)
        combo_curso.pack(fill="x", padx=10, pady=(2, 8))

        # Periodo
        ctk.CTkLabel(scroll, text="Periodo Académico *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(anchor="w", padx=10, pady=(2, 0))
        per_vals = [f"{p.idPeriodo} - {p.codigo} | {p.nombre}" for p in self.controller.periodos_academicos] or ["1 - 2026-1"]
        combo_per = ctk.CTkComboBox(scroll, values=per_vals)
        combo_per.pack(fill="x", padx=10, pady=(2, 8))

        # Grupo y Cupo
        row_gc = ctk.CTkFrame(scroll, fg_color="transparent")
        row_gc.pack(fill="x", padx=10, pady=(2, 8))
        row_gc.columnconfigure(0, weight=1)
        row_gc.columnconfigure(1, weight=1)

        ctk.CTkLabel(row_gc, text="Grupo *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=0, column=0, sticky="w", padx=5)
        ctk.CTkLabel(row_gc, text="Cupo Máximo *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=0, column=1, sticky="w", padx=5)

        entry_grupo = ctk.CTkEntry(row_gc)
        entry_grupo.insert(0, "01")
        entry_grupo.grid(row=1, column=0, sticky="ew", padx=5, pady=2)

        entry_cupo = ctk.CTkEntry(row_gc)
        entry_cupo.insert(0, "35")
        entry_cupo.grid(row=1, column=1, sticky="ew", padx=5, pady=2)

        # Aula y Sede
        row_as = ctk.CTkFrame(scroll, fg_color="transparent")
        row_as.pack(fill="x", padx=10, pady=(2, 8))
        row_as.columnconfigure(0, weight=1)
        row_as.columnconfigure(1, weight=1)

        ctk.CTkLabel(row_as, text="Aula", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=0, column=0, sticky="w", padx=5)
        ctk.CTkLabel(row_as, text="Sede", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=0, column=1, sticky="w", padx=5)

        entry_aula = ctk.CTkEntry(row_as)
        entry_aula.insert(0, "Aula 201")
        entry_aula.grid(row=1, column=0, sticky="ew", padx=5, pady=2)

        entry_sede = ctk.CTkEntry(row_as)
        entry_sede.insert(0, "Sede Sabanas")
        entry_sede.grid(row=1, column=1, sticky="ew", padx=5, pady=2)

        # Modalidad
        ctk.CTkLabel(scroll, text="Modalidad", font=ctk.CTkFont(size=11), text_color="#94A3B8").pack(anchor="w", padx=10, pady=(2, 0))
        combo_mod = ctk.CTkComboBox(scroll, values=["PRESENCIAL", "VIRTUAL", "HIBRIDA"])
        combo_mod.set("PRESENCIAL")
        combo_mod.pack(fill="x", padx=10, pady=(2, 8))

        # Docente a Asignar
        ctk.CTkLabel(scroll, text="Profesor Asignado (Opcional)", font=ctk.CTkFont(size=11, weight="bold"), text_color="#38BDF8").pack(anchor="w", padx=10, pady=(2, 0))
        prof_options = ["Sin Asignar"]
        for pr in self.controller.profesores:
            pe = next((p for p in self.controller.personas if p.idPersona == pr.idPersona), None)
            nom = f"{pe.primerNombre} {pe.primerApellido}" if pe else "Profesor"
            prof_options.append(f"{pr.idProfesor} - {pr.codigoProfesor} | {nom}")

        combo_prof = ctk.CTkComboBox(scroll, values=prof_options)
        combo_prof.set(prof_options[0])
        combo_prof.pack(fill="x", padx=10, pady=(2, 8))

        def _guardar_oferta():
            c_sel = combo_curso.get().split(" - ")[0].strip()
            id_curso = int(c_sel) if c_sel.isdigit() else 1

            p_sel = combo_per.get().split(" - ")[0].strip()
            id_per = int(p_sel) if p_sel.isdigit() else 1

            gr = entry_grupo.get().strip() or "01"
            cupo_str = entry_cupo.get().strip()
            cupo = int(cupo_str) if cupo_str.isdigit() else 35

            new_id_of = max((o.idOfertaCurso or 0 for o in self.controller.ofertas), default=0) + 1
            oferta = OfertaCurso(
                idOfertaCurso=new_id_of,
                idCurso=id_curso,
                idPeriodo=id_per,
                grupo=gr,
                cupoMaximo=cupo,
                cupoDisponible=cupo,
                modalidad=combo_mod.get(),
                aula=entry_aula.get().strip() or "Aula 201",
                sede=entry_sede.get().strip() or "Sede Sabanas",
                fechaInicio=date.today(),
                estado="ACTIVO",
            )
            self.controller.ofertas.append(oferta)

            # Asignar profesor si se seleccionó uno
            pr_sel = combo_prof.get()
            if pr_sel != "Sin Asignar" and " - " in pr_sel:
                id_prof = int(pr_sel.split(" - ")[0].strip())
                new_id_asig = max((a.idAsignacion or 0 for a in self.controller.asignaciones), default=0) + 1
                asig = AsignacionDocente(
                    idAsignacion=new_id_asig,
                    idProfesor=id_prof,
                    idOfertaCurso=new_id_of,
                    numeroHoras=Decimal("4"),
                    fechaAsignacion=date.today(),
                    estado="ACTIVO",
                )
                self.controller.asignaciones.append(asig)

            self.controller._recrear_gestores()
            dialog.destroy()
            self.actualizar()

        ctk.CTkButton(scroll, text="💾 Abrir Oferta de Curso", font=ctk.CTkFont(size=12, weight="bold"), fg_color="#059669", hover_color="#047857", height=38, command=_guardar_oferta).pack(pady=15)

    # ------------------------------------------------------------------
    # MODAL 3: EDITAR CURSO
    # ------------------------------------------------------------------
    def _editar_curso(self, curso: Curso) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"✏️ Editar Asignatura {curso.codigoCurso}")
        dialog.geometry("460x520")
        dialog.grab_set()

        ctk.CTkLabel(dialog, text=f"Modificar Asignatura: {curso.nombre}", font=ctk.CTkFont(size=15, weight="bold")).pack(pady=(15, 10))

        entry_nom = ctk.CTkEntry(dialog)
        entry_nom.insert(0, curso.nombre)
        entry_nom.pack(fill="x", padx=20, pady=6)

        entry_cred = ctk.CTkEntry(dialog)
        entry_cred.insert(0, str(curso.numeroCreditos))
        entry_cred.pack(fill="x", padx=20, pady=6)

        entry_ht = ctk.CTkEntry(dialog)
        entry_ht.insert(0, str(getattr(curso, "horasTeoricas", 3)))
        entry_ht.pack(fill="x", padx=20, pady=6)

        entry_hp = ctk.CTkEntry(dialog)
        entry_hp.insert(0, str(getattr(curso, "horasPracticas", 2)))
        entry_hp.pack(fill="x", padx=20, pady=6)

        entry_nota = ctk.CTkEntry(dialog)
        entry_nota.insert(0, str(curso.notaMinimaAprobatoria))
        entry_nota.pack(fill="x", padx=20, pady=6)

        def _guardar():
            curso.nombre = entry_nom.get().strip() or curso.nombre
            if entry_cred.get().strip().isdigit():
                curso.numeroCreditos = int(entry_cred.get().strip())
            if entry_ht.get().strip().isdigit():
                curso.horasTeoricas = int(entry_ht.get().strip())
            if entry_hp.get().strip().isdigit():
                curso.horasPracticas = int(entry_hp.get().strip())
            try:
                curso.notaMinimaAprobatoria = Decimal(entry_nota.get().strip())
            except Exception:
                pass
            self.controller._recrear_gestores()
            dialog.destroy()
            self.actualizar()

        ctk.CTkButton(dialog, text="💾 Guardar Cambios", font=ctk.CTkFont(size=12, weight="bold"), fg_color="#10B981", hover_color="#059669", height=36, command=_guardar).pack(pady=20)

    def _eliminar_curso(self, id_curso: int) -> None:
        self.controller.cursos = [c for c in self.controller.cursos if c.idCurso != id_curso]
        self.controller._recrear_gestores()
        self.actualizar()

    def _eliminar_oferta(self, id_oferta: int) -> None:
        self.controller.ofertas = [o for o in self.controller.ofertas if o.idOfertaCurso != id_oferta]
        self.controller.asignaciones = [a for a in self.controller.asignaciones if a.idOfertaCurso != id_oferta]
        self.controller._recrear_gestores()
        self.actualizar()

    def _cancelar_curso_estudiante(self, id_detalle: int) -> None:
        det = next((d for d in self.controller.detalles_matricula if d.idDetalleMatricula == id_detalle), None)
        if det:
            det.estadoCurso = EstadoCurso.CANCELADO
            det.fechaCancelacion = date.today()
            det.motivoCancelacion = "Cancelación a solicitud del estudiante"

            # Reponer cupo a la oferta
            oferta = next((o for o in self.controller.ofertas if o.idOfertaCurso == det.idOfertaCurso), None)
            if oferta:
                oferta.cupoDisponible = min(oferta.cupoMaximo or 35, (oferta.cupoDisponible or 0) + 1)

            # Restar créditos de la matrícula
            mat = next((m for m in self.controller.matriculas if m.idMatricula == det.idMatricula), None)
            curso = next((c for c in self.controller.cursos if oferta and c.idCurso == oferta.idCurso), None)
            if mat and curso and mat.totalCreditos:
                mat.totalCreditos = max(0, mat.totalCreditos - (curso.numeroCreditos or 0))

            self.controller._recrear_gestores()
            self.actualizar()

    def actualizar(self) -> None:
        for widget in self.winfo_children():
            widget.destroy()
        self._crear_interfaz()
