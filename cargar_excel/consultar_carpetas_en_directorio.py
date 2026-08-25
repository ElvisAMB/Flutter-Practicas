#!/usr/bin/env python3
"""
arbol.py — Lista el contenido de una ruta en forma de árbol jerárquico.

Permite filtrar qué se muestra: solo carpetas, solo archivos o ambos.

Uso:
    python arbol.py                       # modo interactivo
    python arbol.py "C:\\ruta" --modo todos
    python arbol.py . --modo archivos --plano
    python arbol.py . --modo carpetas --profundidad 2 --ocultos
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable, Iterator

# --- Conectores del árbol -------------------------------------------------
RAMA = "├── "
ULTIMA = "└── "
VERTICAL = "│   "
ESPACIO = "    "

MODOS = ("carpetas", "archivos", "todos")


# --- Utilidades -----------------------------------------------------------
def limpiar_consola() -> None:
    """Limpia la consola. Usa util.limpiar_consola si está disponible."""
    try:
        from util import limpiar_consola as _limpiar  # type: ignore
        _limpiar()
        return
    except Exception:
        pass
    import os
    os.system("cls" if os.name == "nt" else "clear")


def _es_dir(p: Path) -> bool:
    """is_dir() tolerante a enlaces rotos y errores de permisos."""
    try:
        return p.is_dir()
    except OSError:
        return False


def _ordenar(entradas: Iterable[Path], mostrar_ocultos: bool) -> list[Path]:
    """Carpetas primero, luego archivos; ambos alfabéticos e insensibles a mayúsculas."""
    items = [p for p in entradas if mostrar_ocultos or not p.name.startswith(".")]
    return sorted(items, key=lambda p: (not _es_dir(p), p.name.casefold()))


def _tiene_contenido(p: Path, mostrar_ocultos: bool) -> bool:
    """¿La carpeta tiene al menos una entrada visible? (sin recorrerla entera)."""
    try:
        return any(mostrar_ocultos or not h.name.startswith(".") for h in p.iterdir())
    except OSError:
        return False


def _etiqueta(p: Path) -> str:
    """Nombre a mostrar: '/' para carpetas, '@' para enlaces simbólicos."""
    nombre = p.name
    if p.is_symlink():
        nombre += " @"
    if _es_dir(p):
        nombre += "/"
    return nombre


# --- Construcción del árbol ----------------------------------------------
def _construir(
    directorio: Path,
    modo: str,
    profundidad: int,
    max_profundidad: int | None,
    mostrar_ocultos: bool,
    stats: dict[str, int],
) -> tuple[list[str], bool]:
    """
    Devuelve (líneas_relativas, contiene_archivos).

    Las líneas no incluyen el prefijo del nivel padre: el llamador lo antepone.
    Esto permite decidir el conector (├/└) *después* de saber qué hijos se muestran.
    `contiene_archivos` sirve para podar ramas vacías en el modo 'archivos'.
    """
    try:
        entradas = _ordenar(directorio.iterdir(), mostrar_ocultos)
    except PermissionError:
        return [ULTIMA + "[permiso denegado]"], False
    except OSError as exc:
        return [ULTIMA + f"[error: {exc.strerror or exc}]"], False

    # 1ª pasada: resolver hijos y decidir cuáles se muestran.
    visibles: list[tuple[str, list[str]]] = []
    contiene_archivos = False

    for entrada in entradas:
        if _es_dir(entrada):
            sub_lineas: list[str] = []
            sub_tiene_archivos = False
            truncado = False

            if entrada.is_symlink():
                truncado = False  # no seguimos enlaces: evita ciclos infinitos
            elif max_profundidad is not None and profundidad + 1 >= max_profundidad:
                truncado = _tiene_contenido(entrada, mostrar_ocultos)
            else:
                sub_lineas, sub_tiene_archivos = _construir(
                    entrada, modo, profundidad + 1, max_profundidad,
                    mostrar_ocultos, stats,
                )

            contiene_archivos = contiene_archivos or sub_tiene_archivos

            if modo == "archivos" and not sub_tiene_archivos:
                continue  # rama sin archivos: no aporta nada
            if truncado:
                sub_lineas = [ULTIMA + "…"]

            stats["carpetas"] += 1
            visibles.append((_etiqueta(entrada), sub_lineas))
        else:
            contiene_archivos = True
            if modo == "carpetas":
                continue
            stats["archivos"] += 1
            visibles.append((_etiqueta(entrada), []))

    # 2ª pasada: ya sabemos cuál es el último visible → conectores correctos.
    lineas: list[str] = []
    for i, (etiqueta, sub_lineas) in enumerate(visibles):
        ultimo = i == len(visibles) - 1
        lineas.append((ULTIMA if ultimo else RAMA) + etiqueta)
        relleno = ESPACIO if ultimo else VERTICAL
        lineas.extend(relleno + linea for linea in sub_lineas)

    return lineas, contiene_archivos


def arbol(
    ruta: Path,
    modo: str = "todos",
    max_profundidad: int | None = None,
    mostrar_ocultos: bool = False,
) -> tuple[list[str], dict[str, int]]:
    """Genera las líneas del árbol y las estadísticas de conteo."""
    if modo not in MODOS:
        raise ValueError(f"modo inválido: {modo!r} (use {', '.join(MODOS)})")
    if not ruta.exists():
        raise FileNotFoundError(f"La ruta no existe: {ruta}")
    if not ruta.is_dir():
        raise NotADirectoryError(f"La ruta no es una carpeta: {ruta}")

    stats = {"carpetas": 0, "archivos": 0}
    lineas, _ = _construir(ruta, modo, 0, max_profundidad, mostrar_ocultos, stats)
    return [f"{ruta}/"] + lineas, stats


def recorrer_plano(
    ruta: Path, modo: str = "todos", mostrar_ocultos: bool = False
) -> Iterator[Path]:
    """Listado plano de rutas relativas (útil para canalizar a otros comandos)."""
    for p in sorted(ruta.rglob("*"), key=lambda x: str(x).casefold()):
        if not mostrar_ocultos and any(part.startswith(".") for part in p.relative_to(ruta).parts):
            continue
        es_dir = _es_dir(p)
        if modo == "carpetas" and not es_dir:
            continue
        if modo == "archivos" and es_dir:
            continue
        yield p.relative_to(ruta)


# --- Interfaz de línea de comandos ---------------------------------------
def _preguntar_modo() -> str:
    print("¿Qué desea mostrar?")
    print("  1) Solo carpetas")
    print("  2) Solo archivos")
    print("  3) Carpetas y archivos")
    opciones = {"1": "carpetas", "2": "archivos", "3": "todos"}
    while True:
        eleccion = input("Opción [3]: ").strip() or "3"
        if eleccion in opciones:
            return opciones[eleccion]
        print("Opción inválida. Ingrese 1, 2 o 3.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Lista una ruta como árbol jerárquico.")
    parser.add_argument("ruta", nargs="?", help="Ruta a listar (si se omite, se pregunta).")
    parser.add_argument("-m", "--modo", choices=MODOS, help="Qué mostrar.")
    parser.add_argument("-p", "--profundidad", type=int, default=None,
                        help="Niveles máximos a descender (por defecto: sin límite).")
    parser.add_argument("-o", "--ocultos", action="store_true",
                        help="Incluir archivos y carpetas ocultos.")
    parser.add_argument("--plano", action="store_true",
                        help="Salida plana de rutas relativas en lugar de árbol.")
    parser.add_argument("--sin-limpiar", action="store_true",
                        help="No limpiar la consola antes de imprimir.")
    args = parser.parse_args(argv)

    ruta_txt = args.ruta or input("Ruta a listar: ").strip().strip('"')
    modo = args.modo or _preguntar_modo()
    ruta = Path(ruta_txt).expanduser()

    if not args.sin_limpiar:
        limpiar_consola()

    try:
        if args.plano:
            for rel in recorrer_plano(ruta, modo, args.ocultos):
                print(rel)
            return 0
        lineas, stats = arbol(ruta, modo, args.profundidad, args.ocultos)
    except (FileNotFoundError, NotADirectoryError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except PermissionError:
        print(f"Error: sin permisos para leer {ruta}", file=sys.stderr)
        return 1

    print("\n".join(lineas))
    c, a = stats["carpetas"], stats["archivos"]
    print(f"\n{c} carpeta{'s' if c != 1 else ''}, {a} archivo{'s' if a != 1 else ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
    
    
    
    
    
    