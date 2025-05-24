# Dentro de games_format_results.py
from Modules.Games.games_calculations import (
    calc_win_before_deuce,
    calc_exact_deuce,
    calc_win_after_deuce,
    calc_total_game_probability
)

from Modules.Games.match_result import MatchState
import pandas as pd

def calculate_game_probabilities(estado_actual, p_serve):
    """
    Calculates the probabilities of winning a padel game in detail.
    
    Args:
        estado_actual (MatchState): Current match state.
        p_serve (float): Probability of winning a point on serve.

    Returns:
        dict: Contains all the calculated probabilities and breakdowns.
    """
    p_return = 1 - p_serve

    # 1. Probability of winning before deuce
    resultados_df = calc_win_before_deuce(p_serve, p_return, estado_actual)
    prob_before_deuce = resultados_df.iloc[-1]['Probability']

    # 2. Probability of reaching deuce exactly
    deuce_result = calc_exact_deuce(p_serve, p_return, estado_actual)
    prob_reach_deuce = deuce_result['Probability']

    # 3. Probability of winning after deuce
    win_after_deuce_df, prob_win_after_deuce = calc_win_after_deuce(p_serve, estado_actual)

    # 4. Total probability of winning the game
    total_prob = calc_total_game_probability(p_serve, p_return, estado_actual)

    result = {
        'Probability before deuce': prob_before_deuce,
        'Probability to reach deuce': prob_reach_deuce,
        'Probability after deuce': prob_win_after_deuce,
        'Total probability to win the game': total_prob,
        'Breakdown after deuce': []
    }

    # Solo mostramos desglose si se cumplió que prob_before_deuce == 0 y prob_reach_deuce > 0
    # y además omitimos la última fila con .iloc[:-1]
    if prob_before_deuce == 0 and prob_reach_deuce > 0 and not win_after_deuce_df.empty:
        # Recorremos todas las filas menos la última
        truncated_df = win_after_deuce_df.iloc[:-1]
        for i, (_, row) in enumerate(truncated_df.iterrows(), start=1):
            # Para la primera: "Winning on next deuce"
            if i == 1:
                scenario_text = "Winning on next deuce"
            else:
                scenario_text = f"Winning after {i} more deuces"
            result['Breakdown after deuce'].append({
                'Scenario': scenario_text,
                'Probability': row['Probability']
            })

    return result

def print_game_probabilities(result):
    """
    Prints the probabilities in English with a user-friendly format.
    """
    print(f"{'Current Game Probabilities':^40}")
    print(f"{'-'*40}")
    print(f"{'Probability of winning before deuce:':<35} {result['Probability before deuce']:.2f}%")
    print(f"{'Probability to reach deuce:':<35} {result['Probability to reach deuce']:.2f}%")
    print(f"{'Probability of winning after deuce:':<35} {result['Probability after deuce']:.2f}%")
    print(f"{'Total probability to win the game:':<35} {result['Total probability to win the game']:.2f}%")
    print(f"{'-'*40}")

    breakdown = result['Breakdown after deuce']
    if breakdown:
        print(f"{'Breakdown after deuce':^40}")
        print(f"{'-'*40}")
        print(f"{'Scenario':<25} {'Probability':>12}")
        for item in breakdown:
            print(f"{item['Scenario']:<25} {item['Probability']:.6f}%")

# Ejemplo de uso
if __name__ == "__main__":
    # Ejemplo: estado con 4-4 en puntos (tipo 40-40), 4-3 en juegos, 1-1 en sets, T1 sacando
    estado_actual = MatchState(0, 0, 0, 0, 0, 0, 0)
    p_serve = 0.64

    resultado = calculate_game_probabilities(estado_actual, p_serve)
    print_game_probabilities(resultado)