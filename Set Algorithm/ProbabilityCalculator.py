import pandas as pd
from match_result import MatchState

class ProbabilityCalculator:
    def __init__(self, analysis_file_ifwin, analysis_file_ifloss, probabilities_file, output_file_ifwin, output_file_ifloss, estado_actual):
        """
        Inicializa la clase con las rutas de los archivos y el estado actual del partido.
        """
        self.analysis_file_ifwin = analysis_file_ifwin
        self.analysis_file_ifloss = analysis_file_ifloss
        self.probabilities_file = probabilities_file
        self.output_file_ifwin = output_file_ifwin
        self.output_file_ifloss = output_file_ifloss
        self.estado_actual = estado_actual
        self.previous_sequences = set()
        self.game_columns = [f'J{i}' for i in range(1, 14)]

        # Cargar el archivo de probabilidades
        self.df_prob = self.load_data(self.probabilities_file)

        # Procesar IfWin y IfLoss
        self.process_probabilities(win=True)
        self.process_probabilities(win=False)

    def load_data(self, file_path):
        """
        Carga un archivo CSV en un DataFrame.
        """
        return pd.read_csv(file_path, delimiter=';', encoding='utf-8', on_bad_lines='skip')

    def process_probabilities(self, win=True):
        """
        Aplica el cálculo de probabilidades a todas las filas y guarda el resultado en un CSV.
        """
        # Seleccionar el archivo de análisis correcto
        analysis_file = self.analysis_file_ifwin if win else self.analysis_file_ifloss
        output_file = self.output_file_ifwin if win else self.output_file_ifloss

        # Cargar el archivo de análisis
        df_analysis = self.load_data(analysis_file)

        # Verificar que la columna 'Game_Sequence' existe
        if 'Game_Sequence' not in df_analysis.columns:
            raise ValueError(f"❌ Error: 'Game_Sequence' no está en {analysis_file}")

        # Determinar los nuevos valores de juegos ganados
        new_t1_games = self.estado_actual.t1_games + (1 if win else 0)
        new_t2_games = self.estado_actual.t2_games + (0 if win else 1)

        # Aplicar la función de probabilidad
        df_analysis['Calculated_Probability'] = df_analysis.apply(
            lambda row: self.calculate_probability(row, new_t1_games, new_t2_games), axis=1
        )

        # Calcular la suma total de probabilidades en porcentaje
        total_probability = round(df_analysis['Calculated_Probability'].apply(lambda x: float(x.strip('%'))).sum(), 5)

        # Crear una fila con la suma total
        sum_row = pd.DataFrame({'Iteración': ['Total'], 'Calculated_Probability': [f"{total_probability}%"]})

        # Concatenar la fila con la suma total
        df_analysis = pd.concat([df_analysis, sum_row], ignore_index=True)

        # Guardar el resultado en un nuevo archivo CSV
        df_analysis.to_csv(output_file, index=False, sep=';', encoding='utf-8')

        print(f"\n✅ Archivo guardado en {output_file} ({'IfWin' if win else 'IfLoss'}), con probabilidades en porcentaje.")

    def calculate_probability(self, row, new_t1_games, new_t2_games):
        """
        Calcula la probabilidad en porcentaje (%) si la secuencia es válida.
        """
        start_index = new_t1_games + new_t2_games

        # Verificar si la secuencia de juegos es válida
        if not self.validate_sequence(row, new_t1_games, new_t2_games):
            return "0.00%"

        # Si el índice no existe en df_prob, devolver 0%
        if row.name >= len(self.df_prob):
            return "0.00%"  

        # Obtener la fila correspondiente en df_prob
        prob_row = self.df_prob.iloc[row.name]

        # Obtener las probabilidades a partir del índice correcto
        selected_probs = prob_row[self.game_columns[start_index:]].dropna().tolist()

        # Multiplicar las probabilidades seleccionadas
        product_prob = 1.0
        for prob in selected_probs:
            product_prob *= prob

        # Multiplicar por W/L
        win_loss = prob_row['W/L']
        probability = product_prob * win_loss

        # Convertir a porcentaje y redondear a 2 decimales
        return f"{round(probability * 100, 5)}%"

    def validate_sequence(self, row, new_t1_games, new_t2_games):
        """
        Verifica si la secuencia de juegos es válida según el estado actualizado del partido.
        """
        # Obtener los primeros valores de la fila
        first_values = row[self.game_columns[:new_t1_games + new_t2_games]].tolist()

        # Validar si los primeros valores cumplen la cantidad de `1s` y `0s` esperados (sin importar el orden)
        if first_values.count(1) != new_t1_games or first_values.count(0) != new_t2_games:
            return False  # ❌ No coincide con el resultado del partido

        # Validar si la secuencia ya apareció antes
        game_sequence = row['Game_Sequence'] if pd.notna(row['Game_Sequence']) else ""
        if game_sequence in self.previous_sequences:
            return False  # ❌ Secuencia repetida

        # Validar si la fila tiene suficientes `1s` y `0s` en total
        count_ones = (row[self.game_columns] == 1).sum()
        count_zeros = (row[self.game_columns] == 0).sum()
        if count_ones < new_t1_games or count_zeros < new_t2_games:
            return False  # ❌ No hay suficientes 1s o 0s

        # Agregar la secuencia actual a la lista de previas para futuras comprobaciones
        self.previous_sequences.add(game_sequence)
        return True

# 🔹 **Ejemplo de Uso**
if __name__ == "__main__":
    estado_actual = MatchState(2, 1, 2, 1, 0, 0, 1)
    calculator = ProbabilityCalculator(
        analysis_file_ifwin="Set Algorithm/Updated_Set_Analysis_IfWin.csv",
        analysis_file_ifloss="Set Algorithm/Updated_Set_Analysis_IfLoss.csv",
        probabilities_file="Set Algorithm/Set_Probabilities.csv",
        output_file_ifwin="Set Algorithm/Final_Probabilities_IfWin.csv",
        output_file_ifloss="Set Algorithm/Final_Probabilities_IfLoss.csv",
        estado_actual=estado_actual
    )
