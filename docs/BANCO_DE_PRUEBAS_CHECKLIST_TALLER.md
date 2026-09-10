# 📋 BANCO DE PRUEBAS Y CHECKLIST DE CONFORMIDAD

## Sistema PITA v2.0 (Programa Integrado de Transacciones Académicas y Nómina Docente)

**Universidad Popular del Cesar (UPC) — Facultad de Ingenierías y Tecnológicas**  
**Asignatura:** Estructura de Datos — Taller 1 (Listas Enlazadas & TADs)  
**Normatividad:** Decreto 1279 de 2002 | Ley 30 de 1992 | Acuerdo 027 del 31 de octubre de 2024 | Reglamento Estudiantil UPC  

---

## 🎯 Objetivo del Documento

Este banco de pruebas suministra una **guía secuencial paso a paso** diseñada para que docentes, evaluadores y estudiantes puedan validar el cumplimiento del **100% de los requisitos funcionales, normativos y técnicos del Taller 1**, ejecutando el sistema tanto en **Modo 0 Datos (Limpieza Total / Arranque en Blanco)** como con **Datos Precargados** de acuerdo con el **Requerimiento #59**:
> *"El usuario puede decidir si cargar los datos del archivo o ejecutar sin datos."*

El protocolo es idéntico y aplicable tanto para la aplicación de alto rendimiento en **C++20 (`pita_gui.exe` / Dear ImGui)** como para la aplicación en **Python 3.12 (`main.py` / CustomTkinter)**.

---

## 🚀 Fase 0: Inicialización en Limpio (Modo 0 Datos) y Arranque

| Paso | Acción en la Interfaz | Resultado Esperado | C++ | Python |
| :---: | :--- | :--- | :---: | :---: |
| **0.1** | Abrir la aplicación: <br>• C++: `./pita_gui.exe` <br>• Python: `python main.py` | La ventana principal abre con diseño institucional UPC (paleta profesional, tipografía moderna, paneles modulares). | [ ] | [ ] |
| **0.2** | En el menú lateral izquierdo (Sidebar), sección **CONTROL DE DATOS**, pulsar el botón: <br>**`🧹 Iniciar Sin Datos (0 datos)`** | Mensaje en barra de estado / notificación: *"Sistema iniciado en limpio (0 datos operativos). Listo para ingresar datos desde cero."* | [ ] | [ ] |
| **0.3** | Ir a la vista **📊 Dashboard** | Todos los contadores operativos inician en **0**: <br>• 0 Estudiantes Registrados <br>• 0 Alertas EBRA <br>• 0 Docentes <br>• 0 Contratos <br>• Parámetros Salariales activos visibles en el pie o panel normativo. | [ ] | [ ] |

---

## 🏛️ Fase 1: Estructura Institucional (Facultades y Programas)

*Cumple Requerimientos #1 y #2 del Taller.*

### Caso 1.1: Registro de Facultad

- **Ruta:** Menú Lateral ➔ **Facultades & Programas** ➔ Pestaña **Facultades** ➔ Botón **`+ Nueva Facultad`**
- **Datos en el Modal `➕ Registrar Nueva Facultad`:**
  - **Código:** `FIT`
  - **Nombre:** `Facultad de Ingenierias y Tecnologicas`
  - **Ubicación / Sede:** `Campus Sabanas, Bloque B`
  - **Teléfono:** `5842000` | **Correo:** `fit@unicesar.edu.co`
  - **Decano / Autoridad Académica:** Seleccionar `(Sin Decano Asignado)` *(en Modo 0 Datos aún no hay docentes creados; se puede asignar posteriormente al registrar profesores)*.
- **Acción:** Pulsar **`💾 Guardar Facultad`** (Python) o **`Guardar`** (C++).
- **Verificación:**
  - [ ] Aparece la fila en la tabla con código `FIT` y badge `ACTIVO`.
  - [ ] En la pestaña **Universidad**, se confirma la visualización jerárquica de la facultad.

### Caso 1.2: Registro de Programa Académico

- **Ruta:** Pestaña **Programas Académicos** ➔ Botón **`+ Nuevo Programa`**
- **Datos en el Modal `➕ Registrar Nuevo Programa Académico`:**
  - **Nombre del Programa Académico *:** `Ingenieria de Sistemas`
  - **Código Institucional *:** `SIS`
  - **Facultad de Adscripción *:** Seleccionar la facultad registrada `FIT`
  - **Director de Programa:** `(Sin Director Asignado)`
  - **Nivel de Formación *:** `PREGRADO` *(opciones: PREGRADO, POSGRADO, ESPECIALIZACIÓN, MAESTRÍA, DOCTORADO, TECNOLOGÍA)*
  - **Modalidad *:** `PRESENCIAL` *(opciones: PRESENCIAL, VIRTUAL, A DISTANCIA, DUAL, HÍBRIDA / SEMIPRESENCIAL)*
  - **Total Créditos Académicos *:** `160`
  - **Número de Semestres *:** `10`
