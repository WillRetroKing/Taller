cmake_minimum_required(VERSION 3.15)
project(PITA VERSION 2.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Warning flags
if (MSVC)
    add_compile_options(/W3 /EHsc /utf-8)
else()
    add_compile_options(-Wall -Wextra -pedantic)
endif()

# Includes comunes
set(PITA_INCLUDE_DIRS
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/dominio
    ${CMAKE_CURRENT_SOURCE_DIR}/persistencia
    ${CMAKE_CURRENT_SOURCE_DIR}/gestores
    ${CMAKE_CURRENT_SOURCE_DIR}/nomina
)

# Fuentes comunes del backend
set(PITA_BACKEND_SOURCES
    persistencia/gestor_persistencia.cpp
    gestores/gestor_personas.cpp
    gestores/gestor_academico.cpp
    gestores/gestor_contratos.cpp
    gestores/gestor_parametros.cpp
    gestores/gestor_periodos.cpp
    gestores/gestor_factores.cpp
    gestores/gestores_academicos.cpp
    nomina/calculadora_deducciones.cpp
    nomina/calculadora_prestaciones.cpp
    nomina/gestor_nomina.cpp
    nomina/desglose_anual.cpp
)

# Librería estática pita_lib
add_library(pita_lib STATIC ${PITA_BACKEND_SOURCES})
target_include_directories(pita_lib PUBLIC ${PITA_INCLUDE_DIRS})

# Ejecutable CLI (Consola)
add_executable(pita_backend main.cpp)
target_link_libraries(pita_backend PRIVATE pita_lib)

# ======================================================================
# Dependencias GUI via FetchContent (Dear ImGui + GLFW)
# ======================================================================
include(FetchContent)

# 1. GLFW
message(STATUS "Configurando GLFW via FetchContent...")
FetchContent_Declare(
    glfw
    GIT_REPOSITORY https://github.com/glfw/glfw.git
    GIT_TAG 3.4
)
set(GLFW_BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
set(GLFW_BUILD_TESTS OFF CACHE BOOL "" FORCE)
set(GLFW_BUILD_DOCS OFF CACHE BOOL "" FORCE)
set(GLFW_INSTALL OFF CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(glfw)

# 2. Dear ImGui
message(STATUS "Configurando Dear ImGui via FetchContent...")
FetchContent_Declare(
    imgui
    GIT_REPOSITORY https://github.com/ocornut/imgui.git
    GIT_TAG v1.91.5
)
FetchContent_MakeAvailable(imgui)

# Crear librería para Dear ImGui con backends GLFW y OpenGL3
set(IMGUI_SOURCES
    ${imgui_SOURCE_DIR}/imgui.cpp
    ${imgui_SOURCE_DIR}/imgui_demo.cpp
    ${imgui_SOURCE_DIR}/imgui_draw.cpp
    ${imgui_SOURCE_DIR}/imgui_tables.cpp
    ${imgui_SOURCE_DIR}/imgui_widgets.cpp
    ${imgui_SOURCE_DIR}/backends/imgui_impl_glfw.cpp
    ${imgui_SOURCE_DIR}/backends/imgui_impl_opengl3.cpp
)

add_library(imgui_lib STATIC ${IMGUI_SOURCES})
target_include_directories(imgui_lib PUBLIC
    ${imgui_SOURCE_DIR}
    ${imgui_SOURCE_DIR}/backends
)
target_link_libraries(imgui_lib PUBLIC glfw opengl32)

# 3. Ejecutable GUI PITA
set(PITA_GUI_SOURCES
    gui/gui_main.cpp
    gui/gui_app.cpp
    gui/gui_vista_personas.cpp
    gui/gui_vista_facultades.cpp
    gui/gui_vista_academica.cpp
    gui/gui_vista_contratos.cpp
    gui/gui_vista_nomina.cpp
    gui/gui_vista_parametros.cpp
    gui/gui_controller.cpp
)

add_executable(pita_gui ${PITA_GUI_SOURCES})
target_include_directories(pita_gui PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/gui
    ${PITA_INCLUDE_DIRS}
    ${imgui_SOURCE_DIR}
    ${imgui_SOURCE_DIR}/backends
)
target_link_libraries(pita_gui PRIVATE
    pita_lib
    imgui_lib
    glfw
    opengl32
)
