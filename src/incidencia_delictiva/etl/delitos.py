import pandas as pd
import duckdb
from tqdm import tqdm

from incidencia_delictiva.etl.etl_utils import download_file
from incidencia_delictiva.logger import setup_logger
from incidencia_delictiva.config import (
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR, 
    DATABASE_PATH
)

# Paths
DELITOS_RAW_DIR = RAW_DATA_DIR / "delitos"
DELITOS_RAW_DIR.mkdir(exist_ok=True)

DELITOS_PROCESSED_DIR = PROCESSED_DATA_DIR / "delitos"
DELITOS_PROCESSED_DIR.mkdir(exist_ok=True)

log = setup_logger(name='etl')


def download_delitos():
    """Descarga los datos de incidencia delictiva."""
    output_path = DELITOS_RAW_DIR / "delitos.csv"

    url_delitos = r"https://repodatos.atdt.gob.mx/api_update/sesnsp/incidencia_delictiva/IDM_NM_dic25.csv"

    download_file(
        url=url_delitos,
        output_path=output_path
    )

    log.info(f'Archivo descargado en: {output_path}')
    return output_path


def extract_delitos():
    """Orquesta la descarga (placeholder por si después hay múltiples fuentes)."""
    return download_delitos()


def read_delitos():
    """Lee el archivo CSV crudo."""
    filepath = DELITOS_RAW_DIR / "delitos.csv"
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


def transform_delitos():
    """Transforma y guarda los datos en parquet."""
    df = read_delitos()

    df = clean_columns(df)

    df['cvegeo'] = (
        df['clave_ent'].astype(str).str.zfill(2) +
        df['cve._municipio'].astype(str).str.zfill(3)
        )

    output_path = DELITOS_PROCESSED_DIR / "delitos.parquet"
    df.to_parquet(output_path, index=False)

    log.info(f'Datos transformados guardados en: {output_path}')
    return output_path


def load_delitos():
    """Carga los datos a DuckDB."""
    parquet_path = DELITOS_PROCESSED_DIR / "delitos.parquet"
    assert parquet_path.exists(), f'El archivo: {parquet_path} NO existe!'

    con = duckdb.connect(DATABASE_PATH)

    con.execute(f"""
        CREATE OR REPLACE TABLE delitos AS 
        SELECT * FROM read_parquet('{parquet_path}')
    """)

    con.close()

    log.info(f'Tabla delitos cargada en DB: {DATABASE_PATH}')


def transform_and_load_delitos_chunks():
    """Procesa en chunks y carga directo a DuckDB."""
    filepath = DELITOS_RAW_DIR / "delitos.csv"
    output_path = DELITOS_PROCESSED_DIR / "delitos.parquet"

    con = duckdb.connect(DATABASE_PATH)

    con.execute("DROP TABLE IF EXISTS delitos")

    chunks = pd.read_csv(filepath, encoding='latin-1', chunksize=100_000)

    for i, chunk in enumerate(tqdm(chunks, desc="Procesando chunks")):
        chunk = clean_columns(chunk)

        # Calcula el total de delitos
        chunk['total_anual'] = chunk.loc[:, 'enero':'diciembre'].sum(axis=1)

        chunk['cvegeo'] = (
            chunk['clave_ent'].astype(int).astype(str).str.zfill(2) +
            (chunk['cve._municipio'].astype(int) % 1000).astype(str).str.zfill(3)
        )

        con.register("temp_chunk", chunk)

        if i == 0:
            con.execute("CREATE TABLE delitos AS SELECT * FROM temp_chunk")
        else:
            con.execute("INSERT INTO delitos SELECT * FROM temp_chunk")
    
    log.info(f'Datos transformados guardados en: {output_path}')
    con.execute(f"COPY delitos TO '{output_path}' (FORMAT PARQUET)")

    con.close()

    log.info(f'Tabla delitos cargada en DB: {DATABASE_PATH}')

