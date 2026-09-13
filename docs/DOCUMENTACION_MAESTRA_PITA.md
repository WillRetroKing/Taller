# Documentación maestra del sistema PITA

> **Programa Integrado de Transacciones Académicas**  
> **Universidad Popular del Cesar**  
> **Facultad de Ingenierías y Tecnológicas**  
> **Programa:** Ingeniería de Sistemas  
> **Asignatura:** Estructura de Datos  
> **Actividad:** Taller 1, Listas  
> **Versión documental:** 1.8 (ver historial en el Anexo C)  
> **Fecha:** Septiembre de 2026

---

## Control del documento

| Campo | Valor |
|---|---|
| Nombre del documento | Documentación maestra del sistema PITA |
| Tipo | Documento técnico y académico |
| Estado | Contrastado con el código fuente (C++ y Python); pendientes solo evidencias manuales |
| Fuente principal | Enunciado del Taller 1 y consolidado del modelo conceptual PITA |
| Lenguajes objetivo | C++ y Python |
| Persistencia objetivo | Archivos de texto plano |
| Estructura principal | Listas de objetos |

### Integrantes

- **Estudiante 1:** `[PENDIENTE]`
- **Estudiante 2:** `[PENDIENTE]`
- **Estudiante 3:** `[PENDIENTE]`
- **Grupo:** `[PENDIENTE]`
- **Docente:** Adith Pérez

### Convenciones editoriales

Los siguientes marcadores se utilizarán durante la construcción del documento:

- `[DISEÑO]`: elemento definido en el modelo conceptual.
- `[IMPLEMENTADO]`: elemento confirmado en el código fuente.
- `[IMPLEMENTACIÓN PARCIAL]`: elemento presente de forma incompleta.
- `[PENDIENTE DE IMPLEMENTACIÓN]`: elemento diseñado, pero ausente del código.
- `[PENDIENTE DE VERIFICACIÓN]`: elemento que debe contrastarse con C++ o Python.
- `[DECISIÓN DEL EQUIPO]`: aspecto que requiere una decisión explícita.
- `[EVIDENCIA PENDIENTE]`: sección que necesita captura, salida o prueba ejecutada.
- `[NORMA POR VERIFICAR]`: regla citada en las fuentes del proyecto cuya vigencia o interpretación debe confirmarse antes de una aplicación productiva.

> **Nota de alcance:** este archivo es el documento maestro del proyecto. Su contenido ya está contrastado con el código fuente de ambas implementaciones; la versión de entrega en Word se genera a partir de él con `docs/limpiar_md.py` y `docs/exportar_word.py`.

---

# 1. Introducción

El Programa Integrado de Transacciones Académicas, en adelante **PITA**, se concibe como una aplicación para gestionar información académica y organizacional de la Universidad Popular del Cesar. El sistema debe representar facultades, programas académicos, planes de estudio, cursos, estudiantes, profesores, administrativos, periodos, ofertas, matrículas, calificaciones, contratos, parámetros y liquidaciones de nómina.

El proyecto se desarrolla en el contexto de la asignatura Estructura de Datos y tiene como estructura central las listas. Por esta razón, la solución no depende de una base de datos relacional. Los datos se mantienen en colecciones secuenciales en memoria y se cargan y guardan mediante archivos de texto plano.

La documentación distingue tres niveles:

1. **Modelo conceptual:** describe qué debería representar el sistema.
2. **Diseño de la solución:** establece cómo se propone organizar entidades, listas, gestores y archivos.
3. **Implementación real:** describe lo que efectivamente realizan los programas en C++ y Python.

El documento cubre los tres niveles y se mantuvo contrastado con el código fuente durante todo el desarrollo: cada afirmación sobre estructuras, gestores, reglas y persistencia fue verificada contra los archivos reales de ambos lenguajes, y las desviaciones encontradas quedaron registradas en el historial de cambios (Anexo C).

---

# 2. Planteamiento del problema

La gestión universitaria exige mantener conjuntos de datos relacionados y ejecutar operaciones que afectan varias estructuras al mismo tiempo. La complejidad del problema no se limita al almacenamiento de registros. El sistema debe garantizar coherencia, conservar información histórica y aplicar reglas académicas y contractuales.

Entre las situaciones principales se encuentran:

- Una facultad puede contener varios programas académicos.
- Un programa puede contar con diferentes versiones de planes de estudio.
- Un curso puede pertenecer a varios planes mediante detalles de plan.
- Una persona puede desempeñar uno o más roles institucionales.
- Una oferta académica depende de un curso y de un periodo.
- Una matrícula debe validar cupo, prerrequisitos, créditos, duplicidad y cruces de horario.
- Una calificación debe participar en el cálculo de la nota final y los promedios.
- Un promedio acumulado inferior al umbral institucional puede generar una alerta EBRA.
- Un contrato docente debe conservar modalidad, categoría, dedicación, vigencia y acto de vinculación.
- Una liquidación debe seleccionar parámetros vigentes y guardar los valores y fórmulas aplicados.
- Una carga inválida no debe destruir los datos válidos que ya se encuentran en memoria.

El reto consiste en convertir estas necesidades en estructuras de datos comprensibles, operaciones seguras y archivos compatibles entre C++ y Python.

---

# 3. Justificación

El diseño de PITA permite aplicar conceptos fundamentales de estructuras de datos a un dominio institucional amplio. El uso de listas facilita estudiar inserción, recorrido, búsqueda, modificación y eliminación lógica de objetos relacionados.

La solución también permite practicar:

- Modelado orientado a objetos.
- Separación de responsabilidades.
- Validación de reglas de negocio.
- Persistencia en archivos de texto.
- Gestión de históricos.
- Parametrización de reglas variables.
- Implementación equivalente en dos lenguajes.
- Diseño de pruebas y manejo de errores.

Además, documentar el sistema antes de finalizar el código reduce ambigüedades y facilita mantener correspondencia entre las versiones de C++ y Python.

---

# 4. Objetivos

## 4.1 Objetivo general

Diseñar e implementar conceptualmente un sistema basado en listas que permita gestionar transacciones académicas y organizacionales de la Universidad Popular del Cesar, incluyendo operaciones CRUD, matrícula, calificaciones, promedios, alertas EBRA, contratación docente, simulación de nómina y persistencia interoperable entre C++ y Python.

## 4.2 Objetivos específicos

1. Modelar las entidades institucionales, personales, académicas, contractuales y de nómina requeridas.
2. Definir las relaciones entre entidades mediante identificadores únicos.
3. Diseñar operaciones de creación, inclusión, consulta, modificación, desactivación, eliminación y persistencia.
4. Establecer reglas para matrícula, cancelación, calificaciones, promedios y EBRA.
5. Diferenciar las reglas aplicables a profesores de planta, ocasionales, catedráticos y ad honorem.
6. Parametrizar valores económicos, porcentajes, umbrales y periodos de vigencia.
7. Diseñar un formato común de persistencia que pueda ser interpretado por ambos lenguajes.
8. Definir pruebas conceptuales para validar las operaciones principales.
9. Contrastar posteriormente el diseño con los programas fuente y documentar las diferencias.

---

# 5. Alcance del sistema

## 5.1 Alcance funcional

PITA debe permitir:

### Gestión institucional

- Gestionar la universidad.
- Crear, consultar, modificar, desactivar y listar facultades.
- Crear, consultar, modificar, desactivar y listar programas académicos.
- Gestionar planes de estudio y sus cursos.
- Gestionar cursos y prerrequisitos.

### Gestión de personas

- Registrar información común de las personas.
- Gestionar estudiantes.
- Gestionar profesores.
- Gestionar administrativos.
- Permitir que una persona tenga más de un rol institucional.

### Gestión académica

- Crear periodos académicos.
- Abrir y cerrar ventanas de matrícula.
- Crear ofertas de cursos.
- Asignar profesores y horarios.
- Matricular cursos.
- Cancelar cursos.
- Registrar evaluaciones y calificaciones.
- Calcular notas finales y promedios.
- Generar alertas EBRA.

### Contratación docente

- Registrar contratos.
- Identificar modalidad, dedicación y categoría.
- Validar reglas según el tipo de profesor.
- Registrar actos administrativos y vigencias.
- Terminar contratos sin eliminar su historia.

### Nómina docente

- Crear periodos de nómina.
- Configurar parámetros normativos.
- Calcular el salario de profesores de planta.
- Calcular el salario de profesores ocasionales.
- Calcular la remuneración de catedráticos.
- Representar vínculos ad honorem.
- Aplicar descuentos y aportes configurados.
- Calcular prestaciones cuando correspondan.
- Generar y consultar liquidaciones.
- Cerrar periodos y conservar liquidaciones históricas.

### Persistencia

- Iniciar el sistema con datos cargados o sin datos.
- Cargar registros desde archivos.
- Validar formato, duplicados y referencias.
- Guardar las listas en archivos.
- Informar el resultado de la carga y el guardado.
- Evitar la pérdida de datos válidos ante una carga incompleta.

## 5.2 Fuera del alcance inicial

Los siguientes elementos no forman parte obligatoria de la primera implementación académica:

- Base de datos relacional.
- Aplicación web o móvil.
- Autenticación y autorización por roles.
- Integración con plataformas institucionales reales.
- Pago bancario real.
- Contabilidad oficial.
- Firma electrónica de actos administrativos.
- Certificación jurídica de cálculos laborales.
- Despliegue en infraestructura productiva.

---

# 6. Requerimientos

## 6.1 Requerimientos funcionales

| Código | Requerimiento | Estado |
|---|---|---|
| RF-01 | Gestionar facultades. | `[IMPLEMENTADO]` |
| RF-02 | Gestionar programas académicos. | `[IMPLEMENTADO]` |
| RF-03 | Gestionar planes de estudio y cursos. | `[IMPLEMENTADO]` |
| RF-04 | Gestionar personas, estudiantes, profesores y administrativos. | `[IMPLEMENTADO]` |
| RF-05 | Crear periodos y ofertas académicas. | `[IMPLEMENTADO]` |
| RF-06 | Matricular y cancelar cursos. | `[IMPLEMENTADO]` |
| RF-07 | Registrar evaluaciones y calificaciones. | `[IMPLEMENTADO]` |
| RF-08 | Calcular promedios ponderados. | `[IMPLEMENTADO]` |
| RF-09 | Generar alertas EBRA mediante un parámetro institucional. | `[IMPLEMENTADO]` |
| RF-10 | Gestionar contratos docentes. | `[IMPLEMENTADO]` |
| RF-11 | Configurar parámetros de nómina con vigencia. | `[IMPLEMENTADO]` |
| RF-12 | Liquidar profesores según su modalidad. | `[IMPLEMENTADO]` |
| RF-13 | Aplicar descuentos, prestaciones y aportes. | `[IMPLEMENTADO]` |
| RF-14 | Guardar fórmulas y parámetros utilizados. | `[IMPLEMENTADO]` |
| RF-15 | Cargar y guardar datos en archivos de texto. | `[IMPLEMENTADO]` |
| RF-16 | Permitir iniciar con o sin datos previos. | `[IMPLEMENTADO]` |

> RF-01 a RF-05 se verificaron contra el código: las operaciones CRUD genéricas están en `persistencia/gestor_crud.py` (y `gestor_crud.h` en C++); la lógica de planes, cursos, prerrequisitos y asignaciones en `gestores/gestor_academico.py`; la de personas en `gestores/gestor_personas.py` (con generación de IDs y verificación de existencia) y la de periodos en `gestores/gestor_periodos.py`. En la GUI Python existen las vistas de Facultades, Personas y Académico, y en la GUI C++ las vistas `gui_vista_facultades.cpp`, `gui_vista_personas.cpp` y `gui_vista_academica.cpp`. Las pruebas P-01 y P-02 (sección 22) cubren el CRUD con código único.

## 6.2 Requerimientos no funcionales

### Usabilidad

- El menú debe identificar claramente cada módulo.
- Los mensajes deben explicar si una operación fue exitosa o rechazada.
- Los errores de entrada deben señalar el campo incorrecto.

### Integridad

- Los identificadores deben ser únicos.
- Los documentos de personas no pueden repetirse.
- Las referencias deben apuntar a registros existentes.
- Las operaciones compuestas no deben dejar cambios parciales.

### Mantenibilidad

- Las entidades no deben concentrar toda la lógica del sistema.
- Los parámetros variables no deben escribirse de forma fija en los algoritmos.
- Las funciones deben tener una responsabilidad clara.

### Interoperabilidad

- C++ y Python deben usar el mismo orden de campos.
- Ambos programas deben compartir delimitador, formato de fechas y representación booleana.

### Trazabilidad

- Las liquidaciones deben conservar los parámetros y fórmulas utilizados.
- Los cambios posteriores no deben alterar resultados históricos.

---

# 7. Estrategia de solución

## 7.1 Enfoque general

La solución se organiza alrededor de una estructura raíz llamada conceptualmente `SistemaPITA`. Esta estructura mantiene las listas principales y coordina gestores especializados.

El proceso de diseño sigue estos principios:

1. Cada concepto relevante se representa mediante una entidad.
2. Cada entidad tiene identificador y estado.
3. Las relaciones se expresan mediante identificadores.
4. Las operaciones CRUD se centralizan en gestores.
5. Las transacciones validan antes de modificar.
6. Los registros con historia se desactivan en lugar de eliminarse físicamente.
7. Los valores variables se obtienen de parámetros con vigencia.
8. La persistencia se realiza por entidad.

## 7.2 Capas conceptuales

