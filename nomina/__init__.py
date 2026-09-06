"""Paquete de motor de liquidación de nómina docente y prestaciones PITA."""

from __future__ import annotations

from nomina.excepciones import ErrorNomina
from nomina.gestor_nomina import GestorNomina

__all__ = ["ErrorNomina", "GestorNomina"]
