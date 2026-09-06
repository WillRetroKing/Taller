from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any, Iterable

from modelo_datos import AsignacionDocente, Curso, DetallePlanEstudio, Horario, PlanEstudio, Prerrequisito


class ErrorAcademico(ValueError):
    """Error de estructura o referencia académica."""


class GestorAcademico:
    def __init__(
        self,
        planes: list[PlanEstudio],
        detalles_planes: list[DetallePlanEstudio],
        cursos: list[Curso],
        prerrequisitos: list[Prerrequisito],
        programas: Iterable[Any] | None = None,
        horarios: list[Horario] | None = None,
        asignaciones: list[AsignacionDocente] | None = None,
        profesores: Iterable[Any] | None = None,
        ofertas: Iterable[Any] | None = None,
    ) -> None:
        self.planes = planes
        self.detalles_planes = detalles_planes
        self.cursos = cursos
        self.prerrequisitos = prerrequisitos
        self.programas = list(programas or [])
        self.horarios = horarios if horarios is not None else []
        self.asignaciones = asignaciones if asignaciones is not None else []
        self.profesores = list(profesores or [])
        self.ofertas = list(ofertas or [])

    def crear_plan(self, plan: PlanEstudio) -> PlanEstudio:
        if plan.idPlanEstudio is None:
            plan.idPlanEstudio = self._siguiente_id(self.planes, "idPlanEstudio")
        self._id_unico(self.planes, "idPlanEstudio", plan.idPlanEstudio, "plan de estudio")
        if plan.idPrograma is not None:
            self._referencia(self.programas, "idPrograma", plan.idPrograma, "programa")
        if plan.fechaFinVigencia and plan.fechaInicioVigencia and plan.fechaFinVigencia < plan.fechaInicioVigencia:
            raise ErrorAcademico("La vigencia final del plan no puede preceder a la inicial")
        plan.estado = plan.estado or "ACTIVO"
        self.planes.append(plan)
        return plan

    def incluir_curso(
        self,
        id_plan: int,
        id_curso: int,
        semestre_sugerido: int,
        *,
        es_obligatorio: bool = True,
    ) -> DetallePlanEstudio:
        plan = self._buscar(self.planes, "idPlanEstudio", id_plan, "plan de estudio")
        curso = self._buscar(self.cursos, "idCurso", id_curso, "curso")
        if semestre_sugerido < 1:
            raise ErrorAcademico("El semestre sugerido debe ser positivo")
        if any(item.idPlanEstudio == id_plan and item.idCurso == id_curso for item in self.detalles_planes):
            raise ErrorAcademico("El curso ya pertenece a este plan")
        detalle = DetallePlanEstudio(
            idDetallePlan=self._siguiente_id(self.detalles_planes, "idDetallePlan"),
            idPlanEstudio=plan.idPlanEstudio,
            idCurso=curso.idCurso,
            semestreSugerido=semestre_sugerido,
            numeroCreditos=curso.numeroCreditos,
            esObligatorio=es_obligatorio,
            estado="ACTIVO",
        )
        self.detalles_planes.append(detalle)
        plan.totalCreditos = sum(
            item.numeroCreditos or 0
            for item in self.detalles_planes
            if item.idPlanEstudio == id_plan and item.estado != "INACTIVO"
        )
        return detalle

    def registrar_prerrequisito(self, prerrequisito: Prerrequisito) -> Prerrequisito:
        self._buscar(self.cursos, "idCurso", prerrequisito.idCurso, "curso")
        self._buscar(self.cursos, "idCurso", prerrequisito.idCursoRequerido, "curso prerrequisito")
        if prerrequisito.idCurso == prerrequisito.idCursoRequerido:
            raise ErrorAcademico("Un curso no puede ser prerrequisito de sí mismo")
        if any(
            item.idCurso == prerrequisito.idCurso
            and item.idCursoRequerido == prerrequisito.idCursoRequerido
            for item in self.prerrequisitos
        ):
            raise ErrorAcademico("El prerrequisito ya está registrado")
        if prerrequisito.idPrerrequisito is None:
            prerrequisito.idPrerrequisito = self._siguiente_id(self.prerrequisitos, "idPrerrequisito")
        self._id_unico(self.prerrequisitos, "idPrerrequisito", prerrequisito.idPrerrequisito, "prerrequisito")
        prerrequisito.estado = prerrequisito.estado or "ACTIVO"
        self.prerrequisitos.append(prerrequisito)
        return prerrequisito

    def consultar_plan(self, id_plan: int) -> tuple[PlanEstudio, list[DetallePlanEstudio]]:
        plan = self._buscar(self.planes, "idPlanEstudio", id_plan, "plan de estudio")
        detalles = [item for item in self.detalles_planes if item.idPlanEstudio == id_plan]
        return plan, detalles

    def asignar_profesor(self, id_profesor: int, id_oferta: int, numero_horas: Decimal) -> AsignacionDocente:
        self._referencia(self.profesores, "idProfesor", id_profesor, "profesor")
        self._referencia(self.ofertas, "idOfertaCurso", id_oferta, "oferta")
        if any(item.idProfesor == id_profesor and item.idOfertaCurso == id_oferta for item in self.asignaciones):
            raise ErrorAcademico("El profesor ya está asignado a esta oferta")
        if numero_horas <= 0:
            raise ErrorAcademico("El número de horas debe ser positivo")
        asignacion = AsignacionDocente(
            idAsignacion=self._siguiente_id(self.asignaciones, "idAsignacion"),
            idProfesor=id_profesor,
            idOfertaCurso=id_oferta,
            numeroHoras=numero_horas,
            fechaAsignacion=date.today(),
            estado="ACTIVO",
        )
        self.asignaciones.append(asignacion)
        return asignacion

    def agregar_horario(self, horario: Horario) -> Horario:
        if horario.horaInicio is None or horario.horaFin is None or horario.horaInicio >= horario.horaFin:
            raise ErrorAcademico("El horario debe tener horas válidas y consecutivas")
        existentes = [item for item in self.horarios if item.idOfertaCurso == horario.idOfertaCurso]
        if any(self._se_cruzan(horario, existente) for existente in existentes):
            raise ErrorAcademico("El horario se cruza con otro horario de la oferta")
        horario.idHorario = horario.idHorario or self._siguiente_id(self.horarios, "idHorario")
        if any(item.idHorario == horario.idHorario for item in self.horarios):
            raise ErrorAcademico(f"Ya existe un horario con ID {horario.idHorario}")
        self.horarios.append(horario)
        return horario

    @staticmethod
    def _se_cruzan(primero: Horario, segundo: Horario) -> bool:
        return primero.diaSemana == segundo.diaSemana and primero.horaInicio < segundo.horaFin and segundo.horaInicio < primero.horaFin

    def desactivar_plan(self, id_plan: int) -> PlanEstudio:
        plan = self._buscar(self.planes, "idPlanEstudio", id_plan, "plan de estudio")
        plan.estado = "INACTIVO"
        return plan

    @staticmethod
    def _buscar(elementos: Iterable[Any], campo: str, valor: Any, nombre: str) -> Any:
        elemento = next((item for item in elementos if getattr(item, campo, None) == valor), None)
        if elemento is None:
            raise ErrorAcademico(f"No existe el {nombre} con ID {valor}")
        return elemento

    @staticmethod
    def _referencia(elementos: Iterable[Any], campo: str, valor: Any, nombre: str) -> None:
        if not any(getattr(item, campo, None) == valor for item in elementos):
            raise ErrorAcademico(f"No existe el {nombre} con ID {valor}")

    @staticmethod
    def _id_unico(elementos: Iterable[Any], campo: str, valor: Any, nombre: str) -> None:
        if any(getattr(item, campo, None) == valor for item in elementos):
            raise ErrorAcademico(f"Ya existe un {nombre} con ID {valor}")

    @staticmethod
    def _siguiente_id(elementos: Iterable[Any], campo: str) -> int:
        return max((getattr(item, campo) or 0 for item in elementos), default=0) + 1
