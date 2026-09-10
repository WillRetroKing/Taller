from __future__ import annotations
"""Modal para ver la Ficha Técnica detallada de una Persona y sus roles en PITA."""

from typing import TYPE_CHECKING, Any
import customtkinter as ctk

from ui_gui.components import clean_enum
from ui_gui.theme import Colors

if TYPE_CHECKING:
    from ui_gui.gui_controller import PITAController
    from dominio.modelo_datos import Persona


class DialogDetallePersona(ctk.CTkToplevel):
    """Modal de visualización de detalles completos de una persona y sus roles asociados."""

    def __init__(self, parent: ctk.CTkFrame, arg1: Any, arg2: Any):
        super().__init__(parent)
        # Soporte bi-direccional: detecta automáticamente si se pasó (controller, persona) o (persona, controller)
        if hasattr(arg1, "personas"):
            self.controller: "PITAController" = arg1
            self.persona: "Persona" = arg2
        else:
            self.persona: "Persona" = arg1
            self.controller: "PITAController" = arg2

        self.title("📄 Ficha Detallada de Persona")
        self.geometry("660x720")
        self.minsize(580, 620)
        self.configure(fg_color=Colors.BG_WINDOW)

        self.transient(parent.winfo_toplevel())
        self.grab_set()

        self._crear_interfaz()

    def _crear_interfaz(self) -> None:
        p = self.persona
        p_pnom = getattr(p, "primerNombre", "") or ""
        p_snom = getattr(p, "segundoNombre", "") or ""
        p_pape = getattr(p, "primerApellido", "") or ""
        p_sape = getattr(p, "segundoApellido", "") or ""
        nom_completo = f"{p_pnom} {p_snom} {p_pape} {p_sape}".strip() or "Persona Registrada"

        # Header
        header = ctk.CTkFrame(self, fg_color=Colors.BG_CARD, corner_radius=0)
        header.pack(fill="x", padx=0, pady=(0, 10))

        header_content = ctk.CTkFrame(header, fg_color="transparent")
        header_content.pack(fill="x", padx=20, pady=14)

        ctk.CTkLabel(
            header_content,
            text="👤 FICHA INTEGRAL DE PERSONA Y ROLES INSTITUCIONALES",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=Colors.WIN_BLUE,
        ).pack(anchor="w")

        ctk.CTkLabel(
            header_content,
            text=nom_completo,
            font=ctk.CTkFont(family="Segoe UI", size=19, weight="bold"),
            text_color=Colors.TEXT_MAIN,
        ).pack(anchor="w", pady=(2, 0))

        ctk.CTkFrame(self, height=1, fg_color=Colors.BORDER_SUBTLE).pack(fill="x")

        # Scrollable container
        scroll_info = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll_info.pack(fill="both", expand=True, padx=20, pady=10)

        # 1. Tarjeta Datos Personales y Contacto
        info_frame = ctk.CTkFrame(
            scroll_info,
            fg_color=Colors.BG_CARD,
            corner_radius=8,
            border_width=1,
            border_color=Colors.BORDER_SUBTLE,
        )
        info_frame.pack(fill="x", pady=6)
        ctk.CTkLabel(
            info_frame,
            text="📋 Datos Personales y de Contacto",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=Colors.WIN_BLUE,
        ).pack(anchor="w", padx=16, pady=(12, 6))

        ctk.CTkFrame(info_frame, height=1, fg_color=Colors.BORDER_SUBTLE).pack(fill="x", padx=12, pady=(0, 6))

        tipo_doc = clean_enum(getattr(p, "tipoDocumento", None)) or "CC"
        num_doc = getattr(p, "numeroDocumento", "N/A")
        detalles = [
            ("📄 Documento Identidad:", f"{tipo_doc} {num_doc}"),
            ("🎂 Fecha Nacimiento:", str(getattr(p, "fechaNacimiento", None) or "No registrada")),
            ("📧 Correo Institucional:", getattr(p, "correoInstitucional", None) or "N/A"),
            ("📧 Correo Personal:", getattr(p, "correoPersonal", None) or "No registrado"),
            ("📱 Teléfono Contacto:", getattr(p, "telefono", None) or "No registrado"),
            ("🏠 Dirección:", getattr(p, "direccion", None) or "No registrada"),
            ("🏙️ Ciudad de Residencia:", getattr(p, "ciudadResidencia", None) or "No registrada"),
            ("📅 Fecha Registro:", str(getattr(p, "fechaRegistro", None) or "N/A")),
            ("🟢 Estado en el Sistema:", clean_enum(getattr(p, "estado", None) or "ACTIVO")),
        ]
        for lbl, val in detalles:
            self._agregar_fila_detalle(info_frame, lbl, str(val))
        ctk.CTkFrame(info_frame, height=4, fg_color="transparent").pack()

        # 2. Buscar roles asociados
        p_id = getattr(p, "idPersona", None)
        est_rel = next((e for e in getattr(self.controller, "estudiantes", []) if getattr(e, "idPersona", None) == p_id), None)
        prof_rel = next((pr for pr in getattr(self.controller, "profesores", []) if getattr(pr, "idPersona", None) == p_id), None)
        adm_rel = next((a for a in getattr(self.controller, "administrativos", []) if getattr(a, "idPersona", None) == p_id), None)
        contratos_rel = [c for c in getattr(self.controller, "contratos", []) if getattr(c, "idPersona", None) == p_id]

        if est_rel:
            card_est = ctk.CTkFrame(
                scroll_info,
                fg_color=Colors.BG_CARD,
                corner_radius=8,
                border_width=1,
                border_color=Colors.BORDER_SUBTLE,
            )
            card_est.pack(fill="x", pady=6)
            ctk.CTkLabel(
                card_est,
                text="👨‍🎓 Rol Institucional: Estudiante",
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                text_color="#059669",
            ).pack(anchor="w", padx=16, pady=(12, 6))

            ctk.CTkFrame(card_est, height=1, fg_color=Colors.BORDER_SUBTLE).pack(fill="x", padx=12, pady=(0, 6))

            prog_id = getattr(est_rel, "idPrograma", None)
            prog_name = next((pr.nombre for pr in getattr(self.controller, "programas", []) if getattr(pr, "idPrograma", None) == prog_id), f"Programa #{prog_id}")
            prom = float(getattr(est_rel, "promedioAcumulado", 0.0) or 0.0)
            for lbl, val in [
                ("Código Estudiante:", str(getattr(est_rel, "codigoEstudiante", "N/A"))),
                ("Programa Académico:", str(prog_name)),
                ("Semestre Actual:", f"Semestre {getattr(est_rel, 'semestreActual', '1')}"),
                ("Promedio Acumulado:", f"{prom:.2f}"),
                ("Estado Académico:", clean_enum(getattr(est_rel, "estadoAcademico", "ACTIVO"))),
            ]:
                self._agregar_fila_detalle(card_est, lbl, val)
            ctk.CTkFrame(card_est, height=4, fg_color="transparent").pack()

            # Asignaturas y cursos matriculados
            mats_est = [m.idMatricula for m in getattr(self.controller, "matriculas", []) if getattr(m, "idEstudiante", None) == getattr(est_rel, "idEstudiante", None)]
            dets_est = [d for d in getattr(self.controller, "detalles_matricula", []) if getattr(d, "idMatricula", None) in mats_est]
            if dets_est:
                card_mat = ctk.CTkFrame(
                    scroll_info,
                    fg_color=Colors.BG_CARD,
                    corner_radius=8,
                    border_width=1,
                    border_color=Colors.BORDER_SUBTLE,
                )
                card_mat.pack(fill="x", pady=6)
                ctk.CTkLabel(
                    card_mat,
                    text="📚 Asignaturas y Cursos Matriculados",
                    font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                    text_color="#0284C7",
                ).pack(anchor="w", padx=16, pady=(12, 6))

                ctk.CTkFrame(card_mat, height=1, fg_color=Colors.BORDER_SUBTLE).pack(fill="x", padx=12, pady=(0, 6))

                for d in dets_est:
                    of = next((o for o in getattr(self.controller, "ofertas", []) if str(getattr(o, "idOfertaCurso", "")) == str(getattr(d, "idOfertaCurso", ""))), None)
                    c = next((cur for cur in getattr(self.controller, "cursos", []) if of and str(getattr(cur, "idCurso", "")) == str(getattr(of, "idCurso", ""))), None)
                    if not c:
                        c = next((cur for cur in getattr(self.controller, "cursos", []) if str(getattr(cur, "idCurso", "")) == str(getattr(d, "idOfertaCurso", ""))), None)

                    c_nom = getattr(c, "nombre", "Asignatura") if c else "Asignatura"
                    c_cod = getattr(c, "codigoCurso", "") if c else ""
                    c_cred = getattr(c, "numeroCreditos", 3) if c else 3
                    gr = getattr(of, "grupo", "01") if of else "01"
                    est_c = clean_enum(getattr(d, "estadoCurso", "EN_CURSO"))
                    nota_f = getattr(d, "notaFinal", None)
                    nota_txt = f"Nota: {float(nota_f):.2f}" if nota_f is not None else "Sin nota"

                    rotulo = f"📖 {c_cod} - {c_nom} (Gr. {gr})" if c_cod else f"📖 {c_nom} (Gr. {gr})"
                    detalle_val = f"{c_cred} Créditos | {est_c.title()} [{nota_txt}]"
                    self._agregar_fila_detalle(card_mat, rotulo, detalle_val)
                ctk.CTkFrame(card_mat, height=4, fg_color="transparent").pack()

        if prof_rel:
            card_prof = ctk.CTkFrame(
                scroll_info,
                fg_color=Colors.BG_CARD,
                corner_radius=8,
                border_width=1,
                border_color=Colors.BORDER_SUBTLE,
            )
            card_prof.pack(fill="x", pady=6)
            ctk.CTkLabel(
                card_prof,
                text="👨‍🏫 Rol Institucional: Profesor",
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                text_color="#7C3AED",
            ).pack(anchor="w", padx=16, pady=(12, 6))

            ctk.CTkFrame(card_prof, height=1, fg_color=Colors.BORDER_SUBTLE).pack(fill="x", padx=12, pady=(0, 6))

            prog_id = getattr(prof_rel, "idProgramaPrincipal", None)
            prog_name = next((pr.nombre for pr in getattr(self.controller, "programas", []) if getattr(pr, "idPrograma", None) == prog_id), f"Programa #{prog_id}")
            tipo_prof_str = clean_enum(getattr(prof_rel, "tipoProfesor", "PLANTA")).replace("_", " ").title()
            cat_str = clean_enum(getattr(prof_rel, "categoriaDocente", "TITULAR")).replace("_", " ").title()
            ded_str = clean_enum(getattr(prof_rel, "dedicacion", "TIEMPO_COMPLETO")).replace("_", " ").title()
            hrs = getattr(prof_rel, "numeroHorasSemanales", None) or "40"
            for lbl, val in [
                ("Código Profesor:", str(getattr(prof_rel, "codigoProfesor", "N/A"))),
                ("Programa Principal:", str(prog_name)),
                ("Tipo Profesor:", tipo_prof_str),
                ("Categoría Escalafón:", cat_str),
                ("Dedicación Laboral:", ded_str),
                ("Horas Semanales:", f"{hrs} h/sem"),
                ("Puntos Salariales (Dec. 1279):", f"{getattr(prof_rel, 'puntosSalariales', 0)} pts"),
                ("Máximo Nivel de Estudio:", str(getattr(prof_rel, "maximoNivelEstudio", None) or "N/A")),
                ("Título Profesional:", str(getattr(prof_rel, "tituloProfesional", None) or "N/A")),
                ("Área de Conocimiento:", str(getattr(prof_rel, "areaConocimiento", None) or "N/A")),
            ]:
                self._agregar_fila_detalle(card_prof, lbl, val)
            ctk.CTkFrame(card_prof, height=4, fg_color="transparent").pack()

        if adm_rel:
            card_adm = ctk.CTkFrame(
                scroll_info,
                fg_color=Colors.BG_CARD,
                corner_radius=8,
                border_width=1,
                border_color=Colors.BORDER_SUBTLE,
            )
            card_adm.pack(fill="x", pady=6)
            ctk.CTkLabel(
                card_adm,
                text="👔 Rol Institucional: Administrativo",
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                text_color="#D97706",
            ).pack(anchor="w", padx=16, pady=(12, 6))

            ctk.CTkFrame(card_adm, height=1, fg_color=Colors.BORDER_SUBTLE).pack(fill="x", padx=12, pady=(0, 6))

            tipo_adm = clean_enum(getattr(adm_rel, "tipoContratacion", "PLANTA")).replace("_", " ").title()
            sal_adm = getattr(adm_rel, "salarioBase", 0) or 0
            for lbl, val in [
                ("Código Empleado:", str(getattr(adm_rel, "codigoEmpleado", "N/A"))),
                ("Cargo Funcional:", str(getattr(adm_rel, "cargo", "N/A"))),
                ("Dependencia Adscrita:", str(getattr(adm_rel, "dependencia", "N/A"))),
                ("Tipo Contratación:", tipo_adm),
                ("Salario Base Ordinario:", f"$ {int(float(sal_adm)):,} COP".replace(",", ".")),
            ]:
                self._agregar_fila_detalle(card_adm, lbl, val)
            ctk.CTkFrame(card_adm, height=4, fg_color="transparent").pack()

        # 3. Contratos Formalizados Asociados
        if contratos_rel:
            card_con = ctk.CTkFrame(
                scroll_info,
                fg_color=Colors.BG_CARD,
                corner_radius=8,
                border_width=1,
                border_color=Colors.BORDER_SUBTLE,
            )
            card_con.pack(fill="x", pady=6)
            ctk.CTkLabel(
                card_con,
                text="📜 Vinculación Contractual Activa",
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                text_color=Colors.WIN_BLUE,
            ).pack(anchor="w", padx=16, pady=(12, 6))

            ctk.CTkFrame(card_con, height=1, fg_color=Colors.BORDER_SUBTLE).pack(fill="x", padx=12, pady=(0, 6))

            for con in contratos_rel:
                num_c = getattr(con, "numeroContrato", f"CTR-{getattr(con, 'idContrato', 0)}")
                t_con = clean_enum(getattr(con, "tipoContrato", "DOCENTE")).replace("_", " ").title()
                sal_c = getattr(con, "salarioBase", 0) or 0
                est_c = clean_enum(getattr(con, "estado", "ACTIVO"))
                for lbl, val in [
                    ("Número Contrato:", str(num_c)),
                    ("Modalidad / Régimen:", f"{t_con} ({getattr(con, 'regimenAplicable', 'Ley 100 / CST')})"),
                    ("Vigencia Contrato:", f"{getattr(con, 'fechaInicio', '')} al {getattr(con, 'fechaFin', '')}"),
                    ("Asignación / Salario Base:", f"$ {int(float(sal_c)):,} COP".replace(",", ".")),
                    ("Estado Contrato:", est_c),
                ]:
                    self._agregar_fila_detalle(card_con, lbl, val)
                ctk.CTkLabel(card_con, text="").pack(pady=1)
            ctk.CTkFrame(card_con, height=4, fg_color="transparent").pack()

        # Footer con botón Cerrar
        footer = ctk.CTkFrame(self, fg_color=Colors.BG_CARD, corner_radius=0)
        footer.pack(fill="x", side="bottom")

        ctk.CTkFrame(footer, height=1, fg_color=Colors.BORDER_SUBTLE).pack(fill="x")

        footer_content = ctk.CTkFrame(footer, fg_color="transparent")
        footer_content.pack(fill="x", padx=20, pady=10)

        ctk.CTkButton(
            footer_content,
            text="Cerrar Ficha",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#0F172A",
            hover_color="#1E293B",
            text_color="#FFFFFF",
            width=110,
            height=34,
            command=self.destroy,
        ).pack(side="right")

    def _agregar_fila_detalle(self, parent: ctk.CTkFrame, lbl: str, val: str) -> None:
        r = ctk.CTkFrame(parent, fg_color="transparent")
        r.pack(fill="x", padx=16, pady=3)
        ctk.CTkLabel(
            r,
            text=lbl,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=Colors.TEXT_MUTED,
        ).pack(side="left")
        ctk.CTkLabel(
            r,
            text=val,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=Colors.TEXT_MAIN,
        ).pack(side="right")
