from pathlib import Path

import duckdb
import pandas as pd
import geopandas as gpd
from shapely import wkt

from incidencia_delictiva.config import DATABASE_PATH, PROCESSED_DATA_DIR
from incidencia_delictiva.utils import load_sql, save_to_parquet_by_chunks
from incidencia_delictiva.features.spatial import (
    compute_densidad_poblacional, 
    build_neighbors, 
    compute_num_vecinos, 
    compute_spatial_lag, 
    compute_es_frontera,
    compute_min_distance
)
from incidencia_delictiva.logger import setup_logger


log = setup_logger('datasets')

QUERIES_DIR = Path(__file__).parent / "queries"


def make_dataset_baseline():
    """Genera el dataset baseline."""
    output_file = PROCESSED_DATA_DIR / "dataset_baseline.parquet"

    query = load_sql(QUERIES_DIR / "dataset_baseline.sql")

    con = duckdb.connect(DATABASE_PATH)

    con.execute(f"""
        COPY (
            {query}
        ) TO '{output_file}' (FORMAT PARQUET);
    """)

    con.close()

    log.info(f'dataset_baseline generado en: {output_file}')


def make_dataset_geospatial():
    """Genera el dataset con features enriquecido con datos geospaciales."""
    output_dir = PROCESSED_DATA_DIR / "dataset_geospatial"

    dataset_baseline_path = PROCESSED_DATA_DIR / "dataset_baseline.parquet"
    df = pd.read_parquet(dataset_baseline_path)

    geodata_path = PROCESSED_DATA_DIR / "geo" / "geodata.parquet"
    gdf_geo = gpd.read_parquet(geodata_path)

    columns_geo = [
        'cvegeo',
        'geometry',
    ]
    gdf_geo = gdf_geo[columns_geo]

    gdf = df.merge(gdf_geo, on='cvegeo', how='left')

    gdf = gpd.GeoDataFrame(gdf, geometry='geometry')

    # Elimina columna es_frontera
    gdf = gdf.drop(columns='es_frontera')

    gdf = compute_es_frontera(gdf)

    # Calcula densidad poblacional
    gdf['densidad_poblacional'] = compute_densidad_poblacional(gdf)

    # Computa vecinos
    df_vecinos = build_neighbors(gdf)


    num_vecinos = compute_num_vecinos(df_vecinos)
    
    gdf = gdf.merge(num_vecinos, on='cvegeo', how='left')

    # Lags espaciales
    lag_delitos = compute_spatial_lag(
        gdf, df_vecinos,
        value_col='tasa_delitos',
        new_name='lag_delitos'
    )
    
    lag_marginacion = compute_spatial_lag(
        gdf, df_vecinos,
        value_col='indice_marginacion_normalizado_2020',
        new_name='lag_marginacion'
    )
    
    gdf = gdf.merge(lag_delitos, on=['cvegeo', 'año'], how='left')
    gdf = gdf.merge(lag_marginacion, on=['cvegeo', 'año'], how='left')

    # Distancias
    dist_frontera = compute_min_distance(
        gdf, 
        condition_col='es_frontera', 
        new_name='distancia_frontera', 
    )

    dist_zm = compute_min_distance(
        gdf, 
        condition_col='zona_metropolitana', 
        new_name='distancia_zm'
    )

    gdf = gdf.merge(dist_frontera, on="cvegeo", how='left')
    gdf = gdf.merge(dist_zm, on="cvegeo", how='left')

    save_to_parquet_by_chunks(gdf, output_dir, chunk_size=5000)

    log.info(f'dataset_geospatial generado en: {output_dir}')


def make_all_datasets():
    """Ejecuta todos los pipelines de datasets."""
    make_dataset_baseline()
    make_dataset_geospatial()
    log.info('Todos los datasets fueron generados correctamente.')
