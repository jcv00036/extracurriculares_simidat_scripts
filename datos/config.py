import configparser as cp
import os
import enum

os.chdir(__file__.replace(__file__.split("/")[-1], ""))                         # Cambia el directorio de trabajo al directorio del script para que no haga cosas graciosas

class CategoriaConf(enum.StrEnum):
    FICHEROS = enum.auto()
    CONSTANTES = enum.auto()
    
    

def cargar_configuracion():
    """
    Devuelve un objeto ConfigParser con la configuración cargada desde el fichero config.ini

    Returns:
        Objeto ConfigParser con la configuración cargada desde el fichero config.ini
    """
    
    conf = cp.ConfigParser()
    conf.read('config.ini')
    
    # Excepción si no se encuentra el fichero de configuración
    if not conf.sections():
        raise FileNotFoundError("No se ha encontrado el fichero de configuración config.ini")
    
    return conf

conf = cargar_configuracion()