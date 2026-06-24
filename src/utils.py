import os
import pandas as pd
import math

def guardar_tabla_latex(tabla: pd.DataFrame, nombre_archivo: str, caption: str, label: str):
    """
    Guarda una tabla en formato LaTeX en un archivo.

    Args:
        tabla (DataFrame): La tabla a guardar.
        nombre_archivo (str): El nombre del archivo donde se guardará la tabla (dirección relativa a la raíz)
        caption (str): El título de la tabla.
        label (str): La etiqueta de referencia para la tabla.
    """
    # Creamos el directorio si no existe
    os.makedirs(os.path.dirname(nombre_archivo), exist_ok=True)    
    
    # Guardamos la tabla en formato LaTeX
    tabla.to_latex(nombre_archivo, escape=True, caption=caption, label=label, float_format="%.2f", index_names=False, position="h!")
    
def crear_conjuntos_aprendizaje_test(df: pd.DataFrame, prop_test: float = 0.3, semilla: int = 0) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Divide un DataFrame en conjuntos de aprendizaje y test.

    Args:
        df : El dataFrame a dividir.
        prop_test : Proporción del conjunto de test.
        semilla : La semilla para la aleatoriedad.

    Returns:
        Dos DataFrames: el primero es el conjunto de aprendizaje y el segundo es el conjunto de test.
    """
    # Mezclamos el DataFrame
    df_barajado = df.sample(frac=1, random_state=semilla).reset_index(drop=True)        # Quitamos la columna de índice
    
    # Calculamos el punto de corte
    punto_corte = math.floor(len(df) * (1 - prop_test))
    
    # Dividimos el DataFrame en conjuntos de aprendizaje y test
    df_aprendizaje = df_barajado.iloc[:punto_corte]
    df_pruebas = df_barajado.iloc[punto_corte:]
    
    return df_aprendizaje, df_pruebas