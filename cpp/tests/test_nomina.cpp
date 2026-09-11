#include <gtest/gtest.h>
#include <cmath>
#include "../dominio/modelo_datos.h"
#include "../dominio/lista_enlazada.h"
#include "../gestores/gestor_contratos.h"
#include "../gestores/gestor_parametros.h"
#include "../nomina/gestor_nomina.h"
#include "../nomina/calculadora_deducciones.h"

using namespace pita;

TEST(TestNomina, RestriccionesContrato) {
    ListaEnlazada<Contrato> contratos;
    ListaEnlazada<Profesor> profesores;
    ListaEnlazada<Administrativo> administrativos;
    ListaEnlazada<LiquidacionNomina> liquidaciones;

    GestorContratos gestor(contratos, profesores, administrativos, liquidaciones);

    // Contrato inválido: Ocasional con Hora Cátedra y duración irregular
    Contrato invalido;
    invalido.idPersona = 1;
    invalido.tipoContrato = "DOCENTE_OCASIONAL";
    invalido.modalidadProfesor = "OCASIONAL";
    invalido.dedicacion = Dedicacion::HORA_CATEDRA;
    invalido.fechaInicio = "2026-01-01";
    invalido.fechaFin = "2026-06-30"; // 6 meses
    EXPECT_THROW(gestor.crearContrato(invalido), ErrorContrato);

    // Contrato válido: Ocasional Medio Tiempo por 11 meses
    Contrato valido;
    valido.idPersona = 2;
    valido.tipoContrato = "DOCENTE_OCASIONAL";
    valido.modalidadProfesor = "OCASIONAL";
    valido.dedicacion = Dedicacion::MEDIO_TIEMPO;
    valido.fechaInicio = "2026-02-01";
    valido.fechaFin = "2026-12-31"; // 11 meses
    valido.estado = "ACTIVO";

    Contrato& creado = gestor.crearContrato(valido);
    EXPECT_EQ(*creado.idContrato, 1);
}

TEST(TestNomina, ParametrosYNominaPlanta) {
    ListaEnlazada<ParametroNormativo> parametros;
    ListaEnlazada<LiquidacionNomina> liquidaciones;
    GestorParametros gestorParams(parametros, liquidaciones);

    ParametroNormativo p1;
    p1.codigo = ParametroNormativoCodigo::SALARIO_MINIMO;
    p1.valor = "1000";
    p1.fechaInicioVigencia = "2026-01-01";
    p1.estado = "ACTIVO";
    gestorParams.crearParametro(p1);

    // Parámetro solapado con el mismo código debe fallar
    ParametroNormativo p2;
    p2.codigo = ParametroNormativoCodigo::SALARIO_MINIMO;
    p2.valor = "1100";
    p2.fechaInicioVigencia = "2026-01-01";
    p2.estado = "ACTIVO";
    EXPECT_THROW(gestorParams.crearParametro(p2), ErrorParametro);

    // Liquidación Planta con 100 puntos y valor punto = 50 en Medio Tiempo (50%)
    ListaEnlazada<Contrato> contratos;
    Contrato c;
    c.idContrato = 1;
    c.idPersona = 10;
    c.tipoContrato = "DOCENTE_PLANTA";
    c.modalidadProfesor = "PLANTA";
    c.dedicacion = Dedicacion::MEDIO_TIEMPO;
    c.estado = "ACTIVO";
    contratos.push_back(c);

    ListaEnlazada<Profesor> profesores;
    Profesor prof;
    prof.idProfesor = 1;
    prof.idPersona = 10;
    prof.tipoProfesor = TipoProfesor::PLANTA;
    prof.puntosSalariales = 100.0;
    prof.estado = "ACTIVO";
    profesores.push_back(prof);

    ListaEnlazada<PeriodoNomina> periodosNomina;
    PeriodoNomina per;
    per.idPeriodoNomina = 1;
    per.valorPuntoSalarialVigente = 50.0;
    per.salarioMinimoVigente = 1000.0;
    per.estado = "ABIERTO";
    periodosNomina.push_back(per);

    ListaEnlazada<DetalleLiquidacion> detalles;
    ListaEnlazada<CategoriaDocente> categorias;
    ListaEnlazada<FactorSalarial> factores;
    ListaEnlazada<ProduccionAcademica> producciones;

    GestorNomina gestorNom(
        contratos, profesores, periodosNomina, liquidaciones,
        parametros, detalles, categorias, factores, producciones
    );

    LiquidacionNomina liq = gestorNom.liquidarProfesorPlanta(1, 1);
    // 100 pts * 50 = 5000 / 2 (medio tiempo) = 2500
    EXPECT_NEAR(liq.salarioBase.value_or(0.0), 2500.00, 0.01);
}

