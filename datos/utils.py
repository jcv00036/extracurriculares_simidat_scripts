'''
Este fichero contiene funciones útiles para la generación de dataframes no especificas a un script en concreto.
'''

import os
import pandas as pd


def almacenar_dataframe(df : pd.DataFrame, nombre_fichero : str = "unificado", almacenar_xlsx : bool = True):
     # Guardar el dataframe unificado en un fichero csv en la carpeta out
    print("Guardando el fichero")
    # Pongo una barra de progreso para mostrar el progreso del guardado del fichero, ya que puede tardar un poco si el dataframe es muy grande
    
    if almacenar_xlsx:
        df.to_excel(os.path.join('out', f'{nombre_fichero}.xlsx'), engine='xlsxwriter', index=False)
        print(f'Fichero {nombre_fichero} guardado en out/{nombre_fichero}.xlsx')
        
    df.to_csv(os.path.join('out', f'{nombre_fichero}.csv'), index=False)
    print(f'Fichero {nombre_fichero} guardado en out/{nombre_fichero}.csv')