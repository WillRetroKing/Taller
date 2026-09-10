"""Servicio de Dominio y Datos para Gestión de Personas y Roles en PITA."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from dominio.modelo_datos import (
    Administrativo,
    Contrato,
    Dedicacion,
    EstadoAcademico,
    Estudiante,
    Persona,
    Profesor,
    TipoProfesor,
)

if TYPE_CHECKING:
    from ui_gui.gui_controller import PITAController


class PersonasService:
    """Encapsula las reglas de negocio, validaciones y persistencia en memoria para Personas."""

    def __init__(self, controller: PITAController) -> None:
        self.controller = controller

    # ------------------------------------------------------------------
    # VALIDACIONES DE UNICIDAD E INTEGRIDAD
    # ------------------------------------------------------------------
    def validar_documento_unico(self, documento: str, id_persona_excluir: int | None = None) -> tuple[bool, str]:
        doc = documento.strip()
        if not doc:
            return False, "El número de documento es obligatorio."
        for p in self.controller.personas:
            if getattr(p, "idPersona", None) != id_persona_excluir and str(getattr(p, "numeroDocumento", "")).strip() == doc:
                return False, f"Ya existe una persona registrada con el documento {doc}."
        return True, ""

    def validar_codigo_unico(self, rol: str, codigo: str, id_entidad_excluir: int | None = None) -> tuple[bool, str]:
        cod = codigo.strip()
        if not cod:
            return False, f"El código de {rol.lower()} es obligatorio."

        if rol == "ESTUDIANTE":
            for e in self.controller.estudiantes:
                if getattr(e, "idEstudiante", None) != id_entidad_excluir and str(getattr(e, "codigoEstudiante", "")).strip() == cod:
                    return False, f"Ya existe un estudiante con el código {cod}."
        elif rol == "PROFESOR":
            for pr in self.controller.profesores:
                if getattr(pr, "idProfesor", None) != id_entidad_excluir and str(getattr(pr, "codigoProfesor", "")).strip() == cod:
                    return False, f"Ya existe un profesor con el código {cod}."
        elif rol == "ADMINISTRATIVO":
            for a in self.controller.administrativos:
                if getattr(a, "idAdministrativo", None) != id_entidad_excluir and str(getattr(a, "codigoEmpleado", "")).strip() == cod:
                    return False, f"Ya existe un administrativo con el código {cod}."
        return True, ""

    # ------------------------------------------------------------------
    # CREACIÓN DE ENTIDADES
    # ------------------------------------------------------------------
    def crear_persona(self, datos: dict[str, Any]) -> Persona:
        new_id_p = (max((getattr(p, "idPersona", 0) or 0 for p in self.controller.personas), default=0)) + 1
        persona = Persona(
            idPersona=new_id_p,
            tipoDocumento=datos.get("tipoDocumento", "CC"),
            numeroDocumento=datos["numeroDocumento"],
            primerNombre=datos["primerNombre"],
            segundoNombre=datos.get("segundoNombre") or None,
            primerApellido=datos["primerApellido"],
            segundoApellido=datos.get("segundoApellido") or None,
            fechaNacimiento=datos.get("fechaNacimiento"),
            direccion=datos.get("direccion") or None,
            telefono=datos.get("telefono") or None,
            correoPersonal=datos.get("correoPersonal") or None,
            correoInstitucional=datos.get("correoInstitucional") or f"{datos['primerNombre'].lower()}.{datos['primerApellido'].lower()}@unicesar.edu.co",
            ciudadResidencia=datos.get("ciudadResidencia") or None,
            fechaRegistro=date.today(),
            estado="ACTIVO",
        )
        self.controller.personas.append(persona)
        return persona

    def registrar_persona_con_rol(self, datos_persona: dict[str, Any], rol: str, datos_rol: dict[str, Any]) -> None:
        persona = self.crear_persona(datos_persona)
        new_id_p = persona.idPersona

        if rol == "ESTUDIANTE":
            new_id_e = (max((getattr(e, "idEstudiante", 0) or 0 for e in self.controller.estudiantes), default=0)) + 1
            estudiante = Estudiante(
                idEstudiante=new_id_e,
                idPersona=new_id_p,
                codigoEstudiante=datos_rol["codigo"],
                idPrograma=datos_rol.get("idPrograma", 1),
                idPlanEstudio=datos_rol.get("idPlanEstudio", 1),
                fechaIngreso=datos_rol.get("fechaIngreso", date.today()),
                semestreActual=datos_rol.get("semestreActual", 1),
                creditosAprobados=0,
                promedioAcumulado=Decimal("5.0"),
                estadoAcademico=datos_rol.get("estadoAcademico", EstadoAcademico.ACTIVO),
                estado="ACTIVO",
            )
            self.controller.estudiantes.append(estudiante)

        elif rol == "PROFESOR":
            new_id_prof = (max((getattr(p, "idProfesor", 0) or 0 for p in self.controller.profesores), default=0)) + 1
            profesor = Profesor(
                idProfesor=new_id_prof,
                idPersona=new_id_p,
                codigoProfesor=datos_rol["codigo"],
                idProgramaPrincipal=datos_rol.get("idProgramaPrincipal", 1),
                fechaVinculacion=date.today(),
                tipoProfesor=datos_rol.get("tipoProfesor", TipoProfesor.PLANTA),
                categoriaDocente=datos_rol.get("categoriaDocente", "ASISTENTE"),
                dedicacion=datos_rol.get("dedicacion", Dedicacion.TIEMPO_COMPLETO),
                maximoNivelEstudio=datos_rol.get("maximoNivelEstudio", "MAESTRIA"),
                tituloProfesional=datos_rol.get("tituloProfesional") or None,
                areaConocimiento=datos_rol.get("areaConocimiento") or None,
                numeroHorasSemanales=datos_rol.get("numeroHorasSemanales", Decimal("40")),
                puntosSalariales=datos_rol.get("puntosSalariales", Decimal("350")),
                estado="ACTIVO",
            )
            self.controller.profesores.append(profesor)

        elif rol == "ADMINISTRATIVO":
            new_id_adm = (max((getattr(a, "idAdministrativo", 0) or 0 for a in self.controller.administrativos), default=0)) + 1
            cargo_str = datos_rol.get("cargo", "Profesional Universitario")
            dep_str = datos_rol.get("dependencia", "Vicerrectoría Académica")
            cat_str = datos_rol.get("categoria", "PROFESIONAL")
            tipo_cont_str = datos_rol.get("tipoContratacion", "PLANTA")
            f_vinc = datos_rol.get("fechaVinculacion", date.today())
            sal_base = datos_rol.get("salarioBase", Decimal("2800000"))

            administrativo = Administrativo(
                idAdministrativo=new_id_adm,
                idPersona=new_id_p,
                codigoEmpleado=datos_rol["codigo"],
                cargo=cargo_str,
                dependencia=dep_str,
                categoria=cat_str,
                tipoContratacion=tipo_cont_str,
                fechaVinculacion=f_vinc,
                salarioBase=sal_base,
                estado="ACTIVO",
            )
            self.controller.administrativos.append(administrativo)

            # Generar inmediatamente su contrato laboral activo enlazado a la persona
            new_id_c = (max((getattr(c, "idContrato", 0) or 0 for c in self.controller.contratos), default=0)) + 1
            contrato = Contrato(
                idContrato=new_id_c,
                idPersona=new_id_p,
                numeroContrato=f"ADM-CONTRATO-{new_id_c:03d}",
                tipoContrato="TERMINO_INDEFINIDO",
                fechaInicio=f_vinc,
                salarioBase=sal_base,
                aplicaAuxilioTransporte=bool(sal_base <= Decimal("3501810")),
                estado="ACTIVO",
                regimenAplicable="CST_LEY100_ADMINISTRATIVO",
                esRemunerado=True,
                esEmpleadoPublicoDocente=False,
                perteneceCarreraProfesoral=False,
                esTransitorio=False,
                esAdHonorem=False,
                observaciones=f"Cargo: {cargo_str} | Dependencia: {dep_str}",
            )
            self.controller.contratos.append(contrato)

        self.controller._recrear_gestores()

    # ------------------------------------------------------------------
    # ACTUALIZACIONES
    # ------------------------------------------------------------------
    def actualizar_datos_persona(self, persona: Persona, datos: dict[str, Any]) -> None:
        persona.primerNombre = datos["primerNombre"]
        persona.segundoNombre = datos.get("segundoNombre") or None
        persona.primerApellido = datos["primerApellido"]
        persona.segundoApellido = datos.get("segundoApellido") or None
        persona.telefono = datos.get("telefono") or None
        if datos.get("correoInstitucional"):
            persona.correoInstitucional = datos["correoInstitucional"]
        persona.correoPersonal = datos.get("correoPersonal") or None
        persona.direccion = datos.get("direccion") or None
        persona.ciudadResidencia = datos.get("ciudadResidencia") or None
        if "fechaNacimiento" in datos:
            persona.fechaNacimiento = datos["fechaNacimiento"]

    def actualizar_estudiante(self, est: Estudiante, pers: Persona | None, datos_p: dict[str, Any], datos_e: dict[str, Any]) -> None:
        if pers:
            self.actualizar_datos_persona(pers, datos_p)
        est.idPrograma = datos_e["idPrograma"]
        est.idPlanEstudio = datos_e["idPlanEstudio"]
        est.semestreActual = datos_e["semestreActual"]
        est.creditosAprobados = datos_e["creditosAprobados"]
        est.estadoAcademico = datos_e["estadoAcademico"]
        est.promedioAcumulado = datos_e["promedioAcumulado"]

        # Regla de negocio: si el promedio es reprobatorio y está activo, cambia a EBRA
        if est.promedioAcumulado < Decimal("3.0") and est.estadoAcademico == EstadoAcademico.ACTIVO:
            est.estadoAcademico = EstadoAcademico.EBRA

        self.controller._recrear_gestores()
        self.controller.guardar_datos()

    def actualizar_profesor(self, prof: Profesor, pers: Persona | None, datos_p: dict[str, Any], datos_pr: dict[str, Any]) -> None:
        if pers:
            self.actualizar_datos_persona(pers, datos_p)
        prof.idProgramaPrincipal = datos_pr["idProgramaPrincipal"]
        prof.tipoProfesor = datos_pr["tipoProfesor"]
        prof.categoriaDocente = datos_pr["categoriaDocente"]
        prof.dedicacion = datos_pr["dedicacion"]
        prof.numeroHorasSemanales = datos_pr["numeroHorasSemanales"]
        prof.puntosSalariales = datos_pr["puntosSalariales"]
        prof.maximoNivelEstudio = datos_pr["maximoNivelEstudio"]
        prof.tituloProfesional = datos_pr["tituloProfesional"]
        prof.areaConocimiento = datos_pr["areaConocimiento"]

        # Sincronizar automáticamente el salario base del contrato activo si es docente de planta
        if "PLANTA" in str(getattr(prof, "tipoProfesor", "")).upper():
            val_pto = Decimal("23924")
            p_val = next((p for p in self.controller.parametros if p.codigo == "VALOR_PUNTO_SALARIAL"), None)
            if p_val and p_val.valor:
                try:
                    val_pto = Decimal(str(p_val.valor))
                except Exception:
                    pass
            for c in self.controller.contratos:
                if c.idPersona == prof.idPersona and str(getattr(c, "estado", "")).upper() == "ACTIVO":
                    f_ded = Decimal("0.5") if "MEDIO" in str(getattr(c, "dedicacion", "")).upper() else Decimal("1")
                    c.salarioBase = (Decimal(str(prof.puntosSalariales or 0)) * val_pto * f_ded).quantize(Decimal("1"))
                    c.salarioMensualPactado = c.salarioBase
                    break

        self.controller._recrear_gestores()
        self.controller.guardar_datos()

    def actualizar_administrativo(self, adm: Administrativo, pers: Persona | None, datos_p: dict[str, Any], datos_a: dict[str, Any]) -> None:
        if pers:
            self.actualizar_datos_persona(pers, datos_p)
        adm.cargo = datos_a["cargo"]
        adm.dependencia = datos_a["dependencia"]
        if "categoria" in datos_a:
            adm.categoria = datos_a["categoria"]
        adm.tipoContratacion = datos_a["tipoContratacion"]
        adm.salarioBase = datos_a["salarioBase"]

        # Sincronizar automáticamente el salario base y observaciones en su contrato activo
        for c in self.controller.contratos:
            if c.idPersona == adm.idPersona and getattr(c, "estado", "") == "ACTIVO":
                c.salarioBase = adm.salarioBase
                c.aplicaAuxilioTransporte = bool(adm.salarioBase <= Decimal("3501810"))
                c.observaciones = f"Cargo: {adm.cargo} - Dependencia: {adm.dependencia}"
                break

        self.controller._recrear_gestores()
        self.controller.guardar_datos()

    # ------------------------------------------------------------------
    # ACTIVACIÓN Y DESACTIVACIÓN DE ESTADOS
    # ------------------------------------------------------------------
    def conmutar_estado_estudiante(self, id_estudiante: int) -> bool:
        est = next((e for e in self.controller.estudiantes if getattr(e, "idEstudiante", 0) == id_estudiante), None)
        if est:
            es_activo = str(getattr(est, "estado", "ACTIVO")).upper() == "ACTIVO"
            nuevo_estado = "INACTIVO" if es_activo else "ACTIVO"
            est.estado = nuevo_estado
            pers = next((p for p in self.controller.personas if getattr(p, "idPersona", None) == getattr(est, "idPersona", None)), None)
            if pers:
                pers.estado = nuevo_estado
            self.controller._recrear_gestores()
            self.controller.guardar_datos()
            return True
        return False

    def conmutar_estado_profesor(self, id_profesor: int) -> bool:
        prof = next((p for p in self.controller.profesores if getattr(p, "idProfesor", 0) == id_profesor), None)
        if prof:
            es_activo = str(getattr(prof, "estado", "ACTIVO")).upper() == "ACTIVO"
            nuevo_estado = "INACTIVO" if es_activo else "ACTIVO"
            prof.estado = nuevo_estado
            pers = next((p for p in self.controller.personas if getattr(p, "idPersona", None) == getattr(prof, "idPersona", None)), None)
            if pers:
                pers.estado = nuevo_estado
            for c in self.controller.contratos:
                if getattr(c, "idPersona", None) == getattr(prof, "idPersona", None):
                    c.estado = nuevo_estado
            self.controller._recrear_gestores()
            self.controller.guardar_datos()
            return True
        return False

    def conmutar_estado_administrativo(self, id_administrativo: int) -> bool:
        adm = next((a for a in self.controller.administrativos if getattr(a, "idAdministrativo", 0) == id_administrativo), None)
        if adm:
            es_activo = str(getattr(adm, "estado", "ACTIVO")).upper() == "ACTIVO"
            nuevo_estado = "INACTIVO" if es_activo else "ACTIVO"
            adm.estado = nuevo_estado
            pers = next((p for p in self.controller.personas if getattr(p, "idPersona", None) == getattr(adm, "idPersona", None)), None)
            if pers:
                pers.estado = nuevo_estado
            for c in self.controller.contratos:
                if getattr(c, "idPersona", None) == getattr(adm, "idPersona", None):
                    c.estado = nuevo_estado
            self.controller._recrear_gestores()
            self.controller.guardar_datos()
            return True
        return False

    def desactivar_estudiante(self, id_estudiante: int) -> bool:
        return self.conmutar_estado_estudiante(id_estudiante)

    def desactivar_profesor(self, id_profesor: int) -> bool:
        return self.conmutar_estado_profesor(id_profesor)

    def desactivar_administrativo(self, id_administrativo: int) -> bool:
        return self.conmutar_estado_administrativo(id_administrativo)
