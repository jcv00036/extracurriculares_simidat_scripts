import os

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