"""Línea base por fuerza bruta, solo para validar BFS + voraz.

Compara al usuario contra TODOS los demás usuarios y puntúa TODAS las
películas no vistas, luego ordena la lista completa:
O(|U|·|M|) en el peor caso, más O(|M| log |M|) del ordenamiento.
Con max_vecinos = ∞ produce el mismo ranking que BFS + voraz.
"""
from __future__ import annotations

from ..grafo import Grafo


def recomendar_fuerza_bruta(
    grafo: Grafo,
    usuario: int,
    k: int = 10,
    umbral: float = 4.0,
) -> list[tuple[int, float]]:
    vistas = grafo.adj_usuario.get(usuario, {})
    gustos = {m for m, w in vistas.items() if w >= umbral}

    puntaje: dict[int, float] = {}
    for v, calificadas in grafo.adj_usuario.items():
        if v == usuario:
            continue
        sim = sum(1 for m in gustos if calificadas.get(m, 0) >= umbral)
        if sim == 0:
            continue
        for m in grafo.adj_pelicula:
            w = calificadas.get(m, 0)
            if w >= umbral and m not in vistas:
                puntaje[m] = puntaje.get(m, 0.0) + sim * w

    ranking = sorted(puntaje.items(), key=lambda par: (-par[1], par[0]))
    return ranking[:k]
