CONSOLIDADO FINAL DEL MODELO CONCEPTUAL PITA 

1. Alcance definitivo 

El Programa Integrado de Transacciones Académicas, PITA, debe permitir: 

- Gestionar facultades y programas académicos. 
- Gestionar cursos, estudiantes, profesores y administrativos. 
- Gestionar periodos académicos y ofertas de cursos. 
- Matricular y cancelar cursos. 
- Registrar calificaciones. 
- Calcular promedios académicos. 
- Generar alertas cuando un estudiante se encuentre en EBRA. 
- Gestionar categorías y tipos de contratación. 
- Calcular la nómina de profesores de planta, ocasionales y catedráticos. 
- Aplicar descuentos de salud, pensión y demás conceptos configurados. 
- Calcular prestaciones sociales cuando correspondan. 
- Crear, incluir, consultar, modificar, desactivar y eliminar registros. 
- Guardar y cargar la información desde archivos. 
- Permitir que el usuario inicie el programa con datos cargados o sin datos previos.  ![ref1]
2. Entidades definitivas 
1. Entidades institucionales 
1. Universidad 
1. Facultad 
1. ProgramaAcademico 
1. PlanEstudio 
1. DetallePlanEstudio 
1. Curso 
1. Prerrequisito 
8. PeriodoAcademico 
2. Entidades de personas 
   1. Persona 
   1. Estudiante 
   1. Profesor 
   1. Administrativo 
2. Entidades académicas 
   1. OfertaCurso 
   1. AsignacionDocente 
   1. Horario 
   1. MatriculaAcademica 
   1. DetalleMatricula 
   1. Evaluacion 
   1. Calificacion 
   1. AlertaAcademica 
2. Entidades de contratación docente 
   1. Contrato 
   1. CategoriaDocente 
   1. FactorSalarial 
   1. ProduccionAcademica 
2. Entidades de nómina docente 
   1. PeriodoNomina 
   1. LiquidacionNomina 
   1. ConceptoNomina 
   1. DetalleLiquidacion 
2. Entidades de configuración y persistencia 
1. ParametroNormativo 
2. ArchivoPersistencia 

Estas entidades cubren las estructuras académicas, las personas, la contratación, la nómina y la persistencia exigidas por el taller. Las entidades de contratación y nómina permiten diferenciar las reglas aplicables a profesores de planta, ocasionales, catedráticos remunerados y catedráticos ad honorem. ![ref2]

3. Atributos definitivos 
1. Universidad \
   Universidad 
   1. idUniversidad 
   1. nombre 
   1. nit 
   1. codigoInstitucional 
   1. direccion 
   1. ciudad 
   1. departamento 
   1. telefono 
   1. correoInstitucional 
   1. sitioWeb 
   1. estado ![ref3]
1. Facultad \
   Facultad 
- idFacultad 
- codigoFacultad 
- nombre 
- descripcion 
- ubicacion 
- telefono 
- correo 
- idDecano 
- fechaCreacion 
- estado ![ref2]
3. ProgramaAcademico \
   ProgramaAcademico 
   1. idPrograma 
   1. codigoPrograma 
   1. nombre 
   1. nivelFormacion 
   1. modalidad 
   1. numeroSemestres 
   1. totalCreditos 
   1. registroCalificado 
   1. fechaCreacion 
   1. idDirector 
   1. idFacultad 
   1. estado ![ref3]
3. PlanEstudio \
   PlanEstudio 
- idPlanEstudio 
- codigo 
- nombre 
- version 
- fechaInicioVigencia 
- fechaFinVigencia 
- totalCreditos 
- idPrograma 
- estado ![ref4]
5. DetallePlanEstudio \
   DetallePlanEstudio 
   1. idDetallePlan 
   1. idPlanEstudio 
   1. idCurso 
   1. semestreSugerido 
   1. tipoCurso 
   1. numeroCreditos 
   1. esObligatorio 
   1. estado ![ref1]
5. Curso 

   Curso 

- idCurso 
- codigoCurso 
- nombre 
- descripcion 
- numeroCreditos 
- horasTeoricas 
- horasPracticas 
- horasTrabajoIndependiente 
- cupoSugerido 
- notaMinimaAprobatoria 
- estado ![ref2]
7. Prerrequisito \
   Prerrequisito 
   1. idPrerrequisito 
   1. idCurso 
   1. idCursoRequerido 
   1. tipoRequisito 
   1. notaMinima 
   1. creditosMinimos 
   1. estado ![ref1]
7. PeriodoAcademico \
   PeriodoAcademico 
- idPeriodo 
- codigo 
- nombre 
- anio 
- numeroPeriodo 
- fechaInicio 
- fechaFin 
- fechaInicioMatricula 
- fechaFinMatricula 
- fechaLimiteCancelacion 
- estado ![ref5]
9. Persona \
   Persona 
- idPersona 
- tipoDocumento 
- numeroDocumento 
- primerNombre 
- segundoNombre 
- primerApellido 
- segundoApellido 
- fechaNacimiento 
- direccion 
- telefono 
- correoPersonal 
- correoInstitucional 
- ciudadResidencia 
- fechaRegistro 
- estado 

Persona concentra la información común para evitar duplicación en estudiantes, profesores y administrativos. ![ref6]

10. Estudiante \
    Estudiante 
- idEstudiante 
- idPersona 
- codigoEstudiante 
- idPrograma 
- idPlanEstudio 
- fechaIngreso 
- semestreActual 
- creditosAprobados 
- promedioAcumulado 
- estadoAcademico 
- estado 

Estados académicos 

ASPIRANTE 

ADMITIDO 

MATRICULADO 

ACTIVO 

INACTIVO 

RESERVA\_CUPO 

EBRA 

GRADUADO 

RETIRADO 

SUSPENDIDO ![ref3]

11. Profesor \
    Profesor 
- idProfesor 
- idPersona 
- codigoProfesor 
- idProgramaPrincipal 
- fechaVinculacion 
- tipoProfesor 
- categoriaDocente 
- dedicacion 
- maximoNivelEstudio 
- tituloProfesional 
- areaConocimiento 
- numeroHorasSemanales 
- puntosSalariales 
- estado 
- regimenSalarial 
- modalidadVinculacion 
- perteneceCarreraDocente 
- fechaIngresoCarreraDocente 
- fechaPosesion 
- fechaUltimaVinculacion 
- fechaRetiro 
- motivoRetiro 
- actoAdministrativoIngreso 
- actoAdministrativoRetiro 
- evaluacionDesempenoAnterior 
- puedeSerVinculadoSiguientePeriodo 
- idCategoriaDocente 
- categoriaReconocida 
- categoriaInstitucionOrigen 
- fechaReconocimientoCategoria 
- actoReconocimientoCategoria 
- categoriaComoInvestigador 
- grupoInvestigacion 
- categoriaGrupoInvestigacion 
- perteneceSemillero 
- semilleroInvestigacion 
- productividadInvestigativaVigente 
- participaProyectoInvestigacionVigente 
- certificacionVicerrectoriaInvestigacion 
- nivelPosgradoReconocido 
- tituloPosgradoReconocido 
- fechaObtencionPosgrado 
- tituloConvalidado 
- numeroResolucionConvalidacion 
- esEspecializacionClinica 
- posgradoRelacionadoConAreaDesempeno 
- factorBonificacionPosgrado 
- fechaInicioReconocimientoPosgrado 
- fechaFinReconocimientoPosgrado 
- aniosExperienciaDocenteUniversitaria 
- periodosExperienciaDocenteUniversitaria 
- aniosExperienciaInvestigacion 
- aniosExperienciaProfesional 
- aniosExperienciaDireccionAcademica 
- experienciaEquivalenteTiempoCompleto 
- experienciaCertificada 
- fechaCorteExperiencia 
- puntosExperienciaReconocidos 

Tipos de profesor 

PLANTA 

OCASIONAL 

CATEDRATICO 

CATEDRATICO\_AD\_HONOREM 

Dedicaciones 

TIEMPO\_COMPLETO 

MEDIO\_TIEMPO 

HORA\_CATEDRA 

Los profesores ocasionales y catedráticos no pertenecen a la carrera docente ni están sometidos al régimen salarial especial del Decreto 1279. Su vinculación y remuneración se rigen por las normas internas de la Universidad. ![ref7]

12. Administrativo \
    Administrativo 
- idAdministrativo 
- idPersona 
- codigoEmpleado 
- cargo 
- dependencia 
- categoria 
- tipoContratacion 
- fechaVinculacion 
- salarioBase 
- estado ![ref5]
13. OfertaCurso \
    OfertaCurso 
    1. idOfertaCurso 
    1. idCurso 
    1. idPeriodo 
    1. grupo 
    1. cupoMaximo 
    1. cupoDisponible 
    1. modalidad 
    1. aula 
    1. sede 
    1. fechaInicio 
    1. fechaFin 
    1. estado ![ref3]
13. AsignacionDocente \
    AsignacionDocente 
- idAsignacion 
- idProfesor 
- idOfertaCurso 
- rolDocente 
- numeroHoras 
- porcentajeResponsabilidad 
- fechaAsignacion 
- estado ![ref5]
15. Horario \
    Horario 
    1. idHorario 
    1. idOfertaCurso 
    1. diaSemana 
    1. horaInicio 
    1. horaFin 
    1. aula 
    1. sede 
    1. tipoSesion 
    1. estado ![ref1]
15. MatriculaAcademica \
    MatriculaAcademica 
- idMatricula 
- idEstudiante 
- idPeriodo 
- fechaMatricula 
- totalCreditos 
- promedioPeriodo 
- estadoMatricula 
- observaciones ![](Aspose.Words.88732198-408d-4729-9f4d-b7417c864c2e.008.png)
17. DetalleMatricula \
    DetalleMatricula 
    1. idDetalleMatricula 
    1. idMatricula 
    1. idOfertaCurso 
    1. fechaInscripcion 
    1. estadoCurso 
    1. notaFinal 
    1. numeroFallas 
    1. fechaCancelacion 
    1. motivoCancelacion \
       Estados posibles \
       MATRICULADO \
       EN\_CURSO \
       CANCELADO \
       APROBADO \
       REPROBADO \
       RETIRADO \
       HOMOLOGADO \
       VALIDADO ![ref3]
17. Evaluacion \
    Evaluacion 
- idEvaluacion 
- idOfertaCurso 
- nombre 
- tipo 
- porcentaje 
- fechaProgramada 
- descripcion 
- estado ![ref2]
19. Calificacion \
    Calificacion 
    1. idCalificacion 
    1. idEvaluacion 
    1. idDetalleMatricula 
    1. nota 
    1. fechaRegistro 
    1. observacion 
    1. estado ![ref1]
19. AlertaAcademica \
    AlertaAcademica 
