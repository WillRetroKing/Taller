#include <gtest/gtest.h>
#include <filesystem>
#include "../dominio/modelo_datos.h"
#include "../dominio/lista_enlazada.h"
#include "../persistencia/gestor_persistencia.h"
#include "../nomina/gestor_nomina.h"
#include "../nomina/desglose_anual.h"

namespace fs = std::filesystem;
using namespace pita;

class TestMultiUniversidades : public ::testing::Test {
protected:
    fs::path tempDir;

    void SetUp() override {
        tempDir = fs::temp_directory_path() / ("pita_test_multi_univ_" + std::to_string(std::chrono::system_clock::now().time_since_epoch().count()));
        fs::create_directories(tempDir);
    }

    void TearDown() override {
        std::error_code ec;
        fs::remove_all(tempDir, ec);
    }
};

TEST_F(TestMultiUniversidades, PersistenciaMultiUniversidad) {
    GestorPersistencia gestor(tempDir.string());

    DatosSistema datos;

    // Universidad 1: UPC
    Universidad u1;
    u1.idUniversidad = 1;
    u1.nombre = "Universidad Popular del Cesar";
    u1.nit = "892300128-6";
    u1.codigoInstitucional = "1084";
    u1.ciudad = "Valledupar";
    u1.cajaCompensacion = "Comfacesar";
    u1.arl = "Positiva";
    u1.estado = "ACTIVO";
    datos.universidades.push_back(u1);

    // Universidad 2: UNAL
    Universidad u2;
    u2.idUniversidad = 2;
    u2.nombre = "Universidad Nacional de Colombia";
    u2.nit = "899999063-3";
    u2.codigoInstitucional = "1101";
    u2.ciudad = "Bogota";
    u2.cajaCompensacion = "Compensar";
    u2.arl = "Sura";
    u2.estado = "ACTIVO";
    datos.universidades.push_back(u2);

    gestor.guardarTodosLosDatos(datos);

    DatosSistema cargados = gestor.cargarTodosLosDatos();
    ASSERT_EQ(cargados.universidades.size(), 2u);

    auto it = cargados.universidades.begin();
    EXPECT_EQ(it->codigoInstitucional.value_or(""), "1084");
    EXPECT_EQ(it->cajaCompensacion.value_or(""), "Comfacesar");
    EXPECT_EQ(it->arl.value_or(""), "Positiva");

    ++it;
    EXPECT_EQ(it->codigoInstitucional.value_or(""), "1101");
    EXPECT_EQ(it->cajaCompensacion.value_or(""), "Compensar");
    EXPECT_EQ(it->arl.value_or(""), "Sura");
}

TEST_F(TestMultiUniversidades, DesgloseInstitucionalConsolidado) {
    ListaEnlazada<Contrato> contratos;
    Contrato c1;
    c1.idContrato = 1;
    c1.idPersona = 10;
    c1.tipoContrato = "DOCENTE_PLANTA";
    c1.modalidadProfesor = "PLANTA";
    c1.dedicacion = Dedicacion::TIEMPO_COMPLETO;
    c1.salarioBase = 8000000.0;
    c1.estado = "ACTIVO";
    contratos.push_back(c1);

    Contrato c2;
    c2.idContrato = 2;
    c2.idPersona = 20;
    c2.tipoContrato = "DOCENTE_OCASIONAL";
    c2.modalidadProfesor = "OCASIONAL";
    c2.dedicacion = Dedicacion::TIEMPO_COMPLETO;
    c2.factorSalarialSMMLV = 2.5;
    c2.estado = "ACTIVO";
    contratos.push_back(c2);

    ListaEnlazada<Profesor> profesores;
    Profesor p1;
    p1.idProfesor = 1;
    p1.idPersona = 10;
    p1.puntosSalariales = 400.0;
    p1.estado = "ACTIVO";
    profesores.push_back(p1);

    Profesor p2;
    p2.idProfesor = 2;
    p2.idPersona = 20;
    p2.puntosSalariales = 0.0;
    p2.estado = "ACTIVO";
    profesores.push_back(p2);

    ListaEnlazada<PeriodoNomina> periodos;
    PeriodoNomina per;
    per.idPeriodoNomina = 1;
    per.anio = 2026;
    per.mes = 1;
    per.salarioMinimoVigente = 1750905.0;
    per.valorPuntoSalarialVigente = 23924.0;
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

    CalculadorDesgloseAnual calc(gestor);
    ResumenNominaAnual resumen = calc.generarDesgloseInstitucional(2026);

    EXPECT_EQ(resumen.totalEmpleados, 2);
    EXPECT_GT(resumen.totalDevengadoAnual, 0.0);
    EXPECT_GT(resumen.totalDeduccionesAnual, 0.0);
    EXPECT_GT(resumen.netoAnualTotal, 0.0);
    EXPECT_GT(resumen.totalPrestacionesAnual, 0.0);
    EXPECT_GT(resumen.totalAportesPatronalesAnual, 0.0);
    EXPECT_GT(resumen.costoTotalInstitucional, 0.0);
    EXPECT_EQ(resumen.desglosesIndividuales.size(), 2u);
}
