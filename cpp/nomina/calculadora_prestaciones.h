#ifndef CALCULADORA_PRESTACIONES_H
#define CALCULADORA_PRESTACIONES_H

#include <string>
#include <optional>
#include <map>
#include "../dominio/modelo_datos.h"
#include "calculadora_deducciones.h"

namespace pita {

class CalculadoraPrestaciones {
public:
    CalculadoraDeducciones& calcDed;

    explicit CalculadoraPrestaciones(CalculadoraDeducciones& calculadoraDeducciones);

    static double redondear(double valor);

    double calcularAuxilioTransporte(
        const Contrato& contrato,
        double salario,
        double smmlv,
        const std::string& fecha = "",
        std::map<std::string, std::string>* codigosUtilizados = nullptr
    );

    double calcularBonificacionPosgrado(
        const Profesor& profesor,
        double smmlv,
        const Contrato& contrato,
        std::optional<double> horas,
        bool incluirBonificaciones,
        std::map<std::string, std::string>* codigosUtilizados = nullptr
    );

    double calcularBonificacionInvestigacion(
        const Profesor& profesor,
        double smmlv,
        const Contrato& contrato,
        std::optional<double> horas,
        bool incluirBonificaciones,
        std::map<std::string, std::string>* codigosUtilizados = nullptr
    );

    std::map<std::string, double> calcularProvisiones(
        double basePrestacional,
        double ibc,
        double dias,
        bool regimenEspecial = false
    );

private:
    static double bonificacionProporcional(double valor, const Contrato& contrato, std::optional<double> horas);
};

} // namespace pita

#endif // CALCULADORA_PRESTACIONES_H