| Capa | Responsabilidad | Ejemplos |
|---|---|---|
| Interacción | Menús, lectura de entradas y presentación de resultados. | Menú principal, formularios de consola, reportes. |
| Aplicación | Coordina casos de uso y transacciones. | GestorMatriculas, GestorNomina. |
| Dominio | Mantiene entidades, enumeraciones y reglas invariantes. | Estudiante, Contrato, LiquidacionNomina. |
| Persistencia | Lee y escribe archivos de texto. | GestorPersistencia. |

## 7.3 Separaciones fundamentales

### Modelo académico

- Universidad.
- Facultad.
- Programa académico.
- Plan de estudio.
- Curso.
- Oferta.
- Matrícula.
- Calificación.
- Promedio.
- Alerta EBRA.

### Modelo de contratación

- Persona.
- Profesor.
- Categoría.
- Contrato.
- Asignación docente.

### Modelo de nómina

- Profesor.
- Contrato vigente.
- Régimen aplicable.
- Parámetros vigentes.
- Periodo de nómina.
- Liquidación.
- Conceptos.
- Descuentos.
- Prestaciones.
- Neto a pagar.

---

# 8. Diseño de las estructuras de datos

## 8.1 Estructura raíz

La estructura conceptual `SistemaPITA` contiene:

- Una referencia a la universidad.
- Una lista de facultades.
- Una lista de programas.
- Una lista de planes de estudio.
- Una lista de cursos.
- Una lista de personas.
- Una lista de estudiantes.
- Una lista de profesores.
- Una lista de administrativos.
- Una lista de periodos académicos.
- Una lista de ofertas de curso.
- Una lista de matrículas.
- Una lista de contratos.
- Una lista de categorías.
- Una lista de factores salariales.
- Una lista de producciones académicas.
- Una lista de parámetros.
- Una lista de periodos de nómina.
- Una lista de liquidaciones.
- Una lista de conceptos de nómina.

## 8.2 Colecciones propuestas

> `[IMPLEMENTADO]` El tipo de colección fue verificado en el código. En **C++ no se usa `std::list`**: el proyecto implementa su propia estructura `ListaEnlazada<T>` en `cpp/dominio/lista_enlazada.h`, una lista **doblemente enlazada** con nodos (`Nodo<T>` con punteros `anterior`/`siguiente`), iteradores bidireccionales propios y control de longitud — decisión coherente con el objetivo del taller (implementar listas manualmente). En **Python** se usan las listas nativas `list[T]`.

| Colección conceptual | Tipo de elemento | C++ real | Python real | Estado real |
|---|---|---|---|---|
| facultades | Facultad | `ListaEnlazada<Facultad>` | `list[Facultad]` | `[IMPLEMENTADO]` |
| programas | ProgramaAcademico | `ListaEnlazada<ProgramaAcademico>` | `list[ProgramaAcademico]` | `[IMPLEMENTADO]` |
| cursos | Curso | `ListaEnlazada<Curso>` | `list[Curso]` | `[IMPLEMENTADO]` |
| personas | Persona | `ListaEnlazada<Persona>` | `list[Persona]` | `[IMPLEMENTADO]` |
| estudiantes | Estudiante | `ListaEnlazada<Estudiante>` | `list[Estudiante]` | `[IMPLEMENTADO]` |
| profesores | Profesor | `ListaEnlazada<Profesor>` | `list[Profesor]` | `[IMPLEMENTADO]` |
| administrativos | Administrativo | `ListaEnlazada<Administrativo>` | `list[Administrativo]` | `[IMPLEMENTADO]` |
| contratos | Contrato | `ListaEnlazada<Contrato>` | `list[Contrato]` | `[IMPLEMENTADO]` |
| matriculas | MatriculaAcademica | `ListaEnlazada<MatriculaAcademica>` | `list[MatriculaAcademica]` | `[IMPLEMENTADO]` |
| liquidaciones | LiquidacionNomina | `ListaEnlazada<LiquidacionNomina>` | `list[LiquidacionNomina]` | `[IMPLEMENTADO]` |
| parametros | ParametroNormativo | `ListaEnlazada<ParametroNormativo>` | `list[ParametroNormativo]` | `[IMPLEMENTADO]` |

## 8.3 Justificación del uso de listas

Las listas permiten:

- Insertar nuevos registros.
- Recorrer colecciones secuencialmente.
- Localizar objetos por identificador o código.
- Modificar objetos encontrados.
- Eliminar o desactivar registros.
- Representar detalles dependientes dentro de matrículas y liquidaciones.

En una implementación básica, la búsqueda por identificador tiene complejidad aproximada `O(n)`. Para el propósito académico, esta complejidad es aceptable y permite evidenciar el funcionamiento de las listas.

## 8.4 Complejidad esperada

| Operación | Complejidad aproximada | Observación |
|---|---|---|
| Agregar al final | `O(1)` | Depende de la estructura y referencia disponible. |
| Buscar por ID | `O(n)` | Requiere recorrido secuencial. |
| Modificar | `O(n)` | Primero se busca el registro. |
| Desactivar | `O(n)` | Primero se busca el registro. |
| Validar duplicado | `O(n)` | Se compara con elementos existentes. |
| Listar | `O(n)` | Se visitan todos los registros. |
| Guardar | `O(n)` | Cada registro se serializa una vez. |

---

# 9. Modelo de dominio

> `[IMPLEMENTADO]` El modelo de dominio está implementado en ambos lenguajes con las mismas **30 entidades**: en Python como `@dataclass` en `dominio/modelo_datos.py`, y en C++ como `struct` en `cpp/dominio/modelo_datos.h`. Todos los atributos son opcionales por defecto (en Python, `| None = None`), lo que permite construcción incremental y carga tolerante. Los valores monetarios y notas usan `Decimal` en Python para precisión decimal exacta.

## 9.0 Inventario verificado de entidades

| Entidad | Atributos | Grupo |
|---|---|---|
| Universidad | 14 | Institucional |
| Facultad | 11 | Institucional |
| ProgramaAcademico | 12 | Institucional |
| PlanEstudio | 9 | Institucional |
| DetallePlanEstudio | 8 | Institucional |
| Curso | 11 | Institucional |
| Prerrequisito | 7 | Institucional |
| PeriodoAcademico | 11 | Institucional |
| Persona | 15 | Personas |
| Estudiante | 11 | Personas |
| Profesor | 58 | Personas |
| Administrativo | 10 | Personas |
| OfertaCurso | 12 | Académica |
| AsignacionDocente | 8 | Académica |
| Horario | 9 | Académica |
| MatriculaAcademica | 8 | Académica |
| DetalleMatricula | 9 | Académica |
| Evaluacion | 8 | Académica |
| Calificacion | 7 | Académica |
| AlertaAcademica | 11 | Académica |
| Contrato | 82 | Contratación |
| CategoriaDocente | 24 | Contratación |
| FactorSalarial | 32 | Contratación |
| ProduccionAcademica | 37 | Contratación |
| PeriodoNomina | 25 | Nómina |
| LiquidacionNomina | 77 | Nómina |
| ConceptoNomina | 33 | Nómina |
| DetalleLiquidacion | 25 | Nómina |
| ParametroNormativo | 13 | Configuración |
| ArchivoPersistencia | 10 | Configuración |

Las entidades con más atributos (Profesor, Contrato, LiquidacionNomina, ProduccionAcademica) concentran la trazabilidad normativa exigida por el enunciado: conservan los valores usados al momento de vincular o liquidar. El detalle atributo por atributo se llevará al diccionario de datos (anexo pendiente).

## 9.1 Entidades institucionales

### Universidad

Representa la institución principal.

El detalle atributo por atributo (tipo, ejemplo real y validación) está en el **diccionario de datos** (`docs/DICCIONARIO_DE_DATOS.md`).

### Facultad

Representa una unidad académica asociada a la universidad.

El detalle atributo por atributo (tipo, ejemplo real y validación) está en el **diccionario de datos** (`docs/DICCIONARIO_DE_DATOS.md`).

### ProgramaAcademico

Representa un programa adscrito a una facultad.

El detalle atributo por atributo (tipo, ejemplo real y validación) está en el **diccionario de datos** (`docs/DICCIONARIO_DE_DATOS.md`).

### PlanEstudio

Representa una versión del plan curricular de un programa.

El detalle atributo por atributo (tipo, ejemplo real y validación) está en el **diccionario de datos** (`docs/DICCIONARIO_DE_DATOS.md`).

### DetallePlanEstudio

Relaciona un curso con un plan de estudio.

El detalle atributo por atributo (tipo, ejemplo real y validación) está en el **diccionario de datos** (`docs/DICCIONARIO_DE_DATOS.md`).

### Curso

Representa una asignatura institucional.

El detalle atributo por atributo (tipo, ejemplo real y validación) está en el **diccionario de datos** (`docs/DICCIONARIO_DE_DATOS.md`).

### Prerrequisito

Relaciona un curso con los requisitos necesarios para matricularlo.

El detalle atributo por atributo (tipo, ejemplo real y validación) está en el **diccionario de datos** (`docs/DICCIONARIO_DE_DATOS.md`).

### PeriodoAcademico

Representa un periodo institucional con fechas de inicio, finalización, matrícula y cancelación.

## 9.2 Entidades de personas

### Persona

Centraliza la información común para evitar duplicación.

`[IMPLEMENTADO]` El código separa el nombre en cuatro campos (el diseño conceptual decía "nombres" y "apellidos"): primerNombre, segundoNombre, primerApellido y segundoApellido. El detalle atributo por atributo está en el **diccionario de datos**.

### Estudiante

Representa el rol académico de una persona.

El detalle atributo por atributo (tipo, ejemplo real y validación) está en el **diccionario de datos** (`docs/DICCIONARIO_DE_DATOS.md`).

### Profesor

Representa el rol docente de una persona y conserva información académica, contractual y salarial necesaria para su vinculación.

> `[IMPLEMENTADO]` La duda conceptual se resolvió así: Profesor quedó como una entidad amplia de **58 atributos**, todos opcionales. Agrupa: identificación y vínculo (código, programa principal, tipo, dedicación, régimen), carrera docente, categoría y reconocimiento, investigación (grupo, semillero, productividad), posgrado y su bonificación, y experiencia certificada con puntos reconocidos. Al ser todos opcionales, cada modalidad de profesor usa solo el subconjunto que le aplica.

### Administrativo

Representa el rol administrativo de una persona.

El detalle atributo por atributo (tipo, ejemplo real y validación) está en el **diccionario de datos** (`docs/DICCIONARIO_DE_DATOS.md`).

## 9.3 Entidades académicas

### OfertaCurso

Representa la apertura de un curso para un periodo y grupo específicos.

### AsignacionDocente

Relaciona profesores con ofertas de curso.

### Horario

Representa día, intervalo, aula, sede y tipo de sesión.

### MatriculaAcademica

Agrupa la matrícula de un estudiante durante un periodo.

### DetalleMatricula

Representa cada oferta incluida en una matrícula.

### Evaluacion

Define actividades evaluativas y su porcentaje.

### Calificacion

Registra la nota obtenida por un estudiante en una evaluación.

### AlertaAcademica

Registra alertas derivadas del promedio u otras condiciones académicas.

## 9.4 Entidades de contratación

- **Contrato:** vínculo laboral de una persona; conserva modalidad, categoría, dedicación, vigencia y los valores pactados al momento de la vinculación.
- **CategoriaDocente:** clasificación escalafonaria del profesor (auxiliar, asistente, asociado, titular) según Decreto 1279.
- **FactorSalarial:** factor de puntos o porcentaje aplicable según categoría y dedicación.
- **ProduccionAcademica:** producción intelectual del profesor (artículos, libros, ponencias) usada en la valoración de méritos.

## 9.5 Entidades de nómina

- **PeriodoNomina:** mes o periodo de pago con su estado (abierto/cerrado) y valores de referencia vigentes.
- **LiquidacionNomina:** resultado de liquidar a una persona en un periodo; conserva los parámetros utilizados para trazabilidad (RF-14).
- **ConceptoNomina:** tipo de devengado o deducción (salario, auxilio, salud, pensión, bonificaciones).
- **DetalleLiquidacion:** cada renglón de la liquidación con su concepto, base, porcentaje y valor.

## 9.6 Entidades de configuración y persistencia

- **ParametroNormativo:** valor normativo con vigencia (salario mínimo, valor hora cátedra, umbrales EBRA, topes); el sistema siempre aplica el vigente en la fecha de la operación.
- **ArchivoPersistencia:** metadatos de cada archivo de datos (nombre, entidad asociada, orden de campos) para carga y guardado tolerante.

> `[IMPLEMENTADO]` El diccionario de datos existe como documento independiente: **`docs/DICCIONARIO_DE_DATOS.md`**. Se genera automáticamente con `docs/generar_diccionario.py` desde `dominio/modelo_datos.py` y los datos reales de `datos/upc/` (607 atributos en 30 entidades), por lo que siempre corresponde al código. Cada atributo documenta tipo, ejemplo real tomado del primer registro del tenant UPC y la regla de validación verificada en los gestores (rango de notas 0–5, porcentajes que suman 100, topes de horas por modalidad, unicidad de IDs, integridad referencial, etc.).

---

# 10. Relaciones entre entidades

