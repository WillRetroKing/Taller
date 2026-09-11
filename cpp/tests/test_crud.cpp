#include <gtest/gtest.h>
#include "../dominio/modelo_datos.h"
#include "../dominio/lista_enlazada.h"
#include "../persistencia/gestor_crud.h"

using namespace pita;

TEST(TestCRUD, CrudYCodigoUnico) {
    ListaEnlazada<Facultad> registros;

    GestorCRUD<Facultad> gestor(
        registros,
        [](const Facultad& f) { return f.idFacultad; },
        [](Facultad& f, int id) { f.idFacultad = id; },
        [](const Facultad& f) { return f.codigoFacultad; },
        [](const Facultad& f) { return f.estado.value_or("ACTIVO"); },
        [](Facultad& f, const std::string& st) { f.estado = st; }
    );

    // 1. Crear registro
    Facultad f1;
    f1.codigoFacultad = "F-01";
    f1.nombre = "Ingenieria";
    Facultad& creada = gestor.crear(f1);
    ASSERT_TRUE(creada.idFacultad.has_value());
    int idCreado = *creada.idFacultad;
    EXPECT_EQ(idCreado, 1);

    // 2. Rechazar código duplicado
    Facultad f2;
    f2.codigoFacultad = "F-01";
    f2.nombre = "Duplicada";
    EXPECT_THROW(gestor.crear(f2), ErrorCRUD);

    // 3. Modificar datos
    Facultad fActualizada = creada;
    fActualizada.nombre = "Ciencias";
    gestor.actualizar(idCreado, fActualizada);
    EXPECT_EQ(gestor.buscarPorId(idCreado)->nombre.value_or(""), "Ciencias");

    // 4. Desactivar y listar sólo activos
    gestor.desactivar(idCreado);
    auto activos = gestor.listar(false);
    EXPECT_EQ(activos.size(), 0u);

    // 5. Reactivar
    gestor.reactivar(idCreado);
    auto activosReactivados = gestor.listar(false);
    EXPECT_EQ(activosReactivados.size(), 1u);
    EXPECT_EQ(gestor.buscarPorId(idCreado)->nombre.value_or(""), "Ciencias");
}
