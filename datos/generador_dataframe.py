'''
Este fichero contiene un script para unificar los ficheros xlsx de la carpeta in en un único fichero en la carpeta out con el formato adecuado para el análisis de datos.
'''
import os
import pandas as pd
from tqdm import tqdm, trange

COLUMNAS_ALMACENAR = ['Time', 'Temperature', ' Humidity', ' Wind Speed',
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
UMBRAL_MINIMA_POTENCIA = 50
UMBRAL_MINIMA_IRRADIANCIA = 15
COLUMNA_MUESTRAS_POTENCIA = 'Pdc1_1'    # Usaremos esta columna como muestra de si la fila nos es útil (para recortar en función del umbral mínimo de potencia)
TAM_MUESTRA_CALCULO_RANGO_UTIL = 20
ALMACENAR_XLSX = True                  # True si se quiere almacenar un fichero xlsx en lugar de un csv, False si solo se quiere almacenar el csv
COLUMNAS_POTENCIA = ['Pdc1_1', 'Pdc1_2', 'Pdc2_1', 'Pdc2_2', 'Pdc3_1', 'Pdc3_2', 'Pdc4_1', 'Pdc4_2', 'Pdc5_1', 'Pdc5_2', 'Pac_1', 'Pac_2', 'Pac_3', 'Pac_4', 'Pac_5']
COLUMNAS_SENSORES_IRRADIANCIA = ['PIR F1', 'PIR R1', 'PIR F2', 'PIR R2', 'G FRONT', 'G REAR G4 STR1', 'G REAR G4 STR2', 'G REAR BOT', 'G REAR MID', 'G REAR TOP', 'G GEAR G5']

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
    df_unificado_recortado = pd.DataFrame()
    
    for i in trange(len(ficheros), desc='Procesando ficheros', unit='fichero'):
        fichero = ficheros[i]
        data_frame = pd.read_excel(fichero, engine='openpyxl')
        # Le pongo a la primera columna el nombre
        data_frame.columns = ['Time'] + list(data_frame.columns[1:])
        # Le recorto las dos primeras filas porque son la unidad de medida y la media de la serie o algo así
        data_frame = data_frame.iloc[2:]
        data_frame = recortar_filas_dataframe(recortar_columnas_dataframe(data_frame, COLUMNAS_ALMACENAR), UMBRAL_MINIMA_POTENCIA)
        data_frame = cambiar_a_NA_si_valor_inferior_a_umbral(data_frame, COLUMNAS_POTENCIA, UMBRAL_MINIMA_POTENCIA)
        data_frame = cambiar_a_NA_si_valor_inferior_a_umbral(data_frame, COLUMNAS_SENSORES_IRRADIANCIA, UMBRAL_MINIMA_IRRADIANCIA)
        data_frame["Date"] = os.path.basename(fichero).split('_')[0]
        # Calculo una columna Datetime a partir de la columna Time y la fecha del fichero
        data_frame['Datetime'] = pd.to_datetime(data_frame["Date"].astype(str) + ' ' + data_frame['Time'].astype(str), format='%Y%m%d %H:%M:%S')
        df_unificado_recortado = pd.concat([df_unificado_recortado, data_frame], ignore_index=True)
        
        
    # Muevo la columna Datetime a la primera posición para mejorar la legibilidad del dataframe y elimino las columnas Time y Date que ya no son necesarias
    df_unificado_recortado = df_unificado_recortado.drop(columns=['Time', 'Date'])
    columna_date = df_unificado_recortado.pop('Datetime')
    df_unificado_recortado.insert(0, 'Datetime', columna_date)
    return df_unificado_recortado

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

def almacenar_dataframe(df : pd.DataFrame):
     # Guardar el dataframe unificado en un fichero csv en la carpeta out
    print("Guardando el fichero")
    # Pongo una barra de progreso para mostrar el progreso del guardado del fichero, ya que puede tardar un poco si el dataframe es muy grande
    
    if ALMACENAR_XLSX:
        df.to_excel(os.path.join('out', 'unificado.xlsx'), engine='xlsxwriter', index=False)
        print('Fichero unificado guardado en out/unificado.xlsx')
        
    df.to_csv(os.path.join('out', 'unificado.csv'), index=False)
    print('Fichero unificado guardado en out/unificado.csv')

df = generar_dataframe()
almacenar_dataframe(df)