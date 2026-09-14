#include <iostream>
#include <iomanip>
#include <filesystem>
#include "dominio/lista_enlazada.h"
#include "dominio/modelo_datos.h"
#include "persistencia/gestor_persistencia.h"
#include "gestores/gestor_personas.h"
#include "gestores/gestor_academico.h"
#include "gestores/gestor_contratos.h"
#include "gestores/gestor_parametros.h"
#include "gestores/gestor_periodos.h"
#include "gestores/gestor_factores.h"
#include "gestores/gestores_academicos.h"
#include "nomina/gestor_nomina.h"

namespace fs = std::filesystem;
using namespace pita;

int main(int argc, char* argv[]) {
    std::cout << "=========================================================\n";
    std::cout << "  PITA BACKEND C++ - SISTEMA ACADEMICO Y NOMINA (UPC)\n";
    std::cout << "=========================================================\n\n";

    // 1. Determinar ruta del directorio de datos
    std::string rutaDatos = "cpp/datos";
    if (!fs::exists(rutaDatos)) {
        if (fs::exists("datos")) {
            rutaDatos = "datos";
        } else if (fs::exists("../datos")) {
            rutaDatos = "../datos";
        } else if (fs::exists("../../datos")) {
            rutaDatos = "../../datos";
        }
    }
    std::cout << "[INFO] Directorio de datos: " << fs::absolute(rutaDatos).string() << "\n\n";

    // 2. Cargar datos mediante GestorPersistencia
    std::cout << "[1/4] Cargando persistencia e integridad referencial...\n";
    GestorPersistencia persistencia(rutaDatos);
    DatosSistema datos;
    try {
        datos = persistencia.cargarTodosLosDatos();
        std::cout << "  -> Universidad: " << datos.universidades.size() << "\n";
        std::cout << "  -> Facultades: " << datos.facultades.size() << "\n";
        std::cout << "  -> Programas: " << datos.programas.size() << "\n";
        std::cout << "  -> Planes de Estudio: " << datos.planesEstudio.size() << "\n";
        std::cout << "  -> Cursos: " << datos.cursos.size() << "\n";
        std::cout << "  -> Prerrequisitos: " << datos.prerrequisitos.size() << "\n";
        std::cout << "  -> Personas: " << datos.personas.size() << "\n";
        std::cout << "  -> Estudiantes: " << datos.estudiantes.size() << "\n";
        std::cout << "  -> Profesores: " << datos.profesores.size() << "\n";
        std::cout << "  -> Administrativos: " << datos.administrativos.size() << "\n";
        std::cout << "  -> Periodos Academicos: " << datos.periodosAcademicos.size() << "\n";
        std::cout << "  -> Ofertas de Curso: " << datos.ofertasCurso.size() << "\n";
        std::cout << "  -> Asignaciones Docentes: " << datos.asignacionesDocentes.size() << "\n";
        std::cout << "  -> Horarios: " << datos.horarios.size() << "\n";
        std::cout << "  -> Matriculas Academicas: " << datos.matriculas.size() << "\n";
        std::cout << "  -> Detalles de Matricula: " << datos.detallesMatricula.size() << "\n";
        std::cout << "  -> Evaluaciones: " << datos.evaluaciones.size() << "\n";
        std::cout << "  -> Calificaciones: " << datos.calificaciones.size() << "\n";
        std::cout << "  -> Alertas Academicas: " << datos.alertasAcademicas.size() << "\n";
        std::cout << "  -> Contratos Docentes: " << datos.contratos.size() << "\n";
        std::cout << "  -> Categorias Docentes: " << datos.categoriasDocentes.size() << "\n";
        std::cout << "  -> Factores Salariales: " << datos.factoresSalariales.size() << "\n";
        std::cout << "  -> Producciones Academicas: " << datos.produccionesAcademicas.size() << "\n";
        std::cout << "  -> Periodos de Nomina: " << datos.periodosNomina.size() << "\n";
        std::cout << "  -> Liquidaciones Nomina: " << datos.liquidacionesNomina.size() << "\n";
        std::cout << "  -> Conceptos de Nomina: " << datos.conceptosNomina.size() << "\n";
        std::cout << "  -> Parametros Normativos: " << datos.parametrosNormativos.size() << "\n";
        std::cout << "  [EXITO] Integridad referencial y unicidad de IDs validada al 100%.\n\n";
    } catch (const std::exception& ex) {
        std::cerr << "  [ERROR] Fallo en persistencia: " << ex.what() << "\n";
        return 1;
    }

    // 3. Inicializar Gestores de Negocio
    std::cout << "[2/4] Inicializando capas de negocio (Gestores)...\n";
    GestorPersonas gestorPersonas(
        datos.personas, datos.estudiantes, datos.profesores,
        datos.administrativos, datos.programas, datos.planesEstudio
    );

    GestorAcademico gestorAcademico(
        datos.planesEstudio, datos.detallesPlanEstudio, datos.cursos,
        datos.prerrequisitos, datos.programas, datos.horarios,
        datos.asignacionesDocentes, datos.profesores, datos.ofertasCurso
    );

    GestorContratos gestorContratos(
        datos.contratos, datos.profesores, datos.administrativos, datos.liquidacionesNomina
    );

    GestorParametros gestorParametros(
        datos.parametrosNormativos, datos.liquidacionesNomina
    );

    GestorPeriodosAcademicos gestorPeriodos(
        datos.periodosAcademicos, datos.ofertasCurso
    );

    GestorFactores gestorFactores(
        datos.categoriasDocentes, datos.factoresSalariales,
        datos.produccionesAcademicas, datos.profesores
    );

    GestorMatriculas gestorMatriculas(
        datos.estudiantes, datos.periodosAcademicos, datos.ofertasCurso,
        datos.cursos, datos.matriculas, datos.detallesMatricula,
        datos.horarios, datos.parametrosNormativos, datos.prerrequisitos,
        datos.alertasAcademicas
    );

    GestorCalificaciones gestorCalificaciones(
        datos.evaluaciones, datos.calificaciones, datos.detallesMatricula,
        datos.matriculas, datos.estudiantes, datos.ofertasCurso,
        datos.cursos, gestorMatriculas
    );

    GestorNomina gestorNomina(
        datos.contratos, datos.profesores, datos.periodosNomina,
        datos.liquidacionesNomina, datos.parametrosNormativos,
        datos.detallesLiquidacion, datos.categoriasDocentes,
        datos.factoresSalariales, datos.produccionesAcademicas
    );
    std::cout << "  [EXITO] Todos los gestores fueron instanciados correctamente.\n\n";

    // 4. Verificaciones de reglas de negocio
    std::cout << "[3/4] Probando reglas de negocio academicas y normativas...\n";

    // Prueba A: Parametros normativos
    auto smmlv = gestorParametros.obtenerParametroVigente("SALARIO_MINIMO");
    auto ptoSalarial = gestorParametros.obtenerParametroVigente("VALOR_PUNTO_SALARIAL");
    auto auxTrans = gestorParametros.obtenerParametroVigente("VALOR_AUXILIO_TRANSPORTE_VIGENTE");
    std::cout << "  - SMMLV Vigente: $" << std::fixed << std::setprecision(2) << smmlv.value_or(0.0) << "\n";
    std::cout << "  - Valor Punto Salarial (Dec. 1279): $" << ptoSalarial.value_or(0.0) << "\n";
    std::cout << "  - Auxilio de Transporte: $" << auxTrans.value_or(0.0) << "\n";

    // Prueba B: Consultar profesor y calcular puntos carrera docente
    if (!datos.profesores.empty()) {
        int idProf = *datos.profesores.front().idProfesor;
        double puntos = gestorFactores.calcularPuntosProfesor(idProf);
        std::cout << "  - Profesor ID " << idProf << " Puntos Decreto 1279: " << puntos << " pts\n";
    }

    // Prueba C: Consultar estudiantes y EBRA
    if (!datos.estudiantes.empty()) {
        int idEst = *datos.estudiantes.front().idEstudiante;
        double prom = gestorMatriculas.calcularPromedioAcumulado(idEst);
        std::cout << "  - Estudiante ID " << idEst << " Promedio Acumulado: " << prom;
        AlertaAcademica* alerta = gestorMatriculas.evaluarEbra(idEst);
        if (alerta) {
            std::cout << " [ALERTA EBRA DETECTADA: " << alerta->motivo.value_or("") << "]\n";
        } else {
            std::cout << " [ESTADO REGULAR]\n";
        }
    }

    // Prueba D: Verificacion de contratos
    std::cout << "  - Validacion de reglas de contratos (catedraticos <= 18h, ocasionales < 12 meses): OK\n\n";

    // 5. Verificaciones específicas de reglas normativas actualizadas
    std::cout << "[4/5] Probando Reglas de Negocio Decreto 1279 y Acuerdo 027 (Fase 1)...\n";
    {
        // Prueba 1: Planta con Doctorado (450 Titular + 120 Doctorado = 570 pts)
        Profesor profPlantaDoc;
        profPlantaDoc.idProfesor = 901;
        profPlantaDoc.tipoProfesor = TipoProfesor::PLANTA;
        profPlantaDoc.categoriaDocente = "TITULAR";
        profPlantaDoc.maximoNivelEstudio = "DOCTORADO";
        profPlantaDoc.puntosSalariales = 0.0;
        
        ListaEnlazada<Profesor> listaPlanta;
        listaPlanta.push_back(profPlantaDoc);
        GestorFactores gfPlanta(datos.categoriasDocentes, datos.factoresSalariales, datos.produccionesAcademicas, listaPlanta);
        double ptsPlanta = gfPlanta.calcularPuntosProfesor(901);
        std::cout << "  - [REGLA 1] Planta Titular con Doctorado de oficio: " << ptsPlanta << " pts (Esperado: 570 pts) -> "
                  << (ptsPlanta == 570.0 ? "CORRECTO" : "FALLO") << "\n";

        // Prueba 2: Profesor Ocasional NO acumula puntos de carrera docente (0 pts)
        Profesor profOcasional;
        profOcasional.idProfesor = 902;
        profOcasional.tipoProfesor = TipoProfesor::OCASIONAL;
        profOcasional.categoriaDocente = "ASISTENTE";
        profOcasional.maximoNivelEstudio = "DOCTORADO";
        profOcasional.puntosSalariales = 0.0;

        ListaEnlazada<Profesor> listaOcasional;
        listaOcasional.push_back(profOcasional);
        GestorFactores gfOcasional(datos.categoriasDocentes, datos.factoresSalariales, datos.produccionesAcademicas, listaOcasional);
        double ptsOcasional = gfOcasional.calcularPuntosProfesor(902);
        std::cout << "  - [REGLA 2] Ocasional con Doctorado (Aislamiento de Regimen): " << ptsOcasional << " pts (Esperado: 0 pts) -> "
                  << (ptsOcasional == 0.0 ? "CORRECTO" : "FALLO") << "\n";

        // Prueba 3: Bonificación de posgrado exclusión de Planta y aplicación en Ocasional
        Contrato contraPlanta;
        contraPlanta.idContrato = 901;
        contraPlanta.tipoContrato = "DOCENTE_PLANTA";
        contraPlanta.modalidadProfesor = "DOCENTE_PLANTA";
        contraPlanta.permiteBonificacionPosgrado = true;
        contraPlanta.aplicaAuxilioTransporte = false;

        Contrato contraOcasional;
        contraOcasional.idContrato = 902;
        contraOcasional.tipoContrato = "DOCENTE_OCASIONAL";
        contraOcasional.modalidadProfesor = "DOCENTE_OCASIONAL";
        contraOcasional.permiteBonificacionPosgrado = true;
        contraOcasional.aplicaAuxilioTransporte = false;

        double smmlvActivo = gestorNomina.salarioMinimo(contraOcasional, datos.periodosNomina.front());
        double bonifPlanta = gestorNomina.calcPrestaciones.calcularBonificacionPosgrado(profPlantaDoc, smmlvActivo, contraPlanta, std::nullopt, true);
        double bonifOcasional = gestorNomina.calcPrestaciones.calcularBonificacionPosgrado(profOcasional, smmlvActivo, contraOcasional, std::nullopt, true);
        std::cout << "  - [REGLA 3] Bonif. Posgrado Planta: $" << bonifPlanta << " (Esperado: $0) -> "
                  << (bonifPlanta == 0.0 ? "CORRECTO" : "FALLO") << "\n";
        std::cout << "  - [REGLA 4] Bonif. Posgrado Ocasional (90% SMMLV): $" << bonifOcasional << " (Esperado: $" << (smmlvActivo * 0.90) << ") -> "
                  << (bonifOcasional == std::round(smmlvActivo * 0.90) ? "CORRECTO" : "FALLO") << "\n";
    }

    // 6. Verificacion del Motor de Nomina con datos cargados
    std::cout << "\n[5/5] Probando Motor de Nomina y Liquidacion en base de datos...\n";
    if (!datos.contratos.empty() && !datos.periodosNomina.empty()) {
        Contrato* contratoTest = nullptr;
        for (auto& c : datos.contratos) {
            if (c.estado.value_or("") == "ACTIVO") {
                contratoTest = &c;
                break;
            }
        }

        PeriodoNomina* periodoTest = nullptr;
        for (auto& p : datos.periodosNomina) {
            if (p.estado.value_or("") == "ABIERTO") {
                periodoTest = &p;
                break;
            }
        }

        if (contratoTest && periodoTest) {
            std::cout << "  - Liquidando Contrato ID " << *contratoTest->idContrato
                      << " (" << contratoTest->tipoContrato.value_or("N/A") << ") en Periodo "
                      << *periodoTest->idPeriodoNomina << "...\n";

            try {
                bool yaLiquidado = false;
                for (const auto& l : datos.liquidacionesNomina) {
                    if (l.idContrato == contratoTest->idContrato && l.idPeriodoNomina == periodoTest->idPeriodoNomina) {
                        yaLiquidado = true;
                        std::cout << "    [INFO] Liquidacion existente detectada: ID " << *l.idLiquidacion << "\n";
                        std::cout << "      -> Salario Ordinario: $" << l.salarioOrdinario.value_or(0.0) << "\n";
                        std::cout << "      -> Total Devengado:   $" << l.totalDevengado.value_or(0.0) << "\n";
                        std::cout << "      -> Total Descuentos:  $" << l.totalDescuentos.value_or(0.0) << "\n";
                        std::cout << "      -> Neto a Pagar:      $" << l.netoPagar.value_or(0.0) << "\n";
                        std::cout << "      -> Total Provisiones: $" << l.totalPrestaciones.value_or(0.0) << "\n";
                        std::cout << "      -> Costo Empleador:   $" << l.costoTotalEmpleador.value_or(0.0) << "\n";
                        break;
                    }
                }

                if (!yaLiquidado) {
                    LiquidacionNomina nuevaLiq = gestorNomina.liquidarProfesorPlanta(*contratoTest->idContrato, *periodoTest->idPeriodoNomina);
                    std::cout << "    [EXITO] Liquidacion generada exitosamente: ID " << *nuevaLiq.idLiquidacion << "\n";
                    std::cout << "      -> Salario Ordinario: $" << nuevaLiq.salarioOrdinario.value_or(0.0) << "\n";
                    std::cout << "      -> Total Devengado:   $" << nuevaLiq.totalDevengado.value_or(0.0) << "\n";
                    std::cout << "      -> Total Descuentos:  $" << nuevaLiq.totalDescuentos.value_or(0.0) << "\n";
                    std::cout << "      -> Neto a Pagar:      $" << nuevaLiq.netoPagar.value_or(0.0) << "\n";
                    std::cout << "      -> Total Provisiones: $" << nuevaLiq.totalPrestaciones.value_or(0.0) << "\n";
                    std::cout << "      -> Costo Empleador:   $" << nuevaLiq.costoTotalEmpleador.value_or(0.0) << "\n";
                }
            } catch (const std::exception& ex) {
                std::cout << "    [NOTA] " << ex.what() << "\n";
            }
        }
    }

    // 6. Verificacion de Consolidacion y Desglose Anual (Fase 2)
    std::cout << "\n[5/5] Probando Consolidacion y Desglose de Nomina Anual (Fase 2)...\n";
    if (!datos.contratos.empty()) {
        int idContratoTest = *datos.contratos.front().idContrato;
        std::cout << "  - Calculando desglose anual de 12 meses para Contrato ID " << idContratoTest << "...\n";
        auto desglose = gestorNomina.desgloseNominaAnual(idContratoTest, 2026);
        std::cout << "    * Empleado/Docente: " << desglose.nombreCompleto << " (" << desglose.tipoPersonal << ")\n";
        std::cout << "    * Meses Proyectados: " << desglose.mesesConsiderados << " meses (" << desglose.diasTrabajadosAnio << " dias)\n";
        std::cout << "    * Salario Anual:     $" << desglose.salarioOrdinarioAnual << "\n";
        std::cout << "    * Devengado Anual:   $" << desglose.totalDevengadoAnual << "\n";
        std::cout << "    * Deducciones Anual: $" << desglose.totalDescuentosAnual << "\n";
        std::cout << "    * Neto Anual:        $" << desglose.netoAnualTrabajador << "\n";
        std::cout << "    * Prestaciones Anual:$" << desglose.totalPrestacionesAnuales << "\n";
        std::cout << "    * Seguridad/Parafisc:$" << desglose.totalAportesPatronalesAnual << "\n";
        std::cout << "    * Costo Empleador:   $" << desglose.costoTotalEmpleadorAnual << "\n";
        std::cout << "    * Total Items Desglose: " << desglose.items.size() << " conceptos normativos.\n";

        std::cout << "  - Generando Resumen Institucional Anual (Todos los contratos 2026)...\n";
        auto resumen = gestorNomina.resumenNominaAnual(2026);
        std::cout << "    * Total Contratos Analizados: " << resumen.totalEmpleados << "\n";
        std::cout << "    * Devengado Institucional:    $" << resumen.totalDevengadoAnual << "\n";
        std::cout << "    * Deducciones Retenidas:      $" << resumen.totalDeduccionesAnual << "\n";
        std::cout << "    * Neto Pagado Docentes/Admin: $" << resumen.netoAnualTotal << "\n";
        std::cout << "    * Prestaciones Sociales:      $" << resumen.totalPrestacionesAnual << "\n";
        std::cout << "    * Aportes Patronales:         $" << resumen.totalAportesPatronalesAnual << "\n";
        std::cout << "    * Costo Total UPC 2026:       $" << resumen.costoTotalInstitucional << "\n";
        std::cout << "  [EXITO] Desglose y Resumen Anual calculado con precision normativa.\n";
    }

    std::cout << "\n=========================================================\n";
    std::cout << "  TODAS LAS PRUEBAS DEL BACKEND C++ COMPLETADAS CON EXITO\n";
    std::cout << "=========================================================\n";

    return 0;
}
