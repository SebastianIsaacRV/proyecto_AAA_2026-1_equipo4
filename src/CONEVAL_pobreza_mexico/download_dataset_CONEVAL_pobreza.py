import os
import logging
from pathlib import Path
import requests
import pandas as pd
from typing import Final
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging


BASE_PATH = Path(__file__).resolve().parent
PATH_DATASETS_CONEVAL_POVERTY_MEXICO     = BASE_PATH.parent.parent / "data" / "raw" / "CONEVAL_pobreza_mexico"
PATH_DICTIONARIES_CONEVAL_POVERTY_MEXICO = BASE_PATH.parent.parent / "references" / "diccionarios_CONEVAL_pobreza_mexico"
PATH_LOG_FILE                            = BASE_PATH / "download_coneval_pobreza_mexico_log.log"

DATASET_PATHS = {
        "path_dataset":PATH_DATASETS_CONEVAL_POVERTY_MEXICO,
        "path_dictionary":PATH_DICTIONARIES_CONEVAL_POVERTY_MEXICO
    }

URLS_DATASETS: Final[list[dict[str,str]]] = [
    {
        "name":"pobreza_nivel_municipal",
        "url":"https://www.datos.gob.mx/dataset/b6981ccc-083b-4e57-ba6f-d800a7398fa8/resource/1e5a4536-b6dd-4dde-900a-7198797d9843/download/pobreza_grupos_poblacionales_poblacion_indigena.csv",
        "filename":"pobreza_nivel_municipal.csv",
        "dictionary_name":"diccionario_pobreza_nivel_municipal.csv",
        "encoding":"latin-1",
        "sep":";"
    },
    {
        "name":"pobreza_urbana_localidad_2020",
        "url":"https://www.datos.gob.mx/dataset/b6981ccc-083b-4e57-ba6f-d800a7398fa8/resource/04a777ab-dcd4-4a45-b0f4-8b34a610300d/download/rangos_pobreza_loc_urbana_2020.csv",
        "filename":"pobreza_urbana_localidad_2020.csv",
        "dictionary_name":"diccionario_localidad_202.csv",
        "encoding":"latin-1",
        "sep":";"
    },
    {
        "name":"pobreza_municipal_sexo",
        "url":"https://www.datos.gob.mx/dataset/b6981ccc-083b-4e57-ba6f-d800a7398fa8/resource/a4cecd72-d7b6-4ef8-85d7-10804c9837c4/download/pobreza_grupos_poblacionales_sexo.csv",
        "filename":"pobreza_municipal_sexo.csv",
        "dictionary_name":"diccionario_municipal_sexo.csv",
        "encoding":"latin-1",
        "sep":";"
    },
    {
        "name":"pobreza_municipal_ambito_residencia",
        "url":"https://www.datos.gob.mx/dataset/b6981ccc-083b-4e57-ba6f-d800a7398fa8/resource/7301b6f1-07a1-4c6a-9f29-bdccf6e2cf54/download/pobreza_grupos_poblacionales_rural_urbano.csv",
        "filename":"pobreza_municipal_ambito_residencia.csv",
        "dictionary_name":"pobreza_municipal_ambito_residencia.csv",
        "encoding":"latin-1",
        "sep":";"
    },
    {
        "name":"pobreza_municipal_grupos_edad",
        "url":"https://www.datos.gob.mx/dataset/b6981ccc-083b-4e57-ba6f-d800a7398fa8/resource/f97c2271-ac51-4096-bbfb-5162b867b43f/download/pobreza_grupos_poblacionales_edad.csv",
        "filename":"pobreza_municipal_grupos_edad.csv",
        "dictionary_name":"pobreza_municipal_grupos_edad.csv",
        "encoding":"latin-1",
        "sep":";"
    },
    {
        "name":"pobreza_municipal_indicadores",
        "url":"https://www.datos.gob.mx/dataset/b6981ccc-083b-4e57-ba6f-d800a7398fa8/resource/6e409e3a-aa08-45f5-b84b-f5d8cc6fafa8/download/pobreza_municipal.csv",
        "filename":"pobreza_municipal_indicadores.csv",
        "dictionary_name":"pobreza_municipal_indicadores.csv",
        "encoding":"latin-1",
        "sep":";"
    }
]

logger = logging.getLogger(__name__)

def configure_logging(path_log_file:str)->None:
    """
    It configures logger to save logs in a file
    """
    
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    if logger.hasHandlers():
        logger.handlers.clear()

    formato = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formato)

    file_handler = logging.FileHandler(path_log_file)
    file_handler.setFormatter(formato)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler) 

def create_session() -> requests.Session:
    """
    Create a session object to make GET request
    """
    
    session = requests.Session()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Referer": "https://www.datos.gob.mx/",
    }

    retry_strategy = Retry(
        allowed_methods=["GET"]
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)

    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update(headers)

    return session

