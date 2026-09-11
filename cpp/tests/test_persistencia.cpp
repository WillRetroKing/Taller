#include <gtest/gtest.h>
#include <filesystem>
#include "../dominio/modelo_datos.h"
#include "../dominio/lista_enlazada.h"
#include "../persistencia/gestor_persistencia.h"

namespace fs = std::filesystem;
using namespace pita;

class TestPersistencia : public ::testing::Test {
protected:
    fs::path tempDir;

    void SetUp() override {
        tempDir = fs::temp_directory_path() / ("pita_test_persistencia_" + std::to_string(std::chrono::system_clock::now().time_since_epoch().count()));
        fs::create_directories(tempDir);
    }

    void TearDown() override {
        std::error_code ec;
        fs::remove_all(tempDir, ec);
    }
};

TEST_F(TestPersistencia, GuardarCargarYReferencia) {
    GestorPersistencia gestor(tempDir.string());

    DatosSistema datos;
    Facultad fac;
    fac.idFacultad = 1;
    fac.codigoFacultad = "F-ING";
    fac.nombre = "Ingenieria";
    fac.estado = "ACTIVO";
    datos.facultades.push_back(fac);

    ProgramaAcademico prog;
    prog.idPrograma = 2;
    prog.codigoPrograma = "P-SIS";
    prog.nombre = "Ingenieria de Sistemas";
    prog.idFacultad = 1;
    prog.fechaCreacion = "2026-09-03";
    prog.estado = "ACTIVO";
    datos.programas.push_back(prog);

    gestor.guardarTodosLosDatos(datos);

    DatosSistema cargados = gestor.cargarTodosLosDatos();
    ASSERT_EQ(cargados.programas.size(), 1u);
    EXPECT_EQ(cargados.programas.front().fechaCreacion.value_or(""), "2026-09-03");

    // Violación de integridad referencial: Programa con idFacultad inexistente (99)
    ProgramaAcademico progInvalido;
    progInvalido.idPrograma = 3;
    progInvalido.codigoPrograma = "P-INV";
    progInvalido.nombre = "Invalido";
    progInvalido.idFacultad = 99; // NO existe
    progInvalido.estado = "ACTIVO";
    datos.programas.push_back(progInvalido);

    gestor.guardarTodosLosDatos(datos);

    EXPECT_THROW(gestor.cargarTodosLosDatos(), std::runtime_error);
}

TEST_F(TestPersistencia, FlujoIntegralGuardarYCargarRelaciones) {
    GestorPersistencia gestor(tempDir.string());

    DatosSistema datos;
    Facultad fac;
    fac.idFacultad = 1;
    fac.codigoFacultad = "F-01";
    fac.nombre = "Ingenieria";
    fac.estado = "ACTIVO";
    datos.facultades.push_back(fac);

    ProgramaAcademico prog;
    prog.idPrograma = 1;
    prog.codigoPrograma = "P-01";
    prog.nombre = "Sistemas";
    prog.idFacultad = 1;
    prog.estado = "ACTIVO";
    datos.programas.push_back(prog);

    Curso cur;
    cur.idCurso = 1;
    cur.codigoCurso = "CUR-01";
    cur.nombre = "Algoritmos";
    cur.numeroCreditos = 3;
    cur.estado = "ACTIVO";
    datos.cursos.push_back(cur);

    PeriodoAcademico per;
    per.idPeriodo = 1;
    per.codigo = "2026-1";
    per.estado = "ACTIVO";
    datos.periodosAcademicos.push_back(per);

    OfertaCurso ofr;
    ofr.idOfertaCurso = 1;
    ofr.idCurso = 1;
    ofr.idPeriodo = 1;
    ofr.grupo = "A";
    ofr.cupoMaximo = 25;
    ofr.cupoDisponible = 20;
    ofr.estado = "ACTIVO";
    datos.ofertasCurso.push_back(ofr);

    gestor.guardarTodosLosDatos(datos);

    DatosSistema cargados = gestor.cargarTodosLosDatos();
    EXPECT_EQ(cargados.facultades.size(), 1u);
    EXPECT_EQ(cargados.programas.size(), 1u);
    EXPECT_EQ(cargados.cursos.size(), 1u);
    EXPECT_EQ(cargados.periodosAcademicos.size(), 1u);
    EXPECT_EQ(cargados.ofertasCurso.size(), 1u);

    EXPECT_EQ(*cargados.programas.front().idFacultad, *cargados.facultades.front().idFacultad);
    EXPECT_EQ(*cargados.ofertasCurso.front().idCurso, *cargados.cursos.front().idCurso);
    EXPECT_EQ(*cargados.ofertasCurso.front().idPeriodo, *cargados.periodosAcademicos.front().idPeriodo);
}

TEST_F(TestPersistencia, AislamientoFisicoEntreCarpetas) {
    fs::path dirUpc = tempDir / "upc";
    fs::path dirUnal = tempDir / "unal";
    fs::create_directories(dirUpc);
    fs::create_directories(dirUnal);

    GestorPersistencia gpUpc(dirUpc.string());
    GestorPersistencia gpUnal(dirUnal.string());

    DatosSistema datosUpc;
    Facultad fUpc;
    fUpc.idFacultad = 1;
    fUpc.codigoFacultad = "FIT";
    fUpc.nombre = "Facultad Ingenieria UPC";
    datosUpc.facultades.push_back(fUpc);
    gpUpc.guardarTodosLosDatos(datosUpc);

    DatosSistema datosUnal;
    Facultad fUnal;
    fUnal.idFacultad = 1;
    fUnal.codigoFacultad = "FING";
    fUnal.nombre = "Facultad Minas UNAL";
    datosUnal.facultades.push_back(fUnal);
    gpUnal.guardarTodosLosDatos(datosUnal);

    // Cargar independientemente y verificar que no se sobreescriban
    DatosSistema cargadosUpc = gpUpc.cargarTodosLosDatos();
    DatosSistema cargadosUnal = gpUnal.cargarTodosLosDatos();

    EXPECT_EQ(cargadosUpc.facultades.front().codigoFacultad.value_or(""), "FIT");
    EXPECT_EQ(cargadosUnal.facultades.front().codigoFacultad.value_or(""), "FING");
}
