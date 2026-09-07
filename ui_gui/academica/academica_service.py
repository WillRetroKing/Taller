"""Servicio de lógica de negocio y reglas de dominio para la gestión académica."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from dominio.modelo_datos import (
    AsignacionDocente,
    Curso,
    DetalleMatricula,
    EstadoAcademico,
    EstadoCurso,
    MatriculaAcademica,
    OfertaCurso,
)
from ui_gui.components import clean_enum

if TYPE_CHECKING:
    from ui_gui.gui_controller import PITAController


class AcademicaService:
    """Encapsula la lógica de negocio, validaciones y orquestación académica."""

    def __init__(self, controller: PITAController) -> None:
        self.controller = controller

    # ------------------------------------------------------------------
    # GESTIÓN DE PARÁMETROS Y REGLAS DE CRÉDITOS
    # ------------------------------------------------------------------
    def obtener_max_creditos(self) -> int:
        """Obtiene el tope de créditos por periodo desde los parámetros normativos o valor por defecto."""
        max_creditos = 20
        gp = getattr(self.controller, "gestor_parametros", None)
        if gp:
            fn_param = getattr(gp, "obtener_parametro", None) or getattr(gp, "buscar_parametro_vigente", None)
            if callable(fn_param):
                p_obj = fn_param("MAXIMO_CREDITOS_PERIODO")
                if p_obj and getattr(p_obj, "valor", None):
                    try:
                        max_creditos = int(p_obj.valor)
                    except (ValueError, TypeError):
                        pass
        return max_creditos

    def calcular_creditos_estudiante(self, id_estudiante: int) -> int:
        """Calcula el total de créditos activos inscritos para un estudiante."""
        matricula_ids = {m.idMatricula for m in self.controller.matriculas if m.idEstudiante == id_estudiante}
        ofertas_map = {o.idOfertaCurso: o for o in self.controller.ofertas}
        cursos_map = {c.idCurso: c for c in self.controller.cursos}

        creditos = 0
        for d in self.controller.detalles_matricula:
            if clean_enum(getattr(d, "estadoCurso", "")) != "CANCELADO" and d.idMatricula in matricula_ids:
                oferta = ofertas_map.get(d.idOfertaCurso)
                if oferta:
                    curso = cursos_map.get(oferta.idCurso)
                    if curso and curso.numeroCreditos:
                        creditos += curso.numeroCreditos
        return creditos

    # ------------------------------------------------------------------
    # MATRÍCULA Y CANCELACIÓN DE ASIGNATURAS
    # ------------------------------------------------------------------
    def matricular_estudiante(self, cod_estudiante: str, id_oferta: int) -> tuple[bool, str]:
        """Aplica todas las validaciones académicas y formaliza la matrícula de un estudiante."""
        est = next((e for e in self.controller.estudiantes if getattr(e, "codigoEstudiante", "") == cod_estudiante), None)
        oferta = next((o for o in self.controller.ofertas if o.idOfertaCurso == id_oferta), None)

        if not est or not oferta:
            return False, "⚠️ Estudiante u oferta no encontrados."

        curso = next((c for c in self.controller.cursos if c.idCurso == oferta.idCurso), None)
        if not curso:
            return False, "⚠️ Asignatura asociada a la oferta no encontrada."

        # 1. Validar cupo
        if (oferta.cupoDisponible or 0) <= 0:
            return False, f"⚠️ No hay cupos disponibles en la oferta {oferta.idOfertaCurso} (Cupo 0)."

        # 2. Validar inscripción previa
        matricula_ids = {m.idMatricula for m in self.controller.matriculas if m.idEstudiante == est.idEstudiante}
        ya_inscrito = any(
            d.idOfertaCurso == oferta.idOfertaCurso
            and clean_enum(getattr(d, "estadoCurso", "")) != "CANCELADO"
            and d.idMatricula in matricula_ids
            for d in self.controller.detalles_matricula
        )
        if ya_inscrito:
            return False, f"⚠️ El estudiante {cod_estudiante} ya se encuentra matriculado en este curso/grupo."

        # 3. Validar límite normativo de créditos
        creditos_actuales = self.calcular_creditos_estudiante(est.idEstudiante)
        max_creditos = self.obtener_max_creditos()
        nuevo_cred = curso.numeroCreditos or 3

        if creditos_actuales + nuevo_cred > max_creditos:
            return False, f"⚠️ Excede límite de créditos ({creditos_actuales} + {nuevo_cred} > {max_creditos} créditos máx)."

        # 4. Obtener o crear Matrícula para el periodo
        id_per = oferta.idPeriodo or 1
        mat = next((m for m in self.controller.matriculas if m.idEstudiante == est.idEstudiante and m.idPeriodo == id_per), None)
        if not mat:
            new_id_m = max((m.idMatricula or 0 for m in self.controller.matriculas), default=0) + 1
            mat = MatriculaAcademica(
                idMatricula=new_id_m,
                idEstudiante=est.idEstudiante,
                idPeriodo=id_per,
                fechaMatricula=date.today(),
                totalCreditos=nuevo_cred,
                promedioPeriodo=Decimal("0.0"),
                estadoMatricula="ACTIVO",
            )
            self.controller.matriculas.append(mat)
        else:
            mat.totalCreditos = (mat.totalCreditos or 0) + nuevo_cred

        # 5. Crear DetalleMatricula
        new_id_d = max((d.idDetalleMatricula or 0 for d in self.controller.detalles_matricula), default=0) + 1
        det = DetalleMatricula(
            idDetalleMatricula=new_id_d,
            idMatricula=mat.idMatricula,
            idOfertaCurso=oferta.idOfertaCurso,
            fechaInscripcion=date.today(),
            estadoCurso=EstadoCurso.EN_CURSO,
            notaFinal=None,
        )
        self.controller.detalles_matricula.append(det)

        # 6. Descontar cupo
        oferta.cupoDisponible = max(0, (oferta.cupoDisponible or 1) - 1)

        self.controller._recrear_gestores()
        self.controller.guardar_datos()
        return True, f"✅ Matrícula exitosa para {est.codigoEstudiante} en {curso.nombre} (Gr. {oferta.grupo})."

    def cancelar_curso_estudiante(self, id_detalle: int) -> bool:
        """Cancela la inscripción de un estudiante, restituyendo el cupo y ajustando créditos."""
        det = next((d for d in self.controller.detalles_matricula if d.idDetalleMatricula == id_detalle), None)
        if not det:
            return False

        det.estadoCurso = EstadoCurso.CANCELADO
        det.fechaCancelacion = date.today()
        det.motivoCancelacion = "Cancelación a solicitud del estudiante"

        # Reponer cupo a la oferta
        oferta = next((o for o in self.controller.ofertas if o.idOfertaCurso == det.idOfertaCurso), None)
        if oferta:
            oferta.cupoDisponible = min(oferta.cupoMaximo or 35, (oferta.cupoDisponible or 0) + 1)

        # Restar créditos de la matrícula
        mat = next((m for m in self.controller.matriculas if m.idMatricula == det.idMatricula), None)
        curso = next((c for c in self.controller.cursos if oferta and c.idCurso == oferta.idCurso), None)
        if mat and curso and mat.totalCreditos:
            mat.totalCreditos = max(0, mat.totalCreditos - (curso.numeroCreditos or 0))

        self.controller._recrear_gestores()
        self.controller.guardar_datos()
        return True

    # ------------------------------------------------------------------
    # EVALUACIONES, NOTAS Y PROMEDIO EBRA
    # ------------------------------------------------------------------
    def actualizar_promedio_estudiante(self, id_estudiante: int) -> None:
        """Recalcula el promedio acumulado del estudiante y actualiza el estado EBRA."""
        est = next((e for e in self.controller.estudiantes if e.idEstudiante == id_estudiante), None)
        if not est:
            return

        matricula_ids = {m.idMatricula for m in self.controller.matriculas if m.idEstudiante == id_estudiante}
        notas_est = [
            float(d.notaFinal) for d in self.controller.detalles_matricula
            if clean_enum(getattr(d, "estadoCurso", "")) != "CANCELADO"
            and d.notaFinal is not None
            and d.idMatricula in matricula_ids
        ]

        if notas_est:
            prom = round(sum(notas_est) / len(notas_est), 2)
            est.promedioAcumulado = Decimal(str(prom))
            if prom < 3.0:
                est.estadoAcademico = EstadoAcademico.EBRA
            else:
                est.estadoAcademico = EstadoAcademico.ACTIVO
        else:
            est.promedioAcumulado = Decimal("0.0")
            est.estadoAcademico = EstadoAcademico.ACTIVO

    def registrar_nota(self, id_detalle: int, nota: Decimal) -> bool:
        """Registra o actualiza la nota definitiva de un detalle de matrícula."""
        det = next((d for d in self.controller.detalles_matricula if d.idDetalleMatricula == id_detalle), None)
        if not det:
            return False

        det.notaFinal = nota
        det.estadoCurso = EstadoCurso.APROBADO if nota >= Decimal("3.0") else EstadoCurso.REPROBADO

        mat = next((m for m in self.controller.matriculas if m.idMatricula == det.idMatricula), None)
        if mat and mat.idEstudiante:
            self.actualizar_promedio_estudiante(mat.idEstudiante)

        self.controller._recrear_gestores()
        self.controller.guardar_datos()
        return True

    def limpiar_nota(self, id_detalle: int) -> bool:
        """Elimina la nota definitiva devolviendo el detalle a estado EN_CURSO."""
        det = next((d for d in self.controller.detalles_matricula if d.idDetalleMatricula == id_detalle), None)
        if not det:
            return False

        det.notaFinal = None
        det.estadoCurso = EstadoCurso.EN_CURSO

        mat = next((m for m in self.controller.matriculas if m.idMatricula == det.idMatricula), None)
        if mat and mat.idEstudiante:
            self.actualizar_promedio_estudiante(mat.idEstudiante)

        self.controller._recrear_gestores()
        self.controller.guardar_datos()
        return True

    # ------------------------------------------------------------------
    # CRUD ASIGNATURAS Y OFERTAS
    # ------------------------------------------------------------------
    def crear_curso(
        self,
        codigo: str,
        nombre: str,
        creditos: int,
        ht: int,
        hp: int,
        cupo: int,
        nota_minima: Decimal = Decimal("3.0"),
    ) -> Curso:
        """Crea una nueva asignatura en el catálogo y persiste los cambios."""
        new_id = max((c.idCurso or 0 for c in self.controller.cursos), default=0) + 1
        curso = Curso(
            idCurso=new_id,
            codigoCurso=codigo,
            nombre=nombre,
            descripcion=nombre,
            numeroCreditos=creditos,
            horasTeoricas=ht,
            horasPracticas=hp,
            horasTrabajoIndependiente=ht * 2,
            cupoSugerido=cupo,
            notaMinimaAprobatoria=nota_minima,
            estado="ACTIVO",
        )
        self.controller.cursos.append(curso)
        self.controller._recrear_gestores()
        self.controller.guardar_datos()
        return curso

    def eliminar_curso(self, id_curso: int) -> None:
        """Elimina una asignatura del catálogo y persiste los cambios."""
        self.controller.cursos = [c for c in self.controller.cursos if c.idCurso != id_curso]
        self.controller._recrear_gestores()
        self.controller.guardar_datos()

    def crear_oferta(
        self,
        id_curso: int,
        id_periodo: int,
        grupo: str,
        cupo: int,
        aula: str,
        sede: str,
        modalidad: str,
        id_profesor: int | None = None,
    ) -> OfertaCurso:
        """Crea una nueva oferta académica para un periodo y grupo."""
        new_id_of = max((o.idOfertaCurso or 0 for o in self.controller.ofertas), default=0) + 1
        oferta = OfertaCurso(
            idOfertaCurso=new_id_of,
            idCurso=id_curso,
            idPeriodo=id_periodo,
            grupo=grupo,
            cupoMaximo=cupo,
            cupoDisponible=cupo,
            aula=aula,
            sede=sede,
            modalidad=modalidad,
            estado="ACTIVO",
        )
        self.controller.ofertas.append(oferta)

        if id_profesor:
            new_id_asig = max((a.idAsignacionDocente or 0 for a in self.controller.asignaciones), default=0) + 1
            asig = AsignacionDocente(
                idAsignacionDocente=new_id_asig,
                idProfesor=id_profesor,
                idOfertaCurso=new_id_of,
                horasSemanales=4,
                fechaAsignacion=date.today(),
                estado="ACTIVO",
            )
            self.controller.asignaciones.append(asig)

        self.controller._recrear_gestores()
        self.controller.guardar_datos()
        return oferta

    def eliminar_oferta(self, id_oferta: int) -> None:
        """Elimina una oferta académica y sus asignaciones docentes asociadas."""
        self.controller.ofertas = [o for o in self.controller.ofertas if o.idOfertaCurso != id_oferta]
        self.controller.asignaciones = [a for a in self.controller.asignaciones if a.idOfertaCurso != id_oferta]
        self.controller._recrear_gestores()
        self.controller.guardar_datos()

    # ------------------------------------------------------------------
    # ANALÍTICA EBRA
    # ------------------------------------------------------------------
    def calcular_kpis_ebra(self) -> dict[str, Any]:
        """Calcula los indicadores globales de desempeño y alertas EBRA."""
        total_est = len(self.controller.estudiantes)
        ebras = [e for e in self.controller.estudiantes if clean_enum(getattr(e, "estadoAcademico", "")) == "EBRA"]
        total_ebras = len(ebras)
        normales = total_est - total_ebras

        promedios = [float(e.promedioAcumulado) for e in self.controller.estudiantes if e.promedioAcumulado]
        prom_global = sum(promedios) / max(1, len(promedios)) if promedios else 0.0

        return {
            "total_estudiantes": total_est,
            "total_ebras": total_ebras,
            "normales": normales,
            "promedio_global": prom_global,
            "estudiantes_ebra": ebras,
        }
