# Diccionario de datos — Índice de Marginación Municipal 2020

**Fuente:** Consejo Nacional de Población (CONAPO)  
**Archivo:** `data/raw/indice_marginacion_municipal_2020.csv`  
**Cobertura:** 2,469 municipios · Nacional  
**Año de referencia:** 2020  
**Encoding:** UTF-8  
**Valores nulos:** Ninguno  

---

## Claves geográficas

| Variable | Tipo | Descripción | Ejemplo |
|---|---|---|---|
| `CVE_ENT` | int | Clave de entidad federativa (2 dígitos) | `26` = Sonora |
| `NOM_ENT` | str | Nombre de la entidad federativa | `Sonora` |
| `CVE_MUN` | int | Clave del municipio (4 dígitos: ENT+MUN) | `26001` |
| `NOM_MUN` | str | Nombre del municipio | `Aconchi` |

> **Para construir CVEGEO** (clave única de 5 dígitos usada en merges):
> ```python
> df["CVEGEO"] = df["CVE_ENT"].astype(str).str.zfill(2) + \
>                df["CVE_MUN"].astype(str).str.zfill(3)
> ```
> Nota: `CVE_MUN` en este dataset ya viene como 4 dígitos (ej. `1001`), por lo que hay que extraer solo los últimos 3 para construir el CVEGEO estándar.

---

## Variables socioeconómicas (porcentajes)

Todas las variables de porcentaje refieren a la **población o viviendas en esa situación** dentro del municipio.

| Variable | Tipo | Descripción | Min | Media | Max |
|---|---|---|---|---|---|
| `POB_TOT` | int | Población total del municipio | 81 | 51,038 | 1,922,523 |
| `ANALF` | float | % de población de 15 años o más analfabeta | 0.35 | 10.16 | 53.07 |
| `SBASC` | float | % de población de 15 años o más sin educación básica completa | 5.54 | 45.85 | 88.33 |
| `OVSDE` | float | % de ocupantes en viviendas sin drenaje ni excusado | 0.00 | 3.16 | 64.45 |
| `OVSEE` | float | % de ocupantes en viviendas sin energía eléctrica | 0.00 | 1.50 | 53.07 |
| `OVSAE` | float | % de ocupantes en viviendas sin agua entubada | 0.00 | 6.12 | 81.79 |
| `OVPT` | float | % de ocupantes en viviendas con piso de tierra | 0.00 | 7.99 | 68.15 |
| `VHAC` | float | % de viviendas con hacinamiento (>2.5 personas/cuarto) | 3.95 | 26.57 | 69.56 |
| `PL.5000` | float | % de población que vive en localidades menores a 5,000 habitantes | 0.00 | 69.90 | 100.00 |
| `PO2SM` | float | % de población ocupada con ingresos de hasta 2 salarios mínimos | 28.45 | 82.14 | 100.00 |

---

## Índices calculados

| Variable | Tipo | Descripción | Rango | Interpretación |
|---|---|---|---|---|
| `IM_2020` | float | Índice de marginación 2020 (componente principal de las variables anteriores) | 21.4 – 62.4 | **Mayor valor = MENOS marginado** |
| `GM_2020` | str | Grado de marginación categorizado en 5 niveles | — | Ver tabla de grados |
| `IMN_2020` | float | Índice de marginación normalizado entre 0 y 1 | 0.335 – 0.977 | Mayor = menos marginado |

### Grados de marginación (`GM_2020`)

| Grado | Municipios | % del total | Rango IM_2020 aproximado |
|---|---|---|---|
| Muy alto | 204 | 8.3% | 21 – 38 |
| Alto | 586 | 23.7% | 38 – 48 |
| Medio | 494 | 20.0% | 48 – 52 |
| Bajo | 530 | 21.5% | 52 – 57 |
| Muy bajo | 655 | 26.5% | 57 – 62 |

---

## Correlaciones relevantes con `% pobreza` (CONEVAL)

> Calculadas al hacer merge con el dataset de pobreza municipal.

| Variable | r con pobreza | Interpretación |
|---|---|---|
| `PO2SM` | +0.814 | **Más fuerte** — ingresos bajos predicen pobreza |
| `VHAC` | +0.757 | Hacinamiento ligado a pobreza |
| `ANALF` | +0.703 | Analfabetismo correlaciona con pobreza |
| `SBASC` | +0.674 | Baja escolaridad asociada a pobreza |
| `OVPT` | +0.618 | Vivienda precaria ligada a pobreza |
| `IM_2020` | −0.741 | Negativa porque escala está invertida |

---

## Notas de uso para el modelo predictivo

- `IM_2020` e `IMN_2020` son prácticamente idénticos (r = 1.0) — usar solo uno.
- `PO2SM` y `ANALF` son los predictores más potentes para incluir como variables independientes.
- `SBASC` y `ANALF` están muy correlacionadas entre sí (multicolinealidad) — considerar usar solo una.
- Para análisis de Sonora: el rango de variación es mucho menor que el nacional, lo que puede reducir el poder explicativo del modelo.
- El dataset no tiene valores nulos — se puede usar directamente sin imputación.
