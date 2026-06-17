from datetime import datetime
import logging
import os
import pandas as pd
from tqdm import tqdm, trange

from utils import almacenar_dataframe
from config import conf, CategoriaConf

os.chdir(__file__.replace(__file__.split("/")[-1], ""))                         # Cambia el directorio de trabajo al directorio del script para que no haga cosas graciosas

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(f"log/procesamiento_dataframe{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log")
                    ])
logger = logging.getLogger(__name__)

COLUMNAS_POTENCIA = ['Pdc1_1', 'Pdc1_2', 'Pdc2_1', 'Pdc2_2', 'Pdc3_1', 'Pdc3_2', 'Pdc4_1', 'Pdc4_2', 'Pdc5_1', 'Pdc5_2']
COLUMNAS_SENSORES_IRRADIANCIA = ['PIR F1', 'PIR R1', 'PIR F2', 'PIR R2', 'G FRONT', 'G REAR G4 STR1', 'G REAR G4 STR2', 'G REAR BOT', 'G REAR MID', 'G REAR TOP', 'G GEAR G5']
UMBRAL_MINIMA_POTENCIA = conf.getfloat(CategoriaConf.CONSTANTES, 'umbral_minima_potencia')
UMBRAL_MINIMA_IRRADIANCIA = conf.getfloat(CategoriaConf.CONSTANTES, 'umbral_minima_irradiancia')
COLUMNA_MUESTRAS_POTENCIA = conf.get(CategoriaConf.CONSTANTES, 'columna_muestras_potencia')
TAM_MUESTRA_CALCULO_RANGO_UTIL = conf.getint(CategoriaConf.CONSTANTES, 'tam_muestra_calculo_rango_util')
COLUMNAS_ALMACENAR = ['Datetime', 'Temperature', ' Humidity', ' Wind Speed',
                      'T G4 STR1', 'T G4 STR2', 'T MONO', 'T G3 STR2', 'T G3 STR1',
                      'PIR F1', 'PIR R1', 'PIR F2', 'PIR R2',
                      'G FRONT', 'G REAR G4 STR1', 'G REAR G4 STR2', 'G REAR BOT', 'G REAR MID', 'G REAR TOP', 'G GEAR G5',
                      'MOD SENSOR G4', 'MOD SENSOR G5',
                      'Pdc1_1', 'Pdc1_2',
                      'Pdc2_1', 'Pdc2_2',
                      'Pdc3_1', 'Pdc3_2',
                      'Pdc4_1', 'Pdc4_2',
                      'Pdc5_1', 'Pdc5_2',
                      'Pac_1', 'Pac_2', 'Pac_3', 'Pac_4', 'Pac_5']

FICHERO_DATAFRAME_UNIFICADO = f"{conf.get(CategoriaConf.FICHEROS, 'fichero_df_unificado')}.csv"
FICHERO_SALIDA = conf.get(CategoriaConf.FICHEROS, 'fichero_df_procesado')
ALMACENAR_XLSX = conf.getboolean(CategoriaConf.CONSTANTES, "almacenar_xlsx")

# =*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*| Funciones |*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=
def recortar_columnas_dataframe(df,  columnas_a_almacenar):
    # Recortar el dataframe para quedarnos solo con las columnas que nos interesan
    df_recortado = df[columnas_a_almacenar]
    return df_recortado

def recortar_filas_dataframe(df, umbral_minima_potencia):
    # Recortar el dataframe para quedarnos solo las filas tras haber logrado superar el umbral mínimo de potencia y antes de que la potencia vuelva a caer por debajo del umbral mínimo de potencia
    esta_en_rango = False
    indice_inicio = 0
    indice_fin = 0
    ultimas_filas = []        # Para detectar si sale del rango, miramos las últimas filas y calculamos la media para evitar falsos positivos por valles de potencoa
    for i in range(len(df)):
        if not esta_en_rango and df.iloc[i][COLUMNA_MUESTRAS_POTENCIA] > umbral_minima_potencia:
            esta_en_rango = True
            indice_inicio = i
        elif esta_en_rango:
            # Si la media de las últimas filas es menor que el umbral, consideramos que ha salido del rango útil
            ultimas_filas.append(df.iloc[i][COLUMNA_MUESTRAS_POTENCIA])
            if len(ultimas_filas) > TAM_MUESTRA_CALCULO_RANGO_UTIL:
                ultimas_filas.pop(0)
            if len(ultimas_filas) == TAM_MUESTRA_CALCULO_RANGO_UTIL and sum(ultimas_filas) / TAM_MUESTRA_CALCULO_RANGO_UTIL < umbral_minima_potencia:
                esta_en_rango = False
                indice_fin = i - TAM_MUESTRA_CALCULO_RANGO_UTIL
                break
    df_recortado = df.iloc[indice_inicio:indice_fin]
    return df_recortado

