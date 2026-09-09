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
- **Datos de Prueba:**
  - **Código:** `FIT`
  - **Nombre:** `Facultad de Ingenierias y Tecnologicas`
  - **Ubicación:** `Campus Sabanas, Bloque B`
  - **Decano / Responsable:** `Dr. Efraín Quintero Maya`
- **Verificación:**
  - [ ] Aparece la fila en la tabla con código `FIT` y badge `ACTIVO`.
  - [ ] En la pestaña **Universidad**, se confirma la visualización jerárquica de la facultad.

### Caso 1.2: Registro de Programa Académico
- **Ruta:** Pestaña **Programas Académicos** ➔ Botón **`+ Nuevo Programa`**
- **Datos de Prueba:**
  - **Código:** `SIS`
  - **Nombre:** `Ingenieria de Sistemas`
  - **Facultad:** Seleccionar `FIT`
  - **Nivel Formación:** `PREGRADO`
  - **Créditos Totales:** `160`
- **Verificación:**
  - [ ] El programa queda vinculado a la facultad `FIT` con 160 créditos y estado `ACTIVO`.

---

## 👥 Fase 2: Gestión de Personas y Roles
*Cumple Requerimientos #3, #4, #8 y #10 del Taller (TAD con Creación, Inclusión, Consulta, Modificación, Desactivación).*

### Caso 2.1: Registro de Profesor de Planta (Dec. 1279)
- **Ruta:** Menú Lateral ➔ **Personas** ➔ Botón **`+ Registrar Persona / Rol`**
- **Datos Personales:**
  - **Tipo Doc:** `CC` | **Número:** `12345678`
  - **Nombres:** `Carlos Alberto` | **Apellidos:** `Gomez Solano`
  - **Correo:** `cgomez@unicesar.edu.co` | **Ciudad:** `Valledupar`
- **Rol Asignado:** Seleccionar `Profesor`
  - **Código Profesor:** `DOC-001`
  - **Tipo Profesor:** `DOCENTE_PLANTA`
  - **Dedicación:** `TIEMPO_COMPLETO`
  - **Horas Semanales:** `40.0`
  - **Categoría Docente:** `ASISTENTE` (Piso legal mínimo: 58 puntos)
  - **Puntos Salariales Iniciales:** `250.0`
- **Verificación:**
  - [ ] Se visualiza en pestaña **Personas** y en pestaña **Profesores** con 250 pts salariales.

### Caso 2.2: Registro de Profesor de Cátedra (Acuerdo 027/2024)
- **Ruta:** Botón **`+ Registrar Persona / Rol`**
- **Datos Personales:**
  - **Tipo Doc:** `CC` | **Número:** `23456789`
  - **Nombres:** `Maria Mercedes` | **Apellidos:** `Perez Cuello`
  - **Correo:** `mperez@unicesar.edu.co` | **Ciudad:** `Valledupar`
- **Rol Asignado:** Seleccionar `Profesor`
  - **Código Profesor:** `DOC-002`
  - **Tipo Profesor:** `DOCENTE_CATEDRA`
  - **Dedicación:** `HORA_CATEDRA`
  - **Horas Semanales:** `16.0` (Respetando tope legal de 18h)
  - **Categoría:** `INSTRUCTOR`
  - **Puntos Salariales:** `0.0`
- **Verificación:**
  - [ ] Aparece correctamente clasificado como `DOCENTE_CATEDRA` (16h semanales).

### Caso 2.3: Registro de Estudiantes (Regular y Caso EBRA)
1. **Estudiante 1 (Rendimiento Óptimo):**
   - **CC:** `1003456789` | **Nombre:** `Juan Diego Rodriguez Vega`
   - **Rol:** `Estudiante` | **Código:** `EST-2026-001` | **Programa:** `Ingenieria de Sistemas` | **Semestre:** `3`
2. **Estudiante 2 (Candidato a Alerta EBRA):**
   - **CC:** `1004567890` | **Nombre:** `Andres Felipe Morales Mejia`
   - **Rol:** `Estudiante` | **Código:** `EST-2026-002` | **Programa:** `Ingenieria de Sistemas` | **Semestre:** `2`
