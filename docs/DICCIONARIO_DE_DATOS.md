# Diccionario de datos del sistema PITA

> Anexo del *Documento maestro PITA* (sección 9). Generado automáticamente desde `dominio/modelo_datos.py` y los datos reales de `datos/upc/` el 2026-09-12 (`docs/generar_diccionario.py`), por lo que corresponde exactamente al código.
>
> **Convenciones:**
> - Todos los atributos son opcionales en la construcción (aceptan vacío); la obligatoriedad real la imponen los gestores según la operación.
> - Las referencias entre entidades se expresan con atributos `idXxx` (sección 10 del documento maestro).
> - La columna **Ejemplo** muestra el primer registro real del tenant UPC; `*(vacío)*` indica que el campo se serializa vacío en ese registro.
> - La columna **Validación / descripción** resume la regla verificada en el código; las reglas de negocio completas están en las secciones 12 a 14 del documento maestro.
> - Los tipos `enum X` toman valores de la enumeración correspondiente (sección 11).
> - El orden de los atributos en cada tabla es el orden de serialización en los `.txt` (sección 17).

---

## Institucionales

### Universidad

| # | Atributo | Tipo | Ejemplo (UPC) | Validación / descripción |
|---|---|---|---|---|
| 1 | `idUniversidad` | entero | 1 | Identificador único de la entidad; entero mayor que 0. |
| 2 | `nombre` | texto | Universidad Popular del Cesar | — |
| 3 | `nit` | texto | 892300128-6 | — |
| 4 | `codigoInstitucional` | texto | 1084 | — |
| 5 | `direccion` | texto | Sede Sabanas, Av. Universidad | — |
| 6 | `ciudad` | texto | Valledupar | — |
| 7 | `departamento` | texto | Cesar | — |
| 8 | `telefono` | texto | 5842000 | — |
| 9 | `correoInstitucional` | texto | rectoria@unicesar.edu.co | — |
| 10 | `sitioWeb` | texto | https://www.unicesar.edu.co | — |
| 11 | `estado` | texto | ACTIVO | Texto libre; valores de uso común: ACTIVO, INACTIVO, CERRADO. |
| 12 | `cajaCompensacion` | texto | *(vacío)* | — |
| 13 | `arl` | texto | *(vacío)* | — |
| 14 | `aplicaExoneracionLey1819` | booleano (1/0) | *(vacío)* | 1 = verdadero, 0 = falso. |

### Facultad

| # | Atributo | Tipo | Ejemplo (UPC) | Validación / descripción |
|---|---|---|---|---|
| 1 | `idFacultad` | entero | 1 | Identificador único de la entidad; entero mayor que 0. |
| 2 | `codigoFacultad` | texto | FIT | — |
| 3 | `nombre` | texto | Facultad de Ingenierias y Tecnologicas | — |
| 4 | `descripcion` | texto | Facultad institucional UPC | — |
| 5 | `ubicacion` | texto | Campus Sabanas, Bloque B | — |
| 6 | `telefono` | texto | 5842000 | — |
| 7 | `correo` | texto | fit@unicesar.edu.co | — |
| 8 | `idDecano` | entero | *(vacío)* | Referencia a **Persona**; debe existir (integridad referencial). |
| 9 | `fechaCreacion` | fecha (AAAA-MM-DD) | 2026-09-09 | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 10 | `estado` | texto | ACTIVO | Texto libre; valores de uso común: ACTIVO, INACTIVO, CERRADO. |
| 11 | `idUniversidad` | entero | *(vacío)* | Referencia a **Universidad**; debe existir (integridad referencial). |

### ProgramaAcademico

| # | Atributo | Tipo | Ejemplo (UPC) | Validación / descripción |
|---|---|---|---|---|
| 1 | `idPrograma` | entero | 1 | Identificador único de la entidad; entero mayor que 0. |
| 2 | `codigoPrograma` | texto | SIS | — |
| 3 | `nombre` | texto | Ingenieria de Sistemas | — |
| 4 | `nivelFormacion` | texto | PREGRADO | — |
| 5 | `modalidad` | texto | PRESENCIAL | — |
| 6 | `numeroSemestres` | entero | 10 | — |
| 7 | `totalCreditos` | entero | 160 | — |
| 8 | `registroCalificado` | texto | RC-2026-V1 | — |
| 9 | `fechaCreacion` | fecha (AAAA-MM-DD) | 2026-09-09 | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 10 | `idDirector` | entero | *(vacío)* | Referencia a **Persona**; debe existir (integridad referencial). |
| 11 | `idFacultad` | entero | 1 | Referencia a **Facultad**; debe existir (integridad referencial). |
| 12 | `estado` | texto | ACTIVO | Texto libre; valores de uso común: ACTIVO, INACTIVO, CERRADO. |

### PlanEstudio

| # | Atributo | Tipo | Ejemplo (UPC) | Validación / descripción |
|---|---|---|---|---|
| 1 | `idPlanEstudio` | entero | 1 | Identificador único de la entidad; entero mayor que 0. |
| 2 | `codigo` | texto | PLAN-SIS-2026 | — |
| 3 | `nombre` | texto | Plan Ingenieria de Sistemas 2026 | — |
| 4 | `version` | texto | V1 | — |
| 5 | `fechaInicioVigencia` | fecha (AAAA-MM-DD) | 2026-09-09 | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 6 | `fechaFinVigencia` | fecha (AAAA-MM-DD) | *(vacío)* | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 7 | `totalCreditos` | entero | 7 | — |
| 8 | `idPrograma` | entero | 1 | Referencia a **ProgramaAcademico**; debe existir (integridad referencial). |
| 9 | `estado` | texto | ACTIVO | Texto libre; valores de uso común: ACTIVO, INACTIVO, CERRADO. |

### DetallePlanEstudio

| # | Atributo | Tipo | Ejemplo (UPC) | Validación / descripción |
|---|---|---|---|---|
| 1 | `idDetallePlan` | entero | 1 | Identificador único de la entidad; entero mayor que 0. |
| 2 | `idPlanEstudio` | entero | 1 | Referencia a **PlanEstudio**; debe existir (integridad referencial). |
| 3 | `idCurso` | entero | 1 | Referencia a **Curso**; debe existir (integridad referencial). |
| 4 | `semestreSugerido` | entero | 1 | — |
| 5 | `tipoCurso` | texto | OBLIGATORIA | — |
| 6 | `numeroCreditos` | entero | 3 | — |
| 7 | `esObligatorio` | booleano (1/0) | 1 | 1 = verdadero, 0 = falso. |
| 8 | `estado` | texto | ACTIVO | Texto libre; valores de uso común: ACTIVO, INACTIVO, CERRADO. |

### Curso

| # | Atributo | Tipo | Ejemplo (UPC) | Validación / descripción |
|---|---|---|---|---|
| 1 | `idCurso` | entero | 1 | Identificador único de la entidad; entero mayor que 0. |
| 2 | `codigoCurso` | texto | SIS-301 | — |
| 3 | `nombre` | texto | Estructuras de Datos | — |
| 4 | `descripcion` | texto | Estructuras de Datos | — |
| 5 | `numeroCreditos` | entero | 3 | — |
| 6 | `horasTeoricas` | entero | 3 | — |
| 7 | `horasPracticas` | entero | 2 | — |
| 8 | `horasTrabajoIndependiente` | entero | 6 | — |
| 9 | `cupoSugerido` | entero | 30 | — |
| 10 | `notaMinimaAprobatoria` | decimal | 3.0 | Número decimal exacto, normalmente ≥ 0. |
| 11 | `estado` | texto | ACTIVO | Texto libre; valores de uso común: ACTIVO, INACTIVO, CERRADO. |

### Prerrequisito

| # | Atributo | Tipo | Ejemplo (UPC) | Validación / descripción |
|---|---|---|---|---|
| 1 | `idPrerrequisito` | entero | — | Identificador único de la entidad; entero mayor que 0. |
| 2 | `idCurso` | entero | — | Referencia a **Curso**; debe existir (integridad referencial). |
| 3 | `idCursoRequerido` | entero | — | Referencia a **Curso**; debe existir (integridad referencial). |
| 4 | `tipoRequisito` | texto | — | — |
| 5 | `notaMinima` | decimal | — | Número decimal exacto, normalmente ≥ 0. |
| 6 | `creditosMinimos` | entero | — | — |
| 7 | `estado` | texto | — | Texto libre; valores de uso común: ACTIVO, INACTIVO, CERRADO. |

