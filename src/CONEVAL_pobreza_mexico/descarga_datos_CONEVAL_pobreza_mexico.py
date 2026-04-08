import os
from pathlib import Path
import requests
import pandas as pd

URLS_ARCHIVOS = {
    "CONEVAL_pobreza_nivel_municipal": "https://www.datos.gob.mx/dataset/b6981ccc-083b-4e57-ba6f-d800a7398fa8/resource/1e5a4536-b6dd-4dde-900a-7198797d9843/download/pobreza_grupos_poblacionales_poblacion_indigena.csv",
    "CONEVAL_pobreza_urbana_por_localidad_2020": "https://www.datos.gob.mx/dataset/b6981ccc-083b-4e57-ba6f-d800a7398fa8/resource/04a777ab-dcd4-4a45-b0f4-8b34a610300d/download/rangos_pobreza_loc_urbana_2020.csv",
    "CONEVAL_pobreza_a nivel_municipal_por_sexo": "https://www.datos.gob.mx/dataset/b6981ccc-083b-4e57-ba6f-d800a7398fa8/resource/a4cecd72-d7b6-4ef8-85d7-10804c9837c4/download/pobreza_grupos_poblacionales_sexo.csv",
    "CONEVAL_pobreza_a nivel municipal_por_ambito_residencia": "https://www.datos.gob.mx/dataset/b6981ccc-083b-4e57-ba6f-d800a7398fa8/resource/7301b6f1-07a1-4c6a-9f29-bdccf6e2cf54/download/pobreza_grupos_poblacionales_rural_urbano.csv",
    "CONEVAL_pobreza_a nivel municipal_por_grupos_edad": "https://www.datos.gob.mx/dataset/b6981ccc-083b-4e57-ba6f-d800a7398fa8/resource/f97c2271-ac51-4096-bbfb-5162b867b43f/download/pobreza_grupos_poblacionales_edad.csv",
    "CONEVAL_pobreza_a_nivel_municipal_indicadores" : "https://www.datos.gob.mx/dataset/b6981ccc-083b-4e57-ba6f-d800a7398fa8/resource/6e409e3a-aa08-45f5-b84b-f5d8cc6fafa8/download/pobreza_municipal.csv"
}

RUTA_BASE = Path(__file__).parent
RUTA_DATASETS_CONEVAL_POBREZA_MEXICO = RUTA_BASE / "../" / "../" / "data" / "raw" / "CONEVAL_pobreza_mexico"
RUTA_DICCIONARIOS_CONEVAL_POBREZA_MEXICO = RUTA_BASE / "../" / "../" / "references" / "diccionarios_CONEVAL_pobreza_mexico"

def descarga_datos_CONEVAL_pobreza_mexico():
    
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Referer": "https://www.datos.gob.mx/",
    }
    
    directorio_datasets = Path(RUTA_DATASETS_CONEVAL_POBREZA_MEXICO)

    if not directorio_datasets.exists():
        directorio_datasets.mkdir(parents=True, exist_ok=True)

    for i, (clave, valor) in enumerate(URLS_ARCHIVOS.items()):
        
        nombre_archivo = f"{clave}.csv"
        ruta_completa_archivo = Path(RUTA_DATASETS_CONEVAL_POBREZA_MEXICO) / nombre_archivo

        response = requests.get(valor, headers=headers, timeout=60)
        response.raise_for_status()

        if response.status_code != 200:
            raise Exception(f"Error HTTP {response.status_code}: {response.reason}")
        if not response.content:
            raise Exception("La respuesta llegó vacía.")

        with open(ruta_completa_archivo, "wb") as f:
            f.write(response.content)


def generar_diccionarios_datos():
 
    archivos = Path(RUTA_DATASETS_CONEVAL_POBREZA_MEXICO)

    directorio_diccionarios = Path(RUTA_DICCIONARIOS_CONEVAL_POBREZA_MEXICO)
    if not directorio_diccionarios.exists():
        directorio_diccionarios.mkdir(parents=True, exist_ok=True)

    for archivo in archivos.iterdir():

        ruta_archivo = Path(RUTA_DATASETS_CONEVAL_POBREZA_MEXICO) / archivo.name
        nombre_diccionario = f"diccionario_{archivo.name}"
        ruta_nombre_diccionario = Path(RUTA_DICCIONARIOS_CONEVAL_POBREZA_MEXICO) / nombre_diccionario

        df_datos = pd.read_csv(ruta_archivo, encoding='latin-1', sep=';')

        for col in df_datos.columns:
            
            datos = {
                "nombre": col,
                "descripcion": str(""),
                "tipo_dato": str(df_datos[col].dtype),
                "valores_unicos": str(df_datos[col].unique().tolist()),
                "valores_nulos": df_datos[col].isnull().sum()
            }

            df_diccionario = pd.DataFrame(datos, index=[0])
            df_diccionario = df_diccionario.T
            df_diccionario.to_csv(ruta_nombre_diccionario)
        

def main():
    print("     Descargado datos CONEVAL... \n")
    descarga_datos_CONEVAL_pobreza_mexico()
    print("     Generando diccionario datos CONEVAL... \n")
    generar_diccionarios_datos()

if __name__ == "__main__":
    main()