from math import comb
import pandas as pd

# Parámetros
p_serve = 0.645  # Probabilidad de ganar un punto al saque
p_return = 0.37  # Probabilidad de ganar un punto al resto

# Calcular combinaciones y probabilidades (Ganar antes de deuce)
def calc_win_before_deuce(p_serve, p_return):
    resultados = []
    total_prob = 0

    for t2_points in range(3):  # T2 puede ganar 0, 1 o 2 puntos
        t1_points_needed = 4
        t2_wins = t2_points
        num_points = t1_points_needed + t2_wins  # Total de puntos jugados

        # Calcular combinatoria (nCk)
        combin = comb(num_points - 1, t2_wins)

        # Calcular probabilidad usando fórmula binomial
        prob = combin * (p_serve ** t1_points_needed) * ((1 - p_serve) ** t2_wins)

        total_prob += prob
        resultados.append({
            "Points needed (T1)": t1_points_needed,
            "Points needed (T2)": t2_wins,
            "Num points": num_points,
            "Combin": int(combin),
            "Probability": prob * 100
        })

    # Crear DataFrame para visualización
    df = pd.DataFrame(resultados)
    df.loc[len(df)] = ["", "", "", "Total", total_prob * 100]
    return df


# Calcular probabilidad de llegar exactamente a deuce (40-40)
def calc_exact_deuce(p_serve, p_return):
    points_needed = 3
    total_points = 6

    # Calcular combinatoria (C(6, 3))
    combin = comb(total_points, points_needed)

    # Calcular probabilidad básica
    prob = combin * (p_serve ** points_needed) * (p_return ** points_needed)

    return {
        "Points needed (T1)": points_needed,
        "Points needed (T2)": points_needed,
        "Num points": total_points,
        "Combin": int(combin),
        "Probability": prob * 100
    }



# Calcular y mostrar resultados
resultados_df = calc_win_before_deuce(p_serve, p_return)
print("Probabilidad de ganar antes de deuce:")
print(resultados_df)

deuce_result = calc_exact_deuce(p_serve, p_return)
print("\nProbabilidad de llegar exactamente a deuce (40-40):")
print(pd.DataFrame([deuce_result]))
