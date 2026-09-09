#include "gestores_academicos.h"
#include <ctime>
#include <iomanip>
#include <sstream>
#include <algorithm>
#include <cmath>
#include <unordered_set>

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

static double redondear2(double val) {
    return std::round(val * 100.0) / 100.0;
}

// ==========================================
// GESTOR MATRICULAS
// ==========================================

GestorMatriculas::GestorMatriculas(
    ListaEnlazada<Estudiante>& estudiantes,
    ListaEnlazada<PeriodoAcademico>& periodos,
    ListaEnlazada<OfertaCurso>& ofertas,
    ListaEnlazada<Curso>& cursos,
    ListaEnlazada<MatriculaAcademica>& matriculas,
    ListaEnlazada<DetalleMatricula>& detalles,
    ListaEnlazada<Horario>& horarios,
    ListaEnlazada<ParametroNormativo>& parametros,
    ListaEnlazada<Prerrequisito>& prerrequisitos,
    ListaEnlazada<AlertaAcademica>& alertas
) : estudiantes(estudiantes),
    periodos(periodos),
    ofertas(ofertas),
    cursos(cursos),
    matriculas(matriculas),
    detalles(detalles),
    horarios(horarios),
    parametros(parametros),
    prerrequisitos(prerrequisitos),
    alertas(alertas) {}

int GestorMatriculas::siguienteIdMatricula() {
    int maxId = 0;
    for (const auto& m : matriculas) {
        if (m.idMatricula.has_value() && *m.idMatricula > maxId) {
            maxId = *m.idMatricula;
        }
    }
    return maxId + 1;
}

int GestorMatriculas::siguienteIdDetalle() {
    int maxId = 0;
    for (const auto& d : detalles) {
        if (d.idDetalleMatricula.has_value() && *d.idDetalleMatricula > maxId) {
            maxId = *d.idDetalleMatricula;
        }
    }
    return maxId + 1;
}

int GestorMatriculas::siguienteIdAlerta() {
    int maxId = 0;
    for (const auto& a : alertas) {
        if (a.idAlerta.has_value() && *a.idAlerta > maxId) {
            maxId = *a.idAlerta;
        }
    }
    return maxId + 1;
}

bool GestorMatriculas::esPeriodoAbierto(const PeriodoAcademico& periodo, const std::string& fecha) {
    std::string est = periodo.estado.has_value() ? a_mayusculas(*periodo.estado) : "";
    if (est != "ACTIVO" && est != "ABIERTO") return false;

    if (periodo.fechaInicioMatricula.has_value() && !periodo.fechaInicioMatricula->empty()) {
        if (fecha < *periodo.fechaInicioMatricula) return false;
    }
    if (periodo.fechaFinMatricula.has_value() && !periodo.fechaFinMatricula->empty()) {
        if (fecha > *periodo.fechaFinMatricula) return false;
    }
    return true;
}

bool GestorMatriculas::esActivo(const std::optional<std::string>& estado) {
    if (!estado.has_value()) return false;
    std::string s = a_mayusculas(*estado);
    return (s == "ACTIVO" || s == "MATRICULADO" || s == "ADMITIDO");
}

bool GestorMatriculas::seCruzan(const Horario& primer, const Horario& segundo) {
    if (!primer.diaSemana.has_value() || !segundo.diaSemana.has_value()) return false;
    if (*primer.diaSemana != *segundo.diaSemana) return false;
    if (!primer.horaInicio.has_value() || !primer.horaFin.has_value()) return false;
    if (!segundo.horaInicio.has_value() || !segundo.horaFin.has_value()) return false;
    return (*primer.horaInicio < *segundo.horaFin && *segundo.horaInicio < *primer.horaFin);
}

Curso* GestorMatriculas::cursoDeOferta(int idOferta) {
    for (auto& o : ofertas) {
        if (o.idOfertaCurso.has_value() && *o.idOfertaCurso == idOferta) {
            for (auto& c : cursos) {
                if (c.idCurso.has_value() && o.idCurso.has_value() && *c.idCurso == *o.idCurso) {
                    return &c;
                }
            }
        }
    }
    throw ErrorMatricula("No se encontro curso para la oferta " + std::to_string(idOferta));
}

