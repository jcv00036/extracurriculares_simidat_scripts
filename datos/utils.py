'''
Este fichero contiene funciones útiles para la generación de dataframes no especificas a un script en concreto.
'''

import os
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def almacenar_dataframe(df : pd.DataFrame, nombre_fichero : str, almacenar_xlsx : bool = True, almacenar_indice : bool = False):
     # Guardar el dataframe unificado en un fichero csv en la carpeta out
    logger.info("Guardando el fichero")
    # Pongo una barra de progreso para mostrar el progreso del guardado del fichero, ya que puede tardar un poco si el dataframe es muy grande
    
    if almacenar_xlsx:
        # Si el dataframe es demasiado grande, se parte en varios ficheros xlsx de 1 millón de filas cada uno, ya que Excel no soporta más de 1 millón de filas por hoja
        if len(df) > 1000000:
            logger.warning(f"El dataframe tiene {len(df)} filas, se va a partir en varios ficheros xlsx de 1 millón de filas cada uno")
            for i in range(0, len(df), 1000000):
                df.iloc[i:i+1000000].to_excel(f'{nombre_fichero}_{i//1000000 + 1}.xlsx', engine='xlsxwriter', index=False)
                logger.info(f'Fichero {nombre_fichero.split("/")[-1]}_{i//1000000 + 1}.xlsx guardado en {nombre_fichero}_{i//1000000 + 1}.xlsx')
        else:
            df.to_excel(f'{nombre_fichero}.xlsx', engine='xlsxwriter', index=almacenar_indice)
            logger.info(f'Fichero {nombre_fichero.split("/")[-1]} guardado en {nombre_fichero}.xlsx')
        
    df.to_csv(f'{nombre_fichero}.csv', index=almacenar_indice)
    logger.info(f'Fichero {nombre_fichero.split("/")[-1]} guardado en {nombre_fichero}.csv')