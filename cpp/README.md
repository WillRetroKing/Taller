# PITA C++ — Módulo Backend e Interfaz Gráfica de Alto Rendimiento
### Universidad Popular del Cesar (UPC) — Departamento de Ingeniería de Sistemas

[![Standard: C++17](https://img.shields.io/badge/C%2B%2B-17-blue.svg)](https://en.cppreference.com/w/cpp/17)
[![Build Tool: CMake](https://img.shields.io/badge/Build-CMake%203.20%2B-brightgreen.svg)](https://cmake.org/)
[![GUI: Dear ImGui](https://img.shields.io/badge/GUI-Dear%20ImGui%20v1.91-red.svg)](https://github.com/ocornut/imgui)
[![Windowing: GLFW](https://img.shields.io/badge/Window-GLFW%203.4-informational.svg)](https://www.glfw.org/)

---

## 📌 Introducción y Cumplimiento de Requerimientos

Este submódulo contiene la implementación completa y desacoplada del sistema **PITA** en **C++17**, satisfaciendo con rigor los lineamientos académicos y estructurales del taller universitario:

1. **Estructura de Datos Propia (`ListaEnlazada<T>`)**:
   - Para cumplir con la exigencia pedagógica de estructuras de datos fundamentales sin depender de contenedores cerrados de la STL (`std::vector` / `std::list`), se diseñó una plantilla genérica `ListaEnlazada<T>` con punteros dinámicos, iteración eficiente y métodos de manipulación (`push_back`, `obtener`, `eliminar`, `tamano`).
2. **Arquitectura Desacoplada en Capas**:
   - Separación estricta entre el **Modelo de Dominio**, **Gestores de Negocio**, **Motor de Nómina & Prestaciones**, **Capa de Persistencia** y **Vistas de Usuario**.
3. **Persistencia Transaccional con Integridad Referencial**:
   - Lee y escribe directamente sobre los archivos planos situados en el directorio `datos/`, garantizando compatibilidad e intercambio de datos con la versión en Python.
4. **Interfaz Gráfica Modular (Dear ImGui + GLFW + OpenGL3)**:
   - GUI de alto rendimiento y bajo consumo de memoria con un tema limpio estilo Windows 11 Fluent/Light, métricas responsivas y modales de diálogo para todas las operaciones CRUD.

---

## 🏗️ Arquitectura del Código Fuente en C++

```text
cpp/
├── CMakeLists.txt              # Script de compilación CMake (descarga GLFW e ImGui con FetchContent)
├── main.cpp                    # Punto de entrada para el CLI verificador de backend (pita_backend)
│
├── dominio/                    # Entidades de negocio y estructuras de datos
│   ├── lista_enlazada.h        # Estructura de datos dinámica propia implementada con plantillas (templates)
│   └── modelo_datos.h          # Clases/Structs (Persona, Estudiante, Profesor, Contrato, Liquidacion, etc.)
│
├── gestores/                   # Capa de servicios y reglas de negocio
│   ├── gestor_academico.h/.cpp # Validación de asignaturas, créditos y requisitos
│   ├── gestor_contratos.h/.cpp # Estados y vigencia contractual docente
│   ├── gestor_factores.h/.cpp  # Bonificaciones, primas y factores Decreto 1279
│   ├── gestor_parametros.h/.cpp# Parámetros institucionales (puntos, SMMLV, auxilio transporte)
│   ├── gestor_periodos.h/.cpp  # Periodos académicos y calendarios de corte
│   ├── gestor_personas.h/.cpp  # Directorio y roles de personas
│   └── gestores_academicos.h/.cpp # Matrículas y calificaciones con control EBRA
│
├── nomina/                     # Motor de liquidación salarial y prestaciones
│   ├── calculadora_deducciones.h/.cpp  # Retenciones, aportes a salud (4%) y pensión (4%)
│   ├── calculadora_prestaciones.h/.cpp # Cesantías, primas y vacaciones
│   └── gestor_nomina.h/.cpp            # Orquestador general de liquidación mensual
│
├── persistencia/               # Capa de acceso a datos y archivo
│   └── gestor_persistencia.h/.cpp      # Serializador/Deserializador plano con integridad referencial
│
├── tests/                      # Suite de pruebas unitarias automatizadas (GoogleTest / CTest)
│   ├── test_crud.cpp           # Validación de operaciones CRUD y código único
│   ├── test_persistencia.cpp   # Guardado, carga, integridad referencial y aislamiento físico
│   ├── test_academico.cpp      # Matrículas, cruce de horarios, calificaciones y control EBRA
│   ├── test_nomina.cpp         # CU-21, deducciones exactas 4%, liquidaciones Planta/Ocasional/Cátedra y anual
│   ├── test_puntos_doctorado.cpp # Puntos Decreto 1279, régimen y bonificaciones Acuerdo 027
│   └── test_multi_universidades.cpp # Persistencia multi-entidad y desglose anual consolidado
│
└── gui/                        # Interfaz gráfica modularizada (Dear ImGui + GLFW)
    ├── gui_main.cpp            # Punto de entrada de la aplicación gráfica (pita_gui)
    ├── gui_app.h               # Declaración de la clase PITAApp, ciclo de vida y buffers
    ├── gui_app.cpp             # Shell principal, navegación, Dashboard, estado y dispatcher
    ├── gui_controller.h/.cpp   # Controlador que conecta la GUI con la persistencia
    ├── gui_vista_personas.cpp  # Gestión de Personas, Profesores, Estudiantes y Administrativos
    ├── gui_vista_facultades.cpp# Facultades y Programas académicos + Modales

    ├── gui_vista_academica.cpp # Cursos, Matrículas, Calificaciones y Alertas EBRA
    ├── gui_vista_contratos.cpp # Contratos docentes y terminaciones laborales
    ├── gui_vista_nomina.cpp    # Periodos, Liquidación general/individual, Desprendibles y Pago
    ├── gui_vista_parametros.cpp# Parámetros institucionales y actualización
    └── tema.h                  # Paleta de colores Windows 11 Light (réplica de ui_gui/theme.py)
```

---

## 🛠️ Requisitos de Compilación

| Componente | Requisito Mínimo | Recomendado |
|---|---|---|
| **Compilador C++** | Compatible con C++17 | Visual Studio 2022 (MSVC v143), GCC 11+ o Clang 14+ |
| **Generador** | CMake 3.20 o superior | CMake 3.28+ |
| **Sistema Operativo** | Windows 10/11, Linux o macOS | Windows 11 64-bit |
| **Librerías Externas** | Ninguna manual | Se descargan automáticamente vía `FetchContent` (GLFW y Dear ImGui) |

### 📥 Instalación Rápida de Herramientas (Windows)

Si no tienes instaladas las herramientas de compilación en tu equipo:

1. **Instalar CMake:**
   - Vía consola (PowerShell): `winget install Kitware.CMake`
   - O descargando el instalador desde [cmake.org/download](https://cmake.org/download/) (asegúrate de marcar **"Add CMake to the system PATH"**).
   - Verifica en una nueva consola con: `cmake --version`.

2. **Instalar Compilador C++17 (MSVC):**
   - Abre el **Visual Studio Installer** y marca la carga de trabajo **"Desarrollo para el escritorio con C++"**.
   - O vía consola con Winget:
     ```powershell
     winget install Microsoft.VisualStudio.2022.BuildTools --override "--passive --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"
     ```

---

## 🚀 Instrucciones de Compilación y Ejecución

> ℹ️ **Nota:** Los ejecutables (`.exe`) no se incluyen en el repositorio Git por estándar de exclusión (`.gitignore`), por lo que deben compilarse localmente una vez.

### 1. Configurar el Entorno con CMake

Abre una consola (PowerShell o Command Prompt) en el directorio `cpp/`:

```powershell
cmake -B build -S .
```

> **Nota**: Durante este paso, CMake descargará automáticamente las bibliotecas **GLFW** y **Dear ImGui** sin requerir que el usuario configure rutas ni descargue librerías manualmente. Requiere conexión a internet activa en la primera ejecución.

### 2. Compilar el Proyecto

Ejecuta el comando de compilación en configuración **Release**:

```powershell
cmake --build build --config Release
```

La compilación generará dos ejecutables independientes en `build/Release/`:
1. `pita_gui.exe` (Interfaz Gráfica completa con Dear ImGui)
2. `pita_backend.exe` (Consola y verificación de integridad)

### 3. Ejecutar la Interfaz Gráfica

```powershell
.\build\Release\pita_gui.exe
```

*(Opcional: Si copias el binario a la raíz del repositorio con `copy .\build\Release\pita_gui.exe ..\`, podrás ejecutarlo directamente desde la raíz como `.\pita_gui.exe`).*

### 4. Ejecutar la Verificación en Consola (Backend CLI)

```powershell
.\build\Release\pita_backend.exe
```

El verificador de consola realiza una auditoría completa:
- Carga de todas las tablas de persistencia en `datos/`.
- Verificación de consistencia e integridad referencial.
- Simulación del cálculo de nómina y liquidación de docentes con desglose salarial.

### 5. Ejecutar la Suite de Pruebas Automatizadas (GoogleTest / CTest)

El proyecto cuenta con una suite completa de pruebas unitarias e integración que valida el 100% de la lógica de negocio migrada desde Python:

- **Método A (Ejecutable nativo GoogleTest):**
  ```powershell
  .\build\Release\pita_tests.exe
  ```

- **Método B (Mediante el runner CTest de CMake):**
  ```powershell
  ctest --test-dir build -C Release --output-on-failure
  ```


---

### ❓ Solución de Problemas Frecuentes

| Error / Mensaje | Causa | Solución |
|---|---|---|
| `'cmake' no se reconoce como un comando interno o externo` | CMake no está instalado o no se añadió al PATH. | Instala CMake y reinicia la terminal para actualizar las variables de entorno. |
| `No CMAKE_CXX_COMPILER could be found` | No se encontró el compilador de C++ (cl.exe / g++). | Instala Visual Studio 2022 con la carga "Desarrollo para el escritorio con C++". |
| Error clonando GLFW o ImGui | Fallo de conexión o Git no disponible. | Verifica tu conexión a internet durante el primer `cmake -B build -S .`. |

---

## 💡 Aspectos Clave de la Implementación Gráfica

- **Modularización Estricta**: Cada vista funcional y sus ventanas modales emergentes residen en su propio archivo de implementación (`gui_vista_*.cpp`), evitando archivos monolíticos y permitiendo mantenimiento desacoplado.
- **Grids Responsivos**: Las tarjetas de indicadores clave (KPIs de Nómina y Dashboard) utilizan tablas de proporción fija (`ImGuiTableFlags_SizingStretchSame`) para adaptarse armónicamente a cualquier resolución de pantalla.
- **Desprendibles de Pago**: El modal de nómina docente presenta un desglose exacto de devengados (sueldo básico, puntos salariales, bonificaciones), deducciones obligatorias de ley (salud y pensión) y total neto liquidado.
- **Control EBRA**: Marcado visual inmediato para estudiantes en alerta por bajo rendimiento académico con badges distintivos.