- **Acción:** Pulsar **`💾 Registrar Programa`** (Python) o **`Guardar`** (C++).
- **Verificación:**
  - [ ] El programa queda vinculado a la facultad `FIT` con 160 créditos y badge `ACTIVO`.

---

## 👥 Fase 2: Gestión de Personas y Role  s

*Cumple Requerimientos #3, #4, #8 y #10 del Taller (TAD con Creación, Inclusión, Consulta, Modificación, Desactivación).*

### Caso 2.1: Registro de Profesor de Planta (Dec. 1279)

- **Ruta:** Menú Lateral ➔ **Personas** ➔ Botón **`+ Registrar Persona / Rol`** (Python) o **`+ Nueva Persona`** (C++)
- **1. Información Personal y de Contacto:**
  - **Tipo Documento *:** `CC` |**Número de Documento *:** `12345678`
  - **Primer Nombre *:** `Carlos` | **Segundo Nombre:** `Alberto`
  - **Primer Apellido *:** `Gomez` | **Segundo Apellido:** `Solano`
  - **Correo Institucional / Personal:** `cgomez@unicesar.edu.co`
  - **Ciudad de Residencia:** `Valledupar` | **Teléfono:** `3001234567`
- **2. Rol y Vinculación en PITA:**
  - **Rol Institucional a Asignar:** Seleccionar `PROFESOR` (o `Profesor`)
  - **Código Profesor *:** `DOC-001`
  - **Programa Principal *:** Seleccionar `Ingenieria de Sistemas`
  - **Tipo de Profesor / Vinculación *:** `PLANTA` *(opciones disponibles: PLANTA, OCASIONAL, CATEDRATICO, CATEDRATICO_AD_HONOREM)*
  - **Categoría Docente *:** `ASISTENTE` *(opciones disponibles: AUXILIAR, ASISTENTE, ASOCIADO, TITULAR, NO_CATEGORIZADO)*
  - **Dedicación *:** `TIEMPO_COMPLETO` *(opciones disponibles: TIEMPO_COMPLETO, MEDIO_TIEMPO, HORA_CATEDRA)*
  - **Horas Semanales:** `40`
  - **Máximo Nivel de Estudio:** `MAESTRIA`
  - **Puntos Salariales (Dec. 1279):** `250`
  - **Título Profesional:** `Ingeniero de Sistemas` | **Área:** `Ingeniería de Software`
- **Acción:** Pulsar **`💾 Registrar Persona y Guardar Rol`** (Python) o **`Guardar`** (C++).
- **Verificación:**
  - [ ] Se visualiza en la pestaña **Personas** y en la pestaña **Profesores** con 250 pts y badge `ACTIVO`.

### Caso 2.2: Registro de Profesor de Cátedra (Acuerdo 027/2024)

- **Ruta:** Botón **`+ Registrar Persona / Rol`**
- **1. Información Personal y de Contacto:**
  - **Tipo Documento *:** `CC` |**Número de Documento *:** `23456789`
  - **Primer Nombre *:** `Maria` | **Segundo Nombre:** `Mercedes`
  - **Primer Apellido *:** `Perez` | **Segundo Apellido:** `Cuello`
  - **Correo Institucional / Personal:** `mperez@unicesar.edu.co`
  - **Ciudad de Residencia:** `Valledupar` | **Teléfono:** `3002345678`
- **2. Rol y Vinculación en PITA:**
  - **Rol Institucional a Asignar:** Seleccionar `PROFESOR`
  - **Código Profesor *:** `DOC-002`
  - **Programa Principal *:** Seleccionar `Ingenieria de Sistemas`
  - **Tipo de Profesor / Vinculación *:** `CATEDRATICO` *(valor exacto en dropdown)*
  - **Categoría Docente *:** `AUXILIAR` *(o NO_CATEGORIZADO; no usar nombres fuera del escalafón oficial)*
  - **Dedicación *:** `HORA_CATEDRA`
  - **Horas Semanales:** `16` *(respetando tope legal de 18h cátedra)*
  - **Máximo Nivel de Estudio:** `ESPECIALIZACION`
  - **Puntos Salariales (Dec. 1279):** `0`
  - **Título Profesional:** `Especialista en Telemática`
- **Acción:** Pulsar **`💾 Registrar Persona y Guardar Rol`**.
- **Verificación:**
  - [ ] Aparece correctamente clasificado en la tabla de **Profesores** como `CATEDRATICO` (16h semanales) con categoría `AUXILIAR`.

### Caso 2.3: Registro de Estudiantes (Regular y Caso EBRA)

