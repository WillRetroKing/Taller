#include "gestor_nomina.h"
#include "../gestores/gestor_factores.h"
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

static int diasEnMes(int anio, int mes) {
    if (mes == 2) {
        bool bisiesto = (anio % 4 == 0 && (anio % 100 != 0 || anio % 400 == 0));
        return bisiesto ? 29 : 28;
    }
    if (mes == 4 || mes == 6 || mes == 9 || mes == 11) return 30;
    return 31;
}

// ==========================================
// MOTOR LIQUIDACION BASE
// ==========================================

MotorLiquidacionBase::MotorLiquidacionBase(GestorNomina& gestor) : gestor(gestor) {}

LiquidacionNomina MotorLiquidacionBase::ensamblarLiquidacion(
    Contrato& contrato,
    Profesor& profesor,
    PeriodoNomina& periodo,
    const std::string& fechaLiquidacion,
    double salarioBase,
    double salarioOrdinario,
    double ibc,
    std::optional<double> horasAsignadas,
    std::optional<double> horasCumplidas,
    double horasIncumplidas,
    double descuentoIncumplimiento,
    TipoProfesor tipo,
    std::optional<double> horasPagables,
    bool esAdHonorem,
    bool incluirBonificaciones
) {
    if (ibc < 0.0) {
        throw ErrorNomina("El IBC no puede ser negativo");
    }

    std::string fechaParam;
    if (periodo.fechaFin.has_value() && !periodo.fechaFin->empty()) fechaParam = *periodo.fechaFin;
    else if (periodo.fechaInicio.has_value() && !periodo.fechaInicio->empty()) fechaParam = *periodo.fechaInicio;
    else fechaParam = fecha_hoy();

    std::map<std::string, std::string> codigosUtilizados;

    double salarioMinimo = gestor.salarioMinimo(contrato, periodo, fechaParam, &codigosUtilizados);
    double auxilio = gestor.calcPrestaciones.calcularAuxilioTransporte(contrato, salarioOrdinario, salarioMinimo, fechaParam, &codigosUtilizados);
    double basePrestacional = ibc + auxilio;

    double bonifPosgrado = gestor.calcPrestaciones.calcularBonificacionPosgrado(profesor, salarioMinimo, contrato, horasPagables, incluirBonificaciones, &codigosUtilizados);
    double bonifInvestigacion = gestor.calcPrestaciones.calcularBonificacionInvestigacion(profesor, salarioMinimo, contrato, horasPagables, incluirBonificaciones, &codigosUtilizados);

    auto& calcDed = gestor.calcDeducciones;
    double descuentoSalud = calcDed.calcularDescuentoSalud(ibc, fechaParam, &codigosUtilizados);
    double descuentoPension = calcDed.calcularDescuentoPension(ibc, fechaParam, &codigosUtilizados);
    double fondoSolidaridad = calcDed.calcularFondoSolidaridad(ibc, salarioMinimo, fechaParam, &codigosUtilizados);
    double retencion = calcDed.calcularRetencionFuente(ibc, fechaParam, &codigosUtilizados);
    double descuentoEstampilla = calcDed.calcularDescuentoEstampilla(salarioOrdinario, fechaParam, &codigosUtilizados);

    bool esExoneradoSalud = (tipo != TipoProfesor::PLANTA);
    double aporteSalud = calcDed.calcularAporteSaludPatronal(ibc, salarioMinimo, fechaParam, &codigosUtilizados, esExoneradoSalud);
    double aportePension = calcDed.calcularAportePensionPatronal(ibc, fechaParam, &codigosUtilizados);
    double aporteArl = calcDed.calcularAporteArl(ibc, contrato.claseARL, fechaParam, &codigosUtilizados);
    double aporteCaja = calcDed.calcularAporteCaja(ibc, fechaParam, &codigosUtilizados);
    double aporteSena = calcDed.calcularAporteSena(ibc, salarioMinimo, fechaParam, &codigosUtilizados);
    double aporteIcbf = calcDed.calcularAporteIcbf(ibc, salarioMinimo, fechaParam, &codigosUtilizados);

    double dias = static_cast<double>(periodo.diasBaseLiquidacion.value_or(30));
    bool regimenEspecial = (tipo == TipoProfesor::PLANTA && (!contrato.regimenAplicable.has_value() || GestorNomina::esRegimen1279(contrato.regimenAplicable)));
    auto provisiones = gestor.calcPrestaciones.calcularProvisiones(basePrestacional, ibc, dias, regimenEspecial);

    double bonificaciones = bonifPosgrado + bonifInvestigacion;
    double totalDescuentos = descuentoSalud + descuentoPension + fondoSolidaridad + retencion + descuentoEstampilla + descuentoIncumplimiento;
    double totalDevengado = salarioOrdinario + auxilio + bonificaciones;

    double totalPrestaciones = 0.0;
    for (const auto& kv : provisiones) {
        totalPrestaciones += kv.second;
    }
    double neto = totalDevengado - totalDescuentos;

    LiquidacionNomina liq;
    liq.idLiquidacion = gestor.siguienteId();
    liq.idProfesor = profesor.idProfesor;
    liq.idContrato = contrato.idContrato;
    liq.idPeriodoNomina = periodo.idPeriodoNomina;
    liq.fechaLiquidacion = fechaLiquidacion.empty() ? fecha_hoy() : fechaLiquidacion;
    liq.salarioBase = salarioBase;
    liq.totalDevengado = GestorNomina::redondear(totalDevengado);
    liq.totalDescuentos = GestorNomina::redondear(totalDescuentos);
    liq.totalPrestaciones = GestorNomina::redondear(totalPrestaciones);
    liq.baseLiquidacionPrestaciones = GestorNomina::redondear(basePrestacional);
    liq.baseCotizacionSeguridadSocial = GestorNomina::redondear(ibc);
    liq.valorAuxilioTransporteCotizado = GestorNomina::redondear(auxilio);
    liq.aportePatronalSENA = GestorNomina::redondear(aporteSena);
    liq.aportePatronalICBF = GestorNomina::redondear(aporteIcbf);
    liq.netoPagar = GestorNomina::redondear(neto);
    liq.estado = "PROCESADA";
    liq.tipoProfesorLiquidado = tipo;
    liq.regimenLiquidado = contrato.regimenAplicable;
    liq.dedicacionLiquidada = contrato.dedicacion;
    liq.diasTrabajados = dias;
    liq.horasAsignadas = horasAsignadas;
    liq.horasCumplidas = horasCumplidas;
    liq.horasIncumplidas = horasIncumplidas;
    liq.salarioMinimoUsado = salarioMinimo;
    liq.valorHoraCatedraUsado = contrato.valorHoraCatedraVigente;
    liq.factorCategoriaUsado = contrato.factorSalarialSMMLV;
    liq.salarioOrdinario = GestorNomina::redondear(salarioOrdinario);
    liq.baseSalarialPrestacional = GestorNomina::redondear(basePrestacional);
    liq.baseSeguridadSocial = GestorNomina::redondear(ibc);
    liq.bonificacionPosgrado = GestorNomina::redondear(bonifPosgrado);
    liq.bonificacionInvestigacion = GestorNomina::redondear(bonifInvestigacion);
    liq.bonificacionesNoSalariales = GestorNomina::redondear(bonificaciones);
    liq.descuentoSalud = descuentoSalud;
    liq.descuentoPension = descuentoPension;
    liq.fondoSolidaridadPensional = fondoSolidaridad;
    liq.retencionFuente = retencion;
    liq.descuentoHorasIncumplidas = GestorNomina::redondear(descuentoIncumplimiento);
    liq.otrosDescuentos = GestorNomina::redondear(descuentoEstampilla);
    liq.provisionCesantias = provisiones["cesantias"];
    liq.provisionInteresesCesantias = provisiones["intereses"];
    liq.provisionPrimaServicios = provisiones["prima_servicios"];
    liq.provisionPrimaNavidad = provisiones["prima_navidad"];
    liq.provisionVacaciones = provisiones["vacaciones"];
    liq.provisionPrimaVacaciones = provisiones["prima_vacaciones"];
    liq.bonificacionServiciosPrestados = provisiones["bonificacion_servicios"];
    liq.aportePatronalSalud = GestorNomina::redondear(aporteSalud);
    liq.aportePatronalPension = aportePension;
    liq.aporteRiesgosLaborales = aporteArl;
    liq.aporteCajaCompensacion = aporteCaja;

    double costoTotal = totalDevengado + totalPrestaciones + aporteSalud + aportePension + aporteArl + aporteSena + aporteIcbf + aporteCaja;
    liq.costoTotalEmpleador = GestorNomina::redondear(costoTotal);

    gestor.liquidaciones.push_back(std::move(liq));
    LiquidacionNomina& liqGuardada = gestor.liquidaciones.back();

    crearDetalles(
        liqGuardada, periodo, ibc, salarioOrdinario, auxilio,
        bonifPosgrado, bonifInvestigacion, descuentoSalud, descuentoPension,
        fondoSolidaridad, retencion, descuentoEstampilla, descuentoIncumplimiento, aporteSalud,
        aportePension, aporteArl, aporteCaja, aporteSena, aporteIcbf, &codigosUtilizados
    );

    return liqGuardada;
}

