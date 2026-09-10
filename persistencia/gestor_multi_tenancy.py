"""Gestor de Aislamiento de Datos Multi-Tenancy por Universidad para PITA."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class TenantUniversidad:
    """Metadatos de una universidad registrada con su espacio de almacenamiento aislado."""
    idUniversidad: int
    codigo: str
    nombre: str
    directorio: str  # Nombre de la subcarpeta relativa, ej: "upc"
    estado: str = "ACTIVO"


class GestorMultiTenancy:
    """Orquestador de espacios de almacenamiento independientes por universidad."""

    DELIMITADOR = "|"
    ARCHIVO_CATALOGO = "universidades.txt"

    def __init__(self, directorio_base: Path | str = "datos") -> None:
        self.directorio_base = Path(directorio_base)
        self.archivo_catalogo = self.directorio_base / self.ARCHIVO_CATALOGO
        self.tenants: list[TenantUniversidad] = []
        self.cargar_catalogo()

    def cargar_catalogo(self) -> list[TenantUniversidad]:
        """Carga el catálogo maestro de universidades y sus carpetas asignadas."""
        if not self.directorio_base.exists():
            self.directorio_base.mkdir(parents=True, exist_ok=True)

        if not self.archivo_catalogo.exists():
            self._crear_catalogo_por_defecto()

        self.tenants = []
        with self.archivo_catalogo.open("r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if not linea:
                    continue
                partes = linea.split(self.DELIMITADOR)
                if len(partes) >= 4:
                    t = TenantUniversidad(
                        idUniversidad=int(partes[0]),
                        codigo=partes[1].strip(),
                        nombre=partes[2].strip(),
                        directorio=partes[3].strip(),
                        estado=partes[4].strip() if len(partes) > 4 else "ACTIVO",
                    )
                    self.tenants.append(t)
        return self.tenants

    def guardar_catalogo(self) -> None:
        """Guarda la lista de tenants en el archivo catálogo."""
        with self.archivo_catalogo.open("w", encoding="utf-8", newline="\n") as f:
            for t in self.tenants:
                f.write(f"{t.idUniversidad}|{t.codigo}|{t.nombre}|{t.directorio}|{t.estado}\n")

    def _crear_catalogo_por_defecto(self) -> None:
        """Crea el catálogo inicial asociando UPC y UNAL a sus respectivas subcarpetas."""
        self.tenants = [
            TenantUniversidad(1, "UPC", "Universidad Popular del Cesar", "upc", "ACTIVO"),
            TenantUniversidad(2, "UNAL", "Universidad Nacional de Colombia", "unal", "ACTIVO"),
        ]
        self.guardar_catalogo()

    def obtener_tenant(self, identificador: int | str) -> TenantUniversidad | None:
        """Busca un tenant por su idUniversidad, código (UPC, UNAL) o nombre de carpeta."""
        id_str = str(identificador).strip().upper()
        for t in self.tenants:
            if str(t.idUniversidad) == id_str or t.codigo.upper() == id_str or t.directorio.upper() == id_str:
                return t
            if id_str in t.nombre.upper():
                return t
        return None

    def obtener_directorio_tenant(self, identificador: int | str) -> Path:
        """Retorna la ruta absoluta al directorio aislado de la universidad."""
        tenant = self.obtener_tenant(identificador)
        if tenant:
            dir_tenant = self.directorio_base / tenant.directorio
            dir_tenant.mkdir(parents=True, exist_ok=True)
            return dir_tenant
        # Si no se encuentra como tenant, pero es una subcarpeta existente, retornarla
        posible = self.directorio_base / str(identificador).lower()
        if posible.is_dir():
            return posible
        raise ValueError(f"No se encontró el espacio aislado de datos para la universidad: {identificador}")

    def generar_codigo_sugerido(self, nombre: str) -> str:
        """Genera un código mnemónico sugerido a partir del nombre institucional."""
        palabras_todas = [p.strip() for p in nombre.upper().split() if p.strip()]
        if not palabras_todas:
            base = "UNIV"
        elif len(palabras_todas) >= 3 and palabras_todas[0] in ("UNIVERSIDAD", "UNIV") and palabras_todas[1] in ("DE", "DEL"):
            resto = palabras_todas[2]
            if palabras_todas[1] == "DE":
                if resto in ("ANTIOQUIA", "AMAZONIA"):
                    base = f"UDE{resto[0]}"
                elif len(palabras_todas) == 3:
                    base = f"U{resto[:5]}"
                else:
                    base = f"U{''.join(p[0] for p in palabras_todas[1:] if p not in ('DE', 'DEL', 'LA', 'EL', 'LOS', 'LAS'))}"
            elif palabras_todas[1] == "DEL":
                if resto == "VALLE":
                    base = "UNIVALLE"
                else:
                    base = f"U{resto[:5]}"
            else:
                base = f"U{resto[:4]}"
        else:
            partes_siglas = [p for p in palabras_todas if p not in ("DE", "DEL", "LA", "EL", "Y", "E", "EN", "LOS", "LAS")]
            if not partes_siglas:
                base = "UNIV"
            elif len(partes_siglas) == 1:
                base = partes_siglas[0][:6]
            elif len(partes_siglas) == 2 and partes_siglas[0] in ("UNIVERSIDAD", "UNIV"):
                base = f"U{partes_siglas[1][:5]}"
            else:
                base = "".join(p[0] for p in partes_siglas[:5])

        codigo_candidato = base.upper().strip()
        idx = 1
        while not self.validar_codigo_disponible(codigo_candidato):
            idx += 1
            codigo_candidato = f"{base}-{idx}"
        return codigo_candidato

    def validar_codigo_disponible(self, codigo: str, id_excluir: int | None = None) -> bool:
        """Retorna True si el código no está siendo usado por otra universidad."""
        cod_limpio = codigo.strip().upper()
        for t in self.tenants:
            if id_excluir is not None and t.idUniversidad == id_excluir:
                continue
            if t.codigo.upper() == cod_limpio or t.directorio.upper() == cod_limpio:
                return False
        return True

    def registrar_tenant(
        self,
        nombre: str | int,
        codigo: str | None = None,
        id_universidad: int | str | None = None,
        directorio: str | None = None,
        nit: str = "",
        ciudad: str = "",
        departamento: str = "",
        direccion: str = "",
        telefono: str = "",
        correo: str = "",
        web: str = "",
        caja_compensacion: str = "",
        arl: str = "",
        plantilla_dir: Path | None = None,
    ) -> TenantUniversidad:
        """Registra una nueva universidad con código único y aprovisiona su carpeta aislada."""
        # Soporte para firma clásica posicional: (id_universidad, codigo, nombre, directorio)
        if isinstance(nombre, int) or (isinstance(nombre, str) and str(nombre).isdigit() and isinstance(id_universidad, str)):
            id_real = int(nombre)
            nombre_real = str(id_universidad)
            codigo_real = str(codigo) if codigo is not None else None
            dir_real = str(directorio) if directorio is not None else None
            id_universidad = id_real
            nombre = nombre_real
            codigo = codigo_real
            directorio = dir_real

        nombre_str = str(nombre).strip()
        # 1. Asignar ID institucional correlativo si no se especifica
        if id_universidad is None or not str(id_universidad).isdigit():
            max_id = max((t.idUniversidad for t in self.tenants), default=0)
            id_universidad = max_id + 1
        else:
            id_universidad = int(id_universidad)

        # 2. Asignar y validar código institucional único
        if not codigo or not str(codigo).strip():
            codigo_final = self.generar_codigo_sugerido(nombre_str)
        else:
            codigo_final = str(codigo).strip().upper()
            if not self.validar_codigo_disponible(codigo_final, id_excluir=id_universidad):
                raise ValueError(f"El código institucional '{codigo_final}' ya está registrado. Debe ser único.")

        dir_name = directorio or codigo_final.lower().replace("-", "_").strip()
        dir_path = self.directorio_base / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)

        nuevo_tenant = TenantUniversidad(
            idUniversidad=id_universidad,
            codigo=codigo_final,
            nombre=nombre_str,
            directorio=dir_name,
            estado="ACTIVO",
        )

        # Reemplazar si ya existe por ID o agregar
        self.tenants = [t for t in self.tenants if t.idUniversidad != id_universidad]
        self.tenants.append(nuevo_tenant)
        self.guardar_catalogo()

        # 3. Aprovisionar archivos base en el espacio aislado
        fuente_plantilla = plantilla_dir or (self.directorio_base / "upc")
        if not fuente_plantilla.is_dir():
            fuente_plantilla = self.directorio_base

        import shutil
        for arch in fuente_plantilla.glob("*.txt"):
            if arch.name in ("universidades.txt", "universidad.txt"):
                continue
            destino = dir_path / arch.name
            if not destino.exists():
                shutil.copy2(arch, destino)

        # 4. Escribir los datos institucionales propios en su universidad.txt
        linea_univ = (
            f"{id_universidad}|{nombre.strip()}|{nit.strip()}|{codigo_final}|"
            f"{direccion.strip()}|{ciudad.strip()}|{departamento.strip()}|{telefono.strip()}|"
            f"{correo.strip()}|{web.strip()}|ACTIVO|{caja_compensacion.strip()}|{arl.strip()}\n"
        )
        with (dir_path / "universidad.txt").open("w", encoding="utf-8") as f:
            f.write(linea_univ)

        return nuevo_tenant