1. **Estudiante 1 (Rendimiento Óptimo):**
   - **Información Personal:** `CC` | `1003456789` | `Juan Diego` `Rodriguez Vega` | `jrodriguez@unicesar.edu.co`
   - **Rol:** `ESTUDIANTE` | **Código Estudiante *:** `EST-2026-001`
   - **Semestre Actual:** `3` | **Programa:** `Ingenieria de Sistemas` | **Estado Académico:** `ACTIVO`
2. **Estudiante 2 (Candidato a Alerta EBRA):**
   - **Información Personal:** `CC` | `1004567890` | `Andres Felipe` `Morales Mejia` | `amorales@unicesar.edu.co`
   - **Rol:** `ESTUDIANTE` | **Código Estudiante *:** `EST-2026-002`
   - **Semestre Actual:** `2` | **Programa:** `Ingenieria de Sistemas` | **Estado Académico:** `ACTIVO`

- **Verificación:**
  - [ ] Ambos estudiantes figuran en la pestaña **Estudiantes** con estado inicial `ACTIVO`.

### Caso 2.4: Registro de Personal Administrativo

- **Ruta:** Botón **`+ Registrar Persona / Rol`**
- **Información Personal:** `CC` | `34567890` | `Laura Patricia` `Sanchez Meza` | `lsanchez@unicesar.edu.co`
- **Rol:** Seleccionar `ADMINISTRATIVO`
  - **Código Empleado *:** `ADM-2026-01`
  - **Cargo Institucional *:** `Secretaria Academica FIT`
  - **Dependencia *:** `Facultad de Ingenierias y Tecnologicas`
  - **Nivel / Categoría *:** `PROFESIONAL` *(opciones: PROFESIONAL, DIRECTIVO, ASESOR, TECNICO, ASISTENCIAL)*
  - **Tipo Contratación:** `PLANTA` *(opciones: PLANTA, CARRERA_ADMINISTRATIVA, LIBRE_NOMBRAMIENTO, PROVISIONALIDAD, PRESTACION_SERVICIOS)*
  - **Salario Base Mensual ($) *:** `3200000`
- **Verificación:**
  - [ ] Aparece en la pestaña **Administrativos** con cargo, dependencia, salario base y badge `ACTIVO`.

### Caso 2.5: Validación del Buscador en Tiempo Real y Desactivación

- [ ] En la pestaña **Personas**, escribir `Morales` en el campo de búsqueda: la tabla filtra instantáneamente mostrando únicamente a Andrés Felipe.
- [ ] Pulsar **`Limpiar`**: la tabla restaura todas las personas registradas.
- [ ] Probar el botón **`Desactivar`** en una fila: su badge cambia de `ACTIVO` a `INACTIVO`. Al pulsar **`Activar`**, regresa inmediatamente a `ACTIVO`.

---

## 📚 Fase 3: Planes de Estudio, Períodos Académicos, Catálogo y Matrícula

*Cumple Requerimientos #3, #11 y #12 del Taller y Casos de Uso CU-03 (Planes de Estudio) y CU-04 (Períodos y Oferta).*

### Caso 3.1: Configuración y Verificación de Período Académico

- **Ruta:** Menú Lateral ➔ **Gestión Académica** ➔ Pestaña **`📅 Períodos Académicos`**

1. **Verificación del Período Activo:**
   - [ ] Se observa el período `2026-1` en la tabla con:
     - **Código:** `2026-1` | **Nombre:** `Primer Período Académico 2026`
     - **Año / Semestre:** `2026-1`
     - **Fechas de Clases:** `2026-02-01  ➔  2026-06-30`
     - **Fechas de Matrícula:** `2026-01-15  ➔  2026-02-10`
     - **Límite Cancelación:** `2026-04-15`
     - **Estado:** Badge verde `ABIERTO`
2. **Acciones Interactivas:**
   - [ ] Probar el botón **`🔄 Cerrar`**: el estado cambia a `CERRADO`. Al pulsar **`🔄 Aperturar`**, regresa inmediatamente a `ABIERTO`.
   - [ ] Probar el botón **`✏️ Editar`**: permite modificar fechas del calendario académico.
   - [ ] Probar el botón superior **`📅 + Aperturar Período`**: permite aperturar nuevos períodos (ej. `2026-2`).

### Caso 3.2: Gestión de Planes de Estudio y Malla Curricular (CU-03)

- **Ruta:** Menú Lateral ➔ **Gestión Académica** ➔ Pestaña **`📋 Planes de Estudio`**

1. **Verificación de Planes Registrados:**
   - [ ] Aparece el plan institucional `PLAN-SIS-2026` con:
     - **Nombre:** `Plan Ingenieria de Sistemas 2026`
     - **Programa:** `SIS - Ingenieria de Sistemas`
     - **Versión:** `V1` | **Créditos:** `160 cr`
     - **Estado:** Badge verde `ACTIVO`