### PeriodoAcademico

| # | Atributo | Tipo | Ejemplo (UPC) | Validación / descripción |
|---|---|---|---|---|
| 1 | `idPeriodo` | entero | 1 | Identificador único de la entidad; entero mayor que 0. |
| 2 | `codigo` | texto | 2026-1 | — |
| 3 | `nombre` | texto | Primer Período Académico 2026 | — |
| 4 | `anio` | entero | 2026 | — |
| 5 | `numeroPeriodo` | entero | 1 | — |
| 6 | `fechaInicio` | fecha (AAAA-MM-DD) | 2026-02-01 | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 7 | `fechaFin` | fecha (AAAA-MM-DD) | 2026-06-30 | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 8 | `fechaInicioMatricula` | fecha (AAAA-MM-DD) | 2026-01-15 | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 9 | `fechaFinMatricula` | fecha (AAAA-MM-DD) | 2026-02-10 | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 10 | `fechaLimiteCancelacion` | fecha (AAAA-MM-DD) | 2026-04-15 | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 11 | `estado` | texto | ABIERTO | Texto libre; valores de uso común: ACTIVO, INACTIVO, CERRADO. |

## Personas

### Persona

| # | Atributo | Tipo | Ejemplo (UPC) | Validación / descripción |
|---|---|---|---|---|
| 1 | `idPersona` | entero | 1 | Identificador único de la entidad; entero mayor que 0. |
| 2 | `tipoDocumento` | texto | CC | — |
| 3 | `numeroDocumento` | texto | 12345678 | — |
| 4 | `primerNombre` | texto | Carlos | — |
| 5 | `segundoNombre` | texto | Alberto | — |
| 6 | `primerApellido` | texto | Gomez | — |
| 7 | `segundoApellido` | texto | Solano | — |
| 8 | `fechaNacimiento` | fecha (AAAA-MM-DD) | *(vacío)* | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 9 | `direccion` | texto | *(vacío)* | — |
| 10 | `telefono` | texto | 3001234567 | — |
| 11 | `correoPersonal` | texto | *(vacío)* | — |
| 12 | `correoInstitucional` | texto | cgomez@unicesar.edu.co | — |
| 13 | `ciudadResidencia` | texto | Valledupar | — |
| 14 | `fechaRegistro` | fecha (AAAA-MM-DD) | 2026-09-09 | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 15 | `estado` | texto | ACTIVO | Texto libre; valores de uso común: ACTIVO, INACTIVO, CERRADO. |

### Estudiante

| # | Atributo | Tipo | Ejemplo (UPC) | Validación / descripción |
|---|---|---|---|---|
| 1 | `idEstudiante` | entero | 1 | Identificador único de la entidad; entero mayor que 0. |
| 2 | `idPersona` | entero | 3 | Referencia a **Persona**; debe existir (integridad referencial). |
| 3 | `codigoEstudiante` | texto | EST-2026-001 | — |
| 4 | `idPrograma` | entero | 1 | Referencia a **ProgramaAcademico**; debe existir (integridad referencial). |
| 5 | `idPlanEstudio` | entero | 1 | Referencia a **PlanEstudio**; debe existir (integridad referencial). |
| 6 | `fechaIngreso` | fecha (AAAA-MM-DD) | 2026-09-09 | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 7 | `semestreActual` | entero | 3 | — |
| 8 | `creditosAprobados` | entero | 0 | — |
| 9 | `promedioAcumulado` | decimal | 4.2 | 0.00 a 5.00; si cae por debajo de `PROMEDIO_MINIMO_EBRA` se genera una alerta EBRA. |
| 10 | `estadoAcademico` | enum EstadoAcademico | ACTIVO | Solo los estudiantes ACTIVO pueden matricular. |
| 11 | `estado` | texto | ACTIVO | Texto libre; valores de uso común: ACTIVO, INACTIVO, CERRADO. |

### Profesor

| # | Atributo | Tipo | Ejemplo (UPC) | Validación / descripción |
|---|---|---|---|---|
| 1 | `idProfesor` | entero | 1 | Identificador único de la entidad; entero mayor que 0. |
| 2 | `idPersona` | entero | 1 | Referencia a **Persona**; debe existir (integridad referencial). |
| 3 | `codigoProfesor` | texto | DOC-001 | — |
| 4 | `idProgramaPrincipal` | entero | 1 | Referencia a **ProgramaAcademico**; debe existir (integridad referencial). |
| 5 | `fechaVinculacion` | fecha (AAAA-MM-DD) | 2026-09-09 | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 6 | `tipoProfesor` | enum TipoProfesor | PLANTA | Uno de: `PLANTA`, `OCASIONAL`, `CATEDRATICO`, `CATEDRATICO_AD_HONOREM`. |
| 7 | `categoriaDocente` | texto | ASISTENTE | — |
| 8 | `dedicacion` | enum Dedicacion | TIEMPO_COMPLETO | Uno de: `TIEMPO_COMPLETO`, `MEDIO_TIEMPO`, `HORA_CATEDRA`. |
| 9 | `maximoNivelEstudio` | texto | MAESTRIA | — |
| 10 | `tituloProfesional` | texto | Ingeniero de Sistemas | — |
| 11 | `areaConocimiento` | texto | Ingeniería de Software | — |
| 12 | `numeroHorasSemanales` | decimal | 40 | Número decimal exacto, normalmente ≥ 0. |
| 13 | `puntosSalariales` | decimal | 58 | Número decimal exacto, normalmente ≥ 0. |
| 14 | `estado` | texto | ACTIVO | Texto libre; valores de uso común: ACTIVO, INACTIVO, CERRADO. |
| 15 | `regimenSalarial` | texto | *(vacío)* | — |
| 16 | `modalidadVinculacion` | texto | *(vacío)* | — |
| 17 | `perteneceCarreraDocente` | booleano (1/0) | *(vacío)* | 1 = verdadero, 0 = falso. |
| 18 | `fechaIngresoCarreraDocente` | fecha (AAAA-MM-DD) | *(vacío)* | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 19 | `fechaPosesion` | fecha (AAAA-MM-DD) | *(vacío)* | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 20 | `fechaUltimaVinculacion` | fecha (AAAA-MM-DD) | *(vacío)* | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 21 | `fechaRetiro` | fecha (AAAA-MM-DD) | *(vacío)* | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 22 | `motivoRetiro` | texto | *(vacío)* | — |
| 23 | `actoAdministrativoIngreso` | texto | *(vacío)* | — |
| 24 | `actoAdministrativoRetiro` | texto | *(vacío)* | — |
| 25 | `evaluacionDesempenoAnterior` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 26 | `puedeSerVinculadoSiguientePeriodo` | booleano (1/0) | *(vacío)* | 1 = verdadero, 0 = falso. |
| 27 | `idCategoriaDocente` | entero | *(vacío)* | Referencia a **CategoriaDocente**; debe existir (integridad referencial). |
| 28 | `categoriaReconocida` | texto | *(vacío)* | — |
| 29 | `categoriaInstitucionOrigen` | texto | *(vacío)* | — |
| 30 | `fechaReconocimientoCategoria` | fecha (AAAA-MM-DD) | *(vacío)* | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 31 | `actoReconocimientoCategoria` | texto | *(vacío)* | — |
| 32 | `categoriaComoInvestigador` | texto | *(vacío)* | — |
| 33 | `grupoInvestigacion` | texto | *(vacío)* | — |
| 34 | `categoriaGrupoInvestigacion` | texto | *(vacío)* | — |
| 35 | `perteneceSemillero` | booleano (1/0) | *(vacío)* | 1 = verdadero, 0 = falso. |
| 36 | `semilleroInvestigacion` | texto | *(vacío)* | — |
| 37 | `productividadInvestigativaVigente` | booleano (1/0) | *(vacío)* | 1 = verdadero, 0 = falso. |
| 38 | `participaProyectoInvestigacionVigente` | booleano (1/0) | *(vacío)* | 1 = verdadero, 0 = falso. |
| 39 | `certificacionVicerrectoriaInvestigacion` | texto | *(vacío)* | — |
| 40 | `nivelPosgradoReconocido` | texto | *(vacío)* | — |
| 41 | `tituloPosgradoReconocido` | texto | *(vacío)* | — |
| 42 | `fechaObtencionPosgrado` | fecha (AAAA-MM-DD) | *(vacío)* | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 43 | `tituloConvalidado` | booleano (1/0) | *(vacío)* | 1 = verdadero, 0 = falso. |
| 44 | `numeroResolucionConvalidacion` | texto | *(vacío)* | — |
| 45 | `esEspecializacionClinica` | booleano (1/0) | *(vacío)* | 1 = verdadero, 0 = falso. |
| 46 | `posgradoRelacionadoConAreaDesempeno` | booleano (1/0) | *(vacío)* | 1 = verdadero, 0 = falso. |
| 47 | `factorBonificacionPosgrado` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 48 | `fechaInicioReconocimientoPosgrado` | fecha (AAAA-MM-DD) | *(vacío)* | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 49 | `fechaFinReconocimientoPosgrado` | fecha (AAAA-MM-DD) | *(vacío)* | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 50 | `aniosExperienciaDocenteUniversitaria` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 51 | `periodosExperienciaDocenteUniversitaria` | entero | *(vacío)* | — |
| 52 | `aniosExperienciaInvestigacion` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 53 | `aniosExperienciaProfesional` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 54 | `aniosExperienciaDireccionAcademica` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 55 | `experienciaEquivalenteTiempoCompleto` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 56 | `experienciaCertificada` | booleano (1/0) | *(vacío)* | 1 = verdadero, 0 = falso. |
| 57 | `fechaCorteExperiencia` | fecha (AAAA-MM-DD) | *(vacío)* | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 58 | `puntosExperienciaReconocidos` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |

