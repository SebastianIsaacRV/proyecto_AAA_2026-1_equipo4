import numpy as np
import pandas as pd
import geopandas as gpd
from libpysal.weights import Queen


def compute_densidad_poblacional(df):
    return df['poblacion_total'] / df['area_km2']


def build_neighbors(gdf):
    gdf_unique = gdf.drop_duplicates('cvegeo').reset_index(drop=True)
    
    w = Queen.from_dataframe(gdf_unique)
    
    rows = []
    for i, neighbors in w.neighbors.items():
        cvegeo = gdf_unique.iloc[i]['cvegeo']
        for n in neighbors:
            vecino = gdf_unique.iloc[n]['cvegeo']
            rows.append((cvegeo, vecino))
    
    return pd.DataFrame(rows, columns=['cvegeo', 'vecino'])


def compute_num_vecinos(df_vecinos):
    return (
        df_vecinos
        .groupby('cvegeo')
        .size()
        .reset_index(name='num_vecinos')
    )


def compute_spatial_lag(df, df_vecinos, value_col, new_name):
    
    df_base = df[['cvegeo', 'año', value_col]].copy()
    
    df_lag = df_base.merge(df_vecinos, on='cvegeo')
    
    df_lag = df_lag.merge(
        df_base,
        left_on=['vecino', 'año'],
        right_on=['cvegeo', 'año'],
        suffixes=('', '_vecino')
    )
    
    lag = (
        df_lag
        .groupby(['cvegeo', 'año'])[f'{value_col}_vecino']
        .mean()
        .reset_index()
        .rename(columns={f'{value_col}_vecino': new_name})
    )
    
    return lag


def compute_min_distance(gdf, condition_col, new_name):
    
    gdf_unique = gdf.drop_duplicates('cvegeo').copy()
    gdf_unique['centroid'] = gdf_unique.geometry.centroid
    
    target = gdf_unique[gdf_unique[condition_col] == 1]
    base = gdf_unique.copy()
    
    def min_dist(point):
        return target['centroid'].distance(point).min()
    
    base[new_name] = base['centroid'].apply(min_dist)
    
    return base[['cvegeo', new_name]]


def compute_es_frontera(gdf): 
    import warnings
    warnings.filterwarnings('ignore')

    # Carga mapamunidi
    url = "https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip"
    world = gpd.read_file(url)

    # Filtra territorios: Mexico, USA, Belize, Guatemala
    mexico = world[world.NAME == 'Mexico']
    usa = world[world.NAME == 'United States of America']
    guatemala = world[world.NAME == 'Guatemala']
    belize = world[world.NAME == 'Belize']

    # Computa lineas de frontera
    frontera_norte = mexico.geometry.boundary.intersection(usa.geometry.unary_union)
    frontera_sur = mexico.geometry.boundary.intersection(
        guatemala.geometry.unary_union.union(belize.geometry.unary_union)
    )

    municipios = gdf[['cvegeo', 'geometry']].drop_duplicates('cvegeo').copy()
    municipios = municipios.to_crs(mexico.crs)

    # Computa intersecciones
    municipios_norte = municipios[municipios.intersects(frontera_norte.buffer(0.1).unary_union)]
    municipios_sur = municipios[municipios.intersects(frontera_sur.buffer(0.1).unary_union)]

    # Municipios frontera
    municipios_frontera = (
        municipios_norte.cvegeo.tolist() + 
        municipios_sur.cvegeo.tolist()
    )

    gdf['es_frontera'] = np.where(gdf.cvegeo.isin(municipios_frontera), 1, 0)
    return gdf