std::optional<double> GestorMatriculas::parametroDecimal(ParametroNormativoCodigo codigo) {
    std::string codStr = to_string(codigo);
    for (const auto& p : parametros) {
        if (p.codigo.has_value() && to_string(*p.codigo) == codStr) {
            if (p.valor.has_value() && !p.valor->empty()) {
                try {
                    return std::stod(*p.valor);
                } catch (...) {
                    return std::nullopt;
                }
            }
        }
    }
    return std::nullopt;
}

std::optional<int> GestorMatriculas::ultimoPeriodoDelEstudiante(int idEstudiante) {
    std::optional<int> ult;
    for (const auto& m : matriculas) {
        if (m.idEstudiante.has_value() && *m.idEstudiante == idEstudiante) {
            ult = m.idPeriodo;
        }
    }
    return ult;
}

bool GestorMatriculas::cumplePrerrequisitos(int idEstudiante, int idCurso) {
    for (const auto& req : prerrequisitos) {
        if (req.idCurso.has_value() && *req.idCurso == idCurso) {
            bool aprobado = false;
            double notaMin = req.notaMinima.value_or(0.0);
            int cursoReq = req.idCursoRequerido.value_or(-1);

            for (const auto& m : matriculas) {
                if (m.idEstudiante.has_value() && *m.idEstudiante == idEstudiante) {
                    for (const auto& d : detalles) {
                        if (d.idMatricula == m.idMatricula) {
                            if (d.notaFinal.has_value() && *d.notaFinal >= notaMin) {
                                if (d.estadoCurso.has_value() &&
                                    (*d.estadoCurso == EstadoCurso::APROBADO ||
                                     *d.estadoCurso == EstadoCurso::HOMOLOGADO ||
                                     *d.estadoCurso == EstadoCurso::VALIDADO)) {
                                    try {
                                        Curso* c = cursoDeOferta(*d.idOfertaCurso);
                                        if (c && c->idCurso.has_value() && *c->idCurso == cursoReq) {
                                            aprobado = true;
                                            break;
                                        }
                                    } catch (...) {}
                                }
                            }
                        }
                    }
                }
                if (aprobado) break;
            }
            if (!aprobado) return false;
        }
    }
    return true;
}

bool GestorMatriculas::tieneCruceHorario(int idEstudiante, int idOferta, int idPeriodo) {
    ListaEnlazada<Horario> horariosNuevos;
    for (const auto& h : horarios) {
        if (h.idOfertaCurso.has_value() && *h.idOfertaCurso == idOferta) {
            horariosNuevos.push_back(h);
        }
    }

    ListaEnlazada<Horario> horariosActuales;
    for (const auto& m : matriculas) {
        if (m.idEstudiante.has_value() && *m.idEstudiante == idEstudiante &&
            m.idPeriodo.has_value() && *m.idPeriodo == idPeriodo) {
            for (const auto& d : detalles) {
                if (d.idMatricula == m.idMatricula &&
                    (!d.estadoCurso.has_value() || *d.estadoCurso != EstadoCurso::CANCELADO)) {
                    for (const auto& h : horarios) {
                        if (h.idOfertaCurso == d.idOfertaCurso) {
                            horariosActuales.push_back(h);
                        }
                    }
                }
            }
        }
    }

    for (const auto& hn : horariosNuevos) {
        for (const auto& ha : horariosActuales) {
            if (seCruzan(hn, ha)) return true;
        }
    }
    return false;
}

MatriculaAcademica& GestorMatriculas::obtenerOCrearMatricula(Estudiante& est, PeriodoAcademico& per, const std::string& fecha) {
    for (auto& m : matriculas) {
        if (m.idEstudiante == est.idEstudiante && m.idPeriodo == per.idPeriodo) {
            return m;
        }
    }
    MatriculaAcademica nueva;
    nueva.idMatricula = siguienteIdMatricula();
    nueva.idEstudiante = est.idEstudiante;
    nueva.idPeriodo = per.idPeriodo;
    nueva.fechaMatricula = fecha;
    nueva.totalCreditos = 0;
    nueva.estadoMatricula = "ACTIVA";

    matriculas.push_back(std::move(nueva));
    return matriculas.back();
}

