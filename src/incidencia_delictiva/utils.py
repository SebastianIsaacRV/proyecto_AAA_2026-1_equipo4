from pathlib import Path


def load_sql(path):
    """Carga un archivo .sql y regresa el query como string."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
    

def save_to_parquet_by_chunks(df, output_dir, chunk_size=1000, prefix="part"):
    """
    Guarda un DataFrame en múltiples archivos parquet por chunks.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    for i in range(0, len(df), chunk_size):
        chunk = df.iloc[i:i + chunk_size]
        file_path = output_dir / f"{prefix}_{i // chunk_size}.parquet"
        chunk.to_parquet(file_path, index=False)
