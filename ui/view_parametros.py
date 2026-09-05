"""Vista de configuración: gestión de parámetros normativos."""

from __future__ import annotations

from modelo_datos import ParametroNormativo, ParametroNormativoCodigo
from ui.base_view import BaseView


class ParametrosView(BaseView):
    titulo = "CONFIGURACIÓN Y PARÁMETROS"
    color = "blue"

    def __init__(self, gestor_parametros, gestor_personas, gestor_academico) -> None:
        super().__init__()
        self._gestor_parametros = gestor_parametros
        self._gestor_personas = gestor_personas
        self._gestor_academico = gestor_academico

    def opciones(self):
        return [
            ("1", "Crear parámetro normativo", self.crear_parametro),
            ("2", "Buscar parámetro vigente", self.buscar_vigente),
            ("3", "Listar parámetros por tipo", self.listar_por_tipo),
            ("4", "Listar todos los parámetros", self.listar_todos),
            ("5", "Modificar valor de parámetro", self.modificar_parametro),
            ("6", "Desactivar parámetro", self.desactivar_parametro),
        ]

    # ------------------------------------------------------------------
    # Búsqueda y selección de parámetros
    # ------------------------------------------------------------------
    def _seleccionar_parametro(self) -> Any | None:
        """Mostrar parámetros disponibles y dejar que el usuario seleccione uno.

        Returns: El parámetro seleccionado o None si cancela.
        """
        param = self._gestor_parametros.parametros if hasattr(self._gestor_parametros, 'parametros') else []

        if not param:
            self.mostrar_alerta("No hay parámetros normativos registrados.")
            return None

        # Mostrar parámetros con código y nombre para identificación
        self.console.clear()
        lineas = [f"[bold {self.color}]Seleccionar parámetro[/bold {self.color}]", "-" * 60]
        for i, p in enumerate(param, 1):
            codigo = getattr(p.codigo, "value", p.codigo) if hasattr(p, 'codigo') else "N/A"
            lineas.append(f"{i}. Código: {codigo}, Nombre: {p.nombre or 'N/A'}")
        lineas.append("0. Cancelar")
        lineas.append("-" * 60)
        self.console.print(Panel("\n".join(lineas), border_style=self.color))

        while True:
            try:
                eleccion = Prompt.ask(f"\nSeleccione un parámetro (1-{len(param)}) o 0 para cancelar", default="0").strip()
                if eleccion == "0":
                    return None
                idx = int(eleccion)
                if 1 <= idx <= len(param):
                    return param[idx - 1]
                self.mostrar_error(f"Por favor seleccione un número entre 1 y {len(param)}")
            except (ValueError, EOFError, KeyboardInterrupt):
                return None

    # ------------------------------------------------------------------
    def crear_parametro(self) -> None:
        codigo = ParametroNormativoCodigo(
            self.pedir_opcion("Código", [c.value for c in ParametroNormativoCodigo])
        )
        nombre = self.pedir_texto("Nombre")
        descripcion = self.pedir_texto("Descripción", obligatorio=False)
        tipo_dato = self.pedir_opcion(
            "Tipo de dato", ["MONETARIO", "PORCENTUAL", "ENTERO", "TEXTO"]
        )
        valor = self.pedir_texto("Valor")
        unidad = self.pedir_texto("Unidad", obligatorio=False)
        norma_origen = self.pedir_texto("Norma de origen", obligatorio=False)
        articulo = self.pedir_texto("Artículo", obligatorio=False)
        fecha_inicio_vigencia = self.pedir_fecha("Inicio de vigencia")
        fecha_fin_vigencia = self.pedir_fecha("Fin de vigencia", obligatorio=False)
        aplica_a = self.pedir_opcion(
            "Aplica a", ["TODOS", "PLANTA", "OCASIONAL", "CATEDRATICO", "EMPLEADOR", "ESTUDIANTES"]
        )

        parametro = ParametroNormativo(
            codigo=codigo,
            nombre=nombre,
            descripcion=descripcion,
            tipoDato=tipo_dato,
            valor=valor,
            unidad=unidad,
            normaOrigen=norma_origen,
            articulo=articulo,
            fechaInicioVigencia=fecha_inicio_vigencia,
            fechaFinVigencia=fecha_fin_vigencia,
            aplicaA=aplica_a,
        )
        creado = self._gestor_parametros.crear_parametro(parametro)
        self.mostrar_exito(f"Parámetro creado con ID {creado.idParametro}.")

    def buscar_vigente(self) -> None:
        codigo = self.pedir_opcion(
            "Código", [c.value for c in ParametroNormativoCodigo]
        )
        parametro = self._gestor_parametros.buscar_parametro_vigente(codigo)
        if parametro is None:
            self.mostrar_alerta("No hay parámetro vigente con ese código.")
            return
        self._mostrar_parametros([parametro])

    def listar_por_tipo(self) -> None:
        tipo = self.pedir_opcion(
            "Tipo de dato", ["MONETARIO", "PORCENTUAL", "ENTERO", "TEXTO"]
        )
        parametros = self._gestor_parametros.listar_parametros_por_tipo(tipo)
        if not parametros:
            self.mostrar_alerta(f"No hay parámetros de tipo {tipo}.")
            self.pausar()
            return
        self._mostrar_parametros(parametros)

    def listar_todos(self) -> None:
        parametros = list(self._gestor_parametros.parametros)
        if not parametros:
            self.mostrar_alerta("No hay parámetros normativos registrados.")
            self.pausar()
            return
        # Usar selección en lugar de listar todos directamente
        self._mostrar_parametros(parametros)

    def modificar_parametro(self) -> None:
        # Seleccionar parámetro en lugar de pedir ID
        parametro = self._seleccionar_parametro()
        if parametro is None:
            return

        valor = self.pedir_texto("Nuevo valor")
        self._gestor_parametros.modificar_parametro(parametro.idParametro, valor=valor)
        self.mostrar_exito("Parámetro modificado.")

    def desactivar_parametro(self) -> None:
        # Seleccionar parámetro en lugar de pedir ID
        parametro = self._seleccionar_parametro()
        if parametro is None:
            return

        if self.pedir_bool(f"¿Confirma desactivar el parámetro {parametro.idParametro}?"):
            self._gestor_parametros.desactivar_parametro(parametro.idParametro)
            self.mostrar_exito("Parámetro desactivado.")

    def _mostrar_parametros(self, parametros) -> None:
        self.mostrar_tabla(
            "Parámetros normativos",
            ["ID", "Código", "Nombre", "Tipo", "Valor", "Unidad", "Vigencia", "Estado"],
            [[p.idParametro, getattr(p.codigo, "value", p.codigo), p.nombre,
              p.tipoDato, p.valor, p.unidad,
              f"{p.fechaInicioVigencia} a {p.fechaFinVigencia or 'indefinido'}",
              p.estado] for p in parametros],
        )