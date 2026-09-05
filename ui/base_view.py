"""Vista base del sistema PITA.

Define el contrato común de todas las vistas de consola:
- ``display()`` ejecuta el ciclo del menú de la vista y devuelve
  ``True`` para volver al menú principal o ``False`` para salir
  de la aplicación.
- Helpers de entrada (texto, entero, decimal, fecha, booleano)
  y de salida (mensajes, tablas) construidos sobre ``rich``.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Callable

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table


class BaseView:
    """Clase base para las vistas de consola del sistema PITA."""

    titulo: str = "Vista"
    color: str = "cyan"

    def __init__(self) -> None:
        self.console = Console()

    # ------------------------------------------------------------------
    # Ciclo de vida
    # ------------------------------------------------------------------
    def opciones(self) -> list[tuple[str, str, Callable[[], None]]]:
        """Devuelve la lista de (tecla, descripción, manejador) del menú.

        Las subclases deben sobreescribir este método. La tecla "0" se
        reserva para "Volver al menú principal" y la tecla "9" para
        "Salir de la aplicación"; se agregan automáticamente.
        """
        raise NotImplementedError

    def display(self) -> bool:
        """Ejecutar el menú de la vista.

        Retorna ``True`` para volver al menú principal o ``False``
        para terminar la aplicación.
        """
        while True:
            self._mostrar_menu()
            eleccion = Prompt.ask("\nOpción", default="0").strip()

            if eleccion == "0":
                return True
            if eleccion == "9":
                return False

            manejador = next(
                (handler for tecla, _desc, handler in self.opciones() if tecla == eleccion),
                None,
            )
            if manejador is None:
                self.mostrar_error("Opción no válida, intente nuevamente.")
                self.pausar()
                continue

            try:
                manejador()
            except (EOFError, KeyboardInterrupt):
                self.mostrar_info("Operación cancelada por el usuario.")
            except Exception as e:  # errores de negocio (ErrorX) y validaciones
                self.mostrar_error(str(e))
            self.pausar()

    # ------------------------------------------------------------------
    # Presentación
    # ------------------------------------------------------------------
    def _mostrar_menu(self) -> None:
        self.console.clear()
        lineas = [f"[bold {self.color}]{self.titulo}[/bold {self.color}]", "-" * 40]
        for tecla, descripcion, _handler in self.opciones():
            lineas.append(f"{tecla}. {descripcion}")
        lineas.append("-" * 40)
        lineas.append("0. Volver al menú principal")
        lineas.append("9. Salir de la aplicación")
        self.console.print(Panel("\n".join(lineas), border_style=self.color))

    def mostrar_error(self, mensaje: str) -> None:
        self.console.print(f"[red]ERROR:[/red] {mensaje}")

    def mostrar_exito(self, mensaje: str) -> None:
        self.console.print(f"[green]{mensaje}[/green]")

    def mostrar_info(self, mensaje: str) -> None:
        self.console.print(f"[blue]{mensaje}[/blue]")

    def mostrar_alerta(self, mensaje: str) -> None:
        self.console.print(f"[yellow]{mensaje}[/yellow]")

    def pausar(self) -> None:
        try:
            self.console.input("\nPresione Enter para continuar...")
        except EOFError:
            pass

    def mostrar_tabla(self, titulo: str, columnas: list[str], filas: list[list[Any]]) -> None:
        """Mostrar una tabla rich con las filas dadas."""
        tabla = Table(title=titulo, header_style=f"bold {self.color}")
        for columna in columnas:
            tabla.add_column(columna)
        for fila in filas:
            tabla.add_row(*("" if celda is None else str(celda) for celda in fila))
        self.console.print(tabla)
        if not filas:
            self.mostrar_info("No hay registros para mostrar.")

    # ------------------------------------------------------------------
    # Entrada de datos
    # ------------------------------------------------------------------
    def pedir_texto(self, etiqueta: str, *, obligatorio: bool = True, defecto: str | None = None) -> str | None:
        while True:
            valor = Prompt.ask(etiqueta, default=defecto) if defecto is not None else Prompt.ask(etiqueta)
            valor = (valor or "").strip()
            if valor:
                return valor
            if not obligatorio:
                return None
            self.mostrar_error("Este campo es obligatorio.")

    def pedir_entero(self, etiqueta: str, *, obligatorio: bool = True) -> int | None:
        while True:
            valor = Prompt.ask(etiqueta).strip()
            if not valor and not obligatorio:
                return None
            try:
                return int(valor)
            except ValueError:
                self.mostrar_error("Ingrese un número entero válido.")

    def pedir_decimal(self, etiqueta: str, *, obligatorio: bool = True) -> Decimal | None:
        while True:
            valor = Prompt.ask(etiqueta).strip()
            if not valor and not obligatorio:
                return None
            try:
                return Decimal(valor)
            except InvalidOperation:
                self.mostrar_error("Ingrese un número válido (use punto decimal).")

    def pedir_fecha(self, etiqueta: str, *, obligatorio: bool = True) -> date | None:
        while True:
            valor = Prompt.ask(f"{etiqueta} (AAAA-MM-DD)").strip()
            if not valor and not obligatorio:
                return None
            try:
                return datetime.strptime(valor, "%Y-%m-%d").date()
            except ValueError:
                self.mostrar_error("Fecha inválida. Use el formato AAAA-MM-DD.")

    def pedir_bool(self, etiqueta: str, *, defecto: bool = False) -> bool:
        valor = Prompt.ask(
            f"{etiqueta} (s/n)", choices=["s", "n"], default="s" if defecto else "n"
        )
        return valor == "s"

    def pedir_opcion(self, etiqueta: str, opciones: list[str]) -> str:
        """Pedir un valor entre una lista de opciones válidas."""
        self.console.print(f"Opciones: {', '.join(opciones)}")
        while True:
            valor = Prompt.ask(etiqueta).strip()
            if valor in opciones:
                return valor
            self.mostrar_error(f"Debe ser una de: {', '.join(opciones)}")

    def seleccionar_de_resultados(self, titulo: str, resultados: list, campos_display: list[str], campo_id: str = None) -> any:
        """Mostrar resultados y dejar que el usuario seleccione uno.

        Args:
            titulo: Título para la tabla de resultados
            resultados: Lista de objetos o tuplas con los datos
            campos_display: Lista de nombres de campos para mostrar
            campo_id: Nombre del campo que contiene el ID (si es None, se usa el primer campo numérico)

        Returns:
            El objeto/registro seleccionado por el usuario, o None si cancela
        """
        if not resultados:
            self.mostrar_info("No hay resultados para mostrar.")
            return None

        # Si hay pocos resultados (1-2), mostrar y seleccionar automáticamente
        if len(resultados) <= 2:
            self.mostrar_tabla(titulo, campos_display, [
                [str(getattr(r, campo, r[i]) if hasattr(r, campo) else r[i]) for i, campo in enumerate(campos_display)]
                for r in resultados
            ])
            input(f"\nPresione Enter para continuar...")
            return resultados[0] if resultados else None

        # Mostrar tabla con números de selección
        self.console.clear()
        lineas = [f"[bold {self.color}]{titulo}[/bold {self.color}]", "-" * 60]
        for i, r in enumerate(resultados, 1):
            valores = [str(getattr(r, campo, r[i-1]) if hasattr(r, campo) else r[i-1]) for i, campo in enumerate(campos_display)]
            lineas.append(f"{i}. {', '.join(valores)}")
        lineas.append("0. Cancelar")
        lineas.append("-" * 60)
        self.console.print(Panel("\n".join(lineas), border_style=self.color))

        while True:
            try:
                eleccion = Prompt.ask(f"\nSeleccione una opción (1-{len(resultados)}) o 0 para cancelar", default="0").strip()
                if eleccion == "0":
                    return None
                idx = int(eleccion)
                if 1 <= idx <= len(resultados):
                    return resultados[idx - 1]
                self.mostrar_error(f"Por favor seleccione un número entre 1 y {len(resultados)}")
            except (ValueError, EOFError, KeyboardInterrupt):
                return None
