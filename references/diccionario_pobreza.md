# Diccionario de datos — Pobreza Municipal 2020

**Fuente:** Consejo Nacional de Evaluación de la Política de Desarrollo Social (CONEVAL)  
**Archivo:** `data/raw/pobreza_municipal_2020.csv`  
**Cobertura:** 2,469 municipios · Nacional (2,466 con datos completos)  
**Año de referencia:** 2020  
**Encoding:** latin-1  
**Valores nulos:** 3 municipios (ver sección de calidad de datos)  
**Separador de miles:** coma (`,`) — requiere limpieza al leer con pandas  

---

## Lectura recomendada

```python
import pandas as pd

df = pd.read_csv("data/raw/pobreza_municipal_2020.csv", encoding="latin-1")

# Limpiar separador de miles en columnas numéricas
cols_id = ["clave_entidad", "entidad_federativa", "clave_municipio", "municipio"]
for col in df.columns:
    if col not in cols_id:
        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace(",", "").str.strip(), errors="coerce"
        )

# Construir clave geográfica para merge
df["CVEGEO"] = (df["clave_entidad"].astype(str).str.zfill(2) +
                df["clave_municipio"].astype(str).str.zfill(3))
```

---

## Claves geográficas

| Variable | Tipo | Descripción | Ejemplo |
|---|---|---|---|
| `clave_entidad` | int | Clave de la entidad federativa (1–32) | `26` = Sonora |
| `entidad_federativa` | str | Nombre del estado | `Sonora` |
| `clave_municipio` | int | Clave del municipio dentro del estado (3 dígitos) | `001` |
| `municipio` | str | Nombre del municipio | `Aconchi` |
| `poblacion` | float | Población total del municipio | 2,986 |

---

## Medición multidimensional de la pobreza

Las variables de porcentaje (`%`) y de población absoluta (`_pob`) vienen en pares. Para el modelo usar preferentemente los **porcentajes** para evitar colinealidad con `poblacion`.

### Pobreza por ingresos y carencias

| Variable | Descripción | Media | Mediana | Min | Max |
|---|---|---|---|---|---|
| `pobreza` | % de población en situación de pobreza | 62.0 | 62.7 | 5.5 | 99.6 |
| `pobreza_pob` | Población en situación de pobreza | — | — | — | — |
| `pobreza_e` | % en pobreza **extrema** (≥3 carencias + ingreso muy bajo) | 17.2 | 12.6 | 0.0 | 84.4 |
| `pobreza_e_pob` | Población en pobreza extrema | — | — | — | — |
| `pobreza_m` | % en pobreza **moderada** (pobreza − pobreza extrema) | 44.8 | 46.0 | 5.2 | 85.0 |
| `pobreza_m_pob` | Población en pobreza moderada | — | — | — | — |

### Vulnerabilidad

| Variable | Descripción | Media | Mediana |
|---|---|---|---|
| `vul_car` | % vulnerable por carencias sociales (sin pobreza por ingresos) | 25.1 | 24.3 |
| `vul_car_pob` | Población vulnerable por carencias | — | — |
| `vul_ing` | % vulnerable por ingresos (sin carencias) | 3.9 | 2.7 |
| `vul_ing_pob` | Población vulnerable por ingresos | — | — |
| `npnv` | % **no pobre y no vulnerable** | 9.0 | 5.4 |
| `npnv_pob` | Población no pobre y no vulnerable | — | — |

> **Identidad de suma**: `pobreza + vul_car + vul_ing + npnv = 100%` para cada municipio.

---

## Las 6 carencias sociales (indicadores de carencia, `ic_*`)

