# Diccionario de datos — marginacion (Índice de marginación municipal en México)

## Descripción general

Este dataset contiene información a nivel **municipio en México** sobre condiciones estructurales asociadas a la marginación, incluyendo variables de educación, vivienda, distribución poblacional e ingresos.

La fuente original corresponde al **Índice de Marginación 2020** publicado por CONAPO a través de [datos abiertos](https://www.datos.gob.mx/dataset/indices_marginacion/resource/216bb68c-d3fa-42a7-84ac-10337cd1f6cd), el cual resume **carencias estructurales de la población** mediante indicadores porcentuales y un índice sintético (`im_2020`) junto con su clasificación (`gm_2020`).

---

## Transformaciones aplicadas

Los datos fueron procesados en el módulo:

```text
incidencia_delictiva/etl/marginacion.py
```

Durante el proceso ETL se realizaron las siguientes transformaciones principales:

* Normalización de nombres de columnas a minúsculas
* Estandarización de claves (`cve_ent`, `cve_mun`)
* Creación de la clave geográfica (`cvegeo`) mediante concatenación
* Limpieza básica de texto en variables categóricas
* Conversión de variables numéricas a tipo adecuado
* Exportación a formato parquet para eficiencia de consulta

El resultado final se almacenó en:

```text
incidencia_delictiva.duckdb
```

Tabla:

```sql
marginacion
```

---

## Nota de calidad de datos

Se observa un posible problema de encoding en nombres de municipios (`CosÃ­o`, `JesÃºs MarÃ­a`), lo que sugiere una codificación incorrecta en la fuente original (UTF-8 vs Latin-1). Esto puede requerir limpieza adicional si se utilizan campos de texto para visualización o análisis.

Adicionalmente, algunas columnas originales contienen caracteres especiales en su nombre (ej. `pl.5000`), los cuales fueron normalizados para evitar problemas en consultas.

---

# Estructura del dataset

| Columna    | Tipo    | Descripción                                                              |
| ---------- | ------- | ------------------------------------------------------------------------ |
| `cvegeo`   | str     | Clave geográfica única del municipio (concatenación entidad + municipio) |
| `cve_ent`  | str     | Clave de la entidad federativa                                           |
| `nom_ent`  | str     | Nombre de la entidad federativa                                          |
| `cve_mun`  | str     | Clave del municipio dentro de la entidad                                 |
| `nom_mun`  | str     | Nombre del municipio                                                     |
| `pob_tot`  | int64   | Población total del municipio                                            |
| `analf`    | float64 | Porcentaje de población analfabeta                                       |
| `sbasc`    | float64 | Porcentaje de población sin educación básica                             |
| `ovsde`    | float64 | Porcentaje de viviendas sin drenaje                                      |
| `ovsee`    | float64 | Porcentaje de viviendas sin energía eléctrica                            |
| `ovsae`    | float64 | Porcentaje de viviendas sin agua entubada                                |
| `ovpt`     | float64 | Porcentaje de viviendas con piso de tierra                               |
| `vhac`     | float64 | Porcentaje de viviendas con hacinamiento                                 |
| `pl_5000`  | float64 | Porcentaje de población en localidades menores a 5,000 habitantes        |
| `po2sm`    | float64 | Porcentaje de población ocupada con ingresos de hasta 2 salarios mínimos |
| `im_2020`  | float64 | Índice de marginación (valor continuo)                                   |
| `gm_2020`  | str     | Grado de marginación (categoría: muy bajo, bajo, medio, alto, muy alto)  |
| `imn_2020` | float64 | Índice de marginación normalizado                                        |

---

## Uso esperado

Este dataset funciona como **dimensión socioeconómica** en la etapa de modelado, permitiendo:

* Analizar condiciones estructurales por municipio
* Clasificar territorios según su nivel de marginación
* Cruces con los otros datasets mediante `cvegeo`
* Análisis de correlación entre marginación y otros fenómenos (ej. incidencia delictiva)
