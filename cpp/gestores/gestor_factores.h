#ifndef GESTOR_FACTORES_H
#define GESTOR_FACTORES_H

#include <string>
#include <stdexcept>
#include <optional>
#include "../dominio/lista_enlazada.h"
#include "../dominio/modelo_datos.h"

namespace pita {

class ErrorFactor : public std::runtime_error {
public:
    explicit ErrorFactor(const std::string& mensaje) : std::runtime_error(mensaje) {}
};

class GestorFactores {
public:
    ListaEnlazada<CategoriaDocente>& categorias;
    ListaEnlazada<FactorSalarial>& factores;
    ListaEnlazada<ProduccionAcademica>& producciones;
    ListaEnlazada<Profesor>& profesores;

    GestorFactores(
        ListaEnlazada<CategoriaDocente>& categorias,
        ListaEnlazada<FactorSalarial>& factores,
        ListaEnlazada<ProduccionAcademica>& producciones,
        ListaEnlazada<Profesor>& profesores
    );

    CategoriaDocente& crearCategoria(CategoriaDocente categoria);
    FactorSalarial& registrarFactor(FactorSalarial factor);
    FactorSalarial& aprobarFactor(int idFactor, double puntosAprobados);
    ProduccionAcademica& registrarProduccion(ProduccionAcademica produccion);
    ProduccionAcademica& reconocerPuntos(int idProduccion, double puntos);
    double calcularPuntosProfesor(int idProfesor, const std::string& fechaCorte = "");
    ListaEnlazada<FactorSalarial> consultarFactoresProfesor(int idProfesor) const;

    static double calcularFactorCoautoria(int numeroAutores);

private:
    void actualizarPuntosProfesor(std::optional<int> idProfesor);
    void validarProfesorExiste(int idProfesor, const std::string& contexto);
    void validarTipoFactor(const std::optional<TipoFactor>& tipo, const FactorSalarial& factor);
    void validarTipoProduccion(const std::optional<std::string>& tipo, const ProduccionAcademica& prod);
    void validarReconocimientoSimultaneo(ProduccionAcademica& prod);
    CategoriaDocente* categoriaVigente(const Profesor& prof, const std::string& fecha);
    static double puntosCategoria(const CategoriaDocente* cat, const Profesor& prof);
    static double puntosFactor(const FactorSalarial& f, const std::string& fecha);
    static double puntosProduccion(const ProduccionAcademica& prod, const std::string& fecha);

    int siguienteIdCategoria();
    int siguienteIdFactor();
    int siguienteIdProduccion();
};

} // namespace pita

#endif // GESTOR_FACTORES_H
