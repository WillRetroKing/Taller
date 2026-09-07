#ifndef GESTOR_NOMINA_H
#define GESTOR_NOMINA_H

#include <string>
#include <stdexcept>
#include <optional>
#include <map>
#include <memory>
#include "../dominio/lista_enlazada.h"
#include "../dominio/modelo_datos.h"
#include "calculadora_deducciones.h"
#include "calculadora_prestaciones.h"

namespace pita {

class ErrorNomina : public std::runtime_error {
public:
    explicit ErrorNomina(const std::string& mensaje) : std::runtime_error(mensaje) {}
};

class GestorNomina;

class MotorLiquidacionBase {
public:
    GestorNomina& gestor;

    explicit MotorLiquidacionBase(GestorNomina& gestor);

    LiquidacionNomina ensamblarLiquidacion(
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
        std::optional<double> horasPagables = std::nullopt,
        bool esAdHonorem = false,
        bool incluirBonificaciones = true
    );

    void crearDetalles(
        LiquidacionNomina& liquidacion,
        PeriodoNomina& periodo,
        double ibc,
        double salarioOrdinario,
        double auxilio,
        double bonificacionPosgrado,
        double bonificacionInvestigacion,
        double descuentoSalud,
        double descuentoPension,
        double fondoSolidaridad,
        double retencion,
        double descuentoIncumplimiento,
        double aporteSalud,
        double aportePension,
        double aporteArl,
        double aporteCaja,
        double aporteSena,
        double aporteIcbf,
        std::map<std::string, std::string>* codigosUtilizados = nullptr
    );
};

class LiquidadorOcasional : public MotorLiquidacionBase {
public:
    explicit LiquidadorOcasional(GestorNomina& gestor) : MotorLiquidacionBase(gestor) {}

    LiquidacionNomina liquidar(
        int idContrato,
        int idPeriodoNomina,
        std::optional<double> horasIncumplidas = std::nullopt,
        const std::string& fechaLiquidacion = ""
    );
};

class LiquidadorPlanta : public MotorLiquidacionBase {
public:
    explicit LiquidadorPlanta(GestorNomina& gestor) : MotorLiquidacionBase(gestor) {}

    LiquidacionNomina liquidar(
        int idContrato,
        int idPeriodoNomina,
        const std::string& fechaLiquidacion = ""
    );
};

class LiquidadorCatedratico : public MotorLiquidacionBase {
public:
    explicit LiquidadorCatedratico(GestorNomina& gestor) : MotorLiquidacionBase(gestor) {}

    LiquidacionNomina liquidar(
        int idContrato,
        int idPeriodoNomina,
        const std::string& fechaLiquidacion = ""
    );
};

class LiquidadorAdministrativo : public MotorLiquidacionBase {
public:
    explicit LiquidadorAdministrativo(GestorNomina& gestor) : MotorLiquidacionBase(gestor) {}

    LiquidacionNomina liquidar(
        int idContrato,
        int idPeriodoNomina,
        const std::string& fechaLiquidacion = ""
    );
};

class CicloVidaNomina {
public:
    GestorNomina& gestor;

    explicit CicloVidaNomina(GestorNomina& gestor);

    PeriodoNomina& crearPeriodoNomina(PeriodoNomina periodo);
    PeriodoNomina& abrirPeriodoNomina(int idPeriodoNomina);
    PeriodoNomina& cerrarPeriodoNomina(int idPeriodoNomina);
    PeriodoNomina& crearPeriodoNominaMensual(int anio, int mes);

    LiquidacionNomina& aprobarLiquidacion(int idLiquidacion, const std::string& usuario);
    LiquidacionNomina& pagarLiquidacion(int idLiquidacion, const std::string& medioPago, const std::string& referencia);
    LiquidacionNomina reliquidar(int idLiquidacion);

    bool tieneHistorialLiquidacion(const LiquidacionNomina& liquidacion) const;
    LiquidacionNomina& desactivarLiquidacion(int idLiquidacion);
    LiquidacionNomina& reactivarLiquidacion(int idLiquidacion);
    void eliminarLiquidacion(int idLiquidacion);

    std::map<std::string, double> resumenNominaPeriodo(int idPeriodoNomina);
    std::map<std::string, std::map<std::string, double>> totalesPorTipoProfesor(int idPeriodoNomina);
};

class GestorNomina {
public:
    ListaEnlazada<Contrato>& contratos;
    ListaEnlazada<Profesor>& profesores;
    ListaEnlazada<PeriodoNomina>& periodosNomina;
    ListaEnlazada<LiquidacionNomina>& liquidaciones;
    ListaEnlazada<ParametroNormativo>& parametros;
    ListaEnlazada<DetalleLiquidacion>& detallesLiquidacion;
    ListaEnlazada<CategoriaDocente>& categorias;
    ListaEnlazada<FactorSalarial>& factores;
    ListaEnlazada<ProduccionAcademica>& producciones;
    ListaEnlazada<Administrativo>* administrativos;

