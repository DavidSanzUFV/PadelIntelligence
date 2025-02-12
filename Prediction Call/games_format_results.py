from games_calculations import calc_win_before_deuce, calc_exact_deuce, calc_win_after_deuce, calc_total_game_probability
from match_result import MatchState
import pandas as pd

"""
Este programa contiene todas las funcionalidades encapsuladas de otros módulos relacionados
con el cálculo de probabilidades en un juego de pádel. Estas funciones están diseñadas para
ser llamadas desde `predictioncall.py` o cualquier otro programa que las necesite, proporcionando
resultados detallados y formateados sobre las probabilidades de ganar puntos, llegar a deuce,
y ganar después de deuce en un juego de pádel.
"""


def calculate_game_probabilities(estado_actual, p_serve):
    """
    Calcula las probabilidades de ganar un juego de pádel, desglose completo.

    Parámetros:
        estado_actual (MatchState): El estado actual del partido.
        p_serve (float): Probabilidad de ganar un punto al servicio (para el jugador que saca).

    Devuelve:
        dict: Contiene todas las probabilidades calculadas y detalles.
    """
    # Calcular la probabilidad de ganar al resto
    p_return = 1 - p_serve

    # Calcular las probabilidades
    resultados_df = calc_win_before_deuce(p_serve, p_return, estado_actual)
    prob_before_deuce = resultados_df.iloc[-1]['Probability']

    deuce_result = calc_exact_deuce(p_serve, p_return, estado_actual)
    prob_reach_deuce = deuce_result['Probability']

    win_after_deuce_df, prob_win_after_deuce = calc_win_after_deuce(p_serve, estado_actual)
    total_prob = calc_total_game_probability(p_serve, p_return, estado_actual)

    # Crear un desglose completo en un diccionario
    result = {
        'Probabilidad de ganar antes de deuce': prob_before_deuce,
        'Probabilidad de llegar a deuce': prob_reach_deuce,
        'Total probabilidad de ganar después de deuce': prob_win_after_deuce,
        'Total probabilidad de ganar el juego': total_prob,
        'Desglose ganar después de deuce': []
    }

    # Si es necesario, añadir el desglose de ganar después de deuce
    if prob_before_deuce == 0 and prob_reach_deuce > 0:
        for _, row in win_after_deuce_df.iterrows():
            if row['Points needed (T1)'] != '':
                marcador = f"{row['Points needed (T1)']}-{row['Points needed (T2)']}"
                result['Desglose ganar después de deuce'].append({
                    'Marcador': marcador,
                    'Probabilidad': row['Probability']
                })

    return result


def print_game_probabilities(result):
    """
    Imprime de manera legible el desglose de probabilidades.

    Parámetros:
        result (dict): Diccionario con los resultados de las probabilidades.
    """
    print(f"{'Probabilidades generales':^40}")
    print(f"{'-'*40}")
    print(f"{'Probabilidad de ganar antes de deuce:':<35} {result['Probabilidad de ganar antes de deuce']:.2f}%")
    print(f"{'Probabilidad de llegar a deuce:':<35} {result['Probabilidad de llegar a deuce']:.2f}%")
    print(f"{'Total probabilidad de ganar después de deuce:':<35} {result['Total probabilidad de ganar después de deuce']:.2f}%")
    print(f"{'Total probabilidad de ganar el juego:':<35} {result['Total probabilidad de ganar el juego']:.2f}%")
    print(f"{'-'*40}")

    if result['Desglose ganar después de deuce']:
        print(f"{'Desglose ganar después de deuce':^40}")
        print(f"{'-'*40}")
        print(f"{'Marcador':<15} {'Probabilidad':>15}")
        for item in result['Desglose ganar después de deuce']:
            print(f"{item['Marcador']:<15} {item['Probabilidad']:.6f}%")

"""
# Ejemplo de uso
estado_actual = MatchState(4, 4, 4, 3, 1, 1, 1)
p_serve = 0.645
resultado = calculate_game_probabilities(estado_actual, p_serve)
print_game_probabilities(resultado)
"""