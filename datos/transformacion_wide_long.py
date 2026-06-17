'''
Este fichero contiene un script que pretende transformar el dataframe generado en `generador_dataframe.py` de formato wide
a formato long, para poder analizar los efectos de la disposición de las placas sobre su producción.
'''

import os
import pandas as pd
import tqdm

from utils import almacenar_dataframe
from config import conf, CategoriaConf

os.chdir(__file__.replace(__file__.split("/")[-1], ""))                         # Cambia el directorio de trabajo al directorio del script para que no haga cosas graciosas

RUTA_ENTRADA = f"{conf.get(CategoriaConf.FICHEROS, "fichero_df_procesado")}.csv"
NOMBRE_FICHERO_SALIDA = conf.get(CategoriaConf.FICHEROS, "fichero_df_long")
ALMACENAR_XLSX = conf.getboolean(CategoriaConf.CONSTANTES, "almacenar_xlsx")

STRINGS = ["1_1", "1_2", "2_1", "2_2", "3_1", "3_2", "4_1", "4_2", "5_1", "5_2"]
NOMBRES_VARIABLES_DF = [f"Pdc{string}" for string in STRINGS]
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
df_long = pd.melt(df, id_vars=["Datetime"], value_vars=NOMBRES_VARIABLES_DF, var_name="Placa", value_name="Pdc")

# Creo las columnas de las variables a partir del nombre de la placa
for nombre_variable, valores in tqdm.tqdm(VALORES_VARIABLES.items(), desc="Mapeando variables", unit="variable"):
    df_long[nombre_variable] = df_long["Placa"].map(valores)

# Transformo la columna de fecha a tipo datetime
df_long["Datetime"] = pd.to_datetime(df_long["Datetime"])

# Transformo la columna Placa en dos columnas: Grupo y String
df_long["Grupo"] = df_long["Placa"].apply(lambda x: int(x.replace("Pdc", "").split("_")[0]))
df_long["String"] = df_long["Placa"].apply(lambda x: x.replace("Pdc", "").split("_")[1])

# Elimino la columna Placa porque ya no es necesaria y reordeno las columnas
df_long = df_long.drop(columns=["Placa"])
df_long = df_long[["Datetime", "Grupo", "String", "Pdc"] + list(VALORES_VARIABLES.keys())]      # Para que al visualizarlo quede más claro de dónde es la medida

print("Almacenando dataframe final en fichero...")
almacenar_dataframe(df_long, NOMBRE_FICHERO_SALIDA, almacenar_xlsx=ALMACENAR_XLSX)