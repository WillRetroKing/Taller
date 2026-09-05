"""Punto de Entrada Principal de la Interfaz Gráfica (GUI) para PITA."""

from __future__ import annotations

import sys
from pathlib import Path

from ui_gui.gui_app import PITAApplication


def main() -> None:
    """Arranca la GUI del sistema PITA."""
    directorio_datos = "datos"
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        directorio_datos = sys.argv[1]

    app = PITAApplication(directorio_datos=directorio_datos)
    app.mainloop()


if __name__ == "__main__":
    main()
