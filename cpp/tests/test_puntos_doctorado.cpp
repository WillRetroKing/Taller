#include <gtest/gtest.h>
#include <cmath>
#include "../dominio/modelo_datos.h"
#include "../dominio/lista_enlazada.h"
#include "../gestores/gestor_factores.h"
#include "../nomina/gestor_nomina.h"
#include "../nomina/calculadora_prestaciones.h"

using namespace pita;

class TestPuntosDoctoradoYNomina : public ::testing::Test {
protected:
    ListaEnlazada<CategoriaDocente> categorias;
    ListaEnlazada<FactorSalarial> factores;
    ListaEnlazada<ProduccionAcademica> producciones;
    ListaEnlazada<Profesor> profesores;
    ListaEnlazada<Contrato> contratos;
    ListaEnlazada<PeriodoNomina> periodosNomina;
    ListaEnlazada<LiquidacionNomina> liquidaciones;
    ListaEnlazada<ParametroNormativo> parametros;
    ListaEnlazada<DetalleLiquidacion> detalles;

    void SetUp() override {
        // Cargar parámetros base
        ParametroNormativo pSMMLV;
        pSMMLV.codigo = ParametroNormativoCodigo::SALARIO_MINIMO;
        pSMMLV.valor = "1750905";
        pSMMLV.estado = "ACTIVO";
        parametros.push_back(pSMMLV);

        ParametroNormativo pPunto;
        pPunto.codigo = ParametroNormativoCodigo::VALOR_PUNTO_SALARIAL;
        pPunto.valor = "23924";
        pPunto.estado = "ACTIVO";
        parametros.push_back(pPunto);

        PeriodoNomina per;
        per.idPeriodoNomina = 1;
        per.salarioMinimoVigente = 1750905.0;
        per.valorPuntoSalarialVigente = 23924.0;
        per.estado = "ABIERTO";
        periodosNomina.push_back(per);
    }
};

TEST_F(TestPuntosDoctoradoYNomina, PlantaCalculaPuntosDoctoradoDecreto1279) {
    // Verifica que un docente de PLANTA con Doctorado reciba los 120 puntos reglamentarios (450 + 120 = 570)
    Profesor prof;
    prof.idProfesor = 1;
    prof.idPersona = 10;
    prof.codigoProfesor = "DOC-PL-DOC";
    prof.tipoProfesor = TipoProfesor::PLANTA;
    prof.categoriaDocente = "TITULAR"; // 450 pts base
    prof.dedicacion = Dedicacion::TIEMPO_COMPLETO;
    prof.maximoNivelEstudio = "DOCTORADO";
    prof.puntosSalariales = 0.0;
    prof.estado = "ACTIVO";
    profesores.push_back(prof);

    GestorFactores gestorFactores(categorias, factores, producciones, profesores);
    double puntos = gestorFactores.calcularPuntosProfesor(1);

    EXPECT_NEAR(puntos, 570.0, 0.01);
    EXPECT_NEAR(profesores.front().puntosSalariales.value_or(0.0), 570.0, 0.01);
}

TEST_F(TestPuntosDoctoradoYNomina, PlantaConFactoresYProduccionReconocidos) {
    // 350 (Asociado) + 120 (Doctorado) + 15 (Artículo A1) = 485 puntos
    Profesor prof;
    prof.idProfesor = 2;
    prof.idPersona = 20;
    prof.tipoProfesor = TipoProfesor::PLANTA;
    prof.categoriaDocente = "ASOCIADO"; // 350 pts base
    prof.dedicacion = Dedicacion::TIEMPO_COMPLETO;
    prof.maximoNivelEstudio = "DOCTORADO";
    prof.puntosSalariales = 0.0;
    prof.estado = "ACTIVO";
    profesores.push_back(prof);

    FactorSalarial factorDoc;
    factorDoc.idFactor = 1;
    factorDoc.idProfesor = 2;
    factorDoc.tipoFactor = TipoFactor::TITULO_ACADEMICO;
    factorDoc.nombre = "TITULO_DOCTORADO";
    factorDoc.puntosReconocidos = 120.0;
    factorDoc.estado = "APROBADO";
    factores.push_back(factorDoc);

    ProduccionAcademica prod;
    prod.idProduccion = 1;
    prod.idProfesor = 2;
    prod.tipoProduccion = "ARTICULO_A1";
    prod.puntosReconocidosProfesor = 15.0;
    prod.estadoValidacion = "VALIDADO";
    producciones.push_back(prod);

    GestorFactores gestorFactores(categorias, factores, producciones, profesores);
    double puntos = gestorFactores.calcularPuntosProfesor(2);

    EXPECT_NEAR(puntos, 485.0, 0.01);
}

TEST_F(TestPuntosDoctoradoYNomina, OcasionalYCatedraticoNoRecibenPuntosDecreto1279) {
    // Verifica que docentes OCASIONALES o CATEDRÁTICOS no perciban puntos salariales (Decreto 1279 es solo Planta)
    Profesor profOcasional;
    profOcasional.idProfesor = 3;
    profOcasional.idPersona = 30;
    profOcasional.tipoProfesor = TipoProfesor::OCASIONAL;
    profOcasional.categoriaDocente = "ASISTENTE";
    profOcasional.maximoNivelEstudio = "DOCTORADO";
    profOcasional.puntosSalariales = 0.0;
    profOcasional.estado = "ACTIVO";
    profesores.push_back(profOcasional);

    GestorFactores gestorFactores(categorias, factores, producciones, profesores);
    double puntos = gestorFactores.calcularPuntosProfesor(3);

    EXPECT_NEAR(puntos, 0.0, 0.01);
}

TEST_F(TestPuntosDoctoradoYNomina, BonificacionPosgradoRegimenAcuerdo027) {
    // Bonificación de posgrado bajo Acuerdo 027:
    // Planta: 0 (se remunera con puntos salariales)
    // Ocasional Tiempo Completo con Doctorado: 90% del SMMLV ($1.750.905 * 0.90 = $1.575.814,50 -> $1.575.815)
    CalculadoraDeducciones calcDed(parametros);
    CalculadoraPrestaciones calcPres(calcDed);

    Profesor profPlanta;
    profPlanta.tipoProfesor = TipoProfesor::PLANTA;
    profPlanta.maximoNivelEstudio = "DOCTORADO";
    profPlanta.nivelPosgradoReconocido = "DOCTORADO";

    Profesor profOcasional;
    profOcasional.tipoProfesor = TipoProfesor::OCASIONAL;
    profOcasional.maximoNivelEstudio = "DOCTORADO";
    profOcasional.nivelPosgradoReconocido = "DOCTORADO";

    Contrato cPlanta;
    cPlanta.modalidadProfesor = "DOCENTE_PLANTA";
    cPlanta.dedicacion = Dedicacion::TIEMPO_COMPLETO;
    cPlanta.permiteBonificacionPosgrado = true;

    Contrato cOcasional;
    cOcasional.modalidadProfesor = "DOCENTE_OCASIONAL";
    cOcasional.dedicacion = Dedicacion::TIEMPO_COMPLETO;
    cOcasional.permiteBonificacionPosgrado = true;

    double smmlv = 1750905.0;
    double bonifPlanta = calcPres.calcularBonificacionPosgrado(profPlanta, smmlv, cPlanta, std::nullopt, true);
    double bonifOcasional = calcPres.calcularBonificacionPosgrado(profOcasional, smmlv, cOcasional, std::nullopt, true);

    EXPECT_NEAR(bonifPlanta, 0.0, 0.01);
    EXPECT_NEAR(bonifOcasional, std::round(smmlv * 0.90), 1.0);
}
