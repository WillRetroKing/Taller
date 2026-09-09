"""Renderizadores modulares para las pestañas de gestión académica."""

from __future__ import annotations

from decimal import Decimal
from tkinter import messagebox
from typing import TYPE_CHECKING, Callable
import customtkinter as ctk

from ui_gui.theme import Colors, create_styled_tabview
from ui_gui.components import PITAGridTable, clean_enum

if TYPE_CHECKING:
    from ui_gui.academica.academica_service import AcademicaService
    from ui_gui.gui_controller import PITAController
    from dominio.modelo_datos import Curso, DetalleMatricula


class AcademicaTabs:
    """Componentes modulares de interfaz para cada pestaña de gestión académica."""

    @staticmethod
    def render_tab_oferta(
        parent_tab: ctk.CTkFrame,
        controller: PITAController,
        on_editar_curso: Callable[[Curso], None],
        on_eliminar_curso: Callable[[int], None],
        on_eliminar_oferta: Callable[[int], None],
    ) -> None:
        """Renderiza la pestaña 1: Catálogo de Asignaturas y Ofertas / Grupos Abiertos."""
        for w in parent_tab.winfo_children():
            w.destroy()

        sub_tabview = create_styled_tabview(parent_tab)
        sub_tabview.pack(fill="both", expand=True, padx=5, pady=5)

        sub_tab_cursos = sub_tabview.add("📖 Catálogo de Asignaturas")
        sub_tab_ofertas = sub_tabview.add("🏫 Ofertas y Grupos Abiertos")

        # 1. Catálogo de Asignaturas
        headers_c = ["Código Curso", "Nombre Asignatura", "Créditos", "Horas T / P", "Nota Mínima", "Cupo Sugerido", "Acciones"]
        col_w_c = [2, 4, 1, 2, 1, 1, 2]
        col_m_c = [80, 160, 60, 90, 70, 70, 80]

        table_c = PITAGridTable(sub_tab_cursos, headers=headers_c, col_weights=col_w_c, col_mins=col_m_c)
        table_c.pack(fill="both", expand=True, padx=5, pady=5)

        if not controller.cursos:
            ctk.CTkLabel(table_c, text="No hay asignaturas en el catálogo.", text_color="#94A3B8").pack(pady=30)
        else:
            for c in controller.cursos:
                act_spec = (
                    "actions",
                    [
                        ("✏️ Editar", lambda cur=c: on_editar_curso(cur), "#334155", "#475569"),
                        ("❌ Eliminar", lambda c_id=c.idCurso: on_eliminar_curso(c_id), "#EF4444", "#DC2626"),
                    ],
                )
                nota_min_raw = getattr(c, "notaMinimaAprobatoria", None)
                try:
                    nota_min_fmt = f"{float(nota_min_raw):.1f}" if (nota_min_raw is not None and float(nota_min_raw) > 0) else "3.0"
                except Exception:
                    nota_min_fmt = "3.0"

                cells = [
                    (getattr(c, "codigoCurso", "N/A"), "#38BDF8"),
                    (getattr(c, "nombre", "N/A"), "#F8FAFC"),
                    f"{getattr(c, 'numeroCreditos', 3)} créditos",
                    f"{getattr(c, 'horasTeoricas', 3)}h T / {getattr(c, 'horasPracticas', 2)}h P",
                    nota_min_fmt,
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

        if not controller.ofertas:
            ctk.CTkLabel(table_o, text="No hay ofertas ni grupos abiertos para este periodo.", text_color="#94A3B8").pack(pady=30)
        else:
            for of in controller.ofertas:
                curso = next((c for c in controller.cursos if c.idCurso == of.idCurso), None)
                nom_curso = curso.nombre if curso else f"Curso #{of.idCurso}"

                periodo = next((p for p in controller.periodos_academicos if p.idPeriodo == of.idPeriodo), None)
                nom_per = periodo.codigo if periodo else f"Per #{of.idPeriodo}"

                asig = next((a for a in controller.asignaciones if a.idOfertaCurso == of.idOfertaCurso and a.estado != "INACTIVO"), None)
                prof = next((p for p in controller.profesores if asig and p.idProfesor == asig.idProfesor), None)
                pers_prof = next((pe for pe in controller.personas if prof and pe.idPersona == prof.idPersona), None)

                nom_prof = f"{pers_prof.primerNombre} {pers_prof.primerApellido}" if pers_prof else "Sin asignar"

                act_o = (
                    "actions",
                    [
                        ("❌ Cerrar", lambda of_id=of.idOfertaCurso: on_eliminar_oferta(of_id), "#EF4444", "#DC2626"),
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

    @staticmethod
    def render_tab_matricula(
        parent_tab: ctk.CTkFrame,
        controller: PITAController,
        service: AcademicaService,
        on_refresh: Callable[[], None],
        on_cancelar_curso: Callable[[int], None],
    ) -> None:
        """Renderiza la pestaña 2: Formulario de Matrícula de Cursos y Tabla de Inscripciones."""
        for w in parent_tab.winfo_children():
            w.destroy()

        container = ctk.CTkFrame(parent_tab, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=5, pady=5)

        form = ctk.CTkFrame(container, fg_color=Colors.BG_CARD, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
        form.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(form, text="✍️ Registrar Matrícula en Oferta Académica", font=ctk.CTkFont(size=14, weight="bold"), text_color="#38BDF8").pack(anchor="w", padx=15, pady=(10, 5))

        f_row = ctk.CTkFrame(form, fg_color="transparent")
        f_row.pack(fill="x", padx=15, pady=5)

        # Opciones de estudiantes
        estud_options = [
            f"{e.codigoEstudiante} - {next((p.primerNombre + ' ' + p.primerApellido for p in controller.personas if p.idPersona == e.idPersona), 'Estudiante')}"
            for e in controller.estudiantes
            if e.estado != "INACTIVO"
        ] or ["Sin estudiantes disponibles"]

        ctk.CTkLabel(f_row, text="Estudiante:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(side="left", padx=(0, 5))
        combo_est = ctk.CTkComboBox(f_row, values=estud_options, width=270)
        combo_est.pack(side="left", padx=5)

        # Opciones de ofertas disponibles
        oferta_options = []
        for of in controller.ofertas:
            c = next((cur for cur in controller.cursos if cur.idCurso == of.idCurso), None)
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
            id_of_str = sel_o.split(" | ")[0].replace("OFER-", "").strip()
            id_oferta = int(id_of_str) if id_of_str.isdigit() else 0

            exito, msg = service.matricular_estudiante(cod_e, id_oferta)
            lbl_msg.configure(text=msg, text_color="#10B981" if exito else "#EF4444")
            if exito:
                on_refresh()

        btn_mat = ctk.CTkButton(f_row, text="✍️ Matricular Estudiante", font=ctk.CTkFont(size=12, weight="bold"), fg_color="#10B981", hover_color="#059669", corner_radius=8, command=_matricular)
        btn_mat.pack(side="left", padx=15)

        # Tabla de Inscripciones
        headers = ["ID Inscripción", "Estudiante", "Asignatura & Grupo", "Créditos", "Estado Curso", "Nota Definitiva", "Acciones"]
        col_weights = [2, 3, 3, 1, 2, 2, 2]
        col_mins = [90, 150, 150, 70, 90, 90, 100]

        table = PITAGridTable(container, headers=headers, col_weights=col_weights, col_mins=col_mins)
        table.pack(fill="both", expand=True, padx=5, pady=5)

        if not controller.detalles_matricula:
            ctk.CTkLabel(table, text="No hay inscripciones registradas aún.", text_color="#94A3B8").pack(pady=20)
            return

        for det in controller.detalles_matricula:
            mat = next((m for m in controller.matriculas if m.idMatricula == det.idMatricula), None)
            est = next((e for e in controller.estudiantes if mat and e.idEstudiante == mat.idEstudiante), None)
            pers = next((p for p in controller.personas if est and p.idPersona == est.idPersona), None)

            oferta = next((o for o in controller.ofertas if o.idOfertaCurso == det.idOfertaCurso), None)
            curso = next((c for c in controller.cursos if oferta and c.idCurso == oferta.idCurso), None)
            if not curso:
                curso = next((c for c in controller.cursos if c.idCurso == det.idOfertaCurso), None)

            nom_e = f"{pers.primerNombre} {pers.primerApellido} ({est.codigoEstudiante})" if pers and est else "Estudiante"
            nom_c = f"{curso.nombre} (Gr. {oferta.grupo if oferta else '01'})" if curso else "Curso"
            cred_c = f"{curso.numeroCreditos or 3} cr." if curso else "3 cr."

            est_c = clean_enum(getattr(det, "estadoCurso", "EN_CURSO"))
            nota_f = getattr(det, "notaFinal", None)
            nota_str = f"{float(nota_f):.2f}" if nota_f is not None else "Sin nota"
            color_nota = "#F87171" if (nota_f is not None and float(nota_f) < 3.0) else ("#34D399" if nota_f is not None else "#94A3B8")

            badge_type = "cancelado" if est_c == "CANCELADO" else ("active" if est_c == "APROBADO" else ("danger" if est_c == "REPROBADO" else "info"))
            badge_tuple = ("badge", est_c.replace("_", " ").title(), badge_type)

            if est_c != "CANCELADO":
                btn_canc = ("button", "🚫 Cancelar", lambda d_id=det.idDetalleMatricula: on_cancelar_curso(d_id), "#EF4444", "#DC2626", 90, 28)
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

    @staticmethod
    def render_tab_evaluaciones(
        parent_tab: ctk.CTkFrame,
        controller: PITAController,
        service: AcademicaService,
        on_refresh: Callable[[], None],
        on_editar_nota: Callable[[DetalleMatricula], None],
        on_limpiar_nota: Callable[[DetalleMatricula], None],
    ) -> None:
        """Renderiza la pestaña 3: Registro de Calificaciones y Tabla con Acciones."""
        for w in parent_tab.winfo_children():
            w.destroy()

        container = ctk.CTkFrame(parent_tab, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=5, pady=5)

        form = ctk.CTkFrame(container, fg_color=Colors.BG_CARD, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
        form.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(form, text="📝 Asignación de Calificaciones y Evaluaciones", font=ctk.CTkFont(size=14, weight="bold"), text_color="#34D399").pack(anchor="w", padx=15, pady=(10, 5))

        f_row = ctk.CTkFrame(form, fg_color="transparent")
        f_row.pack(fill="x", padx=15, pady=5)

        # Opciones legibles de inscripciones activas
        det_options = []
        for d in controller.detalles_matricula:
            if clean_enum(getattr(d, "estadoCurso", "")) == "CANCELADO":
                continue
            mat = next((m for m in controller.matriculas if m.idMatricula == d.idMatricula), None)
            est = next((e for e in controller.estudiantes if mat and e.idEstudiante == mat.idEstudiante), None)
            pers = next((p for p in controller.personas if est and p.idPersona == est.idPersona), None)

            of = next((o for o in controller.ofertas if o.idOfertaCurso == d.idOfertaCurso), None)
            c = next((cur for cur in controller.cursos if of and cur.idCurso == of.idCurso), None)
            if not c:
                c = next((cur for cur in controller.cursos if cur.idCurso == d.idOfertaCurso), None)

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
            service.registrar_nota(det_id, Decimal(str(round(val_nota, 2))))
            lbl_msg_nota.configure(text=f"✅ Calificación de {val_nota:.2f} registrada exitosamente.", text_color="#10B981")
            on_refresh()

        btn_nota = ctk.CTkButton(f_row, text="💾 Registrar Nota", font=ctk.CTkFont(size=12, weight="bold"), fg_color="#0067C0", hover_color="#005FB8", command=_guardar_nota)
        btn_nota.pack(side="left", padx=10)

        # Tabla de Calificaciones
        headers_n = ["ID Inscripción", "Estudiante", "Asignatura", "Nota Definitiva", "Estado Calificación", "Impacto EBRA", "Acciones"]
        col_w_n = [2, 3, 3, 2, 2, 2, 2]
        col_m_n = [80, 140, 140, 80, 90, 90, 130]

        table_n = PITAGridTable(container, headers=headers_n, col_weights=col_w_n, col_mins=col_m_n)
        table_n.pack(fill="both", expand=True, padx=5, pady=5)

        if not controller.detalles_matricula:
            ctk.CTkLabel(table_n, text="No hay registros de calificaciones.", text_color="#94A3B8").pack(pady=20)
            return

        for det in controller.detalles_matricula:
            if clean_enum(getattr(det, "estadoCurso", "")) == "CANCELADO":
                continue
            mat = next((m for m in controller.matriculas if m.idMatricula == det.idMatricula), None)
            est = next((e for e in controller.estudiantes if mat and e.idEstudiante == mat.idEstudiante), None)
            pers = next((p for p in controller.personas if est and p.idPersona == est.idPersona), None)

            oferta = next((o for o in controller.ofertas if o.idOfertaCurso == det.idOfertaCurso), None)
            curso = next((c for c in controller.cursos if oferta and c.idCurso == oferta.idCurso), None)
            if not curso:
                curso = next((c for c in controller.cursos if c.idCurso == det.idOfertaCurso), None)

            nom_e = f"{pers.primerNombre} {pers.primerApellido}" if pers else "Estudiante"
            nom_c = curso.nombre if curso else "Curso"

            nota_f = getattr(det, "notaFinal", None)
            nota_str = f"{float(nota_f):.2f}" if nota_f is not None else "Sin calificar"
            color_nota = "#F87171" if (nota_f is not None and float(nota_f) < 3.0) else ("#34D399" if nota_f is not None else "#94A3B8")

            est_c = clean_enum(getattr(det, "estadoCurso", "EN_CURSO"))
            badge_type = "active" if est_c == "APROBADO" else ("danger" if est_c == "REPROBADO" else "info")
            badge_tuple = ("badge", est_c.replace("_", " ").title(), badge_type)

            prom_est = float(getattr(est, "promedioAcumulado", 0.0) or 0.0) if est else 0.0
            if prom_est < 3.0 and prom_est > 0:
                ebra_badge = ("badge", f"⚠️ EBRA ({prom_est:.2f})", "ebra")
            else:
                ebra_badge = ("badge", f"● Normal ({prom_est:.2f})", "active")

            actions_list = [
                ("✏️ Editar Nota", lambda d=det: on_editar_nota(d)),
            ]
            if nota_f is not None:
                actions_list.append(("🗑️ Limpiar Nota", lambda d=det: on_limpiar_nota(d)))

            act_spec = ("actions", actions_list)

            cells = [
                f"INS-{det.idDetalleMatricula}",
                (f"{nom_e} ({getattr(est, 'codigoEstudiante', '')})", "#F8FAFC"),
                (nom_c, "#38BDF8"),
                (nota_str, color_nota),
                badge_tuple,
                ebra_badge,
                act_spec,
            ]
            table_n.add_row_items(cells, is_highlighted=(nota_f is not None and float(nota_f) < 3.0))

    @staticmethod
    def render_tab_ebra(
        parent_tab: ctk.CTkFrame,
        controller: PITAController,
        service: AcademicaService,
    ) -> None:
        """Renderiza la pestaña 4: Tablero Analítico y Alertas EBRA con KPIs."""
        for w in parent_tab.winfo_children():
            w.destroy()

        scroll = ctk.CTkScrollableFrame(parent_tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=5, pady=5)

        top_bar = ctk.CTkFrame(scroll, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 10))

        title_box = ctk.CTkFrame(top_bar, fg_color="transparent")
        title_box.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            title_box,
            text="🚨 Tablero de Monitoreo y Alertas Académicas EBRA",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color="#F8FAFC",
        ).pack(anchor="w", pady=(0, 2))

        ctk.CTkLabel(
            title_box,
            text="Identificación temprana de estudiantes en condición de Bajo Rendimiento Académico (Promedio < 3.0).",
            font=ctk.CTkFont(size=12),
            text_color="#94A3B8",
        ).pack(anchor="w")

        def _ejecutar_deteccion():
            periodo = controller.periodos_academicos[0] if controller.periodos_academicos else None
            id_per = periodo.idPeriodoAcademico if periodo else 1
            alertas = controller.gestor_matriculas.evaluar_alertas_periodo(id_per)
            controller.guardar_datos()
            messagebox.showinfo(
                "Detección EBRA",
                f"Evaluación finalizada.\nSe evaluaron los estudiantes y se detectaron/actualizaron {len(alertas)} alertas EBRA.",
            )
            AcademicaTabs.render_tab_ebra(parent_tab, controller, service)

        ctk.CTkButton(
            top_bar,
            text="⚡ Ejecutar Detección EBRA Masiva",
            command=_ejecutar_deteccion,
            fg_color="#DC2626",
            hover_color="#B91C1C",
            font=ctk.CTkFont(size=12, weight="bold"),
            height=32,
        ).pack(side="right", padx=5)

        # Métricas de riesgo EBRA
        kpi_data = service.calcular_kpis_ebra()
        total_est = kpi_data["total_estudiantes"]
        total_ebras = kpi_data["total_ebras"]
        normales = kpi_data["normales"]
        prom_global = kpi_data["promedio_global"]
        ebras = kpi_data["estudiantes_ebra"]

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

            pers = next((p for p in controller.personas if p.idPersona == est.idPersona), None)
            nom = f"{pers.primerNombre} {pers.primerApellido}" if pers else "Estudiante"
            tipo_doc = clean_enum(pers.tipoDocumento) if pers else ""
            doc = f"{tipo_doc} {pers.numeroDocumento}".strip() if pers else "N/A"

            prog = next((pr.nombre for pr in controller.programas if pr.idPrograma == est.idPrograma), f"Prog #{est.idPrograma}")

            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=15, pady=(10, 4))

            ctk.CTkLabel(top, text=f"👨‍🎓 {nom} ({est.codigoEstudiante}) — Doc: {doc}", font=ctk.CTkFont(size=13, weight="bold"), text_color="#F8FAFC").pack(side="left")
            ctk.CTkLabel(top, text="⚠️ CONDICIÓN EBRA ACTIVA", font=ctk.CTkFont(size=11, weight="bold"), text_color="#EF4444").pack(side="right")

            bot = ctk.CTkFrame(card, fg_color="transparent")
            bot.pack(fill="x", padx=15, pady=(0, 10))

            ctk.CTkLabel(bot, text=f"Programa: {prog} | Semestre: {est.semestreActual} | Promedio: {est.promedioAcumulado} / 5.0", font=ctk.CTkFont(size=11), text_color="#FCA5A5").pack(side="left")
            ctk.CTkLabel(bot, text="📌 Acción: Remitir a Tutoría y Plan de Acompañamiento Académico", font=ctk.CTkFont(size=11, weight="bold"), text_color="#FBBF24").pack(side="right")