void MotorLiquidacionBase::crearDetalles(
    LiquidacionNomina& liq,
    PeriodoNomina& periodo,
    double ibc,
    double salarioOrdinario,
    double auxilio,
    double bonifPosgrado,
    double bonifInvestigacion,
    double descuentoSalud,
    double descuentoPension,
    double fondoSolidaridad,
    double retencion,
    double descuentoEstampilla,
    double descuentoIncumplimiento,
    double aporteSalud,
    double aportePension,
    double aporteArl,
    double aporteCaja,
    double aporteSena,
    double aporteIcbf,
    std::map<std::string, std::string>* codigosUtilizados
) {
    auto& calcDed = gestor.calcDeducciones;

    struct ConceptoItem {
        std::string codigo;
        double valor;
        double base;
        std::optional<double> porcentaje;
        std::string formula;
    };

    std::vector<ConceptoItem> conceptos = {
        {"SALARIO_ORDINARIO", salarioOrdinario, ibc, std::nullopt, "salarioOrdinario = IBC"},
        {"AUXILIO_TRANSPORTE", auxilio, 0.0, std::nullopt, "auxilio segun salario y SMMLV"},
        {"BONIFICACION_POSGRADO", bonifPosgrado, 0.0, std::nullopt, "SMMLV * factorPosgrado"},
        {"BONIFICACION_INVESTIGACION", bonifInvestigacion, 0.0, std::nullopt, "SMMLV * factorInvestigacion"},
        {"DESCUENTO_SALUD", descuentoSalud, ibc, calcDed.obtenerPorcentaje("PORCENTAJE_SALUD_TRABAJADOR", 0.0, "", codigosUtilizados), "IBC * porcentajeSaludTrabajador"},
        {"DESCUENTO_PENSION", descuentoPension, ibc, calcDed.obtenerPorcentaje("PORCENTAJE_PENSION_TRABAJADOR", 0.0), "IBC * porcentajePensionTrabajador"},
        {"FONDO_SOLIDARIDAD", fondoSolidaridad, ibc, calcDed.obtenerPorcentaje("PORCENTAJE_FONDO_SOLIDARIDAD", 0.0), "IBC * porcentajeFondoSolidaridad"},
        {"RETENCION_FUENTE", retencion, ibc, calcDed.obtenerPorcentaje("PORCENTAJE_RETENCION_FUENTE", 0.0), "IBC * porcentajeRetencionFuente"},
    };

    if (descuentoEstampilla > 0.0) {
        conceptos.push_back({"DESCUENTO_ESTAMPILLA", descuentoEstampilla, salarioOrdinario, calcDed.obtenerPorcentaje("PORCENTAJE_ESTAMPILLA", 0.002), "salarioBase * porcentajeEstampilla"});
    }

    conceptos.push_back({"DESCUENTO_INCUMPLIMIENTO", descuentoIncumplimiento, descuentoIncumplimiento, std::nullopt, "horasIncumplidas * valorHoraIncumplida"});
    conceptos.push_back({"APORTE_SALUD_PATRONAL", aporteSalud, ibc, calcDed.obtenerPorcentaje("PORCENTAJE_SALUD_EMPLEADOR", 0.0), "IBC * porcentajeSaludEmpleador"});
    conceptos.push_back({"APORTE_PENSION_PATRONAL", aportePension, ibc, calcDed.obtenerPorcentaje("PORCENTAJE_PENSION_EMPLEADOR", 0.0), "IBC * porcentajePensionEmpleador"});
    conceptos.push_back({"APORTE_ARL", aporteArl, ibc, std::nullopt, "IBC * porcentajeARL"});
    conceptos.push_back({"APORTE_CAJA", aporteCaja, ibc, calcDed.obtenerPorcentaje("PORCENTAJE_CAJA_COMPENSACION", 0.0), "IBC * porcentajeCajaCompensacion"});
    conceptos.push_back({"APORTE_SENA", aporteSena, ibc, calcDed.obtenerPorcentaje("PORCENTAJE_SENA", 0.0), "IBC * porcentajeSENA"});
    conceptos.push_back({"APORTE_ICBF", aporteIcbf, ibc, calcDed.obtenerPorcentaje("PORCENTAJE_ICBF", 0.0), "IBC * porcentajeICBF"});

    for (const auto& item : conceptos) {
        DetalleLiquidacion d;
        d.idDetalleLiquidacion = gestor.siguienteIdDetalle();
        d.idLiquidacion = liq.idLiquidacion;
        d.cantidad = 1.0;
        d.baseCalculo = GestorNomina::redondear(item.base);
        d.porcentajeAplicado = item.porcentaje;
        d.valorCalculado = GestorNomina::redondear(item.valor);
        d.valorDefinitivo = GestorNomina::redondear(item.valor);
        d.tipoMovimiento = item.codigo;
        d.observaciones = item.codigo;
        d.periodoCausacion = periodo.idPeriodoNomina.has_value() ? std::to_string(*periodo.idPeriodoNomina) : "";
        d.formulaAplicada = item.formula;
        d.fechaRegistro = fecha_hoy();
        d.esSalarial = (item.codigo == "SALARIO_ORDINARIO");
        d.integraSeguridadSocial = (item.codigo == "SALARIO_ORDINARIO");
        d.integraPrestaciones = (item.codigo == "SALARIO_ORDINARIO" || item.codigo == "AUXILIO_TRANSPORTE");
        d.integraParafiscales = (item.codigo == "SALARIO_ORDINARIO");

        gestor.detallesLiquidacion.push_back(std::move(d));
    }
}

// ==========================================
// LIQUIDADORES ESPECIFICOS
// ==========================================

