"""Vista del subsistema de contratos: vinculación, consulta, modificación
y terminación de contratos."""

from __future__ import annotations

from modelo_datos import Contrato, Dedicacion
from ui.base_view import BaseView


class ContractsView(BaseView):
    titulo = "SUBSISTEMA DE CONTRATOS"
    color = "yellow"

    def __init__(self, gestor_contratos, gestor_personas, gestor_nomina) -> None:
        super().__init__()
        self._gestor_contratos = gestor_contratos
        self._gestor_personas = gestor_personas
        self._gestor_nomina = gestor_nomina

    def opciones(self):
        return [
            ("1", "Crear contrato", self.crear_contrato),
            ("2", "Buscar contrato vigente de una persona", self.buscar_vigente),
            ("3", "Listar contratos de un profesor", self.listar_contratos),
            ("4", "Modificar contrato", self.modificar_contrato),
            ("5", "Terminar contrato", self.terminar_contrato),
        ]

    # ------------------------------------------------------------------
    # Búsqueda y selección de personas para contrato
    # ------------------------------------------------------------------
    def _seleccionar_persona(self) -> Any | None:
        """Mostrar personas disponibles y dejar que el usuario seleccione una.

        Returns: La persona seleccionada o None si cancela.
        """
        from modelo_datos import Persona

        # Listar personas activas
        personas = self._gestor_personas.listar(
            incluir_inactivos=False
        ) if hasattr(self._gestor_personas, 'listar') else []

        if not personas:
            self.mostrar_alerta("No hay personas registradas en el sistema.")
            return None

        # Mostrar personas con documento y nombres
        self.console.clear()
        lineas = [f"[bold {self.color}]Seleccionar persona[/bold {self.color}]", "-" * 60]
        for i, p in enumerate(personas, 1):
            doc = f"{p.tipoDocumento} {p.numeroDocumento or 'N/A'}" if hasattr(p, 'tipoDocumento') else "N/A"
            nombres = f"{p.primerNombre or ''} {p.segundoNombre or ''}".strip() if hasattr(p, 'primerNombre') else "N/A"
            apellidos = f"{p.primerApellido or ''} {p.segundoApellido or ''}".strip() if hasattr(p, 'primerApellido') else "N/A"
            lineas.append(f"{i}. Doc: {doc}, Nombres: {nombres} {apellidos}, ID: {p.idPersona}")
        lineas.append("0. Cancelar")
        lineas.append("-" * 60)
        self.console.print(Panel("\n".join(lineas), border_style=self.color))

        while True:
            try:
                eleccion = Prompt.ask(f"\nSeleccione una persona (1-{len(personas)}) o 0 para cancelar", default="0").strip()
                if eleccion == "0":
                    return None
                idx = int(eleccion)
                if 1 <= idx <= len(personas):
                    return personas[idx - 1]
                self.mostrar_error(f"Por favor seleccione un número entre 1 y {len(personas)}")
            except (ValueError, EOFError, KeyboardInterrupt):
                return None

    # ------------------------------------------------------------------
    def crear_contrato(self) -> None:
        persona = self._seleccionar_persona()
        if persona is None:
            return

        contrato = Contrato(
            idPersona=persona.idPersona,
            numeroContrato=self.pedir_texto("Número de contrato"),
            tipoContrato=self.pedir_opcion(
                "Tipo de contrato",
                ["OCASIONAL", "CATEDRATICO", "PLANTA", "ADMINISTRATIVO"],
            ),
            fechaInicio=self.pedir_fecha("Fecha de inicio"),
            fechaFin=self.pedir_fecha("Fecha de fin"),
            dedicacion=Dedicacion(
                self.pedir_opcion("Dedicación", [d.value for d in Dedicacion])
            ),
            horasSemanalesAsignadas=self.pedir_decimal("Horas semanales asignadas", obligatorio=False),
            factorSalarialSMMLV=self.pedir_decimal("Factor salarial (SMMLV)", obligatorio=False),
            salarioMensualPactado=self.pedir_decimal("Salario mensual pactado", obligatorio=False),
            valorHora=self.pedir_decimal("Valor hora (cátedra)", obligatorio=False),
            aplicaAuxilioTransporte=self.pedir_bool("¿Aplica auxilio de transporte?", defecto=True),
            claseARL=self.pedir_opcion("Clase ARL", ["I", "II", "III", "IV", "V"]),
            actoAdministrativo=self.pedir_texto("Acto administrativo", obligatorio=False),
            observaciones=self.pedir_texto("Observaciones", obligatorio=False),
            estado="ACTIVO",
        )
        jubilado = self.pedir_bool("¿La persona es pensionada/jubilada?", defecto=False)
        creado = self._gestor_contratos.crear_contrato(contrato, jubilado=jubilado)
        self.mostrar_exito(f"Contrato creado con ID {creado.idContrato}.")

    def buscar_vigente(self) -> None:
        persona = self._seleccionar_persona()
        if persona is None:
            return

        contrato = self._gestor_contratos.buscar_contrato_vigente(persona.idPersona)
        if contrato is None:
            self.mostrar_alerta("La persona no tiene contrato vigente.")
            return
        self.mostrar_tabla(
            "Contrato vigente",
            ["ID", "Número", "Tipo", "Inicio", "Fin", "Dedicación", "Estado"],
            [[contrato.idContrato, contrato.numeroContrato, contrato.tipoContrato,
              contrato.fechaInicio, contrato.fechaFin,
              getattr(contrato.dedicacion, "value", contrato.dedicacion),
              contrato.estado]],
        )

    def listar_contratos(self) -> None:
        persona = self._seleccionar_persona()
        if persona is None:
            return

        contratos = self._gestor_contratos.listar_contratos_profesor(persona.idPersona)
        self.mostrar_tabla(
            "Contratos de la persona",
            ["ID", "Número", "Tipo", "Inicio", "Fin", "Estado"],
            [[c.idContrato, c.numeroContrato, c.tipoContrato,
              c.fechaInicio, c.fechaFin, c.estado] for c in contratos],
        )

    def modificar_contrato(self) -> None:
        # Listar contratos de la persona primero
        persona = self._seleccionar_persona()
        if persona is None:
            return

        contratos = self._gestor_contratos.listar_contratos_profesor(persona.idPersona)
        if not contratos:
            self.mostrar_alerta("La persona no tiene contratos registrados.")
            self.pausar()
            return

        # Mostrar contratos para que el usuario elija
        self.console.clear()
        lineas = [f"[bold {self.color}]Seleccionar contrato[/bold {self.color}]", "-" * 60]
        for i, c in enumerate(contratos, 1):
            lineas.append(f"{i}. ID {c.idContrato}, Número: {c.numeroContrato}, Tipo: {c.tipoContrato}, Estado: {c.estado}")
        lineas.append("0. Cancelar")
        lineas.append("-" * 60)
        self.console.print(Panel("\n".join(lineas), border_style=self.color))

        while True:
            try:
                eleccion = Prompt.ask(f"\nSeleccione un contrato (1-{len(contratos)}) o 0 para cancelar", default="0").strip()
                if eleccion == "0":
                    return
                idx = int(eleccion)
                if 1 <= idx <= len(contratos):
                    id_contrato = contratos[idx - 1].idContrato
                    break
                self.mostrar_error(f"Por favor seleccione un número entre 1 y {len(contratos)}")
            except (ValueError, EOFError, KeyboardInterrupt):
                return

        # Ahora permitir modificar el contrato
        campo = self.pedir_opcion(
            "Campo a modificar",
            ["observaciones", "horasSemanalesAsignadas", "salarioMensualPactado", "fechaFin"],
        )
        if campo == "fechaFin":
            valor = self.pedir_fecha("Nueva fecha de fin")
        elif campo in ("horasSemanalesAsignadas", "salarioMensualPactado"):
            valor = self.pedir_decimal(f"Nuevo valor de {campo}")
        else:
            valor = self.pedir_texto(f"Nuevo valor de {campo}")
        self._gestor_contratos.modificar_contrato(id_contrato, **{campo: valor})
        self.mostrar_exito("Contrato modificado.")

    def terminar_contrato(self) -> None:
        # Listar contratos de la persona primero
        persona = self._seleccionar_persona()
        if persona is None:
            return

        contratos = self._gestor_contratos.listar_contratos_profesor(persona.idPersona)
        if not contratos:
            self.mostrar_alerta("La persona no tiene contratos registrados.")
            self.pausar()
            return

        # Mostrar contratos para que el usuario elija
        self.console.clear()
        lineas = [f"[bold {self.color}]Seleccionar contrato[/bold {self.color}]", "-" * 60]
        for i, c in enumerate(contratos, 1):
            lineas.append(f"{i}. ID {c.idContrato}, Número: {c.numeroContrato}, Tipo: {c.tipoContrato}, Estado: {c.estado}")
        lineas.append("0. Cancelar")
        lineas.append("-" * 60)
        self.console.print(Panel("\n".join(lineas), border_style=self.color))

        while True:
            try:
                eleccion = Prompt.ask(f"\nSeleccione un contrato (1-{len(contratos)}) o 0 para cancelar", default="0").strip()
                if eleccion == "0":
                    return
                idx = int(eleccion)
                if 1 <= idx <= len(contratos):
                    id_contrato = contratos[idx - 1].idContrato
                    break
                self.mostrar_error(f"Por favor seleccione un número entre 1 y {len(contratos)}")
            except (ValueError, EOFError, KeyboardInterrupt):
                return

        causal = self.pedir_opcion(
            "Causal de terminación",
            ["RENUNCIA", "VENCIMIENTO", "INCUMPLIMIENTO", "MUTUO_ACUERDO", "JUBILACION"],
        )
        documento = self.pedir_texto("Documento soporte de la terminación")
        if self.pedir_bool(f"¿Confirma terminar el contrato {id_contrato}?"):
            self._gestor_contratos.terminar_contrato(id_contrato, causal, documento)
            self.mostrar_exito("Contrato terminado.")