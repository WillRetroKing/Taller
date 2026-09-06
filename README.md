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
├── pita_gui.exe                   # Binario ejecutable compilado de la GUI C++ para Windows
├── .gitignore                     # Configuración de exclusiones de Git
└── README.md                      # Este documento
```

---

## 🚀 Guía de Inicio Rápido

### Opción A: Ejecución del Proyecto en Python

#### Requisitos Previos:
- Python 3.10 o superior instalado.
- Administrador de paquetes `pip`.

#### 1. Instalar Dependencias:
Abre una terminal en la raíz del proyecto y ejecuta:
```bash
pip install -r requirements.txt
```

#### 2. Iniciar la Interfaz Gráfica (CustomTkinter):
```bash
python gui_main.py
```
*(Opcionalmente: `python main.py`)*

#### 3. Ejecutar las Pruebas Automatizadas:
```bash
pytest -v test_pita.py
```

---

### Opción B: Ejecución y Compilación del Proyecto en C++

Para más detalles específicos sobre la arquitectura interna en C++, consulta el [README de C++](file:///c:/Users/Chick/Desktop/Taller/cpp/README.md).

#### Requisitos Previos:
- Compilador con soporte para **C++17** (Visual Studio 2022 / MSVC v143+, GCC 11+ o Clang 13+).
- **CMake** versión 3.20 o superior.

#### 1. Ejecutar el Binario ya Compilado (Windows):
Puedes ejecutar directamente el binario generado en la raíz:
```powershell
.\pita_gui.exe
```

#### 2. Compilar desde el Código Fuente con CMake:
```powershell
# 1. Ingresar a la carpeta de C++
cd cpp

# 2. Configurar el proyecto (descargará GLFW e ImGui vía FetchContent)
cmake -B build -S .

# 3. Compilar en modo Release
cmake --build build --config Release
```

Los ejecutables generados se ubicarán en `cpp/build/Release/`:
- **`pita_gui.exe`**: Interfaz gráfica interactiva completa.
- **`pita_backend.exe`**: Verificador de consola para persistencia e integridad de datos.

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
