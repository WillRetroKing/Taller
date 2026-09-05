"""Vista para gestionar planes de estudio y ofertas cursables."""

from __future__ import annotations

from modelo_datos import PlanEstudio, OfertaCurso
from ui.base_view import BaseView


class ProgramasView(BaseView):
    titulo = "GESTIONAR PROGRAMAS / OFERTAS"
    color = "green"

    def __init__(self, gestor_academico) -> None:
        super().__init__()
        self._gestor_academico = gestor_academico

    def opciones(self):
        return [
            ("1", "Crear plan de estudio", self.crear_plan),
            ("2", "Consultar plan de estudio", self.consultar_plan),
            ("3", "Incluir curso en plan", self.incluir_curso),
            ("4", "Listar planes de estudio", self.listar_planes),
            ("5", "Crear oferta de curso", self.crear_oferta),
            ("6", "Listar ofertas activas", self.listar_ofertas),
        ]

    # ------------------------------------------------------------------
    # Búsqueda y selección de planes de estudio
    # ------------------------------------------------------------------
    def _seleccionar_plan(self) -> Any | None:
        """Mostrar planes de estudio disponibles y dejar que el usuario seleccione uno.

        Returns: El plan de estudio seleccionado o None si cancela.
        """
        planes = self._gestor_academico.planes if hasattr(self._gestor_academico, 'planes') else []

        if not planes:
            self.mostrar_alerta("No hay planes de estudio registrados.")
            return None

        # Mostrar planes con códigos y nombres para identificación
        self.console.clear()
        lineas = [f"[bold {self.color}]Seleccionar plan de estudio[/bold {self.color}]", "-" * 60]
        for i, p in enumerate(planes, 1):
            lineas.append(f"{i}. Código: {p.codigo or 'N/A'}, Nombre: {p.nombre or 'N/A'}")
        lineas.append("0. Cancelar")
        lineas.append("-" * 60)
        self.console.print(Panel("\n".join(lineas), border_style=self.color))

        while True:
            try:
                eleccion = Prompt.ask(f"\nSeleccione un plan (1-{len(planes)}) o 0 para cancelar", default="0").strip()
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
        # Seleccionar si ya existe un plan o crear uno nuevo
        plan = self._seleccionar_plan()
        if plan is None:
            from modelo_datos import PlanEstudio

            codigo = self.pedir_texto("Código del plan")
            nombre = self.pedir_texto("Nombre del plan")
            version = self.pedir_texto("Versión", obligatorio=False)
            fecha_inicio = self.pedir_fecha("Inicio de vigencia")
            fecha_fin = self.pedir_fecha("Fin de vigencia", obligatorio=False)
            total_creditos = self.pedir_entero("Total de créditos")
            id_director = self.pedir_entero("ID del director", obligatorio=False)

            plan = PlanEstudio(
                codigo=codigo,
                nombre=nombre,
                version=version,
                fechaInicioVigencia=fecha_inicio,
                fechaFinVigencia=fecha_fin,
                totalCreditos=total_creditos,
                idDirector=id_director,
            )

        creado = self._gestor_academico.crear_plan(plan)
        self.mostrar_exito(f"Plan de estudio creado con ID {creado.idPlanEstudio}.")

    def consultar_plan(self) -> None:
        # Seleccionar plan en lugar de pedir ID directamente
        plan = self._seleccionar_plan()
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
        plan = self._seleccionar_plan()
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

    def listar_planes(self) -> None:
        planos = self._gestor_academico.planes if hasattr(self._gestor_academico, 'planes') else []
        self.mostrar_tabla(
            "Planes de estudio",
            ["ID", "Código", "Nombre", "Versión", "Créditos", "Director", "Estado"],
            [[p.idPlanEstudio, p.codigo, p.nombre, p.version,
              p.totalCreditos, p.idDirector, p.estado] for p in planos],
        )

    def crear_oferta(self) -> None:
        from modelo_datos import Curso

        # Seleccionar el plan primero
        plan = self._seleccionar_plan()
        if plan is None:
            return

        # Luego seleccionar el curso por código (búsqueda) en lugar de pedir ID
        codigo_curso = self.pedir_texto("Código del curso para la oferta")

        # Buscar el curso en el plan o pedir su ID si no está en el plan
        id_curso = self.pedir_entero("ID del curso para la oferta", obligatorio=False)
        if id_curso is None:
            # Intentar buscar por código en los cursos del plan
            cursos_plan = getattr(plan, 'cursos', [])
            codigo_coincidente = None
            for c in cursos_plan:
                if hasattr(c, 'codigo') and c.codigo == codigo_curso:
                    codigo_coincidente = c
                    break
            if codigo_coincidente is not None:
                id_curso = codigo_coincidente.idCurso if hasattr(codigo_coincidente, 'idCurso') else None

        if id_curso is None:
            self.mostrar_alerta("Se requiere un ID de curso para crear la oferta.")
            self.pausar()
            return

        grupo = self.pedir_texto("Grupo", obligatorio=False)
        cupo = self.pedir_entero("Cupo sugerido", obligatorio=False)

        creado = self._gestor_academico.crear_oferta(
            idOfertaCurso=self._gestor_academico.ofertas.__class__()._siguiente_id()
            if hasattr(self._gestor_academico.ofertas, "_siguiente_id")
            else len(self._gestor_academico.ofertas) + 1,
            idCurso=id_curso,
            idPlan=id_plan.idPlanEstudio,
            grupo=grupo,
            cupoMaximo=cupo,
        )
        self.mostrar_info(f"Oferta creada para el curso {codigo_curso} en el plan {plan.nombre}.")
        # Nota: la creación real de ofertas depende del gestor, aquí mostramos la info

    def listar_ofertas(self) -> None:
        ofertas = self._gestor_academico.listar_ofertas_disponibles()
        self.mostrar_tabla(
            "Ofertas activas",
            ["ID", "ID Curso", "ID Plan", "Grupo", "Cupo", "Estado"],
            [[o.idOfertaCurso, o.idCurso, o.idPlan,
              getattr(o, "grupo", ""), getattr(o, "cupoDisponible", ""),
              getattr(o, "estado", "")] for o in ofertas],
        )