### Administrativo

| # | Atributo | Tipo | Ejemplo (UPC) | Validación / descripción |
|---|---|---|---|---|
| 1 | `idAdministrativo` | entero | 1 | Identificador único de la entidad; entero mayor que 0. |
| 2 | `idPersona` | entero | 5 | Referencia a **Persona**; debe existir (integridad referencial). |
| 3 | `codigoEmpleado` | texto | ADM-2026-01 | — |
| 4 | `cargo` | texto | Secretaria Academica FIT | — |
| 5 | `dependencia` | texto | Facultad de Ingenierias y Tecnologicas | — |
| 6 | `categoria` | texto | PROFESIONAL | — |
| 7 | `tipoContratacion` | texto | PLANTA | — |
| 8 | `fechaVinculacion` | fecha (AAAA-MM-DD) | 2026-09-09 | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 9 | `salarioBase` | decimal | 3200000 | Número decimal exacto, normalmente ≥ 0. |
| 10 | `estado` | texto | ACTIVO | Texto libre; valores de uso común: ACTIVO, INACTIVO, CERRADO. |

## Académicas

### OfertaCurso

| # | Atributo | Tipo | Ejemplo (UPC) | Validación / descripción |
|---|---|---|---|---|
| 1 | `idOfertaCurso` | entero | 1 | Identificador único de la entidad; entero mayor que 0. |
| 2 | `idCurso` | entero | 1 | Referencia a **Curso**; debe existir (integridad referencial). |
| 3 | `idPeriodo` | entero | 1 | Referencia a **PeriodoAcademico**; debe existir (integridad referencial). |
| 4 | `grupo` | texto | 01 | — |
| 5 | `cupoMaximo` | entero | 30 | — |
| 6 | `cupoDisponible` | entero | 28 | Entre 0 y `cupoMaximo`; se descuenta en 1 por cada matrícula y se repone al cancelar. |
| 7 | `modalidad` | texto | PRESENCIAL | — |
| 8 | `aula` | texto | 204 Sabanas | — |
| 9 | `sede` | texto | Sede Sabanas | — |
| 10 | `fechaInicio` | fecha (AAAA-MM-DD) | *(vacío)* | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 11 | `fechaFin` | fecha (AAAA-MM-DD) | *(vacío)* | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 12 | `estado` | texto | ACTIVO | Texto libre; valores de uso común: ACTIVO, INACTIVO, CERRADO. |

### AsignacionDocente

| # | Atributo | Tipo | Ejemplo (UPC) | Validación / descripción |
|---|---|---|---|---|
| 1 | `idAsignacion` | entero | 1 | Identificador único de la entidad; entero mayor que 0. |
| 2 | `idProfesor` | entero | 1 | Referencia a **Profesor**; debe existir (integridad referencial). |
| 3 | `idOfertaCurso` | entero | 1 | Referencia a **OfertaCurso**; debe existir (integridad referencial). |
| 4 | `rolDocente` | texto | TITULAR | — |
| 5 | `numeroHoras` | decimal | 4 | Número decimal exacto, normalmente ≥ 0. |
| 6 | `porcentajeResponsabilidad` | decimal | 100 | Número decimal exacto, normalmente ≥ 0. |
| 7 | `fechaAsignacion` | fecha (AAAA-MM-DD) | 2026-09-09 | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 8 | `estado` | texto | ACTIVO | Texto libre; valores de uso común: ACTIVO, INACTIVO, CERRADO. |

### Horario

| # | Atributo | Tipo | Ejemplo (UPC) | Validación / descripción |
|---|---|---|---|---|
| 1 | `idHorario` | entero | — | Identificador único de la entidad; entero mayor que 0. |
| 2 | `idOfertaCurso` | entero | — | Referencia a **OfertaCurso**; debe existir (integridad referencial). |
| 3 | `diaSemana` | texto | — | — |
| 4 | `horaInicio` | hora (HH:MM) | — | Con `horaFin` define los cruces de horario validados en matrícula. |
| 5 | `horaFin` | hora (HH:MM) | — | Formato HH:MM. |
| 6 | `aula` | texto | — | — |
| 7 | `sede` | texto | — | — |
| 8 | `tipoSesion` | texto | — | — |
| 9 | `estado` | texto | — | Texto libre; valores de uso común: ACTIVO, INACTIVO, CERRADO. |

### MatriculaAcademica

| # | Atributo | Tipo | Ejemplo (UPC) | Validación / descripción |
|---|---|---|---|---|
| 1 | `idMatricula` | entero | 1 | Identificador único de la entidad; entero mayor que 0. |
| 2 | `idEstudiante` | entero | 1 | Referencia a **Estudiante**; debe existir (integridad referencial). |
| 3 | `idPeriodo` | entero | 1 | Referencia a **PeriodoAcademico**; debe existir (integridad referencial). |
| 4 | `fechaMatricula` | fecha (AAAA-MM-DD) | 2026-09-09 | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 5 | `totalCreditos` | entero | 3 | No puede superar el parámetro `MAXIMO_CREDITOS_PERIODO` al matricular. |
| 6 | `promedioPeriodo` | decimal | 0.0 | Número decimal exacto, normalmente ≥ 0. |
| 7 | `estadoMatricula` | texto | ACTIVO | — |
| 8 | `observaciones` | texto | *(vacío)* | — |

### DetalleMatricula

| # | Atributo | Tipo | Ejemplo (UPC) | Validación / descripción |
|---|---|---|---|---|
| 1 | `idDetalleMatricula` | entero | 1 | Identificador único de la entidad; entero mayor que 0. |
| 2 | `idMatricula` | entero | 1 | Referencia a **MatriculaAcademica**; debe existir (integridad referencial). |
| 3 | `idOfertaCurso` | entero | 1 | Referencia a **OfertaCurso**; debe existir (integridad referencial). |
| 4 | `fechaInscripcion` | fecha (AAAA-MM-DD) | 2026-09-09 | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 5 | `estadoCurso` | enum EstadoCurso | APROBADO | Los detalles CANCELADO no cuentan para duplicados, créditos ni promedios. |
| 6 | `notaFinal` | decimal | 4.2 | 0.00 a 5.00, ponderada por porcentaje; aprobación con nota ≥ 3.0 (o el umbral del parámetro vigente). |
| 7 | `numeroFallas` | entero | *(vacío)* | — |
| 8 | `fechaCancelacion` | fecha (AAAA-MM-DD) | *(vacío)* | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 9 | `motivoCancelacion` | texto | *(vacío)* | Obligatorio al cancelar un curso. |

