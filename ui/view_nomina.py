"""Vista del subsistema de nómina: periodos, liquidaciones, aprobación,
pago y reportes."""

from __future__ import annotations

from ui.base_view import BaseView


class PayrollView(BaseView):
    titulo = "SUBSISTEMA DE NÓMINA"
    color = "magenta"

    def __init__(self, gestor_nomina, gestor_personas, gestor_academico) -> None:
        super().__init__()
        self._gestor_nomina = gestor_nomina
        self._gestor_personas = gestor_personas
        self._gestor_academico = gestor_academico

    def opciones(self):
        return [
            ("1", "Crear periodo de nómina mensual", self.crear_periodo),
            ("2", "Abrir periodo de nómina", self.abrir_periodo),
            ("3", "Cerrar periodo de nómina", self.cerrar_periodo),
            ("4", "Liquidar profesor", self.liquidar_profesor),
            ("5", "Aprobar liquidación", self.aprobar_liquidacion),
            ("6", "Pagar liquidación", self.pagar_liquidacion),
            ("7", "Consultar liquidaciones", self.consultar_liquidaciones),
            ("8", "Ver detalle de liquidación", self.ver_detalle),
            ("9", "Reliquidar", self.reliquidar),
            ("10", "Resumen de nómina del periodo", self.resumen_periodo),
            ("11", "Totales por tipo de profesor", self.totales_por_tipo),
        ]

    # ------------------------------------------------------------------
    # Búsqueda y selección de personas para liquidación
    # ------------------------------------------------------------------
    def _seleccionar_profesor(self) -> Any | None:
        """Mostrar profesores disponibles y dejar que el usuario seleccione uno.

        Returns: El profesor seleccionado o None si cancela.
        """
        from modelo_datos import Profesor

        # Listar profesores - intentar por programa o listar todos
        id_programa = self.pedir_entero("ID del programa (vacío = todos)", obligatorio=False)

        if id_programa is not None:
            profesores = self._gestor_personas.listar_profesores_por_programa(id_programa) if hasattr(self._gestor_personas, 'listar_profesores_por_programa') else []
        else:
            # Listar todos los intentando por la lista general
            try:
                profesores = []
            except Exception:
                profesores = []

        if not profesores:
            # Intentar listar todos los profesores posibles
            self.mostrar_alerta("No hay profesores registrados en el sistema.")
            self.pausar()
            return None

        # Mostrar profesores con información relevante
        self.console.clear()
        lineas = [f"[bold {self.color}]Seleccionar profesor[/bold {self.color}]", "-" * 60]
        for i, p in enumerate(profesores, 1):
            tp = getattr(p.tipoProfesor, "value", str(p.tipoProfesor)) if hasattr(p, 'tipoProfesor') else "N/A"
            dc = getattr(p.dedicacion, "value", str(p.dedicacion)) if hasattr(p, 'dedicacion') else "N/A"
            lineas.append(f"{i}. ID {p.idProfesor}, Código: {p.codigoProfesor or 'N/A'}, {tp}, {dc}")
        lineas.append("0. Cancelar")
        lineas.append("-" * 60)
        self.console.print(Panel("\n".join(lineas), border_style=self.color))

        while True:
            try:
                eleccion = Prompt.ask(f"\nSeleccione un profesor (1-{len(profesores)}) o 0 para cancelar", default="0").strip()
                if eleccion == "0":
                    return None
                idx = int(eleccion)
                if 1 <= idx <= len(profesores):
                    return profesores[idx - 1]
                self.mostrar_error(f"Por favor seleccione un número entre 1 y {len(profesores)}")
            except (ValueError, EOFError, KeyboardInterrupt):
                return None

    # ------------------------------------------------------------------
    def crear_periodo(self) -> None:
        anio = self.pedir_entero("Año")
        mes = self.pedir_entero("Mes (1-12)")
        periodo = self._gestor_nomina.crear_periodo_nomina_mensual(
            anio=anio,
            mes=mes,
        )
        self.mostrar_exito(
            f"Periodo de nómina creado con ID {periodo.idPeriodoNomina} "
            f"({periodo.mes}/{periodo.anio}, estado {periodo.estado})."
        )

    def abrir_periodo(self) -> None:
        # Intentar seleccionar un periodo en lugar de pedir ID directamente
        # Mostrar periodos disponibles
        periodos = self._gestor_nomina.consultar_liquidaciones() if hasattr(self._gestor_nomina, 'consultar_liquidaciones') else []

        if not periodos:
            self.mostrar_alerta("No hay periodos de nómina registrados.")
            return

        self.console.clear()
        lineas = [f"[bold {self.color}]Seleccionar periodo de nómina[/bold {self.color}]", "-" * 60]
        for i, p in enumerate(periodos, 1):
            # Los periodos pueden ser tuplas o dicts, mostrar lo disponible
            anio = getattr(p, 'anio', p[4] if len(p) > 4 else 'N/A')
            mes = getattr(p, 'mes', p[3] if len(p) > 3 else 'N/A')
            lineas.append(f"{i}. {mes}/{anio} - ID: {getattr(p, 'idPeriodoNomina', p[0] if len(p) > 0 else 'N/A')}")
        lineas.append("0. Cancelar")
        lineas.append("-" * 60)
        self.console.print(Panel("\n".join(lineas), border_style=self.color))

        while True:
            try:
                eleccion = Prompt.ask(f"\nSeleccione un periodo (1-{len(periodos)}) o 0 para cancelar", default="0").strip()
                if eleccion == "0":
                    return
                idx = int(eleccion)
                if 1 <= idx <= len(periodos):
                    id_periodo = periodos[idx - 1].idPeriodoNomina if hasattr(periodos[idx - 1], 'idPeriodoNomina') else periodos[idx - 1][0]
                    self._gestor_nomina.abrir_periodo_nomina(id_periodo)
                    self.mostrar_exito("Periodo abierto.")
                    return
                self.mostrar_error(f"Por favor seleccione un número entre 1 y {len(periodos)}")
            except (ValueError, EOFError, KeyboardInterrupt):
                return

    def cerrar_periodo(self) -> None:
        # Similar a abrir_periodo
        periodos = self._gestor_nomina.consultar_liquidaciones() if hasattr(self._gestor_nomina, 'consultar_liquidaciones') else []

        if not periodos:
            self.mostrar_alerta("No hay periodos de nómina registrados.")
            return

        self.console.clear()
        lineas = [f"[bold {self.color}]Seleccionar periodo de nómina[/bold {self.color}]", "-" * 60]
        for i, p in enumerate(periodos, 1):
            anio = getattr(p, 'anio', p[4] if len(p) > 4 else 'N/A')
            mes = getattr(p, 'mes', p[3] if len(p) > 3 else 'N/A')
            lineas.append(f"{i}. {mes}/{anio} - ID: {getattr(p, 'idPeriodoNomina', p[0] if len(p) > 0 else 'N/A')}")
        lineas.append("0. Cancelar")
        lineas.append("-" * 60)
        self.console.print(Panel("\n".join(lineas), border_style=self.color))

        while True:
            try:
                eleccion = Prompt.ask(f"\nSeleccione un periodo (1-{len(periodos)}) o 0 para cancelar", default="0").strip()
                if eleccion == "0":
                    return
                idx = int(eleccion)
                if 1 <= idx <= len(periodos):
                    id_periodo = periodos[idx - 1].idPeriodoNomina if hasattr(periodos[idx - 1], 'idPeriodoNomina') else periodos[idx - 1][0]
                    if self.pedir_bool(f"¿Confirma cerrar el periodo {id_periodo}?"):
                        self._gestor_nomina.cerrar_periodo_nomina(id_periodo)
                        self.mostrar_exito("Periodo cerrado.")
                    return
                self.mostrar_error(f"Por favor seleccione un número entre 1 y {len(periodos)}")
            except (ValueError, EOFError, KeyboardInterrupt):
                return

    def liquidar_profesor(self) -> None:
        # Seleccionar el profesor
        profesor = self._seleccionar_profesor()
        if profesor is None:
            return

        # Seleccionar el periodo
        periodos = self._gestor_nomina.consultar_liquidaciones() if hasattr(self._gestor_nomina, 'consultar_liquidaciones') else []

        if not periodos:
            self.mostrar_alerta("No hay periodos de nómina registrados.")
            self.pausar()
            return

        self.console.clear()
        lineas = [f"[bold {self.color}]Seleccionar periodo de nómina[/bold {self.color}]", "-" * 60]
        for i, p in enumerate(periodos, 1):
            anio = getattr(p, 'anio', p[4] if len(p) > 4 else 'N/A')
            mes = getattr(p, 'mes', p[3] if len(p) > 3 else 'N/A')
            lineas.append(f"{i}. {mes}/{anio} - ID: {getattr(p, 'idPeriodoNomina', p[0] if len(p) > 0 else 'N/A')}")
        lineas.append("0. Cancelar")
        lineas.append("-" * 60)
        self.console.print(Panel("\n".join(lineas), border_style=self.color))

        while True:
            try:
                eleccion = Prompt.ask(f"\nSeleccione un periodo (1-{len(periodos)}) o 0 para cancelar", default="0").strip()
                if eleccion == "0":
                    return
                idx = int(eleccion)
                if 1 <= idx <= len(periodos):
                    id_periodo = periodos[idx - 1].idPeriodoNomina if hasattr(periodos[idx - 1], 'idPeriodoNomina') else periodos[idx - 1][0]
                    break
                self.mostrar_error(f"Por favor seleccione un número entre 1 y {len(periodos)}")
            except (ValueError, EOFError, KeyboardInterrupt):
                return

        tipo = self.pedir_opcion(
            "Tipo de profesor", ["OCASIONAL", "PLANTA", "CATEDRATICO"]
        )

        if tipo == "OCASIONAL":
            horas = self.pedir_decimal("Horas incumplidas", obligatorio=False)
            liquidacion = self._gestor_nomina.liquidarProfesorOcasional(
                profesor.idProfesor, id_periodo, horas_incumplidas=horas
            )
        elif tipo == "PLANTA":
            liquidacion = self._gestor_nomina.liquidarProfesorPlanta(
                profesor.idProfesor, id_periodo
            )
        else:
            liquidacion = self._gestor_nomina.liquidarProfesorCatedratico(
                profesor.idProfesor, id_periodo
            )
        self.mostrar_exito(
            f"Liquidación {liquidacion.idLiquidacion} creada: "
            f"devengado {liquidacion.totalDevengado}, "
            f"descuentos {liquidacion.totalDescuentos}, "
            f"neto a pagar {liquidacion.netoPagar}."
        )

    def aprobar_liquidacion(self) -> None:
        # Listar liquidaciones pendientes para que el usuario elija
        liquidaciones = self._gestor_nomina.consultar_liquidaciones() if hasattr(self._gestor_nomina, 'consultar_liquidaciones') else []

        if not liquidaciones:
            self.mostrar_alerta("No hay liquidaciones registradas.")
            self.pausar()
            return

        self.console.clear()
        lineas = [f"[bold {self.color}]Seleccionar liquidación[/bold {self.color}]", "-" * 60]
        for i, l in enumerate(liquidaciones, 1):
            profesor_nom = getattr(l, 'idProfesor', l[1] if len(l) > 1 else 'N/A')
            lineas.append(f"{i}. ID {getattr(l, 'idLiquidacion', l[0])}, Profesor: {profesor_nom}, Estado: {getattr(l, 'estado', l[-1])}")
        lineas.append("0. Cancelar")
        lineas.append("-" * 60)
        self.console.print(Panel("\n".join(lineas), border_style=self.color))

        while True:
            try:
                eleccion = Prompt.ask(f"\nSeleccione una liquidación (1-{len(liquidaciones)}) o 0 para cancelar", default="0").strip()
                if eleccion == "0":
                    return
                idx = int(eleccion)
                if 1 <= idx <= len(liquidaciones):
                    id_liquidacion = liquidaciones[idx - 1].idLiquidacion if hasattr(liquidaciones[idx - 1], 'idLiquidacion') else liquidaciones[idx - 1][0]
                    break
                self.mostrar_error(f"Por favor seleccione un número entre 1 y {len(liquidaciones)}")
            except (ValueError, EOFError, KeyboardInterrupt):
                return

        usuario = self.pedir_texto("Usuario que aprueba")
        self._gestor_nomina.aprobar_liquidacion(id_liquidacion, usuario)
        self.mostrar_exito("Liquidación aprobada.")

    def pagar_liquidacion(self) -> None:
        # Listar liquidaciones aprobadas para pagar
        liquidaciones = self._gestor_nomina.consultar_liquidaciones() if hasattr(self._gestor_nomina, 'consultar_liquidaciones') else []

        if not liquidaciones:
            self.mostrar_alerta("No hay liquidaciones registradas.")
            self.pausar()
            return

        self.console.clear()
        lineas = [f"[bold {self.color}]Seleccionar liquidación[/bold {self.color}]", "-" * 60]
        for i, l in enumerate(liquidaciones, 1):
            profesor_nom = getattr(l, 'idProfesor', l[1] if len(l) > 1 else 'N/A')
            lineas.append(f"{i}. ID {getattr(l, 'idLiquidacion', l[0])}, Profesor: {profesor_nom}, Estado: {getattr(l, 'estado', l[-1])}")
        lineas.append("0. Cancelar")
        lineas.append("-" * 60)
        self.console.print(Panel("\n".join(lineas), border_style=self.color))

        while True:
            try:
                eleccion = Prompt.ask(f"\nSeleccione una liquidación (1-{len(liquidaciones)}) o 0 para cancelar", default="0").strip()
                if eleccion == "0":
                    return
                idx = int(eleccion)
                if 1 <= idx <= len(liquidaciones):
                    id_liquidacion = liquidaciones[idx - 1].idLiquidacion if hasattr(liquidaciones[idx - 1], 'idLiquidacion') else liquidaciones[idx - 1][0]
                    break
                self.mostrar_error(f"Por favor seleccione un número entre 1 y {len(liquidaciones)}")
            except (ValueError, EOFError, KeyboardInterrupt):
                return

        medio = self.pedir_opcion(
            "Medio de pago", ["TRANSFERENCIA", "CHEQUE", "EFECTIVO"]
        )
        referencia = self.pedir_texto("Referencia de pago")
        self._gestor_nomina.pagar_liquidacion(id_liquidacion, medio, referencia)
        self.mostrar_exito("Liquidación pagada.")

    def consultar_liquidaciones(self) -> None:
        # Filtrar por profesor o periodo usando selección
        print("\n¿Filtrar por?")
        print("1. Por profesor")
        print("2. Por periodo")
        print("0. Sin filtros (mostrar todas)")
        filtro = Prompt.ask("\nOpción", choices=["0", "1", "2"], default="0").strip()

        liquidaciones = []

        if filtro == "1":
            profesor = self._seleccionar_profesor()
            if profesor is not None:
                liquidaciones = self._gestor_nomina.consultar_liquidaciones(
                    id_profesor=profesor.idProfesor
                )
        elif filtro == "2":
            # Seleccionar periodo
            periodos = self._gestor_nomina.consultar_liquidaciones() if hasattr(self._gestor_nomina, 'consultar_liquidaciones') else []

            if periodos:
                self.console.clear()
                lineas = [f"[bold {self.color}]Seleccionar periodo[/bold {self.color}]", "-" * 60]
                for i, p in enumerate(periodos, 1):
                    anio = getattr(p, 'anio', p[4] if len(p) > 4 else 'N/A')
                    mes = getattr(p, 'mes', p[3] if len(p) > 3 else 'N/A')
                    lineas.append(f"{i}. {mes}/{anio} - ID: {getattr(p, 'idPeriodoNomina', p[0] if len(p) > 0 else 'N/A')}")
                lineas.append("0. Cancelar")
                lineas.append("-" * 60)
                self.console.print(Panel("\n".join(lineas), border_style=self.color))

                while True:
                    try:
                        eleccion = Prompt.ask(f"\nSeleccione un periodo (1-{len(periodos)}) o 0 para cancelar", default="0").strip()
                        if eleccion == "0":
                            return
                        idx = int(eleccion)
                        if 1 <= idx <= len(periodos):
                            id_periodo = periodos[idx - 1].idPeriodoNomina if hasattr(periodos[idx - 1], 'idPeriodoNomina') else periodos[idx - 1][0]
                            liquidaciones = self._gestor_nomina.consultar_liquidaciones(
                                id_profesor=None, id_periodo_nomina=id_periodo
                            )
                            break
                        self.mostrar_error(f"Por favor seleccione un número entre 1 y {len(periodos)}")
                    except (ValueError, EOFError, KeyboardInterrupt):
                        return

        if not liquidaciones:
            self.mostrar_alerta("No hay liquidaciones con los filtros seleccionados.")
            self.pausar()
            return

        self.mostrar_tabla(
            "Liquidaciones",
            ["ID", "Profesor", "Contrato", "Periodo", "Devengado", "Descuentos", "Neto", "Estado"],
            [[l.idLiquidacion, l.idProfesor, l.idContrato, l.idPeriodoNomina,
              l.totalDevengado, l.totalDescuentos, l.netoPagar, l.estado]
             for l in liquidaciones],
        )

    def ver_detalle(self) -> None:
        # Listar liquidaciones para selección
        liquidaciones = self._gestor_nomina.consultar_liquidaciones() if hasattr(self._gestor_nomina, 'consultar_liquidaciones') else []

        if not liquidaciones:
            self.mostrar_alerta("No hay liquidaciones registradas.")
            self.pausar()
            return

        self.console.clear()
        lineas = [f"[bold {self.color}]Seleccionar liquidación[/bold {self.color}]", "-" * 60]
        for i, l in enumerate(liquidaciones, 1):
            profesor_nom = getattr(l, 'idProfesor', l[1] if len(l) > 1 else 'N/A')
            lineas.append(f"{i}. ID {getattr(l, 'idLiquidacion', l[0])}, Profesor: {profesor_nom}, Estado: {getattr(l, 'estado', l[-1])}")
        lineas.append("0. Cancelar")
        lineas.append("-" * 60)
        self.console.print(Panel("\n".join(lineas), border_style=self.color))

        while True:
            try:
                eleccion = Prompt.ask(f"\nSeleccione una liquidación (1-{len(liquidaciones)}) o 0 para cancelar", default="0").strip()
                if eleccion == "0":
                    return
                idx = int(eleccion)
                if 1 <= idx <= len(liquidaciones):
                    id_liquidacion = liquidaciones[idx - 1].idLiquidacion if hasattr(liquidaciones[idx - 1], 'idLiquidacion') else liquidaciones[idx - 1][0]
                    break
                self.mostrar_error(f"Por favor seleccione un número entre 1 y {len(liquidaciones)}")
            except (ValueError, EOFError, KeyboardInterrupt):
                return

        id_liquidacion = id_liquidacion  # Ya definido en el bucle while
        detalles = self._gestor_nomina.consultar_detalles_liquidacion(id_liquidacion)
        self.mostrar_tabla(
            f"Detalle de la liquidación {id_liquidacion}",
            ["ID", "Concepto", "Tipo", "Base", "Porcentaje", "Valor"],
            [[d.idDetalleLiquidacion, d.idConcepto, d.tipoMovimiento,
              d.baseCalculo, d.porcentajeAplicado, d.valorCalculado]
             for d in detalles],
        )

    def reliquidar(self) -> None:
        # Listar liquidaciones para selección
        liquidaciones = self._gestor_nomina.consultar_liquidaciones() if hasattr(self._gestor_nomina, 'consultar_liquidaciones') else []

        if not liquidaciones:
            self.mostrar_alerta("No hay liquidaciones registradas.")
            self.pausar()
            return

        self.console.clear()
        lineas = [f"[bold {self.color}]Seleccionar liquidación[/bold {self.color}]", "-" * 60]
        for i, l in enumerate(liquidaciones, 1):
            profesor_nom = getattr(l, 'idProfesor', l[1] if len(l) > 1 else 'N/A')
            lineas.append(f"{i}. ID {getattr(l, 'idLiquidacion', l[0])}, Profesor: {profesor_nom}, Estado: {getattr(l, 'estado', l[-1])}")
        lineas.append("0. Cancelar")
        lineas.append("-" * 60)
        self.console.print(Panel("\n".join(lineas), border_style=self.color))

        while True:
            try:
                eleccion = Prompt.ask(f"\nSeleccione una liquidación (1-{len(liquidaciones)}) o 0 para cancelar", default="0").strip()
                if eleccion == "0":
                    return
                idx = int(eleccion)
                if 1 <= idx <= len(liquidaciones):
                    id_liquidacion = liquidaciones[idx - 1].idLiquidacion if hasattr(liquidaciones[idx - 1], 'idLiquidacion') else liquidaciones[idx - 1][0]
                    break
                self.mostrar_error(f"Por favor seleccione un número entre 1 y {len(liquidaciones)}")
            except (ValueError, EOFError, KeyboardInterrupt):
                return

        if self.pedir_bool(f"¿Confirma reliquidar la liquidación {id_liquidacion}?"):
            nueva = self._gestor_nomina.reliquidar(id_liquidacion)
            self.mostrar_exito(
                f"Nueva versión creada con ID {nueva.idLiquidacion}, "
                f"neto a pagar {nueva.netoPagar}."
            )

    def resumen_periodo(self) -> None:
        # Seleccionar periodo
        periodos = self._gestor_nomina.consultar_liquidaciones() if hasattr(self._gestor_nomina, 'consultar_liquidaciones') else []

        if not periodos:
            self.mostrar_alerta("No hay periodos de nómina registrados.")
            self.pausar()
            return

        self.console.clear()
        lineas = [f"[bold {self.color}]Seleccionar periodo[/bold {self.color}]", "-" * 60]
        for i, p in enumerate(periodos, 1):
            anio = getattr(p, 'anio', p[4] if len(p) > 4 else 'N/A')
            mes = getattr(p, 'mes', p[3] if len(p) > 3 else 'N/A')
            lineas.append(f"{i}. {mes}/{anio} - ID: {getattr(p, 'idPeriodoNomina', p[0] if len(p) > 0 else 'N/A')}")
        lineas.append("0. Cancelar")
        lineas.append("-" * 60)
        self.console.print(Panel("\n".join(lineas), border_style=self.color))

        while True:
            try:
                eleccion = Prompt.ask(f"\nSeleccione un periodo (1-{len(periodos)}) o 0 para cancelar", default="0").strip()
                if eleccion == "0":
                    return
                idx = int(eleccion)
                if 1 <= idx <= len(periodos):
                    id_periodo = periodos[idx - 1].idPeriodoNomina if hasattr(periodos[idx - 1], 'idPeriodoNomina') else periodos[idx - 1][0]
                    break
                self.mostrar_error(f"Por favor seleccione un número entre 1 y {len(periodos)}")
            except (ValueError, EOFError, KeyboardInterrupt):
                return

        resumen = self._gestor_nomina.resumen_nomina_periodo(id_periodo)
        self.mostrar_tabla(
            f"Resumen del periodo {id_periodo}",
            ["Concepto", "Valor"],
            [[clave, valor] for clave, valor in resumen.items()],
        )

    def totales_por_tipo(self) -> None:
        # Seleccionar periodo
        periodos = self._gestor_nomina.consultar_liquidaciones() if hasattr(self._gestor_nomina, 'consultar_liquidaciones') else []

        if not periodos:
            self.mostrar_alerta("No hay periodos de nómina registrados.")
            self.pausar()
            return

        self.console.clear()
        lineas = [f"[bold {self.color}]Seleccionar periodo[/bold {self.color}]", "-" * 60]
        for i, p in enumerate(periodos, 1):
            anio = getattr(p, 'anio', p[4] if len(p) > 4 else 'N/A')
            mes = getattr(p, 'mes', p[3] if len(p) > 3 else 'N/A')
            lineas.append(f"{i}. {mes}/{anio} - ID: {getattr(p, 'idPeriodoNomina', p[0] if len(p) > 0 else 'N/A')}")
        lineas.append("0. Cancelar")
        lineas.append("-" * 60)
        self.console.print(Panel("\n".join(lineas), border_style=self.color))

        while True:
            try:
                eleccion = Prompt.ask(f"\nSeleccione un periodo (1-{len(periodos)}) o 0 para cancelar", default="0").strip()
                if eleccion == "0":
                    return
                idx = int(eleccion)
                if 1 <= idx <= len(periodos):
                    id_periodo = periodos[idx - 1].idPeriodoNomina if hasattr(periodos[idx - 1], 'idPeriodoNomina') else periodos[idx - 1][0]
                    break
                self.mostrar_error(f"Por favor seleccione un número entre 1 y {len(periodos)}")
            except (ValueError, EOFError, KeyboardInterrupt):
                return

        totales = self._gestor_nomina.totales_por_tipo_profesor(id_periodo)
        filas = []
        for tipo, valores in totales.items():
            for concepto, valor in valores.items():
                filas.append([tipo, concepto, valor])
        self.mostrar_tabla(
            f"Totales por tipo de profesor - periodo {id_periodo}",
            ["Tipo de profesor", "Concepto", "Valor"],
            filas,
        )