- **Verificación:**
  - [ ] Ambos estudiantes figuran en la pestaña **Estudiantes** con estado inicial `ACTIVO`.

### Caso 2.4: Registro de Personal Administrativo
- **Ruta:** Botón **`+ Registrar Persona / Rol`**
- **Datos:** `CC 34567890` | `Laura Patricia Sanchez` | **Rol:** `Administrativo` | **Cargo:** `Secretaria Academica FIT`
- **Verificación:**
  - [ ] Aparece en la pestaña **Administrativos** con su cargo y estado `ACTIVO`.

### Caso 2.5: Validación del Buscador en Tiempo Real y Desactivación
- [ ] En la pestaña **Personas**, escribir `Morales` en el buscador: la tabla se filtra inmediatamente mostrando solo a Andrés.
- [ ] Pulsar **`Limpiar`**: la tabla restaura todas las personas.
- [ ] Probar botón **`Desactivar`** en una persona: su badge cambia a `INACTIVO`. Al pulsar **`Activar`**, regresa a `ACTIVO`.

---

## 📚 Fase 3: Catálogo, Ofertas y Matrícula Académica
*Cumple Requerimientos #3, #11 y #12 del Taller.*

### Caso 3.1: Configuración de Período y Cursos
- **Ruta:** Menú Lateral ➔ **Gestion Académica**
1. **Pestaña Periodos:** Verificar o crear periodo activo `2026-1` (Estado: `ABIERTO`).
2. **Pestaña Cursos & Ofertas ➔ Catálogo de Asignaturas ➔ `+ Nueva Asignatura`:**
   - **Curso 1:** Código `SIS-301` | Nombre `Estructuras de Datos` | Créditos `3` | Horas: `3h T / 2h P` | **Nota Mínima Aprobatoria:** `3.0` | Cupo: `30`
   - **Curso 2 (Umbral Diferenciado):** Código `SIS-401` | Nombre `Sistemas Operativos Avanzados` | Créditos `4` | Horas: `4h T / 1h P` | **Nota Mínima Aprobatoria:** `3.5` | Cupo: `25`
- **Verificación:**
  - [ ] Ambos cursos aparecen con sus créditos, distribución teórica/práctica y sus respectivas notas mínimas aprobatorias configurables.

### Caso 3.2: Apertura de Oferta / Grupo Abierto
- **Ruta:** Pestaña **Cursos & Ofertas** ➔ **Ofertas y Grupos Abiertos** ➔ **`+ Nueva Oferta`**
- **Oferta 1:** `SIS-301 Estructuras de Datos` (Grupo `01`, Aula `204 Sabanas`, Cupo: `30`, Profesor: `DOC-001`).
- **Oferta 2:** `SIS-401 Sistemas Operativos Avanzados` (Grupo `01`, Aula `301 Sabanas`, Cupo: `25`, Profesor: `DOC-002`).
- **Verificación:**
  - [ ] Los semáforos de cupos muestran disponibilidad completa (`30 / 30` y `25 / 25`) en color verde.

### Caso 3.3: Matrícula de Cursos
- **Ruta:** Pestaña **Matrículas de Cursos** ➔ Botón **`+ Matricular Estudiante`**
1. Matricular `EST-2026-001 - Juan Diego Rodriguez` en oferta `SIS-301`.
2. Matricular `EST-2026-002 - Andres Felipe Morales` en oferta `SIS-301` y en oferta `SIS-401`.
- **Verificación:**
  - [ ] Se crean las inscripciones de detalle de matrícula.
  - [ ] Los cupos disponibles se descuentan correctamente.
  - [ ] Se visualiza la opción de **`Cancelar`** matrícula en cada fila.

---

## 🚨 Fase 4: Evaluaciones, Calificaciones y Alertas EBRA
*Cumple Requerimientos #11, #12 y Cierre de Brechas #4 y #6 (Umbral dinámico `notaMinimaAprobatoria` y detección EBRA en lote en UI).*