### Evaluacion

| # | Atributo | Tipo | Ejemplo (UPC) | Validación / descripción |
|---|---|---|---|---|
| 1 | `idEvaluacion` | entero | — | Identificador único de la entidad; entero mayor que 0. |
| 2 | `idOfertaCurso` | entero | — | Referencia a **OfertaCurso**; debe existir (integridad referencial). |
| 3 | `nombre` | texto | — | — |
| 4 | `tipo` | texto | — | — |
| 5 | `porcentaje` | decimal | — | 0 a 100; la suma por oferta debe ser exactamente 100 para calcular la nota final. |
| 6 | `fechaProgramada` | fecha (AAAA-MM-DD) | — | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 7 | `descripcion` | texto | — | — |
| 8 | `estado` | texto | — | Texto libre; valores de uso común: ACTIVO, INACTIVO, CERRADO. |

### Calificacion

| # | Atributo | Tipo | Ejemplo (UPC) | Validación / descripción |
|---|---|---|---|---|
| 1 | `idCalificacion` | entero | — | Identificador único de la entidad; entero mayor que 0. |
| 2 | `idEvaluacion` | entero | — | Referencia a **Evaluacion**; debe existir (integridad referencial). |
| 3 | `idDetalleMatricula` | entero | — | Referencia a **DetalleMatricula**; debe existir (integridad referencial). |
| 4 | `nota` | decimal | — | Rango 0.00 a 5.00 (`registrar_calificacion`). |
| 5 | `fechaRegistro` | fecha (AAAA-MM-DD) | — | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 6 | `observacion` | texto | — | — |
| 7 | `estado` | texto | — | Texto libre; valores de uso común: ACTIVO, INACTIVO, CERRADO. |

### AlertaAcademica

| # | Atributo | Tipo | Ejemplo (UPC) | Validación / descripción |
|---|---|---|---|---|
| 1 | `idAlerta` | entero | 1 | Identificador único de la entidad; entero mayor que 0. |
| 2 | `idEstudiante` | entero | 2 | Referencia a **Estudiante**; debe existir (integridad referencial). |
| 3 | `idPeriodo` | entero | 1 | Referencia a **PeriodoAcademico**; debe existir (integridad referencial). |
| 4 | `tipoAlerta` | texto | EBRA | — |
| 5 | `motivo` | texto | El promedio acumulado está por debajo … | — |
| 6 | `valorObservado` | decimal | 2.65 | Número decimal exacto, normalmente ≥ 0. |
| 7 | `valorLimite` | decimal | 3.0 | Número decimal exacto, normalmente ≥ 0. |
| 8 | `fechaGeneracion` | fecha (AAAA-MM-DD) | 2026-09-09 | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 9 | `atendida` | booleano (1/0) | 0 | 1 = verdadero, 0 = falso. |
| 10 | `observaciones` | texto | *(vacío)* | — |
| 11 | `estado` | texto | ACTIVO | Texto libre; valores de uso común: ACTIVO, INACTIVO, CERRADO. |

## Contratación

### Contrato

| # | Atributo | Tipo | Ejemplo (UPC) | Validación / descripción |
|---|---|---|---|---|
| 1 | `idContrato` | entero | 1 | Identificador único de la entidad; entero mayor que 0. |
| 2 | `idPersona` | entero | 5 | Referencia a **Persona**; debe existir (integridad referencial). |
| 3 | `numeroContrato` | texto | ADM-CONTRATO-001 | — |
| 4 | `tipoContrato` | texto | TERMINO_INDEFINIDO | — |
| 5 | `fechaInicio` | fecha (AAAA-MM-DD) | 2026-09-09 | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 6 | `fechaFin` | fecha (AAAA-MM-DD) | *(vacío)* | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 7 | `dedicacion` | enum Dedicacion | *(vacío)* | Uno de: `TIEMPO_COMPLETO`, `MEDIO_TIEMPO`, `HORA_CATEDRA`. |
| 8 | `horasSemanales` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 9 | `horasCatedra` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 10 | `valorHora` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 11 | `aplicaAuxilioTransporte` | booleano (1/0) | 1 | 1 = verdadero, 0 = falso. |
| 12 | `salarioBase` | decimal | 3200000 | Número decimal exacto, normalmente ≥ 0. |
| 13 | `claseARL` | texto | *(vacío)* | — |
| 14 | `actoAdministrativo` | texto | *(vacío)* | — |
| 15 | `observaciones` | texto | Cargo: Secretaria Academica FIT  -  De… | — |
| 16 | `estado` | texto | ACTIVO | Texto libre; valores de uso común: ACTIVO, INACTIVO, CERRADO. |
| 17 | `regimenAplicable` | texto | CST_LEY100_ADMINISTRATIVO | — |
| 18 | `normaVinculacion` | texto | *(vacío)* | — |
| 19 | `articuloNormativo` | texto | *(vacío)* | — |
| 20 | `modalidadProfesor` | texto | *(vacío)* | OCASIONAL exige dedicación TC o MT; los jubilados no pueden vincularse como ocasionales ni de planta. |
| 21 | `esEmpleadoPublicoDocente` | booleano (1/0) | 0 | 1 = verdadero, 0 = falso. |
| 22 | `perteneceCarreraProfesoral` | booleano (1/0) | 0 | 1 = verdadero, 0 = falso. |
| 23 | `esTransitorio` | booleano (1/0) | 0 | 1 = verdadero, 0 = falso. |
| 24 | `esRemunerado` | booleano (1/0) | 1 | 1 = verdadero, 0 = falso. |
| 25 | `esAdHonorem` | booleano (1/0) | 0 | Si es verdadero, la liquidación sale con devengado y costo en cero (LiquidadorCatedratico). |
| 26 | `tipoDedicacion` | texto | *(vacío)* | — |
| 27 | `porcentajeDedicacion` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 28 | `duracionEnMeses` | entero | *(vacío)* | Vinculación ocasional: debe ser menor de 12 meses. |
| 29 | `periodoAcademicoInicial` | entero | *(vacío)* | — |
| 30 | `periodoAcademicoFinal` | entero | *(vacío)* | — |
| 31 | `tipoActoVinculacion` | texto | *(vacío)* | — |
| 32 | `numeroActoVinculacion` | texto | *(vacío)* | — |
| 33 | `fechaActoVinculacion` | fecha (AAAA-MM-DD) | *(vacío)* | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 34 | `fechaPosesion` | fecha (AAAA-MM-DD) | *(vacío)* | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 35 | `certificadoDisponibilidadPresupuestal` | texto | *(vacío)* | — |
| 36 | `numeroCDP` | texto | *(vacío)* | — |
| 37 | `fechaCDP` | fecha (AAAA-MM-DD) | *(vacío)* | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 38 | `valorDisponibilidadPresupuestal` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 39 | `resolucionRectoral` | texto | *(vacío)* | — |
| 40 | `fechaResolucionRectoral` | fecha (AAAA-MM-DD) | *(vacío)* | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 41 | `estadoFormalizacion` | texto | *(vacío)* | — |
| 42 | `fechaInicioEfectiva` | fecha (AAAA-MM-DD) | *(vacío)* | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 43 | `fechaTerminacionEfectiva` | fecha (AAAA-MM-DD) | *(vacío)* | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 44 | `horasSemanalesAsignadas` | decimal | *(vacío)* | Catedráticos: máximo 18 h semanales en total; administrativos ad honorem: máximo 8 h. |
| 45 | `horasMensualesAsignadas` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 46 | `horasDocenciaDirecta` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 47 | `horasActividadesComplementarias` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 48 | `horasMensualesReconocidas` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 49 | `horasMensualesCumplidas` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 50 | `horasIncumplidas` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 51 | `valorHoraIncumplida` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 52 | `valorDescuentoIncumplimiento` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 53 | `limiteHorasSemanales` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 54 | `requiereCertificacionCumplimiento` | booleano (1/0) | *(vacío)* | 1 = verdadero, 0 = falso. |
| 55 | `certificacionCumplimiento` | texto | *(vacío)* | — |
| 56 | `fechaCertificacionCumplimiento` | fecha (AAAA-MM-DD) | *(vacío)* | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 57 | `categoriaDocenteAlVincular` | texto | *(vacío)* | — |
| 58 | `nivelPosgradoAlVincular` | texto | *(vacío)* | — |
| 59 | `grupoInvestigacionAlVincular` | texto | *(vacío)* | — |
| 60 | `categoriaGrupoAlVincular` | texto | *(vacío)* | — |
| 61 | `semilleroAlVincular` | texto | *(vacío)* | — |
| 62 | `salarioMinimoVigente` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 63 | `factorSalarialSMMLV` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 64 | `valorHoraCatedraVigente` | decimal | *(vacío)* | Si falta, se deriva de `salarioBase`/horas o del parámetro `VALOR_HORA_CATEDRA`. |
| 65 | `resolucionValorHoraCatedra` | texto | *(vacío)* | — |
| 66 | `fechaVigenciaValorHora` | fecha (AAAA-MM-DD) | *(vacío)* | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 67 | `salarioMensualPactado` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 68 | `permiteBonificacionPosgrado` | booleano (1/0) | *(vacío)* | 1 = verdadero, 0 = falso. |
| 69 | `permiteBonificacionInvestigacion` | booleano (1/0) | *(vacío)* | 1 = verdadero, 0 = falso. |
| 70 | `permitePrestacionesSociales` | booleano (1/0) | *(vacío)* | 1 = verdadero, 0 = falso. |
| 71 | `permiteAportesParafiscales` | booleano (1/0) | *(vacío)* | 1 = verdadero, 0 = falso. |
| 72 | `causalTerminacion` | texto | *(vacío)* | — |
| 73 | `fechaNovedadTerminacion` | fecha (AAAA-MM-DD) | *(vacío)* | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 74 | `actoTerminacion` | texto | *(vacío)* | — |
| 75 | `renunciaPresentada` | booleano (1/0) | *(vacío)* | 1 = verdadero, 0 = falso. |
| 76 | `renunciaAceptada` | booleano (1/0) | *(vacío)* | 1 = verdadero, 0 = falso. |
| 77 | `necesidadServicioVigente` | booleano (1/0) | *(vacío)* | 1 = verdadero, 0 = falso. |
| 78 | `incumplimientoComprobado` | booleano (1/0) | *(vacío)* | 1 = verdadero, 0 = falso. |
| 79 | `decisionJudicialOAdministrativa` | texto | *(vacío)* | — |
| 80 | `documentoSoporteTerminacion` | texto | *(vacío)* | — |
| 81 | `estadoFinalContrato` | texto | *(vacío)* | — |
| 82 | `idUniversidad` | entero | *(vacío)* | Referencia a **Universidad**; debe existir (integridad referencial). |

