import os
import pandas as pd
import math
from sklearn.base import RegressorMixin

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

def realizar_prueba_regresor(regresor : RegressorMixin, df : pd.DataFrame, variable_objetivo : str, variables_independientes : list[str], param_grid : dict, semilla : int, prop_test : float = 0.3, nombre_regresor : str = None, nombre_fichero : str = None, unidad : str = None) -> pd.DataFrame:
    """
    Prueba un regresor, almacena los resultados en el fichero de salida (si se le pasa uno) y  devuelve el resultado de las pruebas

    Args:
        regresor : El regresor a probar.
        df : El DataFrame con los datos de entrada.
        variable_objetivo : Variable que se pretende predecir.
        variables_independientes : Variables con las que se pretende predecir `variable_objetivo`.
        param_grid : La cuadrícula de hiperparámetros a optimizar.
        semilla : La semilla para la aleatoriedad.
        prop_test : Proporción del tamaño del conjunto de test.
        nombre_regresor : El nombre del regresor (para mostrarlo en los resultados, por defecto es el nombre de la clase).
        nombre_fichero : El nombre del archivo donde se guardarán los resultados (si no se le pasa, no se guardan resultados).
        unidad : La unidad de la variable objetivo (para mostrarla en los resultados).
    """
    nombre_regresor = nombre_regresor if nombre_regresor else regresor.__class__.__name__
    
    print(f"{nombre_regresor}:")
    
    # Creamos la carpeta por si no existe
    if nombre_fichero: os.makedirs(os.path.dirname(nombre_fichero), exist_ok=True)
    
    hay_hiperparametros = False
    hiperparametros = {}
    
    try:
        if not nombre_fichero: raise FileNotFoundError()
        hiperparametros = pd.read_csv(f"{nombre_fichero.replace('.csv', '')}_hiperparametros.csv").iloc[0].to_dict()
        hay_hiperparametros = True
        resultados = pd.read_csv(nombre_fichero)
        ejecutar_regresion = False
    except FileNotFoundError:
        if not hiperparametros: hay_hiperparametros = False
        ejecutar_regresion = True

    from . import estadistica as est
    from . import representacion as rep
    
    if ejecutar_regresion:
        
        if hay_hiperparametros:
            param_grid = {k: [v] for k, v in hiperparametros.items()}  # Si ya hay hiperparámetros, los utilizo para entrenar el modelo y no busco otros
        
        resultados, fila_reg_lin, hiperparametros = est.probar_regresor(regresor, df, semilla, variable_objetivo, variables_independientes, param_grid, prop_test, nombre_regresor)
        
        # Guardo los resultados en un csv
        if nombre_fichero: 
            # Guardo los hiperparámetros del modelo en otro csv
            pd.DataFrame([hiperparametros]).to_csv(f"{nombre_fichero.replace('.csv', '')}_hiperparametros.csv", index=False)
            resultados.to_csv(nombre_fichero, index=False)
        
    resultados_ba = est.bland_altman(resultados[variable_objetivo], resultados["prediccion"], resultados)
    est.interpretar_bland_altman(resultados_ba, unidad if unidad else " ")
    rep.mostrar_bland_altman(resultados_ba, f"Comparación entre la predicción del modelo de {nombre_regresor.lower().replace('_', ' ')} y los valores reales de {variable_objetivo}", unidad if unidad else " ")
    
    fila = rep.fila_diferencia_series(nombre_regresor, resultados[variable_objetivo], resultados["prediccion"])
    
    print(f"Mejores hiperparámetros encontrados para {nombre_regresor}:\n{hiperparametros}")
    print(f"Fila de resultados para {nombre_regresor}:\n{fila}")
    
    return fila
    