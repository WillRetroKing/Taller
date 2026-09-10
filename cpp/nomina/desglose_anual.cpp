#include "desglose_anual.h"
#include "gestor_nomina.h"
#include <cmath>
#include <sstream>
#include <iomanip>
#include <algorithm>

namespace pita {

static std::string a_mayusculas(std::string s) {
    std::transform(s.begin(), s.end(), s.begin(), [](unsigned char c) { return std::toupper(c); });
    return s;
}

static std::string formatearMoneda(double valor) {
    long long entero = static_cast<long long>(std::round(valor));
    std::string s = std::to_string(std::abs(entero));
    std::string res;
    int count = 0;
    for (int i = static_cast<int>(s.length()) - 1; i >= 0; --i) {
        res.insert(res.begin(), s[i]);
        count++;
        if (count % 3 == 0 && i > 0) {
            res.insert(res.begin(), '.');
        }
    }
    std::string signo = (entero < 0) ? "-$" : "$";
    return signo + " " + res + " COP";
}

double CalculadorDesgloseAnual::redondear(double valor) {
    return std::round(valor * 100.0) / 100.0;
}

CalculadorDesgloseAnual::CalculadorDesgloseAnual(GestorNomina& gestor, const ListaEnlazada<Persona>* personas)
    : gestor(gestor), personas(personas) {}

Profesor* CalculadorDesgloseAnual::obtenerProfesor(std::optional<int> idPersona) {
    if (!idPersona.has_value()) return nullptr;
    for (auto& p : gestor.profesores) {
        if (p.idPersona == idPersona) return &p;
    }
    return nullptr;
}

Persona* CalculadorDesgloseAnual::obtenerPersona(std::optional<int> idPersona) {
    if (!idPersona.has_value() || !personas) return nullptr;
    for (auto& p : const_cast<ListaEnlazada<Persona>&>(*personas)) {
        if (p.idPersona == idPersona) return &p;
    }
    return nullptr;
}

DesgloseNominaAnual CalculadorDesgloseAnual::generarDesglosePorContrato(
    int idContrato,
    int anio,
    bool /*proyectar12Meses*/
) {
    Contrato& c = gestor.contrato(idContrato);
    Profesor* prof = obtenerProfesor(c.idPersona);
    Persona* pers = obtenerPersona(c.idPersona);

    std::string nombre = "Empleado #" + std::to_string(idContrato);
    std::string doc = "";
    if (pers) {
        std::string pNom = pers->primerNombre.value_or("");
        std::string sNom = pers->segundoNombre.value_or("");
        std::string pApe = pers->primerApellido.value_or("");
        std::string sApe = pers->segundoApellido.value_or("");
        std::string nomComp = pNom;
        if (!sNom.empty()) nomComp += " " + sNom;
        if (!pApe.empty()) nomComp += " " + pApe;
        if (!sApe.empty()) nomComp += " " + sApe;
        if (!nomComp.empty()) nombre = nomComp;
        doc = pers->numeroDocumento.value_or("");
    } else if (prof) {
        nombre = "Profesor #" + std::to_string(prof->idProfesor.value_or(idContrato));
    }

    std::string modContra = c.modalidadProfesor.value_or(c.tipoContrato.value_or("PLANTA"));
    modContra = a_mayusculas(modContra);
    std::string regAplicable = c.regimenAplicable.value_or("GENERAL");
    regAplicable = a_mayusculas(regAplicable);

    std::string tipoPersonal = "PLANTA";
    if (modContra.find("ADMINISTRATIVO") != std::string::npos || regAplicable.find("ADMINISTRATIVO") != std::string::npos) {
        tipoPersonal = "ADMINISTRATIVO";
    } else if (modContra.find("CATEDRATICO") != std::string::npos || modContra.find("CATEDRA") != std::string::npos) {
        tipoPersonal = "CATEDRATICO";
    } else if (modContra.find("OCASIONAL") != std::string::npos) {
        tipoPersonal = "OCASIONAL";
    } else if (modContra.find("PLANTA") != std::string::npos) {
        tipoPersonal = "PLANTA";
    }

    int mesesVigencia = 12;
    if (tipoPersonal == "PLANTA" || tipoPersonal == "ADMINISTRATIVO") {
        mesesVigencia = 12;
    } else if (c.fechaInicio.has_value() && c.fechaFin.has_value() &&
               c.fechaInicio->length() >= 7 && c.fechaFin->length() >= 7) {
        try {
            int yIni = std::stoi(c.fechaInicio->substr(0, 4));
            int mIni = std::stoi(c.fechaInicio->substr(5, 2));
            int yFin = std::stoi(c.fechaFin->substr(0, 4));
            int mFin = std::stoi(c.fechaFin->substr(5, 2));

            if (yIni == anio && yFin == anio) {
                mesesVigencia = std::max(1, (yFin - yIni) * 12 + mFin - mIni + 1);
            } else if (yIni == anio) {
                mesesVigencia = std::max(1, 12 - mIni + 1);
            } else if (yFin == anio) {
                mesesVigencia = std::max(1, mFin);
            }
        } catch (...) {
            mesesVigencia = 11;
        }
    } else {
        mesesVigencia = 11;
    }

    int diasAnio = mesesVigencia * 30;

    // Buscar liquidación mensual base
    LiquidacionNomina* liqExistente = nullptr;
    for (auto& l : gestor.liquidaciones) {
        if (l.idContrato == idContrato && l.idPeriodoNomina.value_or(0) != 9999) {
            liqExistente = &l;
            break;
        }
    }

    LiquidacionNomina liqBase;
    bool fueSimulada = false;
    if (liqExistente) {
        liqBase = *liqExistente;
    } else {
        // Simular liquidación
        int idPer = 1;
        if (!gestor.periodosNomina.empty() && gestor.periodosNomina.front().idPeriodoNomina.has_value()) {
            idPer = *gestor.periodosNomina.front().idPeriodoNomina;
        }

        try {
            if (tipoPersonal == "ADMINISTRATIVO") {
                liqBase = gestor.liquidarAdministrativo(idContrato, idPer);
            } else if (tipoPersonal == "PLANTA") {
                liqBase = gestor.liquidarProfesorPlanta(idContrato, idPer);
            } else if (tipoPersonal == "CATEDRATICO") {
                liqBase = gestor.liquidarProfesorCatedratico(idContrato, idPer);
            } else {
                liqBase = gestor.liquidarProfesorOcasional(idContrato, idPer);
            }
            fueSimulada = true;
        } catch (...) {
            // Valores fallback si no hay período
            liqBase.salarioBase = c.salarioBase.value_or(1750905.0);
            liqBase.salarioOrdinario = liqBase.salarioBase;
            liqBase.totalDevengado = liqBase.salarioBase;
            liqBase.totalDescuentos = 0.0;
            liqBase.netoPagar = liqBase.salarioBase;
        }

        // Limpiar la liquidación simulada del gestor
        if (fueSimulada && !gestor.liquidaciones.empty()) {
            gestor.liquidaciones.pop_back();
        }
    }

    double mesesMult = static_cast<double>(mesesVigencia);

    DesgloseNominaAnual d;
    d.idContrato = idContrato;
    d.idPersona = c.idPersona;
    d.nombreCompleto = nombre;
    d.identificacion = doc;
    d.tipoPersonal = tipoPersonal;
    d.regimen = regAplicable;
    d.anio = anio;
    d.mesesConsiderados = mesesVigencia;
    d.diasTrabajadosAnio = diasAnio;

    // 1. Devengados Anuales
    double salOrd = redondear(liqBase.salarioOrdinario.value_or(liqBase.salarioBase.value_or(0.0)));
    double bonPos = redondear(liqBase.bonificacionPosgrado.value_or(0.0));
    double bonInv = redondear(liqBase.bonificacionInvestigacion.value_or(0.0));
    double otrasBon = redondear(
        liqBase.bonificacionesSalariales.value_or(0.0) +
        liqBase.bonificacionesNoSalariales.value_or(0.0) - bonPos - bonInv
    );
    if (otrasBon < 0.0) otrasBon = 0.0;
    double auxTrans = redondear(liqBase.valorAuxilioTransporteCotizado.value_or(0.0));

    d.salarioOrdinarioAnual = redondear(salOrd * mesesMult);
    d.bonificacionesPosgradoAnual = redondear(bonPos * mesesMult);
    d.bonificacionesInvestigacionAnual = redondear(bonInv * mesesMult);
    d.otrasBonificacionesAnual = redondear(otrasBon * mesesMult);
    d.auxilioTransporteAnual = redondear(auxTrans * mesesMult);
    d.totalDevengadoAnual = redondear(
        d.salarioOrdinarioAnual + d.bonificacionesPosgradoAnual +
        d.bonificacionesInvestigacionAnual + d.otrasBonificacionesAnual +
        d.auxilioTransporteAnual
    );

    // 2. Deducciones Anuales
    double descSalud = redondear(liqBase.descuentoSalud.value_or(0.0));
    double descPens = redondear(liqBase.descuentoPension.value_or(0.0));
    double fsp = redondear(liqBase.fondoSolidaridadPensional.value_or(0.0));
    double retFuente = redondear(liqBase.retencionFuente.value_or(0.0));
    double estamp = redondear(liqBase.otrosDescuentos.value_or(0.0));

    d.descuentoSaludAnual = redondear(descSalud * mesesMult);
    d.descuentoPensionAnual = redondear(descPens * mesesMult);
    d.fondoSolidaridadAnual = redondear(fsp * mesesMult);
    d.retencionFuenteAnual = redondear(retFuente * mesesMult);
    d.estampillasAnual = redondear(estamp * mesesMult);
    d.totalDescuentosAnual = redondear(
        d.descuentoSaludAnual + d.descuentoPensionAnual +
        d.fondoSolidaridadAnual + d.retencionFuenteAnual + d.estampillasAnual
    );
    d.totalDeduccionesAnual = d.totalDescuentosAnual;

    // 3. Neto Anual
    d.netoAnualTrabajador = redondear(d.totalDevengadoAnual - d.totalDescuentosAnual);

    // 4. Prestaciones Sociales Consolidadas Anuales
    double diasDec = static_cast<double>(diasAnio);
    double basePrest = redondear(liqBase.baseLiquidacionPrestaciones.value_or(salOrd));
    double baseIbc = redondear(liqBase.baseSeguridadSocial.value_or(salOrd));

    d.cesantiasAnuales = redondear(basePrest * diasDec / 360.0);
    d.interesesCesantiasAnuales = redondear(d.cesantiasAnuales * 0.12 * diasDec / 360.0);
    d.primaServiciosAnual = redondear(basePrest * diasDec / 360.0);

    if (tipoPersonal == "PLANTA") {
        double tope = 756411.0;
        double pctBon = (baseIbc <= tope) ? 0.50 : 0.35;
        d.bonificacionServiciosAnual = redondear(baseIbc * pctBon * diasDec / 360.0);

        double basePVac = (baseIbc * 2.0 / 3.0) + (d.primaServiciosAnual / 12.0) + (d.bonificacionServiciosAnual / 12.0);
        d.primaVacacionesAnual = redondear(basePVac * diasDec / 540.0);

        double baseVac = baseIbc + (d.primaServiciosAnual / 12.0) + (d.bonificacionServiciosAnual / 12.0);
        d.vacacionesAnuales = redondear(baseVac * diasDec / 720.0);

        double baseNav = baseIbc + (d.primaServiciosAnual / 12.0) + (d.primaVacacionesAnual / 12.0) + (d.bonificacionServiciosAnual / 12.0);
        d.primaNavidadAnual = redondear(baseNav * diasDec / 360.0);
    } else {
        d.vacacionesAnuales = redondear(baseIbc * diasDec / 720.0);
        d.primaNavidadAnual = redondear(basePrest * diasDec / 360.0);
        d.primaVacacionesAnual = 0.0;
        d.bonificacionServiciosAnual = 0.0;
    }

    d.totalPrestacionesAnuales = redondear(
        d.cesantiasAnuales + d.interesesCesantiasAnuales +
        d.primaServiciosAnual + d.primaNavidadAnual +
        d.vacacionesAnuales + d.primaVacacionesAnual +
        d.bonificacionServiciosAnual
    );

    // 5. Aportes Patronales Anuales
    double salPat = redondear(liqBase.aportePatronalSalud.value_or(0.0));
    double penPat = redondear(liqBase.aportePatronalPension.value_or(0.0));
    double arlPat = redondear(liqBase.aporteRiesgosLaborales.value_or(0.0));
    double cajaPat = redondear(liqBase.aporteCajaCompensacion.value_or(0.0));
    double senaPat = redondear(liqBase.aportePatronalSENA.value_or(0.0));
    double icbfPat = redondear(liqBase.aportePatronalICBF.value_or(0.0));

    d.saludPatronalAnual = redondear(salPat * mesesMult);
    d.pensionPatronalAnual = redondear(penPat * mesesMult);
    d.arlPatronalAnual = redondear(arlPat * mesesMult);
    d.cajaCompensacionAnual = redondear(cajaPat * mesesMult);
    d.senaAnual = redondear(senaPat * mesesMult);
    d.icbfAnual = redondear(icbfPat * mesesMult);
    d.totalAportesPatronalesAnual = redondear(
        d.saludPatronalAnual + d.pensionPatronalAnual +
        d.arlPatronalAnual + d.cajaCompensacionAnual +
        d.senaAnual + d.icbfAnual
    );

    // 6. Costo Total Institucional Anual
    d.costoTotalEmpleadorAnual = redondear(
        d.totalDevengadoAnual + d.totalPrestacionesAnuales +
        d.totalAportesPatronalesAnual
    );

    d.items = construirItemsDetalle(d, liqBase);
    return d;
}

std::vector<ItemDesgloseAnual> CalculadorDesgloseAnual::construirItemsDetalle(
    const DesgloseNominaAnual& d,
    const LiquidacionNomina& liq
) {
    std::vector<ItemDesgloseAnual> items;

    // DEVENGADOS
    items.push_back({
        "Salario Basico / Asignacion Ordinaria", "DEVENGADO",
        redondear(liq.salarioOrdinario.value_or(0.0)), "100%",
        redondear(liq.salarioOrdinario.value_or(0.0)),
        d.salarioOrdinarioAnual,
        std::to_string(d.mesesConsiderados) + " meses laborados (" + std::to_string(d.diasTrabajadosAnio) + " dias)"
    });

    if (d.bonificacionesPosgradoAnual > 0.0) {
        items.push_back({
            "Bonificacion por Posgrado (Acuerdo 027)", "DEVENGADO",
            redondear(liq.salarioMinimoUsado.value_or(1750905.0)), "Factor s/SMMLV",
            redondear(liq.bonificacionPosgrado.value_or(0.0)),
            d.bonificacionesPosgradoAnual,
            "No constitutivo de salario"
        });
    }

    if (d.bonificacionesInvestigacionAnual > 0.0) {
        items.push_back({
            "Bonificacion por Grupo de Investigacion", "DEVENGADO",
            redondear(liq.salarioMinimoUsado.value_or(1750905.0)), "Factor s/SMMLV",
            redondear(liq.bonificacionInvestigacion.value_or(0.0)),
            d.bonificacionesInvestigacionAnual,
            "Acreditado MinCiencias"
        });
    }

    if (d.auxilioTransporteAnual > 0.0) {
        items.push_back({
            "Auxilio de Transporte Legal", "DEVENGADO",
            0.0, "Ley 15/1959",
            redondear(liq.valorAuxilioTransporteCotizado.value_or(0.0)),
            d.auxilioTransporteAnual,
            "Aplica para salarios <= 2 SMMLV"
        });
    }

    // DEDUCCIONES
    items.push_back({
        "Aporte a Salud (Empleado)", "DEDUCCION",
        redondear(liq.baseSeguridadSocial.value_or(0.0)), "4.00%",
        redondear(liq.descuentoSalud.value_or(0.0)),
        d.descuentoSaludAnual,
        "Ley 100 de 1993"
    });

    items.push_back({
        "Aporte a Pension (Empleado)", "DEDUCCION",
        redondear(liq.baseSeguridadSocial.value_or(0.0)), "4.00%",
        redondear(liq.descuentoPension.value_or(0.0)),
        d.descuentoPensionAnual,
        "Ley 100 de 1993"
    });

    if (d.fondoSolidaridadAnual > 0.0) {
        items.push_back({
            "Fondo de Solidaridad Pensional", "DEDUCCION",
            redondear(liq.baseSeguridadSocial.value_or(0.0)), "1.00%",
            redondear(liq.fondoSolidaridadPensional.value_or(0.0)),
            d.fondoSolidaridadAnual,
            "Salarios > 4 SMMLV"
        });
    }

    if (d.retencionFuenteAnual > 0.0) {
        items.push_back({
            "Retencion en la Fuente", "DEDUCCION",
            redondear(liq.baseSeguridadSocial.value_or(0.0)), "Estatuto Tributario",
            redondear(liq.retencionFuente.value_or(0.0)),
            d.retencionFuenteAnual,
            "Retencion salarial"
        });
    }

    // PRESTACIONES SOCIALES
    items.push_back({
        "Cesantias Anuales", "PRESTACION",
        redondear(liq.baseLiquidacionPrestaciones.value_or(0.0)), "8.33%",
        redondear(d.cesantiasAnuales / d.mesesConsiderados),
        d.cesantiasAnuales,
        "Consignacion a fondo antes del 15 de febrero"
    });

    items.push_back({
        "Intereses sobre Cesantias", "PRESTACION",
        d.cesantiasAnuales, "12.00% anual",
        redondear(d.interesesCesantiasAnuales / d.mesesConsiderados),
        d.interesesCesantiasAnuales,
        "Pago directo en enero"
    });

    items.push_back({
        "Prima de Servicios", "PRESTACION",
        redondear(liq.baseLiquidacionPrestaciones.value_or(0.0)), "8.33%",
        redondear(d.primaServiciosAnual / d.mesesConsiderados),
        d.primaServiciosAnual,
        "Junio y Diciembre"
    });

    items.push_back({
        "Vacaciones Consolidadas", "PRESTACION",
        redondear(liq.baseSeguridadSocial.value_or(0.0)), "4.17%",
        redondear(d.vacacionesAnuales / d.mesesConsiderados),
        d.vacacionesAnuales,
        "Descanso remunerado anual"
    });

    if (d.primaVacacionesAnual > 0.0) {
        items.push_back({
            "Prima de Vacaciones (Dec. 1279)", "PRESTACION",
            redondear(liq.baseSeguridadSocial.value_or(0.0)), "5.56%",
            redondear(d.primaVacacionesAnual / d.mesesConsiderados),
            d.primaVacacionesAnual,
            "Regimen especial docente de planta"
        });
    }

    if (d.bonificacionServiciosAnual > 0.0) {
        items.push_back({
            "Bonificacion por Servicios Prestados", "PRESTACION",
            redondear(liq.baseSeguridadSocial.value_or(0.0)), "35% / 50%",
            redondear(d.bonificacionServiciosAnual / d.mesesConsiderados),
            d.bonificacionServiciosAnual,
            "Causacion anual en fecha de vinculacion"
        });
    }

    items.push_back({
        "Prima de Navidad", "PRESTACION",
        redondear(liq.baseLiquidacionPrestaciones.value_or(0.0)), "8.33%",
        redondear(d.primaNavidadAnual / d.mesesConsiderados),
        d.primaNavidadAnual,
        "Pago en diciembre"
    });

    // APORTES PATRONALES
    if (d.saludPatronalAnual > 0.0) {
        items.push_back({
            "Salud Patronal", "APORTE_PATRONAL",
            redondear(liq.baseSeguridadSocial.value_or(0.0)), "8.50%",
            redondear(liq.aportePatronalSalud.value_or(0.0)),
            d.saludPatronalAnual,
            "Aporte institucional UPC"
        });
    }

    items.push_back({
        "Pension Patronal", "APORTE_PATRONAL",
        redondear(liq.baseSeguridadSocial.value_or(0.0)), "12.00%",
        redondear(liq.aportePatronalPension.value_or(0.0)),
        d.pensionPatronalAnual,
        "Aporte institucional UPC"
    });

    items.push_back({
        "Riesgos Laborales (ARL)", "APORTE_PATRONAL",
        redondear(liq.baseSeguridadSocial.value_or(0.0)), "Clase ARL",
        redondear(liq.aporteRiesgosLaborales.value_or(0.0)),
        d.arlPatronalAnual,
        "Cobertura riesgos profesionales"
    });

    items.push_back({
        "Caja de Compensacion Familiar", "APORTE_PATRONAL",
        redondear(liq.baseSeguridadSocial.value_or(0.0)), "4.00%",
        redondear(liq.aporteCajaCompensacion.value_or(0.0)),
        d.cajaCompensacionAnual,
        "Parafiscal Comfacesar"
    });

    if (d.senaAnual > 0.0) {
        items.push_back({
            "Aporte SENA", "APORTE_PATRONAL",
            redondear(liq.baseSeguridadSocial.value_or(0.0)), "2.00%",
            redondear(liq.aportePatronalSENA.value_or(0.0)),
            d.senaAnual,
            "Parafiscal SENA"
        });
    }

    if (d.icbfAnual > 0.0) {
        items.push_back({
            "Aporte ICBF", "APORTE_PATRONAL",
            redondear(liq.baseSeguridadSocial.value_or(0.0)), "3.00%",
            redondear(liq.aportePatronalICBF.value_or(0.0)),
            d.icbfAnual,
            "Parafiscal ICBF"
        });
    }

    return items;
}

ResumenNominaAnual CalculadorDesgloseAnual::generarDesgloseInstitucional(int anio) {
    ResumenNominaAnual res;
    res.anio = anio;

    for (const auto& c : gestor.contratos) {
        if (!c.idContrato.has_value()) continue;
        std::string est = c.estado.value_or("ACTIVO");
        if (a_mayusculas(est) != "ACTIVO") continue;

        DesgloseNominaAnual d = generarDesglosePorContrato(*c.idContrato, anio, true);
        res.desglosesIndividuales.push_back(d);

        res.totalEmpleados++;
        res.totalDevengadoAnual = redondear(res.totalDevengadoAnual + d.totalDevengadoAnual);
        res.totalDeduccionesAnual = redondear(res.totalDeduccionesAnual + d.totalDeduccionesAnual);
        res.netoAnualTotal = redondear(res.netoAnualTotal + d.netoAnualTrabajador);
        res.totalPrestacionesAnual = redondear(res.totalPrestacionesAnual + d.totalPrestacionesAnuales);
        res.totalAportesPatronalesAnual = redondear(res.totalAportesPatronalesAnual + d.totalAportesPatronalesAnual);
        res.costoTotalInstitucional = redondear(res.costoTotalInstitucional + d.costoTotalEmpleadorAnual);

        auto& grupo = res.porTipoPersonal[d.tipoPersonal];
        grupo.tipoPersonal = d.tipoPersonal;
        grupo.cantidadContratos++;
        grupo.totalDevengado = redondear(grupo.totalDevengado + d.totalDevengadoAnual);
        grupo.totalDeducciones = redondear(grupo.totalDeducciones + d.totalDeduccionesAnual);
        grupo.totalNeto = redondear(grupo.totalNeto + d.netoAnualTrabajador);
        grupo.totalPrestaciones = redondear(grupo.totalPrestaciones + d.totalPrestacionesAnuales);
        grupo.totalAportesPatronales = redondear(grupo.totalAportesPatronales + d.totalAportesPatronalesAnual);
        grupo.costoTotalEmpleador = redondear(grupo.costoTotalEmpleador + d.costoTotalEmpleadorAnual);
    }

    return res;
}

std::string CalculadorDesgloseAnual::generarInformeTexto(int anio) {
    ResumenNominaAnual res = generarDesgloseInstitucional(anio);
    std::ostringstream oss;
    oss << "========================================================================================\n";
    oss << "        UNIVERSIDAD POPULAR DEL CESAR - CONSOLIDADO DE NOMINA ANUAL " << anio << "\n";
    oss << "========================================================================================\n\n";

    oss << "1. RESUMEN EJECUTIVO INSTITUCIONAL:\n";
    oss << "   - Total Contratos Activos:      " << res.totalEmpleados << "\n";
    oss << "   - Total Devengado Anual:        " << formatearMoneda(res.totalDevengadoAnual) << "\n";
    oss << "   - Total Deducciones Anuales:    " << formatearMoneda(res.totalDeduccionesAnual) << "\n";
    oss << "   - Total Neto Pagado Anual:      " << formatearMoneda(res.netoAnualTotal) << "\n";
    oss << "   - Total Prestaciones Anuales:   " << formatearMoneda(res.totalPrestacionesAnual) << "\n";
    oss << "   - Total Aportes Patronales:     " << formatearMoneda(res.totalAportesPatronalesAnual) << "\n";
    oss << "   ------------------------------------------------------------------------------------\n";
    oss << "   - COSTO TOTAL EMPLEADOR (UPC):  " << formatearMoneda(res.costoTotalInstitucional) << "\n\n";

    oss << "2. DISTRIBUCION POR MODALIDAD / TIPO DE PERSONAL:\n";
    for (const auto& [tipo, g] : res.porTipoPersonal) {
        oss << "   * " << tipo << " (" << g.cantidadContratos << " contratos):\n";
        oss << "     - Devengado: " << formatearMoneda(g.totalDevengado)
            << " | Neto: " << formatearMoneda(g.totalNeto)
            << " | Prestaciones: " << formatearMoneda(g.totalPrestaciones)
            << " | Costo Empleador: " << formatearMoneda(g.costoTotalEmpleador) << "\n";
    }

    oss << "\n3. DETALLE DE EMPLEADOS CONSOLIDADOS:\n";
    for (const auto& d : res.desglosesIndividuales) {
        oss << "   ------------------------------------------------------------------------------------\n";
        oss << "   [" << d.tipoPersonal << "] " << d.nombreCompleto << " (Doc: " << d.identificacion << ") - "
            << d.mesesConsiderados << " meses (" << d.diasTrabajadosAnio << " dias)\n";
        oss << "     - Devengado Anual:    " << formatearMoneda(d.totalDevengadoAnual) << "\n";
        oss << "     - Deducciones Anual:  " << formatearMoneda(d.totalDeduccionesAnual) << "\n";
        oss << "     - Neto Pagado Anual:  " << formatearMoneda(d.netoAnualTrabajador) << "\n";
        oss << "     - Prestaciones Anual: " << formatearMoneda(d.totalPrestacionesAnuales) << "\n";
        oss << "     - Aportes Patronales: " << formatearMoneda(d.totalAportesPatronalesAnual) << "\n";
        oss << "     - Costo Empleador:    " << formatearMoneda(d.costoTotalEmpleadorAnual) << "\n";
    }

    return oss.str();
}

std::string CalculadorDesgloseAnual::generarInformeMarkdown(int anio) {
    ResumenNominaAnual res = generarDesgloseInstitucional(anio);
    std::ostringstream oss;
    oss << "# 📋 Consolidado Institucional de Nómina Anual " << anio << " (UPC)\n\n";
    oss << "## 🏛️ Resumen Ejecutivo de Presupuesto de Personal\n\n";
    oss << "| Indicador Financiero | Monto Consolidado (COP) |\n";
    oss << "| :--- | :---: |\n";
    oss << "| **Total Contratos Activos** | `" << res.totalEmpleados << "` |\n";
    oss << "| **Total Devengados Anuales** | `" << formatearMoneda(res.totalDevengadoAnual) << "` |\n";
    oss << "| **Total Deducciones de Ley (Empleados)** | `" << formatearMoneda(res.totalDeduccionesAnual) << "` |\n";
    oss << "| **Neto Total Transferido (Bancos)** | `" << formatearMoneda(res.netoAnualTotal) << "` |\n";
    oss << "| **Provisiones de Prestaciones Sociales (Causadas)** | `" << formatearMoneda(res.totalPrestacionesAnual) << "` |\n";
    oss << "| **Seguridad Social y Parafiscales Patronales** | `" << formatearMoneda(res.totalAportesPatronalesAnual) << "` |\n";
    oss << "| **COSTO TOTAL INSTITUCIONAL (EMPLEADOR UPC)** | **`" << formatearMoneda(res.costoTotalInstitucional) << "`** |\n\n";

    oss << "## 👥 Distribución por Modalidad Contractual\n\n";
    oss << "| Modalidad | Contratos | Total Devengado | Total Neto | Prestaciones | Costo Total UPC |\n";
    oss << "| :--- | :---: | :---: | :---: | :---: | :---: |\n";
    for (const auto& [tipo, g] : res.porTipoPersonal) {
        oss << "| **" << tipo << "** | " << g.cantidadContratos
            << " | " << formatearMoneda(g.totalDevengado)
            << " | " << formatearMoneda(g.totalNeto)
            << " | " << formatearMoneda(g.totalPrestaciones)
            << " | **" << formatearMoneda(g.costoTotalEmpleador) << "** |\n";
    }
    oss << "\n";

    return oss.str();
}

} // namespace pita
