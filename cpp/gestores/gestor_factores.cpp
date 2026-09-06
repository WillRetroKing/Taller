#include "gestor_factores.h"
#include <ctime>
#include <iomanip>
#include <sstream>
#include <algorithm>

namespace pita {

static std::string fecha_hoy() {
    std::time_t t = std::time(nullptr);
    std::tm tm = *std::localtime(&t);
    std::ostringstream oss;
    oss << std::put_time(&tm, "%Y-%m-%d");
    return oss.str();
}

static std::string a_mayusculas(std::string s) {
    std::transform(s.begin(), s.end(), s.begin(), [](unsigned char c) { return std::toupper(c); });
    return s;
}

GestorFactores::GestorFactores(
    ListaEnlazada<CategoriaDocente>& categorias,
    ListaEnlazada<FactorSalarial>& factores,
    ListaEnlazada<ProduccionAcademica>& producciones,
    ListaEnlazada<Profesor>& profesores
) : categorias(categorias),
    factores(factores),
    producciones(producciones),
    profesores(profesores) {}

int GestorFactores::siguienteIdCategoria() {
    int maxId = 0;
    for (const auto& c : categorias) {
        if (c.idCategoria.has_value() && *c.idCategoria > maxId) {
            maxId = *c.idCategoria;
        }
    }
    return maxId + 1;
}

int GestorFactores::siguienteIdFactor() {
    int maxId = 0;
    for (const auto& f : factores) {
        if (f.idFactor.has_value() && *f.idFactor > maxId) {
            maxId = *f.idFactor;
        }
    }
    return maxId + 1;
}

int GestorFactores::siguienteIdProduccion() {
    int maxId = 0;
    for (const auto& p : producciones) {
        if (p.idProduccion.has_value() && *p.idProduccion > maxId) {
            maxId = *p.idProduccion;
        }
    }
    return maxId + 1;
}

double GestorFactores::calcularFactorCoautoria(int numeroAutores) {
    if (numeroAutores <= 0) {
        throw ErrorFactor("El numero de autores debe ser positivo");
    }
    if (numeroAutores <= 3) return 1.0;
    if (numeroAutores <= 5) return 0.5;
    return 2.0 / static_cast<double>(numeroAutores);
}

void GestorFactores::validarProfesorExiste(int idProfesor, const std::string& contexto) {
    for (const auto& p : profesores) {
        if (p.idProfesor.has_value() && *p.idProfesor == idProfesor) {
            return;
        }
    }
    throw ErrorFactor("No existe el profesor con ID " + std::to_string(idProfesor) + " para el " + contexto);
}

void GestorFactores::validarTipoFactor(const std::optional<TipoFactor>& tipo, const FactorSalarial& factor) {
    if (!tipo.has_value()) {
        throw ErrorFactor("El tipo de factor es obligatorio para registrar un factor salarial");
    }

    switch (*tipo) {
        case TipoFactor::TITULO_ACADEMICO:
            if (!factor.puntosReconocidos.has_value() && !factor.puntosAprobados.has_value()) {
                throw ErrorFactor("El factor de titulo academico requiere puntos reconocidos o aprobados");
            }
            break;
        case TipoFactor::CATEGORIA_DOCENTE:
            if (!factor.idProfesor.has_value()) {
                throw ErrorFactor("El factor de categoria docente requiere ID de profesor");
            }
            break;
        case TipoFactor::EXPERIENCIA:
            if (!factor.puntosSolicitados.has_value() && !factor.cantidad.has_value()) {
                throw ErrorFactor("El factor de experiencia requiere puntos o cantidad solicitados");
            }
            break;
        case TipoFactor::PRODUCTIVIDAD_ACADEMICA: {
            bool tieneProd = false;
            for (const auto& p : producciones) {
                if (p.idProfesor == factor.idProfesor) {
                    tieneProd = true;
                    break;
                }
            }
            if (!tieneProd) {
                throw ErrorFactor("El factor de productividad requiere producciones academicas registradas");
            }
            break;
        }
        case TipoFactor::GRUPO_INVESTIGACION:
            if (!factor.nombre.has_value() || factor.nombre->empty()) {
                throw ErrorFactor("El factor de grupo de investigacion requiere nombre");
            }
            break;
        case TipoFactor::SEMILLERO:
            if (!factor.idProfesor.has_value()) {
                throw ErrorFactor("El factor de semillero requiere ID de profesor");
            }
            break;
        default:
            break;
    }
}

void GestorFactores::validarTipoProduccion(const std::optional<std::string>& tipoOpt, const ProduccionAcademica& prod) {
    if (!tipoOpt.has_value() || tipoOpt->empty()) {
        throw ErrorFactor("El tipo de produccion es obligatorio");
    }

    std::string tipo = a_mayusculas(*tipoOpt);
    if (tipo == "ARTICULO" || tipo == "ARTICULO_CIENTIFICO") {
        if (!prod.titulo.has_value() || prod.titulo->empty()) {
            throw ErrorFactor("La produccion de articulo requiere titulo");
        }
        if (!prod.entidadPublicadora.has_value() || prod.entidadPublicadora->empty()) {
            throw ErrorFactor("La produccion de articulo requiere entidad publicadora");
        }
    } else if (tipo == "LIBRO" || tipo == "CAPITULO_LIBRO") {
        if (!prod.titulo.has_value() || prod.titulo->empty()) {
            throw ErrorFactor("La produccion de libro/capitulo requiere titulo");
        }
        if (!prod.identificadorProducto.has_value() || prod.identificadorProducto->empty()) {
            throw ErrorFactor("La produccion de libro requiere identificador (ISBN o similar)");
        }
    } else if (tipo == "INVENTO" || tipo == "MODELO_UTILIDAD") {
        if (!prod.titulo.has_value() || prod.titulo->empty()) {
            throw ErrorFactor("La produccion de invento requiere titulo");
        }
        if (!prod.registroDerechoAutor.has_value() || prod.registroDerechoAutor->empty()) {
            throw ErrorFactor("La produccion de invento requiere registro de derecho autor");
        }
    } else if (tipo == "PROYECTO_INVESTIGACION") {
        if (!prod.titulo.has_value() || prod.titulo->empty()) {
            throw ErrorFactor("El proyecto de investigacion requiere titulo");
        }
        if (!prod.entidadIndexadora.has_value() || prod.entidadIndexadora->empty()) {
            throw ErrorFactor("El proyecto requiere entidad indexadora");
        }
    }
}

void GestorFactores::validarReconocimientoSimultaneo(ProduccionAcademica& prod) {
    for (const auto& prodAnt : producciones) {
        if (prodAnt.idProfesor == prod.idProfesor &&
            prodAnt.idProduccion != prod.idProduccion &&
            prodAnt.estadoValidacion.has_value() &&
            a_mayusculas(*prodAnt.estadoValidacion) == "VALIDADO") {
            if (prodAnt.puntosReconocidosProfesor.has_value() && prodAnt.puntosReconocidos.has_value()) {
                prod.productoReclasificado = true;
                double diferencia = prod.puntosSolicitados.value_or(0.0) - *prodAnt.puntosReconocidosProfesor;
                if (diferencia > 0.0) {
                    prod.puntosAdicionalesReclasificacion = diferencia;
                }
                prod.yaReconocidoOtroConcepto = true;
            }
        }
    }
}

CategoriaDocente& GestorFactores::crearCategoria(CategoriaDocente cat) {
    if (!cat.idCategoria.has_value()) {
        cat.idCategoria = siguienteIdCategoria();
    } else {
        for (const auto& c : categorias) {
            if (c.idCategoria.has_value() && *c.idCategoria == *cat.idCategoria) {
                throw ErrorFactor("Ya existe una categoria con ID " + std::to_string(*cat.idCategoria));
            }
        }
    }

    if (cat.fechaFinVigencia.has_value() && cat.fechaInicioVigencia.has_value()) {
        if (*cat.fechaFinVigencia <= *cat.fechaInicioVigencia) {
            throw ErrorFactor("La vigencia de la categoria es invalida");
        }
    }

    if (!cat.estado.has_value() || cat.estado->empty()) {
        cat.estado = "ACTIVO";
    }

    categorias.push_back(std::move(cat));
    return categorias.back();
}

FactorSalarial& GestorFactores::registrarFactor(FactorSalarial factor) {
    if (factor.idProfesor.has_value()) {
        validarProfesorExiste(*factor.idProfesor, "factor salarial");
    } else {
        throw ErrorFactor("El factor salarial requiere un profesor");
    }

    validarTipoFactor(factor.tipoFactor, factor);

    if (!factor.idFactor.has_value()) {
        factor.idFactor = siguienteIdFactor();
    } else {
        for (const auto& f : factores) {
            if (f.idFactor.has_value() && *f.idFactor == *factor.idFactor) {
                throw ErrorFactor("Ya existe un factor con ID " + std::to_string(*factor.idFactor));
            }
        }
    }

    if (factor.puntosSolicitados.has_value() && *factor.puntosSolicitados < 0) {
        throw ErrorFactor("Los puntos solicitados no pueden ser negativos");
    }

    if (!factor.estado.has_value() || factor.estado->empty()) {
        factor.estado = "SOLICITADO";
    }

    factores.push_back(std::move(factor));
    actualizarPuntosProfesor(factores.back().idProfesor);
    return factores.back();
}

FactorSalarial& GestorFactores::aprobarFactor(int idFactor, double puntosAprobados) {
    FactorSalarial* factor = nullptr;
    for (auto& f : factores) {
        if (f.idFactor.has_value() && *f.idFactor == idFactor) {
            factor = &f;
            break;
        }
    }
    if (!factor) {
        throw ErrorFactor("No existe el factor con ID " + std::to_string(idFactor));
    }

    if (puntosAprobados < 0 || (factor->puntosSolicitados.has_value() && puntosAprobados > *factor->puntosSolicitados)) {
        throw ErrorFactor("Los puntos aprobados no son validos");
    }

    factor->puntosAprobados = puntosAprobados;
    factor->puntosReconocidos = puntosAprobados;
    factor->estado = "APROBADO";
    if (!factor->fechaReconocimiento.has_value() || factor->fechaReconocimiento->empty()) {
        factor->fechaReconocimiento = fecha_hoy();
    }

    actualizarPuntosProfesor(factor->idProfesor);
    return *factor;
}

ProduccionAcademica& GestorFactores::registrarProduccion(ProduccionAcademica prod) {
    if (prod.idProfesor.has_value()) {
        validarProfesorExiste(*prod.idProfesor, "produccion academica");
    } else {
        throw ErrorFactor("La produccion academica requiere un profesor");
    }

    validarTipoProduccion(prod.tipoProduccion, prod);

    if (prod.identificadorProducto.has_value() && !prod.identificadorProducto->empty()) {
        for (const auto& p : producciones) {
            if (p.identificadorProducto == prod.identificadorProducto) {
                throw ErrorFactor("El producto academico ya fue registrado");
            }
        }
    }

    validarReconocimientoSimultaneo(prod);

    if (!prod.idProduccion.has_value()) {
        prod.idProduccion = siguienteIdProduccion();
    } else {
        for (const auto& p : producciones) {
            if (p.idProduccion.has_value() && *p.idProduccion == *prod.idProduccion) {
                throw ErrorFactor("Ya existe una produccion con ID " + std::to_string(*prod.idProduccion));
            }
        }
    }

    prod.factorCoautoria = calcularFactorCoautoria(prod.numeroAutores.value_or(1));
    if (!prod.estadoValidacion.has_value() || prod.estadoValidacion->empty()) {
        prod.estadoValidacion = "PENDIENTE";
    }

    producciones.push_back(std::move(prod));
    actualizarPuntosProfesor(producciones.back().idProfesor);
    return producciones.back();
}

ProduccionAcademica& GestorFactores::reconocerPuntos(int idProduccion, double puntos) {
    ProduccionAcademica* prod = nullptr;
    for (auto& p : producciones) {
        if (p.idProduccion.has_value() && *p.idProduccion == idProduccion) {
            prod = &p;
            break;
        }
    }
    if (!prod) {
        throw ErrorFactor("No existe la produccion con ID " + std::to_string(idProduccion));
    }

    if (puntos < 0) {
        throw ErrorFactor("Los puntos reconocidos no pueden ser negativos");
    }

    validarReconocimientoSimultaneo(*prod);

    prod->puntosReconocidos = puntos;
    if (prod->numeroAutores.has_value() && *prod->numeroAutores > 0) {
        prod->factorCoautoria = calcularFactorCoautoria(*prod->numeroAutores);
    }
    prod->puntosReconocidosProfesor = puntos * prod->factorCoautoria.value_or(1.0);
    prod->estadoValidacion = "VALIDADO";
    if (!prod->fechaReconocimiento.has_value() || prod->fechaReconocimiento->empty()) {
        prod->fechaReconocimiento = fecha_hoy();
    }

    actualizarPuntosProfesor(prod->idProfesor);
    return *prod;
}

CategoriaDocente* GestorFactores::categoriaVigente(const Profesor& prof, const std::string& fecha) {
    std::string catDoc = prof.categoriaDocente.has_value() ? a_mayusculas(*prof.categoriaDocente) : "";
    std::string catRec = prof.categoriaReconocida.has_value() ? a_mayusculas(*prof.categoriaReconocida) : "";

    CategoriaDocente* mejor = nullptr;
    for (auto& c : categorias) {
        std::string est = c.estado.has_value() ? a_mayusculas(*c.estado) : "ACTIVO";
        if (est != "ACTIVO") continue;

        if (c.fechaInicioVigencia.has_value() && *c.fechaInicioVigencia > fecha) continue;
        if (c.fechaFinVigencia.has_value() && fecha > *c.fechaFinVigencia) continue;

        std::string cCod = c.codigo.has_value() ? to_string(*c.codigo) : "";
        bool coincide = (c.idCategoria == prof.idCategoriaDocente || cCod == catDoc || cCod == catRec);
        if (coincide) {
            if (!mejor || (c.fechaInicioVigencia.value_or("") > mejor->fechaInicioVigencia.value_or(""))) {
                mejor = &c;
            }
        }
    }
    return mejor;
}

double GestorFactores::puntosCategoria(const CategoriaDocente* cat, const Profesor& prof) {
    if (cat) {
        if (cat->puntosCategoria.has_value()) return *cat->puntosCategoria;
        if (cat->puntosBase.has_value()) return *cat->puntosBase;
        return 0.0;
    }
    std::string cod = prof.categoriaReconocida.value_or(prof.categoriaDocente.value_or(""));
    cod = a_mayusculas(cod);
    if (cod == "AUXILIAR") return 37.0;
    if (cod == "ASISTENTE") return 58.0;
    if (cod == "ASOCIADO") return 74.0;
    if (cod == "TITULAR") return 96.0;
    return 0.0;
}

double GestorFactores::puntosFactor(const FactorSalarial& f, const std::string& fecha) {
    std::string est = f.estado.has_value() ? a_mayusculas(*f.estado) : "";
    if (est != "APROBADO") return 0.0;
    if (f.tipoFactor.has_value() && *f.tipoFactor == TipoFactor::CATEGORIA_DOCENTE) return 0.0;

    std::string inicio;
    if (f.fechaEfectoSalarial.has_value() && !f.fechaEfectoSalarial->empty()) inicio = *f.fechaEfectoSalarial;
    else if (f.fechaReconocimiento.has_value() && !f.fechaReconocimiento->empty()) inicio = *f.fechaReconocimiento;
    else if (f.vigenciaDesde.has_value() && !f.vigenciaDesde->empty()) inicio = *f.vigenciaDesde;

    if (!inicio.empty() && inicio > fecha) return 0.0;
    if (f.vigenciaHasta.has_value() && !f.vigenciaHasta->empty() && fecha > *f.vigenciaHasta) return 0.0;

    if (f.puntosReconocidos.has_value()) return *f.puntosReconocidos;
    if (f.puntosAprobados.has_value()) return *f.puntosAprobados;
    return 0.0;
}

double GestorFactores::puntosProduccion(const ProduccionAcademica& p, const std::string& fecha) {
    std::string est = p.estadoValidacion.has_value() ? a_mayusculas(*p.estadoValidacion) : "";
    if (est != "VALIDADO") return 0.0;

    std::string fechaEfecto = p.fechaActoReconocimiento.value_or(p.fechaReconocimiento.value_or(""));
    if (!fechaEfecto.empty() && fechaEfecto > fecha) return 0.0;

    return p.puntosReconocidosProfesor.value_or(0.0);
}

double GestorFactores::calcularPuntosProfesor(int idProfesor, const std::string& fechaCorte) {
    Profesor* prof = nullptr;
    for (auto& p : profesores) {
        if (p.idProfesor.has_value() && *p.idProfesor == idProfesor) {
            prof = &p;
            break;
        }
    }
    if (!prof) {
        throw ErrorFactor("No existe el profesor con ID " + std::to_string(idProfesor));
    }

    std::string fecha = fechaCorte.empty() ? fecha_hoy() : fechaCorte;
    CategoriaDocente* cat = categoriaVigente(*prof, fecha);
    double ptsCat = puntosCategoria(cat, *prof);

    double ptsFact = 0.0;
    for (const auto& f : factores) {
        if (f.idProfesor.has_value() && *f.idProfesor == idProfesor) {
            ptsFact += puntosFactor(f, fecha);
        }
    }

    double ptsProd = 0.0;
    for (const auto& p : producciones) {
        if (p.idProfesor.has_value() && *p.idProfesor == idProfesor) {
            ptsProd += puntosProduccion(p, fecha);
        }
    }

    double total = ptsCat + ptsFact + ptsProd;
    prof->puntosSalariales = total;
    return total;
}

void GestorFactores::actualizarPuntosProfesor(std::optional<int> idProfesor) {
    if (idProfesor.has_value()) {
        for (const auto& p : profesores) {
            if (p.idProfesor.has_value() && *p.idProfesor == *idProfesor) {
                calcularPuntosProfesor(*idProfesor);
                break;
            }
        }
    }
}

ListaEnlazada<FactorSalarial> GestorFactores::consultarFactoresProfesor(int idProfesor) const {
    ListaEnlazada<FactorSalarial> res;
    for (const auto& f : factores) {
        if (f.idProfesor.has_value() && *f.idProfesor == idProfesor) {
            res.push_back(f);
        }
    }
    return res;
}

} // namespace pita
