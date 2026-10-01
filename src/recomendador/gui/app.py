"""Interfaz gráfica (pendiente para Hito 2).

Controles previstos: selector de usuario, K, filtro por género, botón
"Recomendar" y pestaña con el subgrafo ego del usuario (Matplotlib/NetworkX).
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from ..algoritmos import candidatos_bfs, top_k
from ..grafo import Grafo


def ejecutar(grafo: Grafo) -> None:
    raiz = tk.Tk()
    raiz.title("Recomendador Grupo 4")

    ttk.Label(raiz, text="Usuario:").grid(row=0, column=0, padx=8, pady=8)
    usuario = ttk.Combobox(raiz, values=sorted(grafo.adj_usuario), width=10)
    usuario.grid(row=0, column=1)
    ttk.Label(raiz, text="K:").grid(row=0, column=2)
    k = ttk.Spinbox(raiz, from_=1, to=50, width=5)
    k.set(10)
    k.grid(row=0, column=3)

    salida = tk.Listbox(raiz, width=60, height=15)
    salida.grid(row=1, column=0, columnspan=5, padx=8, pady=8)

    def recomendar():
        salida.delete(0, tk.END)
        if not usuario.get():
            return
        ranking = top_k(candidatos_bfs(grafo, int(usuario.get())), int(k.get()))
        for i, (m, p) in enumerate(ranking, 1):
            salida.insert(tk.END, f"{i}. {grafo.titulo(m)}  ({p:.1f})")

    ttk.Button(raiz, text="Recomendar", command=recomendar).grid(row=0, column=4, padx=8)
    raiz.mainloop()
