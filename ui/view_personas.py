"""Vista del subsistema de personas: registro y consulta de personas,
estudiantes, profesores y administrativos."""

from __future__ import annotations

from modelo_datos import (
    Administrativo,
    Dedicacion,
    EstadoAcademico,
    Estudiante,
    Persona,
    Profesor,
    TipoProfesor,
)
from ui.base_view import BaseView


class PeopleView(BaseView):
    titulo = "SUBSISTEMA DE PERSONAS"
    color = "green"

    def __init__(self, gestor_personas, gestor_academico, gestor_nomina) -> None:
        super().__init__()
        self._gestor_personas = gestor_personas
        self._gestor_academico = gestor_academico
        self._gestor_nomina = gestor_nomina

    def opciones(self):
        return [
            ("1", "Registrar persona", self.crear_persona),
            ("2", "Registrar estudiante", self.crear_estudiante),
            ("3", "Registrar profesor", self.crear_profesor),
            ("4", "Registrar administrativo", self.crear_administrativo),
            ("5", "Buscar persona por documento", self.buscar_por_documento),
            ("6", "Listar estudiantes por programa", self.listar_estudiantes),
            ("7", "Listar profesores por programa", self.listar_profesores),
            ("8", "Desactivar persona", self.desactivar_persona),
        ]

    # ------------------------------------------------------------------
    def _pedir_datos_persona(self) -> Persona:
        return Persona(
            tipoDocumento=self.pedir_opcion(
                "Tipo de documento", ["CC", "TI", "CE", "PASAPORTE"]
            ),
            numeroDocumento=self.pedir_texto("Número de documento"),
            primerNombre=self.pedir_texto("Primer nombre"),
            segundoNombre=self.pedir_texto("Segundo nombre", obligatorio=False),
            primerApellido=self.pedir_texto("Primer apellido"),
            segundoApellido=self.pedir_texto("Segundo apellido", obligatorio=False),
            fechaNacimiento=self.pedir_fecha("Fecha de nacimiento", obligatorio=False),
            direccion=self.pedir_texto("Dirección", obligatorio=False),
            telefono=self.pedir_texto("Teléfono", obligatorio=False),
            correoPersonal=self.pedir_texto("Correo personal", obligatorio=False),
            correoInstitucional=self.pedir_texto("Correo institucional", obligatorio=False),
            ciudadResidencia=self.pedir_texto("Ciudad de residencia", obligatorio=False),
        )

    def crear_persona(self) -> None:
        persona = self._gestor_personas.crear_persona(self._pedir_datos_persona())
        self.mostrar_exito(f"Persona registrada con ID {persona.idPersona}.")

    # ------------------------------------------------------------------
    # Búsqueda y selección de entidades por criterios naturales
    # ------------------------------------------------------------------
    def _seleccionar_persona(self, titulo: str = "Seleccionar persona") -> Persona | None:
        """Mostrar una búsqueda de personas y dejar que el usuario seleccione una.

        Permite buscar por número de documento o mostrar una lista para elegir.
        Retorna la persona seleccionada o None si cancela.
        """
        while True:
            self.console.clear()
            print("\n¿Cómo desea buscar?")
            print("1. Por número de documento")
            print("2. Ver todas las personas (lista larga)")
            print("0. Cancelar")
            opcion = Prompt.ask("\nOpción", choices=["0", "1", "2"], default="0").strip()

            if opcion == "0":
                return None
            elif opcion == "1":
                documento = self.pedir_texto("Número de documento")
                persona = self._gestor_personas.buscar_persona_por_documento(documento)
                if persona is not None:
                    return persona
                self.mostrar_alerta("No se encontró ninguna persona con ese documento.")
                self.pausar()
            elif opcion == "2":
                # Listar todas las personas activas
                from modelo_datos import Persona
                todas = self._gestor_personas.listar(
                    incluir_inactivos=False
                ) if hasattr(self._gestor_personas, 'listar') else []
                if not todas:
                    self.mostrar_alerta("No hay personas registradas.")
                    self.pausar()
                    continue

                campos = ["ID", "Documento", "Nombres", "Apellidos", "Estado"]
                seleccion = self.seleccionar_de_resultados(
                    titulo="Personas registradas",
                    resultados=todas,
                    campos_display=campos,
                    campo_id="idPersona",
                )
                if seleccion is not None:
                    return seleccion
                # User canceled or no selection, ask if they want to try again
                continuar = self.pedir_opcion("¿Otra búsqueda? (s/n)", ["s", "n"])
                if continuar == "n":
                    return None

    def crear_estudiante(self) -> None:
        persona = self._seleccionar_persona("Seleccionar persona para estudiante")
        if persona is None:
            return

        codigo_estudiante = self.pedir_texto("Código de estudiante")
        id_programa = self.pedir_entero("ID del programa")
        id_plan_estudio = self.pedir_entero("ID del plan de estudio")
        fecha_ingreso = self.pedir_fecha("Fecha de ingreso", obligatorio=False)
        semestre_actual = self.pedir_entero("Semestre actual", obligatorio=False)

        estudiante = Estudiante(
            idPersona=persona.idPersona,
            codigoEstudiante=codigo_estudiante,
            idPrograma=id_programa,
            idPlanEstudio=id_plan_estudio,
            fechaIngreso=fecha_ingreso,
            semestreActual=semestre_actual,
            estadoAcademico=EstadoAcademico.ACTIVO,
        )
        creado = self._gestor_personas.crear_estudiante(estudiante)
        self.mostrar_exito(f"Estudiante registrado con ID {creado.idEstudiante}.")

    def crear_profesor(self) -> None:
        persona = self._seleccionar_persona("Seleccionar persona para profesor")
        if persona is None:
            return

        codigo_profesor = self.pedir_texto("Código de profesor")
        id_programa_principal = self.pedir_entero("ID del programa principal", obligatorio=False)
        fecha_vinculacion = self.pedir_fecha("Fecha de vinculación", obligatorio=False)

        from modelo_datos import TipoProfesor, Dedicacion
        profesor = Profesor(
            idPersona=persona.idPersona,
            codigoProfesor=codigo_profesor,
            idProgramaPrincipal=id_programa_principal,
            fechaVinculacion=fecha_vinculacion,
            tipoProfesor=TipoProfesor(
                self.pedir_opcion("Tipo de profesor", [t.value for t in TipoProfesor])
            ),
            dedicacion=Dedicacion(
                self.pedir_opcion("Dedicación", [d.value for d in Dedicacion])
            ),
            tituloProfesional=self.pedir_texto("Título profesional", obligatorio=False),
            maximoNivelEstudio=self.pedir_texto("Máximo nivel de estudio", obligatorio=False),
        )
        creado = self._gestor_personas.crear_profesor(profesor)
        self.mostrar_exito(f"Profesor registrado con ID {creado.idProfesor}.")

    def crear_administrativo(self) -> None:
        persona = self._seleccionar_persona("Seleccionar persona para administrativo")
        if persona is None:
            return

        codigo_empleado = self.pedir_texto("Código de empleado")
        cargo = self.pedir_texto("Cargo")
        dependencia = self.pedir_texto("Dependencia", obligatorio=False)
        fecha_vinculacion = self.pedir_fecha("Fecha de vinculación", obligatorio=False)
        salario_base = self.pedir_decimal("Salario base", obligatorio=False)

        administrativo = Administrativo(
            idPersona=persona.idPersona,
            codigoEmpleado=codigo_empleado,
            cargo=cargo,
            dependencia=dependencia,
            fechaVinculacion=fecha_vinculacion,
            salarioBase=salario_base,
        )
        creado = self._gestor_personas.crear_administrativo(administrativo)
        self.mostrar_exito(f"Administrativo registrado con ID {creado.idAdministrativo}.")

    def buscar_por_documento(self) -> None:
        documento = self.pedir_texto("Número de documento")
        persona = self._gestor_personas.buscar_persona_por_documento(documento)
        if persona is None:
            self.mostrar_alerta("No se encontró ninguna persona con ese documento.")
            return
        self.mostrar_tabla(
            "Persona encontrada",
            ["ID", "Documento", "Nombres", "Apellidos", "Correo", "Estado"],
            [[
                persona.idPersona,
                f"{persona.tipoDocumento} {persona.numeroDocumento}",
                f"{persona.primerNombre} {persona.segundoNombre or ''}".strip(),
                f"{persona.primerApellido} {persona.segundoApellido or ''}".strip(),
                persona.correoInstitucional,
                persona.estado,
            ]],
        )

    def listar_estudiantes(self) -> None:
        # Buscar programa por código o nombre en lugar de ID
        codigo_prog = self.pedir_texto("Código del programa (o nombre)")
        # Intentar buscar en gestor si tiene método de búsqueda
        id_programa = self.pedir_entero("ID del programa")  # Fallback a ID

        estudiantes = self._gestor_personas.listar_estudiantes_por_programa(id_programa)
        if not estudiantes:
            self.mostrar_alerta(f"No hay estudiantes en el programa {id_programa}.")
            self.pausar()
            return

        self.mostrar_tabla(
            f"Estudiantes del programa {id_programa}",
            ["ID", "Código", "ID Persona", "Semestre", "Promedio", "Estado"],
            [[e.idEstudiante, e.codigoEstudiante, e.idPersona, e.semestreActual,
              e.promedioAcumulado, e.estado] for e in estudiantes],
        )

    def listar_profesores(self) -> None:
        # Buscar programa por código o nombre en lugar de ID
        codigo_prog = self.pedir_texto("Código del programa (o nombre)")
        id_programa = self.pedir_entero("ID del programa")  # Fallback a ID

        profesores = self._gestor_personas.listar_profesores_por_programa(id_programa)
        if not profesores:
            self.mostrar_alerta(f"No hay profesores en el programa {id_programa}.")
            self.pausar()
            return

        self.mostrar_tabla(
            f"Profesores del programa {id_programa}",
            ["ID", "Código", "ID Persona", "Tipo", "Dedicación", "Estado"],
            [[p.idProfesor, p.codigoProfesor, p.idPersona,
              getattr(p.tipoProfesor, "value", p.tipoProfesor),
              getattr(p.dedicacion, "value", p.dedicacion),
              p.estado] for p in profesores],
        )

    def desactivar_persona(self) -> None:
        persona = self._seleccionar_persona("Seleccionar persona para desactivar")
        if persona is None:
            return

        if self.pedir_bool(f"¿Confirma desactivar la persona {persona.idPersona}?"):
            self._gestor_personas.desactivar_persona(persona.idPersona)
            self.mostrar_exito("Persona desactivada.")
