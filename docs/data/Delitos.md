# Diccionario de datos — delitos (Incidencia delictiva municipal en México)

## Descripción general

Este dataset contiene información de **incidencia delictiva a nivel municipal en México**, desagregada por tipo, subtipo y modalidad del delito, así como por mes.

La fuente original corresponde a datos abiertos del [SESNSP](https://www.datos.gob.mx/dataset/incidencia_delictiva/resource/57fbd692-3e5c-4b1b-8621-694cb3a33035), los cuales representan **conteos mensuales de delitos registrados en carpetas de investigación**, organizados por entidad y municipio.

Cada registro representa una combinación de:

* ubicación geográfica (entidad y municipio)
* clasificación del delito
* año
* conteos mensuales

---

## Transformaciones aplicadas

Los datos fueron procesados en el módulo:

```text
incidencia_delictiva/etl/delitos.py
```

Durante el proceso ETL se realizaron las siguientes transformaciones principales:

* Descarga automatizada del dataset desde fuente oficial
* Lectura eficiente del archivo mediante procesamiento por **chunks**
* Normalización de nombres de columnas a minúsculas
* Generación de la clave geográfica `cvegeo` (concatenación entidad + municipio)
* Carga incremental a base de datos para manejo de archivos grandes

El resultado final se almacenó en:

```text
incidencia_delictiva.duckdb
```

Tabla:

```sql
delitos
```

---

## Nota de calidad de datos

* Se utiliza codificación `latin-1`, lo que puede generar problemas de encoding en nombres de texto (ej. acentos incorrectos).
* La columna `cve._municipio` contiene un carácter especial (`.`), lo cual puede dificultar su uso en SQL o herramientas de análisis.
* El dataset se encuentra en formato **wide (columnas por mes)**, lo que puede requerir transformación adicional a formato long para análisis de series de tiempo.

---

# Estructura del dataset

| Columna                  | Tipo  | Descripción                                                |
| ------------------------ | ----- | ---------------------------------------------------------- |
| `año`                    | int64 | Año de registro de los delitos                             |
| `clave_ent`              | int64 | Clave numérica de la entidad federativa                    |
| `entidad`                | str   | Nombre de la entidad federativa                            |
| `cve._municipio`         | int64 | Clave del municipio dentro de la entidad                   |
| `municipio`              | str   | Nombre del municipio                                       |
| `bien_jurídico_afectado` | str   | Categoría general del bien jurídico afectado               |
| `tipo_de_delito`         | str   | Tipo de delito                                             |
| `subtipo_de_delito`      | str   | Subclasificación del delito                                |
| `modalidad`              | str   | Modalidad específica del delito                            |
| `enero`                  | int64 | Número de delitos registrados en enero                     |
| `febrero`                | int64 | Número de delitos registrados en febrero                   |
| `marzo`                  | int64 | Número de delitos registrados en marzo                     |
| `abril`                  | int64 | Número de delitos registrados en abril                     |
| `mayo`                   | int64 | Número de delitos registrados en mayo                      |
| `junio`                  | int64 | Número de delitos registrados en junio                     |
| `julio`                  | int64 | Número de delitos registrados en julio                     |
| `agosto`                 | int64 | Número de delitos registrados en agosto                    |
| `septiembre`             | int64 | Número de delitos registrados en septiembre                |
| `octubre`                | int64 | Número de delitos registrados en octubre                   |
| `noviembre`              | int64 | Número de delitos registrados en noviembre                 |
| `diciembre`              | int64 | Número de delitos registrados en diciembre                 |
| `cvegeo`                 | str   | Clave geográfica única del municipio (entidad + municipio) |

---

## Uso esperado

Este dataset funciona como **tabla de hechos (fact table)** en el modelo de datos, permitiendo:

* Análisis de incidencia delictiva por municipio, estado o tipo de delito
* Construcción de series de tiempo (mensuales y anuales)
* Cruce con los otros datasets mediante la clave única `cvegeo`
* Cálculo de indicadores (tasas por población, tendencias, variación temporal)