    CalculadoraDeducciones calcDeducciones;
    CalculadoraPrestaciones calcPrestaciones;
    LiquidadorPlanta liquidadorPlanta;
    LiquidadorOcasional liquidadorOcasional;
    LiquidadorCatedratico liquidadorCatedratico;
    LiquidadorAdministrativo liquidadorAdministrativo;
    CicloVidaNomina cicloVida;

    GestorNomina(
        ListaEnlazada<Contrato>& contratos,
        ListaEnlazada<Profesor>& profesores,
        ListaEnlazada<PeriodoNomina>& periodosNomina,
        ListaEnlazada<LiquidacionNomina>& liquidaciones,
        ListaEnlazada<ParametroNormativo>& parametros,
        ListaEnlazada<DetalleLiquidacion>& detallesLiquidacion,
        ListaEnlazada<CategoriaDocente>& categorias,
        ListaEnlazada<FactorSalarial>& factores,
        ListaEnlazada<ProduccionAcademica>& producciones,
        ListaEnlazada<Administrativo>* administrativos = nullptr
    );

    // Liquidaciones principales
    LiquidacionNomina liquidarProfesorOcasional(int idContrato, int idPeriodoNomina, std::optional<double> horasIncumplidas = std::nullopt, const std::string& fechaLiquidacion = "");
    LiquidacionNomina liquidarProfesorPlanta(int idContrato, int idPeriodoNomina, const std::string& fechaLiquidacion = "");
    LiquidacionNomina liquidarProfesorCatedratico(int idContrato, int idPeriodoNomina, const std::string& fechaLiquidacion = "");
    LiquidacionNomina liquidarAdministrativo(int idContrato, int idPeriodoNomina, const std::string& fechaLiquidacion = "");
    LiquidacionNomina crearLiquidacion(LiquidacionNomina liquidacion);

    // Ciclo de vida
    PeriodoNomina& crearPeriodoNomina(PeriodoNomina periodo);
    PeriodoNomina& abrirPeriodoNomina(int idPeriodoNomina);
    PeriodoNomina& cerrarPeriodoNomina(int idPeriodoNomina);
    PeriodoNomina& crearPeriodoNominaMensual(int anio, int mes);
    LiquidacionNomina& aprobarLiquidacion(int idLiquidacion, const std::string& usuario);
    LiquidacionNomina& pagarLiquidacion(int idLiquidacion, const std::string& medioPago, const std::string& referencia);
    LiquidacionNomina reliquidar(int idLiquidacion);

    ListaEnlazada<LiquidacionNomina> consultarLiquidaciones(std::optional<int> idProfesor = std::nullopt, std::optional<int> idPeriodoNomina = std::nullopt) const;
    ListaEnlazada<DetalleLiquidacion> consultarDetallesLiquidacion(int idLiquidacion) const;

    std::map<std::string, double> resumenNominaPeriodo(int idPeriodoNomina);
    std::map<std::string, std::map<std::string, double>> totalesPorTipoProfesor(int idPeriodoNomina);

    // Helpers internos
    Contrato& contrato(int idContrato);
    PeriodoNomina& periodo(int idPeriodo);
    Profesor& profesor(std::optional<int> idPersona);
    Administrativo* administrativo(std::optional<int> idPersona);
    LiquidacionNomina& liquidacion(int idLiquidacion);

    int siguienteId();
    int siguienteIdDetalle();
    static double redondear(double valor);
    void validarPeriodoAbierto(const PeriodoNomina& p);
    void evitarLiquidacionDuplicada(int idContrato, int idPeriodoNomina);
    void evitarLiquidacionDuplicadaVersion(int idContrato, int idPeriodoNomina, int idLiquidacionOrigen);
    ListaEnlazada<LiquidacionNomina> liquidacionesPeriodo(int idPeriodoNomina);
    double totalPeriodo(int idPeriodoNomina, const std::string& campo);
    static double aportes(const LiquidacionNomina& l);
    static bool esRegimen1279(const std::optional<std::string>& regimen);
    double puntosPlanta(const Profesor& prof, const PeriodoNomina& per);
    double salarioMinimo(const Contrato& c, const PeriodoNomina& p, const std::string& fecha = "", std::map<std::string, std::string>* codigosUtilizados = nullptr);
    void validarContrato(const Contrato& c, TipoProfesor tipo, const PeriodoNomina& p);
    void validarHorasIncumplidas(const Contrato& c, double horasIncumplidas);
    void eliminarDetallesVersion(int idLiquidacionOriginal);
};

} // namespace pita

#endif // GESTOR_NOMINA_H
