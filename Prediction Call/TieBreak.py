import pandas as pd
from match_result import MatchState

class TiebreakCalculator:
    def __init__(self, estado_actual):
        """
        Inicializa el cálculo del tiebreak con el estado actual del partido.
        Solo se ejecuta si el partido está en un tiebreak (6-6 en juegos).
        """
        self.estado_actual = estado_actual

        # Verificar si realmente es un tiebreak (6-6 en juegos)
        if self.estado_actual.t1_games != 6 or self.estado_actual.t2_games != 6:
            #print("⚠️ No es un tiebreak. No se calcularán probabilidades.")
            self.is_tiebreak = False
        else:
            self.is_tiebreak = True

    def calculate_probabilities(self):
        """
        Calcula las probabilidades de ganar el tiebreak para cada jugador usando las fórmulas correctas.
        """
        if not self.is_tiebreak:
            return None  # No ejecutar cálculos si no es un tiebreak

        t1_points = self.estado_actual.t1_points
        t2_points = self.estado_actual.t2_points

        # Cálculo correcto de puntos restantes para ganar el tiebreak
        calculation1 = max(7, t2_points + 2) - t1_points
        calculation2 = max(7, t1_points + 2) - t2_points

        # Evitar divisiones por cero
        total_points = calculation1 + calculation2
        probability_t1 = 1 - (calculation1 / total_points) if total_points > 0 else 0.5
        probability_t2 = 1 - probability_t1

        # Convertir a porcentaje
        probability_t1 *= 100
        probability_t2 *= 100

        # Crear un DataFrame con los resultados
        data = {
            "Us": [t1_points, t1_points + 1, t1_points],
            "Them": [t2_points, t2_points, t2_points + 1],
            "Calculation1": [
                calculation1,
                max(7, (t2_points + 2)) - (t1_points + 1),  # Si T1 gana el siguiente punto
                max(7, (t2_points + 2)) - t1_points,  # Si T2 gana el siguiente punto
            ],
            "Calculation2": [
                calculation2,
                max(7, (t1_points + 2)) - t2_points,  # Si T1 gana el siguiente punto
                max(7, (t1_points + 2)) - (t2_points + 1),  # Si T2 gana el siguiente punto
            ],
            "Probability T1": [
                round(probability_t1, 2),
                round(1 - (max(7, (t2_points + 2)) - (t1_points + 1)) / (max(7, (t2_points + 2)) - (t1_points + 1) + max(7, (t1_points + 2)) - t2_points), 2) * 100,
                round(1 - (max(7, (t2_points + 2)) - t1_points) / (max(7, (t2_points + 2)) - t1_points + max(7, (t1_points + 2)) - (t2_points + 1)), 2) * 100,
            ],
            "Probability T2": [
                round(probability_t2, 2),
                round(100 - (1 - (max(7, (t2_points + 2)) - (t1_points + 1)) / (max(7, (t2_points + 2)) - (t1_points + 1) + max(7, (t1_points + 2)) - t2_points)) * 100, 2),
                round(100 - (1 - (max(7, (t2_points + 2)) - t1_points) / (max(7, (t2_points + 2)) - t1_points + max(7, (t1_points + 2)) - (t2_points + 1))) * 100, 2),
            ],
        }

        df = pd.DataFrame(data, index=["Baseline", "If Wins", "If Loses"])
        return df


"""# 🔹 **Ejemplo de uso con un estado actual del tiebreak**
estado_actual_tiebreak = MatchState(t1_points=3, t2_points=2, t1_games=5, t2_games=6, t1_sets=0, t2_sets=0, serve=1)

tiebreak_calculator = TiebreakCalculator(estado_actual_tiebreak)
df_tiebreak = tiebreak_calculator.calculate_probabilities()

# Solo imprimir si es un tiebreak válido
if df_tiebreak is not None:
    print(df_tiebreak)
"""