## Diccionario de datos — Features espaciales (V2)

En esta sección se documentan las variables adicionales generadas durante el proceso de **feature engineering espacial**. Estas variables extienden el dataset baseline incorporando información sobre **estructura territorial, proximidad y dependencia espacial** entre municipios.

A diferencia de la versión anterior, se actualizó la definición de municipios en frontera utilizando **fronteras geográficas reales**, en lugar de una asignación a nivel entidad federativa. Esto permite una representación más precisa de los efectos geopolíticos.

La generación de estas variables forma parte del pipeline definido en
`incidencia_delictiva.pipelines.datasets:make_dataset_geospatial`, mientras que la libreta
`notebooks/features_geoespaciales.ipynb` documenta su construcción y la selección de variables.


## Variables

| Variable          | Descripción                                             |
| ----------------- | ------------------------------------------------------- |
| `densidad_poblacional` | Población total dividida entre el área del municipio (hab/$\text{km}^2$)|
| `lag_delitos`        | Promedio de la tasa de delitos en municipios vecinos (mismo año)|
| `lag_marginacion`    | Promedio del índice de marginación en municipios vecinos |
| `num_vecinos`        | Número de municipios colindantes (contigüidad tipo *queen*)|
| `distancia_frontera` | Distancia mínima desde el municipio a un municipio fronterizo|
| `distancia_zm`       | Distancia mínima a un municipio perteneciente a una zona metropolitana|
