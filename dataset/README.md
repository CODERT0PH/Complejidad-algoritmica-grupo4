# Dataset: MovieLens 1M

Fuente: GroupLens Research, Universidad de Minnesota.
https://grouplens.org/datasets/movielens/1m/

| Archivo | Formato | Registros |
|---|---|---|
| `users.dat` | `UserID::Gender::Age::Occupation::Zip-code` | 6,040 |
| `movies.dat` | `MovieID::Title::Genres` (géneros separados por `\|`) | 3,883 |
| `ratings.dat` | `UserID::MovieID::Rating::Timestamp` | 1,000,209 |

## Cómo obtenerlo

1. Descargar `ml-1m.zip` desde la página de GroupLens.
2. Descomprimirlo aquí, de modo que quede `dataset/ml-1m/ratings.dat`.

La carpeta `ml-1m/` está en `.gitignore`: la licencia de MovieLens no permite
redistribuir los datos, así que cada integrante lo descarga localmente.

## `muestra/`

Subconjunto sintético pequeño con el mismo formato `::`, usado por las pruebas
y para correr el programa sin descargar nada.
