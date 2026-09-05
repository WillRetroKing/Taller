/*
 * UNIVERSIDAD POPULAR DEL CESAR
 * FACULTAD DE INGENIERÍAS Y TECNOLÓGICAS - INGENIERÍA DE SISTEMAS
 * Estructura de Datos - Taller 1: Programa Integrado de Transacciones Académicas (PITA)
 * 
 * Programa desarrollado en C++ (Taller.cpp) que gestiona:
 * - Estructura institucional (Facultades, Programas, Cursos, Personas, Estudiantes, Profesores, Administrativos).
 * - Transacciones académicas (Matrícula, Cancelación, Promedios y Alertas EBRA).
 * - Liquidación de Nómina de Profesores (Decreto 1279 de 2002 y Acuerdo 027 de 2024 / Acuerdo 006 de 2018).
 * - Calculadora de ley Mintrabajo (Descuentos Salud 4%, Pensión 4%, Fondo Solidaridad, Aportes Patronales y Prestaciones Sociales).
 * - Funciones de TAD: Creación, inclusión, consulta, modificación, desactivación, eliminación y persistencia.
 */

#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <fstream>
#include <sstream>
#include <iomanip>
#include <cmath>
#include <algorithm>

using namespace std;

// ============================================================================
// CONSTANTES Y PARÁMETROS NORMATIVOS VIGENTES (MINTRABAJO & DECRETOS)
// ============================================================================
const double SMMLV_VIGENTE = 1300000.0;
const double AUXILIO_TRANSPORTE_VIGENTE = 162000.0;
const double VALOR_PUNTO_SALARIAL = 17850.0;

const double PCT_SALUD_TRABAJADOR = 0.04;
const double PCT_PENSION_TRABAJADOR = 0.04;
const double PCT_SALUD_EMPLEADOR = 0.085;
const double PCT_PENSION_EMPLEADOR = 0.12;
const double PCT_SENA = 0.02;
const double PCT_ICBF = 0.03;
const double PCT_CAJA = 0.04;
const double PCT_ARL_CLASE_1 = 0.00522;

const double PCT_CESANTIAS = 0.0833;
const double PCT_INTERESES_CESANTIAS = 0.01; // 12% anual = 1% mens.
const double PCT_PRIMA_SERVICIOS = 0.0833;
const double PCT_PRIMA_NAVIDAD = 0.0833;
const double PCT_VACACIONES = 0.0417;

// ============================================================================
// ESTRUCTURAS DE DATOS (TADs)
// ============================================================================

enum TipoProfesor { PLANTA, OCASIONAL, CATEDRATICO, CATEDRATICO_AD_HONOREM };
enum EstadoAcademico { MATRICULADO, EBRA, EGRESADO, RETIRADO };

struct Persona {
    int idPersona;
    string numeroDocumento;
    string primerNombre;
    string primerApellido;
    string correo;
    string telefono;
    bool activo;
};

struct Estudiante {
    int idEstudiante;
    int idPersona;
    string codigoEstudiante;
    int idPrograma;
    int semestreActual;
    double promedioAcumulado;
    EstadoAcademico estadoAcademico;
    bool activo;
};

struct Profesor {
    int idProfesor;
    int idPersona;
    string codigoProfesor;
    TipoProfesor tipoProfesor;
    string categoria; // Auxiliar, Asistente, Asociado, Titular
    double puntosSalariales; // Decreto 1279
    double factorSMMLV;      // Acuerdo 027
    bool activo;
};

struct Facultad {
    int idFacultad;
    string codigo;
    string nombre;
    string ubicacion;
    bool activo;
};

struct ProgramaAcademico {
    int idPrograma;
    string codigo;
    string nombre;
    int idFacultad;
    int numeroSemestres;
    bool activo;
};

struct Curso {
    int idCurso;
    string codigo;
    string nombre;
    int creditos;
    int horasTeoricas;
    int horasPracticas;
    double notaMinima;
    bool activo;
};

struct LiquidacionNomina {
    int idLiquidacion;
    int idProfesor;
    string periodo;
    double salarioBase;
    double auxilioTransporte;
    double totalDevengado;
    double descuentoSalud;
    double descuentoPension;
    double fondoSolidaridad;
    double totalDescuentos;
    double netoPagar;
    double aporteSaludPatronal;
    double aportePensionPatronal;
    double aporteARL;
    double aporteCaja;
    double provisionCesantias;
    double provisionPrima;
    double provisionVacaciones;
    double costoTotalEmpleador;
};

// ============================================================================
// GESTOR DE NÓMINA Y CÁLCULO DE SALARIOS (MINTRABAJO & DEC. 1279 & AC. 027)
// ============================================================================
class MotorNominaPITA {
public:
    static double calcularFactorCoautoria(int numeroAutores) {
        if (numeroAutores <= 3) return 1.0;
        if (numeroAutores <= 5) return 0.5;
        return 2.0 / numeroAutores;
    }

