"""Regenera docs/DICCIONARIO_DE_DATOS.md desde dominio/modelo_datos.py.

Para cada entidad documenta, en el orden de serialización de los .txt:
  # | Atributo | Tipo | Ejemplo (primer registro real de datos/upc) | Validación / descripción

Uso:  python docs/generar_diccionario.py
"""

from __future__ import annotations

import sys
from dataclasses import fields
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from dominio import modelo_datos as m  # noqa: E402
from persistencia.gestor_persistencia import GestorPersistencia  # noqa: E402

DATOS_UPC = RAIZ / "datos" / "upc"
SALIDA = RAIZ / "docs" / "DICCIONARIO_DE_DATOS.md"

GRUPOS: list[tuple[str, list[str]]] = [
    ("Institucionales", ["Universidad", "Facultad", "ProgramaAcademico", "PlanEstudio",
                          "DetallePlanEstudio", "Curso", "Prerrequisito", "PeriodoAcademico"]),
    ("Personas", ["Persona", "Estudiante", "Profesor", "Administrativo"]),
    ("Académicas", ["OfertaCurso", "AsignacionDocente", "Horario", "MatriculaAcademica",
                     "DetalleMatricula", "Evaluacion", "Calificacion", "AlertaAcademica"]),
    ("Contratación", ["Contrato", "CategoriaDocente", "FactorSalarial", "ProduccionAcademica"]),
    ("Nómina", ["PeriodoNomina", "LiquidacionNomina", "ConceptoNomina", "DetalleLiquidacion"]),
    ("Configuración", ["ParametroNormativo", "ArchivoPersistencia"]),
]

ENUMS = {
    nombre: [e.value for e in clase]
    for nombre, clase in vars(m).items()
    if isinstance(clase, type) and issubclass(clase, __import__("enum").Enum)
}

TIPOS = {
    "int": "entero",
    "str": "texto",
    "Decimal": "decimal",
    "date": "fecha (AAAA-MM-DD)",
    "time": "hora (HH:MM)",
    "bool": "booleano (1/0)",
}

# Atributos idXxx cuyo nombre no coincide con el de la entidad referenciada.
ALIAS_REF = {
    "idDecano": "Persona",
    "idDirector": "Persona",
    "idPeriodo": "PeriodoAcademico",
    "idMatricula": "MatriculaAcademica",
    "idParametro": "ParametroNormativo",
    "idAlerta": "AlertaAcademica",
    "idAsignacion": "AsignacionDocente",
    "idPlan": "PlanEstudio",
    "idPrograma": "ProgramaAcademico",
    "idLiquidacion": "LiquidacionNomina",
    "idCursoRequerido": "Curso",
    "idProgramaPrincipal": "ProgramaAcademico",
    "idConcepto": "ConceptoNomina",
}

# Reglas de negocio verificadas en el código (gestores y liquidadores).
ESPECIFICAS: dict[tuple[str, str], str] = {
    ("Calificacion", "nota"): "Rango 0.00 a 5.00 (`registrar_calificacion`).",
    ("Evaluacion", "porcentaje"): "0 a 100; la suma por oferta debe ser exactamente 100 para calcular la nota final.",
    ("DetalleMatricula", "notaFinal"): "0.00 a 5.00, ponderada por porcentaje; aprobación con nota ≥ 3.0 (o el umbral del parámetro vigente).",
    ("OfertaCurso", "cupoDisponible"): "Entre 0 y `cupoMaximo`; se descuenta en 1 por cada matrícula y se repone al cancelar.",
    ("Estudiante", "promedioAcumulado"): "0.00 a 5.00; si cae por debajo de `PROMEDIO_MINIMO_EBRA` se genera una alerta EBRA.",
    ("Estudiante", "estadoAcademico"): "Solo los estudiantes ACTIVO pueden matricular.",
    ("Contrato", "horasSemanalesAsignadas"): "Catedráticos: máximo 18 h semanales en total; administrativos ad honorem: máximo 8 h.",
    ("Contrato", "duracionEnMeses"): "Vinculación ocasional: debe ser menor de 12 meses.",
    ("Contrato", "modalidadProfesor"): "OCASIONAL exige dedicación TC o MT; los jubilados no pueden vincularse como ocasionales ni de planta.",
    ("Contrato", "esAdHonorem"): "Si es verdadero, la liquidación sale con devengado y costo en cero (LiquidadorCatedratico).",
    ("Contrato", "valorHoraCatedraVigente"): "Si falta, se deriva de `salarioBase`/horas o del parámetro `VALOR_HORA_CATEDRA`.",
    ("ParametroNormativo", "valor"): "Porcentuales: 0 a 1; monetarios: mayor que 0 (`GestorParametros`).",
    ("ParametroNormativo", "fechaInicioVigencia"): "No puede haber dos vigencias solapadas para el mismo código.",
    ("PeriodoNomina", "estado"): "Solo se liquida en periodos ABIERTO; al cerrar se bloquean cambios directos (reliquidación por versiones).",
    ("LiquidacionNomina", "parametros_utilizados"): "Trazabilidad RF-14: códigos y valores usados. Se guarda como repr de diccionario Python (no portable a C++).",
    ("MatriculaAcademica", "totalCreditos"): "No puede superar el parámetro `MAXIMO_CREDITOS_PERIODO` al matricular.",
    ("DetalleMatricula", "estadoCurso"): "Los detalles CANCELADO no cuentan para duplicados, créditos ni promedios.",
    ("DetalleMatricula", "motivoCancelacion"): "Obligatorio al cancelar un curso.",
    ("Horario", "horaInicio"): "Con `horaFin` define los cruces de horario validados en matrícula.",
}


