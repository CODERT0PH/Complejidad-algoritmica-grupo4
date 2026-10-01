"""Punto de entrada.

Ejemplos:
    python main.py --usuario 1 --k 10                  # usa dataset/ml-1m si existe
    python main.py --s 30                              # cambia el umbral de E_UU y E_MM
    python main.py --datos dataset/muestra --usuario 1 # muestra incluida en el repo
    python main.py --gui
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from recomendador.algoritmos import candidatos_bfs, recomendar_fuerza_bruta, top_k  # noqa: E402
from recomendador.grafo import Grafo  # noqa: E402

RAIZ = Path(__file__).parent
DATOS_COMPLETOS = RAIZ / "dataset" / "ml-1m"
DATOS_MUESTRA = RAIZ / "dataset" / "muestra"


def main() -> None:
    p = argparse.ArgumentParser(description="Recomendador MovieLens 1M - Grupo 4")
    p.add_argument("--datos", type=Path, default=DATOS_COMPLETOS if DATOS_COMPLETOS.exists() else DATOS_MUESTRA)
    p.add_argument("--usuario", type=int, default=1)
    p.add_argument("--k", type=int, default=10)
    p.add_argument("--s", type=int, default=20,
                   help="mínimo de películas (o usuarios) en común para crear aristas E_UU y E_MM")
    p.add_argument("--comparar", action="store_true", help="también corre fuerza bruta y compara tiempos")
    p.add_argument("--gui", action="store_true")
    args = p.parse_args()

    t0 = time.perf_counter()
    grafo = Grafo.desde_carpeta(args.datos)
    ms_um = (time.perf_counter() - t0) * 1000
    t0 = time.perf_counter()
    grafo.agregar_aristas_similitud(args.s)
    ms_sim = (time.perf_counter() - t0) * 1000
    print(f"Datos: {args.datos}")
    filas = [
        ("Nodos |V|", grafo.num_nodos()),
        ("Aristas E_UM", grafo.num_aristas_um()),
        (f"Aristas E_UU (s={args.s})", grafo.num_aristas_uu()),
        (f"Aristas E_MM (s={args.s})", grafo.num_aristas_mm()),
        ("Total |E|", grafo.num_aristas()),
    ]
    for nombre, valor in filas:
        print(f"{nombre:<24}{valor:>12,}")
    print(f"Tiempo E_UM: {ms_um:.0f} ms; E_UU + E_MM: {ms_sim:.0f} ms")
    print(f"Densidad 2|E|/(|V|(|V|-1)): {grafo.densidad():.6f}")

    if args.gui:
        from recomendador.gui.app import ejecutar
        ejecutar(grafo)
        return

    t0 = time.perf_counter()
    ranking = top_k(candidatos_bfs(grafo, args.usuario), args.k)
    ms = (time.perf_counter() - t0) * 1000
    print(f"\nTop-{args.k} para el usuario {args.usuario} (BFS + voraz, {ms:.1f} ms):")
    for i, (m, s) in enumerate(ranking, 1):
        print(f"{i:>3}. {grafo.titulo(m)}  [{s:.1f}]")

    if args.comparar:
        t0 = time.perf_counter()
        base = recomendar_fuerza_bruta(grafo, args.usuario, args.k)
        ms_fb = (time.perf_counter() - t0) * 1000
        coincidencias = len({m for m, _ in ranking} & {m for m, _ in base})
        print(f"\nFuerza bruta: {ms_fb:.1f} ms; coincidencias en el Top-{args.k}: {coincidencias}/{len(base)}")


if __name__ == "__main__":
    main()
