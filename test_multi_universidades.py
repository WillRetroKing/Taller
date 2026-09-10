"""Suite de pruebas unitarias para la funcionalidad Multi-Universidad en PITA."""

import unittest
from datetime import date
from decimal import Decimal
from tempfile import TemporaryDirectory

from dominio.modelo_datos import (
    Administrativo,
    Contrato,
    Dedicacion,
    Facultad,
    LiquidacionNomina,
    ParametroNormativo,
    PeriodoNomina,
    Persona,
    Profesor,
    ProgramaAcademico,
    TipoProfesor,
    Universidad,
)
from persistencia.gestor_persistencia import GestorPersistencia
from nomina.gestor_nomina import GestorNomina
from nomina.desglose_anual import CalculadorDesgloseAnual
from ui_gui.gui_controller import PITAController


class TestMultiUniversidades(unittest.TestCase):
    def setUp(self) -> None:
        self.u1 = Universidad(
            idUniversidad=1,
            nombre="Universidad Popular del Cesar",
            nit="892300128-6",
            codigoInstitucional="1084",
            ciudad="Valledupar",
            cajaCompensacion="Comfacesar",
            arl="Positiva",
            estado="ACTIVO",
        )
        self.u2 = Universidad(
            idUniversidad=2,
            nombre="Universidad Nacional de Colombia",
            nit="899999063-3",
            codigoInstitucional="1101",
            ciudad="Bogota",
            cajaCompensacion="Compensar",
            arl="Sura",
            estado="ACTIVO",
        )
        self.fac1 = Facultad(
            idFacultad=1,
            codigoFacultad="FIT",
            nombre="Facultad de Ingenieria UPC",
            idUniversidad=1,
        )
        self.fac2 = Facultad(
            idFacultad=2,
            codigoFacultad="FING",
            nombre="Facultad de Ingenieria UNAL",
            idUniversidad=2,
        )
        self.prog1 = ProgramaAcademico(
            idPrograma=1,
            codigoPrograma="SIS-UPC",
            nombre="Ingenieria de Sistemas",
            idFacultad=1,
        )
        self.prog2 = ProgramaAcademico(
            idPrograma=2,
            codigoPrograma="SIS-UNAL",
            nombre="Ingenieria de Sistemas UNAL",
            idFacultad=2,
        )
        self.per1 = Persona(idPersona=1, primerNombre="Docente", primerApellido="Cesar")
        self.per2 = Persona(idPersona=2, primerNombre="Docente", primerApellido="Nacional")
        self.prof1 = Profesor(
            idProfesor=1,
            idPersona=1,
            idProgramaPrincipal=1,
            tipoProfesor=TipoProfesor.PLANTA,
            dedicacion=Dedicacion.TIEMPO_COMPLETO,
        )
        self.prof2 = Profesor(
            idProfesor=2,
            idPersona=2,
            idProgramaPrincipal=2,
            tipoProfesor=TipoProfesor.PLANTA,
            dedicacion=Dedicacion.TIEMPO_COMPLETO,
        )
        self.c1 = Contrato(
            idContrato=1,
            idPersona=1,
            salarioBase=Decimal("3000000.00"),
            tipoContrato="PLANTA",
            dedicacion=Dedicacion.TIEMPO_COMPLETO,
            estado="ACTIVO",
        )
        # Contrato 2 asignado directamente por idUniversidad
        self.c2 = Contrato(
            idContrato=2,
            idPersona=2,
            salarioBase=Decimal("4000000.00"),
            tipoContrato="PLANTA",
            dedicacion=Dedicacion.TIEMPO_COMPLETO,
            idUniversidad=2,
            estado="ACTIVO",
        )

    def test_persistencia_multi_universidad(self) -> None:
        """Valida que se puedan guardar y cargar múltiples universidades y sus facultades."""
        with TemporaryDirectory() as tmp_dir:
            gestor = GestorPersistencia(tmp_dir)
            datos_guardar = {
                Universidad: [self.u1, self.u2],
                Facultad: [self.fac1, self.fac2],
            }
            gestor.guardar_todos_los_datos(datos_guardar)
            datos_cargados = gestor.cargar_todos_los_datos()

            univs = datos_cargados[Universidad]
            self.assertEqual(len(univs), 2)
            self.assertEqual(univs[0].nombre, "Universidad Popular del Cesar")
            self.assertEqual(univs[1].cajaCompensacion, "Compensar")

            facs = datos_cargados[Facultad]
            self.assertEqual(len(facs), 2)
            self.assertEqual(facs[0].idUniversidad, 1)
            self.assertEqual(facs[1].idUniversidad, 2)

    def test_integridad_referencial_universidad_invalida(self) -> None:
        """Verifica que una facultad con idUniversidad inexistente falle la validación."""
        with TemporaryDirectory() as tmp_dir:
            gestor = GestorPersistencia(tmp_dir)
            datos_guardar = {
                Universidad: [self.u1],
                Facultad: [Facultad(idFacultad=1, idUniversidad=999)],
            }
            gestor.guardar_todos_los_datos(datos_guardar)
            with self.assertRaises(ValueError) as ctx:
                gestor.cargar_todos_los_datos()
            self.assertIn("Facultad.idUniversidad=999 no existe en Universidad", str(ctx.exception))

    def test_resolucion_institucional_contratos(self) -> None:
        """Verifica que el calculador resuelva la universidad por vía directa o por programa/facultad."""
        gestor_nom = GestorNomina(
            contratos=[self.c1, self.c2],
            profesores=[self.prof1, self.prof2],
            periodos_nomina=[],
            universidades=[self.u1, self.u2],
            facultades=[self.fac1, self.fac2],
            programas=[self.prog1, self.prog2],
        )
        setattr(gestor_nom, "personas", [self.per1, self.per2])

        calc = CalculadorDesgloseAnual(
            gestor_nom,
            universidades=[self.u1, self.u2],
            facultades=[self.fac1, self.fac2],
            programas=[self.prog1, self.prog2],
        )

        # c1 se resuelve por jerarquía: c1 -> prof1 -> prog1 -> fac1 -> u1
        u_c1 = calc._resolver_universidad_contrato(self.c1)
        self.assertIsNotNone(u_c1)
        self.assertEqual(u_c1.idUniversidad, 1)
        self.assertEqual(u_c1.nombre, "Universidad Popular del Cesar")

        # c2 se resuelve directamente por c2.idUniversidad = 2
        u_c2 = calc._resolver_universidad_contrato(self.c2)
        self.assertIsNotNone(u_c2)
        self.assertEqual(u_c2.idUniversidad, 2)
        self.assertEqual(u_c2.nombre, "Universidad Nacional de Colombia")

    def test_desglose_individual_con_caja_y_arl_dinamicos(self) -> None:
        """Verifica que cada contrato muestre la ARL y Caja de su respectiva universidad."""
        periodo = PeriodoNomina(
            idPeriodoNomina=1,
            anio=2026,
            mes=1,
            salarioMinimoVigente=Decimal("1750905"),
            valorPuntoSalarialVigente=Decimal("23924"),
            diasBaseLiquidacion=30,
            estado="ABIERTO",
        )
        gestor_nom = GestorNomina(
            contratos=[self.c1, self.c2],
            profesores=[self.prof1, self.prof2],
            periodos_nomina=[periodo],
            universidades=[self.u1, self.u2],
            facultades=[self.fac1, self.fac2],
            programas=[self.prog1, self.prog2],
        )
        setattr(gestor_nom, "personas", [self.per1, self.per2])

        calc = CalculadorDesgloseAnual(
            gestor_nom,
            universidades=[self.u1, self.u2],
            facultades=[self.fac1, self.fac2],
            programas=[self.prog1, self.prog2],
        )

        # Desglose Contrato 1 (UPC)
        d1 = calc.generar_desglose_por_contrato(1, anio=2026)
        self.assertEqual(d1.id_universidad, 1)
        self.assertEqual(d1.nombre_universidad, "Universidad Popular del Cesar")
        item_caja_1 = next(it for it in d1.items if "Caja de Compensación" in it.concepto)
        self.assertIn("Comfacesar", item_caja_1.observaciones)

        # Desglose Contrato 2 (UNAL)
        d2 = calc.generar_desglose_por_contrato(2, anio=2026)
        self.assertEqual(d2.id_universidad, 2)
        self.assertEqual(d2.nombre_universidad, "Universidad Nacional de Colombia")
        item_caja_2 = next(it for it in d2.items if "Caja de Compensación" in it.concepto)
        self.assertIn("Compensar", item_caja_2.observaciones)

    def test_desglose_institucional_filtrado_y_consolidado(self) -> None:
        """Verifica la emisión de desglose por universidad y agrupado consolidado."""
        periodo = PeriodoNomina(
            idPeriodoNomina=1,
            anio=2026,
            mes=1,
            salarioMinimoVigente=Decimal("1750905"),
            valorPuntoSalarialVigente=Decimal("23924"),
            diasBaseLiquidacion=30,
            estado="ABIERTO",
        )
        gestor_nom = GestorNomina(
            contratos=[self.c1, self.c2],
            profesores=[self.prof1, self.prof2],
            periodos_nomina=[periodo],
            universidades=[self.u1, self.u2],
            facultades=[self.fac1, self.fac2],
            programas=[self.prog1, self.prog2],
        )
        setattr(gestor_nom, "personas", [self.per1, self.per2])

        calc = CalculadorDesgloseAnual(
            gestor_nom,
            universidades=[self.u1, self.u2],
            facultades=[self.fac1, self.fac2],
            programas=[self.prog1, self.prog2],
        )

        # Filtrado solo UPC
        res_upc = calc.generar_desglose_institucional(anio=2026, id_universidad=1)
        self.assertEqual(res_upc["total_contratos"], 1)
        self.assertEqual(res_upc["nombre_institucion"], "Universidad Popular del Cesar")

        # Filtrado solo UNAL
        res_unal = calc.generar_desglose_institucional(anio=2026, id_universidad=2)
        self.assertEqual(res_unal["total_contratos"], 1)
        self.assertEqual(res_unal["nombre_institucion"], "Universidad Nacional de Colombia")

        # Consolidado general (sin filtro)
        res_total = calc.generar_desglose_institucional(anio=2026, id_universidad=None)
        self.assertEqual(res_total["total_contratos"], 2)
        self.assertIn(1, res_total["por_universidad"])
        self.assertIn(2, res_total["por_universidad"])

        # Generación de reporte en texto
        rep_texto = calc.generar_reporte_texto(anio=2026)
        self.assertIn("RESUMEN COMPARATIVO POR UNIVERSIDAD", rep_texto)
        self.assertIn("Universidad Popular del Cesar", rep_texto)
        self.assertIn("Universidad Nacional de Colombia", rep_texto)

    def test_gui_controller_universidades(self) -> None:
        """Verifica que el controlador de GUI soporte la lista de universidades y cambio activo."""
        ctrl = PITAController(directorio_datos="datos")
        self.assertGreaterEqual(len(ctrl.universidades), 2)
        self.assertIsNotNone(ctrl.universidad_activa)
        id_inicial = ctrl.universidad_activa.idUniversidad

        # Cambiar a la segunda universidad
        self.assertTrue(ctrl.seleccionar_universidad(2))
        self.assertEqual(ctrl.universidad_activa.idUniversidad, 2)
        self.assertEqual(ctrl.universidad.idUniversidad, 2)

        # Regresar a la inicial
        self.assertTrue(ctrl.seleccionar_universidad(id_inicial))
        self.assertEqual(ctrl.universidad_activa.idUniversidad, id_inicial)


if __name__ == "__main__":
    unittest.main()
