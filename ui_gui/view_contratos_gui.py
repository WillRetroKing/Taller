"""Vista de Contratación Docente (Planta, Ocasional, Catedrático, Ad Honorem) y Factores Salariales."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
import customtkinter as ctk
from typing import TYPE_CHECKING

from ui_gui.components import PITAGridTable, create_badge
from modelo_datos import CategoriaDocente, Contrato, FactorSalarial, ProduccionAcademica, TipoFactor

if TYPE_CHECKING:
    from ui_gui.gui_controller import PITAController


class ContratosViewGUI(ctk.CTkFrame):
    """Vista de gestión, factores salariales y validación de contratación docente."""

    def __init__(self, parent: ctk.CTk, controller: PITAController) -> None:
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        self._crear_interfaz()

    def _crear_interfaz(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(
            header,
            text="📝 Gestión de Contratación y Factores Salariales (Dec. 1279)",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#F8FAFC",
        ).pack(side="left")

        h_buttons = ctk.CTkFrame(header, fg_color="transparent")
        h_buttons.pack(side="right")

        btn_nuevo_contrato = ctk.CTkButton(
            h_buttons,
            text="➕ Registrar Contrato",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#10B981",
            hover_color="#059669",
            corner_radius=8,
            command=self._abrir_modal_nuevo_contrato,
        )
        btn_nuevo_contrato.pack(side="left", padx=5)

        btn_reconocer_puntos = ctk.CTkButton(
            h_buttons,
            text="🎓 Reconocer Puntos / Productividad",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#6366F1",
            hover_color="#4F46E5",
            corner_radius=8,
            command=self._abrir_modal_reconocer_puntos,
        )
        btn_reconocer_puntos.pack(side="left", padx=5)

        # Tabview
        self.tabview = ctk.CTkTabview(self, fg_color="transparent")
        self.tabview.pack(fill="both", expand=True, padx=10, pady=5)

        self.tab_contratos = self.tabview.add("📜 Contratos Vigentes")
        self.tab_factores = self.tabview.add("⭐ Puntos y Producción Académica")

        self._llenar_tab_contratos()
        self._llenar_tab_factores()

    def _llenar_tab_contratos(self) -> None:
        for w in self.tab_contratos.winfo_children():
            w.destroy()

        headers = ["Código Contrato", "Docente", "Tipo Contratación", "Horas/Sem", "Asignación Básica", "Vigencia", "Estado", "Acción"]
        col_weights = [2, 3, 3, 2, 3, 3, 2, 2]
        col_mins = [100, 160, 140, 80, 130, 140, 100, 90]

        table = PITAGridTable(self.tab_contratos, headers=headers, col_weights=col_weights, col_mins=col_mins)
        table.pack(fill="both", expand=True, padx=5, pady=5)

        if not self.controller.contratos:
            ctk.CTkLabel(table, text="No hay contratos vigentes registrados.", text_color="#94A3B8").pack(pady=20)
            return

        for cont in self.controller.contratos:
            prof = next((p for p in self.controller.profesores if getattr(p, "idProfesor", None) == getattr(cont, "idProfesor", None)), None)
            pers = next((p for p in self.controller.personas if prof and getattr(p, "idPersona", None) == getattr(prof, "idPersona", None)), None)
            nom_prof = f"{getattr(pers, 'primerNombre', '')} {getattr(pers, 'primerApellido', '')}" if pers else "Docente"

            asig = str(getattr(cont, "salarioBase", "0") or getattr(cont, "asignacionBasicaMensual", "0"))
            asig_fmt = f"$ {int(float(asig)):,} COP" if asig.replace(".","").isdigit() else asig
            est = str(getattr(cont, "estado", "ACTIVO"))

            badge_tuple = ("badge", est, "cancelado" if est == "TERMINADO" else "active")

            btn_list = [("✏️", lambda c=cont: self._editar_contrato(c), "#334155", "#475569", 30, 28)]
            if est != "TERMINADO":
                btn_list.append(("🚫", lambda c_id=cont.idContrato: self._terminar_contrato(c_id), "#EF4444", "#DC2626", 30, 28))
            act_spec = ("actions", btn_list)

            cells = [
                (getattr(cont, "numeroContrato", "N/A"), "#F59E0B"),
                (nom_prof, "#F8FAFC"),
                str(getattr(cont, "tipoContrato", "DOCENTE")),
                f"{getattr(cont, 'horasSemanales', 40)}h",
                (asig_fmt, "#10B981"),
                f"{getattr(cont, 'fechaInicio', '')} al {getattr(cont, 'fechaFin', '')}",
                badge_tuple,
                act_spec,
            ]
            table.add_row_items(cells, is_highlighted=(est == "TERMINADO"))

    def _llenar_tab_factores(self) -> None:
        for w in self.tab_factores.winfo_children():
            w.destroy()

        headers = ["Docente", "Factor Salarial", "Puntos Otorgados", "Acto Administrativo", "Estado"]
        col_weights = [4, 4, 3, 4, 2]
        col_mins = [180, 180, 120, 180, 100]

        table = PITAGridTable(self.tab_factores, headers=headers, col_weights=col_weights, col_mins=col_mins)
        table.pack(fill="both", expand=True, padx=5, pady=5)

        if not self.controller.factores:
            ctk.CTkLabel(table, text="No hay factores salariales registrados.", text_color="#94A3B8").pack(pady=20)
            return

        for fac in self.controller.factores:
            prof = next((p for p in self.controller.profesores if getattr(p, "idProfesor", None) == getattr(fac, "idProfesor", None)), None)
            pers = next((p for p in self.controller.personas if prof and getattr(p, "idPersona", None) == getattr(prof, "idPersona", None)), None)
            nom_prof = f"{getattr(pers, 'primerNombre', '')} {getattr(pers, 'primerApellido', '')}" if pers else "Docente"

            cells = [
                (nom_prof, "#F8FAFC"),
                getattr(fac, "nombre", "Factor"),
                (f"+{getattr(fac, 'puntosReconocidos', 0)} pts", "#F59E0B"),
                getattr(fac, "actoAdministrativo", "N/A"),
                ("badge", "● APROBADO", "active"),
            ]
            table.add_row_items(cells)

    def _abrir_modal_nuevo_contrato(self) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title("📝 Registrar Contrato Docente")
        dialog.geometry("450x550")
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Vincular Docente y Especificar Tipo de Contrato", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)

        ctk.CTkLabel(dialog, text="Docente:").pack(anchor="w", padx=20)
        prof_options = [
            f"{p.codigoProfesor} - {next((pers.primerNombre + ' ' + pers.primerApellido for pers in self.controller.personas if pers.idPersona == p.idPersona), 'Profesor')}"
            for p in self.controller.profesores
        ] or ["Sin docentes"]
        combo_prof = ctk.CTkComboBox(dialog, values=prof_options)
        combo_prof.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(dialog, text="Modalidad de Vinculación:").pack(anchor="w", padx=20, pady=(10, 0))
        combo_tipo = ctk.CTkComboBox(dialog, values=["DOCENTE_PLANTA", "DOCENTE_OCASIONAL", "DOCENTE_CATEDRATICO", "DOCENTE_AD_HONOREM"])
        combo_tipo.pack(fill="x", padx=20, pady=5)

        entry_num = ctk.CTkEntry(dialog, placeholder_text="Número de Contrato (ej: CONT-2026-05)")
        entry_num.pack(fill="x", padx=20, pady=10)

        entry_horas = ctk.CTkEntry(dialog, placeholder_text="Horas Semanales (ej: 40 para Planta, 12 para Cátedra)")
        entry_horas.pack(fill="x", padx=20, pady=5)

        entry_monto = ctk.CTkEntry(dialog, placeholder_text="Asignación Básica Mensual ($)")
        entry_monto.pack(fill="x", padx=20, pady=5)

        def _guardar():
            num = entry_num.get().strip()
            hrs = entry_horas.get().strip()
            monto = entry_monto.get().strip()
            sel_p = combo_prof.get()
            tipo = combo_tipo.get()

            if not num or not self.controller.profesores:
                return

            cod_p = sel_p.split(" - ")[0]
            prof = self.controller.gestor_personas.buscar_profesor_por_codigo(cod_p)

            if prof:
                c = Contrato(
                    idContrato=len(self.controller.contratos) + 1,
                    idPersona=prof.idPersona,
                    numeroContrato=num,
                    tipoContrato=tipo,
                    fechaInicio=date.today(),
                    fechaFin=date(2026, 12, 31),
                    dedicacion=Dedicacion.TIEMPO_COMPLETO if hrs == "40" else Dedicacion.HORA_CATEDRA,
                    horasSemanales=Decimal(hrs) if hrs.isdigit() else Decimal("40"),
                    salarioBase=Decimal(monto) if monto.isdigit() else Decimal("3000000"),
                    estado="ACTIVO",
                )
                self.controller.contratos.append(c)
                self.controller._recrear_gestores()
                dialog.destroy()
                self.actualizar()

        ctk.CTkButton(dialog, text="💾 Registrar Contrato", fg_color="#006837", hover_color="#004D28", command=_guardar).pack(pady=20)

    def _abrir_modal_reconocer_puntos(self) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title("⭐ Reconocer Puntos Decreto 1279")
        dialog.geometry("450x450")
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Reconocimiento de Puntos y Productividad", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)

        prof_options = [
            f"{p.codigoProfesor} - {next((pers.primerNombre + ' ' + pers.primerApellido for pers in self.controller.personas if pers.idPersona == p.idPersona), 'Profesor')}"
            for p in self.controller.profesores
        ] or ["Sin docentes"]
        combo_prof = ctk.CTkComboBox(dialog, values=prof_options)
        combo_prof.pack(fill="x", padx=20, pady=5)

        entry_nombre = ctk.CTkEntry(dialog, placeholder_text="Descripción Factor / Título / Publicación")
        entry_nombre.pack(fill="x", padx=20, pady=10)

        entry_puntos = ctk.CTkEntry(dialog, placeholder_text="Puntos a Otorgar (ej: 40 para Maestría, 120 para Doctorado)")
        entry_puntos.pack(fill="x", padx=20, pady=5)

        entry_acto = ctk.CTkEntry(dialog, placeholder_text="Acto Administrativo (ej: Res. Rectoral 105)")
        entry_acto.pack(fill="x", padx=20, pady=5)

        def _guardar_puntos():
            desc = entry_nombre.get().strip()
            pts = entry_puntos.get().strip()
            acto = entry_acto.get().strip()
            sel_p = combo_prof.get()

            if not desc or not pts.isdigit():
                return

            cod_p = sel_p.split(" - ")[0]
            prof = self.controller.gestor_personas.buscar_profesor_por_codigo(cod_p)

            if prof:
                fac = FactorSalarial(
                    idFactor=len(self.controller.factores) + 1,
                    idProfesor=prof.idProfesor,
                    tipoFactor=TipoFactor.TITULO_ACADEMICO,
                    nombre=desc,
                    puntosReconocidos=Decimal(pts),
                    fechaReconocimiento=date.today(),
                    actoAdministrativo=acto or "Res. Rectoral",
                    estado="ACTIVO",
                )
                self.controller.factores.append(fac)

                # Sumar puntos al profesor
                p_actual = Decimal(str(getattr(prof, "puntosSalariales", "0")))
                prof.puntosSalariales = p_actual + Decimal(pts)

                self.controller._recrear_gestores()
                dialog.destroy()
                self.actualizar()

        ctk.CTkButton(dialog, text="💾 Otorgar Puntos", fg_color="#006837", hover_color="#004D28", command=_guardar_puntos).pack(pady=20)

    def _editar_contrato(self, cont: Contrato) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"✏️ Editar Contrato {cont.numeroContrato}")
        dialog.geometry("450x450")
        dialog.grab_set()

        ctk.CTkLabel(dialog, text=f"Modificar Contrato: {cont.numeroContrato}", font=ctk.CTkFont(size=15, weight="bold")).pack(pady=12)

        entry_sal = ctk.CTkEntry(dialog)
        asig = str(getattr(cont, "salarioBase", "0") or getattr(cont, "asignacionBasicaMensual", "0"))
        entry_sal.insert(0, asig)
        entry_sal.pack(fill="x", padx=20, pady=6)

        entry_hrs = ctk.CTkEntry(dialog)
        entry_hrs.insert(0, str(getattr(cont, "horasSemanales", 40)))
        entry_hrs.pack(fill="x", padx=20, pady=6)

        def _guardar():
            v_sal = entry_sal.get().strip()
            if v_sal:
                cont.salarioBase = Decimal(v_sal)
            if entry_hrs.get().strip().isdigit():
                cont.horasSemanales = int(entry_hrs.get().strip())
            self.controller._recrear_gestores()
            dialog.destroy()
            self.actualizar()

        ctk.CTkButton(dialog, text="💾 Guardar Cambios", font=ctk.CTkFont(size=12, weight="bold"), fg_color="#10B981", hover_color="#059669", height=36, command=_guardar).pack(pady=20)

    def _terminar_contrato(self, id_contrato: int) -> None:
        cont = next((c for c in self.controller.contratos if c.idContrato == id_contrato), None)
        if cont:
            cont.estado = "TERMINADO"
            self.controller._recrear_gestores()
            self.actualizar()

    def actualizar(self) -> None:
        for widget in self.winfo_children():
            widget.destroy()
        self._crear_interfaz()