2. **Exploración y Malla Curricular (`📜 Malla`):**
   - [ ] Pulsar el botón **`📜 Malla`** en la fila del plan: se despliega el modal interactivo de la **Malla Curricular**.
   - [ ] En el panel superior **➕ Incluir Asignatura a la Malla**:
     - Seleccionar una asignatura del catálogo (ej. `SIS-301`).
     - Indicar **Semestre Sugerido:** `3` | **Tipo:** `OBLIGATORIA` | **Obligatoria:** `Sí`.
     - Pulsar **`➕ Incluir`**: la materia se suma a la tabla del semestre correspondiente y el total de créditos de la malla se actualiza automáticamente.
   - [ ] Probar el botón **`❌ Quitar`** en una fila para remover materias de la malla.
3. **Control de Versiones y Estados:**
   - [ ] Pulsar el botón **`🔄 Desactivar`** en la tabla principal: el plan cambia a badge rojo `INACTIVO`. Al pulsar **`🔄 Activar`**, se restablece a `ACTIVO`.
   - [ ] Probar el botón superior **`📋 + Nuevo Plan`** para dar de alta nuevas versiones o planes curriculares.

### Caso 3.3: Catálogo de Asignaturas (Creación de Cursos con Umbrales Dinámicos)

- **Ruta:** Pestaña **`📚 Cursos & Ofertas`** ➔ **Catálogo de Asignaturas** ➔ Botón **`➕ Crear Asignatura`** (o `+ Nueva Asignatura`):
  - **Curso 1:**
    - **Código de la Asignatura *:** `SIS-301`
    - **Nombre de la Asignatura *:** `Estructuras de Datos`
    - **Número de Créditos *:** `3`
    - **Horas Teóricas:** `3` | **Horas Prácticas:** `2`
    - **Nota Mínima Aprobatoria *:** `3.0`
    - **Cupo Sugerido de Estudiantes:** `30`
  - **Curso 2 (Umbral Diferenciado):**
    - **Código de la Asignatura *:** `SIS-401`
    - **Nombre de la Asignatura *:** `Sistemas Operativos Avanzados`
    - **Número de Créditos *:** `4`
    - **Horas Teóricas:** `4` | **Horas Prácticas:** `1`
    - **Nota Mínima Aprobatoria *:** `3.5` *(umbral reglamentario especial de posgrado/avanzado)*
    - **Cupo Sugerido de Estudiantes:** `25`
- **Verificación:**
  - [ ] Ambos cursos aparecen en la tabla con sus créditos, distribución teórica/práctica y sus respectivas notas mínimas aprobatorias configurables.

### Caso 3.4: Apertura de Oferta / Grupo Abierto

- **Ruta:** Pestaña **Cursos & Ofertas** ➔ **Ofertas y Grupos Abiertos** ➔ Botón **`🏫 Abrir Oferta / Grupo`** (o `+ Nueva Oferta`)
- **Oferta 1:**
  - **Asignatura a Ofertar *:** `SIS-301 | Estructuras de Datos`
  - **Periodo Académico *:** `2026-1`
  - **Grupo *:** `01` |**Cupo Máximo *:** `30`
  - **Aula:** `204 Sabanas` | **Sede:** `Sede Sabanas` | **Modalidad:** `PRESENCIAL`
  - **Profesor Asignado:** Seleccionar `DOC-001 | Carlos Gomez`
- **Oferta 2:**
  - **Asignatura a Ofertar *:** `SIS-401 | Sistemas Operativos Avanzados`
  - **Periodo Académico *:** `2026-1`
  - **Grupo *:** `01` |**Cupo Máximo *:** `25`
  - **Aula:** `301 Sabanas` | **Sede:** `Sede Sabanas` | **Modalidad:** `PRESENCIAL`
  - **Profesor Asignado:** Seleccionar `DOC-002 | Maria Mercedes Perez`
- **Verificación:**
  - [ ] Las ofertas quedan aperturadas y sus semáforos de cupos reflejan disponibilidad total (`30 / 30` y `25 / 25`).

### Caso 3.5: Matrícula de Cursos

- **Ruta:** Pestaña **Matrículas** (o **✍️ Matrícula de Cursos**)
- **Acción en el panel superior de inscripción:**
  1. En el combobox **Estudiante a Matricular:** seleccionar `EST-2026-001 - Juan Diego Rodriguez`.
  2. En el combobox **Oferta / Curso Disponible:** seleccionar `SIS-301`.
  3. Pulsar el botón **`✍️ Matricular Estudiante`**.
  4. Repetir la operación para matricular a `EST-2026-002 - Andres Felipe Morales` en la oferta `SIS-301` y en la oferta `SIS-401`.
- **Verificación:**
  - [ ] Se crean las filas de detalle en la tabla de inscripciones (`INS-1`, `INS-2`, `INS-3`).
  - [ ] En la pestaña **Cursos & Ofertas**, los cupos disponibles se descuentan automáticamente.
  - [ ] Cada fila activa cuenta con el botón **`🚫 Cancelar`** para cancelaciones reglamentarias de asignaturas.

