"""Pruebas unitarias y de integración para la asignación de puntos por Doctorado
(Decreto 1279 de 2002) en docentes de PLANTA y la bonificación por posgrado
(Acuerdo 027) en docentes OCASIONALES y CATEDRÁTICOS.
"""

import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

from dominio.modelo_datos import (
    Profesor,
    Contrato,
    FactorSalarial,
    ProduccionAcademica,
    PeriodoNomina,
    LiquidacionNomina,
    ParametroNormativo,
)
from gestores.gestor_factores import GestorFactores
from nomina.calculadora_deducciones import CalculadoraDeducciones
from nomina.calculadora_prestaciones import CalculadoraPrestaciones
from nomina.gestor_nomina import GestorNomina
from persistencia.gestor_persistencia import GestorPersistencia
from persistencia.gestor_multi_tenancy import GestorMultiTenancy


class TestPuntosDoctoradoYNomina(unittest.TestCase):
    def setUp(self) -> None:
        self.calc_deducciones = CalculadoraDeducciones([])
        self.calculadora = CalculadoraPrestaciones(self.calc_deducciones)
        self.smmlv = Decimal("1750905")
        self.valor_punto = Decimal("23924")

    def test_planta_calcula_puntos_doctorado_decreto_1279(self) -> None:
        """Verifica que un profesor de PLANTA con Doctorado reciba los 120 puntos reglamentarios."""
        prof_planta = Profesor(
            idProfesor=1,
            idPersona=10,
            codigoProfesor="DOC-PL-DOC",
            idProgramaPrincipal=1,
            tipoProfesor="PLANTA",
            categoriaDocente="TITULAR",  # 450 pts base
            dedicacion="TIEMPO_COMPLETO",
            maximoNivelEstudio="DOCTORADO",
            tituloProfesional="Doctor en Ciencias",
            areaConocimiento="Física",
            numeroHorasSemanales=Decimal("40"),
            puntosSalariales=Decimal("0"),
            estado="ACTIVO",
            regimenSalarial="Decreto 1279",
        )

        gestor_factores = GestorFactores(profesores=[prof_planta])
        puntos = gestor_factores.calcular_puntos_profesor(1)
        # 450 (Titular) + 120 (Doctorado) = 570 puntos
        self.assertEqual(puntos, Decimal("570"))
        self.assertEqual(prof_planta.puntosSalariales, Decimal("570"))

    def test_planta_con_factores_y_produccion_reconocidos(self) -> None:
        """Verifica acumulación de puntos por escalafón, factores registrados y producción científica."""
        prof_planta = Profesor(
            idProfesor=2,
            idPersona=20,
            codigoProfesor="DOC-PL-PROD",
            idProgramaPrincipal=1,
            tipoProfesor="PLANTA",
            categoriaDocente="ASOCIADO",  # 350 pts base
            dedicacion="TIEMPO_COMPLETO",
            maximoNivelEstudio="DOCTORADO",
            tituloProfesional="Doctor en Informática",
            areaConocimiento="IA",
            numeroHorasSemanales=Decimal("40"),
            puntosSalariales=Decimal("0"),
            estado="ACTIVO",
            regimenSalarial="Decreto 1279",
        )

        factor_doc = FactorSalarial(
            idFactor=1,
            idProfesor=2,
            tipoFactor="TITULO_DOCTORADO",
            puntosReconocidos=Decimal("120"),
            estado="APROBADO",
        )
        prod = ProduccionAcademica(
            idProduccion=1,
            idProfesor=2,
            tipoProduccion="ARTICULO_A1",
            puntosReconocidosProfesor=Decimal("15"),
            estadoValidacion="VALIDADO",
        )

        gestor_factores = GestorFactores(
            factores=[factor_doc],
            producciones=[prod],
            profesores=[prof_planta],
        )
        puntos = gestor_factores.calcular_puntos_profesor(2)
        # 350 (Asociado) + 120 (Doctorado) + 15 (Artículo) = 485
        self.assertEqual(puntos, Decimal("485"))
        self.assertEqual(prof_planta.puntosSalariales, Decimal("485"))

    def test_ocasional_y_catedratico_no_reciben_puntos_decreto_1279(self) -> None:
        """Verifica que docentes OCASIONALES o CATEDRÁTICOS no perciban puntos salariales (Decreto 1279 es solo Planta)."""
        prof_ocasional = Profesor(
            idProfesor=3,
            idPersona=30,
            codigoProfesor="DOC-OCA-DOC",
            idProgramaPrincipal=1,
            tipoProfesor="OCASIONAL",
            categoriaDocente="ASOCIADO",
            dedicacion="TIEMPO_COMPLETO",
            maximoNivelEstudio="DOCTORADO",
            tituloProfesional="Doctor en Biomedicina",
            areaConocimiento="Salud",
            numeroHorasSemanales=Decimal("40"),
            puntosSalariales=Decimal("500"),  # Si viniera con puntos erróneos
            estado="ACTIVO",
            regimenSalarial="Acuerdo 027",
        )
        prof_catedra = Profesor(
            idProfesor=4,
            idPersona=40,
            codigoProfesor="DOC-CAT-MAE",
            idProgramaPrincipal=1,
            tipoProfesor="CATEDRATICO",
            categoriaDocente="ASISTENTE",
            dedicacion="HORA_CATEDRA",
            maximoNivelEstudio="MAESTRIA",
            tituloProfesional="Magíster en Educación",
            areaConocimiento="Pedagogía",
            numeroHorasSemanales=Decimal("16"),
            puntosSalariales=Decimal("300"),
            estado="ACTIVO",
            regimenSalarial="Acuerdo 027",
        )

        gestor_factores = GestorFactores(profesores=[prof_ocasional, prof_catedra])
        puntos_oca = gestor_factores.calcular_puntos_profesor(3)
        self.assertEqual(puntos_oca, Decimal("0"))
        self.assertEqual(prof_ocasional.puntosSalariales, Decimal("0"))

        puntos_cat = gestor_factores.calcular_puntos_profesor(4)
        self.assertEqual(puntos_cat, Decimal("0"))
        self.assertEqual(prof_catedra.puntosSalariales, Decimal("0"))

    def test_bonificacion_posgrado_regimen_acuerdo_027(self) -> None:
        """Verifica que la bonificación en SMMLV aplique a Ocasional/Cátedra y sea 0 para Planta."""
        prof_planta = Profesor(
            idProfesor=1,
            idPersona=1,
            tipoProfesor="PLANTA",
            maximoNivelEstudio="DOCTORADO",
        )
        contrato_planta = Contrato(
            idContrato=1,
            idPersona=1,
            modalidadProfesor="PLANTA",
            dedicacion="TIEMPO_COMPLETO",
            permiteBonificacionPosgrado=True,
        )

        prof_ocasional_doc = Profesor(
            idProfesor=2,
            idPersona=2,
            tipoProfesor="OCASIONAL",
            maximoNivelEstudio="DOCTORADO",
        )
        contrato_oca_doc = Contrato(
            idContrato=2,
            idPersona=2,
            modalidadProfesor="OCASIONAL",
            dedicacion="TIEMPO_COMPLETO",
            permiteBonificacionPosgrado=True,
        )

        prof_ocasional_mae = Profesor(
            idProfesor=3,
            idPersona=3,
            tipoProfesor="OCASIONAL",
            maximoNivelEstudio="MAESTRIA",
        )
        contrato_oca_mae = Contrato(
            idContrato=3,
            idPersona=3,
            modalidadProfesor="OCASIONAL",
            dedicacion="TIEMPO_COMPLETO",
            permiteBonificacionPosgrado=True,
        )

        prof_catedra_esp = Profesor(
            idProfesor=4,
            idPersona=4,
            tipoProfesor="CATEDRATICO",
            maximoNivelEstudio="ESPECIALIZACION",
        )
        contrato_cat_esp = Contrato(
            idContrato=4,
            idPersona=4,
            modalidadProfesor="CATEDRATICO",
            dedicacion="HORA_CATEDRA",
            permiteBonificacionPosgrado=True,
        )

        # Planta NO recibe bonificación mensual en SMMLV (recibe puntos Decreto 1279 en salario base)
        bono_planta = self.calculadora.calcular_bonificacion_posgrado(
            prof_planta, self.smmlv, contrato_planta, None, True
        )
        self.assertEqual(bono_planta, Decimal("0"))

        # Ocasional con Doctorado: 0.90 SMMLV = 1,575,815.00
        bono_oca_doc = self.calculadora.calcular_bonificacion_posgrado(
            prof_ocasional_doc, self.smmlv, contrato_oca_doc, None, True
        )
        self.assertEqual(bono_oca_doc, Decimal("1575815.00"))

        # Ocasional con Maestría: 0.45 SMMLV = 787,907.00
        bono_oca_mae = self.calculadora.calcular_bonificacion_posgrado(
            prof_ocasional_mae, self.smmlv, contrato_oca_mae, None, True
        )
        self.assertEqual(bono_oca_mae, Decimal("787907.00"))

        # Cátedra con Especialización: 0.10 SMMLV = 175,091.00
        bono_cat_esp = self.calculadora.calcular_bonificacion_posgrado(
            prof_catedra_esp, self.smmlv, contrato_cat_esp, None, True
        )
        self.assertEqual(bono_cat_esp, Decimal("175091.00"))

    def test_impacto_doctorado_en_salario_base_y_devengado_planta(self) -> None:
        """Verifica que el salario base y devengado de un docente de planta con doctorado se incremente por los 120 puntos."""
        periodo = PeriodoNomina(
            idPeriodoNomina=1,
            mes=8,
            anio=2026,
            estado="ABIERTO",
            valorPuntoSalarialVigente=self.valor_punto,
            salarioMinimoVigente=self.smmlv,
        )

        # Docente Planta A: Titular sin doctorado (450 pts)
        prof_sin_doc = Profesor(
            idProfesor=1,
            idPersona=1,
            codigoProfesor="DOC-SIN-DOC",
            idProgramaPrincipal=1,
            tipoProfesor="PLANTA",
            categoriaDocente="TITULAR",
            dedicacion="TIEMPO_COMPLETO",
            maximoNivelEstudio="PREGRADO",
            numeroHorasSemanales=Decimal("40"),
            puntosSalariales=Decimal("450"),
            estado="ACTIVO",
            regimenSalarial="Decreto 1279",
        )
        contrato_a = Contrato(
            idContrato=1,
            idPersona=1,
            modalidadProfesor="PLANTA",
            dedicacion="TIEMPO_COMPLETO",
            estado="ACTIVO",
        )

        # Docente Planta B: Titular con doctorado (450 + 120 = 570 pts)
        prof_con_doc = Profesor(
            idProfesor=2,
            idPersona=2,
            codigoProfesor="DOC-CON-DOC",
            idProgramaPrincipal=1,
            tipoProfesor="PLANTA",
            categoriaDocente="TITULAR",
            dedicacion="TIEMPO_COMPLETO",
            maximoNivelEstudio="DOCTORADO",
            numeroHorasSemanales=Decimal("40"),
            puntosSalariales=Decimal("0"),  # El gestor de nómina debe calcular 570
            estado="ACTIVO",
            regimenSalarial="Decreto 1279",
        )
        contrato_b = Contrato(
            idContrato=2,
            idPersona=2,
            modalidadProfesor="PLANTA",
            dedicacion="TIEMPO_COMPLETO",
            estado="ACTIVO",
        )

        gestor_nom = GestorNomina(
            contratos=[contrato_a, contrato_b],
            profesores=[prof_sin_doc, prof_con_doc],
            periodos_nomina=[periodo],
        )

        liq_a = gestor_nom.liquidarProfesorPlanta(1, 1)
        liq_b = gestor_nom.liquidarProfesorPlanta(2, 1)

        diferencia_base = liq_b.salarioBase - liq_a.salarioBase
        diferencia_esperada = Decimal("120") * self.valor_punto  # 120 * 23924 = 2,870,880

        self.assertEqual(diferencia_base, diferencia_esperada)
        self.assertEqual(liq_b.salarioBase, Decimal("570") * self.valor_punto)
        self.assertEqual(liq_a.salarioBase, Decimal("450") * self.valor_punto)
        self.assertEqual(liq_b.puntosSalarialesUsados, Decimal("570"))
        self.assertEqual(liq_a.puntosSalarialesUsados, Decimal("450"))
        # Planta no tiene bonificación mensual en SMMLV
        self.assertEqual(liq_b.bonificacionPosgrado, Decimal("0"))
        self.assertEqual(liq_a.bonificacionPosgrado, Decimal("0"))

    def test_coherencia_datos_multitenant_almacenados(self) -> None:
        """Verifica que los datos almacenados en UNAL, UNAD y UPC cumplan las reglas reglamentarias."""
        gmt = GestorMultiTenancy(Path("datos"))
        for tenant in gmt.tenants:
            gp = GestorPersistencia(gmt.obtener_directorio_tenant(tenant.directorio))
            profesores: list[Profesor] = gp.cargar_entidad(Profesor)
            liquidaciones: list[LiquidacionNomina] = gp.cargar_entidad(LiquidacionNomina)

            self.assertGreater(len(profesores), 0, f"No hay profesores en tenant {tenant.codigo}")
            self.assertGreater(len(liquidaciones), 0, f"No hay liquidaciones en tenant {tenant.codigo}")

            for p in profesores:
                tipo = getattr(p, "tipoProfesor", None) or getattr(p, "tipoVinculacion", None)
                if hasattr(tipo, "value"):
                    tipo = tipo.value
                tipo = str(tipo).upper() if tipo else ""

                if tipo == "PLANTA":
                    self.assertGreater(
                        p.puntosSalariales,
                        Decimal("0"),
                        f"Profesor de planta {p.codigoProfesor} en {tenant.codigo} debería tener puntos salariales asignados"
                    )
                else:
                    self.assertEqual(
                        p.puntosSalariales,
                        Decimal("0"),
                        f"Profesor {tipo} {p.codigoProfesor} en {tenant.codigo} no debe tener puntos Decreto 1279"
                    )

            for liq in liquidaciones:
                tipo = getattr(liq, "tipoProfesorLiquidado", None) or getattr(liq, "tipoVinculacion", None)
                if hasattr(tipo, "value"):
                    tipo = tipo.value
                tipo = str(tipo).upper() if tipo else ""

                if tipo == "PLANTA":
                    self.assertIsNotNone(liq.puntosSalarialesUsados)
                    self.assertGreater(Decimal(str(liq.puntosSalarialesUsados)), Decimal("0"))
                    bono = Decimal(str(liq.bonificacionPosgrado or "0"))
                    self.assertEqual(
                        bono,
                        Decimal("0.00"),
                        f"Docente planta {liq.idProfesor} no debe devengar bonificación posgrado SMMLV"
                    )
                elif tipo in ("OCASIONAL", "CATEDRATICO"):
                    self.assertTrue(
                        liq.puntosSalarialesUsados is None or Decimal(str(liq.puntosSalarialesUsados)) == Decimal("0"),
                        f"Docente ocasional/cátedra {liq.idProfesor} no debe tener puntos Decreto 1279"
                    )
                    bono = Decimal(str(liq.bonificacionPosgrado or "0"))
                    self.assertGreater(
                        bono,
                        Decimal("0.00"),
                        f"Docente ocasional/cátedra {liq.idProfesor} con posgrado debe devengar bonificación posgrado"
                    )


if __name__ == "__main__":
    unittest.main()
