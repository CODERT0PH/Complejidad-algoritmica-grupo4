"""Union-Find (UFDS) con compresión de caminos y unión por rango.

find / union cuestan O(α(n)) amortizado. `clusterizar_usuarios` agrupa
usuarios estilo Kruskal: ordena las aristas E_UU por similitud
descendente y las une hasta llegar a `num_clusters` componentes.
"""
from __future__ import annotations

from collections import defaultdict

from ..grafo import Grafo


class UnionFind:
    def __init__(self, elementos):
        self.padre = {e: e for e in elementos}
        self.rango = {e: 0 for e in elementos}
        self.componentes = len(self.padre)

    def find(self, x):
        raiz = x
        while self.padre[raiz] != raiz:
            raiz = self.padre[raiz]
        while self.padre[x] != raiz:
            self.padre[x], x = raiz, self.padre[x]
        return raiz

    def union(self, a, b) -> bool:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rango[ra] < self.rango[rb]:
            ra, rb = rb, ra
        self.padre[rb] = ra
        if self.rango[ra] == self.rango[rb]:
            self.rango[ra] += 1
        self.componentes -= 1
        return True

    def grupos(self) -> dict:
        g = defaultdict(list)
        for e in self.padre:
            g[self.find(e)].append(e)
        return dict(g)


def clusterizar_usuarios(grafo: Grafo, num_clusters: int) -> list[list[int]]:
    """Kruskal sobre las aristas usuario–usuario (E_UU) del grafo.

    Requiere haber llamado antes a `grafo.agregar_aristas_similitud(s)`.
    Ordenar las aristas cuesta O(|E_UU| log |E_UU|) y cada unión O(α(n)).
    """
    aristas = [(w, a, b) for a, vecinos in grafo.adj_uu.items() for b, w in vecinos.items() if a < b]
    aristas.sort(key=lambda t: (-t[0], t[1], t[2]))

    uf = UnionFind(grafo.adj_usuario.keys())
    for _, a, b in aristas:
        if uf.componentes <= num_clusters:
            break
        uf.union(a, b)
    return sorted((sorted(g) for g in uf.grupos().values()), key=lambda g: g[0])
