from __future__ import annotations
"""Modal para ver la Ficha Técnica detallada de una Persona y sus roles en PITA."""

from ui_gui.components import clean_enum

from typing import TYPE_CHECKING
import customtkinter as ctk

from ui_gui.theme import Colors

if TYPE_CHECKING:
    from ui_gui.gui_controller import PITAController
    from dominio.modelo_datos import Persona


class DialogDetallePersona(ctk.CTkToplevel):
    """Modal de visualización de detalles completos de una persona y sus roles asociados."""

    def __init__(self, parent: ctk.CTkFrame, controller: "PITAController", persona: "Persona"):
        super().__init__(parent)
        self.controller = controller
        self.persona = persona

        self.title("📄 Ficha Detallada de Persona")
        self.geometry("640x700")
        self.resizable(False, False)
        self.configure(fg_color=Colors.BG_PAGE)

        self.transient(parent.winfo_toplevel())
        self.grab_set()

        self._crear_interfaz()

    def _crear_interfaz(self) -> None:
        p = self.persona
        nom_completo = f"{p.primerNombre or ''} {p.segundoNombre or ''} {p.primerApellido or ''} {p.segundoApellido or ''}".strip()

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 10))

        ctk.CTkLabel(header, text="👤 FICHA INTEGRAL DE PERSONA", font=ctk.CTkFont(size=11, weight="bold"), text_color="#38BDF8").pack(anchor="w")
        ctk.CTkLabel(header, text=nom_completo, font=ctk.CTkFont(size=18, weight="bold"), text_color="#F8FAFC").pack(anchor="w")

        # Scrollable container
        scroll_info = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll_info.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        # Tarjeta Datos Personales
        info_frame = ctk.CTkFrame(scroll_info, fg_color=Colors.BG_CARD_HOVER, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
        info_frame.pack(fill="x", pady=6)
        ctk.CTkLabel(info_frame, text="Datos Personales y Contacto", font=ctk.CTkFont(size=12, weight="bold"), text_color="#38BDF8").pack(anchor="w", padx=15, pady=(10, 6))

        tipo_doc = clean_enum(p.tipoDocumento) or "CC"
        detalles = [
            ("📄 Documento Identidad:", f"{tipo_doc} {p.numeroDocumento}"),
            ("🎂 Fecha Nacimiento:", str(p.fechaNacimiento or "No registrada")),
            ("📧 Correo Institucional:", p.correoInstitucional or "N/A"),
            ("📧 Correo Personal:", p.correoPersonal or "No registrado"),
            ("📱 Teléfono Contacto:", p.telefono or "No registrado"),
            ("🏠 Dirección:", p.direccion or "No registrada"),
            ("🏙️ Ciudad de Residencia:", p.ciudadResidencia or "No registrada"),
            ("📅 Fecha Registro:", str(p.fechaRegistro or "N/A")),
            ("🟢 Estado Sistema:", clean_enum(p.estado or "ACTIVO")),
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
                ("Estado Académico:", clean_enum(est_rel.estadoAcademico)),
            ]:
                self._agregar_fila_detalle(card_est, lbl, val)
            ctk.CTkLabel(card_est, text="").pack(pady=2)

        if prof_rel:
            card_prof = ctk.CTkFrame(scroll_info, fg_color=Colors.BG_CARD_HOVER, corner_radius=8, border_width=1, border_color=Colors.BORDER_SUBTLE)
            card_prof.pack(fill="x", pady=6)
            ctk.CTkLabel(card_prof, text="👨‍🏫 Rol: Profesor", font=ctk.CTkFont(size=12, weight="bold"), text_color="#C084FC").pack(anchor="w", padx=15, pady=(10, 6))

            prog_name = next((pr.nombre for pr in self.controller.programas if pr.idPrograma == prof_rel.idProgramaPrincipal), f"Prog #{prof_rel.idProgramaPrincipal}")
            tipo_prof_str = clean_enum(prof_rel.tipoProfesor).replace("_", " ").title()
            cat_str = clean_enum(prof_rel.categoriaDocente).replace("_", " ").title()
            ded_str = clean_enum(prof_rel.dedicacion).replace("_", " ").title()
            for lbl, val in [
                ("Código Profesor:", str(prof_rel.codigoProfesor)),
                ("Programa Principal:", str(prog_name)),
                ("Tipo Profesor:", tipo_prof_str),
                ("Categoría:", cat_str),
                ("Dedicación:", ded_str),
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

            tipo_adm = clean_enum(getattr(adm_rel, "tipoContratacion", "PLANTA")).replace("_", " ").title()
            for lbl, val in [
                ("Código Empleado:", str(adm_rel.codigoEmpleado)),
                ("Cargo:", str(adm_rel.cargo)),
                ("Dependencia:", str(adm_rel.dependencia)),
                ("Tipo Contratación:", tipo_adm),
                ("Salario Base:", f"${float(adm_rel.salarioBase or 0):,.2f}"),
            ]:
                self._agregar_fila_detalle(card_adm, lbl, val)
            ctk.CTkLabel(card_adm, text="").pack(pady=2)

    def _agregar_fila_detalle(self, parent: ctk.CTkFrame, lbl: str, val: str) -> None:
        r = ctk.CTkFrame(parent, fg_color="transparent")
        r.pack(fill="x", padx=15, pady=3)
        ctk.CTkLabel(r, text=lbl, font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(side="left")
        ctk.CTkLabel(r, text=val, font=ctk.CTkFont(size=11), text_color="#F8FAFC").pack(side="right")
