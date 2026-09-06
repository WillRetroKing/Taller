#include "gestor_parametros.h"
#include <ctime>
#include <iomanip>
#include <sstream>
#include <algorithm>

namespace pita {

static const std::unordered_set<std::string> PARAMETROS_PORCENTUALES = {
    "PORCENTAJE_ARL_CLASE_I",
    "PORCENTAJE_ARL_CLASE_II",
    "PORCENTAJE_SENA",
    "PORCENTAJE_ICBF",
    "PORCENTAJE_SALUD_TRABAJADOR",
    "PORCENTAJE_SALUD_EMPLEADOR",
    "PORCENTAJE_PENSION_TRABAJADOR",
    "PORCENTAJE_PENSION_EMPLEADOR",
    "PORCENTAJE_FONDO_SOLIDARIDAD",
    "PORCENTAJE_RIESGOS_LABORALES",
    "PORCENTAJE_CAJA_COMPENSACION",
    "PORCENTAJE_BONIFICACION_SERVICIOS_HASTA_TOPE",
    "PORCENTAJE_BONIFICACION_SERVICIOS_SOBRE_TOPE",
    "PORCENTAJE_RETENCION_FUENTE"
};

static const std::unordered_set<std::string> PARAMETROS_MONETARIOS = {
    "SALARIO_MINIMO",
    "VALOR_PUNTO_SALARIAL",
    "VALOR_AUXILIO_TRANSPORTE_VIGENTE",
    "VALOR_HORA_CATEDRA",
    "TOPE_BONIFICACION_SERVICIOS",
    "BASE_MINIMA_RETENCION_FUENTE"
};

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

GestorParametros::GestorParametros(
    ListaEnlazada<ParametroNormativo>& parametros,
    ListaEnlazada<LiquidacionNomina>& liquidaciones
) : parametros(parametros),
    liquidaciones(liquidaciones) {}

int GestorParametros::siguienteId() {
    int maxId = 0;
    for (const auto& p : parametros) {
        if (p.idParametro.has_value() && *p.idParametro > maxId) {
            maxId = *p.idParametro;
        }
    }
    return maxId + 1;
}

ParametroNormativo* GestorParametros::buscar(int idParametro) {
    for (auto& p : parametros) {
        if (p.idParametro.has_value() && *p.idParametro == idParametro) {
            return &p;
        }
    }
    throw ErrorParametro("No existe el parametro con ID " + std::to_string(idParametro));
}

std::string GestorParametros::codigoStr(const ParametroNormativo& p) {
    if (p.codigo.has_value()) {
        return to_string(*p.codigo);
    }
    return "";
}

std::string GestorParametros::codigoStr(const std::string& cod) {
    return a_mayusculas(cod);
}

bool GestorParametros::esActivo(const std::optional<std::string>& estado) {
    if (!estado.has_value()) return false;
    return a_mayusculas(*estado) == "ACTIVO";
}

bool GestorParametros::vigenteEn(const ParametroNormativo& p, const std::string& fecha) {
    std::string inicio = p.fechaInicioVigencia.value_or("0000-00-00");
    if (inicio > fecha) return false;
    if (p.fechaFinVigencia.has_value() && !p.fechaFinVigencia->empty()) {
        if (fecha > *p.fechaFinVigencia) return false;
    }
    return true;
}

bool GestorParametros::intervalosSeCruzan(const ParametroNormativo& primero, const ParametroNormativo& segundo) {
    std::string p_ini = primero.fechaInicioVigencia.value_or("0000-00-00");
    std::string p_fin = (primero.fechaFinVigencia.has_value() && !primero.fechaFinVigencia->empty()) ? *primero.fechaFinVigencia : "9999-99-99";

    std::string s_ini = segundo.fechaInicioVigencia.value_or("0000-00-00");
    std::string s_fin = (segundo.fechaFinVigencia.has_value() && !segundo.fechaFinVigencia->empty()) ? *segundo.fechaFinVigencia : "9999-99-99";

    return (p_ini <= s_fin && s_ini <= p_fin);
}

bool GestorParametros::estaUsadoEnLiquidacion(const ParametroNormativo& p) {
    std::string cod = codigoStr(p);
    for (const auto& l : liquidaciones) {
        if (l.aprobada.value_or(false)) {
            if (l.regimenLiquidado.has_value() && l.regimenLiquidado->find(cod) != std::string::npos) return true;
            if (l.medioPago.has_value() && l.medioPago->find(cod) != std::string::npos) return true;
            if (l.referenciaPago.has_value() && l.referenciaPago->find(cod) != std::string::npos) return true;
        }
    }
    return false;
}

void GestorParametros::validar(const ParametroNormativo& p) {
    if (!p.codigo.has_value()) {
        throw ErrorParametro("El codigo del parametro es obligatorio");
    }
    if (!p.fechaInicioVigencia.has_value() || p.fechaInicioVigencia->empty()) {
        throw ErrorParametro("La fecha de inicio de vigencia es obligatoria");
    }
    if (p.fechaFinVigencia.has_value() && !p.fechaFinVigencia->empty()) {
        if (*p.fechaFinVigencia <= *p.fechaInicioVigencia) {
            throw ErrorParametro("La fecha de fin debe ser posterior a la fecha de inicio");
        }
    }
    if (!p.valor.has_value() || p.valor->empty()) {
        throw ErrorParametro("El valor del parametro es obligatorio");
    }

    double v = 0.0;
    try {
        v = std::stod(*p.valor);
    } catch (...) {
        throw ErrorParametro("El valor del parametro debe ser numerico");
    }

    std::string cod = codigoStr(p);
    if (PARAMETROS_PORCENTUALES.find(cod) != PARAMETROS_PORCENTUALES.end()) {
        if (v < 0.0 || v > 1.0) {
            throw ErrorParametro("Los porcentajes deben estar entre 0 y 1");
        }
    }
    if (PARAMETROS_MONETARIOS.find(cod) != PARAMETROS_MONETARIOS.end()) {
        if (v <= 0.0) {
            throw ErrorParametro("Los montos monetarios deben ser mayores que cero");
        }
    }
}

void GestorParametros::validarNoSolapamiento(const ParametroNormativo& nuevo, const ParametroNormativo* excluir) {
    std::string nuevoCod = codigoStr(nuevo);
    for (const auto& actual : parametros) {
        if (&actual == excluir) continue;
        if (!esActivo(actual.estado)) continue;
        if (codigoStr(actual) != nuevoCod) continue;

        if (intervalosSeCruzan(nuevo, actual)) {
            throw ErrorParametro("La vigencia se solapa para el parametro " + nuevoCod);
        }
    }
}

ParametroNormativo& GestorParametros::crearParametro(ParametroNormativo parametro) {
    validar(parametro);
    if (!parametro.idParametro.has_value()) {
        parametro.idParametro = siguienteId();
    } else {
        for (const auto& item : parametros) {
            if (item.idParametro.has_value() && *item.idParametro == *parametro.idParametro) {
                throw ErrorParametro("Ya existe un parametro con ID " + std::to_string(*parametro.idParametro));
            }
        }
    }
    validarNoSolapamiento(parametro);
    parametro.estado = "ACTIVO";
    parametros.push_back(std::move(parametro));
    return parametros.back();
}

ParametroNormativo* GestorParametros::buscarParametroVigente(const std::string& codigo, const std::string& fecha) {
    std::string fechaConsulta = fecha.empty() ? fecha_hoy() : fecha;
    std::string cod = codigoStr(codigo);

    ParametroNormativo* mejor = nullptr;
    for (auto& p : parametros) {
        if (codigoStr(p) == cod && esActivo(p.estado) && vigenteEn(p, fechaConsulta)) {
            if (!mejor || (p.fechaInicioVigencia.value_or("") > mejor->fechaInicioVigencia.value_or(""))) {
                mejor = &p;
            }
        }
    }
    return mejor;
}

ParametroNormativo* GestorParametros::obtenerParametro(const std::string& codigo, const std::string& fecha) {
    return buscarParametroVigente(codigo, fecha);
}

std::optional<double> GestorParametros::obtenerParametroVigente(const std::string& codigo, const std::string& fecha) {
    ParametroNormativo* p = buscarParametroVigente(codigo, fecha);
    if (p && p->valor.has_value() && !p->valor->empty()) {
        try {
            return std::stod(*p->valor);
        } catch (...) {
            return std::nullopt;
        }
    }
    return std::nullopt;
}

ParametroNormativo& GestorParametros::modificarParametro(int idParametro, const ParametroNormativo& datosActualizados) {
    ParametroNormativo* actual = buscar(idParametro);
    if (estaUsadoEnLiquidacion(*actual)) {
        throw ErrorParametro("No se puede modificar un parametro utilizado en una liquidacion");
    }

    ParametroNormativo copia = datosActualizados;
    copia.idParametro = actual->idParametro;
    validar(copia);
    validarNoSolapamiento(copia, actual);

    *actual = copia;
    return *actual;
}

ParametroNormativo& GestorParametros::desactivarParametro(int idParametro) {
    ParametroNormativo* p = buscar(idParametro);
    if (estaUsadoEnLiquidacion(*p)) {
        throw ErrorParametro("No se puede desactivar un parametro utilizado en una liquidacion");
    }
    p->estado = "INACTIVO";
    return *p;
}

ListaEnlazada<ParametroNormativo> GestorParametros::listarParametrosPorTipo(const std::string& tipoDato) const {
    ListaEnlazada<ParametroNormativo> res;
    for (const auto& p : parametros) {
        if (p.tipoDato.has_value() && *p.tipoDato == tipoDato) {
            res.push_back(p);
        }
    }
    return res;
}

} // namespace pita