LiquidacionNomina LiquidadorOcasional::liquidar(
    int idContrato,
    int idPeriodoNomina,
    std::optional<double> horasIncumplidas,
    const std::string& fechaLiquidacion
) {
    Contrato& contrato = gestor.contrato(idContrato);
    PeriodoNomina& periodo = gestor.periodo(idPeriodoNomina);
    gestor.validarPeriodoAbierto(periodo);
    gestor.evitarLiquidacionDuplicada(idContrato, idPeriodoNomina);
    Profesor& profesor = gestor.profesor(contrato.idPersona);
    gestor.validarContrato(contrato, TipoProfesor::OCASIONAL, periodo);

    double salarioMinimo = gestor.salarioMinimo(contrato, periodo);
    std::string catProf = profesor.categoriaDocente.has_value() ? a_mayusculas(*profesor.categoriaDocente) :
                          (profesor.categoriaReconocida.has_value() ? a_mayusculas(*profesor.categoriaReconocida) : "");
    std::string dedContra = contrato.dedicacion.has_value() ? to_string(*contrato.dedicacion) :
                           (contrato.tipoDedicacion.has_value() ? a_mayusculas(*contrato.tipoDedicacion) :
                           (profesor.dedicacion.has_value() ? to_string(*profesor.dedicacion) : ""));

    std::optional<double> factorCategoria = std::nullopt;
    if (catProf.find("TITULAR") != std::string::npos) {
        factorCategoria = 3.918;
    } else if (catProf.find("ASOCIADO") != std::string::npos) {
        factorCategoria = 3.606;
    } else if (catProf.find("ASISTENTE") != std::string::npos) {
        factorCategoria = 3.125;
    } else if (catProf.find("AUXILIAR") != std::string::npos) {
        factorCategoria = 2.645;
    }

    if (factorCategoria.has_value() && dedContra.find("MEDIO") != std::string::npos) {
        factorCategoria = *factorCategoria / 2.0;
    }

    double factor = 2.645;
    if (factorCategoria.has_value()) {
        factor = *factorCategoria;
    } else if (contrato.factorSalarialSMMLV.has_value() && *contrato.factorSalarialSMMLV > 0.0) {
        factor = *contrato.factorSalarialSMMLV;
    } else {
        factor = (dedContra.find("MEDIO") != std::string::npos) ? 1.3225 : 2.645;
    }

    // CU-21: salarioBase = SALARIO_MINIMO * factorCategoriaDedicacion (no asignar SMMLV directo)
    double salarioBase = GestorNomina::redondear(salarioMinimo * factor);
    double horasNoCumplidas = horasIncumplidas.value_or(contrato.horasIncumplidas.value_or(0.0));
    gestor.validarHorasIncumplidas(contrato, horasNoCumplidas);

    double valorHoraIncumplida = contrato.valorHoraIncumplida.value_or(0.0);
    double descuentoIncumplimiento = horasNoCumplidas * valorHoraIncumplida;
    double salarioOrdinario = salarioBase;
    double ibc = salarioOrdinario - descuentoIncumplimiento;

    return ensamblarLiquidacion(
        contrato, profesor, periodo, fechaLiquidacion,
        salarioBase, salarioOrdinario, ibc,
        contrato.horasSemanalesAsignadas, std::nullopt,
        horasNoCumplidas, descuentoIncumplimiento,
        TipoProfesor::OCASIONAL
    );
}

LiquidacionNomina LiquidadorPlanta::liquidar(
    int idContrato,
    int idPeriodoNomina,
    const std::string& fechaLiquidacion
) {
    Contrato& contrato = gestor.contrato(idContrato);
    PeriodoNomina& periodo = gestor.periodo(idPeriodoNomina);
    gestor.validarPeriodoAbierto(periodo);
    gestor.evitarLiquidacionDuplicada(idContrato, idPeriodoNomina);
    Profesor& profesor = gestor.profesor(contrato.idPersona);
    gestor.validarContrato(contrato, TipoProfesor::PLANTA, periodo);

    double puntos = gestor.puntosPlanta(profesor, periodo);
    double valorPunto = periodo.valorPuntoSalarialVigente.value_or(
        gestor.calcDeducciones.obtenerParametroDecimal("VALOR_PUNTO_SALARIAL").value_or(0.0)
    );

    std::string ded = contrato.dedicacion.has_value() ? to_string(*contrato.dedicacion) :
                     (contrato.tipoDedicacion.has_value() ? a_mayusculas(*contrato.tipoDedicacion) : "");
    double factorDedicacion = -1.0;
    if (ded == "TIEMPO_COMPLETO") factorDedicacion = 1.0;
    else if (ded == "MEDIO_TIEMPO") factorDedicacion = 0.5;
    else {
        throw ErrorNomina("La dedicacion de planta debe ser tiempo completo o medio tiempo");
    }

    double salarioBase = puntos * valorPunto * factorDedicacion;
    LiquidacionNomina liq = ensamblarLiquidacion(
        contrato, profesor, periodo, fechaLiquidacion,
        salarioBase, salarioBase, salarioBase,
        contrato.horasSemanalesAsignadas, std::nullopt,
        0.0, 0.0,
        TipoProfesor::PLANTA,
        std::nullopt, false, false
    );

    liq.valorPuntoUsado = valorPunto;
    liq.puntosSalarialesUsados = puntos;
    return liq;
}

LiquidacionNomina LiquidadorCatedratico::liquidar(
    int idContrato,
    int idPeriodoNomina,
    const std::string& fechaLiquidacion
) {
    Contrato& contrato = gestor.contrato(idContrato);
    PeriodoNomina& periodo = gestor.periodo(idPeriodoNomina);
    gestor.validarPeriodoAbierto(periodo);
    gestor.evitarLiquidacionDuplicada(idContrato, idPeriodoNomina);
    Profesor& profesor = gestor.profesor(contrato.idPersona);
    gestor.validarContrato(contrato, TipoProfesor::CATEDRATICO, periodo);

    double horasSemanales = contrato.horasSemanales.value_or(contrato.horasSemanalesAsignadas.value_or(12.0));
    double horasAsignadas = contrato.horasMensualesAsignadas.value_or(horasSemanales * 4.0);
    double horasCumplidas = contrato.horasMensualesCumplidas.value_or(horasAsignadas);
    double horasPagables = std::min(horasAsignadas, horasCumplidas);

    double valorHora = contrato.valorHoraCatedraVigente.value_or(contrato.valorHora.value_or(0.0));
    if (valorHora == 0.0) {
        if (contrato.salarioBase.has_value() && horasPagables > 0.0) {
            valorHora = std::round(*contrato.salarioBase / horasPagables);
        } else {
            valorHora = gestor.calcDeducciones.obtenerParametroDecimal("VALOR_HORA_CATEDRA").value_or(38500.0);
        }
    }

    std::string mod = contrato.modalidadProfesor.has_value() ? a_mayusculas(*contrato.modalidadProfesor) :
                     (contrato.tipoContrato.has_value() ? a_mayusculas(*contrato.tipoContrato) : "");
    bool esAdHonorem = (contrato.esAdHonorem.value_or(false) || mod.find("AD_HONOREM") != std::string::npos);

    double salarioBase = esAdHonorem ? 0.0 : (contrato.salarioBase.value_or(horasPagables * valorHora));

    return ensamblarLiquidacion(
        contrato, profesor, periodo, fechaLiquidacion,
        salarioBase, salarioBase, salarioBase,
        horasAsignadas, horasCumplidas,
        0.0, 0.0,
        TipoProfesor::CATEDRATICO,
        horasPagables, esAdHonorem
    );
}

