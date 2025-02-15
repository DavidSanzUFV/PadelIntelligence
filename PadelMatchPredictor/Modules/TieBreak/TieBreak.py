import pandas as pd
from Modules.TieBreak.match_result import MatchState

class TiebreakCalculator:
    def __init__(self, estado_actual):
        """
        Inicializa el cálculo del tiebreak con el estado actual del partido.
        Solo se ejecuta si el partido está en un tiebreak (6-6 en juegos).
        """
        self.estado_actual = estado_actual
        self.is_tiebreak = self.estado_actual.t1_games == 6 and self.estado_actual.t2_games == 6

    def calculate_probabilities(self):
        """
        Calcula las probabilidades de ganar el tiebreak para cada jugador usando las fórmulas correctas.
        """
        if not self.is_tiebreak:
            return None  # No ejecutar cálculos si no es un tiebreak

        t1_points = self.estado_actual.t1_points
        t2_points = self.estado_actual.t2_points

        # Cálculo de probabilidades base
        calculation1 = max(7, t2_points + 2) - t1_points
        calculation2 = max(7, t1_points + 2) - t2_points

        total_points = calculation1 + calculation2
        probability_t1 = 1 - (calculation1 / total_points) if total_points > 0 else 0.5
        probability_t2 = 1 - probability_t1

        # Probabilidades si T1 gana o pierde el siguiente punto
        if_win_t1 = 1 - ((max(7, t2_points + 2) - (t1_points + 1)) / 
                         ((max(7, t2_points + 2) - (t1_points + 1)) + (max(7, t1_points + 2) - t2_points)))
        
        if_loss_t1 = 1 - ((max(7, t2_points + 2) - t1_points) / 
                          ((max(7, t2_points + 2) - t1_points) + (max(7, t1_points + 2) - (t2_points + 1))))
        
        # Convertir a porcentaje
        probability_t1 *= 100
        if_win_t1 *= 100
        if_loss_t1 *= 100

        # Imprimir resultados en texto
        print("\n--- Tiebreak Probabilities ---")
        print(f"Probability of winning the tiebreak for T1: {probability_t1:.2f}%")
        print(f"If T1 wins the next point: {if_win_t1:.2f}%")
        print(f"If T1 loses the next point: {if_loss_t1:.2f}%")
        print("--------------------------------\n")


# 🔹 **Ejemplo de uso con un estado actual del tiebreak**
if __name__ == "__main__":
    """
    estado_actual_tiebreak = MatchState(t1_points=3, t2_points=2, t1_games=6, t2_games=6, t1_sets=0, t2_sets=0, serve=1)

    tiebreak_calculator = TiebreakCalculator(estado_actual_tiebreak)
    tiebreak_calculator.calculate_probabilities()
    """