- idAlerta 
- idEstudiante 
- idPeriodo 
- tipoAlerta 
- motivo 
- valorObservado 
- valorLimite 
- fechaGeneracion 
- atendida 
- observaciones 
- estado ![ref5]
21. Contrato 

Contrato 

- idContrato 
- idPersona 
- numeroContrato 
- tipoContrato 
- fechaInicio 
- fechaFin 
- dedicacion 
- horasSemanales 
- horasCatedra 
- valorHora 
- aplicaAuxilioTransporte 
- salarioBase 
- claseARL 
- actoAdministrativo 
- observaciones 
- estado 
- regimenAplicable 
- normaVinculacion 
- articuloNormativo 
- modalidadProfesor 
- esEmpleadoPublicoDocente 
- perteneceCarreraProfesoral 
- esTransitorio 
- esRemunerado 
- esAdHonorem 
- tipoDedicacion 
- porcentajeDedicacion 
- duracionEnMeses 
- periodoAcademicoInicial 
- periodoAcademicoFinal 
- tipoActoVinculacion 
- numeroActoVinculacion 
- fechaActoVinculacion 
- fechaPosesion 
- certificadoDisponibilidadPresupuestal 
- numeroCDP 
- fechaCDP 
- valorDisponibilidadPresupuestal 
- resolucionRectoral 
- fechaResolucionRectoral 
- estadoFormalizacion 
- fechaInicioEfectiva 
- fechaTerminacionEfectiva 
- horasSemanalesAsignadas 
- horasMensualesAsignadas 
- horasDocenciaDirecta 
- horasActividadesComplementarias 
- horasMensualesReconocidas 
- horasMensualesCumplidas 
- horasIncumplidas 
- valorHoraIncumplida 
- valorDescuentoIncumplimiento 
- limiteHorasSemanales 
- requiereCertificacionCumplimiento 
- certificacionCumplimiento 
- fechaCertificacionCumplimiento 
- categoriaDocenteAlVincular 
- nivelPosgradoAlVincular 
- grupoInvestigacionAlVincular 
- categoriaGrupoAlVincular 
- semilleroAlVincular 
- salarioMinimoVigente 
- factorSalarialSMMLV 
- valorHoraCatedraVigente 
- resolucionValorHoraCatedra 
- fechaVigenciaValorHora 
- salarioMensualPactado 
- permiteBonificacionPosgrado 
- permiteBonificacionInvestigacion 
- permitePrestacionesSociales 
- permiteAportesParafiscales 
- causalTerminacion 
- fechaNovedadTerminacion 
- actoTerminacion 
- renunciaPresentada 
- renunciaAceptada 
- necesidadServicioVigente 
- incumplimientoComprobado 
- decisionJudicialOAdministrativa 
- documentoSoporteTerminacion 
- estadoFinalContrato ![ref4]
22. CategoriaDocente \
    CategoriaDocente 
- idCategoria 
- codigo 
- nombre 
- descripcion 
- puntosBase 
- valorHoraBase 
- nivelJerarquico 
- normaOrigen 
- fechaInicioVigencia 
- fechaFinVigencia 
- estado 
- tipoRegimen 
- puntosCategoria 
- factorSalarialTiempoCompleto 
- factorSalarialMedioTiempo 
- unidadFactorSalarial 
- requiereActoReconocimiento 
- actoReconocimiento 
- fechaReconocimiento 
- categoriaAnterior 
- fechaAscenso 
- esCategoriaPorDefecto 
- permiteReconocimientoCategoriaOrigen 
- evaluacionSatisfactoriaInstitucionOrigen 

Categorías 

AUXILIAR 

ASISTENTE 

ASOCIADO 

TITULAR 

NO\_CATEGORIZADO 

Para profesores de carrera, los puntos de categoría son 37 para auxiliar, 58 para asistente, 74 para asociado y 96 para titular. Los puntajes no se acumulan entre categorías.  

Para profesores ocasionales, los factores salariales sobre el salario mínimo son: AUXILIAR\_TIEMPO\_COMPLETO = 2.645 AUXILIAR\_MEDIO\_TIEMPO = 1.509 ASISTENTE\_TIEMPO\_COMPLETO = 3.125 ASISTENTE\_MEDIO\_TIEMPO = 1.749 ASOCIADO\_TIEMPO\_COMPLETO = 3.606 

ASOCIADO\_MEDIO\_TIEMPO = 1.990 

TITULAR\_TIEMPO\_COMPLETO = 3.918 

TITULAR\_MEDIO\_TIEMPO = 2.146 

Estos factores deben guardarse como parámetros con vigencia, no como constantes permanentes.  ![ref2]

23. FactorSalarial \
    FactorSalarial 
- idFactor 
- nombre 
- tipoFactor 
- cantidad 
- puntosReconocidos 
- valorReconocido 
- fechaReconocimiento 
- actoAdministrativo 
- idProfesor 
- estado 
- regimenAplicable 
- factorGenerador 
- tipoReconocimiento 
- puntosSolicitados 
- puntosAprobados 
- puntosAcumulables 
- topeIndividual 
- topePorCategoria 
- topeAnual 
- numeroAutores 
- factorCoautoria 
- requiereEvaluacionPares 
- resultadoEvaluacionPares 
- requiereAprobacionComite 
- fechaAprobacionComite 
- actoReconocimiento 
- fechaEfectoSalarial 
- esConstitutivoSalario 
- integraBasePrestacional 
- integraBaseParafiscal 
- vigenciaDesde 
- vigenciaHasta 

Tipos de factor 

TITULO\_ACADEMICO 

CATEGORIA\_DOCENTE 

EXPERIENCIA 

PRODUCTIVIDAD\_ACADEMICA 

DIRECCION\_ACADEMICO\_ADMINISTRATIVA 

DESEMPENO\_DESTACADO POSGRADO 

GRUPO\_INVESTIGACION 

SEMILLERO ![ref8]

24. ProduccionAcademica \
    ProduccionAcademica 
- idProduccion 
- idProfesor 
- tipoProduccion 
- titulo 
- fechaPublicacion 
- entidadPublicadora 
- identificadorProducto 
- puntosSolicitados 
- puntosReconocidos 
- fechaReconocimiento 
- actoAdministrativo 
- estadoValidacion 
- modalidadProducto 
- subtipoProducto 
- nivelImpacto 
- clasificacionRevista 
- isbn 
- issn 
- registroDerechoAutor 
- numeroPatente 
- entidadIndexadora 
- numeroAutores 
- posicionAutor 
- porcentajeParticipacion 
- creditoInstitucional 
- evaluadoPorPares 
- cantidadPares 
- resultadoEvaluacion 
- puntosTotalesProducto 
- factorCoautoria 
- puntosReconocidosProfesor 
- tipoReconocimiento 
- fechaActoReconocimiento 
- yaReconocidoOtroConcepto 
- productoReclasificado 
- puntosAdicionalesReclasificacion 
- fechaLimiteReclasificacion ![ref1]
25. PeriodoNomina \
    PeriodoNomina 
- idPeriodoNomina 
- anio 
- mes 
- fechaInicio 
- fechaFin 
- fechaPago 
- estado 
- tipoPeriodicidad 
- salarioMinimoVigente 
- valorPuntoSalarialVigente 
- fechaVigenciaValorPunto 
- resolucionValorPunto 
- diasBaseLiquidacion 
- fechaCorteNovedades 
- fechaCierreNomina 
- fechaAprobacion 
- usuarioAprobador 
- totalDevengadoPeriodo 
- totalDescuentosPeriodo 
- totalPrestacionesPeriodo 
- totalAportesPatronalesPeriodo 
- costoTotalPeriodo 
- estaCerrado 
- permiteReliquidacion 
- versionLiquidacion ![ref1]
26. LiquidacionNomina \
    LiquidacionNomina 
- idLiquidacion 
- idProfesor 
- idContrato 
- idPeriodoNomina 
- fechaLiquidacion 
- salarioBase 
- totalDevengado 
- totalDescuentos 
- totalPrestaciones 
- baseLiquidacionPrestaciones 
- baseCotizacionSeguridadSocial 
- valorAuxilioTransporteCotizado 
- aportePatronalSENA 
- aportePatronalICBF 
- netoPagar 
- estado 
- tipoProfesorLiquidado 
- regimenLiquidado 
- categoriaLiquidada 
- dedicacionLiquidada 
- diasTrabajados 
- diasNoRemunerados 
- horasAsignadas 
- horasCumplidas 
- horasIncumplidas 
- salarioMinimoUsado 
- valorPuntoUsado 
- valorHoraCatedraUsado 
- factorCategoriaUsado 
- puntosSalarialesUsados 
- salarioOrdinario 
- baseSalarialPrestacional 
- baseSeguridadSocial 
- baseParafiscales 
- bonificacionPosgrado 
- bonificacionInvestigacion 
- bonificacionesSalariales 
- bonificacionesNoSalariales 
- otrosDevengadosSalariales 
- otrosDevengadosNoSalariales 
- ajustesDevengados 
- descuentoSalud 
- descuentoPension 
- fondoSolidaridadPensional 
- retencionFuente 
- descuentoHorasIncumplidas 
- descuentoLibranza 
- descuentoEmbargo 
- otrosDescuentos 
- ajustesDescuentos 
- provisionCesantias 
- provisionInteresesCesantias 
- provisionPrimaServicios 
- provisionPrimaNavidad 
- provisionVacaciones 
- provisionPrimaVacaciones 
- bonificacionServiciosPrestados 
- aportePatronalSalud 
- aportePatronalPension 
- aporteRiesgosLaborales 
- aporteCajaCompensacion 
- otrosAportesPatronales 
- costoTotalEmpleador 
- fechaGeneracion 
- fechaAprobacion 
- aprobada 
- pagada 
- fechaPago 
- medioPago 
- referenciaPago 
- requiereReliquidacion 
- motivoReliquidacion 
- liquidacionOrigen 
- version 
- usuarioLiquidador 
- usuarioAprobador ![ref1]
27. ConceptoNomina \
    ConceptoNomina 
- idConcepto 
- codigo 
- nombre 
- tipoConcepto 
- naturaleza 
- formaCalculo 
- porcentaje 
- valorFijo 
- baseCalculo 
- aplicaA 
- normaOrigen 
- fechaInicioVigencia 
- fechaFinVigencia 
- estado 
- codigoContable 
- regimenAplicable 
- modalidadProfesorAplicable 
- categoriaAplicable 
- dedicacionAplicable 
- periodicidad 
- esSalarial 
- esBonificacion 
- esDescuentoLey 
- esPrestacionSocial 
- esAportePatronal 
- integraBaseSalud 
- integraBasePension 
- integraBasePrestacional 
- integraBaseParafiscal 
- integraLiquidacionFinal 
- requiereActoAdministrativo 
- articuloOrigen 
- prioridadCalculo 
28. DetalleLiquidacion \
    ![ref5]DetalleLiquidacion 
