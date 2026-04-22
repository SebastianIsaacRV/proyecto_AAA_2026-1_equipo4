"""
Funciones utilitarias para descarga y extracción de archivos.
"""

import zipfile
from pathlib import Path

import requests
from tqdm import tqdm

from incidencia_delictiva.logger import setup_logger

log = setup_logger(name='etl')


def download_file(url, output_path, chunk_size=1024):
    """
    Descarga un archivo desde una URL y lo guarda en disco.
    """
    if output_path.exists():
        log.info(f'El archivo ya existe: {output_path}')
        return output_path

    log.info(f'Iniciando descarga desde {url}')
    log.debug(f'Ruta destino: {output_path} | chunk_size: {chunk_size}')

    with requests.get(url, stream=True) as r:
        r.raise_for_status()

        total = int(r.headers.get('content-length', 0))
        log.info(f'Tamaño del archivo: {total} bytes')

        with open(output_path, 'wb') as f, tqdm(
            total=total,
            unit='B',
            unit_scale=True,
            desc=f'Descargando {output_path.name}'
        ) as pbar:

            for chunk in r.iter_content(chunk_size):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))

    log.info(f'Descarga completada: {output_path}')
    return output_path


def unpack_zip(zipfile_path, output_dir_path):
    """
    Extrae un archivo ZIP en un directorio.
    """
    log.info(f'Extrayendo ZIP: {zipfile_path}')
    log.debug(f'Directorio destino: {output_dir_path}')

    extracted_files = []

    with zipfile.ZipFile(zipfile_path) as z:
        members = z.namelist()
        log.info(f'Archivos en el ZIP: {len(members)}')

        for member in members:
            out_path = output_dir_path / member

            if out_path.exists():
                log.debug(f'Se omite archivo existente: {out_path}')
                continue

            log.debug(f'Extrayendo: {member}')
            z.extract(member, output_dir_path)
            extracted_files.append(out_path)

    log.info(f'Extracción completada. Total extraídos: {len(extracted_files)}')
    return extracted_files