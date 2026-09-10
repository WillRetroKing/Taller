#include "calculadora_prestaciones.h"
#include <algorithm>
#include <cmath>

namespace pita {

static std::string a_mayusculas(std::string s) {
    std::transform(s.begin(), s.end(), s.begin(), [](unsigned char c) { return std::toupper(c); });
    return s;
}

CalculadoraPrestaciones::CalculadoraPrestaciones(CalculadoraDeducciones& calculadoraDeducciones)
    : calcDed(calculadoraDeducciones) {}

double CalculadoraPrestaciones::redondear(double valor) {
    return std::round(valor * 100.0) / 100.0;
}

double CalculadoraPrestaciones::calcularAuxilioTransporte(
    const Contrato& contrato,
    double salario,
    double smmlv,
    const std::string& fecha,
    std::map<std::string, std::string>* codigosUtilizados
) {
    std::string dedicacion = contrato.dedicacion.has_value() ? to_string(*contrato.dedicacion) :
                            (contrato.tipoDedicacion.value_or(""));
    dedicacion = a_mayusculas(dedicacion);

    // Docentes de hora cátedra no devengan auxilio legal mensual salvo pacto
    if (dedicacion.find("CATEDRA") != std::string::npos && !contrato.aplicaAuxilioTransporte.value_or(false)) {
        return 0.0;
    }

    // Por mandato legal (Ley 15/1959), si devenga hasta 2 SMMLV aplica auxilio de transporte
    if (salario <= 2.0 * smmlv) {
        auto valorOpt = calcDed.obtenerParametroDecimal("VALOR_AUXILIO_TRANSPORTE_VIGENTE", fecha);
        if (codigosUtilizados) {
            (*codigosUtilizados)["VALOR_AUXILIO_TRANSPORTE_VIGENTE"] = valorOpt.has_value() ? std::to_string(*valorOpt) : "0";
        }
        return valorOpt.value_or(0.0);
    }
    return 0.0;
}

double CalculadoraPrestaciones::calcularBonificacionPosgrado(
    const Profesor& profesor,
    double smmlv,
    const Contrato& contrato,
    std::optional<double> horas,
    bool incluirBonificaciones,
    std::map<std::string, std::string>* codigosUtilizados
) {
    std::string tipoProf = profesor.tipoProfesor.has_value() ? to_string(*profesor.tipoProfesor) : "";
    std::string modContra = contrato.modalidadProfesor.value_or(contrato.tipoContrato.value_or(""));
    tipoProf = a_mayusculas(tipoProf);
    modContra = a_mayusculas(modContra);
    if (tipoProf.find("PLANTA") != std::string::npos || modContra.find("PLANTA") != std::string::npos) {
        return 0.0;
    }

    if ((contrato.permiteBonificacionPosgrado.has_value() && !*contrato.permiteBonificacionPosgrado) || !incluirBonificaciones) {
        return 0.0;
    }

    std::string nivel = profesor.nivelPosgradoReconocido.value_or(
        profesor.maximoNivelEstudio.value_or(
            contrato.nivelPosgradoAlVincular.value_or("")
        )
    );
    nivel = a_mayusculas(nivel);

    double factor = 0.0;
    if (nivel.find("DOCTOR") != std::string::npos) factor = 0.90;
    else if (nivel.find("MAESTR") != std::string::npos) factor = 0.45;
    else if (nivel.find("ESPEC") != std::string::npos) factor = 0.10;

    if (codigosUtilizados) {
        (*codigosUtilizados)["BONIFICACION_POSGRADO"] = std::to_string(factor);
    }
    return bonificacionProporcional(smmlv * factor, contrato, horas);
}

double CalculadoraPrestaciones::calcularBonificacionInvestigacion(
    const Profesor& profesor,
    double smmlv,
    const Contrato& contrato,
    std::optional<double> horas,
    bool incluirBonificaciones,
    std::map<std::string, std::string>* codigosUtilizados
) {
    if ((contrato.permiteBonificacionInvestigacion.has_value() && !*contrato.permiteBonificacionInvestigacion) || !incluirBonificaciones) {
        return 0.0;
    }
    std::string grupo = profesor.categoriaGrupoInvestigacion.has_value() ? a_mayusculas(*profesor.categoriaGrupoInvestigacion) : "";
    double factor = 0.0;
    if (grupo == "GRUPO_A1" || grupo == "A1") factor = 0.56;
    else if (grupo == "GRUPO_A" || grupo == "A") factor = 0.47;
    else if (grupo == "GRUPO_B" || grupo == "B") factor = 0.42;
    else if (grupo == "GRUPO_C" || grupo == "C") factor = 0.38;
    else if (grupo == "GRUPO_RECONOCIDO") factor = 0.33;
    else if (grupo == "SEMILLERO") factor = 0.20;

    bool prodVigente = profesor.productividadInvestigativaVigente.value_or(false) || profesor.participaProyectoInvestigacionVigente.value_or(false);
    bool certOk = profesor.certificacionVicerrectoriaInvestigacion.has_value() && !profesor.certificacionVicerrectoriaInvestigacion->empty();
    bool acreditada = (prodVigente && certOk);

    if (codigosUtilizados) {
        (*codigosUtilizados)["BONIFICACION_INVESTIGACION"] = (factor > 0.0) ? std::to_string(factor) : "0";
    }
    return bonificacionProporcional(acreditada ? (smmlv * factor) : 0.0, contrato, horas);
}

double CalculadoraPrestaciones::bonificacionProporcional(double valor, const Contrato& contrato, std::optional<double> horas) {
    if (!horas.has_value() || !contrato.horasMensualesAsignadas.has_value() || *contrato.horasMensualesAsignadas == 0.0) {
        return (valor >= 100.0) ? std::round(valor) : valor;
    }
    double res = valor * (*horas) / (*contrato.horasMensualesAsignadas);
    return (res >= 100.0) ? std::round(res) : res;
}

std::map<std::string, double> CalculadoraPrestaciones::calcularProvisiones(
    double basePrestacional,
    double ibc,
    double dias,
    bool regimenEspecial
) {
    std::map<std::string, double> provisiones;
    double cesantias = redondear(basePrestacional * dias / 360.0);
    double intereses = redondear(cesantias * dias * 0.12 / 360.0);
    provisiones["cesantias"] = cesantias;
    provisiones["intereses"] = intereses;
    provisiones["prima_servicios"] = redondear(basePrestacional * dias / 360.0);
    provisiones["prima_navidad"] = regimenEspecial ? redondear(basePrestacional * dias / 360.0) : 0.0;
    provisiones["vacaciones"] = redondear(ibc * dias / 720.0);
    provisiones["prima_vacaciones"] = 0.0;
    provisiones["bonificacion_servicios"] = 0.0;

    if (!regimenEspecial) {
        return provisiones;
    }

    double tope = calcDed.obtenerParametroDecimal("TOPE_BONIFICACION_SERVICIOS").value_or(756411.0);
    double porcentaje = (ibc <= tope)
        ? calcDed.obtenerPorcentaje("PORCENTAJE_BONIFICACION_SERVICIOS_HASTA_TOPE", 0.50)
        : calcDed.obtenerPorcentaje("PORCENTAJE_BONIFICACION_SERVICIOS_SOBRE_TOPE", 0.35);

    provisiones["bonificacion_servicios"] = redondear(ibc * porcentaje * dias / 360.0);

    double baseVacaciones = ibc + (provisiones["prima_servicios"] / 12.0) + (provisiones["bonificacion_servicios"] / 12.0);
    double basePrimaVacaciones = (ibc * 2.0 / 3.0) + (provisiones["prima_servicios"] / 12.0) + (provisiones["bonificacion_servicios"] / 12.0);

    provisiones["vacaciones"] = redondear(baseVacaciones * dias / 720.0);
    provisiones["prima_vacaciones"] = redondear(basePrimaVacaciones * dias / 540.0);

    double basePrimaNavidad = ibc + (provisiones["prima_servicios"] / 12.0)
                                + (provisiones["prima_vacaciones"] / 12.0)
                                + (provisiones["bonificacion_servicios"] / 12.0);

    provisiones["prima_navidad"] = redondear(basePrimaNavidad * dias / 360.0);
    return provisiones;
}

} // namespace pita