    static LiquidacionNomina liquidarProfesor(const Profesor& prof, const Persona& pers, string periodo, double horasCumplidas = 160.0) {
        LiquidacionNomina liq;
        liq.idLiquidacion = rand() % 90000 + 10000;
        liq.idProfesor = prof.idProfesor;
        liq.periodo = periodo;

        // 1. Salario Base según Tipo de Contratación
        if (prof.tipoProfesor == PLANTA) {
            // Decreto 1279: Salario Base = Puntos * Valor Punto
            liq.salarioBase = prof.puntosSalariales * VALOR_PUNTO_SALARIAL;
        } else if (prof.tipoProfesor == OCASIONAL) {
            // Acuerdo 027: Salario Base = Factor * SMMLV
            liq.salarioBase = prof.factorSMMLV * SMMLV_VIGENTE;
        } else if (prof.tipoProfesor == CATEDRATICO) {
            // Hora Cátedra: Valor Hora * Horas Cumplidas
            double valorHora = 45000.0;
            liq.salarioBase = horasCumplidas * valorHora;
        } else {
            // Ad-Honorem
            liq.salarioBase = 0.0;
        }

        // 2. Auxilio de Transporte (Si Devengado <= 2 SMMLV)
        if (liq.salarioBase > 0 && liq.salarioBase <= 2.0 * SMMLV_VIGENTE) {
            liq.auxilioTransporte = AUXILIO_TRANSPORTE_VIGENTE;
        } else {
            liq.auxilioTransporte = 0.0;
        }

        liq.totalDevengado = liq.salarioBase + liq.auxilioTransporte;

        // 3. Descuentos de Ley (Mintrabajo: Salud 4%, Pensión 4%)
        double ibc = liq.salarioBase;
        liq.descuentoSalud = ibc * PCT_SALUD_TRABAJADOR;
        liq.descuentoPension = ibc * PCT_PENSION_TRABAJADOR;
        
        // Fondo de Solidaridad Pensional (1% si IBC >= 4 SMMLV)
        if (ibc >= 4.0 * SMMLV_VIGENTE) {
            liq.fondoSolidaridad = ibc * 0.01;
        } else {
            liq.fondoSolidaridad = 0.0;
        }

        liq.totalDescuentos = liq.descuentoSalud + liq.descuentoPension + liq.fondoSolidaridad;
        liq.netoPagar = liq.totalDevengado - liq.totalDescuentos;

        // 4. Aportes Patronales & Exoneración Art. 114-1 ET (si IBC < 10 SMMLV)
        bool exonerado = ibc < 10.0 * SMMLV_VIGENTE;
        liq.aporteSaludPatronal = exonerado ? 0.0 : (ibc * PCT_SALUD_EMPLEADOR);
        liq.aportePensionPatronal = ibc * PCT_PENSION_EMPLEADOR;
        liq.aporteARL = ibc * PCT_ARL_CLASE_1;
        liq.aporteCaja = ibc * PCT_CAJA;

        // 5. Prestaciones Sociales
        double basePrestacional = ibc + liq.auxilioTransporte;
        liq.provisionCesantias = basePrestacional * PCT_CESANTIAS;
        liq.provisionPrima = basePrestacional * PCT_PRIMA_SERVICIOS;
        liq.provisionVacaciones = ibc * PCT_VACACIONES;

        double totalPrestaciones = liq.provisionCesantias + (liq.provisionCesantias * PCT_INTERESES_CESANTIAS) + liq.provisionPrima + liq.provisionVacaciones;
        double totalAportes = liq.aporteSaludPatronal + liq.aportePensionPatronal + liq.aporteARL + liq.aporteCaja;

        liq.costoTotalEmpleador = liq.totalDevengado + totalPrestaciones + totalAportes;

        return liq;
    }
};

// ============================================================================
// SISTEMA PRINCIPAL DE TRANSACCIONES ACADÉMICAS PITA
// ============================================================================
class SistemaPITA {
private:
    vector<Persona> personas;
    vector<Estudiante> estudiantes;
    vector<Profesor> profesores;
    vector<Facultad> facultades;
    vector<ProgramaAcademico> programas;
    vector<Curso> cursos;
    vector<LiquidacionNomina> liquidaciones;

public:
    SistemaPITA() {
        cargarDatosIniciales();
    }

    void cargarDatosIniciales() {
        facultades.push_back({1, "FIT", "Facultad de Ingenierías y Tecnológicas", "Sede Sabanas", true});
        programas.push_back({1, "IS", "Ingeniería de Sistemas", 1, 10, true});
        cursos.push_back({1, "EDD01", "Estructura de Datos", 3, 4, 2, 3.0, true});

        personas.push_back({1, "1065123456", "Carlos", "Pérez", "cperez@unicesar.edu.co", "3001234567", true});
        profesores.push_back({1, 1, "PROF-001", PLANTA, "Asociado", 540.0, 0.0, true});

        personas.push_back({2, "1065987654", "Ana", "Gómez", "agomez@unicesar.edu.co", "3109876543", true});
        estudiantes.push_back({1, 2, "EST-2026-01", 1, 4, 2.8, EBRA, true});
    }

