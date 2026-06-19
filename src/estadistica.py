import itertools as it
import pandas as pd
import numpy as np
from scipy.stats import anderson

from .representacion import mostrar_boxplot

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
    
def evaluar_diferencias_series(df: pd.Dataframe, variable: str, variables_ficticias: list, nombres_series: list = []):
    """
    Evalúa las diferencias entre las series de un dataframe generadas por una variable según el valor de las variables ficticias.
    
    Args:
        df: DataFrame que contiene las series temporales
        variable: nombre de la columna que contiene la variable a evaluar
        variables_ficticias: lista de nombres de las variables ficticias (el orden debe coincidir con el orden de los nombres de las series)
        nombres_series: lista de nombres que recibiran las series generadas por las variables ficticias
    Returns:
        p_valores: diccionario con los p-valores de los test de normalidad de cada serie
        normales: booleano que indica si todas las series siguen una distribución normal
        diferentes: booleano que indica si hay diferencias significativas entre las series
        p_valor: p-valor del test de Friedman o ANOVA
        estadistico: estadístico del test de Friedman o ANOVA
        tabla_diferencias: DataFrame con los resultados de las comparaciones entre las series (mbe)
        
    """
    
    # Ajustamos la lista de nombres de series si es necesario
    for i in range(1,len(variables_ficticias)):
        if i > len(nombres_series):
            nombres_series.append(f"Serie-{variables_ficticias[i]}")
        
    df_series = {}
    # Creamos un dataframe para cada serie generada con el valor de una variable ficticia a 1
    for variable_ficticia, nombre_serie in zip(variables_ficticias, nombres_series):
        df_series[nombre_serie] = df[df[variable_ficticia] == 1]
        df_series[nombre_serie].name = nombre_serie
        
        
    # =*=*=*=*=*=*=*=*=*=*=*|   Evaluación de disparidad significativa   |*=*=*=*=*=*=*=*=*=*=*=
    
    p_valores = {}
    
    for serie in df_series.values():
        p_valores.update({serie.name: test_normalidad(serie[variable])["pvalor"]})
    
    normales = False
    if all(p > 0.05 for p in p_valores.values()):
        normales = True
    
    if len(df_series) == 2:
        # Si hay solo dos series, aplico el test de Wilcoxon para comparar las dos series
        from scipy.stats import wilcoxon
        df_unido = pd.merge(df_series[nombres_series[0]][["Datetime", variable]], df_series[nombres_series[1]][["Datetime", variable]], on="Datetime", suffixes=('_' + nombres_series[0], '_' + nombres_series[1]))
        df_unido.dropna(subset=[f"{variable}_{nombres_series[0]}", f"{variable}_{nombres_series[1]}"], inplace=True)
        estadistico, p_valor = wilcoxon(df_unido[f"{variable}_{nombres_series[0]}"], df_unido[f"{variable}_{nombres_series[1]}"])
    else:
        # Unifico los dataframes en uno solo para poder aplicar el test de Friedman o ANOVA
        df_unido = pd.merge(df_series[nombres_series[0]][["Datetime", variable]], df_series[nombres_series[1]][["Datetime", variable]], on="Datetime", suffixes=('_' + nombres_series[0], '_' + nombres_series[1]))
        for nombre_serie in nombres_series[2:]:
            df_unido = pd.merge(df_unido, df_series[nombre_serie][["Datetime", variable]], on="Datetime")
            df_unido.rename(columns={variable: f"{variable}_{nombre_serie}"}, inplace=True)
        
        df_unido.dropna(subset=[f"{variable}_{nombre_serie}" for nombre_serie in nombres_series], inplace=True)
        
        if normales:
            from scipy.stats import f_oneway
            estadistico, p_valor = f_oneway(*[df_unido[f"{variable}_{nombre_serie}"] for nombre_serie in nombres_series])
        else:
            from scipy.stats import friedmanchisquare
            estadistico, p_valor = friedmanchisquare(*[df_unido[f"{variable}_{nombre_serie}"] for nombre_serie in nombres_series])
    
    diferentes = p_valor < 0.05
    
    # =*=*=*=*=*=*=*=*=*=*=*|  Evaluación de dominancia entre las series |*=*=*=*=*=*=*=*=*=*=*=
    
    # Hago un producto cartesiano de las tres series para compararlas dos a dos
    pruebas = list(it.product(list(df_series.values()), repeat=2))
    
    diccionario_tabla = {
                            "Serie" : [serie.name for serie in df_series.values()],
                        }
    
    # Añadimos una fila por cada serie con los resultados de las comparaciones con las demás series
    for serie in df_series.values():
        diccionario_tabla[serie.name] = []
        for serie2 in df_series.values():
            diccionario_tabla[serie.name].append(0.0)
    
    tabla_diferencias = pd.DataFrame(diccionario_tabla)
    tabla_diferencias.set_index("Serie", inplace=True)
    
    for (serie1, serie2) in pruebas:
        if serie1.name != serie2.name:
            # Uno los dataframes según la hora de la lectura para que tengan el mismo tamaño y poder aplicar el test de Wilcoxon
            df_unido = pd.merge(serie1, serie2, on="Datetime", suffixes=('_' + serie1.name, '_' + serie2.name))
            
            mbe_series = mbe(df_unido[f"{variable}_{serie1.name}"], df_unido[f"{variable}_{serie2.name}"])
            tabla_diferencias.loc[serie1.name, serie2.name] = mbe_series
            
    # Muestro un diagrama de cajas y bigotes para cada serie para ver la distribución de los datos
    mostrar_boxplot([serie[variable] for serie in df_series.values()], nombres_series)
                        
    return p_valores, normales, diferentes, p_valor, estadistico, tabla_diferencias

