from __future__ import annotations

from datetime import date, time
from decimal import Decimal
from typing import Any, Iterable

from dominio.modelo_datos import (
    AlertaAcademica,
    Calificacion,
    Curso,
    DetalleMatricula,
    Estudiante,
    EstadoAcademico,
    EstadoCurso,
    Evaluacion,
    Horario,
    MatriculaAcademica,
    OfertaCurso,
    ParametroNormativo,
    ParametroNormativoCodigo,
    PeriodoAcademico,
)


class ErrorMatricula(ValueError):
    """Error de una regla de matrícula."""


class ErrorCalificacion(ValueError):
    """Error de una regla de calificaciones."""


class GestorMatriculas:
    def __init__(
        self,
        estudiantes: list[Estudiante],
        periodos: list[PeriodoAcademico],
        ofertas: list[OfertaCurso],
        cursos: list[Curso],
        matriculas: list[MatriculaAcademica],
        detalles: list[DetalleMatricula],
        horarios: list[Horario],
        parametros: list[ParametroNormativo] | None = None,
        prerrequisitos: list[Any] | None = None,
        alertas: list[AlertaAcademica] | None = None,
    ) -> None:
        self.estudiantes = estudiantes
        self.periodos = periodos
        self.ofertas = ofertas
        self.cursos = cursos
        self.matriculas = matriculas
        self.detalles = detalles
        self.horarios = horarios
        self.parametros = parametros or []
        self.prerrequisitos = prerrequisitos or []
        self.alertas = alertas if alertas is not None else []

    def matricular_curso(
        self, id_estudiante: int, id_oferta: int, fecha_matricula: date | None = None
    ) -> DetalleMatricula:
        estudiante = self._buscar(self.estudiantes, "idEstudiante", id_estudiante, "estudiante")
        oferta = self._buscar(self.ofertas, "idOfertaCurso", id_oferta, "oferta")
        periodo = self._buscar(self.periodos, "idPeriodo", oferta.idPeriodo, "periodo")
        curso = self._buscar(self.cursos, "idCurso", oferta.idCurso, "curso")
        fecha = fecha_matricula or date.today()

        if getattr(estudiante.estadoAcademico, "value", estudiante.estadoAcademico) != "ACTIVO":
            raise ErrorMatricula("El estudiante no está activo para matricular cursos")
        if not self._es_periodo_abierto(periodo, fecha):
            raise ErrorMatricula("El periodo no está abierto para matrícula")
        if not self._es_activo(oferta.estado):
            raise ErrorMatricula("La oferta no está activa")
        if oferta.cupoDisponible is None or oferta.cupoDisponible <= 0:
            raise ErrorMatricula("La oferta no tiene cupos disponibles")

        matricula = self._obtener_o_crear_matricula(estudiante, periodo, fecha)
        detalles_periodo = self._detalles_de_matricula(matricula.idMatricula)
        if any(detalle.idOfertaCurso == id_oferta and detalle.estadoCurso != EstadoCurso.CANCELADO for detalle in detalles_periodo):
            raise ErrorMatricula("El estudiante ya está matriculado en esta oferta")
        if not self._cumple_prerrequisitos(estudiante.idEstudiante, curso.idCurso):
            raise ErrorMatricula("El estudiante no cumple los prerrequisitos")

        creditos_actuales = sum(
            self._curso_de_oferta(detalle.idOfertaCurso).numeroCreditos or 0
            for detalle in detalles_periodo
            if detalle.estadoCurso != EstadoCurso.CANCELADO
        )
        maximo = self._parametro_decimal(ParametroNormativoCodigo.MAXIMO_CREDITOS_PERIODO)
        if maximo is not None and Decimal(creditos_actuales + (curso.numeroCreditos or 0)) > maximo:
            raise ErrorMatricula("Se supera el máximo de créditos permitido")
        if self._tiene_cruce_horario(id_estudiante, id_oferta, periodo.idPeriodo):
            raise ErrorMatricula("El curso tiene cruce de horario")

        detalle = DetalleMatricula(
            idDetalleMatricula=self._siguiente_id(self.detalles, "idDetalleMatricula"),
            idMatricula=matricula.idMatricula,
            idOfertaCurso=id_oferta,
            fechaInscripcion=fecha,
            estadoCurso=EstadoCurso.MATRICULADO,
        )
        self.detalles.append(detalle)
        oferta.cupoDisponible -= 1
        matricula.totalCreditos = creditos_actuales + (curso.numeroCreditos or 0)
        return detalle

    def calcular_promedio_periodo(self, id_matricula: int) -> Decimal:
        matricula = self._buscar(self.matriculas, "idMatricula", id_matricula, "matrícula")
        suma_notas = Decimal("0")
        suma_creditos = 0
        for detalle in self._detalles_de_matricula(id_matricula):
            if detalle.notaFinal is None or detalle.estadoCurso == EstadoCurso.CANCELADO:
                continue
            creditos = self._curso_de_oferta(detalle.idOfertaCurso).numeroCreditos or 0
            suma_notas += detalle.notaFinal * creditos
            suma_creditos += creditos
        promedio = suma_notas / suma_creditos if suma_creditos else Decimal("0")
        matricula.promedioPeriodo = promedio.quantize(Decimal("0.01"))
        estudiante = self._buscar(self.estudiantes, "idEstudiante", matricula.idEstudiante, "estudiante")
        self.calcular_promedio_acumulado(estudiante.idEstudiante)
        return matricula.promedioPeriodo

    def cancelar_curso(
        self,
        id_estudiante: int,
        id_oferta: int,
        motivo: str,
        fecha_cancelacion: date | None = None,
    ) -> DetalleMatricula:
        if not motivo.strip():
            raise ErrorMatricula("El motivo de cancelación es obligatorio")
        fecha = fecha_cancelacion or date.today()
        estudiante = self._buscar(self.estudiantes, "idEstudiante", id_estudiante, "estudiante")
        oferta = self._buscar(self.ofertas, "idOfertaCurso", id_oferta, "oferta")
        periodo = self._buscar(self.periodos, "idPeriodo", oferta.idPeriodo, "periodo")
        if periodo.fechaLimiteCancelacion is not None and fecha > periodo.fechaLimiteCancelacion:
            raise ErrorMatricula("La fecha límite de cancelación ya fue superada")

        detalle = next(
            (
                item for matricula in self.matriculas
                if matricula.idEstudiante == estudiante.idEstudiante
                for item in self._detalles_de_matricula(matricula.idMatricula)
                if item.idOfertaCurso == id_oferta and item.estadoCurso != EstadoCurso.CANCELADO
            ),
            None,
        )
        if detalle is None:
            raise ErrorMatricula("El estudiante no tiene esa oferta matriculada")
        detalle.estadoCurso = EstadoCurso.CANCELADO
        detalle.fechaCancelacion = fecha
        detalle.motivoCancelacion = motivo.strip()
        if oferta.cupoDisponible is None:
            oferta.cupoDisponible = 0
        oferta.cupoDisponible += 1
        matricula = self._buscar(self.matriculas, "idMatricula", detalle.idMatricula, "matrícula")
        matricula.totalCreditos = sum(
            self._curso_de_oferta(item.idOfertaCurso).numeroCreditos or 0
            for item in self._detalles_de_matricula(matricula.idMatricula)
            if item.estadoCurso != EstadoCurso.CANCELADO
        )
        return detalle

    def calcular_promedio_acumulado(self, id_estudiante: int) -> Decimal:
        estudiante = self._buscar(self.estudiantes, "idEstudiante", id_estudiante, "estudiante")
        suma_notas = Decimal("0")
        suma_creditos = 0
        for matricula in self.matriculas:
            if matricula.idEstudiante != id_estudiante:
                continue
            for detalle in self._detalles_de_matricula(matricula.idMatricula):
                if detalle.notaFinal is None or detalle.estadoCurso == EstadoCurso.CANCELADO:
                    continue
                creditos = self._curso_de_oferta(detalle.idOfertaCurso).numeroCreditos or 0
                suma_notas += detalle.notaFinal * creditos
                suma_creditos += creditos
        promedio = suma_notas / suma_creditos if suma_creditos else Decimal("0")
        estudiante.promedioAcumulado = promedio.quantize(Decimal("0.01"))
        self.evaluar_ebra(estudiante.idEstudiante)
        return estudiante.promedioAcumulado

    def evaluar_ebra(self, id_estudiante: int) -> AlertaAcademica | None:
        estudiante = self._buscar(self.estudiantes, "idEstudiante", id_estudiante, "estudiante")
        umbral = self._parametro_decimal(ParametroNormativoCodigo.PROMEDIO_MINIMO_EBRA)
        if umbral is None or estudiante.promedioAcumulado is None or estudiante.promedioAcumulado >= umbral:
            return None
        estudiante.estadoAcademico = EstadoAcademico.EBRA
        periodo_id = self._ultimo_periodo_del_estudiante(id_estudiante)
        existente = next(
            (alerta for alerta in self.alertas
             if alerta.idEstudiante == id_estudiante and alerta.tipoAlerta == "EBRA"
             and not alerta.atendida),
            None,
        )
        if existente is not None:
            return existente
        alerta = AlertaAcademica(
            idAlerta=self._siguiente_id(self.alertas, "idAlerta"),
            idEstudiante=id_estudiante,
            idPeriodo=periodo_id,
            tipoAlerta="EBRA",
            motivo="El promedio acumulado está por debajo del mínimo institucional",
            valorObservado=estudiante.promedioAcumulado,
            valorLimite=umbral,
            fechaGeneracion=date.today(),
            atendida=False,
            estado="ACTIVO",
        )
        self.alertas.append(alerta)
        return alerta

    def _obtener_o_crear_matricula(self, estudiante: Estudiante, periodo: PeriodoAcademico, fecha: date) -> MatriculaAcademica:
        matricula = next(
            (item for item in self.matriculas if item.idEstudiante == estudiante.idEstudiante and item.idPeriodo == periodo.idPeriodo),
            None,
        )
        if matricula is not None:
            return matricula
        matricula = MatriculaAcademica(
            idMatricula=self._siguiente_id(self.matriculas, "idMatricula"),
            idEstudiante=estudiante.idEstudiante,
            idPeriodo=periodo.idPeriodo,
            fechaMatricula=fecha,
            totalCreditos=0,
            estadoMatricula="ACTIVA",
        )
        self.matriculas.append(matricula)
        return matricula

    def _cumple_prerrequisitos(self, id_estudiante: int, id_curso: int | None) -> bool:
        requisitos = [item for item in self.prerrequisitos if item.idCurso == id_curso]
        for requisito in requisitos:
            aprobados = any(
                detalle.notaFinal is not None
                and detalle.notaFinal >= (requisito.notaMinima or Decimal("0"))
                and detalle.estadoCurso in {EstadoCurso.APROBADO, EstadoCurso.HOMOLOGADO, EstadoCurso.VALIDADO}
                and self._curso_de_oferta(detalle.idOfertaCurso).idCurso == requisito.idCursoRequerido
                for matricula in self.matriculas if matricula.idEstudiante == id_estudiante
                for detalle in self._detalles_de_matricula(matricula.idMatricula)
            )
            if not aprobados:
                return False
        return True

    def _tiene_cruce_horario(self, id_estudiante: int, id_oferta: int, id_periodo: int | None) -> bool:
        horarios_nuevos = [item for item in self.horarios if item.idOfertaCurso == id_oferta]
        ofertas_actuales = {
            detalle.idOfertaCurso
            for matricula in self.matriculas
            if matricula.idEstudiante == id_estudiante and matricula.idPeriodo == id_periodo
            for detalle in self._detalles_de_matricula(matricula.idMatricula)
            if detalle.estadoCurso != EstadoCurso.CANCELADO
        }
        horarios_actuales = [item for item in self.horarios if item.idOfertaCurso in ofertas_actuales]
        return any(self._se_cruzan(nuevo, actual) for nuevo in horarios_nuevos for actual in horarios_actuales)

    @staticmethod
    def _se_cruzan(primer: Horario, segundo: Horario) -> bool:
        if primer.diaSemana != segundo.diaSemana or primer.horaInicio is None or primer.horaFin is None or segundo.horaInicio is None or segundo.horaFin is None:
            return False
        return primer.horaInicio < segundo.horaFin and segundo.horaInicio < primer.horaFin

    def _parametro_decimal(self, codigo: ParametroNormativoCodigo) -> Decimal | None:
        parametro = next((item for item in self.parametros if item.codigo == codigo or item.codigo == codigo.value), None)
        return Decimal(parametro.valor) if parametro is not None and parametro.valor else None

    def _ultimo_periodo_del_estudiante(self, id_estudiante: int) -> int | None:
        periodos = [item.idPeriodo for item in self.matriculas if item.idEstudiante == id_estudiante]
        return periodos[-1] if periodos else None

    def _detalles_de_matricula(self, id_matricula: int | None) -> list[DetalleMatricula]:
        return [item for item in self.detalles if item.idMatricula == id_matricula]

    def _curso_de_oferta(self, id_oferta: int | None) -> Curso:
        oferta = self._buscar(self.ofertas, "idOfertaCurso", id_oferta, "oferta")
        return self._buscar(self.cursos, "idCurso", oferta.idCurso, "curso")

    @staticmethod
    def _buscar(elementos: Iterable[Any], campo: str, valor: Any, nombre: str) -> Any:
        elemento = next((item for item in elementos if getattr(item, campo, None) == valor), None)
        if elemento is None:
            raise ErrorMatricula(f"No existe el {nombre} con ID {valor}")
        return elemento

    @staticmethod
    def _siguiente_id(elementos: Iterable[Any], campo: str) -> int:
        return max((getattr(item, campo) or 0 for item in elementos), default=0) + 1

    @staticmethod
    def _es_activo(estado: Any) -> bool:
        return getattr(estado, "value", estado) in {"ACTIVO", "MATRICULADO", "ADMITIDO"}

    def consultar_matriculas(
        self,
        *,
        id_estudiante: int | None = None,
        id_periodo: int | None = None,
        estado: str | None = None,
    ) -> list[MatriculaAcademica]:
        """Consultar matrículas con filtros opcionales."""
        resultados = []
        for matricula in self.matriculas:
            if id_estudiante is not None and matricula.idEstudiante != id_estudiante:
                continue
            if id_periodo is not None and matricula.idPeriodo != id_periodo:
                continue
            if estado is not None and str(matricula.estadoMatricula or "").upper() != estado.upper():
                continue
            resultados.append(matricula)
        return resultados

    def consultar_detalle_matricula(self, id_matricula: int) -> list[DetalleMatricula]:
        """Consultar detalles de una matrícula específica."""
        return self._detalles_de_matricula(id_matricula)

    def consultar_matricula_estudiante_periodo(self, id_estudiante: int, id_periodo: int) -> MatriculaAcademica | None:
        """Consultar matrícula de un estudiante en un periodo específico."""
        return next(
            (m for m in self.matriculas if m.idEstudiante == id_estudiante and m.idPeriodo == id_periodo),
            None,
        )

    def listar_ofertas_disponibles(self, id_periodo: int) -> list[OfertaCurso]:
        """Listar ofertas disponibles para matrícula en un periodo."""
        return [
            o for o in self.ofertas
            if o.idPeriodo == id_periodo
            and self._es_activo(o.estado)
            and (o.cupoDisponible or 0) > 0
        ]

    @staticmethod
    def _es_periodo_abierto(periodo: PeriodoAcademico, fecha: date) -> bool:
        estado = getattr(periodo.estado, "value", periodo.estado)
        return estado in {"ACTIVO", "ABIERTO"} and (
            periodo.fechaInicioMatricula is None or fecha >= periodo.fechaInicioMatricula
        ) and (periodo.fechaFinMatricula is None or fecha <= periodo.fechaFinMatricula)