### Caso 4.1: Calificaciones con Umbrales Dinámicos
- **Ruta:** Pestaña **Evaluaciones y Calificaciones** ➔ Botón **`+ Registrar Calificacion`**
1. **Estudiante Juan Diego (`EST-2026-001`) en `SIS-301` (Umbral 3.0):**
   - Calificación final: `4.2`
   - [ ] Estado: `APROBADO` en verde.
2. **Estudiante Andrés Morales (`EST-2026-002`) en `SIS-301` (Umbral 3.0):**
   - Calificación final: `2.1`
   - [ ] Estado: `REPROBADO` en rojo brillante.
3. **Estudiante Andrés Morales (`EST-2026-002`) en `SIS-401` (Umbral 3.5):**
   - Calificación: `3.2` (Nota inferior a 3.5 pero superior a 3.0)
   - [ ] **Comportamiento Dinámico Verificado:** Se clasifica como `REPROBADO` debido a que la asignatura exige 3.5 de nota mínima.

### Caso 4.2: Detección y Panel de Alertas EBRA en Tiempo Real
- **Ruta:** Pestaña **Alertas EBRA** (o **Informe Alertas EBRA**)
- **Acción:** Pulsar el botón interactivo **`⚡ Ejecutar Detección EBRA Masiva`**
- **Verificación:**
  - [ ] Se ejecuta `evaluar_alertas_periodo` / `evaluarAlertasPeriodo` en backend.
  - [ ] Diálogo / Mensaje confirma las alertas EBRA evaluadas y registradas.
  - [ ] **Tarjetas KPI EBRA:**
    - `Total Estudiantes`: Refleja el censo activo.
    - `En Riesgo EBRA`: Marca los estudiantes con promedio < 3.0 o condición EBRA en rojo crítico.
  - [ ] **Tabla de Alertas / Diagnóstico:**
    - Fila generada para `EST-2026-002 (Andrés Felipe Morales)`.
    - Tipo de Alerta: `EBRA`.
    - Motivo: `Bajo Rendimiento Académico`.
    - Acción Recomendada: Badge `Plan Tutoria UPC` / Remitir a acompañamiento institucional.
  - [ ] En el **Dashboard General**: La tarjeta KPI y el panel de alertas en riesgo reflejan inmediatamente el estado de Andrés.

---

## 📝 Fase 5: Contratación Docente y Factores Salariales (Dec. 1279)
*Cumple Requerimientos #4, #5, #6, #7, #9, #13 y Cierre de Brecha #2 (Pisos de escalafón 37/58/74/96).*

### Caso 5.1: Vinculación Contractual Obligatoria
- **Ruta:** Menú Lateral ➔ **Contratos & Factores Salariales** ➔ Botón **`+ Registrar Contrato`**
1. **Contrato Docente Planta:**
   - **Docente:** `Carlos Alberto Gomez Solano`
   - **Tipo Contrato:** `PLANTA` | **Dedicación:** `TIEMPO_COMPLETO` | **Horas:** `40.0`
   - **Régimen:** `DECRETO_1279`
   - **Vigencia:** `2026-01-01` al `2026-12-31`
2. **Contrato Docente Cátedra:**
   - **Docente:** `Maria Mercedes Perez Cuello`
   - **Tipo Contrato:** `CATEDRA` | **Dedicación:** `HORA_CATEDRA` | **Horas:** `16.0` (Validar control legal <= 18h)
   - **Vigencia:** `2026-02-01` al `2026-06-30`
3. **Contrato Administrativo:**
   - **Funcionario:** `Laura Patricia Sanchez`
   - **Tipo Contrato:** `TERMINO_INDEFINIDO` | **Horas:** `40.0`
- **Verificación:**
  - [ ] Todos los contratos se registran con su cargo y vigencia.
  - [ ] Las tarjetas KPI consolidan contratos activos, distribución docente y masa salarial.

### Caso 5.2: Reconocimiento de Puntos y Pisos Salariales de Escalafón
- **Ruta:** Pestaña **Factores Salariales & Producción** ➔ Botón **`⭐ Reconocer Puntos / Productividad`**
1. **Puntos por Título Académico:**
   - **Docente:** `Carlos Alberto Gomez Solano` (Categoría `ASISTENTE`)
   - **Tipo Factor:** `TITULO_ACADEMICO`
   - **Concepto:** `Doctorado en Ciencias de la Computacion`
   - **Puntos:** `120.0` | **Acto Administrativo:** `Resolucion VRA-042-2026`
   - [ ] Al confirmar, se listan los 120 pts reconocidos.