### CategoriaDocente

| # | Atributo | Tipo | Ejemplo (UPC) | Validación / descripción |
|---|---|---|---|---|
| 1 | `idCategoria` | entero | — | Identificador único de la entidad; entero mayor que 0. |
| 2 | `codigo` | enum CategoriaDocenteCodigo | — | Uno de: `AUXILIAR`, `ASISTENTE`, `ASOCIADO`, `TITULAR`, `NO_CATEGORIZADO`. |
| 3 | `nombre` | texto | — | — |
| 4 | `descripcion` | texto | — | — |
| 5 | `puntosBase` | decimal | — | Número decimal exacto, normalmente ≥ 0. |
| 6 | `valorHoraBase` | decimal | — | Número decimal exacto, normalmente ≥ 0. |
| 7 | `nivelJerarquico` | texto | — | — |
| 8 | `normaOrigen` | texto | — | — |
| 9 | `fechaInicioVigencia` | fecha (AAAA-MM-DD) | — | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 10 | `fechaFinVigencia` | fecha (AAAA-MM-DD) | — | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 11 | `estado` | texto | — | Texto libre; valores de uso común: ACTIVO, INACTIVO, CERRADO. |
| 12 | `tipoRegimen` | texto | — | — |
| 13 | `puntosCategoria` | decimal | — | Número decimal exacto, normalmente ≥ 0. |
| 14 | `factorSalarialTiempoCompleto` | decimal | — | Número decimal exacto, normalmente ≥ 0. |
| 15 | `factorSalarialMedioTiempo` | decimal | — | Número decimal exacto, normalmente ≥ 0. |
| 16 | `unidadFactorSalarial` | texto | — | — |
| 17 | `requiereActoReconocimiento` | booleano (1/0) | — | 1 = verdadero, 0 = falso. |
| 18 | `actoReconocimiento` | texto | — | — |
| 19 | `fechaReconocimiento` | fecha (AAAA-MM-DD) | — | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 20 | `categoriaAnterior` | texto | — | — |
| 21 | `fechaAscenso` | fecha (AAAA-MM-DD) | — | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 22 | `esCategoriaPorDefecto` | booleano (1/0) | — | 1 = verdadero, 0 = falso. |
| 23 | `permiteReconocimientoCategoriaOrigen` | booleano (1/0) | — | 1 = verdadero, 0 = falso. |
| 24 | `evaluacionSatisfactoriaInstitucionOrigen` | booleano (1/0) | — | 1 = verdadero, 0 = falso. |

### FactorSalarial

| # | Atributo | Tipo | Ejemplo (UPC) | Validación / descripción |
|---|---|---|---|---|
| 1 | `idFactor` | entero | 1 | Identificador único de la entidad; entero mayor que 0. |
| 2 | `nombre` | texto | Título de Doctorado en Ciencias de la … | — |
| 3 | `tipoFactor` | enum TipoFactor | TITULO_ACADEMICO | Uno de: `TITULO_ACADEMICO`, `CATEGORIA_DOCENTE`, `EXPERIENCIA`, `PRODUCTIVIDAD_ACADEMICA`, `DIRECCION_ACADEMICO_ADMINISTRATIVA`, `DESEMPENO_DESTACADO`, `POSGRADO`, `GRUPO_INVESTIGACION`, `SEMILLERO`. |
| 4 | `cantidad` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 5 | `puntosReconocidos` | decimal | 120 | Número decimal exacto, normalmente ≥ 0. |
| 6 | `valorReconocido` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 7 | `fechaReconocimiento` | fecha (AAAA-MM-DD) | 2026-09-10 | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 8 | `actoAdministrativo` | texto | Resolución CIARP N° 045-2026 | — |
| 9 | `idProfesor` | entero | 1 | Referencia a **Profesor**; debe existir (integridad referencial). |
| 10 | `estado` | texto | APROBADO | Texto libre; valores de uso común: ACTIVO, INACTIVO, CERRADO. |
| 11 | `regimenAplicable` | texto | *(vacío)* | — |
| 12 | `factorGenerador` | texto | *(vacío)* | — |
| 13 | `tipoReconocimiento` | texto | *(vacío)* | — |
| 14 | `puntosSolicitados` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 15 | `puntosAprobados` | decimal | 120 | Número decimal exacto, normalmente ≥ 0. |
| 16 | `puntosAcumulables` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 17 | `topeIndividual` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 18 | `topePorCategoria` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 19 | `topeAnual` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 20 | `numeroAutores` | entero | *(vacío)* | — |
| 21 | `factorCoautoria` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 22 | `requiereEvaluacionPares` | booleano (1/0) | *(vacío)* | 1 = verdadero, 0 = falso. |
| 23 | `resultadoEvaluacionPares` | texto | *(vacío)* | — |
| 24 | `requiereAprobacionComite` | booleano (1/0) | *(vacío)* | 1 = verdadero, 0 = falso. |
| 25 | `fechaAprobacionComite` | fecha (AAAA-MM-DD) | *(vacío)* | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 26 | `actoReconocimiento` | texto | *(vacío)* | — |
| 27 | `fechaEfectoSalarial` | fecha (AAAA-MM-DD) | *(vacío)* | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 28 | `esConstitutivoSalario` | booleano (1/0) | *(vacío)* | 1 = verdadero, 0 = falso. |
| 29 | `integraBasePrestacional` | booleano (1/0) | *(vacío)* | 1 = verdadero, 0 = falso. |
| 30 | `integraBaseParafiscal` | booleano (1/0) | *(vacío)* | 1 = verdadero, 0 = falso. |
| 31 | `vigenciaDesde` | fecha (AAAA-MM-DD) | *(vacío)* | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 32 | `vigenciaHasta` | fecha (AAAA-MM-DD) | *(vacío)* | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |

