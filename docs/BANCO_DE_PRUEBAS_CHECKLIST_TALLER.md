# 📋 BANCO DE PRUEBAS Y CHECKLIST DE CONFORMIDAD
## Sistema PITA v2.0 (Programa Integrado de Transacciones Académicas y Nómina Docente)
**Universidad Popular del Cesar (UPC) — Facultad de Ingenierías y Tecnológicas**  
**Asignatura:** Estructura de Datos — Taller 1 (Listas Enlazadas & TADs)  
**Normatividad:** Decreto 1279 de 2002 | Acuerdo 027 del 31 de octubre de 2024 | Reglamento Estudiantil UPC  

---

## 🎯 Objetivo del Documento
Este banco de pruebas suministra una **guía secuencial paso a paso** diseñada para que docentes, evaluadores y estudiantes puedan validar el cumplimiento del **100% de los requisitos del Taller 1**, ejecutando el sistema en **Modo 0 Datos (Limpieza Total / Arranque en Blanco)** de acuerdo con el **Requerimiento #59**:
> *"El usuario puede decidir si cargar los datos del archivo o ejecutar sin datos."*

El protocolo es idéntico y aplicable tanto para la aplicación en **C++ (`pita_gui.exe` / `Taller.cpp`)** como para la aplicación en **Python (`main.py` / `ui_gui`)**.

---

## 🚀 Fase 0: Inicialización en Limpio (0 Datos)

| Paso | Acción en la Interfaz | Resultado Esperado | C++ | Python |
| :---: | :--- | :--- | :---: | :---: |
| **0.1** | Abrir la aplicación: <br>• C++: `pita_gui.exe` <br>• Python: `python main.py` | La ventana principal abre con diseño institucional UPC (Windows 11). | [ ] | [ ] |
| **0.2** | En el menú lateral izquierdo (Sidebar), sección **CONTROL DE DATOS**, pulsar el botón: <br>**`🧹 Iniciar Sin Datos (0 datos)`** | Mensaje en barra de estado: *"Sistema iniciado en limpio (0 datos operativos). Listo para ingresar datos desde cero."* | [ ] | [ ] |
| **0.3** | Ir a la vista **📊 Dashboard** | Todos los contadores operativos inician en **0**: <br>• 0 Estudiantes Registrados <br>• 0 Alertas EBRA <br>• 0 Docentes <br>• 0 Contratos <br>• Parámetros Salariales activos (SMMLV $1.750.905, Punto $23.924, etc.). | [ ] | [ ] |

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
  - [ ] En la pestaña **Universidad**, se confirma la asociación institucional.

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
  - **Categoría Docente:** `ASISTENTE`
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
  - [ ] Ambos estudiantes figuran en la pestaña **Estudiantes**.

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
   - **Curso 1:** Código `SIS-301` | Nombre `Estructuras de Datos` | Créditos `3` | Horas: `3h T / 2h P` | Nota Mínima: `3.0` | Cupo: `30`
   - **Curso 2:** Código `MAT-101` | Nombre `Calculo Diferencial` | Créditos `4` | Horas: `4h T / 1h P` | Nota Mínima: `3.0` | Cupo: `35`
- **Verificación:**
  - [ ] Ambos cursos aparecen con sus créditos y distribución horaria teórica/práctica.

### Caso 3.2: Apertura de Oferta / Grupo Abierto
- **Ruta:** Pestaña **Cursos & Ofertas** ➔ **Ofertas y Grupos Abiertos**
- En los datos del sistema, la oferta `OFER-1` queda habilitada para `SIS-301 Estructuras de Datos` (Grupo `01`, Aula `204 Sabanas`, Cupo: `30`).
- **Verificación:**
  - [ ] El semáforo de cupo muestra `30 / 30` en color verde brillante.

