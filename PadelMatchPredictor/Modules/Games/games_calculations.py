from math import comb, log, exp
import pandas as pd
from math import floor
from Modules.Games.match_result import MatchState
"""
Este programa calcula las probabilidades detalladas de ganar un juego de pádel, basándose en el estado actual del partido.

El programa incluye las siguientes funcionalidades:

1. **Calcular la probabilidad de ganar antes de deuce:**
   - Evalúa las combinaciones necesarias para que un jugador gane el juego sin llegar a deuce.
   - Usa probabilidades de servicio y resto para calcular los escenarios posibles.

2. **Calcular la probabilidad de llegar a deuce:**
   - Determina la probabilidad de que el marcador alcance el estado de deuce (3-3).
   - Evalúa las combinaciones necesarias para llegar a este marcador desde el estado actual.

3. **Calcular la probabilidad de ganar después de deuce:**
   - Genera combinaciones posibles para ganar después de deuce.
   - Evalúa probabilidades basadas en un diccionario dinámico de combinaciones.

4. **Calcular la probabilidad total de ganar el juego:**
   - Combina las probabilidades anteriores utilizando la fórmula:
     P(ganar el juego) = P(ganar antes de deuce) + P(reach deuce) * P(ganar después de deuce)

El programa utiliza:
- Librerías matemáticas para cálculos combinatorios.
- Pandas para estructurar los resultados en tablas detalladas.
- Un modelo de estado del partido representado por la clase `MatchState`.

Salida:
- DataFrames con detalles de cada escenario y probabilidades.
- Valores agregados como la probabilidad total de ganar el juego.
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
        prob = combin * (p_serve ** t1_wins) * (p_return ** t2_wins)
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
        prob = combin * (p_serve ** t1_wins) * (p_return ** t2_wins) * 100

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
    POINTS_NEEDED_AFTER_DEUCE = [(5 + i, 3 + i) for i in range(22)]  # (5, 3) hasta (26, 24)

    for i, (t1_needed, t2_needed) in enumerate(POINTS_NEEDED_AFTER_DEUCE):
        t1_wins = t1_needed - max(t1_points, 3)
        t2_wins = t2_needed - max(t2_points, 3)
        num_points = t1_wins + t2_wins

        # Buscar en el diccionario, si no existe devolver 0
        combin = comb_dict.get(num_points, 0)
        
        # Calcular probabilidad directamente
        prob = combin * (p_serve ** t1_wins) * ((1 - p_serve) ** t2_wins) if combin > 0 else 0

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