#ifndef CALCULADORA_DEDUCCIONES_H
#define CALCULADORA_DEDUCCIONES_H

#include <string>
#include <optional>
#include <map>
#include "../dominio/lista_enlazada.h"
#include "../dominio/modelo_datos.h"

namespace pita {

class CalculadoraDeducciones {
public:
    ListaEnlazada<ParametroNormativo>& parametros;

    explicit CalculadoraDeducciones(ListaEnlazada<ParametroNormativo>& parametros);

    static double redondear(double valor);
    static double redondearPila(double valor);

    std::optional<double> obtenerParametroDecimal(const std::string& codigo, const std::string& fecha = "");
    double obtenerPorcentaje(const std::string& codigo, double defecto, const std::string& fecha = "", std::map<std::string, std::string>* codigosUtilizados = nullptr);

    // Deducciones trabajador
    double calcularDescuentoSalud(double ibc, const std::string& fecha = "", std::map<std::string, std::string>* codigosUtilizados = nullptr);
    double calcularDescuentoPension(double ibc, const std::string& fecha = "", std::map<std::string, std::string>* codigosUtilizados = nullptr);
    double calcularFondoSolidaridad(double ibc, double salarioMinimo, const std::string& fecha = "", std::map<std::string, std::string>* codigosUtilizados = nullptr);
    double calcularRetencionFuente(double ibc, const std::string& fecha = "", std::map<std::string, std::string>* codigosUtilizados = nullptr);
    double calcularDescuentoEstampilla(double salarioBase, const std::string& fecha = "", std::map<std::string, std::string>* codigosUtilizados = nullptr);

    // Aportes patronales
    double calcularAporteSaludPatronal(double ibc, double salarioMinimo, const std::string& fecha = "", std::map<std::string, std::string>* codigosUtilizados = nullptr, bool exonerado = false);
    double calcularAportePensionPatronal(double ibc, const std::string& fecha = "", std::map<std::string, std::string>* codigosUtilizados = nullptr);
    double calcularAporteArl(double ibc, const std::optional<std::string>& claseArl, const std::string& fecha = "", std::map<std::string, std::string>* codigosUtilizados = nullptr);
    double calcularAporteCaja(double ibc, const std::string& fecha = "", std::map<std::string, std::string>* codigosUtilizados = nullptr);
    double calcularAporteSena(double ibc, double salarioMinimo, const std::string& fecha = "", std::map<std::string, std::string>* codigosUtilizados = nullptr);
    double calcularAporteIcbf(double ibc, double salarioMinimo, const std::string& fecha = "", std::map<std::string, std::string>* codigosUtilizados = nullptr);
};

} // namespace pita

#endif // CALCULADORA_DEDUCCIONES_H