---

## 🚨 Fase 4: Evaluaciones, Calificaciones y Alertas EBRA

*Cumple Requerimientos #11, #12 y Cierre de Brechas #4 y #6 (Umbral dinámico `notaMinimaAprobatoria` y detección EBRA en lote en UI).*

### Caso 4.1: Calificaciones con Umbrales Dinámicos

- **Ruta:** Pestaña **Calificaciones** (o **Evaluaciones**)
- **Acción en el formulario superior `📝 Asignación de Calificaciones y Evaluaciones`:**
  1. **Juan Diego (`EST-2026-001`) en `SIS-301` (Umbral 3.0):**
     - Seleccionar inscripción `INS-1 | EST-2026-001 - Juan Diego Rodriguez — Estructuras de Datos`
     - En **Nota Definitiva (0.0 - 5.0):** ingresar `4.2`
     - Pulsar **`💾 Registrar Nota`**
     - [ ] Estado: badge `Aprobado` en color verde.
  2. **Andrés Morales (`EST-2026-002`) en `SIS-301` (Umbral 3.0):**
     - Seleccionar inscripción `INS-2 | EST-2026-002 - Andres Felipe Morales — Estructuras de Datos`
     - En **Nota Definitiva (0.0 - 5.0):** ingresar `2.1`
     - Pulsar **`💾 Registrar Nota`**
     - [ ] Estado: badge `Reprobado` en color rojo.
  3. **Andrés Morales (`EST-2026-002`) en `SIS-401` (Umbral 3.5):**
     - Seleccionar inscripción `INS-3 | EST-2026-002 - Andres Felipe Morales — Sistemas Operativos Avanzados`
     - En **Nota Definitiva (0.0 - 5.0):** ingresar `3.2` *(nota superior a 3.0 pero inferior a 3.5)*
     - Pulsar **`💾 Registrar Nota`**
     - [ ] **Comportamiento Dinámico Verificado:** Se clasifica como badge `Reprobado` porque este curso exige `3.5` como nota mínima aprobatoria.

### Caso 4.2: Detección y Panel de Alertas EBRA en Tiempo Real

- **Ruta:** Pestaña **Alertas EBRA**
- **Acción:** En la barra superior, pulsar el botón interactivo **`⚡ Ejecutar Detección EBRA Masiva`**
- **Verificación:**
  - [ ] El sistema ejecuta la evaluación masiva y muestra mensajede confirmación: *"Evaluación finalizada. Se detectaron/actualizaron alertas EBRA."*
  - [ ] **Tarjetas KPI EBRA:**
    - `Total Estudiantes Registrados`: Refleja el censo activo (2).
    - `En Riesgo EBRA (Promedio < 3.0)`: Refleja a los estudiantes con promedio crítico (Andrés Morales: promedio 2.65).
  - [ ] **Tabla de Diagnóstico EBRA:**
    - Fila generada para `EST-2026-002 (Andres Felipe Morales Mejia)`.
    - Badge `⚠️ EBRA` y plan de tutoría UPC sugerido.
  - [ ] En el **Dashboard General**: La tarjeta KPI de alertas refleja el estado de riesgo académico.

---

## 📝 Fase 5: Contratación Docente y Factores Salariales (Dec. 1279)

*Cumple Requerimientos #4, #5, #6, #7, #9, #13 y Cierre de Brecha #2 (Pisos de escalafón 37/58/74/96).*

### Caso 5.1: Vinculación Contractual Obligatoria

- **Ruta:** Menú Lateral ➔ **Contratos & Factores** ➔ Botón **`➕ Registrar Contrato`**

1. **Contrato Docente Planta:**
   - **Selector de Personal:** `👨‍🏫 Personal Docente`
   - **Docente *:** `DOC-001 - Carlos Alberto Gomez Solano [ASISTENTE, 250 pts]`
   - **Modalidad Contractual / Régimen Jurídico:** `DOCENTE_PLANTA (Dec. 1279)` *(valor exacto en dropdown)*
   - **Dedicación:** `TIEMPO_COMPLETO` | **Horas Semanales:** `40`
   - **Vigencia:** `2026-01-01` al `2026-12-31`
   - **Asistente:** Pulsar **`⚡ Calcular Según Régimen`** para autocalcular el salario según puntos.
   - Pulsar **`💾 Formalizar y Registrar Vinculación Contractual`**.
2. **Contrato Docente Cátedra:**
   - **Selector de Personal:** `👨‍🏫 Personal Docente`
   - **Docente *:** `DOC-002 - Maria Mercedes Perez Cuello [AUXILIAR, 0 pts]`
   - **Modalidad Contractual / Régimen Jurídico:** `DOCENTE_CATEDRATICO (Ac. 027/2024)` *(valor exacto en dropdown)*
   - **Dedicación:** `HORA_CATEDRA` | **Horas Semanales:** `16` *(validar control legal <= 18h)*
   - **Vigencia:** `2026-02-01` al `2026-06-30`
   - **Asistente:** Pulsar **`⚡ Calcular Según Régimen`** y formalizar.
