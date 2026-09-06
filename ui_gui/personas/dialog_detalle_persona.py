"""Modal para ver la Ficha Técnica detallada de una Persona y sus roles en PITA."""

from __future__ import annotations

from typing import TYPE_CHECKING
import customtkinter as ctk

from ui_gui.theme import Colors

if TYPE_CHECKING:
    from ui_gui.gui_controller import PITAController
    from dominio.modelo_datos import Persona


class DialogDetallePersona(ctk.CTkToplevel):
    """Diálogo modal para inspección de información de una Persona."""

    def __init__(self, parent: ctk.CTkBaseClass, persona: Persona | None, controller: PITAController) -> None:
        super().__init__(parent)
        if not persona:
            self.destroy()
            return

        self.persona = persona
        self.controller = controller

        self.title(f"👁️ Ficha Técnica — {persona.primerNombre} {persona.primerApellido}")
        self.geometry("520x620")
        self.grab_set()
        self._construir_ui()

    def _construir_ui(self) -> None:
        p = self.persona
        nom_completo = f"{p.primerNombre} {p.segundoNombre or ''} {p.primerApellido} {p.segundoApellido or ''}".strip()

        ctk.CTkLabel(self, text=f"👤 {nom_completo}", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 5))
        ctk.CTkLabel(self, text="Ficha de Identificación, Contacto y Roles en PITA", font=ctk.CTkFont(size=11), text_color="#94A3B8").pack(pady=(0, 10))

        scroll_info = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll_info.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        # Tarjeta Datos Personales
        info_frame = ctk.CTkFrame(scroll_info, fg_color=Colors.BG_CARD_HOVER, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
        info_frame.pack(fill="x", pady=6)
        ctk.CTkLabel(info_frame, text="Datos Personales y Contacto", font=ctk.CTkFont(size=12, weight="bold"), text_color="#38BDF8").pack(anchor="w", padx=15, pady=(10, 6))

        detalles = [
            ("📄 Documento Identidad:", f"{p.tipoDocumento or 'CC'} {p.numeroDocumento}"),
            ("🎂 Fecha Nacimiento:", str(p.fechaNacimiento or "No registrada")),
            ("📧 Correo Institucional:", p.correoInstitucional or "N/A"),
            ("📧 Correo Personal:", p.correoPersonal or "No registrado"),
            ("📱 Teléfono Contacto:", p.telefono or "No registrado"),
            ("🏠 Dirección:", p.direccion or "No registrada"),
            ("🏙️ Ciudad de Residencia:", p.ciudadResidencia or "No registrada"),
            ("📅 Fecha Registro:", str(p.fechaRegistro or "N/A")),
            ("🟢 Estado Sistema:", p.estado or "ACTIVO"),
        ]
        for lbl, val in detalles:
            self._agregar_fila_detalle(info_frame, lbl, str(val))
        ctk.CTkLabel(info_frame, text="").pack(pady=2)

        # Buscar roles asociados
        est_rel = next((e for e in self.controller.estudiantes if getattr(e, "idPersona", None) == p.idPersona), None)
        prof_rel = next((pr for pr in self.controller.profesores if getattr(pr, "idPersona", None) == p.idPersona), None)
        adm_rel = next((a for a in self.controller.administrativos if getattr(a, "idPersona", None) == p.idPersona), None)

        if est_rel:
            card_est = ctk.CTkFrame(scroll_info, fg_color=Colors.BG_CARD_HOVER, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
            card_est.pack(fill="x", pady=6)
            ctk.CTkLabel(card_est, text="👨‍🎓 Rol: Estudiante", font=ctk.CTkFont(size=12, weight="bold"), text_color="#34D399").pack(anchor="w", padx=15, pady=(10, 6))

            prog_name = next((pr.nombre for pr in self.controller.programas if pr.idPrograma == est_rel.idPrograma), f"Prog #{est_rel.idPrograma}")
            for lbl, val in [
                ("Código Estudiante:", str(est_rel.codigoEstudiante)),
                ("Programa Académico:", str(prog_name)),
                ("Semestre Actual:", f"Semestre {est_rel.semestreActual}"),
                ("Promedio Acumulado:", f"{float(est_rel.promedioAcumulado or 0.0):.2f}"),
                ("Estado Académico:", str(est_rel.estadoAcademico)),
            ]:
                self._agregar_fila_detalle(card_est, lbl, val)
            ctk.CTkLabel(card_est, text="").pack(pady=2)

        if prof_rel:
            card_prof = ctk.CTkFrame(scroll_info, fg_color=Colors.BG_CARD_HOVER, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
            card_prof.pack(fill="x", pady=6)
            ctk.CTkLabel(card_prof, text="👨‍🏫 Rol: Profesor", font=ctk.CTkFont(size=12, weight="bold"), text_color="#C084FC").pack(anchor="w", padx=15, pady=(10, 6))

            prog_name = next((pr.nombre for pr in self.controller.programas if pr.idPrograma == prof_rel.idProgramaPrincipal), f"Prog #{prof_rel.idProgramaPrincipal}")
            for lbl, val in [
                ("Código Profesor:", str(prof_rel.codigoProfesor)),
                ("Programa Principal:", str(prog_name)),
                ("Tipo Profesor:", str(prof_rel.tipoProfesor)),
                ("Categoría:", str(prof_rel.categoriaDocente)),
                ("Dedicación:", str(prof_rel.dedicacion)),
                ("Horas Semanales:", f"{prof_rel.numeroHorasSemanales} h/sem"),
                ("Puntos Salariales:", str(prof_rel.puntosSalariales or "0")),
                ("Máximo Nivel Estudio:", str(prof_rel.maximoNivelEstudio or "N/A")),
                ("Título Profesional:", str(prof_rel.tituloProfesional or "N/A")),
            ]:
                self._agregar_fila_detalle(card_prof, lbl, val)
            ctk.CTkLabel(card_prof, text="").pack(pady=2)

        if adm_rel:
            card_adm = ctk.CTkFrame(scroll_info, fg_color=Colors.BG_CARD_HOVER, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
            card_adm.pack(fill="x", pady=6)
            ctk.CTkLabel(card_adm, text="👔 Rol: Administrativo", font=ctk.CTkFont(size=12, weight="bold"), text_color="#F59E0B").pack(anchor="w", padx=15, pady=(10, 6))

            for lbl, val in [
                ("Código Empleado:", str(adm_rel.codigoEmpleado)),
                ("Cargo:", str(adm_rel.cargo)),
                ("Dependencia:", str(adm_rel.dependencia)),
                ("Tipo Contratación:", str(getattr(adm_rel, "tipoContratacion", "PLANTA"))),
                ("Salario Base:", f"${float(adm_rel.salarioBase or 0):,.2f}"),
            ]:
                self._agregar_fila_detalle(card_adm, lbl, val)
            ctk.CTkLabel(card_adm, text="").pack(pady=2)

    def _agregar_fila_detalle(self, parent: ctk.CTkFrame, lbl: str, val: str) -> None:
        r = ctk.CTkFrame(parent, fg_color="transparent")
        r.pack(fill="x", padx=15, pady=3)
        ctk.CTkLabel(r, text=lbl, font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(side="left")
        ctk.CTkLabel(r, text=val, font=ctk.CTkFont(size=11), text_color="#F8FAFC").pack(side="right")