### ProduccionAcademica

| # | Atributo | Tipo | Ejemplo (UPC) | Validación / descripción |
|---|---|---|---|---|
| 1 | `idProduccion` | entero | 1 | Identificador único de la entidad; entero mayor que 0. |
| 2 | `idProfesor` | entero | 1 | Referencia a **Profesor**; debe existir (integridad referencial). |
| 3 | `tipoProduccion` | texto | ARTICULO_A2 | — |
| 4 | `titulo` | texto | Optimizacion de Algoritmos en Grafos P… | — |
| 5 | `fechaPublicacion` | fecha (AAAA-MM-DD) | 2026-09-10 | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 6 | `entidadPublicadora` | texto | IEEE Transactions on Computers | — |
| 7 | `identificadorProducto` | texto | IEEE Transactions on Computers | — |
| 8 | `puntosSolicitados` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 9 | `puntosReconocidos` | decimal | 6.00 | Número decimal exacto, normalmente ≥ 0. |
| 10 | `fechaReconocimiento` | fecha (AAAA-MM-DD) | 2026-09-10 | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 11 | `actoAdministrativo` | texto | *(vacío)* | — |
| 12 | `estadoValidacion` | texto | VALIDADO | — |
| 13 | `modalidadProducto` | texto | *(vacío)* | — |
| 14 | `subtipoProducto` | texto | *(vacío)* | — |
| 15 | `nivelImpacto` | texto | *(vacío)* | — |
| 16 | `clasificacionRevista` | texto | *(vacío)* | — |
| 17 | `isbn` | texto | *(vacío)* | — |
| 18 | `issn` | texto | *(vacío)* | — |
| 19 | `registroDerechoAutor` | texto | *(vacío)* | — |
| 20 | `numeroPatente` | texto | *(vacío)* | — |
| 21 | `entidadIndexadora` | texto | *(vacío)* | — |
| 22 | `numeroAutores` | entero | 2 | — |
| 23 | `posicionAutor` | entero | *(vacío)* | — |
| 24 | `porcentajeParticipacion` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 25 | `creditoInstitucional` | booleano (1/0) | *(vacío)* | 1 = verdadero, 0 = falso. |
| 26 | `evaluadoPorPares` | booleano (1/0) | *(vacío)* | 1 = verdadero, 0 = falso. |
| 27 | `cantidadPares` | entero | *(vacío)* | — |
| 28 | `resultadoEvaluacion` | texto | *(vacío)* | — |
| 29 | `puntosTotalesProducto` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 30 | `factorCoautoria` | decimal | 0.5 | Número decimal exacto, normalmente ≥ 0. |
| 31 | `puntosReconocidosProfesor` | decimal | 6.00 | Número decimal exacto, normalmente ≥ 0. |
| 32 | `tipoReconocimiento` | texto | *(vacío)* | — |
| 33 | `fechaActoReconocimiento` | fecha (AAAA-MM-DD) | *(vacío)* | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 34 | `yaReconocidoOtroConcepto` | booleano (1/0) | *(vacío)* | 1 = verdadero, 0 = falso. |
| 35 | `productoReclasificado` | booleano (1/0) | *(vacío)* | 1 = verdadero, 0 = falso. |
| 36 | `puntosAdicionalesReclasificacion` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 37 | `fechaLimiteReclasificacion` | fecha (AAAA-MM-DD) | *(vacío)* | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |

## Nómina

### PeriodoNomina

| # | Atributo | Tipo | Ejemplo (UPC) | Validación / descripción |
|---|---|---|---|---|
| 1 | `idPeriodoNomina` | entero | 1 | Identificador único de la entidad; entero mayor que 0. |
| 2 | `anio` | entero | 2026 | — |
| 3 | `mes` | entero | 1 | — |
| 4 | `fechaInicio` | fecha (AAAA-MM-DD) | 2026-01-01 | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 5 | `fechaFin` | fecha (AAAA-MM-DD) | 2026-01-31 | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 6 | `fechaPago` | fecha (AAAA-MM-DD) | 2026-01-31 | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 7 | `estado` | texto | CERRADO | Solo se liquida en periodos ABIERTO; al cerrar se bloquean cambios directos (reliquidación por versiones). |
| 8 | `tipoPeriodicidad` | texto | MENSUAL | — |
| 9 | `salarioMinimoVigente` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 10 | `valorPuntoSalarialVigente` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 11 | `fechaVigenciaValorPunto` | fecha (AAAA-MM-DD) | *(vacío)* | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 12 | `resolucionValorPunto` | texto | *(vacío)* | — |
| 13 | `diasBaseLiquidacion` | entero | 30 | — |
| 14 | `fechaCorteNovedades` | fecha (AAAA-MM-DD) | *(vacío)* | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 15 | `fechaCierreNomina` | fecha (AAAA-MM-DD) | *(vacío)* | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 16 | `fechaAprobacion` | fecha (AAAA-MM-DD) | *(vacío)* | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 17 | `usuarioAprobador` | texto | *(vacío)* | — |
| 18 | `totalDevengadoPeriodo` | decimal | 15190265.00 | Número decimal exacto, normalmente ≥ 0. |
| 19 | `totalDescuentosPeriodo` | decimal | 1191723.00 | Número decimal exacto, normalmente ≥ 0. |
| 20 | `totalPrestacionesPeriodo` | decimal | 3684004.53 | Número decimal exacto, normalmente ≥ 0. |
| 21 | `totalAportesPatronalesPeriodo` | decimal | 1390363.19 | Número decimal exacto, normalmente ≥ 0. |
| 22 | `costoTotalPeriodo` | decimal | 13085349.72 | Número decimal exacto, normalmente ≥ 0. |
| 23 | `estaCerrado` | booleano (1/0) | 1 | 1 = verdadero, 0 = falso. |
| 24 | `permiteReliquidacion` | booleano (1/0) | *(vacío)* | 1 = verdadero, 0 = falso. |
| 25 | `versionLiquidacion` | entero | *(vacío)* | — |

### LiquidacionNomina