def tipo_de(anotacion: str) -> str:
    base = anotacion.replace(" | None", "").strip()
    if base in TIPOS:
        return TIPOS[base]
    if base in ENUMS:
        return f"enum {base}"
    if base.startswith("dict"):
        return "diccionario (texto)"
    if base.startswith("list"):
        return "lista (texto)"
    return base


def validacion(entidad: str, campo: str, anotacion: str, es_pk: bool) -> str:
    if (entidad, campo) in ESPECIFICAS:
        return ESPECIFICAS[(entidad, campo)]
    base = anotacion.replace(" | None", "").strip()
    if es_pk:
        return "Identificador único de la entidad; entero mayor que 0."
    if campo.startswith("id") and len(campo) > 2 and campo[2].isupper():
        destino = ALIAS_REF.get(campo, campo[2:])
        if hasattr(m, destino):
            return f"Referencia a **{destino}**; debe existir (integridad referencial)."
        return "Referencia a otra entidad; debe existir (integridad referencial)."
    if base in ENUMS:
        return "Uno de: " + ", ".join(f"`{v}`" for v in ENUMS[base]) + "."
    if base == "date":
        return "Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial."
    if base == "time":
        return "Formato HH:MM."
    if base == "bool":
        return "1 = verdadero, 0 = falso."
    if base == "Decimal":
        return "Número decimal exacto, normalmente ≥ 0."
    if campo == "estado":
        return "Texto libre; valores de uso común: ACTIVO, INACTIVO, CERRADO."
    return "—"


def ejemplos(entidad: type, n_campos: int) -> list[str]:
    """Primera línea no vacía del archivo del tenant UPC, como ejemplo real."""
    archivo = GestorPersistencia.ARCHIVOS.get(entidad)
    if not archivo:
        return ["—"] * n_campos
    ruta = DATOS_UPC / archivo
    if not ruta.exists():
        return ["—"] * n_campos
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        if linea.strip():
            valores = linea.split(GestorPersistencia.DELIMITADOR)
            valores += [""] * (n_campos - len(valores))
            return [v[:38] + "…" if len(v) > 38 else (v if v else "*(vacío)*") for v in valores[:n_campos]]
    return ["—"] * n_campos


def main() -> None:
    lineas = [
        "# Diccionario de datos del sistema PITA",
        "",
        "> Anexo del *Documento maestro PITA* (sección 9). Generado automáticamente desde "
        "`dominio/modelo_datos.py` y los datos reales de `datos/upc/` el 2026-09-12 "
        "(`docs/generar_diccionario.py`), por lo que corresponde exactamente al código.",
        ">",
        "> **Convenciones:**",
        "> - Todos los atributos son opcionales en la construcción (aceptan vacío); la obligatoriedad "
        "real la imponen los gestores según la operación.",
        "> - Las referencias entre entidades se expresan con atributos `idXxx` (sección 10 del documento maestro).",
        "> - La columna **Ejemplo** muestra el primer registro real del tenant UPC; `*(vacío)*` "
        "indica que el campo se serializa vacío en ese registro.",
        "> - La columna **Validación / descripción** resume la regla verificada en el código; "
        "las reglas de negocio completas están en las secciones 12 a 14 del documento maestro.",
        "> - Los tipos `enum X` toman valores de la enumeración correspondiente (sección 11).",
        "> - El orden de los atributos en cada tabla es el orden de serialización en los `.txt` (sección 17).",
        "",
        "---",
        "",
    ]
    total_atributos = 0
    for titulo, nombres in GRUPOS:
        lineas += [f"## {titulo}", ""]
        for nombre in nombres:
            entidad = getattr(m, nombre)
            campos = list(fields(entidad))
            total_atributos += len(campos)
            muestra = ejemplos(entidad, len(campos))
            lineas += [
                f"### {nombre}",
                "",
                "| # | Atributo | Tipo | Ejemplo (UPC) | Validación / descripción |",
                "|---|---|---|---|---|",
            ]
            for i, campo in enumerate(campos, 1):
                anotacion = str(campo.type)
                fila = (
                    f"| {i} | `{campo.name}` | {tipo_de(anotacion)} | {muestra[i - 1]} "
                    f"| {validacion(nombre, campo.name, anotacion, i == 1)} |"
                )
                lineas.append(fila)
            lineas.append("")
    SALIDA.write_text("\n".join(lineas), encoding="utf-8", newline="\n")
    entidades = sum(len(n) for _, n in GRUPOS)
    print(f"Diccionario regenerado: {entidades} entidades, {total_atributos} atributos -> {SALIDA}")


if __name__ == "__main__":
    main()
