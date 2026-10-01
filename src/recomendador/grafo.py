"""Grafo general no dirigido y ponderado G = (V, E) de usuarios y películas.

V = U ∪ M y E = E_UM ∪ E_UU ∪ E_MM:

- E_UM: el usuario calificó la película; peso = estrellas (1.0 a 5.0).
- E_UU: dos usuarios dieron 4 o 5 estrellas a por lo menos `s` películas en
  común; peso = número de películas en común.
- E_MM: por lo menos `s` usuarios dieron 4 o 5 estrellas a ambas películas;
  peso = número de usuarios en común.

Cada tipo de arista se guarda como lista de adyacencia (diccionarios).
E_UM se construye en O(|V| + |E_UM|). E_UU y E_MM se agregan aparte con
`agregar_aristas_similitud`.
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from .datos import Calificacion, Pelicula, Usuario, cargar_calificaciones, cargar_peliculas, cargar_usuarios

UMBRAL_GUSTO = 4.0


class Grafo:
    def __init__(self):
        self.usuarios: dict[int, Usuario] = {}
        self.peliculas: dict[int, Pelicula] = {}
        # E_UM, vista desde cada lado
        self.adj_usuario: dict[int, dict[int, float]] = defaultdict(dict)
        self.adj_pelicula: dict[int, dict[int, float]] = defaultdict(dict)
        # E_UU y E_MM
        self.adj_uu: dict[int, dict[int, int]] = defaultdict(dict)
        self.adj_mm: dict[int, dict[int, int]] = defaultdict(dict)

    @classmethod
    def desde_calificaciones(
        cls,
        calificaciones: list[Calificacion],
        usuarios: dict[int, Usuario] | None = None,
        peliculas: dict[int, Pelicula] | None = None,
    ) -> "Grafo":
        g = cls()
        g.usuarios = usuarios or {}
        g.peliculas = peliculas or {}
        for c in calificaciones:
            g.agregar_arista(c.usuario, c.pelicula, c.puntaje)
        return g

    @classmethod
    def desde_carpeta(cls, carpeta: str | Path) -> "Grafo":
        return cls.desde_calificaciones(
            cargar_calificaciones(carpeta), cargar_usuarios(carpeta), cargar_peliculas(carpeta)
        )

    def agregar_arista(self, usuario: int, pelicula: int, peso: float) -> None:
        self.adj_usuario[usuario][pelicula] = peso
        self.adj_pelicula[pelicula][usuario] = peso

    def agregar_aristas_similitud(self, s: int, umbral: float = UMBRAL_GUSTO) -> None:
        """Construye E_UU y E_MM con el umbral `s` de elementos en común.

        Cada usuario se codifica como un entero cuyos bits son las películas
        que le gustan (y cada película, con los bits de sus fans), de modo que
        |A ∩ B| = popcount(a & b). Comparar todos los pares cuesta
        O(|U|² · |M| / w + |M|² · |U| / w), con w = 64 bits por palabra.
        """
        if s < 1:
            raise ValueError("s debe ser al menos 1")
        id_peli = {m: i for i, m in enumerate(sorted(self.adj_pelicula))}
        id_usr = {u: i for i, u in enumerate(sorted(self.adj_usuario))}

        bits_usuario: dict[int, int] = {}
        bits_pelicula: dict[int, int] = defaultdict(int)
        for u, pelis in self.adj_usuario.items():
            b = 0
            for m, w in pelis.items():
                if w >= umbral:
                    b |= 1 << id_peli[m]
                    bits_pelicula[m] |= 1 << id_usr[u]
            bits_usuario[u] = b

        self.adj_uu = _aristas_por_interseccion(bits_usuario, s)
        self.adj_mm = _aristas_por_interseccion(bits_pelicula, s)

    def num_nodos(self) -> int:
        return len(self.usuarios.keys() | self.adj_usuario.keys()) + len(
            self.peliculas.keys() | self.adj_pelicula.keys()
        )

    def num_aristas_um(self) -> int:
        return sum(len(v) for v in self.adj_usuario.values())

    def num_aristas_uu(self) -> int:
        return sum(len(v) for v in self.adj_uu.values()) // 2

    def num_aristas_mm(self) -> int:
        return sum(len(v) for v in self.adj_mm.values()) // 2

    def num_aristas(self) -> int:
        return self.num_aristas_um() + self.num_aristas_uu() + self.num_aristas_mm()

    def densidad(self) -> float:
        """2|E| / (|V|(|V| − 1)), densidad de un grafo no dirigido."""
        n = self.num_nodos()
        return 2 * self.num_aristas() / (n * (n - 1)) if n > 1 else 0.0

    def titulo(self, pelicula: int) -> str:
        p = self.peliculas.get(pelicula)
        return p.titulo if p else str(pelicula)


def _aristas_por_interseccion(bits: dict[int, int], s: int) -> dict[int, dict[int, int]]:
    adj: dict[int, dict[int, int]] = defaultdict(dict)
    # Quien tiene menos de s "me gusta" no puede tener aristas.
    nodos = [(x, b) for x, b in sorted(bits.items()) if b.bit_count() >= s]
    for i, (a, ba) in enumerate(nodos):
        for b, bb in nodos[i + 1:]:
            comun = (ba & bb).bit_count()
            if comun >= s:
                adj[a][b] = comun
                adj[b][a] = comun
    return adj
