#ifndef GUI_CONTROLLER_H
#define GUI_CONTROLLER_H

#include <string>
#include <memory>
#include "../dominio/modelo_datos.h"
#include "../dominio/lista_enlazada.h"
#include "../persistencia/gestor_persistencia.h"
#include "../gestores/gestor_personas.h"
#include "../gestores/gestor_academico.h"
#include "../gestores/gestor_contratos.h"
#include "../gestores/gestor_parametros.h"
#include "../gestores/gestor_periodos.h"
#include "../gestores/gestor_factores.h"
#include "../gestores/gestores_academicos.h"
#include "../nomina/gestor_nomina.h"

namespace pita {

/**
 * Controlador central de la GUI.
 * Encapsula toda la lógica de negocio y persistencia,
 * ofreciendo acceso directo a los datos y gestores.
 */
class GUIController {
public:
    // Directorio de datos
    std::string directorioDatos;

    // Persistencia
    GestorPersistencia persistencia;
    DatosSistema datos;

    // Gestores (se inicializan después de cargar datos)
    std::unique_ptr<GestorPersonas> gestorPersonas;
    std::unique_ptr<GestorAcademico> gestorAcademico;
    std::unique_ptr<GestorContratos> gestorContratos;
    std::unique_ptr<GestorParametros> gestorParametros;
    std::unique_ptr<GestorPeriodosAcademicos> gestorPeriodos;
    std::unique_ptr<GestorFactores> gestorFactores;
    std::unique_ptr<GestorMatriculas> gestorMatriculas;
    std::unique_ptr<GestorCalificaciones> gestorCalificaciones;
    std::unique_ptr<GestorNomina> gestorNomina;

    // Estado
    bool datosDisponibles = false;
    std::string ultimoMensaje;
    bool hayError = false;

    explicit GUIController(const std::string& dirDatos = "datos");

    void cargarDatos();
    void guardarDatos();
    void iniciarSinDatos();
    void inicializarGestores();

    // Mensajes de estado
    void setMensaje(const std::string& msg, bool error = false);
    void limpiarMensaje();
};

} // namespace pita

#endif // GUI_CONTROLLER_H
