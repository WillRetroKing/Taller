#ifndef DESGLOSE_ANUAL_H
#define DESGLOSE_ANUAL_H

#include <string>
#include <vector>
#include <optional>
#include <map>
#include "../dominio/modelo_datos.h"
#include "../dominio/lista_enlazada.h"

namespace pita {

class GestorNomina;

struct ItemDesgloseAnual {
    std::string concepto;
    std::string categoria; // DEVENGADO, DEDUCCION, PRESTACION, APORTE_PATRONAL
    double baseCalculo = 0.0;
    std::string porcentajeOFactor;
    double valorMensualPromedio = 0.0;
    double valorAnualConsolidado = 0.0;
    std::string observaciones;
};

struct DesgloseNominaAnual {
    int idContrato = 0;
    std::optional<int> idPersona;
    std::string nombreCompleto;
    std::string identificacion;
    std::string tipoPersonal; // PLANTA, OCASIONAL, CATEDRATICO, ADMINISTRATIVO
    std::string regimen;      // DECRETO_1279, ACUERDO_027, LEY_100_CST
    int anio = 2026;
    int mesesConsiderados = 12;
    int diasTrabajadosAnio = 360;

    // 1. Devengados Anuales
    double salarioOrdinarioAnual = 0.0;
    double bonificacionesPosgradoAnual = 0.0;
    double bonificacionesInvestigacionAnual = 0.0;
    double otrasBonificacionesAnual = 0.0;
    double auxilioTransporteAnual = 0.0;
    double totalDevengadoAnual = 0.0;

    // 2. Deducciones Anuales (Trabajador)
    double descuentoSaludAnual = 0.0;
    double descuentoPensionAnual = 0.0;
    double fondoSolidaridadAnual = 0.0;
    double retencionFuenteAnual = 0.0;
    double estampillasAnual = 0.0;
    double otrosDescuentosAnual = 0.0;
    double totalDescuentosAnual = 0.0;
    double totalDeduccionesAnual = 0.0;

    // 3. Neto Anual Pagado al Trabajador
    double netoAnualTrabajador = 0.0;

    // 4. Prestaciones Sociales Anuales (Consolidadas / Causadas)
    double cesantiasAnuales = 0.0;
    double interesesCesantiasAnuales = 0.0;
    double primaServiciosAnual = 0.0;
    double vacacionesAnuales = 0.0;
    double primaNavidadAnual = 0.0;
    double primaVacacionesAnual = 0.0;
    double bonificacionServiciosAnual = 0.0;
    double totalPrestacionesAnuales = 0.0;

    // 5. Aportes Patronales y Parafiscales Anuales (Costo Institucional UPC)
    double saludPatronalAnual = 0.0;
    double pensionPatronalAnual = 0.0;
    double arlPatronalAnual = 0.0;
    double cajaCompensacionAnual = 0.0;
    double senaAnual = 0.0;
    double icbfAnual = 0.0;
    double totalAportesPatronalesAnual = 0.0;

    // 6. Costo Total Institucional Anual (Presupuesto Empleador)
    double costoTotalEmpleadorAnual = 0.0;

    // Detalle concepto a concepto
    std::vector<ItemDesgloseAnual> items;
};

struct ResumenTipoPersonal {
    std::string tipoPersonal;
    int cantidadContratos = 0;
    double totalDevengado = 0.0;
    double totalDeducciones = 0.0;
    double totalNeto = 0.0;
    double totalPrestaciones = 0.0;
    double totalAportesPatronales = 0.0;
    double costoTotalEmpleador = 0.0;
};

struct ResumenNominaAnual {
    int anio = 2026;
    int totalEmpleados = 0;
    double totalDevengadoAnual = 0.0;
    double totalDeduccionesAnual = 0.0;
    double netoAnualTotal = 0.0;
    double totalPrestacionesAnual = 0.0;
    double totalAportesPatronalesAnual = 0.0;
    double costoTotalInstitucional = 0.0;

    std::map<std::string, ResumenTipoPersonal> porTipoPersonal;
    std::vector<DesgloseNominaAnual> desglosesIndividuales;
};

class CalculadorDesgloseAnual {
public:
    GestorNomina& gestor;
    const ListaEnlazada<Persona>* personas = nullptr;

    explicit CalculadorDesgloseAnual(GestorNomina& gestor, const ListaEnlazada<Persona>* personas = nullptr);

    DesgloseNominaAnual generarDesglosePorContrato(int idContrato, int anio = 2026, bool proyectar12Meses = true);
    ResumenNominaAnual generarDesgloseInstitucional(int anio = 2026);
    std::string generarInformeMarkdown(int anio = 2026);
    std::string generarInformeTexto(int anio = 2026);

private:
    static double redondear(double valor);
    std::vector<ItemDesgloseAnual> construirItemsDetalle(const DesgloseNominaAnual& d, const LiquidacionNomina& liq);
    Profesor* obtenerProfesor(std::optional<int> idPersona);
    Persona* obtenerPersona(std::optional<int> idPersona);
};

} // namespace pita

#endif // DESGLOSE_ANUAL_H
