'''
Este fichero contiene un script para unificar los ficheros xlsx de la carpeta in en un único fichero en la carpeta out con el formato adecuado para el análisis de datos.
'''
from datetime import datetime
import os
import pandas as pd
import logging
from tqdm import tqdm, trange

from utils import almacenar_dataframe
from config import conf, CategoriaConf

os.chdir(__file__.replace(__file__.split("/")[-1], ""))                         # Cambia el directorio de trabajo al directorio del script para que no haga cosas graciosas

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(f"log/generador_dataframe{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log")
                    ])
logger = logging.getLogger(__name__)

FICHERO_SALIDA = os.path.join(os.getcwd(), conf.get(CategoriaConf.FICHEROS, "fichero_df_unificado"))
ALMACENAR_XLSX = conf.getboolean(CategoriaConf.CONSTANTES, "almacenar_xlsx")


def generar_dataframe():
    # Crear la carpeta out si no existe
    if not os.path.exists('out'):
        os.makedirs('out')

    # Listar los ficheros xlsx de la carpeta in
    ficheros = [
        os.path.join('in', dir, f)
        for dir in os.listdir('in')
        if os.path.isdir(os.path.join('in', dir))
        for f in os.listdir(os.path.join('in', dir))    
        if f.endswith('.xlsx') and f.startswith(('2024', '2025')) and not f.startswith(('2024.', '2025.'))
    ]
        
    # Abro fichero por fichero y concateno las filas en un único dataframe añadiendo una columna con el día
    df_unificado = pd.DataFrame()
    
    logger.info("Iniciando procesamiento de ficheros...")
    
    for i in trange(len(ficheros), desc='Procesando ficheros', unit='fichero'):
        fichero = ficheros[i]
        data_frame = pd.read_excel(fichero, engine='openpyxl')
        # Le pongo a la primera columna el nombre
        data_frame.columns = ['Time'] + list(data_frame.columns[1:])
        
        # Le añado una columna con la fecha del fichero
        data_frame["Date"] = os.path.basename(fichero).split('_')[0]
        
        # Calculo una columna Datetime a partir de la columna Time y la fecha del fichero
        data_frame['Datetime'] = pd.to_datetime(data_frame["Date"].astype(str) + ' ' + data_frame['Time'].astype(str), format='%Y%m%d %H:%M:%S')
        
        # Le recorto las dos primeras filas porque son la unidad de medida y la media de la serie o algo así
        data_frame = data_frame.iloc[2:]
        
        logger.warning(f"Valores nulos encontrados por columna en el fichero {fichero}:\n{data_frame.isna().sum()}")
        
        # Concateno el dataframe al dataframe unificado
        df_unificado = pd.concat([df_unificado, data_frame], ignore_index=True)
        
    # Muevo la columna Datetime a la primera posición para mejorar la legibilidad del dataframe y elimino las columnas Time y Date que ya no son necesarias
    df_unificado = df_unificado.drop(columns=['Time', 'Date'])
    columna_date = df_unificado.pop('Datetime')
    df_unificado.insert(0, 'Datetime', columna_date)
    
    # Ordeno el dataframe por la columna Datetime
    df_unificado = df_unificado.sort_values(by='Datetime')
    
    logger.warning(f"Valores nulos encontrados por columna:\n{df_unificado.isna().sum()}")
    
    return df_unificado

df = generar_dataframe()
logger.info(f"Cabeza del dataframe unificado:\n{df.head()}")

print("Almacenando dataframe final en fichero...")
almacenar_dataframe(df, FICHERO_SALIDA, almacenar_xlsx=ALMACENAR_XLSX)