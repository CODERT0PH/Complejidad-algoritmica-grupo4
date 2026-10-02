# Complejidad Algorítmica · Grupo 4

Recomendador de contenido tipo Netflix sobre **MovieLens 1M**, modelado como una
red general de muchos usuarios a muchas películas. Trabajo del curso 1ACC0184 Complejidad
Algorítmica (UPC, ciclo 2026-20), caso de estudio 4.

## Modelo de grafo

G = (V, E) no dirigido y ponderado, con V = U ∪ M y E = E_UM ∪ E_UU ∪ E_MM:

| Arista | Cuándo existe | Peso |
|---|---|---|
| Usuario–película (E_UM) | El usuario calificó la película | Estrellas, 1.0 a 5.0 |
| Usuario–usuario (E_UU) | Ambos dieron 4 o 5 estrellas a por lo menos `s` películas en común | Películas en común |
| Película–película (E_MM) | Al menos `s` usuarios dieron 4 o 5 estrellas a ambas | Usuarios en común |

`s` se elige con `--s` (por defecto 20). `main.py` imprime cuántas aristas hay de
cada tipo y la densidad 2|E| / (|V|(|V| − 1)).

## Algoritmos

| Módulo | Algoritmo | Complejidad | Hito |
|---|---|---|---|
| `algoritmos/bfs.py` | BFS acotado a 3 niveles (w ≥ 4, top N = 50 vecinos) | O(\|V\| + \|E\|) peor caso | 1 |
| `algoritmos/voraz.py` | Selección voraz Top-K con min-heap | O(C log K) | 1 |
| `algoritmos/fuerza_bruta.py` | Línea base para validar | O(\|U\|·\|M\|) | 1 |
| `algoritmos/ufds.py` | Union-Find + Kruskal sobre E_UU | O(α(n)) por operación | 2 |

## Estructura

```
main.py                    # CLI: recomendar, comparar con fuerza bruta, abrir GUI
figuras.py                 # genera las Figuras 2, 3 y 4 del informe (PNG)
notebooks/Figuras_TB1_Colab.ipynb  # Colab: Figura 1 (usuario–película) y Figura 2 (usuario–usuario) con ML-1M
src/recomendador/
  datos.py                 # carga de users.dat, movies.dat, ratings.dat
  grafo.py                 # Grafo con E_UM, E_UU y E_MM (listas de adyacencia)
  algoritmos/              # BFS, voraz, fuerza bruta, UFDS
  gui/app.py               # interfaz Tkinter (borrador)
tests/                     # pruebas con unittest sobre dataset/muestra
dataset/
  muestra/                 # 6 usuarios, 8 películas, mismo formato que ML-1M
  ml-1m/                   # dataset completo (no versionado, ver dataset/README.md)
```

## Uso

Requiere Python 3.10+. El núcleo usa solo la biblioteca estándar.

```bash
pip install -r requirements.txt          # solo para GUI y visualización
python main.py --usuario 1 --k 10 --comparar
python main.py --s 30                      # otro umbral para E_UU y E_MM
python main.py --gui
python -m unittest discover -s tests -v
python figuras.py --usuario 1 --s 20      # Figuras 2, 3 y 4 del informe en figuras/
```

Sin `dataset/ml-1m/`, el programa usa `dataset/muestra/` automáticamente.

Para las figuras del TB1 sin instalar nada, abre `notebooks/Figuras_TB1_Colab.ipynb` en Google Colab
(Archivo → Abrir cuaderno → GitHub) y ejecuta todas las celdas: descarga MovieLens 1M, imprime las cifras
del grafo completo y descarga los PNG.

## Entregables

| Hito | Fecha | Nombre de archivo |
|---|---|---|
| Hito 1 (TB1) | 04/10/2026 | `TB1_1ACC0184_2026-20_CodigoAlum_ApellidoAlum` |
| Hito 2 (TB2) | 22/11/2026 | `TB2_1ACC0184_2026-20_CodigoAlum_ApellidoAlum` |
| Trabajo final | 29/11/2026 | `TrabajoFinal_1ACC0184_2026-20_CodigoAlum_ApellidoAlum.zip` |
