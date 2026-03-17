"""
download_datasets.py  v2
========================
Fixes aplicados:
  - CONAPO  → verify_ssl=False  (certificado con hostname mismatch)
  - CONEVAL → URL corregida
  - ITER    → timeout=600s para ZIP de ~500 MB

Uso:
    pip install requests tqdm
    python download_datasets.py
    python download_datasets.py --estado 26
"""

import io, os, time, zipfile, argparse, logging, warnings
from pathlib import Path
import requests
from urllib3.exceptions import InsecureRequestWarning

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

# ── Configuración ───────────────────────────────────────────
DATA_DIR        = Path("../data/raw")
LOG_FILE        = Path("download_log.txt")
REQUEST_TIMEOUT = 120
ITER_TIMEOUT    = 600   # ZIP del Censo pesa ~500 MB
MAX_RETRIES     = 3
RETRY_DELAY     = 5

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(),
              logging.FileHandler(LOG_FILE, encoding="utf-8")],
)
log = logging.getLogger(__name__)

# ── Catálogo de datasets ─────────────────────────────────────
DATASETS = [
    {
        "filename": "incidencia_delictiva_municipal.csv",
        "url": "https://repodatos.atdt.gob.mx/api_update/sesnsp/incidencia_delictiva/IDM_NM_dic25.csv",
        "notes": "SESNSP – Incidencia delictiva municipal 2015-2025",
        "cve_ent_col": "CVE_ENT",
    },
    {
        "filename": "incidencia_delictiva_estatal.csv",
        "url": "https://repodatos.atdt.gob.mx/api_update/sesnsp/incidencia_delictiva/INM_estatal_dic25.csv",
        "notes": "SESNSP – Incidencia delictiva estatal 2015-2025",
        "cve_ent_col": "CVE_ENT",
    },
    {
        "filename": "indice_marginacion_municipal_2020.csv",
        "url": "https://www.datos.gob.mx/dataset/d8f2a534-bcee-4114-853d-82982a81ce24/resource/551d8f48-5d0c-4d11-964a-e2911f732615/download/imm_2020-3.csv",
        "notes": "CONAPO – Índice de marginación municipal 2020",
        "cve_ent_col": "CVE_ENT",
        "verify_ssl": False,   # FIX: hostname mismatch en su certificado
    },
    {
        "filename": "pobreza_municipal_2020.csv",
        "url": "https://www.coneval.org.mx/Informes/Pobreza/Datos_abiertos/pobreza_municipal_2010-2020/indicadores de pobreza municipal_2020.csv",
        "notes": "CONEVAL – Indicadores de pobreza municipal 2020",
        "cve_ent_col": "cve_ent",
    },
    {
        "filename": "censo_iter_municipios_2020.csv",
        "url": "https://www.inegi.org.mx/contenidos/programas/ccpv/2020/datosabiertos/iter/iter_00_cpv2020_csv.zip",
        "zip_path": "conjunto_de_datos/conjunto_de_datos_iter_00CSV20.csv",
        "notes": "INEGI – Censo 2020 ITER (~500 MB ZIP, puede tardar varios minutos)",
        "cve_ent_col": "ENTIDAD",
        "timeout": ITER_TIMEOUT,   # FIX: timeout extendido
    },
    {
        "filename": "indicadores_laborales_municipios.csv",
        "url": "https://www.inegi.org.mx/contenidos/programas/ilmm/2020/datosabiertos/ILMM_2020.csv",
        "notes": "INEGI – Indicadores laborales municipales (PEA, ocupación, informalidad)",
        "cve_ent_col": "CVE_ENT",
    },
]

# ── Funciones ────────────────────────────────────────────────

def _make_session():
    s = requests.Session()
    s.headers.update({"User-Agent": "Mozilla/5.0 (compatible; DataScienceBot/1.0)"})
    return s


