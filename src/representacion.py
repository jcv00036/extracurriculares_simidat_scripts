import matplotlib.pyplot as plt
import numpy as np

def mostrar_serie(serie, titulo=None):
    """
    
    Grafica una única serie temporal con un título

    Args:
        serie: serie temporal a graficar
        titulo: título de la gráfica (opcional)
    """
    plt.figure(figsize=(10, 5))
    plt.plot(serie)
    if titulo:
        plt.title(titulo)
    plt.xlabel('Índice')
    plt.ylabel('Valor')
    plt.grid()
    plt.show()
    
def mostrar_series(series, titulos=None, titulo_figura=None):
    """
    
    Grafica múltiples series temporales con títulos

    Args:
        series: lista de series temporales a graficar
        titulos: lista de títulos para cada serie (opcional, no necesita ser del mismo tamaño que series)
        titulo_figura: título de la figura (opcional)
    """    
    plt.figure(figsize=(10, 5))
    for i, serie in enumerate(series):
        plt.plot(serie, label=titulos[i] if titulos and i < len(titulos) else f'Serie {i+1}')
    if titulo_figura:
        plt.title(titulo_figura)
    plt.xlabel('Índice')
    plt.ylabel('Valor')
    plt.grid()
    if titulos:
        plt.legend()
    plt.show()
    
def mostrar_bland_altman(resultado: dict, titulo=None, u_medida=None):
    """
    
    Grafica los resultados de un test Bland Altman

    Args:
        resultado: diccionario con los resultados del test Bland Altman
        titulo: título de la gráfica (opcional)
        u_medida: unidad de medida para el eje y (opcional)
    """
    plt.figure(figsize=(10, 5))
    plt.scatter(resultado["m"], resultado["d"], color='cyan', alpha=0.5)                # Gráfico de dispersión de las diferencias vs las medias
    plt.axhline(0, color='red', linestyle='-')                                          # Línea de referencia en 0
    plt.axhline(resultado["sesgo"], color='red', linestyle='--', label='Sesgo')         # Línea del sesgo
    plt.axhline(resultado["sesgo"] - resultado["margen_error_sesgo"], color='orange', linestyle='-.', label=f'Intervalo de confianza inferior del sesgo: {resultado["sesgo"] - resultado["margen_error_sesgo"]:.5f}')    # Línea del límite inferior del intervalo de confianza del sesgo
    plt.axhline(resultado["sesgo"] + resultado["margen_error_sesgo"], color='orange', linestyle='-.', label=f'Intervalo de confianza superior del sesgo: {resultado["sesgo"] + resultado["margen_error_sesgo"]:.5f}')    # Línea del límite superior del intervalo de confianza del sesgo
    plt.axhline(resultado["lim_inf"], color='blue', linestyle='--', label='Límite Inferior')    # Línea del límite inferior de acuerdo
    plt.axhline(resultado["lim_sup"], color='green', linestyle='--', label='Límite Superior')   # Línea del límite superior de acuerdo
    if titulo:
        plt.title(titulo)
    plt.xlabel(f'Media de las lecturas ({u_medida})' if u_medida else 'Media de las lecturas')
    plt.ylabel(f'Diferencia ({u_medida})' if u_medida else 'Diferencia')
    plt.grid()
    plt.legend()
    plt.show()

def mostrar_scatter_plot(serie_x, serie_y, titulo=None, titulo_serie_x=None, titulo_serie_y=None, u_medida_x=None, u_medida_y=None):
    """
    
    Grafica un scatter plot de dos series temporales enfrentadas

    Args:
        serie_x: serie temporal para el eje x
        serie_y: serie temporal para el eje y
        titulo: título de la gráfica (opcional)
        titulo_serie_x: título para la serie del eje x (opcional)
        titulo_serie_y: título para la serie del eje y (opcional)
        u_medida_x: unidad de medida para el eje x (opcional)
        u_medida_y: unidad de medida para el eje y (opcional)
    """
    titulo_serie_x = titulo_serie_x if titulo_serie_x else "Valor de la serie X"
    titulo_serie_y = titulo_serie_y if titulo_serie_y else "Valor de la serie Y"

    plt.figure(figsize=(10, 5))
    plt.scatter(serie_x, serie_y, color='cyan', alpha=0.5)
    if titulo:
        plt.title(titulo)
    plt.xlabel(f'{titulo_serie_x} ({u_medida_x})' if u_medida_x else f'{titulo_serie_x}')
    plt.ylabel(f'{titulo_serie_y} ({u_medida_y})' if u_medida_y else f'{titulo_serie_y}')
    plt.grid()
    plt.show()