| Origen | Destino | Cardinalidad | Resolución |
|---|---|---|---|
| Universidad | Facultad | 1 a N | idUniversidad en Facultad. |
| Facultad | ProgramaAcademico | 1 a N | idFacultad en ProgramaAcademico. |
| ProgramaAcademico | PlanEstudio | 1 a N | idPrograma en PlanEstudio. |
| PlanEstudio | Curso | N a M | DetallePlanEstudio. |
| Persona | Estudiante | 1 a 0..1 | idPersona en Estudiante. |
| Persona | Profesor | 1 a 0..1 | idPersona en Profesor. |
| Persona | Administrativo | 1 a 0..1 | idPersona en Administrativo. |
| PeriodoAcademico | OfertaCurso | 1 a N | idPeriodo en OfertaCurso. |
| Profesor | OfertaCurso | N a M | AsignacionDocente. |
| Estudiante | OfertaCurso | N a M | MatriculaAcademica y DetalleMatricula. |
| OfertaCurso | Evaluacion | 1 a N | idOfertaCurso en Evaluacion. |
| Evaluacion | Calificacion | 1 a N | idEvaluacion en Calificacion. |
| Estudiante | AlertaAcademica | 1 a N | idEstudiante en AlertaAcademica. |
| Profesor | Contrato | 1 a N | idProfesor o idPersona en Contrato. |
| Profesor | LiquidacionNomina | 1 a N | idProfesor en LiquidacionNomina. |
| Contrato | LiquidacionNomina | 1 a N | idContrato en LiquidacionNomina. |
| PeriodoNomina | LiquidacionNomina | 1 a N | idPeriodoNomina en LiquidacionNomina. |
| LiquidacionNomina | ConceptoNomina | N a M | DetalleLiquidacion. |

> `[IMPLEMENTADO]` Confirmado en el código: **Contrato referencia a la persona** mediante `idPersona` (no existe `idProfesor` en Contrato). En cambio, `LiquidacionNomina` conserva ambas referencias: `idProfesor` e `idContrato`. Además, Contrato incluye `idUniversidad`, coherente con el aislamiento multi-tenancy.

---

# 11. Enumeraciones y estados

> `[IMPLEMENTADO]` El código define **7 enumeraciones**, idénticas en ambos lenguajes: `enum class` en C++ y clases `str, Enum` en Python (heredan de `str` para serializar directamente a texto en los archivos de persistencia).

## 11.1 EstadoAcademico `[IMPLEMENTADO]`

- ASPIRANTE, ADMITIDO, MATRICULADO, ACTIVO, INACTIVO, RESERVA_CUPO, EBRA, GRADUADO, RETIRADO, SUSPENDIDO.

## 11.2 TipoProfesor `[IMPLEMENTADO]`

- PLANTA, OCASIONAL, CATEDRATICO, CATEDRATICO_AD_HONOREM.

## 11.3 Dedicacion `[IMPLEMENTADO]`

- TIEMPO_COMPLETO, MEDIO_TIEMPO, HORA_CATEDRA.

## 11.4 EstadoCurso `[IMPLEMENTADO]`

- MATRICULADO, EN_CURSO, CANCELADO, APROBADO, REPROBADO, RETIRADO, HOMOLOGADO, VALIDADO.

## 11.5 CategoriaDocenteCodigo `[IMPLEMENTADO]`

- AUXILIAR, ASISTENTE, ASOCIADO, TITULAR, NO_CATEGORIZADO.

## 11.6 TipoFactor `[IMPLEMENTADO]`

Enum adicional respecto al diseño conceptual; clasifica los factores salariales del profesor de planta:

- TITULO_ACADEMICO, CATEGORIA_DOCENTE, EXPERIENCIA, PRODUCTIVIDAD_ACADEMICA, DIRECCION_ACADEMICO_ADMINISTRATIVA, DESEMPENO_DESTACADO, POSGRADO, GRUPO_INVESTIGACION, SEMILLERO.

## 11.7 ParametroNormativoCodigo `[IMPLEMENTADO]`

Enum adicional que fija el catálogo de parámetros normativos reconocidos por el sistema (26 valores):

- Económicos: SALARIO_MINIMO, VALOR_PUNTO_SALARIAL, VALOR_AUXILIO_TRANSPORTE_VIGENTE, VALOR_HORA_CATEDRA.
- Seguridad social: PORCENTAJE_SALUD_TRABAJADOR, PORCENTAJE_SALUD_EMPLEADOR, PORCENTAJE_PENSION_TRABAJADOR, PORCENTAJE_PENSION_EMPLEADOR, PORCENTAJE_FONDO_SOLIDARIDAD, PORCENTAJE_RIESGOS_LABORALES, PORCENTAJE_ARL_CLASE_I, PORCENTAJE_ARL_CLASE_II.
- Parafiscales: PORCENTAJE_CAJA_COMPENSACION, PORCENTAJE_SENA, PORCENTAJE_ICBF.
- Bonificación por servicios: TOPE_BONIFICACION_SERVICIOS, PORCENTAJE_BONIFICACION_SERVICIOS_HASTA_TOPE, PORCENTAJE_BONIFICACION_SERVICIOS_SOBRE_TOPE.
- Impuestos: PORCENTAJE_RETENCION_FUENTE, BASE_MINIMA_RETENCION_FUENTE, PORCENTAJE_ESTAMPILLA, RETENCION_FUENTE_SALARIO.
- Académicos: NOTA_MINIMA_APROBATORIA, PROMEDIO_MINIMO_EBRA, MAXIMO_CREDITOS_PERIODO.
- Institucional: APLICA_EXONERACION_LEY_1819.

## 11.8 Nota sobre el estado de los registros

El `EstadoRegistro` conceptual (ACTIVO / INACTIVO / ELIMINADO_LOGICO) **no existe como enum en el código**: el atributo `estado` de cada entidad es una cadena de texto libre. Formalizarlo como enumeración queda como mejora opcional para evitar valores inconsistentes en los archivos (sección 26.3).

---

# 12. Reglas de negocio

## 12.1 Reglas institucionales

1. Una facultad debe pertenecer a una universidad.
2. Un programa debe pertenecer a una facultad.
3. Un plan debe pertenecer a un programa.
4. Un curso puede participar en diferentes planes.
5. Los códigos institucionales deben ser únicos en su ámbito.
6. Un registro con historia debe desactivarse y no eliminarse físicamente.

## 12.2 Reglas de personas

1. El documento debe ser único.
2. Todo estudiante debe tener una persona asociada.
3. Todo profesor debe tener una persona asociada.
4. Todo administrativo debe tener una persona asociada.
5. Una persona puede tener varios roles.
6. Desactivar una persona no elimina sus operaciones históricas.

## 12.3 Reglas de matrícula `[IMPLEMENTADO]`

Verificado en `GestorMatriculas.matricular_curso` y `cancelar_curso` (`gestores/gestores_academicos.py`). El orden real de validación es:

1. El estudiante debe tener `estadoAcademico = ACTIVO`.
2. El periodo debe estar abierto para matrícula (validado por ventana de fechas).
3. La oferta debe estar activa.
4. Debe existir cupo disponible (`cupoDisponible > 0`).
5. No se puede matricular dos veces la misma oferta (salvo que la anterior esté CANCELADA).
6. El estudiante debe cumplir los prerrequisitos.
7. No debe superarse el máximo de créditos (parámetro `MAXIMO_CREDITOS_PERIODO`).
8. No deben existir cruces de horario.
9. Al matricular se crea el detalle con estado MATRICULADO y **se disminuye el cupo en 1**.
10. Al cancelar: el motivo es **obligatorio**, no puede superarse la `fechaLimiteCancelacion`, el detalle pasa a CANCELADO (se conserva la historia) y **se libera el cupo**.

Detalle de implementación: si el estudiante no tiene matrícula en el periodo, se crea automáticamente (`_obtener_o_crear_matricula`).

## 12.4 Reglas de evaluaciones y calificaciones `[IMPLEMENTADO]`

Verificado en `GestorCalificaciones.registrar_calificacion` y `recalcular_nota_final`:

1. La nota debe estar entre **0 y 5** (escala fija en el código).
2. Los porcentajes de las evaluaciones activas deben sumar **exactamente 100** para poder calcular la nota final.
3. No se pueden registrar notas en matrículas CANCELADAS o RETIRADAS, ni en evaluaciones inactivas.
4. La evaluación debe pertenecer a la oferta del curso matriculado.
5. Si ya existe calificación para esa evaluación, se **actualiza** en lugar de duplicarse.
6. La nota final solo se recalcula cuando **todas** las evaluaciones activas tienen nota.
7. Al calcularse la nota final, el detalle pasa a APROBADO o REPROBADO según la `notaMinimaAprobatoria` del curso (por defecto **3.0**).
8. Cadena de recálculo en cascada: nota final → promedio del periodo → promedio acumulado → evaluación EBRA.

### Fórmula de nota final `[IMPLEMENTADO]`

```text
notaFinal = suma(notaEvaluacion * porcentajeEvaluacion / 100)
```

> **Resuelto:** el porcentaje se almacena en escala **0 a 100** (no 0–1). La nota final y los promedios se redondean a 2 decimales (`quantize 0.01`).

### Promedio del periodo

```text
promedioPeriodo =
    suma(notaFinalCurso * creditosCurso)
    / suma(creditosCurso)
```

### Promedio acumulado

```text
promedioAcumulado =
    suma(notaFinalHistorica * creditosCurso)
    / suma(creditosHistoricosConNota)
```

## 12.5 Regla EBRA `[IMPLEMENTADO]`

Verificado en `GestorMatriculas.evaluar_ebra`:

```text
si promedioAcumulado < PROMEDIO_MINIMO_EBRA (parámetro vigente):
    estadoAcademico = EBRA
    generar AlertaAcademica (tipoAlerta="EBRA", con valorObservado y valorLimite)
```

Detalles reales:

- El umbral se toma del parámetro `PROMEDIO_MINIMO_EBRA`; si el parámetro no existe o el estudiante no tiene promedio, no se genera alerta.
- **No se duplican alertas**: si ya existe una alerta EBRA no atendida, se retorna la existente.
- La alerta se genera también de forma masiva por periodo con `evaluar_alertas_periodo`.

## 12.6 Reglas generales de contratación

1. Todo vínculo debe identificar modalidad, fechas, dedicación, categoría y estado.
2. La categoría usada para pagar debe ser la vigente durante el contrato.
3. El contrato debe conservar los datos usados en su formalización.
4. Un contrato cerrado no se modifica directamente.
5. La terminación debe registrar fecha, causal y soporte.
6. Un contrato histórico no debe eliminarse físicamente.

## 12.7 Reglas por tipo de profesor

### Validaciones de contrato `[IMPLEMENTADO]`

Verificado en `GestorContratos.validar_contrato`:

- Las horas semanales no pueden ser negativas y la fecha de fin no puede preceder a la de inicio.
- **Catedrático**: máximo **18 horas semanales** (`HORAS_MAXIMAS_CATEDRATICO`), sumando los contratos activos del mismo tipo.
- **Administrativo catedrático ad honorem**: máximo **8 horas semanales**.
- **Ocasional**: solo dedicación TIEMPO_COMPLETO o MEDIO_TIEMPO, y duración **menor a 12 meses**.
- **Jubilados**: no pueden vincularse como ocasionales ni de planta.

### Profesor de planta `[IMPLEMENTADO]`

Verificado en `LiquidadorPlanta` y `GestorNomina._puntos_planta` (régimen Decreto 1279 de 2002):

- La remuneración depende de puntos salariales. Los puntos se obtienen así, en orden de prioridad:
  1. Si el profesor tiene `puntosSalariales` registrados, se usan directamente.
  2. Si no, tabla de escalafón por categoría: con categoría reconocida AUXILIAR 180 / ASISTENTE 250 / ASOCIADO 350 / TITULAR 450; sin reconocer 37 / 58 / 74 / 96.
  3. Si existen factores o producciones registradas, se calculan con `GestorFactores.calcular_puntos_profesor` y se toma el mayor entre el escalafón y el calculado.
- La dedicación aplica factor proporcional: TIEMPO_COMPLETO = 1, MEDIO_TIEMPO = 0.5 (otra dedicación genera error).
- El valor del punto se toma del periodo de nómina o del parámetro `VALOR_PUNTO_SALARIAL`.

```text
salarioBase = puntosSalariales * valorPuntoVigente * factorDedicacion
```

### Profesor ocasional `[IMPLEMENTADO]`

Verificado en `LiquidadorOcasional` (régimen Acuerdo 027 de 2024):

- La dedicación debe ser tiempo completo o medio tiempo; duración menor a un año (validado en `GestorContratos`).
- Factor por categoría a tiempo completo: TITULAR **3.918**, ASOCIADO **3.606**, ASISTENTE **3.125**, AUXILIAR **2.645** SMMLV. A medio tiempo, el factor se divide entre 2.
- Si el contrato tiene `salarioBase` pactado explícito, se respeta; si no, se calcula `SMMLV * factor`.
- Las horas incumplidas generan descuento sobre la base de cotización.

```text
salarioBase = salarioMinimoVigente * factorCategoriaDedicacion
descuentoIncumplimiento = horasIncumplidas * valorHoraIncumplida
ibc = salarioOrdinario - descuentoIncumplimiento
```

### Profesor catedrático `[IMPLEMENTADO]`

Verificado en `LiquidadorCatedratico` (Acuerdo 027 de 2024):

- Máximo 18 horas semanales (validado en `GestorContratos`).
- Horas mensuales asignadas: las del contrato, o `horasSemanales * 4` (12 por defecto).
- Solo se pagan horas reconocidas y cumplidas: `horasPagables = min(asignadas, cumplidas)`.
- El valor de la hora se toma del contrato (`valorHoraCatedraVigente` o `valorHora`); si no, se deriva del salario base, y en último caso del parámetro `VALOR_HORA_CATEDRA` (defecto 38 500).

```text
horasPagables = min(horasMensualesAsignadas, horasMensualesCumplidas)
salarioBaseCatedra = horasPagables * valorHoraCatedraVigente
```

### Profesor ad honorem `[IMPLEMENTADO]`