3. **Contrato Administrativo:**
   - **Selector de Personal:** `👔 Personal Administrativo`
   - **Funcionario *:** `ADM-2026-01 - Laura Patricia Sanchez (Secretaria Academica FIT)`
   - **Modalidad Contractual:** `TERMINO_INDEFINIDO (CST)`
   - **Asistente:** Pulsar **`⚡ Asignar Salario del Cargo`** (`$3.200.000 COP`) y formalizar.

- **Verificación:**
  - [ ] Los contratos quedan formalizados y listados en la pestaña **📜 Contratos Docentes Vigentes**.
  - [ ] Las tarjetas KPI consolidan el conteo de contratos y la nómina proyectada.

### Caso 5.2: Reconocimiento de Puntos y Pisos Salariales de Escalafón

- **Ruta:** Botón superior **`⭐ Reconocer Puntos / Productividad`** (Modal `⭐ Comité de Puntaje Salarial (Decreto 1279)`)

1. **Sub-pestaña `📜 Títulos y Escalafón`:**
   - **Docente Beneficiario:** `DOC-001 - Carlos Alberto Gomez Solano`
   - **Tipo de Factor Salarial:** `TITULO_ACADEMICO` *(opciones: TITULO_ACADEMICO, CATEGORIA_DOCENTE, EXPERIENCIA_CALIFICADA, CARGO_DIRECCION_ACADEMICA)*
   - **Concepto / Denominación:** `Título de Doctorado en Ciencias de la Computación`
   - **Puntos Salariales a Asignar (+):** `120`
   - **Resolución:** `Resolución CIARP N° 045-2026`
   - Pulsar **`💾 Formalizar y Asignar Puntos Salariales`**.
   - [ ] Al guardar, los puntos del docente se incrementan a **370 pts** en tiempo real.
2. **Sub-pestaña `🔬 Producción Intelectual`:**
   - **Docente Autor:** `DOC-001 - Carlos Alberto Gomez Solano`
   - **Tipo de Obra Intelectual (MinCiencias):** `ARTICULO_A2 (12 pts)` *(opciones: ARTICULO_A1, ARTICULO_A2, ARTICULO_B, LIBRO_INVESTIGACION, PATENTE_INVENCION, SOFTWARE_REGISTRADO)*
   - **Título de la Obra o Producto:** `Optimizacion de Algoritmos en Grafos Paralelos`
   - **Revista / Editorial:** `IEEE Transactions on Computers`
   - **Número Total de Autores:** `2 (50%)` *(aplica factor de coautoría legal del 50%)*
   - **Puntos Base Producto:** `12`
   - Pulsar **`💾 Registrar y Reconocer Producción Intelectual`**.
   - [ ] Al guardar, se le reconocen **6 puntos netos** (12 × 50%) y se suman a su acumulado.
3. **Garantía de Pisos Legales de Escalafón (Brecha 2):**
   - [ ] Si un docente de planta tiene categoría `AUXILIAR`, el sistema garantiza mínimo **37 puntos**.
   - [ ] Si es `ASISTENTE`, garantiza mínimo **58 puntos**.
   - [ ] Si es `ASOCIADO`, garantiza mínimo **74 puntos**.
   - [ ] Si es `TITULAR`, garantiza mínimo **96 puntos**.

---

## 💰 Fase 6: Liquidación de Nómina, Prestaciones Especiales y Reliquidación

*Cumple Requerimientos #5, #9, #13 y Cierre de Brechas #1, #3 y #5.*

### Caso 6.1: Regla de Negocio: Bloqueo de Liquidación sin Contrato

- **Prueba de Control:**
  - Menú Lateral ➔ **Nómina Docente** ➔ Botón **`👤 Liquidar Empleado`**
  - Seleccionar un docente o administrativo que no cuente con contrato activo en el período seleccionado.
  - [ ] El sistema bloquea la acción con mensaje explícito: *"⚠️ Este empleado NO cuenta con un contrato activo registrado. Debe formalizar su vinculación en el módulo de Contratos antes de liquidar."*

### Caso 6.2: Liquidación de Nómina Multi-Régimen y Validación con Desprendible Real UPC

- **Ruta:** Menú Lateral ➔ **Nómina Docente**

