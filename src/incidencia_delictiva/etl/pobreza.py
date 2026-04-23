import pandas as pd
import duckdb

from incidencia_delictiva.etl.etl_utils import download_file
from incidencia_delictiva.logger import setup_logger
from incidencia_delictiva.config import (
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR, 
    DATABASE_PATH
)

# Paths
POBREZA_RAW_DIR = RAW_DATA_DIR / "pobreza"
POBREZA_RAW_DIR.mkdir(exist_ok=True)

POBREZA_PROCESSED_DIR = PROCESSED_DATA_DIR / "pobreza"
POBREZA_PROCESSED_DIR.mkdir(exist_ok=True)

log = setup_logger(name='etl')


# URLs
URL_INDICADORES = r"https://www.datos.gob.mx/dataset/b6981ccc-083b-4e57-ba6f-d800a7398fa8/resource/6e409e3a-aa08-45f5-b84b-f5d8cc6fafa8/download/pobreza_municipal.csv" 
URL_GRUPO_RESIDENCIA = r"https://www.datos.gob.mx/dataset/b6981ccc-083b-4e57-ba6f-d800a7398fa8/resource/7301b6f1-07a1-4c6a-9f29-bdccf6e2cf54/download/pobreza_grupos_poblacionales_rural_urbano.csv"


def download_pobreza_data():
    """Descarga los datasets de pobreza desde las fuentes oficiales."""
    
    files = {
        'indicadores': download_file(
            url=URL_INDICADORES,
            output_path=POBREZA_RAW_DIR / "indicadores.csv"
        ),
        'grupo_residencia': download_file(
            url=URL_GRUPO_RESIDENCIA,
            output_path=POBREZA_RAW_DIR / "grupo_residencia.csv"
        )
    }

    return files


def extract_pobreza():
    """Orquesta la descarga de datos."""
    return download_pobreza_data()


def read_pobreza_data():
    """Lee los archivos CSV descargados."""
    
    paths = {
        'indicadores': POBREZA_RAW_DIR / "indicadores.csv",
        'grupo_residencia': POBREZA_RAW_DIR / "grupo_residencia.csv"
    }

    for name, path in paths.items():
        assert path.exists(), f'El archivo {name} NO existe en {path}'

    data = {
        'indicadores': pd.read_csv(paths['indicadores']),
        'grupo_residencia': pd.read_csv(paths['grupo_residencia'])
    }

    return data


def clean_columns(df):
    """Estandariza nombres de columnas."""
    df.columns = df.columns.str.lower().str.strip()
    return df


def add_cvegeo(df):
    df['cvegeo'] = (
        df['clave_entidad'].astype(str).str.zfill(2) +
        df['clave_municipio'].astype(str).str.zfill(3)
    )
    return df


def select_periodo(df): 
    return df.query("periodo == '2020-01-01'")


def transform_indicadores(df):
    """Transformaciones específicas para indicadores."""

    # Selecciona periodo 2020-01-01
    df = select_periodo(df)

    df = clean_columns(df)

    # Columnas base
    base_columns = ['clave_entidad', 'entidad_federativa', 'clave_municipio', 'municipio'  ]
    
    # Columnas limpias
    fn_columns = [col for col in df.columns if str(col).startswith('fn')]

    columns_out = base_columns + fn_columns

    # Selecciona columnas útiles
    df = df[columns_out]

    # Crear columna cvegeo
    df = add_cvegeo(df)

    return df


def transform_grupo_residencia(df):
    """Transformaciones específicas para grupo residencia."""

    # Selecciona periodo 2020-01-01
    df = select_periodo(df)

    df = clean_columns(df)

    # Crear columna cvegeo
    df = add_cvegeo(df)

    # Filtrar parte de string útil
    df['grupo'] = df['grupo'].str.split(':').str[-1].str.strip().astype(str)

    # Filtrar columnas útiles
    columns_to_remove = [
        'clave_entidad', 
        'entidad_federativa', 
        'clave_municipio',
        'municipio', 
        'periodo', 
        'entidad_federativa_etq', 
        'periodo', 
        'entidad'
    ]
    
    df = df.drop(columns=columns_to_remove)

    # Pivotar por grupo
    df_pivot = df.pivot_table(
        index='cvegeo', 
        columns='grupo', 
        values=df.columns.tolist(), 
        aggfunc='first'
    )

    # Renombrar columnas por grupo
    df_pivot.columns = [
        f'{col}_{grupo}' for col, grupo in df_pivot.columns
    ]

    df_pivot = df_pivot.reset_index()

    cols_drop = ['grupo_rural', 'grupo_urbano', 'cvegeo_rural', 'cvegeo_urbano']

    df_pivot = df_pivot.drop(columns=cols_drop, errors='ignore')

    return df_pivot


def transform_pobreza():
    """Transforma todos los datasets y los guarda en parquet."""
    
    data = read_pobreza_data()

    indicadores = transform_indicadores(data['indicadores'])
    grupo_residencia = transform_grupo_residencia(data['grupo_residencia'])

    # Merge indicadores y grupo residencia
    pobreza = indicadores.merge(grupo_residencia, on='cvegeo', how='left')

    indidcadores_path = POBREZA_PROCESSED_DIR / "indicadores.parquet"
    grupo_residencia_path = POBREZA_PROCESSED_DIR / "grupo_residencia.parquet"
    output_path = POBREZA_PROCESSED_DIR / "pobreza.parquet"
    
    indicadores.to_parquet(indidcadores_path, index=False)
    grupo_residencia.to_parquet(grupo_residencia_path, index=False)
    pobreza.to_parquet(output_path, index=False)

    log.info(f'Datos de pobreza transformados guardados en: {POBREZA_PROCESSED_DIR}')

    return output_path


def load_pobreza():
    """Carga los datasets de pobreza en DuckDB."""
    
    parquet_path = POBREZA_PROCESSED_DIR / "pobreza.parquet"
    assert parquet_path.exists(), f'El archivo: {parquet_path} NO existe!'
    
    con = duckdb.connect(DATABASE_PATH)

    con.execute(f"""
        CREATE OR REPLACE TABLE pobreza AS 
        SELECT * FROM read_parquet('{parquet_path}')
    """)

    con.close()

    log.info(f'Datos de pobreza cargados en DB: {DATABASE_PATH}')
