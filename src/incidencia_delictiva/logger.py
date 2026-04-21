# logger.py
"""
Logger configurable con salida a consola y archivo.
"""
import sys

from loguru import logger

from incidencia_delictiva.config import LOGS_DIR


def setup_logger(
        name='log',
        level='DEBUG',
        log_dir=LOGS_DIR, 
        rotation='10 MB', 
        retention='7 days'
):
    """
    Configura logger con salida a consola y archivo.

    Args:
        name (str): Nombre del proceso (ej: 'etl', 'api', etc.)
        log_dir (str): Directorio donde guardar logs (default: ~/logs)
        level (str): Nivel de logging
        rotation (str): Tamaño/tiempo para rotación de logs
        retention (str): Tiempo de retención de logs
    """

    # Remove default config
    logger.remove()

    # Logger file
    log_file = log_dir / f"{name}.log"

    # base format
    log_format = (
        '<green>{time:YYYY-MM-DD HH:mm:ss}</green> | '
        '<level>{level: <8}</level> | '
        '<magenta>{extra[process]}</magenta> | '
        '<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - '
        '<level>{message}</level>'
    )

    # Loguru handler
    logger.add(
        sys.stdout,
        level=level,
        format=log_format,
        colorize=True,
    )

    # File logger
    logger.add(
        log_file, 
        level=level, 
        format=log_format, 
        rotation=rotation, 
        retention=retention, encoding='utf-8'
    )

    return logger.bind(process=name)


# Global logger
log = setup_logger()


if __name__ == "__main__":
    log.info('Init logger')
    log.debug('Debug message')
    log.warning('Warning message')
    log.error('Error message')
    log.critical('Critical message')