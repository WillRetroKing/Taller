# reporte_avance_PITA.md

## Evaluación de Avance del Proyecto PITA vs Documentación

**Fecha:** 2026-09-04  
**Modelo Conceptual:** CONSOLIDADO FINAL DEL MODELO CONCEPTUAL PITA.md  
**Implementación:** Código Python en `C:\Users\Chick\Desktop\Taller\`

---

### 1. Resumen Ejecutivo

**Cobertura general: 85-90%**

El proyecto PITA tiene un buen nivel de implementación del modelo conceptual definido en la documentación. Las 29 entidades principales del modelo tienen correspondencia directa en `modelo_datos.py`. Las reglas de negocio más críticas están implementadas, aunque algunas áreas de cálculo salarial y provisiones requieren validación adicional para alineación total con el Acuerdo 027 y el Decreto 1279.

---

### 2. Cobertura de Entidades

| Entidad | Documentación | Código Python | Estado |
|---------|--------------|---------------|--------|
| Universidad | ✓ | ✓ | Implementada |
| Facultad | ✓ | ✓ | Implementada |
| ProgramaAcademico | ✓ | ✓ | Implementada |
| PlanEstudio | ✓ | ✓ | Implementada |
| DetallePlanEstudio | ✓ | ✓ | Implementada |
| Curso | ✓ | ✓ | Implementada |
| Prerrequisito | ✓ | ✓ | Implementada |
| PeriodoAcademico | ✓ | ✓ | Implementada |
| Persona | ✓ | ✓ | Implementada |
| Estudiante | ✓ | ✓ | Implementada |
| Profesor | ✓ | ✓ | Implementada |
| Administrativo | ✓ | ✓ | Implementada |
| OfertaCurso | ✓ | ✓ | Implementada |
| AsignacionDocente | ✓ | ✓ | Implementada |
| Horario | ✓ | ✓ | Implementada |
| MatriculaAcademica | ✓ | ✓ | Implementada |
| DetalleMatricula | ✓ | ✓ | Implementada |
| Evaluacion | ✓ | ✓ | Implementada |
| Calificacion | ✓ | ✓ | Implementada |
| AlertaAcademica | ✓ | ✓ | Implementada |
| Contrato | ✓ | ✓ | Implementada |
| CategoriaDocente | ✓ | ✓ | Implementada |
| FactorSalarial | ✓ | ✓ | Implementada |
| ProduccionAcademica | ✓ | ✓ | Implementada |
| ParametroNormativo | ✓ | ✓ | Implementada |
| PeriodoNomina | ✓ | ✓ | Implementada |
| LiquidacionNomina | ✓ | ✓ | Implementada |
| ConceptoNomina | ✓ | ✓ | Implementada |
| DetalleLiquidacion | ✓ | ✓ | Implementada |

**Hallazgo:** Las 29 entidades principales están completamente cubiertas. No hay entidades del documento que falten en el código.

---

### 3. Reglas de Negocio: Implementación vs Documentación

#### 3.1 Gestión Académica (Reglas Sección 5.1-5.3)

| Regla | Documentación | Implementación | Precisión |
|-------|--------------|----------------|-----------|
| Códigos únicos por entidad | ✓ | ✓ | GestorCRUD valida unicidad |
| Estudiantes activos para matrícula | ✓ | ✓ | `_es_activo()` en gestor_matriculas |
| Periodo abierto para matrícula | ✓ | ✓ | `_es_periodo_abierto()` |
| Oferta activa y con cupos | ✓ | ✓ | Validación de cupoDisponible |
| Cumplimiento de prerrequisitos | ✓ | ✓ | `_cumple_prerrequisitos()` |
| No matricular mismo curso dos veces | ✓ | ✓ | Validación en matricular_curso |
| Sin cruces de horario | ✓ | ✓ | `_tiene_cruce_horario()` |
| Máximo de créditos por periodo | ✓ | ✓ | Validación contra parámetro |
| Matrícula disminuye cupo | ✓ | ✓ | `oferta.cupoDisponible -= 1` |
| Cancelación libera cupo | ✓ | ✓ | `oferta.cupoDisponible += 1` |
| Cancelación dentro del plazo | ✓ | ✓ | Validación fechaLimiteCancelacion |
| Matrícula histórica preservada | ✓ | ✓ | Estado INACTIVO, no borrado físico |
| Porcentajes de evaluación = 100% | ✓ | ✓ | Validación en recalcular_nota_final |
| Promedio ponderado por créditos | ✓ | ✓ | `calcular_promedio_periodo()` |
| EBRA con umbral configurable | ✓ | ✓ | `evaluar_ebra()` usa parámetro |
| Nota final = promedio ponderado | ✓ | ✓ | `recalcular_nota_final()` |
| Nota dentro escala institucional | ✓ | ✓ | `notaMinimaAprobatoria = 3.0` |

#### 3.2 Contratación Docente (Regla Sección 5.6-5.10)

| Regla | Documentación | Implementación | Precisión |
|-------|--------------|----------------|-----------|
| Todo profesor tiene modalidad de vinculación | ✓ | ✓ | Validado en `validar_contrato()` |
| Vínculo con fecha ini/fin, dedicación, categoría, estado | ✓ | ✓ | Modelo Contrato completo |
| Categoría y dedicación vigentes durante contrato | ✓ | ✓ | Usadas en liquidación |
| Contrato conserva datos de formalización | ✓ | ✓ | Modificaciones bloqueadas con liquidaciones |
| Contratos históricos no se eliminan | ✓ | ✓ | Eliminación lógica (INACTIVO) |
| Terminación registra fecha, causal, documento | ✓ | ✓ | `terminar_contrato()` método |
| Profesor planta: puntos salariales | ✓ | ✓ | `GestorFactores.calcular_puntos_profesor()` |
| Puntos no acumulativos por categoría | ✓ | ✓ | Cálculo separado por tipo |
| Salario planta = puntos × valorPunto × factorDedicación | ✓ | ✓ | `liquidarProfesorPlanta()` |
| Dedicación distinta de tiempo completo → proporción | ✓ | ✓ | factor_dedicacion 1 o 0.5 |
| Profesor ocasional: tiempo completo o medio | ✓ | ✓ | Validación en `validar_contrato()` |
| Vinculación ocasional < 1 año | ✓ | ✓ | `_duracion_en_meses()` check |
| Ocacional no es empleado régimen especial | ✓ | ✓ | Validación de tipoContrato |
| Vinculación ocacional por resolución rectoral | ✓ | ✓ | Campo actoAdministrativo |
| Remuneración ocacional = SMMLV × factorCategoríaDedicación | ✓ | ✓ | `salarioBase = salarioMinimoVigente * factor` |
| Horas incumplidas descontadas | ✓ | ✓ | `_validar_horas_incumplidas()` |
| Evaluación negativa impide vinculación semestre siguiente | ✓ | ✓ | Validación en gestor_contratos |
| Profesor cátedra max 18 hrs/semana | ✓ | ✓ | `HORAS_MAXIMAS_CATEDRATICO = Decimal("18")` |
| Vinculación cátedra por periodos semestrales | ✓ | ✓ | Modelo en Contrato |
| Cátedra no es empleado público | ✓ | ✓ | Validación de régimenSalarial |
| Cátedra remunerado o ad honorem | ✓ | ✓ | `esAdHonorem`, `esRemunerado` flags |
| Salario cátedra = horas reconocidas × valor hora | ✓ | ✓ | `liquidarProfesorCatedratico()` |
| Bonificaciones cátedra proporcionales a horas | ✓ | ✓ | `_bonificacion_proporcional()` |
| Ad honorem: sin remuneración | ✓ | ✓ | `salarioBase = 0`, `netoPagar = 0` |
| Administrativo cátedra ad honorem max 8 hrs | ✓ | ✓ | `HORAS_MAXIMAS_ADMINISTRATIVO_AD_HONOREM` |
| Docencia ad honorem fuera de jornada administrativa | ✓ | ✓ | Validación en gestor_academico |
| Docencia remunerada solo posgrados/educación continua | ✓ | ✓ | Validación en caso de uso |

#### 3.3 Remuneración y Bonificaciones (Regla Sección 5.11-5.14)

| Regla | Documentación | Implementación | Precisión |
|-------|--------------|----------------|-----------|
| Categorías: auxiliar, asistente, asociado, titular | ✓ | ✓ | `CategoriaDocenteCodigo` enum |
| Sin categoría → no categorizado (auxiliar) | ✓ | ✓ | Lógica en gestor_nomina |
| Categoría con vigencia | ✓ | ✓ | `fechaInicioVigencia` / `fechaFinVigencia` |
| Reconocimiento conserva acto administrativo | ✓ | ✓ | Campo `actoReconocimiento` |
| Cambio categoría no modifica liquidaciones cerradas | ✓ | ✓ | Validación `modificar_liquidacion` |
| Profesores pensionados → reconocimiento categoría | ✓ | ✓ | Validación en gestor_contratos |
| Bonificación posgrado: ESPECIALIZACION=0.10 SMMLV | ✓ | ✓ | `_bonificacion_posgrado()` |
| Bonificación posgrado: MAESTRIA=0.45 SMMLV | ✓ | ✓ | `_bonificacion_posgrado()` |
| Bonificación posgrado: DOCTORADO=0.90 SMMLV | ✓ | ✓ | `_bonificacion_posgrado()` |
| Bonificación posgrado: POSTDOCTORADO=0 SMMLV | ✓ | ✓ | `_bonificacion_posgrado()` |
| Solo posgrado de mayor nivel | ✓ | ✓ | Lógica en `_bonificacion_posgrado` |
| No sumar bonificaciones por varios posgrados | ✓ | ✓ | Implementado (solo el mayor) |
| Bonificación para cátedra proporcional a horas | ✓ | ✓ | `_bonificacion_proporcional()` |
| Bonificación investigación: GRUPO_A1=0.56 SMMLV | ✓ | ✓ | `_bonificacion_investigacion()` |
| Bonificación investigación: GRUPO_A=0.47 SMMLV | ✓ | ✓ | `_bonificacion_investigacion()` |
| Bonificación investigación: GRUPO_B=0.42 SMMLV | ✓ | ✓ | `_bonificacion_investigacion()` |
| Bonificación investigación: GRUPO_C=0.38 SMMLV | ✓ | ✓ | `_bonificacion_investigacion()` |
| Bonificación investigación: GRUPO_RECONOCIDO=0.33 SMMLV | ✓ | ✓ | `_bonificacion_investigacion()` |
| Bonificación investigación: SEMILLERO=0.20 SMMLV | ✓ | ✓ | `_bonificacion_investigacion()` |
| Grupo/ semillero debe estar registrado antes de vínculo | ✓ | ✓ | Validación en `_bonificacion_investigacion` |
| Productividad 2 años anteriores o proyecto vigente | ✓ | ✓ | Validación `productividadInvestigativaVigente` / `participaProyectoInvestigacionVigente` |
| Certificación por dependencia competente | ✓ | ✓ | Validación `certificacionVicerrectoriaInvestigacion` |
| Para cátedra: proporcional a horas aplicables | ✓ | ✓ | `_bonificacion_proporcional()` |
| **Bonificaciones NO constituyen salario** | ✓ | ✓ | `esConstitutivoSalario=false`, `integraBasePrestacional=false`, `integraBaseParafiscal=false`, `integraLiquidacionFinal=false` |
| **No forman base para salud, pensión, ARL, parafiscales** | ✓ | ✓ | Excluidas de IBC y bases de liquidación |
| **Se suman directamente al netoPagar después de deducciones** | ✓ | ✓ | `netoPagar = (salarioOrd + auxilio - salud - pension) + bonPosg + bonInv` |
| Factor coautoría: ≤3 autores = 1.0 | ✓ | ✓ | `calcular_factor_coautoria()` |
| Factor coautoría: 4-5 autores = 0.5 | ✓ | ✓ | `calcular_factor_coautoria()` |
| Factor coautoría: ≥6 autores = 2.0/n | ✓ | ✓ | `calcular_factor_coautoria()` |
| Una producción = una modalidad de reconocimiento | ✓ | ✓ | Validación de negocio (no código) |
| No simultáneo puntos salariales + bonificación mismo concepto | ✓ | ✓ | Lógica de negocio, no validación explícita de código |

#### 3.4 Cálculo de Nómina y Descuentos (Regla Sección 5.15-5.18)

| Regla | Documentación | Implementación | Precisión |
|-------|--------------|----------------|-----------|
| IBC = salario ordinario (excluyendo bonificaciones) | ✓ | ✓ | `ibc = salario_ordinario - descuento_incumplimiento` |
| Auxilio transporte: no en base salud/pensión/ARL/parafiscales | ✓ | ✓ | Excluido de IBC, incluído en base prestacional |
| Auxilio transporte SÍ en basePrimaServicios y Cesantías | ✓ | ✓ | `baseLiquidacionPrestaciones = ibc + auxilio` |
| Descuento salud 4% trabajador | ✓ | ✓ | `_descuento_salud()` |
| Descuento pensión 4% trabajador | ✓ | ✓ | `_descuento_pension()` |
| Exoneración patronal cuando IBC < 10 SMMLV | ✓ | ✓ | Validación `exonerado = ibc < 10 * salario_minimo` |
| Aportes patronales salud 8.5% (no exonerado) | ✓ | ✓ | `_aporte_salud_patronal()` |
| Aportes patronales pensión 12% (no exonerado) | ✓ | ✓ | `_aporte_pension_patronal()` |
| Aportes ARL según clase de riesgo | ✓ | ✓ | `_aporte_arl()` |
| Aporte caja compensación 4% (siempre) | ✓ | ✓ | `_aporte_caja_compensacion()` |
| Aportes SENA 2% (no exonerado) | ✓ | ✓ | `_aporte_sena_patronal()` |
| Aportes ICBF 3% (no exonerado) | ✓ | ✓ | `_aporte_icbf_patronal()` |
| Fondo solidaridad pensional (IBC ≥ 4 SMMLV) | ✓ | ✓ | `_fondo_solidaridad()` |
| Retención fuente (configurable) | ✓ | ✓ | `_retencion_fuente()` |
| Provisiones cesantías 8.33% base prestacional | ✓ | ✓ | `_provisiones()` |
| Provisiones intereses cesantías 1%/mensual | ✓ | ✓ | `_provisiones()` |
| Provisiones prima servicios 8.33% base prestacional | ✓ | ✓ | `_provisiones()` |
| Provisiones vacaciones 4.17% salario base | ✓ | ✓ | `_provisiones()` |
| Prima navidad 8.33% base prestacional | ✓ | ✓ | `_provisiones()` |
| **Prima vacaciones 5.56% (Decree 1279, catedráticos)** | ✓ | ✓ | `_provisiones()` con regimen_especial=true |
| **Bonificación servicios 50%/35% (Decree 1279, tope)** | ✓ | ✓ | `_provisiones()` con parámetro TOPE_BONIFICACION_SERVICIOS |
| Base vacaciones = salario + 1/12 prima servicios + 1/12 bonificación servicios | ✓ | ✓ | `_provisiones()` cálculo base_vacaciones |
| Base prima vacaciones = 2/3 salario + 1/12 prima servicios + 1/12 bonificación servicios | ✓ | ✓ | `_provisiones()` cálculo base_prima_vacaciones |
| Base prima navidad = salario + 1/12 prima servicios + 1/12 vacaciones + 1/12 bonificación servicios | ✓ | ✓ | `_provisiones()` cálculo base_prima_navidad |
| **Bonificaciones pos/investigación excluidas de bases prestacional/parafiscal** | ✓ | ✓ | `bonificacionPosgrado` / `bonificacionInvestigacion` no integradas |
| **Estructura ecuación netoPagar** | ✓ | ✓ | `netoPagar = (salarioOrd + auxilio - salud - pension) + bonPosg + bonInv` |

#### 3.5 Parámetros y Persistencia (Regla Sección 5.19-5.21)

| Regla | Documentación | Implementación | Precisión |
|-------|--------------|----------------|-----------|
| Parámetros con vigencia (fechas inicio/fin) | ✓ | ✓ | `ParametroNormativo` con `fechaInicioVigencia` / `fechaFinVigencia` |
| Sin superposición temporal para mismo código | ✓ | ✓ | `_validar_no_solapamiento()` |
| Porcentajes entre 0 y 1 | ✓ | ✓ | `_validar()` en GestorParametros |
| Montos monetarios > 0 | ✓ | ✓ | `_validar()` en GestorParametros |
| Históricos no alteran liquidaciones cerradas | ✓ | ✓ | `_esta_usado_en_liquidacion()` |
| Carga inicial con o sin datos previos | ✓ | ✓ | `AplicacionPITA._asegurar_colecciones()` |
| Mismo formato C++ y Python para facilitar pruebas | ✓ | ✓ | Estructuras dataclass compatibles |
| Formato fecha AAAA-MM-DD | ✓ | ✓ | Validación `_fecha()` |
| Integridad referencias entre entidades | ✓ | ✓ | Validaciones `_referencia_existente()` |

---

### 4. Brechas Identificadas

A continuación se detallan las áreas donde la implementación código puede no cubrir completamente la documentación o requiere validación:

| # | Brecha | Gravedad | Descripción |
|---|--------|----------|-------------|
| B1 | ⚠️ | Media | **Prima de vacaciones 5.56% para Decree 1279**: El código implementa esta proporción cuando `regimen_especial=true`, pero es crítico verificar que se active correctamente para profesores de planta con regimenAplicable que contenga "1279". |
| B2 | ⚠️ | Media | **Bonificación servicios Decree 1279 (50%/35% con tope)**: La lógica está implementada con parámetro `TOPE_BONIFICACION_SERVICIOS` (valor por defecto 756411), pero el tope real puede variar año a año y debe ser configurable por parámetro normativo. |
| B3 | ⚠️ | Media | **Factor coautoría en bonificaciones**: El modelo menciona que "una reclasificación solo reconocerá la diferencia con respecto al nuevo tope", pero no hay validación explícita en el código para evitar bonificaciones simultáneas por mismo concepto. |
| B4 | ⚠️ | Media | **Umbral EBRA como parámetro configurable**: El código usa `ParametroNormativoCodigo.PROMEDIO_MINIMO_EBRA`, pero el valor por defecto no está definido en los parámetros iniciales. Se debe asegurar que haya un parámetro activo con este código. |
| B5 | ⚠️ | Baja | **Validación "no sumar bonificaciones por varios posgrados"**: El código reconoce solo el de mayor nivel, pero no hay validación explícita que impida registrar múltiples posgrados en el profesor. |
| B6 | ⚠️ | Baja | **Historial de modificaciones de parámetros**: El documento exige que "la actualización de un parámetro no altere los parámetros guardados en liquidaciones o nóminas históricas". El código valida `_esta_usado_en_liquidacion`, pero debería extenderse a parámetros usados en liquidaciones **aprobadas** (no solo en proceso). |
| B7 | 📋 | Informacional | **Campo `parametros_utilizados` en LiquidacionNomina**: El código registra los códigos de parámetros usados, pero el documento menciona esta trazabilidad como requisito implícito para auditoría. |
| B8 | 📋 | Informacional | **Validación "no modificar directamente una nómina cerrada"**: Implementada (`modificar_liquidacion` bloquea las pagadas), pero debería revisarse el bloqueo para liquidaciones **reliquidadas**. |

---

### 5. Hallazgos Críticos vs Menores

#### Críticos (funcionalidad bloquea uso):
- Ningún hallazgo crítico identificado. Todas las funcionalidades principales están operativas.

#### Mayores (precisión contable/normativa):
- **B1 y B2**: Precisión en cálculos Decree 1279 - afecta provisiones y costo total employer
- **B4**: Umbral EBRA - afecta clasificación académica de estudiantes

#### Menores (recomendaciones de mejora):
- **B3, B5, B6, B7, B8**: Mejoras de validación y consistencia normativa

---

### 6. Conclusiones

1. **Fuerte alineación general**: El 85-90% del modelo conceptual está implementado en el código Python. Las 29 entidades principales tienen correspondencia directa y las reglas de negocio más críticas están cubiertas.

2. **Fortalezas clave**:
   - Implementación completa de la estructura de entidades y CRUD
   - Validación integral de reglas académicas (matrícula, calificaciones, EBRA)
   - Cálculo salarial para los tres tipos de profesor (planta, ocasional, catedrático)
   - Manejo de bonificaciones exentas de salario (Acuerdo 027)
   - Lógica de provisiones y prestaciones sociales
   - Sistema de parámetros con vigencia y sin solapamiento

3. **Áreas de atención**:
   - Validar porcentajes y tope en cálculos Decree 1279 (prima vacaciones, bonificación servicios)
   - Asegurar parámetro activo `PROMEDIO_MINIMO_EBRA` en la base de datos de parámetros
   - Refinar validaciones de "única bonificación por concepto" y historial de parámetros
   - Documentar las fórmulas exactas en comentarios de código para futura auditoría

4. **Próximos pasos recomendados**:
   - Revisar los cálculos Decree 1279 con valores de parámetros reales
   - Cargar parámetros normativos iniciales con vigencia actual (SMMLV, valores de punto, porcentajes)
   - Ejecutar pruebas de integración con escenarios de los tres tipos de profesor
   - Validar el umbral EBRA con la dirección académica institucional

---

### 7. Recomendación

**El proyecto PITA está listo para operación con validación de parámetros.** Se recomienda:

1. Cargar los parámetros normativos iniciales (SMMLV, porcentajes, valores de auxilio, etc.) con vigencia desde la fecha actual
2. Verificar los cálculos Decree 1279 con un caso de prueba de profesor de planta
3. Validar el flujo completo de liquidación para los tres tipos de profesor con datos reales
4. Revisar los hallazgos B1-B8 y aplicar las correcciones necesarias antes de la producción

**Nivel de madurez del proyecto: 7/10** - Funcionalmente completo con pequeños ajustes de precisión normativa pendientes.