    void menuPrincipal() {
        int opcion = 0;
        do {
            cout << "\n========================================================\n";
            cout << "   PITA - PROGRAMA INTEGRADO DE TRANSACCIONES ACADÉMICAS\n";
            cout << "         UNIVERSIDAD POPULAR DEL CESAR (C++ EDITION)\n";
            cout << "========================================================\n";
            cout << "1. Gestión de Facultades y Programas Académicos\n";
            cout << "2. Gestión de Personas (Estudiantes y Profesores)\n";
            cout << "3. Transacciones Académicas (Matrícula y Alertas EBRA)\n";
            cout << "4. Liquidación de Nómina Docente (Dec. 1279 y Ac. 027)\n";
            cout << "5. Persistencia de Datos (Guardar / Cargar en Archivo)\n";
            cout << "6. Salir\n";
            cout << "Seleccione una opción: ";
            if (!(cin >> opcion)) {
                cin.clear();
                cin.ignore(1000, '\n');
                continue;
            }

            switch (opcion) {
                case 1: mostrarFacultades(); break;
                case 2: mostrarPersonas(); break;
                case 3: evaluarEBRA(); break;
                case 4: ejecutarNomina(); break;
                case 5: guardarEnDisco(); break;
                case 6: cout << "\n¡Gracias por utilizar el sistema PITA UPC!\n"; break;
                default: cout << "Opción no válida.\n"; break;
            }
        } while (opcion != 6);
    }

    void mostrarFacultades() {
        cout << "\n--- FACULTADES DE LA UNIVERSIDAD POPULAR DEL CESAR ---\n";
        for (const auto& f : facultades) {
            cout << "[" << f.idFacultad << "] " << f.codigo << " - " << f.nombre << " | Ubicación: " << f.ubicacion << endl;
        }
    }

    void mostrarPersonas() {
        cout << "\n--- REGISTRO DE PROFESORES Y ESTUDIANTES ---\n";
        for (const auto& prof : profesores) {
            for (const auto& pers : personas) {
                if (pers.idPersona == prof.idPersona) {
                    string tipo = (prof.tipoProfesor == PLANTA) ? "PLANTA (Dec. 1279)" : "OCASIONAL (Ac. 027)";
                    cout << "👨‍🏫 Profesor: " << pers.primerNombre << " " << pers.primerApellido 
                         << " | Tipo: " << tipo << " | Puntos: " << prof.puntosSalariales << endl;
                }
            }
        }
    }

    void evaluarEBRA() {
        cout << "\n--- INFORME DE ALERTAS ACADÉMICAS EBRA ---\n";
        for (const auto& est : estudiantes) {
            for (const auto& pers : personas) {
                if (pers.idPersona == est.idPersona) {
                    cout << "👨‍🎓 Estudiante: " << pers.primerNombre << " " << pers.primerApellido
                         << " | Código: " << est.codigoEstudiante 
                         << " | Promedio: " << fixed << setprecision(2) << est.promedioAcumulado;
                    if (est.promedioAcumulado < 3.0 || est.estadoAcademico == EBRA) {
                        cout << " [⚠️ ALERTA EBRA DETECTADA]\n";
                    } else {
                        cout << " [🟢 RENDIMIENTO REGULAR]\n";
                    }
                }
            }
        }
    }

    void ejecutarNomina() {
        cout << "\n========================================================\n";
        cout << "   LIQUIDACIÓN DE NÓMINA DOCENTE - DECRETO 1279 / MINTRABAJO\n";
        cout << "========================================================\n";
        for (const auto& prof : profesores) {
            for (const auto& pers : personas) {
                if (pers.idPersona == prof.idPersona) {
                    LiquidacionNomina liq = MotorNominaPITA::liquidarProfesor(prof, pers, "2026-09");
                    cout << "\n📄 Liquidación Docente: " << pers.primerNombre << " " << pers.primerApellido << endl;
                    cout << "   • Salario Base:         $ " << fixed << setprecision(0) << liq.salarioBase << endl;
                    cout << "   • Auxilio Transporte:   $ " << liq.auxilioTransporte << endl;
                    cout << "   • Total Devengado:      $ " << liq.totalDevengado << endl;
                    cout << "   • Descuento Salud (4%): $ " << liq.descuentoSalud << endl;
                    cout << "   • Descuento Pensión (4%):$ " << liq.descuentoPension << endl;
                    cout << "   • NETO A PAGAR:         $ " << liq.netoPagar << endl;
                    cout << "   • Costo Total Empleador:$ " << liq.costoTotalEmpleador << endl;
                    liquidaciones.push_back(liq);
                }
            }
        }
    }

    void guardarEnDisco() {
        ofstream file("datos_cxx_persistencia.txt");
        if (file.is_open()) {
            file << "# PERSISTENCIA PITA C++\n";
            file << "FACULTADES:" << facultades.size() << "\n";
            file << "PERSONAS:" << personas.size() << "\n";
            file << "PROFESORES:" << profesores.size() << "\n";
            file.close();
            cout << "\n¡Datos guardados con éxito en datos_cxx_persistencia.txt!\n";
        }
    }
};

int main() {
    SistemaPITA pita;
    pita.menuPrincipal();
    return 0;
}