DetalleMatricula& GestorMatriculas::matricularCurso(int idEstudiante, int idOferta, const std::string& fechaMatricula) {
    Estudiante* estudiante = nullptr;
    for (auto& e : estudiantes) {
        if (e.idEstudiante.has_value() && *e.idEstudiante == idEstudiante) {
            estudiante = &e;
            break;
        }
    }
    if (!estudiante) throw ErrorMatricula("No existe el estudiante con ID " + std::to_string(idEstudiante));

    OfertaCurso* oferta = nullptr;
    for (auto& o : ofertas) {
        if (o.idOfertaCurso.has_value() && *o.idOfertaCurso == idOferta) {
            oferta = &o;
            break;
        }
    }
    if (!oferta) throw ErrorMatricula("No existe la oferta con ID " + std::to_string(idOferta));

    PeriodoAcademico* periodo = nullptr;
    for (auto& p : periodos) {
        if (p.idPeriodo == oferta->idPeriodo) {
            periodo = &p;
            break;
        }
    }
    if (!periodo) throw ErrorMatricula("No existe el periodo para la oferta");

    Curso* curso = nullptr;
    for (auto& c : cursos) {
        if (c.idCurso == oferta->idCurso) {
            curso = &c;
            break;
        }
    }
    if (!curso) throw ErrorMatricula("No existe el curso para la oferta");

    std::string fecha = fechaMatricula.empty() ? fecha_hoy() : fechaMatricula;

    if (!estudiante->estadoAcademico.has_value() || *estudiante->estadoAcademico != EstadoAcademico::ACTIVO) {
        throw ErrorMatricula("El estudiante no esta activo para matricular cursos");
    }
    if (!esPeriodoAbierto(*periodo, fecha)) {
        throw ErrorMatricula("El periodo no esta abierto para matricula");
    }
    if (!esActivo(oferta->estado)) {
        throw ErrorMatricula("La oferta no esta activa");
    }
    if (!oferta->cupoDisponible.has_value() || *oferta->cupoDisponible <= 0) {
        throw ErrorMatricula("La oferta no tiene cupos disponibles");
    }

    MatriculaAcademica& matricula = obtenerOCrearMatricula(*estudiante, *periodo, fecha);

    int creditosActuales = 0;
    for (const auto& d : detalles) {
        if (d.idMatricula == matricula.idMatricula) {
            if (d.idOfertaCurso.has_value() && *d.idOfertaCurso == idOferta &&
                d.estadoCurso.has_value() && *d.estadoCurso != EstadoCurso::CANCELADO) {
                throw ErrorMatricula("El estudiante ya esta matriculado en esta oferta");
            }
            if (!d.estadoCurso.has_value() || *d.estadoCurso != EstadoCurso::CANCELADO) {
                Curso* c = cursoDeOferta(*d.idOfertaCurso);
                if (c && c->numeroCreditos.has_value()) {
                    creditosActuales += *c->numeroCreditos;
                }
            }
        }
    }

    if (!cumplePrerrequisitos(*estudiante->idEstudiante, curso->idCurso.value_or(-1))) {
        throw ErrorMatricula("El estudiante no cumple los prerrequisitos");
    }

    auto maximo = parametroDecimal(ParametroNormativoCodigo::MAXIMO_CREDITOS_PERIODO);
    if (maximo.has_value() && (creditosActuales + curso->numeroCreditos.value_or(0)) > *maximo) {
        throw ErrorMatricula("Se supera el maximo de creditos permitido");
    }

    if (tieneCruceHorario(idEstudiante, idOferta, periodo->idPeriodo.value_or(-1))) {
        throw ErrorMatricula("El curso tiene cruce de horario");
    }

    DetalleMatricula detalle;
    detalle.idDetalleMatricula = siguienteIdDetalle();
    detalle.idMatricula = matricula.idMatricula;
    detalle.idOfertaCurso = idOferta;
    detalle.fechaInscripcion = fecha;
    detalle.estadoCurso = EstadoCurso::MATRICULADO;

    detalles.push_back(std::move(detalle));
    oferta->cupoDisponible = *oferta->cupoDisponible - 1;
    matricula.totalCreditos = creditosActuales + curso->numeroCreditos.value_or(0);

    return detalles.back();
}

