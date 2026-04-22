import geopandas as gpd
import duckdb

from incidencia_delictiva.etl.etl_utils import download_file, unpack_zip
from incidencia_delictiva.logger import setup_logger
from incidencia_delictiva.config import (
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR, 
    DATABASE_PATH
)

# Paths
GEO_RAW_DIR = RAW_DATA_DIR / "geo" 
GEO_RAW_DIR.mkdir(exist_ok=True)

GEO_PROCESSED_DIR = PROCESSED_DATA_DIR / "geo"
GEO_PROCESSED_DIR.mkdir(exist_ok=True)

log = setup_logger(name='etl')


def download_geodata():
    """Descarga el archivo ZIP de datos geográficos desde la fuente oficial."""
    url_mpios_zip = r"http://www.conabio.gob.mx/informacion/gis/maps/geo/mun22gw.zip"
    zipfile_mpios = download_file(
        url=url_mpios_zip, 
        output_path=GEO_RAW_DIR / "mpios.zip"
    )
    return zipfile_mpios


def unzip_geodata(clean=True):
    """Descomprime el archivo ZIP descargado y opcionalmente elimina el archivo original."""
    zipfile_mpios = GEO_RAW_DIR / "mpios.zip"
    assert zipfile_mpios.exists(), f'El archivo: {zipfile_mpios} NO existe!'
    
    extracted_files = unpack_zip(zipfile_mpios, GEO_RAW_DIR)
    
    if clean:
        zipfile_mpios.unlink()
        log.info(f'Archivo: {zipfile_mpios} eliminado')

    return extracted_files


def extract_geodata(): 
    """Orquesta la descarga de datos."""
    download_geodata()
    unzip_geodata()
    


def add_region(gdf):
    """Agrega la columna de región basada en la clave de entidad."""
    region_map = {
        # Noroeste
        '02': 'noroeste', '03': 'noroeste',
        '25': 'noroeste', '26': 'noroeste',

        # Norte
        '05': 'norte', '08': 'norte',

        # Noreste
        '19': 'noreste', '28': 'noreste',

        # Occidente
        '14': 'occidente', '16': 'occidente',
        '18': 'occidente', '32': 'occidente',
        '06': 'occidente',

        # Centro-Norte
        '01': 'centro-norte', '10': 'centro-norte',
        '24': 'centro-norte',

        # Centro-Sur
        '09': 'centro-sur', '11': 'centro-sur',
        '13': 'centro-sur', '15': 'centro-sur',
        '17': 'centro-sur', '21': 'centro-sur',
        '22': 'centro-sur', '29': 'centro-sur',

        # Sur
        '07': 'sur', '12': 'sur', '20': 'sur',

        # Sureste
        '04': 'sureste', '23': 'sureste',
        '27': 'sureste', '30': 'sureste',
        '31': 'sureste'
    }
    gdf['cve_ent'] = gdf['cve_ent'].astype(str).str.zfill(2)
    gdf['region'] = gdf['cve_ent'].map(region_map)
    
    return gdf


def add_es_frontera(gdf):
    """Marca si el municipio pertenece a una entidad fronteriza."""
    frontera_norte = [
        '02', '26', '08',
        '05', '19', '28'
    ]

    frontera_sur = [
        '07', '27', '04', '23'
    ] 

    gdf['es_frontera'] = gdf['cve_ent'].isin(frontera_norte + frontera_sur).astype(int)

    return gdf


