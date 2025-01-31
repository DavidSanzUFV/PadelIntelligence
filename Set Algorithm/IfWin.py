import pandas as pd
from match_result import MatchState

def generate_game_sequence(estado_actual, analysis_file_path, output_csv):
    """
    Genera la secuencia de juegos para todas las iteraciones, 
    agregando la columna 'Game_Sequence' al archivo de análisis original.

    Parámetros:
        estado_actual (MatchState): Estado actual del partido.
        analysis_file_path (str): Ruta del archivo CSV de análisis.
        output_csv (str): Ruta donde se guardará el CSV de salida con la nueva columna.
    """

    # Cargar el archivo CSV de análisis de sets
    df_analysis = pd.read_csv(analysis_file_path, delimiter=';', encoding='utf-8', on_bad_lines='skip')

    # Determinar la columna de inicio basado en los juegos ganados (T1_Win + T2_Win)
    start_index = estado_actual.t1_games + estado_actual.t2_games

    # Obtener solo las columnas de juegos (J1, J2, ..., J13)
    game_columns = [col for col in df_analysis.columns if col.startswith('J')]

    # Asegurar que el índice no exceda las columnas disponibles
    if start_index >= len(game_columns):
        start_index = len(game_columns) - 1

    # Extraer la secuencia correcta para cada fila, garantizando enteros
    def create_game_sequence(row):
        values = row[game_columns[start_index:]].dropna().astype(int)  # Convertir a enteros eliminando NaN
        values = [str(v) for v in values if v != ""]  # Eliminar valores vacíos
        return ','.join(values) if values else "0"  # Convertir a string sin espacios y evitar secuencias vacías

    # Aplicar la función a todas las filas y añadir la nueva columna al DataFrame original
    df_analysis['Game_Sequence'] = df_analysis.apply(create_game_sequence, axis=1)

    # Guardar el archivo actualizado con la columna de secuencia
    df_analysis.to_csv(output_csv, index=False, sep=';', encoding='utf-8')

    print(f"✅ Archivo guardado correctamente en {output_csv}")

# 🔹 **Ejemplo de Uso**
estado_actual = MatchState(2, 1, 2, 1, 0, 0, 1)  # Partido va 2-1 en juegos
analysis_file_path = "Set Algorithm/Set_Analysis_with_T1_and_T2_Wins.csv"
output_csv = "Set Algorithm/Updated_Set_Analysis.csv"

generate_game_sequence(estado_actual, analysis_file_path, output_csv)


