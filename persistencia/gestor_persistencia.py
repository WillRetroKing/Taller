from __future__ import annotations

from dataclasses import fields
from datetime import date, time
from decimal import Decimal
from enum import Enum
from pathlib import Path
from types import UnionType
from typing import Any, Iterable, Mapping, Union, get_args, get_origin, get_type_hints

from dominio.modelo_datos import (
    AlertaAcademica,
    Administrativo,
    ArchivoPersistencia,
    AsignacionDocente,
    Calificacion,
    CategoriaDocente,
    ConceptoNomina,
    Contrato,
    Curso,
    DetalleLiquidacion,
    DetalleMatricula,
    DetallePlanEstudio,
    Estudiante,
    Evaluacion,
    Facultad,
    FactorSalarial,
    Horario,
    LiquidacionNomina,
    MatriculaAcademica,
    ParametroNormativo,
    Persona,
    PeriodoAcademico,
    PeriodoNomina,
    PlanEstudio,
    Prerrequisito,
    ProduccionAcademica,
    Profesor,
    ProgramaAcademico,
    Universidad,
    OfertaCurso,
)


class GestorPersistencia:
    DELIMITADOR = "|"
    ARCHIVOS: dict[type, str] = {
        Universidad: "universidad.txt",
        Facultad: "facultades.txt",
        ProgramaAcademico: "programas.txt",
        PlanEstudio: "planes_estudio.txt",
        DetallePlanEstudio: "detalles_plan_estudio.txt",
        Curso: "cursos.txt",
        Prerrequisito: "prerrequisitos.txt",
        Persona: "personas.txt",
        Estudiante: "estudiantes.txt",
        Profesor: "profesores.txt",
        Administrativo: "administrativos.txt",
        PeriodoAcademico: "periodos_academicos.txt",
        OfertaCurso: "ofertas_curso.txt",
        AsignacionDocente: "asignaciones_docentes.txt",
        Horario: "horarios.txt",
        MatriculaAcademica: "matriculas.txt",
        DetalleMatricula: "detalles_matricula.txt",
        Evaluacion: "evaluaciones.txt",
        Calificacion: "calificaciones.txt",
        AlertaAcademica: "alertas_academicas.txt",
        Contrato: "contratos.txt",
        CategoriaDocente: "categorias_docentes.txt",
        FactorSalarial: "factores_salariales.txt",
        ProduccionAcademica: "producciones_academicas.txt",
        PeriodoNomina: "periodos_nomina.txt",
        LiquidacionNomina: "liquidaciones_nomina.txt",
        ConceptoNomina: "conceptos_nomina.txt",
        DetalleLiquidacion: "detalles_liquidacion.txt",
        ParametroNormativo: "parametros_normativos.txt",
        ArchivoPersistencia: "archivos_persistencia.txt",
    }

    def __init__(self, directorio: str | Path = "datos") -> None:
        self.directorio = Path(directorio)
        self.directorio.mkdir(parents=True, exist_ok=True)

    def guardar_entidad(self, entidades: Iterable[Any], tipo: type) -> Path:
        """Guarda una colección sin encabezado y con el orden de campos de la dataclass."""
        if tipo not in self.ARCHIVOS:
            raise ValueError(f"Entidad no registrada: {tipo.__name__}")

        ruta = self.directorio / self.ARCHIVOS[tipo]
        campos = fields(tipo)
        with ruta.open("w", encoding="utf-8", newline="\n") as archivo:
            for entidad in entidades:
                valores = [self._serializar(getattr(entidad, campo.name)) for campo in campos]
                archivo.write(self.DELIMITADOR.join(valores) + "\n")
        return ruta

    def cargar_entidad(self, tipo: type) -> list[Any]:
        if tipo not in self.ARCHIVOS:
            raise ValueError(f"Entidad no registrada: {tipo.__name__}")

        ruta = self.directorio / self.ARCHIVOS[tipo]
        if not ruta.exists():
            return []

        tipos = get_type_hints(tipo)
        campos = fields(tipo)
        entidades: list[Any] = []
        with ruta.open("r", encoding="utf-8", newline="") as archivo:
            for numero_linea, linea in enumerate(archivo, start=1):
                linea = linea.rstrip("\r\n")
                if not linea:
                    continue
                valores = linea.split(self.DELIMITADOR)
                if len(valores) != len(campos):
                    raise ValueError(
                        f"{ruta}:{numero_linea}: se esperaban {len(campos)} campos; "
                        f"se recibieron {len(valores)}"
                    )
                datos = {
                    campo.name: self._deserializar(valores[indice], tipos[campo.name])
                    for indice, campo in enumerate(campos)
                }
                entidades.append(tipo(**datos))
        return entidades

    def guardar_todos_los_datos(self, datos: Mapping[type | str, Iterable[Any]]) -> None:
        for tipo in self.ARCHIVOS:
            if tipo in datos:
                self.guardar_entidad(datos[tipo], tipo)
            elif tipo.__name__ in datos:
                self.guardar_entidad(datos[tipo.__name__], tipo)

    def cargar_todos_los_datos(self) -> dict[type, list[Any]]:
        datos = {tipo: self.cargar_entidad(tipo) for tipo in self.ARCHIVOS}
        self.validar_integridad_datos(datos)
        return datos

    @staticmethod
    def validar_integridad_datos(datos: Mapping[type, list[Any]]) -> None:
        """Valida IDs y referencias antes de entregar datos cargados a la aplicación."""
        indices: dict[type, set[Any]] = {}
        for tipo, campo_id in (
            (Universidad, "idUniversidad"), (Facultad, "idFacultad"),
            (ProgramaAcademico, "idPrograma"), (PlanEstudio, "idPlanEstudio"),
            (DetallePlanEstudio, "idDetallePlan"), (Curso, "idCurso"),
            (Prerrequisito, "idPrerrequisito"), (Persona, "idPersona"),
            (Estudiante, "idEstudiante"), (Profesor, "idProfesor"),
            (Administrativo, "idAdministrativo"), (PeriodoAcademico, "idPeriodo"),
            (OfertaCurso, "idOfertaCurso"), (AsignacionDocente, "idAsignacion"),
            (Horario, "idHorario"), (MatriculaAcademica, "idMatricula"),
            (DetalleMatricula, "idDetalleMatricula"), (Evaluacion, "idEvaluacion"),
            (Calificacion, "idCalificacion"), (AlertaAcademica, "idAlerta"),
            (Contrato, "idContrato"), (CategoriaDocente, "idCategoria"),
            (FactorSalarial, "idFactor"), (ProduccionAcademica, "idProduccion"),
            (PeriodoNomina, "idPeriodoNomina"), (LiquidacionNomina, "idLiquidacion"),
            (ConceptoNomina, "idConcepto"), (DetalleLiquidacion, "idDetalleLiquidacion"),
            (ParametroNormativo, "idParametro"), (ArchivoPersistencia, "idArchivo"),
        ):
            valores = [getattr(item, campo_id) for item in datos.get(tipo, [])]
            valores_definidos = [valor for valor in valores if valor is not None]
            if len(valores_definidos) != len(set(valores_definidos)):
                raise ValueError(f"IDs duplicados en {tipo.__name__}")
            indices[tipo] = set(valores_definidos)

        referencias = (
            (ProgramaAcademico, "idFacultad", Facultad),
            (PlanEstudio, "idPrograma", ProgramaAcademico),
            (DetallePlanEstudio, "idPlanEstudio", PlanEstudio),
            (DetallePlanEstudio, "idCurso", Curso),
            (Prerrequisito, "idCurso", Curso),
            (Prerrequisito, "idCursoRequerido", Curso),
            (Estudiante, "idPersona", Persona),
            (Estudiante, "idPrograma", ProgramaAcademico),
            (Estudiante, "idPlanEstudio", PlanEstudio),
            (Profesor, "idPersona", Persona),
            (Administrativo, "idPersona", Persona),
            (OfertaCurso, "idCurso", Curso),
            (OfertaCurso, "idPeriodo", PeriodoAcademico),
            (AsignacionDocente, "idProfesor", Profesor),
            (AsignacionDocente, "idOfertaCurso", OfertaCurso),
            (Horario, "idOfertaCurso", OfertaCurso),
            (MatriculaAcademica, "idEstudiante", Estudiante),
            (MatriculaAcademica, "idPeriodo", PeriodoAcademico),
            (DetalleMatricula, "idMatricula", MatriculaAcademica),
            (DetalleMatricula, "idOfertaCurso", OfertaCurso),
            (Evaluacion, "idOfertaCurso", OfertaCurso),
            (Calificacion, "idEvaluacion", Evaluacion),
            (Calificacion, "idDetalleMatricula", DetalleMatricula),
            (AlertaAcademica, "idEstudiante", Estudiante),
            (AlertaAcademica, "idPeriodo", PeriodoAcademico),
            (Contrato, "idPersona", Persona),
            (FactorSalarial, "idProfesor", Profesor),
            (ProduccionAcademica, "idProfesor", Profesor),
            (LiquidacionNomina, "idProfesor", Profesor),
            (LiquidacionNomina, "idContrato", Contrato),
            (LiquidacionNomina, "idPeriodoNomina", PeriodoNomina),
            (DetalleLiquidacion, "idLiquidacion", LiquidacionNomina),
            (DetalleLiquidacion, "idConcepto", ConceptoNomina),
        )
        for tipo, campo, tipo_referenciado in referencias:
            for objeto in datos.get(tipo, []):
                valor = getattr(objeto, campo, None)
                if valor is not None and valor not in indices[tipo_referenciado]:
                    # Si es un campo opcional o preliminar, sanear a None para no bloquear la carga de la universidad
                    if campo in ("idPlanEstudio", "idPeriodo", "idPeriodoAcademico", "idProgramaPrincipal"):
                        setattr(objeto, campo, None)
                        continue
                    raise ValueError(
                        f"Referencia inválida: {tipo.__name__}.{campo}={valor} "
                        f"no existe en {tipo_referenciado.__name__}"
                    )

    @staticmethod
    def reconstruir_relaciones(datos: Mapping[type, list[Any]]) -> dict[str, dict[int, Any]]:
        """Construye índices en memoria; los objetos conservan sus IDs como referencia estable."""
        por_tipo = {
            tipo: {
                getattr(objeto, campo): objeto
                for objeto in datos.get(tipo, [])
                if getattr(objeto, campo, None) is not None
            }
            for tipo, campo in (
                (Facultad, "idFacultad"), (ProgramaAcademico, "idPrograma"),
                (PlanEstudio, "idPlanEstudio"), (Curso, "idCurso"),
                (Persona, "idPersona"), (Estudiante, "idEstudiante"),
                (Profesor, "idProfesor"), (Administrativo, "idAdministrativo"),
                (PeriodoAcademico, "idPeriodo"), (OfertaCurso, "idOfertaCurso"),
                (MatriculaAcademica, "idMatricula"), (Contrato, "idContrato"),
                (PeriodoNomina, "idPeriodoNomina"), (LiquidacionNomina, "idLiquidacion"),
                (ConceptoNomina, "idConcepto"),
            )
        }

        def resolver(
            objetos: Iterable[Any], campo_id: str, campo_referencia: str, indice: type
        ) -> dict[int, Any]:
            return {
                getattr(objeto, campo_id): por_tipo[indice].get(getattr(objeto, campo_referencia))
                for objeto in objetos
                if getattr(objeto, campo_id, None) is not None
            }

        def agrupar(tipo: type, objetos: Iterable[Any], campo_grupo: str) -> dict[int, list[Any]]:
            resultado: dict[int, list[Any]] = {}
            for objeto in objetos:
                clave = getattr(objeto, campo_grupo, None)
                if clave is not None:
                    resultado.setdefault(clave, []).append(objeto)
            return resultado

        relaciones: dict[str, dict[int, Any]] = {}
        relaciones["facultad_por_programa"] = resolver(datos.get(ProgramaAcademico, []), "idPrograma", "idFacultad", Facultad)
        relaciones["programa_por_plan"] = resolver(datos.get(PlanEstudio, []), "idPlanEstudio", "idPrograma", ProgramaAcademico)
        relaciones["persona_por_estudiante"] = resolver(datos.get(Estudiante, []), "idEstudiante", "idPersona", Persona)
        relaciones["persona_por_profesor"] = resolver(datos.get(Profesor, []), "idProfesor", "idPersona", Persona)
        relaciones["persona_por_administrativo"] = resolver(datos.get(Administrativo, []), "idAdministrativo", "idPersona", Persona)
        relaciones["curso_por_oferta"] = resolver(datos.get(OfertaCurso, []), "idOfertaCurso", "idCurso", Curso)
        relaciones["periodo_por_oferta"] = resolver(datos.get(OfertaCurso, []), "idOfertaCurso", "idPeriodo", PeriodoAcademico)
        relaciones["estudiante_por_matricula"] = resolver(datos.get(MatriculaAcademica, []), "idMatricula", "idEstudiante", Estudiante)
        relaciones["periodo_por_matricula"] = resolver(datos.get(MatriculaAcademica, []), "idMatricula", "idPeriodo", PeriodoAcademico)
        relaciones["contrato_por_liquidacion"] = resolver(datos.get(LiquidacionNomina, []), "idLiquidacion", "idContrato", Contrato)
        relaciones["profesor_por_liquidacion"] = resolver(datos.get(LiquidacionNomina, []), "idLiquidacion", "idProfesor", Profesor)
        relaciones["periodo_nomina_por_liquidacion"] = resolver(datos.get(LiquidacionNomina, []), "idLiquidacion", "idPeriodoNomina", PeriodoNomina)

        relaciones["detalles_plan_por_plan"] = agrupar(DetallePlanEstudio, datos.get(DetallePlanEstudio, []), "idPlanEstudio")
        relaciones["prerrequisitos_por_curso"] = agrupar(Prerrequisito, datos.get(Prerrequisito, []), "idCurso")
        relaciones["asignaciones_por_oferta"] = agrupar(AsignacionDocente, datos.get(AsignacionDocente, []), "idOfertaCurso")
        relaciones["horarios_por_oferta"] = agrupar(Horario, datos.get(Horario, []), "idOfertaCurso")
        relaciones["detalles_por_matricula"] = agrupar(DetalleMatricula, datos.get(DetalleMatricula, []), "idMatricula")
        relaciones["evaluaciones_por_oferta"] = agrupar(Evaluacion, datos.get(Evaluacion, []), "idOfertaCurso")
        relaciones["calificaciones_por_evaluacion"] = agrupar(Calificacion, datos.get(Calificacion, []), "idEvaluacion")
        relaciones["factores_por_profesor"] = agrupar(FactorSalarial, datos.get(FactorSalarial, []), "idProfesor")
        relaciones["producciones_por_profesor"] = agrupar(ProduccionAcademica, datos.get(ProduccionAcademica, []), "idProfesor")
        relaciones["detalles_liquidacion_por_liquidacion"] = agrupar(DetalleLiquidacion, datos.get(DetalleLiquidacion, []), "idLiquidacion")
        return relaciones

    @staticmethod
    def _serializar(valor: Any) -> str:
        if valor is None:
            return ""
        if isinstance(valor, Enum):
            return str(valor.value)
        if isinstance(valor, bool):
            return "1" if valor else "0"
        if isinstance(valor, (date, time)):
            return valor.isoformat()
        return str(valor).replace("|", " - ")

    @staticmethod
    def _deserializar(valor: str, tipo: Any) -> Any:
        if valor == "":
            return None

        origen = get_origin(tipo)
        if origen in (Union, UnionType):
            tipos = [candidato for candidato in get_args(tipo) if candidato is not type(None)]
            return GestorPersistencia._deserializar(valor, tipos[0])
        if isinstance(tipo, type) and issubclass(tipo, Enum):
            return tipo(valor)
        if tipo is bool:
            if valor not in {"0", "1"}:
                raise ValueError(f"Booleano inválido: {valor}")
            return valor == "1"
        if tipo is int:
            return int(valor)
        if tipo is Decimal:
            return Decimal(valor)
        if tipo is date:
            return date.fromisoformat(valor)
        if tipo is time:
            return time.fromisoformat(valor)
        return valor
