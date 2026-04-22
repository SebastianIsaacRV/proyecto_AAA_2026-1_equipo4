from datetime import datetime

from incidencia_delictiva.etl.geograficos import (
    extract_geodata, 
    transform_geodata, 
    load_geodata
)
from incidencia_delictiva.etl.pobreza import (
    extract_pobreza, 
    transform_pobreza, 
    load_pobreza
)
from incidencia_delictiva.etl.marginacion import (
    extract_marginacion, 
    transform_marginacion, 
    load_marginacion
)

from incidencia_delictiva.etl.delitos import (
    extract_delitos, 
    transform_delitos, 
    load_delitos, 
    transform_and_load_delitos_chunks
)
from incidencia_delictiva.logger import setup_logger


log = setup_logger(name='etl')


def run_geodata_pipeline(): 
    start = datetime.now()
    log.info('Inicia proceso ETL-GeoData')
    _ = extract_geodata()
    _ = transform_geodata()
    _ = load_geodata()
    elapsed = (datetime.now() - start).total_seconds()
    log.info(f'Proceso ETL-GeoData completado en {elapsed:.2f} s')


def run_pobreza_pipeline(): 
    start = datetime.now()
    log.info('Inicia proceso ETL-Pobreza')
    _ = extract_pobreza()
    _ = transform_pobreza()
    _ = load_pobreza()
    elapsed = (datetime.now() - start).total_seconds()
    log.info(f'Proceso ETL-Pobreza completado en {elapsed:.2f} s')


def run_marginacion_pipeline():
    start = datetime.now()
    log.info('Inicia proceso ETL-Marginación')
    _ = extract_marginacion()
    _ = transform_marginacion()
    _ = load_marginacion()
    elapsed = (datetime.now() - start).total_seconds()
    log.info(f'Proceso ETL-Marginación completado en {elapsed:.2f} s')


def run_delitos_pipeline():
    start = datetime.now()
    log.info('Inicia proceso ETL-Delitos')
    _ = extract_delitos()
    # _ = transform_delitos()
    # _ = load_delitos()
    _ = transform_and_load_delitos_chunks()
    elapsed = (datetime.now() - start).total_seconds()
    log.info(f'Proceso ETL-Delitos completado en {elapsed:.2f} s')


def run_all_pipelines(): 
    _ = run_geodata_pipeline()
    _ = run_pobreza_pipeline()
    _ = run_marginacion_pipeline()
    _ = run_delitos_pipeline()