- idDetalleLiquidacion 
- idLiquidacion 
- idConcepto 
- cantidad 
- baseCalculo 
- porcentajeAplicado 
- valorUnitario 
- valorCalculado 
- observaciones 
- tipoMovimiento 
- fechaCausacion 
- periodoCausacion 
- formulaAplicada 
- parametrosAplicados 
- valorAntesAjuste 
- valorAjuste 
- valorDefinitivo 
- esSalarial 
- integraSeguridadSocial 
- integraPrestaciones 
- integraParafiscales 
- actoSoporte 
- documentoSoporte 
- usuarioRegistro 
- fechaRegistro ![ref5]
29. ParametroNormativo 

ParametroNormativo 

- idParametro 
- codigo 
- nombre 
- descripcion 
- tipoDato 
- valor 
- unidad 
- normaOrigen 
- articulo 
- fechaInicioVigencia 
- fechaFinVigencia 
- aplicaA 
- estado 

Parámetros esperados 

SALARIO\_MINIMO 

VALOR\_PUNTO\_SALARIAL 

VALOR\_AUXILIO\_TRANSPORTE\_VIGENTE 

PORCENTAJE\_ARL\_CLASE\_I (0.522%) 

PORCENTAJE\_ARL\_CLASE\_II (1.044%) 

PORCENTAJE\_SENA (2%) 

PORCENTAJE\_ICBF (3%) 

VALOR\_HORA\_CATEDRA 

PORCENTAJE\_SALUD\_TRABAJADOR 

PORCENTAJE\_SALUD\_EMPLEADOR 

PORCENTAJE\_PENSION\_TRABAJADOR 

PORCENTAJE\_PENSION\_EMPLEADOR 

PORCENTAJE\_FONDO\_SOLIDARIDAD 

PORCENTAJE\_RIESGOS\_LABORALES 

PORCENTAJE\_CAJA\_COMPENSACION 

NOTA\_MINIMA\_APROBATORIA 

PROMEDIO\_MINIMO\_EBRA 

MAXIMO\_CREDITOS\_PERIODO ![ref4]

30. ArchivoPersistencia \
    ArchivoPersistencia 
- idArchivo 
- nombreArchivo 
- ruta 
- formato 
- fechaCreacion 
- fechaUltimaCarga 
- fechaUltimoGuardado 
- versionEstructura 
- cantidadRegistros 
- estado ![ref8]
4. Relaciones definitivas \
   Universidad 1 -------- N Facultad 

   Facultad 1 -------- N ProgramaAcademico \
   ProgramaAcademico 1 -------- N PlanEstudio 

   ProgramaAcademico 1 -------- N Estudiante 

   PlanEstudio 1 -------- N DetallePlanEstudio 

   Curso 1 -------- N DetallePlanEstudio 

   Curso 1 -------- N Prerrequisito 

   Curso 1 -------- N OfertaCurso 

   Persona 1 -------- 0..1 Estudiante 

   Persona 1 -------- 0..1 Profesor 

   Persona 1 -------- 0..1 Administrativo 

   PeriodoAcademico 1 -------- N OfertaCurso 

   PeriodoAcademico 1 -------- N MatriculaAcademica 

   Profesor 1 -------- N AsignacionDocente 

   OfertaCurso 1 -------- N AsignacionDocente OfertaCurso 1 -------- N Horario Estudiante 1 -------- N MatriculaAcademica 

   MatriculaAcademica 1 -------- N DetalleMatricula 

   OfertaCurso 1 -------- N DetalleMatricula 

   OfertaCurso 1 -------- N Evaluacion 

   Evaluacion 1 -------- N Calificacion 

   DetalleMatricula 1 -------- N Calificacion 

   Estudiante 1 -------- N AlertaAcademica 

   PeriodoAcademico 1 -------- N AlertaAcademica 

   Profesor 1 -------- N Contrato 

   CategoriaDocente 1 -------- N Profesor 

   Profesor 1 -------- N FactorSalarial 

   Profesor 1 -------- N ProduccionAcademica 

   PeriodoNomina 1 -------- N LiquidacionNomina 

   Profesor 1 -------- N LiquidacionNomina 

   Contrato 1 -------- N LiquidacionNomina 

   LiquidacionNomina 1 -------- N DetalleLiquidacion 

   ConceptoNomina 1 -------- N DetalleLiquidacion 

   Relaciones muchos a muchos resueltas Programa y curso 

   La relación se resuelve mediante: 

   PlanEstudio 

   DetallePlanEstudio 

   Profesor y oferta de curso 

   La relación se resuelve mediante: 

   AsignacionDocente 

   Estudiante y oferta de curso 

   La relación se resuelve mediante: 

   MatriculaAcademica 

   DetalleMatricula 

   Liquidación y conceptos de nómina 

   La relación se resuelve mediante: 

   DetalleLiquidacion ![ref4]

5. Reglas de negocio definitivas 
1. Reglas institucionales 
1. Una universidad puede tener varias facultades. 
1. Una facultad debe pertenecer a una universidad. 
1. Un programa académico debe pertenecer a una facultad. 
1. Un plan de estudio debe pertenecer a un programa. 
1. Un curso puede formar parte de diferentes planes de estudio. 
1. Los códigos de facultad, programa, curso, estudiante y profesor deben ser únicos en su ámbito correspondiente. 
1. Los registros con movimientos históricos deben desactivarse, no eliminarse físicamente. ![](Aspose.Words.88732198-408d-4729-9f4d-b7417c864c2e.010.png)
2. Reglas de personas 
1. El número de documento debe ser único por persona. 
1. Una persona puede desempeñar uno o más roles institucionales. 
1. Un estudiante debe tener una persona asociada. 
1. Un profesor debe tener una persona asociada. 
1. Un administrativo debe tener una persona asociada. 
1. La desactivación de una persona no debe eliminar sus matrículas, contratos, asignaciones ni liquidaciones. 
3. Reglas de matrícula ![ref5]
   1. El estudiante debe encontrarse activo. 
   1. El periodo académico debe estar abierto para matrícula. 
   1. La oferta debe encontrarse activa. 
   1. La oferta debe tener cupos disponibles. 
   1. El estudiante debe cumplir los prerrequisitos. 
   1. El estudiante no puede matricular dos veces la misma oferta. 
   1. No deben existir cruces de horario. 
   1. No debe superarse el máximo de créditos permitido. 
   1. Al matricular un curso debe disminuir el cupo disponible. 
   1. Al cancelar un curso debe liberarse el cupo. 
   1. La cancelación ordinaria debe realizarse dentro del plazo del periodo académico. 
   1. Una matrícula finalizada debe conservarse como información histórica. ![ref1]
3. Reglas de calificaciones 
1. La nota debe estar dentro de la escala institucional configurada. 
1. La suma de porcentajes de las evaluaciones activas debe ser igual al 100 %. 
1. La nota final se calcula mediante promedio ponderado: 

   notaFinal = suma(notaEvaluacion \* porcentajeEvaluacion) 

1. Después de registrar o modificar una nota se debe recalcular la nota final. 
1. Después de recalcular la nota final se debe recalcular el promedio del periodo. 
1. Después de recalcular el promedio del periodo se debe actualizar el promedio acumulado. ![](Aspose.Words.88732198-408d-4729-9f4d-b7417c864c2e.011.png)
5. Reglas de promedio y EBRA 

El promedio recomendado es ponderado por créditos: 

promedioPeriodo = suma(notaFinalCurso \* creditosCurso) / suma(creditosCurso) 

promedioAcumulado =n suma(notaFinalHistorica \* creditosCurso) / suma(creditosHistoricosConNota) 

La regla EBRA debe utilizar un parámetro institucional, porque el taller exige generar la alerta, pero no proporciona el umbral exacto.  

Si promedioAcumulado < promedioMinimoEBRA: estadoAcademico = EBRA generar AlertaAcademica 

El umbral no debe quedar escrito como constante en el programa. ![ref4]

6. Reglas generales de contratación docente 
1. Todo profesor debe tener una modalidad de vinculación identificable. 
1. Todo vínculo debe registrar fecha inicial, fecha final, dedicación, categoría y estado. 
1. La categoría y dedicación utilizadas para pagar al profesor deben corresponder a las vigentes durante el contrato. 
1. El contrato debe conservar los datos utilizados al momento de su formalización. 
1. Un contrato cerrado o terminado no debe modificarse directamente. 
1. Los contratos históricos no deben eliminarse físicamente. 
1. La terminación debe registrar fecha, causal y documento de soporte. ![ref9]
7. Profesor de planta 
1. Debe identificarse como empleado público docente y miembro de la carrera profesoral cuando corresponda. 
1. Su remuneración se calcula mediante puntos salariales. 
1. Los factores iniciales de puntuación son títulos, categoría, experiencia calificada y productividad académica. 
1. Las modificaciones posteriores pueden considerar categoría, nuevos títulos, productividad, dirección académico-administrativa, desempeño y experiencia. 
1. Los puntos por categoría no son acumulativos. 
1. Los puntos iniciales tienen efectos desde la fecha de posesión. 
7. Los puntos posteriores tienen efectos desde la fecha del acto formal de reconocimiento. 
7. Para dedicaciones distintas de tiempo completo, el salario debe calcularse proporcionalmente. 

totalPuntos =puntosTitulos+ puntosCategoria+ puntosExperiencia+ puntosProductividad+ puntosDireccion+ puntosDesempeno 

salarioTiempoCompleto =totalPuntos \* valorPuntoVigente salarioBase =salarioTiempoCompleto \* factorDedicacion ![](Aspose.Words.88732198-408d-4729-9f4d-b7417c864c2e.013.png)

8. Profesor ocasional 
1. Solo puede tener dedicación de tiempo completo o medio tiempo. 
1. Su vinculación es transitoria. 
1. El periodo de vinculación debe ser inferior a un año. 
1. No debe clasificarse como empleado público docente de régimen especial. 
1. No pertenece a la carrera profesoral. 
1. La vinculación debe formalizarse mediante resolución rectoral. 
1. La remuneración depende de la categoría docente, la dedicación y el salario mínimo vigente. 
1. Las horas correspondientes a actividades incumplidas deben descontarse. 
1. Una evaluación de desempeño no satisfactoria impide la vinculación durante el semestre siguiente.  

salarioBase =salarioMinimoVigente \* factorCategoriaDedicacion descuentoIncumplimiento =horasIncumplidas \* valorHoraIncumplida ![](Aspose.Words.88732198-408d-4729-9f4d-b7417c864c2e.014.png)

