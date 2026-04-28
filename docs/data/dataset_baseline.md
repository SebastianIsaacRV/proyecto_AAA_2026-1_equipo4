## Diccionario de datos — Dataset baseline

El dataset de modelado corresponde a un **panel a nivel municipio-año**, donde cada observación representa un municipio de México en un año determinado. Integra información de incidencia delictiva, condiciones socioeconómicas y contexto geográfico, con el objetivo de analizar y modelar la tasa de delitos.

La generación de este dataset fue **automatizada** en el módulo
`incidencia_delictiva.pipelines.datasets:dataset_baseline`, mientras que la libreta
`notebooks/dataset_modelado.ipynb` documenta su construcción y la selección de variables.

## Variables

| Variable          | Descripción                                             |
| ----------------- | ------------------------------------------------------- |
| `año`             | Año de observación                                      |
| `cvegeo`          | Clave geográfica única del municipio                    |
| `total_delitos`   | Total anual de delitos registrados                      |
| `poblacion_total` | Población total del municipio                           |
| `tasa_delitos`    | Delitos por cada 100,000 habitantes (variable objetivo) |
| `indice_marginacion_normalizado_2020` | Índice sintético de marginación           |
| `porcentaje_analfabetismo`            | Proporción de población analfabeta        |
| `porcentaje_sin_agua_entubada`        | Viviendas sin acceso a agua entubada      |
| `porcentaje_viviendas_hacinamiento`   | Viviendas con condiciones de hacinamiento |
| `fn_pobreza_porcentaje`                   | Porcentaje de población en situación de pobreza |
| `fn_pobreza_extrema_porcentaje`           | Porcentaje en pobreza extrema                   |
| `fn_vulnerable_ingresos_porcentaje`       | Población vulnerable por ingresos               |
| `fn_carencia_seguridad_social_porcentaje` | Población sin acceso a seguridad social         |
| `fn_poblacion`                            | Población estimada (fuente pobreza)             |
| `poblacion_urbano`                        | Población en zonas urbanas                      |
| `prop_urbano`                             | Proporción de población urbana                  |
| `nomgeo`             | Nombre del municipio                          |
| `area_km2`           | Área del municipio en $\text{Km}^2$                     |
| `region`             | Región geográfica del país                    |
| `zona_metropolitana` | Indicador de pertenencia a zona metropolitana |
| `es_frontera`        | Indicador de municipio en entidad fronteriza  |


Este dataset constituye una **línea base de modelado**, diseñada para capturar múltiples dimensiones del fenómeno delictivo manteniendo interpretabilidad y simplicidad.
