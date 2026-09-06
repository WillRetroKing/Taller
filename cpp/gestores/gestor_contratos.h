#ifndef GESTOR_CONTRATOS_H
#define GESTOR_CONTRATOS_H

#include <string>
#include <stdexcept>
#include <optional>
#include "../dominio/lista_enlazada.h"
#include "../dominio/modelo_datos.h"

namespace pita {

class ErrorContrato : public std::runtime_error {
public:
    explicit ErrorContrato(const std::string& mensaje) : std::runtime_error(mensaje) {}
};

class GestorContratos {
public:
    static constexpr double HORAS_MAXIMAS_CATEDRATICO = 18.0;
    static constexpr double HORAS_MAXIMAS_ADMINISTRATIVO_AD_HONOREM = 8.0;

    ListaEnlazada<Contrato>& contratos;
    ListaEnlazada<Profesor>& profesores;
    ListaEnlazada<Administrativo>& administrativos;
    ListaEnlazada<LiquidacionNomina>& liquidaciones;

    GestorContratos(
        ListaEnlazada<Contrato>& contratos,
        ListaEnlazada<Profesor>& profesores,
        ListaEnlazada<Administrativo>& administrativos,
        ListaEnlazada<LiquidacionNomina>& liquidaciones
    );

    Contrato& crearContrato(Contrato contrato, std::optional<bool> jubilado = std::nullopt);
    Contrato* buscarContratoVigente(int idPersona, const std::string& fecha = "");
    ListaEnlazada<Contrato> listarContratosProfesor(int idPersona) const;
    Contrato& terminarContrato(int idContrato, const std::string& causal, const std::string& documento, const std::string& fecha = "");
    Contrato& desactivarContrato(int idContrato);
    void validarContrato(const Contrato& contrato, std::optional<bool> jubilado = std::nullopt);

    double horasActivas(std::optional<int> idPersona, const std::string& tipo);
    int duracionEnMeses(const Contrato& contrato);
    bool esJubilado(std::optional<int> idPersona, std::optional<bool> jubilado);
    bool esAdministrativo(std::optional<int> idPersona);
    static bool esCatedraticoAdHonorem(const Contrato& contrato);
    static std::string tipo(const Contrato& contrato);
    static std::string dedicacion(const Contrato& contrato);
    static double horasSemanales(const Contrato& contrato);
    static bool esActivo(const std::optional<std::string>& estado);

private:
    int siguienteId();
    Contrato* buscar(int identificador);
};

} // namespace pita

#endif // GESTOR_CONTRATOS_H