2. **Puntos por Producción Intelectual:**
   - **Docente:** `Carlos Alberto Gomez Solano`
   - **Tipo de Obra:** `ARTICULO`
   - **Título:** `Optimizacion de Algoritmos en Grafos Paralelos`
   - **Revista / Editorial:** `IEEE Transactions on Computers`
   - **Número de Autores:** `2` (Se aplica factor de coautoría legal del 80%)
   - **Puntos Reconocidos:** `12.0`
   - [ ] Al confirmar, la producción queda registrada con acto administrativo.
3. **Piso Legal de Escalafón (Brecha 2):**
   - [ ] Si un docente de planta tiene categoría `TITULAR` y acumula pocos puntos, el sistema le garantiza automáticamente el piso legal de **96 puntos**.
   - [ ] Si es `ASISTENTE`, garantiza mínimo **58 puntos**.
   - [ ] Si es `AUXILIAR`, garantiza mínimo **37 puntos**.
   - [ ] Si es `ASOCIADO`, garantiza mínimo **74 puntos**.

---

## 💰 Fase 6: Liquidación de Nómina, Prestaciones Especiales y Reliquidación
*Cumple Requerimientos #5, #9, #13 y Cierre de Brechas #1, #3 y #5.*

### Caso 6.1: Regla de Negocio: Bloqueo de Liquidación sin Contrato
- **Prueba de Control:**
  - [ ] Intentar liquidar un docente que no tenga contrato activo en el período: el sistema **no** lo incluye en la nómina y emite advertencia de contrato ausente.

### Caso 6.2: Liquidación de Nómina con Prestaciones del Decreto 1279
- **Ruta:** Menú Lateral ➔ **Nómina Docente**
1. **Pestaña Periodos:** Seleccionar periodo `2026-01` (Enero 2026, Estado: `ABIERTO`).
2. **Acción:** Pulsar el botón **`⚡ Liquidar Nomina General`**.
- **Verificación de Desprendible Detallado (Brecha 1):**
  - Pulsar **`👁️ Ver Desprendible`** sobre Carlos Gómez (Planta):
  - [ ] **Sueldo Básico:** Calculado como `Puntos × Valor Punto ($23.924 COP)`.
  - [ ] **Deducciones de Ley:** Salud (4%), Pensión (4%), Fondo de Solidaridad Pensional (1% al superar 4 SMMLV).
  - [ ] **Prestaciones Especiales Decreto 1279 Verificadas en Desprendible:**
    - **Provisión Prima de Vacaciones:** 5.56% de la base prestacional calculada y no vacía.
    - **Bonificación por Servicios Prestados:** Calculada (50% / 35% mensualizado según tope) con base en doceavas.
    - **Cesantías (8.33%), Intereses (1%), Prima de Servicios (8.33%), Vacaciones (4.17%)**.

### Caso 6.3: Flujo Completo de Reliquidación (CU-25 en UI - Brecha 5)
- **Ruta:** Pestaña **Liquidaciones del Periodo** o Modal de Desprendible
1. Con la liquidación en estado `GENERADA` (no pagada):
   - [ ] Se visualiza el botón interactivo **`🔄 Reliquidar`** en la fila de la tabla y en el pie del modal de desprendible.
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
| **7.3** | Ejecutar suite de pruebas unitarias automatizadas: <br>`python -m pytest test_pita.py` | Salida: **18 passed in 0.44s (100% aprobado sin advertencias ni fallos)**. | [ ] | [ ] |
| **7.4** | Compilación C++ Release: <br>`cmake --build cpp/build --config Release` | Compilación limpia: **0 errores, binarios `pita_gui.exe` y `pita_backend.exe` generados exitosamente**. | [ ] | [ ] |

---

## 📊 Matriz de Cumplimiento de la Rúbrica del Taller 1 UPC

