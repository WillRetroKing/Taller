"""Genera versiones limpias de los .md para exportar (sin marcadores editoriales).

Lee DOCUMENTACION_MAESTRA_PITA.md y DICCIONARIO_DE_DATOS.md y escribe copias
depuradas en docs/export/. Los originales conservan los marcadores de trabajo.

Limpieza aplicada:
  - Elimina la sección "Convenciones editoriales" (leyenda de marcadores).
  - `[IMPLEMENTADO]` en títulos y texto: se elimina la etiqueta.
  - `[IMPLEMENTADO]` como celda de tabla: se reemplaza por "Implementado".
  - Marcadores de pendiente en prosa: se convierten en nota en cursiva.
  - `[PENDIENTE]` (integrantes, enlaces): se reemplaza por "Por definir".
  - ~~tachado~~: se elimina el texto tachado (queda la decisión vigente).
  - "✅ Superada" → "Superada"; ✅ sueltos se eliminan.

Uso:  python docs/limpiar_md.py
"""

from __future__ import annotations

import re
from pathlib import Path

DOCS = Path(__file__).resolve().parent
SALIDA = DOCS / "export"

# Marcadores que desaparecen por completo (estado ya verificado).
RESUELTOS = ["[IMPLEMENTADO]", "[DISEÑO]", "[DECISIÓN DEL EQUIPO]"]

# Marcadores de pendiente -> nota en cursiva legible en el documento final.
PENDIENTES = {
    "[IMPLEMENTACIÓN PARCIAL]": "*Implementación parcial:*",
    "[PENDIENTE DE IMPLEMENTACIÓN]": "*Pendiente de implementación:*",
    "[PENDIENTE DE VERIFICACIÓN]": "*Pendiente de verificación:*",
    "[VERIFICACIÓN PENDIENTE]": "*Pendiente de verificación:*",
    "[EVIDENCIA PENDIENTE]": "*(evidencia pendiente)*",
    "[CAPTURA O SALIDA PENDIENTE]": "*(captura o salida pendiente)*",
    "[PENDIENTE DE PRUEBA]": "*Pendiente de prueba:*",
    "[NORMA POR VERIFICAR]": "*Norma por verificar:*",
}


def limpiar(texto: str) -> str:
    lineas = texto.splitlines()
    limpias: list[str] = []
    saltar = False
    for linea in lineas:
        # Eliminar la sección de convenciones editoriales completa.
        if linea.strip().startswith("### Convenciones editoriales"):
            saltar = True
            continue
        if saltar:
            if linea.startswith("## ") or linea.startswith("---"):
                saltar = False
            else:
                continue

        l = linea

        # Tachados: quitar el texto tachado junto con los ~~.
        l = re.sub(r"~~[^~]+~~\s*", "", l)

        # Marcadores resueltos: quitar la etiqueta (con o sin backticks).
        for tag in RESUELTOS:
            l = l.replace(f"`{tag}`", "").replace(tag, "")

        # Marcadores de pendiente: convertir en nota en cursiva.
        for tag, nota in PENDIENTES.items():
            l = l.replace(f"`{tag}`", nota).replace(tag, nota)

        # [PENDIENTE] aislado (integrantes, enlaces, capturas).
        l = l.replace("`[PENDIENTE]`", "Por definir").replace("[PENDIENTE]", "Por definir")

        # Emojis de estado en tablas de pruebas.
        if "✅" in l:
            l = l.replace("✅ Superada", "Superada").replace("✅", "")
            l = l.rstrip().rstrip("|").rstrip() + (" |" if l.lstrip().startswith("|") else "")

        # En celdas de tabla que quedaron vacías por la limpieza, poner "Implementado".
        if l.startswith("|") and re.search(r"\|\s*\|", l):
            l = re.sub(r"\|\s*\|", "| Implementado |", l)

        # Colapsar espacios dobles dejados por las etiquetas eliminadas
        # (sin tocar código ni el inicio de las viñetas).
        if not l.startswith((" ", "\t", "-", "|")):
            l = re.sub(r" {2,}", " ", l)
            if l.startswith(">"):
                l = "> " + l[1:].lstrip()

        limpias.append(l.rstrip())

    return "\n".join(limpias) + "\n"


def main() -> None:
    SALIDA.mkdir(exist_ok=True)
    for nombre in ("DOCUMENTACION_MAESTRA_PITA.md", "DICCIONARIO_DE_DATOS.md"):
        origen = DOCS / nombre
        destino = SALIDA / nombre
        destino.write_text(limpiar(origen.read_text(encoding="utf-8")), encoding="utf-8", newline="\n")
        print(f"Limpiado: {destino}")


if __name__ == "__main__":
    main()
