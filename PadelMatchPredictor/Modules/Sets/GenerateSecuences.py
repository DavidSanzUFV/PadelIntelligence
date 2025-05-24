import pandas as pd
from Modules.Sets.match_result import MatchState

def generate_game_sequence(estado_actual, analysis_file_path, output_csv_ifwin, output_csv_ifloss, win=True):
    """
    Generates the sequence of games for all iterations and saves them in two separate files:
    - `Updated_Set_Analysis_IfWin.csv` if `win=True` (T1 wins)
    - `Updated_Set_Analysis_IfLoss.csv` if `win=False` (T2 wins)

    Parameters:
        estado_actual (MatchState): Current match state.
        analysis_file_path (str): Path to the analysis CSV file.
        output_csv_ifwin (str): Path to save the CSV if T1 wins.
        output_csv_ifloss (str): Path to save the CSV if T2 wins.
        win (bool): `True` to compute the scenario where T1 wins, `False` for T2's win scenario.
    """

    # Cargar el archivo CSV de análisis de sets
    df_analysis = pd.read_csv(analysis_file_path, delimiter=';', encoding='utf-8', on_bad_lines='skip')

    # Determinar el nuevo estado según el caso de IfWin o IfLoss
    new_t1_games = estado_actual.t1_games + (1 if win else 0)  # Si es IfWin, T1 suma 1
    new_t2_games = estado_actual.t2_games + (0 if win else 1)  # Si es IfLoss, T2 suma 1

    # Determinar la columna de inicio basado en los juegos ganados (nuevo resultado del set)
    start_index = new_t1_games + new_t2_games

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

    # Determinar el archivo de salida según el parámetro `win`
    output_csv = output_csv_ifwin if win else output_csv_ifloss

    # Guardar el archivo actualizado con la columna de secuencia
    df_analysis.to_csv(output_csv, index=False, sep=';', encoding='utf-8')

    #print(f"✅ Archivo guardado correctamente en {output_csv} ({'IfWin' if win else 'IfLoss'})")

# 🔹 **Ejemplo de Uso**
if __name__ == "__main__":
    """
    estado_actual = MatchState(2, 1, 2, 1, 0, 0, 1)  # Estado actual del set
    analysis_file_path = "Set Algorithm/Set_Analysis_with_T1_and_T2_Wins.csv"
    output_csv_ifwin = "Set Algorithm/Updated_Set_Analysis_IfWin.csv"
    output_csv_ifloss = "Set Algorithm/Updated_Set_Analysis_IfLoss.csv"

    # Generar ambos archivos con un solo programa
    generate_game_sequence(estado_actual, analysis_file_path, output_csv_ifwin, output_csv_ifloss, win=True)  # Para IfWin
    generate_game_sequence(estado_actual, analysis_file_path, output_csv_ifwin, output_csv_ifloss, win=False)  # Para IfLoss
    """