double GestorMatriculas::calcularPromedioPeriodo(int idMatricula) {
    MatriculaAcademica* matricula = nullptr;
    for (auto& m : matriculas) {
        if (m.idMatricula.has_value() && *m.idMatricula == idMatricula) {
            matricula = &m;
            break;
        }
    }
    if (!matricula) throw ErrorMatricula("No existe la matricula con ID " + std::to_string(idMatricula));

    double sumaNotas = 0.0;
    int sumaCreditos = 0;
    for (const auto& d : detalles) {
        if (d.idMatricula == idMatricula) {
            if (!d.notaFinal.has_value() || (d.estadoCurso.has_value() && *d.estadoCurso == EstadoCurso::CANCELADO)) {
                continue;
            }
            Curso* c = cursoDeOferta(*d.idOfertaCurso);
            int cred = c->numeroCreditos.value_or(0);
            sumaNotas += *d.notaFinal * cred;
            sumaCreditos += cred;
        }
    }

    double prom = sumaCreditos > 0 ? (sumaNotas / sumaCreditos) : 0.0;
    matricula->promedioPeriodo = redondear2(prom);

    if (matricula->idEstudiante.has_value()) {
        calcularPromedioAcumulado(*matricula->idEstudiante);
    }
    return *matricula->promedioPeriodo;
}

DetalleMatricula& GestorMatriculas::cancelarCurso(int idEstudiante, int idOferta, const std::string& motivo, const std::string& fechaCancelacion) {
    if (motivo.empty()) {
        throw ErrorMatricula("El motivo de cancelacion es obligatorio");
    }
    std::string fecha = fechaCancelacion.empty() ? fecha_hoy() : fechaCancelacion;

    OfertaCurso* oferta = nullptr;
    for (auto& o : ofertas) {
        if (o.idOfertaCurso.has_value() && *o.idOfertaCurso == idOferta) {
            oferta = &o;
            break;
        }
    }
    if (!oferta) throw ErrorMatricula("No existe la oferta con ID " + std::to_string(idOferta));

    for (const auto& p : periodos) {
        if (p.idPeriodo == oferta->idPeriodo) {
            if (p.fechaLimiteCancelacion.has_value() && !p.fechaLimiteCancelacion->empty()) {
                if (fecha > *p.fechaLimiteCancelacion) {
                    throw ErrorMatricula("La fecha limite de cancelacion ya fue superada");
                }
            }
            break;
        }
    }

    DetalleMatricula* detEncontrado = nullptr;
    MatriculaAcademica* matEncontrada = nullptr;

    for (auto& m : matriculas) {
        if (m.idEstudiante.has_value() && *m.idEstudiante == idEstudiante) {
            for (auto& d : detalles) {
                if (d.idMatricula == m.idMatricula && d.idOfertaCurso.has_value() && *d.idOfertaCurso == idOferta &&
                    (!d.estadoCurso.has_value() || *d.estadoCurso != EstadoCurso::CANCELADO)) {
                    detEncontrado = &d;
                    matEncontrada = &m;
                    break;
                }
            }
        }
        if (detEncontrado) break;
    }

    if (!detEncontrado) {
        throw ErrorMatricula("El estudiante no tiene esa oferta matriculada");
    }

    detEncontrado->estadoCurso = EstadoCurso::CANCELADO;
    detEncontrado->fechaCancelacion = fecha;
    detEncontrado->motivoCancelacion = motivo;
    oferta->cupoDisponible = oferta->cupoDisponible.value_or(0) + 1;

    int totalCred = 0;
    for (const auto& d : detalles) {
        if (d.idMatricula == matEncontrada->idMatricula &&
            (!d.estadoCurso.has_value() || *d.estadoCurso != EstadoCurso::CANCELADO)) {
            Curso* c = cursoDeOferta(*d.idOfertaCurso);
            totalCred += c->numeroCreditos.value_or(0);
        }
    }
    matEncontrada->totalCreditos = totalCred;

    return *detEncontrado;
}

double GestorMatriculas::calcularPromedioAcumulado(int idEstudiante) {
    Estudiante* est = nullptr;
    for (auto& e : estudiantes) {
        if (e.idEstudiante.has_value() && *e.idEstudiante == idEstudiante) {
            est = &e;
            break;
        }
    }
    if (!est) throw ErrorMatricula("No existe el estudiante con ID " + std::to_string(idEstudiante));

    double sumaNotas = 0.0;
    int sumaCreditos = 0;
    for (const auto& m : matriculas) {
        if (m.idEstudiante.has_value() && *m.idEstudiante == idEstudiante) {
            for (const auto& d : detalles) {
                if (d.idMatricula == m.idMatricula) {
                    if (!d.notaFinal.has_value() || (d.estadoCurso.has_value() && *d.estadoCurso == EstadoCurso::CANCELADO)) {
                        continue;
                    }
                    Curso* c = cursoDeOferta(*d.idOfertaCurso);
                    int cred = c->numeroCreditos.value_or(0);
                    sumaNotas += *d.notaFinal * cred;
                    sumaCreditos += cred;
                }
            }
        }
    }

    double prom = sumaCreditos > 0 ? (sumaNotas / sumaCreditos) : 0.0;
    est->promedioAcumulado = redondear2(prom);
    evaluarEbra(idEstudiante);
    return *est->promedioAcumulado;
}