LiquidacionNomina LiquidadorAdministrativo::liquidar(
    int idContrato,
    int idPeriodoNomina,
    const std::string& fechaLiquidacion
) {
    Contrato& contrato = gestor.contrato(idContrato);
    PeriodoNomina& periodo = gestor.periodo(idPeriodoNomina);
    gestor.validarPeriodoAbierto(periodo);
    gestor.evitarLiquidacionDuplicada(idContrato, idPeriodoNomina);

    if (contrato.estado.has_value() && a_mayusculas(*contrato.estado) != "ACTIVO") {
        throw ErrorNomina("El contrato no esta activo");
    }
    std::string inicioPeriodo = periodo.fechaInicio.value_or(periodo.fechaFin.value_or(fecha_hoy()));
    std::string finPeriodo = periodo.fechaFin.value_or(inicioPeriodo);
    if (contrato.fechaInicio.has_value() && !contrato.fechaInicio->empty() && *contrato.fechaInicio > finPeriodo) {
        throw ErrorNomina("El contrato inicia despues del periodo de liquidacion");
    }
    if (contrato.fechaFin.has_value() && !contrato.fechaFin->empty() && *contrato.fechaFin < inicioPeriodo) {
        throw ErrorNomina("El contrato termino antes del periodo de liquidacion");
    }

    Administrativo* adm = gestor.administrativo(contrato.idPersona);

    double salarioBase = contrato.salarioBase.value_or(0.0);
    if (salarioBase <= 0.0 && adm && adm->salarioBase.has_value()) {
        salarioBase = *adm->salarioBase;
    }

    double salarioOrdinario = salarioBase;
    double ibc = salarioOrdinario;

    std::string fechaParam = periodo.fechaFin.value_or(periodo.fechaInicio.value_or(fecha_hoy()));
    std::map<std::string, std::string> codigosUtilizados;

    double salarioMinimo = gestor.salarioMinimo(contrato, periodo, fechaParam, &codigosUtilizados);
    double auxilio = 0.0;
    if (salarioOrdinario <= 2.0 * salarioMinimo) {
        auxilio = gestor.calcPrestaciones.calcularAuxilioTransporte(contrato, salarioOrdinario, salarioMinimo, fechaParam, &codigosUtilizados);
    }
    double basePrestacional = ibc + auxilio;

    auto& calcDed = gestor.calcDeducciones;
    double descuentoSalud = calcDed.calcularDescuentoSalud(ibc, fechaParam, &codigosUtilizados);
    double descuentoPension = calcDed.calcularDescuentoPension(ibc, fechaParam, &codigosUtilizados);
    double fondoSolidaridad = calcDed.calcularFondoSolidaridad(ibc, salarioMinimo, fechaParam, &codigosUtilizados);
    double retencion = calcDed.calcularRetencionFuente(ibc, fechaParam, &codigosUtilizados);

    // Aportes patronales CST / Ley 100
    double aporteSalud = calcDed.calcularAporteSaludPatronal(ibc, salarioMinimo, fechaParam, &codigosUtilizados, true);
    double aportePension = calcDed.calcularAportePensionPatronal(ibc, fechaParam, &codigosUtilizados);
    std::string claseARL = contrato.claseARL.value_or("RIESGO_I");
    double aporteArl = calcDed.calcularAporteArl(ibc, claseARL, fechaParam, &codigosUtilizados);
    double aporteCaja = calcDed.calcularAporteCaja(ibc, fechaParam, &codigosUtilizados);
    double aporteSena = calcDed.calcularAporteSena(ibc, salarioMinimo, fechaParam, &codigosUtilizados);
    double aporteIcbf = calcDed.calcularAporteIcbf(ibc, salarioMinimo, fechaParam, &codigosUtilizados);

    double dias = periodo.diasBaseLiquidacion.value_or(30);
    auto provisiones = gestor.calcPrestaciones.calcularProvisiones(basePrestacional, ibc, dias, false);

    double totalDescuentos = descuentoSalud + descuentoPension + fondoSolidaridad + retencion;
    double totalDevengado = salarioOrdinario + auxilio;
    double totalPrestaciones = 0.0;
    for (const auto& [_, val] : provisiones) {
        totalPrestaciones += val;
    }
    double neto = totalDevengado - totalDescuentos;

    std::string cargo = (adm && adm->cargo.has_value()) ? *adm->cargo : "ADMINISTRATIVO";

    LiquidacionNomina liq;
    liq.idLiquidacion = gestor.siguienteId();
    liq.idProfesor = std::nullopt;
    liq.idContrato = contrato.idContrato;
    liq.idPeriodoNomina = periodo.idPeriodoNomina;
    liq.fechaLiquidacion = fechaLiquidacion.empty() ? fecha_hoy() : fechaLiquidacion;
    liq.salarioBase = salarioBase;
    liq.totalDevengado = GestorNomina::redondear(totalDevengado);
    liq.totalDescuentos = GestorNomina::redondear(totalDescuentos);
    liq.totalPrestaciones = GestorNomina::redondear(totalPrestaciones);
    liq.baseLiquidacionPrestaciones = GestorNomina::redondear(basePrestacional);
    liq.baseCotizacionSeguridadSocial = GestorNomina::redondear(ibc);
    liq.valorAuxilioTransporteCotizado = GestorNomina::redondear(auxilio);
    liq.aportePatronalSENA = GestorNomina::redondear(aporteSena);
    liq.aportePatronalICBF = GestorNomina::redondear(aporteIcbf);
    liq.netoPagar = GestorNomina::redondear(neto);
    liq.estado = "PROCESADA";
    liq.tipoProfesorLiquidado = std::nullopt;
    liq.regimenLiquidado = contrato.regimenAplicable.value_or("LEY_100_CST");
    liq.categoriaLiquidada = cargo;
    liq.dedicacionLiquidada = contrato.dedicacion.value_or(Dedicacion::TIEMPO_COMPLETO);
    liq.diasTrabajados = dias;
    liq.horasAsignadas = contrato.horasSemanales.value_or(40.0);
    liq.salarioMinimoUsado = salarioMinimo;
    liq.salarioOrdinario = GestorNomina::redondear(salarioOrdinario);
    liq.baseSalarialPrestacional = GestorNomina::redondear(basePrestacional);
    liq.baseSeguridadSocial = GestorNomina::redondear(ibc);
    liq.descuentoSalud = descuentoSalud;
    liq.descuentoPension = descuentoPension;
    liq.fondoSolidaridadPensional = fondoSolidaridad;
    liq.retencionFuente = retencion;
    liq.provisionCesantias = provisiones["cesantias"];
    liq.provisionInteresesCesantias = provisiones["intereses"];
    liq.provisionPrimaServicios = provisiones["prima_servicios"];
    liq.provisionPrimaNavidad = provisiones["prima_navidad"];
    liq.provisionVacaciones = provisiones["vacaciones"];
    liq.provisionPrimaVacaciones = provisiones["prima_vacaciones"];
    liq.bonificacionServiciosPrestados = provisiones["bonificacion_servicios"];
    liq.aportePatronalSalud = GestorNomina::redondear(aporteSalud);
    liq.aportePatronalPension = aportePension;
    liq.aporteRiesgosLaborales = aporteArl;
    liq.aporteCajaCompensacion = aporteCaja;

    double costoTotal = totalDevengado + totalPrestaciones + aporteSalud + aportePension + aporteArl + aporteSena + aporteIcbf + aporteCaja;
    liq.costoTotalEmpleador = GestorNomina::redondear(costoTotal);

    gestor.liquidaciones.push_back(std::move(liq));
    LiquidacionNomina& liqGuardada = gestor.liquidaciones.back();

    crearDetalles(
        liqGuardada, periodo, ibc, salarioOrdinario, auxilio,
        0.0, 0.0, descuentoSalud, descuentoPension,
        fondoSolidaridad, retencion, 0.0, 0.0, aporteSalud,
        aportePension, aporteArl, aporteCaja, aporteSena, aporteIcbf, &codigosUtilizados
    );

    return liqGuardada;
}

// ==========================================
// CICLO DE VIDA NOMINA
// ==========================================

CicloVidaNomina::CicloVidaNomina(GestorNomina& gestor) : gestor(gestor) {}

