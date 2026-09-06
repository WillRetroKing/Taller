from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any, Iterable

from modelo_datos import Administrativo, Estudiante, EstadoAcademico, Persona, Profesor


class ErrorPersona(ValueError):
    """Error de integridad o validación de personas."""


class GestorPersonas:
    def __init__(
        self,
        personas: list[Persona],
        estudiantes: list[Estudiante] | None = None,
        profesores: list[Profesor] | None = None,
        administrativos: list[Administrativo] | None = None,
        programas: Iterable[Any] | None = None,
        planes_estudio: Iterable[Any] | None = None,
    ) -> None:
        self.personas = personas
        self.estudiantes = estudiantes if estudiantes is not None else []
        self.profesores = profesores if profesores is not None else []
        self.administrativos = administrativos if administrativos is not None else []
        self.programas = list(programas or [])
        self.planes_estudio = list(planes_estudio or [])

    def crear_persona(self, persona: Persona) -> Persona:
        if persona.idPersona is None:
            persona.idPersona = self._siguiente_id(self.personas, "idPersona")
        if any(item.idPersona == persona.idPersona for item in self.personas):
            raise ErrorPersona(f"Ya existe una persona con ID {persona.idPersona}")
        if not persona.numeroDocumento:
            raise ErrorPersona("El número de documento es obligatorio")
        if any(item.numeroDocumento == persona.numeroDocumento for item in self.personas):
            raise ErrorPersona(f"Ya existe el documento {persona.numeroDocumento}")
        persona.fechaRegistro = persona.fechaRegistro or date.today()
        persona.estado = persona.estado or "ACTIVO"
        self.personas.append(persona)
        return persona

    def crear_estudiante(self, estudiante: Estudiante) -> Estudiante:
        self._persona_existente(estudiante.idPersona)
        if estudiante.idEstudiante is None:
            estudiante.idEstudiante = self._siguiente_id(self.estudiantes, "idEstudiante")
        self._id_unico(self.estudiantes, "idEstudiante", estudiante.idEstudiante, "estudiante")
        if any(item.codigoEstudiante == estudiante.codigoEstudiante for item in self.estudiantes if estudiante.codigoEstudiante):
            raise ErrorPersona(f"Ya existe el código de estudiante {estudiante.codigoEstudiante}")
        self._referencia_existente(self.programas, "idPrograma", estudiante.idPrograma, "programa")
        self._referencia_existente(self.planes_estudio, "idPlanEstudio", estudiante.idPlanEstudio, "plan de estudio")
        estudiante.estadoAcademico = estudiante.estadoAcademico or EstadoAcademico.ACTIVO
        estudiante.estado = estudiante.estado or "ACTIVO"
        self.estudiantes.append(estudiante)
        return estudiante

    def crear_profesor(self, profesor: Profesor) -> Profesor:
        self._persona_existente(profesor.idPersona)
        if profesor.idProfesor is None:
            profesor.idProfesor = self._siguiente_id(self.profesores, "idProfesor")
        self._id_unico(self.profesores, "idProfesor", profesor.idProfesor, "profesor")
        if any(item.codigoProfesor == profesor.codigoProfesor for item in self.profesores if profesor.codigoProfesor):
            raise ErrorPersona(f"Ya existe el código de profesor {profesor.codigoProfesor}")
        # Validación B5: Evitar registrar múltiples posgrados por profesor
        # El profesor ya tiene un nivel de posgrado reconocido, no se permite otro
        posgrado_existente = next(
            (p for p in self.profesores if p.idProfesor == profesor.idProfesor),
            None,
        )
        if posgrado_existente and posgrado_existente.nivelPosgradoReconocido is not None:
            raise ErrorPersona(
                f"El profesor con ID {profesor.idProfesor} ya tiene un posgrado reconocido "
                f"('{posgrado_existente.nivelPosgradoReconocido}'), no se pueden registrar múltiples posgrados"
            )
        profesor.estado = profesor.estado or "ACTIVO"
        self.profesores.append(profesor)
        return profesor

    def crear_administrativo(self, administrativo: Administrativo) -> Administrativo:
        self._persona_existente(administrativo.idPersona)
        if administrativo.idAdministrativo is None:
            administrativo.idAdministrativo = self._siguiente_id(self.administrativos, "idAdministrativo")
        self._id_unico(self.administrativos, "idAdministrativo", administrativo.idAdministrativo, "administrativo")
        if any(item.codigoEmpleado == administrativo.codigoEmpleado for item in self.administrativos if administrativo.codigoEmpleado):
            raise ErrorPersona(f"Ya existe el código de empleado {administrativo.codigoEmpleado}")
        administrativo.estado = administrativo.estado or "ACTIVO"
        self.administrativos.append(administrativo)
        return administrativo

    def buscar_persona_por_documento(self, numero_documento: str) -> Persona | None:
        return next((item for item in self.personas if item.numeroDocumento == numero_documento), None)

    def buscar_estudiante_por_codigo(self, codigo: str) -> Estudiante | None:
        return next((item for item in self.estudiantes if item.codigoEstudiante == codigo), None)

    def buscar_profesor_por_codigo(self, codigo: str) -> Profesor | None:
        return next((item for item in self.profesores if item.codigoProfesor == codigo), None)

    def listar_estudiantes_por_programa(self, id_programa: int) -> list[Estudiante]:
        return [item for item in self.estudiantes if item.idPrograma == id_programa]

    def listar_profesores_por_programa(self, id_programa: int) -> list[Profesor]:
        return [item for item in self.profesores if item.idProgramaPrincipal == id_programa]

    def modificar_persona(self, id_persona: int, **cambios: Any) -> Persona:
        persona = self._buscar(self.personas, "idPersona", id_persona, "persona")
        if "numeroDocumento" in cambios and cambios["numeroDocumento"] != persona.numeroDocumento:
            if any(item.numeroDocumento == cambios["numeroDocumento"] for item in self.personas):
                raise ErrorPersona(f"Ya existe el documento {cambios['numeroDocumento']}")
        self._actualizar(persona, cambios)
        return persona

    def desactivar_persona(self, id_persona: int) -> Persona:
        persona = self._buscar(self.personas, "idPersona", id_persona, "persona")
        persona.estado = "INACTIVO"
        return persona

    def desactivar_estudiante(self, id_estudiante: int) -> Estudiante:
        estudiante = self._buscar(self.estudiantes, "idEstudiante", id_estudiante, "estudiante")
        estudiante.estado = "INACTIVO"
        return estudiante

    def desactivar_profesor(self, id_profesor: int) -> Profesor:
        profesor = self._buscar(self.profesores, "idProfesor", id_profesor, "profesor")
        profesor.estado = "INACTIVO"
        return profesor

    def desactivar_administrativo(self, id_administrativo: int) -> Administrativo:
        administrativo = self._buscar(self.administrativos, "idAdministrativo", id_administrativo, "administrativo")
        administrativo.estado = "INACTIVO"
        return administrativo

    def _persona_existente(self, id_persona: int | None) -> Persona:
        if id_persona is None:
            raise ErrorPersona("El rol debe estar asociado a una persona")
        return self._buscar(self.personas, "idPersona", id_persona, "persona")

    @staticmethod
    def _referencia_existente(elementos: Iterable[Any], campo: str, valor: int | None, nombre: str) -> None:
        if valor is not None and not any(getattr(item, campo, None) == valor for item in elementos):
            raise ErrorPersona(f"No existe el {nombre} con ID {valor}")

    @staticmethod
    def _id_unico(elementos: Iterable[Any], campo: str, valor: int | None, nombre: str) -> None:
        if any(getattr(item, campo, None) == valor for item in elementos):
            raise ErrorPersona(f"Ya existe un {nombre} con ID {valor}")

    @staticmethod
    def _buscar(elementos: Iterable[Any], campo: str, valor: Any, nombre: str) -> Any:
        elemento = next((item for item in elementos if getattr(item, campo, None) == valor), None)
        if elemento is None:
            raise ErrorPersona(f"No existe el {nombre} con ID {valor}")
        return elemento

    @staticmethod
    def _actualizar(objeto: Any, cambios: dict[str, Any]) -> None:
        campos = set(getattr(objeto, "__dataclass_fields__", {}))
        desconocidos = set(cambios) - campos
        if desconocidos:
            raise ErrorPersona(f"Campos no válidos: {', '.join(sorted(desconocidos))}")
        for nombre, valor in cambios.items():
            setattr(objeto, nombre, valor)

    @staticmethod
    def _siguiente_id(elementos: Iterable[Any], campo: str) -> int:
        return max((getattr(item, campo) or 0 for item in elementos), default=0) + 1
