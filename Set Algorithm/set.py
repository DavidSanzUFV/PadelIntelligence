import pandas as pd
import numpy as np

# Definir datos iniciales
juegos_ganados_servicio = 0.821
juegos_ganados_resto = 1 - juegos_ganados_servicio
juego_final = 0.5  # Probabilidad de 0.5 para el último juego si se juega

# Leer el archivo CSV con delimitador correcto
file_path = r'Set Algorithm\Set_Analysis_with_T1_and_T2_Wins.csv'
df = pd.read_csv(file_path, delimiter=';', encoding='utf-8', on_bad_lines='skip')

# Opción de saque (1 = T1 saca primero, 2 = T2 saca primero)
saque_inicial = int(input("Elige equipo que saca primero (1 = T1, 2 = T2): "))

# Calcular probabilidades para cada juego en la secuencia
def calcular_probabilidad_secuencia(row):
    secuencia = []
    saque = saque_inicial  # Comenzar con el equipo que saca primero
    for i, juego in enumerate(row):
        if pd.isna(juego):
            secuencia.append(1)  # Juego no jugado, probabilidad neutral
        else:
            if i == len(row) - 1:  # Último juego (posición 13)
                prob = juego_final if juego == 1 else 1 - juego_final
            else:
                if saque == 1:  # T1 saca
                    prob = juegos_ganados_servicio if juego == 1 else juegos_ganados_resto
                else:  # T2 saca
                    prob = juegos_ganados_resto if juego == 1 else juegos_ganados_servicio
            secuencia.append(prob)  # No redondear aquí
            # Alternar el saque para el siguiente juego
            saque = 2 if saque == 1 else 1
    return secuencia

# Aplicar el cálculo a cada fila del CSV
df_probabilidades = df.iloc[:, 1:14].apply(calcular_probabilidad_secuencia, axis=1)

# Crear un nuevo DataFrame con las probabilidades
df_resultado = pd.DataFrame(df_probabilidades.tolist())

# Ajustar encabezados de 1 a 13
df_resultado.columns = range(1, 14)

# Calcular columna W/L (Win/Loss)
df_resultado['W/L'] = (df.iloc[:, 1:14] == 1).sum(axis=1) > (df.iloc[:, 1:14] == 0).sum(axis=1)
df_resultado['W/L'] = df_resultado['W/L'].astype(int)  # Convertir a 0 o 1

# Calcular la probabilidad acumulada de ganar el set
def calcular_probabilidad_acumulada(row):
    prob_acumulada = np.prod(row)  # Producto de todas las probabilidades en la fila
    return prob_acumulada * 100  # Escalar a porcentaje sin redondeo

# Añadir columna de probabilidad acumulada
df_resultado['Prob_Acumulada'] = df_resultado.apply(calcular_probabilidad_acumulada, axis=1)

# Imprimir las probabilidades acumuladas
print("Probabilidades acumuladas por fila:")
print(df_resultado['Prob_Acumulada'])

# Calcular la suma total de probabilidades acumuladas
suma_total = df_resultado['Prob_Acumulada'].sum()
print("\nSuma total de probabilidades acumuladas:", suma_total)

# Guardar el nuevo CSV con las secuencias de probabilidades
output_path = r'Set Algorithm\Set_Probabilities.csv'
df_resultado.to_csv(output_path, index=False, sep=';')

print("Archivo CSV con secuencias de probabilidades creado:", output_path)