PeriodoNomina& CicloVidaNomina::crearPeriodoNomina(PeriodoNomina periodo) {
    if (!periodo.idPeriodoNomina.has_value()) {
        int maxId = 0;
        for (const auto& p : gestor.periodosNomina) {
            if (p.idPeriodoNomina.has_value() && *p.idPeriodoNomina > maxId) {
                maxId = *p.idPeriodoNomina;
            }
        }
        periodo.idPeriodoNomina = maxId + 1;
    } else {
        for (const auto& p : gestor.periodosNomina) {
            if (p.idPeriodoNomina.has_value() && *p.idPeriodoNomina == *periodo.idPeriodoNomina) {
                throw ErrorNomina("Ya existe el periodo de nomina " + std::to_string(*periodo.idPeriodoNomina));
            }
        }
    }

    if (periodo.fechaInicio.has_value() && periodo.fechaFin.has_value() && !periodo.fechaInicio->empty() && !periodo.fechaFin->empty()) {
        if (*periodo.fechaFin < *periodo.fechaInicio) {
            throw ErrorNomina("La fecha final no puede preceder a la fecha inicial");
        }
    }

    periodo.estaCerrado = false;
    if (!periodo.estado.has_value() || periodo.estado->empty()) {
        periodo.estado = "ABIERTO";
    }

    gestor.periodosNomina.push_back(std::move(periodo));
    return gestor.periodosNomina.back();
}

PeriodoNomina& CicloVidaNomina::abrirPeriodoNomina(int idPeriodoNomina) {
    PeriodoNomina& p = gestor.periodo(idPeriodoNomina);
    if (p.estaCerrado.value_or(false)) {
        throw ErrorNomina("Un periodo cerrado no puede reabrirse");
    }
    p.estado = "ABIERTO";
    return p;
}

PeriodoNomina& CicloVidaNomina::cerrarPeriodoNomina(int idPeriodoNomina) {
    PeriodoNomina& p = gestor.periodo(idPeriodoNomina);
    if (p.estaCerrado.value_or(false)) {
        throw ErrorNomina("El periodo ya esta cerrado");
    }

    p.totalDevengadoPeriodo = gestor.totalPeriodo(idPeriodoNomina, "totalDevengado");
    p.totalDescuentosPeriodo = gestor.totalPeriodo(idPeriodoNomina, "totalDescuentos");
    p.totalPrestacionesPeriodo = gestor.totalPeriodo(idPeriodoNomina, "totalPrestaciones");

    double totalAportes = 0.0;
    for (const auto& l : gestor.liquidacionesPeriodo(idPeriodoNomina)) {
        totalAportes += GestorNomina::aportes(l);
    }
    p.totalAportesPatronalesPeriodo = totalAportes;
    p.costoTotalPeriodo = gestor.totalPeriodo(idPeriodoNomina, "costoTotalEmpleador");
    p.estaCerrado = true;
    p.estado = "CERRADO";
    return p;
}

PeriodoNomina& CicloVidaNomina::crearPeriodoNominaMensual(int anio, int mes) {
    int ultDia = diasEnMes(anio, mes);
    PeriodoNomina p;
    p.anio = anio;
    p.mes = mes;

    std::ostringstream ssIni, ssFin;
    ssIni << anio << "-" << (mes < 10 ? "0" : "") << mes << "-01";
    ssFin << anio << "-" << (mes < 10 ? "0" : "") << mes << "-" << (ultDia < 10 ? "0" : "") << ultDia;

    p.fechaInicio = ssIni.str();
    p.fechaFin = ssFin.str();
    p.fechaPago = ssFin.str();
    p.tipoPeriodicidad = "MENSUAL";
    p.diasBaseLiquidacion = 30;
    p.estado = "ABIERTO";

    return crearPeriodoNomina(p);
}

LiquidacionNomina& CicloVidaNomina::aprobarLiquidacion(int idLiquidacion, const std::string& usuario) {
    LiquidacionNomina& l = gestor.liquidacion(idLiquidacion);
    PeriodoNomina& p = gestor.periodo(l.idPeriodoNomina.value_or(-1));
    if (p.estaCerrado.value_or(false)) {
        throw ErrorNomina("No se puede aprobar una liquidacion de un periodo cerrado");
    }
    if (usuario.empty()) {
        throw ErrorNomina("El usuario aprobador es obligatorio");
    }

    l.aprobada = true;
    l.fechaAprobacion = fecha_hoy();
    l.usuarioAprobador = usuario;
    l.estado = "APROBADA";
    return l;
}

LiquidacionNomina& CicloVidaNomina::pagarLiquidacion(int idLiquidacion, const std::string& medioPago, const std::string& referencia) {
    LiquidacionNomina& l = gestor.liquidacion(idLiquidacion);
    PeriodoNomina& p = gestor.periodo(l.idPeriodoNomina.value_or(-1));
    gestor.validarPeriodoAbierto(p);

    if (!l.aprobada.value_or(false)) {
        throw ErrorNomina("Solo se puede pagar una liquidacion aprobada");
    }
    if (medioPago.empty() || referencia.empty()) {
        throw ErrorNomina("Medio y referencia de pago son obligatorios");
    }

    l.pagada = true;
    l.fechaPago = fecha_hoy();
    l.medioPago = medioPago;
    l.referenciaPago = referencia;
    l.estado = "PAGADA";
    return l;
}

LiquidacionNomina CicloVidaNomina::reliquidar(int idLiquidacion) {
    LiquidacionNomina& orig = gestor.liquidacion(idLiquidacion);
    if (orig.pagada.value_or(false)) {
        throw ErrorNomina("No se puede reliquidar una liquidacion ya pagada");
    }

    int nuevaVersion = orig.version.value_or(0) + 1;
    PeriodoNomina& p = gestor.periodo(orig.idPeriodoNomina.value_or(-1));
    gestor.validarPeriodoAbierto(p);
    gestor.evitarLiquidacionDuplicadaVersion(orig.idContrato.value_or(-1), orig.idPeriodoNomina.value_or(-1), idLiquidacion);

    std::string fechaLiq = orig.fechaLiquidacion.value_or("");

    LiquidacionNomina nueva;
    if (!orig.tipoProfesorLiquidado.has_value() ||
        (orig.regimenLiquidado.has_value() &&
         (orig.regimenLiquidado->find("ADMINISTRATIVO") != std::string::npos || orig.regimenLiquidado->find("CST") != std::string::npos))) {
        nueva = gestor.liquidadorAdministrativo.liquidar(*orig.idContrato, *orig.idPeriodoNomina, fechaLiq);
    } else {
        TipoProfesor tipo = *orig.tipoProfesorLiquidado;
        if (tipo == TipoProfesor::PLANTA) {
            nueva = gestor.liquidadorPlanta.liquidar(*orig.idContrato, *orig.idPeriodoNomina, fechaLiq);
        } else if (tipo == TipoProfesor::OCASIONAL) {
            double horasInc = orig.horasIncumplidas.value_or(0.0);
            nueva = gestor.liquidadorOcasional.liquidar(*orig.idContrato, *orig.idPeriodoNomina, horasInc, fechaLiq);
        } else if (tipo == TipoProfesor::CATEDRATICO) {
            nueva = gestor.liquidadorCatedratico.liquidar(*orig.idContrato, *orig.idPeriodoNomina, fechaLiq);
        } else {
            throw ErrorNomina("Tipo de vinculacion no soportado para reliquidacion");
        }
    }

    nueva.version = nuevaVersion;
    nueva.liquidacionOrigen = idLiquidacion;
    orig.requiereReliquidacion = true;
    orig.motivoReliquidacion = "Reliquidacion version " + std::to_string(nuevaVersion) + " solicitada";

    gestor.eliminarDetallesVersion(idLiquidacion);
    return nueva;
}

