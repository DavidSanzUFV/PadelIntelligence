from math import comb, log, exp
import pandas as pd
import numpy as np

# Parámetros
p_serve = 0.645  # Probabilidad de ganar un punto al saque
p_return = 1 - p_serve  # Probabilidad de ganar un punto al resto
  
# Calcular combinaciones y probabilidades (Ganar antes de deuce)
def calc_win_before_deuce(p_serve, p_return):
    resultados = []
    total_prob = 0

    for t2_points in range(3):  # T2 puede ganar 0, 1 o 2 puntos
        t1_points_needed = 4
        t2_wins = t2_points
        num_points = t1_points_needed + t2_wins

        combin = comb(num_points - 1, t2_wins)
        prob = combin * (p_serve ** t1_points_needed) * ((1 - p_serve) ** t2_wins)

        total_prob += prob
        resultados.append({
            "Points needed (T1)": t1_points_needed,
            "Points needed (T2)": t2_wins,
            "Num points": num_points,
            "Combin": int(combin),
            "Probability": prob * 100
        })

    df = pd.DataFrame(resultados)
    df.loc[len(df)] = ["", "", "", "Total", total_prob * 100]
    return df


# Calcular probabilidad de llegar exactamente a deuce (40-40)
def calc_exact_deuce(p_serve, p_return):
    points_needed = 3
    total_points = 6
    combin = comb(total_points, points_needed)
    prob = combin * (p_serve ** points_needed) * (p_return ** points_needed)

    return {
        "Points needed (T1)": points_needed,
        "Points needed (T2)": points_needed,
        "Num points": total_points,
        "Combin": int(combin),
        "Probability": prob * 100
    }


# Calcular probabilidad de ganar después de deuce (máx 21 iteraciones)
def calc_win_after_deuce(p_serve, max_iterations=21):
    results = []
    total_prob = 0

    t1_wins, t2_wins = 4, 3  # T1 empieza en 4 (deuce + 1), T2 en 3
    iterations = 0

    while iterations <= max_iterations:
        t1_wins += 1
        t2_wins = 3 + iterations  # T2 incrementa con cada iteración (3, 4, 5...)

        if t1_wins >= t2_wins + 2:
            # Calcular puntos jugados después del deuce
            num_points = (t1_wins - 3) + (t2_wins - 3)

            # Determinar combinatoria siguiendo el patrón binomial
            combin = 2**iterations

            # Calcular probabilidad
            log_prob = log(combin) + ((t1_wins - 3) * log(p_serve)) + ((t2_wins - 3) * log(1 - p_serve))
            prob = exp(log_prob)

            total_prob += prob
            results.append({
                "Points needed (T1)": t1_wins,
                "Points needed (T2)": t2_wins,
                "T1 wins": t1_wins - 3,
                "T2 wins": t2_wins - 3,
                "Num points": num_points,  # Refleja los puntos totales jugados
                "Combin": combin,
                "Probability": prob * 100
            })

        iterations += 1
        if iterations > max_iterations:
            print("Máximo de 21 iteraciones alcanzado después del deuce.")
            break

    df = pd.DataFrame(results)
    return df, total_prob * 100



# Calcular y mostrar resultados
resultados_df = calc_win_before_deuce(p_serve, p_return)
print("Probabilidad de ganar antes de deuce:")
print(resultados_df)

deuce_result = calc_exact_deuce(p_serve, p_return)
print("\nProbabilidad de llegar exactamente a deuce (40-40):")
print(pd.DataFrame([deuce_result]))

win_after_deuce_df, prob_win_after_deuce = calc_win_after_deuce(p_serve)
print("\nProbabilidad de ganar después de deuce (detalle por iteraciones):")
print(win_after_deuce_df)

print(f"\nProbabilidad total de ganar después de deuce: {prob_win_after_deuce:.2f}%")

# Probabilidad total de ganar el juego
total_win_prob = resultados_df.iloc[-1]['Probability'] + (deuce_result['Probability'] * prob_win_after_deuce / 100)
print(f"\nProbabilidad total de ganar el juego: {total_win_prob:.2f}%")
