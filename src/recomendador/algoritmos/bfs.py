"""BFS acotado a 3 niveles sobre el grafo usuario–película.

Nivel 1: películas que el usuario objetivo calificó con w >= umbral.
Nivel 2: usuarios que también calificaron esas películas con w >= umbral;
         su similitud es el número de "me gusta" compartidos. Se conservan
         los `max_vecinos` más similares.
Nivel 3: películas que esos vecinos calificaron con w >= umbral y que el
         usuario objetivo no ha visto. Puntaje = Σ similitud(v) · w(v, m).

Complejidad: O(|V'| + |E'|) sobre el subgrafo alcanzado en 3 saltos, más
O(|V2| log N) para quedarse con los N vecinos (heap). En el peor caso
O(|V| + |E|), igual que un BFS completo.
"""
from __future__ import annotations

import heapq
from collections import defaultdict

from ..grafo import Grafo


def candidatos_bfs(
    grafo: Grafo,
    usuario: int,
    umbral: float = 4.0,
    max_vecinos: int = 50,
) -> dict[int, float]:
    vistas = grafo.adj_usuario.get(usuario, {})

    # Nivel 1
    nivel1 = [m for m, w in vistas.items() if w >= umbral]

    # Nivel 2
    similitud: dict[int, int] = defaultdict(int)
    for m in nivel1:
        for v, w in grafo.adj_pelicula[m].items():
            if v != usuario and w >= umbral:
                similitud[v] += 1
    vecinos = heapq.nlargest(max_vecinos, similitud.items(), key=lambda par: par[1])

    # Nivel 3
    puntaje: dict[int, float] = defaultdict(float)
    for v, sim in vecinos:
        for m, w in grafo.adj_usuario[v].items():
            if w >= umbral and m not in vistas:
                puntaje[m] += sim * w
    return dict(puntaje)
