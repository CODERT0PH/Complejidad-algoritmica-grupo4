"""Carga de los archivos MovieLens 1M (formato `campo::campo::...`).

Los archivos .dat vienen en latin-1. Cada carga es O(n) en el número de líneas.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

SEP = "::"
ENCODING = "latin-1"


@dataclass(frozen=True)
class Usuario:
    id: int
    genero: str
    edad: int
    ocupacion: int
    zip: str


@dataclass(frozen=True)
class Pelicula:
    id: int
    titulo: str
    generos: tuple[str, ...]


@dataclass(frozen=True)
class Calificacion:
    usuario: int
    pelicula: int
    puntaje: float
    timestamp: int


def _lineas(ruta: Path):
    with open(ruta, encoding=ENCODING) as f:
        for linea in f:
            linea = linea.strip()
            if linea:
                yield linea.split(SEP)


def cargar_usuarios(carpeta: str | Path) -> dict[int, Usuario]:
    return {
        int(u): Usuario(int(u), g, int(e), int(o), z)
        for u, g, e, o, z in _lineas(Path(carpeta) / "users.dat")
    }


def cargar_peliculas(carpeta: str | Path) -> dict[int, Pelicula]:
    return {
        int(m): Pelicula(int(m), t, tuple(gs.split("|")))
        for m, t, gs in _lineas(Path(carpeta) / "movies.dat")
    }


def cargar_calificaciones(carpeta: str | Path) -> list[Calificacion]:
    return [
        Calificacion(int(u), int(m), float(r), int(ts))
        for u, m, r, ts in _lineas(Path(carpeta) / "ratings.dat")
    ]