AlertaAcademica* GestorMatriculas::evaluarEbra(int idEstudiante) {
    Estudiante* est = nullptr;
    for (auto& e : estudiantes) {
        if (e.idEstudiante.has_value() && *e.idEstudiante == idEstudiante) {
            est = &e;
            break;
        }
    }
    if (!est) return nullptr;

    auto umbral = parametroDecimal(ParametroNormativoCodigo::PROMEDIO_MINIMO_EBRA);
    if (!umbral.has_value() || !est->promedioAcumulado.has_value() || *est->promedioAcumulado >= *umbral) {
        return nullptr;
    }

    est->estadoAcademico = EstadoAcademico::EBRA;

    for (auto& a : alertas) {
        if (a.idEstudiante.has_value() && *a.idEstudiante == idEstudiante &&
            a.tipoAlerta.has_value() && *a.tipoAlerta == "EBRA" &&
            (!a.atendida.has_value() || !*a.atendida)) {
            return &a;
        }
    }

    AlertaAcademica alerta;
    alerta.idAlerta = siguienteIdAlerta();
    alerta.idEstudiante = idEstudiante;
    alerta.idPeriodo = ultimoPeriodoDelEstudiante(idEstudiante);
    alerta.tipoAlerta = "EBRA";
    alerta.motivo = "El promedio acumulado esta por debajo del minimo institucional";
    alerta.valorObservado = est->promedioAcumulado;
    alerta.valorLimite = *umbral;
    alerta.fechaGeneracion = fecha_hoy();
    alerta.atendida = false;
    alerta.estado = "ACTIVO";

    alertas.push_back(std::move(alerta));
    return &alertas.back();
}

ListaEnlazada<AlertaAcademica> GestorMatriculas::evaluarAlertasPeriodo(int idPeriodo) {
    ListaEnlazada<AlertaAcademica> res;
    std::vector<int> estudiantesPeriodo;
    for (const auto& m : matriculas) {
        if (m.idPeriodo == idPeriodo && m.idEstudiante.has_value()) {
            int idEst = *m.idEstudiante;
            if (std::find(estudiantesPeriodo.begin(), estudiantesPeriodo.end(), idEst) == estudiantesPeriodo.end()) {
                estudiantesPeriodo.push_back(idEst);
            }
        }
    }
    for (int idEst : estudiantesPeriodo) {
        AlertaAcademica* al = evaluarEbra(idEst);
        if (al) {
            res.push_back(*al);
        }
    }
    return res;
}

ListaEnlazada<MatriculaAcademica> GestorMatriculas::consultarMatriculas(
    std::optional<int> idEstudiante,
    std::optional<int> idPeriodo,
    const std::string& estado
) const {
    ListaEnlazada<MatriculaAcademica> res;
    std::string estBusq = a_mayusculas(estado);
    for (const auto& m : matriculas) {
        if (idEstudiante.has_value() && m.idEstudiante != idEstudiante) continue;
        if (idPeriodo.has_value() && m.idPeriodo != idPeriodo) continue;
        if (!estado.empty() && (!m.estadoMatricula.has_value() || a_mayusculas(*m.estadoMatricula) != estBusq)) continue;
        res.push_back(m);
    }
    return res;
}

ListaEnlazada<DetalleMatricula> GestorMatriculas::consultarDetalleMatricula(int idMatricula) const {
    ListaEnlazada<DetalleMatricula> res;
    for (const auto& d : detalles) {
        if (d.idMatricula.has_value() && *d.idMatricula == idMatricula) {
            res.push_back(d);
        }
    }
    return res;
}

MatriculaAcademica* GestorMatriculas::consultarMatriculaEstudiantePeriodo(int idEstudiante, int idPeriodo) {
    for (auto& m : matriculas) {
        if (m.idEstudiante.has_value() && *m.idEstudiante == idEstudiante &&
            m.idPeriodo.has_value() && *m.idPeriodo == idPeriodo) {
            return &m;
        }
    }
    return nullptr;
}

