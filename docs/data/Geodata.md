# Diccionario de datos — geodata (Municipios de México)

## Descripción general

Este dataset contiene información geográfica a nivel **municipio en México**, incluyendo identificadores oficiales, nombres, atributos espaciales (área, perímetro, geometría) y variables derivadas para análisis regional.

La fuente original corresponde a un [shapefile](http://geoportal.conabio.gob.mx/metadatos/doc/html/mun22gw.html) de municipios (INEGI), el cual representa **polígonos geoespaciales administrativos**.

---

## Transformaciones aplicadas

Los datos fueron procesados en el módulo:

```text
incidencia_delictiva/etl/geograficos.py
```

Durante el proceso ETL se realizaron las siguientes transformaciones principales:

* Normalización de nombres de columnas a minúsculas
* Estandarización de claves (`cve_ent`, `cve_mun`, `cvegeo`)
* Asignación de **región geográfica** (`region`)
* Identificación de **municipios en zonas metropolitanas**
* Identificación de **municipios fronterizos**
* Reproyección espacial para cálculo de área
* Cálculo de **área en $\text{km}^2$ (`area_km2`)**

El resultado final se almacenó en:

```text
incidencia_delictiva.duckdb
```

Tabla:

```sql
geodata
```

---

##  Nota de calidad de datos

Se observa un posible problema de encoding en nombres (`San JosÃ©`, `TepezalÃ¡`), lo que sugiere una codificación incorrecta (probablemente UTF-8 vs Latin-1). Esto puede requerir limpieza posterior si se usan textos para análisis o visualización.

---

# Estructura del dataset

| Columna                     | Tipo            | Descripción                                                              |
| --------------------------- | --------------- | ------------------------------------------------------------------------ |
| `cvegeo`                    | str             | Clave geográfica única del municipio (concatenación entidad + municipio) |
| `cve_ent`                   | str             | Clave de la entidad federativa                                           |
| `cve_mun`                   | str             | Clave del municipio dentro de la entidad                                 |
| `nomgeo`                    | str             | Nombre del municipio                                                     |
| `nom_ent`                   | str             | Nombre de la entidad federativa                                          |
| `cov_`                      | int64           | Identificador interno del dataset original                               |
| `cov_id`                    | int64           | ID adicional del shapefile original                                      |
| `area`                      | float64         | Área original del polígono (unidad del shapefile original)               |
| `perimeter`                 | float64         | Perímetro del polígono                                                   |
| `geometry`                  | geometry/object | Geometría del municipio (polígono)                                       |
| `region`                    | str             | Región geográfica asignada (ej. norte, centro-sur, etc.)                 |
| `zona_metropolitana`        | int64           | Indicador binario (1 = pertenece a zona metropolitana, 0 = no)           |
| `zona_metropolitana_nombre` | str             | Nombre de la zona metropolitana asociada                                 |
| `es_frontera`               | int64           | Indicador binario de municipio fronterizo                                |
| `area_km2`                  | float64         | Área calculada en kilómetros cuadrados                                   |

---

## Uso esperado

Este dataset funciona como **dimensión geográfica** en la etapa de modelado, permitiendo:

* Agregar datos por municipio, estado o región
* Calcular tasas (ej. delitos por $\text{km}$^2 o población)
* Análisis espacial y visualización geográfica
* Cruces con los otros datasets