1. **Pestaña Periodos de Nómina:** Seleccionar el período `2026-08` (Agosto 2026, Estado: `ABIERTO` o `EN_CURSO`).
2. **Acción:** Pulsar el botón **`⚙️ Liquidar Periodo Completo`** (o **`👤 Liquidar Empleado`** para liquidación individual).
3. **Validación Cruce 100% con Desprendible Oficial UPC (Prof. Adith Bismarck Pérez Orozco - Ocasional Tiempo Completo):**
   - En la pestaña **Liquidaciones del Periodo**, pulsar el botón **`📋 Desglose`** en la fila de Adith Bismarck Pérez:
   - [ ] **Sueldo Básico Ordinario (30 días):** `$ 6.313.763,00 COP`
   - [ ] **Bonificación por Posgrado (Doctorado 90% SMMLV Dec. 1279):** `$ 1.575.815,00 COP`
   - [ ] **Total Devengados:** `$ 7.889.578,00 COP`
   - [ ] **Deducciones de Ley e Institucionales Verificadas al Peso:**
     - **Aporte Salud Trabajador (4% - Redondeo PILA Dec. 1990/2016 a centena):** `$ 252.600,00 COP`
     - **Aporte Pensión Trabajador (4% - Redondeo PILA Dec. 1990/2016 a centena):** `$ 252.600,00 COP`
     - **Retención en la Fuente Salarial (Art. 383 E.T. > 95 UVT):** `$ 107.000,00 COP`
     - **Descuento Estampilla Pro-Universidad (0.2% salario básico):** `$ 12.628,00 COP`
   - [ ] **Total Deducciones:** `$ 624.828,00 COP`
   - [ ] **Neto a Pagar Exacto:** **`$ 7.264.750,00 COP`** *(Coincidencia exacta al 100% con el volante oficial UPC Código FGH-37 v.01)*.
4. **Verificación de Prestaciones Especiales Decreto 1279 (Docente de Planta):**
   - En la fila de docente Planta (Carlos Gómez):
   - [ ] **Provisión Prima de Vacaciones:** 5.56% de la base prestacional calculada y no vacía.
   - [ ] **Bonificación por Servicios Prestados:** Calculada (50% / 35% mensualizado según tope legal de SMMLV) con base en doceavas.
   - [ ] **Cesantías (8.33%), Intereses (1%), Prima de Servicios (8.33%), Vacaciones (4.17%)**.

### Caso 6.3: Flujo Completo de Reliquidación (CU-25 en UI - Brecha 5)

- **Ruta:** Pestaña **Liquidaciones del Periodo** o Modal de Desprendible

1. Con la liquidación en estado `GENERADA` (no pagada):
   - [ ] Se visualiza el botón interactivo **`🔄 Reliquidar`** en la fila de la tabla y **`🔄 Reliquidar Nómina`** en el pie del modal de desprendible.
2. Actualizar los puntos del docente o corregir parámetros normativos.
3. Pulsar **`🔄 Reliquidar`**:
   - [ ] El sistema ejecuta el ciclo de vida de reliquidación (`ciclo_vida.reliquidar()`).
   - [ ] Se recalculan devengados, deducciones y prestaciones con los nuevos datos.
   - [ ] Se guarda automáticamente en disco y se actualiza la tabla.
4. Una vez verificada, pulsar **`💵 Pagar`**:
   - [ ] El estado pasa a `PAGADA`.
   - [ ] Una liquidación pagada ya no puede ser alterada ni reliquidada.

### Caso 6.4: Inmutabilidad de Parámetros Usados en Liquidación (Brecha 3)

- **Ruta:** Menú Lateral ➔ **Parámetros Normativos**

1. Buscar el parámetro `VALOR_PUNTO_SALARIAL` o `SALARIO_MINIMO` cuya vigencia cubre el periodo liquidado.
2. Intentar editar su valor o eliminarlo:
   - [ ] El sistema lanza excepción / diálogo bloqueante: *"No se puede modificar el parámetro porque está siendo utilizado en liquidaciones de nómina aprobadas o pagadas."*
   - [ ] Parámetros no asociados a nóminas pagadas sí permiten actualización.

---

## 💾 Fase 7: Persistencia, Reinicio y Validación Automática

*Cumple Requerimientos #20, #57, #58 y #59 del Taller.*

| Paso | Acción de Prueba | Resultado Esperado | C++ | Python |
| :---: | :--- | :--- | :---: | :---: |
| **7.1** | Pulsar **`Guardar Cambios`** en el sidebar o barra superior | Mensaje en barra de estado: *"Datos guardados exitosamente en 'datos/'"*. Archivos `.txt` actualizados. | [ ] | [ ] |
| **7.2** | Cerrar la aplicación por completo y volver a iniciarla | La aplicación arranca sin pérdidas: las facultades, programas, personas, contratos, asignaciones, notas y desprendibles se cargan **100% intactos**. | [ ] | [ ] |
| **7.3** | Ejecutar suite de pruebas unitarias automatizadas: <br>`python -m pytest test_pita.py` | Salida: **22 passed in 1.5s (100% aprobado sin advertencias ni fallos)**. | [ ] | [ ] |
| **7.4** | Compilación C++ Release: <br>`cmake --build cpp/build --config Release` | Compilación limpia: **0 errores, binarios `pita_gui.exe` y `pita_backend.exe` generados exitosamente**. | [ ] | [ ] |

