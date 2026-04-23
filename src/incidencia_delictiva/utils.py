from pathlib import Path


def load_sql(path):
    """Carga un archivo .sql y regresa el query como string."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()