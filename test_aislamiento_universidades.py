"""Suite de pruebas para el aislamiento físico y lógico de datos por universidad (Multi-Tenancy)."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from persistencia.gestor_multi_tenancy import GestorMultiTenancy, TenantUniversidad
from persistencia.gestor_persistencia import GestorPersistencia
from dominio.modelo_datos import Contrato, Facultad, Universidad
from ui_gui.gui_controller import PITAController
from nomina.desglose_anual import CalculadorDesgloseAnual
from nomina.gestor_nomina import GestorNomina


class TestAislamientoUniversidades(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory()
        self.base_path = Path(self.temp_dir.name)
        self.gmt = GestorMultiTenancy(self.base_path)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_catalogo_maestro_tenants(self) -> None:
        """Verifica que se cree y consulte correctamente el catálogo de universidades."""
        tenants = self.gmt.tenants
        self.assertGreaterEqual(len(tenants), 2)
        
        upc = self.gmt.obtener_tenant("upc")
        self.assertIsNotNone(upc)
        self.assertEqual(upc.codigo, "UPC")
        self.assertEqual(upc.directorio, "upc")

        unal = self.gmt.obtener_tenant(2)
        self.assertIsNotNone(unal)
        self.assertEqual(unal.codigo, "UNAL")
        self.assertEqual(unal.directorio, "unal")

    def test_registro_nuevo_tenant_aislado(self) -> None:
        """Verifica el registro dinámico de una nueva universidad con su carpeta creada."""
        nuevo = self.gmt.registrar_tenant(3, "UDEA", "Universidad de Antioquia", "udea")
        self.assertEqual(nuevo.codigo, "UDEA")
        
        dir_udea = self.base_path / "udea"
        self.assertTrue(dir_udea.is_dir())
        
        # Debe persistirse en el archivo catálogo
        gmt2 = GestorMultiTenancy(self.base_path)
        tenant_recuperado = gmt2.obtener_tenant("UDEA")
        self.assertIsNotNone(tenant_recuperado)
        self.assertEqual(tenant_recuperado.nombre, "Universidad de Antioquia")

    def test_aislamiento_fisico_entre_carpetas(self) -> None:
        """Verifica que guardar datos en el almacén de una universidad no altere el almacén de otra."""
        dir_upc = self.gmt.obtener_directorio_tenant("upc")
        dir_unal = self.gmt.obtener_directorio_tenant("unal")

        gp_upc = GestorPersistencia(dir_upc)
        gp_unal = GestorPersistencia(dir_unal)

        # Guardar facultades distintas en cada almacén aislado
        f_upc = [Facultad(1, codigoFacultad="FIT-UPC", nombre="Facultad Ingenieria Cesar", idUniversidad=1)]
        f_unal = [
            Facultad(1, codigoFacultad="FING-UNAL", nombre="Facultad Ingenieria Bogota", idUniversidad=2),
            Facultad(2, codigoFacultad="FMED-UNAL", nombre="Facultad Medicina Bogota", idUniversidad=2),
        ]

        gp_upc.guardar_entidad(f_upc, Facultad)
        gp_unal.guardar_entidad(f_unal, Facultad)

        # Cargar de forma independiente
        cargadas_upc = gp_upc.cargar_entidad(Facultad)
        cargadas_unal = gp_unal.cargar_entidad(Facultad)

        self.assertEqual(len(cargadas_upc), 1)
        self.assertEqual(cargadas_upc[0].codigoFacultad, "FIT-UPC")

        self.assertEqual(len(cargadas_unal), 2)
        self.assertEqual(cargadas_unal[0].codigoFacultad, "FING-UNAL")
        self.assertEqual(cargadas_unal[1].codigoFacultad, "FMED-UNAL")

    def test_conmutacion_de_almacen_en_controller(self) -> None:
        """Verifica que PITAController conmute en caliente su almacenamiento físico y gestores."""
        # Inicializar controller apuntando al directorio datos del proyecto
        ctrl = PITAController(directorio_datos="datos")
        
        # Conmutar a UNAL
        exito_unal = ctrl.seleccionar_universidad("unal")
        self.assertTrue(exito_unal)
        self.assertEqual(ctrl.directorio_datos.name, "unal")
        self.assertEqual(ctrl.tenant_activo.codigo, "UNAL")

        # Conmutar a UPC
        exito_upc = ctrl.seleccionar_universidad("upc")
        self.assertTrue(exito_upc)
        self.assertEqual(ctrl.directorio_datos.name, "upc")
        self.assertEqual(ctrl.tenant_activo.codigo, "UPC")

    def test_generacion_y_validacion_codigo_unico(self) -> None:
        """Verifica la generación sugerida de códigos mnemónicos y su validación de unicidad."""
        sug_udea = self.gmt.generar_codigo_sugerido("Universidad de Antioquia")
        self.assertEqual(sug_udea, "UDEA")

        sug_uis = self.gmt.generar_codigo_sugerido("Universidad Industrial de Santander")
        self.assertEqual(sug_uis, "UIS")

        # Códigos existentes no están disponibles
        self.assertFalse(self.gmt.validar_codigo_disponible("UPC"))
        self.assertFalse(self.gmt.validar_codigo_disponible("UNAL"))
        # Código nuevo sí está disponible
        self.assertTrue(self.gmt.validar_codigo_disponible("UIS"))

    def test_rechazo_codigo_duplicado(self) -> None:
        """Verifica que registrar una universidad con un código repetido lance ValueError."""
        with self.assertRaises(ValueError) as ctx:
            self.gmt.registrar_tenant(nombre="Otra UPC", codigo="UPC")
        self.assertIn("ya está registrado", str(ctx.exception))

    def test_agregar_universidad_en_controller(self) -> None:
        """Verifica que PITAController registre una nueva universidad, cree su directorio y conmute a ella."""
        # Usar un directorio temporal para no afectar datos de producción
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            ctrl = PITAController(directorio_datos=temp_path)

            nuevo_tenant = ctrl.agregar_universidad(
                nombre="Universidad del Valle",
                codigo="UNIVALLE",
                nit="890399010-6",
                ciudad="Cali",
                caja_compensacion="Comfandi",
                arl="Sura",
            )

            self.assertEqual(nuevo_tenant.codigo, "UNIVALLE")
            self.assertEqual(ctrl.tenant_activo.codigo, "UNIVALLE")
            self.assertEqual(ctrl.directorio_datos.name, "univalle")
            self.assertTrue(ctrl.directorio_datos.is_dir())
            self.assertTrue((ctrl.directorio_datos / "universidad.txt").exists())

            # La universidad activa en controller debe coincidir
            self.assertIsNotNone(ctrl.universidad_activa)
            self.assertEqual(ctrl.universidad_activa.codigoInstitucional, "UNIVALLE")


if __name__ == "__main__":
    unittest.main()