ListaEnlazada<OfertaCurso> GestorMatriculas::listarOfertasDisponibles(int idPeriodo) const {
    ListaEnlazada<OfertaCurso> res;
    for (const auto& o : ofertas) {
        if (o.idPeriodo.has_value() && *o.idPeriodo == idPeriodo &&
            esActivo(o.estado) && o.cupoDisponible.value_or(0) > 0) {
            res.push_back(o);
        }
    }
    return res;
}

// ==========================================
// GESTOR CALIFICACIONES
// ==========================================

GestorCalificaciones::GestorCalificaciones(
    ListaEnlazada<Evaluacion>& evaluaciones,
    ListaEnlazada<Calificacion>& calificaciones,
    ListaEnlazada<DetalleMatricula>& detalles,
    ListaEnlazada<MatriculaAcademica>& matriculas,
    ListaEnlazada<Estudiante>& estudiantes,
    ListaEnlazada<OfertaCurso>& ofertas,
    ListaEnlazada<Curso>& cursos,
    GestorMatriculas& gestorMatriculas
) : evaluaciones(evaluaciones),
    calificaciones(calificaciones),
    detalles(detalles),
    matriculas(matriculas),
    estudiantes(estudiantes),
    ofertas(ofertas),
    cursos(cursos),
    gestorMatriculas(gestorMatriculas) {}

int GestorCalificaciones::siguienteIdCalificacion() {
    int maxId = 0;
    for (const auto& c : calificaciones) {
        if (c.idCalificacion.has_value() && *c.idCalificacion > maxId) {
            maxId = *c.idCalificacion;
        }
    }
    return maxId + 1;
}

int GestorCalificaciones::siguienteIdEvaluacion() {
    int maxId = 0;
    for (const auto& e : evaluaciones) {
        if (e.idEvaluacion.has_value() && *e.idEvaluacion > maxId) {
            maxId = *e.idEvaluacion;
        }
    }
    return maxId + 1;
}

Calificacion& GestorCalificaciones::registrarCalificacion(int idEvaluacion, int idDetalle, double nota, const std::string& fechaRegistro) {
    Evaluacion* evaluacion = nullptr;
    for (auto& ev : evaluaciones) {
        if (ev.idEvaluacion.has_value() && *ev.idEvaluacion == idEvaluacion) {
            evaluacion = &ev;
            break;
        }
    }
    if (!evaluacion) throw ErrorCalificacion("No existe la evaluacion con ID " + std::to_string(idEvaluacion));

    DetalleMatricula* detalle = nullptr;
    for (auto& d : detalles) {
        if (d.idDetalleMatricula.has_value() && *d.idDetalleMatricula == idDetalle) {
            detalle = &d;
            break;
        }
    }
    if (!detalle) throw ErrorCalificacion("No existe el detalle de matricula con ID " + std::to_string(idDetalle));

    if (detalle->estadoCurso.has_value() && (*detalle->estadoCurso == EstadoCurso::CANCELADO || *detalle->estadoCurso == EstadoCurso::RETIRADO)) {
        throw ErrorCalificacion("No se pueden registrar notas para una matricula cancelada o retirada");
    }
    if (evaluacion->estado.has_value() && a_mayusculas(*evaluacion->estado) != "ACTIVO") {
        throw ErrorCalificacion("No se pueden registrar notas para una evaluacion inactiva");
    }
    if (evaluacion->idOfertaCurso != detalle->idOfertaCurso) {
        throw ErrorCalificacion("La evaluacion no pertenece al curso matriculado");
    }
    if (!evaluacion->porcentaje.has_value() || *evaluacion->porcentaje < 0) {
        throw ErrorCalificacion("El porcentaje de la evaluacion no es valido");
    }
    if (nota < 0.0 || nota > 5.0) {
        throw ErrorCalificacion("La nota debe estar entre 0 y 5");
    }

    Calificacion* existente = nullptr;
    for (auto& c : calificaciones) {
        if (c.idEvaluacion.has_value() && *c.idEvaluacion == idEvaluacion &&
            c.idDetalleMatricula.has_value() && *c.idDetalleMatricula == idDetalle) {
            existente = &c;
            break;
        }
    }

    std::string fReg = fechaRegistro.empty() ? fecha_hoy() : fechaRegistro;
    if (!existente) {
        Calificacion c;
        c.idCalificacion = siguienteIdCalificacion();
        c.idEvaluacion = idEvaluacion;
        c.idDetalleMatricula = idDetalle;
        c.nota = nota;
        c.fechaRegistro = fReg;
        c.estado = "ACTIVA";
        calificaciones.push_back(std::move(c));
        existente = &calificaciones.back();
    } else {
        existente->nota = nota;
        existente->fechaRegistro = fReg;
    }

    // Verificar si estan completas
    bool completas = true;
    for (const auto& ev : evaluaciones) {
        if (ev.idOfertaCurso == detalle->idOfertaCurso && (!ev.estado.has_value() || a_mayusculas(*ev.estado) == "ACTIVO")) {
            bool tieneNota = false;
            for (const auto& c : calificaciones) {
                if (c.idEvaluacion == ev.idEvaluacion && c.idDetalleMatricula == idDetalle && c.nota.has_value()) {
                    tieneNota = true;
                    break;
                }
            }
            if (!tieneNota) {
                completas = false;
                break;
            }
        }
    }

    if (completas) {
        recalcularNotaFinal(idDetalle);
    }
    return *existente;
}