---

## 📊 Matriz de Cumplimiento de la Rúbrica del Taller 1 UPC

| # | Requerimiento Exigido en el Taller 1 UPC | Componente en C++ (`pita_gui`) | Componente en Python (`ui_gui`) | Estado Verificado |
| :-: | :--- | :--- | :--- | :---: |
| **1** | Gestión de conjunto de Facultades | `gui_vista_facultades.cpp` (Tab Facultades) | `view_facultades_gui.py` | ✅ CUMPLIDO |
| **2** | Gestión de conjunto de Programas Académicos | `gui_vista_facultades.cpp` (Tab Programas) | `view_facultades_gui.py` | ✅ CUMPLIDO |
| **CU-03** | Gestión de Planes de Estudio y Malla Curricular | `gestor_academico.cpp` | `academica_tabs.py` (Tab Planes) & `dialogs_planes_periodos.py` | ✅ CUMPLIDO |
| **CU-04** | Gestión y Apertura de Períodos Académicos | `gestor_periodos.cpp` | `academica_tabs.py` (Tab Períodos) & `dialogs_planes_periodos.py` | ✅ CUMPLIDO |
| **3** | Cursos, Estudiantes y Profesores por programa | `gui_vista_academica.cpp`, `gui_vista_personas.cpp` | `view_academica_gui.py`, `view_personas_gui.py` | ✅ CUMPLIDO |
| **4** | Información personal y de nómina por profesor | `gui_vista_contratos.cpp`, `gui_vista_nomina.cpp` | `view_contratos_gui.py`, `view_nomina_gui.py` | ✅ CUMPLIDO |
| **5** | Nómina Planta, Ocasional y Cátedra (Dec. 1279 / Ac. 027) | `calculadora_deducciones.cpp`, `gestor_nomina.cpp` | `nomina_service.py`, `liquidadores.py` | ✅ CUMPLIDO |
| **6** | Identificación de variables de entrada y salida | Estructura en `modelo_datos.h`, desprendibles y KPIs | `modelo_datos.py`, desprendibles y KPIs | ✅ CUMPLIDO |
| **7** | Estructura adaptada al Dec. 1279 y Ac. 006 de 2018 | Tablas de Factores, Categorías, Puntos y Producción | Sub-tabs de Factores y Producción Intelectual | ✅ CUMPLIDO |
| **8** | CRUD y Desactivación de Profesor, Estudiante y Admin | Modales en `gui_vista_personas.cpp` | Modales en `personas/` | ✅ CUMPLIDO |
| **9** | Simulación del cálculo del salario con normatividad | Motor de nómina multi-régimen | Motor de nómina multi-régimen | ✅ CUMPLIDO |
| **10** | Aspecto estético profesional e institucional UPC | ImGui estilizado con paleta moderna y contrastes | CustomTkinter con diseño Windows 11 Dark/Light | ✅ CUMPLIDO |
| **11** | Gerencia académica de estudiantes (matrícula y notas) | `gui_vista_academica.cpp` (Matrículas y Cancelación) | `academica_tabs.py` | ✅ CUMPLIDO |
| **12** | Cálculo de promedio y alertas de estudiantes en EBRA | Detección masiva EBRA, botón en UI y tutorías UPC | Detección masiva EBRA, botón en UI y tutorías UPC | ✅ CUMPLIDO |
| **13** | Descuentos de ley y prestaciones especiales MinTrabajo | Salud 4%, Pensión 4%, FSP, Prima Vac. 5.56%, Bonific. | Salud 4%, Pensión 4%, FSP, Prima Vac. 5.56%, Bonific. | ✅ CUMPLIDO |
| **20** | Validación de inmutabilidad de parámetros liquidados | `gestor_parametros.cpp` (`estaUsadoEnLiquidacion`) | `gestor_parametros.py` (`_esta_usado_en_liquidacion`) | ✅ CUMPLIDO |
| **25** | Ciclo de vida y reliquidación de nómina (CU-25) | Botón interactivo `Reliquidar` en tabla y modal | Botón interactivo `🔄 Reliquidar` en tabla y modal | ✅ CUMPLIDO |
| **57** | Persistencia de datos en archivos planos estructurados | `gestor_persistencia.cpp` (`datos/*.txt`) | `gestor_persistencia.py` (`datos/*.txt`) | ✅ CUMPLIDO |
| **58** | Cargar y guardar datos en archivo | Métodos `cargarDatos()` y `guardarDatos()` | Métodos `cargar_datos()` y `guardar_datos()` | ✅ CUMPLIDO |
| **59** | **Decidir si cargar datos o ejecutar con 0 datos** | **Botón `Iniciar Sin Datos` en sidebar** | **Botón `Iniciar Sin Datos` en bienvenida y sidebar** | ✅ CUMPLIDO |
