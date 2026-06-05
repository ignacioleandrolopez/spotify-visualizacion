from pathlib import Path

import pandas as pd


RUTA_ORIGINAL = Path("data") / "Spotify Tracks Dataset.csv"
RUTA_LIMPIO = Path("data") / "tracks_clean.csv"
RUTA_UNICAS = Path("data") / "tracks_unique.csv"


def preparar_datos() -> None:
    if not RUTA_ORIGINAL.exists():
        raise FileNotFoundError(
            f"No se ha encontrado el archivo original: {RUTA_ORIGINAL}"
        )

    # Cargar el conjunto original
    df = pd.read_csv(RUTA_ORIGINAL)

    print(f"Filas originales: {len(df):,}")
    print(f"Columnas originales: {df.shape[1]}")

    # Eliminar la columna de índice creada al exportar el CSV
    df = df.drop(columns=["Unnamed: 0"], errors="ignore")

    # Eliminar filas sin información básica de la canción
    df = df.dropna(
        subset=["track_id", "track_name", "artists", "popularity"]
    )

    # Eliminar filas completamente duplicadas
    df = df.drop_duplicates()

    # Convertir la duración de milisegundos a minutos
    df["duration_min"] = df["duration_ms"] / 60_000

    # Crear grupos interpretables de popularidad
    df["popularity_group"] = pd.cut(
        df["popularity"],
        bins=[-1, 30, 69, 100],
        labels=["Baja", "Media", "Alta"],
        ordered=True,
    )

    # Índice descriptivo de dinamismo
    df["dynamic_index"] = (
        df["danceability"] +
        df["energy"] +
        df["valence"]
    ) / 3

    # Dataset completo para estudiar géneros
    df.to_csv(RUTA_LIMPIO, index=False)

    # Dataset con una única fila por canción
    df_unique = df.drop_duplicates(
        subset=["track_id"],
        keep="first",
    ).copy()

    df_unique.to_csv(RUTA_UNICAS, index=False)

    print("\nPreparación completada")
    print(f"Filas del dataset limpio: {len(df):,}")
    print(f"Canciones únicas: {len(df_unique):,}")
    print(f"Columnas finales: {df.shape[1]}")
    print("\nDistribución por nivel de popularidad:")
    print(df_unique["popularity_group"].value_counts().sort_index())
    print(f"\nArchivo creado: {RUTA_LIMPIO}")
    print(f"Archivo creado: {RUTA_UNICAS}")


if __name__ == "__main__":
    preparar_datos()