| # | Requerimiento Exigido en el Taller 1 UPC | Componente en C++ (`pita_gui`) | Componente en Python (`ui_gui`) | Estado Verificado |
| :-: | :--- | :--- | :--- | :---: |
| **1** | Gestión de conjunto de Facultades | `gui_vista_facultades.cpp` (Tab Facultades) | `view_facultades_gui.py` | ✅ CUMPLIDO |
| **2** | Gestión de conjunto de Programas Académicos | `gui_vista_facultades.cpp` (Tab Programas) | `view_facultades_gui.py` | ✅ CUMPLIDO |
| **3** | Cursos, Estudiantes y Profesores por programa | `gui_vista_academica.cpp`, `gui_vista_personas.cpp` | `view_academica_gui.py`, `view_personas_gui.py` | ✅ CUMPLIDO |
| **4** | Información personal y de nómina por profesor | `gui_vista_contratos.cpp`, `gui_vista_nomina.cpp` | `view_contratos_gui.py`, `view_nomina_gui.py` | ✅ CUMPLIDO |
| **5** | Nómina Planta, Ocasional y Cátedra (Dec. 1279 / Ac. 027) | `calculadora_deducciones.cpp`, `gestor_nomina.cpp` | `nomina_service.py`, `liquidadores.py` | ✅ CUMPLIDO |
| **6** | Identificación de variables de entrada y salida | Estructura en `modelo_datos.h`, desprendibles y KPIs | `modelo_datos.py`, desprendibles y KPIs | ✅ CUMPLIDO |
| **7** | Estructura adaptada al Dec. 1279 y Ac. 006 de 2018 | Tablas de Factores, Categorías, Puntos y Producción | Sub-tabs de Factores y Producción Intelectual | ✅ CUMPLIDO |
| **8** | CRUD y Desactivación de Profesor, Estudiante y Admin | Modales en `gui_vista_personas.cpp` | Modales en `personas/` | ✅ CUMPLIDO |
| **9** | Simulación del cálculo del salario con normatividad | Motor de nómina multi-régimen | Motor de nómina multi-régimen | ✅ CUMPLIDO |
| **10**| Aspecto estético profesional e institucional UPC | ImGui estilizado con paleta moderna y contrastes | CustomTkinter con diseño Windows 11 Dark/Light | ✅ CUMPLIDO |
| **11**| Gerencia académica de estudiantes (matrícula y notas) | `gui_vista_academica.cpp` (Matrículas y Cancelación) | `academica_tabs.py` | ✅ CUMPLIDO |
| **12**| Cálculo de promedio y alertas de estudiantes en EBRA | Detección masiva EBRA, botón en UI y tutorías UPC | Detección masiva EBRA, botón en UI y tutorías UPC | ✅ CUMPLIDO |
| **13**| Descuentos de ley y prestaciones especiales MinTrabajo | Salud 4%, Pensión 4%, FSP, Prima Vac. 5.56%, Bonific. | Salud 4%, Pensión 4%, FSP, Prima Vac. 5.56%, Bonific. | ✅ CUMPLIDO |
| **20**| Validación de inmutabilidad de parámetros liquidados | `gestor_parametros.cpp` (`estaUsadoEnLiquidacion`) | `gestor_parametros.py` (`_esta_usado_en_liquidacion`) | ✅ CUMPLIDO |
| **25**| Ciclo de vida y reliquidación de nómina (CU-25) | Botón interactivo `Reliquidar` en tabla y modal | Botón interactivo `🔄 Reliquidar` en tabla y modal | ✅ CUMPLIDO |
| **57**| Persistencia de datos en archivos planos estructurados | `gestor_persistencia.cpp` (`datos/*.txt`) | `gestor_persistencia.py` (`datos/*.txt`) | ✅ CUMPLIDO |
| **58**| Cargar y guardar datos en archivo | Métodos `cargarDatos()` y `guardarDatos()` | Métodos `cargar_datos()` y `guardar_datos()` | ✅ CUMPLIDO |
| **59**| **Decidir si cargar datos o ejecutar con 0 datos** | **Botón `Iniciar Sin Datos` en sidebar** | **Botón `Iniciar Sin Datos` en bienvenida y sidebar** | ✅ CUMPLIDO |