def cambiar_a_NA_si_valor_inferior_a_umbral(df, columnas, umbral):
    # Cambiar a NA los valores de las columnas indicadas que sean inferiores al umbral (Para que no afecten a los análisis posteriores)
    for columna in columnas:
        df[columna] = df[columna].apply(lambda x: pd.NA if x < umbral else x)
    return df

def recorte_NA(df):
    # Recortar el dataframe para quedarnos solo con las filas que tengan al menos un valor no nulo en las columnas de potencia y sensores de irradiancia
    df_recortado = df.dropna(subset=COLUMNAS_POTENCIA, how='all')
    df_recortado = df_recortado.dropna(subset=COLUMNAS_SENSORES_IRRADIANCIA, how='all')
    return df_recortado

# =*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*| Script | =*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=
# Procesamos día a día del dataframe original
df_original = pd.read_csv(FICHERO_DATAFRAME_UNIFICADO)
df_original["Datetime"] = pd.to_datetime(df_original["Datetime"], format="%Y-%m-%d %H:%M:%S")

df_unificado_recortado = pd.DataFrame(columns=COLUMNAS_ALMACENAR)  # Dataframe final que contendrá todos los días procesados
for df_dia in trange(len(df_original.groupby(df_original["Datetime"].dt.date)), desc='Procesando días', unit='día'):
    data_frame = df_original[df_original["Datetime"].dt.date == df_original["Datetime"].dt.date.unique()[df_dia]]
    
    log_dia = f"Procesando día: {data_frame['Datetime'].dt.date.unique()[0]}:\n"
    
    filas_antes = len(data_frame)
    data_frame = recortar_filas_dataframe(recortar_columnas_dataframe(data_frame, COLUMNAS_ALMACENAR), UMBRAL_MINIMA_POTENCIA)
    
    # Si tras el recorte de filas no queda ninguna fila, descartamos el día por completo
    if data_frame.empty:
        log_dia += f"Filas tras recorte: 0 ({filas_antes} eliminadas) -> Día descartado por completo: Sin producción que supere el umbral mínimo.\n"
        logger.info(log_dia)
        continue
    
    log_dia += f"Filas tras recorte: {len(data_frame)} ({len(data_frame) - filas_antes} eliminadas) -> Se ha determinado que el día útil va desde las {data_frame['Datetime'].min().time()} hasta las {data_frame['Datetime'].max().time()}\n"
    
    filas_antes = len(data_frame)
    data_frame = cambiar_a_NA_si_valor_inferior_a_umbral(data_frame, COLUMNAS_POTENCIA+['Pac_1', 'Pac_2', 'Pac_3', 'Pac_4', 'Pac_5'], UMBRAL_MINIMA_POTENCIA)
    data_frame = cambiar_a_NA_si_valor_inferior_a_umbral(data_frame, COLUMNAS_SENSORES_IRRADIANCIA, UMBRAL_MINIMA_IRRADIANCIA)
    
    log_dia += f"Valores nulos encontrados por columna:\n{data_frame.isna().sum()}"
    
    data_frame = recorte_NA(data_frame)
    
    log_dia += f"\nFilas tras recorte de valores NA: {len(data_frame)} ({len(data_frame) - filas_antes} eliminadas)\n"
    
    logger.info(log_dia)
    
    df_unificado_recortado = pd.concat([df_unificado_recortado, data_frame], ignore_index=True)
    
    
# Muevo la columna Datetime a la primera posición para mejorar la legibilidad del dataframe
columna_date = df_unificado_recortado.pop('Datetime')
df_unificado_recortado.insert(0, 'Datetime', columna_date)

logger.info(f"Cabecera del dataframe final:\n{df_unificado_recortado.head()}")

print("Almacenando dataframe final en fichero...")
almacenar_dataframe(df_unificado_recortado, FICHERO_SALIDA, almacenar_xlsx=ALMACENAR_XLSX)