Se procesa con el mismo liquidador de cátedra: si el contrato tiene `esAdHonorem = true` o la modalidad es AD_HONOREM, el salario base se fuerza a **cero** (valorHora = 0, netoPagar = 0).

### Personal administrativo `[IMPLEMENTADO]` — fuera del diseño conceptual

Existe además `LiquidadorAdministrativo` (Código Sustantivo del Trabajo y Ley 100 de 1993), no contemplado en el modelo conceptual, que liquida empleados administrativos con su propio régimen.

---

# 13. Diseño conceptual de nómina

> **Advertencia académica:** este módulo representa una simulación. Los porcentajes, topes, valores y condiciones deben parametrizarse y verificarse con las fuentes oficiales y actos institucionales vigentes antes de cualquier uso diferente al ejercicio académico.

## 13.1 Entradas

- Profesor.
- Contrato vigente.
- Tipo de profesor.
- Categoría.
- Dedicación.
- Puntos salariales.
- Horas asignadas.
- Horas cumplidas.
- Horas incumplidas.
- Días trabajados.
- Salario mínimo vigente.
- Valor del punto.
- Valor de hora cátedra.
- Porcentajes de salud y pensión.
- Tarifa de ARL.
- Porcentajes parafiscales.
- Auxilio de transporte.
- Bonificaciones aplicables.

## 13.2 Salidas

- Salario base.
- Salario ordinario.
- Bonificaciones salariales.
- Bonificaciones no salariales.
- Auxilio de transporte.
- Base de seguridad social.
- Base prestacional.
- Descuento de salud.
- Descuento de pensión.
- Fondo de solidaridad.
- Otros descuentos.
- Prestaciones.
- Aportes patronales.
- Total devengado.
- Total descuentos.
- Neto a pagar.
- Costo total para el empleador.

## 13.3 Fórmulas generales

```text
totalDevengado =
    salarioOrdinario
    + bonificacionesSalariales
    + bonificacionesNoSalariales
    + otrosDevengados
```

```text
totalDescuentos =
    descuentoSalud
    + descuentoPension
    + fondoSolidaridadPensional
    + retencionFuente
    + descuentoHorasIncumplidas
    + otrosDescuentos
```

```text
netoPagar = totalDevengado - totalDescuentos
```

```text
costoTotalEmpleador =
    totalDevengado
    + totalPrestaciones
    + totalAportesPatronales
```

## 13.4 Separación de bases

### Base de seguridad social

```text
baseSeguridadSocial = salarioOrdinario
```

La base excluye el auxilio de transporte y las bonificaciones no constitutivas de salario definidas en el modelo.

### Base prestacional

```text
baseLiquidacionPrestaciones =
    salarioOrdinario + auxilioTransporteAplicable
```

## 13.5 Descuentos del trabajador `[IMPLEMENTADO]`

Verificado en `CalculadoraDeducciones`. Todos los porcentajes se leen de parámetros vigentes; se indican los valores por defecto del código:

| Descuento | Porcentaje por defecto | Observación |
|---|---|---|
| Salud trabajador | 4 % del IBC | `PORCENTAJE_SALUD_TRABAJADOR`. |
| Pensión trabajador | 4 % del IBC | `PORCENTAJE_PENSION_TRABAJADOR`. |
| Fondo de solidaridad pensional | Según parámetro | Solo si IBC ≥ **4 SMMLV**; redondeo PILA al múltiplo de 100. |
| Retención en la fuente | Valor fijo o porcentaje | Si existe `RETENCION_FUENTE_SALARIO` se aplica ese valor; si no, se aplica el porcentaje cuando el IBC supera la `BASE_MINIMA_RETENCION_FUENTE` (defecto 4 500 000). |
| Estampilla pro-universidad | 0.2 % del salario base | `PORCENTAJE_ESTAMPILLA`; descuento institucional. |

## 13.6 Aportes del empleador `[IMPLEMENTADO]`

| Aporte | Porcentaje por defecto | Observación |
|---|---|---|
| Salud patronal | 8.5 % del IBC | El código documenta que las universidades públicas (como la UPC) **no son exoneradas** (Art. 114-1, par. 2, ET): `exonerado=False` por defecto. |
| Pensión patronal | 12 % del IBC | `PORCENTAJE_PENSION_EMPLEADOR`. |
| Riesgos laborales (ARL) | 0.522 % (clase I) | La tarifa depende de la clase ARL del contrato (`PORCENTAJE_ARL_CLASE_I`, `_II`, ...). |
| Caja de compensación | 4 % del IBC | `PORCENTAJE_CAJA_COMPENSACION`. |
| SENA | 2 % del IBC | Solo si IBC ≥ **10 SMMLV** (exoneración por debajo). |
| ICBF | 3 % del IBC | Solo si IBC ≥ **10 SMMLV**. |

> `[NORMA POR VERIFICAR]` La exoneración de SENA/ICBF implementada usa el umbral de 10 SMMLV; confirmar la interpretación normativa antes de un uso no académico.

## 13.7 Prestaciones y provisiones `[IMPLEMENTADO]`

Verificado en `CalculadoraPrestaciones.calcular_provisiones` (año comercial de 360 días):

**Régimen general** (ocasionales y administrativos):

```text
cesantias          = basePrestacional * dias / 360
interesesCesantias = cesantias * dias * 12 % / 360
primaServicios     = basePrestacional * dias / 360
vacaciones         = ibc * dias / 720
```

**Régimen especial** (profesores de planta, Decreto 1279, arts. 33, 39 y 46) agrega:

- **Bonificación por servicios**: 50 % si el IBC no supera el tope (`TOPE_BONIFICACION_SERVICIOS`, defecto 756 411) y 35 % por encima, prorrateado por días.
- **Vacaciones** con base especial: `ibc + primaServicios/12 + bonificacionServicios/12`, sobre 720.
- **Prima de vacaciones**: base con 2/3 del IBC, sobre 540.
- **Prima de Navidad**: base con IBC + primas y bonificación mensualizadas, sobre 360.

## 13.8 Bonificaciones `[IMPLEMENTADO]`

Verificado en `CalculadoraPrestaciones`. Ambas se calculan como factor del **SMMLV** y se prorratean por horas cuando aplica:

**Bonificación de posgrado** (no aplica a profesores de planta; se puede desactivar por contrato):

| Nivel | Factor sobre SMMLV |
|---|---|
| Doctorado | 0.90 |
| Maestría | 0.45 |
| Especialización | 0.10 |
| Postdoctorado | 0 (pendiente de definición) |

**Bonificación de investigación** (exige productividad o proyecto vigente **y** certificación de Vicerrectoría de Investigación):

| Categoría del grupo | Factor | | Categoría | Factor |
|---|---|---|---|---|
| A1 | 0.56 | | C | 0.38 |
| A | 0.47 | | Reconocido | 0.33 |
| B | 0.42 | | Semillero | 0.20 |

Cada liquidación registra los factores aplicados en `parametros_utilizados` (trazabilidad).

## 13.9 Ciclo de vida de la liquidación `[IMPLEMENTADO]`

Verificado en `GestorNomina` y `nomina/ciclo_vida_nomina.py`:

1. Se crean periodos de nómina mensuales (`crear_periodo_nomina_mensual`) y se abren.
2. Solo se liquida con el periodo **abierto**; no se permiten liquidaciones duplicadas por contrato y periodo.
3. La liquidación se **aprueba** (con usuario aprobador) y luego se **paga** (medio y referencia de pago).
4. Las correcciones se hacen por **reliquidación**: se crea una nueva versión vinculada a la original (`liquidacionOrigen`, `version`), sin modificar la historia.
5. Reportes: resumen por periodo, totales por tipo de profesor y desglose anual por contrato (`desglose_anual.py`).

---

# 14. Parámetros normativos

Los valores variables deben almacenarse mediante `ParametroNormativo`.

## 14.1 Atributos mínimos

- idParametro.
- codigo.
- nombre.
- descripcion.
- tipoDato.
- valor.
- unidad.
- normaOrigen.
- articulo.
- fechaInicioVigencia.
- fechaFinVigencia.
- aplicaA.
- estado.

## 14.2 Parámetros esperados

- SALARIO_MINIMO.
- VALOR_PUNTO_SALARIAL.
- VALOR_AUXILIO_TRANSPORTE_VIGENTE.
- VALOR_HORA_CATEDRA.
- PORCENTAJE_SALUD_TRABAJADOR.
- PORCENTAJE_SALUD_EMPLEADOR.
- PORCENTAJE_PENSION_TRABAJADOR.
- PORCENTAJE_PENSION_EMPLEADOR.
- PORCENTAJE_FONDO_SOLIDARIDAD.
- PORCENTAJE_RIESGOS_LABORALES.
- PORCENTAJE_CAJA_COMPENSACION.
- PORCENTAJE_SENA.
- PORCENTAJE_ICBF.
- PORCENTAJE_RETENCION_FUENTE.
- NOTA_MINIMA_APROBATORIA.
- PROMEDIO_MINIMO_EBRA.
- MAXIMO_CREDITOS_PERIODO.
- APLICA_EXONERACION_LEY_1819.

## 14.3 Reglas de validación `[IMPLEMENTADO]`

Verificado en `GestorParametros._validar` y `_validar_no_solapamiento`:

1. Código, valor y fecha de inicio de vigencia son obligatorios.
2. El valor debe ser numérico.
3. Los parámetros porcentuales (conjunto `PARAMETROS_PORCENTUALES`) deben estar entre **0 y 1** — esa es la convención confirmada.
4. Los parámetros monetarios (`PARAMETROS_MONETARIOS`) deben ser mayores que cero.
5. La fecha final debe ser posterior a la inicial.
6. **No se permiten vigencias activas superpuestas** para el mismo código (validación de intersección de intervalos).
7. Un parámetro usado en una liquidación tiene restricciones de modificación (`_esta_usado_en_liquidacion`), y cada liquidación conserva copia de los parámetros aplicados en `parametros_utilizados`.

---

# 15. Casos de uso

## 15.1 Catálogo resumido

| Código | Caso de uso | Actor principal |
|---|---|---|
| CU-01 | Gestionar facultades | Usuario administrativo |
| CU-02 | Gestionar programas | Usuario administrativo |
| CU-03 | Gestionar planes | Usuario académico |
| CU-04 | Gestionar cursos | Usuario académico |
| CU-05 | Gestionar estudiante | Usuario académico |
| CU-06 | Gestionar profesor | Usuario administrativo |
| CU-07 | Gestionar administrativo | Usuario administrativo |
| CU-08 | Crear periodo académico | Usuario académico |
| CU-09 | Crear oferta de curso | Usuario académico |
| CU-10 | Matricular curso | Usuario académico |
| CU-11 | Cancelar curso | Usuario académico |
| CU-12 | Registrar calificación | Profesor o usuario académico |
| CU-13 | Calcular promedio | Sistema |
| CU-14 | Generar alerta EBRA | Sistema |
| CU-15 | Registrar contrato | Usuario administrativo |
| CU-16 | Vincular profesor ocasional | Usuario administrativo |
| CU-17 | Vincular catedrático | Usuario administrativo |
| CU-18 | Terminar contrato | Usuario administrativo |
| CU-19 | Configurar parámetros | Usuario de nómina |
| CU-20 | Liquidar profesor de planta | Usuario de nómina |
| CU-21 | Liquidar profesor ocasional | Usuario de nómina |
| CU-22 | Liquidar catedrático | Usuario de nómina |
| CU-23 | Aplicar bonificación de posgrado | Sistema |
| CU-24 | Aplicar bonificación de investigación | Sistema |
| CU-25 | Cerrar nómina | Usuario de nómina |
| CU-26 | Consultar liquidación | Usuario administrativo |
| CU-27 | Cargar datos | Usuario |
| CU-28 | Guardar datos | Usuario |

## 15.2 CU-10: Matricular curso

### Actor

Usuario académico.

### Precondiciones

- Estudiante existente y activo.
- Periodo abierto.
- Oferta activa.

### Flujo principal `[IMPLEMENTADO]`

Orden real de validación en `GestorMatriculas.matricular_curso` (`gestores/gestores_academicos.py`), idéntico en C++:

1. Buscar el estudiante, la oferta, el periodo y el curso (referencia inexistente → error).
2. Validar que el estudiante esté **ACTIVO**.
3. Validar que el **periodo esté abierto** a la fecha de matrícula.
4. Validar que la **oferta esté activa**.
5. Validar **cupo disponible** (`cupoDisponible > 0`).
6. Obtener o crear la matrícula del periodo; validar que la oferta **no esté ya matriculada** (excluye detalles CANCELADO).
7. Validar **prerrequisitos** del curso.
8. Validar el **máximo de créditos** del periodo (parámetro `MAXIMO_CREDITOS_PERIODO`).
9. Validar **cruce de horario** con las demás ofertas matriculadas.
10. Crear el detalle de matrícula (estado MATRICULADO).
11. Disminuir el cupo disponible en 1 y actualizar `totalCreditos` de la matrícula.
12. Mostrar el resultado.

### Flujos alternos

- Estudiante inactivo.
- Periodo cerrado.
- Oferta sin cupo.
- Prerrequisito incumplido.
- Cruce de horario.
- Exceso de créditos.
- Oferta ya matriculada.

### Postcondición

La matrícula conserva el nuevo detalle y la oferta refleja el cupo actualizado.

## 15.3 CU-12: Registrar calificación

### Flujo principal

1. Seleccionar oferta.
2. Seleccionar evaluación.
3. Seleccionar estudiante matriculado.
4. Validar la escala.
5. Registrar la nota.
6. Recalcular la nota final.
7. Recalcular el promedio del periodo.
8. Recalcular el promedio acumulado.
9. Evaluar EBRA.

