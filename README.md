# ¿Existe una fórmula del éxito musical en Spotify?

Proyecto interactivo de visualización de datos desarrollado para la asignatura de Visualización de Datos del Máster en Ciencia de Datos de la UOC.

La aplicación explora qué características musicales distinguen a las canciones más populares de Spotify y hasta qué punto estas diferencias dependen del género y de la combinación entre atributos sonoros.

## Pregunta principal

**¿Qué distingue musicalmente a las canciones más populares de Spotify y hasta qué punto esas diferencias dependen del género musical?**

## Principales conclusiones

* Alcanzar una popularidad elevada es poco frecuente dentro del conjunto analizado.
* Ninguna característica musical individual explica claramente la popularidad.
* Las canciones populares tienden a ser algo más bailables, menos acústicas y menos instrumentales.
* La popularidad media y los perfiles musicales varían considerablemente entre géneros.
* El perfil denominado **Bailable y positivo** presenta la mayor proporción de canciones altamente populares, aunque la mayoría de sus canciones tampoco alcanza una popularidad elevada.
* No existe una fórmula musical única que garantice el éxito en Spotify.

## Tecnologías utilizadas

* Python
* Pandas
* Scikit-learn
* Streamlit
* Altair

## Conjunto de datos

Se utiliza el **Spotify Tracks Dataset**, publicado en Kaggle y construido a partir de información procedente de la Spotify Web API.

El conjunto original contiene aproximadamente 114.000 registros y variables relacionadas con:

* Popularidad
* Género musical
* Bailabilidad
* Energía
* Positividad emocional
* Carácter acústico
* Carácter instrumental
* Tempo
* Volumen
* Presencia de voz hablada

## Preparación de los datos

Durante la preparación se realizaron las siguientes operaciones:

1. Eliminación de la columna de índice innecesaria.
2. Eliminación de filas completamente duplicadas.
3. Eliminación de registros sin información básica.
4. Creación de un conjunto con canciones únicas.
5. Conservación de un conjunto canción-género para realizar comparaciones.
6. Conversión de la duración a minutos.
7. Creación de un índice descriptivo de dinamismo.
8. Creación de perfiles musicales mediante K-Means.
9. Reducción de dimensionalidad mediante PCA.

## Ejecución local

Instalar las dependencias:

```bash
python -m pip install -r requirements.txt
```

Ejecutar la aplicación:

```bash
python -m streamlit run app.py
```

## Scripts

* `app.py`: aplicación interactiva principal.
* `prepare_data.py`: limpieza y preparación de los datos.
* `create_profiles.py`: creación y análisis de los perfiles musicales.

## Limitaciones

Los resultados representan asociaciones descriptivas y no relaciones causales. La popularidad también puede depender de factores no incluidos en el conjunto de datos, como la promoción, la inclusión en listas de reproducción, la fama previa del artista o la actividad en redes sociales.

## Licencia

Este proyecto se publica bajo la licencia MIT.

## Visualización pública

La aplicación interactiva está disponible en:

https://spotify-visualizacion-final.streamlit.app