TEST(TestNomina, NominaCatedraticoProrrateaHoras) {
    ListaEnlazada<Contrato> contratos;
    Contrato c;
    c.idContrato = 1;
    c.idPersona = 10;
    c.tipoContrato = "DOCENTE_CATEDRA";
    c.modalidadProfesor = "CATEDRATICO";
    c.horasMensualesAsignadas = 100.0;
    c.horasMensualesCumplidas = 80.0;
    c.valorHoraCatedraVigente = 20.0;
    c.estado = "ACTIVO";
    contratos.push_back(c);

    ListaEnlazada<Profesor> profesores;
    Profesor prof;
    prof.idProfesor = 1;
    prof.idPersona = 10;
    prof.tipoProfesor = TipoProfesor::CATEDRATICO;
    prof.nivelPosgradoReconocido = "ESPECIALIZACION";
    prof.estado = "ACTIVO";
    profesores.push_back(prof);

    ListaEnlazada<PeriodoNomina> periodos;
    PeriodoNomina per;
    per.idPeriodoNomina = 1;
    per.salarioMinimoVigente = 1000.0;
    per.estado = "ABIERTO";
    periodos.push_back(per);

    ListaEnlazada<LiquidacionNomina> liquidaciones;
    ListaEnlazada<ParametroNormativo> parametros;
    ListaEnlazada<DetalleLiquidacion> detalles;
    ListaEnlazada<CategoriaDocente> categorias;
    ListaEnlazada<FactorSalarial> factores;
    ListaEnlazada<ProduccionAcademica> producciones;

    GestorNomina gestor(
        contratos, profesores, periodos, liquidaciones,
        parametros, detalles, categorias, factores, producciones
    );

    LiquidacionNomina liq = gestor.liquidarProfesorCatedratico(1, 1);
    // 80 horas * $20 = $1600.00
    EXPECT_NEAR(liq.salarioOrdinario.value_or(0.0), 1600.00, 0.01);
    // Especialización cátedra (Acuerdo 027): 0.10 * (80/100) * 1000 = 80.00
    EXPECT_NEAR(liq.bonificacionPosgrado.value_or(0.0), 80.00, 0.01);
    EXPECT_NEAR(liq.baseSeguridadSocial.value_or(0.0), 1600.00, 0.01);
}