bool CicloVidaNomina::tieneHistorialLiquidacion(const LiquidacionNomina& l) const {
    return (l.pagada.value_or(false) ||
            l.requiereReliquidacion.value_or(false) ||
            (l.version.has_value() && *l.version > 0) ||
            (l.estado.has_value() && *l.estado == "RELIQUIDADA"));
}

LiquidacionNomina& CicloVidaNomina::desactivarLiquidacion(int idLiquidacion) {
    LiquidacionNomina& l = gestor.liquidacion(idLiquidacion);
    l.estado = "INACTIVO";
    l.fechaGeneracion = fecha_hoy();
    return l;
}

LiquidacionNomina& CicloVidaNomina::reactivarLiquidacion(int idLiquidacion) {
    LiquidacionNomina& l = gestor.liquidacion(idLiquidacion);
    l.estado = "PROCESADA";
    return l;
}

void CicloVidaNomina::eliminarLiquidacion(int idLiquidacion) {
    LiquidacionNomina& l = gestor.liquidacion(idLiquidacion);
    if (tieneHistorialLiquidacion(l)) {
        desactivarLiquidacion(idLiquidacion);
        return;
    }

    gestor.liquidaciones.remove_if([idLiquidacion](const LiquidacionNomina& item) {
        return item.idLiquidacion.has_value() && *item.idLiquidacion == idLiquidacion;
    });
    gestor.detallesLiquidacion.remove_if([idLiquidacion](const DetalleLiquidacion& item) {
        return item.idLiquidacion.has_value() && *item.idLiquidacion == idLiquidacion;
    });
}

std::map<std::string, double> CicloVidaNomina::resumenNominaPeriodo(int idPeriodoNomina) {
    auto liqs = gestor.liquidacionesPeriodo(idPeriodoNomina);
    std::map<std::string, double> res;
    if (liqs.empty()) {
        res["total_liquidaciones"] = 0.0;
        res["total_devengado"] = 0.0;
        res["total_descuentos"] = 0.0;
        res["total_prestaciones"] = 0.0;
        res["total_aportes"] = 0.0;
        res["costo_total"] = 0.0;
        return res;
    }

    double totalAportes = 0.0;
    for (const auto& l : liqs) {
        totalAportes += GestorNomina::aportes(l);
    }

    res["total_liquidaciones"] = static_cast<double>(liqs.size());
    res["total_devengado"] = gestor.totalPeriodo(idPeriodoNomina, "totalDevengado");
    res["total_descuentos"] = gestor.totalPeriodo(idPeriodoNomina, "totalDescuentos");
    res["total_prestaciones"] = gestor.totalPeriodo(idPeriodoNomina, "totalPrestaciones");
    res["total_aportes"] = totalAportes;
    res["costo_total"] = gestor.totalPeriodo(idPeriodoNomina, "costoTotalEmpleador");
    return res;
}

std::map<std::string, std::map<std::string, double>> CicloVidaNomina::totalesPorTipoProfesor(int idPeriodoNomina) {
    auto liqs = gestor.liquidacionesPeriodo(idPeriodoNomina);
    std::map<std::string, std::map<std::string, double>> resultado;

    for (const auto& liq : liqs) {
        std::string tipo = liq.tipoProfesorLiquidado.has_value() ? to_string(*liq.tipoProfesorLiquidado) : "ADMINISTRATIVO";
        resultado[tipo]["cantidad"] += 1.0;
        resultado[tipo]["total_devengado"] += liq.totalDevengado.value_or(0.0);
        resultado[tipo]["total_descuentos"] += liq.totalDescuentos.value_or(0.0);
        resultado[tipo]["neto"] += liq.netoPagar.value_or(0.0);
    }

    for (auto& kv : resultado) {
        for (auto& inner : kv.second) {
            inner.second = GestorNomina::redondear(inner.second);
        }
    }
    return resultado;
}

// ==========================================
// GESTOR NOMINA (FACHADA)
// ==========================================

GestorNomina::GestorNomina(
    ListaEnlazada<Contrato>& contratos,
    ListaEnlazada<Profesor>& profesores,
    ListaEnlazada<PeriodoNomina>& periodosNomina,
    ListaEnlazada<LiquidacionNomina>& liquidaciones,
    ListaEnlazada<ParametroNormativo>& parametros,
    ListaEnlazada<DetalleLiquidacion>& detallesLiquidacion,
    ListaEnlazada<CategoriaDocente>& categorias,
    ListaEnlazada<FactorSalarial>& factores,
    ListaEnlazada<ProduccionAcademica>& producciones,
    ListaEnlazada<Administrativo>* administrativos
) : contratos(contratos),
    profesores(profesores),
    periodosNomina(periodosNomina),
    liquidaciones(liquidaciones),
    parametros(parametros),
    detallesLiquidacion(detallesLiquidacion),
    categorias(categorias),
    factores(factores),
    producciones(producciones),
    administrativos(administrativos),
    calcDeducciones(this->parametros),
    calcPrestaciones(this->calcDeducciones),
    liquidadorPlanta(*this),
    liquidadorOcasional(*this),
    liquidadorCatedratico(*this),
    liquidadorAdministrativo(*this),
    cicloVida(*this) {}

double GestorNomina::redondear(double valor) {
    return std::round(valor * 100.0) / 100.0;
}

int GestorNomina::siguienteId() {
    int maxId = 0;
    for (const auto& l : liquidaciones) {
        if (l.idLiquidacion.has_value() && *l.idLiquidacion > maxId) {
            maxId = *l.idLiquidacion;
        }
    }
    return maxId + 1;
}

int GestorNomina::siguienteIdDetalle() {
    int maxId = 0;
    for (const auto& d : detallesLiquidacion) {
        if (d.idDetalleLiquidacion.has_value() && *d.idDetalleLiquidacion > maxId) {
            maxId = *d.idDetalleLiquidacion;
        }
    }
    return maxId + 1;
}

Contrato& GestorNomina::contrato(int idContrato) {
    for (auto& c : contratos) {
        if (c.idContrato.has_value() && *c.idContrato == idContrato) {
            return c;
        }
    }
    throw ErrorNomina("No existe el contrato con ID " + std::to_string(idContrato));
}

PeriodoNomina& GestorNomina::periodo(int idPeriodo) {
    for (auto& p : periodosNomina) {
        if (p.idPeriodoNomina.has_value() && *p.idPeriodoNomina == idPeriodo) {
            return p;
        }
    }
    throw ErrorNomina("No existe el periodo de nomina con ID " + std::to_string(idPeriodo));
}

Profesor& GestorNomina::profesor(std::optional<int> idPersona) {
    if (!idPersona.has_value()) throw ErrorNomina("ID de persona requerido para buscar profesor");
    for (auto& p : profesores) {
        if (p.idPersona.has_value() && *p.idPersona == *idPersona) {
            return p;
        }
    }
    throw ErrorNomina("No existe el profesor con idPersona " + std::to_string(*idPersona));
}

Administrativo* GestorNomina::administrativo(std::optional<int> idPersona) {
    if (!idPersona.has_value() || !administrativos) return nullptr;
    for (size_t i = 0; i < administrativos->tamano(); ++i) {
        auto& a = administrativos->obtener(i);
        if (a.idPersona.has_value() && *a.idPersona == *idPersona) {
            return &a;
        }
    }
    return nullptr;
}

