from games_calculations import calc_win_before_deuce, calc_exact_deuce, calc_win_after_deuce,calc_total_game_probability
from match_result import MatchState
import pandas as pd

# Este programa calcula las probabilidades de ganar un juego en un partido de pádel,
# considerando múltiples escenarios: ganar antes de deuce, llegar a deuce, y ganar después de deuce.
# ¡¡Proporciona un desglose detallado de los cálculos de probabilidades de cada punto!!.

estado_actual = MatchState(1, 1, 4, 3, 1, 1, 2)
p_serve = 0.645 if estado_actual.serve == 1 else (1-0.645)
p_return = 1 - p_serve

print("Estado Actual del Partido:")
print(estado_actual)

# 1. Probabilidad de ganar antes de deuce
resultados_df = calc_win_before_deuce(p_serve, p_return, estado_actual)
print("\nProbabilidad de ganar el juego antes de deuce:")
print(resultados_df)

# 2. Probabilidad de llegar a deuce
deuce_result = calc_exact_deuce(p_serve, p_return, estado_actual)
print("\nProbabilidad de llegar a deuce desde el marcador actual:")
print(pd.DataFrame([deuce_result]))

# 3. Probabilidad de ganar después de deuce
win_after_deuce_df, prob_win_after_deuce = calc_win_after_deuce(p_serve, estado_actual)
print("\nProbabilidad de ganar después de deuce desde el marcador actual:")
print(win_after_deuce_df)

total_prob = calc_total_game_probability(p_serve, p_return, estado_actual)
print("\nProbabilidad de ganar el juego con el marcador actual:")
print(f"{round(total_prob, 2)}%")