9. Profesor catedrático 
1. La dedicación máxima es de 18 horas semanales. 
1. La vinculación se realiza por periodos semestrales. 
1. No debe clasificarse como empleado público ni trabajador oficial. 
1. La vinculación se formaliza mediante resolución rectoral. 
5. Puede ser remunerado o ad honorem. 
5. El salario se calcula con las horas mensuales reconocidas y el valor vigente de la hora cátedra. 
5. El valor de hora debe proceder de una resolución rectoral vigente. 
5. Las bonificaciones aplicables deben calcularse proporcionalmente al número de horas.  

horasPagables = minimo(horasMensualesAsignadas, horasMensualesCumplidas) salarioBaseCatedra = horasPagables \* valorHoraCatedraVigente 

Para el vínculo ad honorem: 

esAdHonorem = verdadero 

esRemunerado = falso 

valorHora = 0 

salarioBase = 0 

netoPagar = 0 ![](Aspose.Words.88732198-408d-4729-9f4d-b7417c864c2e.015.png)

10. Administrativo que ejerce docencia 
1. Puede ejercer como catedrático ad honorem con autorización previa. 
1. La docencia directa ad honorem tendrá un máximo de 8 horas semanales. 
1. La actividad debe realizarse fuera de la jornada laboral administrativa. 
1. La docencia remunerada solo podrá registrarse para posgrados o actividades de educación continuada, fuera del horario laboral y siguiendo el procedimiento institucional correspondiente.  ![](Aspose.Words.88732198-408d-4729-9f4d-b7417c864c2e.016.png)
11. Categoría docente 
1. Las categorías son auxiliar, asistente, asociado y titular. 
1. Cuando un ocasional o catedrático no acredite categoría, debe quedar como no categorizado y ubicarse salarialmente en auxiliar. 
1. La categoría debe tener vigencia. 
1. Todo reconocimiento o ascenso debe conservar el acto administrativo. 
1. El cambio de categoría no debe modificar liquidaciones cerradas. 
6. A los profesores pensionados de otras instituciones estatales podrá reconocérseles su categoría anterior cuando sean vinculados como catedráticos y acrediten la evaluación satisfactoria exigida.  ![ref10]
12. Bonificación por posgrado 

Para profesores ocasionales y catedráticos: 

ESPECIALIZACION = 0.10 SMMLV 

MAESTRIA = 0.45 SMMLV 

DOCTORADO = 0.90 SMMLV 

POSTDOCTORADO = 0 SMMLV 

1. Solo se reconoce el posgrado de mayor nivel. 
1. No deben sumarse bonificaciones por varios posgrados. 
1. Para catedráticos debe aplicarse la proporción correspondiente a sus horas reconocidas. 
1. La bonificación debe guardarse separada del salario ordinario.  

bonificacionPosgrado = salarioMinimoVigente \* factorPosgrado ![](Aspose.Words.88732198-408d-4729-9f4d-b7417c864c2e.018.png)

13. Bonificación por investigación 

Los factores mensuales son: 

GRUPO\_A1 = 0.56 SMMLV 

GRUPO\_A = 0.47 SMMLV 

GRUPO\_B = 0.42 SMMLV 

GRUPO\_C = 0.38 SMMLV 

GRUPO\_RECONOCIDO = 0.33 SMMLV 

SEMILLERO = 0.20 SMMLV 

Para reconocerla: 

1. El grupo debe estar categorizado o reconocido antes de la vinculación. 
1. El semillero debe encontrarse registrado antes de la vinculación. 
3. El profesor debe acreditar productividad durante los dos años anteriores o participación activa en un proyecto vigente. 
3. La condición debe estar certificada por la dependencia competente. 
3. Para catedráticos debe calcularse proporcionalmente a las horas aplicables.  ![](Aspose.Words.88732198-408d-4729-9f4d-b7417c864c2e.019.png)
14. Naturaleza de las bonificaciones (Docentes Ocasionales y Catedráticos) 

Descripción Normativa: De conformidad con lo establecido en el Acuerdo No. 027 del 31 de octubre de 2024 de la Universidad Popular del Cesar (Artículos 23, 25 y 26), las bonificaciones mensuales por cualificación en posgrado y por pertenencia a grupos o semilleros de investigación de docentes ocasionales y catedráticos no constituyen salario bajo ninguna circunstancia1more\_horiz. Por consiguiente, deben manejarse de manera estrictamente independiente del salario ordinario en todos los procesos de cálculo, causación y registro del sistema PITA14. 

Reglas de Negocio Asociadas: 

1. Exclusión de Bases de Cotización de Seguridad Social: Ninguno de los montos liquidados por concepto de estas bonificaciones formará parte de la base para cotizar los aportes a salud, pensión ni riesgos laborales (ARL) del docente14. 
1. Exclusión de Bases de Aportes Parafiscales: Estos conceptos están exentos de la base de liquidación de aportes patronales destinados a Cajas de Compensación Familiar, SENA e ICBF14. 
1. Exclusión de Base Prestacional y Liquidación Definitiva: El sistema no debe computar el valor de estas bonificaciones para el cálculo de provisiones mensuales ni para el pago definitivo de prestaciones sociales (cesantías, intereses sobre cesantías, prima de servicios, prima de navidad y vacaciones), ni se integrarán en la liquidación al final del periodo de vinculación14. 
1. Cálculo Proporcional (Pro-rata) para Catedráticos: En el caso de los docentes con dedicación de hora cátedra, el valor de las bonificaciones de posgrado e investigación se reconocerá de forma proporcional al número de horas mensuales asignadas y efectivamente cumplidas15. 
1. Mecánica de Pago: Al tratarse de devengos no salariales libres de descuentos ordinarios de seguridad social, el valor liquidado de las bonificaciones se sumará directamente al netoPagar final, una vez aplicadas las deducciones de ley sobre el salario base o de cátedra ordinario. 

Variables de Control de Software (Lógica del Modelo Conceptual): Para garantizar la integridad de las reglas en la base de datos y en las operaciones de las entidades ConceptoNomina y DetalleLiquidacion, se forzarán los siguientes estados lógicos para estos conceptos específicos6: 

- esConstitutivoSalario = falso (Evita que sume al salario base ordinario para efectos legales). 
- integraBasePrestacional = falso (Bloquea su inclusión en las bases de primas, cesantías y vacaciones). 
- integraBaseParafiscal = falso (Excluye el concepto de los cálculos de aportes patronales y ARL). 
- integraLiquidacionFinal = falso (Asegura que no afecte la liquidación definitiva de fin de contrato). 

Ecuación de Integración en el Gestor de Nómina: Durante la ejecución del cálculo en GestorNomina, el flujo matemático debe operar bajo la siguiente estructura lógica: 

- baseSeguridadSocial = salarioOrdinario  (excluyendo bonificaciones) 
- netoPagar = (salarioOrdinario − descuentoSalud − descuentoPension) + bonificacionPosgrado + bonificacionInvestigacion ![](Aspose.Words.88732198-408d-4729-9f4d-b7417c864c2e.020.png)
15. Productos académicos y coautoría 
1. Un producto no puede recibir reconocimiento por más de una modalidad. 
1. No puede recibir simultáneamente puntos salariales y bonificación por el mismo concepto. 
1. Una reclasificación solo reconocerá la diferencia con respecto al nuevo tope. 
1. La reclasificación debe realizarse dentro del periodo permitido. 
1. Cuando se requiera evaluación externa, deben registrarse los pares y resultados. 
1. El factor de coautoría será:  

Si numeroAutores <= 3:factorCoautoria = 1.0 

Si numeroAutores está entre 4 y 5:factorCoautoria = 0.5 

Si numeroAutores >= 6:factorCoautoria = 2.0 / numeroAutores ![](Aspose.Words.88732198-408d-4729-9f4d-b7417c864c2e.021.png)

16. Liquidación general de nómina 

totalDevengado = salarioOrdinario + bonificacionesSalariales + bonificacionesNoSalariales + otrosDevengados 

totalDescuentos = descuentoSalud + descuentoPension + fondoSolidaridadPensional + retencionFuente + descuentoHorasIncumplidas + otrosDescuentos 

netoPagar = totalDevengado - totalDescuentos 

costoTotalEmpleador = totalDevengado+ totalPrestaciones+ totalAportesPatronales ![ref10]

17. Salud, pensión y demás descuentos 

Descripción Normativa: Para dar cumplimiento a la legislación laboral colombiana y a los requerimientos del taller2, el sistema PITA debe calcular de forma automática las deducciones legales a cargo del empleado (Salud y Pensión)3, así como las contribuciones y aportes a cargo del empleador (Seguridad Social, ARL y Parafiscales)3more\_horiz. Con el fin de evitar la rigidez en el código (*hardcoding*), todos los porcentajes, topes y tarifas deben ser tratados como registros históricos parametrizados con vigencia dentro de la entidad ParametroNormativo36. 

De igual manera, el sistema debe incorporar la exoneración patronal de aportes contemplada en el artículo 65 de la Ley 1819 de 2016 (ilustrada oficialmente en la simulación para empleadores de "Mi Calculadora" de Mintrabajo)7, la cual aplica a empleadores por aquellos trabajadores que devenguen mensualmente menos de diez (10) Salarios Mínimos Mensuales Legales Vigentes (SMMLV)7. ![ref7]

Reglas de Negocio Asociadas: 

1. Diferenciación de Bases de Liquidación: 
- Base de Cotización de Seguridad Social / Ingreso Base de Cotización (IBC): Corresponde al salario ordinario o asignación devengada en el mes (incluyendo el descuento de horas incumplidas en ocasionales o el pro-rata de horas cumplidas en catedráticos)8more\_horiz. Se excluye estrictamente el auxilio de transporte11 y las bonificaciones de posgrado e investigación del Acuerdo 027 por ser conceptos no constitutivos de salario12more\_horiz. 

baseSeguridadSocial = salarioOrdinario 

- Base de Liquidación de Prestaciones Sociales: Corresponde a la suma de la base de cotización de seguridad social más el auxilio de transporte (únicamente si el trabajador tiene derecho a devengarlo por ganar hasta 2 SMMLV en condiciones ordinarias)11. 
2. Cálculo de Descuentos al Trabajador (Deducciones de Nómina): 
- Salud (Trabajador): Deducción mensual obligatoria calculada sobre el IBC utilizando el parámetro vigente3: 

descuentoSalud = baseSeguridadSocial × porcentajeSaludTrabajador 

- Pensión (Trabajador): Deducción mensual obligatoria calculada sobre el IBC utilizando el parámetro vigente3: 

descuentoPension = baseSeguridadSocial × porcentajePensionTrabajador 

- Fondo de Solidaridad Pensional (FSP): Deducción aplicable si el IBC es igual o superior a 4 SMMLV, de acuerdo con la escala tarifaria vigente1516. 
3. Cálculo de Aportes del Empleador (Seguridad Social y Parafiscales): 
- Pensión (Patronal): Aporte mensual a cargo de la universidad calculado sobre el IBC5: 