| # | Atributo | Tipo | Ejemplo (UPC) | Validación / descripción |
|---|---|---|---|---|
| 1 | `idLiquidacion` | entero | 1 | Identificador único de la entidad; entero mayor que 0. |
| 2 | `idProfesor` | entero | 1 | Referencia a **Profesor**; debe existir (integridad referencial). |
| 3 | `idContrato` | entero | 2 | Referencia a **Contrato**; debe existir (integridad referencial). |
| 4 | `idPeriodoNomina` | entero | 1 | Referencia a **PeriodoNomina**; debe existir (integridad referencial). |
| 5 | `fechaLiquidacion` | fecha (AAAA-MM-DD) | 2026-09-10 | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 6 | `salarioBase` | decimal | 1387592 | Número decimal exacto, normalmente ≥ 0. |
| 7 | `totalDevengado` | decimal | 1387592.00 | Número decimal exacto, normalmente ≥ 0. |
| 8 | `totalDescuentos` | decimal | 113775.00 | Número decimal exacto, normalmente ≥ 0. |
| 9 | `totalPrestaciones` | decimal | 513164.68 | Número decimal exacto, normalmente ≥ 0. |
| 10 | `baseLiquidacionPrestaciones` | decimal | 1387592.00 | Número decimal exacto, normalmente ≥ 0. |
| 11 | `baseCotizacionSeguridadSocial` | decimal | 1387592.00 | Número decimal exacto, normalmente ≥ 0. |
| 12 | `valorAuxilioTransporteCotizado` | decimal | 0.00 | Número decimal exacto, normalmente ≥ 0. |
| 13 | `aportePatronalSENA` | decimal | 0.00 | Número decimal exacto, normalmente ≥ 0. |
| 14 | `aportePatronalICBF` | decimal | 0.00 | Número decimal exacto, normalmente ≥ 0. |
| 15 | `netoPagar` | decimal | 1273817.00 | Número decimal exacto, normalmente ≥ 0. |
| 16 | `estado` | texto | PROCESADA | Texto libre; valores de uso común: ACTIVO, INACTIVO, CERRADO. |
| 17 | `tipoProfesorLiquidado` | enum TipoProfesor | PLANTA | Uno de: `PLANTA`, `OCASIONAL`, `CATEDRATICO`, `CATEDRATICO_AD_HONOREM`. |
| 18 | `regimenLiquidado` | texto | Decreto 1279 de 2002 | — |
| 19 | `categoriaLiquidada` | texto | *(vacío)* | — |
| 20 | `dedicacionLiquidada` | enum Dedicacion | TIEMPO_COMPLETO | Uno de: `TIEMPO_COMPLETO`, `MEDIO_TIEMPO`, `HORA_CATEDRA`. |
| 21 | `diasTrabajados` | decimal | 30 | Número decimal exacto, normalmente ≥ 0. |
| 22 | `diasNoRemunerados` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 23 | `horasAsignadas` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 24 | `horasCumplidas` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 25 | `horasIncumplidas` | decimal | 0 | Número decimal exacto, normalmente ≥ 0. |
| 26 | `salarioMinimoUsado` | decimal | 1750905 | Número decimal exacto, normalmente ≥ 0. |
| 27 | `valorPuntoUsado` | decimal | 23924 | Número decimal exacto, normalmente ≥ 0. |
| 28 | `valorHoraCatedraUsado` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 29 | `factorCategoriaUsado` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 30 | `puntosSalarialesUsados` | decimal | 58 | Número decimal exacto, normalmente ≥ 0. |
| 31 | `salarioOrdinario` | decimal | 1387592.00 | Número decimal exacto, normalmente ≥ 0. |
| 32 | `baseSalarialPrestacional` | decimal | 1387592.00 | Número decimal exacto, normalmente ≥ 0. |
| 33 | `baseSeguridadSocial` | decimal | 1387592.00 | Número decimal exacto, normalmente ≥ 0. |
| 34 | `baseParafiscales` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 35 | `bonificacionPosgrado` | decimal | 0.00 | Número decimal exacto, normalmente ≥ 0. |
| 36 | `bonificacionInvestigacion` | decimal | 0.00 | Número decimal exacto, normalmente ≥ 0. |
| 37 | `bonificacionesSalariales` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 38 | `bonificacionesNoSalariales` | decimal | 0.00 | Número decimal exacto, normalmente ≥ 0. |
| 39 | `otrosDevengadosSalariales` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 40 | `otrosDevengadosNoSalariales` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 41 | `ajustesDevengados` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 42 | `descuentoSalud` | decimal | 55500.00 | Número decimal exacto, normalmente ≥ 0. |
| 43 | `descuentoPension` | decimal | 55500.00 | Número decimal exacto, normalmente ≥ 0. |
| 44 | `fondoSolidaridadPensional` | decimal | 0 | Número decimal exacto, normalmente ≥ 0. |
| 45 | `retencionFuente` | decimal | 0 | Número decimal exacto, normalmente ≥ 0. |
| 46 | `descuentoHorasIncumplidas` | decimal | 0.00 | Número decimal exacto, normalmente ≥ 0. |
| 47 | `descuentoLibranza` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 48 | `descuentoEmbargo` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 49 | `otrosDescuentos` | decimal | 2775.00 | Número decimal exacto, normalmente ≥ 0. |
| 50 | `ajustesDescuentos` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 51 | `provisionCesantias` | decimal | 115632.67 | Número decimal exacto, normalmente ≥ 0. |
| 52 | `provisionInteresesCesantias` | decimal | 13875.92 | Número decimal exacto, normalmente ≥ 0. |
| 53 | `provisionPrimaServicios` | decimal | 115632.67 | Número decimal exacto, normalmente ≥ 0. |
| 54 | `provisionPrimaNavidad` | decimal | 117078.63 | Número decimal exacto, normalmente ≥ 0. |
| 55 | `provisionVacaciones` | decimal | 58358.36 | Número decimal exacto, normalmente ≥ 0. |
| 56 | `provisionPrimaVacaciones` | decimal | 52115.00 | Número decimal exacto, normalmente ≥ 0. |
| 57 | `bonificacionServiciosPrestados` | decimal | 40471.43 | Número decimal exacto, normalmente ≥ 0. |
| 58 | `aportePatronalSalud` | decimal | 117945.32 | Número decimal exacto, normalmente ≥ 0. |
| 59 | `aportePatronalPension` | decimal | 166511.04 | Número decimal exacto, normalmente ≥ 0. |
| 60 | `aporteRiesgosLaborales` | decimal | 7243.23 | Número decimal exacto, normalmente ≥ 0. |
| 61 | `aporteCajaCompensacion` | decimal | 55503.68 | Número decimal exacto, normalmente ≥ 0. |
| 62 | `otrosAportesPatronales` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 63 | `costoTotalEmpleador` | decimal | 2247959.95 | Número decimal exacto, normalmente ≥ 0. |
| 64 | `fechaGeneracion` | fecha (AAAA-MM-DD) | *(vacío)* | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 65 | `fechaAprobacion` | fecha (AAAA-MM-DD) | *(vacío)* | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 66 | `aprobada` | booleano (1/0) | *(vacío)* | 1 = verdadero, 0 = falso. |
| 67 | `pagada` | booleano (1/0) | *(vacío)* | 1 = verdadero, 0 = falso. |
| 68 | `fechaPago` | fecha (AAAA-MM-DD) | *(vacío)* | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 69 | `medioPago` | texto | *(vacío)* | — |
| 70 | `referenciaPago` | texto | *(vacío)* | — |
| 71 | `requiereReliquidacion` | booleano (1/0) | *(vacío)* | 1 = verdadero, 0 = falso. |
| 72 | `motivoReliquidacion` | texto | *(vacío)* | — |
| 73 | `liquidacionOrigen` | entero | *(vacío)* | — |
| 74 | `version` | entero | *(vacío)* | — |
| 75 | `usuarioLiquidador` | texto | *(vacío)* | — |
| 76 | `usuarioAprobador` | texto | *(vacío)* | — |
| 77 | `parametros_utilizados` | diccionario (texto) | {'PORCENTAJE_SALUD_TRABAJADOR': '0.04'… | Trazabilidad RF-14: códigos y valores usados. Se guarda como repr de diccionario Python (no portable a C++). |

### ConceptoNomina

| # | Atributo | Tipo | Ejemplo (UPC) | Validación / descripción |
|---|---|---|---|---|
| 1 | `idConcepto` | entero | — | Identificador único de la entidad; entero mayor que 0. |
| 2 | `codigo` | texto | — | — |
| 3 | `nombre` | texto | — | — |
| 4 | `tipoConcepto` | texto | — | — |
| 5 | `naturaleza` | texto | — | — |
| 6 | `formaCalculo` | texto | — | — |
| 7 | `porcentaje` | decimal | — | Número decimal exacto, normalmente ≥ 0. |
| 8 | `valorFijo` | decimal | — | Número decimal exacto, normalmente ≥ 0. |
| 9 | `baseCalculo` | texto | — | — |
| 10 | `aplicaA` | texto | — | — |
| 11 | `normaOrigen` | texto | — | — |
| 12 | `fechaInicioVigencia` | fecha (AAAA-MM-DD) | — | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 13 | `fechaFinVigencia` | fecha (AAAA-MM-DD) | — | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 14 | `estado` | texto | — | Texto libre; valores de uso común: ACTIVO, INACTIVO, CERRADO. |
| 15 | `codigoContable` | texto | — | — |
| 16 | `regimenAplicable` | texto | — | — |
| 17 | `modalidadProfesorAplicable` | texto | — | — |
| 18 | `categoriaAplicable` | texto | — | — |
| 19 | `dedicacionAplicable` | texto | — | — |
| 20 | `periodicidad` | texto | — | — |
| 21 | `esSalarial` | booleano (1/0) | — | 1 = verdadero, 0 = falso. |
| 22 | `esBonificacion` | booleano (1/0) | — | 1 = verdadero, 0 = falso. |
| 23 | `esDescuentoLey` | booleano (1/0) | — | 1 = verdadero, 0 = falso. |
| 24 | `esPrestacionSocial` | booleano (1/0) | — | 1 = verdadero, 0 = falso. |
| 25 | `esAportePatronal` | booleano (1/0) | — | 1 = verdadero, 0 = falso. |
| 26 | `integraBaseSalud` | booleano (1/0) | — | 1 = verdadero, 0 = falso. |
| 27 | `integraBasePension` | booleano (1/0) | — | 1 = verdadero, 0 = falso. |
| 28 | `integraBasePrestacional` | booleano (1/0) | — | 1 = verdadero, 0 = falso. |
| 29 | `integraBaseParafiscal` | booleano (1/0) | — | 1 = verdadero, 0 = falso. |
| 30 | `integraLiquidacionFinal` | booleano (1/0) | — | 1 = verdadero, 0 = falso. |
| 31 | `requiereActoAdministrativo` | booleano (1/0) | — | 1 = verdadero, 0 = falso. |
| 32 | `articuloOrigen` | texto | — | — |
| 33 | `prioridadCalculo` | entero | — | — |

### DetalleLiquidacion

| # | Atributo | Tipo | Ejemplo (UPC) | Validación / descripción |
|---|---|---|---|---|
| 1 | `idDetalleLiquidacion` | entero | 1 | Identificador único de la entidad; entero mayor que 0. |
| 2 | `idLiquidacion` | entero | 1 | Referencia a **LiquidacionNomina**; debe existir (integridad referencial). |
| 3 | `idConcepto` | entero | *(vacío)* | Referencia a **ConceptoNomina**; debe existir (integridad referencial). |
| 4 | `cantidad` | decimal | 1 | Número decimal exacto, normalmente ≥ 0. |
| 5 | `baseCalculo` | decimal | 1387592.00 | Número decimal exacto, normalmente ≥ 0. |
| 6 | `porcentajeAplicado` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 7 | `valorUnitario` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 8 | `valorCalculado` | decimal | 1387592.00 | Número decimal exacto, normalmente ≥ 0. |
| 9 | `observaciones` | texto | Salario Ordinario | — |
| 10 | `tipoMovimiento` | texto | SALARIO_ORDINARIO | — |
| 11 | `fechaCausacion` | fecha (AAAA-MM-DD) | *(vacío)* | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 12 | `periodoCausacion` | texto | 1 | — |
| 13 | `formulaAplicada` | texto | salarioOrdinario = IBC | — |
| 14 | `parametrosAplicados` | texto | *(vacío)* | — |
| 15 | `valorAntesAjuste` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 16 | `valorAjuste` | decimal | *(vacío)* | Número decimal exacto, normalmente ≥ 0. |
| 17 | `valorDefinitivo` | decimal | 1387592.00 | Número decimal exacto, normalmente ≥ 0. |
| 18 | `esSalarial` | booleano (1/0) | 1 | 1 = verdadero, 0 = falso. |
| 19 | `integraSeguridadSocial` | booleano (1/0) | 1 | 1 = verdadero, 0 = falso. |
| 20 | `integraPrestaciones` | booleano (1/0) | 1 | 1 = verdadero, 0 = falso. |
| 21 | `integraParafiscales` | booleano (1/0) | 1 | 1 = verdadero, 0 = falso. |
| 22 | `actoSoporte` | texto | *(vacío)* | — |
| 23 | `documentoSoporte` | texto | *(vacío)* | — |
| 24 | `usuarioRegistro` | texto | *(vacío)* | — |
| 25 | `fechaRegistro` | fecha (AAAA-MM-DD) | 2026-09-10 | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |

## Configuración

### ParametroNormativo

| # | Atributo | Tipo | Ejemplo (UPC) | Validación / descripción |
|---|---|---|---|---|
| 1 | `idParametro` | entero | 1 | Identificador único de la entidad; entero mayor que 0. |
| 2 | `codigo` | enum ParametroNormativoCodigo | SALARIO_MINIMO | Uno de: `SALARIO_MINIMO`, `VALOR_PUNTO_SALARIAL`, `VALOR_AUXILIO_TRANSPORTE_VIGENTE`, `PORCENTAJE_ARL_CLASE_I`, `PORCENTAJE_ARL_CLASE_II`, `PORCENTAJE_SENA`, `PORCENTAJE_ICBF`, `VALOR_HORA_CATEDRA`, `PORCENTAJE_SALUD_TRABAJADOR`, `PORCENTAJE_SALUD_EMPLEADOR`, `PORCENTAJE_PENSION_TRABAJADOR`, `PORCENTAJE_PENSION_EMPLEADOR`, `PORCENTAJE_FONDO_SOLIDARIDAD`, `PORCENTAJE_RIESGOS_LABORALES`, `PORCENTAJE_CAJA_COMPENSACION`, `TOPE_BONIFICACION_SERVICIOS`, `PORCENTAJE_BONIFICACION_SERVICIOS_HASTA_TOPE`, `PORCENTAJE_BONIFICACION_SERVICIOS_SOBRE_TOPE`, `PORCENTAJE_RETENCION_FUENTE`, `BASE_MINIMA_RETENCION_FUENTE`, `PORCENTAJE_ESTAMPILLA`, `RETENCION_FUENTE_SALARIO`, `NOTA_MINIMA_APROBATORIA`, `PROMEDIO_MINIMO_EBRA`, `MAXIMO_CREDITOS_PERIODO`, `APLICA_EXONERACION_LEY_1819`. |
| 3 | `nombre` | texto | Salario Mínimo Legal Vigente | — |
| 4 | `descripcion` | texto | SMMLV Colombia | — |
| 5 | `tipoDato` | texto | MONETARIO | — |
| 6 | `valor` | texto | 1750905 | Porcentuales: 0 a 1; monetarios: mayor que 0 (`GestorParametros`). |
| 7 | `unidad` | texto | COP | — |
| 8 | `normaOrigen` | texto | Decreto Nacional Salarial | — |
| 9 | `articulo` | texto | Art. 1 | — |
| 10 | `fechaInicioVigencia` | fecha (AAAA-MM-DD) | 2026-01-01 | No puede haber dos vigencias solapadas para el mismo código. |
| 11 | `fechaFinVigencia` | fecha (AAAA-MM-DD) | 2026-12-31 | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 12 | `aplicaA` | texto | TODOS | — |
| 13 | `estado` | texto | ACTIVO | Texto libre; valores de uso común: ACTIVO, INACTIVO, CERRADO. |

### ArchivoPersistencia

| # | Atributo | Tipo | Ejemplo (UPC) | Validación / descripción |
|---|---|---|---|---|
| 1 | `idArchivo` | entero | — | Identificador único de la entidad; entero mayor que 0. |
| 2 | `nombreArchivo` | texto | — | — |
| 3 | `ruta` | texto | — | — |
| 4 | `formato` | texto | — | — |
| 5 | `fechaCreacion` | fecha (AAAA-MM-DD) | — | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 6 | `fechaUltimaCarga` | fecha (AAAA-MM-DD) | — | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 7 | `fechaUltimoGuardado` | fecha (AAAA-MM-DD) | — | Formato ISO AAAA-MM-DD; si hay fecha final asociada, no puede ser anterior a la inicial. |
| 8 | `versionEstructura` | texto | — | — |
| 9 | `cantidadRegistros` | entero | — | — |
| 10 | `estado` | texto | — | Texto libre; valores de uso común: ACTIVO, INACTIVO, CERRADO. |
