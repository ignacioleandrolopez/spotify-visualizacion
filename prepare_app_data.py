from pathlib import Path

import pandas as pd


DIRECTORIO_BASE = Path(__file__).parent
DIRECTORIO_DATOS = DIRECTORIO_BASE / "data"
DIRECTORIO_APP = DIRECTORIO_DATOS / "app"

RUTA_CANCIONES_UNICAS = DIRECTORIO_DATOS / "tracks_unique.csv"
RUTA_CANCIONES_GENEROS = DIRECTORIO_DATOS / "tracks_clean.csv"
RUTA_PERFILES = DIRECTORIO_DATOS / "tracks_profiles.csv"


VARIABLES_MUSICALES = [
    "danceability",
    "energy",
    "valence",
    "acousticness",
    "instrumentalness",
    "speechiness",
    "liveness",
    "loudness",
    "tempo",
    "dynamic_index",
]

VARIABLES_PERFIL = [
    "danceability",
    "energy",
    "valence",
    "acousticness",
    "instrumentalness",
    "speechiness",
    "liveness",
]


def tamaño_mb(ruta: Path) -> float:
    """Devuelve el tamaño de un archivo en megabytes."""
    return ruta.stat().st_size / (1024 * 1024)


def preparar_datos_app() -> None:
    """Genera archivos reducidos específicamente para la aplicación."""

    rutas_necesarias = [
        RUTA_CANCIONES_UNICAS,
        RUTA_CANCIONES_GENEROS,
        RUTA_PERFILES,
    ]

    for ruta in rutas_necesarias:
        if not ruta.exists():
            raise FileNotFoundError(
                f"No se ha encontrado el archivo necesario: {ruta}"
            )

    DIRECTORIO_APP.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ---------------------------------------------------------------
    # 1. CANCIONES ÚNICAS REDUCIDAS
    # ---------------------------------------------------------------

    columnas_canciones = [
        "track_name",
        "artists",
        "popularity",
        "popularity_group",
    ] + VARIABLES_MUSICALES

    canciones_unicas = pd.read_csv(
        RUTA_CANCIONES_UNICAS,
        usecols=columnas_canciones,
    )

    columnas_decimales = [
        columna
        for columna in VARIABLES_MUSICALES
        if columna != "tempo"
    ]

    canciones_unicas[columnas_decimales] = (
        canciones_unicas[columnas_decimales].round(4)
    )

    canciones_unicas["tempo"] = canciones_unicas["tempo"].round(2)

    ruta_canciones_app = (
        DIRECTORIO_APP / "tracks_unique_app.csv"
    )

    canciones_unicas.to_csv(
        ruta_canciones_app,
        index=False,
    )

    # ---------------------------------------------------------------
    # 2. RESUMEN DE POPULARIDAD POR GÉNERO
    # ---------------------------------------------------------------

    columnas_generos = [
        "track_genre",
        "track_id",
        "popularity",
    ] + VARIABLES_PERFIL

    canciones_generos = pd.read_csv(
        RUTA_CANCIONES_GENEROS,
        usecols=columnas_generos,
    )

    resumen_generos = (
        canciones_generos
        .groupby("track_genre")
        .agg(
            popularidad_media=("popularity", "mean"),
            popularidad_mediana=("popularity", "median"),
            numero_canciones=("track_id", "nunique"),
        )
        .reset_index()
    )

    resumen_generos[
        ["popularidad_media", "popularidad_mediana"]
    ] = resumen_generos[
        ["popularidad_media", "popularidad_mediana"]
    ].round(3)

    ruta_resumen_generos = (
        DIRECTORIO_APP / "genres_summary_app.csv"
    )

    resumen_generos.to_csv(
        ruta_resumen_generos,
        index=False,
    )

    # ---------------------------------------------------------------
    # 3. PERFIL MUSICAL MEDIO DE CADA GÉNERO
    # ---------------------------------------------------------------

    perfiles_generos = (
        canciones_generos
        .groupby("track_genre")[VARIABLES_PERFIL]
        .mean()
        .round(4)
        .reset_index()
    )

    ruta_perfiles_generos = (
        DIRECTORIO_APP / "genres_profiles_app.csv"
    )

    perfiles_generos.to_csv(
        ruta_perfiles_generos,
        index=False,
    )

    # ---------------------------------------------------------------
    # 4. MUESTRA REDUCIDA PARA EL GRÁFICO PCA
    # ---------------------------------------------------------------

    columnas_perfiles = [
        "track_name",
        "artists",
        "profile",
        "popularity",
        "pca_1",
        "pca_2",
    ]

    perfiles = pd.read_csv(
        RUTA_PERFILES,
        usecols=columnas_perfiles,
    )

    muestra_perfiles = perfiles.sample(
        n=min(4_000, len(perfiles)),
        random_state=42,
    ).copy()

    muestra_perfiles[["pca_1", "pca_2"]] = (
        muestra_perfiles[["pca_1", "pca_2"]].round(4)
    )

    ruta_muestra_perfiles = (
        DIRECTORIO_APP / "profiles_sample_app.csv"
    )

    muestra_perfiles.to_csv(
        ruta_muestra_perfiles,
        index=False,
    )

    # ---------------------------------------------------------------
    # RESULTADOS
    # ---------------------------------------------------------------

    archivos_creados = [
        ruta_canciones_app,
        ruta_resumen_generos,
        ruta_perfiles_generos,
        ruta_muestra_perfiles,
    ]

    print("Archivos optimizados creados correctamente:\n")

    tamaño_total = 0

    for ruta in archivos_creados:
        tamaño = tamaño_mb(ruta)
        tamaño_total += tamaño

        print(
            f"- {ruta.name}: "
            f"{tamaño:.2f} MB"
        )

    print(
        f"\nTamaño total de los archivos optimizados: "
        f"{tamaño_total:.2f} MB"
    )


if __name__ == "__main__":
    preparar_datos_app()