def add_zona_metropolitana(gdf): 
    """Agrega indicadores de zona metropolitana y su nombre."""
    zm_map = {
        'aguas_calientes': ['01001', '01005'], 
        'tijuana': ['01001', '02005'], 
        'monclova': ['05006', '05010', '05018'], 
        'piedras_negras': ['05025', '05022'], 
        'saltillo': ['05004', '05027', '05030'], 
        'la_laguna': ['05017', '05035', '10007', '10012'], 
        'colima_villa_alvarez': ['06002', '06010'], 
        'tecoman': ['06001', '06009'],
        'tuxtla': ['07027', '07101'],
        'chuhuahua': ['08002', '08004', '08019'], 
        'juarez': ['08037'], 
        
        'valle_de_mexico': [
            '15038', '15039', '15044', '15046', '15050', '15053', '15057', '15058',
            '15059', '15060', '15065', '15068', '15069', '15070', '15075', '15081',
            '15083', '15084', '15089', '15091', '15092', '15093', '15094', '15095', 
            '15096', '15099', '15100', '15103', '15104', '15108', '15109', '15112',
            '15120', '15121', '15122'
        ], 
        'moroleon': ['11021', '11041'], 
        'leon': ['11020', '11037'], 
        'san_fco_rincon': ['11025', '11031'], 
        'acapulco': ['12001', '12021'], 
        'pachuca': ['13022', '13039', '13048', '13051', '13052', '13082', '13083'], 
        'tulancingo': ['13016', '13056', '13077'], 
        'tula': ['13010', '13013', '13070', '13074', '13076'], 
        'guadalajara': ['14039', '14044', '14051', '14070', '14097', '14098', '14101', '14120'], 
        'ocotlan': ['14063', '14066'], 
        'puerto_vallarta': ['14067', '18020'], 
        'toluca': ['15005', '15018', '15027', '15051', '15054', '15055', '15062', '15067', '15076', '15106', '15115', '15118'], 
        'zamora': ['16043', '16108'], 
        'la_piedad': ['11023', '16069'], 
        'morelia': ['16053', '16068'], 
        'cuautla': ['17002', '17004', '17006', '17029', '17030'], 
        'cuerna_vaca': ['17007', '17008', '17011', '17018', '17020', '17028'], 
        'tepic': ['18008', '18017'], 
        'monterrey': ['19006', '19018', '19019', '19021', '19026', '19031', '19039', '19045', '19046', '19048', '19049'], 
        'oaxaca': ['20083', '20087', '20091', '20107', '20115', '20157', '20174', '20293', '20350', '20375', '20385', '20390', '20399', '20403', '20409', '20519', '20553'], 
        'puebla': ['21015', '21034', '21041', '21090', '21106', '21114', '21119', '21125', '21136', '21140', '29017', '29022', '29025', '29027', '29028', '29029', '29041', '29042', '29044', '29053', '29054', '29058', '29059'], 
        'texmelucan': ['21132', '21143'], 
        'queretaro': ['22006', '22011', '22014'], 
        'cancun': ['23003', '23005'], 
        'rioverde': ['24011', '24024'], 
        'san_luis_potosi': ['24028', '24035'], 
        'guaymas': ['26025', '26029'],
        'villahermosa': ['27004', '27013'], 
        'tampico': ['28003', '28009', '28038', '30123', '30133'], 
        'matamoros': ['28022'], 
        'nuevo_laredo': ['28027'], 
        'reynosa': ['28032', '28033'], 
        'apizco': ['29005', '29009', '29026', '29031', '29035', '29038', '29039', '29043'], 
        'tlaxcala': ['29001', '29002', '29010', '29018', '29024', '29033', '29036', '29048', '29049', '29050', '29060'], 
        'acayucan': ['30003', '30116', '30145'], 
        'coatzacoalcos': ['30039', '30082', '30206'], 
        'minititlan': ['30048', '30059', '30089', '30108', '30120', '30199'], 
        'cordoba': ['30014', '30044', '30068', '30196'], 
        'xalapa': ['30026', '30038', '30087', '30093', '30136', '30182'], 
        'orizaba': ['30022', '30030', '30074', '30081', '30085', '30101', '30115', '30118', '30135', '30138', '30185'], 
        'poza_rica': ['30040', '30124', '30131', '30175'], 
        'veracruz': ['30011', '30028', '30193'], 
        'merida': ['31013', '31041', '31050', '31100', '31101'], 
        'zacatecas': ['32017', '32056']
    }

    zm_mpios = set(
        mun for lst in zm_map.values() for mun in lst
    )

    gdf['zona_metropolitana'] = gdf['cvegeo'].isin(zm_mpios).astype(int)

    zm_lookup = {
        mun: zm for zm, lista in zm_map.items() for mun in lista
    }

    gdf['zona_metropolitana_nombre'] = gdf['cvegeo'].map(zm_lookup)

    return gdf


def fix_area(gdf):
    """Recalcula el área en km2 usando una proyección adecuada."""
    gdf = gdf.to_crs(epsg=6372)
    gdf['area_km2'] = gdf.geometry.area / 1e6
    return gdf
    

def enrich_geodata(gdf):
    """Aplica todas las transformaciones de enriquecimiento al GeoDataFrame."""
    gdf = add_region(gdf)
    gdf = add_zona_metropolitana(gdf)
    gdf = add_es_frontera(gdf)
    gdf = fix_area(gdf)
    return gdf


def read_geodata():
    """Lee el shapefile de municipios desde disco."""
    geodata_shp=GEO_RAW_DIR/"mun22gw.shp"
    assert geodata_shp.exists(), f'El archivo: {geodata_shp} NO existe!'

    return gpd.read_file(geodata_shp)

def normalize_columns(gdf): 
    cols = [
        'cvegeo', 'cve_ent', 'cve_mun', 'nomgeo', 'nom_ent',
        'cov_', 'cov_id', 'area', 'perimeter', 'geometry',
        'region', 'zona_metropolitana', 'zona_metropolitana_nombre',
        'es_frontera', 'area_km2'
    ]

    gdf = gdf[[c for c in cols if c in gdf.columns]]

    str_cols = ['cvegeo', 'cve_ent', 'cve_mun', 'nomgeo', 'nom_ent', 'region', 'zona_metropolitana_nombre']
    int_cols = ['cov_', 'cov_id', 'zona_metropolitana', 'es_frontera']
    
    for col in str_cols:
        if col in gdf.columns:
            gdf[col] = gdf[col].astype(str)
            gdf[col] = gdf[col].fillna('Unknown')

    for col in int_cols:
        if col in gdf.columns:
            gdf[col] = gdf[col].fillna(0).astype('int64')
    
    return gdf


def transform_geodata():
    """Transforma, normaliza y guarda los datos geográficos en formato parquet."""

    gdf = read_geodata()
    gdf.columns = gdf.columns.str.lower()

    gdf = enrich_geodata(gdf)

    gdf = normalize_columns(gdf)

    # Output
    output_path = GEO_PROCESSED_DIR / "geodata.parquet"
    gdf.to_parquet(output_path, index=False)

    log.info(f'Datos transformados guardados en: {output_path}')

    return output_path    


def load_geodata(): 
    """Carga los datos transformados en la base de datos principal DuckDB."""
    parquet_path = GEO_PROCESSED_DIR / "geodata.parquet"
    assert parquet_path.exists(), f'El archivo: {parquet_path} NO existe!'

    con = duckdb.connect(DATABASE_PATH)

    con.execute(f"""
        CREATE OR REPLACE TABLE geodata AS 
        SELECT * FROM read_parquet('{parquet_path}')
    """)

    con.close()

    log.info(f'Tabla geodata cargada en DB: {DATABASE_PATH}')

