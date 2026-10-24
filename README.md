# ML 3 — Pronóstico experimental Niño 3.4

Estima seis meses futuros y compara el error con persistencia histórica.

**Responsable:** [Completar nombre del integrante]

**Pregunta de investigación:** ¿Cómo podría evolucionar la anomalía Niño 3.4 en los próximos seis meses?

# Trabajo grupal final — Visualización de Datos (UNAP)

Esta entrega individual es **editable** y contiene una aplicación Streamlit (`app.py`), código de análisis, CSV reales y un cuaderno de Google Colab. Cada integrante debe comprender, modificar y explicar su propio módulo antes de subirlo a GitHub.

## En una PC (VS Code, Windows)

1. Extraer el ZIP una sola vez y abrir **la carpeta que contiene `app.py`**.
2. Abrir una terminal en esa carpeta.
3. Ejecutar `python -m pip install -r requirements.txt`.
4. Ejecutar `python -m streamlit run app.py`.
5. Abrir la URL local indicada por Streamlit.

Los archivos `app.py` y el script de análisis son editables. Los resultados del script se generan nuevamente sin reemplazar los CSV originales incluidos en `datos/`.

## En Google Colab

1. Abrir Google Colab y **subir el archivo `Exploracion_Colab.ipynb`** como cuaderno.
2. Ejecutar la primera celda: solicitará subir **el ZIP de este módulo**, sin descomprimirlo.
3. Ejecutar las demás celdas. Mostrarán resultados y gráficos en el propio cuaderno.

**Importante:** Colab ejecuta el análisis y las visualizaciones del cuaderno, pero la interfaz interactiva Streamlit está preparada para PC o publicación web. El cuaderno no abre un servidor Streamlit público.

## GitHub — cada integrante

1. Crear su propio repositorio público, por ejemplo `unap-ml1-enso`, `unap-ml2-peru` o `unap-ml3-pronostico`.
2. Subir **el contenido de esta carpeta**, no únicamente el ZIP. Incluir `app.py`, `datos/`, `requirements.txt`, `Exploracion_Colab.ipynb` y el código del análisis.
3. Editar este README para consignar integrante, interpretación personal, cambios realizados, capturas y fuentes.
4. Registrar cambios mediante commits propios. Para la entrega grupal, agregar los tres enlaces a los repositorios y la URL pública del dashboard integrado.
5. Si desean publicar esta aplicación individual en Streamlit Community Cloud: conectar el repositorio y usar `app.py` como archivo principal. Probar primero la ejecución local.

## Fuentes y límites

- NOAA CPC, índices oceánicos ENSO: https://www.cpc.ncep.noaa.gov/data/indices/sstoi.indices
- NOAA CPC, SOI: https://www.cpc.ncep.noaa.gov/data/indices/soi
- NASA POWER: https://power.larc.nasa.gov/

Los datos históricos se entregan congelados con fecha de corte de septiembre de 2026. Las predicciones de ML 3 no son pronósticos oficiales. Los 25 puntos del ML 2 no son promedios de departamentos. No presentar las semejanzas del ML 1 como pronósticos.

**Rúbrica:** público objetivo, dataset público, paleta de 3–5 colores, al menos un gráfico por integrante, storytelling conectado y repositorios GitHub. Entrega indicada en el documento: 25/10/2026.

## Archivos específicos

- `app.py`: dashboard interactivo.
- `10_ml3_pronostico.py`: análisis reproducible (ejecutar `python 10_ml3_pronostico.py`).
- `datos/`: CSV para mostrar resultados originales.
- `Exploracion_Colab.ipynb`: análisis y gráficos para Colab.

## Interpretación del integrante

[Escribir aquí en sus propias palabras qué muestra el gráfico, qué hallazgo destaca y qué limitación tiene.]
