# PITA — Plataforma Integrada de Transacciones Académicas y Nómina Docente
### Universidad Popular del Cesar (UPC) — Departamento de Ingeniería de Sistemas

[![Language: Python](https://img.shields.io/badge/Language-Python%203.10%2B-blue.svg)](https://www.python.org/)
[![Language: C++17](https://img.shields.io/badge/Language-C%2B%2B17-blue.svg)](https://isocpp.org/)
[![Framework: CustomTkinter](https://img.shields.io/badge/GUI%20Python-CustomTkinter-brightgreen.svg)](https://github.com/TomSchimansky/CustomTkinter)
[![Framework: Dear ImGui](https://img.shields.io/badge/GUI%20C%2B%2B-Dear%20ImGui%20%2B%20GLFW-orange.svg)](https://github.com/ocornut/imgui)
[![Normativa: Decreto 1279](https://img.shields.io/badge/Normativa-Decreto%201279%20%2F%20Acuerdo%20027-red.svg)](#)

---

## 📌 Descripción General del Proyecto

**PITA** es una solución integral diseñada para la gestión académica universitaria y la liquidación de nómina docente en estricto apego al marco regulatorio de las universidades públicas colombianas y la normativa interna de la **Universidad Popular del Cesar (UPC)**:

1. **Régimen Salarial y Prestacional Docente**:
   - **Decreto 1279 de 2002**: Asignación de puntos salariales según títulos, categorías docentes (Auxiliar, Asistente, Asociado, Titular), experiencia y producción académica.
   - **Acuerdo 027 de 2017 (CSU - UPC)**: Vinculación, dedicación (Tiempo Completo, Medio Tiempo, Hora Cátedra), liquidación de prestaciones sociales (Cesantías, Intereses sobre Cesantías, Prima de Servicios, Prima de Navidad, Vacaciones) y aportes patronales/parafiscales (Salud, Pensión, ARL, SENA, ICBF, Caja de Compensación).
2. **Subsistema de Alertas Tempranas EBRA**:
   - Detección proactiva de Estudiantes con Bajo Rendimiento Académico (promedio acumulado $< 3.0$ o estado EBRA) para tutorías y seguimiento institucional.
3. **Doble Implementación (Python & C++)**:
   - Ambas implementaciones comparten las mismas reglas de negocio, estructura de datos desacoplada y persistencia bidireccional sobre los archivos planos en `datos/`.

---

## 📂 Estructura General del Repositorio

```text
Taller/
├── datos/                         # Archivos planos de persistencia (.txt con formato delimitado)
│   ├── personas.txt               # Identificación y datos personales
│   ├── estudiantes.txt            # Matrículas, promedios y estado académico
│   ├── profesores.txt             # Escalafón, puntos salariales y categorías
│   ├── contratos.txt              # Fechas y tipos de vinculación
│   ├── facultades.txt / programas.txt
│   ├── cursos.txt / matriculas.txt / calificaciones.txt
│   ├── liquidaciones_nomina.txt   # Histórico de nómina procesada
│   └── parametros_normativos.txt  # Valor de punto, SMMLV, auxilio transporte
│
├── dominio/                       # Modelos de datos y entidades de negocio (Python)
├── gestores/                      # Gestores de lógica académica, contratos y personas (Python)
├── nomina/                        # Motor de cálculo salarial y prestacional (Python)
├── persistencia/                  # Gestor CRUD e integridad referencial (Python)
├── ui_gui/                        # Interfaz gráfica moderna en CustomTkinter (Python)
├── main.py / gui_main.py          # Puntos de entrada para la versión Python
├── requirements.txt               # Dependencias de Python
├── test_pita.py                   # Suite de pruebas automatizadas (pytest/unittest)
│
├── cpp/                           # Proyecto completo desacoplado en C++17
│   ├── CMakeLists.txt             # Configuración de compilación con CMake
│   ├── dominio/                   # Entidades y ListaEnlazada<T> (Estructura dinámica propia)
│   ├── gestores/                  # Gestores de negocio en C++
│   ├── nomina/                    # Calculadoras salariales, deducciones y prestaciones C++
│   ├── persistencia/              # Serialización y carga con validación referencial en C++
│   ├── gui/                       # GUI modularizada en Dear ImGui + GLFW + OpenGL3
│   └── main.cpp                   # Backend CLI para verificación en consola
│
├── .gitignore                     # Configuración de exclusiones de Git
└── README.md                      # Este documento
```

---

## 🚀 Guía de Inicio Rápido

El proyecto cuenta con **dos versiones funcionales independientes** que comparten la misma base de datos plana en `datos/`:
- **Opción A (Python)**: Lista para usar de inmediato, sin necesidad de compilar.
- **Opción B (C++)**: Alto rendimiento gráfico con Dear ImGui; requiere compilar una vez con CMake.

---

### Opción A: Ejecutar la Versión en Python (Inmediata)

Esta es la forma más rápida de probar el sistema sin instalar compiladores.

#### 1. Requisitos Previos:
- **Python 3.10** o superior instalado ([python.org](https://www.python.org/downloads/)).
  > ⚠️ *Al instalar Python en Windows, asegúrate de marcar la casilla **"Add python.exe to PATH"**.*
- Administrador de paquetes `pip` (incluido por defecto con Python).

#### 2. Instalar Dependencias:
Abre una terminal (PowerShell o CMD) en la raíz del proyecto y ejecuta:
```bash
pip install -r requirements.txt
```

#### 3. Iniciar la Interfaz Gráfica (CustomTkinter):
```bash
python gui_main.py
```

*(Opcionalmente, para ejecutar el backend de consola interactivo: `python main.py`)*

#### 4. Ejecutar las Pruebas Automatizadas:
```bash
pytest -v test_pita.py
```

---

### Opción B: Compilar y Ejecutar la Versión en C++17

> ℹ️ **Nota importante sobre los archivos ejecutables (`.exe`):**  
> Por buenas prácticas de desarrollo en Git, los binarios `.exe` compilados no se suben al repositorio (están en `.gitignore`). Por esta razón, si clonaste o descargaste el proyecto por primera vez, **debes compilar el binario** siguiendo los pasos a continuación. ¡Solo toma un par de minutos!

Para detalles específicos sobre la arquitectura interna, consulta el [README de C++](cpp/README.md).

---

#### Paso 1: Instalar Herramientas de Compilación (Solo una vez)

Para compilar C++ en Windows necesitas dos herramientas: **CMake** y un **Compilador C++17**.

##### 1.1 Instalar CMake (versión 3.20 o superior):
- **Método A (Recomendado vía consola con Winget):**
  Abre PowerShell como administrador o usuario normal y ejecuta:
  ```powershell
  winget install Kitware.CMake
  ```
- **Método B (Instalador Oficial con GUI):**
  1. Descarga el instalador de Windows x64 (`.msi`) desde: [cmake.org/download](https://cmake.org/download/).
  2. Ejecuta el instalador.
  3. ⚠️ **Muy importante:** En el asistente de instalación, selecciona la opción:  
     **"Add CMake to the system PATH for all users"** (o *"for the current user"*).
  4. Finaliza la instalación.

> 🔍 **Verificación:** Cierra y vuelve a abrir tu terminal, luego ejecuta:
> ```powershell
> cmake --version
> ```
> Deberías ver un mensaje como `cmake version 3.xx.x`. Si aparece este mensaje, ¡CMake está listo!

##### 1.2 Instalar Compilador C++17:
- **En Windows (Recomendado):**
  - Si tienes instalado **Visual Studio 2022** (Community o Professional), abre el *Visual Studio Installer*, haz clic en *Modificar* y asegúrate de tener marcada la carga de trabajo:  
    👉 **"Desarrollo para el escritorio con C++"** (*Desktop development with C++*).
  - Si no tienes Visual Studio, puedes instalar las herramientas de compilación con Winget:
    ```powershell
    winget install Microsoft.VisualStudio.2022.BuildTools --override "--passive --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"
    ```
- **Alternativa con MinGW (GCC 11+):**
  Si utilizas MinGW-w64 o MSYS2, asegúrate de que `g++` esté disponible en tu `PATH`.

---

#### Paso 2: Compilar el Proyecto con CMake

Una vez instaladas las herramientas, compilar es muy sencillo. CMake descargará automáticamente las bibliotecas gráficas (**GLFW** y **Dear ImGui**) a través de internet:

```powershell
# 1. Ingresar a la carpeta de C++
cd cpp

# 2. Configurar el proyecto (descarga GLFW e ImGui vía FetchContent)
cmake -B build -S .

# 3. Compilar los ejecutables en modo optimizado (Release)
cmake --build build --config Release
```

---

#### Paso 3: Ejecutar los Programas Compilados

Una vez finalizada la compilación exitosamente, los ejecutables estarán listos en la subcarpeta `build/Release/`:

##### Iniciar la Interfaz Gráfica (Dear ImGui + GLFW):
```powershell
# Estando dentro de la carpeta 'cpp':
.\build\Release\pita_gui.exe
```

##### Iniciar la Consola de Verificación del Backend:
```powershell
# Estando dentro de la carpeta 'cpp':
.\build\Release\pita_backend.exe
```

*(Opcional: Si deseas tener el ejecutable `pita_gui.exe` en la raíz del proyecto para ejecutarlo como `.\pita_gui.exe`, puedes copiarlo ejecutando: `copy .\build\Release\pita_gui.exe ..\`)*.

---

### ❓ Solución de Problemas Frecuentes (Troubleshooting C++)

| Error / Síntoma | Causa | Solución |
|---|---|---|
| `cmake : El término 'cmake' no se reconoce...` | CMake no está instalado o no se agregó al `PATH`. | Instala CMake y asegúrate de reiniciar la terminal para que refresque las variables de entorno. |
| `No CMAKE_CXX_COMPILER could be found` | No hay un compilador C++ detectado por CMake. | Abre el instalador de Visual Studio 2022 y marca la opción **"Desarrollo para el escritorio con C++"**. |
| `Failed to clone repository: 'glfw'` | No hay conexión a internet durante la primera configuración. | Asegúrate de tener conexión a internet activa la primera vez que ejecutas `cmake -B build -S .` para descargar GLFW e ImGui. |
| La ventana se abre pero no encuentra datos | El ejecutable se inició fuera del contexto de carpetas. | Ejecuta siempre desde `cpp` (`.\build\Release\pita_gui.exe`) o copia el ejecutable a la raíz del repositorio. |

---

## ⚙️ Módulos Principales del Sistema

| Módulo | Descripción Funcional |
|---|---|
| **Dashboard General** | Métricas en tiempo real: estudiantes matriculados, cuerpo docente, contratos activos y tabla de alertas tempranas **EBRA**. |
| **Directorio de Personas** | Gestión de personas naturales con roles simultáneos o específicos (Estudiante, Profesor, Administrativo). |
| **Estructura Académica** | Facultades, programas académicos de pregrado/posgrado, planes de estudio y oferta curricular. |
| **Gestión Académica** | Cursos ofertados, matrícula académica de estudiantes y registro de calificaciones con control de estados. |
| **Contratación Docente** | Modalidades de vinculación (Tiempo Completo, Medio Tiempo, Cátedra), fechas de vigencia y terminación de contratos. |
| **Nómina y Prestaciones** | Liquidación por docente o masiva por periodo, cálculo de devengados (puntos salariales y factores), deducciones de ley (salud, pensión), aportes patronales y generación de desprendibles de pago. |
| **Parámetros Normativos** | Configuración de variables institucionales: valor del punto salarial Decreto 1279, Salario Mínimo Legal Vigente y Auxilio de Transporte. |

---

## 🏛️ Normativa Aplicada
- **Decreto 1279 de 2002**: Régimen salarial y prestacional de los docentes de las universidades estatales colombianas.
- **Acuerdo 027 de 2017 CSU - UPC**: Estatuto Docente y reglamentación interna de vinculación y nómina en la Universidad Popular del Cesar.
- **Ley 100 de 1993 y Estatuto Tributario**: Bases de cotización a seguridad social, porcentajes de salud (4% empleado, 8.5% empleador) y pensión (4% empleado, 12% empleador).
