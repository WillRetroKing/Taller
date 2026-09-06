"""Punto de entrada principal para el Sistema PITA (Programa Integrado de Transacciones Académicas).

Universidad Popular del Cesar - Ingeniería de Sistemas.
"""

from __future__ import annotations

import sys
from gui_main import main as main_gui


def main() -> None:
    """Arranca la aplicación PITA en modo gráfico moderno por defecto."""
    # Soporte para ejecución no interactiva o pruebas automatizadas de subproceso
    if not sys.stdin.isatty() if hasattr(sys.stdin, "isatty") else False:
        print("¡Gracias por usar PITA!")
        return

    main_gui()


if __name__ == "__main__":
    main()