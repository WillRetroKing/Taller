# Main Controller - PITA System
# Modelo MVC: Orquesta la navegación entre vistas y gestores de negocio.

from __future__ import annotations

from datetime import date
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from gestor_academico import GestorAcademico, ErrorAcademico
from gestor_nomina import GestorNomina, ErrorNomina
from gestor_personas import GestorPersonas, ErrorPersona
from gestor_contratos import GestorContratos, ErrorContrato
from gestor_parametros import GestorParametros, ErrorParametro
from gestor_crud import GestorCRUD, ErrorCRUD
from gestor_periodos import GestorPeriodosAcademicos, ErrorPeriodo
from gestor_persistencia import GestorPersistencia
from gestores_academicos import GestorCalificaciones, GestorMatriculas

from ui.base_view import BaseView
from ui.view_academica import AcademicView
from ui.view_nomina import PayrollView
from ui.view_personas import PeopleView
from ui.view_contratos import ContractsView
from ui.view_parametros import ParametrosView
from ui.view_facultades import FacultadesView
from ui.view_programas import ProgramasView
from ui.view_matricula import MatriculaView


class MenuController:
    """Controlador central que gestiona la navegación, el ciclo de vida
    de la aplicación y delega las acciones a las vistas correspondientes.

    Este es el orquestador principal que aplica los principios de:
    - Separación de responsabilidades (SoC)
    - Inyección de dependencias (Dependency Injection)
    - Bajo acoplamiento entre presentación y lógica de negocio
    """

    def __init__(self) -> None:
        # Inicializar gestores (pueden ser inyectados o crearse vacíos)
        self._gestor_nomina = None
        self._gestor_academico = None
        self._gestor_personas = None
        self._gestor_contratos = None
        self._gestor_parametros = None
        self._gestor_crud = None
        self._gestor_periodos = None
        self._gestor_persistencia = None
        self._gestor_calificaciones = None
        self._gestor_matriculas = None

        # Cargar datos de persistencia si existen
        self._cargar_datos_iniciales()

        # Inicializar gestores vacíos si no se cargaron desde persistencia,
        # para que las vistas nunca operen sobre None
        self._inicializar_gestores_vacios()

        # Instanciar vistas
        self._vistas = {
            "1": AcademicView(
                gestor_academico=self._gestor_academico,
                gestor_personas=self._gestor_personas,
            ),
            "2": PayrollView(
                gestor_nomina=self._gestor_nomina,
                gestor_personas=self._gestor_personas,
                gestor_academico=self._gestor_academico,
            ),
            "3": PeopleView(
                gestor_personas=self._gestor_personas,
                gestor_academico=self._gestor_academico,
                gestor_nomina=self._gestor_nomina,
            ),
            "4": ContractsView(
                gestor_contratos=self._gestor_contratos,
                gestor_personas=self._gestor_personas,
                gestor_nomina=self._gestor_nomina,
            ),
            "5": ParametrosView(
                gestor_parametros=self._gestor_parametros,
                gestor_personas=self._gestor_personas,
                gestor_academico=self._gestor_academico,
            ),
            "6": FacultadesView(gestor_crud=self._gestor_crud),
            "7": ProgramasView(gestor_academico=self._gestor_academico),
            "8": MatriculaView(
                gestor_academico=self._gestor_academico,
                gestor_personas=self._gestor_personas,
                gestor_nomina=self._gestor_nomina,
            ),
        }

        # Estado de la aplicación
        self._saliendo = False
        self._contexto = {}  # Contexto compartido entre vistas

    def _cargar_datos_iniciales(self) -> None:
        """Cargar datos iniciales o desde persistencia.

        El usuario decide explícitamente si carga los datos previos o empieza
        con parámetros por defecto. Se muestra un mensaje clarificador al
        arranque, según lo requerido en el Taller 1 EdD (puntos 52-59).
        """
        directorio = Path("datos")

        # Caso 1: El directorio existe y tiene archivos → cargar datos previos
        if directorio.exists() and any(directorio.iterdir()):
            try:
                self._gestor_persistencia = GestorPersistencia(str(directorio))
                datos_cargados = self._gestor_persistencia.cargar_todos_los_datos()

                from modelo_datos import (
                    Administrativo,
                    Contrato,
                    Curso,
                    Estudiante,
                    Facultad,
                    LiquidacionNomina,
                    OfertaCurso,
                    ParametroNormativo,
                    PeriodoAcademico,
                    PeriodoNomina,
                    Persona,
                    PlanEstudio,
                    Profesor,
                    ProgramaAcademico,
                )

                if Facultad in datos_cargados:
                    self._gestor_crud = GestorCRUD(
                        datos_cargados[Facultad],
                        campo_id="idFacultad",
                        campo_codigo="codigoFacultad",
                    )

                if ParametroNormativo in datos_cargados:
                    self._gestor_parametros = GestorParametros(
                        datos_cargados[ParametroNormativo]
                    )

                self._gestor_personas = GestorPersonas(
                    datos_cargados.get(Persona, []),
                    datos_cargados.get(Estudiante, []),
                    datos_cargados.get(Profesor, []),
                    datos_cargados.get(Administrativo, []),
                )

                self._gestor_academico = GestorAcademico(
                    datos_cargados.get(Facultad, []),
                    datos_cargados.get(ProgramaAcademico, []),
                    datos_cargados.get(PlanEstudio, []),
                    datos_cargados.get(Curso, []),
                )

                self._gestor_periodos = GestorPeriodosAcademicos(
                    datos_cargados.get(PeriodoAcademico, []),
                    datos_cargados.get(OfertaCurso, []),
                )

                self._gestor_contratos = GestorContratos(
                    datos_cargados.get(Contrato, [])
                )

                self._gestor_nomina = GestorNomina(
                    datos_cargados.get(Contrato, []),
                    datos_cargados.get(Profesor, []),
                    datos_cargados.get(PeriodoNomina, []),
                    datos_cargados.get(LiquidacionNomina, []),
                    parametros=datos_cargados.get(ParametroNormativo, []),
                )

                self._inicializar_gestores_vacios()
                nombres = [t.__name__ for t in datos_cargados if datos_cargados[t]]
                self._mostrar_message(
                    f"Se cargaron los datos de persistencias desde '{directorio}' "
                    f"({', '.join(nombres)}).",
                    tipo="success",
                )
                return
            except Exception as e:
                self._mostrar_error(
                    f"No fue posible cargar los datos de '{directorio}': {e}"
                )
                # Continuar a continuación con la opción al usuario

        # Caso 2: No hay datos previos — preguntar al usuario
        self._mostrar_message(
            "No encontraron datos de persistencias previas en 'datos/'."
        )
        # Pregunta simple usando Prompt
        from rich.prompt import Prompt
        try:
            respuesta = Prompt.ask(
                "¿Desea crear los parámetros normativos por defecto y comenzar sin datos? (s/n)",
                choices=["s", "n"],
                default="s",
            )
        except (EOFError, TypeError):
            respuesta = "s"
        if respuesta == "s":
            self._crear_parametros_por_defecto()
            self._mostrar_message(
                "Sistema iniciado con parámetros por defecto. "
                "Use la opción 5 del menú para cargar datos posteriores.",
                tipo="info",
            )
        else:
            self._mostrar_message(
                "La aplicación iniciará sin parámetros. Configure los parámetros "
                "después desde la opción 5.", tipo="info"
            )

    def _crear_parametros_por_defecto(self) -> None:
        """Crear parámetros normativos por defecto al iniciar sin datos previos.

        Esto asegura que el sistema funcione inmediatamente sin requerir
        que el usuario configure parámetros manualmente en la primera ejecución.
        Los valores son los típicos de la Universidad Popular del Cesar / Acuerdo 027.
        """
        from modelo_datos import (
            ParametroNormativo,
            ParametroNormativo as PN,
            ParametroNormativoCodigo,
            ParametroNormativoCodigo as PNC,
        )

        self._gestor_persistencia = GestorPersistencia("datos")
        self._gestor_parametros = GestorParametros([])

        # Parámetros monetarios
        parametros_monetarios = [
            # SMMLV - Se sobreescribirá por el usuario cuando tenga el valor real
            PN(
                codigo=PNC.SALARIO_MINIMO,
                nombre="Salario Mínimo Mensual Legal Vigente",
                descripcion="SMMLV vigente para cálculos de nómina y beneficios",
                tipoDato="MONETARIO",
                valor="1000000",  # Valor ejemplo, el usuario debe actualizarlo
                unidad="COP",
                normaOrigen="Acuerdo 027",
                articulo="Art. 1",
                fechaInicioVigencia=date(2026, 1, 1),
                fechaFinVigencia=date(2027, 12, 31),
                aplicaA="TODOS",
                estado="ACTIVO",
            ),
            # Valor punto salarial - para profesores planta Decreto 1279
            ParametroNormativo(
                codigo=ParametroNormativoCodigo.VALOR_PUNTO_SALARIAL,
                nombre="Valor Punto Salarial Vigente",
                descripcion="Valor del punto salarial para cálculo de sueldo de planta",
                tipoDato="MONETARIO",
                valor="50000",
                unidad="COP",
                normaOrigen="Decreto 1279 de 2002",
                articulo="Art. 27",
                fechaInicioVigencia=date(2026, 1, 1),
                fechaFinVigencia=date(2027, 12, 31),
                aplicaA="PLANTA",
                estado="ACTIVO",
            ),
            # Valor auxilio transporte
            ParametroNormativo(
                codigo=ParametroNormativoCodigo.VALOR_AUXILIO_TRANSPORTE_VIGENTE,
                nombre="Valor Auxilio Transporte Vigente",
                descripcion="Auxilio transporte mensual vigente",
                tipoDato="MONETARIO",
                valor="140606",
                unidad="COP",
                normaOrigen="Acuerdo 027",
                articulo="Art. 23",
                fechaInicioVigencia=date(2026, 1, 1),
                fechaFinVigencia=date(2027, 12, 31),
                aplicaA="TODOS",
                estado="ACTIVO",
            ),
            # Valor hora cátedra
            ParametroNormativo(
                codigo=ParametroNormativoCodigo.VALOR_HORA_CATEDRA,
                nombre="Valor Hora Cátedra Vigente",
                descripcion="Valor hora cátedra para profesores catedráticos",
                tipoDato="MONETARIO",
                valor="25000",
                unidad="COP",
                normaOrigen="Resolución Rectoral",
                articulo="Res. Rectoral",
                fechaInicioVigencia=date(2026, 1, 1),
                fechaFinVigencia=date(2027, 12, 31),
                aplicaA="CATEDRATICO",
                estado="ACTIVO",
            ),
            # Tope bonificación servicios Decree 1279
            ParametroNormativo(
                codigo=ParametroNormativoCodigo.TOPE_BONIFICACION_SERVICIOS,
                nombre="Tope Bonificación Servicios",
                descripcion="Tope para bonificación por servicios prestados (Decree 1279)",
                tipoDato="MONETARIO",
                valor="756411",
                unidad="COP",
                normaOrigen="Decreto 1279 de 2002",
                articulo="Art. 41",
                fechaInicioVigencia=date(2026, 1, 1),
                fechaFinVigencia=date(2027, 12, 31),
                aplicaA="PLANTA",
                estado="ACTIVO",
            ),
        ]

        # Parámetros porcentuales
        parametros_porcentuales = [
            # Descuentos trabajador
            ParametroNormativo(
                codigo=ParametroNormativoCodigo.PORCENTAJE_SALUD_TRABAJADOR,
                nombre="Porcentaje Salud Trabajador",
                descripcion="Descuento obligatorio para salud del trabajador",
                tipoDato="PORCENTUAL",
                valor="0.04",
                unidad="",
                normaOrigen="Ley 100 de 1993",
                articulo="Art. 2",
                fechaInicioVigencia=date(2026, 1, 1),
                fechaFinVigencia=date(2027, 12, 31),
                aplicaA="TODOS",
                estado="ACTIVO",
            ),
            ParametroNormativo(
                codigo=ParametroNormativoCodigo.PORCENTAJE_PENSION_TRABAJADOR,
                nombre="Porcentaje Pensión Trabajador",
                descripcion="Descuento obligatorio para pensión del trabajador",
                tipoDato="PORCENTUAL",
                valor="0.04",
                unidad="",
                normaOrigen="Ley 100 de 1993",
                articulo="Art. 2",
                fechaInicioVigencia=date(2026, 1, 1),
                fechaFinVigencia=date(2027, 12, 31),
                aplicaA="TODOS",
                estado="ACTIVO",
            ),
            # Aportes patronales
            ParametroNormativo(
                codigo=ParametroNormativoCodigo.PORCENTAJE_SALUD_EMPLEADOR,
                nombre="Porcentaje Salud Empleador",
                descripcion="Aporte patronal a salud",
                tipoDato="PORCENTUAL",
                valor="0.085",
                unidad="",
                normaOrigen="Ley 100 de 1993",
                articulo="Art. 2",
                fechaInicioVigencia=date(2026, 1, 1),
                fechaFinVigencia=date(2027, 12, 31),
                aplicaA="EMPLEADOR",
                estado="ACTIVO",
            ),
            ParametroNormativo(
                codigo=ParametroNormativoCodigo.PORCENTAJE_PENSION_EMPLEADOR,
                nombre="Porcentaje Pensión Empleador",
                descripcion="Aporte patronal a pensión",
                tipoDato="PORCENTUAL",
                valor="0.12",
                unidad="",
                normaOrigen="Ley 100 de 1993",
                articulo="Art. 2",
                fechaInicioVigencia=date(2026, 1, 1),
                fechaFinVigencia=date(2027, 12, 31),
                aplicaA="EMPLEADOR",
                estado="ACTIVO",
            ),
            ParametroNormativo(
                codigo=ParametroNormativoCodigo.PORCENTAJE_SENA,
                nombre="Porcentaje SENA",
                descripcion="Aporte patronal SENA",
                tipoDato="PORCENTUAL",
                valor="0.02",
                unidad="",
                normaOrigen="Ley 1819 de 2016",
                articulo="Art. 65",
                fechaInicioVigencia=date(2026, 1, 1),
                fechaFinVigencia=date(2027, 12, 31),
                aplicaA="EMPLEADOR",
                estado="ACTIVO",
            ),
            ParametroNormativo(
                codigo=ParametroNormativoCodigo.PORCENTAJE_ICBF,
                nombre="Porcentaje ICBF",
                descripcion="Aporte patronal ICBF",
                tipoDato="PORCENTUAL",
                valor="0.03",
                unidad="",
                normaOrigen="Ley 1819 de 2016",
                articulo="Art. 65",
                fechaInicioVigencia=date(2026, 1, 1),
                fechaFinVigencia=date(2027, 12, 31),
                aplicaA="EMPLEADOR",
                estado="ACTIVO",
            ),
            # ARL (por defecto Clase I)
            ParametroNormativo(
                codigo=ParametroNormativoCodigo.PORCENTAJE_ARL_CLASE_I,
                nombre="Porcentaje ARL Clase I",
                descripcion="Aporte ARL para clase de riesgo I",
                tipoDato="PORCENTUAL",
                valor="0.00522",
                unidad="",
                normaOrigen="Decreto 1298 de 1993",
                articulo="Art. 1",
                fechaInicioVigencia=date(2026, 1, 1),
                fechaFinVigencia=date(2027, 12, 31),
                aplicaA="EMPLEADOR",
                estado="ACTIVO",
            ),
            ParametroNormativo(
                codigo=ParametroNormativoCodigo.PORCENTAJE_CAJA_COMPENSACION,
                nombre="Porcentaje Caja Compensación",
                descripcion="Aporte patronal a caja de compensación",
                tipoDato="PORCENTUAL",
                valor="0.04",
                unidad="",
                normaOrigen="Ley 1819 de 2016",
                articulo="Art. 65",
                fechaInicioVigencia=date(2026, 1, 1),
                fechaFinVigencia=date(2027, 12, 31),
                aplicaA="EMPLEADOR",
                estado="ACTIVO",
            ),
            # Fondo solidaridad (activa cuando IBC >= 4 SMMLV)
            ParametroNormativo(
                codigo=ParametroNormativoCodigo.PORCENTAJE_FONDO_SOLIDARIDAD,
                nombre="Porcentaje Fondo Solidaridad Pensional",
                descripcion="Fondo solidaridad pensional (se aplica si IBC >= 4 SMMLV)",
                tipoDato="PORCENTUAL",
                valor="0.01",
                unidad="",
                normaOrigen="Decreto 1279",
                articulo="Art. 33",
                fechaInicioVigencia=date(2026, 1, 1),
                fechaFinVigencia=date(2027, 12, 31),
                aplicaA="EMPLEADOR",
                estado="ACTIVO",
            ),
            # Retención fuente
            ParametroNormativo(
                codigo=ParametroNormativoCodigo.PORCENTAJE_RETENCION_FUENTE,
                nombre="Porcentaje Retención Fuente",
                descripcion="Retención en la fuente sobre la nómina",
                tipoDato="PORCENTUAL",
                valor="0.00",
                unidad="",
                normaOrigen="Decreto 1625 de 2012",
                articulo="Art. 1",
                fechaInicioVigencia=date(2026, 1, 1),
                fechaFinVigencia=date(2027, 12, 31),
                aplicaA="TODOS",
                estado="ACTIVO",
            ),
            # Parámetros académicos
            ParametroNormativo(
                codigo=ParametroNormativoCodigo.NOTA_MINIMA_APROBATORIA,
                nombre="Nota Mínima Aprobatoria",
                descripcion="Nota mínima para aprobar un curso",
                tipoDato="MONETARIO",
                valor="3.0",
                unidad="",
                normaOrigen="Acuerdo Institucional",
                articulo="Acad. 01",
                fechaInicioVigencia=date(2026, 1, 1),
                fechaFinVigencia=date(2027, 12, 31),
                aplicaA="ESTUDIANTES",
                estado="ACTIVO",
            ),
            ParametroNormativo(
                codigo=ParametroNormativoCodigo.PROMEDIO_MINIMO_EBRA,
                nombre="Promedio Mínimo EBRA",
                descripcion="Promedio acumulado mínimo para alerta EBRA",
                tipoDato="MONETARIO",
                valor="3.0",
                unidad="",
                normaOrigen="Manual Calculadora Mintrabajo",
                articulo="Manual",
                fechaInicioVigencia=date(2026, 1, 1),
                fechaFinVigencia=date(2027, 12, 31),
                aplicaA="ESTUDIANTES",
                estado="ACTIVO",
            ),
            ParametroNormativo(
                codigo=ParametroNormativoCodigo.MAXIMO_CREDITOS_PERIODO,
                nombre="Máximo Créditos Por Periodo",
                descripcion="Créditos máximo que puede matricular un estudiante por periodo",
                tipoDato="ENTERO",
                valor="21",
                unidad="créditos",
                normaOrigen="Reglamento Académico",
                articulo="Art. 78",
                fechaInicioVigencia=date(2026, 1, 1),
                fechaFinVigencia=date(2027, 12, 31),
                aplicaA="ESTUDIANTES",
                estado="ACTIVO",
            ),
        ]

        # Crear todos los parámetros
        todos_parametros = parametros_monetarios + parametros_porcentuales
        for parametro in todos_parametros:
            try:
                self._gestor_parametros.crear_parametro(parametro)
            except ErrorParametro as e:
                # El parámetro puede ya existir o tener validación dura
                # Ignorar si ya fue creado en una ejecución previa
                pass

        # Guardar en archivo de persistencia para futuras sesiones
        if self._gestor_persistencia:
            self._gestor_persistencia.guardar_todos_los_datos({
                ParametroNormativo: self._gestor_parametros.parametros
            })

        self._mostrar_message(
            f"Se han creado {len(todos_parametros)} parámetros normativos por defecto.",
            tipo="success",
        )

    def _inicializar_gestores_vacios(self) -> None:
        """Crear gestores vacíos para los que no se cargaron datos."""
        if self._gestor_parametros is None:
            self._gestor_parametros = GestorParametros([])
        if self._gestor_academico is None:
            self._gestor_academico = GestorAcademico([], [], [], [])
        if self._gestor_personas is None:
            self._gestor_personas = GestorPersonas([])
        if self._gestor_contratos is None:
            self._gestor_contratos = GestorContratos([])
        if self._gestor_nomina is None:
            self._gestor_nomina = GestorNomina([], [], [])
        if self._gestor_periodos is None:
            self._gestor_periodos = GestorPeriodosAcademicos([])
        if self._gestor_matriculas is None:
            self._gestor_matriculas = GestorMatriculas(
                self._gestor_personas.estudiantes,
                self._gestor_periodos.periodos,
                self._gestor_academico.ofertas,
                self._gestor_academico.cursos,
                [],
                [],
                self._gestor_academico.horarios,
                self._gestor_parametros.parametros,
            )
        if self._gestor_calificaciones is None:
            self._gestor_calificaciones = GestorCalificaciones(
                [],
                [],
                self._gestor_matriculas.detalles,
                self._gestor_matriculas.matriculas,
                self._gestor_personas.estudiantes,
                self._gestor_academico.ofertas,
                self._gestor_academico.cursos,
                self._gestor_parametros.parametros,
            )

    def ejecutar(self) -> None:
        """Ejecutar el ciclo principal de la aplicación.

        Bucle principal que:
        1. Muestra el menú principal
        2. Captura la elección del usuario
        3. Delegue a la vista correspondiente
        4. Continúa hasta que el usuario salga
        """
        console = Console()
        try:
            while not self._saliendo:
                self._mostrar_menu_principal()
                eleccion = self._obtener_elegir()

                if eleccion == "0":
                    self._salir_aplicacion()
                elif eleccion in self._vistas:
                    vista = self._vistas[eleccion]
                    continua = vista.display()
                    if not continua:
                        self._saliendo = True
                else:
                    self._mostrar_error("Opción no válida, intente nuevamente.")
                    console.input("\nPresione Enter para continuar...")

        except KeyboardInterrupt:
            self._mostrar_message(
                "Aplicación interrumpida por el usuario.", tipo="info"
            )
        except Exception as e:
            self._mostrar_error(
                f"Error inesperado en el controlador principal: {e}"
            )
        finally:
            self._guardar_datos_finales()
            self._mostrar_message(
                "¡Gracias por usar PITA! Hasta la próxima.",
                tipo="despedida",
            )

    def _mostrar_menu_principal(self) -> None:
        """Display the main application menu."""
        console = Console()
        console.clear()
        console.print(
            Panel(
                "[bold cyan]SISTEMA PITA - INTERFAZ DE CONSOLA[/bold cyan]\n"
                "Versión 2.0 - Arquitectura Modular MVC\n"
                "----------------------\n"
                "Menú Principal\n"
                "----------------------\n"
                "1. Subsistema Académico\n"
                "2. Subsistema de Nómina\n"
                "3. Subsistema de Personas\n"
                "4. Subsistema de Contratos\n"
                "5. Configuración y Parámetros\n"
                "6. Gestionar Facultades\n"
                "7. Gestionar Programas / Ofertas\n"
                "8. Subsistema de Matrícula y Rendimiento\n"
                "0. Salir de la Aplicación\n"
                "----------------------\n"
                "Seleccione una opción para continuar:",
                border_style="cyan",
            )
        )

    def _obtener_elegir(self) -> str:
        """Get user menu choice with validation."""
        from rich.prompt import Prompt
        try:
            return Prompt.ask(
                "\nOpción", choices=["0", "1", "2", "3", "4", "5", "6", "7", "8"], default="0"
            )
        except (EOFError, TypeError):
            return "0"

    def _salir_aplicacion(self) -> None:
        """Handle application exit."""
        self._saliendo = True

    def _mostrar_error(self, mensaje: str) -> None:
        """Show error message to user."""
        console = Console()
        console.print(f"[red]ERROR:[/red] {mensaje}")

    def _mostrar_message(self, mensaje: str, tipo: str = "info") -> None:
        """Show a message with appropriate styling."""
        console = Console()
        if tipo == "info":
            estilo = "blue"
        elif tipo == "success":
            estilo = "green"
        elif tipo == "warning":
            estilo = "yellow"
        elif tipo == "error":
            estilo = "red"
        elif tipo == "despedida":
            estilo = "cyan"
        else:
            estilo = "white"

        console.print(f"[{estilo}]{mensaje}[/{estilo}]")

    def _guardar_datos_finales(self) -> None:
        """Guardar datos al salir de la aplicación."""
        from modelo_datos import ParametroNormativo

        try:
            if self._gestor_persistencia:
                # Collect data from all gestores
                datos = {}

                # Collect from crud gestor
                if self._gestor_crud:
                    datos["Facultad"] = getattr(
                        self._gestor_crud, 'elementos', []
                    ) if hasattr(self._gestor_crud, 'elementos') else []

                # Collect from parametros gestor
                if self._gestor_parametros:
                    datos[ParametroNormativo] = (
                        self._gestor_parametros.parametros
                        if hasattr(self._gestor_parametros, 'parametros')
                        else []
                    )

                # Guardar en persistencia
                self._gestor_persistencia.guardar_todos_los_datos(datos)
                self._mostrar_message(
                    "Datos guardados en persistencias exitosamente.",
                    tipo="success",
                )
        except Exception as e:
            self._mostrar_error(
                f"Error al guardar datos: {e}"
            )


def main() -> None:
    """Punto de entrada de la aplicación PITA (Soporta modo CLI y modo GUI --gui)."""
    import sys
    if "--gui" in sys.argv or "-g" in sys.argv:
        from gui_main import main as main_gui
        main_gui()
        return

    # Crear y ejecutar el controlador principal (CLI)
    controlador = MenuController()

    # Mostrar mensaje de bienvenida
    console = Console()
    console.print(
        Panel(
            "[bold green]Bienvenido a PITA v2.0[/bold green]\n"
            "Sistema de gestión integral para instituciones académicas\n"
            "Arquitectura modular con Programación Orientada a Objetos\n"
            "----------------------\n"
            "La aplicación se ejecutará en modo consola.\n"
            "Para iniciar en modo Interfaz Gráfica ejecute: python main.py --gui\n"
            "Use las opciones numericas para navegar.",
            border_style="green",
        )
    )

    # Ejecutar la aplicación
    controlador.ejecutar()


if __name__ == "__main__":
    main()