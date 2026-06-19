import pandas as pd
from scipy.stats import anderson

def bland_altman(serie1: pd.Series, serie2: pd.Series, df: pd.DataFrame):
    """
    Realiza un test Bland Altman para comparar dos series temporales
    
    Args:
        serie1: primera serie temporal a comparar
        serie2: segunda serie temporal a comparar
        df: DataFrame que contiene las series (se utiliza para calcular el tamaño de la muestra)
    Returns:
        diccionario de resultados con el formato:
        {
            "pvalor": p-valor del test de normalidad de las diferencias,
            "sesgo": sesgo entre las dos series,
            "lim_inf": límite inferior de acuerdo,
            "lim_sup": límite superior de acuerdo,
            "margen_error_sesgo": margen de error para el sesgo,
            "d": lista de diferencias entre las dos series,
            "m": lista de medias entre las dos series
        }
    """
    
    d = []
    m = []
    sesgo = 0

    # Calculo los vectores de diferencias y de media 
    for i in range(len(df)):
        d.append(serie1.iloc[i] - serie2.iloc[i])
        m.append((serie1.iloc[i] + serie2.iloc[i]) / 2)
        sesgo += d[i]
        
    sesgo /= len(df)    # Calculo el sesgo como la media de las diferencias

    # Verifico normalidad con el test de Anderson-Darling porque la muestra es demasiado grande para Shapiro
    from scipy.stats import anderson

    resultado = anderson(d, dist='norm', method='interpolate')

    if resultado.pvalue < 0.05:
        normal = False
    else:
        normal = True
        
    # Sabiendo si las diferencias siguen una distribución normal o no, calculo los límites de acuerdo
    if normal:
        coef = 1.96
    else:
        coef = 2
        
    media = sesgo
    std_d = pd.Series(d).std()    

    lim_inf, lim_sup = media - coef * (std_d), media + coef * (std_d)

    confianza = 0.95
    n = len(d)
    margen_error_sesgo = 1.96 * (std_d / (n ** 0.5))    # Margen de error para el sesgo (media)

    return {"pvalor": resultado.pvalue,
            "sesgo": sesgo,
            "lim_inf": lim_inf,
            "lim_sup": lim_sup,
            "margen_error_sesgo": margen_error_sesgo,
            "d": d,
            "m": m
            }

def interpretar_bland_altman(resultado : dict, u_medida : str = None):
    """
    
    Imprime las conclusiones obtenidas a partir de los resultados devueltos por un test Bland Altman

    Args:
        resultado : diccionario con los resultados del test Bland Altman
        u_medida : unidad de medida de las series (opcional)
    """
    
    u_medida = u_medida if u_medida else ""
    
    print(f"Interpretación del resultado:")
    print(f"- El p-valor del test de normalidad es {resultado['pvalor']:.5f}, lo que indica que las diferencias {'no ' if resultado['pvalor'] < 0.05 else ''}siguen una distribución normal.")
    print(f"- El sesgo entre las dos series es de {resultado['sesgo']:.5f} {u_medida}, lo que indica que en promedio, una serie tiende a ser {abs(resultado['sesgo']):.5f} {u_medida} {'mayor' if resultado['sesgo'] > 0 else 'menor'} que la otra.")
    print(f"- Los límites de acuerdo son [{resultado['lim_inf']:.5f}, {resultado['lim_sup']:.5f}] {u_medida}, lo que indica el rango en el que se espera que caigan el 95% de las diferencias entre las dos series.")
    print(f"- El margen de error para el sesgo es de {resultado['margen_error_sesgo']:.5f} {u_medida}, lo que indica la precisión con la que se ha estimado el sesgo.")
    if resultado['sesgo'] - resultado['margen_error_sesgo'] > 0 or resultado['sesgo'] + resultado['margen_error_sesgo'] < 0:
        print("- La línea de igualdad (y=0) no está dentro del intervalo de confianza del sesgo, por lo que el sesgo es estadísticamente significativo.")
    else:
        print("- La línea de igualdad (y=0) está dentro del intervalo de confianza del sesgo, por lo que el sesgo no es estadísticamente significativo.")
        
def rmse(serie1: pd.Series, serie2: pd.Series):
    """
    Calcula el error cuadrático medio entre dos series temporales

    Args:
        serie1: primera serie temporal
        serie2: segunda serie temporal
    """
    return ((serie1 - serie2) ** 2).mean() ** 0.5

def mae(serie1: pd.Series, serie2: pd.Series):
    """
    Calcula el error absoluto medio entre dos series temporales

    Args:
        serie1: primera serie temporal
        serie2: segunda serie temporal
    """
    return (serie1 - serie2).abs().mean()

def mape(serie1: pd.Series, serie2: pd.Series):
    """
    Calcula el error porcentual absoluto medio entre dos series temporales

    Args:
        serie1: primera serie temporal
        serie2: segunda serie temporal
    """
    return ((serie1 - serie2).abs() / serie1.abs()).mean() * 100

def mbe(serie1: pd.Series, serie2: pd.Series):
    """
    Calcula el error medio entre dos series temporales

    Args:
        serie1: primera serie temporal
        serie2: segunda serie temporal
    """
    return (serie1 - serie2).mean()

def test_normalidad(serie: pd.Series):
    """
    Realiza un test de normalidad de Anderson-Darling sobre una serie temporal

    Args:
        serie: serie temporal a analizar
    Returns:
        diccionario con los resultados del test de normalidad
    """
    muestras = serie.dropna().values    
    resultado = anderson(muestras, dist='norm', method='interpolate')
    
    return {"pvalor": resultado.pvalue,
            "estadistico": resultado.statistic}