### Caso 3.3: Matrícula de Cursos
- **Ruta:** Pestaña **Matrículas de Cursos** ➔ Botón **`+ Matricular Estudiante`**
1. Seleccionar estudiante `EST-2026-001 - Juan Diego Rodriguez` en oferta `OFER-1`.
2. Seleccionar estudiante `EST-2026-002 - Andres Felipe Morales` en oferta `OFER-1`.
- **Verificación:**
  - [ ] Se crean las inscripciones `INS-1` e `INS-2`.
  - [ ] El cupo de la oferta disminuye a `28 / 30`.
  - [ ] Se visualiza el botón **`Cancelar`** en cada fila.

---

## 🚨 Fase 4: Evaluaciones, Calificaciones y Alertas EBRA
*Cumple Requerimientos #11 y #12 (Cálculo de promedio, detección de EBRA y recomendaciones).*

### Caso 4.1: Calificaciones de Asignaturas
- **Ruta:** Pestaña **Evaluaciones y Calificaciones** ➔ Botón **`+ Registrar Calificacion`**
1. **Calificación Alumno Normal (`INS-1` - Juan Diego):**
   - Calificación: `4.2`
   - [ ] La nota se pinta en **verde**, estado `APROBADO`, promedio por encima de 3.0.
2. **Calificación Alumno en Riesgo (`INS-2` - Andrés Morales):**
   - Calificación: `2.1`
   - [ ] La nota se pinta en **rojo brillante**, estado `REPROBADO`.
   - [ ] El promedio del estudiante baja a `2.1 / 5.0`.

### Caso 4.2: Detección y Panel de Alertas EBRA
- **Ruta:** Pestaña **Alertas EBRA**
- **Acción:** Pulsar el botón **`⚡ Ejecutar Deteccion EBRA Masiva`**
- **Verificación de Tarjetas KPI Superiores:**
  - [ ] `TOTAL ESTUDIANTES`: `2`
  - [ ] `NORMALIDAD ACADÉMICA`: `1` (50.0% del total)
  - [ ] `EN RIESGO EBRA`: `1` en color **rojo** (50.0% en riesgo crítico)
  - [ ] `PROMEDIO GENERAL`: `3.15 / 5.0`
- **Verificación de la Tabla de Alertas:**
  - [ ] Fila generada para `EST-2026-002 (Andrés Felipe Morales)`.
  - [ ] Tipo de alerta: `EBRA` (Bajo Rendimiento Académico).
  - [ ] Acción Recomendada: Badge `Plan Tutoria UPC`.
- **En el Dashboard General:**
  - [ ] La tarjeta superior `Alertas EBRA Activas` marca `1`.
  - [ ] El panel izquierdo resalta el caso crítico de Andrés Felipe Morales con su promedio `2.10`.

---

## 📝 Fase 5: Contratación Docente y Régimen Dec. 1279
*Cumple Requerimientos #4, #5, #6, #7, #9 y #13 del Taller.*

### Caso 5.1: Vinculación Contractual
- **Ruta:** Menú Lateral ➔ **Contratos & Factores Salariales** ➔ Botón **`+ Registrar Contrato Docente`**
1. **Contrato Docente Planta:**
   - **Docente:** `Carlos Alberto Gomez Solano`
   - **Tipo:** `DOCENTE_PLANTA` | **Horas:** `40.0`
   - **Salario Base:** `$5.981.000` (250 puntos × $23.924 COP)
   - **Vigencia:** `2026-02-01` al `2026-11-30`
2. **Contrato Docente Cátedra:**
   - **Docente:** `Maria Mercedes Perez Cuello`
   - **Tipo:** `DOCENTE_CATEDRA` | **Horas:** `16.0` (Validar que si se ingresa > 18h muestre advertencia legal)
   - **Salario Base:** `$1.850.000`
- **Verificación de Tarjetas KPI:**
  - [ ] `CONTRATOS ACTIVOS`: `2 Activos` (2 vinculaciones totales)
  - [ ] `DISTRIBUCIÓN DOCENTE`: `1 Planta | 1 Trans.`
  - [ ] `PUNTOS SALARIALES TOTALES`: `250 Pts`
  - [ ] `MASA SALARIAL MENSUAL`: `$7.831.000 COP`

