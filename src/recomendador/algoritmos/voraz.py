"""Selección voraz del Top-K con un min-heap de tamaño K.

Cada candidato entra al heap y, si se excede K, sale el peor: O(C log K)
para C candidatos, mejor que ordenar todo, O(C log C), cuando K << C.
Empates: gana el id de película menor, para que el resultado sea determinista.
"""
from __future__ import annotations

import heapq


def top_k(puntajes: dict[int, float], k: int = 10) -> list[tuple[int, float]]:
    heap: list[tuple[float, int]] = []
    for pelicula, p in puntajes.items():
        item = (p, -pelicula)
        if len(heap) < k:
            heapq.heappush(heap, item)
        elif item > heap[0]:
            heapq.heapreplace(heap, item)
    return [(-neg_id, p) for p, neg_id in sorted(heap, reverse=True)]