## 15.4 CU-21: Liquidar profesor ocasional

### Precondiciones

- Contrato ocasional activo.
- Periodo de nómina abierto.
- Parámetros vigentes.
- Novedades de cumplimiento registradas.

### Flujo resumido

1. Recuperar contrato.
2. Obtener categoría y dedicación.
3. Buscar SMMLV y factor vigentes.
4. Calcular salario base.
5. Descontar horas incumplidas.
6. Determinar auxilio aplicable.
7. Calcular bases.
8. Calcular descuentos.
9. Calcular aportes.
10. Calcular prestaciones.
11. Calcular bonificaciones.
12. Calcular neto y costo.
13. Crear la liquidación y sus detalles.

## 15.5 CU-27: Cargar datos

### Flujo principal

1. Preguntar si el usuario desea cargar datos.
2. Leer archivos hacia estructuras temporales.
3. Validar formato.
4. Validar identificadores.
5. Validar referencias.
6. Construir relaciones.
7. Reemplazar los datos en memoria solo si la carga completa es válida.
8. Informar cantidades y errores.

---

# 16. Operaciones CRUD y servicios

## 16.1 Operaciones generales

- `crear()`.
- `agregar()`.
- `buscarPorId()`.
- `buscarPorCodigo()`.
- `listar()`.
- `modificar()`.
- `desactivar()`.
- `reactivar()`.
- `eliminar()`.
- `validar()`.
- `guardar()`.
- `cargar()`.

## 16.2 Gestores reales `[IMPLEMENTADO]`

Los gestores existen como clases independientes (no hay una clase única `SistemaPITA`). Cada uno recibe en su constructor las listas que administra y lanza excepciones propias (`ErrorPersona`, `ErrorMatricula`, `ErrorCalificacion`, `ErrorContrato`, `ErrorParametro`, `ErrorFactor`, `ErrorPeriodo`, `ErrorAcademico`, todas derivadas de `ValueError`):

| Gestor | Archivo Python | Responsabilidad principal |
|---|---|---|
| GestorCRUD (genérico) | `persistencia/gestor_crud.py` | CRUD genérico reutilizable: crear, buscar por ID/código, listar, modificar, desactivar, reactivar, eliminar. |
| GestorPersonas | `gestores/gestor_personas.py` | Personas y roles (estudiante, profesor, administrativo); unicidad de documento. |
| GestorAcademico | `gestores/gestor_academico.py` | Planes de estudio, prerrequisitos, asignación docente y horarios. |
| GestorPeriodosAcademicos | `gestores/gestor_periodos.py` | Periodos: crear, abrir, cerrar, ofertas del periodo. |
| GestorMatriculas | `gestores/gestores_academicos.py` | Matrícula, cancelación, promedios y alertas EBRA. |
| GestorCalificaciones | `gestores/gestores_academicos.py` | Evaluaciones, calificaciones y nota final. |
| GestorContratos | `gestores/gestor_contratos.py` | Contratos: crear, validar por modalidad, terminar con causal y soporte. |
| GestorFactores | `gestores/gestor_factores.py` | Categorías, factores salariales, producciones académicas y cálculo de puntos. |
| GestorParametros | `gestores/gestor_parametros.py` | Parámetros normativos con vigencia y sin solapamiento. |
| GestorNomina | `nomina/gestor_nomina.py` | Liquidación por modalidad (sección 13). |
| GestorPersistencia | `persistencia/gestor_persistencia.py` | Carga/guardado y validación de integridad (sección 17). |
| GestorMultiTenancy | `persistencia/gestor_multi_tenancy.py` | Aislamiento por universidad (sección 17). |

En C++ existe el mismo conjunto de gestores bajo `cpp/gestores/` y `cpp/nomina/`.

---

# 17. Persistencia

> `[IMPLEMENTADO]` Sección verificada contra `persistencia/gestor_persistencia.py`, `persistencia/gestor_multi_tenancy.py`, `cpp/persistencia/gestor_persistencia.h/.cpp` y los archivos reales de `datos/`.

## 17.1 Organización real: multi-tenancy por universidad `[IMPLEMENTADO]`

A diferencia del diseño conceptual (una sola carpeta de datos), el sistema implementa **aislamiento por universidad**. Un archivo catálogo registra cada institución y sus datos viven en una subcarpeta propia:

```text
datos/
├── universidades.txt          # Catálogo maestro de tenants
├── upc/                       # Universidad Popular del Cesar
│   ├── universidad.txt
│   ├── facultades.txt
│   ├── programas.txt
│   ├── planes_estudio.txt
│   ├── detalles_plan_estudio.txt
│   ├── cursos.txt
│   ├── prerrequisitos.txt
│   ├── personas.txt
│   ├── estudiantes.txt
│   ├── profesores.txt
│   ├── administrativos.txt
│   ├── periodos_academicos.txt
│   ├── ofertas_curso.txt
│   ├── asignaciones_docentes.txt
│   ├── horarios.txt
│   ├── matriculas.txt
│   ├── detalles_matricula.txt
│   ├── evaluaciones.txt
│   ├── calificaciones.txt
│   ├── alertas_academicas.txt
│   ├── contratos.txt
│   ├── categorias_docentes.txt
│   ├── factores_salariales.txt
│   ├── producciones_academicas.txt
│   ├── periodos_nomina.txt
│   ├── liquidaciones_nomina.txt
│   ├── conceptos_nomina.txt
│   ├── detalles_liquidacion.txt
│   ├── parametros_normativos.txt
│   └── archivos_persistencia.txt
├── unal/                      # Universidad Nacional de Colombia (mismos 30 archivos)
└── unad_001/                  # UNAD (mismos 30 archivos)
```

### Catálogo de universidades

`universidades.txt` tiene 5 campos por línea:

```text
idUniversidad|codigo|nombre|directorio|estado
1|UPC|Universidad Popular del Cesar|upc|ACTIVO
2|UNAL|Universidad Nacional de Colombia|unal|ACTIVO
3|UNAD|Universidad Nacional Abierta y a Distancia|unad_001|ACTIVO
```

`GestorMultiTenancy` (`persistencia/gestor_multi_tenancy.py`) se encarga de:

- Cargar y guardar el catálogo; si no existe, crea uno por defecto con UPC y UNAL.
- Resolver un tenant por ID, código o nombre de carpeta.
- Registrar una nueva universidad: asigna ID correlativo, genera y valida un código único, crea su carpeta, la aprovisiona copiando los archivos de la plantilla (UPC) y escribe su `universidad.txt`.

## 17.2 Formato de archivo real `[IMPLEMENTADO]`

Un archivo por entidad, **sin encabezado**, un registro por línea. El orden de los campos es **el orden de declaración de los atributos** de la entidad (en Python se toma de la `dataclass`; en C++ el orden está fijado manualmente en el serializador). Ejemplo real de `personas.txt`:

```text
1|CC|12345678|Carlos|Alberto|Gomez|Solano|||3001234567||cgomez@unicesar.edu.co|Valledupar|2026-09-09|ACTIVO
```

### Convenciones verificadas

| Aspecto | Regla real |
|---|---|
| Delimitador | `\|` (constante `DELIMITADOR` en ambos lenguajes). |
| Valor ausente (`None`) | Campo vacío entre delimitadores. |
| Booleanos | `1` / `0`. |
| Fechas | ISO 8601: `AAAA-MM-DD`. |
| Horas | ISO 8601: `HH:MM:SS`. |
| Decimales | Punto como separador (`Decimal` en Python). |
| Enumeraciones | Su valor textual en mayúsculas (ej. `PLANTA`). |
| Codificación | UTF-8. |
| Delimitador dentro de un texto | Al guardar, cualquier `\|` dentro de un texto se reemplaza por `" - "`. |

> `[PENDIENTE DE VERIFICACIÓN]` El campo `parametros_utilizados` de `LiquidacionNomina` (un diccionario) se guarda con la representación de texto de Python (`{'CLAVE': 'valor', ...}`). Ese formato no es portable a C++ tal cual; si se requiere interoperabilidad de ese campo habrá que definir una codificación neutral.

## 17.3 Reglas de carga `[IMPLEMENTADO]`

1. Si el archivo de una entidad no existe, esa entidad carga como lista vacía (no es error).
2. Las líneas vacías se ignoran.
3. Si faltan campos al final de la línea y esos campos tienen valor por defecto, se rellenan como vacíos (compatibilidad con versiones anteriores del formato).
4. Si sobran campos, o faltan campos sin valor por defecto, la carga falla con un mensaje que incluye **archivo, número de línea y cantidad de campos esperada y recibida**.
5. Cada campo se convierte a su tipo declarado (`int`, `Decimal`, `date`, `time`, `bool`, enum); un valor inválido produce error controlado.
6. **Validación de integridad posterior a la carga** (`validar_integridad_datos`):
   - Identificadores duplicados en cualquier entidad → error.
   - Se verifican **35 referencias cruzadas** (por ejemplo `Facultad.idUniversidad → Universidad`, `DetalleMatricula.idOfertaCurso → OfertaCurso`, `LiquidacionNomina.idContrato → Contrato`).
   - Excepción tolerante: las referencias opcionales `idPlanEstudio`, `idPeriodo`, `idPeriodoAcademico` e `idProgramaPrincipal` que no existen se sanean a vacío en lugar de bloquear toda la carga.
7. Tras cargar, `reconstruir_relaciones` construye **índices en memoria** (diccionarios por ID y agrupaciones) para navegar las relaciones sin búsquedas repetidas: facultad por programa, persona por profesor, detalles por matrícula, evaluaciones por oferta, etc.

## 17.4 Reglas de guardado `[IMPLEMENTADO]`

1. Un archivo por entidad, en el orden de campos declarado.
2. Se reescribe el archivo completo con el contenido actual en memoria.
3. Cada valor se serializa con las convenciones de 17.2.

> `[IMPLEMENTACIÓN PARCIAL]` El diseño conceptual pedía escribir primero en un archivo temporal y reemplazar de forma controlada (guardado atómico). El código actual escribe directamente sobre el archivo destino; el guardado atómico queda como mejora pendiente.

---

# 18. Diseño para C++

## 18.1 Enfoque propuesto

- Clases o estructuras para entidades. `[IMPLEMENTADO]` como `struct` con atributos `std::optional`.
- ~~`std::list<T>`~~ `ListaEnlazada<T>` propia como colección principal `[IMPLEMENTADO]` (decisión ajustada al enunciado del taller: estructura de datos implementada a mano).
- `enum class` para valores controlados. `[IMPLEMENTADO]` (7 enumeraciones).
- Identificadores para relaciones. `[IMPLEMENTADO]`
- `fstream` para persistencia. `[IMPLEMENTADO]`
- Funciones separadas de validación. `[IMPLEMENTADO]` (métodos `validar*` en los gestores).

## 18.2 Fragmentos reales del código `[IMPLEMENTADO]`

Las entidades son `struct` con atributos `std::optional` (dominio/`modelo_datos.h`). Ejemplo real:

```cpp
struct MatriculaAcademica {
    std::optional<int> idMatricula;
    std::optional<int> idEstudiante;
    std::optional<int> idPeriodo;
    std::optional<std::string> fechaMatricula;
    std::optional<int> totalCreditos;
    std::optional<double> promedioPeriodo;
    std::optional<std::string> estadoMatricula;
    std::optional<std::string> observaciones;
};

struct DetalleMatricula {
    std::optional<int> idDetalleMatricula;
    std::optional<int> idMatricula;
    std::optional<int> idOfertaCurso;
    std::optional<std::string> fechaInscripcion;
    std::optional<EstadoCurso> estadoCurso;
    std::optional<double> notaFinal;
    std::optional<int> numeroFallas;
    std::optional<std::string> fechaCancelacion;
    std::optional<std::string> motivoCancelacion;
};
```

Diferencias frente al diseño conceptual, ya verificadas:

- **No hay listas embebidas dentro de las entidades**: los detalles (`DetalleMatricula`, `DetalleLiquidacion`) son entidades independientes relacionadas por identificador, lo que facilita la persistencia en archivos planos.
- La colección principal **no es `std::list`** sino la lista doblemente enlazada propia `ListaEnlazada<T>` (`dominio/lista_enlazada.h`, con `Nodo<T>` e iteradores bidireccionales), requisito central del taller.
- Todos los atributos son opcionales (`std::optional`), lo que permite serializar campos vacíos como `None` en el archivo de texto.

## 18.3 Estructura de archivos C++

`[IMPLEMENTADO]` Verificado contra el repositorio (directorio `cpp/` y `cpp/CMakeLists.txt`).

```text
cpp/
├── CMakeLists.txt              # Proyecto "PITA" v2.0.0, C++17, compilación con CMake
├── main.cpp                    # Punto de entrada CLI (ejecutable pita_backend)
├── dominio/
│   ├── modelo_datos.h          # Entidades y enumeraciones del dominio
│   └── lista_enlazada.h        # Estructura de lista enlazada propia
├── persistencia/
│   ├── gestor_persistencia.h/.cpp
│   └── gestor_crud.h
├── gestores/
│   ├── gestor_personas.h/.cpp
│   ├── gestor_academico.h/.cpp
│   ├── gestores_academicos.h/.cpp
│   ├── gestor_contratos.h/.cpp
│   ├── gestor_parametros.h/.cpp
│   ├── gestor_periodos.h/.cpp
│   └── gestor_factores.h/.cpp
├── nomina/
│   ├── gestor_nomina.h/.cpp
│   ├── calculadora_deducciones.h/.cpp
│   ├── calculadora_prestaciones.h/.cpp
│   └── desglose_anual.h/.cpp
├── gui/                        # GUI con Dear ImGui + GLFW (OpenGL3)
│   ├── gui_main.cpp
│   ├── gui_app.h/.cpp
│   ├── gui_controller.h/.cpp
│   ├── gui_vista_personas.cpp
│   ├── gui_vista_facultades.cpp
│   ├── gui_vista_academica.cpp
│   ├── gui_vista_contratos.cpp
│   ├── gui_vista_nomina.cpp
│   ├── gui_vista_parametros.cpp
│   └── tema.h
└── datos/                      # Archivos de persistencia .txt (una carpeta por defecto)
```

