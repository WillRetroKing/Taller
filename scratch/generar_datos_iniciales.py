"""Script para poblar archivos de persistencia en datos/ y data/ con datos iniciales ricos y limpios."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datetime import date
from decimal import Decimal

from dominio.modelo_datos import (
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
    TipoFactor,
    TipoProfesor,
    Universidad,
)
from persistencia.gestor_persistencia import GestorPersistencia
from nomina.gestor_nomina import GestorNomina


def generar() -> None:
    # 1. Universidad
    uni = Universidad(
        idUniversidad=1,
        nombre="Universidad Popular del Cesar",
        nit="892300128-6",
        codigoInstitucional="1084",
        direccion="Sede Sabanas, Av. Universidad",
        ciudad="Valledupar",
        departamento="Cesar",
        telefono="5842000",
        correoInstitucional="rectoria@unicesar.edu.co",
        sitioWeb="https://www.unicesar.edu.co",
        estado="ACTIVO",
    )

    # 2. Facultades
    f1 = Facultad(idFacultad=1, codigoFacultad="FAC-ING", nombre="Facultad de Ingenierías y Tecnológicas", descripcion="Formación integral en tecnologías", ubicacion="Sede Sabanas", telefono="5842001", correo="ingenieria@unicesar.edu.co", idDecano=1, fechaCreacion=date(1998, 3, 15), estado="ACTIVO")
    f2 = Facultad(idFacultad=2, codigoFacultad="FAC-SALUD", nombre="Facultad de Ciencias de la Salud", descripcion="Formación en salud", ubicacion="Sede Campus San Martín", telefono="5842002", correo="salud@unicesar.edu.co", idDecano=2, fechaCreacion=date(2000, 5, 20), estado="ACTIVO")
    f3 = Facultad(idFacultad=3, codigoFacultad="FAC-FACAC", nombre="Facultad de Ciencias Administrativas", descripcion="Formación empresarial", ubicacion="Sede Hurtado", telefono="5842003", correo="facac@unicesar.edu.co", idDecano=3, fechaCreacion=date(1995, 8, 10), estado="ACTIVO")
    facultades = [f1, f2, f3]

    # 3. Programas Académicos
    p1 = ProgramaAcademico(idPrograma=1, codigoPrograma="PROG-ING-SIST", nombre="Ingeniería de Sistemas", nivelFormacion="PREGRADO", modalidad="PRESENCIAL", numeroSemestres=10, totalCreditos=165, registroCalificado="RC-2024-001", fechaCreacion=date(2000, 1, 10), idDirector=1, idFacultad=1, estado="ACTIVO")
    p2 = ProgramaAcademico(idPrograma=2, codigoPrograma="PROG-ENFERMERIA", nombre="Enfermería", nivelFormacion="PREGRADO", modalidad="PRESENCIAL", numeroSemestres=9, totalCreditos=170, registroCalificado="RC-2023-088", fechaCreacion=date(2002, 3, 12), idDirector=2, idFacultad=2, estado="ACTIVO")
    p3 = ProgramaAcademico(idPrograma=3, codigoPrograma="PROG-ADMIN", nombre="Administración de Empresas", nivelFormacion="PREGRADO", modalidad="PRESENCIAL", numeroSemestres=10, totalCreditos=160, registroCalificado="RC-2022-045", fechaCreacion=date(1996, 6, 18), idDirector=3, idFacultad=3, estado="ACTIVO")
    programas = [p1, p2, p3]

    # 4. Planes de Estudio
    pe1 = PlanEstudio(idPlanEstudio=1, codigo="PLAN-SIST-2024", nombre="Plan Sistemas 2024", version="v2", fechaInicioVigencia=date(2024, 1, 1), fechaFinVigencia=date(2028, 12, 31), totalCreditos=165, idPrograma=1, estado="ACTIVO")
    pe2 = PlanEstudio(idPlanEstudio=2, codigo="PLAN-ENF-2023", nombre="Plan Enfermería 2023", version="v1", fechaInicioVigencia=date(2023, 1, 1), fechaFinVigencia=date(2027, 12, 31), totalCreditos=170, idPrograma=2, estado="ACTIVO")
    planes = [pe1, pe2]

    # 5. Cursos
    c1 = Curso(idCurso=1, codigoCurso="INF-101", nombre="Estructura de Datos", descripcion="Listas, Árboles, Grafos", numeroCreditos=4, horasTeoricas=4, horasPracticas=2, horasTrabajoIndependiente=6, cupoSugerido=35, notaMinimaAprobatoria=Decimal("3.0"), estado="ACTIVO")
    c2 = Curso(idCurso=2, codigoCurso="INF-102", nombre="Bases de Datos I", descripcion="Modelado relacional y SQL", numeroCreditos=3, horasTeoricas=3, horasPracticas=2, horasTrabajoIndependiente=4, cupoSugerido=30, notaMinimaAprobatoria=Decimal("3.0"), estado="ACTIVO")
    c3 = Curso(idCurso=3, codigoCurso="INF-103", nombre="Programación Orientada a Objetos", descripcion="Paradigma POO en Java/Python", numeroCreditos=4, horasTeoricas=4, horasPracticas=2, horasTrabajoIndependiente=6, cupoSugerido=35, notaMinimaAprobatoria=Decimal("3.0"), estado="ACTIVO")
    c4 = Curso(idCurso=4, codigoCurso="ENF-101", nombre="Anatomía Humana", descripcion="Morfología general", numeroCreditos=4, horasTeoricas=3, horasPracticas=3, horasTrabajoIndependiente=4, cupoSugerido=25, notaMinimaAprobatoria=Decimal("3.0"), estado="ACTIVO")
    c5 = Curso(idCurso=5, codigoCurso="ADM-101", nombre="Fundamentos de Administración", descripcion="Teoría administrativa", numeroCreditos=3, horasTeoricas=3, horasPracticas=0, horasTrabajoIndependiente=6, cupoSugerido=40, notaMinimaAprobatoria=Decimal("3.0"), estado="ACTIVO")
    cursos = [c1, c2, c3, c4, c5]

    dp1 = DetallePlanEstudio(idDetallePlan=1, idPlanEstudio=1, idCurso=1, semestreSugerido=3, tipoCurso="OBLIGATORIO", numeroCreditos=4, esObligatorio=True, estado="ACTIVO")
    dp2 = DetallePlanEstudio(idDetallePlan=2, idPlanEstudio=1, idCurso=2, semestreSugerido=4, tipoCurso="OBLIGATORIO", numeroCreditos=3, esObligatorio=True, estado="ACTIVO")
    dp3 = DetallePlanEstudio(idDetallePlan=3, idPlanEstudio=1, idCurso=3, semestreSugerido=2, tipoCurso="OBLIGATORIO", numeroCreditos=4, esObligatorio=True, estado="ACTIVO")
    detalles_plan = [dp1, dp2, dp3]

    pr1 = Prerrequisito(idPrerrequisito=1, idCurso=1, idCursoRequerido=3, tipoRequisito="ASIGNATURA", notaMinima=Decimal("3.0"), creditosMinimos=0, estado="ACTIVO")
    prerrequisitos = [pr1]

    per1 = PeriodoAcademico(idPeriodo=1, codigo="2026-1", nombre="Periodo Académico 2026-I", anio=2026, numeroPeriodo=1, fechaInicio=date(2026, 2, 1), fechaFin=date(2026, 6, 30), fechaInicioMatricula=date(2026, 1, 15), fechaFinMatricula=date(2026, 1, 30), fechaLimiteCancelacion=date(2026, 3, 15), estado="ACTIVO")
    periodos = [per1]

    o1 = OfertaCurso(idOfertaCurso=1, idCurso=1, idPeriodo=1, grupo=1, cupoMaximo=35, cupoDisponible=30, modalidad="PRESENCIAL", aula="Lab 201", sede="Sabanas", fechaInicio=date(2026, 2, 1), fechaFin=date(2026, 6, 30), estado="ACTIVO")
    o2 = OfertaCurso(idOfertaCurso=2, idCurso=2, idPeriodo=1, grupo=1, cupoMaximo=30, cupoDisponible=25, modalidad="PRESENCIAL", aula="Aula 104", sede="Sabanas", fechaInicio=date(2026, 2, 1), fechaFin=date(2026, 6, 30), estado="ACTIVO")
    o3 = OfertaCurso(idOfertaCurso=3, idCurso=3, idPeriodo=1, grupo=1, cupoMaximo=35, cupoDisponible=32, modalidad="PRESENCIAL", aula="Lab 202", sede="Sabanas", fechaInicio=date(2026, 2, 1), fechaFin=date(2026, 6, 30), estado="ACTIVO")
    ofertas = [o1, o2, o3]

    # 6. Personas
    p_e1 = Persona(idPersona=1, tipoDocumento="CC", numeroDocumento="1065123456", primerNombre="Carlos", segundoNombre="Alberto", primerApellido="Mendoza", segundoApellido="Ríos", fechaNacimiento=date(2003, 5, 12), direccion="Calle 12 #4-20", telefono="3001234567", correoPersonal="carlos@gmail.com", correoInstitucional="cmendoza@unicesar.edu.co", ciudadResidencia="Valledupar", fechaRegistro=date(2023, 1, 15), estado="ACTIVO")
    p_e2 = Persona(idPersona=2, tipoDocumento="CC", numeroDocumento="1065987654", primerNombre="Ana", segundoNombre="María", primerApellido="Gómez", segundoApellido="López", fechaNacimiento=date(2004, 8, 22), direccion="Cra 9 #15-30", telefono="3159876543", correoPersonal="ana@gmail.com", correoInstitucional="agomez@unicesar.edu.co", ciudadResidencia="Valledupar", fechaRegistro=date(2023, 1, 15), estado="ACTIVO")
    p_e3 = Persona(idPersona=3, tipoDocumento="CC", numeroDocumento="1065444555", primerNombre="Juan", segundoNombre="David", primerApellido="Pérez", segundoApellido="Castro", fechaNacimiento=date(2002, 11, 30), direccion="Calle 20 #12-05", telefono="3205556677", correoPersonal="juan@gmail.com", correoInstitucional="jperezc@unicesar.edu.co", ciudadResidencia="Valledupar", fechaRegistro=date(2022, 8, 10), estado="ACTIVO")

    p_p1 = Persona(idPersona=4, tipoDocumento="CC", numeroDocumento="79985291", primerNombre="Adith", segundoNombre="Bismarck", primerApellido="Pérez", segundoApellido="Orozco", fechaNacimiento=date(1980, 4, 10), direccion="Campus Sabanas, Dpto. Sistemas", telefono="3104567890", correoPersonal="adith@gmail.com", correoInstitucional="adithperez@unicesar.edu.co", ciudadResidencia="Valledupar", fechaRegistro=date(2010, 2, 1), estado="ACTIVO")
    p_p2 = Persona(idPersona=5, tipoDocumento="CC", numeroDocumento="77987654", primerNombre="Roberto", segundoNombre="Carlos", primerApellido="Martínez", segundoApellido="Díaz", fechaNacimiento=date(1985, 11, 5), direccion="Calle 16 #9-40", telefono="3017654321", correoPersonal="roberto@gmail.com", correoInstitucional="rmartinez@unicesar.edu.co", ciudadResidencia="Valledupar", fechaRegistro=date(2015, 8, 10), estado="ACTIVO")
    p_p3 = Persona(idPersona=6, tipoDocumento="CC", numeroDocumento="77555111", primerNombre="Laura", segundoNombre="Elena", primerApellido="Sánchez", segundoApellido="Vargas", fechaNacimiento=date(1988, 7, 14), direccion="Cra 12 #8-19", telefono="3182223344", correoPersonal="laura@gmail.com", correoInstitucional="lsanchez@unicesar.edu.co", ciudadResidencia="Valledupar", fechaRegistro=date(2018, 1, 20), estado="ACTIVO")

    p_a1 = Persona(idPersona=7, tipoDocumento="CC", numeroDocumento="49777888", primerNombre="María", segundoNombre="Fernanda", primerApellido="Torres", segundoApellido="Suárez", fechaNacimiento=date(1982, 2, 28), direccion="Calle 8 #14-22", telefono="3004445566", correoPersonal="mfer@gmail.com", correoInstitucional="mtorres@unicesar.edu.co", ciudadResidencia="Valledupar", fechaRegistro=date(2012, 5, 1), estado="ACTIVO")
    personas = [p_e1, p_e2, p_e3, p_p1, p_p2, p_p3, p_a1]

    estudiantes = [
        Estudiante(idEstudiante=1, idPersona=1, codigoEstudiante="EST-2026-01", idPrograma=1, idPlanEstudio=1, fechaIngreso=date(2023, 1, 15), semestreActual=4, creditosAprobados=45, promedioAcumulado=Decimal("2.7"), estadoAcademico=EstadoAcademico.EBRA, estado="ACTIVO"),
        Estudiante(idEstudiante=2, idPersona=2, codigoEstudiante="EST-2026-02", idPrograma=1, idPlanEstudio=1, fechaIngreso=date(2023, 1, 15), semestreActual=4, creditosAprobados=52, promedioAcumulado=Decimal("4.2"), estadoAcademico=EstadoAcademico.ACTIVO, estado="ACTIVO"),
        Estudiante(idEstudiante=3, idPersona=3, codigoEstudiante="EST-2026-03", idPrograma=1, idPlanEstudio=1, fechaIngreso=date(2022, 8, 10), semestreActual=6, creditosAprobados=80, promedioAcumulado=Decimal("3.8"), estadoAcademico=EstadoAcademico.ACTIVO, estado="ACTIVO"),
    ]

    profesores = [
        Profesor(idProfesor=1, idPersona=4, codigoProfesor="DOC-5277", idProgramaPrincipal=1, fechaVinculacion=date(2010, 2, 1), tipoProfesor=TipoProfesor.OCASIONAL, categoriaDocente="ASOCIADO", dedicacion=Dedicacion.TIEMPO_COMPLETO, maximoNivelEstudio="DOCTORADO", nivelPosgradoReconocido="DOCTORADO", tituloProfesional="Ingeniero de Sistemas", areaConocimiento="Estructura de Datos e Ingeniería de Software", numeroHorasSemanales=Decimal("40"), puntosSalariales=Decimal("0"), estado="ACTIVO", regimenSalarial="Acuerdo 027"),
        Profesor(idProfesor=2, idPersona=5, codigoProfesor="PROF-002", idProgramaPrincipal=1, fechaVinculacion=date(2020, 1, 15), tipoProfesor=TipoProfesor.CATEDRATICO, categoriaDocente="ASISTENTE", dedicacion=Dedicacion.HORA_CATEDRA, maximoNivelEstudio="MAESTRIA", tituloProfesional="Ingeniero de Sistemas", areaConocimiento="Bases de Datos", numeroHorasSemanales=Decimal("12"), puntosSalariales=Decimal("0"), estado="ACTIVO", regimenSalarial="Acuerdo 027"),
        Profesor(idProfesor=3, idPersona=6, codigoProfesor="PROF-003", idProgramaPrincipal=2, fechaVinculacion=date(2018, 1, 20), tipoProfesor=TipoProfesor.PLANTA, categoriaDocente="TITULAR", dedicacion=Dedicacion.TIEMPO_COMPLETO, maximoNivelEstudio="DOCTORADO", tituloProfesional="Enfermera Especialista", areaConocimiento="Salud Pública", numeroHorasSemanales=Decimal("40"), puntosSalariales=Decimal("450"), estado="ACTIVO", regimenSalarial="Decreto 1279"),
    ]

    administrativos = [
        Administrativo(idAdministrativo=1, idPersona=7, codigoEmpleado="ADM-001", cargo="Director Admisiones", dependencia="Vicerrectoría Académica", categoria="PROFESIONAL", tipoContratacion="LIBRE_NOMBRAMIENTO", fechaVinculacion=date(2012, 5, 1), salarioBase=Decimal("3800000"), estado="ACTIVO"),
    ]

    asignaciones = [
        AsignacionDocente(idAsignacion=1, idProfesor=1, idOfertaCurso=1, rolDocente="TITULAR", numeroHoras=4, porcentajeResponsabilidad=Decimal("100"), fechaAsignacion=date(2026, 2, 1), estado="ACTIVO"),
        AsignacionDocente(idAsignacion=2, idProfesor=2, idOfertaCurso=2, rolDocente="TITULAR", numeroHoras=3, porcentajeResponsabilidad=Decimal("100"), fechaAsignacion=date(2026, 2, 1), estado="ACTIVO"),
    ]

    horarios = [
        Horario(idHorario=1, idOfertaCurso=1, diaSemana="LUNES", horaInicio="08:00", horaFin="10:00", aula="Lab 201", sede="Sabanas", tipoSesion="TEORICA", estado="ACTIVO"),
        Horario(idHorario=2, idOfertaCurso=1, diaSemana="MIERCOLES", horaInicio="08:00", horaFin="10:00", aula="Lab 201", sede="Sabanas", tipoSesion="PRACTICA", estado="ACTIVO"),
    ]

    matriculas = [
        MatriculaAcademica(idMatricula=1, idEstudiante=1, idPeriodo=1, fechaMatricula=date(2026, 1, 20), totalCreditos=7, promedioPeriodo=Decimal("2.7"), estadoMatricula="ACTIVO", observaciones="Alerta EBRA"),
        MatriculaAcademica(idMatricula=2, idEstudiante=2, idPeriodo=1, fechaMatricula=date(2026, 1, 21), totalCreditos=7, promedioPeriodo=Decimal("4.2"), estadoMatricula="ACTIVO", observaciones="Ordinaria"),
    ]

    detalles_matricula = [
        DetalleMatricula(idDetalleMatricula=1, idMatricula=1, idOfertaCurso=1, fechaInscripcion=date(2026, 1, 20), estadoCurso=EstadoCurso.EN_CURSO, notaFinal=Decimal("2.5"), numeroFallas=2, fechaCancelacion=None, motivoCancelacion=None),
        DetalleMatricula(idDetalleMatricula=2, idMatricula=1, idOfertaCurso=2, fechaInscripcion=date(2026, 1, 20), estadoCurso=EstadoCurso.EN_CURSO, notaFinal=Decimal("2.9"), numeroFallas=1, fechaCancelacion=None, motivoCancelacion=None),
        DetalleMatricula(idDetalleMatricula=3, idMatricula=2, idOfertaCurso=1, fechaInscripcion=date(2026, 1, 21), estadoCurso=EstadoCurso.APROBADO, notaFinal=Decimal("4.5"), numeroFallas=0, fechaCancelacion=None, motivoCancelacion=None),
        DetalleMatricula(idDetalleMatricula=4, idMatricula=2, idOfertaCurso=2, fechaInscripcion=date(2026, 1, 21), estadoCurso=EstadoCurso.APROBADO, notaFinal=Decimal("4.0"), numeroFallas=0, fechaCancelacion=None, motivoCancelacion=None),
    ]

    evaluaciones = [
        Evaluacion(idEvaluacion=1, idOfertaCurso=1, nombre="Primer Parcial", tipo="PARCIAL", porcentaje=Decimal("30"), fechaProgramada=date(2026, 3, 15), descripcion="Estructuras lineales", estado="ACTIVO"),
        Evaluacion(idEvaluacion=2, idOfertaCurso=1, nombre="Segundo Parcial", tipo="PARCIAL", porcentaje=Decimal("30"), fechaProgramada=date(2026, 4, 30), descripcion="Árboles y grafos", estado="ACTIVO"),
        Evaluacion(idEvaluacion=3, idOfertaCurso=1, nombre="Examen Final", tipo="FINAL", porcentaje=Decimal("40"), fechaProgramada=date(2026, 6, 15), descripcion="Examen práctico acumulativo", estado="ACTIVO"),
    ]

    calificaciones = [
        Calificacion(idCalificacion=1, idEvaluacion=1, idDetalleMatricula=1, nota=Decimal("2.5"), fechaRegistro=date(2026, 3, 16), observacion="Parcial 1", estado="ACTIVO"),
        Calificacion(idCalificacion=2, idEvaluacion=1, idDetalleMatricula=3, nota=Decimal("4.5"), fechaRegistro=date(2026, 3, 16), observacion="Parcial 1", estado="ACTIVO"),
    ]

    alertas = [
        AlertaAcademica(idAlerta=1, idEstudiante=1, idPeriodo=1, tipoAlerta="EBRA", motivo="Promedio acumulado menor a 3.0", valorObservado=Decimal("2.7"), valorLimite=Decimal("3.0"), fechaGeneracion=date(2026, 2, 1), atendida=False, observaciones="Notificado a Bienestar", estado="ACTIVO"),
    ]

    contratos = [
        Contrato(idContrato=1, idPersona=4, numeroContrato="CONT-2026-001", tipoContrato="DOCENTE_OCASIONAL", modalidadProfesor="OCASIONAL", fechaInicio=date(2026, 1, 15), fechaFin=date(2026, 12, 15), dedicacion=Dedicacion.TIEMPO_COMPLETO, horasSemanales=Decimal("40"), salarioBase=Decimal("6313763.00"), observaciones="Banco de Bogotá Cta Ahorros #863032983", estado="ACTIVO"),
        Contrato(idContrato=2, idPersona=5, numeroContrato="CONT-2026-002", tipoContrato="DOCENTE_CATEDRATICO", modalidadProfesor="CATEDRATICO", fechaInicio=date(2026, 2, 1), fechaFin=date(2026, 11, 30), dedicacion=Dedicacion.HORA_CATEDRA, horasSemanales=Decimal("12"), salarioBase=Decimal("1848000"), observaciones="Bancolombia Cta Ahorros #123456789", estado="ACTIVO"),
        Contrato(idContrato=3, idPersona=6, numeroContrato="CONT-2026-003", tipoContrato="DOCENTE_PLANTA", modalidadProfesor="PLANTA", regimenAplicable="DECRETO_1279", fechaInicio=date(2026, 1, 1), fechaFin=date(2026, 12, 31), dedicacion=Dedicacion.TIEMPO_COMPLETO, horasSemanales=Decimal("40"), salarioBase=Decimal("10765800"), observaciones="Davivienda Cta Ahorros #987654321", estado="ACTIVO"),
    ]

    categorias = [
        CategoriaDocente(idCategoria=1, codigo="TITULAR", nombre="Docente Titular", puntosCategoria=Decimal("450"), fechaInicioVigencia=date(2010, 1, 1), normaOrigen="Decreto 1279", estado="ACTIVO"),
        CategoriaDocente(idCategoria=2, codigo="ASOCIADO", nombre="Docente Asociado", puntosCategoria=Decimal("350"), fechaInicioVigencia=date(2012, 1, 1), normaOrigen="Decreto 1279", estado="ACTIVO"),
        CategoriaDocente(idCategoria=3, codigo="ASISTENTE", nombre="Docente Asistente", puntosCategoria=Decimal("250"), fechaInicioVigencia=date(2015, 1, 1), normaOrigen="Decreto 1279", estado="ACTIVO"),
        CategoriaDocente(idCategoria=4, codigo="AUXILIAR", nombre="Docente Auxiliar", puntosCategoria=Decimal("180"), fechaInicioVigencia=date(2018, 1, 1), normaOrigen="Decreto 1279", estado="ACTIVO"),
    ]

    factores = [
        FactorSalarial(idFactor=1, idProfesor=3, tipoFactor=TipoFactor.TITULO_ACADEMICO, nombre="Doctorado en Ciencias Computacionales", puntosReconocidos=Decimal("120"), fechaReconocimiento=date(2015, 6, 1), actoAdministrativo="Res. 102", estado="ACTIVO"),
        FactorSalarial(idFactor=2, idProfesor=3, tipoFactor=TipoFactor.PRODUCTIVIDAD_ACADEMICA, nombre="Artículo A1 en Revista Indexada Q1", puntosReconocidos=Decimal("15"), fechaReconocimiento=date(2023, 4, 10), actoAdministrativo="Res. 205", estado="ACTIVO"),
    ]

    producciones = [
        ProduccionAcademica(idProduccion=1, idProfesor=1, tipoProduccion="ARTICULO", titulo="Algoritmos Genéticos y Grafos Paralelos", fechaPublicacion=date(2024, 5, 12), entidadPublicadora="IEEE Transactions", clasificacionRevista="A1", puntosReconocidos=Decimal("15"), numeroAutores=2, factorCoautoria=Decimal("1.0"), estadoValidacion="APROBADO"),
        ProduccionAcademica(idProduccion=2, idProfesor=3, tipoProduccion="ARTICULO", titulo="Modelos de Optimización en Epidemiología", fechaPublicacion=date(2023, 4, 10), entidadPublicadora="Springer Nature", clasificacionRevista="A1", puntosReconocidos=Decimal("15"), numeroAutores=1, factorCoautoria=Decimal("1.0"), estadoValidacion="APROBADO"),
    ]

    periodos_nomina = [
        PeriodoNomina(idPeriodoNomina=1, anio=2026, mes=8, fechaInicio=date(2026, 8, 1), fechaFin=date(2026, 8, 31), fechaPago=date(2026, 8, 31), diasBaseLiquidacion=30, estado="ABIERTO"),
    ]

    parametros = [
        ParametroNormativo(idParametro=1, codigo=PNC.SALARIO_MINIMO, nombre="Salario Mínimo Legal Vigente", descripcion="SMMLV Colombia", tipoDato="MONETARIO", valor="1750905", unidad="COP", normaOrigen="Decreto Nacional Salarial", articulo="Art. 1", fechaInicioVigencia=date(2026, 1, 1), fechaFinVigencia=date(2026, 12, 31), aplicaA="TODOS", estado="ACTIVO"),
        ParametroNormativo(idParametro=2, codigo=PNC.VALOR_PUNTO_SALARIAL, nombre="Valor Punto Salarial", descripcion="Punto Salarial Dec. 1279", tipoDato="MONETARIO", valor="23924", unidad="COP", normaOrigen="Decreto 1279 de 2002", articulo="Art. 27", fechaInicioVigencia=date(2026, 1, 1), fechaFinVigencia=date(2026, 12, 31), aplicaA="PLANTA", estado="ACTIVO"),
        ParametroNormativo(idParametro=3, codigo=PNC.VALOR_AUXILIO_TRANSPORTE_VIGENTE, nombre="Auxilio Transporte", descripcion="Auxilio legal transporte", tipoDato="MONETARIO", valor="249095", unidad="COP", normaOrigen="Decreto Nacional Auxilio Transporte", articulo="Art. 1", fechaInicioVigencia=date(2026, 1, 1), fechaFinVigencia=date(2026, 12, 31), aplicaA="TODOS", estado="ACTIVO"),
        ParametroNormativo(idParametro=4, codigo=PNC.VALOR_HORA_CATEDRA, nombre="Valor Hora Cátedra", descripcion="Valor hora catedrático", tipoDato="MONETARIO", valor="38500", unidad="COP", normaOrigen="Acuerdo 027 de 2024", articulo="Art. 15", fechaInicioVigencia=date(2026, 1, 1), fechaFinVigencia=date(2026, 12, 31), aplicaA="CATEDRATICO", estado="ACTIVO"),
        ParametroNormativo(idParametro=5, codigo=PNC.PORCENTAJE_SALUD_TRABAJADOR, nombre="Salud Trabajador %", descripcion="Descuento Salud 4%", tipoDato="PORCENTUAL", valor="0.04", unidad="%", normaOrigen="Ley 100 de 1993", articulo="Art. 204", fechaInicioVigencia=date(2026, 1, 1), fechaFinVigencia=date(2026, 12, 31), aplicaA="TODOS", estado="ACTIVO"),
        ParametroNormativo(idParametro=6, codigo=PNC.PORCENTAJE_SALUD_EMPLEADOR, nombre="Salud Empleador %", descripcion="Aporte Salud Empleador 8.5%", tipoDato="PORCENTUAL", valor="0.085", unidad="%", normaOrigen="Ley 100 de 1993", articulo="Art. 204", fechaInicioVigencia=date(2026, 1, 1), fechaFinVigencia=date(2026, 12, 31), aplicaA="TODOS", estado="ACTIVO"),
        ParametroNormativo(idParametro=7, codigo=PNC.PORCENTAJE_PENSION_TRABAJADOR, nombre="Pensión Trabajador %", descripcion="Descuento Pensión 4%", tipoDato="PORCENTUAL", valor="0.04", unidad="%", normaOrigen="Ley 100 de 1993", articulo="Art. 20", fechaInicioVigencia=date(2026, 1, 1), fechaFinVigencia=date(2026, 12, 31), aplicaA="TODOS", estado="ACTIVO"),
        ParametroNormativo(idParametro=8, codigo=PNC.PORCENTAJE_PENSION_EMPLEADOR, nombre="Pensión Empleador %", descripcion="Aporte Pensión Empleador 12%", tipoDato="PORCENTUAL", valor="0.12", unidad="%", normaOrigen="Ley 100 de 1993", articulo="Art. 20", fechaInicioVigencia=date(2026, 1, 1), fechaFinVigencia=date(2026, 12, 31), aplicaA="TODOS", estado="ACTIVO"),
        ParametroNormativo(idParametro=9, codigo=PNC.PORCENTAJE_FONDO_SOLIDARIDAD, nombre="Fondo Solidaridad %", descripcion="FSP para IBC >= 4 SMMLV", tipoDato="PORCENTUAL", valor="0.01", unidad="%", normaOrigen="Ley 797 de 2003", articulo="Art. 8", fechaInicioVigencia=date(2026, 1, 1), fechaFinVigencia=date(2026, 12, 31), aplicaA="TODOS", estado="ACTIVO"),
        ParametroNormativo(idParametro=10, codigo=PNC.PORCENTAJE_ARL_CLASE_I, nombre="ARL Clase I %", descripcion="Riesgos Laborales Clase I", tipoDato="PORCENTUAL", valor="0.00522", unidad="%", normaOrigen="Decreto 1772 de 1994", articulo="Art. 13", fechaInicioVigencia=date(2026, 1, 1), fechaFinVigencia=date(2026, 12, 31), aplicaA="TODOS", estado="ACTIVO"),
        ParametroNormativo(idParametro=11, codigo=PNC.PORCENTAJE_ARL_CLASE_II, nombre="ARL Clase II %", descripcion="Riesgos Laborales Clase II", tipoDato="PORCENTUAL", valor="0.01044", unidad="%", normaOrigen="Decreto 1772 de 1994", articulo="Art. 13", fechaInicioVigencia=date(2026, 1, 1), fechaFinVigencia=date(2026, 12, 31), aplicaA="TODOS", estado="ACTIVO"),
        ParametroNormativo(idParametro=12, codigo=PNC.PORCENTAJE_SENA, nombre="SENA %", descripcion="Aporte Parafiscal SENA 2%", tipoDato="PORCENTUAL", valor="0.02", unidad="%", normaOrigen="Ley 21 de 1982", articulo="Art. 7", fechaInicioVigencia=date(2026, 1, 1), fechaFinVigencia=date(2026, 12, 31), aplicaA="TODOS", estado="ACTIVO"),
        ParametroNormativo(idParametro=13, codigo=PNC.PORCENTAJE_ICBF, nombre="ICBF %", descripcion="Aporte Parafiscal ICBF 3%", tipoDato="PORCENTUAL", valor="0.03", unidad="%", normaOrigen="Ley 89 de 1988", articulo="Art. 1", fechaInicioVigencia=date(2026, 1, 1), fechaFinVigencia=date(2026, 12, 31), aplicaA="TODOS", estado="ACTIVO"),
        ParametroNormativo(idParametro=14, codigo=PNC.PORCENTAJE_CAJA_COMPENSACION, nombre="Caja Compensación %", descripcion="Aporte Cuidado Familiar 4%", tipoDato="PORCENTUAL", valor="0.04", unidad="%", normaOrigen="Ley 21 de 1982", articulo="Art. 7", fechaInicioVigencia=date(2026, 1, 1), fechaFinVigencia=date(2026, 12, 31), aplicaA="TODOS", estado="ACTIVO"),
        ParametroNormativo(idParametro=15, codigo=PNC.TOPE_BONIFICACION_SERVICIOS, nombre="Tope Bonificación Servicios", descripcion="Tope Decreto 1279", tipoDato="MONETARIO", valor="756411", unidad="COP", normaOrigen="Decreto 1279 de 2002", articulo="Art. 41", fechaInicioVigencia=date(2026, 1, 1), fechaFinVigencia=date(2026, 12, 31), aplicaA="PLANTA", estado="ACTIVO"),
        ParametroNormativo(idParametro=16, codigo=PNC.PORCENTAJE_BONIFICACION_SERVICIOS_HASTA_TOPE, nombre="Bonificación Hasta Tope %", descripcion="Porcentaje BSP <= Tope (50%)", tipoDato="PORCENTUAL", valor="0.50", unidad="%", normaOrigen="Decreto 1279 de 2002", articulo="Art. 41", fechaInicioVigencia=date(2026, 1, 1), fechaFinVigencia=date(2026, 12, 31), aplicaA="PLANTA", estado="ACTIVO"),
        ParametroNormativo(idParametro=17, codigo=PNC.PORCENTAJE_BONIFICACION_SERVICIOS_SOBRE_TOPE, nombre="Bonificación Sobre Tope %", descripcion="Porcentaje BSP > Tope (35%)", tipoDato="PORCENTUAL", valor="0.35", unidad="%", normaOrigen="Decreto 1279 de 2002", articulo="Art. 41", fechaInicioVigencia=date(2026, 1, 1), fechaFinVigencia=date(2026, 12, 31), aplicaA="PLANTA", estado="ACTIVO"),
        ParametroNormativo(idParametro=18, codigo=PNC.NOTA_MINIMA_APROBATORIA, nombre="Nota Mínima Aprobatoria", descripcion="Nota mínima aprobar", tipoDato="DECIMAL", valor="3.0", unidad="puntos", normaOrigen="Reglamento Estudiantil", articulo="Art. 45", fechaInicioVigencia=date(2026, 1, 1), fechaFinVigencia=date(2026, 12, 31), aplicaA="ESTUDIANTES", estado="ACTIVO"),
        ParametroNormativo(idParametro=19, codigo=PNC.PROMEDIO_MINIMO_EBRA, nombre="Promedio Mínimo EBRA", descripcion="Umbral de riesgo EBRA", tipoDato="DECIMAL", valor="3.0", unidad="puntos", normaOrigen="Reglamento Estudiantil", articulo="Art. 52", fechaInicioVigencia=date(2026, 1, 1), fechaFinVigencia=date(2026, 12, 31), aplicaA="ESTUDIANTES", estado="ACTIVO"),
        ParametroNormativo(idParametro=20, codigo=PNC.MAXIMO_CREDITOS_PERIODO, nombre="Máximo Créditos Período", descripcion="Límite máximo de créditos semestrales", tipoDato="DECIMAL", valor="22", unidad="créditos", normaOrigen="Reglamento Estudiantil", articulo="Art. 30", fechaInicioVigencia=date(2026, 1, 1), fechaFinVigencia=date(2026, 12, 31), aplicaA="ESTUDIANTES", estado="ACTIVO"),
    ]

    conceptos = [
        ConceptoNomina(idConcepto=1, codigo="DEV-01", nombre="Sueldo Básico", tipoConcepto="DEVENGADO", naturaleza="DEVENGADO", esSalarial=True, estado="ACTIVO"),
        ConceptoNomina(idConcepto=2, codigo="DEV-02", nombre="Bonificación Posgrado", tipoConcepto="DEVENGADO", naturaleza="DEVENGADO", esSalarial=False, estado="ACTIVO"),
        ConceptoNomina(idConcepto=3, codigo="DED-01", nombre="Descuento Salud (4%)", tipoConcepto="DEDUCCION", naturaleza="DEDUCCION", esSalarial=False, estado="ACTIVO"),
        ConceptoNomina(idConcepto=4, codigo="DED-02", nombre="Descuento Pensión (4%)", tipoConcepto="DEDUCCION", naturaleza="DEDUCCION", esSalarial=False, estado="ACTIVO"),
        ConceptoNomina(idConcepto=5, codigo="DED-03", nombre="Fondo Solidaridad Pensional (1%)", tipoConcepto="DEDUCCION", naturaleza="DEDUCCION", esSalarial=False, estado="ACTIVO"),
        ConceptoNomina(idConcepto=6, codigo="PAT-01", nombre="Aporte Patronal Salud (8.5%)", tipoConcepto="APORTE_PATRONAL", naturaleza="APORTE", esSalarial=False, estado="ACTIVO"),
        ConceptoNomina(idConcepto=7, codigo="PAT-02", nombre="Aporte Patronal Pensión (12%)", tipoConcepto="APORTE_PATRONAL", naturaleza="APORTE", esSalarial=False, estado="ACTIVO"),
        ConceptoNomina(idConcepto=8, codigo="PAT-03", nombre="Aporte ARL Riesgos Laborales", tipoConcepto="APORTE_PATRONAL", naturaleza="APORTE", esSalarial=False, estado="ACTIVO"),
        ConceptoNomina(idConcepto=9, codigo="PAT-04", nombre="Caja de Compensación Familiar (4%)", tipoConcepto="PARAFISCAL", naturaleza="APORTE", esSalarial=False, estado="ACTIVO"),
        ConceptoNomina(idConcepto=10, codigo="PAT-05", nombre="Aporte Parafiscal SENA (2%)", tipoConcepto="PARAFISCAL", naturaleza="APORTE", esSalarial=False, estado="ACTIVO"),
        ConceptoNomina(idConcepto=11, codigo="PAT-06", nombre="Aporte Parafiscal ICBF (3%)", tipoConcepto="PARAFISCAL", naturaleza="APORTE", esSalarial=False, estado="ACTIVO"),
        ConceptoNomina(idConcepto=12, codigo="PRE-01", nombre="Cesantías", tipoConcepto="PRESTACION", naturaleza="PRESTACION", esSalarial=False, estado="ACTIVO"),
        ConceptoNomina(idConcepto=13, codigo="PRE-02", nombre="Intereses sobre Cesantías", tipoConcepto="PRESTACION", naturaleza="PRESTACION", esSalarial=False, estado="ACTIVO"),
        ConceptoNomina(idConcepto=14, codigo="PRE-03", nombre="Prima de Servicios", tipoConcepto="PRESTACION", naturaleza="PRESTACION", esSalarial=False, estado="ACTIVO"),
        ConceptoNomina(idConcepto=15, codigo="PRE-04", nombre="Vacaciones", tipoConcepto="PRESTACION", naturaleza="PRESTACION", esSalarial=False, estado="ACTIVO"),
    ]

    # Generación reglamentaria de liquidaciones y detalles mediante GestorNomina
    gestor_nom = GestorNomina(
        contratos=contratos,
        profesores=profesores,
        periodos_nomina=periodos_nomina,
        parametros=parametros,
        categorias=categorias,
        factores=factores,
        producciones=producciones,
    )
    gestor_nom.liquidarProfesorOcasional(id_contrato=1, id_periodo_nomina=1, fecha_liquidacion=date(2026, 8, 31))
    gestor_nom.liquidarProfesorCatedratico(id_contrato=2, id_periodo_nomina=1, fecha_liquidacion=date(2026, 8, 31))
    gestor_nom.liquidarProfesorPlanta(id_contrato=3, id_periodo_nomina=1, fecha_liquidacion=date(2026, 8, 31))

    liquidaciones = gestor_nom.liquidaciones
    detalles_liq = gestor_nom.detalles_liquidacion

    diccionario_datos = {
        Universidad: [uni],
        Facultad: facultades,
        ProgramaAcademico: programas,
        PlanEstudio: planes,
        DetallePlanEstudio: detalles_plan,
        Curso: cursos,
        Prerrequisito: prerrequisitos,
        PeriodoAcademico: periodos,
        OfertaCurso: ofertas,
        Persona: personas,
        Estudiante: estudiantes,
        Profesor: profesores,
        Administrativo: administrativos,
        AsignacionDocente: asignaciones,
        Horario: horarios,
        MatriculaAcademica: matriculas,
        DetalleMatricula: detalles_matricula,
        Evaluacion: evaluaciones,
        Calificacion: calificaciones,
        AlertaAcademica: alertas,
        Contrato: contratos,
        CategoriaDocente: categorias,
        FactorSalarial: factores,
        ProduccionAcademica: producciones,
        PeriodoNomina: periodos_nomina,
        LiquidacionNomina: liquidaciones,
        ConceptoNomina: conceptos,
        DetalleLiquidacion: detalles_liq,
        ParametroNormativo: parametros,
    }

    for dir_nombre in ["datos", "cpp/datos"]:
        gp = GestorPersistencia(dir_nombre)
        gp.guardar_todos_los_datos(diccionario_datos)
        print(f"¡Persistencia limpia generada con éxito en '{dir_nombre}/'!")


if __name__ == "__main__":
    generar()
