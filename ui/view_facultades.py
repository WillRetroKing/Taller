"""Vista para gestionar facultades usando GestorCRUD."""

from __future__ import annotations

from ui.base_view import BaseView


class FacultadesView(BaseView):
    titulo = "GESTIONAR FACULTADES"
    color = "cyan"

    def __init__(self, gestor_crud) -> None:
        super().__init__()
        self._gestor_crud = gestor_crud

    def opciones(self):
        return [
            ("1", "Crear facultad", self.crear_facultad),
            ("2", "Buscar facultad", self.buscar_facultad),
            ("3", "Listar facultades", self.listar),
            ("4", "Modificar facultad", self.modificar),
            ("5", "Desactivar facultad", self.desactivar),
        ]

    # ------------------------------------------------------------------
    # Búsqueda de facultades por criterios naturales
    # ------------------------------------------------------------------
    def _seleccionar_facultad(self) -> Any | None:
        """Mostrar facultades disponibles y dejar que el usuario seleccione una.

        Returns: La facultad seleccionada o None si cancela.
        """
        facs = self._gestor_crud.listar() if hasattr(self._gestor_crud, 'listar') else []

        if not facs:
            self.mostrar_alerta("No hay facultades registradas.")
            return None

        # Mostrar facultades con código y nombre para identificación
        self.console.clear()
        lineas = [f"[bold {self.color}]Seleccionar facultad[/bold {self.color}]", "-" * 60]
        for i, f in enumerate(facs, 1):
            lineas.append(f"{i}. Código: {f.codigoFacultad or 'N/A'}, Nombre: {f.nombre or 'N/A'}")
        lineas.append("0. Cancelar")
        lineas.append("-" * 60)
        self.console.print(Panel("\n".join(lineas), border_style=self.color))

        while True:
            try:
                eleccion = Prompt.ask(f"\nSeleccione una facultad (1-{len(facs)}) o 0 para cancelar", default="0").strip()
                if eleccion == "0":
                    return None
                idx = int(eleccion)
                if 1 <= idx <= len(facs):
                    return facs[idx - 1]
                self.mostrar_error(f"Por favor seleccione un número entre 1 y {len(facs)}")
            except (ValueError, EOFError, KeyboardInterrupt):
                return None

    # ------------------------------------------------------------------
    def crear_facultad(self) -> None:
        codigo = self.pedir_texto("Código de facultad")
        nombre = self.pedir_texto("Nombre de la facultad")
        descripcion = self.pedir_texto("Descripción", obligatorio=False)
        ubicacion = self.pedir_texto("Ubicación", obligatorio=False)
        telefono = self.pedir_texto("Teléfono", obligatorio=False)
        correo = self.pedir_texto("Correo institucional", obligatorio=False)
        id_decano = self.pedir_entero("ID del decano", obligatorio=False)

        from modelo_datos import Facultad
        f = Facultad(
            codigoFacultad=codigo,
            nombre=nombre,
            descripcion=descripcion,
            ubicacion=ubicacion,
            telefono=telefono,
            correo=correo,
            idDecano=id_decano,
        )
        creado = self._gestor_crud.crear(f)
        self.mostrar_exito(f"Facultad creada con ID {creado.idFacultad}.")

    def buscar_facultad(self) -> None:
        # Seleccionar una facultad de la lista en lugar de pedir ID
        facultad = self._seleccionar_facultad()
        if facultad is None:
            return

        self.mostrar_tabla(
            "Facultad encontrada",
            ["ID", "Código", "Nombre", "Descripción", "Ubicación", "Teléfono", "Correo", "Decano", "Estado"],
            [[
                facultad.idFacultad,
                facultad.codigoFacultad,
                facultad.nombre,
                facultad.descripcion,
                facultad.ubicacion,
                facultad.telefono,
                facultad.correo,
                facultad.idDecano,
                facultad.estado,
            ]],
        )

    def listar(self) -> None:
        facs = self._gestor_crud.listar()
        self.mostrar_tabla(
            "Lista de facultades",
            ["ID", "Código", "Nombre", "Descripción", "Estado"],
            [[f.idFacultad, f.codigoFacultad, f.nombre, f.descripcion, f.estado] for f in facs],
        )

    def modificar(self) -> None:
        # Seleccionar facultad en lugar de pedir ID
        facultad = self._seleccionar_facultad()
        if facultad is None:
            return

        campo = self.pedir_opcion(
            "Campo a cambiar",
            ["codigoFacultad", "nombre", "descripcion", "ubicacion", "telefono", "correo", "idDecano"],
        )
        valor = self.pedir_texto(f"Nuevo valor de {campo}")
        self._gestor_crud.modificar(facultad.idFacultad, **{campo: valor})
        self.mostrar_exito("Facultad modificada.")

    def desactivar(self) -> None:
        # Seleccionar facultad en lugar de pedir ID
        facultad = self._seleccionar_facultad()
        if facultad is None:
            return

        if self.pedir_bool(f"¿Confirma desactivar la facultad {facultad.idFacultad}?"):
            self._gestor_crud.desactivar(facultad.idFacultad)
            self.mostrar_exito("Facultad desactivada.")