from pathlib import Path

import duckdb
from incidencia_delictiva.config import DATABASE_PATH, PROCESSED_DATA_DIR
from incidencia_delictiva.utils import load_sql
from incidencia_delictiva.logger import setup_logger


log = setup_logger('datasets')

QUERIES_DIR = Path(__file__).parent / "queries"


def make_dataset_baseline():
    """Genera el dataset baseline ejecutando el SQL y guardándolo en parquet."""
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


def make_all_datasets():
    """Ejecuta todos los pipelines de datasets."""
    make_dataset_baseline()
    log.info('Todos los datasets fueron generados correctamente.')
    