### Caso 5.2: Reconocimiento de Puntos Salariales (Comité de Puntaje Dec. 1279)
- **Ruta:** Botón **`⭐ Reconocer Puntos / Productividad`**
1. **Puntos por Título Académico:**
   - **Docente:** `Carlos Alberto Gomez Solano`
   - **Tipo Factor:** `TITULO_ACADEMICO`
   - **Concepto:** `Doctorado en Ciencias de la Computacion`
   - **Puntos:** `120.0` | **Acto:** `Resolucion VRA-042-2026`
   - [ ] Al confirmar, los puntos de Carlos aumentan a **370 pts** y se lista en **Factores Salariales Reconocidos**.
2. **Puntos por Producción Intelectual:**
   - **Docente:** `Carlos Alberto Gomez Solano`
   - **Tipo de Obra:** `ARTICULO`
   - **Título:** `Optimizacion de Algoritmos en Grafos Paralelos`
   - **Editorial:** `IEEE Transactions on Computers`
   - **Número de Autores:** `2` (Se aplica factor de coautoría automático del 80%)
   - **Puntos Reconocidos:** `12.0`
   - [ ] Al confirmar, los puntos totales del docente suben a **382 pts** y se lista en **Producción Intelectual / Obras**.

---

## 💰 Fase 6: Liquidación de Nómina con Descuentos de Ley
*Cumple Requerimientos #5, #9 y #13 (Mi Calculadora MinTrabajo: Salud 4%, Pensión 4%, FSP 1%, Aportes Patronales, Prestaciones).*

### Caso 6.1: Configuración de Período y Liquidación
- **Ruta:** Menú Lateral ➔ **Nomina Docente**
1. **Pestaña Periodos:** Crear o seleccionar `2026-01` (Enero 2026).
2. **Acción Principal:** Pulsar el botón **`⚡ Liquidar Nomina General`**.
- **Verificación de Tarjetas KPI de Nómina:**
  - [ ] `TOTAL DEVENGADO`: Refleja el salario bruto consolidado.
  - [ ] `TOTAL DEDUCCIONES`: Suma exacta de Salud (4%) + Pensión (4%) + FSP (si devenga ≥ 4 SMMLV).
  - [ ] `NETO A PAGAR`: Devengado menos deducciones.
  - [ ] `COSTO TOTAL UPC`: Incluye la carga prestacional patronal (Cesantías 8.33%, Intereses 1%, Prima 8.33%, Vacaciones 4.17%, ARL, Caja 4%, SENA, ICBF).

### Caso 6.2: Verificación de Desprendible de Pago Individual
- **Ruta:** Pestaña **Liquidaciones del Periodo** ➔ Botón **`👁️ Ver Desprendible`** sobre Carlos Gómez:
  - [ ] **Sueldo Básico:** Liquidado conforme a su vinculación y puntos.
  - [ ] **Deducción Salud (4%):** Calculada exactamente sobre el IBC.
  - [ ] **Deducción Pensión (4%):** Calculada exactamente sobre el IBC.
  - [ ] **Fondo Solidaridad Pensional (1%):** Aplicado legalmente al superar 4 SMMLV ($7.003.620 COP).
  - [ ] **Aprobar y Pagar:** Al pulsar **`💵 Pagar`**, el estado cambia a `PAGADA` mediante `TRANSFERENCIA_BANCARIA`.

---

## 💾 Fase 7: Persistencia y Ciclo de Reinicio
*Cumple Requerimientos #20, #57, #58 y #59 del Taller.*

| Paso | Acción de Prueba | Resultado Esperado | C++ | Python |
| :---: | :--- | :--- | :---: | :---: |
| **7.1** | Pulsar **`Guardar Cambios`** en el sidebar | Mensaje verde en barra de estado: *"Datos guardados exitosamente en 'datos/'"* | [ ] | [ ] |
| **7.2** | Cerrar la aplicación por completo y volver a iniciarla | La aplicación arranca sin pérdidas: la facultad `FIT`, el programa `SIS`, las personas, contratos, notas y nómina se cargan **100% intactos**. | [ ] | [ ] |
| **7.3** | Ejecutar pruebas unitarias automatizadas: <br>`python -m pytest test_pita.py` | Salida: **17 passed in 0.43s (100% aprobado)**. | [ ] | [ ] |
| **7.4** | Compilar en C++: <br>`cmake --build . --config Release` | Compilación limpia: **0 errores, 0 advertencias**, binarios generados. | [ ] | [ ] |

