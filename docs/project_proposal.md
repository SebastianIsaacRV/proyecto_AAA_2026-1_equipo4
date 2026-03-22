# Proyecto: Predicción de Incidencia Delictiva Municipal en México

## 1. Problema a resolver

En México, la incidencia delictiva varía significativamente entre municipios y a lo largo del tiempo. Sin embargo, no siempre es claro **qué factores socioeconómicos están más asociados con estos niveles de violencia**.

Este proyecto busca responder:

> **¿Qué variables socioeconómicas explican y permiten predecir la tasa de incidencia delictiva a nivel municipal en México?**

Para ello, construiremos un modelo basado en datos públicos que permita estimar la **tasa de delitos (por cada X habitantes)** a partir de características como marginación, escolaridad, empleo y densidad poblacional.

* X = 100000, dependerá de la unidad de observación que definamos: municipal ó estatal. 

---

## 2. ¿Por qué es importante este problema?

Este problema es relevante porque:

* **Toma de decisiones públicas:** Instituciones gubernamentales pueden identificar factores estructurales asociados a la violencia.
* **Asignación de recursos:** Permite enfocar políticas públicas en municipios/estados con mayor riesgo.
* **Análisis social:** Ayuda a entender relaciones entre desigualdad, educación y criminalidad.
* **Transparencia y reproducibilidad:** Uso de datos abiertos fortalece análisis públicos verificables.

En términos simples:
*No solo queremos saber dónde hay más delitos, sino entender por qué.*

---

## 3. Tipo de problema de aprendizaje

Este proyecto corresponde a un problema de: **Regresión supervisada**

La **variable objetivo (target):**

```
tasa_delitos = (número de delitos / población) * X
```

* Necesita construirse a partir de los datos de incidencia delictiva y de demografía (población).

**Unidad de observación:** Por definir, de momento consideraremos a nivel municipal. En el futuro podríamos cambiar a nivel estatal.

Ejemplo:

| Municipio  | Año  | Tasa_delitos |
| ---------- | ---- | ------------ |
| Hermosillo | 2020 | 450          |
| Hermosillo | 2021 | 520          |

---

## 4. Variables (features)

A partir de integración de múltiples datasets:

La lista de a continuación serán las variables principales tentativas:

* índice de marginación
* escolaridad promedio
* tasa de desempleo
* densidad poblacional
* población total

Algunas variables derivadas:

* delitos per cápita
* densidad = población / área
* transformaciones 

---

## 5. Métricas de evaluación

Dado que es un problema de regresión, las métricas principales: 

* **RMSE (Root Mean Squared Error)**
* **MAE (Mean Absolute Error)**
* **$R^2$ (coeficiente de determinación)**
---

## 6. Valores deseables

* RMSE bajo (dependiente de escala, pero minimizado comparativamente)
* MAE bajo
* $R^2$ alto (idealmente > 0.6 en este contexto, ya que contaremos con datos de diferentes regiones del país)

Más importante que las métricas buscamos **consistencia del modelo y capacidad explicativa**

---

## 7. Alineación con objetivos del usuario / institución

Las métricas están alineadas con el objetivo del proyecto porque:

* **RMSE / MAE bajos** &rarr; permiten predicciones confiables
* **$R^2$ alto** &rarr; indica que variables socioeconómicas realmente explican el fenómeno
* **Interpretabilidad del modelo** &rarr; permite extraer conclusiones útiles (no solo predicción)

---

# Datasets iniciales (para ETL)

Para construir el dataset final, integraremos múltiples fuentes. En principio, necesitamos datos relacionados a características como marginación, escolaridad, empleo y densidad poblacional. El futuro podríamos agregar más.

---

## 1. Incidencia delictiva (TARGET)

* Fuente: SESNSP (datos.gob.mx)
* Nivel: municipal, mensual

Este dataset contiene:

* municipio
* estado
* tipo de delito
* mes
* año
* número de delitos

y cubre los años **2015-2025** con desagregación municipal y estatal.

En primera instancia, tenemos que decidir: 

1. Unidad de observación: municipal ó estatal. 
2. Tipo de delito: existen múltiples tipos de delitos,  entre los cuales se incluyen "Abuso de confianza", "Daño a la propiedad", "Despojo", "Extorsión", etc. 
    Alternativamente al tipo de delito, podríamos considerar un filtrado por la feature "Bien judrídico afectado". O bien, considerar todos los tipos de delitos por municipio (o estado).

Ejemplo de columnas: 

```
anio
mes
clave_ent
entidad
clave_mun
municipio
tipo_delito
subtipo_delito
modalidad
total
```

---

## 2. Población

* Fuente: INEGI

Datos con información demográfica y socioeconómica a nivel municipal (o estatal).

Algunas variables útiles: 

```
poblacion_total
poblacion_hombres
poblacion_mujeres
densidad_poblacional
```

Estas servirán para construir la variable objetivo `tasa_delictiva`.

## 3. Marginación / Pobreza

* Fuente: CONAPO/INEGI


Necesitamos variables como:

  * índice de marginación
  * condiciones de vivienda
  * analfabetismo

Estas servirán como features explicativas.

---

## 4. Educación

* Fuente: INEGI / SEP

Variables:

  * escolaridad promedio
  * % educación media/superior

Útiles como features explicativas.

---

## 5. Empleo

* Fuente: INEGI (ENOE)
Variables:

  * tasa de desempleo
  * % de informalidad

Features para explicabilidad.
---

# Dataset final

Después del ETL, el dataset final tentativo podría contener algunas features como:

| municipio | año | poblacion | marginacion | escolaridad | desempleo | densidad_poblacional | tasa_delitos |
| --------- | --- | --------- | ----------- | ----------- | --------- | -------- | ------------ |
|A|2020|500000|0.332|9.2|4.5|1200| 5.2|

* Los datos de la tabla anterior son ficticios.

---

# Pipeline de trabajo

## 1. ETL

* limpieza de claves
* agregación temporal (mes/anio, por definir)
* joins entre datasets (por clave de municipio y anio)
* generación de variable objetivo
---

## 2. EDA

* correlaciones
* distribución de variables
* análisis geográfico (opcional)

### Métodos no supervisados sugeridos:

* PCA &rarr; reducción de dimensionalidad
* K-means &rarr; clusters de municipios

---

## 3. Modelado

* Linear Regression (baseline)
* Ridge (selección de features, penalización moderada)
* Lasso (selección de features, alta penalización)

---

## 4. Interpretación

* análisis de coeficientes
* impacto de variables
* discusión social

---

# Entregable esperado

Un modelo capaz de:

* predecir la tasa de delitos por municipio
* identificar variables clave asociadas al crimen
* generar conclusiones interpretables
