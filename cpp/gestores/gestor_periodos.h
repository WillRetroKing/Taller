#ifndef GESTOR_PERIODOS_H
#define GESTOR_PERIODOS_H

#include <string>
#include <stdexcept>
#include <optional>
#include "../dominio/lista_enlazada.h"
#include "../dominio/modelo_datos.h"

namespace pita {

class ErrorPeriodo : public std::runtime_error {
public:
    explicit ErrorPeriodo(const std::string& mensaje) : std::runtime_error(mensaje) {}
};

class GestorPeriodosAcademicos {
public:
    ListaEnlazada<PeriodoAcademico>& periodos;
    ListaEnlazada<OfertaCurso>& ofertas;

    GestorPeriodosAcademicos(
        ListaEnlazada<PeriodoAcademico>& periodos,
        ListaEnlazada<OfertaCurso>& ofertas
    );

    PeriodoAcademico& crearPeriodo(PeriodoAcademico periodo);
    PeriodoAcademico& cerrarPeriodo(int idPeriodo);
    PeriodoAcademico& abrirPeriodo(int idPeriodo);
    PeriodoAcademico* consultarPeriodo(int idPeriodo);
    ListaEnlazada<PeriodoAcademico> listarPeriodos(bool incluirCerrados = true) const;
    ListaEnlazada<PeriodoAcademico> consultarPeriodos(const std::string& estado = "") const;
    PeriodoAcademico& modificarPeriodo(int idPeriodo, const PeriodoAcademico& datosActualizados);

    ListaEnlazada<OfertaCurso> consultarOfertasPeriodo(int idPeriodo);
    OfertaCurso& modificarOferta(int idOferta, int idPeriodo, const OfertaCurso& cambios);

    static void validarFechas(const PeriodoAcademico& periodo);

private:
    int siguienteId();
    PeriodoAcademico* buscar(int idPeriodo);
};

} // namespace pita

#endif // GESTOR_PERIODOS_H
