from math import comb, log, exp
import pandas as pd
from math import floor
from Modules.Games.match_result import MatchState

"""
This program calculates the detailed probabilities of winning a padel game based on the current match state.

The program includes the following features:

1. **Calculate the probability of winning before deuce:**
   - Evaluates the combinations needed for a player to win the game without reaching deuce.
   - Uses serve and return probabilities to compute the possible scenarios.

2. **Calculate the probability of reaching deuce:**
   - Determines the probability that the score reaches the deuce state (3-3).
   - Evaluates the necessary combinations to reach this score from the current state.

3. **Calculate the probability of winning after deuce:**
   - Generates possible combinations to win after reaching deuce.
   - Evaluates probabilities based on a dynamic dictionary of combinations.

4. **Calculate the total probability of winning the game:**
   - Combines the previous probabilities using the formula:
     P(win the game) = P(win before deuce) + P(reach deuce) * P(win after deuce)

The program uses:
- Math libraries for combinatorial calculations.
- Pandas to structure the results into detailed tables.
- A match state model represented by the `MatchState` class.

Output:
- DataFrames with details of each scenario and corresponding probabilities.
- Aggregated values such as the total probability of winning the game.
"""

# Calcular probabilidad de ganar el juego antes de deuce
def calc_win_before_deuce(p_serve, p_return, state:MatchState):
    t1_points = state.t1_points
    t2_points = state.t2_points
    resultados = []
    total_prob = 0

    # Definir los puntos necesarios antes del deuce
    POINTS_NEEDED_BEFORE_DEUCE = [(4, 0), (4, 1), (4, 2)]

    for t1_points_needed, t2_points_needed in POINTS_NEEDED_BEFORE_DEUCE:
        # Calcular puntos ganados por T1 y T2
        t1_wins = t1_points_needed - t1_points
        t2_wins = t2_points_needed - t2_points
        
        # Evitar combinatorias negativas
        num_points = t1_wins + t2_wins - 1
        
        # Calcular combinatoria o poner 0 si no es posible
        combin = comb(num_points, t2_wins) if num_points >= t2_wins >= 0 else 0
        
        # Calcular probabilidad
        if state.serve == 1:
            prob = combin * (p_serve ** t1_wins) * (p_return ** t2_wins)
        else:
            prob = combin * (p_return ** t1_wins) * (p_serve ** t2_wins)

        total_prob += prob

        # Añadir resultado
        resultados.append({
            "Points needed (T1)": t1_points_needed,
            "Points needed (T2)": t2_points_needed,
            "T1 wins": t1_wins,
            "T2 wins": t2_wins,
            "Num points": num_points,
            "Combin": int(combin),
            "Probability": prob * 100
        })

    # Convertir a DataFrame
    df = pd.DataFrame(resultados)

    # Añadir la fila de total
    total_row = [""] * (len(df.columns) - 2) + ["Total", total_prob * 100]
    df.loc[len(df)] = total_row

    return df


# Calcular probabilidad de llegar a deuce
def calc_exact_deuce(p_serve, p_return, state:MatchState):
    t1_points = state.t1_points
    t2_points = state.t2_points

    POINTS_NEEDED_DEUCE = (3, 3)  # Siempre 3-3 para deuce

    t1_wins = POINTS_NEEDED_DEUCE[0] - t1_points
    t2_wins = POINTS_NEEDED_DEUCE[1] - t2_points

    num_points = t1_wins + t2_wins

    # Asegurar que num_points y t2_wins no sean negativos
    if t1_points >= 3 and t2_points >= 3:
        prob = 100  # Si ya están en deuce, la probabilidad es 100%
        combin = 1
    elif num_points < 0 or t2_wins < 0:
        combin = 0
        prob = 0
    else:
        combin = comb(num_points, t2_wins)
        if state.serve == 1:
            prob = combin * (p_serve ** t1_wins) * (p_return ** t2_wins) * 100
        else:
            prob = combin * (p_return ** t1_wins) * (p_serve ** t2_wins) * 100

    return {
        "Points needed (T1)": POINTS_NEEDED_DEUCE[0],
        "Points needed (T2)": POINTS_NEEDED_DEUCE[1],
        "T1 wins": t1_wins,
        "T2 wins": t2_wins,
        "Num points": num_points,
        "Combin": int(combin),
        "Probability": prob
    }

# Generar secuencia de combinaciones como en Excel
def generate_comb_dict(n):
    sequence = {}
    for i in range(1, n + 1):
        if i <= 3:
            sequence[i] = 1
        else:
            sequence[i] = 2 ** ((i - 2) // 2)  # Duplica cada dos pasos después de 3
    return sequence


# Calcular probabilidad de ganar después de deuce
def calc_win_after_deuce(p_serve, state:MatchState, max_iterations=21):
    t1_points = state.t1_points
    t2_points = state.t2_points
    results = []
    total_prob = 0

    # Generar diccionario de combinaciones
    comb_dict = generate_comb_dict(50)

    # Lista de puntos necesarios después de deuce
    POINTS_NEEDED_AFTER_DEUCE = [(5 + i, 3 + i) for i in range(10)]  # (5, 3) hasta (14, 12) --> 10 deuces

    for i, (t1_needed, t2_needed) in enumerate(POINTS_NEEDED_AFTER_DEUCE):
        t1_wins = t1_needed - max(t1_points, 3)
        t2_wins = t2_needed - max(t2_points, 3)
        num_points = t1_wins + t2_wins

        # Si alguno de los puntos necesarios es negativo, ese escenario es imposible.
        if t1_wins < 0 or t2_wins < 0:
            prob = 0
            combin = 0
        else:
            combin = comb_dict.get(num_points, 0)
            if state.serve == 1:
                prob = combin * (p_serve ** t1_wins) * ((1 - p_serve) ** t2_wins) if combin > 0 else 0
            else:
                prob = combin * ((1 - p_serve) ** t1_wins) * (p_serve ** t2_wins) if combin > 0 else 0

        total_prob += prob
        results.append({
            "Points needed (T1)": t1_needed,
            "Points needed (T2)": t2_needed,
            "T1 wins": t1_wins,
            "T2 wins": t2_wins,
            "Num points": num_points,
            "Combin": combin,
            "Probability": prob * 100
        })


    # Convertir a DataFrame
    df = pd.DataFrame(results)
    total_row = ["", "", "", "", "Total", "", total_prob * 100]
    df.loc[len(df)] = total_row

    return df, total_prob * 100

def calc_total_game_probability(p_serve, p_return, state):
    # Calcular probabilidad de ganar antes de deuce
    resultados_df = calc_win_before_deuce(p_serve, p_return, state)
    prob_before_deuce = resultados_df.iloc[-1]['Probability']  # Última fila es el total

    # Calcular probabilidad de llegar a deuce
    deuce_result = calc_exact_deuce(p_serve, p_return, state)
    prob_reach_deuce = deuce_result['Probability']

    # Calcular probabilidad de ganar después de deuce
    win_after_deuce_df, prob_win_after_deuce = calc_win_after_deuce(p_serve, state)

    # Fórmula final:  
    # P(ganar el juego) = P(ganar antes de deuce) + P(reach deuce) * P(ganar después de deuce)
    total_prob = prob_before_deuce + (prob_reach_deuce * prob_win_after_deuce / 100)
    return total_prob