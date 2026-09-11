#include "gestor_persistencia.h"
#include <filesystem>
#include <cmath>

namespace fs = std::filesystem;

namespace pita {

GestorPersistencia::GestorPersistencia(const std::string& rutaDirectorio) : directorio(rutaDirectorio) {
    if (!fs::exists(directorio)) {
        fs::create_directories(directorio);
    }
}

std::vector<std::string> GestorPersistencia::split(const std::string& s, char delim) {
    std::vector<std::string> tokens;
    size_t start = 0;
    size_t end = s.find(delim);
    while (end != std::string::npos) {
        tokens.push_back(s.substr(start, end - start));
        start = end + 1;
        end = s.find(delim, start);
    }
    tokens.push_back(s.substr(start));
    return tokens;
}

std::string GestorPersistencia::doubleToString(double val) {
    std::ostringstream ss;
    if (std::floor(val) == val) {
        ss << static_cast<long long>(val);
    } else {
        ss << std::fixed << std::setprecision(4) << val;
        std::string str = ss.str();
        while (str.back() == '0') str.pop_back();
        if (str.back() == '.') str.pop_back();
        return str;
    }
    return ss.str();
}

std::optional<int> GestorPersistencia::parseOptionalInt(const std::string& s) {
    if (s.empty()) return std::nullopt;
    try { return std::stoi(s); } catch (...) { return std::nullopt; }
}

std::optional<double> GestorPersistencia::parseOptionalDouble(const std::string& s) {
    if (s.empty()) return std::nullopt;
    try { return std::stod(s); } catch (...) { return std::nullopt; }
}

std::optional<bool> GestorPersistencia::parseOptionalBool(const std::string& s) {
    if (s.empty()) return std::nullopt;
    return (s == "1" || s == "true" || s == "True");
}

std::optional<std::string> GestorPersistencia::parseOptionalString(const std::string& s) {
    if (s.empty()) return std::nullopt;
    return s;
}

std::optional<EstadoAcademico> GestorPersistencia::parseOptionalEstadoAcademico(const std::string& s) {
    if (s.empty()) return std::nullopt;
    return estado_academico_from_string(s);
}

std::optional<TipoProfesor> GestorPersistencia::parseOptionalTipoProfesor(const std::string& s) {
    if (s.empty()) return std::nullopt;
    return tipo_profesor_from_string(s);
}

std::optional<Dedicacion> GestorPersistencia::parseOptionalDedicacion(const std::string& s) {
    if (s.empty()) return std::nullopt;
    return dedicacion_from_string(s);
}

std::optional<EstadoCurso> GestorPersistencia::parseOptionalEstadoCurso(const std::string& s) {
    if (s.empty()) return std::nullopt;
    return estado_curso_from_string(s);
}

std::optional<CategoriaDocenteCodigo> GestorPersistencia::parseOptionalCategoriaDocente(const std::string& s) {
    if (s.empty()) return std::nullopt;
    return categoria_docente_from_string(s);
}

std::optional<TipoFactor> GestorPersistencia::parseOptionalTipoFactor(const std::string& s) {
    if (s.empty()) return std::nullopt;
    return tipo_factor_from_string(s);
}

std::optional<ParametroNormativoCodigo> GestorPersistencia::parseOptionalParametroNormativo(const std::string& s) {
    if (s.empty()) return std::nullopt;
    return parametro_normativo_from_string(s);
}

std::string GestorPersistencia::serializarUniversidad(const Universidad& e) {
    std::string res;
    res += (e.idUniversidad.has_value() ? std::to_string(*e.idUniversidad) : "");
    res += '|';
    res += (e.nombre.has_value() ? *e.nombre : "");
    res += '|';
    res += (e.nit.has_value() ? *e.nit : "");
    res += '|';
    res += (e.codigoInstitucional.has_value() ? *e.codigoInstitucional : "");
    res += '|';
    res += (e.direccion.has_value() ? *e.direccion : "");
    res += '|';
    res += (e.ciudad.has_value() ? *e.ciudad : "");
    res += '|';
    res += (e.departamento.has_value() ? *e.departamento : "");
    res += '|';
    res += (e.telefono.has_value() ? *e.telefono : "");
    res += '|';
    res += (e.correoInstitucional.has_value() ? *e.correoInstitucional : "");
    res += '|';
    res += (e.sitioWeb.has_value() ? *e.sitioWeb : "");
    res += '|';
    res += (e.estado.has_value() ? *e.estado : "");
    res += '|';
    res += (e.cajaCompensacion.has_value() ? *e.cajaCompensacion : "");
    res += '|';
    res += (e.arl.has_value() ? *e.arl : "");
    res += '|';
    res += (e.aplicaExoneracionLey1819.has_value() ? (*e.aplicaExoneracionLey1819 ? "1" : "0") : "");
    return res;
}

Universidad GestorPersistencia::deserializarUniversidad(const std::string& linea) {
    std::vector<std::string> parts = split(linea, '|');
    if (parts.size() < 11) {
        throw std::runtime_error("Error en universidad.txt: se esperaban al menos 11 campos pero se obtuvieron " + std::to_string(parts.size()));
    }
    Universidad e;
    e.idUniversidad = parseOptionalInt(parts[0]);
    e.nombre = parseOptionalString(parts[1]);
    e.nit = parseOptionalString(parts[2]);
    e.codigoInstitucional = parseOptionalString(parts[3]);
    e.direccion = parseOptionalString(parts[4]);
    e.ciudad = parseOptionalString(parts[5]);
    e.departamento = parseOptionalString(parts[6]);
    e.telefono = parseOptionalString(parts[7]);
    e.correoInstitucional = parseOptionalString(parts[8]);
    e.sitioWeb = parseOptionalString(parts[9]);
    e.estado = parseOptionalString(parts[10]);
    if (parts.size() > 11) e.cajaCompensacion = parseOptionalString(parts[11]);
    if (parts.size() > 12) e.arl = parseOptionalString(parts[12]);
    if (parts.size() > 13) e.aplicaExoneracionLey1819 = parseOptionalBool(parts[13]);
    return e;
}

ListaEnlazada<Universidad> GestorPersistencia::cargarUniversidad() {
    ListaEnlazada<Universidad> lista;
    std::string ruta = (fs::path(directorio) / "universidad.txt").string();
    if (!fs::exists(ruta)) return lista;
    std::ifstream arch(ruta);
    if (!arch.is_open()) return lista;
    std::string linea;
    while (std::getline(arch, linea)) {
        if (!linea.empty() && linea.back() == '\r') linea.pop_back();
        if (linea.empty()) continue;
        lista.push_back(deserializarUniversidad(linea));
    }
    return lista;
}

void GestorPersistencia::guardarUniversidad(const ListaEnlazada<Universidad>& lista) {
    std::string ruta = (fs::path(directorio) / "universidad.txt").string();
    std::ofstream arch(ruta);
    if (!arch.is_open()) throw std::runtime_error("No se pudo abrir para escritura: " + ruta);
    for (const auto& e : lista) {
        arch << serializarUniversidad(e) << "\n";
    }
}

std::string GestorPersistencia::serializarFacultad(const Facultad& e) {
    std::string res;
    res += (e.idFacultad.has_value() ? std::to_string(*e.idFacultad) : "");
    res += '|';
    res += (e.codigoFacultad.has_value() ? *e.codigoFacultad : "");
    res += '|';
    res += (e.nombre.has_value() ? *e.nombre : "");
    res += '|';
    res += (e.descripcion.has_value() ? *e.descripcion : "");
    res += '|';
    res += (e.ubicacion.has_value() ? *e.ubicacion : "");
    res += '|';
    res += (e.telefono.has_value() ? *e.telefono : "");
    res += '|';
    res += (e.correo.has_value() ? *e.correo : "");
    res += '|';
    res += (e.idDecano.has_value() ? std::to_string(*e.idDecano) : "");
    res += '|';
    res += (e.fechaCreacion.has_value() ? *e.fechaCreacion : "");
    res += '|';
    res += (e.estado.has_value() ? *e.estado : "");
    return res;
}

Facultad GestorPersistencia::deserializarFacultad(const std::string& linea) {
    std::vector<std::string> parts = split(linea, '|');
    if (parts.size() < 10) {
        throw std::runtime_error("Error en facultades.txt: se esperaban al menos 10 campos pero se obtuvieron " + std::to_string(parts.size()));
    }
    Facultad e;
    e.idFacultad = parseOptionalInt(parts[0]);
    e.codigoFacultad = parseOptionalString(parts[1]);
    e.nombre = parseOptionalString(parts[2]);
    e.descripcion = parseOptionalString(parts[3]);
    e.ubicacion = parseOptionalString(parts[4]);
    e.telefono = parseOptionalString(parts[5]);
    e.correo = parseOptionalString(parts[6]);
    e.idDecano = parseOptionalInt(parts[7]);
    e.fechaCreacion = parseOptionalString(parts[8]);
    e.estado = parseOptionalString(parts[9]);
    return e;
}

ListaEnlazada<Facultad> GestorPersistencia::cargarFacultad() {
    ListaEnlazada<Facultad> lista;
    std::string ruta = (fs::path(directorio) / "facultades.txt").string();
    if (!fs::exists(ruta)) return lista;
    std::ifstream arch(ruta);
    if (!arch.is_open()) return lista;
    std::string linea;
    while (std::getline(arch, linea)) {
        if (!linea.empty() && linea.back() == '\r') linea.pop_back();
        if (linea.empty()) continue;
        lista.push_back(deserializarFacultad(linea));
    }
    return lista;
}

void GestorPersistencia::guardarFacultad(const ListaEnlazada<Facultad>& lista) {
    std::string ruta = (fs::path(directorio) / "facultades.txt").string();
    std::ofstream arch(ruta);
    if (!arch.is_open()) throw std::runtime_error("No se pudo abrir para escritura: " + ruta);
    for (const auto& e : lista) {
        arch << serializarFacultad(e) << "\n";
    }
}

std::string GestorPersistencia::serializarProgramaAcademico(const ProgramaAcademico& e) {
    std::string res;
    res += (e.idPrograma.has_value() ? std::to_string(*e.idPrograma) : "");
    res += '|';
    res += (e.codigoPrograma.has_value() ? *e.codigoPrograma : "");
    res += '|';
    res += (e.nombre.has_value() ? *e.nombre : "");
    res += '|';
    res += (e.nivelFormacion.has_value() ? *e.nivelFormacion : "");
    res += '|';
    res += (e.modalidad.has_value() ? *e.modalidad : "");
    res += '|';
    res += (e.numeroSemestres.has_value() ? std::to_string(*e.numeroSemestres) : "");
    res += '|';
    res += (e.totalCreditos.has_value() ? std::to_string(*e.totalCreditos) : "");
    res += '|';
    res += (e.registroCalificado.has_value() ? *e.registroCalificado : "");
    res += '|';
    res += (e.fechaCreacion.has_value() ? *e.fechaCreacion : "");
    res += '|';
    res += (e.idDirector.has_value() ? std::to_string(*e.idDirector) : "");
    res += '|';
    res += (e.idFacultad.has_value() ? std::to_string(*e.idFacultad) : "");
    res += '|';
    res += (e.estado.has_value() ? *e.estado : "");
    return res;
}

ProgramaAcademico GestorPersistencia::deserializarProgramaAcademico(const std::string& linea) {
    std::vector<std::string> parts = split(linea, '|');
    if (parts.size() != 12) {
        throw std::runtime_error("Error en programas.txt: se esperaban 12 campos pero se obtuvieron " + std::to_string(parts.size()));
    }
    ProgramaAcademico e;
    e.idPrograma = parseOptionalInt(parts[0]);
    e.codigoPrograma = parseOptionalString(parts[1]);
    e.nombre = parseOptionalString(parts[2]);
    e.nivelFormacion = parseOptionalString(parts[3]);
    e.modalidad = parseOptionalString(parts[4]);
    e.numeroSemestres = parseOptionalInt(parts[5]);
    e.totalCreditos = parseOptionalInt(parts[6]);
    e.registroCalificado = parseOptionalString(parts[7]);
    e.fechaCreacion = parseOptionalString(parts[8]);
    e.idDirector = parseOptionalInt(parts[9]);
    e.idFacultad = parseOptionalInt(parts[10]);
    e.estado = parseOptionalString(parts[11]);
    return e;
}

ListaEnlazada<ProgramaAcademico> GestorPersistencia::cargarProgramaAcademico() {
    ListaEnlazada<ProgramaAcademico> lista;
    std::string ruta = (fs::path(directorio) / "programas.txt").string();
    if (!fs::exists(ruta)) return lista;
    std::ifstream arch(ruta);
    if (!arch.is_open()) return lista;
    std::string linea;
    while (std::getline(arch, linea)) {
        if (!linea.empty() && linea.back() == '\r') linea.pop_back();
        if (linea.empty()) continue;
        lista.push_back(deserializarProgramaAcademico(linea));
    }
    return lista;
}

void GestorPersistencia::guardarProgramaAcademico(const ListaEnlazada<ProgramaAcademico>& lista) {
    std::string ruta = (fs::path(directorio) / "programas.txt").string();
    std::ofstream arch(ruta);
    if (!arch.is_open()) throw std::runtime_error("No se pudo abrir para escritura: " + ruta);
    for (const auto& e : lista) {
        arch << serializarProgramaAcademico(e) << "\n";
    }
}

std::string GestorPersistencia::serializarPlanEstudio(const PlanEstudio& e) {
    std::string res;
    res += (e.idPlanEstudio.has_value() ? std::to_string(*e.idPlanEstudio) : "");
    res += '|';
    res += (e.codigo.has_value() ? *e.codigo : "");
    res += '|';
    res += (e.nombre.has_value() ? *e.nombre : "");
    res += '|';
    res += (e.version.has_value() ? *e.version : "");
    res += '|';
    res += (e.fechaInicioVigencia.has_value() ? *e.fechaInicioVigencia : "");
    res += '|';
    res += (e.fechaFinVigencia.has_value() ? *e.fechaFinVigencia : "");
    res += '|';
    res += (e.totalCreditos.has_value() ? std::to_string(*e.totalCreditos) : "");
    res += '|';
    res += (e.idPrograma.has_value() ? std::to_string(*e.idPrograma) : "");
    res += '|';
    res += (e.estado.has_value() ? *e.estado : "");
    return res;
}

PlanEstudio GestorPersistencia::deserializarPlanEstudio(const std::string& linea) {
    std::vector<std::string> parts = split(linea, '|');
    if (parts.size() != 9) {
        throw std::runtime_error("Error en planes_estudio.txt: se esperaban 9 campos pero se obtuvieron " + std::to_string(parts.size()));
    }
    PlanEstudio e;
    e.idPlanEstudio = parseOptionalInt(parts[0]);
    e.codigo = parseOptionalString(parts[1]);
    e.nombre = parseOptionalString(parts[2]);
    e.version = parseOptionalString(parts[3]);
    e.fechaInicioVigencia = parseOptionalString(parts[4]);
    e.fechaFinVigencia = parseOptionalString(parts[5]);
    e.totalCreditos = parseOptionalInt(parts[6]);
    e.idPrograma = parseOptionalInt(parts[7]);
    e.estado = parseOptionalString(parts[8]);
    return e;
}

ListaEnlazada<PlanEstudio> GestorPersistencia::cargarPlanEstudio() {
    ListaEnlazada<PlanEstudio> lista;
    std::string ruta = (fs::path(directorio) / "planes_estudio.txt").string();
    if (!fs::exists(ruta)) return lista;
    std::ifstream arch(ruta);
    if (!arch.is_open()) return lista;
    std::string linea;
    while (std::getline(arch, linea)) {
        if (!linea.empty() && linea.back() == '\r') linea.pop_back();
        if (linea.empty()) continue;
        lista.push_back(deserializarPlanEstudio(linea));
    }
    return lista;
}

void GestorPersistencia::guardarPlanEstudio(const ListaEnlazada<PlanEstudio>& lista) {
    std::string ruta = (fs::path(directorio) / "planes_estudio.txt").string();
    std::ofstream arch(ruta);
    if (!arch.is_open()) throw std::runtime_error("No se pudo abrir para escritura: " + ruta);
    for (const auto& e : lista) {
        arch << serializarPlanEstudio(e) << "\n";
    }
}

std::string GestorPersistencia::serializarDetallePlanEstudio(const DetallePlanEstudio& e) {
    std::string res;
    res += (e.idDetallePlan.has_value() ? std::to_string(*e.idDetallePlan) : "");
    res += '|';
    res += (e.idPlanEstudio.has_value() ? std::to_string(*e.idPlanEstudio) : "");
    res += '|';
    res += (e.idCurso.has_value() ? std::to_string(*e.idCurso) : "");
    res += '|';
    res += (e.semestreSugerido.has_value() ? std::to_string(*e.semestreSugerido) : "");
    res += '|';
    res += (e.tipoCurso.has_value() ? *e.tipoCurso : "");
    res += '|';
    res += (e.numeroCreditos.has_value() ? std::to_string(*e.numeroCreditos) : "");
    res += '|';
    res += (e.esObligatorio.has_value() ? (*e.esObligatorio ? "1" : "0") : "");
    res += '|';
    res += (e.estado.has_value() ? *e.estado : "");
    return res;
}

DetallePlanEstudio GestorPersistencia::deserializarDetallePlanEstudio(const std::string& linea) {
    std::vector<std::string> parts = split(linea, '|');
    if (parts.size() != 8) {
        throw std::runtime_error("Error en detalles_plan_estudio.txt: se esperaban 8 campos pero se obtuvieron " + std::to_string(parts.size()));
    }
    DetallePlanEstudio e;
    e.idDetallePlan = parseOptionalInt(parts[0]);
    e.idPlanEstudio = parseOptionalInt(parts[1]);
    e.idCurso = parseOptionalInt(parts[2]);
    e.semestreSugerido = parseOptionalInt(parts[3]);
    e.tipoCurso = parseOptionalString(parts[4]);
    e.numeroCreditos = parseOptionalInt(parts[5]);
    e.esObligatorio = parseOptionalBool(parts[6]);
    e.estado = parseOptionalString(parts[7]);
    return e;
}

ListaEnlazada<DetallePlanEstudio> GestorPersistencia::cargarDetallePlanEstudio() {
    ListaEnlazada<DetallePlanEstudio> lista;
    std::string ruta = (fs::path(directorio) / "detalles_plan_estudio.txt").string();
    if (!fs::exists(ruta)) return lista;
    std::ifstream arch(ruta);
    if (!arch.is_open()) return lista;
    std::string linea;
    while (std::getline(arch, linea)) {
        if (!linea.empty() && linea.back() == '\r') linea.pop_back();
        if (linea.empty()) continue;
        lista.push_back(deserializarDetallePlanEstudio(linea));
    }
    return lista;
}

void GestorPersistencia::guardarDetallePlanEstudio(const ListaEnlazada<DetallePlanEstudio>& lista) {
    std::string ruta = (fs::path(directorio) / "detalles_plan_estudio.txt").string();
    std::ofstream arch(ruta);
    if (!arch.is_open()) throw std::runtime_error("No se pudo abrir para escritura: " + ruta);
    for (const auto& e : lista) {
        arch << serializarDetallePlanEstudio(e) << "\n";
    }
}

std::string GestorPersistencia::serializarCurso(const Curso& e) {
    std::string res;
    res += (e.idCurso.has_value() ? std::to_string(*e.idCurso) : "");
    res += '|';
    res += (e.codigoCurso.has_value() ? *e.codigoCurso : "");
    res += '|';
    res += (e.nombre.has_value() ? *e.nombre : "");
    res += '|';
    res += (e.descripcion.has_value() ? *e.descripcion : "");
    res += '|';
    res += (e.numeroCreditos.has_value() ? std::to_string(*e.numeroCreditos) : "");
    res += '|';
    res += (e.horasTeoricas.has_value() ? std::to_string(*e.horasTeoricas) : "");
    res += '|';
    res += (e.horasPracticas.has_value() ? std::to_string(*e.horasPracticas) : "");
    res += '|';
    res += (e.horasTrabajoIndependiente.has_value() ? std::to_string(*e.horasTrabajoIndependiente) : "");
    res += '|';
    res += (e.cupoSugerido.has_value() ? std::to_string(*e.cupoSugerido) : "");
    res += '|';
    double nota = (e.notaMinimaAprobatoria.has_value() && *e.notaMinimaAprobatoria > 0.0) ? *e.notaMinimaAprobatoria : 3.0;
    res += doubleToString(nota);
    res += '|';
    res += (e.estado.has_value() ? *e.estado : "");
    return res;
}

Curso GestorPersistencia::deserializarCurso(const std::string& linea) {
    std::vector<std::string> parts = split(linea, '|');
    if (parts.size() != 11) {
        throw std::runtime_error("Error en cursos.txt: se esperaban 11 campos pero se obtuvieron " + std::to_string(parts.size()));
    }
    Curso e;
    e.idCurso = parseOptionalInt(parts[0]);
    e.codigoCurso = parseOptionalString(parts[1]);
    e.nombre = parseOptionalString(parts[2]);
    e.descripcion = parseOptionalString(parts[3]);
    e.numeroCreditos = parseOptionalInt(parts[4]);
    e.horasTeoricas = parseOptionalInt(parts[5]);
    e.horasPracticas = parseOptionalInt(parts[6]);
    e.horasTrabajoIndependiente = parseOptionalInt(parts[7]);
    e.cupoSugerido = parseOptionalInt(parts[8]);
    e.notaMinimaAprobatoria = parseOptionalDouble(parts[9]);
    if (!e.notaMinimaAprobatoria.has_value() || *e.notaMinimaAprobatoria <= 0.0) {
        e.notaMinimaAprobatoria = 3.0;
    }
    e.estado = parseOptionalString(parts[10]);
    return e;
}

ListaEnlazada<Curso> GestorPersistencia::cargarCurso() {
    ListaEnlazada<Curso> lista;
    std::string ruta = (fs::path(directorio) / "cursos.txt").string();
    if (!fs::exists(ruta)) return lista;
    std::ifstream arch(ruta);
    if (!arch.is_open()) return lista;
    std::string linea;
    while (std::getline(arch, linea)) {
        if (!linea.empty() && linea.back() == '\r') linea.pop_back();
        if (linea.empty()) continue;
        lista.push_back(deserializarCurso(linea));
    }
    return lista;
}

void GestorPersistencia::guardarCurso(const ListaEnlazada<Curso>& lista) {
    std::string ruta = (fs::path(directorio) / "cursos.txt").string();
    std::ofstream arch(ruta);
    if (!arch.is_open()) throw std::runtime_error("No se pudo abrir para escritura: " + ruta);
    for (const auto& e : lista) {
        arch << serializarCurso(e) << "\n";
    }
}

std::string GestorPersistencia::serializarPrerrequisito(const Prerrequisito& e) {
    std::string res;
    res += (e.idPrerrequisito.has_value() ? std::to_string(*e.idPrerrequisito) : "");
    res += '|';
    res += (e.idCurso.has_value() ? std::to_string(*e.idCurso) : "");
    res += '|';
    res += (e.idCursoRequerido.has_value() ? std::to_string(*e.idCursoRequerido) : "");
    res += '|';
    res += (e.tipoRequisito.has_value() ? *e.tipoRequisito : "");
    res += '|';
    res += (e.notaMinima.has_value() ? doubleToString(*e.notaMinima) : "");
    res += '|';
    res += (e.creditosMinimos.has_value() ? std::to_string(*e.creditosMinimos) : "");
    res += '|';
    res += (e.estado.has_value() ? *e.estado : "");
    return res;
}

Prerrequisito GestorPersistencia::deserializarPrerrequisito(const std::string& linea) {
    std::vector<std::string> parts = split(linea, '|');
    if (parts.size() != 7) {
        throw std::runtime_error("Error en prerrequisitos.txt: se esperaban 7 campos pero se obtuvieron " + std::to_string(parts.size()));
    }
    Prerrequisito e;
    e.idPrerrequisito = parseOptionalInt(parts[0]);
    e.idCurso = parseOptionalInt(parts[1]);
    e.idCursoRequerido = parseOptionalInt(parts[2]);
    e.tipoRequisito = parseOptionalString(parts[3]);
    e.notaMinima = parseOptionalDouble(parts[4]);
    e.creditosMinimos = parseOptionalInt(parts[5]);
    e.estado = parseOptionalString(parts[6]);
    return e;
}

ListaEnlazada<Prerrequisito> GestorPersistencia::cargarPrerrequisito() {
    ListaEnlazada<Prerrequisito> lista;
    std::string ruta = (fs::path(directorio) / "prerrequisitos.txt").string();
    if (!fs::exists(ruta)) return lista;
    std::ifstream arch(ruta);
    if (!arch.is_open()) return lista;
    std::string linea;
    while (std::getline(arch, linea)) {
        if (!linea.empty() && linea.back() == '\r') linea.pop_back();
        if (linea.empty()) continue;
        lista.push_back(deserializarPrerrequisito(linea));
    }
    return lista;
}

void GestorPersistencia::guardarPrerrequisito(const ListaEnlazada<Prerrequisito>& lista) {
    std::string ruta = (fs::path(directorio) / "prerrequisitos.txt").string();
    std::ofstream arch(ruta);
    if (!arch.is_open()) throw std::runtime_error("No se pudo abrir para escritura: " + ruta);
    for (const auto& e : lista) {
        arch << serializarPrerrequisito(e) << "\n";
    }
}

std::string GestorPersistencia::serializarPersona(const Persona& e) {
    std::string res;
    res += (e.idPersona.has_value() ? std::to_string(*e.idPersona) : "");
    res += '|';
    res += (e.tipoDocumento.has_value() ? *e.tipoDocumento : "");
    res += '|';
    res += (e.numeroDocumento.has_value() ? *e.numeroDocumento : "");
    res += '|';
    res += (e.primerNombre.has_value() ? *e.primerNombre : "");
    res += '|';
    res += (e.segundoNombre.has_value() ? *e.segundoNombre : "");
    res += '|';
    res += (e.primerApellido.has_value() ? *e.primerApellido : "");
    res += '|';
    res += (e.segundoApellido.has_value() ? *e.segundoApellido : "");
    res += '|';
    res += (e.fechaNacimiento.has_value() ? *e.fechaNacimiento : "");
    res += '|';
    res += (e.direccion.has_value() ? *e.direccion : "");
    res += '|';
    res += (e.telefono.has_value() ? *e.telefono : "");
    res += '|';
    res += (e.correoPersonal.has_value() ? *e.correoPersonal : "");
    res += '|';
    res += (e.correoInstitucional.has_value() ? *e.correoInstitucional : "");
    res += '|';
    res += (e.ciudadResidencia.has_value() ? *e.ciudadResidencia : "");
    res += '|';
    res += (e.fechaRegistro.has_value() ? *e.fechaRegistro : "");
    res += '|';
    res += (e.estado.has_value() ? *e.estado : "");
    return res;
}

Persona GestorPersistencia::deserializarPersona(const std::string& linea) {
    std::vector<std::string> parts = split(linea, '|');
    if (parts.size() != 15) {
        throw std::runtime_error("Error en personas.txt: se esperaban 15 campos pero se obtuvieron " + std::to_string(parts.size()));
    }
    Persona e;
    e.idPersona = parseOptionalInt(parts[0]);
    e.tipoDocumento = parseOptionalString(parts[1]);
    e.numeroDocumento = parseOptionalString(parts[2]);
    e.primerNombre = parseOptionalString(parts[3]);
    e.segundoNombre = parseOptionalString(parts[4]);
    e.primerApellido = parseOptionalString(parts[5]);
    e.segundoApellido = parseOptionalString(parts[6]);
    e.fechaNacimiento = parseOptionalString(parts[7]);
    e.direccion = parseOptionalString(parts[8]);
    e.telefono = parseOptionalString(parts[9]);
    e.correoPersonal = parseOptionalString(parts[10]);
    e.correoInstitucional = parseOptionalString(parts[11]);
    e.ciudadResidencia = parseOptionalString(parts[12]);
    e.fechaRegistro = parseOptionalString(parts[13]);
    e.estado = parseOptionalString(parts[14]);
    return e;
}

ListaEnlazada<Persona> GestorPersistencia::cargarPersona() {
    ListaEnlazada<Persona> lista;
    std::string ruta = (fs::path(directorio) / "personas.txt").string();
    if (!fs::exists(ruta)) return lista;
    std::ifstream arch(ruta);
    if (!arch.is_open()) return lista;
    std::string linea;
    while (std::getline(arch, linea)) {
        if (!linea.empty() && linea.back() == '\r') linea.pop_back();
        if (linea.empty()) continue;
        lista.push_back(deserializarPersona(linea));
    }
    return lista;
}

void GestorPersistencia::guardarPersona(const ListaEnlazada<Persona>& lista) {
    std::string ruta = (fs::path(directorio) / "personas.txt").string();
    std::ofstream arch(ruta);
    if (!arch.is_open()) throw std::runtime_error("No se pudo abrir para escritura: " + ruta);
    for (const auto& e : lista) {
        arch << serializarPersona(e) << "\n";
    }
}

std::string GestorPersistencia::serializarEstudiante(const Estudiante& e) {
    std::string res;
    res += (e.idEstudiante.has_value() ? std::to_string(*e.idEstudiante) : "");
    res += '|';
    res += (e.idPersona.has_value() ? std::to_string(*e.idPersona) : "");
    res += '|';
    res += (e.codigoEstudiante.has_value() ? *e.codigoEstudiante : "");
    res += '|';
    res += (e.idPrograma.has_value() ? std::to_string(*e.idPrograma) : "");
    res += '|';
    res += (e.idPlanEstudio.has_value() ? std::to_string(*e.idPlanEstudio) : "");
    res += '|';
    res += (e.fechaIngreso.has_value() ? *e.fechaIngreso : "");
    res += '|';
    res += (e.semestreActual.has_value() ? std::to_string(*e.semestreActual) : "");
    res += '|';
    res += (e.creditosAprobados.has_value() ? std::to_string(*e.creditosAprobados) : "");
    res += '|';
    res += (e.promedioAcumulado.has_value() ? doubleToString(*e.promedioAcumulado) : "");
    res += '|';
    res += (e.estadoAcademico.has_value() ? to_string(*e.estadoAcademico) : "");
    res += '|';
    res += (e.estado.has_value() ? *e.estado : "");
    return res;
}

Estudiante GestorPersistencia::deserializarEstudiante(const std::string& linea) {
    std::vector<std::string> parts = split(linea, '|');
    if (parts.size() != 11) {
        throw std::runtime_error("Error en estudiantes.txt: se esperaban 11 campos pero se obtuvieron " + std::to_string(parts.size()));
    }
    Estudiante e;
    e.idEstudiante = parseOptionalInt(parts[0]);
    e.idPersona = parseOptionalInt(parts[1]);
    e.codigoEstudiante = parseOptionalString(parts[2]);
    e.idPrograma = parseOptionalInt(parts[3]);
    e.idPlanEstudio = parseOptionalInt(parts[4]);
    e.fechaIngreso = parseOptionalString(parts[5]);
    e.semestreActual = parseOptionalInt(parts[6]);
    e.creditosAprobados = parseOptionalInt(parts[7]);
    e.promedioAcumulado = parseOptionalDouble(parts[8]);
    e.estadoAcademico = parseOptionalEstadoAcademico(parts[9]);
    e.estado = parseOptionalString(parts[10]);
    return e;
}

ListaEnlazada<Estudiante> GestorPersistencia::cargarEstudiante() {
    ListaEnlazada<Estudiante> lista;
    std::string ruta = (fs::path(directorio) / "estudiantes.txt").string();
    if (!fs::exists(ruta)) return lista;
    std::ifstream arch(ruta);
    if (!arch.is_open()) return lista;
    std::string linea;
    while (std::getline(arch, linea)) {
        if (!linea.empty() && linea.back() == '\r') linea.pop_back();
        if (linea.empty()) continue;
        lista.push_back(deserializarEstudiante(linea));
    }
    return lista;
}

void GestorPersistencia::guardarEstudiante(const ListaEnlazada<Estudiante>& lista) {
    std::string ruta = (fs::path(directorio) / "estudiantes.txt").string();
    std::ofstream arch(ruta);
    if (!arch.is_open()) throw std::runtime_error("No se pudo abrir para escritura: " + ruta);
    for (const auto& e : lista) {
        arch << serializarEstudiante(e) << "\n";
    }
}

std::string GestorPersistencia::serializarProfesor(const Profesor& e) {
    std::string res;
    res += (e.idProfesor.has_value() ? std::to_string(*e.idProfesor) : "");
    res += '|';
    res += (e.idPersona.has_value() ? std::to_string(*e.idPersona) : "");
    res += '|';
    res += (e.codigoProfesor.has_value() ? *e.codigoProfesor : "");
    res += '|';
    res += (e.idProgramaPrincipal.has_value() ? std::to_string(*e.idProgramaPrincipal) : "");
    res += '|';
    res += (e.fechaVinculacion.has_value() ? *e.fechaVinculacion : "");
    res += '|';
    res += (e.tipoProfesor.has_value() ? to_string(*e.tipoProfesor) : "");
    res += '|';
    res += (e.categoriaDocente.has_value() ? *e.categoriaDocente : "");
    res += '|';
    res += (e.dedicacion.has_value() ? to_string(*e.dedicacion) : "");
    res += '|';
    res += (e.maximoNivelEstudio.has_value() ? *e.maximoNivelEstudio : "");
    res += '|';
    res += (e.tituloProfesional.has_value() ? *e.tituloProfesional : "");
    res += '|';
    res += (e.areaConocimiento.has_value() ? *e.areaConocimiento : "");
    res += '|';
    res += (e.numeroHorasSemanales.has_value() ? doubleToString(*e.numeroHorasSemanales) : "");
    res += '|';
    res += (e.puntosSalariales.has_value() ? doubleToString(*e.puntosSalariales) : "");
    res += '|';
    res += (e.estado.has_value() ? *e.estado : "");
    res += '|';
    res += (e.regimenSalarial.has_value() ? *e.regimenSalarial : "");
    res += '|';
    res += (e.modalidadVinculacion.has_value() ? *e.modalidadVinculacion : "");
    res += '|';
    res += (e.perteneceCarreraDocente.has_value() ? (*e.perteneceCarreraDocente ? "1" : "0") : "");
    res += '|';
    res += (e.fechaIngresoCarreraDocente.has_value() ? *e.fechaIngresoCarreraDocente : "");
    res += '|';
    res += (e.fechaPosesion.has_value() ? *e.fechaPosesion : "");
    res += '|';
    res += (e.fechaUltimaVinculacion.has_value() ? *e.fechaUltimaVinculacion : "");
    res += '|';
    res += (e.fechaRetiro.has_value() ? *e.fechaRetiro : "");
    res += '|';
    res += (e.motivoRetiro.has_value() ? *e.motivoRetiro : "");
    res += '|';
    res += (e.actoAdministrativoIngreso.has_value() ? *e.actoAdministrativoIngreso : "");
    res += '|';
    res += (e.actoAdministrativoRetiro.has_value() ? *e.actoAdministrativoRetiro : "");
    res += '|';
    res += (e.evaluacionDesempenoAnterior.has_value() ? doubleToString(*e.evaluacionDesempenoAnterior) : "");
    res += '|';
    res += (e.puedeSerVinculadoSiguientePeriodo.has_value() ? (*e.puedeSerVinculadoSiguientePeriodo ? "1" : "0") : "");
    res += '|';
    res += (e.idCategoriaDocente.has_value() ? std::to_string(*e.idCategoriaDocente) : "");
    res += '|';
    res += (e.categoriaReconocida.has_value() ? *e.categoriaReconocida : "");
    res += '|';
    res += (e.categoriaInstitucionOrigen.has_value() ? *e.categoriaInstitucionOrigen : "");
    res += '|';
    res += (e.fechaReconocimientoCategoria.has_value() ? *e.fechaReconocimientoCategoria : "");
    res += '|';
    res += (e.actoReconocimientoCategoria.has_value() ? *e.actoReconocimientoCategoria : "");
    res += '|';
    res += (e.categoriaComoInvestigador.has_value() ? *e.categoriaComoInvestigador : "");
    res += '|';
    res += (e.grupoInvestigacion.has_value() ? *e.grupoInvestigacion : "");
    res += '|';
    res += (e.categoriaGrupoInvestigacion.has_value() ? *e.categoriaGrupoInvestigacion : "");
    res += '|';
    res += (e.perteneceSemillero.has_value() ? (*e.perteneceSemillero ? "1" : "0") : "");
    res += '|';
    res += (e.semilleroInvestigacion.has_value() ? *e.semilleroInvestigacion : "");
    res += '|';
    res += (e.productividadInvestigativaVigente.has_value() ? (*e.productividadInvestigativaVigente ? "1" : "0") : "");
    res += '|';
    res += (e.participaProyectoInvestigacionVigente.has_value() ? (*e.participaProyectoInvestigacionVigente ? "1" : "0") : "");
    res += '|';
    res += (e.certificacionVicerrectoriaInvestigacion.has_value() ? *e.certificacionVicerrectoriaInvestigacion : "");
    res += '|';
    res += (e.nivelPosgradoReconocido.has_value() ? *e.nivelPosgradoReconocido : "");
    res += '|';
    res += (e.tituloPosgradoReconocido.has_value() ? *e.tituloPosgradoReconocido : "");
    res += '|';
    res += (e.fechaObtencionPosgrado.has_value() ? *e.fechaObtencionPosgrado : "");
    res += '|';
    res += (e.tituloConvalidado.has_value() ? (*e.tituloConvalidado ? "1" : "0") : "");
    res += '|';
    res += (e.numeroResolucionConvalidacion.has_value() ? *e.numeroResolucionConvalidacion : "");
    res += '|';
    res += (e.esEspecializacionClinica.has_value() ? (*e.esEspecializacionClinica ? "1" : "0") : "");
    res += '|';
    res += (e.posgradoRelacionadoConAreaDesempeno.has_value() ? (*e.posgradoRelacionadoConAreaDesempeno ? "1" : "0") : "");
    res += '|';
    res += (e.factorBonificacionPosgrado.has_value() ? doubleToString(*e.factorBonificacionPosgrado) : "");
    res += '|';
    res += (e.fechaInicioReconocimientoPosgrado.has_value() ? *e.fechaInicioReconocimientoPosgrado : "");
    res += '|';
    res += (e.fechaFinReconocimientoPosgrado.has_value() ? *e.fechaFinReconocimientoPosgrado : "");
    res += '|';
    res += (e.aniosExperienciaDocenteUniversitaria.has_value() ? doubleToString(*e.aniosExperienciaDocenteUniversitaria) : "");
    res += '|';
    res += (e.periodosExperienciaDocenteUniversitaria.has_value() ? std::to_string(*e.periodosExperienciaDocenteUniversitaria) : "");
    res += '|';
    res += (e.aniosExperienciaInvestigacion.has_value() ? doubleToString(*e.aniosExperienciaInvestigacion) : "");
    res += '|';
    res += (e.aniosExperienciaProfesional.has_value() ? doubleToString(*e.aniosExperienciaProfesional) : "");
    res += '|';
    res += (e.aniosExperienciaDireccionAcademica.has_value() ? doubleToString(*e.aniosExperienciaDireccionAcademica) : "");
    res += '|';
    res += (e.experienciaEquivalenteTiempoCompleto.has_value() ? doubleToString(*e.experienciaEquivalenteTiempoCompleto) : "");
    res += '|';
    res += (e.experienciaCertificada.has_value() ? (*e.experienciaCertificada ? "1" : "0") : "");
    res += '|';
    res += (e.fechaCorteExperiencia.has_value() ? *e.fechaCorteExperiencia : "");
    res += '|';
    res += (e.puntosExperienciaReconocidos.has_value() ? doubleToString(*e.puntosExperienciaReconocidos) : "");
    return res;
}

Profesor GestorPersistencia::deserializarProfesor(const std::string& linea) {
    std::vector<std::string> parts = split(linea, '|');
    if (parts.size() != 58) {
        throw std::runtime_error("Error en profesores.txt: se esperaban 58 campos pero se obtuvieron " + std::to_string(parts.size()));
    }
    Profesor e;
    e.idProfesor = parseOptionalInt(parts[0]);
    e.idPersona = parseOptionalInt(parts[1]);
    e.codigoProfesor = parseOptionalString(parts[2]);
    e.idProgramaPrincipal = parseOptionalInt(parts[3]);
    e.fechaVinculacion = parseOptionalString(parts[4]);
    e.tipoProfesor = parseOptionalTipoProfesor(parts[5]);
    e.categoriaDocente = parseOptionalString(parts[6]);
    e.dedicacion = parseOptionalDedicacion(parts[7]);
    e.maximoNivelEstudio = parseOptionalString(parts[8]);
    e.tituloProfesional = parseOptionalString(parts[9]);
    e.areaConocimiento = parseOptionalString(parts[10]);
    e.numeroHorasSemanales = parseOptionalDouble(parts[11]);
    e.puntosSalariales = parseOptionalDouble(parts[12]);
    e.estado = parseOptionalString(parts[13]);
    e.regimenSalarial = parseOptionalString(parts[14]);
    e.modalidadVinculacion = parseOptionalString(parts[15]);
    e.perteneceCarreraDocente = parseOptionalBool(parts[16]);
    e.fechaIngresoCarreraDocente = parseOptionalString(parts[17]);
    e.fechaPosesion = parseOptionalString(parts[18]);
    e.fechaUltimaVinculacion = parseOptionalString(parts[19]);
    e.fechaRetiro = parseOptionalString(parts[20]);
    e.motivoRetiro = parseOptionalString(parts[21]);
    e.actoAdministrativoIngreso = parseOptionalString(parts[22]);
    e.actoAdministrativoRetiro = parseOptionalString(parts[23]);
    e.evaluacionDesempenoAnterior = parseOptionalDouble(parts[24]);
    e.puedeSerVinculadoSiguientePeriodo = parseOptionalBool(parts[25]);
    e.idCategoriaDocente = parseOptionalInt(parts[26]);
    e.categoriaReconocida = parseOptionalString(parts[27]);
    e.categoriaInstitucionOrigen = parseOptionalString(parts[28]);
    e.fechaReconocimientoCategoria = parseOptionalString(parts[29]);
    e.actoReconocimientoCategoria = parseOptionalString(parts[30]);
    e.categoriaComoInvestigador = parseOptionalString(parts[31]);
    e.grupoInvestigacion = parseOptionalString(parts[32]);
    e.categoriaGrupoInvestigacion = parseOptionalString(parts[33]);
    e.perteneceSemillero = parseOptionalBool(parts[34]);
    e.semilleroInvestigacion = parseOptionalString(parts[35]);
    e.productividadInvestigativaVigente = parseOptionalBool(parts[36]);
    e.participaProyectoInvestigacionVigente = parseOptionalBool(parts[37]);
    e.certificacionVicerrectoriaInvestigacion = parseOptionalString(parts[38]);
    e.nivelPosgradoReconocido = parseOptionalString(parts[39]);
    e.tituloPosgradoReconocido = parseOptionalString(parts[40]);
    e.fechaObtencionPosgrado = parseOptionalString(parts[41]);
    e.tituloConvalidado = parseOptionalBool(parts[42]);
    e.numeroResolucionConvalidacion = parseOptionalString(parts[43]);
    e.esEspecializacionClinica = parseOptionalBool(parts[44]);
    e.posgradoRelacionadoConAreaDesempeno = parseOptionalBool(parts[45]);
    e.factorBonificacionPosgrado = parseOptionalDouble(parts[46]);
    e.fechaInicioReconocimientoPosgrado = parseOptionalString(parts[47]);
    e.fechaFinReconocimientoPosgrado = parseOptionalString(parts[48]);
    e.aniosExperienciaDocenteUniversitaria = parseOptionalDouble(parts[49]);
    e.periodosExperienciaDocenteUniversitaria = parseOptionalInt(parts[50]);
    e.aniosExperienciaInvestigacion = parseOptionalDouble(parts[51]);
    e.aniosExperienciaProfesional = parseOptionalDouble(parts[52]);
    e.aniosExperienciaDireccionAcademica = parseOptionalDouble(parts[53]);
    e.experienciaEquivalenteTiempoCompleto = parseOptionalDouble(parts[54]);
    e.experienciaCertificada = parseOptionalBool(parts[55]);
    e.fechaCorteExperiencia = parseOptionalString(parts[56]);
    e.puntosExperienciaReconocidos = parseOptionalDouble(parts[57]);
    return e;
}

ListaEnlazada<Profesor> GestorPersistencia::cargarProfesor() {
    ListaEnlazada<Profesor> lista;
    std::string ruta = (fs::path(directorio) / "profesores.txt").string();
    if (!fs::exists(ruta)) return lista;
    std::ifstream arch(ruta);
    if (!arch.is_open()) return lista;
    std::string linea;
    while (std::getline(arch, linea)) {
        if (!linea.empty() && linea.back() == '\r') linea.pop_back();
        if (linea.empty()) continue;
        lista.push_back(deserializarProfesor(linea));
    }
    return lista;
}

void GestorPersistencia::guardarProfesor(const ListaEnlazada<Profesor>& lista) {
    std::string ruta = (fs::path(directorio) / "profesores.txt").string();
    std::ofstream arch(ruta);
    if (!arch.is_open()) throw std::runtime_error("No se pudo abrir para escritura: " + ruta);
    for (const auto& e : lista) {
        arch << serializarProfesor(e) << "\n";
    }
}

std::string GestorPersistencia::serializarAdministrativo(const Administrativo& e) {
    std::string res;
    res += (e.idAdministrativo.has_value() ? std::to_string(*e.idAdministrativo) : "");
    res += '|';
    res += (e.idPersona.has_value() ? std::to_string(*e.idPersona) : "");
    res += '|';
    res += (e.codigoEmpleado.has_value() ? *e.codigoEmpleado : "");
    res += '|';
    res += (e.cargo.has_value() ? *e.cargo : "");
    res += '|';
    res += (e.dependencia.has_value() ? *e.dependencia : "");
    res += '|';
    res += (e.categoria.has_value() ? *e.categoria : "");
    res += '|';
    res += (e.tipoContratacion.has_value() ? *e.tipoContratacion : "");
    res += '|';
    res += (e.fechaVinculacion.has_value() ? *e.fechaVinculacion : "");
    res += '|';
    res += (e.salarioBase.has_value() ? doubleToString(*e.salarioBase) : "");
    res += '|';
    res += (e.estado.has_value() ? *e.estado : "");
    return res;
}

Administrativo GestorPersistencia::deserializarAdministrativo(const std::string& linea) {
    std::vector<std::string> parts = split(linea, '|');
    if (parts.size() != 10) {
        throw std::runtime_error("Error en administrativos.txt: se esperaban 10 campos pero se obtuvieron " + std::to_string(parts.size()));
    }
    Administrativo e;
    e.idAdministrativo = parseOptionalInt(parts[0]);
    e.idPersona = parseOptionalInt(parts[1]);
    e.codigoEmpleado = parseOptionalString(parts[2]);
    e.cargo = parseOptionalString(parts[3]);
    e.dependencia = parseOptionalString(parts[4]);
    e.categoria = parseOptionalString(parts[5]);
    e.tipoContratacion = parseOptionalString(parts[6]);
    e.fechaVinculacion = parseOptionalString(parts[7]);
    e.salarioBase = parseOptionalDouble(parts[8]);
    e.estado = parseOptionalString(parts[9]);
    return e;
}

ListaEnlazada<Administrativo> GestorPersistencia::cargarAdministrativo() {
    ListaEnlazada<Administrativo> lista;
    std::string ruta = (fs::path(directorio) / "administrativos.txt").string();
    if (!fs::exists(ruta)) return lista;
    std::ifstream arch(ruta);
    if (!arch.is_open()) return lista;
    std::string linea;
    while (std::getline(arch, linea)) {
        if (!linea.empty() && linea.back() == '\r') linea.pop_back();
        if (linea.empty()) continue;
        lista.push_back(deserializarAdministrativo(linea));
    }
    return lista;
}

void GestorPersistencia::guardarAdministrativo(const ListaEnlazada<Administrativo>& lista) {
    std::string ruta = (fs::path(directorio) / "administrativos.txt").string();
    std::ofstream arch(ruta);
    if (!arch.is_open()) throw std::runtime_error("No se pudo abrir para escritura: " + ruta);
    for (const auto& e : lista) {
        arch << serializarAdministrativo(e) << "\n";
    }
}

std::string GestorPersistencia::serializarPeriodoAcademico(const PeriodoAcademico& e) {
    std::string res;
    res += (e.idPeriodo.has_value() ? std::to_string(*e.idPeriodo) : "");
    res += '|';
    res += (e.codigo.has_value() ? *e.codigo : "");
    res += '|';
    res += (e.nombre.has_value() ? *e.nombre : "");
    res += '|';
    res += (e.anio.has_value() ? std::to_string(*e.anio) : "");
    res += '|';
    res += (e.numeroPeriodo.has_value() ? std::to_string(*e.numeroPeriodo) : "");
    res += '|';
    res += (e.fechaInicio.has_value() ? *e.fechaInicio : "");
    res += '|';
    res += (e.fechaFin.has_value() ? *e.fechaFin : "");
    res += '|';
    res += (e.fechaInicioMatricula.has_value() ? *e.fechaInicioMatricula : "");
    res += '|';
    res += (e.fechaFinMatricula.has_value() ? *e.fechaFinMatricula : "");
    res += '|';
    res += (e.fechaLimiteCancelacion.has_value() ? *e.fechaLimiteCancelacion : "");
    res += '|';
    res += (e.estado.has_value() ? *e.estado : "");
    return res;
}

PeriodoAcademico GestorPersistencia::deserializarPeriodoAcademico(const std::string& linea) {
    std::vector<std::string> parts = split(linea, '|');
    if (parts.size() != 11) {
        throw std::runtime_error("Error en periodos_academicos.txt: se esperaban 11 campos pero se obtuvieron " + std::to_string(parts.size()));
    }
    PeriodoAcademico e;
    e.idPeriodo = parseOptionalInt(parts[0]);
    e.codigo = parseOptionalString(parts[1]);
    e.nombre = parseOptionalString(parts[2]);
    e.anio = parseOptionalInt(parts[3]);
    e.numeroPeriodo = parseOptionalInt(parts[4]);
    e.fechaInicio = parseOptionalString(parts[5]);
    e.fechaFin = parseOptionalString(parts[6]);
    e.fechaInicioMatricula = parseOptionalString(parts[7]);
    e.fechaFinMatricula = parseOptionalString(parts[8]);
    e.fechaLimiteCancelacion = parseOptionalString(parts[9]);
    e.estado = parseOptionalString(parts[10]);
    return e;
}

ListaEnlazada<PeriodoAcademico> GestorPersistencia::cargarPeriodoAcademico() {
    ListaEnlazada<PeriodoAcademico> lista;
    std::string ruta = (fs::path(directorio) / "periodos_academicos.txt").string();
    if (!fs::exists(ruta)) return lista;
    std::ifstream arch(ruta);
    if (!arch.is_open()) return lista;
    std::string linea;
    while (std::getline(arch, linea)) {
        if (!linea.empty() && linea.back() == '\r') linea.pop_back();
        if (linea.empty()) continue;
        lista.push_back(deserializarPeriodoAcademico(linea));
    }
    return lista;
}

void GestorPersistencia::guardarPeriodoAcademico(const ListaEnlazada<PeriodoAcademico>& lista) {
    std::string ruta = (fs::path(directorio) / "periodos_academicos.txt").string();
    std::ofstream arch(ruta);
    if (!arch.is_open()) throw std::runtime_error("No se pudo abrir para escritura: " + ruta);
    for (const auto& e : lista) {
        arch << serializarPeriodoAcademico(e) << "\n";
    }
}

std::string GestorPersistencia::serializarOfertaCurso(const OfertaCurso& e) {
    std::string res;
    res += (e.idOfertaCurso.has_value() ? std::to_string(*e.idOfertaCurso) : "");
    res += '|';
    res += (e.idCurso.has_value() ? std::to_string(*e.idCurso) : "");
    res += '|';
    res += (e.idPeriodo.has_value() ? std::to_string(*e.idPeriodo) : "");
    res += '|';
    res += (e.grupo.has_value() ? *e.grupo : "");
    res += '|';
    res += (e.cupoMaximo.has_value() ? std::to_string(*e.cupoMaximo) : "");
    res += '|';
    res += (e.cupoDisponible.has_value() ? std::to_string(*e.cupoDisponible) : "");
    res += '|';
    res += (e.modalidad.has_value() ? *e.modalidad : "");
    res += '|';
    res += (e.aula.has_value() ? *e.aula : "");
    res += '|';
    res += (e.sede.has_value() ? *e.sede : "");
    res += '|';
    res += (e.fechaInicio.has_value() ? *e.fechaInicio : "");
    res += '|';
    res += (e.fechaFin.has_value() ? *e.fechaFin : "");
    res += '|';
    res += (e.estado.has_value() ? *e.estado : "");
    return res;
}

OfertaCurso GestorPersistencia::deserializarOfertaCurso(const std::string& linea) {
    std::vector<std::string> parts = split(linea, '|');
    if (parts.size() != 12) {
        throw std::runtime_error("Error en ofertas_curso.txt: se esperaban 12 campos pero se obtuvieron " + std::to_string(parts.size()));
    }
    OfertaCurso e;
    e.idOfertaCurso = parseOptionalInt(parts[0]);
    e.idCurso = parseOptionalInt(parts[1]);
    e.idPeriodo = parseOptionalInt(parts[2]);
    e.grupo = parseOptionalString(parts[3]);
    e.cupoMaximo = parseOptionalInt(parts[4]);
    e.cupoDisponible = parseOptionalInt(parts[5]);
    e.modalidad = parseOptionalString(parts[6]);
    e.aula = parseOptionalString(parts[7]);
    e.sede = parseOptionalString(parts[8]);
    e.fechaInicio = parseOptionalString(parts[9]);
    e.fechaFin = parseOptionalString(parts[10]);
    e.estado = parseOptionalString(parts[11]);
    return e;
}

ListaEnlazada<OfertaCurso> GestorPersistencia::cargarOfertaCurso() {
    ListaEnlazada<OfertaCurso> lista;
    std::string ruta = (fs::path(directorio) / "ofertas_curso.txt").string();
    if (!fs::exists(ruta)) return lista;
    std::ifstream arch(ruta);
    if (!arch.is_open()) return lista;
    std::string linea;
    while (std::getline(arch, linea)) {
        if (!linea.empty() && linea.back() == '\r') linea.pop_back();
        if (linea.empty()) continue;
        lista.push_back(deserializarOfertaCurso(linea));
    }
    return lista;
}

void GestorPersistencia::guardarOfertaCurso(const ListaEnlazada<OfertaCurso>& lista) {
    std::string ruta = (fs::path(directorio) / "ofertas_curso.txt").string();
    std::ofstream arch(ruta);
    if (!arch.is_open()) throw std::runtime_error("No se pudo abrir para escritura: " + ruta);
    for (const auto& e : lista) {
        arch << serializarOfertaCurso(e) << "\n";
    }
}

std::string GestorPersistencia::serializarAsignacionDocente(const AsignacionDocente& e) {
    std::string res;
    res += (e.idAsignacion.has_value() ? std::to_string(*e.idAsignacion) : "");
    res += '|';
    res += (e.idProfesor.has_value() ? std::to_string(*e.idProfesor) : "");
    res += '|';
    res += (e.idOfertaCurso.has_value() ? std::to_string(*e.idOfertaCurso) : "");
    res += '|';
    res += (e.rolDocente.has_value() ? *e.rolDocente : "");
    res += '|';
    res += (e.numeroHoras.has_value() ? doubleToString(*e.numeroHoras) : "");
    res += '|';
    res += (e.porcentajeResponsabilidad.has_value() ? doubleToString(*e.porcentajeResponsabilidad) : "");
    res += '|';
    res += (e.fechaAsignacion.has_value() ? *e.fechaAsignacion : "");
    res += '|';
    res += (e.estado.has_value() ? *e.estado : "");
    return res;
}

AsignacionDocente GestorPersistencia::deserializarAsignacionDocente(const std::string& linea) {
    std::vector<std::string> parts = split(linea, '|');
    if (parts.size() != 8) {
        throw std::runtime_error("Error en asignaciones_docentes.txt: se esperaban 8 campos pero se obtuvieron " + std::to_string(parts.size()));
    }
    AsignacionDocente e;
    e.idAsignacion = parseOptionalInt(parts[0]);
    e.idProfesor = parseOptionalInt(parts[1]);
    e.idOfertaCurso = parseOptionalInt(parts[2]);
    e.rolDocente = parseOptionalString(parts[3]);
    e.numeroHoras = parseOptionalDouble(parts[4]);
    e.porcentajeResponsabilidad = parseOptionalDouble(parts[5]);
    e.fechaAsignacion = parseOptionalString(parts[6]);
    e.estado = parseOptionalString(parts[7]);
    return e;
}

ListaEnlazada<AsignacionDocente> GestorPersistencia::cargarAsignacionDocente() {
    ListaEnlazada<AsignacionDocente> lista;
    std::string ruta = (fs::path(directorio) / "asignaciones_docentes.txt").string();
    if (!fs::exists(ruta)) return lista;
    std::ifstream arch(ruta);
    if (!arch.is_open()) return lista;
    std::string linea;
    while (std::getline(arch, linea)) {
        if (!linea.empty() && linea.back() == '\r') linea.pop_back();
        if (linea.empty()) continue;
        lista.push_back(deserializarAsignacionDocente(linea));
    }
    return lista;
}

void GestorPersistencia::guardarAsignacionDocente(const ListaEnlazada<AsignacionDocente>& lista) {
    std::string ruta = (fs::path(directorio) / "asignaciones_docentes.txt").string();
    std::ofstream arch(ruta);
    if (!arch.is_open()) throw std::runtime_error("No se pudo abrir para escritura: " + ruta);
    for (const auto& e : lista) {
        arch << serializarAsignacionDocente(e) << "\n";
    }
}

std::string GestorPersistencia::serializarHorario(const Horario& e) {
    std::string res;
    res += (e.idHorario.has_value() ? std::to_string(*e.idHorario) : "");
    res += '|';
    res += (e.idOfertaCurso.has_value() ? std::to_string(*e.idOfertaCurso) : "");
    res += '|';
    res += (e.diaSemana.has_value() ? *e.diaSemana : "");
    res += '|';
    res += (e.horaInicio.has_value() ? *e.horaInicio : "");
    res += '|';
    res += (e.horaFin.has_value() ? *e.horaFin : "");
    res += '|';
    res += (e.aula.has_value() ? *e.aula : "");
    res += '|';
    res += (e.sede.has_value() ? *e.sede : "");
    res += '|';
    res += (e.tipoSesion.has_value() ? *e.tipoSesion : "");
    res += '|';
    res += (e.estado.has_value() ? *e.estado : "");
    return res;
}

Horario GestorPersistencia::deserializarHorario(const std::string& linea) {
    std::vector<std::string> parts = split(linea, '|');
    if (parts.size() != 9) {
        throw std::runtime_error("Error en horarios.txt: se esperaban 9 campos pero se obtuvieron " + std::to_string(parts.size()));
    }
    Horario e;
    e.idHorario = parseOptionalInt(parts[0]);
    e.idOfertaCurso = parseOptionalInt(parts[1]);
    e.diaSemana = parseOptionalString(parts[2]);
    e.horaInicio = parseOptionalString(parts[3]);
    e.horaFin = parseOptionalString(parts[4]);
    e.aula = parseOptionalString(parts[5]);
    e.sede = parseOptionalString(parts[6]);
    e.tipoSesion = parseOptionalString(parts[7]);
    e.estado = parseOptionalString(parts[8]);
    return e;
}

ListaEnlazada<Horario> GestorPersistencia::cargarHorario() {
    ListaEnlazada<Horario> lista;
    std::string ruta = (fs::path(directorio) / "horarios.txt").string();
    if (!fs::exists(ruta)) return lista;
    std::ifstream arch(ruta);
    if (!arch.is_open()) return lista;
    std::string linea;
    while (std::getline(arch, linea)) {
        if (!linea.empty() && linea.back() == '\r') linea.pop_back();
        if (linea.empty()) continue;
        lista.push_back(deserializarHorario(linea));
    }
    return lista;
}

void GestorPersistencia::guardarHorario(const ListaEnlazada<Horario>& lista) {
    std::string ruta = (fs::path(directorio) / "horarios.txt").string();
    std::ofstream arch(ruta);
    if (!arch.is_open()) throw std::runtime_error("No se pudo abrir para escritura: " + ruta);
    for (const auto& e : lista) {
        arch << serializarHorario(e) << "\n";
    }
}

std::string GestorPersistencia::serializarMatriculaAcademica(const MatriculaAcademica& e) {
    std::string res;
    res += (e.idMatricula.has_value() ? std::to_string(*e.idMatricula) : "");
    res += '|';
    res += (e.idEstudiante.has_value() ? std::to_string(*e.idEstudiante) : "");
    res += '|';
    res += (e.idPeriodo.has_value() ? std::to_string(*e.idPeriodo) : "");
    res += '|';
    res += (e.fechaMatricula.has_value() ? *e.fechaMatricula : "");
    res += '|';
    res += (e.totalCreditos.has_value() ? std::to_string(*e.totalCreditos) : "");
    res += '|';
    res += (e.promedioPeriodo.has_value() ? doubleToString(*e.promedioPeriodo) : "");
    res += '|';
    res += (e.estadoMatricula.has_value() ? *e.estadoMatricula : "");
    res += '|';
    res += (e.observaciones.has_value() ? *e.observaciones : "");
    return res;
}

MatriculaAcademica GestorPersistencia::deserializarMatriculaAcademica(const std::string& linea) {
    std::vector<std::string> parts = split(linea, '|');
    if (parts.size() != 8) {
        throw std::runtime_error("Error en matriculas.txt: se esperaban 8 campos pero se obtuvieron " + std::to_string(parts.size()));
    }
    MatriculaAcademica e;
    e.idMatricula = parseOptionalInt(parts[0]);
    e.idEstudiante = parseOptionalInt(parts[1]);
    e.idPeriodo = parseOptionalInt(parts[2]);
    e.fechaMatricula = parseOptionalString(parts[3]);
    e.totalCreditos = parseOptionalInt(parts[4]);
    e.promedioPeriodo = parseOptionalDouble(parts[5]);
    e.estadoMatricula = parseOptionalString(parts[6]);
    e.observaciones = parseOptionalString(parts[7]);
    return e;
}

ListaEnlazada<MatriculaAcademica> GestorPersistencia::cargarMatriculaAcademica() {
    ListaEnlazada<MatriculaAcademica> lista;
    std::string ruta = (fs::path(directorio) / "matriculas.txt").string();
    if (!fs::exists(ruta)) return lista;
    std::ifstream arch(ruta);
    if (!arch.is_open()) return lista;
    std::string linea;
    while (std::getline(arch, linea)) {
        if (!linea.empty() && linea.back() == '\r') linea.pop_back();
        if (linea.empty()) continue;
        lista.push_back(deserializarMatriculaAcademica(linea));
    }
    return lista;
}

void GestorPersistencia::guardarMatriculaAcademica(const ListaEnlazada<MatriculaAcademica>& lista) {
    std::string ruta = (fs::path(directorio) / "matriculas.txt").string();
    std::ofstream arch(ruta);
    if (!arch.is_open()) throw std::runtime_error("No se pudo abrir para escritura: " + ruta);
    for (const auto& e : lista) {
        arch << serializarMatriculaAcademica(e) << "\n";
    }
}

std::string GestorPersistencia::serializarDetalleMatricula(const DetalleMatricula& e) {
    std::string res;
    res += (e.idDetalleMatricula.has_value() ? std::to_string(*e.idDetalleMatricula) : "");
    res += '|';
    res += (e.idMatricula.has_value() ? std::to_string(*e.idMatricula) : "");
    res += '|';
    res += (e.idOfertaCurso.has_value() ? std::to_string(*e.idOfertaCurso) : "");
    res += '|';
    res += (e.fechaInscripcion.has_value() ? *e.fechaInscripcion : "");
    res += '|';
    res += (e.estadoCurso.has_value() ? to_string(*e.estadoCurso) : "");
    res += '|';
    res += (e.notaFinal.has_value() ? doubleToString(*e.notaFinal) : "");
    res += '|';
    res += (e.numeroFallas.has_value() ? std::to_string(*e.numeroFallas) : "");
    res += '|';
    res += (e.fechaCancelacion.has_value() ? *e.fechaCancelacion : "");
    res += '|';
    res += (e.motivoCancelacion.has_value() ? *e.motivoCancelacion : "");
    return res;
}

DetalleMatricula GestorPersistencia::deserializarDetalleMatricula(const std::string& linea) {
    std::vector<std::string> parts = split(linea, '|');
    if (parts.size() != 9) {
        throw std::runtime_error("Error en detalles_matricula.txt: se esperaban 9 campos pero se obtuvieron " + std::to_string(parts.size()));
    }
    DetalleMatricula e;
    e.idDetalleMatricula = parseOptionalInt(parts[0]);
    e.idMatricula = parseOptionalInt(parts[1]);
    e.idOfertaCurso = parseOptionalInt(parts[2]);
    e.fechaInscripcion = parseOptionalString(parts[3]);
    e.estadoCurso = parseOptionalEstadoCurso(parts[4]);
    e.notaFinal = parseOptionalDouble(parts[5]);
    e.numeroFallas = parseOptionalInt(parts[6]);
    e.fechaCancelacion = parseOptionalString(parts[7]);
    e.motivoCancelacion = parseOptionalString(parts[8]);
    return e;
}

ListaEnlazada<DetalleMatricula> GestorPersistencia::cargarDetalleMatricula() {
    ListaEnlazada<DetalleMatricula> lista;
    std::string ruta = (fs::path(directorio) / "detalles_matricula.txt").string();
    if (!fs::exists(ruta)) return lista;
    std::ifstream arch(ruta);
    if (!arch.is_open()) return lista;
    std::string linea;
    while (std::getline(arch, linea)) {
        if (!linea.empty() && linea.back() == '\r') linea.pop_back();
        if (linea.empty()) continue;
        lista.push_back(deserializarDetalleMatricula(linea));
    }
    return lista;
}

void GestorPersistencia::guardarDetalleMatricula(const ListaEnlazada<DetalleMatricula>& lista) {
    std::string ruta = (fs::path(directorio) / "detalles_matricula.txt").string();
    std::ofstream arch(ruta);
    if (!arch.is_open()) throw std::runtime_error("No se pudo abrir para escritura: " + ruta);
    for (const auto& e : lista) {
        arch << serializarDetalleMatricula(e) << "\n";
    }
}

std::string GestorPersistencia::serializarEvaluacion(const Evaluacion& e) {
    std::string res;
    res += (e.idEvaluacion.has_value() ? std::to_string(*e.idEvaluacion) : "");
    res += '|';
    res += (e.idOfertaCurso.has_value() ? std::to_string(*e.idOfertaCurso) : "");
    res += '|';
    res += (e.nombre.has_value() ? *e.nombre : "");
    res += '|';
    res += (e.tipo.has_value() ? *e.tipo : "");
    res += '|';
    res += (e.porcentaje.has_value() ? doubleToString(*e.porcentaje) : "");
    res += '|';
    res += (e.fechaProgramada.has_value() ? *e.fechaProgramada : "");
    res += '|';
    res += (e.descripcion.has_value() ? *e.descripcion : "");
    res += '|';
    res += (e.estado.has_value() ? *e.estado : "");
    return res;
}

Evaluacion GestorPersistencia::deserializarEvaluacion(const std::string& linea) {
    std::vector<std::string> parts = split(linea, '|');
    if (parts.size() != 8) {
        throw std::runtime_error("Error en evaluaciones.txt: se esperaban 8 campos pero se obtuvieron " + std::to_string(parts.size()));
    }
    Evaluacion e;
    e.idEvaluacion = parseOptionalInt(parts[0]);
    e.idOfertaCurso = parseOptionalInt(parts[1]);
    e.nombre = parseOptionalString(parts[2]);
    e.tipo = parseOptionalString(parts[3]);
    e.porcentaje = parseOptionalDouble(parts[4]);
    e.fechaProgramada = parseOptionalString(parts[5]);
    e.descripcion = parseOptionalString(parts[6]);
    e.estado = parseOptionalString(parts[7]);
    return e;
}

ListaEnlazada<Evaluacion> GestorPersistencia::cargarEvaluacion() {
    ListaEnlazada<Evaluacion> lista;
    std::string ruta = (fs::path(directorio) / "evaluaciones.txt").string();
    if (!fs::exists(ruta)) return lista;
    std::ifstream arch(ruta);
    if (!arch.is_open()) return lista;
    std::string linea;
    while (std::getline(arch, linea)) {
        if (!linea.empty() && linea.back() == '\r') linea.pop_back();
        if (linea.empty()) continue;
        lista.push_back(deserializarEvaluacion(linea));
    }
    return lista;
}

void GestorPersistencia::guardarEvaluacion(const ListaEnlazada<Evaluacion>& lista) {
    std::string ruta = (fs::path(directorio) / "evaluaciones.txt").string();
    std::ofstream arch(ruta);
    if (!arch.is_open()) throw std::runtime_error("No se pudo abrir para escritura: " + ruta);
    for (const auto& e : lista) {
        arch << serializarEvaluacion(e) << "\n";
    }
}

std::string GestorPersistencia::serializarCalificacion(const Calificacion& e) {
    std::string res;
    res += (e.idCalificacion.has_value() ? std::to_string(*e.idCalificacion) : "");
    res += '|';
    res += (e.idEvaluacion.has_value() ? std::to_string(*e.idEvaluacion) : "");
    res += '|';
    res += (e.idDetalleMatricula.has_value() ? std::to_string(*e.idDetalleMatricula) : "");
    res += '|';
    res += (e.nota.has_value() ? doubleToString(*e.nota) : "");
    res += '|';
    res += (e.fechaRegistro.has_value() ? *e.fechaRegistro : "");
    res += '|';
    res += (e.observacion.has_value() ? *e.observacion : "");
    res += '|';
    res += (e.estado.has_value() ? *e.estado : "");
    return res;
}

Calificacion GestorPersistencia::deserializarCalificacion(const std::string& linea) {
    std::vector<std::string> parts = split(linea, '|');
    if (parts.size() != 7) {
        throw std::runtime_error("Error en calificaciones.txt: se esperaban 7 campos pero se obtuvieron " + std::to_string(parts.size()));
    }
    Calificacion e;
    e.idCalificacion = parseOptionalInt(parts[0]);
    e.idEvaluacion = parseOptionalInt(parts[1]);
    e.idDetalleMatricula = parseOptionalInt(parts[2]);
    e.nota = parseOptionalDouble(parts[3]);
    e.fechaRegistro = parseOptionalString(parts[4]);
    e.observacion = parseOptionalString(parts[5]);
    e.estado = parseOptionalString(parts[6]);
    return e;
}

ListaEnlazada<Calificacion> GestorPersistencia::cargarCalificacion() {
    ListaEnlazada<Calificacion> lista;
    std::string ruta = (fs::path(directorio) / "calificaciones.txt").string();
    if (!fs::exists(ruta)) return lista;
    std::ifstream arch(ruta);
    if (!arch.is_open()) return lista;
    std::string linea;
    while (std::getline(arch, linea)) {
        if (!linea.empty() && linea.back() == '\r') linea.pop_back();
        if (linea.empty()) continue;
        lista.push_back(deserializarCalificacion(linea));
    }
    return lista;
}

void GestorPersistencia::guardarCalificacion(const ListaEnlazada<Calificacion>& lista) {
    std::string ruta = (fs::path(directorio) / "calificaciones.txt").string();
    std::ofstream arch(ruta);
    if (!arch.is_open()) throw std::runtime_error("No se pudo abrir para escritura: " + ruta);
    for (const auto& e : lista) {
        arch << serializarCalificacion(e) << "\n";
    }
}

std::string GestorPersistencia::serializarAlertaAcademica(const AlertaAcademica& e) {
    std::string res;
    res += (e.idAlerta.has_value() ? std::to_string(*e.idAlerta) : "");
    res += '|';
    res += (e.idEstudiante.has_value() ? std::to_string(*e.idEstudiante) : "");
    res += '|';
    res += (e.idPeriodo.has_value() ? std::to_string(*e.idPeriodo) : "");
    res += '|';
    res += (e.tipoAlerta.has_value() ? *e.tipoAlerta : "");
    res += '|';
    res += (e.motivo.has_value() ? *e.motivo : "");
    res += '|';
    res += (e.valorObservado.has_value() ? doubleToString(*e.valorObservado) : "");
    res += '|';
    res += (e.valorLimite.has_value() ? doubleToString(*e.valorLimite) : "");
    res += '|';
    res += (e.fechaGeneracion.has_value() ? *e.fechaGeneracion : "");
    res += '|';
    res += (e.atendida.has_value() ? (*e.atendida ? "1" : "0") : "");
    res += '|';
    res += (e.observaciones.has_value() ? *e.observaciones : "");
    res += '|';
    res += (e.estado.has_value() ? *e.estado : "");
    return res;
}

AlertaAcademica GestorPersistencia::deserializarAlertaAcademica(const std::string& linea) {
    std::vector<std::string> parts = split(linea, '|');
    if (parts.size() != 11) {
        throw std::runtime_error("Error en alertas_academicas.txt: se esperaban 11 campos pero se obtuvieron " + std::to_string(parts.size()));
    }
    AlertaAcademica e;
    e.idAlerta = parseOptionalInt(parts[0]);
    e.idEstudiante = parseOptionalInt(parts[1]);
    e.idPeriodo = parseOptionalInt(parts[2]);
    e.tipoAlerta = parseOptionalString(parts[3]);
    e.motivo = parseOptionalString(parts[4]);
    e.valorObservado = parseOptionalDouble(parts[5]);
    e.valorLimite = parseOptionalDouble(parts[6]);
    e.fechaGeneracion = parseOptionalString(parts[7]);
    e.atendida = parseOptionalBool(parts[8]);
    e.observaciones = parseOptionalString(parts[9]);
    e.estado = parseOptionalString(parts[10]);
    return e;
}

ListaEnlazada<AlertaAcademica> GestorPersistencia::cargarAlertaAcademica() {
    ListaEnlazada<AlertaAcademica> lista;
    std::string ruta = (fs::path(directorio) / "alertas_academicas.txt").string();
    if (!fs::exists(ruta)) return lista;
    std::ifstream arch(ruta);
    if (!arch.is_open()) return lista;
    std::string linea;
    while (std::getline(arch, linea)) {
        if (!linea.empty() && linea.back() == '\r') linea.pop_back();
        if (linea.empty()) continue;
        lista.push_back(deserializarAlertaAcademica(linea));
    }
    return lista;
}

void GestorPersistencia::guardarAlertaAcademica(const ListaEnlazada<AlertaAcademica>& lista) {
    std::string ruta = (fs::path(directorio) / "alertas_academicas.txt").string();
    std::ofstream arch(ruta);
    if (!arch.is_open()) throw std::runtime_error("No se pudo abrir para escritura: " + ruta);
    for (const auto& e : lista) {
        arch << serializarAlertaAcademica(e) << "\n";
    }
}

std::string GestorPersistencia::serializarContrato(const Contrato& e) {
    std::string res;
    res += (e.idContrato.has_value() ? std::to_string(*e.idContrato) : "");
    res += '|';
    res += (e.idPersona.has_value() ? std::to_string(*e.idPersona) : "");
    res += '|';
    res += (e.numeroContrato.has_value() ? *e.numeroContrato : "");
    res += '|';
    res += (e.tipoContrato.has_value() ? *e.tipoContrato : "");
    res += '|';
    res += (e.fechaInicio.has_value() ? *e.fechaInicio : "");
    res += '|';
    res += (e.fechaFin.has_value() ? *e.fechaFin : "");
    res += '|';
    res += (e.dedicacion.has_value() ? to_string(*e.dedicacion) : "");
    res += '|';
    res += (e.horasSemanales.has_value() ? doubleToString(*e.horasSemanales) : "");
    res += '|';
    res += (e.horasCatedra.has_value() ? doubleToString(*e.horasCatedra) : "");
    res += '|';
    res += (e.valorHora.has_value() ? doubleToString(*e.valorHora) : "");
    res += '|';
    res += (e.aplicaAuxilioTransporte.has_value() ? (*e.aplicaAuxilioTransporte ? "1" : "0") : "");
    res += '|';
    res += (e.salarioBase.has_value() ? doubleToString(*e.salarioBase) : "");
    res += '|';
    res += (e.claseARL.has_value() ? *e.claseARL : "");
    res += '|';
    res += (e.actoAdministrativo.has_value() ? *e.actoAdministrativo : "");
    res += '|';
    res += (e.observaciones.has_value() ? *e.observaciones : "");
    res += '|';
    res += (e.estado.has_value() ? *e.estado : "");
    res += '|';
    res += (e.regimenAplicable.has_value() ? *e.regimenAplicable : "");
    res += '|';
    res += (e.normaVinculacion.has_value() ? *e.normaVinculacion : "");
    res += '|';
    res += (e.articuloNormativo.has_value() ? *e.articuloNormativo : "");
    res += '|';
    res += (e.modalidadProfesor.has_value() ? *e.modalidadProfesor : "");
    res += '|';
    res += (e.esEmpleadoPublicoDocente.has_value() ? (*e.esEmpleadoPublicoDocente ? "1" : "0") : "");
    res += '|';
    res += (e.perteneceCarreraProfesoral.has_value() ? (*e.perteneceCarreraProfesoral ? "1" : "0") : "");
    res += '|';
    res += (e.esTransitorio.has_value() ? (*e.esTransitorio ? "1" : "0") : "");
    res += '|';
    res += (e.esRemunerado.has_value() ? (*e.esRemunerado ? "1" : "0") : "");
    res += '|';
    res += (e.esAdHonorem.has_value() ? (*e.esAdHonorem ? "1" : "0") : "");
    res += '|';
    res += (e.tipoDedicacion.has_value() ? *e.tipoDedicacion : "");
    res += '|';
    res += (e.porcentajeDedicacion.has_value() ? doubleToString(*e.porcentajeDedicacion) : "");
    res += '|';
    res += (e.duracionEnMeses.has_value() ? std::to_string(*e.duracionEnMeses) : "");
    res += '|';
    res += (e.periodoAcademicoInicial.has_value() ? std::to_string(*e.periodoAcademicoInicial) : "");
    res += '|';
    res += (e.periodoAcademicoFinal.has_value() ? std::to_string(*e.periodoAcademicoFinal) : "");
    res += '|';
    res += (e.tipoActoVinculacion.has_value() ? *e.tipoActoVinculacion : "");
    res += '|';
    res += (e.numeroActoVinculacion.has_value() ? *e.numeroActoVinculacion : "");
    res += '|';
    res += (e.fechaActoVinculacion.has_value() ? *e.fechaActoVinculacion : "");
    res += '|';
    res += (e.fechaPosesion.has_value() ? *e.fechaPosesion : "");
    res += '|';
    res += (e.certificadoDisponibilidadPresupuestal.has_value() ? *e.certificadoDisponibilidadPresupuestal : "");
    res += '|';
    res += (e.numeroCDP.has_value() ? *e.numeroCDP : "");
    res += '|';
    res += (e.fechaCDP.has_value() ? *e.fechaCDP : "");
    res += '|';
    res += (e.valorDisponibilidadPresupuestal.has_value() ? doubleToString(*e.valorDisponibilidadPresupuestal) : "");
    res += '|';
    res += (e.resolucionRectoral.has_value() ? *e.resolucionRectoral : "");
    res += '|';
    res += (e.fechaResolucionRectoral.has_value() ? *e.fechaResolucionRectoral : "");
    res += '|';
    res += (e.estadoFormalizacion.has_value() ? *e.estadoFormalizacion : "");
    res += '|';
    res += (e.fechaInicioEfectiva.has_value() ? *e.fechaInicioEfectiva : "");
    res += '|';
    res += (e.fechaTerminacionEfectiva.has_value() ? *e.fechaTerminacionEfectiva : "");
    res += '|';
    res += (e.horasSemanalesAsignadas.has_value() ? doubleToString(*e.horasSemanalesAsignadas) : "");
    res += '|';
    res += (e.horasMensualesAsignadas.has_value() ? doubleToString(*e.horasMensualesAsignadas) : "");
    res += '|';
    res += (e.horasDocenciaDirecta.has_value() ? doubleToString(*e.horasDocenciaDirecta) : "");
    res += '|';
    res += (e.horasActividadesComplementarias.has_value() ? doubleToString(*e.horasActividadesComplementarias) : "");
    res += '|';
    res += (e.horasMensualesReconocidas.has_value() ? doubleToString(*e.horasMensualesReconocidas) : "");
    res += '|';
    res += (e.horasMensualesCumplidas.has_value() ? doubleToString(*e.horasMensualesCumplidas) : "");
    res += '|';
    res += (e.horasIncumplidas.has_value() ? doubleToString(*e.horasIncumplidas) : "");
    res += '|';
    res += (e.valorHoraIncumplida.has_value() ? doubleToString(*e.valorHoraIncumplida) : "");
    res += '|';
    res += (e.valorDescuentoIncumplimiento.has_value() ? doubleToString(*e.valorDescuentoIncumplimiento) : "");
    res += '|';
    res += (e.limiteHorasSemanales.has_value() ? doubleToString(*e.limiteHorasSemanales) : "");
    res += '|';
    res += (e.requiereCertificacionCumplimiento.has_value() ? (*e.requiereCertificacionCumplimiento ? "1" : "0") : "");
    res += '|';
    res += (e.certificacionCumplimiento.has_value() ? *e.certificacionCumplimiento : "");
    res += '|';
    res += (e.fechaCertificacionCumplimiento.has_value() ? *e.fechaCertificacionCumplimiento : "");
    res += '|';
    res += (e.categoriaDocenteAlVincular.has_value() ? *e.categoriaDocenteAlVincular : "");
    res += '|';
    res += (e.nivelPosgradoAlVincular.has_value() ? *e.nivelPosgradoAlVincular : "");
    res += '|';
    res += (e.grupoInvestigacionAlVincular.has_value() ? *e.grupoInvestigacionAlVincular : "");
    res += '|';
    res += (e.categoriaGrupoAlVincular.has_value() ? *e.categoriaGrupoAlVincular : "");
    res += '|';
    res += (e.semilleroAlVincular.has_value() ? *e.semilleroAlVincular : "");
    res += '|';
    res += (e.salarioMinimoVigente.has_value() ? doubleToString(*e.salarioMinimoVigente) : "");
    res += '|';
    res += (e.factorSalarialSMMLV.has_value() ? doubleToString(*e.factorSalarialSMMLV) : "");
    res += '|';
    res += (e.valorHoraCatedraVigente.has_value() ? doubleToString(*e.valorHoraCatedraVigente) : "");
    res += '|';
    res += (e.resolucionValorHoraCatedra.has_value() ? *e.resolucionValorHoraCatedra : "");
    res += '|';
    res += (e.fechaVigenciaValorHora.has_value() ? *e.fechaVigenciaValorHora : "");
    res += '|';
    res += (e.salarioMensualPactado.has_value() ? doubleToString(*e.salarioMensualPactado) : "");
    res += '|';
    res += (e.permiteBonificacionPosgrado.has_value() ? (*e.permiteBonificacionPosgrado ? "1" : "0") : "");
    res += '|';
    res += (e.permiteBonificacionInvestigacion.has_value() ? (*e.permiteBonificacionInvestigacion ? "1" : "0") : "");
    res += '|';
    res += (e.permitePrestacionesSociales.has_value() ? (*e.permitePrestacionesSociales ? "1" : "0") : "");
    res += '|';
    res += (e.permiteAportesParafiscales.has_value() ? (*e.permiteAportesParafiscales ? "1" : "0") : "");
    res += '|';
    res += (e.causalTerminacion.has_value() ? *e.causalTerminacion : "");
    res += '|';
    res += (e.fechaNovedadTerminacion.has_value() ? *e.fechaNovedadTerminacion : "");
    res += '|';
    res += (e.actoTerminacion.has_value() ? *e.actoTerminacion : "");
    res += '|';
    res += (e.renunciaPresentada.has_value() ? (*e.renunciaPresentada ? "1" : "0") : "");
    res += '|';
    res += (e.renunciaAceptada.has_value() ? (*e.renunciaAceptada ? "1" : "0") : "");
    res += '|';
    res += (e.necesidadServicioVigente.has_value() ? (*e.necesidadServicioVigente ? "1" : "0") : "");
    res += '|';
    res += (e.incumplimientoComprobado.has_value() ? (*e.incumplimientoComprobado ? "1" : "0") : "");
    res += '|';
    res += (e.decisionJudicialOAdministrativa.has_value() ? *e.decisionJudicialOAdministrativa : "");
    res += '|';
    res += (e.documentoSoporteTerminacion.has_value() ? *e.documentoSoporteTerminacion : "");
    res += '|';
    res += (e.estadoFinalContrato.has_value() ? *e.estadoFinalContrato : "");
    return res;
}

Contrato GestorPersistencia::deserializarContrato(const std::string& linea) {
    std::vector<std::string> parts = split(linea, '|');
    if (parts.size() < 81) {
        throw std::runtime_error("Error en contratos.txt: se esperaban al menos 81 campos pero se obtuvieron " + std::to_string(parts.size()));
    }
    Contrato e;
    e.idContrato = parseOptionalInt(parts[0]);
    e.idPersona = parseOptionalInt(parts[1]);
    e.numeroContrato = parseOptionalString(parts[2]);
    e.tipoContrato = parseOptionalString(parts[3]);
    e.fechaInicio = parseOptionalString(parts[4]);
    e.fechaFin = parseOptionalString(parts[5]);
    e.dedicacion = parseOptionalDedicacion(parts[6]);
    e.horasSemanales = parseOptionalDouble(parts[7]);
    e.horasCatedra = parseOptionalDouble(parts[8]);
    e.valorHora = parseOptionalDouble(parts[9]);
    e.aplicaAuxilioTransporte = parseOptionalBool(parts[10]);
    e.salarioBase = parseOptionalDouble(parts[11]);
    e.claseARL = parseOptionalString(parts[12]);
    e.actoAdministrativo = parseOptionalString(parts[13]);
    e.observaciones = parseOptionalString(parts[14]);
    e.estado = parseOptionalString(parts[15]);
    e.regimenAplicable = parseOptionalString(parts[16]);
    e.normaVinculacion = parseOptionalString(parts[17]);
    e.articuloNormativo = parseOptionalString(parts[18]);
    e.modalidadProfesor = parseOptionalString(parts[19]);
    e.esEmpleadoPublicoDocente = parseOptionalBool(parts[20]);
    e.perteneceCarreraProfesoral = parseOptionalBool(parts[21]);
    e.esTransitorio = parseOptionalBool(parts[22]);
    e.esRemunerado = parseOptionalBool(parts[23]);
    e.esAdHonorem = parseOptionalBool(parts[24]);
    e.tipoDedicacion = parseOptionalString(parts[25]);
    e.porcentajeDedicacion = parseOptionalDouble(parts[26]);
    e.duracionEnMeses = parseOptionalInt(parts[27]);
    e.periodoAcademicoInicial = parseOptionalInt(parts[28]);
    e.periodoAcademicoFinal = parseOptionalInt(parts[29]);
    e.tipoActoVinculacion = parseOptionalString(parts[30]);
    e.numeroActoVinculacion = parseOptionalString(parts[31]);
    e.fechaActoVinculacion = parseOptionalString(parts[32]);
    e.fechaPosesion = parseOptionalString(parts[33]);
    e.certificadoDisponibilidadPresupuestal = parseOptionalString(parts[34]);
    e.numeroCDP = parseOptionalString(parts[35]);
    e.fechaCDP = parseOptionalString(parts[36]);
    e.valorDisponibilidadPresupuestal = parseOptionalDouble(parts[37]);
    e.resolucionRectoral = parseOptionalString(parts[38]);
    e.fechaResolucionRectoral = parseOptionalString(parts[39]);
    e.estadoFormalizacion = parseOptionalString(parts[40]);
    e.fechaInicioEfectiva = parseOptionalString(parts[41]);
    e.fechaTerminacionEfectiva = parseOptionalString(parts[42]);
    e.horasSemanalesAsignadas = parseOptionalDouble(parts[43]);
    e.horasMensualesAsignadas = parseOptionalDouble(parts[44]);
    e.horasDocenciaDirecta = parseOptionalDouble(parts[45]);
    e.horasActividadesComplementarias = parseOptionalDouble(parts[46]);
    e.horasMensualesReconocidas = parseOptionalDouble(parts[47]);
    e.horasMensualesCumplidas = parseOptionalDouble(parts[48]);
    e.horasIncumplidas = parseOptionalDouble(parts[49]);
    e.valorHoraIncumplida = parseOptionalDouble(parts[50]);
    e.valorDescuentoIncumplimiento = parseOptionalDouble(parts[51]);
    e.limiteHorasSemanales = parseOptionalDouble(parts[52]);
    e.requiereCertificacionCumplimiento = parseOptionalBool(parts[53]);
    e.certificacionCumplimiento = parseOptionalString(parts[54]);
    e.fechaCertificacionCumplimiento = parseOptionalString(parts[55]);
    e.categoriaDocenteAlVincular = parseOptionalString(parts[56]);
    e.nivelPosgradoAlVincular = parseOptionalString(parts[57]);
    e.grupoInvestigacionAlVincular = parseOptionalString(parts[58]);
    e.categoriaGrupoAlVincular = parseOptionalString(parts[59]);
    e.semilleroAlVincular = parseOptionalString(parts[60]);
    e.salarioMinimoVigente = parseOptionalDouble(parts[61]);
    e.factorSalarialSMMLV = parseOptionalDouble(parts[62]);
    e.valorHoraCatedraVigente = parseOptionalDouble(parts[63]);
    e.resolucionValorHoraCatedra = parseOptionalString(parts[64]);
    e.fechaVigenciaValorHora = parseOptionalString(parts[65]);
    e.salarioMensualPactado = parseOptionalDouble(parts[66]);
    e.permiteBonificacionPosgrado = parseOptionalBool(parts[67]);
    e.permiteBonificacionInvestigacion = parseOptionalBool(parts[68]);
    e.permitePrestacionesSociales = parseOptionalBool(parts[69]);
    e.permiteAportesParafiscales = parseOptionalBool(parts[70]);
    e.causalTerminacion = parseOptionalString(parts[71]);
    e.fechaNovedadTerminacion = parseOptionalString(parts[72]);
    e.actoTerminacion = parseOptionalString(parts[73]);
    e.renunciaPresentada = parseOptionalBool(parts[74]);
    e.renunciaAceptada = parseOptionalBool(parts[75]);
    e.necesidadServicioVigente = parseOptionalBool(parts[76]);
    e.incumplimientoComprobado = parseOptionalBool(parts[77]);
    e.decisionJudicialOAdministrativa = parseOptionalString(parts[78]);
    e.documentoSoporteTerminacion = parseOptionalString(parts[79]);
    e.estadoFinalContrato = parseOptionalString(parts[80]);
    return e;
}

ListaEnlazada<Contrato> GestorPersistencia::cargarContrato() {
    ListaEnlazada<Contrato> lista;
    std::string ruta = (fs::path(directorio) / "contratos.txt").string();
    if (!fs::exists(ruta)) return lista;
    std::ifstream arch(ruta);
    if (!arch.is_open()) return lista;
    std::string linea;
    while (std::getline(arch, linea)) {
        if (!linea.empty() && linea.back() == '\r') linea.pop_back();
        if (linea.empty()) continue;
        lista.push_back(deserializarContrato(linea));
    }
    return lista;
}

void GestorPersistencia::guardarContrato(const ListaEnlazada<Contrato>& lista) {
    std::string ruta = (fs::path(directorio) / "contratos.txt").string();
    std::ofstream arch(ruta);
    if (!arch.is_open()) throw std::runtime_error("No se pudo abrir para escritura: " + ruta);
    for (const auto& e : lista) {
        arch << serializarContrato(e) << "\n";
    }
}

std::string GestorPersistencia::serializarCategoriaDocente(const CategoriaDocente& e) {
    std::string res;
    res += (e.idCategoria.has_value() ? std::to_string(*e.idCategoria) : "");
    res += '|';
    res += (e.codigo.has_value() ? to_string(*e.codigo) : "");
    res += '|';
    res += (e.nombre.has_value() ? *e.nombre : "");
    res += '|';
    res += (e.descripcion.has_value() ? *e.descripcion : "");
    res += '|';
    res += (e.puntosBase.has_value() ? doubleToString(*e.puntosBase) : "");
    res += '|';
    res += (e.valorHoraBase.has_value() ? doubleToString(*e.valorHoraBase) : "");
    res += '|';
    res += (e.nivelJerarquico.has_value() ? *e.nivelJerarquico : "");
    res += '|';
    res += (e.normaOrigen.has_value() ? *e.normaOrigen : "");
    res += '|';
    res += (e.fechaInicioVigencia.has_value() ? *e.fechaInicioVigencia : "");
    res += '|';
    res += (e.fechaFinVigencia.has_value() ? *e.fechaFinVigencia : "");
    res += '|';
    res += (e.estado.has_value() ? *e.estado : "");
    res += '|';
    res += (e.tipoRegimen.has_value() ? *e.tipoRegimen : "");
    res += '|';
    res += (e.puntosCategoria.has_value() ? doubleToString(*e.puntosCategoria) : "");
    res += '|';
    res += (e.factorSalarialTiempoCompleto.has_value() ? doubleToString(*e.factorSalarialTiempoCompleto) : "");
    res += '|';
    res += (e.factorSalarialMedioTiempo.has_value() ? doubleToString(*e.factorSalarialMedioTiempo) : "");
    res += '|';
    res += (e.unidadFactorSalarial.has_value() ? *e.unidadFactorSalarial : "");
    res += '|';
    res += (e.requiereActoReconocimiento.has_value() ? (*e.requiereActoReconocimiento ? "1" : "0") : "");
    res += '|';
    res += (e.actoReconocimiento.has_value() ? *e.actoReconocimiento : "");
    res += '|';
    res += (e.fechaReconocimiento.has_value() ? *e.fechaReconocimiento : "");
    res += '|';
    res += (e.categoriaAnterior.has_value() ? *e.categoriaAnterior : "");
    res += '|';
    res += (e.fechaAscenso.has_value() ? *e.fechaAscenso : "");
    res += '|';
    res += (e.esCategoriaPorDefecto.has_value() ? (*e.esCategoriaPorDefecto ? "1" : "0") : "");
    res += '|';
    res += (e.permiteReconocimientoCategoriaOrigen.has_value() ? (*e.permiteReconocimientoCategoriaOrigen ? "1" : "0") : "");
    res += '|';
    res += (e.evaluacionSatisfactoriaInstitucionOrigen.has_value() ? (*e.evaluacionSatisfactoriaInstitucionOrigen ? "1" : "0") : "");
    return res;
}

CategoriaDocente GestorPersistencia::deserializarCategoriaDocente(const std::string& linea) {
    std::vector<std::string> parts = split(linea, '|');
    if (parts.size() != 24) {
        throw std::runtime_error("Error en categorias_docentes.txt: se esperaban 24 campos pero se obtuvieron " + std::to_string(parts.size()));
    }
    CategoriaDocente e;
    e.idCategoria = parseOptionalInt(parts[0]);
    e.codigo = parseOptionalCategoriaDocente(parts[1]);
    e.nombre = parseOptionalString(parts[2]);
    e.descripcion = parseOptionalString(parts[3]);
    e.puntosBase = parseOptionalDouble(parts[4]);
    e.valorHoraBase = parseOptionalDouble(parts[5]);
    e.nivelJerarquico = parseOptionalString(parts[6]);
    e.normaOrigen = parseOptionalString(parts[7]);
    e.fechaInicioVigencia = parseOptionalString(parts[8]);
    e.fechaFinVigencia = parseOptionalString(parts[9]);
    e.estado = parseOptionalString(parts[10]);
    e.tipoRegimen = parseOptionalString(parts[11]);
    e.puntosCategoria = parseOptionalDouble(parts[12]);
    e.factorSalarialTiempoCompleto = parseOptionalDouble(parts[13]);
    e.factorSalarialMedioTiempo = parseOptionalDouble(parts[14]);
    e.unidadFactorSalarial = parseOptionalString(parts[15]);
    e.requiereActoReconocimiento = parseOptionalBool(parts[16]);
    e.actoReconocimiento = parseOptionalString(parts[17]);
    e.fechaReconocimiento = parseOptionalString(parts[18]);
    e.categoriaAnterior = parseOptionalString(parts[19]);
    e.fechaAscenso = parseOptionalString(parts[20]);
    e.esCategoriaPorDefecto = parseOptionalBool(parts[21]);
    e.permiteReconocimientoCategoriaOrigen = parseOptionalBool(parts[22]);
    e.evaluacionSatisfactoriaInstitucionOrigen = parseOptionalBool(parts[23]);
    return e;
}

ListaEnlazada<CategoriaDocente> GestorPersistencia::cargarCategoriaDocente() {
    ListaEnlazada<CategoriaDocente> lista;
    std::string ruta = (fs::path(directorio) / "categorias_docentes.txt").string();
    if (!fs::exists(ruta)) return lista;
    std::ifstream arch(ruta);
    if (!arch.is_open()) return lista;
    std::string linea;
    while (std::getline(arch, linea)) {
        if (!linea.empty() && linea.back() == '\r') linea.pop_back();
        if (linea.empty()) continue;
        lista.push_back(deserializarCategoriaDocente(linea));
    }
    return lista;
}

void GestorPersistencia::guardarCategoriaDocente(const ListaEnlazada<CategoriaDocente>& lista) {
    std::string ruta = (fs::path(directorio) / "categorias_docentes.txt").string();
    std::ofstream arch(ruta);
    if (!arch.is_open()) throw std::runtime_error("No se pudo abrir para escritura: " + ruta);
    for (const auto& e : lista) {
        arch << serializarCategoriaDocente(e) << "\n";
    }
}

std::string GestorPersistencia::serializarFactorSalarial(const FactorSalarial& e) {
    std::string res;
    res += (e.idFactor.has_value() ? std::to_string(*e.idFactor) : "");
    res += '|';
    res += (e.nombre.has_value() ? *e.nombre : "");
    res += '|';
    res += (e.tipoFactor.has_value() ? to_string(*e.tipoFactor) : "");
    res += '|';
    res += (e.cantidad.has_value() ? doubleToString(*e.cantidad) : "");
    res += '|';
    res += (e.puntosReconocidos.has_value() ? doubleToString(*e.puntosReconocidos) : "");
    res += '|';
    res += (e.valorReconocido.has_value() ? doubleToString(*e.valorReconocido) : "");
    res += '|';
    res += (e.fechaReconocimiento.has_value() ? *e.fechaReconocimiento : "");
    res += '|';
    res += (e.actoAdministrativo.has_value() ? *e.actoAdministrativo : "");
    res += '|';
    res += (e.idProfesor.has_value() ? std::to_string(*e.idProfesor) : "");
    res += '|';
    res += (e.estado.has_value() ? *e.estado : "");
    res += '|';
    res += (e.regimenAplicable.has_value() ? *e.regimenAplicable : "");
    res += '|';
    res += (e.factorGenerador.has_value() ? *e.factorGenerador : "");
    res += '|';
    res += (e.tipoReconocimiento.has_value() ? *e.tipoReconocimiento : "");
    res += '|';
    res += (e.puntosSolicitados.has_value() ? doubleToString(*e.puntosSolicitados) : "");
    res += '|';
    res += (e.puntosAprobados.has_value() ? doubleToString(*e.puntosAprobados) : "");
    res += '|';
    res += (e.puntosAcumulables.has_value() ? doubleToString(*e.puntosAcumulables) : "");
    res += '|';
    res += (e.topeIndividual.has_value() ? doubleToString(*e.topeIndividual) : "");
    res += '|';
    res += (e.topePorCategoria.has_value() ? doubleToString(*e.topePorCategoria) : "");
    res += '|';
    res += (e.topeAnual.has_value() ? doubleToString(*e.topeAnual) : "");
    res += '|';
    res += (e.numeroAutores.has_value() ? std::to_string(*e.numeroAutores) : "");
    res += '|';
    res += (e.factorCoautoria.has_value() ? doubleToString(*e.factorCoautoria) : "");
    res += '|';
    res += (e.requiereEvaluacionPares.has_value() ? (*e.requiereEvaluacionPares ? "1" : "0") : "");
    res += '|';
    res += (e.resultadoEvaluacionPares.has_value() ? *e.resultadoEvaluacionPares : "");
    res += '|';
    res += (e.requiereAprobacionComite.has_value() ? (*e.requiereAprobacionComite ? "1" : "0") : "");
    res += '|';
    res += (e.fechaAprobacionComite.has_value() ? *e.fechaAprobacionComite : "");
    res += '|';
    res += (e.actoReconocimiento.has_value() ? *e.actoReconocimiento : "");
    res += '|';
    res += (e.fechaEfectoSalarial.has_value() ? *e.fechaEfectoSalarial : "");
    res += '|';
    res += (e.esConstitutivoSalario.has_value() ? (*e.esConstitutivoSalario ? "1" : "0") : "");
    res += '|';
    res += (e.integraBasePrestacional.has_value() ? (*e.integraBasePrestacional ? "1" : "0") : "");
    res += '|';
    res += (e.integraBaseParafiscal.has_value() ? (*e.integraBaseParafiscal ? "1" : "0") : "");
    res += '|';
    res += (e.vigenciaDesde.has_value() ? *e.vigenciaDesde : "");
    res += '|';
    res += (e.vigenciaHasta.has_value() ? *e.vigenciaHasta : "");
    return res;
}

FactorSalarial GestorPersistencia::deserializarFactorSalarial(const std::string& linea) {
    std::vector<std::string> parts = split(linea, '|');
    if (parts.size() != 32) {
        throw std::runtime_error("Error en factores_salariales.txt: se esperaban 32 campos pero se obtuvieron " + std::to_string(parts.size()));
    }
    FactorSalarial e;
    e.idFactor = parseOptionalInt(parts[0]);
    e.nombre = parseOptionalString(parts[1]);
    e.tipoFactor = parseOptionalTipoFactor(parts[2]);
    e.cantidad = parseOptionalDouble(parts[3]);
    e.puntosReconocidos = parseOptionalDouble(parts[4]);
    e.valorReconocido = parseOptionalDouble(parts[5]);
    e.fechaReconocimiento = parseOptionalString(parts[6]);
    e.actoAdministrativo = parseOptionalString(parts[7]);
    e.idProfesor = parseOptionalInt(parts[8]);
    e.estado = parseOptionalString(parts[9]);
    e.regimenAplicable = parseOptionalString(parts[10]);
    e.factorGenerador = parseOptionalString(parts[11]);
    e.tipoReconocimiento = parseOptionalString(parts[12]);
    e.puntosSolicitados = parseOptionalDouble(parts[13]);
    e.puntosAprobados = parseOptionalDouble(parts[14]);
    e.puntosAcumulables = parseOptionalDouble(parts[15]);
    e.topeIndividual = parseOptionalDouble(parts[16]);
    e.topePorCategoria = parseOptionalDouble(parts[17]);
    e.topeAnual = parseOptionalDouble(parts[18]);
    e.numeroAutores = parseOptionalInt(parts[19]);
    e.factorCoautoria = parseOptionalDouble(parts[20]);
    e.requiereEvaluacionPares = parseOptionalBool(parts[21]);
    e.resultadoEvaluacionPares = parseOptionalString(parts[22]);
    e.requiereAprobacionComite = parseOptionalBool(parts[23]);
    e.fechaAprobacionComite = parseOptionalString(parts[24]);
    e.actoReconocimiento = parseOptionalString(parts[25]);
    e.fechaEfectoSalarial = parseOptionalString(parts[26]);
    e.esConstitutivoSalario = parseOptionalBool(parts[27]);
    e.integraBasePrestacional = parseOptionalBool(parts[28]);
    e.integraBaseParafiscal = parseOptionalBool(parts[29]);
    e.vigenciaDesde = parseOptionalString(parts[30]);
    e.vigenciaHasta = parseOptionalString(parts[31]);
    return e;
}

ListaEnlazada<FactorSalarial> GestorPersistencia::cargarFactorSalarial() {
    ListaEnlazada<FactorSalarial> lista;
    std::string ruta = (fs::path(directorio) / "factores_salariales.txt").string();
    if (!fs::exists(ruta)) return lista;
    std::ifstream arch(ruta);
    if (!arch.is_open()) return lista;
    std::string linea;
    while (std::getline(arch, linea)) {
        if (!linea.empty() && linea.back() == '\r') linea.pop_back();
        if (linea.empty()) continue;
        lista.push_back(deserializarFactorSalarial(linea));
    }
    return lista;
}

void GestorPersistencia::guardarFactorSalarial(const ListaEnlazada<FactorSalarial>& lista) {
    std::string ruta = (fs::path(directorio) / "factores_salariales.txt").string();
    std::ofstream arch(ruta);
    if (!arch.is_open()) throw std::runtime_error("No se pudo abrir para escritura: " + ruta);
    for (const auto& e : lista) {
        arch << serializarFactorSalarial(e) << "\n";
    }
}

std::string GestorPersistencia::serializarProduccionAcademica(const ProduccionAcademica& e) {
    std::string res;
    res += (e.idProduccion.has_value() ? std::to_string(*e.idProduccion) : "");
    res += '|';
    res += (e.idProfesor.has_value() ? std::to_string(*e.idProfesor) : "");
    res += '|';
    res += (e.tipoProduccion.has_value() ? *e.tipoProduccion : "");
    res += '|';
    res += (e.titulo.has_value() ? *e.titulo : "");
    res += '|';
    res += (e.fechaPublicacion.has_value() ? *e.fechaPublicacion : "");
    res += '|';
    res += (e.entidadPublicadora.has_value() ? *e.entidadPublicadora : "");
    res += '|';
    res += (e.identificadorProducto.has_value() ? *e.identificadorProducto : "");
    res += '|';
    res += (e.puntosSolicitados.has_value() ? doubleToString(*e.puntosSolicitados) : "");
    res += '|';
    res += (e.puntosReconocidos.has_value() ? doubleToString(*e.puntosReconocidos) : "");
    res += '|';
    res += (e.fechaReconocimiento.has_value() ? *e.fechaReconocimiento : "");
    res += '|';
    res += (e.actoAdministrativo.has_value() ? *e.actoAdministrativo : "");
    res += '|';
    res += (e.estadoValidacion.has_value() ? *e.estadoValidacion : "");
    res += '|';
    res += (e.modalidadProducto.has_value() ? *e.modalidadProducto : "");
    res += '|';
    res += (e.subtipoProducto.has_value() ? *e.subtipoProducto : "");
    res += '|';
    res += (e.nivelImpacto.has_value() ? *e.nivelImpacto : "");
    res += '|';
    res += (e.clasificacionRevista.has_value() ? *e.clasificacionRevista : "");
    res += '|';
    res += (e.isbn.has_value() ? *e.isbn : "");
    res += '|';
    res += (e.issn.has_value() ? *e.issn : "");
    res += '|';
    res += (e.registroDerechoAutor.has_value() ? *e.registroDerechoAutor : "");
    res += '|';
    res += (e.numeroPatente.has_value() ? *e.numeroPatente : "");
    res += '|';
    res += (e.entidadIndexadora.has_value() ? *e.entidadIndexadora : "");
    res += '|';
    res += (e.numeroAutores.has_value() ? std::to_string(*e.numeroAutores) : "");
    res += '|';
    res += (e.posicionAutor.has_value() ? std::to_string(*e.posicionAutor) : "");
    res += '|';
    res += (e.porcentajeParticipacion.has_value() ? doubleToString(*e.porcentajeParticipacion) : "");
    res += '|';
    res += (e.creditoInstitucional.has_value() ? (*e.creditoInstitucional ? "1" : "0") : "");
    res += '|';
    res += (e.evaluadoPorPares.has_value() ? (*e.evaluadoPorPares ? "1" : "0") : "");
    res += '|';
    res += (e.cantidadPares.has_value() ? std::to_string(*e.cantidadPares) : "");
    res += '|';
    res += (e.resultadoEvaluacion.has_value() ? *e.resultadoEvaluacion : "");
    res += '|';
    res += (e.puntosTotalesProducto.has_value() ? doubleToString(*e.puntosTotalesProducto) : "");
    res += '|';
    res += (e.factorCoautoria.has_value() ? doubleToString(*e.factorCoautoria) : "");
    res += '|';
    res += (e.puntosReconocidosProfesor.has_value() ? doubleToString(*e.puntosReconocidosProfesor) : "");
    res += '|';
    res += (e.tipoReconocimiento.has_value() ? *e.tipoReconocimiento : "");
    res += '|';
    res += (e.fechaActoReconocimiento.has_value() ? *e.fechaActoReconocimiento : "");
    res += '|';
    res += (e.yaReconocidoOtroConcepto.has_value() ? (*e.yaReconocidoOtroConcepto ? "1" : "0") : "");
    res += '|';
    res += (e.productoReclasificado.has_value() ? (*e.productoReclasificado ? "1" : "0") : "");
    res += '|';
    res += (e.puntosAdicionalesReclasificacion.has_value() ? doubleToString(*e.puntosAdicionalesReclasificacion) : "");
    res += '|';
    res += (e.fechaLimiteReclasificacion.has_value() ? *e.fechaLimiteReclasificacion : "");
    return res;
}

ProduccionAcademica GestorPersistencia::deserializarProduccionAcademica(const std::string& linea) {
    std::vector<std::string> parts = split(linea, '|');
    if (parts.size() != 37) {
        throw std::runtime_error("Error en producciones_academicas.txt: se esperaban 37 campos pero se obtuvieron " + std::to_string(parts.size()));
    }
    ProduccionAcademica e;
    e.idProduccion = parseOptionalInt(parts[0]);
    e.idProfesor = parseOptionalInt(parts[1]);
    e.tipoProduccion = parseOptionalString(parts[2]);
    e.titulo = parseOptionalString(parts[3]);
    e.fechaPublicacion = parseOptionalString(parts[4]);
    e.entidadPublicadora = parseOptionalString(parts[5]);
    e.identificadorProducto = parseOptionalString(parts[6]);
    e.puntosSolicitados = parseOptionalDouble(parts[7]);
    e.puntosReconocidos = parseOptionalDouble(parts[8]);
    e.fechaReconocimiento = parseOptionalString(parts[9]);
    e.actoAdministrativo = parseOptionalString(parts[10]);
    e.estadoValidacion = parseOptionalString(parts[11]);
    e.modalidadProducto = parseOptionalString(parts[12]);
    e.subtipoProducto = parseOptionalString(parts[13]);
    e.nivelImpacto = parseOptionalString(parts[14]);
    e.clasificacionRevista = parseOptionalString(parts[15]);
    e.isbn = parseOptionalString(parts[16]);
    e.issn = parseOptionalString(parts[17]);
    e.registroDerechoAutor = parseOptionalString(parts[18]);
    e.numeroPatente = parseOptionalString(parts[19]);
    e.entidadIndexadora = parseOptionalString(parts[20]);
    e.numeroAutores = parseOptionalInt(parts[21]);
    e.posicionAutor = parseOptionalInt(parts[22]);
    e.porcentajeParticipacion = parseOptionalDouble(parts[23]);
    e.creditoInstitucional = parseOptionalBool(parts[24]);
    e.evaluadoPorPares = parseOptionalBool(parts[25]);
    e.cantidadPares = parseOptionalInt(parts[26]);
    e.resultadoEvaluacion = parseOptionalString(parts[27]);
    e.puntosTotalesProducto = parseOptionalDouble(parts[28]);
    e.factorCoautoria = parseOptionalDouble(parts[29]);
    e.puntosReconocidosProfesor = parseOptionalDouble(parts[30]);
    e.tipoReconocimiento = parseOptionalString(parts[31]);
    e.fechaActoReconocimiento = parseOptionalString(parts[32]);
    e.yaReconocidoOtroConcepto = parseOptionalBool(parts[33]);
    e.productoReclasificado = parseOptionalBool(parts[34]);
    e.puntosAdicionalesReclasificacion = parseOptionalDouble(parts[35]);
    e.fechaLimiteReclasificacion = parseOptionalString(parts[36]);
    return e;
}

ListaEnlazada<ProduccionAcademica> GestorPersistencia::cargarProduccionAcademica() {
    ListaEnlazada<ProduccionAcademica> lista;
    std::string ruta = (fs::path(directorio) / "producciones_academicas.txt").string();
    if (!fs::exists(ruta)) return lista;
    std::ifstream arch(ruta);
    if (!arch.is_open()) return lista;
    std::string linea;
    while (std::getline(arch, linea)) {
        if (!linea.empty() && linea.back() == '\r') linea.pop_back();
        if (linea.empty()) continue;
        lista.push_back(deserializarProduccionAcademica(linea));
    }
    return lista;
}

void GestorPersistencia::guardarProduccionAcademica(const ListaEnlazada<ProduccionAcademica>& lista) {
    std::string ruta = (fs::path(directorio) / "producciones_academicas.txt").string();
    std::ofstream arch(ruta);
    if (!arch.is_open()) throw std::runtime_error("No se pudo abrir para escritura: " + ruta);
    for (const auto& e : lista) {
        arch << serializarProduccionAcademica(e) << "\n";
    }
}

std::string GestorPersistencia::serializarPeriodoNomina(const PeriodoNomina& e) {
    std::string res;
    res += (e.idPeriodoNomina.has_value() ? std::to_string(*e.idPeriodoNomina) : "");
    res += '|';
    res += (e.anio.has_value() ? std::to_string(*e.anio) : "");
    res += '|';
    res += (e.mes.has_value() ? std::to_string(*e.mes) : "");
    res += '|';
    res += (e.fechaInicio.has_value() ? *e.fechaInicio : "");
    res += '|';
    res += (e.fechaFin.has_value() ? *e.fechaFin : "");
    res += '|';
    res += (e.fechaPago.has_value() ? *e.fechaPago : "");
    res += '|';
    res += (e.estado.has_value() ? *e.estado : "");
    res += '|';
    res += (e.tipoPeriodicidad.has_value() ? *e.tipoPeriodicidad : "");
    res += '|';
    res += (e.salarioMinimoVigente.has_value() ? doubleToString(*e.salarioMinimoVigente) : "");
    res += '|';
    res += (e.valorPuntoSalarialVigente.has_value() ? doubleToString(*e.valorPuntoSalarialVigente) : "");
    res += '|';
    res += (e.fechaVigenciaValorPunto.has_value() ? *e.fechaVigenciaValorPunto : "");
    res += '|';
    res += (e.resolucionValorPunto.has_value() ? *e.resolucionValorPunto : "");
    res += '|';
    res += (e.diasBaseLiquidacion.has_value() ? std::to_string(*e.diasBaseLiquidacion) : "");
    res += '|';
    res += (e.fechaCorteNovedades.has_value() ? *e.fechaCorteNovedades : "");
    res += '|';
    res += (e.fechaCierreNomina.has_value() ? *e.fechaCierreNomina : "");
    res += '|';
    res += (e.fechaAprobacion.has_value() ? *e.fechaAprobacion : "");
    res += '|';
    res += (e.usuarioAprobador.has_value() ? *e.usuarioAprobador : "");
    res += '|';
    res += (e.totalDevengadoPeriodo.has_value() ? doubleToString(*e.totalDevengadoPeriodo) : "");
    res += '|';
    res += (e.totalDescuentosPeriodo.has_value() ? doubleToString(*e.totalDescuentosPeriodo) : "");
    res += '|';
    res += (e.totalPrestacionesPeriodo.has_value() ? doubleToString(*e.totalPrestacionesPeriodo) : "");
    res += '|';
    res += (e.totalAportesPatronalesPeriodo.has_value() ? doubleToString(*e.totalAportesPatronalesPeriodo) : "");
    res += '|';
    res += (e.costoTotalPeriodo.has_value() ? doubleToString(*e.costoTotalPeriodo) : "");
    res += '|';
    res += (e.estaCerrado.has_value() ? (*e.estaCerrado ? "1" : "0") : "");
    res += '|';
    res += (e.permiteReliquidacion.has_value() ? (*e.permiteReliquidacion ? "1" : "0") : "");
    res += '|';
    res += (e.versionLiquidacion.has_value() ? std::to_string(*e.versionLiquidacion) : "");
    return res;
}

PeriodoNomina GestorPersistencia::deserializarPeriodoNomina(const std::string& linea) {
    std::vector<std::string> parts = split(linea, '|');
    if (parts.size() != 25) {
        throw std::runtime_error("Error en periodos_nomina.txt: se esperaban 25 campos pero se obtuvieron " + std::to_string(parts.size()));
    }
    PeriodoNomina e;
    e.idPeriodoNomina = parseOptionalInt(parts[0]);
    e.anio = parseOptionalInt(parts[1]);
    e.mes = parseOptionalInt(parts[2]);
    e.fechaInicio = parseOptionalString(parts[3]);
    e.fechaFin = parseOptionalString(parts[4]);
    e.fechaPago = parseOptionalString(parts[5]);
    e.estado = parseOptionalString(parts[6]);
    e.tipoPeriodicidad = parseOptionalString(parts[7]);
    e.salarioMinimoVigente = parseOptionalDouble(parts[8]);
    e.valorPuntoSalarialVigente = parseOptionalDouble(parts[9]);
    e.fechaVigenciaValorPunto = parseOptionalString(parts[10]);
    e.resolucionValorPunto = parseOptionalString(parts[11]);
    e.diasBaseLiquidacion = parseOptionalInt(parts[12]);
    e.fechaCorteNovedades = parseOptionalString(parts[13]);
    e.fechaCierreNomina = parseOptionalString(parts[14]);
    e.fechaAprobacion = parseOptionalString(parts[15]);
    e.usuarioAprobador = parseOptionalString(parts[16]);
    e.totalDevengadoPeriodo = parseOptionalDouble(parts[17]);
    e.totalDescuentosPeriodo = parseOptionalDouble(parts[18]);
    e.totalPrestacionesPeriodo = parseOptionalDouble(parts[19]);
    e.totalAportesPatronalesPeriodo = parseOptionalDouble(parts[20]);
    e.costoTotalPeriodo = parseOptionalDouble(parts[21]);
    e.estaCerrado = parseOptionalBool(parts[22]);
    e.permiteReliquidacion = parseOptionalBool(parts[23]);
    e.versionLiquidacion = parseOptionalInt(parts[24]);
    return e;
}

ListaEnlazada<PeriodoNomina> GestorPersistencia::cargarPeriodoNomina() {
    ListaEnlazada<PeriodoNomina> lista;
    std::string ruta = (fs::path(directorio) / "periodos_nomina.txt").string();
    if (!fs::exists(ruta)) return lista;
    std::ifstream arch(ruta);
    if (!arch.is_open()) return lista;
    std::string linea;
    while (std::getline(arch, linea)) {
        if (!linea.empty() && linea.back() == '\r') linea.pop_back();
        if (linea.empty()) continue;
        lista.push_back(deserializarPeriodoNomina(linea));
    }
    return lista;
}

void GestorPersistencia::guardarPeriodoNomina(const ListaEnlazada<PeriodoNomina>& lista) {
    std::string ruta = (fs::path(directorio) / "periodos_nomina.txt").string();
    std::ofstream arch(ruta);
    if (!arch.is_open()) throw std::runtime_error("No se pudo abrir para escritura: " + ruta);
    for (const auto& e : lista) {
        arch << serializarPeriodoNomina(e) << "\n";
    }
}

std::string GestorPersistencia::serializarLiquidacionNomina(const LiquidacionNomina& e) {
    std::string res;
    res += (e.idLiquidacion.has_value() ? std::to_string(*e.idLiquidacion) : "");
    res += '|';
    res += (e.idProfesor.has_value() ? std::to_string(*e.idProfesor) : "");
    res += '|';
    res += (e.idContrato.has_value() ? std::to_string(*e.idContrato) : "");
    res += '|';
    res += (e.idPeriodoNomina.has_value() ? std::to_string(*e.idPeriodoNomina) : "");
    res += '|';
    res += (e.fechaLiquidacion.has_value() ? *e.fechaLiquidacion : "");
    res += '|';
    res += (e.salarioBase.has_value() ? doubleToString(*e.salarioBase) : "");
    res += '|';
    res += (e.totalDevengado.has_value() ? doubleToString(*e.totalDevengado) : "");
    res += '|';
    res += (e.totalDescuentos.has_value() ? doubleToString(*e.totalDescuentos) : "");
    res += '|';
    res += (e.totalPrestaciones.has_value() ? doubleToString(*e.totalPrestaciones) : "");
    res += '|';
    res += (e.baseLiquidacionPrestaciones.has_value() ? doubleToString(*e.baseLiquidacionPrestaciones) : "");
    res += '|';
    res += (e.baseCotizacionSeguridadSocial.has_value() ? doubleToString(*e.baseCotizacionSeguridadSocial) : "");
    res += '|';
    res += (e.valorAuxilioTransporteCotizado.has_value() ? doubleToString(*e.valorAuxilioTransporteCotizado) : "");
    res += '|';
    res += (e.aportePatronalSENA.has_value() ? doubleToString(*e.aportePatronalSENA) : "");
    res += '|';
    res += (e.aportePatronalICBF.has_value() ? doubleToString(*e.aportePatronalICBF) : "");
    res += '|';
    res += (e.netoPagar.has_value() ? doubleToString(*e.netoPagar) : "");
    res += '|';
    res += (e.estado.has_value() ? *e.estado : "");
    res += '|';
    res += (e.tipoProfesorLiquidado.has_value() ? to_string(*e.tipoProfesorLiquidado) : "");
    res += '|';
    res += (e.regimenLiquidado.has_value() ? *e.regimenLiquidado : "");
    res += '|';
    res += (e.categoriaLiquidada.has_value() ? *e.categoriaLiquidada : "");
    res += '|';
    res += (e.dedicacionLiquidada.has_value() ? to_string(*e.dedicacionLiquidada) : "");
    res += '|';
    res += (e.diasTrabajados.has_value() ? doubleToString(*e.diasTrabajados) : "");
    res += '|';
    res += (e.diasNoRemunerados.has_value() ? doubleToString(*e.diasNoRemunerados) : "");
    res += '|';
    res += (e.horasAsignadas.has_value() ? doubleToString(*e.horasAsignadas) : "");
    res += '|';
    res += (e.horasCumplidas.has_value() ? doubleToString(*e.horasCumplidas) : "");
    res += '|';
    res += (e.horasIncumplidas.has_value() ? doubleToString(*e.horasIncumplidas) : "");
    res += '|';
    res += (e.salarioMinimoUsado.has_value() ? doubleToString(*e.salarioMinimoUsado) : "");
    res += '|';
    res += (e.valorPuntoUsado.has_value() ? doubleToString(*e.valorPuntoUsado) : "");
    res += '|';
    res += (e.valorHoraCatedraUsado.has_value() ? doubleToString(*e.valorHoraCatedraUsado) : "");
    res += '|';
    res += (e.factorCategoriaUsado.has_value() ? doubleToString(*e.factorCategoriaUsado) : "");
    res += '|';
    res += (e.puntosSalarialesUsados.has_value() ? doubleToString(*e.puntosSalarialesUsados) : "");
    res += '|';
    res += (e.salarioOrdinario.has_value() ? doubleToString(*e.salarioOrdinario) : "");
    res += '|';
    res += (e.baseSalarialPrestacional.has_value() ? doubleToString(*e.baseSalarialPrestacional) : "");
    res += '|';
    res += (e.baseSeguridadSocial.has_value() ? doubleToString(*e.baseSeguridadSocial) : "");
    res += '|';
    res += (e.baseParafiscales.has_value() ? doubleToString(*e.baseParafiscales) : "");
    res += '|';
    res += (e.bonificacionPosgrado.has_value() ? doubleToString(*e.bonificacionPosgrado) : "");
    res += '|';
    res += (e.bonificacionInvestigacion.has_value() ? doubleToString(*e.bonificacionInvestigacion) : "");
    res += '|';
    res += (e.bonificacionesSalariales.has_value() ? doubleToString(*e.bonificacionesSalariales) : "");
    res += '|';
    res += (e.bonificacionesNoSalariales.has_value() ? doubleToString(*e.bonificacionesNoSalariales) : "");
    res += '|';
    res += (e.otrosDevengadosSalariales.has_value() ? doubleToString(*e.otrosDevengadosSalariales) : "");
    res += '|';
    res += (e.otrosDevengadosNoSalariales.has_value() ? doubleToString(*e.otrosDevengadosNoSalariales) : "");
    res += '|';
    res += (e.ajustesDevengados.has_value() ? doubleToString(*e.ajustesDevengados) : "");
    res += '|';
    res += (e.descuentoSalud.has_value() ? doubleToString(*e.descuentoSalud) : "");
    res += '|';
    res += (e.descuentoPension.has_value() ? doubleToString(*e.descuentoPension) : "");
    res += '|';
    res += (e.fondoSolidaridadPensional.has_value() ? doubleToString(*e.fondoSolidaridadPensional) : "");
    res += '|';
    res += (e.retencionFuente.has_value() ? doubleToString(*e.retencionFuente) : "");
    res += '|';
    res += (e.descuentoHorasIncumplidas.has_value() ? doubleToString(*e.descuentoHorasIncumplidas) : "");
    res += '|';
    res += (e.descuentoLibranza.has_value() ? doubleToString(*e.descuentoLibranza) : "");
    res += '|';
    res += (e.descuentoEmbargo.has_value() ? doubleToString(*e.descuentoEmbargo) : "");
    res += '|';
    res += (e.otrosDescuentos.has_value() ? doubleToString(*e.otrosDescuentos) : "");
    res += '|';
    res += (e.ajustesDescuentos.has_value() ? doubleToString(*e.ajustesDescuentos) : "");
    res += '|';
    res += (e.provisionCesantias.has_value() ? doubleToString(*e.provisionCesantias) : "");
    res += '|';
    res += (e.provisionInteresesCesantias.has_value() ? doubleToString(*e.provisionInteresesCesantias) : "");
    res += '|';
    res += (e.provisionPrimaServicios.has_value() ? doubleToString(*e.provisionPrimaServicios) : "");
    res += '|';
    res += (e.provisionPrimaNavidad.has_value() ? doubleToString(*e.provisionPrimaNavidad) : "");
    res += '|';
    res += (e.provisionVacaciones.has_value() ? doubleToString(*e.provisionVacaciones) : "");
    res += '|';
    res += (e.provisionPrimaVacaciones.has_value() ? doubleToString(*e.provisionPrimaVacaciones) : "");
    res += '|';
    res += (e.bonificacionServiciosPrestados.has_value() ? doubleToString(*e.bonificacionServiciosPrestados) : "");
    res += '|';
    res += (e.aportePatronalSalud.has_value() ? doubleToString(*e.aportePatronalSalud) : "");
    res += '|';
    res += (e.aportePatronalPension.has_value() ? doubleToString(*e.aportePatronalPension) : "");
    res += '|';
    res += (e.aporteRiesgosLaborales.has_value() ? doubleToString(*e.aporteRiesgosLaborales) : "");
    res += '|';
    res += (e.aporteCajaCompensacion.has_value() ? doubleToString(*e.aporteCajaCompensacion) : "");
    res += '|';
    res += (e.otrosAportesPatronales.has_value() ? doubleToString(*e.otrosAportesPatronales) : "");
    res += '|';
    res += (e.costoTotalEmpleador.has_value() ? doubleToString(*e.costoTotalEmpleador) : "");
    res += '|';
    res += (e.fechaGeneracion.has_value() ? *e.fechaGeneracion : "");
    res += '|';
    res += (e.fechaAprobacion.has_value() ? *e.fechaAprobacion : "");
    res += '|';
    res += (e.aprobada.has_value() ? (*e.aprobada ? "1" : "0") : "");
    res += '|';
    res += (e.pagada.has_value() ? (*e.pagada ? "1" : "0") : "");
    res += '|';
    res += (e.fechaPago.has_value() ? *e.fechaPago : "");
    res += '|';
    res += (e.medioPago.has_value() ? *e.medioPago : "");
    res += '|';
    res += (e.referenciaPago.has_value() ? *e.referenciaPago : "");
    res += '|';
    res += (e.requiereReliquidacion.has_value() ? (*e.requiereReliquidacion ? "1" : "0") : "");
    res += '|';
    res += (e.motivoReliquidacion.has_value() ? *e.motivoReliquidacion : "");
    res += '|';
    res += (e.liquidacionOrigen.has_value() ? std::to_string(*e.liquidacionOrigen) : "");
    res += '|';
    res += (e.version.has_value() ? std::to_string(*e.version) : "");
    res += '|';
    res += (e.usuarioLiquidador.has_value() ? *e.usuarioLiquidador : "");
    res += '|';
    res += (e.usuarioAprobador.has_value() ? *e.usuarioAprobador : "");
    res += '|';
    res += (e.parametros_utilizados.has_value() ? *e.parametros_utilizados : "");
    return res;
}

LiquidacionNomina GestorPersistencia::deserializarLiquidacionNomina(const std::string& linea) {
    std::vector<std::string> parts = split(linea, '|');
    if (parts.size() != 77) {
        throw std::runtime_error("Error en liquidaciones_nomina.txt: se esperaban 77 campos pero se obtuvieron " + std::to_string(parts.size()));
    }
    LiquidacionNomina e;
    e.idLiquidacion = parseOptionalInt(parts[0]);
    e.idProfesor = parseOptionalInt(parts[1]);
    e.idContrato = parseOptionalInt(parts[2]);
    e.idPeriodoNomina = parseOptionalInt(parts[3]);
    e.fechaLiquidacion = parseOptionalString(parts[4]);
    e.salarioBase = parseOptionalDouble(parts[5]);
    e.totalDevengado = parseOptionalDouble(parts[6]);
    e.totalDescuentos = parseOptionalDouble(parts[7]);
    e.totalPrestaciones = parseOptionalDouble(parts[8]);
    e.baseLiquidacionPrestaciones = parseOptionalDouble(parts[9]);
    e.baseCotizacionSeguridadSocial = parseOptionalDouble(parts[10]);
    e.valorAuxilioTransporteCotizado = parseOptionalDouble(parts[11]);
    e.aportePatronalSENA = parseOptionalDouble(parts[12]);
    e.aportePatronalICBF = parseOptionalDouble(parts[13]);
    e.netoPagar = parseOptionalDouble(parts[14]);
    e.estado = parseOptionalString(parts[15]);
    e.tipoProfesorLiquidado = parseOptionalTipoProfesor(parts[16]);
    e.regimenLiquidado = parseOptionalString(parts[17]);
    e.categoriaLiquidada = parseOptionalString(parts[18]);
    e.dedicacionLiquidada = parseOptionalDedicacion(parts[19]);
    e.diasTrabajados = parseOptionalDouble(parts[20]);
    e.diasNoRemunerados = parseOptionalDouble(parts[21]);
    e.horasAsignadas = parseOptionalDouble(parts[22]);
    e.horasCumplidas = parseOptionalDouble(parts[23]);
    e.horasIncumplidas = parseOptionalDouble(parts[24]);
    e.salarioMinimoUsado = parseOptionalDouble(parts[25]);
    e.valorPuntoUsado = parseOptionalDouble(parts[26]);
    e.valorHoraCatedraUsado = parseOptionalDouble(parts[27]);
    e.factorCategoriaUsado = parseOptionalDouble(parts[28]);
    e.puntosSalarialesUsados = parseOptionalDouble(parts[29]);
    e.salarioOrdinario = parseOptionalDouble(parts[30]);
    e.baseSalarialPrestacional = parseOptionalDouble(parts[31]);
    e.baseSeguridadSocial = parseOptionalDouble(parts[32]);
    e.baseParafiscales = parseOptionalDouble(parts[33]);
    e.bonificacionPosgrado = parseOptionalDouble(parts[34]);
    e.bonificacionInvestigacion = parseOptionalDouble(parts[35]);
    e.bonificacionesSalariales = parseOptionalDouble(parts[36]);
    e.bonificacionesNoSalariales = parseOptionalDouble(parts[37]);
    e.otrosDevengadosSalariales = parseOptionalDouble(parts[38]);
    e.otrosDevengadosNoSalariales = parseOptionalDouble(parts[39]);
    e.ajustesDevengados = parseOptionalDouble(parts[40]);
    e.descuentoSalud = parseOptionalDouble(parts[41]);
    e.descuentoPension = parseOptionalDouble(parts[42]);
    e.fondoSolidaridadPensional = parseOptionalDouble(parts[43]);
    e.retencionFuente = parseOptionalDouble(parts[44]);
    e.descuentoHorasIncumplidas = parseOptionalDouble(parts[45]);
    e.descuentoLibranza = parseOptionalDouble(parts[46]);
    e.descuentoEmbargo = parseOptionalDouble(parts[47]);
    e.otrosDescuentos = parseOptionalDouble(parts[48]);
    e.ajustesDescuentos = parseOptionalDouble(parts[49]);
    e.provisionCesantias = parseOptionalDouble(parts[50]);
    e.provisionInteresesCesantias = parseOptionalDouble(parts[51]);
    e.provisionPrimaServicios = parseOptionalDouble(parts[52]);
    e.provisionPrimaNavidad = parseOptionalDouble(parts[53]);
    e.provisionVacaciones = parseOptionalDouble(parts[54]);
    e.provisionPrimaVacaciones = parseOptionalDouble(parts[55]);
    e.bonificacionServiciosPrestados = parseOptionalDouble(parts[56]);
    e.aportePatronalSalud = parseOptionalDouble(parts[57]);
    e.aportePatronalPension = parseOptionalDouble(parts[58]);
    e.aporteRiesgosLaborales = parseOptionalDouble(parts[59]);
    e.aporteCajaCompensacion = parseOptionalDouble(parts[60]);
    e.otrosAportesPatronales = parseOptionalDouble(parts[61]);
    e.costoTotalEmpleador = parseOptionalDouble(parts[62]);
    e.fechaGeneracion = parseOptionalString(parts[63]);
    e.fechaAprobacion = parseOptionalString(parts[64]);
    e.aprobada = parseOptionalBool(parts[65]);
    e.pagada = parseOptionalBool(parts[66]);
    e.fechaPago = parseOptionalString(parts[67]);
    e.medioPago = parseOptionalString(parts[68]);
    e.referenciaPago = parseOptionalString(parts[69]);
    e.requiereReliquidacion = parseOptionalBool(parts[70]);
    e.motivoReliquidacion = parseOptionalString(parts[71]);
    e.liquidacionOrigen = parseOptionalInt(parts[72]);
    e.version = parseOptionalInt(parts[73]);
    e.usuarioLiquidador = parseOptionalString(parts[74]);
    e.usuarioAprobador = parseOptionalString(parts[75]);
    e.parametros_utilizados = parseOptionalString(parts[76]);
    return e;
}

ListaEnlazada<LiquidacionNomina> GestorPersistencia::cargarLiquidacionNomina() {
    ListaEnlazada<LiquidacionNomina> lista;
    std::string ruta = (fs::path(directorio) / "liquidaciones_nomina.txt").string();
    if (!fs::exists(ruta)) return lista;
    std::ifstream arch(ruta);
    if (!arch.is_open()) return lista;
    std::string linea;
    while (std::getline(arch, linea)) {
        if (!linea.empty() && linea.back() == '\r') linea.pop_back();
        if (linea.empty()) continue;
        lista.push_back(deserializarLiquidacionNomina(linea));
    }
    return lista;
}

void GestorPersistencia::guardarLiquidacionNomina(const ListaEnlazada<LiquidacionNomina>& lista) {
    std::string ruta = (fs::path(directorio) / "liquidaciones_nomina.txt").string();
    std::ofstream arch(ruta);
    if (!arch.is_open()) throw std::runtime_error("No se pudo abrir para escritura: " + ruta);
    for (const auto& e : lista) {
        arch << serializarLiquidacionNomina(e) << "\n";
    }
}

std::string GestorPersistencia::serializarConceptoNomina(const ConceptoNomina& e) {
    std::string res;
    res += (e.idConcepto.has_value() ? std::to_string(*e.idConcepto) : "");
    res += '|';
    res += (e.codigo.has_value() ? *e.codigo : "");
    res += '|';
    res += (e.nombre.has_value() ? *e.nombre : "");
    res += '|';
    res += (e.tipoConcepto.has_value() ? *e.tipoConcepto : "");
    res += '|';
    res += (e.naturaleza.has_value() ? *e.naturaleza : "");
    res += '|';
    res += (e.formaCalculo.has_value() ? *e.formaCalculo : "");
    res += '|';
    res += (e.porcentaje.has_value() ? doubleToString(*e.porcentaje) : "");
    res += '|';
    res += (e.valorFijo.has_value() ? doubleToString(*e.valorFijo) : "");
    res += '|';
    res += (e.baseCalculo.has_value() ? *e.baseCalculo : "");
    res += '|';
    res += (e.aplicaA.has_value() ? *e.aplicaA : "");
    res += '|';
    res += (e.normaOrigen.has_value() ? *e.normaOrigen : "");
    res += '|';
    res += (e.fechaInicioVigencia.has_value() ? *e.fechaInicioVigencia : "");
    res += '|';
    res += (e.fechaFinVigencia.has_value() ? *e.fechaFinVigencia : "");
    res += '|';
    res += (e.estado.has_value() ? *e.estado : "");
    res += '|';
    res += (e.codigoContable.has_value() ? *e.codigoContable : "");
    res += '|';
    res += (e.regimenAplicable.has_value() ? *e.regimenAplicable : "");
    res += '|';
    res += (e.modalidadProfesorAplicable.has_value() ? *e.modalidadProfesorAplicable : "");
    res += '|';
    res += (e.categoriaAplicable.has_value() ? *e.categoriaAplicable : "");
    res += '|';
    res += (e.dedicacionAplicable.has_value() ? *e.dedicacionAplicable : "");
    res += '|';
    res += (e.periodicidad.has_value() ? *e.periodicidad : "");
    res += '|';
    res += (e.esSalarial.has_value() ? (*e.esSalarial ? "1" : "0") : "");
    res += '|';
    res += (e.esBonificacion.has_value() ? (*e.esBonificacion ? "1" : "0") : "");
    res += '|';
    res += (e.esDescuentoLey.has_value() ? (*e.esDescuentoLey ? "1" : "0") : "");
    res += '|';
    res += (e.esPrestacionSocial.has_value() ? (*e.esPrestacionSocial ? "1" : "0") : "");
    res += '|';
    res += (e.esAportePatronal.has_value() ? (*e.esAportePatronal ? "1" : "0") : "");
    res += '|';
    res += (e.integraBaseSalud.has_value() ? (*e.integraBaseSalud ? "1" : "0") : "");
    res += '|';
    res += (e.integraBasePension.has_value() ? (*e.integraBasePension ? "1" : "0") : "");
    res += '|';
    res += (e.integraBasePrestacional.has_value() ? (*e.integraBasePrestacional ? "1" : "0") : "");
    res += '|';
    res += (e.integraBaseParafiscal.has_value() ? (*e.integraBaseParafiscal ? "1" : "0") : "");
    res += '|';
    res += (e.integraLiquidacionFinal.has_value() ? (*e.integraLiquidacionFinal ? "1" : "0") : "");
    res += '|';
    res += (e.requiereActoAdministrativo.has_value() ? (*e.requiereActoAdministrativo ? "1" : "0") : "");
    res += '|';
    res += (e.articuloOrigen.has_value() ? *e.articuloOrigen : "");
    res += '|';
    res += (e.prioridadCalculo.has_value() ? std::to_string(*e.prioridadCalculo) : "");
    return res;
}

ConceptoNomina GestorPersistencia::deserializarConceptoNomina(const std::string& linea) {
    std::vector<std::string> parts = split(linea, '|');
    if (parts.size() != 33) {
        throw std::runtime_error("Error en conceptos_nomina.txt: se esperaban 33 campos pero se obtuvieron " + std::to_string(parts.size()));
    }
    ConceptoNomina e;
    e.idConcepto = parseOptionalInt(parts[0]);
    e.codigo = parseOptionalString(parts[1]);
    e.nombre = parseOptionalString(parts[2]);
    e.tipoConcepto = parseOptionalString(parts[3]);
    e.naturaleza = parseOptionalString(parts[4]);
    e.formaCalculo = parseOptionalString(parts[5]);
    e.porcentaje = parseOptionalDouble(parts[6]);
    e.valorFijo = parseOptionalDouble(parts[7]);
    e.baseCalculo = parseOptionalString(parts[8]);
    e.aplicaA = parseOptionalString(parts[9]);
    e.normaOrigen = parseOptionalString(parts[10]);
    e.fechaInicioVigencia = parseOptionalString(parts[11]);
    e.fechaFinVigencia = parseOptionalString(parts[12]);
    e.estado = parseOptionalString(parts[13]);
    e.codigoContable = parseOptionalString(parts[14]);
    e.regimenAplicable = parseOptionalString(parts[15]);
    e.modalidadProfesorAplicable = parseOptionalString(parts[16]);
    e.categoriaAplicable = parseOptionalString(parts[17]);
    e.dedicacionAplicable = parseOptionalString(parts[18]);
    e.periodicidad = parseOptionalString(parts[19]);
    e.esSalarial = parseOptionalBool(parts[20]);
    e.esBonificacion = parseOptionalBool(parts[21]);
    e.esDescuentoLey = parseOptionalBool(parts[22]);
    e.esPrestacionSocial = parseOptionalBool(parts[23]);
    e.esAportePatronal = parseOptionalBool(parts[24]);
    e.integraBaseSalud = parseOptionalBool(parts[25]);
    e.integraBasePension = parseOptionalBool(parts[26]);
    e.integraBasePrestacional = parseOptionalBool(parts[27]);
    e.integraBaseParafiscal = parseOptionalBool(parts[28]);
    e.integraLiquidacionFinal = parseOptionalBool(parts[29]);
    e.requiereActoAdministrativo = parseOptionalBool(parts[30]);
    e.articuloOrigen = parseOptionalString(parts[31]);
    e.prioridadCalculo = parseOptionalInt(parts[32]);
    return e;
}

ListaEnlazada<ConceptoNomina> GestorPersistencia::cargarConceptoNomina() {
    ListaEnlazada<ConceptoNomina> lista;
    std::string ruta = (fs::path(directorio) / "conceptos_nomina.txt").string();
    if (!fs::exists(ruta)) return lista;
    std::ifstream arch(ruta);
    if (!arch.is_open()) return lista;
    std::string linea;
    while (std::getline(arch, linea)) {
        if (!linea.empty() && linea.back() == '\r') linea.pop_back();
        if (linea.empty()) continue;
        lista.push_back(deserializarConceptoNomina(linea));
    }
    return lista;
}

void GestorPersistencia::guardarConceptoNomina(const ListaEnlazada<ConceptoNomina>& lista) {
    std::string ruta = (fs::path(directorio) / "conceptos_nomina.txt").string();
    std::ofstream arch(ruta);
    if (!arch.is_open()) throw std::runtime_error("No se pudo abrir para escritura: " + ruta);
    for (const auto& e : lista) {
        arch << serializarConceptoNomina(e) << "\n";
    }
}

std::string GestorPersistencia::serializarDetalleLiquidacion(const DetalleLiquidacion& e) {
    std::string res;
    res += (e.idDetalleLiquidacion.has_value() ? std::to_string(*e.idDetalleLiquidacion) : "");
    res += '|';
    res += (e.idLiquidacion.has_value() ? std::to_string(*e.idLiquidacion) : "");
    res += '|';
    res += (e.idConcepto.has_value() ? std::to_string(*e.idConcepto) : "");
    res += '|';
    res += (e.cantidad.has_value() ? doubleToString(*e.cantidad) : "");
    res += '|';
    res += (e.baseCalculo.has_value() ? doubleToString(*e.baseCalculo) : "");
    res += '|';
    res += (e.porcentajeAplicado.has_value() ? doubleToString(*e.porcentajeAplicado) : "");
    res += '|';
    res += (e.valorUnitario.has_value() ? doubleToString(*e.valorUnitario) : "");
    res += '|';
    res += (e.valorCalculado.has_value() ? doubleToString(*e.valorCalculado) : "");
    res += '|';
    res += (e.observaciones.has_value() ? *e.observaciones : "");
    res += '|';
    res += (e.tipoMovimiento.has_value() ? *e.tipoMovimiento : "");
    res += '|';
    res += (e.fechaCausacion.has_value() ? *e.fechaCausacion : "");
    res += '|';
    res += (e.periodoCausacion.has_value() ? *e.periodoCausacion : "");
    res += '|';
    res += (e.formulaAplicada.has_value() ? *e.formulaAplicada : "");
    res += '|';
    res += (e.parametrosAplicados.has_value() ? *e.parametrosAplicados : "");
    res += '|';
    res += (e.valorAntesAjuste.has_value() ? doubleToString(*e.valorAntesAjuste) : "");
    res += '|';
    res += (e.valorAjuste.has_value() ? doubleToString(*e.valorAjuste) : "");
    res += '|';
    res += (e.valorDefinitivo.has_value() ? doubleToString(*e.valorDefinitivo) : "");
    res += '|';
    res += (e.esSalarial.has_value() ? (*e.esSalarial ? "1" : "0") : "");
    res += '|';
    res += (e.integraSeguridadSocial.has_value() ? (*e.integraSeguridadSocial ? "1" : "0") : "");
    res += '|';
    res += (e.integraPrestaciones.has_value() ? (*e.integraPrestaciones ? "1" : "0") : "");
    res += '|';
    res += (e.integraParafiscales.has_value() ? (*e.integraParafiscales ? "1" : "0") : "");
    res += '|';
    res += (e.actoSoporte.has_value() ? *e.actoSoporte : "");
    res += '|';
    res += (e.documentoSoporte.has_value() ? *e.documentoSoporte : "");
    res += '|';
    res += (e.usuarioRegistro.has_value() ? *e.usuarioRegistro : "");
    res += '|';
    res += (e.fechaRegistro.has_value() ? *e.fechaRegistro : "");
    return res;
}

DetalleLiquidacion GestorPersistencia::deserializarDetalleLiquidacion(const std::string& linea) {
    std::vector<std::string> parts = split(linea, '|');
    if (parts.size() != 25) {
        throw std::runtime_error("Error en detalles_liquidacion.txt: se esperaban 25 campos pero se obtuvieron " + std::to_string(parts.size()));
    }
    DetalleLiquidacion e;
    e.idDetalleLiquidacion = parseOptionalInt(parts[0]);
    e.idLiquidacion = parseOptionalInt(parts[1]);
    e.idConcepto = parseOptionalInt(parts[2]);
    e.cantidad = parseOptionalDouble(parts[3]);
    e.baseCalculo = parseOptionalDouble(parts[4]);
    e.porcentajeAplicado = parseOptionalDouble(parts[5]);
    e.valorUnitario = parseOptionalDouble(parts[6]);
    e.valorCalculado = parseOptionalDouble(parts[7]);
    e.observaciones = parseOptionalString(parts[8]);
    e.tipoMovimiento = parseOptionalString(parts[9]);
    e.fechaCausacion = parseOptionalString(parts[10]);
    e.periodoCausacion = parseOptionalString(parts[11]);
    e.formulaAplicada = parseOptionalString(parts[12]);
    e.parametrosAplicados = parseOptionalString(parts[13]);
    e.valorAntesAjuste = parseOptionalDouble(parts[14]);
    e.valorAjuste = parseOptionalDouble(parts[15]);
    e.valorDefinitivo = parseOptionalDouble(parts[16]);
    e.esSalarial = parseOptionalBool(parts[17]);
    e.integraSeguridadSocial = parseOptionalBool(parts[18]);
    e.integraPrestaciones = parseOptionalBool(parts[19]);
    e.integraParafiscales = parseOptionalBool(parts[20]);
    e.actoSoporte = parseOptionalString(parts[21]);
    e.documentoSoporte = parseOptionalString(parts[22]);
    e.usuarioRegistro = parseOptionalString(parts[23]);
    e.fechaRegistro = parseOptionalString(parts[24]);
    return e;
}

ListaEnlazada<DetalleLiquidacion> GestorPersistencia::cargarDetalleLiquidacion() {
    ListaEnlazada<DetalleLiquidacion> lista;
    std::string ruta = (fs::path(directorio) / "detalles_liquidacion.txt").string();
    if (!fs::exists(ruta)) return lista;
    std::ifstream arch(ruta);
    if (!arch.is_open()) return lista;
    std::string linea;
    while (std::getline(arch, linea)) {
        if (!linea.empty() && linea.back() == '\r') linea.pop_back();
        if (linea.empty()) continue;
        lista.push_back(deserializarDetalleLiquidacion(linea));
    }
    return lista;
}

void GestorPersistencia::guardarDetalleLiquidacion(const ListaEnlazada<DetalleLiquidacion>& lista) {
    std::string ruta = (fs::path(directorio) / "detalles_liquidacion.txt").string();
    std::ofstream arch(ruta);
    if (!arch.is_open()) throw std::runtime_error("No se pudo abrir para escritura: " + ruta);
    for (const auto& e : lista) {
        arch << serializarDetalleLiquidacion(e) << "\n";
    }
}

std::string GestorPersistencia::serializarParametroNormativo(const ParametroNormativo& e) {
    std::string res;
    res += (e.idParametro.has_value() ? std::to_string(*e.idParametro) : "");
    res += '|';
    res += (e.codigo.has_value() ? to_string(*e.codigo) : "");
    res += '|';
    res += (e.nombre.has_value() ? *e.nombre : "");
    res += '|';
    res += (e.descripcion.has_value() ? *e.descripcion : "");
    res += '|';
    res += (e.tipoDato.has_value() ? *e.tipoDato : "");
    res += '|';
    res += (e.valor.has_value() ? *e.valor : "");
    res += '|';
    res += (e.unidad.has_value() ? *e.unidad : "");
    res += '|';
    res += (e.normaOrigen.has_value() ? *e.normaOrigen : "");
    res += '|';
    res += (e.articulo.has_value() ? *e.articulo : "");
    res += '|';
    res += (e.fechaInicioVigencia.has_value() ? *e.fechaInicioVigencia : "");
    res += '|';
    res += (e.fechaFinVigencia.has_value() ? *e.fechaFinVigencia : "");
    res += '|';
    res += (e.aplicaA.has_value() ? *e.aplicaA : "");
    res += '|';
    res += (e.estado.has_value() ? *e.estado : "");
    return res;
}

ParametroNormativo GestorPersistencia::deserializarParametroNormativo(const std::string& linea) {
    std::vector<std::string> parts = split(linea, '|');
    if (parts.size() != 13) {
        throw std::runtime_error("Error en parametros_normativos.txt: se esperaban 13 campos pero se obtuvieron " + std::to_string(parts.size()));
    }
    ParametroNormativo e;
    e.idParametro = parseOptionalInt(parts[0]);
    e.codigo = parseOptionalParametroNormativo(parts[1]);
    e.nombre = parseOptionalString(parts[2]);
    e.descripcion = parseOptionalString(parts[3]);
    e.tipoDato = parseOptionalString(parts[4]);
    e.valor = parseOptionalString(parts[5]);
    e.unidad = parseOptionalString(parts[6]);
    e.normaOrigen = parseOptionalString(parts[7]);
    e.articulo = parseOptionalString(parts[8]);
    e.fechaInicioVigencia = parseOptionalString(parts[9]);
    e.fechaFinVigencia = parseOptionalString(parts[10]);
    e.aplicaA = parseOptionalString(parts[11]);
    e.estado = parseOptionalString(parts[12]);
    return e;
}

ListaEnlazada<ParametroNormativo> GestorPersistencia::cargarParametroNormativo() {
    ListaEnlazada<ParametroNormativo> lista;
    std::string ruta = (fs::path(directorio) / "parametros_normativos.txt").string();
    if (!fs::exists(ruta)) return lista;
    std::ifstream arch(ruta);
    if (!arch.is_open()) return lista;
    std::string linea;
    while (std::getline(arch, linea)) {
        if (!linea.empty() && linea.back() == '\r') linea.pop_back();
        if (linea.empty()) continue;
        lista.push_back(deserializarParametroNormativo(linea));
    }
    return lista;
}

void GestorPersistencia::guardarParametroNormativo(const ListaEnlazada<ParametroNormativo>& lista) {
    std::string ruta = (fs::path(directorio) / "parametros_normativos.txt").string();
    std::ofstream arch(ruta);
    if (!arch.is_open()) throw std::runtime_error("No se pudo abrir para escritura: " + ruta);
    for (const auto& e : lista) {
        arch << serializarParametroNormativo(e) << "\n";
    }
}

std::string GestorPersistencia::serializarArchivoPersistencia(const ArchivoPersistencia& e) {
    std::string res;
    res += (e.idArchivo.has_value() ? std::to_string(*e.idArchivo) : "");
    res += '|';
    res += (e.nombreArchivo.has_value() ? *e.nombreArchivo : "");
    res += '|';
    res += (e.ruta.has_value() ? *e.ruta : "");
    res += '|';
    res += (e.formato.has_value() ? *e.formato : "");
    res += '|';
    res += (e.fechaCreacion.has_value() ? *e.fechaCreacion : "");
    res += '|';
    res += (e.fechaUltimaCarga.has_value() ? *e.fechaUltimaCarga : "");
    res += '|';
    res += (e.fechaUltimoGuardado.has_value() ? *e.fechaUltimoGuardado : "");
    res += '|';
    res += (e.versionEstructura.has_value() ? *e.versionEstructura : "");
    res += '|';
    res += (e.cantidadRegistros.has_value() ? std::to_string(*e.cantidadRegistros) : "");
    res += '|';
    res += (e.estado.has_value() ? *e.estado : "");
    return res;
}

ArchivoPersistencia GestorPersistencia::deserializarArchivoPersistencia(const std::string& linea) {
    std::vector<std::string> parts = split(linea, '|');
    if (parts.size() != 10) {
        throw std::runtime_error("Error en archivos_persistencia.txt: se esperaban 10 campos pero se obtuvieron " + std::to_string(parts.size()));
    }
    ArchivoPersistencia e;
    e.idArchivo = parseOptionalInt(parts[0]);
    e.nombreArchivo = parseOptionalString(parts[1]);
    e.ruta = parseOptionalString(parts[2]);
    e.formato = parseOptionalString(parts[3]);
    e.fechaCreacion = parseOptionalString(parts[4]);
    e.fechaUltimaCarga = parseOptionalString(parts[5]);
    e.fechaUltimoGuardado = parseOptionalString(parts[6]);
    e.versionEstructura = parseOptionalString(parts[7]);
    e.cantidadRegistros = parseOptionalInt(parts[8]);
    e.estado = parseOptionalString(parts[9]);
    return e;
}

ListaEnlazada<ArchivoPersistencia> GestorPersistencia::cargarArchivoPersistencia() {
    ListaEnlazada<ArchivoPersistencia> lista;
    std::string ruta = (fs::path(directorio) / "archivos_persistencia.txt").string();
    if (!fs::exists(ruta)) return lista;
    std::ifstream arch(ruta);
    if (!arch.is_open()) return lista;
    std::string linea;
    while (std::getline(arch, linea)) {
        if (!linea.empty() && linea.back() == '\r') linea.pop_back();
        if (linea.empty()) continue;
        lista.push_back(deserializarArchivoPersistencia(linea));
    }
    return lista;
}

void GestorPersistencia::guardarArchivoPersistencia(const ListaEnlazada<ArchivoPersistencia>& lista) {
    std::string ruta = (fs::path(directorio) / "archivos_persistencia.txt").string();
    std::ofstream arch(ruta);
    if (!arch.is_open()) throw std::runtime_error("No se pudo abrir para escritura: " + ruta);
    for (const auto& e : lista) {
        arch << serializarArchivoPersistencia(e) << "\n";
    }
}

DatosSistema GestorPersistencia::cargarTodosLosDatos() {
    DatosSistema d;
    d.universidades = cargarUniversidad();
    d.facultades = cargarFacultad();
    d.programas = cargarProgramaAcademico();
    d.planesEstudio = cargarPlanEstudio();
    d.detallesPlanEstudio = cargarDetallePlanEstudio();
    d.cursos = cargarCurso();
    d.prerrequisitos = cargarPrerrequisito();
    d.personas = cargarPersona();
    d.estudiantes = cargarEstudiante();
    d.profesores = cargarProfesor();
    d.administrativos = cargarAdministrativo();
    d.periodosAcademicos = cargarPeriodoAcademico();
    d.ofertasCurso = cargarOfertaCurso();
    d.asignacionesDocentes = cargarAsignacionDocente();
    d.horarios = cargarHorario();
    d.matriculas = cargarMatriculaAcademica();
    d.detallesMatricula = cargarDetalleMatricula();
    d.evaluaciones = cargarEvaluacion();
    d.calificaciones = cargarCalificacion();
    d.alertasAcademicas = cargarAlertaAcademica();
    d.contratos = cargarContrato();
    d.categoriasDocentes = cargarCategoriaDocente();
    d.factoresSalariales = cargarFactorSalarial();
    d.produccionesAcademicas = cargarProduccionAcademica();
    d.periodosNomina = cargarPeriodoNomina();
    d.liquidacionesNomina = cargarLiquidacionNomina();
    d.conceptosNomina = cargarConceptoNomina();
    d.detallesLiquidacion = cargarDetalleLiquidacion();
    d.parametrosNormativos = cargarParametroNormativo();
    d.archivosPersistencia = cargarArchivoPersistencia();
    validarIntegridadDatos(d);
    return d;
}

void GestorPersistencia::guardarTodosLosDatos(const DatosSistema& d) {
    guardarUniversidad(d.universidades);
    guardarFacultad(d.facultades);
    guardarProgramaAcademico(d.programas);
    guardarPlanEstudio(d.planesEstudio);
    guardarDetallePlanEstudio(d.detallesPlanEstudio);
    guardarCurso(d.cursos);
    guardarPrerrequisito(d.prerrequisitos);
    guardarPersona(d.personas);
    guardarEstudiante(d.estudiantes);
    guardarProfesor(d.profesores);
    guardarAdministrativo(d.administrativos);
    guardarPeriodoAcademico(d.periodosAcademicos);
    guardarOfertaCurso(d.ofertasCurso);
    guardarAsignacionDocente(d.asignacionesDocentes);
    guardarHorario(d.horarios);
    guardarMatriculaAcademica(d.matriculas);
    guardarDetalleMatricula(d.detallesMatricula);
    guardarEvaluacion(d.evaluaciones);
    guardarCalificacion(d.calificaciones);
    guardarAlertaAcademica(d.alertasAcademicas);
    guardarContrato(d.contratos);
    guardarCategoriaDocente(d.categoriasDocentes);
    guardarFactorSalarial(d.factoresSalariales);
    guardarProduccionAcademica(d.produccionesAcademicas);
    guardarPeriodoNomina(d.periodosNomina);
    guardarLiquidacionNomina(d.liquidacionesNomina);
    guardarConceptoNomina(d.conceptosNomina);
    guardarDetalleLiquidacion(d.detallesLiquidacion);
    guardarParametroNormativo(d.parametrosNormativos);
    guardarArchivoPersistencia(d.archivosPersistencia);
}

void GestorPersistencia::validarIntegridadDatos(const DatosSistema& d) {
    std::unordered_set<int> idsUniv, idsFac, idsProg, idsPlan, idsDetPlan, idsCurso, idsPrerr;
    std::unordered_set<int> idsPers, idsEst, idsProf, idsAdm, idsPerAcad, idsOferta, idsAsig, idsHor;
    std::unordered_set<int> idsMatr, idsDetMatr, idsEval, idsCalif, idsAlerta, idsCont, idsCatDoc;
    std::unordered_set<int> idsFact, idsProd, idsPerNom, idsLiq, idsConc, idsDetLiq, idsParam, idsArch;

    for (const auto& item : d.universidades) {
        if (item.idUniversidad.has_value()) {
            if (!idsUniv.insert(*item.idUniversidad).second) {
                throw std::runtime_error("IDs duplicados en Universidad");
            }
        }
    }
    for (const auto& item : d.facultades) {
        if (item.idFacultad.has_value()) {
            if (!idsFac.insert(*item.idFacultad).second) {
                throw std::runtime_error("IDs duplicados en Facultad");
            }
        }
    }
    for (const auto& item : d.programas) {
        if (item.idPrograma.has_value()) {
            if (!idsProg.insert(*item.idPrograma).second) {
                throw std::runtime_error("IDs duplicados en ProgramaAcademico");
            }
        }
    }
    for (const auto& item : d.planesEstudio) {
        if (item.idPlanEstudio.has_value()) {
            if (!idsPlan.insert(*item.idPlanEstudio).second) {
                throw std::runtime_error("IDs duplicados en PlanEstudio");
            }
        }
    }
    for (const auto& item : d.detallesPlanEstudio) {
        if (item.idDetallePlan.has_value()) {
            if (!idsDetPlan.insert(*item.idDetallePlan).second) {
                throw std::runtime_error("IDs duplicados en DetallePlanEstudio");
            }
        }
    }
    for (const auto& item : d.cursos) {
        if (item.idCurso.has_value()) {
            if (!idsCurso.insert(*item.idCurso).second) {
                throw std::runtime_error("IDs duplicados en Curso");
            }
        }
    }
    for (const auto& item : d.prerrequisitos) {
        if (item.idPrerrequisito.has_value()) {
            if (!idsPrerr.insert(*item.idPrerrequisito).second) {
                throw std::runtime_error("IDs duplicados en Prerrequisito");
            }
        }
    }
    for (const auto& item : d.personas) {
        if (item.idPersona.has_value()) {
            if (!idsPers.insert(*item.idPersona).second) {
                throw std::runtime_error("IDs duplicados en Persona");
            }
        }
    }
    for (const auto& item : d.estudiantes) {
        if (item.idEstudiante.has_value()) {
            if (!idsEst.insert(*item.idEstudiante).second) {
                throw std::runtime_error("IDs duplicados en Estudiante");
            }
        }
    }
    for (const auto& item : d.profesores) {
        if (item.idProfesor.has_value()) {
            if (!idsProf.insert(*item.idProfesor).second) {
                throw std::runtime_error("IDs duplicados en Profesor");
            }
        }
    }
    for (const auto& item : d.administrativos) {
        if (item.idAdministrativo.has_value()) {
            if (!idsAdm.insert(*item.idAdministrativo).second) {
                throw std::runtime_error("IDs duplicados en Administrativo");
            }
        }
    }
    for (const auto& item : d.periodosAcademicos) {
        if (item.idPeriodo.has_value()) {
            if (!idsPerAcad.insert(*item.idPeriodo).second) {
                throw std::runtime_error("IDs duplicados en PeriodoAcademico");
            }
        }
    }
    for (const auto& item : d.ofertasCurso) {
        if (item.idOfertaCurso.has_value()) {
            if (!idsOferta.insert(*item.idOfertaCurso).second) {
                throw std::runtime_error("IDs duplicados en OfertaCurso");
            }
        }
    }
    for (const auto& item : d.asignacionesDocentes) {
        if (item.idAsignacion.has_value()) {
            if (!idsAsig.insert(*item.idAsignacion).second) {
                throw std::runtime_error("IDs duplicados en AsignacionDocente");
            }
        }
    }
    for (const auto& item : d.horarios) {
        if (item.idHorario.has_value()) {
            if (!idsHor.insert(*item.idHorario).second) {
                throw std::runtime_error("IDs duplicados en Horario");
            }
        }
    }
    for (const auto& item : d.matriculas) {
        if (item.idMatricula.has_value()) {
            if (!idsMatr.insert(*item.idMatricula).second) {
                throw std::runtime_error("IDs duplicados en MatriculaAcademica");
            }
        }
    }
    for (const auto& item : d.detallesMatricula) {
        if (item.idDetalleMatricula.has_value()) {
            if (!idsDetMatr.insert(*item.idDetalleMatricula).second) {
                throw std::runtime_error("IDs duplicados en DetalleMatricula");
            }
        }
    }
    for (const auto& item : d.evaluaciones) {
        if (item.idEvaluacion.has_value()) {
            if (!idsEval.insert(*item.idEvaluacion).second) {
                throw std::runtime_error("IDs duplicados en Evaluacion");
            }
        }
    }
    for (const auto& item : d.calificaciones) {
        if (item.idCalificacion.has_value()) {
            if (!idsCalif.insert(*item.idCalificacion).second) {
                throw std::runtime_error("IDs duplicados en Calificacion");
            }
        }
    }
    for (const auto& item : d.alertasAcademicas) {
        if (item.idAlerta.has_value()) {
            if (!idsAlerta.insert(*item.idAlerta).second) {
                throw std::runtime_error("IDs duplicados en AlertaAcademica");
            }
        }
    }
    for (const auto& item : d.contratos) {
        if (item.idContrato.has_value()) {
            if (!idsCont.insert(*item.idContrato).second) {
                throw std::runtime_error("IDs duplicados en Contrato");
            }
        }
    }
    for (const auto& item : d.categoriasDocentes) {
        if (item.idCategoria.has_value()) {
            if (!idsCatDoc.insert(*item.idCategoria).second) {
                throw std::runtime_error("IDs duplicados en CategoriaDocente");
            }
        }
    }
    for (const auto& item : d.factoresSalariales) {
        if (item.idFactor.has_value()) {
            if (!idsFact.insert(*item.idFactor).second) {
                throw std::runtime_error("IDs duplicados en FactorSalarial");
            }
        }
    }
    for (const auto& item : d.produccionesAcademicas) {
        if (item.idProduccion.has_value()) {
            if (!idsProd.insert(*item.idProduccion).second) {
                throw std::runtime_error("IDs duplicados en ProduccionAcademica");
            }
        }
    }
    for (const auto& item : d.periodosNomina) {
        if (item.idPeriodoNomina.has_value()) {
            if (!idsPerNom.insert(*item.idPeriodoNomina).second) {
                throw std::runtime_error("IDs duplicados en PeriodoNomina");
            }
        }
    }
    for (const auto& item : d.liquidacionesNomina) {
        if (item.idLiquidacion.has_value()) {
            if (!idsLiq.insert(*item.idLiquidacion).second) {
                throw std::runtime_error("IDs duplicados en LiquidacionNomina");
            }
        }
    }
    for (const auto& item : d.conceptosNomina) {
        if (item.idConcepto.has_value()) {
            if (!idsConc.insert(*item.idConcepto).second) {
                throw std::runtime_error("IDs duplicados en ConceptoNomina");
            }
        }
    }
    for (const auto& item : d.detallesLiquidacion) {
        if (item.idDetalleLiquidacion.has_value()) {
            if (!idsDetLiq.insert(*item.idDetalleLiquidacion).second) {
                throw std::runtime_error("IDs duplicados en DetalleLiquidacion");
            }
        }
    }
    for (const auto& item : d.parametrosNormativos) {
        if (item.idParametro.has_value()) {
            if (!idsParam.insert(*item.idParametro).second) {
                throw std::runtime_error("IDs duplicados en ParametroNormativo");
            }
        }
    }
    for (const auto& item : d.archivosPersistencia) {
        if (item.idArchivo.has_value()) {
            if (!idsArch.insert(*item.idArchivo).second) {
                throw std::runtime_error("IDs duplicados en ArchivoPersistencia");
            }
        }
    }
    for (const auto& item : d.programas) {
        if (item.idFacultad.has_value()) {
            if (idsFac.find(*item.idFacultad) == idsFac.end()) {
                throw std::runtime_error("Referencia invalida: ProgramaAcademico.idFacultad=" + std::to_string(*item.idFacultad) + " no existe en Facultad");
            }
        }
    }
    for (const auto& item : d.planesEstudio) {
        if (item.idPrograma.has_value()) {
            if (idsProg.find(*item.idPrograma) == idsProg.end()) {
                throw std::runtime_error("Referencia invalida: PlanEstudio.idPrograma=" + std::to_string(*item.idPrograma) + " no existe en ProgramaAcademico");
            }
        }
    }
    for (const auto& item : d.detallesPlanEstudio) {
        if (item.idPlanEstudio.has_value()) {
            if (idsPlan.find(*item.idPlanEstudio) == idsPlan.end()) {
                throw std::runtime_error("Referencia invalida: DetallePlanEstudio.idPlanEstudio=" + std::to_string(*item.idPlanEstudio) + " no existe en PlanEstudio");
            }
        }
    }
    for (const auto& item : d.detallesPlanEstudio) {
        if (item.idCurso.has_value()) {
            if (idsCurso.find(*item.idCurso) == idsCurso.end()) {
                throw std::runtime_error("Referencia invalida: DetallePlanEstudio.idCurso=" + std::to_string(*item.idCurso) + " no existe en Curso");
            }
        }
    }
    for (const auto& item : d.prerrequisitos) {
        if (item.idCurso.has_value()) {
            if (idsCurso.find(*item.idCurso) == idsCurso.end()) {
                throw std::runtime_error("Referencia invalida: Prerrequisito.idCurso=" + std::to_string(*item.idCurso) + " no existe en Curso");
            }
        }
    }
    for (const auto& item : d.prerrequisitos) {
        if (item.idCursoRequerido.has_value()) {
            if (idsCurso.find(*item.idCursoRequerido) == idsCurso.end()) {
                throw std::runtime_error("Referencia invalida: Prerrequisito.idCursoRequerido=" + std::to_string(*item.idCursoRequerido) + " no existe en Curso");
            }
        }
    }
    for (const auto& item : d.estudiantes) {
        if (item.idPersona.has_value()) {
            if (idsPers.find(*item.idPersona) == idsPers.end()) {
                throw std::runtime_error("Referencia invalida: Estudiante.idPersona=" + std::to_string(*item.idPersona) + " no existe en Persona");
            }
        }
    }
    for (const auto& item : d.estudiantes) {
        if (item.idPrograma.has_value()) {
            if (idsProg.find(*item.idPrograma) == idsProg.end()) {
                throw std::runtime_error("Referencia invalida: Estudiante.idPrograma=" + std::to_string(*item.idPrograma) + " no existe en ProgramaAcademico");
            }
        }
    }
    for (const auto& item : d.estudiantes) {
        if (item.idPlanEstudio.has_value()) {
            if (idsPlan.find(*item.idPlanEstudio) == idsPlan.end()) {
                throw std::runtime_error("Referencia invalida: Estudiante.idPlanEstudio=" + std::to_string(*item.idPlanEstudio) + " no existe en PlanEstudio");
            }
        }
    }
    for (const auto& item : d.profesores) {
        if (item.idPersona.has_value()) {
            if (idsPers.find(*item.idPersona) == idsPers.end()) {
                throw std::runtime_error("Referencia invalida: Profesor.idPersona=" + std::to_string(*item.idPersona) + " no existe en Persona");
            }
        }
    }
    for (const auto& item : d.administrativos) {
        if (item.idPersona.has_value()) {
            if (idsPers.find(*item.idPersona) == idsPers.end()) {
                throw std::runtime_error("Referencia invalida: Administrativo.idPersona=" + std::to_string(*item.idPersona) + " no existe en Persona");
            }
        }
    }
    for (const auto& item : d.ofertasCurso) {
        if (item.idCurso.has_value()) {
            if (idsCurso.find(*item.idCurso) == idsCurso.end()) {
                throw std::runtime_error("Referencia invalida: OfertaCurso.idCurso=" + std::to_string(*item.idCurso) + " no existe en Curso");
            }
        }
    }
    for (const auto& item : d.ofertasCurso) {
        if (item.idPeriodo.has_value()) {
            if (idsPerAcad.find(*item.idPeriodo) == idsPerAcad.end()) {
                throw std::runtime_error("Referencia invalida: OfertaCurso.idPeriodo=" + std::to_string(*item.idPeriodo) + " no existe en PeriodoAcademico");
            }
        }
    }
    for (const auto& item : d.asignacionesDocentes) {
        if (item.idProfesor.has_value()) {
            if (idsProf.find(*item.idProfesor) == idsProf.end()) {
                throw std::runtime_error("Referencia invalida: AsignacionDocente.idProfesor=" + std::to_string(*item.idProfesor) + " no existe en Profesor");
            }
        }
    }
    for (const auto& item : d.asignacionesDocentes) {
        if (item.idOfertaCurso.has_value()) {
            if (idsOferta.find(*item.idOfertaCurso) == idsOferta.end()) {
                throw std::runtime_error("Referencia invalida: AsignacionDocente.idOfertaCurso=" + std::to_string(*item.idOfertaCurso) + " no existe en OfertaCurso");
            }
        }
    }
    for (const auto& item : d.horarios) {
        if (item.idOfertaCurso.has_value()) {
            if (idsOferta.find(*item.idOfertaCurso) == idsOferta.end()) {
                throw std::runtime_error("Referencia invalida: Horario.idOfertaCurso=" + std::to_string(*item.idOfertaCurso) + " no existe en OfertaCurso");
            }
        }
    }
    for (const auto& item : d.matriculas) {
        if (item.idEstudiante.has_value()) {
            if (idsEst.find(*item.idEstudiante) == idsEst.end()) {
                throw std::runtime_error("Referencia invalida: MatriculaAcademica.idEstudiante=" + std::to_string(*item.idEstudiante) + " no existe en Estudiante");
            }
        }
    }
    for (const auto& item : d.matriculas) {
        if (item.idPeriodo.has_value()) {
            if (idsPerAcad.find(*item.idPeriodo) == idsPerAcad.end()) {
                throw std::runtime_error("Referencia invalida: MatriculaAcademica.idPeriodo=" + std::to_string(*item.idPeriodo) + " no existe en PeriodoAcademico");
            }
        }
    }
    for (const auto& item : d.detallesMatricula) {
        if (item.idMatricula.has_value()) {
            if (idsMatr.find(*item.idMatricula) == idsMatr.end()) {
                throw std::runtime_error("Referencia invalida: DetalleMatricula.idMatricula=" + std::to_string(*item.idMatricula) + " no existe en MatriculaAcademica");
            }
        }
    }
    for (const auto& item : d.detallesMatricula) {
        if (item.idOfertaCurso.has_value()) {
            if (idsOferta.find(*item.idOfertaCurso) == idsOferta.end()) {
                throw std::runtime_error("Referencia invalida: DetalleMatricula.idOfertaCurso=" + std::to_string(*item.idOfertaCurso) + " no existe en OfertaCurso");
            }
        }
    }
    for (const auto& item : d.evaluaciones) {
        if (item.idOfertaCurso.has_value()) {
            if (idsOferta.find(*item.idOfertaCurso) == idsOferta.end()) {
                throw std::runtime_error("Referencia invalida: Evaluacion.idOfertaCurso=" + std::to_string(*item.idOfertaCurso) + " no existe en OfertaCurso");
            }
        }
    }
    for (const auto& item : d.calificaciones) {
        if (item.idEvaluacion.has_value()) {
            if (idsEval.find(*item.idEvaluacion) == idsEval.end()) {
                throw std::runtime_error("Referencia invalida: Calificacion.idEvaluacion=" + std::to_string(*item.idEvaluacion) + " no existe en Evaluacion");
            }
        }
    }
    for (const auto& item : d.calificaciones) {
        if (item.idDetalleMatricula.has_value()) {
            if (idsDetMatr.find(*item.idDetalleMatricula) == idsDetMatr.end()) {
                throw std::runtime_error("Referencia invalida: Calificacion.idDetalleMatricula=" + std::to_string(*item.idDetalleMatricula) + " no existe en DetalleMatricula");
            }
        }
    }
    for (const auto& item : d.alertasAcademicas) {
        if (item.idEstudiante.has_value()) {
            if (idsEst.find(*item.idEstudiante) == idsEst.end()) {
                throw std::runtime_error("Referencia invalida: AlertaAcademica.idEstudiante=" + std::to_string(*item.idEstudiante) + " no existe en Estudiante");
            }
        }
    }
    for (const auto& item : d.alertasAcademicas) {
        if (item.idPeriodo.has_value()) {
            if (idsPerAcad.find(*item.idPeriodo) == idsPerAcad.end()) {
                throw std::runtime_error("Referencia invalida: AlertaAcademica.idPeriodo=" + std::to_string(*item.idPeriodo) + " no existe en PeriodoAcademico");
            }
        }
    }
    for (const auto& item : d.contratos) {
        if (item.idPersona.has_value()) {
            if (idsPers.find(*item.idPersona) == idsPers.end()) {
                throw std::runtime_error("Referencia invalida: Contrato.idPersona=" + std::to_string(*item.idPersona) + " no existe en Persona");
            }
        }
    }
    for (const auto& item : d.factoresSalariales) {
        if (item.idProfesor.has_value()) {
            if (idsProf.find(*item.idProfesor) == idsProf.end()) {
                throw std::runtime_error("Referencia invalida: FactorSalarial.idProfesor=" + std::to_string(*item.idProfesor) + " no existe en Profesor");
            }
        }
    }
    for (const auto& item : d.produccionesAcademicas) {
        if (item.idProfesor.has_value()) {
            if (idsProf.find(*item.idProfesor) == idsProf.end()) {
                throw std::runtime_error("Referencia invalida: ProduccionAcademica.idProfesor=" + std::to_string(*item.idProfesor) + " no existe en Profesor");
            }
        }
    }
    for (const auto& item : d.liquidacionesNomina) {
        if (item.idProfesor.has_value()) {
            if (idsProf.find(*item.idProfesor) == idsProf.end()) {
                throw std::runtime_error("Referencia invalida: LiquidacionNomina.idProfesor=" + std::to_string(*item.idProfesor) + " no existe en Profesor");
            }
        }
    }
    for (const auto& item : d.liquidacionesNomina) {
        if (item.idContrato.has_value()) {
            if (idsCont.find(*item.idContrato) == idsCont.end()) {
                throw std::runtime_error("Referencia invalida: LiquidacionNomina.idContrato=" + std::to_string(*item.idContrato) + " no existe en Contrato");
            }
        }
    }
    for (const auto& item : d.liquidacionesNomina) {
        if (item.idPeriodoNomina.has_value()) {
            if (idsPerNom.find(*item.idPeriodoNomina) == idsPerNom.end()) {
                throw std::runtime_error("Referencia invalida: LiquidacionNomina.idPeriodoNomina=" + std::to_string(*item.idPeriodoNomina) + " no existe en PeriodoNomina");
            }
        }
    }
    for (const auto& item : d.detallesLiquidacion) {
        if (item.idLiquidacion.has_value()) {
            if (idsLiq.find(*item.idLiquidacion) == idsLiq.end()) {
                throw std::runtime_error("Referencia invalida: DetalleLiquidacion.idLiquidacion=" + std::to_string(*item.idLiquidacion) + " no existe en LiquidacionNomina");
            }
        }
    }
    for (const auto& item : d.detallesLiquidacion) {
        if (item.idConcepto.has_value()) {
            if (idsConc.find(*item.idConcepto) == idsConc.end()) {
                throw std::runtime_error("Referencia invalida: DetalleLiquidacion.idConcepto=" + std::to_string(*item.idConcepto) + " no existe en ConceptoNomina");
            }
        }
    }
}

} // namespace pita
