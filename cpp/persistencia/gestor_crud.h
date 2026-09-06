#ifndef GESTOR_CRUD_H
#define GESTOR_CRUD_H

#include <stdexcept>
#include <string>
#include <functional>
#include <optional>
#include <algorithm>
#include "../dominio/lista_enlazada.h"

namespace pita {

class ErrorCRUD : public std::runtime_error {
public:
    explicit ErrorCRUD(const std::string& mensaje) : std::runtime_error(mensaje) {}
};

template <typename Entidad>
class GestorCRUD {
public:
    using ValidadorFunc = std::function<void(const Entidad&)>;
    using HistorialFunc = std::function<bool(const Entidad&)>;
    using GetIdFunc = std::function<std::optional<int>(const Entidad&)>;
    using SetIdFunc = std::function<void(Entidad&, int)>;
    using GetCodigoFunc = std::function<std::optional<std::string>(const Entidad&)>;
    using GetEstadoFunc = std::function<std::string(const Entidad&)>;
    using SetEstadoFunc = std::function<void(Entidad&, const std::string&)>;

private:
    ListaEnlazada<Entidad>& registros;
    GetIdFunc getId;
    SetIdFunc setId;
    GetCodigoFunc getCodigo;
    GetEstadoFunc getEstado;
    SetEstadoFunc setEstado;
    ValidadorFunc validador;
    HistorialFunc tieneHistorial;

public:
    GestorCRUD(
        ListaEnlazada<Entidad>& lista,
        GetIdFunc fnGetId,
        SetIdFunc fnSetId,
        GetCodigoFunc fnGetCodigo = nullptr,
        GetEstadoFunc fnGetEstado = nullptr,
        SetEstadoFunc fnSetEstado = nullptr,
        ValidadorFunc fnValidador = nullptr,
        HistorialFunc fnTieneHistorial = nullptr
    ) : registros(lista),
        getId(fnGetId),
        setId(fnSetId),
        getCodigo(fnGetCodigo),
        getEstado(fnGetEstado),
        setEstado(fnSetEstado),
        validador(fnValidador),
        tieneHistorial(fnTieneHistorial ? fnTieneHistorial : [](const Entidad&) { return false; }) {}

    Entidad& crear(Entidad registro) {
        validar(registro);
        auto optId = getId(registro);
        if (!optId.has_value()) {
            int nuevoId = siguienteId();
            setId(registro, nuevoId);
        } else {
            if (buscarPorId(*optId) != nullptr) {
                throw ErrorCRUD("Ya existe un registro con ID " + std::to_string(*optId));
            }
        }

        if (getCodigo) {
            auto optCod = getCodigo(registro);
            if (optCod.has_value() && !optCod->empty()) {
                if (buscarPorCodigo(*optCod) != nullptr) {
                    throw ErrorCRUD("Ya existe el codigo " + *optCod);
                }
            }
        }

        registros.push_back(std::move(registro));
        return registros.back();
    }

    Entidad* buscarPorId(int id) {
        for (auto& r : registros) {
            auto optId = getId(r);
            if (optId.has_value() && *optId == id) {
                return &r;
            }
        }
        return nullptr;
    }

    const Entidad* buscarPorId(int id) const {
        for (const auto& r : registros) {
            auto optId = getId(r);
            if (optId.has_value() && *optId == id) {
                return &r;
            }
        }
        return nullptr;
    }

    Entidad* buscarPorCodigo(const std::string& codigo) {
        if (!getCodigo) {
            throw ErrorCRUD("Esta entidad no tiene campo de codigo configurado");
        }
        for (auto& r : registros) {
            auto optCod = getCodigo(r);
            if (optCod.has_value() && *optCod == codigo) {
                return &r;
            }
        }
        return nullptr;
    }

    const Entidad* buscarPorCodigo(const std::string& codigo) const {
        if (!getCodigo) {
            throw ErrorCRUD("Esta entidad no tiene campo de codigo configurado");
        }
        for (const auto& r : registros) {
            auto optCod = getCodigo(r);
            if (optCod.has_value() && *optCod == codigo) {
                return &r;
            }
        }
        return nullptr;
    }

    ListaEnlazada<Entidad> listar(bool incluirInactivos = true) const {
        if (incluirInactivos || !getEstado) {
            return registros;
        }
        ListaEnlazada<Entidad> filtrados;
        for (const auto& r : registros) {
            if (getEstado(r) != "INACTIVO") {
                filtrados.push_back(r);
            }
        }
        return filtrados;
    }

    Entidad& actualizar(int id, const Entidad& nuevosDatos) {
        Entidad* existente = buscarPorId(id);
        if (!existente) {
            throw ErrorCRUD("No existe un registro con ID " + std::to_string(id));
        }
        if (tieneHistorial(*existente)) {
            throw ErrorCRUD("No se puede modificar directamente un registro historico");
        }

        validar(nuevosDatos);

        if (getCodigo) {
            auto nuevoCod = getCodigo(nuevosDatos);
            if (nuevoCod.has_value()) {
                Entidad* conMismoCodigo = buscarPorCodigo(*nuevoCod);
                if (conMismoCodigo && conMismoCodigo != existente) {
                    throw ErrorCRUD("Ya existe el codigo " + *nuevoCod);
                }
            }
        }

        *existente = nuevosDatos;
        setId(*existente, id);
        return *existente;
    }

    Entidad& desactivar(int id) {
        Entidad* existente = requerir(id);
        if (setEstado) {
            setEstado(*existente, "INACTIVO");
        }
        return *existente;
    }

    Entidad& reactivar(int id) {
        Entidad* existente = requerir(id);
        if (setEstado) {
            setEstado(*existente, "ACTIVO");
        }
        validar(*existente);
        return *existente;
    }

    void eliminar(int id) {
        Entidad* existente = requerir(id);
        if (tieneHistorial(*existente)) {
            if (setEstado) {
                setEstado(*existente, "INACTIVO");
            }
            return;
        }
        registros.remove_if([this, id](const Entidad& r) {
            auto optId = getId(r);
            return optId.has_value() && *optId == id;
        });
    }

    void validar(const Entidad& registro) {
        auto optId = getId(registro);
        if (optId.has_value() && *optId < 0) {
            throw ErrorCRUD("El ID no puede ser negativo");
        }
        if (getCodigo) {
            auto optCod = getCodigo(registro);
            if (optCod.has_value() && optCod->empty()) {
                throw ErrorCRUD("El codigo no puede estar vacio");
            }
        }
        if (validador) {
            validador(registro);
        }
    }

    int siguienteId() const {
        int maxId = 0;
        for (const auto& r : registros) {
            auto optId = getId(r);
            if (optId.has_value() && *optId > maxId) {
                maxId = *optId;
            }
        }
        return maxId + 1;
    }

    Entidad* requerir(int id) {
        Entidad* r = buscarPorId(id);
        if (!r) {
            throw ErrorCRUD("No existe un registro con ID " + std::to_string(id));
        }
        return r;
    }
};

} // namespace pita

#endif // GESTOR_CRUD_H