TEST(TestNomina, RubricCorrectionsCU21YDeduccionesExactas) {
    // 1. Verificación de exactitud del 4% sobre 1 SMMLV ($1.750.905) -> $70.036,20
    ListaEnlazada<ParametroNormativo> params;
    CalculadoraDeducciones calc(params);
    double ibc = 1750905.00;
    double salud = calc.calcularDescuentoSalud(ibc);
    double pension = calc.calcularDescuentoPension(ibc);
    double caja = calc.calcularAporteCaja(ibc);

    EXPECT_NEAR(salud, 70036.20, 0.01);
    EXPECT_NEAR(pension, 70036.20, 0.01);
    EXPECT_NEAR(caja, 70036.20, 0.01);

    // 2. CU-21: Salario Base Ocasional = 1.750.905 * 3.125 = 5.471.578,13
    ListaEnlazada<Contrato> contratos;
    Contrato c;
    c.idContrato = 100;
    c.idPersona = 100;
    c.tipoContrato = "DOCENTE_OCASIONAL";
    c.modalidadProfesor = "DOCENTE_OCASIONAL";
    c.dedicacion = Dedicacion::TIEMPO_COMPLETO;
    c.factorSalarialSMMLV = 3.125;
    c.estado = "ACTIVO";
    contratos.push_back(c);

    ListaEnlazada<Profesor> profesores;
    Profesor prof;
    prof.idProfesor = 100;
    prof.idPersona = 100;
    prof.tipoProfesor = TipoProfesor::OCASIONAL;
    prof.categoriaDocente = "ASISTENTE";
    prof.dedicacion = Dedicacion::TIEMPO_COMPLETO;
    prof.nivelPosgradoReconocido = "MAESTRIA";
    prof.categoriaGrupoInvestigacion = "GRUPO_B";
    prof.productividadInvestigativaVigente = true;
    prof.certificacionVicerrectoriaInvestigacion = "CERT-001";
    prof.estado = "ACTIVO";
    profesores.push_back(prof);

    ListaEnlazada<PeriodoNomina> periodos;
    PeriodoNomina per;
    per.idPeriodoNomina = 100;
    per.salarioMinimoVigente = 1750905.00;
    per.estado = "ABIERTO";
    periodos.push_back(per);

    ListaEnlazada<LiquidacionNomina> liquidaciones;
    ListaEnlazada<DetalleLiquidacion> detalles;
    ListaEnlazada<CategoriaDocente> categorias;
    ListaEnlazada<FactorSalarial> factores;
    ListaEnlazada<ProduccionAcademica> producciones;

    GestorNomina gestor(
        contratos, profesores, periodos, liquidaciones,
        params, detalles, categorias, factores, producciones
    );

    LiquidacionNomina liq = gestor.liquidarProfesorOcasional(100, 100);

    // Salario base con factor 3.125
    EXPECT_NEAR(liq.salarioBase.value_or(0.0), 5471578.13, 0.05);

    // Bonificaciones CU-23 y CU-24
    // Maestría (0.45): 1.750.905 * 0.45 = 787.907,25 -> 787.907,00
    // Grupo B (0.42): 1.750.905 * 0.42 = 735.380,10 -> 735.380,00
    EXPECT_NEAR(liq.bonificacionPosgrado.value_or(0.0), 787907.00, 1.0);
    EXPECT_NEAR(liq.bonificacionInvestigacion.value_or(0.0), 735380.00, 1.0);

    // Descuentos del 4% calculados con exactitud de centavos
    EXPECT_NEAR(liq.descuentoSalud.value_or(0.0), 218863.13, 0.05);
    EXPECT_NEAR(liq.descuentoPension.value_or(0.0), 218863.13, 0.05);
    EXPECT_NEAR(liq.aporteCajaCompensacion.value_or(0.0), 218863.13, 0.05);
}