---

## 📊 Matriz de Cumplimiento de la Rúbrica del Taller

| # | Requerimiento Exigido en el Taller 1 UPC | Componente en C++ (`pita_gui`) | Componente en Python (`ui_gui`) | Estado |
| :-: | :--- | :--- | :--- | :---: |
| **1** | Gestión de conjunto de Facultades | `gui_vista_facultades.cpp` (Tab Facultades) | `view_facultades_gui.py` | ✅ CUMPLIDO |
| **2** | Gestión de conjunto de Programas Académicos | `gui_vista_facultades.cpp` (Tab Programas) | `view_facultades_gui.py` | ✅ CUMPLIDO |
| **3** | Cursos, Estudiantes y Profesores por programa | `gui_vista_academica.cpp`, `gui_vista_personas.cpp` | `view_academica_gui.py`, `view_personas_gui.py` | ✅ CUMPLIDO |
| **4** | Información personal y de nómina por profesor | `gui_vista_contratos.cpp`, `gui_vista_nomina.cpp` | `view_contratos_gui.py`, `view_nomina_gui.py` | ✅ CUMPLIDO |
| **5** | Nómina Planta, Ocasional y Cátedra (Dec. 1279 / Ac. 027) | `calculadora_deducciones.cpp`, `gestor_nomina.cpp` | `nomina_service.py`, `calculadora_prestaciones.py` | ✅ CUMPLIDO |
| **6** | Identificación de variables de entrada y salida | Estructura en `modelo_datos.h`, desprendibles y KPIs | `modelo_datos.py`, desprendibles y KPIs | ✅ CUMPLIDO |
| **7** | Estructura adaptada al Dec. 1279 y Ac. 006 de 2018 | Tablas de Factores, Categorías, Puntos y Producción | Sub-tabs de Factores y Producción Intelectual | ✅ CUMPLIDO |
| **8** | CRUD y Desactivación de Profesor, Estudiante y Admin | Modales en `gui_vista_personas.cpp` | Modales en `personas/` | ✅ CUMPLIDO |
| **9** | Simulación del cálculo del salario con normatividad | Motor de nómina multi-régimen | Motor de nómina multi-régimen | ✅ CUMPLIDO |
| **10**| Aspecto estético profesional e institucional UPC | ImGui estilizado con paleta Windows 11 UPC | CustomTkinter con diseño Windows 11 Light | ✅ CUMPLIDO |
| **11**| Gerencia académica de estudiantes (matrícula y cancelación) | `gui_vista_academica.cpp` (Matrículas y Cancelación) | `academica_tabs.py` | ✅ CUMPLIDO |
| **12**| Cálculo de promedio y alertas de estudiantes en EBRA | Algoritmo EBRA (< 3.0), KPIs y tutoría UPC | Algoritmo EBRA (< 3.0), KPIs y tutoría UPC | ✅ CUMPLIDO |
| **13**| Descuentos de ley (Salud 4%, Pensión 4%, Prestaciones) | Conceptos 1..15 reglamentarios MinTrabajo | Conceptos 1..15 reglamentarios MinTrabajo | ✅ CUMPLIDO |
| **57**| Persistencia de datos en archivos | `gestor_persistencia.cpp` (`datos/*.txt`) | `gestor_persistencia.py` (`datos/*.txt`) | ✅ CUMPLIDO |
| **58**| Cargar y guardar datos en archivo | Métodos `cargarDatos()` y `guardarDatos()` | Métodos `cargar_datos()` y `guardar_datos()` | ✅ CUMPLIDO |
| **59**| **Decidir si cargar datos o ejecutar con 0 datos** | **Botón `Iniciar Sin Datos` en sidebar** | **Botón `Iniciar Sin Datos` en bienvenida y sidebar** | ✅ CUMPLIDO |
