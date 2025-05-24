import pandas as pd

class SetProbabilitiesGenerator:
    def __init__(self, analysis_file, probabilities_file, p_games_won_on_serve, match_state):
        """
        Genera Set_Probabilities.csv basado en la probabilidad de ganar juegos al saque.
        """
        self.analysis_file = analysis_file
        self.probabilities_file = probabilities_file
        self.p_games_won_on_serve = p_games_won_on_serve
        self.match_state = match_state
        self.game_columns = [f'J{i}' for i in range(1, 14)]

        # Determinar quién sacó primero
        total_games = self.match_state.t1_games + self.match_state.t2_games
        self.quien_saco_primero = self.match_state.serve if total_games % 2 == 0 else 3 - self.match_state.serve

        # Generar las probabilidades
        self.generate_probabilities()

    def generate_probabilities(self):
        """
        Calcula las probabilidades y genera Set_Probabilities.csv.
        """
        df_analysis = pd.read_csv(self.analysis_file, delimiter=';', encoding='utf-8')
        df_prob = pd.DataFrame(columns=self.game_columns + ['W/L', 'Prob_Acumulada'])

        for index, row in df_analysis.iterrows():
            secuencia = row[self.game_columns].tolist()
            probabilidad_fila = []
            servidor_actual = self.quien_saco_primero

            for i, valor in enumerate(secuencia):
                if pd.isna(valor):
                    probabilidad_fila.append(1.0)  # Juegos no jugados aún tienen probabilidad 1.0
                elif i == 12:  # Si estamos en J13, siempre es 0.5
                    probabilidad_fila.append(0.5)
                else:
                    if valor == 1:
                        probabilidad_fila.append(self.p_games_won_on_serve if servidor_actual == 1 else (1 - self.p_games_won_on_serve))
                    elif valor == 0:
                        probabilidad_fila.append(1 - self.p_games_won_on_serve if servidor_actual == 1 else self.p_games_won_on_serve)

                    # Alternar el servidor para el próximo juego
                    servidor_actual = 2 if servidor_actual == 1 else 1

            # Calcular W/L
            w_l = 1 if row['Set_Status'] == 'Ganado' else 0

            # Calcular la probabilidad acumulada
            prob_acumulada = 1.0
            for prob in probabilidad_fila:
                prob_acumulada *= prob
            prob_acumulada *= w_l  # Ajustar por W/L

            # Agregar al DataFrame de probabilidades
            df_prob.loc[index] = probabilidad_fila + [w_l, prob_acumulada]

        # Guardar el CSV actualizado
        df_prob.to_csv(self.probabilities_file, index=False, sep=';', encoding='utf-8')

        # Mostrar la suma de la columna Prob_Acumulada
        suma_prob_acumulada = df_prob['Prob_Acumulada'].sum()
        #print(f" Suma total de Prob_Acumulada: {suma_prob_acumulada}")

#  **Ejemplo de uso**
if __name__ == "__main__":
    """
    from match_result import MatchState
    
    match_state = MatchState(t1_points=0, t2_points=0, t1_games=4, t2_games=3, t1_sets=1, t2_sets=1, serve=1)
    p_games_won_on_serve = float(input("Introduce el porcentaje de **juegos** ganados al servicio (0-1): "))

    generator = SetProbabilitiesGenerator(
        analysis_file="Prediction Call/CSV Files/Data/Set_Analysis_with_T1_and_T2_Wins.csv",
        probabilities_file="Prediction Call/CSV Files/Exports/Set_Probabilities.csv",
        p_games_won_on_serve=p_games_won_on_serve,
        match_state=match_state
    )
    """