def download_raw(url, session, verify_ssl=True, timeout=REQUEST_TIMEOUT, retries=MAX_RETRIES):
    if not verify_ssl:
        warnings.filterwarnings("ignore", category=InsecureRequestWarning)
        log.warning("  SSL verification desactivado para este dominio.")

    for attempt in range(1, retries + 1):
        try:
            resp = session.get(url, timeout=timeout, stream=True, verify=verify_ssl)
            resp.raise_for_status()

            total = int(resp.headers.get("content-length", 0))
            buf = io.BytesIO()

            if TQDM_AVAILABLE and total:
                with tqdm(total=total, unit="B", unit_scale=True, desc="  bytes") as bar:
                    for chunk in resp.iter_content(chunk_size=65536):
                        buf.write(chunk); bar.update(len(chunk))
            else:
                downloaded = 0
                for chunk in resp.iter_content(chunk_size=65536):
                    buf.write(chunk)
                    downloaded += len(chunk)
                    if downloaded % (10 * 1024 * 1024) < 65536:
                        log.info(f"  ... {downloaded/1024/1024:.1f} MB descargados")

            return buf.getvalue()

        except requests.RequestException as exc:
            log.warning(f"  Intento {attempt}/{retries} fallido: {exc}")
            if attempt < retries:
                time.sleep(RETRY_DELAY)
            else:
                raise


def extract_from_zip(raw_bytes, zip_path):
    with zipfile.ZipFile(io.BytesIO(raw_bytes)) as zf:
        names = zf.namelist()
        target_name = zip_path.lower().split("/")[-1]
        target = next((n for n in names if n.lower().endswith(target_name)), None)
        if target is None:
            raise FileNotFoundError(
                f"No se encontró '{zip_path}' en el ZIP.\n"
                f"Archivos disponibles:\n  " + "\n  ".join(names[:20])
            )
        log.info(f"  Extrayendo '{target}' del ZIP…")
        return zf.read(target)


def filter_by_estado(csv_bytes, col, cve_ent):
    lines = csv_bytes.decode("latin-1", errors="replace").splitlines()
    if not lines:
        return csv_bytes
    header = lines[0]
    cols = [c.strip().strip('"') for c in header.split(",")]
    try:
        idx = cols.index(col)
    except ValueError:
        log.warning(f"  Columna '{col}' no encontrada; guardando CSV completo.")
        return csv_bytes
    filtered = [header] + [
        row for row in lines[1:]
        if len(row.split(",")) > idx
        and row.split(",")[idx].strip().strip('"').zfill(2) == cve_ent.zfill(2)
    ]
    log.info(f"  Filtrado: {len(filtered)-1} registros para CVE_ENT={cve_ent}.")
    return "\n".join(filtered).encode("utf-8")


def save_dataset(entry, cve_ent, session):
    dest = DATA_DIR / entry["filename"]
    log.info(f"\n{'─'*60}")
    log.info(f"Dataset : {entry['filename']}")
    log.info(f"Fuente  : {entry.get('notes', '')}")
    log.info(f"URL     : {entry['url']}")

    raw = download_raw(
        url=entry["url"], session=session,
        verify_ssl=entry.get("verify_ssl", True),
        timeout=entry.get("timeout", REQUEST_TIMEOUT),
    )
    log.info(f"  Descargado: {len(raw)/1024:.1f} KB")

    if entry.get("zip_path"):
        raw = extract_from_zip(raw, entry["zip_path"])
        log.info(f"  Extraído CSV: {len(raw)/1024:.1f} KB")

    if cve_ent and entry.get("cve_ent_col"):
        raw = filter_by_estado(raw, entry["cve_ent_col"], cve_ent)

    dest.write_bytes(raw)
    log.info(f"  ✓ Guardado en: {dest}")

# ── Main ─────────────────────────────────────────────────────

def main():
    global DATA_DIR

    parser = argparse.ArgumentParser()
    parser.add_argument("--estado", type=str, default=None,
                        help="CVE_ENT de 2 dígitos. Ej: 26 = Sonora")
    parser.add_argument("--output-dir", type=str, default=None,
                        help="Carpeta de destino (default: ../data/raw)")
    args = parser.parse_args()

    if args.output_dir:
        DATA_DIR = Path(args.output_dir)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    cve_ent = args.estado
    log.info(f"Modo: {'CVE_ENT=' + cve_ent if cve_ent else 'descarga nacional completa'}")

    session = _make_session()
    errores = []

    for entry in DATASETS:
        try:
            save_dataset(entry, cve_ent, session)
        except Exception as exc:
            log.error(f"  ✗ ERROR en '{entry['filename']}': {exc}")
            errores.append((entry["filename"], str(exc)))

    log.info(f"\n{'═'*60}")
    if errores:
        log.warning(f"Datasets con error ({len(errores)}):")
        for nombre, msg in errores:
            log.warning(f"  - {nombre}: {msg}")
    else:
        log.info("Todos los datasets descargados correctamente ✓")

if __name__ == "__main__":
    main()