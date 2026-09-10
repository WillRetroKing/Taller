#include "calculadora_deducciones.h"
#include <ctime>
#include <iomanip>
#include <sstream>
#include <algorithm>
#include <cmath>

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

CalculadoraDeducciones::CalculadoraDeducciones(ListaEnlazada<ParametroNormativo>& parametros)
    : parametros(parametros) {}

double CalculadoraDeducciones::redondear(double valor) {
    return std::round(valor * 100.0) / 100.0;
}

double CalculadoraDeducciones::redondearPila(double valor) {
    if (valor < 100.0) {
        return redondear(valor);
    }
    return std::round(valor / 100.0) * 100.0;
}

std::optional<double> CalculadoraDeducciones::obtenerParametroDecimal(const std::string& codigo, const std::string& fecha) {
    std::string fechaConsulta = fecha.empty() ? fecha_hoy() : fecha;
    std::string codBuscado = a_mayusculas(codigo);

    for (const auto& p : parametros) {
        std::string pCod = p.codigo.has_value() ? to_string(*p.codigo) : "";
        if (pCod == codBuscado) {
            std::string est = p.estado.has_value() ? a_mayusculas(*p.estado) : "ACTIVO";
            if (est == "ACTIVO") {
                bool fIniOk = (!p.fechaInicioVigencia.has_value() || p.fechaInicioVigencia->empty() || *p.fechaInicioVigencia <= fechaConsulta);
                bool fFinOk = (!p.fechaFinVigencia.has_value() || p.fechaFinVigencia->empty() || fechaConsulta <= *p.fechaFinVigencia);
                if (fIniOk && fFinOk && p.valor.has_value() && !p.valor->empty()) {
                    try {
                        return std::stod(*p.valor);
                    } catch (...) {
                        return std::nullopt;
                    }
                }
            }
        }
    }
    return std::nullopt;
}

double CalculadoraDeducciones::obtenerPorcentaje(
    const std::string& codigo,
    double defecto,
    const std::string& fecha,
    std::map<std::string, std::string>* codigosUtilizados
) {
    auto val = obtenerParametroDecimal(codigo, fecha);
    if (codigosUtilizados) {
        (*codigosUtilizados)[codigo] = val.has_value() ? std::to_string(*val) : std::to_string(defecto);
    }
    return val.value_or(defecto);
}

double CalculadoraDeducciones::calcularDescuentoSalud(double ibc, const std::string& fecha, std::map<std::string, std::string>* codigosUtilizados) {
    double pct = obtenerPorcentaje("PORCENTAJE_SALUD_TRABAJADOR", 0.04, fecha, codigosUtilizados);
    return redondear(ibc * pct);
}

double CalculadoraDeducciones::calcularDescuentoPension(double ibc, const std::string& fecha, std::map<std::string, std::string>* codigosUtilizados) {
    double pct = obtenerPorcentaje("PORCENTAJE_PENSION_TRABAJADOR", 0.04, fecha, codigosUtilizados);
    return redondear(ibc * pct);
}

double CalculadoraDeducciones::calcularFondoSolidaridad(double ibc, double salarioMinimo, const std::string& fecha, std::map<std::string, std::string>* codigosUtilizados) {
    if (ibc >= 4.0 * salarioMinimo) {
        double pct = obtenerPorcentaje("PORCENTAJE_FONDO_SOLIDARIDAD", 0.0, fecha, codigosUtilizados);
        return redondearPila(ibc * pct);
    }
    return 0.0;
}

