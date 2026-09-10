#include "gestor_contratos.h"
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

GestorContratos::GestorContratos(
    ListaEnlazada<Contrato>& contratos,
    ListaEnlazada<Profesor>& profesores,
    ListaEnlazada<Administrativo>& administrativos,
    ListaEnlazada<LiquidacionNomina>& liquidaciones
) : contratos(contratos),
    profesores(profesores),
    administrativos(administrativos),
    liquidaciones(liquidaciones) {}

int GestorContratos::siguienteId() {
    int maxId = 0;
    for (const auto& c : contratos) {
        if (c.idContrato.has_value() && *c.idContrato > maxId) {
            maxId = *c.idContrato;
        }
    }
    return maxId + 1;
}

Contrato* GestorContratos::buscar(int identificador) {
    for (auto& c : contratos) {
        if (c.idContrato.has_value() && *c.idContrato == identificador) {
            return &c;
        }
    }
    throw ErrorContrato("No existe el contrato con ID " + std::to_string(identificador));
}

std::string GestorContratos::tipo(const Contrato& c) {
    std::string v;
    if (c.modalidadProfesor.has_value() && !c.modalidadProfesor->empty()) {
        v = *c.modalidadProfesor;
    } else if (c.tipoContrato.has_value() && !c.tipoContrato->empty()) {
        v = *c.tipoContrato;
    }
    return a_mayusculas(v);
}

std::string GestorContratos::dedicacion(const Contrato& c) {
    if (c.dedicacion.has_value()) {
        return to_string(*c.dedicacion);
    }
    if (c.tipoDedicacion.has_value()) {
        return a_mayusculas(*c.tipoDedicacion);
    }
    return "";
}

double GestorContratos::horasSemanales(const Contrato& c) {
    if (c.horasSemanales.has_value()) return *c.horasSemanales;
    if (c.horasSemanalesAsignadas.has_value()) return *c.horasSemanalesAsignadas;
    return 0.0;
}

bool GestorContratos::esActivo(const std::optional<std::string>& estado) {
    if (!estado.has_value()) return false;
    return a_mayusculas(*estado) == "ACTIVO";
}

bool GestorContratos::esCatedraticoAdHonorem(const Contrato& c) {
    std::string t = tipo(c);
    std::string m = c.modalidadProfesor.has_value() ? a_mayusculas(*c.modalidadProfesor) : "";
    return (t == "CATEDRATICO_AD_HONOREM" ||
           (t == "CATEDRATICO" && ((c.esAdHonorem.has_value() && *c.esAdHonorem) || m == "CATEDRATICO_AD_HONOREM")));
}

bool GestorContratos::esAdministrativo(std::optional<int> idPersona) {
    if (!idPersona.has_value()) return false;
    for (const auto& a : administrativos) {
        if (a.idPersona.has_value() && *a.idPersona == *idPersona) {
            return true;
        }
    }
    return false;
}

bool GestorContratos::esJubilado(std::optional<int> idPersona, std::optional<bool> jubilado) {
    if (jubilado.has_value()) return *jubilado;
    if (!idPersona.has_value()) return false;
    for (const auto& p : profesores) {
        if (p.idPersona.has_value() && *p.idPersona == *idPersona) {
            if (p.estado.has_value()) {
                std::string est = a_mayusculas(*p.estado);
                if (est == "JUBILADO" || est == "PENSIONADO") return true;
            }
            break;
        }
    }
    return false;
}

double GestorContratos::horasActivas(std::optional<int> idPersona, const std::string& t) {
    double total = 0.0;
    for (const auto& item : contratos) {
        if (item.idPersona == idPersona && esActivo(item.estado)) {
            std::string itemTipo = tipo(item);
            if (t == "CATEDRATICO") {
                if (itemTipo == "CATEDRATICO" || itemTipo == "CATEDRATICO_AD_HONOREM" || itemTipo == "DOCENTE_CATEDRA") {
                    total += horasSemanales(item);
                }
            } else if (itemTipo == t) {
                total += horasSemanales(item);
            }
        }
    }
    return total;
}

int GestorContratos::duracionEnMeses(const Contrato& c) {
    if (c.duracionEnMeses.has_value()) {
        return *c.duracionEnMeses;
    }
    if (!c.fechaInicio.has_value() || !c.fechaFin.has_value() || c.fechaInicio->empty() || c.fechaFin->empty()) {
        throw ErrorContrato("La vinculacion ocasional requiere duracion o fechas de inicio y fin");
    }
    try {
        int y1 = std::stoi(c.fechaInicio->substr(0, 4));
        int m1 = std::stoi(c.fechaInicio->substr(5, 2));
        int d1 = std::stoi(c.fechaInicio->substr(8, 2));

        int y2 = std::stoi(c.fechaFin->substr(0, 4));
        int m2 = std::stoi(c.fechaFin->substr(5, 2));
        int d2 = std::stoi(c.fechaFin->substr(8, 2));

        int meses = (y2 - y1) * 12 + (m2 - m1);
        if (d2 >= d1) meses += 1;
        return meses;
    } catch (...) {
        throw ErrorContrato("Formato de fecha invalido en contrato");
    }
}

