from math import comb
import pandas as pd

# Parámetros
p_serve = 0.645  # Probabilidad de ganar un punto al saque
p_return = 1 - p_serve  # Probabilidad de perder un punto al saque (resto)

# Calcular combinaciones y probabilidades (Ganar antes de deuce)
def calc_win_before_deuce(p_serve, p_return):
    resultados = []
    total_prob = 0

    for t2_points in range(3):  # T2 puede ganar 0, 1 o 2 puntos
        t1_points_needed = 4
        t2_wins = t2_points
        num_points = t1_points_needed + t2_wins  # Total de puntos jugados

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


# Calcular probabilidad de ganar después de deuce
def calc_win_after_deuce(p_serve):
    results = []
    total_prob = 0

    # Empezamos desde el deuce (40-40), ambos jugadores necesitan dos puntos seguidos para ganar
    t1_needed = 2
    t2_needed = 2

    for i in range(30):  # Máximo de iteraciones
        t1_wins = i // 2
        t2_wins = i - t1_wins

        # Se necesita ventaja de 2 puntos para ganar
        if t1_wins >= t2_wins + 2:
            combin = comb(t1_wins + t2_wins, t1_wins)
            prob = (p_serve ** t1_wins) * ((1 - p_serve) ** t2_wins) * combin
            total_prob += prob
        else:
            prob = 0

        results.append({
            "Points needed (T1)": t1_needed + t1_wins,
            "Points needed (T2)": t2_needed + t2_wins,
            "T1 wins": t1_wins,
            "T2 wins": t2_wins,
            "Num points": t1_wins + t2_wins,
            "Combin": comb(t1_wins + t2_wins, t1_wins),
            "Probability": prob * 100
        })

        # Detener iteraciones si la probabilidad es muy baja
        if prob < 0.0001:
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