LiquidacionNomina& GestorNomina::liquidacion(int idLiquidacion) {
    for (auto& l : liquidaciones) {
        if (l.idLiquidacion.has_value() && *l.idLiquidacion == idLiquidacion) {
            return l;
        }
    }
    throw ErrorNomina("No existe la liquidacion con ID " + std::to_string(idLiquidacion));
}

void GestorNomina::validarPeriodoAbierto(const PeriodoNomina& p) {
    if (p.estaCerrado.value_or(false) || (p.estado.has_value() && a_mayusculas(*p.estado) == "CERRADO")) {
        throw ErrorNomina("El periodo de nomina esta cerrado");
    }
}

void GestorNomina::evitarLiquidacionDuplicada(int idContrato, int idPeriodoNomina) {
    for (const auto& l : liquidaciones) {
        if (l.idContrato.has_value() && *l.idContrato == idContrato &&
            l.idPeriodoNomina.has_value() && *l.idPeriodoNomina == idPeriodoNomina &&
            (!l.estado.has_value() || *l.estado != "RELIQUIDADA")) {
            throw ErrorNomina("Ya existe una liquidacion para ese contrato y periodo");
        }
    }
}

void GestorNomina::evitarLiquidacionDuplicadaVersion(int idContrato, int idPeriodoNomina, int idLiquidacionOrigen) {
    for (const auto& l : liquidaciones) {
        if (l.idContrato.has_value() && *l.idContrato == idContrato &&
            l.idPeriodoNomina.has_value() && *l.idPeriodoNomina == idPeriodoNomina &&
            l.version.has_value() &&
            (!l.estado.has_value() || *l.estado != "RELIQUIDADA") &&
            l.idLiquidacion.value_or(-1) != idLiquidacionOrigen) {
            throw ErrorNomina("Ya existe una version de liquidacion para ese contrato y periodo");
        }
    }
}

ListaEnlazada<LiquidacionNomina> GestorNomina::liquidacionesPeriodo(int idPeriodoNomina) {
    ListaEnlazada<LiquidacionNomina> res;
    for (const auto& l : liquidaciones) {
        if (l.idPeriodoNomina.has_value() && *l.idPeriodoNomina == idPeriodoNomina) {
            res.push_back(l);
        }
    }
    return res;
}

double GestorNomina::totalPeriodo(int idPeriodoNomina, const std::string& campo) {
    double total = 0.0;
    for (const auto& l : liquidacionesPeriodo(idPeriodoNomina)) {
        if (campo == "totalDevengado") total += l.totalDevengado.value_or(0.0);
        else if (campo == "totalDescuentos") total += l.totalDescuentos.value_or(0.0);
        else if (campo == "totalPrestaciones") total += l.totalPrestaciones.value_or(0.0);
        else if (campo == "costoTotalEmpleador") total += l.costoTotalEmpleador.value_or(0.0);
    }
    return redondear(total);
}

double GestorNomina::aportes(const LiquidacionNomina& l) {
    return l.aportePatronalSalud.value_or(0.0) +
           l.aportePatronalPension.value_or(0.0) +
           l.aporteRiesgosLaborales.value_or(0.0) +
           l.aporteCajaCompensacion.value_or(0.0) +
           l.aportePatronalSENA.value_or(0.0) +
           l.aportePatronalICBF.value_or(0.0);
}

bool GestorNomina::esRegimen1279(const std::optional<std::string>& regimen) {
    if (!regimen.has_value() || regimen->empty()) return true;
    std::string s = a_mayusculas(*regimen);
    return s.find("1279") != std::string::npos || s.find("PLANTA") != std::string::npos || s.find("ESPECIAL") != std::string::npos;
}

double GestorNomina::puntosPlanta(const Profesor& prof, const PeriodoNomina& per) {
    std::string catDoc = prof.categoriaDocente.has_value() ? a_mayusculas(*prof.categoriaDocente) : "";
    std::string catRec = prof.categoriaReconocida.has_value() ? a_mayusculas(*prof.categoriaReconocida) : "";

    bool tieneCat = false;
    for (const auto& c : categorias) {
        std::string cCod = c.codigo.has_value() ? to_string(*c.codigo) : "";
        if (c.idCategoria == prof.idCategoriaDocente || cCod == catDoc || cCod == catRec) {
            tieneCat = true;
            break;
        }
    }

    bool tieneFact = false;
    for (const auto& f : factores) {
        if (f.idProfesor == prof.idProfesor) {
            tieneFact = true;
            break;
        }
    }

    bool tieneProd = false;
    for (const auto& p : producciones) {
        if (p.idProfesor == prof.idProfesor) {
            tieneProd = true;
            break;
        }
    }

    double pts = 0.0;
    if (tieneCat || tieneFact || tieneProd) {
        GestorFactores gf(categorias, factores, producciones, profesores);
        std::string fecha = per.fechaFin.value_or(per.fechaInicio.value_or(fecha_hoy()));
        pts = gf.calcularPuntosProfesor(*prof.idProfesor, fecha);
    } else {
        pts = prof.puntosSalariales.value_or(0.0);
    }

    // Decreto 1279: Pisos mínimos de escalafón por categoría (Auxiliar: 37, Asistente: 58, Asociado: 74, Titular: 96)
    double piso = 0.0;
    std::string catBusqueda = catDoc.empty() ? catRec : catDoc;
    if (catBusqueda.find("TITULAR") != std::string::npos) {
        piso = 96.0;
    } else if (catBusqueda.find("ASOCIADO") != std::string::npos) {
        piso = 74.0;
    } else if (catBusqueda.find("ASISTENTE") != std::string::npos) {
        piso = 58.0;
    } else if (catBusqueda.find("AUXILIAR") != std::string::npos) {
        piso = 37.0;
    }
    if (pts < piso) {
        pts = piso;
    }
    return pts;
}

double GestorNomina::salarioMinimo(const Contrato& c, const PeriodoNomina& p, const std::string& fecha, std::map<std::string, std::string>* codigosUtilizados) {
    auto val = calcDeducciones.obtenerParametroDecimal("SALARIO_MINIMO", fecha);
    if (val.has_value() && *val > 0.0) {
        if (codigosUtilizados) {
            (*codigosUtilizados)["SALARIO_MINIMO"] = std::to_string(*val);
        }
        return *val;
    }
    if (p.salarioMinimoVigente.has_value() && *p.salarioMinimoVigente > 0.0) {
        if (codigosUtilizados) {
            (*codigosUtilizados)["SALARIO_MINIMO"] = std::to_string(*p.salarioMinimoVigente);
        }
        return *p.salarioMinimoVigente;
    }
    if (c.salarioMinimoVigente.has_value() && *c.salarioMinimoVigente > 0.0) {
        if (codigosUtilizados) {
            (*codigosUtilizados)["SALARIO_MINIMO"] = std::to_string(*c.salarioMinimoVigente);
        }
        return *c.salarioMinimoVigente;
    }
    return 1750905.0;
}

void GestorNomina::validarContrato(const Contrato& c, TipoProfesor tipo, const PeriodoNomina& p) {
    std::string actual = c.modalidadProfesor.has_value() ? a_mayusculas(*c.modalidadProfesor) :
                        (c.tipoContrato.has_value() ? a_mayusculas(*c.tipoContrato) : "");

    size_t pos = actual.find("DOCENTE_");
    if (pos != std::string::npos) actual.erase(pos, 8);

    std::string esperado = to_string(tipo);
    pos = esperado.find("DOCENTE_");
    if (pos != std::string::npos) esperado.erase(pos, 8);

    bool coincide = (actual == esperado);
    if (tipo == TipoProfesor::CATEDRATICO) {
        if (actual == "CATEDRATICO_AD_HONOREM" || actual == "AD_HONOREM") coincide = true;
    }

    if (!coincide) {
        throw ErrorNomina("El contrato no es de tipo " + esperado);
    }

    std::string est = c.estado.has_value() ? a_mayusculas(*c.estado) : "";
    if (est != "ACTIVO") {
        throw ErrorNomina("El contrato no esta activo");
    }

    std::string iniPer = p.fechaInicio.value_or(p.fechaFin.value_or(fecha_hoy()));
    std::string finPer = p.fechaFin.value_or(iniPer);

    if (c.fechaInicio.has_value() && !c.fechaInicio->empty() && *c.fechaInicio > finPer) {
        throw ErrorNomina("El contrato inicia despues del periodo de liquidacion");
    }
    if (c.fechaFin.has_value() && !c.fechaFin->empty() && *c.fechaFin < iniPer) {
        throw ErrorNomina("El contrato termino antes del periodo de liquidacion");
    }
}

