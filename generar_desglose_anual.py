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
from persistencia.gestor_multi_tenancy import GestorMultiTenancy
from dominio.modelo_datos import (
    Administrativo,
    CategoriaDocente,
    Contrato,
    DetalleLiquidacion,
    FactorSalarial,
    LiquidacionNomina,
    ParametroNormativo,
    PeriodoNomina,
    Facultad,
    Persona,
    ProduccionAcademica,
    Profesor,
    ProgramaAcademico,
    Universidad,
)
from nomina.gestor_nomina import GestorNomina
from nomina.desglose_anual import CalculadorDesgloseAnual, DesgloseNominaAnual


def cargar_entorno(directorio: Path):
    persistencia = GestorPersistencia(str(directorio))
    datos = persistencia.cargar_todos_los_datos()

    universidades: list[Universidad] = datos.get(Universidad, [])
    facultades: list[Facultad] = datos.get(Facultad, [])
    programas: list[ProgramaAcademico] = datos.get(ProgramaAcademico, [])
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
        universidades=universidades,
        facultades=facultades,
        programas=programas,
    )
    setattr(gestor, "personas", personas)
    calculador = CalculadorDesgloseAnual(
        gestor,
        universidades=universidades,
        facultades=facultades,
        programas=programas,
    )
    return gestor, calculador, universidades


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    parser = argparse.ArgumentParser(description="Generador de Desglose de Nómina Anual PITA (Multi-Universidad Aislado)")
    parser.add_argument("--datos", default="datos", help="Ruta al directorio de datos (por defecto: datos)")
    parser.add_argument("--anio", type=int, default=2026, help="Año de liquidación a consolidar (por defecto: 2026)")
    parser.add_argument("--universidad", type=str, default=None, help="Filtrar por ID o código de universidad (ej: 1, 2, upc, unal)")
    parser.add_argument("--contrato", type=int, default=None, help="Filtrar por ID de contrato específico")
    parser.add_argument("--exportar", type=str, default=None, help="Ruta de archivo para guardar el reporte (ej: desglose_anual.md)")

    # Opciones de creación y aprovisionamiento de nueva universidad
    parser.add_argument("--crear-universidad", action="store_true", help="Registrar una nueva universidad con código único y aprovisionar su directorio aislado")
    parser.add_argument("--codigo", type=str, default=None, help="Código único institucional (ej: UDEA, UIS, UNIVALLE). Si no se provee, se autogenera.")
    parser.add_argument("--nombre", type=str, default=None, help="Nombre oficial de la universidad a registrar")
    parser.add_argument("--nit", type=str, default="", help="NIT de la universidad")
    parser.add_argument("--ciudad", type=str, default="", help="Ciudad sede principal")
    parser.add_argument("--caja", type=str, default="", help="Caja de compensación familiar")
    parser.add_argument("--arl", type=str, default="", help="Aseguradora de Riesgos Laborales (ARL)")

    args = parser.parse_args()

    directorio_base = Path(args.datos)
    if not directorio_base.exists():
        print(f"Error: El directorio de datos '{directorio_base}' no existe.")
        sys.exit(1)

    gmt = GestorMultiTenancy(directorio_base)

    # 0. Si se solicita crear y registrar una nueva universidad
    if args.crear_universidad:
        if not args.nombre:
            print("[ERROR] Debe especificar el nombre de la institución con --nombre 'Nombre Universidad'")
            sys.exit(1)
        try:
            tenant = gmt.registrar_tenant(
                nombre=args.nombre,
                codigo=args.codigo,
                nit=args.nit,
                ciudad=args.ciudad,
                caja_compensacion=args.caja,
                arl=args.arl,
            )
            print("\n" + "=" * 76)
            print(" [OK] NUEVA UNIVERSIDAD REGISTRADA Y APROVISIONADA CON ÉXITO")
            print("=" * 76)
            print(f" ID Institucional:    {tenant.idUniversidad}")
            print(f" Código Único:        {tenant.codigo}")
            print(f" Nombre Institución:  {tenant.nombre}")
            print(f" Carpeta Aislada:     {directorio_base / tenant.directorio}")
            print(f" Estado:              {tenant.estado}")
            print("=" * 76)
            print(f"La universidad '{tenant.codigo}' ahora está disponible para selección y liquidación independiente.\n")
            return
        except Exception as e:
            print(f"\n[ERROR] al registrar universidad: {e}\n")
            sys.exit(1)

    # 1. Si se especifica una universidad, resolver su espacio de almacenamiento aislado
    if args.universidad is not None:
        tenant = gmt.obtener_tenant(args.universidad)
        if tenant:
            dir_aislado = directorio_base / tenant.directorio
            if dir_aislado.is_dir():
                directorio_activo = dir_aislado
            else:
                directorio_activo = directorio_base
        else:
            directorio_activo = directorio_base

        _, calculador, _ = cargar_entorno(directorio_activo)

        if args.contrato is not None:
            desglose = calculador.generar_desglose_por_contrato(args.contrato, anio=args.anio)
            print(f"\n================================================================================")
            print(f" DESGLOSE DE NÓMINA ANUAL {args.anio} — CONTRATO #{args.contrato}")
            print(f" Empleado: {desglose.nombre_completo} | Tipo: {desglose.tipo_personal} | Régimen: {desglose.regimen}")
            print(f" Institución: {desglose.nombre_universidad} (NIT: {desglose.nit_universidad})")
            print(f" Almacén Aislado: {directorio_activo}")
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
            id_u = tenant.idUniversidad if tenant else None
            reporte = calculador.generar_reporte_texto(anio=args.anio, id_universidad=id_u)
            print(reporte)
            if args.exportar:
                Path(args.exportar).write_text(reporte, encoding="utf-8")
                print(f"\n[OK] Reporte guardado en: {args.exportar}")
        return

    # 2. Si no se especifica universidad, consolidar a través de todos los tenants aislados existentes
    tenants_activos = [t for t in gmt.tenants if (directorio_base / t.directorio).is_dir()]
    if tenants_activos:
        desgloses_totales: list[DesgloseNominaAnual] = []
        for t in tenants_activos:
            dir_tenant = directorio_base / t.directorio
            try:
                _, calc_t, _ = cargar_entorno(dir_tenant)
                d_inst = calc_t.generar_desglose_institucional(anio=args.anio)
                desgloses_totales.extend(d_inst["desgloses_individuales"])
            except Exception as e:
                print(f"Advertencia al consolidar {t.nombre} ({dir_tenant}): {e}")

        # Construir reporte consolidado multi-tenant
        from decimal import Decimal
        from nomina.desglose_anual import redondear
        tot_dev = sum((d.total_devengado_anual for d in desgloses_totales), Decimal("0"))
        tot_desc = sum((d.total_descuentos_anual for d in desgloses_totales), Decimal("0"))
        tot_neto = sum((d.neto_anual_trabajador for d in desgloses_totales), Decimal("0"))
        tot_prest = sum((d.total_prestaciones_anuales for d in desgloses_totales), Decimal("0"))
        tot_aport = sum((d.total_aportes_patronales_anual for d in desgloses_totales), Decimal("0"))
        tot_costo = sum((d.costo_total_empleador_anual for d in desgloses_totales), Decimal("0"))

        lineas = []
        lineas.append("=" * 88)
        lineas.append(f" SISTEMA MULTI-UNIVERSITARIO (ALMACENAMIENTOS AISLADOS) — CONSOLIDADO {args.anio}")
        lineas.append(" Subsistema PITA de Gestión Académica y Nómina Docente (Dec. 1279 / CST)")
        lineas.append("=" * 88)
        lineas.append("")
        lineas.append(f"Total Universidades Aisladas Analizadas: {len(tenants_activos)}")
        lineas.append(f"Total Contratos en el Sistema:           {len(desgloses_totales)}")
        lineas.append(f"Presupuesto Consolidado Empleador:       $ {redondear(tot_costo):,.2f} COP")
        lineas.append(f"  -> Total Devengado Anual (Bruto):      $ {redondear(tot_dev):,.2f} COP")
        lineas.append(f"  -> Total Deducciones Anuales:          $ {redondear(tot_desc):,.2f} COP")
        lineas.append(f"  -> Total Neto Pagado a Docentes:       $ {redondear(tot_neto):,.2f} COP")
        lineas.append(f"  -> Total Prestaciones Sociales:        $ {redondear(tot_prest):,.2f} COP")
        lineas.append(f"  -> Total Aportes Patronales/Paraf:     $ {redondear(tot_aport):,.2f} COP")
        lineas.append("")
        lineas.append("RESUMEN COMPARATIVO POR UNIVERSIDAD:")
        lineas.append("-" * 88)
        lineas.append(f"{'INSTITUCIÓN':<45} | {'CONTRATOS':<10} | {'PRESUPUESTO TOTAL':>25}")
        lineas.append("-" * 88)
        for t in tenants_activos:
            sub = [d for d in desgloses_totales if d.id_universidad == t.idUniversidad or t.nombre.upper() in d.nombre_universidad.upper()]
            costo_sub = sum((d.costo_total_empleador_anual for d in sub), Decimal("0"))
            lineas.append(f"{t.nombre[:44]:<45} | {len(sub):<10} | ${redondear(costo_sub):>24,.2f}")
        lineas.append("-" * 88)
        lineas.append("")

        for d in desgloses_totales:
            lineas.append("-" * 88)
            lineas.append(f"EMPLEADO: {d.nombre_completo} (ID Contrato: #{d.id_contrato} | CC: {d.identificacion})")
            lineas.append(f"Institución: {d.nombre_universidad} | Régimen: {d.regimen} | Categoría: {d.tipo_personal}")
            lineas.append(f"Meses laborados: {d.meses_considerados} ({d.dias_trabajados_anio} días)")
            lineas.append("-" * 88)
            lineas.append(f"{'CONCEPTO':<36} | {'FACTOR / %':<16} | {'VALOR MENSUAL':>14} | {'TOTAL ANUAL':>14}")
            lineas.append("-" * 88)
            for item in d.items:
                lineas.append(f"{item.concepto:<36} | {item.porcentaje_o_factor:<16} | ${item.valor_mensual_promedio:>13,.2f} | ${item.valor_anual_consolidado:>13,.2f}")
            lineas.append("." * 88)
            lineas.append(f"{'TOTAL DEVENGADO ANUAL':<36} | {'':<16} | {'':>14} | ${d.total_devengado_anual:>13,.2f}")
            lineas.append(f"{'TOTAL DEDUCCIONES ANUAL':<36} | {'':<16} | {'':>14} | ${d.total_descuentos_anual:>13,.2f}")
            lineas.append(f"{'NETO ANUAL A RECIBIR':<36} | {'':<16} | {'':>14} | ${d.neto_anual_trabajador:>13,.2f}")
            lineas.append(f"{'TOTAL PRESTACIONES ANUAL':<36} | {'':<16} | {'':>14} | ${d.total_prestaciones_anuales:>13,.2f}")
            lineas.append(f"{'TOTAL APORTES PATRONALES':<36} | {'':<16} | {'':>14} | ${d.total_aportes_patronales_anual:>13,.2f}")
            lineas.append(f"{'COSTO TOTAL EMPLEADOR ANUAL':<36} | {'':<16} | {'':>14} | ${d.costo_total_empleador_anual:>13,.2f}")
            lineas.append("")

        rep_str = "\n".join(lineas)
        print(rep_str)
        if args.exportar:
            Path(args.exportar).write_text(rep_str, encoding="utf-8")
            print(f"\n[OK] Reporte guardado en: {args.exportar}")
    else:
        # Fallback a directorio plano
        _, calculador, _ = cargar_entorno(directorio_base)
        rep = calculador.generar_reporte_texto(anio=args.anio)
        print(rep)

if __name__ == "__main__":
    main()