| Variable | Descripción | Media | Mediana | Min | Max |
|---|---|---|---|---|---|
| `ic_rezedu` | % con **rezago educativo** | 25.7 | 25.2 | 2.9 | 61.4 |
| `ic_rezedu_pob` | Población con rezago educativo | — | — | — | — |
| `ic_asalud` | % sin **acceso a servicios de salud** | 25.1 | 23.2 | 1.1 | 83.9 |
| `ic_asalud_pob` | Población sin acceso a salud | — | — | — | — |
| `ic_segsoc` | % sin **acceso a seguridad social** ⚠️ | 72.4 | 76.5 | 22.0 | 97.0 |
| `ic_segsoc_pob` | Población sin seguridad social | — | — | — | — |
| `ic_cv` | % con **carencia por calidad y espacios de vivienda** | 16.3 | 12.8 | 0.8 | 76.7 |
| `ic_cv_pob` | Población con carencia de vivienda | — | — | — | — |
| `ic_sbv` | % con **carencia por servicios básicos en vivienda** | 40.1 | 35.1 | 0.1 | 100.0 |
| `ic_sbv_pob` | Población con carencia de servicios básicos | — | — | — | — |
| `ic_ali` | % con **carencia por acceso a alimentación nutritiva** | 23.0 | 21.3 | 0.0 | 75.7 |
| `ic_ali_pob` | Población con carencia alimentaria | — | — | — | — |

> ⚠️ `ic_segsoc` es la carencia más extendida (media 72.4%) y tiene alta colinealidad con `pobreza`. Usar con precaución en modelos de regresión.

---

## Líneas de pobreza por ingresos

| Variable | Descripción | Media | Mediana |
|---|---|---|---|
| `carencias` | % con al menos **1 carencia social** | 87.1 | 91.6 |
| `carencias_pob` | Población con al menos 1 carencia | — | — |
| `carencias3` | % con **3 o más carencias** sociales | 34.4 | 31.7 |
| `carencias3_pob` | Población con 3+ carencias | — | — |
| `plp` | % bajo **línea de pobreza** por ingresos | 65.9 | 67.0 | 7.2 | 99.9 |
| `plp_pob` | Población bajo línea de pobreza | — | — | — | — |
| `plp_e` | % bajo **línea de pobreza extrema** por ingresos | 33.0 | 28.6 | 1.1 | 97.5 |
| `plp_e_pob` | Población bajo línea de pobreza extrema | — | — | — | — |

---

## Calidad de datos

### Municipios con valores nulos (3 en total)

| Estado | Municipio | Motivo probable |
|---|---|---|
| Campeche | Seybaplaya | Municipio de reciente creación |
| Chiapas | Honduras de la Sierra | Municipio de reciente creación |
| Tlaxcala | La Magdalena Tlaltelulco | Municipio de reciente creación |

**Estrategia de imputación recomendada:** reemplazar con la media de los demás municipios del mismo estado.

```python
for col in df.select_dtypes("float64").columns:
    df[col] = df.groupby("clave_entidad")[col].transform(
        lambda x: x.fillna(x.mean())
    )
```

---

## Correlaciones internas relevantes

| Par de variables | r | Advertencia |
|---|---|---|
| `pobreza` ↔ `plp` | ~0.95 | **Muy alta** — no usar ambas en el mismo modelo |
| `pobreza` ↔ `ic_segsoc` | ~0.80 | Alta — considerar excluir una |
| `pobreza_e` ↔ `carencias3` | ~0.90 | **Muy alta** — son conceptualmente similares |
| `pobreza` ↔ `npnv` | ~−0.95 | Complementarias por construcción — no usar juntas |

---

## Variables recomendadas para el modelo predictivo

Selección sugerida para evitar multicolinealidad y maximizar poder explicativo:

| Variable | Justificación |
|---|---|
| `pobreza` | Variable dependiente principal O predictor socioeconómico |
| `pobreza_e` | Captura la dimensión extrema independiente de `pobreza` |
| `ic_rezedu` | Rezago educativo — baja correlación con otras carencias |
| `ic_sbv` | Servicios básicos — complementa a marginación CONAPO |
| `ic_ali` | Carencia alimentaria — independiente de las demás |

> Evitar incluir simultáneamente: `pobreza + plp`, `pobreza_e + carencias3`, `pobreza + npnv`.

---

## Notas de compatibilidad con otros datasets

| Dataset a combinar | Clave en este dataset | Clave en el otro | Transformación necesaria |
|---|---|---|---|
| Marginación CONAPO | `CVEGEO` (construida) | `CVEGEO` (construida) | Ninguna si se construye igual |
| Censo ITER INEGI | `CVEGEO` | `ENTIDAD`+`MUN` | Construir CVEGEO en ITER |
| Incidencia delictiva SESNSP | `clave_entidad` + `clave_municipio` | `CVE_ENT` + `CVE_MUN` | Renombrar columnas |
