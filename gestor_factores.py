from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any, Iterable

from modelo_datos import CategoriaDocente, FactorSalarial, ProduccionAcademica, Profesor, TipoFactor


class ErrorFactor(ValueError):
    """Error de categoría, factor o producción académica."""


class GestorFactores:
    def __init__(
        self,
        categorias: list[CategoriaDocente],
        factores: list[FactorSalarial],
        producciones: list[ProduccionAcademica],
        profesores: list[Profesor] | None = None,
    ) -> None:
        self.categorias = categorias
        self.factores = factores
        self.producciones = producciones
        self.profesores = profesores if profesores is not None else []

    def crear_categoria(self, categoria: CategoriaDocente) -> CategoriaDocente:
        categoria.idCategoria = categoria.idCategoria or self._siguiente(self.categorias, "idCategoria")
        self._id_unico(self.categorias, "idCategoria", categoria.idCategoria, "categoría")
        if categoria.fechaFinVigencia and categoria.fechaInicioVigencia and categoria.fechaFinVigencia <= categoria.fechaInicioVigencia:
            raise ErrorFactor("La vigencia de la categoría es inválida")
        categoria.estado = categoria.estado or "ACTIVO"
        self.categorias.append(categoria)
        return categoria

    def registrar_factor(self, factor: FactorSalarial) -> FactorSalarial:
        # 1. Validar que el profesor exista
        self._validar_profesor_existe(factor.idProfesor, "factor salarial")

        # 2. Validar tipo de factor y campos asociados
        self._validar_tipo_factor(factor.tipoFactor, factor)

        factor.idFactor = factor.idFactor or self._siguiente(self.factores, "idFactor")
        self._id_unico(self.factores, "idFactor", factor.idFactor, "factor salarial")
        if factor.puntosSolicitados is not None and factor.puntosSolicitados < 0:
            raise ErrorFactor("Los puntos solicitados no pueden ser negativos")
        if factor.puntosSolicitados is not None and factor.puntosSolicitados > 0:
            # Verificar que el profesor tenga la categoría mínima para este tipo de factor
            self._verificar_categoria_minima(factor.idProfesor, factor.tipoFactor)
        factor.estado = factor.estado or "SOLICITADO"
        self.factores.append(factor)
        # Actualizar puntos del profesor automáticamente al registrar
        self._actualizar_puntos_profesor(factor.idProfesor)
        return factor

    def aprobar_factor(self, id_factor: int, puntos_aprobados: Decimal) -> FactorSalarial:
        factor = self._buscar(self.factores, "idFactor", id_factor, "factor salarial")
        if puntos_aprobados < 0 or (factor.puntosSolicitados is not None and puntos_aprobados > factor.puntosSolicitados):
            raise ErrorFactor("Los puntos aprobados no son válidos")
        factor.puntosAprobados = puntos_aprobados
        factor.puntosReconocidos = puntos_aprobados
        factor.estado = "APROBADO"
        factor.fechaReconocimiento = factor.fechaReconocimiento or date.today()
        self._actualizar_puntos_profesor(factor.idProfesor)
        return factor

    def registrar_produccion(self, produccion: ProduccionAcademica) -> ProduccionAcademica:
        # 1. Validar que el profesor exista
        self._validar_profesor_existe(produccion.idProfesor, "producción académica")

        # 2. Validar campos de producto académico según el tipo
        self._validar_tipo_produccion(produccion.tipoProduccion, produccion)

        if any(item.identificadorProducto == produccion.identificadorProducto and produccion.identificadorProducto for item in self.producciones):
            raise ErrorFactor("El producto académico ya fue registrado")
        # 3. Validar que no haya reconocimientos previos por mismo concepto (brecha B3)
        self._validar_reconocimiento_simultaneo(produccion)
        produccion.idProduccion = produccion.idProduccion or self._siguiente(self.producciones, "idProduccion")
        self._id_unico(self.producciones, "idProduccion", produccion.idProduccion, "producción académica")
        produccion.factorCoautoria = self.calcular_factor_coautoria(produccion.numeroAutores or 1)
        produccion.estadoValidacion = produccion.estadoValidacion or "PENDIENTE"
        self.producciones.append(produccion)
        # Actualizar puntos del profesor automáticamente al registrar
        self._actualizar_puntos_profesor(produccion.idProfesor)
        return produccion

    def _validar_reconocimiento_simultaneo(self, produccion: ProduccionAcademica) -> None:
        """Validar que no haya reconocimientos simultáneos por mismo concepto (brecha B3).

        Reglas:
        - Un producto no puede recibir simultáneamente puntos salariales y bonificación por el mismo concepto
        - Una reclasificación solo reconocerá la diferencia con respecto al nuevo tope
        """
        # Buscar producciones previas del mismo profesor con reconocimiento validado
        producciones_previas = [
            p for p in self.producciones
            if p.idProfesor == produccion.idProfesor
            and p.idProduccion != produccion.idProduccion
            and p.estadoValidacion == "VALIDADO"
        ]

        for prod_ant in producciones_previas:
            # Si la producción anterior ya tiene puntos reconocidos, la nueva solo puede
            # reconocer la diferencia con respecto al nuevo tope
            if prod_ant.puntosReconocidosProfesor is not None and prod_ant.puntosReconocidos is not None:
                # Marcar que esta producción es una reclasificación
                produccion.productoReclasificado = True
                # Calcular la diferencia con respecto al reconocimiento anterior
                diferencia = produccion.puntosSolicitados or Decimal("0") - prod_ant.puntosReconocidosProfesor
                if diferencia > Decimal("0"):
                    # Solo se reconoce la diferencia positiva (si el nuevo tope es mayor)
                    produccion.puntosAdicionalesReclasificacion = diferencia
                # Si la diferencia es negativa o cero, no se añaden puntos adicionales
                # (la reclasificación solo reconocerá la diferencia con respecto al nuevo tope)
                produccion.yaReconocidoOtroConcepto = True

    @staticmethod
    def calcular_factor_coautoria(numero_autores: int) -> Decimal:
        if numero_autores <= 0:
            raise ErrorFactor("El número de autores debe ser positivo")
        if numero_autores <= 3:
            return Decimal("1.0")
        if numero_autores <= 5:
            return Decimal("0.5")
        return Decimal("2") / numero_autores

    def reconocer_puntos(self, id_produccion: int, puntos: Decimal) -> ProduccionAcademica:
        produccion = self._buscar(self.producciones, "idProduccion", id_produccion, "producción académica")
        if puntos < 0:
            raise ErrorFactor("Los puntos reconocidos no pueden ser negativos")
        # 3. Validar reconocimiento simultáneo (brecha B3) - solo permite la diferencia con respecto al tope existente
        self._validar_reconocimiento_simultaneo(produccion)
        produccion.puntosReconocidos = puntos
        produccion.puntosReconocidosProfesor = puntos * (produccion.factorCoautoria or Decimal("1"))
        produccion.estadoValidacion = "VALIDADO"
        produccion.fechaReconocimiento = produccion.fechaReconocimiento or date.today()
        self._actualizar_puntos_profesor(produccion.idProfesor)
        return produccion

    def calcular_puntos_profesor(self, id_profesor: int, fecha_corte: date | None = None) -> Decimal:
        """Calcula los puntos vigentes de carrera docente bajo Decreto 1279."""
        profesor = self._buscar(self.profesores, "idProfesor", id_profesor, "profesor")
        fecha = fecha_corte or date.today()
        categoria = self._categoria_vigente(profesor, fecha)
        puntos_categoria = self._puntos_categoria(categoria, profesor)
        puntos_factores = sum((self._puntos_factor(factor, fecha) for factor in self.factores if factor.idProfesor == id_profesor), Decimal("0"))
        puntos_produccion = sum((self._puntos_produccion(produccion, fecha) for produccion in self.producciones if produccion.idProfesor == id_profesor), Decimal("0"))
        total = puntos_categoria + puntos_factores + puntos_produccion
        profesor.puntosSalariales = total
        return total

    def _actualizar_puntos_profesor(self, id_profesor: int | None) -> None:
        if id_profesor is not None and any(item.idProfesor == id_profesor for item in self.profesores):
            self.calcular_puntos_profesor(id_profesor)

    def _categoria_vigente(self, profesor: Profesor, fecha: date) -> CategoriaDocente | None:
        codigos = {str(profesor.categoriaDocente or "").upper(), str(profesor.categoriaReconocida or "").upper()}
        candidatos = [categoria for categoria in self.categorias if str(getattr(categoria.estado, "value", categoria.estado or "ACTIVO")).upper() == "ACTIVO" and (categoria.fechaInicioVigencia is None or categoria.fechaInicioVigencia <= fecha) and (categoria.fechaFinVigencia is None or fecha <= categoria.fechaFinVigencia) and (categoria.idCategoria == profesor.idCategoriaDocente or str(getattr(categoria.codigo, "value", categoria.codigo or "")).upper() in codigos)]
        return max(candidatos, key=lambda item: item.fechaInicioVigencia or date.min, default=None)

    @staticmethod
    def _puntos_categoria(categoria: CategoriaDocente | None, profesor: Profesor) -> Decimal:
        if categoria is not None:
            return categoria.puntosCategoria if categoria.puntosCategoria is not None else (categoria.puntosBase or Decimal("0"))
        codigo = str(profesor.categoriaReconocida or profesor.categoriaDocente or "").upper()
        return {"AUXILIAR": Decimal("37"), "ASISTENTE": Decimal("58"), "ASOCIADO": Decimal("74"), "TITULAR": Decimal("96")}.get(codigo, Decimal("0"))

    @staticmethod
    def _puntos_factor(factor: FactorSalarial, fecha: date) -> Decimal:
        if str(getattr(factor.estado, "value", factor.estado or "")).upper() != "APROBADO" or getattr(factor.tipoFactor, "value", factor.tipoFactor) == TipoFactor.CATEGORIA_DOCENTE.value:
            return Decimal("0")
        inicio = factor.fechaEfectoSalarial or factor.fechaReconocimiento or factor.vigenciaDesde
        if (inicio and inicio > fecha) or (factor.vigenciaHasta and fecha > factor.vigenciaHasta):
            return Decimal("0")
        return factor.puntosReconocidos if factor.puntosReconocidos is not None else (factor.puntosAprobados or Decimal("0"))

    @staticmethod
    def _puntos_produccion(produccion: ProduccionAcademica, fecha: date) -> Decimal:
        if str(produccion.estadoValidacion or "").upper() != "VALIDADO":
            return Decimal("0")
        fecha_efecto = produccion.fechaActoReconocimiento or produccion.fechaReconocimiento
        return Decimal("0") if fecha_efecto and fecha_efecto > fecha else (produccion.puntosReconocidosProfesor or Decimal("0"))

    def consultar_factores_profesor(self, id_profesor: int) -> list[FactorSalarial]:
        return [factor for factor in self.factores if factor.idProfesor == id_profesor]

    def _profesor_id(self, id_profesor: int | None) -> None:
        if id_profesor is None:
            raise ErrorFactor("El factor o producción requiere un profesor")

    def _validar_profesor_existe(self, id_profesor: int, nombre_contexto: str) -> None:
        """Validar que el profesor existe en la lista de profesores registrados."""
        profesor_encontrado = next(
            (profesor for profesor in self.profesores if profesor.idProfesor == id_profesor),
            None,
        )
        if profesor_encontrado is None:
            raise ErrorFactor(f"No existe el profesor con ID {id_profesor} para el {nombre_contexto}")

    def _validar_tipo_factor(self, tipo_factor: str | None, factor: FactorSalarial) -> None:
        """Validar completamente los campos según el tipo de factor."""
        if not tipo_factor:
            raise ErrorFactor("El tipo de factor es obligatorio para registrar un factor salarial")

        tipo = str(getattr(tipo_factor, "value", tipo_factor or "")).upper()

        # Validar según el tipo de factor
        if tipo == TipoFactor.TITULO_ACADEMICO.value:
            # Para títulos académicos, validar que tenga puntos o reconocimiento
            if not factor.puntosReconocidos and not factor.puntosAprobados:
                raise ErrorFactor(
                    "El factor de título académico requiere puntos reconocidos o aprobados"
                )
        elif tipo == TipoFactor.CATEGORIA_DOCENTE.value:
            # Para categoría docente, validar que tenga categoría asociada
            if not factor.idProfesor:
                raise ErrorFactor("El factor de categoría docente requiere ID de profesor")
        elif tipo == TipoFactor.EXPERIENCIA.value:
            # Para experiencia, validar años o puntos
            if factor.puntosSolicitados is None and factor.cantidad is None:
                raise ErrorFactor("El factor de experiencia requiere puntos o cantidad solicitados")
        elif tipo == TipoFactor.PRODUCTIVIDAD_ACADEMICA.value:
            # Para productividad, verificar que haya producciones asociadas
            producciones_profesor = [
                p for p in self.producciones if p.idProfesor == factor.idProfesor
            ]
            if not producciones_profesor:
                raise ErrorFactor(
                    "El factor de productividad requiere producciones académicas registradas"
                )
        elif tipo == TipoFactor.GRUPO_INVESTIGACION.value:
            # Para grupo de investigación, validar nombre y categoría
            if not factor.nombre or not factor.nombre.strip():
                raise ErrorFactor("El factor de grupo de investigación requiere nombre")
        elif tipo == TipoFactor.SEMILLERO.value:
            # Para semillero, validar pertenencia a carrera
            if not factor.idProfesor:
                raise ErrorFactor("El factor de semillero requiere ID de profesor")

    def _validar_tipo_produccion(self, tipo_produccion: str | None, produccion: ProduccionAcademica) -> None:
        """Validar campos según el tipo de producción académica."""
        if not tipo_produccion:
            raise ErrorFactor("El tipo de producción es obligatorio")

        tipo = str(getattr(tipo_produccion, "value", tipo_produccion or "")).upper()

        # Validaciones por tipo de producción
        if tipo in {"ARTICULO", "ARTICULO_CIENTIFICO"}:
            if not produccion.titulo or not produccion.titulo.strip():
                raise ErrorFactor("La producción de artículo requiere título")
            if not produccion.entidadPublicadora or not produccion.entidadPublicadora.strip():
                raise ErrorFactor("La producción de artículo requiere entidad publicadora")
        elif tipo in {"LIBRO", "CAPITULO_LIBRO"}:
            if not produccion.titulo or not produccion.titulo.strip():
                raise ErrorFactor("La producción de libro/capítulo requiere título")
            if not produccion.identificadorProducto or not produccion.identificadorProducto.strip():
                raise ErrorFactor("La producción de libro requiere identificador (ISBN o similar)")
        elif tipo in {"INVENTO", "MODELO_UTILIDAD"}:
            if not produccion.titulo or not produccion.titulo.strip():
                raise ErrorFactor("La producción de invento requiere título")
            if not produccion.registroDerechoAutor or not produccion.registroDerechoAutor.strip():
                raise ErrorFactor("La producción de invento requiere registro de derecho autor")
        elif tipo == {"PROYECTO_INVESTIGACION"}:
            if not produccion.titulo or not produccion.titulo.strip():
                raise ErrorFactor("El proyecto de investigación requiere título")
            if not produccion.entidadIndexadora or not produccion.entidadIndexadora.strip():
                raise ErrorFactor("El proyecto requiere entidad indexadora")
        elif tipo == {"OTRO"}:
            # Para otro tipo, solo validar que tenga descripción o título
            if not produccion.titulo and not produccion.descripcion:
                raise ErrorFactor("La producción 'OTRO' requiere título o descripción")

    def _verificar_categoria_minima(self, id_profesor: int, tipo_factor: str) -> None:
        """Verificar que el profesor tenga la categoría mínima para el tipo de factor."""
        profesor = next(
            (p for p in self.profesores if p.idProfesor == id_profesor),
            None,
        )
        if not profesor:
            return

        codigo_categoria = str(getattr(profesor.categoriaDocente or "", "value", profesor.categoriaDocente or "")).upper()

        # Definir categorías mínimas por tipo de factor
        categorias_minimas = {
            TipoFactor.TITULO_ACADEMICO.value: {"DOCTORADO", "MAESTRIA"},
            TipoFactor.CATEGORIA_DOCENTE.value: {"ASISTENTE", "ASOCIADO", "TITULAR"},
            TipoFactor.PRODUCTIVIDAD_ACADEMICA.value: {"ASISTENTE", "ASOCIADO", "TITULAR"},
        }

        # Verificar si la categoría del profesor es suficiente
        minimas_permitidas = categorias_minimas.get(tipo, set())
        if minimas_permitidas and codigo_categoria not in minimas_permitidas:
            # Advertencia pero no bloquear - el usuario puede sobrescribir después
            pass  # En el futuro podría lanzar warning

    def reconocer_puntos(self, id_produccion: int, puntos: Decimal) -> ProduccionAcademica:
        produccion = self._buscar(self.producciones, "idProduccion", id_produccion, "producción académica")
        if puntos < 0:
            raise ErrorFactor("Los puntos reconocidos no pueden ser negativos")
        produccion.puntosReconocidos = puntos
        # Calcular factor de coautoria si tiene autores
        if produccion.numeroAutores and produccion.numeroAutores > 0:
            produccion.factorCoautoria = self.calcular_factor_coautoria(produccion.numeroAutores)
        produccion.puntosReconocidosProfesor = puntos * (produccion.factorCoautoria or Decimal("1"))
        produccion.estadoValidacion = "VALIDADO"
        produccion.fechaReconocimiento = produccion.fechaReconocimiento or date.today()
        self._actualizar_puntos_profesor(produccion.idProfesor)
        return produccion
        elemento = next((item for item in elementos if getattr(item, campo, None) == valor), None)
        if elemento is None:
            raise ErrorFactor(f"No existe el {nombre} con ID {valor}")
        return elemento

    @staticmethod
    def _id_unico(elementos: Iterable[Any], campo: str, valor: Any, nombre: str) -> None:
        if any(getattr(item, campo, None) == valor for item in elementos):
            raise ErrorFactor(f"Ya existe un {nombre} con ID {valor}")

    @staticmethod
    def _buscar(elementos: Iterable[Any], campo: str, valor: Any, nombre: str) -> Any:
        elemento = next((item for item in elementos if getattr(item, campo, None) == valor), None)
        if elemento is None:
            raise ErrorFactor(f"No existe el {nombre} con ID {valor}")
        return elemento

    @staticmethod
    def _siguiente(elementos: Iterable[Any], campo: str) -> int:
        return max((getattr(item, campo) or 0 for item in elementos), default=0) + 1
