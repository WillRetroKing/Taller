#ifndef GESTOR_PARAMETROS_H
#define GESTOR_PARAMETROS_H

#include <string>
#include <stdexcept>
#include <optional>
#include <unordered_set>
#include "../dominio/lista_enlazada.h"
#include "../dominio/modelo_datos.h"

namespace pita {

class ErrorParametro : public std::runtime_error {
public:
    explicit ErrorParametro(const std::string& mensaje) : std::runtime_error(mensaje) {}
};

class GestorParametros {
public:
    ListaEnlazada<ParametroNormativo>& parametros;
    ListaEnlazada<LiquidacionNomina>& liquidaciones;

    GestorParametros(
        ListaEnlazada<ParametroNormativo>& parametros,
        ListaEnlazada<LiquidacionNomina>& liquidaciones
    );

    ParametroNormativo& crearParametro(ParametroNormativo parametro);
    ParametroNormativo* buscarParametroVigente(const std::string& codigo, const std::string& fecha = "");
    ParametroNormativo* obtenerParametro(const std::string& codigo, const std::string& fecha = "");
    std::optional<double> obtenerParametroVigente(const std::string& codigo, const std::string& fecha = "");
    ParametroNormativo& modificarParametro(int idParametro, const ParametroNormativo& datosActualizados);
    ParametroNormativo& desactivarParametro(int idParametro);
    ListaEnlazada<ParametroNormativo> listarParametrosPorTipo(const std::string& tipoDato) const;

    void validar(const ParametroNormativo& p);
    void validarNoSolapamiento(const ParametroNormativo& nuevo, const ParametroNormativo* excluir = nullptr);
    static bool intervalosSeCruzan(const ParametroNormativo& primero, const ParametroNormativo& segundo);
    bool estaUsadoEnLiquidacion(const ParametroNormativo& p);

    static std::string codigoStr(const ParametroNormativo& p);
    static std::string codigoStr(const std::string& cod);
    static bool esActivo(const std::optional<std::string>& estado);
    static bool vigenteEn(const ParametroNormativo& p, const std::string& fecha);

private:
    int siguienteId();
    ParametroNormativo* buscar(int idParametro);
};

} // namespace pita

#endif // GESTOR_PARAMETROS_H
