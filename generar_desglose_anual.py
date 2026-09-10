"""Script de Consolidación y Desglose de Nómina Anual — Sistema PITA (UPC).

Permite consolidar la nómina liquidada mes a mes y generar el desglose anual
detallado con prestaciones sociales (Cesantías, Intereses, Primas, Vacaciones),
descuentos de ley y costo total del empleador para docentes de Planta (Dec. 1279),
Ocasionales y Catedráticos.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from persistencia.gestor_persistencia import GestorPersistencia
from dominio.modelo_datos import (
    Administrativo,
    CategoriaDocente,
    Contrato,
    DetalleLiquidacion,
    FactorSalarial,
    LiquidacionNomina,
    ParametroNormativo,
    PeriodoNomina,
    Persona,
    ProduccionAcademica,
    Profesor,
)
from nomina.gestor_nomina import GestorNomina
from nomina.desglose_anual import CalculadorDesgloseAnual


def main() -> None:
    parser = argparse.ArgumentParser(description="Generador de Desglose de Nómina Anual PITA (UPC)")
    parser.add_argument("--datos", default="datos", help="Ruta al directorio de datos (por defecto: datos)")
    parser.add_argument("--anio", type=int, default=2026, help="Año de liquidación a consolidar (por defecto: 2026)")
    parser.add_argument("--contrato", type=int, default=None, help="Filtrar por ID de contrato específico")
    parser.add_argument("--exportar", type=str, default=None, help="Ruta de archivo para guardar el reporte (ej: desglose_anual.md)")
    args = parser.parse_args()

    directorio = Path(args.datos)
    if not directorio.exists():
        print(f"Error: El directorio de datos '{directorio}' no existe.")
        sys.exit(1)

    # 1. Cargar persistencia
    persistencia = GestorPersistencia(str(directorio))
    datos = persistencia.cargar_todos_los_datos()

    contratos: list[Contrato] = datos.get(Contrato, [])
    profesores: list[Profesor] = datos.get(Profesor, [])
    periodos: list[PeriodoNomina] = datos.get(PeriodoNomina, [])
    liquidaciones: list[LiquidacionNomina] = datos.get(LiquidacionNomina, [])
    parametros: list[ParametroNormativo] = datos.get(ParametroNormativo, [])
    detalles: list[DetalleLiquidacion] = datos.get(DetalleLiquidacion, [])
    categorias: list[CategoriaDocente] = datos.get(CategoriaDocente, [])
    factores: list[FactorSalarial] = datos.get(FactorSalarial, [])
    producciones: list[ProduccionAcademica] = datos.get(ProduccionAcademica, [])
    administrativos: list[Administrativo] = datos.get(Administrativo, [])
    personas: list[Persona] = datos.get(Persona, [])

    # 2. Instanciar Gestor de Nómina y Calculador
    gestor = GestorNomina(
        contratos=contratos,
        profesores=profesores,
        periodos_nomina=periodos,
        liquidaciones=liquidaciones,
        parametros=parametros,
        detalles_liquidacion=detalles,
        categorias=categorias,
        factores=factores,
        producciones=producciones,
        administrativos=administrativos,
    )
    # Asociar personas para nombres en reportes
    setattr(gestor, "personas", personas)

    calculador = CalculadorDesgloseAnual(gestor)

    # 3. Generar reporte o desglose específico
    if args.contrato is not None:
        desglose = calculador.generar_desglose_por_contrato(args.contrato, anio=args.anio)
        print(f"\n================================================================================")
        print(f" DESGLOSE DE NÓMINA ANUAL {args.anio} — CONTRATO #{args.contrato}")
        print(f" Empleado: {desglose.nombre_completo} | Tipo: {desglose.tipo_personal} | Régimen: {desglose.regimen}")
        print(f" Meses laborados: {desglose.meses_considerados} ({desglose.dias_trabajados_anio} días)")
        print(f"================================================================================")
        print(f"{'CONCEPTO':<38} | {'PORCENTAJE':<16} | {'MENSUAL':>14} | {'ANUAL':>14}")
        print("-" * 88)
        for it in desglose.items:
            print(f"{it.concepto:<38} | {it.porcentaje_o_factor:<16} | ${it.valor_mensual_promedio:>13,.2f} | ${it.valor_anual_consolidado:>13,.2f}")
        print("-" * 88)
        print(f"{'TOTAL DEVENGADO ANUAL':<38} | {'':<16} | {'':>14} | ${desglose.total_devengado_anual:>13,.2f}")
        print(f"{'TOTAL DEDUCCIONES ANUAL':<38} | {'':<16} | {'':>14} | ${desglose.total_descuentos_anual:>13,.2f}")
        print(f"{'NETO ANUAL PAGADO AL EMPLEADO':<38} | {'':<16} | {'':>14} | ${desglose.neto_anual_trabajador:>13,.2f}")
        print(f"{'TOTAL PRESTACIONES SOCIALES ANUAL':<38} | {'':<16} | {'':>14} | ${desglose.total_prestaciones_anuales:>13,.2f}")
        print(f"{'TOTAL APORTES PATRONALES ANUAL':<38} | {'':<16} | {'':>14} | ${desglose.total_aportes_patronales_anual:>13,.2f}")
        print(f"{'COSTO TOTAL INSTITUCIONAL ANUAL':<38} | {'':<16} | {'':>14} | ${desglose.costo_total_empleador_anual:>13,.2f}")
    else:
        reporte = calculador.generar_reporte_texto(anio=args.anio)
        print(reporte)

        if args.exportar:
            ruta_exp = Path(args.exportar)
            ruta_exp.write_text(reporte, encoding="utf-8")
            print(f"\n[OK] Reporte anual guardado exitosamente en: {ruta_exp.resolve()}")


if __name__ == "__main__":
    main()
