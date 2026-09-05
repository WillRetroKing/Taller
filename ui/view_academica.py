"""Vista del subsistema académico: planes de estudio, asignación docente
y horarios."""

from __future__ import annotations

from datetime import datetime

from modelo_datos import Horario, PlanEstudio
from ui.base_view import BaseView


class AcademicView(BaseView):
    titulo = "SUBSISTEMA ACADÉMICO"
    color = "cyan"

    def __init__(self, gestor_academico, gestor_personas) -> None:
        super().__init__()
        self._gestor_academico = gestor_academico
        self._gestor_personas = gestor_personas

    def opciones(self):
        return [
            ("1", "Crear plan de estudio", self.crear_plan),
            ("2", "Consultar plan de estudio", self.consultar_plan),
            ("3", "Incluir curso en plan", self.incluir_curso),
            ("4", "Asignar profesor a oferta", self.asignar_profesor),
            ("5", "Agregar horario a oferta", self.agregar_horario),
            ("6", "Desactivar plan de estudio", self.desactivar_plan),
        ]

    # ------------------------------------------------------------------
    # Búsqueda y selección de planes de estudio
    # ------------------------------------------------------------------
    def _seleccionar_plan_estudio(self) -> Any | None:
        """Mostrar planes de estudio disponibles y dejar que el usuario seleccione uno.

        Returns: El plan de estudio seleccionado o None si cancela.
        """
        planes = self._gestor_academico.listar(
            incluir_inactivos=True
        ) if hasattr(self._gestor_academico, 'listar') else []

        if not planes:
            self.mostrar_alerta("No hay planes de estudio registrados.")
            return None

        # Mostrar con códigos y nombres para que el usuario pueda identificar
        self.console.clear()
        lineas = [f"[bold {self.color}]Seleccionar plan de estudio[/bold {self.color}]", "-" * 60]
        for i, plan in enumerate(planes, 1):
            lineas.append(f"{i}. Código: {plan.codigo or 'N/A'}, Nombre: {plan.nombre or 'N/A'}")
        lineas.append("0. Cancelar")
        lineas.append("-" * 60)
        self.console.print(Panel("\n".join(lineas), border_style=self.color))

        while True:
            try:
                eleccion = Prompt.ask(f"\nSeleccione una opción (1-{len(planes)}) o 0 para cancelar", default="0").strip()
                if eleccion == "0":
                    return None
                idx = int(eleccion)
                if 1 <= idx <= len(planes):
                    return planes[idx - 1]
                self.mostrar_error(f"Por favor seleccione un número entre 1 y {len(planes)}")
            except (ValueError, EOFError, KeyboardInterrupt):
                return None

    # ------------------------------------------------------------------
    def crear_plan(self) -> None:
        plan = self._seleccionar_plan_estudio()
        if plan is None:
            return

        # Si el usuario ya seleccionó un plan, usar su código por defecto,
        # pero permitir modificarlo
        codigo = self.pedir_texto("Código del plan", obligatorio=False) or plan.codigo
        nombre = self.pedir_texto("Nombre del plan")
        version = self.pedir_texto("Versión", obligatorio=False)
        fecha_inicio = self.pedir_fecha("Inicio de vigencia")
        fecha_fin = self.pedir_fecha("Fin de vigencia", obligatorio=False)
        total_creditos = self.pedir_entero("Total de créditos", obligatorio=False)

        id_programa = self.pedir_entero("ID del programa académico")

        plan_nuevo = PlanEstudio(
            codigo=codigo,
            nombre=nombre,
            version=version or (plan.version if hasattr(plan, 'version') else None),
            fechaInicioVigencia=fecha_inicio,
            fechaFinVigencia=fecha_fin or (plan.fechaFinVigencia if hasattr(plan, 'fechaFinVigencia') else None),
            totalCreditos=total_creditos if total_creditos else (plan.totalCreditos if hasattr(plan, 'totalCreditos') else None),
            idPrograma=id_programa,
            estado="ACTIVO",
        )
        creado = self._gestor_academico.crear_plan(plan_nuevo)
        self.mostrar_exito(f"Plan de estudio creado con ID {creado.idPlanEstudio}.")

    def consultar_plan(self) -> None:
        # Intentar seleccionar un plan en lugar de pedir ID directamente
        plan = self._seleccionar_plan_estudio()
        if plan is None:
            return

        id_plan = plan.idPlanEstudio
        plan_obj, detalles = self._gestor_academico.consultar_plan(id_plan)
        self.mostrar_tabla(
            "Plan de estudio",
            ["ID", "Código", "Nombre", "Versión", "Créditos", "Programa", "Estado"],
            [[plan_obj.idPlanEstudio, plan_obj.codigo, plan_obj.nombre, plan_obj.version,
              plan_obj.totalCreditos, plan_obj.idPrograma, plan_obj.estado]],
        )
        self.mostrar_tabla(
            "Cursos del plan",
            ["ID Detalle", "ID Curso", "Semestre", "Tipo", "Créditos", "Obligatorio", "Estado"],
            [[d.idDetallePlan, d.idCurso, d.semestreSugerido, d.tipoCurso,
              d.numeroCreditos, d.esObligatorio, d.estado] for d in detalles],
        )

    def incluir_curso(self) -> None:
        # Seleccionar el plan primero
        plan = self._seleccionar_plan_estudio()
        if plan is None:
            return

        # Luego incluir el curso - pedir ID del curso
        id_curso = self.pedir_entero("ID del curso")

        detalle = self._gestor_academico.incluir_curso(
            id_plan=plan.idPlanEstudio,
            id_curso=id_curso,
            semestre_sugerido=self.pedir_entero("Semestre sugerido"),
            es_obligatorio=self.pedir_bool("¿Es obligatorio?", defecto=True),
        )
        self.mostrar_exito(f"Curso incluido en el plan (detalle ID {detalle.idDetallePlan}).")

    def asignar_profesor(self) -> None:
        # Seleccionar el profesor entre los disponibles
        from modelo_datos import Profesor

        # Primero listar profesores - intentar por programa o listar todos
        id_programa = self.pedir_entero("ID del programa (vacío = todos)", obligatorio=False)
        if id_programa is None:
            # Intentar listar todos los profesores
            try:
                # Esto depende de la implementación del gestor
                profesores = []
            except Exception:
                profesores = []
        else:
            profesores = self._gestor_personas.listar_profesores_por_programa(id_programa) if hasattr(self._gestor_personas, 'listar_profesores_por_programa') else []

        if not profesores:
            # Listar todos intentando una búsqueda diferente
            self.mostrar_alerta("No hay profesores registrados en el sistema.")
            self.pausar()
            return

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
                    return
                idx = int(eleccion)
                if 1 <= idx <= len(profesores):
                    id_profesor = profesores[idx - 1].idProfesor
                    break
                self.mostrar_error(f"Por favor seleccione un número entre 1 y {len(profesores)}")
            except (ValueError, EOFError, KeyboardInterrupt):
                return

        # Seleccionar la oferta de curso
        id_oferta = self.pedir_entero("ID de la oferta de curso")
        numero_horas = self.pedir_decimal("Número de horas")

        asignacion = self._gestor_academico.asignar_profesor(
            id_profesor=id_profesor,
            id_oferta=id_oferta,
            numero_horas=numero_horas,
        )
        self.mostrar_exito(f"Asignación creada con ID {asignacion.idAsignacion}.")

    def agregar_horario(self) -> None:
        id_oferta = self.pedir_entero("ID de la oferta de curso")
        horario = Horario(
            idOfertaCurso=id_oferta,
            diaSemana=self.pedir_opcion(
                "Día de la semana",
                ["LUNES", "MARTES", "MIERCOLES", "JUEVES", "VIERNES", "SABADO"],
            ),
            horaInicio=datetime.strptime(self.pedir_texto("Hora de inicio (HH:MM)"), "%H:%M").time(),
            horaFin=datetime.strptime(self.pedir_texto("Hora de fin (HH:MM)"), "%H:%M").time(),
            aula=self.pedir_texto("Aula", obligatorio=False),
            sede=self.pedir_texto("Sede", obligatorio=False),
            tipoSesion=self.pedir_opcion(
                "Tipo de sesión", ["TEORICA", "PRACTICA", "LABORATORIO", "VIRTUAL"]
            ),
            estado="ACTIVO",
        )
        creado = self._gestor_academico.agregar_horario(horario)
        self.mostrar_exito(f"Horario agregado con ID {creado.idHorario}.")

    def desactivar_plan(self) -> None:
        # Seleccionar el plan en lugar de pedir ID directamente
        plan = self._seleccionar_plan_estudio()
        if plan is None:
            return

        if self.pedir_bool(f"¿Confirma desactivar el plan {plan.idPlanEstudio}?"):
            self._gestor_academico.desactivar_plan(plan.idPlanEstudio)
            self.mostrar_exito("Plan de estudio desactivado.")