def evaluar_diferencia_variable_on_off(df: pd.DataFrame, variable: str, variable_ficticia: str, nombre_serie: str = None):
    """
    Evalúa la diferencia entre una serie de un dataframe generada por una variable según el valor de una variable ficticia según esté encendeada o apagada.
    
    Args:
        df: DataFrame que contiene las series temporales
        variable: nombre de la columna que contiene la variable a evaluar
        variable_ficticia: nombre de la variable ficticia
        nombre_serie: nombre que recibirá la serie generada por la variable ficticia (+ "_SI" y "_NO")
    Returns:
        p_valor: p-valor del test de normalidad
        normal: booleano que indica si la serie sigue una distribución normal
        diferente: booleano que indica si hay diferencias significativas entre las series
        estadistico: estadístico del test de normalidad
        mbe: error medio entre las dos series
    """
    
    # Creo un dataframe con una nueva variable ficticia en la que se niegue el valor de la variable ficticia original para poder comparar las dos series
    df_negado = df.copy()
    nombre_variable = f"{variable_ficticia}_off"
    df_negado[nombre_variable] = df_negado[variable_ficticia].apply(lambda x: 1 if x == 0 else 0)
    
    return evaluar_diferencias_series(df_negado, variable, [variable_ficticia, nombre_variable], [f"{nombre_serie}_SI", f"{nombre_serie}_NO"])

def interpretar_diferencias_series(p_valores: dict, normales: bool, diferentes: bool, p_valor: float, estadistico: float, tabla_diferencias: pd.DataFrame):
    """
    Imprime las conclusiones obtenidas a partir de los resultados devueltos por la función evaluar_diferencias_series

    Args:
        salida de la función `evaluar_diferencias_series` o `evaluar_diferencia_variable_on_off`
    Returns:
        (los mismos valores que recibe como argumentos para poder utilizar la función en una sola línea con las otras dos)
        p_valores: diccionario con los p-valores de los test de normalidad de cada serie
        normales: booleano que indica si todas las series siguen una distribución normal
        diferentes: booleano que indica si hay diferencias significativas entre las series
        p_valor: p-valor del test de Friedman o ANOVA
        estadistico: estadístico del test de Friedman o ANOVA
        tabla_diferencias: DataFrame con los resultados de las comparaciones entre las series
    """
    
    np.set_printoptions(legacy='1.25')  # Para que los números se muestren bien 
    
    print(f"Interpretación del resultado:")
    print(f"- Los p-valores de los test de normalidad son {p_valores}, lo que indica que las series {'siguen' if normales else 'no siguen'} una distribución normal.")
    print(f"- El p-valor de la prueba de equivalencia es {p_valor:.5f}, lo que indica que {'hay' if diferentes else 'no hay'} diferencias significativas entre las series.")
    print(f"- El estadístico del test es {estadistico:.5f}.")
    print(f"- La tabla de diferencias (MBE) entre las series es:\n{tabla_diferencias}")
    
    return p_valores, normales, diferentes, p_valor, estadistico, tabla_diferencias