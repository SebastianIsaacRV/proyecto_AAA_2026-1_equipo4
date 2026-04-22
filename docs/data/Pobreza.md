# Diccionario de datos — pobreza (Indicadores de pobreza municipal, México)

## Descripción general

Este dataset contiene información sobre **condiciones de pobreza a nivel municipio en México para el año 2020**, incluyendo métricas de población, pobreza, vulnerabilidad y carencias sociales.

La fuente original corresponde a datasets abiertos publicados en [datos.gob.mx](https://www.datos.gob.mx/dataset/pobreza_mexico), los cuales integran indicadores estimados por el CONEVAL. Estos datos representan **estadísticas socioeconómicas agregadas por municipio**, incluyendo proporciones y totales poblacionales en distintas condiciones de bienestar.

Adicionalmente, se incorpora información sobre el **tipo de residencia (rural/urbano)** asociada a cada municipio.

---

## Transformaciones aplicadas

Los datos fueron procesados en el módulo:

```text
incidencia_delictiva/etl/pobreza.py
```

Durante el proceso ETL se realizaron las siguientes transformaciones principales:

* Descarga de datasets de indicadores de pobreza y grupo de residencia
* Filtrado del periodo **2020-01-01** (corte temporal único)
* Normalización de nombres de columnas a minúsculas
* Selección de variables relevantes (`fn_*`)
* Construcción de la clave geográfica `cvegeo` (entidad + municipio)
* Limpieza de la variable `grupo` (extracción de categoría rural/urbano)
* Integración de datasets mediante `merge` por `cvegeo`

El resultado final se almacenó en:

```text
incidencia_delictiva.duckdb
```

Tabla:

```sql
pobreza
```

---

## Nota de calidad de datos

* El dataset presenta **duplicidad de registros por municipio**, derivado de la variable `grupo` (rural/urbano), lo que implica una granularidad a nivel *municipio × tipo de residencia*.
* Las variables `fn_*` están agregadas a nivel municipal, por lo que su valor se repite entre categorías de residencia.
* Es importante considerar esta estructura al realizar agregaciones o joins con otros datasets para evitar duplicación de métricas.

---

# Estructura del dataset

| Columna                                                 | Tipo    | Descripción                                                        |
| ------------------------------------------------------- | ------- | ------------------------------------------------------------------ |
| `clave_entidad`                                         | int64   | Clave numérica de la entidad federativa                            |
| `entidad_federativa`                                    | str     | Nombre de la entidad federativa                                    |
| `clave_municipio`                                       | int64   | Clave del municipio dentro de la entidad                           |
| `municipio`                                             | str     | Nombre del municipio                                               |
| `cvegeo`                                                | str     | Clave geográfica única (entidad + municipio)                       |
| `grupo`                                                 | str     | Tipo de residencia (rural o urbano)                                |
| `fn_poblacion`                                          | float64 | Población total del municipio                                      |
| `fn_pobreza_porcentaje`                                 | float64 | Porcentaje de población en situación de pobreza                    |
| `fn_pobreza_poblacion`                                  | float64 | Población en situación de pobreza                                  |
| `fn_pobreza_extrema_porcentaje`                         | float64 | Porcentaje de población en pobreza extrema                         |
| `fn_pobreza_extrema_poblacion`                          | float64 | Población en pobreza extrema                                       |
| `fn_pobreza_moderada_porcentaje`                        | float64 | Porcentaje de población en pobreza moderada                        |
| `fn_pobreza_moderada_poblacion`                         | float64 | Población en pobreza moderada                                      |
| `fn_vulnerable_carencias_sociales_porcentaje`           | float64 | Porcentaje de población vulnerable por carencias sociales          |
| `fn_vulnerable_carencias_sociales_poblacion`            | float64 | Población vulnerable por carencias sociales                        |
| `fn_vulnerable_ingresos_porcentaje`                     | float64 | Porcentaje de población vulnerable por ingresos                    |
| `fn_vulnerable_ingresos_poblacion`                      | float64 | Población vulnerable por ingresos                                  |
| `fn_no_pobre_no_vulnerable_porcentaje`                  | float64 | Porcentaje de población no pobre y no vulnerable                   |
| `fn_no_pobre_no_vulnerable_poblacion`                   | float64 | Población no pobre y no vulnerable                                 |
| `fn_carencia_rezago_educativo_porcentaje`               | float64 | Porcentaje con rezago educativo                                    |
| `fn_carencia_rezago_educativo_poblacion`                | float64 | Población con rezago educativo                                     |
| `fn_carencia_servicios_de_salud_porcentaje`             | float64 | Porcentaje sin acceso a servicios de salud                         |
| `fn_carencia_servicios_de_salud_poblacion`              | float64 | Población sin acceso a servicios de salud                          |
| `fn_carencia_seguridad_social_porcentaje`               | float64 | Porcentaje sin seguridad social                                    |
| `fn_carencia_seguridad_social_poblacion`                | float64 | Población sin seguridad social                                     |
| `fn_carencia_calidad_espacios_vivienda_porcentaje`      | float64 | Porcentaje con carencias en calidad de vivienda                    |
| `fn_carencia_calidad_espacios_vivienda_poblacion`       | float64 | Población con carencias en calidad de vivienda                     |
| `fn_carencia_servicios_basicos_vivienda_porcentaje`     | float64 | Porcentaje con carencias en servicios básicos de vivienda          |
| `fn_carencia_servicios_basicos_vivienda_poblacion`      | float64 | Población con carencias en servicios básicos de vivienda           |
| `fn_carencia_alimentacion_nutritiva_calidad_porcentaje` | float64 | Porcentaje con carencia alimentaria                                |
| `fn_carencia_alimentacion_nutritiva_calidad_poblacion`  | float64 | Población con carencia alimentaria                                 |
| `fn_al_menos_una_carencia_porcentaje`                   | float64 | Porcentaje con al menos una carencia social                        |
| `fn_al_menos_una_carencia_poblacion`                    | float64 | Población con al menos una carencia social                         |
| `fn_al_menos_tres_carencias_porcentaje`                 | float64 | Porcentaje con tres o más carencias                                |
| `fn_al_menos_tres_carencias_poblacion`                  | float64 | Población con tres o más carencias                                 |
| `fn_ingreso_inferior_a_lpi_porcentaje`                  | float64 | Porcentaje con ingreso inferior a la línea de pobreza por ingresos |
| `fn_ingreso_inferior_a_lpi_poblacion`                   | float64 | Población con ingreso inferior a la línea de pobreza               |
| `fn_ingreso_inferior_a_lpei_porcentaje`                 | float64 | Porcentaje con ingreso inferior a la línea de pobreza extrema      |
| `fn_ingreso_inferior_a_lpei_poblacion`                  | float64 | Población con ingreso inferior a la línea de pobreza extrema       |

---

## Uso esperado

Este dataset funciona como **fuente socioeconómica** para análisis a nivel municipal, permitiendo:

* Analizar la relación entre pobreza y **incidencia delictiva**
* Construir variables explicativas para modelos predictivos
* Evaluar desigualdad territorial
* Generar indicadores comparativos entre municipios
* Cruces con los otros datasets mediante `cvegeo`
