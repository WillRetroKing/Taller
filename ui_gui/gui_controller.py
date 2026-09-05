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
from gestor_factores import GestorFactoresSalariales
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

        # Si no hay parámetros normativos, generar los por defecto
        if not self.parametros:
            self._crear_parametros_por_defecto()

        # Si el sistema está vacío, sembrar algunos datos demostrativos
        if not self.facultades and not self.personas:
            self.sembrar_datos_ejemplo()

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
        self.gestor_factores = GestorFactoresSalariales(
            self.factores, self.producciones
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
        self.gestor_crud = GestorCRUD(self.facultades, "idFacultad", "codigoFacultad")

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

    def sembrar_datos_ejemplo(self) -> None:
        """Sembrar datos institucionales iniciales para demostración."""
        # 1. Facultad
        f1 = Facultad(1, "FAC-ING", "Facultad de Ingenierías y Tecnológicas", "Ingenierías UPC", "Sede Sabanas", "5842000", "ingenieria@unicesar.edu.co", None, date(1998, 3, 15), "ACTIVO")
        self.facultades.append(f1)

        # 2. Programa
        p1 = ProgramaAcademico(1, "PROG-ING-SIST", "Ingeniería de Sistemas", "PREGRADO", "PRESENCIAL", 10, 165, "RC-2024-001", date(2000, 1, 10), None, 1, "ACTIVO")
        self.programas.append(p1)

        # 3. Cursos
        c1 = Curso(1, "INF-101", "Estructura de Datos", "Listas, Árboles, Grafos y Complejidad", 4, 4, 2, 6, 35, "3.0", "ACTIVO")
        c2 = Curso(2, "INF-102", "Bases de Datos I", "Modelado relacional y SQL", 3, 3, 2, 4, 30, "3.0", "ACTIVO")
        self.cursos.extend([c1, c2])

        # 4. Periodo Académico
        per1 = PeriodoAcademico(1, "2026-1", "Periodo Académico 2026-I", 2026, 1, date(2026, 2, 1), date(2026, 6, 30), date(2026, 1, 15), date(2026, 1, 30), date(2026, 3, 15), "ACTIVO")
        self.periodos_academicos.append(per1)

        # 5. Personas y Estudiantes
        p_est1 = Persona(1, "CC", "1065123456", "Carlos", "Alberto", "Mendoza", "Ríos", date(2003, 5, 12), "Calle 12 #4-20", "3001234567", "carlos@gmail.com", "cmendoza@unicesar.edu.co", "Valledupar", date(2023, 1, 15), "ACTIVO")
        p_est2 = Persona(2, "CC", "1065987654", "Ana", "María", "Gómez", "López", date(2004, 8, 22), "Cra 9 #15-30", "3159876543", "ana@gmail.com", "agomez@unicesar.edu.co", "Valledupar", date(2023, 1, 15), "ACTIVO")
        self.personas.extend([p_est1, p_est2])

        e1 = Estudiante(1, 1, "EST-2026-01", 1, 1, date(2023, 1, 15), 4, 45, "2.7", EstadoAcademico.EBRA, "ACTIVO")
        e2 = Estudiante(2, 2, "EST-2026-02", 1, 1, date(2023, 1, 15), 4, 52, "4.2", EstadoAcademico.ACTIVO, "ACTIVO")
        self.estudiantes.extend([e1, e2])

        # 6. Profesores
        p_prof1 = Persona(3, "CC", "77123456", "Adith", "Enrique", "Pérez", "Orozco", date(1980, 4, 10), "Av. Universidad", "3104567890", "adith@gmail.com", "adithperez@unicesar.edu.co", "Valledupar", date(2010, 2, 1), "ACTIVO")
        p_prof2 = Persona(4, "CC", "77987654", "Roberto", "Carlos", "Martínez", "Díaz", date(1985, 11, 5), "Calle 16 #9-40", "3017654321", "roberto@gmail.com", "rmartinez@unicesar.edu.co", "Valledupar", date(2015, 8, 10), "ACTIVO")
        self.personas.extend([p_prof1, p_prof2])

        prof1 = Profesor(1, 3, "PROF-001", 1, date(2010, 2, 1), TipoProfesor.PLANTA, CategoriaDocente.TITULAR, Dedicacion.TIEMPO_COMPLETO, "DOCTORADO", "Ingeniero de Sistemas", "Estructura de Datos", 40, "450", "ACTIVO", "Decreto 1279")
        prof2 = Profesor(2, 4, "PROF-002", 1, date(2020, 1, 15), TipoProfesor.CATEDRATICO, CategoriaDocente.ASISTENTE, Dedicacion.HORA_CATEDRA, "MAESTRIA", "Ingeniero de Sistemas", "Bases de Datos", 12, "0", "ACTIVO", "Acuerdo 027")
        self.profesores.extend([prof1, prof2])

        # 7. Contratos
        c_prof1 = Contrato(1, 1, "CONT-2026-001", "DOCENTE_PLANTA", date(2026, 1, 1), date(2026, 12, 31), 40, "4500000", "ASIGNADO", "ACTIVO", "Acto Adm 045")
        c_prof2 = Contrato(2, 2, "CONT-2026-002", "DOCENTE_CATEDRATICO", date(2026, 2, 1), date(2026, 6, 30), 12, "1848000", "ASIGNADO", "ACTIVO", "Acto Adm 089")
        self.contratos.extend([c_prof1, c_prof2])

        # 8. Periodo de Nómina
        per_nom = PeriodoNomina(1, "NOM-2026-03", "Nómina Mar/2026", 2026, 3, date(2026, 3, 1), date(2026, 3, 31), "ABIERTO")
        self.periodos_nomina.append(per_nom)