void GestorNomina::validarHorasIncumplidas(const Contrato& c, double horasIncumplidas) {
    if (horasIncumplidas == 0.0) return;
    if (c.requiereCertificacionCumplimiento.value_or(false) && (!c.certificacionCumplimiento.has_value() || c.certificacionCumplimiento->empty())) {
        throw ErrorNomina("Las horas incumplidas requieren certificacion de cumplimiento segun el art. 87 del decreto sustantivo de la materia");
    }
    double horasSemanales = c.horasSemanalesAsignadas.value_or(c.horasSemanales.value_or(0.0));
    double horasMensualesEstimadas = horasSemanales * 30.0 / 7.0;

    if (horasSemanales <= 0.0) {
        throw ErrorNomina("Se requieren horas asignadas para descontar incumplimientos en el contrato");
    }
    if (horasIncumplidas > horasMensualesEstimadas) {
        throw ErrorNomina("Las horas incumplidas no pueden superar las horas mensuales estimadas");
    }
}

void GestorNomina::eliminarDetallesVersion(int idLiquidacionOriginal) {
    detallesLiquidacion.remove_if([idLiquidacionOriginal](const DetalleLiquidacion& d) {
        return d.idLiquidacion.has_value() && *d.idLiquidacion == idLiquidacionOriginal;
    });
}

LiquidacionNomina GestorNomina::liquidarProfesorOcasional(int idContrato, int idPeriodoNomina, std::optional<double> horasIncumplidas, const std::string& fechaLiquidacion) {
    return liquidadorOcasional.liquidar(idContrato, idPeriodoNomina, horasIncumplidas, fechaLiquidacion);
}

LiquidacionNomina GestorNomina::liquidarProfesorPlanta(int idContrato, int idPeriodoNomina, const std::string& fechaLiquidacion) {
    return liquidadorPlanta.liquidar(idContrato, idPeriodoNomina, fechaLiquidacion);
}

LiquidacionNomina GestorNomina::liquidarProfesorCatedratico(int idContrato, int idPeriodoNomina, const std::string& fechaLiquidacion) {
    return liquidadorCatedratico.liquidar(idContrato, idPeriodoNomina, fechaLiquidacion);
}

LiquidacionNomina GestorNomina::liquidarAdministrativo(int idContrato, int idPeriodoNomina, const std::string& fechaLiquidacion) {
    return liquidadorAdministrativo.liquidar(idContrato, idPeriodoNomina, fechaLiquidacion);
}

LiquidacionNomina GestorNomina::crearLiquidacion(LiquidacionNomina liq) {
    Contrato& c = contrato(liq.idContrato.value_or(-1));
    PeriodoNomina& p = periodo(liq.idPeriodoNomina.value_or(-1));
    validarPeriodoAbierto(p);
    evitarLiquidacionDuplicada(liq.idContrato.value_or(-1), liq.idPeriodoNomina.value_or(-1));

    std::string tipo = c.modalidadProfesor.has_value() ? a_mayusculas(*c.modalidadProfesor) :
                      (c.tipoContrato.has_value() ? a_mayusculas(*c.tipoContrato) : "");

    LiquidacionNomina resultado;
    if (tipo.find("ADMINISTRATIVO") != std::string::npos) {
        resultado = liquidarAdministrativo(*liq.idContrato, *liq.idPeriodoNomina);
    } else if (tipo.find("OCASIONAL") != std::string::npos) {
        resultado = liquidarProfesorOcasional(*liq.idContrato, *liq.idPeriodoNomina, liq.horasIncumplidas.value_or(0.0));
    } else if (tipo.find("PLANTA") != std::string::npos) {
        resultado = liquidarProfesorPlanta(*liq.idContrato, *liq.idPeriodoNomina);
    } else if (tipo.find("CATEDRATICO") != std::string::npos) {
        resultado = liquidarProfesorCatedratico(*liq.idContrato, *liq.idPeriodoNomina);
    } else {
        resultado = liquidarProfesorOcasional(*liq.idContrato, *liq.idPeriodoNomina, liq.horasIncumplidas.value_or(0.0));
    }

    resultado.fechaLiquidacion = liq.fechaLiquidacion.value_or(fecha_hoy());
    resultado.estado = liq.estado.value_or("PROCESADA");
    return resultado;
}

PeriodoNomina& GestorNomina::crearPeriodoNomina(PeriodoNomina periodo) {
    return cicloVida.crearPeriodoNomina(periodo);
}

PeriodoNomina& GestorNomina::abrirPeriodoNomina(int idPeriodoNomina) {
    return cicloVida.abrirPeriodoNomina(idPeriodoNomina);
}

PeriodoNomina& GestorNomina::cerrarPeriodoNomina(int idPeriodoNomina) {
    return cicloVida.cerrarPeriodoNomina(idPeriodoNomina);
}

PeriodoNomina& GestorNomina::crearPeriodoNominaMensual(int anio, int mes) {
    return cicloVida.crearPeriodoNominaMensual(anio, mes);
}

LiquidacionNomina& GestorNomina::aprobarLiquidacion(int idLiquidacion, const std::string& usuario) {
    return cicloVida.aprobarLiquidacion(idLiquidacion, usuario);
}

LiquidacionNomina& GestorNomina::pagarLiquidacion(int idLiquidacion, const std::string& medioPago, const std::string& referencia) {
    return cicloVida.pagarLiquidacion(idLiquidacion, medioPago, referencia);
}

LiquidacionNomina GestorNomina::reliquidar(int idLiquidacion) {
    return cicloVida.reliquidar(idLiquidacion);
}

ListaEnlazada<LiquidacionNomina> GestorNomina::consultarLiquidaciones(std::optional<int> idProfesor, std::optional<int> idPeriodoNomina) const {
    ListaEnlazada<LiquidacionNomina> res;
    for (const auto& l : liquidaciones) {
        if (idProfesor.has_value() && l.idProfesor != idProfesor) continue;
        if (idPeriodoNomina.has_value() && l.idPeriodoNomina != idPeriodoNomina) continue;
        res.push_back(l);
    }
    return res;
}

ListaEnlazada<DetalleLiquidacion> GestorNomina::consultarDetallesLiquidacion(int idLiquidacion) const {
    ListaEnlazada<DetalleLiquidacion> res;
    for (const auto& d : detallesLiquidacion) {
        if (d.idLiquidacion.has_value() && *d.idLiquidacion == idLiquidacion) {
            res.push_back(d);
        }
    }
    return res;
}

std::map<std::string, double> GestorNomina::resumenNominaPeriodo(int idPeriodoNomina) {
    return cicloVida.resumenNominaPeriodo(idPeriodoNomina);
}

std::map<std::string, std::map<std::string, double>> GestorNomina::totalesPorTipoProfesor(int idPeriodoNomina) {
    return cicloVida.totalesPorTipoProfesor(idPeriodoNomina);
}

} // namespace pita
