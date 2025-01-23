import pandas as pd
import numpy as np

# Leer los archivos CSV
analysis_file_path = r'Set Algorithm\Set_Analysis_with_T1_and_T2_Wins.csv'
probabilities_file_path = r'Set Algorithm\Set_Probabilities.csv'

df_analysis = pd.read_csv(analysis_file_path, delimiter=';', encoding='utf-8', on_bad_lines='skip')
df_probabilities = pd.read_csv(probabilities_file_path, delimiter=';', encoding='utf-8', on_bad_lines='skip')

# Verificar columnas disponibles en cada DataFrame
print("Columnas disponibles en Set_Analysis:", df_analysis.columns)
print("Columnas disponibles en Set_Probabilities:", df_probabilities.columns)

# Procesar las filas considerando la lógica de la fórmula en Excel
def procesar_fila(row_analysis, row_probabilities):
    # Sumar juegos ganados por T1 y T2 desde el archivo de análisis
    t1_games = (row_analysis.iloc[1:14] == 1).sum()  # Contar "1"
    t2_games = (row_analysis.iloc[1:14] == 0).sum()  # Contar "0"
    suma_juegos = t1_games + t2_games

    if suma_juegos == 0:
        # Caso en el que no se han jugado juegos (SUMA(AH$3:AH$4) = 0)
        prob_producto = np.prod(row_probabilities.iloc[0:13]) * row_probabilities['W/L']
    else:
        # Caso en el que hay juegos jugados
        contar_1 = t1_games  # "1" representa juegos ganados por T1
        contar_0 = t2_games  # "0" representa juegos ganados por T2
        
        if contar_1 == suma_juegos:  # Validar condición de "Y"
            indice_inicio = contar_1  # Inicia desde la posición dinámica
            prob_parcial = np.prod(row_probabilities.iloc[indice_inicio:13])
            prob_producto = prob_parcial * row_probabilities['W/L']
        else:
            prob_producto = 0  # Si no cumple condiciones

    return {
        'Suma_Juegos': suma_juegos,
        'T1_Games': t1_games,
        'T2_Games': t2_games,
        'Producto_Probabilidades': prob_producto
    }

# Aplicar a las primeras 5 filas de ambos DataFrames
for index in range(5):
    row_analysis = df_analysis.iloc[index]
    row_probabilities = df_probabilities.iloc[index]
    print(f"Fila {index + 1} - Analysis:")
    print(row_analysis)
    print(f"Fila {index + 1} - Probabilities:")
    print(row_probabilities)
    resultado = procesar_fila(row_analysis, row_probabilities)
    print(f"Resultado Fila {index + 1}: {resultado}\n")
