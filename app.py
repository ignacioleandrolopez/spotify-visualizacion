from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st


# Configuración general de la página
st.set_page_config(
    page_title="Spotify: fórmula del éxito",
    page_icon="🎵",
    layout="wide",
)


# Rutas construidas desde la ubicación de app.py
DIRECTORIO_BASE = Path(__file__).parent
DIRECTORIO_DATOS_APP = DIRECTORIO_BASE / "data" / "app"

RUTA_CANCIONES_UNICAS = (
    DIRECTORIO_DATOS_APP / "tracks_unique_app.csv"
)

RUTA_RESUMEN_GENEROS = (
    DIRECTORIO_DATOS_APP / "genres_summary_app.csv"
)

RUTA_PERFILES_GENEROS = (
    DIRECTORIO_DATOS_APP / "genres_profiles_app.csv"
)

RUTA_MUESTRA_PERFILES = (
    DIRECTORIO_DATOS_APP / "profiles_sample_app.csv"
)

RUTA_RESUMEN_PERFILES = (
    DIRECTORIO_BASE / "data" / "profile_summary.csv"
)

@st.cache_data
def cargar_datos() -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
]:
    """Carga los archivos optimizados utilizados por la aplicación."""

    rutas = [
        RUTA_CANCIONES_UNICAS,
        RUTA_RESUMEN_GENEROS,
        RUTA_PERFILES_GENEROS,
        RUTA_MUESTRA_PERFILES,
        RUTA_RESUMEN_PERFILES,
    ]

    for ruta in rutas:
        if not ruta.exists():
            raise FileNotFoundError(
                f"No se ha encontrado el archivo: {ruta}"
            )

    canciones_unicas = pd.read_csv(RUTA_CANCIONES_UNICAS)
    resumen_generos = pd.read_csv(RUTA_RESUMEN_GENEROS)
    perfiles_generos = pd.read_csv(RUTA_PERFILES_GENEROS)
    muestra_perfiles = pd.read_csv(RUTA_MUESTRA_PERFILES)
    resumen_perfiles = pd.read_csv(RUTA_RESUMEN_PERFILES)

    return (
        canciones_unicas,
        resumen_generos,
        perfiles_generos,
        muestra_perfiles,
        resumen_perfiles,
    )
try:
    (
        df,
        resumen_generos,
        perfiles_generos,
        muestra_perfiles,
        resumen_perfiles,
    ) = cargar_datos()

except FileNotFoundError as error:
    st.error(str(error))
    st.stop()


# -------------------------------------------------------------------
# PORTADA
# -------------------------------------------------------------------

st.title("¿Existe una fórmula del éxito musical en Spotify?")

st.markdown(
    """
    **Una exploración interactiva sobre los rasgos musicales, los géneros
    y los distintos perfiles que caracterizan a las canciones populares.**

    El objetivo no es encontrar una receta infalible, sino comprobar si las
    canciones más populares presentan patrones musicales diferenciados.
    """
)

st.divider()


# -------------------------------------------------------------------
# SECCIÓN 1: DISTRIBUCIÓN DE LA POPULARIDAD
# -------------------------------------------------------------------

st.header("1. Alcanzar una popularidad alta es excepcional")

st.write(
    """
    Spotify asigna a cada canción una puntuación de popularidad entre 0 y 100.
    Utiliza el control para decidir a partir de qué puntuación considerarías
    que una canción tiene una popularidad alta.
    """
)

umbral_popularidad = st.slider(
    "Umbral de popularidad alta",
    min_value=50,
    max_value=90,
    value=70,
    step=1,
)


# Cálculos asociados al umbral seleccionado
numero_populares = int((df["popularity"] >= umbral_popularidad).sum())
porcentaje_populares = numero_populares / len(df) * 100
popularidad_mediana = df["popularity"].median()


columna1, columna2, columna3 = st.columns(3)

columna1.metric(
    "Canciones analizadas",
    f"{len(df):,}".replace(",", "."),
)

columna2.metric(
    f"Canciones con popularidad ≥ {umbral_popularidad}",
    f"{numero_populares:,}".replace(",", "."),
)

columna3.metric(
    "Porcentaje sobre el total",
    f"{porcentaje_populares:.1f} %",
)


# Agregamos previamente los datos para evitar enviar 89.740 filas al gráfico
distribucion = (
    df["popularity"]
    .value_counts()
    .sort_index()
    .rename_axis("popularidad")
    .reset_index(name="numero_canciones")
)

distribucion["grupo"] = distribucion["popularidad"].apply(
    lambda valor: (
        "Popularidad alta"
        if valor >= umbral_popularidad
        else "Resto de canciones"
    )
)


grafico_distribucion = (
    alt.Chart(distribucion)
    .mark_bar()
    .encode(
        x=alt.X(
            "popularidad:Q",
            title="Puntuación de popularidad",
            scale=alt.Scale(domain=[0, 100]),
        ),
        y=alt.Y(
            "numero_canciones:Q",
            title="Número de canciones",
        ),
        color=alt.Color(
            "grupo:N",
            title="Clasificación",
            scale=alt.Scale(
                domain=["Resto de canciones", "Popularidad alta"],
                range=["#9E9E9E", "#1DB954"],
            ),
        ),
        tooltip=[
            alt.Tooltip("popularidad:Q", title="Popularidad"),
            alt.Tooltip(
                "numero_canciones:Q",
                title="Número de canciones",
                format=",",
            ),
        ],
    )
    .properties(
        title="Distribución de la popularidad de las canciones",
        height=420,
    )
)


