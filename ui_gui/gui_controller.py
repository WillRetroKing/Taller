"""Controlador de estado y contenedor de servicios para la GUI del sistema PITA.

Administra la inicialización de gestores, la carga/guardado de persistencia
y provee acceso unificado a los servicios de la aplicación.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

from persistencia import GestorPersistencia, GestorCRUD
from nomina import GestorNomina
from gestores import (
    GestorAcademico,
    GestorCalificaciones,
    GestorContratos,
    GestorFactores,
    GestorMatriculas,
    GestorParametros,
    GestorPeriodosAcademicos,
    GestorPersonas,
)
from dominio import (
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

        # Asegurar nota mínima válida en cursos
        for cur in self.cursos:
            val_raw = getattr(cur, "notaMinimaAprobatoria", None)
            if val_raw is None:
                cur.notaMinimaAprobatoria = Decimal("3.0")
            else:
                try:
                    if float(val_raw) <= 0:
                        cur.notaMinimaAprobatoria = Decimal("3.0")
                    elif not isinstance(val_raw, Decimal):
                        cur.notaMinimaAprobatoria = Decimal(str(val_raw))
                except Exception:
                    cur.notaMinimaAprobatoria = Decimal("3.0")

        if not self.facultades:
            # Fallback a cargar entidad individual
            try:
                self.facultades = self.gestor_persistencia.cargar_entidad(Facultad)
                self.programas = self.gestor_persistencia.cargar_entidad(ProgramaAcademico)
            except Exception:
                pass

        # Asegurar parámetros normativos y gestores inicializados
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
            planes=self.planes,
            detalles_planes=self.detalles_plan,
            cursos=self.cursos,
            prerrequisitos=self.prerrequisitos,
            programas=self.programas,
            horarios=self.horarios,
            asignaciones=self.asignaciones,
            profesores=self.profesores,
            ofertas=self.ofertas,
        )
        self.gestor_periodos = GestorPeriodosAcademicos(
            self.periodos_academicos, self.ofertas
        )
        self.gestor_contratos = GestorContratos(
            self.contratos,
            profesores=self.profesores,
            administrativos=self.administrativos,
            liquidaciones=self.liquidaciones,
        )
        self.gestor_factores = GestorFactores(
            self.categorias, self.factores, self.producciones, self.profesores
        )
        self.gestor_nomina = GestorNomina(
            contratos=self.contratos,
            profesores=self.profesores,
            periodos_nomina=self.periodos_nomina,
            liquidaciones=self.liquidaciones,
            parametros=self.parametros,
            detalles_liquidacion=self.detalles_liquidacion,
            categorias=self.categorias,
            factores=self.factores,
            producciones=self.producciones,
            administrativos=self.administrativos,
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
            self.prerrequisitos,
            self.alertas,
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

    def iniciar_sin_datos(self, crear_parametros_defecto: bool = True) -> None:
        """Vacía todas las entidades académicas y contratos, dejando opcionalmente los parámetros normativos."""
        self.facultades.clear()
        self.programas.clear()
        self.planes.clear()
        self.detalles_plan.clear()
        self.cursos.clear()
        self.prerrequisitos.clear()
        self.periodos_academicos.clear()
        self.personas.clear()
        self.estudiantes.clear()
        self.profesores.clear()
        self.administrativos.clear()
        self.ofertas.clear()
        self.asignaciones.clear()
        self.horarios.clear()
        self.matriculas.clear()
        self.detalles_matricula.clear()
        self.evaluaciones.clear()
        self.calificaciones.clear()
        self.alertas.clear()
        self.contratos.clear()
        self.categorias.clear()
        self.factores.clear()
        self.producciones.clear()
        self.periodos_nomina.clear()
        self.liquidaciones.clear()
        self.conceptos.clear()
        self.detalles_liquidacion.clear()
        self.parametros.clear()

        if crear_parametros_defecto:
            self._crear_parametros_por_defecto()
            # Periodo de nómina activo por defecto
            self.periodos_nomina.append(
                PeriodoNomina(
                    idPeriodoNomina=1,
                    anio=2026,
                    mes=3,
                    fechaInicio=date(2026, 3, 1),
                    fechaFin=date(2026, 3, 31),
                    estado="ABIERTO",
                )
            )

        self.guardar_datos()
        self._recrear_gestores()

    def cargar_datos_demo(self) -> None:
        """Regenera la base de datos de demostración con datos iniciales completos de la UPC."""
        from scratch.generar_datos_iniciales import generar
        generar()
        self.cargar_datos()

    def _crear_parametros_por_defecto(self) -> None:
        """Genera los 20 parámetros normativos legales según Decreto 1279, Acuerdo 027 y leyes colombianas."""
        defaults = [
            ParametroNormativo(1, PNC.SALARIO_MINIMO, "Salario Mínimo Legal Vigente", "SMMLV Colombia", "MONETARIO", "1750905", "COP", "Decreto Nacional Salarial", "Art. 1", date(2026, 1, 1), date(2026, 12, 31), "TODOS", "ACTIVO"),
            ParametroNormativo(2, PNC.VALOR_PUNTO_SALARIAL, "Valor Punto Salarial", "Punto Salarial Dec. 1279", "MONETARIO", "23924", "COP", "Decreto 1279 de 2002", "Art. 27", date(2026, 1, 1), date(2026, 12, 31), "PLANTA", "ACTIVO"),
            ParametroNormativo(3, PNC.VALOR_AUXILIO_TRANSPORTE_VIGENTE, "Auxilio Transporte", "Auxilio legal transporte", "MONETARIO", "249095", "COP", "Decreto Nacional Auxilio Transporte", "Art. 1", date(2026, 1, 1), date(2026, 12, 31), "TODOS", "ACTIVO"),
            ParametroNormativo(4, PNC.VALOR_HORA_CATEDRA, "Valor Hora Cátedra", "Valor hora catedrático", "MONETARIO", "38500", "COP", "Acuerdo 027 de 2024", "Art. 15", date(2026, 1, 1), date(2026, 12, 31), "CATEDRATICO", "ACTIVO"),
            ParametroNormativo(5, PNC.PORCENTAJE_SALUD_TRABAJADOR, "Salud Trabajador %", "Descuento Salud 4%", "PORCENTUAL", "0.04", "%", "Ley 100 de 1993", "Art. 204", date(2026, 1, 1), date(2026, 12, 31), "TODOS", "ACTIVO"),
            ParametroNormativo(6, PNC.PORCENTAJE_SALUD_EMPLEADOR, "Salud Empleador %", "Aporte Salud Empleador 8.5%", "PORCENTUAL", "0.085", "%", "Ley 100 de 1993", "Art. 204", date(2026, 1, 1), date(2026, 12, 31), "TODOS", "ACTIVO"),
            ParametroNormativo(7, PNC.PORCENTAJE_PENSION_TRABAJADOR, "Pensión Trabajador %", "Descuento Pensión 4%", "PORCENTUAL", "0.04", "%", "Ley 100 de 1993", "Art. 20", date(2026, 1, 1), date(2026, 12, 31), "TODOS", "ACTIVO"),
            ParametroNormativo(8, PNC.PORCENTAJE_PENSION_EMPLEADOR, "Pensión Empleador %", "Aporte Pensión Empleador 12%", "PORCENTUAL", "0.12", "%", "Ley 100 de 1993", "Art. 20", date(2026, 1, 1), date(2026, 12, 31), "TODOS", "ACTIVO"),
            ParametroNormativo(9, PNC.PORCENTAJE_FONDO_SOLIDARIDAD, "Fondo Solidaridad %", "FSP para IBC >= 4 SMMLV", "PORCENTUAL", "0.01", "%", "Ley 797 de 2003", "Art. 8", date(2026, 1, 1), date(2026, 12, 31), "TODOS", "ACTIVO"),
            ParametroNormativo(10, PNC.PORCENTAJE_ARL_CLASE_I, "ARL Clase I %", "Riesgos Laborales Clase I", "PORCENTUAL", "0.00522", "%", "Decreto 1772 de 1994", "Art. 13", date(2026, 1, 1), date(2026, 12, 31), "TODOS", "ACTIVO"),
            ParametroNormativo(11, PNC.PORCENTAJE_ARL_CLASE_II, "ARL Clase II %", "Riesgos Laborales Clase II", "PORCENTUAL", "0.01044", "%", "Decreto 1772 de 1994", "Art. 13", date(2026, 1, 1), date(2026, 12, 31), "TODOS", "ACTIVO"),
            ParametroNormativo(12, PNC.PORCENTAJE_SENA, "SENA %", "Aporte Parafiscal SENA 2%", "PORCENTUAL", "0.02", "%", "Ley 21 de 1982", "Art. 7", date(2026, 1, 1), date(2026, 12, 31), "TODOS", "ACTIVO"),
            ParametroNormativo(13, PNC.PORCENTAJE_ICBF, "ICBF %", "Aporte Parafiscal ICBF 3%", "PORCENTUAL", "0.03", "%", "Ley 89 de 1988", "Art. 1", date(2026, 1, 1), date(2026, 12, 31), "TODOS", "ACTIVO"),
            ParametroNormativo(14, PNC.PORCENTAJE_CAJA_COMPENSACION, "Caja Compensación %", "Aporte Cuidado Familiar 4%", "PORCENTUAL", "0.04", "%", "Ley 21 de 1982", "Art. 7", date(2026, 1, 1), date(2026, 12, 31), "TODOS", "ACTIVO"),
            ParametroNormativo(15, PNC.TOPE_BONIFICACION_SERVICIOS, "Tope Bonificación Servicios", "Tope Decreto 1279", "MONETARIO", "756411", "COP", "Decreto 1279 de 2002", "Art. 41", date(2026, 1, 1), date(2026, 12, 31), "PLANTA", "ACTIVO"),
            ParametroNormativo(16, PNC.PORCENTAJE_BONIFICACION_SERVICIOS_HASTA_TOPE, "Bonificación Hasta Tope %", "Porcentaje BSP <= Tope (50%)", "PORCENTUAL", "0.50", "%", "Decreto 1279 de 2002", "Art. 41", date(2026, 1, 1), date(2026, 12, 31), "PLANTA", "ACTIVO"),
            ParametroNormativo(17, PNC.PORCENTAJE_BONIFICACION_SERVICIOS_SOBRE_TOPE, "Bonificación Sobre Tope %", "Porcentaje BSP > Tope (35%)", "PORCENTUAL", "0.35", "%", "Decreto 1279 de 2002", "Art. 41", date(2026, 1, 1), date(2026, 12, 31), "PLANTA", "ACTIVO"),
            ParametroNormativo(18, PNC.NOTA_MINIMA_APROBATORIA, "Nota Mínima Aprobatoria", "Nota mínima aprobar", "DECIMAL", "3.0", "puntos", "Reglamento Estudiantil", "Art. 45", date(2026, 1, 1), date(2026, 12, 31), "ESTUDIANTES", "ACTIVO"),
            ParametroNormativo(19, PNC.PROMEDIO_MINIMO_EBRA, "Promedio Mínimo EBRA", "Umbral de riesgo EBRA", "DECIMAL", "3.0", "puntos", "Reglamento Estudiantil", "Art. 52", date(2026, 1, 1), date(2026, 12, 31), "ESTUDIANTES", "ACTIVO"),
            ParametroNormativo(20, PNC.MAXIMO_CREDITOS_PERIODO, "Máximo Créditos Período", "Límite máximo de créditos semestrales", "DECIMAL", "22", "créditos", "Reglamento Estudiantil", "Art. 30", date(2026, 1, 1), date(2026, 12, 31), "ESTUDIANTES", "ACTIVO"),
        ]
        self.parametros.extend(defaults)
