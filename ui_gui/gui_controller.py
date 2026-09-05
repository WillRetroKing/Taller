"""Controlador de estado y contenedor de servicios para la GUI del sistema PITA.

Administra la inicialización de gestores, la carga/guardado de persistencia
y provee acceso unificado a los servicios de la aplicación.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from gestor_academico import GestorAcademico
from gestor_contratos import GestorContratos
from gestor_crud import GestorCRUD
from gestor_factores import GestorFactores
from gestor_nomina import GestorNomina
from gestor_parametros import GestorParametros
from gestor_periodos import GestorPeriodosAcademicos
from gestor_persistencia import GestorPersistencia
from gestor_personas import GestorPersonas
from gestores_academicos import GestorCalificaciones, GestorMatriculas

from modelo_datos import (
    Administrativo,
    AlertaAcademica,
    AsignacionDocente,
    Calificacion,
    CategoriaDocente,
    ConceptoNomina,
    Contrato,
    Curso,
    Dedicacion,
    DetalleLiquidacion,
    DetalleMatricula,
    DetallePlanEstudio,
    EstadoAcademico,
    EstadoCurso,
    Estudiante,
    Evaluacion,
    FactorSalarial,
    Facultad,
    Horario,
    LiquidacionNomina,
    MatriculaAcademica,
    OfertaCurso,
    ParametroNormativo,
    ParametroNormativoCodigo as PNC,
    PeriodoAcademico,
    PeriodoNomina,
    Persona,
    PlanEstudio,
    Prerrequisito,
    ProduccionAcademica,
    Profesor,
    ProgramaAcademico,
    TipoProfesor,
    Universidad,
)


class PITAController:
    """Contenedor singleton/controlador para la GUI."""

    def __init__(self, directorio_datos: str = "datos") -> None:
        self.directorio_datos = Path(directorio_datos)
        self.gestor_persistencia = GestorPersistencia(self.directorio_datos)

        self.universidad: Universidad | None = None
        self.facultades: list[Facultad] = []
        self.programas: list[ProgramaAcademico] = []
        self.planes: list[PlanEstudio] = []
        self.detalles_plan: list[DetallePlanEstudio] = []
        self.cursos: list[Curso] = []
        self.prerrequisitos: list[Prerrequisito] = []
        self.periodos_academicos: list[PeriodoAcademico] = []
        self.personas: list[Persona] = []
        self.estudiantes: list[Estudiante] = []
        self.profesores: list[Profesor] = []
        self.administrativos: list[Administrativo] = []
        self.ofertas: list[OfertaCurso] = []
        self.asignaciones: list[AsignacionDocente] = []
        self.horarios: list[Horario] = []
        self.matriculas: list[MatriculaAcademica] = []
        self.detalles_matricula: list[DetalleMatricula] = []
        self.evaluaciones: list[Evaluacion] = []
        self.calificaciones: list[Calificacion] = []
        self.alertas: list[AlertaAcademica] = []
        self.contratos: list[Contrato] = []
        self.categorias: list[CategoriaDocente] = []
        self.factores: list[FactorSalarial] = []
        self.producciones: list[ProduccionAcademica] = []
        self.periodos_nomina: list[PeriodoNomina] = []
        self.liquidaciones: list[LiquidacionNomina] = []
        self.conceptos: list[ConceptoNomina] = []
        self.detalles_liquidacion: list[DetalleLiquidacion] = []
        self.parametros: list[ParametroNormativo] = []

        self.cargar_datos()

    def cargar_datos(self) -> None:
        """Cargar datos desde disco si existen, o inicializar con valores por defecto."""
        if self.directorio_datos.exists() and any(self.directorio_datos.iterdir()):
            try:
                datos = self.gestor_persistencia.cargar_todos_los_datos()
                self.facultades = datos.get(Facultad, [])
                self.programas = datos.get(ProgramaAcademico, [])
                self.planes = datos.get(PlanEstudio, [])
                self.detalles_plan = datos.get(DetallePlanEstudio, [])
                self.cursos = datos.get(Curso, [])
                self.prerrequisitos = datos.get(Prerrequisito, [])
                self.periodos_academicos = datos.get(PeriodoAcademico, [])
                self.personas = datos.get(Persona, [])
                self.estudiantes = datos.get(Estudiante, [])
                self.profesores = datos.get(Profesor, [])
                self.administrativos = datos.get(Administrativo, [])
                self.ofertas = datos.get(OfertaCurso, [])
                self.asignaciones = datos.get(AsignacionDocente, [])
                self.horarios = datos.get(Horario, [])
                self.matriculas = datos.get(MatriculaAcademica, [])
                self.detalles_matricula = datos.get(DetalleMatricula, [])
                self.evaluaciones = datos.get(Evaluacion, [])
                self.calificaciones = datos.get(Calificacion, [])
                self.alertas = datos.get(AlertaAcademica, [])
                self.contratos = datos.get(Contrato, [])
                self.categorias = datos.get(CategoriaDocente, [])
                self.factores = datos.get(FactorSalarial, [])
                self.producciones = datos.get(ProduccionAcademica, [])
                self.periodos_nomina = datos.get(PeriodoNomina, [])
                self.liquidaciones = datos.get(LiquidacionNomina, [])
                self.conceptos = datos.get(ConceptoNomina, [])
                self.detalles_liquidacion = datos.get(DetalleLiquidacion, [])
                self.parametros = datos.get(ParametroNormativo, [])
            except Exception as e:
                print(f"Advertencia al cargar persistencia: {e}")

        if not self.facultades:
            # Fallback a cargar entidad individual
            try:
                self.facultades = self.gestor_persistencia.cargar_entidad(Facultad)
                self.programas = self.gestor_persistencia.cargar_entidad(ProgramaAcademico)
            except Exception:
                pass

        # Si aún no hay facultades o programas, sembrar datos de inicio de forma segura
        if not self.facultades or not self.programas:
            try:
                from scratch.generar_datos_iniciales import generar
                generar()
                datos = self.gestor_persistencia.cargar_todos_los_datos()
                self.facultades = datos.get(Facultad, [])
                self.programas = datos.get(ProgramaAcademico, [])
                self.planes = datos.get(PlanEstudio, [])
                self.detalles_plan = datos.get(DetallePlanEstudio, [])
                self.cursos = datos.get(Curso, [])
                self.prerrequisitos = datos.get(Prerrequisito, [])
                self.periodos_academicos = datos.get(PeriodoAcademico, [])
                self.personas = datos.get(Persona, [])
                self.estudiantes = datos.get(Estudiante, [])
                self.profesores = datos.get(Profesor, [])
                self.administrativos = datos.get(Administrativo, [])
                self.ofertas = datos.get(OfertaCurso, [])
                self.asignaciones = datos.get(AsignacionDocente, [])
                self.horarios = datos.get(Horario, [])
                self.matriculas = datos.get(MatriculaAcademica, [])
                self.detalles_matricula = datos.get(DetalleMatricula, [])
                self.evaluaciones = datos.get(Evaluacion, [])
                self.calificaciones = datos.get(Calificacion, [])
                self.alertas = datos.get(AlertaAcademica, [])
                self.contratos = datos.get(Contrato, [])
                self.categorias = datos.get(CategoriaDocente, [])
                self.factores = datos.get(FactorSalarial, [])
                self.producciones = datos.get(ProduccionAcademica, [])
                self.periodos_nomina = datos.get(PeriodoNomina, [])
                self.liquidaciones = datos.get(LiquidacionNomina, [])
                self.conceptos = datos.get(ConceptoNomina, [])
                self.detalles_liquidacion = datos.get(DetalleLiquidacion, [])
                self.parametros = datos.get(ParametroNormativo, [])
            except Exception as ex:
                print(f"Error al sembrar datos iniciales: {ex}")

        # Si no hay parámetros normativos, generar los por defecto
        if not self.parametros:
            self._crear_parametros_por_defecto()

        self._recrear_gestores()

    def _recrear_gestores(self) -> None:
        """Instanciar o actualizar gestores con las listas vigentes."""
        self.gestor_parametros = GestorParametros(self.parametros)
        self.gestor_personas = GestorPersonas(
            self.personas, self.estudiantes, self.profesores, self.administrativos
        )
        self.gestor_academico = GestorAcademico(
            self.facultades, self.programas, self.planes, self.cursos
        )
        self.gestor_periodos = GestorPeriodosAcademicos(
            self.periodos_academicos, self.ofertas
        )
        self.gestor_contratos = GestorContratos(self.contratos)
        self.gestor_factores = GestorFactores(
            self.categorias, self.factores, self.producciones, self.profesores
        )
        self.gestor_nomina = GestorNomina(
            self.periodos_nomina, self.liquidaciones, self.conceptos
        )
        self.gestor_matriculas = GestorMatriculas(
            self.estudiantes,
            self.periodos_academicos,
            self.ofertas,
            self.cursos,
            self.matriculas,
            self.detalles_matricula,
            self.horarios,
            self.parametros,
        )
        self.gestor_calificaciones = GestorCalificaciones(
            self.evaluaciones,
            self.calificaciones,
            self.detalles_matricula,
            self.matriculas,
            self.estudiantes,
            self.ofertas,
            self.cursos,
            self.parametros,
        )
        self.gestor_crud = GestorCRUD(self.facultades, campo_id="idFacultad", campo_codigo="codigoFacultad")

    def guardar_datos(self) -> None:
        """Guardar todas las entidades en la persistencia de archivos planos."""
        datos = {
            Facultad: self.facultades,
            ProgramaAcademico: self.programas,
            PlanEstudio: self.planes,
            DetallePlanEstudio: self.detalles_plan,
            Curso: self.cursos,
            Prerrequisito: self.prerrequisitos,
            PeriodoAcademico: self.periodos_academicos,
            Persona: self.personas,
            Estudiante: self.estudiantes,
            Profesor: self.profesores,
            Administrativo: self.administrativos,
            OfertaCurso: self.ofertas,
            AsignacionDocente: self.asignaciones,
            Horario: self.horarios,
            MatriculaAcademica: self.matriculas,
            DetalleMatricula: self.detalles_matricula,
            Evaluacion: self.evaluaciones,
            Calificacion: self.calificaciones,
            AlertaAcademica: self.alertas,
            Contrato: self.contratos,
            CategoriaDocente: self.categorias,
            FactorSalarial: self.factores,
            ProduccionAcademica: self.producciones,
            PeriodoNomina: self.periodos_nomina,
            LiquidacionNomina: self.liquidaciones,
            ConceptoNomina: self.conceptos,
            DetalleLiquidacion: self.detalles_liquidacion,
            ParametroNormativo: self.parametros,
        }
        self.gestor_persistencia.guardar_todos_los_datos(datos)

    def _crear_parametros_por_defecto(self) -> None:
        """Genera parámetros normativos del Decreto 1279 y Acuerdo 027."""
        from datetime import date

        defaults = [
            ParametroNormativo(1, PNC.SALARIO_MINIMO, "Salario Mínimo Legal Vigente", "SMMLV Colombia 2026", "MONETARIO", "1423500", "COP", "Acuerdo 027", "Art. 1", date(2026, 1, 1), date(2026, 12, 31), "TODOS", "ACTIVO"),
            ParametroNormativo(2, PNC.VALOR_PUNTO_SALARIAL, "Valor Punto Salarial", "Punto Salarial Dec. 1279", "MONETARIO", "19850", "COP", "Decreto 1279 de 2002", "Art. 27", date(2026, 1, 1), date(2026, 12, 31), "PLANTA", "ACTIVO"),
            ParametroNormativo(3, PNC.VALOR_AUXILIO_TRANSPORTE_VIGENTE, "Auxilio Transporte", "Auxilio legal transporte", "MONETARIO", "162000", "COP", "Acuerdo 027", "Art. 23", date(2026, 1, 1), date(2026, 12, 31), "TODOS", "ACTIVO"),
            ParametroNormativo(4, PNC.VALOR_HORA_CATEDRA, "Valor Hora Cátedra", "Valor hora catedrático", "MONetARIO", "38500", "COP", "Resolución Rectoral", "Art. 4", date(2026, 1, 1), date(2026, 12, 31), "CATEDRATICO", "ACTIVO"),
            ParametroNormativo(5, PNC.PORCENTAJE_SALUD_TRABAJADOR, "Salud Trabajador %", "Descuento Salud 4%", "PORCENTUAL", "0.04", "%", "Ley 100 de 1993", "Art. 204", date(2026, 1, 1), date(2026, 12, 31), "TODOS", "ACTIVO"),
            ParametroNormativo(6, PNC.PORCENTAJE_PENSION_TRABAJADOR, "Pensión Trabajador %", "Descuento Pensión 4%", "PORCENTUAL", "0.04", "%", "Ley 100 de 1993", "Art. 20", date(2026, 1, 1), date(2026, 12, 31), "TODOS", "ACTIVO"),
            ParametroNormativo(7, PNC.PORCENTAJE_FONDO_SOLIDARIDAD, "Fondo Solidaridad %", "FSP para IBC >= 4 SMMLV", "PORCENTUAL", "0.01", "%", "Ley 797 de 2003", "Art. 8", date(2026, 1, 1), date(2026, 12, 31), "TODOS", "ACTIVO"),
            ParametroNormativo(8, PNC.NOTA_MINIMA_APROBATORIA, "Nota Mínima Aprobatoria", "Nota mínima aprobar", "DECIMAL", "3.0", "puntos", "Reglamento Estudiantil", "Art. 45", date(2026, 1, 1), date(2026, 12, 31), "ESTUDIANTES", "ACTIVO"),
            ParametroNormativo(9, PNC.PROMEDIO_MINIMO_EBRA, "Promedio Mínimo EBRA", "Umbral de riesgo EBRA", "DECIMAL", "3.0", "puntos", "Reglamento Estudiantil", "Art. 52", date(2026, 1, 1), date(2026, 12, 31), "ESTUDIANTES", "ACTIVO"),
            ParametroNormativo(10, PNC.TOPE_BONIFICACION_SERVICIOS, "Tope Bonificación Servicios", "Tope Decreto 1279", "MONETARIO", "756411", "COP", "Decreto 1279 de 2002", "Art. 41", date(2026, 1, 1), date(2026, 12, 31), "PLANTA", "ACTIVO"),
        ]
        self.parametros.extend(defaults)
