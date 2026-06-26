'''
Este fichero contiene un script que pretende transformar el dataframe generado en `generador_dataframe.py` de formato wide
a formato long, para poder analizar los efectos de la disposición de las placas sobre su producción.
'''

import logging
from datetime import datetime
import os
import pandas as pd
import tqdm

from utils import almacenar_dataframe
from config import conf, CategoriaConf
1
os.chdir(__file__.replace(__file__.split("/")[-1], ""))                         # Cambia el directorio de trabajo al directorio del script para que no haga cosas graciosas
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(f"log/transformacion_wide_long{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log")
                    ])
logger = logging.getLogger(__name__)

RUTA_ENTRADA = f"{conf.get(CategoriaConf.FICHEROS, "fichero_df_procesado")}.csv"
NOMBRE_FICHERO_SALIDA = conf.get(CategoriaConf.FICHEROS, "fichero_df_long")
ALMACENAR_XLSX = conf.getboolean(CategoriaConf.CONSTANTES, "almacenar_xlsx")

STRINGS = ["1_1", "1_2", "2_1", "2_2", "3_1", "3_2", "4_1", "4_2", "5_1", "5_2"]
NOMBRES_VARIABLES_DF = [f"Pdc{string}" for string in STRINGS]
VARIABLES_EXTRA_GUARDAR = {
    "G FRONT" : "Irradiancia",
    "T G3 STR2" : "Temperatura_placas"
}                                                            # Este dicccionario guarda los nombres de variables que se van a guardar además de la potencia
VALORES_VARIABLES = {
    "Disp_Izq"      : dict(zip(NOMBRES_VARIABLES_DF, [1, 0, 1, 0, 1, 1, 1, 0, 1, 0])),
    "Disp_Cent"     : dict(zip(NOMBRES_VARIABLES_DF, [0, 0, 0, 1, 1, 1, 0, 0, 0, 0])),
    "Disp_Der"      : dict(zip(NOMBRES_VARIABLES_DF, [0, 1, 1, 0, 1, 1, 0, 1, 0, 1])),
    "Disp_Vert"     : dict(zip(NOMBRES_VARIABLES_DF, [1, 1, 1, 1, 0, 0, 1, 1, 1, 1])),
    "Monofacial"    : dict(zip(NOMBRES_VARIABLES_DF, [0, 0, 0, 0, 0, 0, 0, 0, 0, 1]))
}

# Cargo el dataframe original
df = pd.read_csv(RUTA_ENTRADA)

# Transformo el dataframe de wide a long
df_long = pd.melt(df, id_vars=["Datetime"] + list(VARIABLES_EXTRA_GUARDAR.keys()), value_vars=NOMBRES_VARIABLES_DF, var_name="Placa", value_name="Pdc")

# Creo las columnas de las variables a partir del nombre de la placa
for nombre_variable, valores in tqdm.tqdm(VALORES_VARIABLES.items(), desc="Mapeando variables", unit="variable"):
    df_long[nombre_variable] = df_long["Placa"].map(valores)

df_long.rename(columns=VARIABLES_EXTRA_GUARDAR, inplace=True)

# Transformo la columna de fecha a tipo datetime
df_long["Datetime"] = pd.to_datetime(df_long["Datetime"])

# Transformo la columna Placa en dos columnas: Grupo y String
df_long["Grupo"] = df_long["Placa"].apply(lambda x: int(x.replace("Pdc", "").split("_")[0]))
df_long["String"] = df_long["Placa"].apply(lambda x: x.replace("Pdc", "").split("_")[1])

# Elimino la columna Placa porque ya no es necesaria y reordeno las columnas
df_long = df_long.drop(columns=["Placa"])
df_long = df_long[["Datetime", "Grupo", "String", "Pdc"] + list(VALORES_VARIABLES.keys()) + list(VARIABLES_EXTRA_GUARDAR.values())]      # Para que al visualizarlo quede más claro de dónde es la medida

logger.info(f"Los valores nulos por columna son:\n{df_long.isnull().sum()}")
filas_antes = len(df_long)
# Quitamos todos los valores nulos de Pdc porque no aportan información y solo ensucian el dataframe
df_long = df_long.dropna(subset=["Pdc"])
logger.info(f"Se han eliminado {filas_antes - len(df_long)} filas con valores nulos de Pdc. Las filas con valores nulos tras la limpieza son:\n{df_long.isnull().sum()}")

# Añadimos un datetimeindex al df
df_long = df_long.set_index("Datetime")

# Rellenamos los valores nulos de las variables extra con la media entre los valores no nulos anterior y posterior en el tiempo
for col in VARIABLES_EXTRA_GUARDAR.values():
    df_long[col] = df_long[col].bfill()  # Si hay valores nulos al principio del dataframe, los rellenamos con el primer valor no nulo
    df_long[col] = df_long[col].interpolate(method="time")
    
logger.info(f"Se han rellenado los valores nulos de las variables extra con la interpolación temporal. Los valores nulos por columna tras la interpolación son:\n{df_long.isnull().sum()}")


logger.info(f"La cabeza del dataframe final es:\n{df_long.head()}")

print("Almacenando dataframe final en fichero...")
almacenar_dataframe(df_long, NOMBRE_FICHERO_SALIDA, almacenar_xlsx=ALMACENAR_XLSX, almacenar_indice=True)