### Objetivos de compilación definidos en CMake

| Objetivo | Tipo | Contenido |
|---|---|---|
| `pita_lib` | Biblioteca estática | Backend: persistencia, gestores y nómina. |
| `pita_backend` | Ejecutable CLI | `main.cpp`, enlazado con `pita_lib`. |
| `imgui_lib` | Biblioteca estática | Dear ImGui v1.91.5 con backends GLFW y OpenGL3. |
| `pita_gui` | Ejecutable gráfico | Vistas de `gui/`, enlazado con `pita_lib` e `imgui_lib`. |

Las dependencias gráficas (GLFW 3.4 y Dear ImGui v1.91.5) se descargan automáticamente mediante `FetchContent` de CMake. El estándar configurado es **C++17**, con `/W3 /EHsc /utf-8` en MSVC o `-Wall -Wextra -pedantic` en otros compiladores.

## 18.4 Menú C++ `[IMPLEMENTADO]`

El ejecutable CLI `pita_backend` (`cpp/main.cpp`) **no es un menú interactivo**: es un programa de verificación por fases que carga la persistencia, valida integridad referencial, instancia los gestores y ejecuta pruebas de reglas de negocio con resultados esperados (SMMLV vigente, puntos Decreto 1279, EBRA, reglas de contratos, liquidación de nómina). Su flujo:

```text
[1/4] Cargar persistencia y validar integridad referencial (28 conteos por entidad)
[2/4] Instanciar gestores de negocio
[3/4] Verificar reglas académicas y normativas (SMMLV, valor punto, EBRA, contratos)
[4/5] Verificar reglas Decreto 1279 y Acuerdo 027 (puntos, aislamiento de régimen, bonificaciones)
[5/5] Ejecutar motor de nómina y liquidación
```

La interacción con el usuario en C++ está en el ejecutable **`pita_gui`** (Dear ImGui + GLFW): ventana principal con barra de estado y vistas por módulo (`gui/gui_vista_*.cpp`: personas, facultades, académica, contratos, nómina y parámetros).

## 18.5 Funciones C++ implementadas `[IMPLEMENTADO]`

Selección de funciones reales verificadas en los encabezados de `cpp/`:

| Función | Responsabilidad | Archivo |
|---|---|---|
| `GestorPersistencia::cargarTodosLosDatos` | Carga las 30 entidades y valida integridad referencial. | `persistencia/gestor_persistencia.h/.cpp` |
| `GestorParametros::obtenerParametroVigente` | Devuelve el valor vigente de un parámetro por código y fecha. | `gestores/gestor_parametros.h` |
| `GestorParametros::validarNoSolapamiento` | Impide vigencias superpuestas para el mismo parámetro. | `gestores/gestor_parametros.h` |
| `GestorMatriculas::matricularCurso` / `cancelarCurso` | Matrícula con 8 validaciones ordenadas; cancelación con motivo y liberación de cupo. | `gestores/gestores_academicos.h/.cpp` |
| `GestorMatriculas::calcularPromedioPeriodo` / `calcularPromedioAcumulado` | Promedios ponderados por créditos. | `gestores/gestores_academicos.h/.cpp` |
| `GestorMatriculas::evaluarEbra` | Genera `AlertaAcademica` si el promedio cae bajo el parámetro EBRA. | `gestores/gestores_academicos.h/.cpp` |
| `GestorCalificaciones::recalcularNotaFinal` | Nota final ponderada; exige porcentajes que sumen 100. | `gestores/gestores_academicos.h/.cpp` |
| `GestorContratos::validarContrato` | Reglas por modalidad (cátedra ≤ 18 h, ocasional < 12 meses, ad honorem, jubilados). | `gestores/gestor_contratos.h` |
| `GestorFactores::calcularPuntosProfesor` | Puntos salariales Decreto 1279 con aislamiento de régimen. | `gestores/gestor_factores.h` |
| `GestorNomina::liquidarProfesorPlanta` | Liquidación por puntos (planta) con deducciones y aportes. | `nomina/gestor_nomina.h/.cpp` |
| `GestorNomina::desgloseNominaAnual` / `resumenNominaAnual` | Proyección anual por contrato y consolidado institucional. | `nomina/gestor_nomina.h/.cpp`, `nomina/desglose_anual.h/.cpp` |
| `CalculadoraDeducciones` / `CalculadoraPrestaciones` | Deducciones de ley, aportes patronales, prestaciones y bonificaciones. | `nomina/calculadora_deducciones.h/.cpp`, `nomina/calculadora_prestaciones.h/.cpp` |

---

# 19. Diseño para Python

## 19.1 Enfoque propuesto

- Clases o `dataclass` para entidades.
- Listas nativas.
- `Enum` para valores controlados.
- Identificadores para relaciones.
- `open()` y procesamiento delimitado para persistencia.
- Excepciones controladas para validación.

## 19.2 Fragmentos reales del código `[IMPLEMENTADO]`

Las entidades son `@dataclass` con todos los atributos opcionales (`| None = None`), en `dominio/modelo_datos.py`. Ejemplo real:

```python
@dataclass
class MatriculaAcademica:
    idMatricula: int | None = None
    idEstudiante: int | None = None
    idPeriodo: int | None = None
    fechaMatricula: date | None = None
    totalCreditos: int | None = None
    promedioPeriodo: Decimal | None = None
    estadoMatricula: str | None = None
    observaciones: str | None = None


@dataclass
class DetalleMatricula:
    idDetalleMatricula: int | None = None
    idMatricula: int | None = None
    idOfertaCurso: int | None = None
    fechaInscripcion: date | None = None
    estadoCurso: EstadoCurso | None = None
    notaFinal: Decimal | None = None
    numeroFallas: int | None = None
    fechaCancelacion: date | None = None
    motivoCancelacion: str | None = None
```

Diferencias frente al diseño conceptual, ya verificadas:

- Los nombres de atributo usan **camelCase** (no snake_case), igual que en C++, para que ambas implementaciones compartan exactamente el orden de columnas de los archivos `.txt`.
- Los detalles son entidades independientes relacionadas por identificador, no listas embebidas.
- Los valores monetarios y notas usan `Decimal`; las fechas, `date`; y los valores controlados, los `Enum` de la sección 11.

## 19.3 Estructura de archivos Python

`[IMPLEMENTADO]` Verificado contra el repositorio.

```text
Taller/
├── main.py                     # Punto de entrada: arranca la GUI por defecto
├── gui_main.py                 # Lanza PITAApplication (CustomTkinter)
├── requirements.txt            # Dependencias Python
├── dominio/
│   └── modelo_datos.py         # Entidades y enumeraciones (dataclasses + Enum)
├── persistencia/
│   ├── gestor_persistencia.py  # Carga/guardado de archivos .txt delimitados
│   ├── gestor_crud.py          # Operaciones CRUD genéricas
│   └── gestor_multi_tenancy.py # Aislamiento de datos por universidad
├── gestores/
│   ├── gestor_personas.py
│   ├── gestor_academico.py
│   ├── gestores_academicos.py
│   ├── gestor_contratos.py
│   ├── gestor_parametros.py
│   ├── gestor_periodos.py
│   └── gestor_factores.py
├── nomina/
│   ├── gestor_nomina.py
│   ├── calculadora_deducciones.py
│   ├── calculadora_prestaciones.py
│   ├── liquidadores.py
│   ├── ciclo_vida_nomina.py
│   ├── desglose_anual.py
│   └── excepciones.py
├── ui_gui/                     # GUI con CustomTkinter (estilo Windows 11 Light)
│   ├── gui_app.py              # PITAApplication (ventana raíz)
│   ├── gui_controller.py       # PITAController
│   ├── theme.py, components.py
│   ├── view_dashboard_gui.py, view_personas_gui.py, view_facultades_gui.py,
│   ├── view_academica_gui.py, view_contratos_gui.py, view_nomina_gui.py,
│   ├── view_parametros_gui.py
│   ├── personas/               # Submódulo: tabs, diálogos y servicio de personas
│   ├── contratos/              # Submódulo: tabs, diálogos, KPIs y servicio de contratos
│   └── academica/              # Submódulo: tabs, diálogos y servicio académico
├── datos/
│   ├── universidades.txt       # Catálogo multi-tenancy
│   ├── upc/                    # Datos de la UPC
│   ├── unal/                   # Datos de la UNAL
│   └── unad_001/               # Datos de la UNAD
└── tests/ (archivos sueltos en raíz)
    ├── test_pita.py
    ├── test_multi_universidades.py
    ├── test_aislamiento_universidades.py
    ├── test_puntos_doctorado_nomina.py
    └── test_rubric_corrections.py
```

### Hechos confirmados en el código

- La interfaz gráfica Python usa **CustomTkinter** (`ui_gui/gui_app.py`, clase `PITAApplication`, título "PITA v2.0").
- `main.py` delega en `gui_main.py`, que acepta como argumento el directorio de datos (por defecto `datos/`).
- La persistencia está organizada en modo **multi-tenancy**: `datos/universidades.txt` cataloga las universidades (UPC, UNAL, UNAD) y cada una tiene una subcarpeta propia con sus archivos `.txt`. Esto lo gestiona `persistencia/gestor_multi_tenancy.py`.
- El ejecutable C++ CLI busca los datos en `cpp/datos`, `datos` o `../datos` (en ese orden).

## 19.4 Menú Python `[IMPLEMENTADO]`

La aplicación Python es una GUI de escritorio (CustomTkinter, estilo Windows 11 Light) con esta estructura de navegación real (`ui_gui/gui_app.py`):

- **Header superior**: nombre de la universidad activa, indicador de persistencia conectada, **selector de universidad** (multi-tenancy) y botón "Nueva Universidad".
- **Barra lateral de navegación** con 7 módulos:

| Opción | Vista | Módulo |
|---|---|---|
| 📊 Panel de Control | `dashboard` | Resumen e indicadores. |
| 🏛️ Facultades & Programas | `facultades` | Gestión institucional. |
| 👥 Gestión de Personas | `personas` | Personas, estudiantes, profesores, administrativos. |
| 🎓 Académico & EBRA | `academica` | Periodos, ofertas, matrícula, calificaciones, alertas. |
| 📝 Contratación Docente | `contratos` | Contratos, categorías, factores, KPIs. |
| 💰 Nómina & Liquidación | `nomina` | Periodos de nómina y liquidaciones. |
| ⚙️ Parámetros Legal | `parametros` | Parámetros normativos vigentes. |

- **Arranque**: si la persistencia está vacía, el sistema pregunta si se desea cargar datos o **comenzar sin datos** conservando los 20 parámetros normativos por defecto (cumple RF-16).

## 19.5 Funciones Python implementadas `[IMPLEMENTADO]`

Selección de funciones reales verificadas en el código:

| Función | Responsabilidad | Archivo |
|---|---|---|
| `GestorPersistencia.cargar_todos_los_datos` / `guardar_todos_los_datos` | Carga y guardado de las 30 entidades en `.txt`. | `persistencia/gestor_persistencia.py` |
| `GestorPersistencia.validar_integridad_datos` | IDs duplicados y 35 referencias cruzadas. | `persistencia/gestor_persistencia.py` |
| `GestorMultiTenancy` (catálogo y conmutación) | Carpeta aislada por universidad y plantilla inicial. | `persistencia/gestor_multi_tenancy.py` |
| `GestorMatriculas.matricular_curso` / `cancelar_curso` | Matrícula con 8 validaciones ordenadas; cancelación con motivo y liberación de cupo. | `gestores/gestores_academicos.py` |
| `GestorMatriculas.calcular_promedio_periodo` / `calcular_promedio_acumulado` | Promedios ponderados por créditos. | `gestores/gestores_academicos.py` |
| `GestorMatriculas.evaluar_ebra` / `evaluar_alertas_periodo` | Alertas EBRA individuales y masivas por periodo. | `gestores/gestores_academicos.py` |
| `GestorCalificaciones.registrar_calificacion` / `recalcular_nota_final` | Notas 0–5 con recálculo ponderado en cascada. | `gestores/gestores_academicos.py` |
| `GestorAcademico.crear_plan` / `incluir_curso` / `registrar_prerrequisito` / `asignar_profesor` | Estructura de planes, malla y asignación docente. | `gestores/gestor_academico.py` |
| `GestorContratos.crear_contrato` / `validar_contrato` / `terminar_contrato` | Reglas de contratación por modalidad y ciclo de vida. | `gestores/gestor_contratos.py` |
| `GestorParametros` (vigencia y validación) | Parámetros con vigencia, rangos por tipo y no solapamiento. | `gestores/gestor_parametros.py` |
| `GestorNomina.liquidarProfesorPlanta` / `liquidarProfesorOcasional` / `liquidarProfesorCatedratico` / `liquidarAdministrativo` | Liquidación por modalidad, delegando el cálculo en los liquidadores de `liquidadores.py`. | `nomina/gestor_nomina.py`, `nomina/liquidadores.py` |
| `CalculadoraDeducciones` / `CalculadoraPrestaciones` | Deducciones, aportes patronales, prestaciones y bonificaciones. | `nomina/calculadora_deducciones.py`, `nomina/calculadora_prestaciones.py` |
| `GestorNomina.desglose_nomina_anual` / `resumen_nomina_anual` | Proyección anual por contrato y consolidado institucional. | `nomina/gestor_nomina.py`, `nomina/desglose_anual.py` |