double GestorCalificaciones::recalcularNotaFinal(int idDetalle) {
    DetalleMatricula* detalle = nullptr;
    for (auto& d : detalles) {
        if (d.idDetalleMatricula.has_value() && *d.idDetalleMatricula == idDetalle) {
            detalle = &d;
            break;
        }
    }
    if (!detalle) throw ErrorCalificacion("No existe el detalle de matricula");

    ListaEnlazada<Evaluacion> evals;
    double porcentajeTotal = 0.0;
    for (const auto& ev : evaluaciones) {
        if (ev.idOfertaCurso == detalle->idOfertaCurso && (!ev.estado.has_value() || a_mayusculas(*ev.estado) == "ACTIVO")) {
            evals.push_back(ev);
            porcentajeTotal += ev.porcentaje.value_or(0.0);
        }
    }

    if (evals.empty()) {
        throw ErrorCalificacion("El curso no tiene evaluaciones activas");
    }
    if (std::abs(porcentajeTotal - 100.0) > 0.001) {
        throw ErrorCalificacion("Los porcentajes de evaluacion deben sumar 100");
    }

    double notaPonderada = 0.0;
    for (const auto& ev : evals) {
        bool encontrada = false;
        for (const auto& c : calificaciones) {
            if (c.idEvaluacion == ev.idEvaluacion && c.idDetalleMatricula == idDetalle && c.nota.has_value()) {
                notaPonderada += (*c.nota) * (ev.porcentaje.value_or(0.0) / 100.0);
                encontrada = true;
                break;
            }
        }
        if (!encontrada) {
            throw ErrorCalificacion("Faltan calificaciones para calcular la nota final");
        }
    }

    detalle->notaFinal = redondear2(notaPonderada);
    double notaMinima = 3.0;
    for (const auto& of : ofertas) {
        if (of.idOfertaCurso == detalle->idOfertaCurso) {
            for (const auto& cu : cursos) {
                if (cu.idCurso == of.idCurso) {
                    notaMinima = cu.notaMinimaAprobatoria.value_or(3.0);
                    break;
                }
            }
            break;
        }
    }
    detalle->estadoCurso = (*detalle->notaFinal >= notaMinima) ? EstadoCurso::APROBADO : EstadoCurso::REPROBADO;

    if (detalle->idMatricula.has_value()) {
        gestorMatriculas.calcularPromedioPeriodo(*detalle->idMatricula);
    }
    return *detalle->notaFinal;
}