aportePatronalPension = baseSeguridadSocial × porcentajePensionEmpleador 

- Riesgos Laborales (ARL): Aporte mensual determinado por el IBC y la clase de riesgo (Clase I a V) configurada en el contrato del docente11: aporteRiesgosLaborales = baseSeguridadSocial × porcentajeARL(Clase) 
4. Regla de Exoneración de Aportes Patronales (Ley 1819 de 2016): El sistema evaluará de forma lógica el IBC mensual del empleado para determinar la aplicación de la exención tributaria en salud y aportes parafiscales (SENA e ICBF)7: 
- Condición de Exoneración (IBC < 10 SMMLV): Salud patronal, SENA e ICBF se liquidarán en cero (0) pesos7. 

aportePatronalSalud = 0 

aportePatronalSENA = 0 

aportePatronalICBF = 0 

- Condición de Tarifa Plena (IBC ≥ 10 SMMLV): Se aplicarán las tarifas plenas correspondientes parametrizadas en el sistema (típicamente Salud: 8.5%, SENA: 2%, ICBF: 3%)7: 

aportePatronalSalud = baseSeguridadSocial × porcentajeSaludEmpleador aportePatronalSENA = baseSeguridadSocial × porcentajeSenaEmpleador aportePatronalICBF = baseSeguridadSocial × porcentajeIcbfEmpleador 

5. Aporte a Caja de Compensación Familiar: Este aporte no se encuentra sujeto a la exoneración de la Ley 1819 de 20167. Por lo tanto, se liquidará en todos los casos sobre el IBC utilizando el parámetro de ley (típicamente 4%)416: 

aporteCajaCompensacion = baseSeguridadSocial × porcentajeCajaCompensacion ![](Aspose.Words.88732198-408d-4729-9f4d-b7417c864c2e.022.png)

18. **Prestaciones de profesores de planta (y provisiones bajo Decreto 1279 de 2002)** 

**Descripción Normativa:** De acuerdo con el Capítulo IX del **Decreto 1279 de 2002**3, los empleados públicos docentes de carrera (Planta) tienen derecho a un régimen prestacional especial y completo. Con el fin de estimar con precisión el presupuesto institucional y el costo total mensual del empleador, el sistema PITA debe calcular de manera automática tanto las **provisiones mensuales de nómina** (causación de gastos futuros de acuerdo con el manual de "Mi Calculadora" del Ministerio del Trabajo)12 como las **liquidaciones definitivas** acumuladas al momento del disfrute, del pago anual o de la terminación contractual4more\_horiz. ![ref4]

**Reglas de Negocio Asociadas:** 

1. **Condición de Aplicabilidad (Filtro de Régimen Docente):** El cálculo y provisión de estas prestaciones sociales se aplicará de forma estricta y exclusiva cuando el contrato vigente indique que el tipo de profesor es PLANTA y su régimen aplicable sea el Decreto 12793. Para profesores OCASIONALES y CATEDRÁTICOS, se provisionarán únicamente las prestaciones básicas de ley y se excluirá de la base salarial cualquier bonificación del Acuerdo 027 de 20248more\_horiz. 
1. **Bases de Liquidación y Elementos Integradores (Decreto 1279):** Para cumplir con el marco de la carrera docente de planta, las bases se configuran así: 
- **Remuneración Mensual:** Determinada por el total de puntos salariales vigentes multiplicados por el valor del punto11. 
- **Base Salarial Prestacional (baseLiquidacionPrestaciones):** Incluye la asignación básica y el auxilio de transporte (si aplicase legalmente). 
- **Base de Vacaciones (Art. 33):** Se liquida sobre el salario mensual devengado, sumando una doceava (1/12) de la Prima de Servicios y una doceava (1/12) de la Bonificación por Servicios Prestados4. 
- **Base de la Prima de Vacaciones (Art. 39):** Se determina sumando dos tercios (2/3) del salario mensual, una doceava (1/12) de la Prima de Servicios y una doceava (1/12) de la Bonificación por Servicios Prestados5. 
- **Base de la Prima de Navidad (Art. 46):** Se determina sumando el salario mensual a 30 de noviembre, una doceava (1/12) de la Prima de Servicios, una doceava (1/12) de la Prima de Vacaciones y una doceava (1/12) de la Bonificación por Servicios Prestados12. 
3. **Fórmulas de Provisión Mensual Obligatorias (Mintrabajo - Empleador):** Para reflejar la causación en el costo mensual, el sistema calculará las siguientes provisiones en cada periodo de nómina (PeriodoNomina)1314: 
- **Cesantías (Art. 48):** Provisión equivalente al **8.33%** de la base prestacional. baseLiquidacionPrestaciones × diasTrabajados

provisionCesantias =

360

- **Intereses sobre Cesantías:** Provisión equivalente al **1%** mensual (12% anual) sobre el saldo acumulado provisional de las cesantías. 

provisionCesantias × diasTrabajados × 0.12 provisionInteresesCesantias =

360

- **Prima de Servicios (Art. 44):** Provisión equivalente al **8.33%** de la base prestacional. 

baseLiquidacionPrestaciones × diasTrabajados provisionPrimaServicios =

360

- **Vacaciones (Art. 33):** Provisión equivalente al **4.17%** del salario base (excluyendo auxilio de transporte, pues no hay desplazamiento en el descanso). salarioOrdinario × diasTrabajados

provisionVacaciones =

720

- **Prima de Navidad (Art. 45):** Provisión equivalente al **8.33%** de la base prestacional. 

baseLiquidacionPrestaciones × diasTrabajados provisionPrimaNavidad =

360

4. **Cálculo de Prestaciones Especiales del Decreto 1279:** 
- **Prima de Vacaciones (Art. 38):** Se provisiona mensualmente a una tasa estimada del **5.56%** de la asignación básica y se cancela completa en el mes de diciembre de cada año515. 
- **Bonificación por Servicios Prestados (Art. 41):** Se causará mensualmente y se pagará al cumplir el año de servicio continuo16. Su valor legal equivale a: 
- **50%** del salario mensual si este es inferior o igual al tope parametrizado (históricamente $756.411 en el decreto original, ajustado anualmente)16. 
- **35%** de la asignación mensual para salarios que superen dicho umbral17. 
5. **Aportes Pensionales y Otras Prestaciones:** Las cotizaciones al Sistema General de Pensiones se rigen por la Ley 100 de 1993, aplicando el parámetro de porcentaje vigente (típicamente 16% total: 12% empleador y 4% trabajador)18more\_horiz. Las demás prestaciones complementarias aplicables se liquidarán bajo los mismos términos de la Rama Ejecutiva del Poder Público según el Art. 50 del decreto21. ![](Aspose.Words.88732198-408d-4729-9f4d-b7417c864c2e.023.png)
19. Cierre y reliquidación 
1. Una liquidación cerrada no puede modificarse directamente. 
1. Una corrección debe generar una nueva versión o ajuste. 
1. La liquidación debe conservar los parámetros utilizados. 
1. Los cambios posteriores en salario mínimo, valor del punto o tarifa de hora cátedra no deben alterar liquidaciones históricas. 
1. Una nómina no puede pagarse sin haber sido liquidada y aprobada. 
1. Un contrato inactivo no puede generar nóminas posteriores a su fecha de terminación. 
1. Toda liquidación debe guardar la fórmula, base, porcentaje, cantidad y valor aplicado. ![](Aspose.Words.88732198-408d-4729-9f4d-b7417c864c2e.024.png)
20. Persistencia 
1. El programa debe poder iniciar con datos cargados o sin datos. 
1. La carga debe validar el formato de los registros. 
1. La carga debe comprobar referencias entre entidades. 
1. Los datos deben guardarse en archivos. 
1. Debe evitarse sobrescribir datos válidos cuando una carga falle. 
1. Los valores históricos de contratos y nóminas deben conservarse. 
1. El programa debe informar el resultado de la carga y el guardado.  ![ref9]

6\. Casos de uso 

1. Gestión institucional \
   CU-01. Gestionar facultades \
   Actor: usuario administrativo. \
   Acciones: 
- Crear facultad. 
- Consultar facultad. 
- Modificar facultad. 
- Desactivar facultad. 
- Listar facultades. 

CU-02. Gestionar programas académicos 

Actor: usuario administrativo. 

Acciones: 

- Crear programa. 
- Asociarlo con una facultad. 
- Consultar programas. 
- Modificar programa. 
- Desactivar programa. 

CU-03. Gestionar planes de estudio 

Actor: usuario académico. 

Acciones: 

- Crear plan. 
- Incluir cursos. 
- Definir créditos. 
- Definir semestre sugerido. 
- Consultar plan. 
- Desactivar una versión. 

CU-04. Gestionar cursos 

Actor: usuario académico. 

Acciones: 

- Crear curso. 
- Asignar créditos y horas. 
- Registrar prerrequisitos. 
- Consultar curso. 
- Modificar curso. 
- Desactivar curso. 
2. Gestión de personas ![ref5]

CU-05. Gestionar estudiante 

- Crear persona. 
- Crear estudiante. 
- Asociar programa y plan. 
- Consultar estudiante. 
- Modificar datos. 
- Desactivar estudiante. 

CU-06. Gestionar profesor 

- Crear persona. 
- Crear profesor. 
- Registrar modalidad. 
- Registrar categoría. 
- Registrar formación y experiencia. 
- Consultar profesor. 
- Modificar datos. 
- Desactivar profesor. 

CU-07. Gestionar administrativo 

- Crear persona. 
- Registrar administrativo. 
- Asignar cargo, dependencia y contratación. 
- Consultar. 
- Modificar. 
- Desactivar. ![ref11]
3. Gestión académica 

CU-08. Crear periodo académico 

- Registrar fechas. 
- Registrar ventana de matrícula. 
- Registrar fecha límite de cancelación. 
- Activar o cerrar periodo. 

CU-09. Crear oferta de curso 

- Seleccionar curso. 
- Seleccionar periodo. 
- Asignar grupo. 
- Definir cupo. 
- Definir horario. 
- Asignar profesor. 

CU-10. Matricular curso 

- Validar estudiante. 
- Validar periodo. 
- Validar cupo. 
- Validar prerrequisitos. 
- Validar créditos. 
- Validar cruces. 
- Crear detalle de matrícula. 
- Disminuir cupo. 

CU-11. Cancelar curso 

- Localizar matrícula. 
- Validar plazo. 
- Cambiar estado a cancelado. 
- Registrar fecha y motivo. 
- Liberar cupo. 

CU-12. Registrar calificación 

- Seleccionar oferta. 
- Seleccionar evaluación. 
- Seleccionar estudiante. 
- Registrar nota. 
- Recalcular nota final. 
- Recalcular promedio. 

