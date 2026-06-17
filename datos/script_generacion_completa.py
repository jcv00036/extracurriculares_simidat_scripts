"""
Este script genera 3 dataframes siguiendo la configuración en config.ini:
    1. Un dataframe unificado con todos los días de producción
    2. Un dataframe unificado con todos los días de producción recortado para quedarse solo con las filas útiles
    3. Un dataframe unificado con todos los días de producción recortado y transformado a formato long para poder analizar los efectos de la disposición de las placas sobre su producción
"""

print("Generando dataframe unificado con todos los días de producción...")
import generador_dataframe

print("Generando dataframe unificado con todos los días de producción recortado para quedarse solo con las filas útiles...")
import procesamiento_dataframe

print("Generando dataframe unificado con todos los días de producción recortado y transformado a formato long...")
import transformacion_wide_long

print("Listo.")