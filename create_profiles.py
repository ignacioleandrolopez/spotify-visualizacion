from pathlib import Path

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler


# -------------------------------------------------------------------
# CONFIGURACIÓN
# -------------------------------------------------------------------

DIRECTORIO_BASE = Path(__file__).parent

RUTA_CANCIONES = DIRECTORIO_BASE / "data" / "tracks_unique.csv"
RUTA_PERFILES = DIRECTORIO_BASE / "data" / "tracks_profiles.csv"
RUTA_RESUMEN = DIRECTORIO_BASE / "data" / "profile_summary.csv"


VARIABLES_PERFIL = [
    "danceability",
    "energy",
    "valence",
    "acousticness",
    "instrumentalness",
    "speechiness",
    "liveness",
]


# Los nombres se asignan después de interpretar las medias de cada grupo.
NOMBRES_PERFILES = {
    0: "Intenso y oscuro",
    1: "Directo y hablado",
    2: "Acústico y calmado",
    3: "Bailable y positivo",
}


# -------------------------------------------------------------------
# CREACIÓN DE LOS PERFILES
# -------------------------------------------------------------------

def crear_perfiles() -> None:
    """Crea perfiles musicales mediante clustering y guarda los resultados."""

    if not RUTA_CANCIONES.exists():
        raise FileNotFoundError(
            f"No se ha encontrado el archivo: {RUTA_CANCIONES}"
        )

    # Cargar canciones únicas
    df = pd.read_csv(RUTA_CANCIONES)

    # Conservar únicamente canciones con todas las variables necesarias
    df_modelo = df.dropna(
        subset=VARIABLES_PERFIL
    ).copy()

    print(f"Canciones disponibles: {len(df):,}")
    print(f"Canciones utilizadas en el modelo: {len(df_modelo):,}")


    # -------------------------------------------------------------------
    # ESTANDARIZACIÓN
    # -------------------------------------------------------------------

    # La estandarización permite que todas las variables tengan un peso
    # comparable durante la creación de los grupos.
    escalador = StandardScaler()

    datos_escalados = escalador.fit_transform(
        df_modelo[VARIABLES_PERFIL]
    )


    # -------------------------------------------------------------------
    # CLUSTERING K-MEANS
    # -------------------------------------------------------------------

    modelo = KMeans(
        n_clusters=4,
        random_state=42,
        n_init=20,
    )

    df_modelo["profile_id"] = modelo.fit_predict(
        datos_escalados
    )

    df_modelo["profile"] = df_modelo["profile_id"].map(
        NOMBRES_PERFILES
    )


    # -------------------------------------------------------------------
    # REDUCCIÓN DE DIMENSIONALIDAD CON PCA
    # -------------------------------------------------------------------

    # PCA permite representar visualmente las canciones en dos dimensiones.
    pca = PCA(
        n_components=2,
        random_state=42,
    )

    coordenadas = pca.fit_transform(
        datos_escalados
    )

    df_modelo["pca_1"] = coordenadas[:, 0]
    df_modelo["pca_2"] = coordenadas[:, 1]


    # -------------------------------------------------------------------
    # RESUMEN DE CADA PERFIL
    # -------------------------------------------------------------------

    resumen = (
        df_modelo
        .groupby(
            ["profile_id", "profile"],
            as_index=False,
        )
        .agg(
            numero_canciones=("track_id", "count"),
            popularidad_media=("popularity", "mean"),
            popularidad_mediana=("popularity", "median"),
            porcentaje_popularidad_alta=(
                "popularity",
                lambda valores: (valores >= 70).mean() * 100,
            ),
            danceability=("danceability", "mean"),
            energy=("energy", "mean"),
            valence=("valence", "mean"),
            acousticness=("acousticness", "mean"),
            instrumentalness=("instrumentalness", "mean"),
            speechiness=("speechiness", "mean"),
            liveness=("liveness", "mean"),
        )
        .sort_values("profile_id")
        .reset_index(drop=True)
    )


    # -------------------------------------------------------------------
    # EVALUACIÓN DE LOS GRUPOS
    # -------------------------------------------------------------------

    # Utilizamos una muestra aleatoria reproducible para calcular silhouette,
    # evitando que el cálculo sea demasiado lento.
    tamaño_muestra = min(
        10_000,
        len(df_modelo),
    )

    muestra_indices = df_modelo.sample(
        n=tamaño_muestra,
        random_state=42,
    ).index

    posiciones_muestra = df_modelo.index.get_indexer(
        muestra_indices
    )

    puntuacion_silhouette = silhouette_score(
        datos_escalados[posiciones_muestra],
        df_modelo.loc[muestra_indices, "profile_id"],
    )


    # -------------------------------------------------------------------
    # GUARDAR ARCHIVOS
    # -------------------------------------------------------------------

    df_modelo.to_csv(
        RUTA_PERFILES,
        index=False,
    )

    resumen.to_csv(
        RUTA_RESUMEN,
        index=False,
    )


    # -------------------------------------------------------------------
    # MOSTRAR RESULTADOS
    # -------------------------------------------------------------------

    print("\nCreación de perfiles completada")

    print(
        f"Varianza explicada por las dos componentes PCA: "
        f"{pca.explained_variance_ratio_.sum():.3f}"
    )

    print(
        f"Puntuación silhouette: "
        f"{puntuacion_silhouette:.3f}"
    )


    print("\nResumen de perfiles:")

    print(
        resumen[
            [
                "profile",
                "numero_canciones",
                "popularidad_media",
                "porcentaje_popularidad_alta",
            ]
        ]
        .round(3)
        .to_string(index=False)
    )


    print("\nCaracterísticas medias de cada perfil:")

    print(
        resumen[
            [
                "profile",
                "danceability",
                "energy",
                "valence",
                "acousticness",
                "instrumentalness",
                "speechiness",
                "liveness",
            ]
        ]
        .round(3)
        .to_string(index=False)
    )


    print(f"\nArchivo creado: {RUTA_PERFILES}")
    print(f"Archivo creado: {RUTA_RESUMEN}")


if __name__ == "__main__":
    crear_perfiles()

