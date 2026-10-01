import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from recomendador.algoritmos import (  # noqa: E402
    UnionFind,
    candidatos_bfs,
    clusterizar_usuarios,
    recomendar_fuerza_bruta,
    top_k,
)
from recomendador.grafo import Grafo  # noqa: E402

MUESTRA = RAIZ / "dataset" / "muestra"


class TestGrafo(unittest.TestCase):
    def setUp(self):
        self.g = Grafo.desde_carpeta(MUESTRA)

    def test_conteos(self):
        self.assertEqual(self.g.num_nodos(), 14)
        self.assertEqual(self.g.num_aristas_um(), 18)
        self.assertEqual(self.g.num_aristas(), 18)
        self.assertEqual(self.g.titulo(1), "Toy Story (1995)")

    def test_aristas_similitud_s1(self):
        self.g.agregar_aristas_similitud(1)
        # Gustos (w >= 4): 1 {1,2,5}, 2 {1,2,5,8}, 3 {3,6,7}, 4 {1,8}, 5 {3,4,6}, 6 {7}
        self.assertEqual(dict(self.g.adj_uu[1]), {2: 3, 4: 1})
        self.assertEqual(dict(self.g.adj_uu[3]), {5: 2, 6: 1})
        self.assertEqual(self.g.num_aristas_uu(), 5)
        # Películas 1 y 2: fans comunes {1, 2}
        self.assertEqual(self.g.adj_mm[1][2], 2)
        self.assertEqual(self.g.adj_mm[2][1], 2)

    def test_aristas_similitud_s2(self):
        self.g.agregar_aristas_similitud(2)
        self.assertEqual(self.g.num_aristas_uu(), 3)  # (1,2) con 3, (2,4) con 2 y (3,5) con 2
        self.assertEqual({(a, b) for a in self.g.adj_mm for b in self.g.adj_mm[a] if a < b},
                         {(1, 2), (1, 5), (2, 5), (1, 8), (3, 6)})
        self.assertEqual(self.g.num_aristas(), 18 + 3 + 5)
        n = self.g.num_nodos()
        self.assertAlmostEqual(self.g.densidad(), 2 * 26 / (n * (n - 1)))

    def test_s_invalido(self):
        with self.assertRaises(ValueError):
            self.g.agregar_aristas_similitud(0)

    def test_simetria(self):
        for u, pelis in self.g.adj_usuario.items():
            for m, w in pelis.items():
                self.assertEqual(self.g.adj_pelicula[m][u], w)


class TestRecomendacion(unittest.TestCase):
    def setUp(self):
        self.g = Grafo.desde_carpeta(MUESTRA)

    def test_bfs_usuario_1(self):
        # Usuario 1 gusta de {1, 2, 5}. Vecinos: 2 (sim 3) y 4 (sim 1, el 5 lo calificó con 3).
        # Única no vista con w >= 4: película 8 -> 3·5 + 1·4 = 19.
        self.assertEqual(candidatos_bfs(self.g, 1), {8: 19.0})

    def test_bfs_no_recomienda_vistas(self):
        for u in self.g.adj_usuario:
            self.assertFalse(set(candidatos_bfs(self.g, u)) & set(self.g.adj_usuario[u]))

    def test_top_k_orden_y_empates(self):
        self.assertEqual(top_k({1: 2.0, 2: 5.0, 3: 5.0, 4: 1.0}, 2), [(2, 5.0), (3, 5.0)])
        self.assertEqual(top_k({}, 3), [])

    def test_bfs_voraz_igual_a_fuerza_bruta(self):
        for u in self.g.adj_usuario:
            esperado = recomendar_fuerza_bruta(self.g, u, k=5)
            obtenido = top_k(candidatos_bfs(self.g, u, max_vecinos=10**9), 5)
            self.assertEqual(obtenido, esperado, f"usuario {u}")


class TestUFDS(unittest.TestCase):
    def test_union_find(self):
        uf = UnionFind(range(5))
        self.assertTrue(uf.union(0, 1))
        self.assertTrue(uf.union(1, 2))
        self.assertFalse(uf.union(0, 2))
        self.assertEqual(uf.componentes, 3)
        self.assertEqual(uf.find(2), uf.find(0))

    def test_clusters_muestra(self):
        g = Grafo.desde_carpeta(MUESTRA)
        g.agregar_aristas_similitud(1)
        # Fans de comedia/infantil {1, 2, 4} vs. fans de thriller {3, 5}; 6 no comparte gustos.
        self.assertEqual(clusterizar_usuarios(g, 3), [[1, 2, 4], [3, 5], [6]])


if __name__ == "__main__":
    unittest.main()