CU-13. Calcular promedio 

- Consultar cursos con nota. 
- Aplicar ponderación por créditos. 
- Actualizar promedio del periodo. 
- Actualizar promedio acumulado. 

CU-14. Generar alerta EBRA 

- Comparar promedio acumulado con el umbral. 
- Actualizar estado académico. 
- Crear alerta. 
- Mostrar la alerta al consultar el estudiante. ![ref1]
4. Contratación docente 

CU-15. Registrar contrato docente 

- Seleccionar profesor. 
- Seleccionar modalidad. 
- Registrar dedicación. 
- Registrar fechas. 
- Registrar categoría. 
- Registrar horas. 
- Registrar acto de vinculación. 
- Validar reglas según tipo de profesor. 
- Activar contrato. 

CU-16. Vincular profesor ocasional 

- Validar dedicación. 
- Validar duración inferior a un año. 
- Registrar categoría. 
- Obtener factor salarial. 
- Registrar resolución rectoral. 
- Activar vínculo. 

CU-17. Vincular profesor catedrático 

- Validar máximo de 18 horas semanales. 
- Registrar horas mensuales. 
- Registrar tarifa. 
- Registrar resolución. 
- Indicar si es remunerado o ad honorem. 
- Activar vínculo. 

CU-18. Terminar contrato docente 

- Seleccionar contrato. 
- Registrar causal. 
- Registrar fecha efectiva. 
- Registrar documento. 
- Cambiar estado. 
- Impedir liquidaciones posteriores. ![ref3]
5. Nómina docente 

**CU-19. Configurar parámetros de nómina** 

- **Actor Principal:** Usuario Administrativo (Administrador de Nómina / Analista Financiero). 
- **Precondiciones:** 
1. El sistema debe estar iniciado. 
1. El usuario debe contar con privilegios de rol administrativo en el módulo financiero del sistema PITA. 
- **Flujo Principal:** 
1. El usuario administrativo solicita acceder al módulo de configuración paramétrica de nómina. 
1. El sistema presenta la lista completa de parámetros normativos actualmente vigentes (ParametroNormativo con estado = ACTIVO). 
1. El usuario selecciona la opción de **"Registrar Nueva Vigencia Paramétrica"** o **"Modificar Parámetro Activo"**. 
1. El sistema habilita el formulario y solicita el ingreso o actualización de los siguientes parámetros fundamentales: 
- **Salario Mínimo Mensual Legal Vigente (SMMLV)**. 
- **Auxilio de Transporte Mensual Vigente**. 
- **Valor del Punto Salarial Vigente** (para el escalafón docente de planta Decreto 1279). 
- **Valor de la Hora Cátedra Vigente** (de acuerdo con la resolución rectoral aplicable). 
- **Deducciones del Trabajador (Porcentajes):** Porcentaje de retención para Salud (típicamente 4%) y Pensión (típicamente 4%). 
- **Seguridad Social Patronal (Porcentajes):** Pensión Empleador (12%), Salud Empleador (8.5%) y cotizaciones de Riesgos Laborales (ARL) por cada clase de riesgo (Clase I: 0.522% hasta Clase V: 6.96%). 
- **Aportes Parafiscales Patronales (Porcentajes):** Caja de Compensación Familiar (4%), SENA (2%) e ICBF (3%). 
5. El usuario ingresa los nuevos valores correspondientes. 
5. El sistema solicita ingresar las fechas límites que determinan el período de validez del parámetro: **Fecha de Inicio de Vigencia** y **Fecha de Fin de Vigencia** (utilizando el formato uniforme AAAA-MM-DD). 
7. El usuario registra el rango temporal de vigencia y confirma el guardado. 
7. El sistema **ejecuta las validaciones automáticas de consistencia y coherencia** (Ver *Reglas de Validación* más abajo). 
7. Si las validaciones son exitosas, el sistema guarda de forma permanente el nuevo registro paramétrico en la lista de parametros con estado **ACTIVO**. 
7. El sistema ejecuta la **desactivación lógica de los registros paramétricos históricos obsoletos** cuya vigencia se superponga o haya caducado, actualizando su estado a **INACTIVO**. 
7. El sistema actualiza el archivo plano de persistencia (parametros\_normativos.txt) para asegurar la consistencia del arranque de datos en futuras sesiones. 
7. El sistema muestra un mensaje de confirmación de guardado exitoso y actualización de vigencias. 
- **Flujos Alternos / Excepciones:** 
- **Paso 8 (Error de Validación):** Si los datos de entrada violan las reglas de validación (por ejemplo, porcentajes negativos, fechas inconsistentes o superposiciones), el sistema aborta la operación, muestra una alerta indicando el campo erróneo y retorna al formulario sin modificar el estado previo de los parámetros. ![ref9]

**Reglas de Validación de Negocio (Paso 8):** 

Para evitar errores de digitación que alteren los cálculos masivos de nómina, el sistema PITA forzará las siguientes reglas lógicas antes de almacenar los parámetros: 

1. **Protección de Datos Históricos (Inmutabilidad de Parámetros):** El sistema prohíbe de forma estricta que la actualización o modificación de un parámetro (ej. cambiar el valor de la hora cátedra para el año actual) altere los parámetros guardados en liquidaciones o nóminas históricas de períodos que ya han sido cerrados o aprobados. 
1. **No Superposición Temporal:** Para un mismo código de parámetro (ej. SALARIO\_MINIMO), no pueden existir dos registros activos con intervalos de fecha de vigencia (fechaInicioVigencia y fechaFinVigencia) que se superpongan en el tiempo. 
1. **Límites de Entrada Numérica:** 
- Los porcentajes de cotización y deducción (Salud, Pensión, Parafiscales, ARL) deben validarse de manera estricta entre 0.0 y 1.0 (equivalente a 0% y 100%). 
- Los montos de dinero (SMMLV, valor del punto, valor del auxilio de transporte) deben ser valores numéricos estrictamente mayores a cero (> 0). 
4. **Consistencia de Fechas:** La fecha de fin de vigencia debe ser posterior a la fecha de inicio de vigencia de cada parámetro. 
4. **Postcondiciones:** Los nuevos valores se configuran como parámetros activos del sistema. El GestorNomina consumirá de manera automática estos valores vigentes para procesar las liquidaciones de nómina de los docentes de planta, ocasionales y catedráticos. 

CU-20. Liquidar profesor de planta 

- Obtener contrato vigente. 
- Obtener puntos reconocidos. 
- Obtener valor del punto. 
- Aplicar dedicación. 
- Calcular devengados. 
- Calcular descuentos. 
- Calcular prestaciones. 
- Calcular neto. 

**CU-21. Liquidar profesor ocasional** 

- **Actor Principal:** Usuario Administrativo (Analista de Nómina / Liquidador). 
- **Precondiciones:** 
1. El profesor ocasional debe tener un contrato vigente (Contrato con estado = ACTIVO y modalidadProfesor = OCASIONAL)34. 
1. El período de nómina actual debe estar abierto para liquidación (PeriodoNomina con estaCerrado = falso)56. 
1. Los parámetros normativos de nómina del mes actual (salario mínimo, auxilio de transporte, porcentajes de ley y ARL) deben estar configurados y activos7. 
1. Deben haberse reportado las novedades de asistencia (horas de actividades incumplidas) del período58. 
- **Flujo Principal:** 
1. El usuario administrativo solicita iniciar el proceso de liquidación mensual de un docente ocasional específico o la ejecución masiva para el período de nómina activo9. 
1. El sistema localiza el contrato de vinculación transitoria vigente del docente (menor a un año y de tiempo completo o medio tiempo)4more\_horiz. 
1. El sistema **obtiene la categoría docente registrada** (AUXILIAR, ASISTENTE, ASOCIADO, TITULAR o NO\_CATEGORIZADO)1213. 
1. El sistema **obtiene la dedicación estipulada** en el contrato (TIEMPO\_COMPLETO o MEDIO\_TIEMPO)3more\_horiz. 
1. El sistema **obtiene el valor del Salario Mínimo Mensual Legal Vigente (SMMLV)** parametrizado para el periodo actual715. 
1. El sistema **obtiene y aplica el factor salarial** correspondiente a la combinación de categoría y dedicación (según la tabla del Art. 24 del Acuerdo 027) para calcular el salario base pactado1617: 

salarioBase = salarioMinimoVigente × factorCategoriaDedicacion 

7. El sistema **obtiene el registro de horas de actividades incumplidas** (novedades de nómina) del docente en el mes815. 
7. El sistema **calcula y descuenta el valor de las horas incumplidas** utilizando la fórmula paramétrica (según el parágrafo del Art. 24 del Acuerdo 027) para obtener el salario ordinario ajustado15more\_horiz: valorDescuentoIncumplimiento = horasIncumplidas × valorHoraIncumplida salarioOrdinario = salarioBase − valorDescuentoIncumplimiento 
7. El sistema evalúa el salario ordinario ajustado para determinar si el docente tiene derecho al **Auxilio de Transporte** (si devenga hasta 2 SMMLV en condiciones ordinarias) e incorpora el subsidio si aplica19: 

   valorAuxilioTransporte

- aplicaAuxilioTransporte? VALOR\_AUXILIO\_TRANSPORTE\_VIGENTE: 0 
10. El sistema establece las bases de liquidación independientes para cotizaciones y provisiones15more\_horiz: 
- **Ingreso Base de Cotización (IBC):** baseSeguridadSocial = salarioOrdinario (excluye auxilio de transporte y bonificaciones del Acuerdo 027)1521. 
- **Base de Liquidación Prestacional:** baseLiquidacionPrestaciones = salarioOrdinario + valorAuxilioTransporte1519. 
11. El sistema **calcula los descuentos de ley a cargo del trabajador** (deducciones de nómina) utilizando los parámetros porcentuales vigentes1520: 
- descuentoSalud = baseSeguridadSocial \* porcentajeSaludTrabajador (4%)1520. 
- descuentoPension = baseSeguridadSocial \* porcentajePensionTrabajador (4%)1520. 
12. El sistema **calcula los aportes de seguridad social y parafiscales del empleador (Universidad)**, validando automáticamente la exoneración patronal de la Ley 1819 de 2016 (según se detalla en *"Mi Calculadora"* de Mintrabajo)2223: 
- *Si baseSeguridadSocial < 10 \* SMMLV*: 
  - aportePatronalSalud = 0 (Exonerado)2223 
  - aportePatronalSENA = 0 (Exonerado)23 
  - aportePatronalICBF = 0 (Exonerado)23 