Evaluacion& GestorCalificaciones::crearEvaluacion(
    int idOferta,
    const std::string& nombre,
    const std::string& tipo,
    double porcentaje,
    const std::string& fechaProgramada
) {
    if (nombre.empty()) {
        throw ErrorCalificacion("El nombre de la evaluacion es obligatorio");
    }
    static const std::unordered_set<std::string> TIPOS_VALIDOS = {
        "PARCIAL", "QUIZ", "TALLER", "LABORATORIO", "TRABAJO", "EXAMEN_FINAL", "PARTICIPACION", "OTRO"
    };
    if (TIPOS_VALIDOS.find(tipo) == TIPOS_VALIDOS.end()) {
        throw ErrorCalificacion("Tipo de evaluacion invalido: " + tipo);
    }
    if (porcentaje <= 0.0 || porcentaje > 100.0) {
        throw ErrorCalificacion("El porcentaje debe estar entre 0 y 100");
    }

    OfertaCurso* oferta = nullptr;
    for (auto& o : ofertas) {
        if (o.idOfertaCurso.has_value() && *o.idOfertaCurso == idOferta) {
            oferta = &o;
            break;
        }
    }
    if (!oferta) throw ErrorCalificacion("No existe la oferta con ID " + std::to_string(idOferta));
    if (!GestorMatriculas::esActivo(oferta->estado)) {
        throw ErrorCalificacion("No se pueden crear evaluaciones para una oferta inactiva");
    }

    double porcentajeActual = porcentajeTotalEvaluaciones(idOferta);
    if (porcentajeActual + porcentaje > 100.0) {
        throw ErrorCalificacion("El porcentaje total excede el 100%");
    }

    Evaluacion ev;
    ev.idEvaluacion = siguienteIdEvaluacion();
    ev.idOfertaCurso = idOferta;
    ev.nombre = nombre;
    ev.tipo = tipo;
    ev.porcentaje = porcentaje;
    ev.fechaProgramada = fechaProgramada.empty() ? fecha_hoy() : fechaProgramada;
    ev.estado = "ACTIVO";

    evaluaciones.push_back(std::move(ev));
    return evaluaciones.back();
}

ListaEnlazada<Evaluacion> GestorCalificaciones::consultarEvaluacionesOferta(int idOferta) const {
    ListaEnlazada<Evaluacion> res;
    for (const auto& e : evaluaciones) {
        if (e.idOfertaCurso.has_value() && *e.idOfertaCurso == idOferta &&
            (!e.estado.has_value() || a_mayusculas(*e.estado) == "ACTIVO")) {
            res.push_back(e);
        }
    }
    return res;
}

double GestorCalificaciones::porcentajeTotalEvaluaciones(int idOferta) const {
    double total = 0.0;
    for (const auto& e : evaluaciones) {
        if (e.idOfertaCurso.has_value() && *e.idOfertaCurso == idOferta &&
            (!e.estado.has_value() || a_mayusculas(*e.estado) == "ACTIVO")) {
            total += e.porcentaje.value_or(0.0);
        }
    }
    return total;
}

std::pair<bool, std::string> GestorCalificaciones::validarEvaluacionesParaFinal(int idOferta) const {
    auto evals = consultarEvaluacionesOferta(idOferta);
    if (evals.empty()) {
        return {false, "No hay evaluaciones registradas"};
    }
    double porc = porcentajeTotalEvaluaciones(idOferta);
    if (std::abs(porc - 100.0) > 0.001) {
        return {false, "El porcentaje total debe ser 100%"};
    }
    return {true, "Evaluaciones validas para calculo de nota final"};
}

Evaluacion& GestorCalificaciones::modificarEvaluacion(
    int idEvaluacion,
    const std::optional<std::string>& nombre,
    const std::optional<double>& porcentaje,
    const std::optional<std::string>& fechaProgramada
) {
    Evaluacion* ev = nullptr;
    for (auto& e : evaluaciones) {
        if (e.idEvaluacion.has_value() && *e.idEvaluacion == idEvaluacion) {
            ev = &e;
            break;
        }
    }
    if (!ev) throw ErrorCalificacion("No existe la evaluacion con ID " + std::to_string(idEvaluacion));

    if (nombre.has_value()) {
        if (nombre->empty()) throw ErrorCalificacion("El nombre no puede estar vacio");
        ev->nombre = *nombre;
    }
    if (porcentaje.has_value()) {
        if (*porcentaje <= 0.0 || *porcentaje > 100.0) {
            throw ErrorCalificacion("El porcentaje debe estar entre 0 y 100");
        }
        double porcOtras = 0.0;
        for (const auto& o : evaluaciones) {
            if (o.idOfertaCurso == ev->idOfertaCurso && o.idEvaluacion != idEvaluacion &&
                (!o.estado.has_value() || a_mayusculas(*o.estado) == "ACTIVO")) {
                porcOtras += o.porcentaje.value_or(0.0);
            }
        }
        if (porcOtras + *porcentaje > 100.0) {
            throw ErrorCalificacion("El nuevo porcentaje excederia el 100%");
        }
        ev->porcentaje = *porcentaje;
    }
    if (fechaProgramada.has_value()) {
        ev->fechaProgramada = *fechaProgramada;
    }
    return *ev;
}

} // namespace pita