---

# 20. Flujo principal del programa `[IMPLEMENTADO]`

Flujo real de la aplicación Python (GUI), verificado en `main.py` → `gui_main.py` → `PITAApplication`:

```text
INICIO (python main.py [directorio_datos])
  |
  +-- PITAController carga la persistencia del tenant activo
  |      (catálogo universidades.txt + carpeta de la universidad)
  |
  +-- Si la persistencia está vacía:
  |      +-- Cargar datos de ejemplo, o
  |      +-- Comenzar sin datos (se conservan 20 parámetros normativos)
  |
  +-- Ventana principal (CustomTkinter)
  |      +-- Header: universidad activa + selector multi-tenancy
  |      +-- Sidebar: 7 módulos (Dashboard, Facultades, Personas,
  |      |              Académico & EBRA, Contratación, Nómina, Parámetros)
  |      +-- Cada vista usa los gestores del dominio vía PITAController
  |
  +-- Los cambios se guardan en los archivos del tenant activo
  |
FIN
```

En C++ coexisten dos puntos de entrada: `pita_backend` (verificación por fases, ver 18.4) y `pita_gui` (interfaz Dear ImGui con las mismas vistas por módulo).

> **Diferencia con el diseño conceptual:** el menú de consola de 13 opciones propuesto no se implementó; la interfaz principal es gráfica en ambos lenguajes. El flujo de "guardar al salir" se reemplazó por persistencia en los archivos del tenant activo.

---

# 21. Validaciones y manejo de errores

## 21.1 Integridad

- Identificador duplicado.
- Documento duplicado.
- Referencia inexistente.
- Fecha final anterior a fecha inicial.
- Registro histórico solicitado para eliminación física.

## 21.2 Académicas

- Estudiante inactivo.
- Periodo cerrado.
- Oferta sin cupo.
- Prerrequisito incumplido.
- Máximo de créditos superado.
- Cruce de horario.
- Nota fuera de escala.
- Porcentajes diferentes de 100 %.

## 21.3 Contratación

- Modalidad incompatible con dedicación.
- Contrato ocasional igual o superior a un año.
- Catedrático con más de 18 horas semanales.
- Ad honorem con valor de hora diferente de cero.
- Liquidación sin contrato vigente.

## 21.4 Nómina

- Parámetro fuera de vigencia.
- Horas cumplidas superiores a las asignadas.
- Periodo cerrado.
- Liquidación duplicada.
- Bonificación integrada en una base excluida.
- Intento de modificación directa de una liquidación cerrada.

## 21.5 Persistencia

- Archivo inexistente.
- Línea con campos incompletos.
- Tipo de dato inválido.
- Fecha con formato incorrecto.
- Referencia no cargada.
- Error de escritura.

---

# 22. Pruebas

> `[IMPLEMENTADO]` La suite real de pruebas automatizadas (pytest) se ejecutó el 2026-09-12 con resultado **48 pruebas exitosas, 0 fallos** (1.76 s). Comando: `python -m pytest test_pita.py test_multi_universidades.py test_aislamiento_universidades.py test_puntos_doctorado_nomina.py test_rubric_corrections.py`.

## 22.1 Correspondencia entre pruebas conceptuales y pruebas reales

| Código | Escenario | Prueba(s) real(es) que lo cubren | Estado |
|---|---|---|---|
| P-01 | Crear facultad válida. | `TestCRUD::test_crud_y_codigo_unico` | ✅ Superada |
| P-02 | Crear facultad con código repetido. | `TestCRUD::test_crud_y_codigo_unico` | ✅ Superada |
| P-03 | Matricular curso con cupo. | `TestAcademico::test_matricula_cancelacion_cupo_y_cruce` | ✅ Superada |
| P-04 | Matricular curso con cruce. | `TestAcademico::test_matricula_cancelacion_cupo_y_cruce` | ✅ Superada |
| P-05 | Cancelar dentro del plazo. | `TestAcademico::test_matricula_cancelacion_cupo_y_cruce` | ✅ Superada |
| P-06 | Registrar calificación válida. | `TestAcademico::test_calificacion_ponderada_y_ebra` | ✅ Superada |
| P-07 | Promedio inferior al umbral (EBRA). | `TestAcademico::test_calificacion_ponderada_y_ebra`, `TestAcademicoEstructura::test_crear_oferta_con_docente_y_deteccion_ebra` | ✅ Superada |
| P-08 | Liquidar profesor de planta. | `TestPuntosDoctoradoYNomina::test_planta_calcula_puntos_doctorado_decreto_1279`, `test_impacto_doctorado_en_salario_base_y_devengado_planta` | ✅ Superada |
| P-09 | Liquidar profesor ocasional. | `TestContratosParametrosNomina::test_nomina_ocasional_exoneracion_y_bonificaciones_exentas`, `TestRubricCorrections::test_cu21_salario_base_asistente_tiempo_completo` | ✅ Superada |
| P-10 | Liquidar catedrático. | `TestContratosParametrosNomina::test_nomina_catedratico_prorratea_horas` | ✅ Superada |
| P-11 | Liquidar ad honorem. | `TestContratosParametrosNomina::test_liquidacion_ad_honorem_sin_devengado` | ✅ Superada |
| P-12 | Cargar referencia inexistente. | `TestMultiUniversidades::test_integridad_referencial_universidad_invalida`, `TestPersistencia::test_guardar_cargar_y_referencia` | ✅ Superada |
| P-13 | Modificar nómina cerrada. | `TestContratosParametrosNomina::test_ciclo_nomina_y_bloqueo_periodo_cerrado` | ✅ Superada |

## 22.2 Cobertura adicional de la suite real

La suite cubre escenarios que el plan conceptual no contemplaba:

- **Multi-tenancy** (13 pruebas): aislamiento físico entre carpetas, catálogo maestro, conmutación de almacén en el controlador, códigos únicos, persistencia por universidad y desglose institucional.
- **Reglas salariales Decreto 1279 / Acuerdo 027**: puntos de doctorado de oficio, aislamiento de régimen (ocasionales y catedráticos no reciben puntos 1279), bonificación de posgrado solo para el régimen que aplica.
- **Nómina avanzada**: parámetros vigentes por fecha, auxilio de transporte en el neto, fondo de solidaridad paramétrico, deducciones del 4 % sin truncamiento, desglose anual sin contaminar liquidaciones, liquidación de administrativos.
- **Estructura académica**: planes de estudio con malla completa, prerrequisitos, estados de periodo, integración del controlador GUI.
- **Arranque sin datos**: `test_cli_inicia_sin_datos_y_sale` (RF-16).

## 22.3 Evidencia de ejecución

```text
$ python -m pytest test_pita.py test_multi_universidades.py test_aislamiento_universidades.py test_puntos_doctorado_nomina.py test_rubric_corrections.py -q
................................................                         [100%]
48 passed in 1.76s
```

---

# 23. Matriz de correspondencia entre diseño y código

> Estado del contraste: **modelo de dominio, gestores y lógica de negocio verificados** (30 entidades y 7 enumeraciones idénticas en ambos lenguajes; gestores contrastados contra `gestores/` y `nomina/` en ambas implementaciones).

| Elemento conceptual | C++ | Python | Estado | Observación |
|---|---|---|---|---|
| SistemaPITA | No existe como clase única | No existe como clase única | `[IMPLEMENTADO]` (distinto) | La coordinación se reparte entre gestores especializados y el controlador de la GUI. |
| 30 entidades del dominio | `struct` en `dominio/modelo_datos.h` | `@dataclass` en `dominio/modelo_datos.py` | `[IMPLEMENTADO]` | Mismos nombres y atributos en ambos lenguajes. |
| Lista de objetos | `ListaEnlazada<T>` propia (doblemente enlazada) | `list[T]` nativa | `[IMPLEMENTADO]` | C++ implementa la lista manualmente, acorde al taller. |
| Facultad | `struct Facultad` | `Facultad` | `[IMPLEMENTADO]` | 11 atributos, incluye `idUniversidad`. |
| Estudiante | `struct Estudiante` | `Estudiante` | `[IMPLEMENTADO]` | 11 atributos, `estadoAcademico` usa el enum. |
| Profesor | `struct Profesor` | `Profesor` | `[IMPLEMENTADO]` | 58 atributos, todos opcionales. |
| Contrato | `struct Contrato` | `Contrato` | `[IMPLEMENTADO]` | 82 atributos; referencia por `idPersona`. |
| MatriculaAcademica | `struct MatriculaAcademica` | `MatriculaAcademica` | `[IMPLEMENTADO]` | 8 atributos; detalles en `DetalleMatricula`. |
| LiquidacionNomina | `struct LiquidacionNomina` | `LiquidacionNomina` | `[IMPLEMENTADO]` | 77 atributos; incluye `parametros_utilizados` para trazabilidad. |
| Enumeraciones (7) | `enum class` | `str, Enum` | `[IMPLEMENTADO]` | Ver sección 11. |
| EstadoRegistro | No implementado como enum | No implementado como enum | `[IMPLEMENTADO]` (distinto) | `estado` es texto libre en todas las entidades. |
| GestorNomina | `nomina/gestor_nomina.h/.cpp` | `nomina/gestor_nomina.py` + `liquidadores.py` | `[IMPLEMENTADO]` (Python) | 4 liquidadores por modalidad (planta, ocasional, cátedra/ad honorem, administrativo), calculadoras de deducciones y prestaciones, ciclo de vida con reliquidación por versiones. |
| GestorPersistencia | `persistencia/gestor_persistencia.h/.cpp` | `persistencia/gestor_persistencia.py` | `[IMPLEMENTADO]` | Delimitador `\|` compartido; validación de IDs duplicados y 35 referencias cruzadas (Python). |
| GestorMultiTenancy | No implementado | `persistencia/gestor_multi_tenancy.py` | `[IMPLEMENTADO]` (solo Python) | Catálogo `universidades.txt` y carpeta aislada por universidad; no estaba en el diseño conceptual. El backend C++ trabaja con una sola carpeta de datos (`cpp/datos` por defecto); la entidad `Universidad` sí existe en ambos modelos. |
| Evaluación EBRA | `GestorMatriculas::evaluarEbra` (`gestores/gestores_academicos.h/.cpp`) | `GestorMatriculas.evaluar_ebra` (`gestores/gestores_academicos.py`) | `[IMPLEMENTADO]` | Compara el promedio acumulado con el parámetro `PROMEDIO_MINIMO_EBRA` y genera `AlertaAcademica` sin duplicar alertas activas. Verificado en ejecución C++ (alerta con promedio 2.67, sección 24.1) y en pruebas P-07. |

---

# 24. Evidencias de ejecución

## 24.1 Ejecución en C++ `[IMPLEMENTADO]`

- Compilador: **MSVC (Visual Studio 18 2026)**, generado con CMake 4.3.1.
- Versión del lenguaje: **C++17**.
- Comando de compilación: `cmake -S cpp -B cpp/build` + `cmake --build cpp/build --config Release`.
- Ejecutables producidos: `cpp/build/Release/pita_backend.exe` (verificador CLI) y `pita_gui.exe` (GUI Dear ImGui).
- Ejecución del verificador el 2026-09-12, código de salida 0. Salida real (resumen):

```text
[1/4] Cargando persistencia e integridad referencial...
  -> Personas: 7 | Profesores: 3 | Contratos: 3 | Liquidaciones: 3 | Parametros: 22 ...
  [EXITO] Integridad referencial y unicidad de IDs validada al 100%.
[3/4] Reglas académicas y normativas...
  - SMMLV Vigente: $1750905.00 | Valor Punto: $23924.00 | Auxilio: $249095.00
  - Estudiante ID 1 Promedio Acumulado: 2.67 [ALERTA EBRA DETECTADA]
[4/5] Reglas Decreto 1279 y Acuerdo 027...
  - [REGLA 1] Planta Titular con Doctorado: 570 pts (Esperado: 570) -> CORRECTO
  - [REGLA 2] Ocasional con Doctorado: 0 pts (Esperado: 0) -> CORRECTO
  - [REGLA 3] Bonif. Posgrado Planta: $0 (Esperado: $0) -> CORRECTO
  - [REGLA 4] Bonif. Posgrado Ocasional (90% SMMLV): $1575815.00 -> CORRECTO
[5/5] Motor de nómina y desglose anual...
  - Contrato ocasional: Neto a Pagar $7264750.00, Costo Empleador $10837389.77
  - Resumen institucional 2026: Costo Total UPC $369256573.79
  TODAS LAS PRUEBAS DEL BACKEND C++ COMPLETADAS CON EXITO
```

- Captura de la GUI C++: `[EVIDENCIA PENDIENTE]` (requiere captura de pantalla manual).

## 24.2 Ejecución en Python

- Versión de Python: 3.12 (verificado por los `__pycache__` del proyecto).
- Comando de ejecución: `python main.py` (GUI) — acepta un directorio de datos opcional.
- Suite de pruebas: `python -m pytest -q` → **47 passed in 2.08s** (2026-09-11). ✅
- Captura del menú: `[EVIDENCIA PENDIENTE]` (captura de la GUI).
- Captura de matrícula: `[EVIDENCIA PENDIENTE]`.
- Captura de nómina: `[EVIDENCIA PENDIENTE]`.

## 24.3 Persistencia compartida `[IMPLEMENTACIÓN PARCIAL]`