class GestorCalificaciones:
    def __init__(
        self,
        evaluaciones: list[Evaluacion],
        calificaciones: list[Calificacion],
        detalles: list[DetalleMatricula],
        matriculas: list[MatriculaAcademica],
        estudiantes: list[Estudiante],
        ofertas: list[OfertaCurso],
        cursos: list[Curso],
        parametros: list[ParametroNormativo] | None = None,
        alertas: list[AlertaAcademica] | None = None,
    ) -> None:
        self.evaluaciones = evaluaciones
        self.calificaciones = calificaciones
        self.detalles = detalles
        self.matriculas = matriculas
        self.ofertas = ofertas
        self.cursos = cursos
        self.gestor_matriculas = GestorMatriculas(
            estudiantes, [], ofertas, cursos, matriculas, detalles, [], parametros, alertas=alertas
        )

    def registrar_calificacion(
        self, id_evaluacion: int, id_detalle: int, nota: Decimal, fecha_registro: date | None = None
    ) -> Calificacion:
        evaluacion = self._buscar(self.evaluaciones, "idEvaluacion", id_evaluacion)
        detalle = self._buscar(self.detalles, "idDetalleMatricula", id_detalle)
        if detalle.estadoCurso in {EstadoCurso.CANCELADO, EstadoCurso.RETIRADO}:
            raise ErrorCalificacion("No se pueden registrar notas para una matrícula cancelada o retirada")
        if str(evaluacion.estado or "ACTIVO").upper() != "ACTIVO":
            raise ErrorCalificacion("No se pueden registrar notas para una evaluación inactiva")
        if evaluacion.idOfertaCurso != self._oferta_de_detalle(detalle).idOfertaCurso:
            raise ErrorCalificacion("La evaluación no pertenece al curso matriculado")
        if evaluacion.porcentaje is None or evaluacion.porcentaje < 0:
            raise ErrorCalificacion("El porcentaje de la evaluación no es válido")
        try:
            nota = Decimal(nota)
        except Exception as error:
            raise ErrorCalificacion("La nota debe ser numérica") from error
        if nota < 0 or nota > 5:
            raise ErrorCalificacion("La nota debe estar entre 0 y 5")
        existente = next(
            (item for item in self.calificaciones if item.idEvaluacion == id_evaluacion and item.idDetalleMatricula == id_detalle),
            None,
        )
        if existente is None:
            calificacion = Calificacion(
                idCalificacion=self._siguiente_id(self.calificaciones, "idCalificacion"),
                idEvaluacion=id_evaluacion,
                idDetalleMatricula=id_detalle,
                nota=nota,
                fechaRegistro=fecha_registro or date.today(),
                estado="ACTIVA",
            )
            self.calificaciones.append(calificacion)
        else:
            existente.nota = nota
            existente.fechaRegistro = fecha_registro or date.today()
            calificacion = existente
        evaluaciones_activas = [
            item for item in self.evaluaciones
            if item.idOfertaCurso == detalle.idOfertaCurso and item.estado in {None, "ACTIVO"}
        ]
        calificaciones_completas = all(
            any(
                item.idEvaluacion == evaluacion.idEvaluacion
                and item.idDetalleMatricula == id_detalle
                and item.nota is not None
                for item in self.calificaciones
            )
            for evaluacion in evaluaciones_activas
        )
        if calificaciones_completas:
            self.recalcular_nota_final(id_detalle)
        return calificacion

    def recalcular_nota_final(self, id_detalle: int) -> Decimal:
        detalle = self._buscar(self.detalles, "idDetalleMatricula", id_detalle)
        evaluaciones = [item for item in self.evaluaciones if item.idOfertaCurso == detalle.idOfertaCurso and item.estado in {None, "ACTIVO"}]
        if not evaluaciones:
            raise ErrorCalificacion("El curso no tiene evaluaciones activas")
        porcentaje_total = sum((item.porcentaje or Decimal("0") for item in evaluaciones), Decimal("0"))
        if porcentaje_total != Decimal("100"):
            raise ErrorCalificacion("Los porcentajes de evaluación deben sumar 100")
        notas = {
            item.idEvaluacion: item.nota
            for item in self.calificaciones
            if item.idDetalleMatricula == id_detalle
        }
        if any(item.idEvaluacion not in notas or notas[item.idEvaluacion] is None for item in evaluaciones):
            raise ErrorCalificacion("Faltan calificaciones para calcular la nota final")
        detalle.notaFinal = sum(
            notas[item.idEvaluacion] * (item.porcentaje or Decimal("0")) / Decimal("100")
            for item in evaluaciones
        ).quantize(Decimal("0.01"))
        detalle.estadoCurso = EstadoCurso.APROBADO if detalle.notaFinal >= Decimal("3.0") else EstadoCurso.REPROBADO
        matricula = self._buscar(self.matriculas, "idMatricula", detalle.idMatricula)
        self.gestor_matriculas.calcular_promedio_periodo(matricula.idMatricula)
        return detalle.notaFinal

    def _oferta_de_detalle(self, detalle: DetalleMatricula) -> OfertaCurso:
        return self._buscar(self.ofertas, "idOfertaCurso", detalle.idOfertaCurso)

    @staticmethod
    def _buscar(elementos: Iterable[Any], campo: str, valor: Any) -> Any:
        elemento = next((item for item in elementos if getattr(item, campo, None) == valor), None)
        if elemento is None:
            raise ErrorCalificacion(f"No existe el registro con {campo}={valor}")
        return elemento

    @staticmethod
    def _siguiente_id(elementos: Iterable[Any], campo: str) -> int:
        return max((getattr(item, campo) or 0 for item in elementos), default=0) + 1

    def crear_evaluacion(
        self,
        id_oferta: int,
        nombre: str,
        tipo: str,
        porcentaje: Decimal,
        fecha_programada: date | None = None,
    ) -> Evaluacion:
        """Crear una evaluación con validaciones mejoradas."""
        if not nombre or not nombre.strip():
            raise ErrorCalificacion("El nombre de la evaluación es obligatorio")
        if tipo not in {"PARCIAL", "QUIZ", "TALLER", "LABORATORIO", "TRABAJO", "EXAMEN_FINAL", "PARTICIPACION", "OTRO"}:
            raise ErrorCalificacion(f"Tipo de evaluación inválido: {tipo}")
        if porcentaje <= 0 or porcentaje > 100:
            raise ErrorCalificacion("El porcentaje debe estar entre 0 y 100")
        oferta = next((o for o in self.ofertas if o.idOfertaCurso == id_oferta), None)
        if oferta is None:
            raise ErrorCalificacion(f"No existe la oferta con ID {id_oferta}")
        if not GestorMatriculas._es_activo(oferta.estado):
            raise ErrorCalificacion("No se pueden crear evaluaciones para una oferta inactiva")
        evaluaciones_oferta = [
            e for e in self.evaluaciones
            if e.idOfertaCurso == id_oferta and e.estado in {None, "ACTIVO"}
        ]
        porcentaje_actual = sum((e.porcentaje or Decimal("0") for e in evaluaciones_oferta), Decimal("0"))
        if porcentaje_actual + porcentaje > 100:
            raise ErrorCalificacion(
                f"El porcentaje total ({porcentaje_actual + porcentaje}) excede el 100%. "
                f"Porcentaje disponible: {100 - porcentaje_actual}"
            )
        evaluacion = Evaluacion(
            idEvaluacion=self._siguiente_id(self.evaluaciones, "idEvaluacion"),
            idOfertaCurso=id_oferta,
            nombre=nombre.strip(),
            tipo=tipo,
            porcentaje=porcentaje,
            fechaProgramada=fecha_programada or date.today(),
            estado="ACTIVO",
        )
        self.evaluaciones.append(evaluacion)
        return evaluacion

    def consultar_evaluaciones_oferta(self, id_oferta: int) -> list[Evaluacion]:
        """Consultar todas las evaluaciones de una oferta."""
        return [
            e for e in self.evaluaciones
            if e.idOfertaCurso == id_oferta and e.estado in {None, "ACTIVO"}
        ]

    def porcentaje_total_evaluaciones(self, id_oferta: int) -> Decimal:
        """Calcular el porcentaje total de evaluaciones de una oferta."""
        return sum(
            (e.porcentaje or Decimal("0") for e in self.evaluaciones if e.idOfertaCurso == id_oferta and e.estado in {None, "ACTIVO"}),
            Decimal("0"),
        )

    def validar_evaluaciones_para_final(self, id_oferta: int) -> tuple[bool, str]:
        """Validar si las evaluaciones están completas para calcular nota final."""
        evaluaciones = self.consultar_evaluaciones_oferta(id_oferta)
        if not evaluaciones:
            return False, "No hay evaluaciones registradas"
        porcentaje = self.porcentaje_total_evaluaciones(id_oferta)
        if porcentaje != Decimal("100"):
            return False, f"El porcentaje total debe ser 100%; actualmente es {porcentaje}%"
        return True, "Evaluaciones válidas para cálculo de nota final"

    def modificar_evaluacion(
        self,
        id_evaluacion: int,
        *,
        nombre: str | None = None,
        porcentaje: Decimal | None = None,
        fecha_programada: date | None = None,
    ) -> Evaluacion:
        """Modificar una evaluación existente con validaciones."""
        evaluacion = self._buscar(self.evaluaciones, "idEvaluacion", id_evaluacion)
        if nombre is not None:
            if not nombre.strip():
                raise ErrorCalificacion("El nombre no puede estar vacío")
            evaluacion.nombre = nombre.strip()
        if porcentaje is not None:
            if porcentaje <= 0 or porcentaje > 100:
                raise ErrorCalificacion("El porcentaje debe estar entre 0 y 100")
            evaluaciones_otra = [
                e for e in self.evaluaciones
                if e.idOfertaCurso == evaluacion.idOfertaCurso
                and e.idEvaluacion != id_evaluacion
                and e.estado in {None, "ACTIVO"}
            ]
            porcentaje_actual = sum((e.porcentaje or Decimal("0") for e in evaluaciones_otra), Decimal("0"))
            if porcentaje_actual + porcentaje > 100:
                raise ErrorCalificacion(
                    f"El nuevo porcentaje ({porcentaje}%) excedería el 100%. "
                    f"Porcentaje disponible: {100 - porcentaje_actual}"
                )
            evaluacion.porcentaje = porcentaje
        if fecha_programada is not None:
            evaluacion.fechaProgramada = fecha_programada
        return evaluacion
