"""Modal para reconocer factores salariales y producción académica (Decreto 1279)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, Callable
import customtkinter as ctk

from ui_gui.theme import Colors, create_styled_tabview

if TYPE_CHECKING:
    from ui_gui.gui_controller import PITAController
    from ui_gui.contratos.contratos_service import ContratosService


class DialogReconocerPuntos(ctk.CTkToplevel):
    """Diálogo modal para asignar puntos salariales a docentes."""

    def __init__(
        self,
        parent: ctk.CTkBaseClass,
        controller: PITAController,
        service: ContratosService,
        on_success: Callable[[], None],
    ) -> None:
        super().__init__(parent)
        self.controller = controller
        self.service = service
        self.on_success = on_success

        self.title("⭐ Reconocer Factores y Productividad Académica")
        self.geometry("620x640")
        self.transient(parent.winfo_toplevel())
        self.grab_set()

        self._construir_ui()

    def _construir_ui(self) -> None:
        ctk.CTkLabel(
            self,
            text="⭐ Comité de Puntaje Salarial (Decreto 1279)",
            font=ctk.CTkFont(family="Segoe UI", size=17, weight="bold"),
            text_color=Colors.TEXT_MAIN,
        ).pack(pady=(12, 4))

        ctk.CTkLabel(
            self,
            text="Reconocimiento oficial de puntos salariales por títulos, escalafón o producción intelectual",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=Colors.TEXT_MUTED,
        ).pack(pady=(0, 8))

        sub_tabs = create_styled_tabview(self)
        sub_tabs.pack(fill="both", expand=True, padx=14, pady=6)

        tab_factores = sub_tabs.add("📜 Títulos y Escalafón")
        tab_produccion = sub_tabs.add("🔬 Producción Intelectual")

        prof_options = []
        for p in self.controller.profesores:
            pers = self.service.buscar_persona_por_id(p.idPersona)
            nom = f"{getattr(pers, 'primerNombre', '')} {getattr(pers, 'primerApellido', '')}" if pers else "Profesor"
            pts = getattr(p, "puntosSalariales", 0) or 0
            prof_options.append(f"{p.codigoProfesor} - {nom} [{pts} pts actual]")

        if not prof_options:
            prof_options = ["Sin docentes registrados"]

        self._construir_tab_factores(tab_factores, prof_options)
        self._construir_tab_produccion(tab_produccion, prof_options)

    def _construir_tab_factores(self, container: ctk.CTkFrame, prof_options: list[str]) -> None:
        scroll_f = ctk.CTkScrollableFrame(container, fg_color="transparent")
        scroll_f.pack(fill="both", expand=True, padx=6, pady=6)

        ctk.CTkLabel(scroll_f, text="Docente Beneficiario:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w", padx=4, pady=(4, 1))
        combo_prof_f = ctk.CTkComboBox(scroll_f, values=prof_options, width=400)
        combo_prof_f.pack(fill="x", padx=4, pady=(0, 8))

        ctk.CTkLabel(scroll_f, text="Tipo de Factor Salarial:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w", padx=4, pady=(4, 1))
        combo_tipo_f = ctk.CTkComboBox(
            scroll_f,
            values=[
                "TITULO_ACADEMICO",
                "CATEGORIA_DOCENTE",
                "EXPERIENCIA_CALIFICADA",
                "CARGO_DIRECCION_ACADEMICA",
            ],
            width=400,
        )
        combo_tipo_f.pack(fill="x", padx=4, pady=(0, 8))

        ctk.CTkLabel(scroll_f, text="Concepto / Denominación del Factor:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w", padx=4, pady=(4, 1))
        entry_nom_f = ctk.CTkEntry(scroll_f, placeholder_text="ej: Título de Doctorado en Ciencias de la Computación")
        entry_nom_f.pack(fill="x", padx=4, pady=(0, 8))

        ctk.CTkLabel(scroll_f, text="Puntos Salariales a Asignar (+):", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w", padx=4, pady=(4, 1))
        entry_pts_f = ctk.CTkEntry(scroll_f, placeholder_text="ej: 120")
        entry_pts_f.insert(0, "120")
        entry_pts_f.pack(fill="x", padx=4, pady=(0, 8))

        ctk.CTkLabel(scroll_f, text="Resolución del Comité de Puntaje (Acto Administrativo):", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w", padx=4, pady=(4, 1))
        entry_acto_f = ctk.CTkEntry(scroll_f, placeholder_text="ej: Resolución CIARP N° 045 de 2026")
        entry_acto_f.insert(0, "Resolución CIARP N° 045-2026")
        entry_acto_f.pack(fill="x", padx=4, pady=(0, 8))

        lbl_err_f = ctk.CTkLabel(scroll_f, text="", text_color="#EF4444", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"))
        lbl_err_f.pack(pady=4)

        def _guardar_factor():
            sel_p = combo_prof_f.get()
            if not sel_p or sel_p == "Sin docentes registrados":
                lbl_err_f.configure(text="⚠️ Seleccione un docente válido.")
                return
            cod = sel_p.split(" - ")[0].strip()
            prof = self.controller.gestor_personas.buscar_profesor_por_codigo(cod)
            if not prof:
                lbl_err_f.configure(text="⚠️ Docente no encontrado.")
                return

            nom_f = entry_nom_f.get().strip()
            if not nom_f:
                lbl_err_f.configure(text="⚠️ Ingrese el concepto del factor.")
                return

            try:
                pts_val = Decimal(entry_pts_f.get().strip())
                if pts_val <= 0:
                    raise ValueError
            except Exception:
                lbl_err_f.configure(text="⚠️ Ingrese un puntaje numérico positivo válido.")
                return

            self.service.reconocer_factor_salarial(
                id_profesor=prof.idProfesor,
                tipo_factor_str=combo_tipo_f.get(),
                nombre=nom_f,
                puntos=pts_val,
                acto_administrativo=entry_acto_f.get().strip(),
                fecha_reconocimiento=date.today(),
            )
            self.destroy()
            self.on_success()

        ctk.CTkButton(
            scroll_f,
            text="💾 Reconocer y Aplicar Puntos Salariales",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#006837",
            hover_color="#004D28",
            height=38,
            command=_guardar_factor,
        ).pack(fill="x", padx=4, pady=(8, 16))

    def _construir_tab_produccion(self, container: ctk.CTkFrame, prof_options: list[str]) -> None:
        scroll_p = ctk.CTkScrollableFrame(container, fg_color="transparent")
        scroll_p.pack(fill="both", expand=True, padx=6, pady=6)

        ctk.CTkLabel(scroll_p, text="Docente Autor:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w", padx=4, pady=(4, 1))
        combo_prof_p = ctk.CTkComboBox(scroll_p, values=prof_options, width=400)
        combo_prof_p.pack(fill="x", padx=4, pady=(0, 8))

        ctk.CTkLabel(scroll_p, text="Tipo de Obra Intelectual (MinCiencias):", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w", padx=4, pady=(4, 1))
        def _on_cambiar_tipo_prod(val: str) -> None:
            import re
            m = re.search(r"\((\d+)\s*pts\)", val)
            if m:
                entry_pts_prod.delete(0, "end")
                entry_pts_prod.insert(0, m.group(1))

        combo_tipo_prod = ctk.CTkComboBox(
            scroll_p,
            values=[
                "ARTICULO_A1 (15 pts)",
                "ARTICULO_A2 (12 pts)",
                "ARTICULO_B (8 pts)",
                "LIBRO_INVESTIGACION (20 pts)",
                "PATENTE_INVENCION (25 pts)",
                "SOFTWARE_REGISTRADO (15 pts)",
            ],
            width=400,
            command=_on_cambiar_tipo_prod,
        )
        combo_tipo_prod.pack(fill="x", padx=4, pady=(0, 8))

        ctk.CTkLabel(scroll_p, text="Título de la Obra o Producto:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w", padx=4, pady=(4, 1))
        entry_titulo = ctk.CTkEntry(scroll_p, placeholder_text="ej: Algoritmos Cuánticos para Optimización Universitaria")
        entry_titulo.pack(fill="x", padx=4, pady=(0, 8))

        ctk.CTkLabel(scroll_p, text="Revista / Editorial / Entidad Patrocinadora:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w", padx=4, pady=(4, 1))
        entry_editorial = ctk.CTkEntry(scroll_p, placeholder_text="ej: IEEE Transactions on Software Engineering")
        entry_editorial.pack(fill="x", padx=4, pady=(0, 8))

        row_aut = ctk.CTkFrame(scroll_p, fg_color="transparent")
        row_aut.pack(fill="x", padx=4, pady=(4, 8))
        row_aut.columnconfigure((0, 1), weight=1)

        f_aut = ctk.CTkFrame(row_aut, fg_color="transparent")
        f_aut.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkLabel(f_aut, text="Número Total de Autores:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w")
        combo_autores = ctk.CTkComboBox(f_aut, values=["1 (100%)", "2 (50%)", "3 (33%)", "4 (25%)", "5 o más (20%)"])
        combo_autores.pack(fill="x", pady=2)

        f_pts_b = ctk.CTkFrame(row_aut, fg_color="transparent")
        f_pts_b.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        ctk.CTkLabel(f_pts_b, text="Puntos Base Producto:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(anchor="w")
        entry_pts_prod = ctk.CTkEntry(f_pts_b)
        entry_pts_prod.insert(0, "15")
        entry_pts_prod.pack(fill="x", pady=2)

        lbl_err_p = ctk.CTkLabel(scroll_p, text="", text_color="#EF4444", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"))
        lbl_err_p.pack(pady=4)

        def _guardar_prod():
            sel_p = combo_prof_p.get()
            if not sel_p or "Sin docentes" in sel_p:
                lbl_err_p.configure(text="⚠️ Seleccione un docente válido.")
                return
            cod = sel_p.split(" - ")[0].strip() if " - " in sel_p else sel_p.strip()
            prof = next((p for p in self.controller.profesores if str(getattr(p, "codigoProfesor", "")).strip() == cod), None)
            if not prof:
                prof = self.controller.gestor_personas.buscar_profesor_por_codigo(cod)
            if not prof:
                lbl_err_p.configure(text="⚠️ Docente no encontrado.")
                return

            tit = entry_titulo.get().strip()
            if not tit:
                lbl_err_p.configure(text="⚠️ Ingrese el título de la obra.")
                return

            try:
                pts_base = Decimal(entry_pts_prod.get().strip())
            except Exception:
                lbl_err_p.configure(text="⚠️ Ingrese un puntaje válido.")
                return

            aut_str = (combo_autores.get() or "").strip()
            n_aut = int(aut_str.split(" ")[0]) if aut_str and aut_str[0].isdigit() else 1
            coaut = Decimal("1.0") / Decimal(str(max(n_aut, 1)))
            pts_prof = round(pts_base * coaut, 2)

            tipo_prod_clean = combo_tipo_prod.get().split(" ")[0]
            editorial_clean = entry_editorial.get().strip()

            self.service.reconocer_produccion_academica(
                id_profesor=prof.idProfesor,
                tipo_prod=tipo_prod_clean,
                titulo=tit,
                editorial=editorial_clean,
                num_autores=n_aut,
                puntos_docente=pts_prof,
            )
            self.destroy()
            self.on_success()

        ctk.CTkButton(
            scroll_p,
            text="💾 Registrar y Reconocer Producción Intelectual",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#006837",
            hover_color="#004D28",
            height=38,
            command=_guardar_prod,
        ).pack(fill="x", padx=4, pady=(8, 16))