- *Si baseSeguridadSocial >= 10 \* SMMLV*: 
  - aportePatronalSalud = baseSeguridadSocial \* porcentajeSaludEmpleador (8.5%)2022 
  - aportePatronalSENA = baseSeguridadSocial \* porcentajeSenaEmpleador (2%) 
  - aportePatronalICBF = baseSeguridadSocial \* porcentajeIcbfEmpleador (3%) 
- *Aportes siempre liquidados (no sujetos a exoneración)*: 
  - aportePatronalPension = baseSeguridadSocial \* porcentajePensionEmpleador (12%)2224 
  - aporteRiesgosLaborales = baseSeguridadSocial \* porcentajeARL(Clase) (según riesgo estipulado en el contrato del docente)1922 
  - aporteCajaCompensacion = baseSeguridadSocial \* porcentajeCajaCompensacion (4%)2225 
13. El sistema **calcula las provisiones mensuales de prestaciones sociales** a cargo de la universidad (requerimiento de causación del empleador en *"Mi Calculadora"* de Mintrabajo)222: 
- provisionCesantias = (baseLiquidacionPrestaciones \* diasTrabajados) / 360 (8.33% de la base prestacional)22more\_horiz. 
- provisionInteresesCesantias = (provisionCesantias \* diasTrabajados \* 

  0\.12) / 360 (1% mensual sobre el acumulado de cesantías)22more\_horiz. 

- provisionPrimaServicios = (baseLiquidacionPrestaciones \* diasTrabajados) / 360 (8.33% de la base prestacional)22more\_horiz. 
- provisionVacaciones = (salarioOrdinario \* diasTrabajados) / 720 (4.17% del salario base ajustado, sin incluir auxilio de transporte)22more\_horiz. 
14. El sistema invoca las operaciones de cálculo de **bonificaciones mensuales no constitutivas de salario** vigentes del Acuerdo 02726: 
- **Cualificación de Posgrado (Art. 25):** Si el docente cuenta con posgrado certificado, calcula la bonificación respectiva y la registra por separado1518. 
- **Grupo o Semillero de Investigación (Art. 26):** Si el docente pertenece a grupos o semilleros categorizados, calcula la bonificación de investigación y la registra por separado15more\_horiz. 
15. El sistema **calcula el Neto a Pagar** definitivo al profesor629: 

netoPagar = (salarioOrdinario + valorAuxilioTransporte − descuentoSalud

− descuentoPension) + bonificacionPosgrado

+ bonificacionInvestigacion 
16. El sistema **calcula el Costo Total Empleador** de la contratación2022: costoTotalEmpleador
- netoPagar + totalDescuentos + totalAportesPatronales
+ totalPrestacionesProvisionadas 
17. El sistema almacena la liquidación en estado **PROCESADA** (LiquidacionNomina asociada al contrato y periodo correspondiente) y guarda las fórmulas aplicadas en los registros de detalle630. 
- **Flujos Alternos / Excepciones:** 
- **Fallo en Novedades de Incumplimiento (Paso 7):** Si la novedad del mes indica que el número de horas incumplidas supera la carga horaria del contrato, el sistema emitirá un error crítico de consistencia y detendrá el cálculo de liquidación para el docente. 
- **Incompatibilidad del Docente Pensionado (Paso 2):** Si el docente ocasional se encuentra registrado como jubilado, el sistema lanzará una excepción bloqueante, ya que el Acuerdo 027 prohíbe de manera estricta la vinculación de jubilados como profesores ocasionales (Art. 11, numeral 6)31. 
- **Postcondiciones:** La liquidación queda guardada en el sistema de manera temporal con estado **PROCESADA**. Sus valores se acumulan automáticamente en los reportes preliminares de nómina del periodo para su posterior revisión, aprobación formal y pago definitivo32. 

CU-22. Liquidar profesor catedrático 

- Obtener horas reconocidas. 
- Obtener valor de hora. 
- Calcular salario base. 
- Calcular bonificaciones proporcionales. 
- Calcular descuentos. 
- Calcular neto. 

CU-23. Aplicar bonificación por posgrado 

- Verificar posgrados. 
- Seleccionar el de mayor nivel. 
- Obtener factor. 
- Calcular el reconocimiento. 
- Excluirlo de las bases indicadas por la norma. 

CU-24. Aplicar bonificación por investigación 

- Verificar grupo o semillero. 
- Verificar certificación. 
- Verificar productividad o proyecto vigente. 
- Obtener factor. 
- Calcular bonificación. 

CU-25. Cerrar nómina 

- Validar liquidaciones. 
- Calcular totales. 
- Aprobar periodo. 
- Cerrar nómina. 
- Bloquear modificaciones directas. 

CU-26. Consultar liquidación 

- Buscar profesor. 
- Seleccionar periodo. 
- Mostrar salario base. 
- Mostrar devengados. 
- Mostrar descuentos. 
- Mostrar prestaciones. 
- Mostrar neto pagado. ![ref4]
6. Persistencia 

CU-27. Cargar datos 

- Solicitar al usuario si desea cargar. 
- Leer archivos. 
- Validar datos. 
- Construir relaciones. 
- Informar errores. 
- Continuar con datos válidos o iniciar sin datos. 

CU-28. Guardar datos 

- Serializar las listas. 
- Guardar cada entidad. 
- Verificar escritura. 
- Informar resultado. ![ref11]
7. Restricciones definitivas 
1. Integridad 
   1. Los identificadores deben ser únicos. 
   1. Los documentos de personas no pueden repetirse. 
   1. Las referencias deben apuntar a entidades existentes. 
   1. Un detalle de matrícula debe pertenecer a una matrícula existente. 
   1. Una liquidación debe referenciar profesor, contrato y periodo de nómina existentes. 
   1. Un contrato no puede terminar antes de comenzar. 
1. Restricciones académicas 
   1. No matricular estudiantes inactivos. 
   1. No matricular en periodos cerrados. 
   1. No matricular cursos sin cupo. 
   1. No duplicar una oferta en la misma matrícula. 
   1. No superar el máximo de créditos. 
   1. No permitir cruces de horario. 
   1. No registrar notas fuera de la escala. 
   1. No finalizar un curso si los porcentajes de evaluación no suman 100 %. 
1. Restricciones de contratación 
   1. Un ocasional solo puede ser de tiempo completo o medio tiempo. 
   1. Un contrato ocasional debe durar menos de un año. 
   1. Un catedrático no puede superar 18 horas semanales. 
   1. Un administrativo catedrático ad honorem no puede superar 8 horas semanales. 
   1. Un profesor con evaluación no satisfactoria no puede vincularse en el semestre siguiente. 
   1. Un catedrático ad honorem no genera remuneración. 
   1. No puede liquidarse un profesor sin vínculo vigente. 
1. Restricciones de nómina 
- No usar parámetros fuera de vigencia. 
- No alterar parámetros históricos de una liquidación cerrada. 
- No pagar más horas de las asignadas o reconocidas. 
- No integrar bonificaciones excluidas en bases prestacionales o parafiscales. 
- No reconocer dos veces el mismo producto académico. 
- No modificar directamente una nómina cerrada. 
- El neto debe calcularse después de determinar devengados y descuentos. 
- Los descuentos no deben utilizar porcentajes fijos escritos en el algoritmo. 
- El valor de hora cátedra debe provenir de la resolución vigente. 
- El valor del punto debe corresponder al periodo liquidado. 
- El auxilio de transporte no debe incluirse en la base para cotizar salud, pensión, ARL ni parafiscales, pero debe incluirse obligatoriamente en la base de cálculo de la Prima de Servicios y las Cesantías 
- Ninguna bonificación estipulada en el Acuerdo 027 (posgrados e investigaciones) puede constituir factor para liquidar salud, pensión, riesgos profesionales ni prestaciones sociales 
5. Restricciones de eliminación 

No deben eliminarse físicamente: 

- Profesores con contratos. 
- Estudiantes con matrículas. 
- Cursos con historial. 
- Contratos con liquidaciones. 
- Liquidaciones cerradas. 
- Periodos académicos utilizados. 
- Parámetros utilizados en liquidaciones. 

Debe utilizarse: 

estado = INACTIVO 

6. Restricciones de persistencia 
- No guardar referencias inexistentes. 
- No aceptar identificadores duplicados. 
- No reemplazar los datos en memoria hasta finalizar correctamente la validación de la carga. 
- Mantener el mismo formato en C++ y Python para facilitar pruebas equivalentes. 
- Guardar fechas en un formato uniforme. 

Formato recomendado: 

AAAA-MM-DD ![](Aspose.Words.88732198-408d-4729-9f4d-b7417c864c2e.026.png)

8. Operaciones CRUD 

Cada entidad administrable debe soportar las operaciones pedidas por el taller: creación, inclusión, eliminación, desactivación, consulta, modificación y persistencia.  

1. Operaciones generales \
   crear() 

   agregar() 

   buscarPorId() 

   buscarPorCodigo() 

   listar() 

   modificar() 

   desactivar() 

   reactivar() 

   eliminar() 

   validar() 

   guardar() 

   cargar() 

2. CRUD institucional \
   crearFacultad() \
   buscarFacultad() \
   listarFacultades() \
   modificarFacultad() 

   desactivarFacultad() \
   crearPrograma() 

   buscarPrograma() 

   listarProgramasPorFacultad() 

   modificarPrograma() 

   desactivarPrograma() 

   crearCurso() 

   buscarCurso() 

   listarCursosPorPrograma() 

   modificarCurso() 

   desactivarCurso() 

3. CRUD de personas \
   crearPersona() \
   buscarPersonaPorDocumento() \
   modificarPersona() \
   desactivarPersona() 

   crearEstudiante() 

   buscarEstudiantePorCodigo() 

   listarEstudiantesPorPrograma() 

   modificarEstudiante() 

   desactivarEstudiante() 

   crearProfesor() 

   buscarProfesorPorCodigo() 

   listarProfesoresPorPrograma() 

   modificarProfesor() 

   desactivarProfesor() 

   crearAdministrativo() 

   buscarAdministrativo() 

   modificarAdministrativo() 

   desactivarAdministrativo() 

4. Operaciones académicas \
   crearPeriodoAcademico() \
   abrirPeriodo() \
   cerrarPeriodo() 

   crearOfertaCurso() 

   asignarProfesor() 

   agregarHorario() 

   consultarCupos() 

   crearMatricula() 

   matricularCurso() 

   cancelarCurso() 

   consultarMatricula() 

   crearEvaluacion() 

   registrarCalificacion() 

   modificarCalificacion() 

   calcularNotaFinal() 

   calcularPromedioPeriodo() 

   calcularPromedioAcumulado() 

   evaluarEBRA() 

5. Operaciones de contratación \
   crearContrato() \
   validarContrato() \
   buscarContratoVigente() \
   listarContratosProfesor() \
   modificarContrato() \
   terminarContrato() \
   desactivarContrato() 

   validarContratoPlanta() 

   validarContratoOcasional() 

   validarContratoCatedratico() 

   validarContratoAdHonorem() 