double CalculadoraDeducciones::calcularRetencionFuente(double ibc, const std::string& fecha, std::map<std::string, std::string>* codigosUtilizados) {
    if (ibc <= 0.0) {
        return 0.0;
    }

    auto valFijo = obtenerParametroDecimal("RETENCION_FUENTE_SALARIO", fecha);
    if (valFijo.has_value() && *valFijo > 0.0) {
        if (codigosUtilizados) {
            (*codigosUtilizados)["RETENCION_FUENTE_SALARIO"] = std::to_string(*valFijo);
        }
        return redondear(*valFijo);
    }

    double baseMinima = obtenerParametroDecimal("BASE_MINIMA_RETENCION_FUENTE", fecha).value_or(4500000.0);
    if (ibc < baseMinima) {
        return 0.0;
    }

    double pct = obtenerPorcentaje("PORCENTAJE_RETENCION_FUENTE", 0.0, fecha, codigosUtilizados);
    if (pct <= 0.0) {
        return 0.0;
    }
    return redondear(ibc * pct);
}

double CalculadoraDeducciones::calcularDescuentoEstampilla(double salarioBase, const std::string& fecha, std::map<std::string, std::string>* codigosUtilizados) {
    double pct = obtenerPorcentaje("PORCENTAJE_ESTAMPILLA", 0.002, fecha, codigosUtilizados);
    if (pct <= 0.0) return 0.0;
    return redondear(salarioBase * pct);
}

double CalculadoraDeducciones::calcularAporteSaludPatronal(double ibc, double salarioMinimo, const std::string& fecha, std::map<std::string, std::string>* codigosUtilizados, bool exonerado) {
    // Según Art. 114-1 Parágrafo 2 E.T., las entidades de derecho público (e.g. UPC)
    // no son beneficiarias de la exoneración. Por defecto exonerado = false.
    if (exonerado && ibc < 10.0 * salarioMinimo) {
        return 0.0;
    }
    double pct = obtenerPorcentaje("PORCENTAJE_SALUD_EMPLEADOR", 0.085, fecha, codigosUtilizados);
    return redondear(ibc * pct);
}

double CalculadoraDeducciones::calcularAportePensionPatronal(double ibc, const std::string& fecha, std::map<std::string, std::string>* codigosUtilizados) {
    double pct = obtenerPorcentaje("PORCENTAJE_PENSION_EMPLEADOR", 0.12, fecha, codigosUtilizados);
    return redondear(ibc * pct);
}

double CalculadoraDeducciones::calcularAporteArl(double ibc, const std::optional<std::string>& claseArl, const std::string& fecha, std::map<std::string, std::string>* codigosUtilizados) {
    std::string clase = claseArl.has_value() ? a_mayusculas(*claseArl) : "I";
    size_t pos = clase.find("CLASE ");
    if (pos != std::string::npos) clase.erase(pos, 6);
    while (!clase.empty() && clase.front() == ' ') clase.erase(clase.begin());
    while (!clase.empty() && clase.back() == ' ') clase.pop_back();
    if (clase.empty()) clase = "I";

    double pct = obtenerPorcentaje("PORCENTAJE_ARL_CLASE_" + clase, 0.00522, fecha, codigosUtilizados);
    return redondear(ibc * pct);
}

double CalculadoraDeducciones::calcularAporteCaja(double ibc, const std::string& fecha, std::map<std::string, std::string>* codigosUtilizados) {
    double pct = obtenerPorcentaje("PORCENTAJE_CAJA_COMPENSACION", 0.04, fecha, codigosUtilizados);
    return redondear(ibc * pct);
}

double CalculadoraDeducciones::calcularAporteSena(double ibc, double salarioMinimo, const std::string& fecha, std::map<std::string, std::string>* codigosUtilizados) {
    if (ibc < 10.0 * salarioMinimo) {
        return 0.0; // Exoneración tributaria
    }
    double pct = obtenerPorcentaje("PORCENTAJE_SENA", 0.02, fecha, codigosUtilizados);
    return redondear(ibc * pct);
}

double CalculadoraDeducciones::calcularAporteIcbf(double ibc, double salarioMinimo, const std::string& fecha, std::map<std::string, std::string>* codigosUtilizados) {
    if (ibc < 10.0 * salarioMinimo) {
        return 0.0; // Exoneración tributaria
    }
    double pct = obtenerPorcentaje("PORCENTAJE_ICBF", 0.03, fecha, codigosUtilizados);
    return redondear(ibc * pct);
}

} // namespace pita
