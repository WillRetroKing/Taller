"""Servicio de Dominio y Lógica de Negocio para Contratación Docente y Factores Salariales."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from dominio.modelo_datos import (
    Administrativo,
    Contrato,
    Dedicacion,
    FactorSalarial,
    Persona,
    ProduccionAcademica,
    Profesor,
    TipoFactor,
)

if TYPE_CHECKING:
    from ui_gui.gui_controller import PITAController


class ContratosService:
    """Encapsula reglas de negocio, validaciones legales y persistencia para contratos y factores."""

    def __init__(self, controller: PITAController) -> None:
        self.controller = controller

    # ------------------------------------------------------------------
    # BÚSQUEDAS Y PARÁMETROS
    # ------------------------------------------------------------------
    def obtener_parametro_decimal(self, codigo: str, default: Decimal) -> Decimal:
        try:
            return self.controller.gestor_parametros.obtener_parametro_vigente(codigo, date.today())
        except Exception:
            return default

    def buscar_persona_por_id(self, id_persona: int | None) -> Persona | None:
        if not id_persona:
            return None
        return next((p for p in self.controller.personas if getattr(p, "idPersona", None) == id_persona), None)

    def buscar_profesor_por_id(self, id_profesor: int | None) -> Profesor | None:
        if not id_profesor:
            return None
        return next((p for p in self.controller.profesores if getattr(p, "idProfesor", None) == id_profesor), None)

    def buscar_profesor_por_id_persona(self, id_persona: int | None) -> Profesor | None:
        if not id_persona:
            return None
        return next((p for p in self.controller.profesores if getattr(p, "idPersona", None) == id_persona), None)

    def buscar_administrativo_por_id_persona(self, id_persona: int | None) -> Administrativo | None:
        if not id_persona:
            return None
        return next((a for a in self.controller.administrativos if getattr(a, "idPersona", None) == id_persona), None)

    # ------------------------------------------------------------------
    # ASISTENTE DE CÁLCULO SALARIAL
    # ------------------------------------------------------------------
    def calcular_asignacion_sugerida(
        self,
        tipo_contrato: str,
        profesor: Profesor | None,
        dedicacion: str,
        horas: Decimal,
    ) -> Decimal:
        val_pto = self.obtener_parametro_decimal("VALOR_PUNTO_SALARIAL", Decimal("23924"))
        val_cat = self.obtener_parametro_decimal("VALOR_HORA_CATEDRA", Decimal("38500"))
        smmlv = self.obtener_parametro_decimal("SALARIO_MINIMO", Decimal("1300000"))

        if "PLANTA" in tipo_contrato:
            pts = getattr(profesor, "puntosSalariales", 0) or 0
            if not pts or pts == 0:
                cat = str(getattr(profesor, "categoriaDocente", "") or "").upper()
                pts_cat = {"AUXILIAR": Decimal("180"), "ASISTENTE": Decimal("250"), "ASOCIADO": Decimal("350"), "TITULAR": Decimal("450")}.get(cat, Decimal("250"))
                pts_doc = Decimal("120") if "DOCTOR" in str(getattr(profesor, "maximoNivelEstudio", "")).upper() else Decimal("0")
                pts = pts_cat + pts_doc
            sug = Decimal(str(pts)) * val_pto
            if "MEDIO" in dedicacion:
                sug = sug / Decimal("2")
            return sug

        elif "OCASIONAL" in tipo_contrato:
            cat = getattr(profesor, "categoriaDocente", "AUXILIAR") or "AUXILIAR"
            factores_cat = {
                "AUXILIAR": Decimal("2.645"),
                "ASISTENTE": Decimal("3.125"),
                "ASOCIADO": Decimal("3.606"),
                "TITULAR": Decimal("3.918"),
            }
            mult = factores_cat.get(cat, Decimal("3.125"))
            sug = smmlv * mult
            if "MEDIO" in dedicacion:
                sug = sug / Decimal("2")
            return sug

        elif "CATEDRATICO" in tipo_contrato:
            return horas * Decimal("4") * val_cat

        return Decimal("0")

    # ------------------------------------------------------------------
    # VALIDACIONES Y REGLAS LEGALES
    # ------------------------------------------------------------------
    def validar_contrato(
        self,
        numero_contrato: str,
        id_persona: int,
        tipo_contrato: str,
        horas: Decimal,
        es_jubilado: bool,
        id_contrato_excluir: int | None = None,
    ) -> tuple[bool, str]:
        num = numero_contrato.strip()
        if not num:
            return False, "El número de contrato es obligatorio."

        # Unicidad de número de contrato
        for c in self.controller.contratos:
            if getattr(c, "idContrato", None) != id_contrato_excluir and str(getattr(c, "numeroContrato", "")).strip() == num:
                return False, f"Ya existe un contrato registrado con el número {num}."

        # Restricción cátedra: máximo 18 horas semanales
        if "CATEDRATICO" in tipo_contrato and horas > Decimal("18"):
            return False, "Los profesores de cátedra tienen un tope legal de máximo 18 horas semanales (Acuerdo 027)."

        # Restricción jubilados
        if es_jubilado and "PLANTA" in tipo_contrato:
            return False, "Un docente jubilado/pensionado no puede vincularse como Docente de Planta de Carrera."

        return True, ""

    # ------------------------------------------------------------------
    # CREACIÓN Y ACTUALIZACIÓN DE CONTRATOS
    # ------------------------------------------------------------------
    def registrar_contrato(self, datos: dict[str, Any]) -> Contrato:
        siguiente_id = max((c.idContrato or 0 for c in self.controller.contratos), default=0) + 1
        ded_val = Dedicacion.TIEMPO_COMPLETO if "COMPLETO" in str(datos.get("dedicacion", "TIEMPO_COMPLETO")) else (
            Dedicacion.MEDIO_TIEMPO if "MEDIO" in str(datos.get("dedicacion", "")) else Dedicacion.HORA_CATEDRA
        )
        sal_base_dec = Decimal(str(datos.get("salarioBase", "0")))
        es_admin = "ADMIN" in str(datos.get("tipoContrato", "")).upper() or "CST" in str(datos.get("regimenAplicable", "")).upper()
        regimen_default = "CST_LEY100_ADMINISTRATIVO" if es_admin else (
            "Decreto 1279 de 2002" if "PLANTA" in str(datos.get("tipoContrato", "")) else "Acuerdo 027 de 2024"
        )
        aplica_aux = bool(es_admin and sal_base_dec <= Decimal("3501810"))

        nuevo = Contrato(
            idContrato=siguiente_id,
            numeroContrato=datos["numeroContrato"],
            idPersona=datos["idPersona"],
            tipoContrato=datos["tipoContrato"],
            modalidadProfesor=datos.get("modalidadProfesor", datos["tipoContrato"]),
            regimenAplicable=datos.get("regimenAplicable", regimen_default),
            fechaInicio=datos["fechaInicio"],
            fechaFin=datos.get("fechaFin"),
            dedicacion=ded_val,
            horasSemanales=Decimal(str(datos.get("horasSemanales", 40))),
            salarioBase=sal_base_dec,
            salarioMensualPactado=Decimal(str(datos.get("salarioMensualPactado", datos.get("salarioBase", "0")))),
            aplicaAuxilioTransporte=datos.get("aplicaAuxilioTransporte", aplica_aux),
            estado="ACTIVO",
            esAdHonorem=datos.get("esAdHonorem", False),
            numeroCDP=datos.get("numeroCDP") or None,
            resolucionRectoral=datos.get("resolucionNombramiento") or None,
            claseARL=datos.get("claseRiesgoARL", "CLASE I"),
            observaciones=datos.get("observaciones") or None,
        )
        self.controller.contratos.append(nuevo)

        # Si el contrato pertenece a un administrativo, sincronizar su salario base
        adm = self.buscar_administrativo_por_id_persona(nuevo.idPersona)
        if adm:
            adm.salarioBase = sal_base_dec
            adm.estado = "ACTIVO"

        self.controller._recrear_gestores()
        return nuevo

    def actualizar_contrato(self, contrato: Contrato, datos: dict[str, Any]) -> None:
        for k, v in datos.items():
            if hasattr(contrato, k):
                setattr(contrato, k, v)

        # Sincronizar automáticamente con perfil administrativo si aplica
        adm = self.buscar_administrativo_por_id_persona(contrato.idPersona)
        if adm:
            if "salarioBase" in datos and datos["salarioBase"] is not None:
                adm.salarioBase = Decimal(str(datos["salarioBase"]))
                contrato.aplicaAuxilioTransporte = bool(adm.salarioBase <= Decimal("3501810"))
            if "estado" in datos and datos["estado"]:
                adm.estado = datos["estado"]

        self.controller._recrear_gestores()

    def terminar_contrato(self, contrato: Contrato, motivo: str, fecha_terminacion: date) -> None:
        contrato.estado = "TERMINADO"
        contrato.fechaFin = fecha_terminacion
        if hasattr(contrato, "observaciones"):
            contrato.observaciones = f"Terminado: {motivo}"
        adm = self.buscar_administrativo_por_id_persona(contrato.idPersona)
        if adm:
            adm.estado = "INACTIVO"
        self.controller._recrear_gestores()

    # ------------------------------------------------------------------
    # RECONOCIMIENTO DE FACTORES Y PRODUCCIÓN (DEC. 1279)
    # ------------------------------------------------------------------
    def reconocer_factor_salarial(
        self,
        id_profesor: int,
        tipo_factor_str: str,
        nombre: str,
        puntos: Decimal,
        acto_administrativo: str,
        fecha_reconocimiento: date,
    ) -> FactorSalarial:
        next_id = max((f.idFactor or 0 for f in self.controller.factores), default=0) + 1
        try:
            t_factor = TipoFactor[tipo_factor_str]
        except KeyError:
            t_factor = TipoFactor.TITULO_ACADEMICO

        factor = FactorSalarial(
            idFactor=next_id,
            idProfesor=id_profesor,
            tipoFactor=t_factor,
            nombre=nombre,
            puntosReconocidos=puntos,
            puntosAprobados=puntos,
            actoAdministrativo=acto_administrativo,
            fechaReconocimiento=fecha_reconocimiento,
            estado="APROBADO",
        )
        self.controller.factores.append(factor)

        # Actualizar puntos del profesor
        prof = self.buscar_profesor_por_id(id_profesor)
        if prof:
            prof.puntosSalariales = Decimal(str(getattr(prof, "puntosSalariales", 0) or 0)) + puntos
            if str(getattr(prof, "tipoProfesor", "")).upper() == "PLANTA":
                val_pto = self.obtener_parametro_decimal("VALOR_PUNTO_SALARIAL", Decimal("23924"))
                for c in self.controller.contratos:
                    if c.idPersona == prof.idPersona and str(getattr(c, "estado", "")).upper() == "ACTIVO":
                        f_ded = Decimal("0.5") if "MEDIO" in str(getattr(c, "dedicacion", "")).upper() else Decimal("1")
                        c.salarioBase = (prof.puntosSalariales * val_pto * f_ded).quantize(Decimal("1"))

        self.controller._recrear_gestores()
        return factor

    def reconocer_produccion_academica(
        self,
        id_profesor: int,
        tipo_prod: str,
        titulo: str,
        editorial: str,
        num_autores: int,
        puntos_docente: Decimal,
    ) -> ProduccionAcademica:
        next_id = max((p.idProduccion or 0 for p in self.controller.producciones), default=0) + 1
        factor_coautoria = Decimal("1.0") / Decimal(str(max(num_autores, 1)))

        produccion = ProduccionAcademica(
            idProduccion=next_id,
            idProfesor=id_profesor,
            tipoProduccion=tipo_prod,
            titulo=titulo,
            entidadPublicadora=editorial,
            identificadorProducto=editorial,
            numeroAutores=num_autores,
            factorCoautoria=factor_coautoria,
            puntosReconocidos=puntos_docente,
            puntosReconocidosProfesor=puntos_docente,
            fechaPublicacion=date.today(),
            estado="VALIDADO",
        )
        self.controller.producciones.append(produccion)

        # Actualizar puntos del profesor
        prof = self.buscar_profesor_por_id(id_profesor)
        if prof:
            prof.puntosSalariales = Decimal(str(getattr(prof, "puntosSalariales", 0) or 0)) + puntos_docente
            if str(getattr(prof, "tipoProfesor", "")).upper() == "PLANTA":
                val_pto = self.obtener_parametro_decimal("VALOR_PUNTO_SALARIAL", Decimal("23924"))
                for c in self.controller.contratos:
                    if c.idPersona == prof.idPersona and str(getattr(c, "estado", "")).upper() == "ACTIVO":
                        f_ded = Decimal("0.5") if "MEDIO" in str(getattr(c, "dedicacion", "")).upper() else Decimal("1")
                        c.salarioBase = (prof.puntosSalariales * val_pto * f_ded).quantize(Decimal("1"))

        self.controller._recrear_gestores()
        return produccion
