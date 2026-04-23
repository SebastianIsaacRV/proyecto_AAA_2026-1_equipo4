WITH delitos_agregados AS (
    SELECT
        año,
        cvegeo,
        SUM(total_anual) AS total_delitos
    FROM delitos
    GROUP BY año, cvegeo
),

base AS (
    SELECT
        d.año,
        d.cvegeo,

        d.total_delitos,

        m.poblacion_total,
        m.indice_marginacion_normalizado_2020,
        m.porcentaje_analfabetismo,
        m.porcentaje_sin_agua_entubada,
        m.porcentaje_viviendas_hacinamiento,

        p.fn_pobreza_porcentaje,
        p.fn_pobreza_extrema_porcentaje,
        p.fn_vulnerable_ingresos_porcentaje,
        p.fn_carencia_seguridad_social_porcentaje,
        p.fn_poblacion,
        p.poblacion_urbano,

        g.nomgeo,
        g.area_km2,
        g.region,
        g.zona_metropolitana,
        g.es_frontera

    FROM delitos_agregados d

    LEFT JOIN marginacion m ON d.cvegeo = m.cvegeo
    LEFT JOIN pobreza p ON d.cvegeo = p.cvegeo
    LEFT JOIN geodata g ON d.cvegeo = g.cvegeo
),

features AS (
    SELECT
        *,
        (total_delitos * 100000.0) / NULLIF(poblacion_total, 0) AS tasa_delitos,
        (poblacion_urbano * 1.0) / NULLIF(fn_poblacion, 0) AS prop_urbano
    FROM base
)

SELECT *
FROM features
WHERE poblacion_total IS NOT NULL