st.altair_chart(
    grafico_distribucion,
    use_container_width=True,
)


st.info(
    f"""
    Con un umbral de **{umbral_popularidad} puntos**, solamente
    **{porcentaje_populares:.1f} %** de las canciones alcanza una popularidad
    alta. La mediana del conjunto es de **{popularidad_mediana:.0f} puntos**.
    """
)
# -------------------------------------------------------------------
# SECCIÓN 2: RELACIÓN ENTRE CARACTERÍSTICAS Y POPULARIDAD
# -------------------------------------------------------------------

st.divider()

st.header("2. No existe una variable musical mágica")

st.write(
    """
    Una posible explicación del éxito sería que las canciones más bailables,
    energéticas o positivas fueran también las más populares.

    Para comprobarlo, analizamos la correlación lineal entre la popularidad
    y distintas características musicales. Una correlación próxima a cero
    indica que la variable, por sí sola, no explica bien la popularidad.
    """
)


# Variables musicales que queremos analizar
variables_musicales = [
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


# Nombres legibles para mostrar en la aplicación
nombres_variables = {
    "danceability": "Bailabilidad",
    "energy": "Energía",
    "valence": "Positividad emocional",
    "acousticness": "Carácter acústico",
    "instrumentalness": "Carácter instrumental",
    "speechiness": "Presencia de palabra hablada",
    "liveness": "Probabilidad de interpretación en directo",
    "loudness": "Volumen",
    "tempo": "Tempo",
    "dynamic_index": "Índice de dinamismo",
}


# Calcular correlaciones con popularidad
correlaciones = (
    df[variables_musicales + ["popularity"]]
    .corr(numeric_only=True)["popularity"]
    .drop("popularity")
    .reset_index()
)

correlaciones.columns = ["variable", "correlacion"]

correlaciones["caracteristica"] = correlaciones["variable"].map(
    nombres_variables
)

correlaciones["tipo_relacion"] = correlaciones["correlacion"].apply(
    lambda valor: (
        "Relación positiva"
        if valor >= 0
        else "Relación negativa"
    )
)


grafico_correlaciones = (
    alt.Chart(correlaciones)
    .mark_bar()
    .encode(
        x=alt.X(
            "correlacion:Q",
            title="Correlación con la popularidad",
            scale=alt.Scale(domain=[-0.15, 0.15]),
        ),
        y=alt.Y(
            "caracteristica:N",
            title=None,
            sort="-x",
        ),
        color=alt.Color(
            "tipo_relacion:N",
            title="Dirección de la relación",
            scale=alt.Scale(
                domain=["Relación negativa", "Relación positiva"],
                range=["#D55E00", "#0072B2"],
            ),
        ),
        tooltip=[
            alt.Tooltip("caracteristica:N", title="Característica"),
            alt.Tooltip(
                "correlacion:Q",
                title="Correlación",
                format=".3f",
            ),
        ],
    )
    .properties(
        title="Correlación entre las características musicales y la popularidad",
        height=420,
    )
)


st.altair_chart(
    grafico_correlaciones,
    use_container_width=True,
)


correlacion_maxima = correlaciones.loc[
    correlaciones["correlacion"].abs().idxmax()
]

st.info(
    f"""
    La relación de mayor intensidad corresponde a
    **{correlacion_maxima["caracteristica"]}**, con una correlación de
    **{correlacion_maxima["correlacion"]:.3f}**.

    Como todas las correlaciones son próximas a cero, ninguna característica
    musical individual parece explicar por sí sola la popularidad.
    """
)


# -------------------------------------------------------------------
# EXPLORACIÓN INTERACTIVA DE UNA VARIABLE
# -------------------------------------------------------------------

st.subheader("Explora una característica musical")

variable_seleccionada = st.selectbox(
    "Selecciona la característica que quieres comparar con la popularidad",
    options=variables_musicales,
    format_func=lambda variable: nombres_variables[variable],
)


# Utilizamos una muestra reproducible para evitar sobrecargar el navegador
numero_muestra = min(5_000, len(df))

muestra = df[
    [
        "track_name",
        "artists",
        "popularity",
        variable_seleccionada,
    ]
].dropna()

muestra = muestra.sample(
    n=min(numero_muestra, len(muestra)),
    random_state=42,
)


grafico_dispersion = (
    alt.Chart(muestra)
    .mark_circle(
        opacity=0.25,
        size=35,
    )
    .encode(
        x=alt.X(
            f"{variable_seleccionada}:Q",
            title=nombres_variables[variable_seleccionada],
        ),
        y=alt.Y(
            "popularity:Q",
            title="Popularidad",
            scale=alt.Scale(domain=[0, 100]),
        ),
        tooltip=[
            alt.Tooltip("track_name:N", title="Canción"),
            alt.Tooltip("artists:N", title="Artista"),
            alt.Tooltip("popularity:Q", title="Popularidad"),
            alt.Tooltip(
                f"{variable_seleccionada}:Q",
                title=nombres_variables[variable_seleccionada],
                format=".3f",
            ),
        ],
    )
    .properties(
        title=(
            f"Popularidad frente a "
            f"{nombres_variables[variable_seleccionada].lower()}"
        ),
        height=450,
    )
)


linea_tendencia = (
    alt.Chart(muestra)
    .transform_regression(
        variable_seleccionada,
        "popularity",
    )
    .mark_line(
        color="#D55E00",
        size=3,
    )
    .encode(
        x=f"{variable_seleccionada}:Q",
        y="popularity:Q",
    )
)


st.altair_chart(
    grafico_dispersion + linea_tendencia,
    use_container_width=True,
)


correlacion_seleccionada = correlaciones.loc[
    correlaciones["variable"] == variable_seleccionada,
    "correlacion",
].iloc[0]


st.caption(
    f"""
    Correlación entre {nombres_variables[variable_seleccionada].lower()}
    y popularidad: **{correlacion_seleccionada:.3f}**.
    Cada punto representa una canción de una muestra reproducible de hasta
    5.000 canciones.
    """
)

# -------------------------------------------------------------------
# SECCIÓN 3: DIFERENCIAS ENTRE CANCIONES POPULARES Y POCO POPULARES
# -------------------------------------------------------------------

st.divider()

st.header("3. Las canciones populares sí presentan algunos rasgos frecuentes")

st.write(
    """
    Que ninguna variable explique individualmente la popularidad no significa
    que todas las canciones tengan perfiles idénticos.

    En esta sección comparamos las canciones de popularidad baja —entre 0 y
    30 puntos— con aquellas de popularidad alta —entre 70 y 100 puntos—.
    """
)


variables_comparacion = [
    "danceability",
    "energy",
    "valence",
    "acousticness",
    "instrumentalness",
    "speechiness",
    "liveness",
    "dynamic_index",
]


# Seleccionar únicamente los grupos extremos
df_extremos = df[
    df["popularity_group"].isin(["Baja", "Alta"])
].copy()


# Calcular la media de cada característica por grupo
medias_grupos = (
    df_extremos
    .groupby("popularity_group")[variables_comparacion]
    .mean()
)


# Diferencia entre la media del grupo alto y la del grupo bajo
diferencias = pd.DataFrame(
    {
        "variable": variables_comparacion,
        "media_baja": [
            medias_grupos.loc["Baja", variable]
            for variable in variables_comparacion
        ],
        "media_alta": [
            medias_grupos.loc["Alta", variable]
            for variable in variables_comparacion
        ],
    }
)

diferencias["diferencia"] = (
    diferencias["media_alta"] - diferencias["media_baja"]
)

diferencias["caracteristica"] = diferencias["variable"].map(
    nombres_variables
)

diferencias["direccion"] = diferencias["diferencia"].apply(
    lambda valor: (
        "Mayor en canciones populares"
        if valor >= 0
        else "Menor en canciones populares"
    )
)


grafico_diferencias = (
    alt.Chart(diferencias)
    .mark_bar()
    .encode(
        x=alt.X(
            "diferencia:Q",
            title="Diferencia media: popularidad alta − popularidad baja",
        ),
        y=alt.Y(
            "caracteristica:N",
            title=None,
            sort="-x",
            axis=alt.Axis(labelLimit=300),
        ),
        color=alt.Color(
            "direccion:N",
            title=None,
            scale=alt.Scale(
                domain=[
                    "Mayor en canciones populares",
                    "Menor en canciones populares",
                ],
                range=["#0072B2", "#D55E00"],
            ),
        ),
        tooltip=[
            alt.Tooltip(
                "caracteristica:N",
                title="Característica",
            ),
            alt.Tooltip(
                "media_baja:Q",
                title="Media: popularidad baja",
                format=".3f",
            ),
            alt.Tooltip(
                "media_alta:Q",
                title="Media: popularidad alta",
                format=".3f",
            ),
            alt.Tooltip(
                "diferencia:Q",
                title="Diferencia",
                format=".3f",
            ),
        ],
    )
    .properties(
        title="Diferencias entre canciones de popularidad alta y baja",
        height=420,
    )
)


st.altair_chart(
    grafico_diferencias,
    use_container_width=True,
)


mayor_aumento = diferencias.loc[
    diferencias["diferencia"].idxmax()
]

mayor_descenso = diferencias.loc[
    diferencias["diferencia"].idxmin()
]


st.info(
    f"""
    Las canciones populares presentan especialmente una mayor
    **{mayor_aumento["caracteristica"].lower()}**, con una diferencia media
    de **{mayor_aumento["diferencia"]:.3f}**.

    La mayor diferencia negativa aparece en
    **{mayor_descenso["caracteristica"].lower()}**, cuya media es
    **{abs(mayor_descenso["diferencia"]):.3f} puntos inferior**
    entre las canciones populares.
    """
)


# -------------------------------------------------------------------
# EXPLORACIÓN INTERACTIVA DE DISTRIBUCIONES
# -------------------------------------------------------------------

st.subheader("Compara la distribución de una característica")

variable_distribucion = st.selectbox(
    "Selecciona una característica para comparar ambos grupos",
    options=variables_comparacion,
    format_func=lambda variable: nombres_variables[variable],
    key="selector_distribucion",
)


# Muestra equilibrada para mantener el rendimiento
muestras_grupos = []

for grupo in ["Baja", "Alta"]:
    subconjunto = df_extremos[
        df_extremos["popularity_group"] == grupo
    ][
        [
            "track_name",
            "artists",
            "popularity_group",
            variable_distribucion,
        ]
    ].dropna()

    muestras_grupos.append(
        subconjunto.sample(
            n=min(2_000, len(subconjunto)),
            random_state=42,
        )
    )


muestra_boxplot = pd.concat(
    muestras_grupos,
    ignore_index=True,
)


grafico_boxplot = (
    alt.Chart(muestra_boxplot)
    .mark_boxplot(size=80)
    .encode(
        x=alt.X(
            "popularity_group:N",
            title="Nivel de popularidad",
            sort=["Baja", "Alta"],
        ),
        y=alt.Y(
            f"{variable_distribucion}:Q",
            title=nombres_variables[variable_distribucion],
        ),
        color=alt.Color(
            "popularity_group:N",
            title="Nivel de popularidad",
            scale=alt.Scale(
                domain=["Baja", "Alta"],
                range=["#9E9E9E", "#1DB954"],
            ),
        ),
    )
    .properties(
        title=(
            f"Distribución de "
            f"{nombres_variables[variable_distribucion].lower()}"
        ),
        height=430,
    )
)


st.altair_chart(
    grafico_boxplot,
    use_container_width=True,
)


st.caption(
    """
    Los diagramas muestran la mediana, los cuartiles y los valores extremos
    de una muestra equilibrada de canciones con popularidad baja y alta.
    Las diferencias observadas describen patrones frecuentes, pero no implican
    que estas características causen directamente la popularidad.
    """
)
# -------------------------------------------------------------------
# SECCIÓN 4: INFLUENCIA DEL GÉNERO MUSICAL
# -------------------------------------------------------------------

st.divider()

st.header("4. El género musical cambia las reglas")

st.write(
    """
    Las características de una canción no tienen el mismo significado en
    todos los géneros. Una energía baja puede ser habitual en música clásica,
    mientras que sería menos frecuente en géneros orientados al baile.

    Por ello, resulta necesario analizar la popularidad dentro de su contexto
    musical y no solamente mediante comparaciones globales.
    """
)


# -------------------------------------------------------------------
# POPULARIDAD MEDIA POR GÉNERO
# -------------------------------------------------------------------



numero_generos_mostrar = st.slider(
    "Número de géneros que quieres mostrar",
    min_value=5,
    max_value=30,
    value=15,
    step=1,
)


criterio_orden = st.radio(
    "Ordenar los géneros por:",
    options=[
        "Mayor popularidad media",
        "Menor popularidad media",
    ],
    horizontal=True,
)


if criterio_orden == "Mayor popularidad media":
    resumen_seleccionado = resumen_generos.nlargest(
        numero_generos_mostrar,
        "popularidad_media",
    )

    orden_grafico = "-x"

else:
    resumen_seleccionado = resumen_generos.nsmallest(
        numero_generos_mostrar,
        "popularidad_media",
    )

    orden_grafico = "x"


grafico_generos = (
    alt.Chart(resumen_seleccionado)
    .mark_bar(
        cornerRadiusEnd=3,
    )
    .encode(
        x=alt.X(
            "popularidad_media:Q",
            title="Popularidad media",
            scale=alt.Scale(domain=[0, 100]),
        ),
        y=alt.Y(
            "track_genre:N",
            title="Género musical",
            sort=orden_grafico,
            axis=alt.Axis(labelLimit=250),
        ),
        color=alt.Color(
            "popularidad_media:Q",
            title="Popularidad media",
            scale=alt.Scale(
                scheme="viridis",
                domain=[0, 100],
            ),
        ),
        tooltip=[
            alt.Tooltip(
                "track_genre:N",
                title="Género",
            ),
            alt.Tooltip(
                "popularidad_media:Q",
                title="Popularidad media",
                format=".1f",
            ),
            alt.Tooltip(
                "popularidad_mediana:Q",
                title="Popularidad mediana",
                format=".1f",
            ),
            alt.Tooltip(
                "numero_canciones:Q",
                title="Canciones únicas",
                format=",",
            ),
        ],
    )
    .properties(
        title="Diferencias de popularidad entre géneros musicales",
        height=500,
    )
)


st.altair_chart(
    grafico_generos,
    use_container_width=True,
)


genero_mayor_popularidad = resumen_generos.loc[
    resumen_generos["popularidad_media"].idxmax()
]

genero_menor_popularidad = resumen_generos.loc[
    resumen_generos["popularidad_media"].idxmin()
]


st.info(
    f"""
    El género con mayor popularidad media es
    **{genero_mayor_popularidad["track_genre"]}**, con
    **{genero_mayor_popularidad["popularidad_media"]:.1f} puntos**.

    En el extremo opuesto se encuentra
    **{genero_menor_popularidad["track_genre"]}**, con
    **{genero_menor_popularidad["popularidad_media"]:.1f} puntos**.

    Esta diferencia indica que el género condiciona fuertemente cualquier
    comparación global de popularidad.
    """
)


# -------------------------------------------------------------------
# COMPARACIÓN INTERACTIVA ENTRE DOS GÉNEROS
# -------------------------------------------------------------------

st.subheader("Compara el perfil musical de dos géneros")


lista_generos = sorted(
    perfiles_generos["track_genre"]
    .dropna()
    .unique()
)

columna_genero1, columna_genero2 = st.columns(2)


with columna_genero1:
    genero_1 = st.selectbox(
        "Primer género",
        options=lista_generos,
        index=(
            lista_generos.index("pop")
            if "pop" in lista_generos
            else 0
        ),
        key="genero_1",
    )


with columna_genero2:
    genero_2 = st.selectbox(
        "Segundo género",
        options=lista_generos,
        index=(
            lista_generos.index("classical")
            if "classical" in lista_generos
            else 1
        ),
        key="genero_2",
    )


variables_perfil = [
    "danceability",
    "energy",
    "valence",
    "acousticness",
    "instrumentalness",
    "speechiness",
    "liveness",
]


datos_comparacion_generos = (
    perfiles_generos[
        perfiles_generos["track_genre"].isin(
            [genero_1, genero_2]
        )
    ]
    .melt(
        id_vars="track_genre",
        value_vars=variables_perfil,
        var_name="variable",
        value_name="media",
    )
)


datos_comparacion_generos["caracteristica"] = (
    datos_comparacion_generos["variable"].map(nombres_variables)
)


orden_caracteristicas = [
    nombres_variables[variable]
    for variable in variables_perfil
]


if genero_1 == genero_2:
    st.warning(
        "Selecciona dos géneros diferentes para poder compararlos."
    )

else:
    grafico_comparacion_generos = (
        alt.Chart(datos_comparacion_generos)
        .mark_bar(
            cornerRadiusEnd=3,
        )
        .encode(
            x=alt.X(
                "media:Q",
                title="Valor medio",
                scale=alt.Scale(domain=[0, 1]),
            ),
            y=alt.Y(
                "caracteristica:N",
                title=None,
                sort=orden_caracteristicas,
                axis=alt.Axis(labelLimit=320),
            ),
            yOffset=alt.YOffset(
                "track_genre:N",
                sort=[genero_1, genero_2],
            ),
            color=alt.Color(
                "track_genre:N",
                title="Género musical",
                scale=alt.Scale(
                    domain=[genero_1, genero_2],
                    range=["#0072B2", "#E69F00"],
                ),
            ),
            tooltip=[
                alt.Tooltip(
                    "track_genre:N",
                    title="Género",
                ),
                alt.Tooltip(
                    "caracteristica:N",
                    title="Característica",
                ),
                alt.Tooltip(
                    "media:Q",
                    title="Valor medio",
                    format=".3f",
                ),
            ],
        )
        .properties(
            title=(
                f"Comparación del perfil musical: "
                f"{genero_1} frente a {genero_2}"
            ),
            height=480,
        )
        .configure_view(
            strokeWidth=0,
        )
    )


    st.altair_chart(
        grafico_comparacion_generos,
        use_container_width=True,
    )


st.caption(
    """
    Las diferencias entre géneros muestran que una característica musical
    debe interpretarse dentro de su contexto. La popularidad no depende
    únicamente de los atributos de audio, sino también del tipo de música
    al que pertenece la canción.
    """
)
# -------------------------------------------------------------------
# SECCIÓN 5: PERFILES MUSICALES
# -------------------------------------------------------------------

st.divider()

st.header("5. Existen distintos caminos musicales hacia la popularidad")

st.write(
    """
    Para identificar combinaciones habituales de características musicales,
    agrupamos las canciones mediante un modelo de clustering K-Means.

    El modelo no utiliza el género ni la popularidad para formar los grupos:
    únicamente analiza sus características sonoras. Después, comparamos la
    popularidad alcanzada por cada perfil.
    """
)


# Colores constantes y accesibles para cada perfil
orden_perfiles = [
    "Acústico y calmado",
    "Bailable y positivo",
    "Directo y hablado",
    "Intenso y oscuro",
]

colores_perfiles = [
    "#0072B2",  # Azul
    "#009E73",  # Verde
    "#E69F00",  # Naranja
    "#CC79A7",  # Rosa
]

mapa_colores_perfiles = dict(
    zip(orden_perfiles, colores_perfiles)
)

# Fijar el orden de los perfiles en el dataframe
resumen_perfiles["profile"] = pd.Categorical(
    resumen_perfiles["profile"],
    categories=orden_perfiles,
    ordered=True,
)

resumen_perfiles = resumen_perfiles.sort_values("profile")


# -------------------------------------------------------------------
# POPULARIDAD DE LOS PERFILES
# -------------------------------------------------------------------

grafico_popularidad_perfiles = (
    alt.Chart(resumen_perfiles)
    .mark_bar(
        cornerRadiusEnd=4,
    )
    .encode(
        x=alt.X(
            "popularidad_media:Q",
            title="Popularidad media",
            scale=alt.Scale(domain=[0, 45]),
        ),
        y=alt.Y(
            "profile:N",
            title=None,
            sort=orden_perfiles,
            axis=alt.Axis(labelLimit=300),
        ),
        color=alt.Color(
            "profile:N",
            title="Perfil musical",
            sort=orden_perfiles,
            scale=alt.Scale(
                domain=orden_perfiles,
                range=colores_perfiles,
            ),
        ),
        tooltip=[
            alt.Tooltip("profile:N", title="Perfil"),
            alt.Tooltip(
                "numero_canciones:Q",
                title="Número de canciones",
                format=",",
            ),
            alt.Tooltip(
                "popularidad_media:Q",
                title="Popularidad media",
                format=".2f",
            ),
            alt.Tooltip(
                "porcentaje_popularidad_alta:Q",
                title="% con popularidad ≥ 70",
                format=".2f",
            ),
        ],
    )
    .properties(
        title="Popularidad media de cada perfil musical",
        height=350,
    )
)

st.altair_chart(
    grafico_popularidad_perfiles,
    use_container_width=True,
)


perfil_mas_popular = resumen_perfiles.loc[
    resumen_perfiles["porcentaje_popularidad_alta"].idxmax()
]

perfil_menos_popular = resumen_perfiles.loc[
    resumen_perfiles["porcentaje_popularidad_alta"].idxmin()
]


st.info(
    f"""
    El perfil **{perfil_mas_popular["profile"]}** presenta la mayor proporción
    de canciones con popularidad alta:
    **{perfil_mas_popular["porcentaje_popularidad_alta"]:.2f} %**.

    El perfil **{perfil_menos_popular["profile"]}** presenta la proporción
    más baja:
    **{perfil_menos_popular["porcentaje_popularidad_alta"]:.2f} %**.

    Incluso dentro del perfil más favorable, las canciones altamente
    populares continúan siendo una minoría.
    """
)


# -------------------------------------------------------------------
# EXPLORACIÓN DE UN PERFIL
# -------------------------------------------------------------------

st.subheader("Explora las características de cada perfil")


perfiles_disponibles = resumen_perfiles["profile"].tolist()

lista_perfiles = [
    perfil
    for perfil in orden_perfiles
    if perfil in resumen_perfiles["profile"].astype(str).tolist()
]


perfil_seleccionado = st.selectbox(
    "Selecciona un perfil musical",
    options=lista_perfiles,
    key="perfil_seleccionado",
)


fila_perfil = resumen_perfiles[
    resumen_perfiles["profile"] == perfil_seleccionado
].iloc[0]


columna1, columna2, columna3 = st.columns(3)

columna1.metric(
    "Canciones del perfil",
    f"{int(fila_perfil['numero_canciones']):,}".replace(",", "."),
)

columna2.metric(
    "Popularidad media",
    f"{fila_perfil['popularidad_media']:.2f}",
)

columna3.metric(
    "Canciones con popularidad ≥ 70",
    f"{fila_perfil['porcentaje_popularidad_alta']:.2f} %",
)


variables_perfiles = [
    "danceability",
    "energy",
    "valence",
    "acousticness",
    "instrumentalness",
    "speechiness",
    "liveness",
]


datos_perfil = (
    resumen_perfiles[
        resumen_perfiles["profile"] == perfil_seleccionado
    ][variables_perfiles]
    .melt(
        var_name="variable",
        value_name="media",
    )
)


datos_perfil["caracteristica"] = datos_perfil["variable"].map(
    nombres_variables
)


orden_caracteristicas_perfiles = [
    nombres_variables[variable]
    for variable in variables_perfiles
]


color_perfil_seleccionado = mapa_colores_perfiles[
    perfil_seleccionado
]

grafico_perfil = (
    alt.Chart(datos_perfil)
    .mark_bar(
        cornerRadiusEnd=4,
        color=color_perfil_seleccionado,
    )
    .encode(
        x=alt.X(
            "media:Q",
            title="Valor medio",
            scale=alt.Scale(domain=[0, 1]),
        ),
        y=alt.Y(
            "caracteristica:N",
            title=None,
            sort=orden_caracteristicas_perfiles,
            axis=alt.Axis(labelLimit=320),
        ),
        tooltip=[
            alt.Tooltip(
                "caracteristica:N",
                title="Característica",
            ),
            alt.Tooltip(
                "media:Q",
                title="Valor medio",
                format=".3f",
            ),
        ],
    )
    .properties(
        title=f"Características del perfil: {perfil_seleccionado}",
        height=420,
    )
)


st.altair_chart(
    grafico_perfil,
    use_container_width=True,
)


# -------------------------------------------------------------------
# COMPARACIÓN GENERAL DE PERFILES
# -------------------------------------------------------------------

st.subheader("Compara todos los perfiles musicales")


datos_todos_perfiles = (
    resumen_perfiles[
        ["profile"] + variables_perfiles
    ]
    .melt(
        id_vars="profile",
        var_name="variable",
        value_name="media",
    )
)


datos_todos_perfiles["caracteristica"] = (
    datos_todos_perfiles["variable"].map(nombres_variables)
)


grafico_todos_perfiles = (
    alt.Chart(datos_todos_perfiles)
    .mark_bar(
        cornerRadiusEnd=3,
    )
    .encode(
        x=alt.X(
            "media:Q",
            title="Valor medio",
            scale=alt.Scale(domain=[0, 1]),
        ),
        y=alt.Y(
            "caracteristica:N",
            title=None,
            sort=orden_caracteristicas_perfiles,
            axis=alt.Axis(labelLimit=320),
        ),
        yOffset=alt.YOffset(
            "profile:N",
            sort=orden_perfiles,
        ),
        color=alt.Color(
            "profile:N",
            title="Perfil musical",
            sort=orden_perfiles,
            scale=alt.Scale(
                domain=orden_perfiles,
                range=colores_perfiles,
            ),
        ),
        tooltip=[
            alt.Tooltip("profile:N", title="Perfil"),
            alt.Tooltip(
                "caracteristica:N",
                title="Característica",
            ),
            alt.Tooltip(
                "media:Q",
                title="Valor medio",
                format=".3f",
            ),
        ],
    )
    .properties(
        title="Comparación de las características medias de los perfiles",
        height=500,
    )
)

st.altair_chart(
    grafico_todos_perfiles,
    use_container_width=True,
)


# -------------------------------------------------------------------
# REPRESENTACIÓN PCA
# -------------------------------------------------------------------

st.subheader("Cómo se distribuyen las canciones entre los perfiles")

st.write(
    """
    La siguiente representación reduce las siete características musicales
    utilizadas por el modelo a dos dimensiones. Los puntos cercanos representan
    canciones con perfiles sonoros similares.
    """
)

grafico_clusters = (
    alt.Chart(muestra_perfiles)
    .mark_circle(
        opacity=0.40,
        size=38,
    )
    .encode(
        x=alt.X(
            "pca_1:Q",
            title="Componente principal 1",
        ),
        y=alt.Y(
            "pca_2:Q",
            title="Componente principal 2",
        ),
        color=alt.Color(
            "profile:N",
            title="Perfil musical",
            sort=orden_perfiles,
            scale=alt.Scale(
                domain=orden_perfiles,
                range=colores_perfiles,
            ),
        ),
        tooltip=[
            alt.Tooltip("track_name:N", title="Canción"),
            alt.Tooltip("artists:N", title="Artista"),
            alt.Tooltip("profile:N", title="Perfil"),
            alt.Tooltip("popularity:Q", title="Popularidad"),
        ],
    )
    .properties(
        title="Proyección de las canciones según sus características musicales",
        height=520,
    )
)

st.altair_chart(
    grafico_clusters,
    use_container_width=True,
)


st.caption(
    """
    Las dos componentes principales conservan aproximadamente el 50,3 % de la
    información original. Los grupos presentan algunas zonas diferenciadas,
    pero también un solapamiento considerable. La puntuación silhouette obtenida
    es 0,213, por lo que los perfiles deben interpretarse como tipologías
    orientativas y no como categorías completamente separadas.

    Los colores asignados a cada perfil se mantienen constantes en todas las
    visualizaciones para facilitar su identificación.
    """
)

# -------------------------------------------------------------------
# SECCIÓN 6: CONCLUSIONES, METODOLOGÍA Y LIMITACIONES
# -------------------------------------------------------------------

st.divider()

st.header("6. Entonces, ¿existe una fórmula del éxito musical?")

st.write(
    """
    El análisis muestra que no existe una característica musical aislada
    capaz de explicar la popularidad de una canción en Spotify.

    Sin embargo, sí aparecen determinados patrones: las canciones populares
    tienden a ser algo más bailables, menos instrumentales y menos acústicas.
    Además, el género musical y la combinación entre características modifican
    considerablemente estos patrones.
    """
)


# -------------------------------------------------------------------
# PRINCIPALES HALLAZGOS
# -------------------------------------------------------------------

st.subheader("Principales hallazgos")


columna_hallazgo1, columna_hallazgo2, columna_hallazgo3 = st.columns(3)


with columna_hallazgo1:
    st.metric(
        "Canciones con popularidad ≥ 70",
        f"{(df['popularity'] >= 70).mean() * 100:.1f} %",
    )

    st.caption(
        """
        Alcanzar una popularidad alta es poco frecuente dentro del
        conjunto analizado.
        """
    )


with columna_hallazgo2:
    correlacion_maxima_final = correlaciones.loc[
        correlaciones["correlacion"].abs().idxmax()
    ]

    st.metric(
        "Mayor correlación individual",
        f"{correlacion_maxima_final['correlacion']:.3f}",
    )

    st.caption(
        f"""
        Corresponde a
        {correlacion_maxima_final["caracteristica"].lower()}.
        Su intensidad sigue siendo débil.
        """
    )


with columna_hallazgo3:
    st.metric(
        "Perfil con mayor proporción popular",
        f"{perfil_mas_popular['porcentaje_popularidad_alta']:.2f} %",
    )

    st.caption(
        f"""
        Corresponde al perfil
        {perfil_mas_popular["profile"]}.
        """
    )


st.success(
    """
    **Conclusión principal:** no existe una fórmula musical única que garantice
    el éxito en Spotify. Algunos perfiles y características aparecen con mayor
    frecuencia entre las canciones populares, pero la popularidad depende de
    múltiples factores que no están contenidos completamente en este dataset.
    """
)


# -------------------------------------------------------------------
# RESPUESTA A LAS PREGUNTAS DEL PROYECTO
# -------------------------------------------------------------------

st.subheader("Respuesta a las preguntas planteadas")


with st.expander(
    "¿Qué características musicales se relacionan con la popularidad?"
):
    st.write(
        """
        Las relaciones individuales son débiles. Las canciones populares
        tienden a presentar una mayor bailabilidad y un menor carácter
        instrumental y acústico, pero existe mucho solapamiento entre
        canciones populares y poco populares.
        """
    )


with st.expander(
    "¿El género musical modifica los patrones?"
):
    st.write(
        """
        Sí. La popularidad media y los perfiles musicales cambian
        considerablemente entre géneros. Por esta razón, las características
        de una canción deben interpretarse dentro de su contexto musical.
        """
    )


with st.expander(
    "¿Existen distintos perfiles musicales?"
):
    st.write(
        """
        El clustering identifica cuatro tipologías orientativas:
        acústico y calmado, bailable y positivo, directo y hablado,
        e intenso y oscuro.

        El perfil bailable y positivo presenta la mayor proporción de
        canciones altamente populares, aunque incluso dentro de este perfil
        la mayoría de las canciones no alcanza una popularidad elevada.
        """
    )


# -------------------------------------------------------------------
# METODOLOGÍA
# -------------------------------------------------------------------

st.subheader("Metodología y preparación de los datos")


with st.expander("Consulta el proceso completo de preparación"):
    st.markdown(
        """
        ### Fuente de los datos

        Se ha utilizado el **Spotify Tracks Dataset**, publicado en Kaggle y
        construido a partir de información procedente de la Spotify Web API.

        ### Preparación realizada

        1. Se eliminó la columna de índice innecesaria `Unnamed: 0`.
        2. Se eliminó una fila sin información básica de la canción.
        3. Se eliminaron 450 filas completamente duplicadas.
        4. Se creó un conjunto con una única fila por `track_id` para evitar
           contar varias veces las canciones asociadas a distintos géneros.
        5. Se mantuvo otro conjunto canción-género para comparar géneros.
        6. Se convirtió la duración de milisegundos a minutos.
        7. Se creó un índice descriptivo de dinamismo utilizando
           bailabilidad, energía y positividad emocional.
        8. Se agruparon las canciones mediante K-Means utilizando siete
           características musicales estandarizadas.
        9. Se aplicó PCA para representar visualmente los perfiles en dos
           dimensiones.

        ### Tamaño de los conjuntos resultantes

        - Dataset original: **114.000 registros**.
        - Dataset limpio canción-género: **113.549 registros**.
        - Canciones únicas utilizadas: **89.740 canciones**.
        """
    )


# -------------------------------------------------------------------
# LIMITACIONES
# -------------------------------------------------------------------

st.subheader("Limitaciones del análisis")


st.warning(
    """
    Los resultados deben interpretarse como asociaciones descriptivas y no
    como relaciones causales. Que una característica aparezca con mayor
    frecuencia entre canciones populares no significa que provoque su éxito.
    """
)


st.markdown(
    """
    Entre las principales limitaciones se encuentran:

    - La popularidad puede depender de factores no incluidos, como campañas
      de promoción, inclusión en listas de reproducción, fama previa del
      artista o actividad en redes sociales.
    - El dataset no incluye una dimensión temporal detallada, por lo que no
      permite analizar la evolución de la popularidad.
    - Los géneros disponibles pueden solaparse y algunas canciones aparecen
      asociadas a más de uno.
    - No existe información sociodemográfica sobre artistas o audiencias.
    - Las dos componentes del gráfico PCA conservan aproximadamente el
      50,3 % de la información original.
    - La puntuación silhouette de 0,213 muestra que los perfiles musicales
      identificados presentan un solapamiento considerable.
    """
)


# -------------------------------------------------------------------
# ACCESIBILIDAD Y DECISIONES DE DISEÑO
# -------------------------------------------------------------------

st.subheader("Accesibilidad y decisiones de diseño")


with st.expander("Consulta las decisiones de accesibilidad"):
    st.markdown(
        """
        Para facilitar la interpretación de la visualización:

        - Se utilizan títulos y explicaciones antes y después de los gráficos.
        - Los colores de los perfiles se mantienen constantes.
        - Se emplea una paleta con colores diferenciables ante alteraciones
          frecuentes de la percepción cromática.
        - La información no depende únicamente del color: se incluyen
          etiquetas, leyendas, valores numéricos y textos explicativos.
        - Los gráficos incorporan información adicional al pasar el cursor.
        - Se evita mostrar todas las canciones simultáneamente cuando ello
          perjudicaría la legibilidad o el rendimiento.
        - Los resultados y limitaciones se presentan mediante lenguaje
          comprensible para públicos especializados y no especializados.
        """
    )


# -------------------------------------------------------------------
# CIERRE
# -------------------------------------------------------------------

st.divider()

st.markdown(
    """
    ### Respuesta final

    **La música importa, pero no basta.**

    Las canciones populares presentan algunos patrones frecuentes, pero el
    éxito en Spotify no puede reducirse a una combinación fija de energía,
    bailabilidad o positividad. El género, el contexto y otros factores
    externos desempeñan un papel fundamental.
    """
)

st.caption(
    """
    Proyecto desarrollado con Python, Pandas, Scikit-learn, Streamlit y Altair.
    """
)