6. Operaciones de categoría y factores \
   crearCategoria() 

   buscarCategoria() 

   modificarCategoria() 

   desactivarCategoria() 

   registrarFactorSalarial() 

   aprobarFactorSalarial() 

   consultarFactoresProfesor() 

   calcularPuntosProfesor() 

   registrarProduccionAcademica() 

   validarProduccion() 

   calcularFactorCoautoria() 

   reconocerPuntos() 

7. Operaciones de nómina \
   crearPeriodoNomina() \
   abrirPeriodoNomina() \
   cerrarPeriodoNomina() 

   liquidarProfesor() 

   liquidarProfesorPlanta() 

   liquidarProfesorOcasional() 

   liquidarProfesorCatedratico() 

   calcularSalarioBase() 

   calcularBonificacionPosgrado() 

   calcularBonificacionInvestigacion() 

   calcularDescuentoSalud() 

   calcularDescuentoPension() 

   calcularPrestaciones() 

   calcularNetoPagar() 

   calcularCostoEmpleador() 

   aprobarLiquidacion() 

   pagarLiquidacion() 

   reliquidar() 

   consultarLiquidacion() 

8. Operaciones de parámetros \
   crearParametro() \
   buscarParametroVigente() \
   modificarParametro() \
   desactivarParametro() \
   listarParametrosPorTipo() 
8. Operaciones de persistencia \
   guardarUniversidad() \
   guardarFacultades() \
   guardarProgramas() \
   guardarCursos() \
   guardarPersonas() \
   guardarEstudiantes() \
   guardarProfesores() \
   guardarAdministrativos() \
   guardarContratos() \
   guardarPeriodosAcademicos() \
   guardarOfertas() \
   guardarMatriculas() \
   guardarCalificaciones() \
   guardarParametros() \
   guardarNominas() 

   cargarTodosLosDatos() 

   guardarTodosLosDatos() 

   validarIntegridadDatos() 

9. Estructuras de datos sugeridas ![ref5]

El taller pertenece al tema de listas, por lo que la estructura principal debe ser una colección secuencial de objetos. No es necesario utilizar una base de datos. 

1. Estructura raíz 

SistemaPITA 

- Universidad universidad 
- lista<Facultad> facultades 
- lista<ProgramaAcademico> programas 
- lista<PlanEstudio> planesEstudio 
- lista<Curso> cursos 
- lista<Persona> personas 
- lista<Estudiante> estudiantes 
- lista<Profesor> profesores 
- lista<Administrativo> administrativos 
- lista<PeriodoAcademico> periodosAcademicos 
- lista<OfertaCurso> ofertasCurso 
- lista<MatriculaAcademica> matriculas 
- lista<Contrato> contratos 
- lista<CategoriaDocente> categorias 
- lista<FactorSalarial> factoresSalariales 
- lista<ProduccionAcademica> producciones 
- lista<ParametroNormativo> parametros 
- lista<PeriodoNomina> periodosNomina 
- lista<LiquidacionNomina> liquidaciones 
- lista<ConceptoNomina> conceptosNomina 
2. Estructuras en C++ ![ref5]

Se recomienda utilizar clases o estructuras para las entidades y std::list como colección principal. std::list<Facultad> facultades; 

std::list<ProgramaAcademico> programas; 

std::list<Curso> cursos; 

std::list<Persona> personas; 

std::list<Estudiante> estudiantes; 

std::list<Profesor> profesores; 

std::list<Administrativo> administrativos; 

std::list<Contrato> contratos; 

std::list<MatriculaAcademica> matriculas; 

std::list<LiquidacionNomina> liquidaciones; 

std::list<ParametroNormativo> parametros; 

Para relaciones internas: 

class MatriculaAcademica { 

public: 

int idMatricula; 

int idEstudiante; 

int idPeriodo; 

std::list<DetalleMatricula> detalles; 

}; 

class LiquidacionNomina { 

public: 

int idLiquidacion; 

int idProfesor; 

int idContrato; 

int idPeriodoNomina; 

std::list<DetalleLiquidacion> detalles; 

}; 

Los identificadores deben utilizarse para relacionar objetos y evitar copias inconsistentes. ![ref2]

3. Estructuras en Python 

Se recomienda utilizar clases con dataclass y listas nativas. facultades = [] 

programas = [] 

cursos = [] 

personas = [] 

estudiantes = [] 

profesores = [] 

administrativos = [] 

contratos = [] 

matriculas = [] 

liquidaciones = [] 

parametros = [] 

Composición interna: 

@dataclass 

class MatriculaAcademica: 

id\_matricula: int 

id\_estudiante: int 

id\_periodo: int 

detalles: list[DetalleMatricula] = field(default\_factory=list) @dataclass 

class LiquidacionNomina: 

id\_liquidacion: int 

id\_profesor: int 

id\_contrato: int 

id\_periodo\_nomina: int 

detalles: list[DetalleLiquidacion] = field(default\_factory=list) ![ref2]

4. Enumeraciones sugeridas \
   enum class EstadoRegistro { \
   ACTIVO, 

   INACTIVO, 

   ELIMINADO\_LOGICO 

   }; 

   enum class TipoProfesor { 

   PLANTA, 

   OCASIONAL, 

   CATEDRATICO, 

   CATEDRATICO\_AD\_HONOREM 

   }; 

   enum class Dedicacion { 

   TIEMPO\_COMPLETO, 

   MEDIO\_TIEMPO, 

   HORA\_CATEDRA 

   }; 

   enum class Categoria { 

   AUXILIAR, 

   ASISTENTE, 

   ASOCIADO, 

   TITULAR, 

   NO\_CATEGORIZADO 

   }; 

   class EstadoRegistro(Enum): 

   ACTIVO = "ACTIVO" 

   INACTIVO = "INACTIVO" ELIMINADO\_LOGICO = "ELIMINADO\_LOGICO" 

   class TipoProfesor(Enum): 

   PLANTA = "PLANTA" 

   OCASIONAL = "OCASIONAL" 

   CATEDRATICO = "CATEDRATICO" 

   CATEDRATICO\_AD\_HONOREM = "CATEDRATICO\_AD\_HONOREM" ![ref1]

5. Organización por servicios 

Para evitar que las entidades contengan toda la lógica, se recomienda separar las operaciones en gestores. 

GestorFacultades 

GestorProgramas 

GestorCursos 

GestorPersonas 

GestorEstudiantes 

GestorProfesores 

GestorMatriculas 

GestorCalificaciones 

GestorContratos 

GestorNomina 

GestorParametros 

GestorPersistencia 

Ejemplo conceptual: 

GestorNomina 

- buscarContratoVigente() 
- buscarParametrosVigentes() 
- calcularSalarioBase() 
- calcularBonificaciones() 
- calcularDescuentos() 
- calcularPrestaciones() 
- generarLiquidacion() ![ref1]
6. Persistencia sugerida 

Para que los programas de C++ y Python compartan datos, se recomienda utilizar archivos de texto separados por entidad. 

datos/ 

├── universidad.txt 

├── facultades.txt 

├── programas.txt 

├── planes\_estudio.txt 

├── cursos.txt 

├── personas.txt 

├── estudiantes.txt 

├── profesores.txt 

├── administrativos.txt 

├── periodos\_academicos.txt 

├── ofertas\_curso.txt 

├── matriculas.txt 

├── calificaciones.txt 

├── contratos.txt 

├── categorias\_docentes.txt 

├── factores\_salariales.txt 

├── producciones\_academicas.txt 

├── parametros\_normativos.txt 

├── periodos\_nomina.txt 

├── liquidaciones\_nomina.txt 

└── detalles\_liquidacion.txt 

Formato delimitado recomendado: 

id|campo1|campo2|campo3|estado 

Ejemplo: 1|PROF-001|PLANTA|TIEMPO\_COMPLETO|ACTIVO 2|PROF-002|OCASIONAL|MEDIO\_TIEMPO|ACTIVO 3|PROF-003|CATEDRATICO|HORA\_CATEDRA|ACTIVO 

Debe utilizarse el mismo orden de campos, delimitador, formato de fecha y representación de valores booleanos en ambos lenguajes. ![ref6]

10. Flujo principal sugerido \
    INICIAR 

    Mostrar opción: 

1. Cargar datos desde archivos 
2. Iniciar sin datos 

Si opción = 1: 

Cargar archivos 

Validar integridad 

Mientras el usuario no elija salir: 

Mostrar menú principal 

1. Gestionar facultades 
1. Gestionar programas 
1. Gestionar cursos 
1. Gestionar estudiantes 
1. Gestionar profesores 
1. Gestionar administrativos 
1. Gestionar matrícula académica 
1. Gestionar calificaciones 
1. Gestionar contratación docente 
1. Gestionar nómina docente 
1. Consultar reportes 
1. Guardar datos 
1. Salir 

Antes de salir: 

Ofrecer guardar datos 

FIN 

11\. Resultado definitivo 

La implementación debe conservar tres separaciones fundamentales: MODELO ACADÉMICO 

Universidad 

- Facultad 
- Programa 
- Plan de estudio 
- Curso 
- Oferta 
- Matrícula 
- Calificación 
- Promedio 
- Alerta EBRA 

MODELO DE CONTRATACIÓN 

Persona 

- Profesor 
- Categoría 
- Contrato 
- Asignación docente 

Plain Text 

MODELO DE NÓMINA 

Profesor 

- Contrato vigente 
- Régimen aplicable 
- Parámetros vigentes 
- Liquidación 
- Conceptos 
- Descuentos 
- Prestaciones 
- Neto a pagar 

[ref1]: Aspose.Words.88732198-408d-4729-9f4d-b7417c864c2e.001.png
[ref2]: Aspose.Words.88732198-408d-4729-9f4d-b7417c864c2e.002.png
[ref3]: Aspose.Words.88732198-408d-4729-9f4d-b7417c864c2e.003.png
[ref4]: Aspose.Words.88732198-408d-4729-9f4d-b7417c864c2e.004.png
[ref5]: Aspose.Words.88732198-408d-4729-9f4d-b7417c864c2e.005.png
[ref6]: Aspose.Words.88732198-408d-4729-9f4d-b7417c864c2e.006.png
[ref7]: Aspose.Words.88732198-408d-4729-9f4d-b7417c864c2e.007.png
[ref8]: Aspose.Words.88732198-408d-4729-9f4d-b7417c864c2e.009.png
[ref9]: Aspose.Words.88732198-408d-4729-9f4d-b7417c864c2e.012.png
[ref10]: Aspose.Words.88732198-408d-4729-9f4d-b7417c864c2e.017.png
[ref11]: Aspose.Words.88732198-408d-4729-9f4d-b7417c864c2e.025.png
