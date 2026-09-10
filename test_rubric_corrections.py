"""Pruebas de validación de la rúbrica de correcciones:
1. Cálculo del Salario Base Ocasional (CU-21) con factor 3.125 para Asistente Tiempo Completo.
2. Consumo en tiempo de ejecución de la variable activa de SALARIO_MINIMO (CU-23 y CU-24).
3. Redondeo exacto sin truncamiento para Salud (4%), Pensión (4%) y Caja (4%).
4. Regla de exclusión de bonificaciones sobre el IBC y la base prestacional.
"""

import unittest
from datetime import date
from decimal import Decimal

from dominio.modelo_datos import (
    Profesor,
    Contrato,
    PeriodoNomina,
    ParametroNormativo,
)
from nomina.gestor_nomina import GestorNomina
from nomina.calculadora_deducciones import CalculadoraDeducciones
from persistencia.gestor_persistencia import GestorPersistencia


class TestRubricCorrections(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.persistencia = GestorPersistencia("cpp/datos")
        cls.datos = cls.persistencia.cargar_todos_los_datos()
        cls.parametros = cls.datos.get(ParametroNormativo, [])

    def test_salario_minimo_activo_en_tiempo_ejecucion(self):
        """Verifica que el parámetro normativo activo en tiempo de ejecución sea $1.750.905."""
        smmlv_param = next((p for p in self.parametros if p.codigo == "SALARIO_MINIMO"), None)
        self.assertIsNotNone(smmlv_param)
        self.assertEqual(smmlv_param.valor, "1750905")

    def test_cu21_salario_base_asistente_tiempo_completo(self):
        """CU-21: salarioBase = SALARIO_MINIMO * 3.125 (no asignar SMMLV directo)."""
        prof_ocasional = Profesor(
            idProfesor=100,
            idPersona=100,
            tipoProfesor="OCASIONAL",
            categoriaDocente="ASISTENTE",
            dedicacion="TIEMPO_COMPLETO",
            nivelPosgradoReconocido="MAESTRIA",
            categoriaGrupoInvestigacion="GRUPO_B",
            productividadInvestigativaVigente=True,
            certificacionVicerrectoriaInvestigacion="CERT-001",
            estado="ACTIVO",
        )
        contrato_ocasional = Contrato(
            idContrato=100,
            idPersona=100,
            modalidadProfesor="OCASIONAL",
            dedicacion="TIEMPO_COMPLETO",
            fechaInicio=date(2026, 1, 1),
            fechaFin=date(2026, 12, 31),
            estado="ACTIVO",
        )
        periodo = PeriodoNomina(
            idPeriodoNomina=100,
            anio=2026,
            mes=3,
            fechaInicio=date(2026, 3, 1),
            fechaFin=date(2026, 3, 31),
            estado="ABIERTO",
        )
        gestor = GestorNomina(
            contratos=[contrato_ocasional],
            profesores=[prof_ocasional],
            periodos_nomina=[periodo],
            parametros=self.parametros,
        )

        liq = gestor.liquidarProfesorOcasional(100, 100)

        # 1. Salario Base Ocasional CU-21:
        # 1.750.905 * 3.125 = 5.471.578,125 -> 5.471.578,13
        self.assertEqual(liq.salarioBase, Decimal("5471578.13"))
        self.assertNotEqual(liq.salarioBase, Decimal("1750905.00"))

        # 2. Bonificaciones CU-23 y CU-24 consumen SMMLV activo ($1.750.905):
        # Maestría (0.45): 1.750.905 * 0.45 = 787.907,25 -> 787.907,00
        # Grupo B (0.42): 1.750.905 * 0.42 = 735.380,10 -> 735.380,00
        self.assertEqual(liq.bonificacionPosgrado, Decimal("787907.00"))
        self.assertEqual(liq.bonificacionInvestigacion, Decimal("735380.00"))

        # 3. Deducciones con base salarial ordinaria (excluyen bonificaciones)
        self.assertEqual(liq.baseSeguridadSocial, Decimal("5471578.13"))
        self.assertEqual(liq.baseLiquidacionPrestaciones, Decimal("5471578.13"))

        # Descuentos del 4% calculados con exactitud de centavos
        self.assertEqual(liq.descuentoSalud, Decimal("218863.13"))
        self.assertEqual(liq.descuentoPension, Decimal("218863.13"))
        self.assertEqual(liq.aporteCajaCompensacion, Decimal("218863.13"))

        # Estampilla Pro-Universidad (0.2% de $5.471.578,13 = $10.943 COP)
        self.assertEqual(liq.otrosDescuentos, Decimal("10943.00"))

    def test_deducciones_4_porciento_alineadas_sin_truncamiento(self):
        """Verifica que sobre 1 SMMLV ($1.750.905), Salud, Pensión y Caja den $70.036,20 exactamente."""
        calc_ded = CalculadoraDeducciones(self.parametros)
        ibc = Decimal("1750905")

        salud = calc_ded.calcular_descuento_salud(ibc)
        pension = calc_ded.calcular_descuento_pension(ibc)
        caja = calc_ded.calcular_aporte_caja(ibc)

        self.assertEqual(salud, Decimal("70036.20"))
        self.assertEqual(pension, Decimal("70036.20"))
        self.assertEqual(caja, Decimal("70036.20"))


if __name__ == "__main__":
    unittest.main()