void GestorContratos::validarContrato(const Contrato& c, std::optional<bool> jubilado) {
    std::string t = tipo(c);
    std::string ded = dedicacion(c);
    double h = horasSemanales(c);

    if (h < 0) {
        throw ErrorContrato("Las horas semanales no pueden ser negativas");
    }
    if (c.fechaInicio.has_value() && c.fechaFin.has_value() && !c.fechaInicio->empty() && !c.fechaFin->empty()) {
        if (*c.fechaFin < *c.fechaInicio) {
            throw ErrorContrato("La fecha de terminacion no puede preceder a la fecha de inicio");
        }
    }

    bool esCatedra = (t == "CATEDRATICO" || t == "CATEDRATICO_AD_HONOREM" || t == "DOCENTE_CATEDRA");
    if (esCatedra) {
        double totalHoras = horasActivas(c.idPersona, "CATEDRATICO") + h;
        if (totalHoras > HORAS_MAXIMAS_CATEDRATICO) {
            throw ErrorContrato("Los catedraticos no pueden superar 18 horas semanales");
        }
    }

    if (esCatedraticoAdHonorem(c) && esAdministrativo(c.idPersona)) {
        double totalHoras = horasActivas(c.idPersona, "CATEDRATICO_AD_HONOREM") + h;
        if (totalHoras > HORAS_MAXIMAS_ADMINISTRATIVO_AD_HONOREM) {
            throw ErrorContrato("Los administrativos catedraticos ad-honorem no pueden superar 8 horas semanales");
        }
    }

    bool esOcasional = (t == "OCASIONAL" || t == "DOCENTE_OCASIONAL");
    if (esOcasional) {
        if (ded != "TIEMPO_COMPLETO" && ded != "MEDIO_TIEMPO") {
            throw ErrorContrato("Los profesores ocasionales solo pueden ser de tiempo completo o medio tiempo");
        }
        if (duracionEnMeses(c) >= 12) {
            throw ErrorContrato("La vinculacion ocasional debe durar menos de un ano");
        }
    }

    bool esPlanta = (t == "PLANTA" || t == "DOCENTE_PLANTA");
    if ((esOcasional || esPlanta) && esJubilado(c.idPersona, jubilado)) {
        throw ErrorContrato("No se pueden vincular docentes jubilados en modalidad ocasional o planta");
    }
}

Contrato& GestorContratos::crearContrato(Contrato c, std::optional<bool> jubilado) {
    if (!c.idContrato.has_value()) {
        c.idContrato = siguienteId();
    } else {
        for (const auto& item : contratos) {
            if (item.idContrato.has_value() && *item.idContrato == *c.idContrato) {
                throw ErrorContrato("Ya existe un contrato con ID " + std::to_string(*c.idContrato));
            }
        }
    }

    validarContrato(c, jubilado);
    contratos.push_back(std::move(c));
    return contratos.back();
}

Contrato* GestorContratos::buscarContratoVigente(int idPersona, const std::string& fecha) {
    std::string momento = fecha.empty() ? fecha_hoy() : fecha;
    for (auto& c : contratos) {
        if (c.idPersona.has_value() && *c.idPersona == idPersona && esActivo(c.estado)) {
            bool inicioOk = (!c.fechaInicio.has_value() || c.fechaInicio->empty() || *c.fechaInicio <= momento);
            bool finOk = (!c.fechaFin.has_value() || c.fechaFin->empty() || momento <= *c.fechaFin);
            if (inicioOk && finOk) {
                return &c;
            }
        }
    }
    return nullptr;
}

ListaEnlazada<Contrato> GestorContratos::listarContratosProfesor(int idPersona) const {
    ListaEnlazada<Contrato> res;
    for (const auto& c : contratos) {
        if (c.idPersona.has_value() && *c.idPersona == idPersona) {
            res.push_back(c);
        }
    }
    return res;
}

Contrato& GestorContratos::terminarContrato(int idContrato, const std::string& causal, const std::string& documento, const std::string& fecha) {
    Contrato* c = buscar(idContrato);
    if (causal.empty() || documento.empty()) {
        throw ErrorContrato("La causal y el documento de terminacion son obligatorios");
    }
    c->causalTerminacion = causal;
    c->documentoSoporteTerminacion = documento;
    c->fechaTerminacionEfectiva = fecha.empty() ? fecha_hoy() : fecha;
    c->estadoFinalContrato = "TERMINADO";
    c->estado = "INACTIVO";
    return *c;
}

Contrato& GestorContratos::desactivarContrato(int idContrato) {
    Contrato* c = buscar(idContrato);
    c->estado = "INACTIVO";
    return *c;
}

} // namespace pita