def validate_dataset_paths(paths: dict[str, Path]) -> None:
    """
    Valida que todas las rutas del dataset existan y sean directorios.

    Args:
        paths: Diccionario {nombre_descriptivo: Path}

    Raises:
        NotADirectoryError: Si una ruta existe pero no es directorio.
    """
    logger.info("---------------------------------------------------")
    for name, path in paths.items():
        if path.exists() and not path.is_dir():
            logger.error(f"PATH VALIDATION an error has occurred checking the - [{path}] - , path not a directory")
            raise NotADirectoryError(f"PATH VALIDATION  '[{name}]' - exist but not a directory: - [{path}]")
        elif path.exists() and path.is_dir():
            print(f"PATH VALIDATION [{path}] exist")
            logger.info(f"[{path}] - allready created")
        elif not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"PATH VALIDATION [{path}] created \n")
            logger.info(f"PATH VALIDATION [{path}] - created succefully")
    
    logger.info("---------------------------------------------------")


def download_dataset(urls_datsets:list[dict[str,str]], path_datasets:str, session:requests.Session)-> None:
    """
    """
    
    for dataset_ in urls_datsets:

        url_:str = dataset_["url"]
        filename_:str = dataset_["filename"]
        rutas_archivo:str = Path(path_datasets) / filename_

        try:
            response: str = session.get(url_)
            response.raise_for_status()

            if response.status_code != 200:
                logger.warning(f"Error HTTP {response.status_code}: {response.reason}")
                raise Exception(f"Error HTTP {response.status_code}: {response.reason}")
            if not response.content:
                logger.warning(f"Petition with: [{response.status_code}] status code - but file has no content.")
                raise Exception("Empty response")
            if response.status_code == 200:
                if response.content:
                    with open(rutas_archivo, "wb") as f:
                        f.write(response.content) 
                        logger.info(f"File: [{filename_}] succefully ")
                else:
                    logger.warning(f"Petition with: [{response.status_code}] status code - but file has no content.")
        except Exception as ex:
            logger.warning(f"Downloading datasets: [{ex}] - {dataset_['url']}")

def dictionary_creation(url_datasets:list[dict[str,str]], path_datasets:str, path_directory_dictionaries:str, ext_file:str)-> None:


    datasets: list[str] = list(Path(path_datasets).glob(f"*{ext_file}"))

    directorio_diccionarios = Path(path_directory_dictionaries)
    if not directorio_diccionarios.exists():
        directorio_diccionarios.mkdir(parents=True, exist_ok=True)

    for file in datasets:
        
        dictionary_name = f"diccionario_{file.name}"
        dictionary: str = Path(path_directory_dictionaries) / dictionary_name

        if file.is_file() and file.suffix.lower() == ext_file.lower():
            try:
                df = pd.read_csv(file, encoding='latin-1', sep=',')
                columnas:list[str] = df.columns.to_list()
                rows = list() 
                for col in columnas:
                
                    is_numeric = pd.api.types.is_numeric_dtype(df[col])
                
                    if is_numeric:
                        example_value   = None
                        min_value       = df[col].min()
                        max_value       = df[col].max()
                    else:
                        serie_not_nulls = df[col].dropna()
                        example_value_ = serie_not_nulls.iloc[0] if not serie_not_nulls.empty else "Sin valores"
                        example_value   = example_value_
                        min_value       = None
                        max_value       = None
                    
                    rows.append({
                        "nombre":col,
                        "descripcion":str(""),
                        "tipo_dato":str(df[col].dtype),
                        "valores_nulos":df[col].isnull().sum(),
                        "valor_minimo":min_value,
                        "valor_maximo":max_value, 
                        "valor_ejemplo":example_value
                    })
                df_diccionario = pd.DataFrame(rows)  
                df_diccionario.to_csv(dictionary, index=False)
            except Exception as e:
                logger.warning(f"Error reading: [{file.name}] or creating the dictionary of this dataset - {e}")
                continue
        else:
            logger.info(f"File: [{file}] ist't a .csv file")


        

def main():
    
    configure_logging(PATH_LOG_FILE)
    session = create_session()
    print("  Validating paths... \n")
    validate_dataset_paths(DATASET_PATHS)
    print("  Validating paths DONE... \n")
    print("  Downloading datasets... \n")
    download_dataset(URLS_DATASETS, PATH_DATASETS_CONEVAL_POVERTY_MEXICO, session)
    print("  Downloading datasets DONE... \n")
    print("  Generating dictionaries... \n")
    dictionary_creation(URLS_DATASETS, PATH_DATASETS_CONEVAL_POVERTY_MEXICO, PATH_DICTIONARIES_CONEVAL_POVERTY_MEXICO, ".csv")
    print("  Generating dictionaries DONE... \n")


if __name__ == "__main__":
    main()