TEST(TestNomina, LiquidacionAdministrativo) {
    ListaEnlazada<Administrativo> administrativos;
    Administrativo adm;
    adm.idAdministrativo = 1;
    adm.idPersona = 7;
    adm.cargo = "Director Admisiones";
    adm.salarioBase = 3800000.0;
    adm.estado = "ACTIVO";
    administrativos.push_back(adm);

    ListaEnlazada<Contrato> contratos;
    Contrato c;
    c.idContrato = 4;
    c.idPersona = 7;
    c.tipoContrato = "ADMINISTRATIVO";
    c.salarioBase = 3800000.0;
    c.regimenAplicable = "LEY_100_CST";
    c.estado = "ACTIVO";
    contratos.push_back(c);

    ListaEnlazada<Profesor> profesores;
    ListaEnlazada<PeriodoNomina> periodos;
    PeriodoNomina per;
    per.idPeriodoNomina = 1;
    per.salarioMinimoVigente = 1750905.0;
    per.diasBaseLiquidacion = 30;
    per.estado = "ABIERTO";
    periodos.push_back(per);

    ListaEnlazada<LiquidacionNomina> liquidaciones;
    ListaEnlazada<ParametroNormativo> parametros;
    ListaEnlazada<DetalleLiquidacion> detalles;
    ListaEnlazada<CategoriaDocente> categorias;
    ListaEnlazada<FactorSalarial> factores;
    ListaEnlazada<ProduccionAcademica> producciones;

    GestorNomina gestor(
        contratos, profesores, periodos, liquidaciones,
        parametros, detalles, categorias, factores, producciones,
        &administrativos
    );

    LiquidacionNomina liq = gestor.liquidarAdministrativo(4, 1);

    EXPECT_EQ(liq.regimenLiquidado.value_or(""), "LEY_100_CST");
    EXPECT_NEAR(liq.salarioBase.value_or(0.0), 3800000.00, 0.01);
    EXPECT_NEAR(liq.descuentoSalud.value_or(0.0), 152000.00, 0.01);
    EXPECT_NEAR(liq.descuentoPension.value_or(0.0), 152000.00, 0.01);
    EXPECT_NEAR(liq.totalDescuentos.value_or(0.0), 304000.00, 0.01);
    EXPECT_NEAR(liq.netoPagar.value_or(0.0), 3496000.00, 0.01);
}

TEST(TestNomina, DesgloseNominaAnual) {
    ListaEnlazada<Contrato> contratos;
    Contrato c;
    c.idContrato = 1;
    c.idPersona = 10;
    c.tipoContrato = "DOCENTE_PLANTA";
    c.modalidadProfesor = "PLANTA";
    c.dedicacion = Dedicacion::TIEMPO_COMPLETO;
    c.salarioBase = 10000000.0;
    c.estado = "ACTIVO";
    contratos.push_back(c);

    ListaEnlazada<Profesor> profesores;
    Profesor prof;
    prof.idProfesor = 1;
    prof.idPersona = 10;
    prof.puntosSalariales = 500.0;
    prof.estado = "ACTIVO";
    profesores.push_back(prof);

    ListaEnlazada<PeriodoNomina> periodos;
    PeriodoNomina per;
    per.idPeriodoNomina = 1;
    per.anio = 2026;
    per.mes = 1;
    per.salarioMinimoVigente = 1750905.0;
    per.valorPuntoSalarialVigente = 20000.0;
    per.estado = "ABIERTO";
    periodos.push_back(per);

    ListaEnlazada<LiquidacionNomina> liquidaciones;
    ListaEnlazada<ParametroNormativo> parametros;
    ListaEnlazada<DetalleLiquidacion> detalles;
    ListaEnlazada<CategoriaDocente> categorias;
    ListaEnlazada<FactorSalarial> factores;
    ListaEnlazada<ProduccionAcademica> producciones;

    GestorNomina gestor(
        contratos, profesores, periodos, liquidaciones,
        parametros, detalles, categorias, factores, producciones
    );

    DesgloseNominaAnual desglose = gestor.desgloseNominaAnual(1, 2026);

    EXPECT_EQ(desglose.mesesConsiderados, 12);
    EXPECT_EQ(desglose.diasTrabajadosAnio, 360);
    EXPECT_NEAR(desglose.salarioOrdinarioAnual, 120000000.00, 0.01);
    EXPECT_NEAR(desglose.cesantiasAnuales, 10000000.00, 0.01);
    EXPECT_NEAR(desglose.interesesCesantiasAnuales, 1200000.00, 0.01);
    EXPECT_NEAR(desglose.primaServiciosAnual, 10000000.00, 0.01);
    EXPECT_NEAR(desglose.descuentoSaludAnual, 4800000.00, 0.01);
    EXPECT_NEAR(desglose.descuentoPensionAnual, 4800000.00, 0.01);
    EXPECT_NEAR(desglose.estampillasAnual, 240000.00, 0.01);
    EXPECT_NEAR(desglose.netoAnualTrabajador, 110160000.00, 0.01);
}
