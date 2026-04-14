# Predicción de incidencia delictiva municipal en México mediante variables socioeconómicas

**Equipo 4 · Aprendizaje Automático Aplicado · Semestre 2 · 2026-1**

---

## ¿Qué problema se plantea resolver?

En México, la incidencia delictiva varía enormemente entre municipios: algunos registran tasas de criminalidad muy bajas mientras que otros concentran la mayoría de los delitos del país. Sin embargo, los gobiernos municipales —especialmente los más pequeños— no siempre cuentan con herramientas para anticipar qué tan vulnerable es su territorio al crimen antes de que los delitos ocurran.

Este proyecto busca responder una pregunta concreta: **¿es posible predecir la tasa de incidencia delictiva de un municipio a partir de sus condiciones socioeconómicas?** Variables como el porcentaje de población en pobreza, el grado de marginación, el nivel educativo, el hacinamiento en vivienda o el acceso a seguridad social podrían estar asociadas con mayores o menores niveles de criminalidad.

En términos simples: queremos construir un modelo que, dado el perfil socioeconómico de un municipio, estime cuántos delitos por cada 100,000 habitantes se esperan en ese lugar. Esto permitiría identificar municipios en riesgo antes de que la situación se agrave, y orientar recursos de seguridad pública de manera más eficiente.

---

## ¿Por qué es un problema importante?

La seguridad pública es una de las principales demandas ciudadanas en México. Según el SESNSP, entre 2015 y 2025 se han registrado millones de carpetas de investigación a nivel municipal, pero la respuesta institucional suele ser reactiva: se actúa después de que el crimen ocurre, no antes.

Este problema es relevante para múltiples actores:

- **Gobiernos municipales y estatales:** un modelo predictivo les permitiría priorizar inversión en programas sociales y de seguridad en los territorios con mayor riesgo estructural, antes de que se dispare la incidencia.
- **Secretariado Ejecutivo del SNSP:** contar con un perfil socioeconómico asociado al crimen facilita el diseño de políticas públicas basadas en evidencia.
- **Organizaciones de la sociedad civil:** identificar los factores socioeconómicos más asociados al crimen ayuda a focalizar programas de prevención como educación, empleo y vivienda.
- **Academia:** el modelo contribuye al debate sobre las determinantes estructurales del crimen en México, un tema con escasa evidencia cuantitativa a nivel municipal.

La relevancia aumenta si se considera que el 62% de la población municipal vive en pobreza en promedio nacional, y que la correlación entre marginación e incidencia delictiva aún no está bien documentada con datos actualizados del Censo 2020.

---

## ¿Qué problema de aprendizaje implica resolver?

Se trata de un problema de **regresión supervisada**. La variable dependiente (target) es continua:

> **Variable dependiente:** tasa de incidencia delictiva por cada 100,000 habitantes a nivel municipal (calculada a partir de los datos del SESNSP y la población del Censo 2020).

Las **variables independientes** (features) son indicadores socioeconómicos a nivel municipal provenientes de cuatro fuentes:

| Fuente | Variables principales |
|---|---|
| CONAPO – Marginación 2020 | `ANALF`, `SBASC`, `PO2SM`, `VHAC`, `OVPT`, `OVSAE`, `IM_2020` |
| CONEVAL – Pobreza 2020 | `pobreza`, `pobreza_e`, `ic_rezedu`, `ic_sbv`, `ic_ali`, `ic_segsoc` |
| INEGI – Censo 2020 (ITER) | Densidad poblacional, escolaridad promedio, % jóvenes 15–29 años |
| INEGI – ILMM 2020 | Tasa de ocupación, % informalidad laboral |

El modelo base será una **regresión lineal múltiple**, que servirá como línea base (baseline) para comparar con modelos más complejos si el tiempo del proyecto lo permite (regresión Ridge, Lasso o árbol de decisión).

---

## ¿Qué métricas miden la calidad del modelo?

Para un problema de regresión, las métricas principales son:

