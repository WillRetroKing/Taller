"""Componente reutilizable de UI para formulario de Información Personal y de Contacto."""

from __future__ import annotations

from datetime import datetime
from typing import Any
import customtkinter as ctk

from ui_gui.theme import Colors
from dominio.modelo_datos import Persona


class PersonaFormCard(ctk.CTkFrame):
    """Tarjeta reutilizable con campos de Identificación y Contacto Personal."""

    def __init__(self, parent: ctk.CTkBaseClass, incluir_documento: bool = True) -> None:
        super().__init__(
            parent,
            fg_color=Colors.BG_CARD,
            corner_radius=8,
            border_width=1,
            border_color=Colors.BORDER_SUBTLE,
        )
        self.incluir_documento = incluir_documento
        self.pack(fill="x", pady=6)
        self._construir_campos()

    def _construir_campos(self) -> None:
        ctk.CTkLabel(
            self,
            text="👤 1. Información Personal y de Contacto",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#38BDF8",
        ).pack(anchor="w", padx=15, pady=(12, 8))

        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(fill="x", padx=15, pady=(0, 12))
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        row_idx = 0
        if self.incluir_documento:
            ctk.CTkLabel(grid, text="Tipo Documento *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=row_idx, column=0, sticky="w", padx=5, pady=(2, 0))
            ctk.CTkLabel(grid, text="Número de Documento *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=row_idx, column=1, sticky="w", padx=5, pady=(2, 0))
            row_idx += 1

            self.combo_tdoc = ctk.CTkComboBox(grid, values=["CC", "TI", "CE", "PASAPORTE"])
            self.combo_tdoc.set("CC")
            self.combo_tdoc.grid(row=row_idx, column=0, sticky="ew", padx=5, pady=(2, 8))

            self.entry_doc = ctk.CTkEntry(grid, placeholder_text="ej: 1065890123")
            self.entry_doc.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=(2, 8))
            row_idx += 1

        ctk.CTkLabel(grid, text="Primer Nombre *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=row_idx, column=0, sticky="w", padx=5, pady=(2, 0))
        ctk.CTkLabel(grid, text="Segundo Nombre", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=row_idx, column=1, sticky="w", padx=5, pady=(2, 0))
        row_idx += 1

        self.entry_nom1 = ctk.CTkEntry(grid, placeholder_text="ej: Juan")
        self.entry_nom1.grid(row=row_idx, column=0, sticky="ew", padx=5, pady=(2, 8))

        self.entry_nom2 = ctk.CTkEntry(grid, placeholder_text="ej: Carlos (opcional)")
        self.entry_nom2.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=(2, 8))
        row_idx += 1

        ctk.CTkLabel(grid, text="Primer Apellido *", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").grid(row=row_idx, column=0, sticky="w", padx=5, pady=(2, 0))
        ctk.CTkLabel(grid, text="Segundo Apellido", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=row_idx, column=1, sticky="w", padx=5, pady=(2, 0))
        row_idx += 1

        self.entry_ape1 = ctk.CTkEntry(grid, placeholder_text="ej: Pérez")
        self.entry_ape1.grid(row=row_idx, column=0, sticky="ew", padx=5, pady=(2, 8))

        self.entry_ape2 = ctk.CTkEntry(grid, placeholder_text="ej: Gómez (opcional)")
        self.entry_ape2.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=(2, 8))
        row_idx += 1

        ctk.CTkLabel(grid, text="Teléfono / Celular", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=row_idx, column=0, sticky="w", padx=5, pady=(2, 0))
        ctk.CTkLabel(grid, text="Fecha Nacimiento (AAAA-MM-DD)", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=row_idx, column=1, sticky="w", padx=5, pady=(2, 0))
        row_idx += 1

        self.entry_tel = ctk.CTkEntry(grid, placeholder_text="ej: 3001234567")
        self.entry_tel.grid(row=row_idx, column=0, sticky="ew", padx=5, pady=(2, 8))

        self.entry_fnac = ctk.CTkEntry(grid, placeholder_text="ej: 1998-05-15")
        self.entry_fnac.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=(2, 8))
        row_idx += 1

        ctk.CTkLabel(grid, text="Correo Institucional", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=row_idx, column=0, sticky="w", padx=5, pady=(2, 0))
        ctk.CTkLabel(grid, text="Correo Personal", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=row_idx, column=1, sticky="w", padx=5, pady=(2, 0))
        row_idx += 1

        self.entry_cinst = ctk.CTkEntry(grid, placeholder_text="ej: jperez@unicesar.edu.co")
        self.entry_cinst.grid(row=row_idx, column=0, sticky="ew", padx=5, pady=(2, 8))

        self.entry_cpers = ctk.CTkEntry(grid, placeholder_text="ej: jperez@gmail.com")
        self.entry_cpers.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=(2, 8))
        row_idx += 1

        ctk.CTkLabel(grid, text="Dirección", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=row_idx, column=0, sticky="w", padx=5, pady=(2, 0))
        ctk.CTkLabel(grid, text="Ciudad de Residencia", font=ctk.CTkFont(size=11), text_color="#94A3B8").grid(row=row_idx, column=1, sticky="w", padx=5, pady=(2, 0))
        row_idx += 1

        self.entry_dir = ctk.CTkEntry(grid, placeholder_text="ej: Calle 16 # 14-25")
        self.entry_dir.grid(row=row_idx, column=0, sticky="ew", padx=5, pady=(2, 4))

        self.entry_ciu = ctk.CTkEntry(grid, placeholder_text="ej: Valledupar")
        self.entry_ciu.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=(2, 4))

    def poblar_desde_persona(self, persona: Persona | None) -> None:
        if not persona:
            return
        if self.incluir_documento:
            self.combo_tdoc.set(getattr(persona, "tipoDocumento", "CC") or "CC")
            self.entry_doc.delete(0, "end")
            self.entry_doc.insert(0, getattr(persona, "numeroDocumento", "") or "")

        self.entry_nom1.delete(0, "end")
        self.entry_nom1.insert(0, getattr(persona, "primerNombre", "") or "")

        self.entry_nom2.delete(0, "end")
        self.entry_nom2.insert(0, getattr(persona, "segundoNombre", "") or "")

        self.entry_ape1.delete(0, "end")
        self.entry_ape1.insert(0, getattr(persona, "primerApellido", "") or "")

        self.entry_ape2.delete(0, "end")
        self.entry_ape2.insert(0, getattr(persona, "segundoApellido", "") or "")

        self.entry_tel.delete(0, "end")
        self.entry_tel.insert(0, getattr(persona, "telefono", "") or "")

        if getattr(persona, "fechaNacimiento", None):
            self.entry_fnac.delete(0, "end")
            self.entry_fnac.insert(0, str(persona.fechaNacimiento))

        self.entry_cinst.delete(0, "end")
        self.entry_cinst.insert(0, getattr(persona, "correoInstitucional", "") or "")

        self.entry_cpers.delete(0, "end")
        self.entry_cpers.insert(0, getattr(persona, "correoPersonal", "") or "")

        self.entry_dir.delete(0, "end")
        self.entry_dir.insert(0, getattr(persona, "direccion", "") or "")

        self.entry_ciu.delete(0, "end")
        self.entry_ciu.insert(0, getattr(persona, "ciudadResidencia", "") or "")

    def extraer_datos(self) -> tuple[dict[str, Any] | None, str]:
        nom1 = self.entry_nom1.get().strip()
        ape1 = self.entry_ape1.get().strip()
        if not nom1 or not ape1:
            return None, "El primer nombre y el primer apellido son obligatorios."

        doc = self.entry_doc.get().strip() if self.incluir_documento else ""
        if self.incluir_documento and not doc:
            return None, "El número de documento es obligatorio."

        fnac_str = self.entry_fnac.get().strip()
        f_nac = None
        if fnac_str:
            try:
                f_nac = datetime.strptime(fnac_str, "%Y-%m-%d").date()
            except ValueError:
                return None, "Formato de Fecha de Nacimiento inválido. Use AAAA-MM-DD (ej: 1998-05-15)."

        datos = {
            "primerNombre": nom1,
            "segundoNombre": self.entry_nom2.get().strip() or None,
            "primerApellido": ape1,
            "segundoApellido": self.entry_ape2.get().strip() or None,
            "telefono": self.entry_tel.get().strip() or None,
            "fechaNacimiento": f_nac,
            "correoInstitucional": self.entry_cinst.get().strip() or None,
            "correoPersonal": self.entry_cpers.get().strip() or None,
            "direccion": self.entry_dir.get().strip() or None,
            "ciudadResidencia": self.entry_ciu.get().strip() or None,
        }
        if self.incluir_documento:
            datos["tipoDocumento"] = self.combo_tdoc.get()
            datos["numeroDocumento"] = doc

        return datos, ""
