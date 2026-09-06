#include "gestor_periodos.h"
#include <algorithm>

namespace pita {

static std::string a_mayusculas(std::string s) {
    std::transform(s.begin(), s.end(), s.begin(), [](unsigned char c) { return std::toupper(c); });
    return s;
}

GestorPeriodosAcademicos::GestorPeriodosAcademicos(
    ListaEnlazada<PeriodoAcademico>& periodos,
    ListaEnlazada<OfertaCurso>& ofertas
) : periodos(periodos),
    ofertas(ofertas) {}

int GestorPeriodosAcademicos::siguienteId() {
    int maxId = 0;
    for (const auto& p : periodos) {
        if (p.idPeriodo.has_value() && *p.idPeriodo > maxId) {
            maxId = *p.idPeriodo;
        }
    }
    return maxId + 1;
}

PeriodoAcademico* GestorPeriodosAcademicos::buscar(int idPeriodo) {
    for (auto& p : periodos) {
        if (p.idPeriodo.has_value() && *p.idPeriodo == idPeriodo) {
            return &p;
        }
    }
    throw ErrorPeriodo("No existe el periodo con ID " + std::to_string(idPeriodo));
}

void GestorPeriodosAcademicos::validarFechas(const PeriodoAcademico& p) {
    if (p.fechaInicio.has_value() && p.fechaFin.has_value() && !p.fechaInicio->empty() && !p.fechaFin->empty()) {
        if (*p.fechaFin < *p.fechaInicio) {
            throw ErrorPeriodo("La fecha final no puede preceder a la fecha inicial");
        }
    }
    if (p.fechaInicioMatricula.has_value() && p.fechaFinMatricula.has_value() && !p.fechaInicioMatricula->empty() && !p.fechaFinMatricula->empty()) {
        if (*p.fechaFinMatricula < *p.fechaInicioMatricula) {
            throw ErrorPeriodo("La ventana de matricula tiene fechas invalidas");
        }
    }
    if (p.fechaLimiteCancelacion.has_value() && p.fechaFin.has_value() && !p.fechaLimiteCancelacion->empty() && !p.fechaFin->empty()) {
        if (*p.fechaLimiteCancelacion > *p.fechaFin) {
            throw ErrorPeriodo("La fecha limite de cancelacion no puede superar el fin del periodo");
        }
    }
}

PeriodoAcademico& GestorPeriodosAcademicos::crearPeriodo(PeriodoAcademico periodo) {
    validarFechas(periodo);
    if (!periodo.idPeriodo.has_value()) {
        periodo.idPeriodo = siguienteId();
    } else {
        for (const auto& item : periodos) {
            if (item.idPeriodo.has_value() && *item.idPeriodo == *periodo.idPeriodo) {
                throw ErrorPeriodo("Ya existe el periodo " + std::to_string(*periodo.idPeriodo));
            }
        }
    }

    if (!periodo.estado.has_value() || periodo.estado->empty()) {
        periodo.estado = "ABIERTO";
    }

    periodos.push_back(std::move(periodo));
    return periodos.back();
}

PeriodoAcademico& GestorPeriodosAcademicos::cerrarPeriodo(int idPeriodo) {
    PeriodoAcademico* p = buscar(idPeriodo);
    p->estado = "CERRADO";
    return *p;
}

PeriodoAcademico& GestorPeriodosAcademicos::abrirPeriodo(int idPeriodo) {
    PeriodoAcademico* p = buscar(idPeriodo);
    if (p->estado.has_value() && a_mayusculas(*p->estado) == "CERRADO") {
        throw ErrorPeriodo("No se puede abrir un periodo cerrado");
    }
    p->estado = "ABIERTO";
    return *p;
}

PeriodoAcademico* GestorPeriodosAcademicos::consultarPeriodo(int idPeriodo) {
    return buscar(idPeriodo);
}

ListaEnlazada<PeriodoAcademico> GestorPeriodosAcademicos::listarPeriodos(bool incluirCerrados) const {
    if (incluirCerrados) return periodos;
    ListaEnlazada<PeriodoAcademico> res;
    for (const auto& p : periodos) {
        if (!p.estado.has_value() || a_mayusculas(*p.estado) != "CERRADO") {
            res.push_back(p);
        }
    }
    return res;
}

ListaEnlazada<PeriodoAcademico> GestorPeriodosAcademicos::consultarPeriodos(const std::string& estado) const {
    if (estado.empty()) return periodos;
    std::string estBuscado = a_mayusculas(estado);
    ListaEnlazada<PeriodoAcademico> res;
    for (const auto& p : periodos) {
        if (p.estado.has_value() && a_mayusculas(*p.estado) == estBuscado) {
            res.push_back(p);
        }
    }
    return res;
}

PeriodoAcademico& GestorPeriodosAcademicos::modificarPeriodo(int idPeriodo, const PeriodoAcademico& datosActualizados) {
    PeriodoAcademico* actual = buscar(idPeriodo);
    validarFechas(datosActualizados);
    PeriodoAcademico copia = datosActualizados;
    copia.idPeriodo = actual->idPeriodo;
    *actual = copia;
    return *actual;
}

ListaEnlazada<OfertaCurso> GestorPeriodosAcademicos::consultarOfertasPeriodo(int idPeriodo) {
    buscar(idPeriodo);
    ListaEnlazada<OfertaCurso> res;
    for (const auto& o : ofertas) {
        if (o.idPeriodo.has_value() && *o.idPeriodo == idPeriodo) {
            res.push_back(o);
        }
    }
    return res;
}

OfertaCurso& GestorPeriodosAcademicos::modificarOferta(int idOferta, int idPeriodo, const OfertaCurso& cambios) {
    OfertaCurso* oferta = nullptr;
    for (auto& o : ofertas) {
        if (o.idOfertaCurso.has_value() && *o.idOfertaCurso == idOferta) {
            oferta = &o;
            break;
        }
    }
    if (!oferta) {
        throw ErrorPeriodo("No existe la oferta con ID " + std::to_string(idOferta));
    }
    if (!oferta->idPeriodo.has_value() || *oferta->idPeriodo != idPeriodo) {
        throw ErrorPeriodo("La oferta no pertenece a ese periodo");
    }

    if (cambios.cupoMaximo.has_value() && *cambios.cupoMaximo < 0) {
        throw ErrorPeriodo("El cupo maximo no puede ser negativo");
    }
    if (cambios.cupoDisponible.has_value() && *cambios.cupoDisponible < 0) {
        throw ErrorPeriodo("El cupo disponible no puede ser negativo");
    }
    if (cambios.cupoMaximo.has_value() && cambios.cupoDisponible.has_value() &&
        *cambios.cupoDisponible > *cambios.cupoMaximo) {
        throw ErrorPeriodo("El cupo disponible no puede superar el cupo maximo");
    }

    // Actualizar campos preservando IDs
    if (cambios.grupo.has_value()) oferta->grupo = cambios.grupo;
    if (cambios.cupoMaximo.has_value()) oferta->cupoMaximo = cambios.cupoMaximo;
    if (cambios.cupoDisponible.has_value()) oferta->cupoDisponible = cambios.cupoDisponible;
    if (cambios.modalidad.has_value()) oferta->modalidad = cambios.modalidad;
    if (cambios.aula.has_value()) oferta->aula = cambios.aula;
    if (cambios.sede.has_value()) oferta->sede = cambios.sede;
    if (cambios.fechaInicio.has_value()) oferta->fechaInicio = cambios.fechaInicio;
    if (cambios.fechaFin.has_value()) oferta->fechaFin = cambios.fechaFin;
    if (cambios.estado.has_value()) oferta->estado = cambios.estado;

    return *oferta;
}

} // namespace pita