| Métrica | Fórmula / descripción | Valor deseable |
|---|---|---|
| **R² (coeficiente de determinación)** | Proporción de varianza explicada por el modelo | ≥ 0.50 en entrenamiento; ≥ 0.40 en prueba |
| **RMSE (raíz del error cuadrático medio)** | Error promedio en las mismas unidades que la variable dependiente (delitos/100k hab) | Lo más bajo posible; evaluar relativo a la media de la variable |
| **MAE (error absoluto medio)** | Error promedio sin penalizar outliers | Complementario al RMSE; útil para interpretación |
| **RMSE relativo** | RMSE / media de la variable dependiente | < 30% indica modelo aceptable |

### Valores de referencia esperados

Dado que la tasa de incidencia delictiva tiene alta varianza entre municipios (desde casi 0 hasta más de 5,000 delitos/100k hab), se espera que:

- Un **R² ≥ 0.50** indicaría que las variables socioeconómicas explican al menos la mitad de la variación en criminalidad — resultado relevante y publicable.
- Un **R² entre 0.30 y 0.50** sería aceptable como modelo exploratorio, considerando que el crimen tiene múltiples determinantes no capturados (presencia policial, geografía, crimen organizado).
- Un **R² < 0.30** indicaría que el modelo lineal simple no es suficiente y habría que explorar interacciones o modelos no lineales.

---

## ¿Cómo se alinean las métricas con los objetivos institucionales?

El modelo no busca ser perfecto — busca ser **útil para la toma de decisiones de política pública**. Esta distinción es importante:

| Objetivo institucional | Métrica alineada | Razonamiento |
|---|---|---|
| Identificar municipios en riesgo alto | RMSE bajo + R² aceptable | Un error bajo permite clasificar correctamente los municipios en el cuartil superior de riesgo |
| Priorizar inversión en programas sociales | Coeficientes del modelo (β) interpretables | La regresión lineal permite identificar qué variable socioeconómica tiene mayor impacto en la tasa de crimen |
| Comunicar resultados a tomadores de decisiones no técnicos | MAE en unidades reales | "El modelo se equivoca en promedio por X delitos por cada 100,000 habitantes" es una métrica comprensible para funcionarios |
| Comparar entre regiones del país | R² por estado o región | Evaluar si el modelo funciona mejor en ciertos contextos que en otros |

Un modelo con R² moderado pero coeficientes interpretables y estadísticamente significativos es más valioso para política pública que un modelo de caja negra con R² alto, ya que permite argumentar **qué intervenciones sociales** (reducir pobreza extrema, aumentar escolaridad, reducir informalidad) tendrían mayor impacto esperado en la reducción del crimen.

---

## Datos utilizados

| Dataset | Fuente | Archivo | Municipios |
|---|---|---|---|
| Incidencia delictiva municipal 2015–2025 | SESNSP | `incidencia_delictiva_municipal.csv` | 2,469 |
| Índice de marginación municipal 2020 | CONAPO | `indice_marginacion_municipal_2020.csv` | 2,469 |
| Pobreza municipal 2020 | CONEVAL | `pobreza_municipal_2020.csv` | 2,466 |
| Censo 2020 — ITER | INEGI | `censo_iter_municipios_2020.csv` | 2,469 |
| Indicadores laborales municipales 2020 | INEGI | `indicadores_laborales_municipios.csv` | 2,469 |

La clave de unión entre todos los datasets es `CVEGEO` = `CVE_ENT` (2 dígitos) + `CVE_MUN` (3 dígitos).

---

## Estructura del proyecto

```
proyecto_AAA_2026-1_equipo4/
├── data/
│   └── raw/                  
├── notebooks/
│   ├── 1.0-EDA_marginacion.ipynb
│   └── 1.1-EDA_pobreza.ipynb
├── references/
│   ├── diccionario_marginacion.md
│   └── diccionario_pobreza.md
├── reports/
│   └── figures/
│       ├── marginacion/
│       └── pobreza/
├── src/
│   └── download_datasets.py
└── README.md
```

---

## Equipo

Proyecto desarrollado para la materia **Aprendizaje Automático Aplicado** · Semestre 2 · 2026-1 · Equipo 4.
