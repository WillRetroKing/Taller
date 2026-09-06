#include "gui_app.h"
#include <string>
#include <iostream>

#ifdef _WIN32
#include <windows.h>
#endif

int main(int argc, char* argv[]) {
    // Buscar la carpeta datos en ./datos, ../datos, ../../datos
    std::string dirDatos = "datos";
    if (argc > 1) {
        dirDatos = argv[1];
    }

    std::cout << "[PITA GUI] Iniciando aplicacion PITA v2.0...\n";
    std::cout << "[PITA GUI] Directorio de datos: " << dirDatos << "\n";

    pita::PITAApp app(dirDatos);
    int resultado = app.ejecutar();

    std::cout << "[PITA GUI] Aplicacion finalizada con codigo: " << resultado << "\n";
    return resultado;
}
