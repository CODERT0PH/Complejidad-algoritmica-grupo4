"""Genera las Figuras 2, 3 y 4 del informe a partir del dataset.

    python figuras.py                     # usa dataset/ml-1m si existe
    python figuras.py --usuario 1 --s 20  # usuario de la Figura 4 y umbral s

Guarda en figuras/:
    figura2_muestra_red.png    muestra de la red completa (3 tipos de arista)
    figura3_comunidad.png      subgrafo de una comunidad de gustos (UFDS sobre E_UU)
    figura4_vecindario.png     vecindario a dos saltos de un usuario
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import networkx as nx  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent / "src"))

from recomendador.algoritmos import clusterizar_usuarios  # noqa: E402
from recomendador.grafo import UMBRAL_GUSTO, Grafo  # noqa: E402

RAIZ = Path(__file__).parent
DATOS_COMPLETOS = RAIZ / "dataset" / "ml-1m"
DATOS_MUESTRA = RAIZ / "dataset" / "muestra"

COLOR_USUARIO = "#2f6fb0"
COLOR_PELICULA = "#e08a2c"
COLOR_UM = "#9aa5b1"
COLOR_UU = "#2f6fb0"
COLOR_MM = "#e08a2c"


def gustos(grafo: Grafo, u: int) -> set[int]:
    return {m for m, w in grafo.adj_usuario[u].items() if w >= UMBRAL_GUSTO}


def subgrafo(grafo: Grafo, usuarios: set[int], peliculas: set[int]) -> nx.Graph:
    """Subgrafo inducido con las tres clases de arista entre los nodos dados."""
    g = nx.Graph()
    g.add_nodes_from((("U", u) for u in usuarios), tipo="usuario")
    g.add_nodes_from((("M", m) for m in peliculas), tipo="pelicula")
    for u in usuarios:
        for m, w in grafo.adj_usuario[u].items():
            if m in peliculas and w >= UMBRAL_GUSTO:
                g.add_edge(("U", u), ("M", m), tipo="UM", peso=w)
        for v, w in grafo.adj_uu.get(u, {}).items():
            if v in usuarios:
                g.add_edge(("U", u), ("U", v), tipo="UU", peso=w)
    for m in peliculas:
        for n, w in grafo.adj_mm.get(m, {}).items():
            if n in peliculas:
                g.add_edge(("M", m), ("M", n), tipo="MM", peso=w)
    return g


def dibujar(g: nx.Graph, grafo: Grafo, titulo: str, archivo: Path, centro=None, etiquetas_peliculas=False) -> None:
    fig, ax = plt.subplots(figsize=(11, 8), dpi=150)
    pos = nx.spring_layout(g, seed=7, k=1.6 / max(1, len(g)) ** 0.5)

    for tipo, color, ancho, alfa in (("UM", COLOR_UM, 0.8, 0.5), ("MM", COLOR_MM, 1.2, 0.6), ("UU", COLOR_UU, 1.4, 0.7)):
        aristas = [(a, b) for a, b, d in g.edges(data=True) if d["tipo"] == tipo]
        nx.draw_networkx_edges(g, pos, edgelist=aristas, edge_color=color, width=ancho, alpha=alfa, ax=ax)

    usuarios = [n for n in g if n[0] == "U"]
    peliculas = [n for n in g if n[0] == "M"]
    tam = lambda n: min(600, 60 + 8 * g.degree(n))  # noqa: E731
    nx.draw_networkx_nodes(g, pos, nodelist=usuarios, node_color=COLOR_USUARIO,
                           node_size=[tam(n) for n in usuarios], ax=ax)
    nx.draw_networkx_nodes(g, pos, nodelist=peliculas, node_color=COLOR_PELICULA, node_shape="s",
                           node_size=[tam(n) for n in peliculas], ax=ax)
    if centro is not None:
        nx.draw_networkx_nodes(g, pos, nodelist=[centro], node_color="#c0392b", node_size=600, ax=ax)

    etiquetas = {n: f"U{n[1]}" for n in usuarios}
    if etiquetas_peliculas:
        etiquetas.update({n: grafo.titulo(n[1])[:22] for n in peliculas})
    nx.draw_networkx_labels(g, pos, etiquetas, font_size=6, ax=ax)

    leyenda = [
        Line2D([], [], marker="o", ls="", color=COLOR_USUARIO, label="Usuario"),
        Line2D([], [], marker="s", ls="", color=COLOR_PELICULA, label="Película"),
        Line2D([], [], color=COLOR_UM, label="Usuario–película (E_UM)"),
        Line2D([], [], color=COLOR_UU, label="Usuario–usuario (E_UU)"),
        Line2D([], [], color=COLOR_MM, label="Película–película (E_MM)"),
    ]
    ax.legend(handles=leyenda, loc="lower left", fontsize=8, frameon=False)
    ax.set_title(f"{titulo}\n{len(usuarios)} usuarios, {len(peliculas)} películas, {g.number_of_edges()} aristas",
                 fontsize=11)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(archivo)
    plt.close(fig)
    print(f"Guardada {archivo}")


def figura2(grafo: Grafo, carpeta: Path, n_usuarios: int = 20, n_peliculas: int = 15) -> None:
    """Muestra de la red: los usuarios más conectados y sus películas favoritas en común."""
    usuarios = sorted(grafo.adj_usuario, key=lambda u: (-len(grafo.adj_uu.get(u, {})), u))[:n_usuarios]
    conteo = Counter(m for u in usuarios for m in gustos(grafo, u))
    peliculas = {m for m, _ in conteo.most_common(n_peliculas)}
    g = subgrafo(grafo, set(usuarios), peliculas)
    dibujar(g, grafo, "Figura 2. Muestra de la red usuarios–películas", carpeta / "figura2_muestra_red.png")


def figura3(grafo: Grafo, carpeta: Path, num_clusters: int, max_usuarios: int = 25, n_peliculas: int = 12) -> None:
    """Una comunidad encontrada con UFDS sobre E_UU y las películas que más le gustan."""
    comunidades = [c for c in clusterizar_usuarios(grafo, num_clusters) if len(c) > 1]
    if not comunidades:
        print("Figura 3: no hay comunidades con más de un usuario; baja --s.")
        return
    # La comunidad más pequeña con al menos 5 usuarios se ve mejor que la gigante.
    candidatas = [c for c in comunidades if len(c) >= 5] or comunidades
    comunidad = min(candidatas, key=len)
    usuarios = sorted(comunidad, key=lambda u: -len(grafo.adj_uu.get(u, {})))[:max_usuarios]
    conteo = Counter(m for u in usuarios for m in gustos(grafo, u))
    peliculas = {m for m, _ in conteo.most_common(n_peliculas)}
    g = subgrafo(grafo, set(usuarios), peliculas)
    dibujar(g, grafo, f"Figura 3. Comunidad de gustos ({len(comunidad)} usuarios, UFDS)",
            carpeta / "figura3_comunidad.png", etiquetas_peliculas=True)


def figura4(grafo: Grafo, carpeta: Path, usuario: int, n_peliculas: int = 12, n_vecinos: int = 12) -> None:
    """Vecindario a dos saltos: el usuario, sus películas favoritas y los usuarios más afines."""
    peliculas = sorted(gustos(grafo, usuario), key=lambda m: (-grafo.adj_usuario[usuario][m], -len(grafo.adj_pelicula[m])))
    peliculas = set(peliculas[:n_peliculas])
    afines = Counter()
    for m in peliculas:
        for v, w in grafo.adj_pelicula[m].items():
            if v != usuario and w >= UMBRAL_GUSTO:
                afines[v] += 1
    vecinos = {v for v, _ in afines.most_common(n_vecinos)}
    g = subgrafo(grafo, vecinos | {usuario}, peliculas)
    dibujar(g, grafo, f"Figura 4. Vecindario a dos saltos del usuario {usuario}",
            carpeta / "figura4_vecindario.png", centro=("U", usuario), etiquetas_peliculas=True)


def main() -> None:
    p = argparse.ArgumentParser(description="Genera las Figuras 2, 3 y 4 del informe")
    p.add_argument("--datos", type=Path, default=DATOS_COMPLETOS if DATOS_COMPLETOS.exists() else DATOS_MUESTRA)
    p.add_argument("--s", type=int, default=20, help="umbral de E_UU y E_MM (el mismo que en main.py)")
    p.add_argument("--usuario", type=int, default=1, help="usuario central de la Figura 4")
    p.add_argument("--comunidades", type=int, default=50, help="número de comunidades para UFDS")
    p.add_argument("--salida", type=Path, default=RAIZ / "figuras")
    args = p.parse_args()

    args.salida.mkdir(exist_ok=True)
    grafo = Grafo.desde_carpeta(args.datos)
    grafo.agregar_aristas_similitud(args.s)
    print(f"Datos: {args.datos} (s = {args.s})")

    figura2(grafo, args.salida)
    figura3(grafo, args.salida, args.comunidades)
    figura4(grafo, args.salida, args.usuario)


if __name__ == "__main__":
    main()
