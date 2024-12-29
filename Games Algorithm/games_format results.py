from games_calculations import calc_win_before_deuce, calc_exact_deuce, calc_win_after_deuce,calc_total_game_probability
from match_result import MatchState
import pandas as pd

estado_actual = MatchState(1, 1, 4, 3, 1, 1, 2)
p_serve = 0.645 if estado_actual.serve == 1 else (1-0.645)
p_return = 1 - p_serve

resultados_df = calc_win_before_deuce(p_serve, p_return, estado_actual)
prob_before_deuce = resultados_df.iloc[-1]['Probability']

deuce_result = calc_exact_deuce(p_serve, p_return, estado_actual)
prob_reach_deuce = deuce_result['Probability']

win_after_deuce_df, prob_win_after_deuce = calc_win_after_deuce(p_serve, estado_actual)
total_prob = calc_total_game_probability(p_serve, p_return, estado_actual)

# Probabilidades generales
print(f"{'Probabilidad de ganar antes de deuce:':<35} {prob_before_deuce:.2f}%")
print(f"{'Probabilidad de llegar a deuce:':<35} {prob_reach_deuce:.2f}%\n")

# Si la probabilidad de ganar antes de deuce es 0%, mostrar detalles de ganar después de deuce
if prob_before_deuce == 0 and prob_reach_deuce > 0:
    print(f"{'Desglose de ganar después de deuce':^40}")
    print(f"{'-'*40}")
    print(f"{'Marcador':<15} {'Probabilidad'}")
    print(f"{'-'*40}")
    for _, row in win_after_deuce_df.iterrows():
        if row['Points needed (T1)'] != '':  # Evitar filas vacías
            marcador = f"{row['Points needed (T1)']}-{row['Points needed (T2)']}"
            print(f"{marcador:<15} {row['Probability']:.6f}%")
    
print(f"{'-'*40}")
print(f"{'Total probabilidad de ganar después de llegar a deuce:':<35} {prob_win_after_deuce:.2f}%")
print(f"{'-'*40}")

# Añadir probabilidad total al final
print(f"{'-'*40}")
print(f"{'Total probabilidad de ganar el juego:':<35} {total_prob:.2f}%")
print(f"{'-'*40}")