"""Vista del subsistema de matrícula y rendimiento académico.

Proporciona funcionalidades para:
- Matricular estudiantes en cursos
- Cancelar matrículas
- Registrar calificaciones
- Calcular promedios acumulados
- Consultar y generar alertas EBRA
"""

from __future__ import annotations

from datetime import date

from modelo_datos import (
    EstadoCurso,
    Evaluacion,
)
from ui.base_view import BaseView


class MatriculaView(BaseView):
    titulo = "SUBSISTEMA DE MATRÍCULA Y RENDIMIENTO"
    color = "magenta"

    def __init__(
        self,
        gestor_academico,
        gestor_personas,
        gestor_nomina,
    ) -> None:
        super().__init__()
        self._gestor_academico = gestor_academico
        self._gestor_personas = gestor_personas
        self._gestor_nomina = gestor_nomina

    def opciones(self):
        return [
            ("1", "Matricular estudiante en curso", self.matricular_estudiante),
            ("2", "Cancelar matrícula de un curso", self.cancelar_matricula),
            ("3", "Registrar calificación de evaluación", self.registrar_calificacion),
            ("4", "Calcular promedio acumulado", self.promedio_acumulado),
            ("5", "Consultar alerta EBRA", self.consultar_ebra),
            ("6", "Listar matrículas del estudiante", self.listar_matriculas),
        ]

    # ------------------------------------------------------------------
    # Búsqueda y selección de estudiantes
    # ------------------------------------------------------------------
    def _seleccionar_estudiante(self) -> Any | None:
        """Mostrar estudiantes disponibles y dejar que el usuario seleccione uno.

        Returns: El estudiante seleccionado o None si cancela.
        """
        # Intentar listar estudiantes desde el gestor
        estudiantes = self._gestor_academico.estudiantes if hasattr(self._gestor_academico, 'estudiantes') else []

        if not estudiantes:
            # Intentar por el gestor de personas
            try:
                from modelo_datos import Persona
                todas = self._gestor_personas.listar(
                    incluir_inactivos=False
                ) if hasattr(self._gestor_personas, 'listar') else []
                estudiantes = [e for e in todas if hasattr(e, 'idEstudiante') and e.idEstudiante is not None]
            except Exception:
                estudiantes = []

        if not estudiantes:
            self.mostrar_alerta("No hay estudiantes registrados en el sistema.")
            return None

        # Mostrar estudiantes con nombre y documento para identificación
        self.console.clear()
        lineas = [f"[bold {self.color}]Seleccionar estudiante[/bold {self.color}]", "-" * 60]
        for i, e in enumerate(estudiantes, 1):
            doc = f"{e.tipoDocumento} {e.numeroDocumento or ''}".strip() if hasattr(e, 'tipoDocumento') else "N/A"
            nombres = f"{e.primerNombre or ''} {e.segundoNombre or ''}".strip() if hasattr(e, 'primerNombre') else "N/A"
            apellidos = f"{e.primerApellido or ''} {e.segundoApellido or ''}".strip() if hasattr(e, 'primerApellido') else "N/A"
            lineas.append(f"{i}. Doc: {doc}, Nombres: {nombres} {apellidos}, ID: {getattr(e, 'idEstudiante', e.idPersona)}")
        lineas.append("0. Cancelar")
        lineas.append("-" * 60)
        self.console.print(Panel("\n".join(lineas), border_style=self.color))

        while True:
            try:
                eleccion = Prompt.ask(f"\nSeleccione un estudiante (1-{len(estudiantes)}) o 0 para cancelar", default="0").strip()
                if eleccion == "0":
                    return None
                idx = int(eleccion)
                if 1 <= idx <= len(estudiantes):
                    return estudiantes[idx - 1]
                self.mostrar_error(f"Por favor seleccione un número entre 1 y {len(estudiantes)}")
            except (ValueError, EOFError, KeyboardInterrupt):
                return None

    # ------------------------------------------------------------------
    def _seleccionar_oferta(self) -> Any | None:
        """Mostrar ofertas de curso disponibles y dejar que el usuario seleccione una.

        Returns: La oferta seleccionada o None si cancela.
        """
        ofertas = self._gestor_academico.listar_ofertas_disponibles() if hasattr(self._gestor_academico, 'listar_ofertas_disponibles') else []

        if not ofertas:
            self.mostrar_alerta("No hay ofertas de curso disponibles.")
            return None

        # Mostrar ofertas con información relevante
        self.console.clear()
        lineas = [f"[bold {self.color}]Seleccionar oferta de curso[/bold {self.color}]", "-" * 60]
        for i, o in enumerate(ofertas, 1):
            codigo_curso = getattr(o, 'codigoCurso', getattr(o, 'idCurso', 'N/A'))
            nombre_curso = getattr(o, 'nombreCurso', getattr(o, 'idCurso', 'N/A'))
            plan = getattr(o, 'idPlanEstudio', 'N/A')
            lineas.append(f"{i}. Curso: {codigo_curso} ({nombre_curso}), Plan ID: {plan}")
        lineas.append("0. Cancelar")
        lineas.append("-" * 60)
        self.console.print(Panel("\n".join(lineas), border_style=self.color))

        while True:
            try:
                eleccion = Prompt.ask(f"\nSeleccione una oferta (1-{len(ofertas)}) o 0 para cancelar", default="0").strip()
                if eleccion == "0":
                    return None
                idx = int(eleccion)
                if 1 <= idx <= len(ofertas):
                    return ofertas[idx - 1]
                self.mostrar_error(f"Por favor seleccione un número entre 1 y {len(ofertas)}")
            except (ValueError, EOFError, KeyboardInterrupt):
                return None

    # ------------------------------------------------------------------
    def matricular_estudiante(self) -> None:
        """Matricular un estudiante en un curso ofertado."""
        estudiante = self._seleccionar_estudiante()
        if estudiante is None:
            return

        oferta = self._seleccionar_oferta()
        if oferta is None:
            return

        fecha = self.pedir_fecha("Fecha de matrícula", obligatorio=False) or date.today()

        try:
            detalle = self._gestor_academico.matricular_curso(
                id_estudiante=estudiante.idEstudiante,
                id_oferta=oferta.idOfertaCurso,
                fecha_matricula=fecha,
            )
            self.mostrar_exito(
                f"Estudiante matriculado en la oferta {oferta.idOfertaCurso} "
                f"(detalle ID {detalle.idDetalleMatricula})."
            )
        except Exception as e:
            self.mostrar_error(str(e))

    def cancelar_matricula(self) -> None:
        """Cancelar una matrícula de un curso."""
        estudiante = self._seleccionar_estudiante()
        if estudiante is None:
            return

        # Listar matrículas del estudiante
        matriculas = self._gestor_academico.listar_matriculas_estudiante(
            estudiante.idEstudiante
        ) if hasattr(self._gestor_academico, 'listar_matriculas_estudiante') else []

        if not matriculas:
            self.mostrar_alerta("El estudiante no tiene matrículas registradas.")
            self.pausar()
            return

        # Mostrar matrículas para selección
        self.console.clear()
        lineas = [f"[bold {self.color}]Seleccionar matrícula[/bold {self.color}]", "-" * 60]
        for i, m in enumerate(matriculas, 1):
            oferta = getattr(m, 'idOfertaCurso', getattr(m, 'idDetalleMatricula', i))
            curso = getattr(m, 'idCurso', 'N/A')
            lineas.append(f"{i}. Detalle ID: {getattr(m, 'idDetalleMatricula', i)}, Curso: {curso}")
        lineas.append("0. Cancelar")
        lineas.append("-" * 60)
        self.console.print(Panel("\n".join(lineas), border_style=self.color))

        while True:
            try:
                eleccion = Prompt.ask(f"\nSeleccione una matrícula (1-{len(matriculas)}) o 0 para cancelar", default="0").strip()
                if eleccion == "0":
                    return
                idx = int(eleccion)
                if 1 <= idx <= len(matriculas):
                    id_detalle = matriculas[idx - 1].idDetalleMatricula if hasattr(matriculas[idx - 1], 'idDetalleMatricula') else matriculas[idx - 1][-1] if len(matriculas[idx - 1]) > 1 else 0
                    break
                self.mostrar_error(f"Por favor seleccione un número entre 1 y {len(matriculas)}")
            except (ValueError, EOFError, KeyboardInterrupt):
                return

        id_estudiante = estudiante.idEstudiante

        try:
            self._gestor_academico.cancelar_curso(id_estudiante, id_detalle)
            self.mostrar_exito("Matrícula cancelada.")
        except Exception as e:
            self.mostrar_error(str(e))

    def registrar_calificacion(self) -> None:
        """Registrar una nota para una evaluación de un curso."""
        estudiante = self._seleccionar_estudiante()
        if estudiante is None:
            return

        oferta = self._seleccionar_oferta()
        if oferta is None:
            return

        # Buscar la evaluación
        self.console.clear()
        print("\n¿Qué evaluación desea calificar?")
        print("1. Elegir por ID de evaluación")
        print("2. Usar última evaluación registrada")
        opcion = Prompt.ask("\nOpción", choices=["1", "2"], default="1").strip()

        id_evaluacion = None
        if opcion == "1":
            id_evaluacion = self.pedir_entero("ID de la evaluación")
        # Si es opción 2, dejamos id_evaluacion en None y el gestor usará la última

        nota = self.pedir_decimal("Nota obtenida (0-5)")
        fecha = self.pedir_fecha("Fecha de registro", obligatorio=False)

        try:
            calificacion = self._gestor_academico.registrar_calificon(
                id_estudiante=estudiante.idEstudiante,
                id_oferta=oferta.idOfertaCurso,
                id_evaluacion=id_evaluacion,
                nota=nota,
                fecha_registro=fecha,
            )
            self.mostrar_exito(f"Calificación registrada: {calificacion.nota}")

            # Después de registrar, recalcular promedio y verificar EBRA
            self.promedio_acumulado()
        except Exception as e:
            self.mostrar_error(str(e))

    def promedio_acumulado(self) -> None:
        """Calcular y mostrar el promedio acumulado del estudiante, verificando EBRA."""
        estudiante = self._seleccionar_estudiante()
        if estudiante is None:
            return

        try:
            promedio = self._gestor_academico.calcular_promedio_acumulado(estudiante.idEstudiante)
            self.mostrar_exito(
                f"Promedio acumulado: {promedio:.2f}"
            )

            # Verificar EBRA
            alerta = self._gestor_academico.evaluar_ebra(estudiante.idEstudiante)
            if alerta is not None:
                self.mostrar_alerta(
                    f"ALERTA EBRA activada para el estudiante {estudiante.idEstudiante}. "
                    f"Período: {alerta.idPeriodo}."
                )
            else:
                self.mostrar_info("El estudiante no está en EBRA (promedio suficiente).")
        except Exception as e:
            self.mostrar_error(str(e))

    def consultar_ebra(self) -> None:
        """Consultar el estado EBRA del estudiante."""
        estudiante = self._seleccionar_estudiante()
        if estudiante is None:
            return

        alerta = self._gestor_academico.evaluar_ebra(estudiante.idEstudiante)
        if alerta is None:
            self.mostrar_info("El estudiante no está en EBRA (promedio suficiente).")
        else:
            self.mostrar_alerta(
                f"ALERTA EBRA activada para el estudiante {estudiante.idEstudiante}. "
                f"Período: {alerta.idPeriodo}."
            )

    def listar_matriculas(self) -> None:
        """Listar todas las matrículas de un estudiante."""
        estudiante = self._seleccionar_estudiante()
        if estudiante is None:
            return

        matriculas = self._gestor_academico.listar_matriculas_estudiante(
            estudiante.idEstudiante
        ) if hasattr(self._gestor_academico, 'listar_matriculas_estudiante') else []

        if not matriculas:
            self.mostrar_info("El estudiante no tiene matrículas registradas.")
            return

        self.mostrar_tabla(
            f"Matrículas del estudiante {estudiante.idEstudiante}",
            ["ID Matrícula", "ID Oferta", "Curso", "Semestre", "Estado", "Nota Final"],
            [
                [
                    getattr(m, 'idMatricula', m[0] if len(m) > 0 else 'N/A'),
                    getattr(m, 'idOfertaCurso', m[1] if len(m) > 1 else 'N/A'),
                    getattr(m, 'idCurso', getattr(m, 'codigoCurso', 'N/A')),
                    getattr(m, 'semestreActual', 'N/A'),
                    getattr(m, 'estadoMatricula', 'N/A'),
                    getattr(m, 'notaFinal', 'N/A'),
                ]
                for m in matriculas
            ],
        )