- Ambos lenguajes usan el mismo formato delimitado `|` y las mismas convenciones (sección 17).
- **C++** lee por defecto `cpp/datos` (una copia plana de una universidad); **Python** lee `datos/<tenant>` con el catálogo multi-universidad.
- Verificado: el backend C++ cargó los 28 archivos de `cpp/datos` con integridad referencial al 100 %, y Python carga las mismas estructuras desde `datos/upc` (suite pytest, 48/48).
- `[PENDIENTE DE PRUEBA]` Prueba cruzada directa: guardar desde Python y cargar ese mismo archivo en C++ (y viceversa) con el mismo tenant. Punto de atención conocido: el campo `parametros_utilizados` (repr de diccionario Python) no es portable a C++.

---

# 25. Limitaciones

1. Las búsquedas secuenciales tienen complejidad lineal.
2. El formato delimitado exige tratar separadores dentro de textos.
3. El modelo conceptual es mayor que una implementación mínima del taller.
4. La nómina es una simulación académica sujeta a verificación normativa.
5. El guardado en disco no es atómico (se escribe directamente sobre el archivo destino).
6. El campo `parametros_utilizados` se serializa como representación de diccionario de Python y no es portable a C++.
7. Los valores económicos dependen de los parámetros vigentes y deben actualizarse por periodo.

---

# 26. Trabajo pendiente

## 26.1 Datos de identificación (manuales)

- [ ] Registrar nombres de integrantes y grupo en la portada y el control del documento.
- [ ] Completar las referencias de la sección 28 con enlaces oficiales y fechas de consulta.

## 26.2 Evidencias gráficas (manuales)

- [ ] Captura de la GUI de C++ (sección 24.1).
- [ ] Capturas de la GUI de Python: menú principal, matrícula y nómina (sección 24.2).

## 26.3 Mejoras opcionales

- [ ] Prueba cruzada de persistencia: guardar desde Python y cargar en C++ con el mismo tenant (requiere decidir la codificación neutral de `parametros_utilizados`).
- [ ] Guardado atómico: escribir en archivo temporal y reemplazar de forma controlada.
- [ ] Diagramas: entidades y relaciones, arquitectura, flujo de matrícula y flujo de nómina.

> Completado en esta fase: revisión del código C++ y Python, confirmación de clases, listas, formato de persistencia y cálculos; matriz diseño-código; diccionario de datos generado desde el código con ejemplos reales y validaciones; suite de 48 pruebas en verde; limpieza de marcadores; migración a Word con diseño final.

---

# 27. Conclusiones

El diseño conceptual de PITA organiza un dominio amplio mediante listas, entidades relacionadas por identificadores y gestores especializados. La separación entre información académica, contratación y nómina permite desarrollar el sistema progresivamente sin perder coherencia.

La persistencia en archivos de texto responde al objetivo académico y permite compartir datos entre C++ y Python. Sin embargo, la interoperabilidad exige definir rigurosamente delimitador, orden de campos, codificación, tipos y formato de fechas.

El contraste final con el código confirmó la viabilidad del diseño: las 30 entidades, los gestores especializados y las reglas de negocio existen en ambos lenguajes con comportamiento equivalente, respaldados por una suite de 48 pruebas automatizadas en verde. La decisión de implementar la lista enlazada manualmente en C++ (en lugar de `std::list`) cumplió el objetivo pedagógico del taller sin comprometer la paridad funcional con Python.

Como aprendizaje principal, la parametrización de las reglas económicas y académicas (parámetros normativos con vigencia) demostró ser la pieza que más flexibilidad aporta: permitió ajustar topes, porcentajes y umbrales sin modificar el código. Las limitaciones restantes — guardado no atómico y un campo de trazabilidad no portable a C++ — son acotadas y tienen ruta de solución definida (sección 26).

---

# 28. Referencias documentales

1. Universidad Popular del Cesar. *Taller 1 de Estructura de Datos: Listas*. Enunciado suministrado para el periodo 2026.
2. Equipo del proyecto PITA. *Consolidado final del modelo conceptual PITA*. Documento de trabajo suministrado para el desarrollo del taller.
3. República de Colombia. *Decreto 1279 de 2002*. Citado en los documentos base del proyecto.
4. Universidad Popular del Cesar. *Acuerdo 027 del 31 de octubre de 2024*. Citado en los documentos base del proyecto.
5. Ministerio del Trabajo de Colombia. *Mi Calculadora*. Recurso mencionado en el enunciado como apoyo para la simulación.

> `[VERIFICACIÓN PENDIENTE]` Antes de la entrega final, completar las referencias con enlaces oficiales, fechas de consulta y formato bibliográfico seleccionado.

---

# Anexo A. Plantilla para documentar una entidad

## Nombre de la entidad

### Propósito

`[DESCRIPCIÓN]`

### Atributos

| Atributo | Tipo | Obligatorio | Regla | Ejemplo |
|---|---|---|---|---|
| `[atributo]` | `[tipo]` | Sí/No | `[regla]` | `[ejemplo]` |

### Relaciones

- `[RELACIÓN]`.

### Operaciones

- Crear.
- Consultar.
- Modificar.
- Desactivar.
- Reactivar.
- Eliminar lógicamente.
- Guardar.
- Cargar.

### Correspondencia con C++

`[PENDIENTE]`

### Correspondencia con Python

`[PENDIENTE]`

---

# Anexo B. Plantilla para documentar una prueba

## Código y nombre

`[P-XX: NOMBRE]`

### Objetivo

`[OBJETIVO]`

### Datos de entrada

```text
[DATOS]
```

### Pasos

1. `[PASO]`.

### Resultado esperado

`[RESULTADO]`

### Resultado obtenido en C++

`[PENDIENTE]`

### Resultado obtenido en Python

`[PENDIENTE]`

### Evidencia

`[CAPTURA O SALIDA PENDIENTE]`

---

# Anexo C. Historial de cambios

| Versión | Fecha | Responsable | Cambio |
|---|---|---|---|
| 0.1 | Septiembre de 2026 | Equipo PITA | Creación del documento maestro conceptual. |
| 0.2 | 2026-09-11 | Equipo PITA | Paso 1 de contraste con el código: estructura real de archivos C++ (18.3) y Python (19.3) documentada y verificada; se confirma GUI con CustomTkinter (Python) y Dear ImGui (C++), y persistencia multi-tenancy por universidad. |
| 0.3 | 2026-09-11 | Equipo PITA | Paso 2 de contraste: modelo de dominio verificado — 30 entidades y 7 enumeraciones idénticas en C++ y Python; C++ usa lista doblemente enlazada propia (`ListaEnlazada<T>`) en vez de `std::list`; Contrato referencia por `idPersona`; se documentan los 2 enums adicionales (TipoFactor, ParametroNormativoCodigo) y la ausencia del enum EstadoRegistro. |
| 0.4 | 2026-09-11 | Equipo PITA | Paso 3 de contraste: persistencia verificada — organización multi-tenancy real (catálogo `universidades.txt` + carpeta por universidad), formato delimitado `\|` sin encabezado con convenciones exactas (booleanos 1/0, fechas ISO, vacío = ausente), reglas de carga tolerante con validación de 35 referencias cruzadas, y pendiente identificado: el campo `parametros_utilizados` no es portable a C++ y el guardado no es atómico. |
| 0.5 | 2026-09-11 | Equipo PITA | Paso 4 de contraste: reglas de negocio verificadas — orden real de validaciones de matrícula, porcentajes en escala 0–100, nota 0–5, umbral de aprobación 3.0 por defecto, cadena de recálculo nota→periodo→acumulado→EBRA, EBRA sin duplicar alertas, validaciones de contrato por modalidad (18 h catedrático, 8 h ad honorem administrativo, ocasional < 12 meses, sin jubilados), validación de parámetros con vigencias sin solapamiento, y catálogo real de 12 gestores con excepciones propias. |
| 0.6 | 2026-09-11 | Equipo PITA | Paso 5 de contraste: nómina verificada — fórmulas reales por modalidad (planta por puntos con escalafón 180/250/350/450, ocasional por factor SMMLV 3.918/3.606/3.125/2.645, cátedra por horas pagables, ad honorem en cero), liquidador de administrativos no contemplado en el diseño, tablas de descuentos y aportes con valores por defecto (salud 4 %, pensión 4 %/12 %, ARL 0.522 %, SENA/ICBF exonerados bajo 10 SMMLV), provisiones del régimen general y del régimen especial Decreto 1279, bonificaciones de posgrado (0.90/0.45/0.10 SMMLV) e investigación (A1 0.56 … semillero 0.20), y ciclo de vida de liquidación con reliquidación por versiones. |
| 0.7 | 2026-09-11 | Equipo PITA | Paso 6 de contraste: interfaces verificadas — el CLI de C++ es un verificador por fases (no un menú interactivo) y la interacción real es gráfica en ambos lenguajes (CustomTkinter con 7 módulos y selector de universidad en Python; Dear ImGui en C++); se confirma el arranque con o sin datos conservando 20 parámetros (RF-16). |
| 0.8 | 2026-09-11 | Equipo PITA | Paso 7 de contraste: suite de pruebas ejecutada — 47/47 en verde; sección 22 reescrita con la correspondencia entre las 13 pruebas conceptuales y las pruebas reales de pytest, cobertura adicional documentada (multi-tenancy, Decreto 1279/Acuerdo 027, nómina avanzada) y único vacío identificado: falta prueba dedicada para liquidación ad honorem (P-11). |
| 0.9 | 2026-09-12 | Equipo PITA | Paso 9: creado el diccionario de datos independiente (`docs/DICCIONARIO_DE_DATOS.md`), generado automáticamente desde el código — 30 entidades y 607 atributos con tipo, formato y orden de serialización. |
| 1.0 | 2026-09-12 | Equipo PITA | Paso 8: evidencias de ejecución reales — backend C++ compilado (MSVC, VS 18 2026, C++17, CMake) y ejecutado con éxito (exit 0); salida documentada en 24.1 con reglas Decreto 1279/Acuerdo 027 correctas, alerta EBRA detectada y costo institucional 2026; sección 24.3 actualizada con el estado real de interoperabilidad. |
| 1.1 | 2026-09-12 | Equipo PITA | Limpieza de marcadores pendientes (bloque A): RF-01 a RF-05 marcados `[IMPLEMENTADO]` con justificación; CU-10 alineado con el orden real de validaciones de `matricular_curso`; matriz 23 completada (GestorMultiTenancy solo en Python, EBRA verificado en ambos lenguajes); fragmentos conceptuales 18.2/19.2 reemplazados por el código real; tablas de funciones 18.5 y 19.5 diligenciadas con nombres y archivos verificados. |
| 1.2 | 2026-09-12 | Equipo PITA | Prueba P-11 creada: `test_liquidacion_ad_honorem_sin_devengado` verifica que un contrato catedrático ad honorem se liquida con devengado, deducciones, prestaciones y costo empleador en cero (con contraste contra un catedrático remunerado). Suite completa: 48/48 pruebas en verde; ya no quedan vacíos en el plan de pruebas conceptual. |
| 1.3 | 2026-09-12 | Equipo PITA | Diccionario de datos terminado: creado el generador reproducible `docs/generar_diccionario.py` y regenerado el documento con dos columnas nuevas por atributo — ejemplo real tomado del primer registro del tenant UPC y validación verificada en el código (rango de notas, porcentajes, topes de horas, reglas de contratos, integridad referencial con la entidad destino exacta). Se corrige el conteo real: 607 atributos (no 637). |
| 1.4 | 2026-09-12 | Equipo PITA | Migración a Word: creado `docs/exportar_word.py`, que genera `DOCUMENTACION_MAESTRA_PITA.docx` y `DICCIONARIO_DE_DATOS.docx` con diseño formal (portada, tabla de contenido actualizable, encabezados jerárquicos, tablas con estilo, código en Consolas sombreado, notas destacadas y numeración de páginas). |
| 1.5 | 2026-09-12 | Equipo PITA | Diseño final de entrega: `exportar_word.py` reescrito con estilo ejecutivo moderno (portada con banda lateral azul, títulos con línea inferior, tablas tipo libro, código y notas con barra lateral azul); creado `docs/limpiar_md.py`, que genera en `docs/export/` versiones limpias de los .md (sin marcadores editoriales ni tachados) usadas como fuente de los .docx. |
| 1.6 | 2026-09-12 | Equipo PITA | Actualización de secciones informativas al estado final: la introducción ya refleja que el documento está contrastado con el código (no "se documentará"); la nota de alcance indica que la versión Word se genera desde este archivo; la sección 27 pasa de "Conclusiones preliminares" a "Conclusiones" con los resultados reales (paridad C++/Python, 48 pruebas en verde, lista enlazada propia, parametrización como aprendizaje clave y limitaciones acotadas). |
| 1.7 | 2026-09-12 | Equipo PITA | Deduplicación con el diccionario de datos: las listas de atributos de la sección 9 (93 viñetas) se eliminaron del documento maestro y se reemplazaron por referencias al diccionario; se conservaron las descripciones y notas de decisión de cada entidad; las secciones 9.4 a 9.6 pasaron de listas de nombres a descripciones de una línea por entidad. |
| 1.8 | 2026-09-12 | Equipo PITA | Cierre de inconsistencias internas: conteo de pruebas actualizado a 48/48; limitaciones reformuladas al estado real (guardado no atómico, `parametros_utilizados` no portable, valores por vigencia); sección 26 reescrita con solo el trabajo pendiente real (datos de integrantes, referencias, capturas de GUI y mejoras opcionales) y registro de lo completado; el tipo del documento ya no dice "en construcción". |
