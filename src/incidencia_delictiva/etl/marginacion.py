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
MARGINACION_RAW_DIR = RAW_DATA_DIR / "marginacion"
MARGINACION_RAW_DIR.mkdir(exist_ok=True)

MARGINACION_PROCESSED_DIR = PROCESSED_DATA_DIR / "marginacion"
MARGINACION_PROCESSED_DIR.mkdir(exist_ok=True)

log = setup_logger(name='etl')


def download_marginacion():
    """Descarga los datos de marginacion/marginación."""
    output_path = MARGINACION_RAW_DIR / "marginacion.csv"

    url_marginacion = r"https://www.datos.gob.mx/dataset/d8f2a534-bcee-4114-853d-82982a81ce24/resource/551d8f48-5d0c-4d11-964a-e2911f732615/download/imm_2020-3.csv"

    download_file(
        url=url_marginacion,
        output_path=output_path
    )

    log.info(f'Archivo descargado en: {output_path}')
    return output_path


def extract_marginacion():
    """Orquesta la descarga (placeholder por si después hay ZIPs o múltiples fuentes)."""
    return download_marginacion()


def read_marginacion():
    """Lee el archivo CSV crudo."""
    filepath = MARGINACION_RAW_DIR / "marginacion.csv"
    assert filepath.exists(), f'El archivo: {filepath} NO existe!'

    df = pd.read_csv(filepath, encoding='latin-1')
    return df


def clean_columns(df):
    """Limpia nombres de columnas."""
    df.columns = (
        df.columns
        .str.lower()
        .str.strip()
        .str.replace(" ", "_")
    )
    return df


def transform_marginacion():
    """Transforma y guarda los datos en parquet."""
    df = read_marginacion()

    df = clean_columns(df)

    df['cvegeo'] = (
            df['cve_ent'].astype(int).astype(str).str.zfill(2) +
            (df['cve_mun'].astype(int) % 1000).astype(str).str.zfill(3)
        )

    column_mapping = {
        'pob_tot': 'poblacion_total',
        'analf': 'porcentaje_analfabetismo',
        'sbasc': 'porcentaje_sin_educacion_basica',
        'ovsde': 'porcentaje_sin_drenaje_ni_excusado',
        'ovsee': 'porcentaje_sin_energia_electrica',
        'ovsae': 'porcentaje_sin_agua_entubada',
        'ovpt': 'porcentaje_con_piso_tierra',
        'vhac': 'porcentaje_viviendas_hacinamiento',
        'pl.5000': 'porcentaje_localidades_menores_5000',
        'po2sm': 'porcentaje_ocupados_hasta_2_salarios_minimos',
        'im_2020': 'indice_marginacion_2020',
        'gm_2020': 'grado_marginacion_2020',
        'imn_2020': 'indice_marginacion_normalizado_2020'
    }

    df = df.rename(columns=column_mapping)

    output_path = MARGINACION_PROCESSED_DIR / "marginacion.parquet"
    df.to_parquet(output_path, index=False)

    log.info(f'Datos transformados guardados en: {output_path}')
    return output_path


def load_marginacion():
    """Carga los datos a DuckDB."""
    parquet_path = MARGINACION_PROCESSED_DIR / "marginacion.parquet"
    assert parquet_path.exists(), f'El archivo: {parquet_path} NO existe!'

    con = duckdb.connect(DATABASE_PATH)

    con.execute(f"""
        CREATE OR REPLACE TABLE marginacion AS 
        SELECT * FROM read_parquet('{parquet_path}')
    """)

    con.close()

    log.info(f'Tabla marginacion cargada en DB: {DATABASE_PATH}')
