import pandas as pd
from Modules.Games.match_result import MatchState
from Modules.Games.games_format_results import calculate_game_probabilities, print_game_probabilities
from Modules.Sets.GenerateSecuences import generate_game_sequence
from Modules.Sets.SetProbabilitiesGenerator import SetProbabilitiesGenerator
from Modules.Sets.ProbabilityCalculator import SetProbabilityCalculator
from Modules.TieBreak.TieBreak import TiebreakCalculator
from Modules.Games.games_calculations import calc_total_game_probability
from Modules.Match.Algo_match import probability_match
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Mapa de puntos para conversión
score_map = {
    "0": 0,
    "15": 1,
    "30": 2,
    "40": 3,
    "Adv": 4  # Representación de "Advantage"
}

def validar_resultado(estado):
    # Validación de sets ganados (partido terminado o inválido)
    if (estado.t1_sets == 2 and estado.t2_sets >= 1) or (estado.t2_sets == 2 and estado.t1_sets >= 1):
        print("⚠️ Error: ¡El partido ya está terminado!")
        return False
    if estado.t1_sets == 2 and estado.t2_sets == 2:
        print("⚠️ Error: ¡Marcador de sets inválido: 2-2 no es posible!")
        return False

    # Validación de juegos: permitir 6-5, pero no 6-4, 7-5 o 7-4
    if (estado.t1_games == 6 and estado.t2_games <= 4) or (estado.t2_games == 6 and estado.t1_games <= 4):
        print("⚠️ Error: ¡Conteo de juegos no válido! El set ya está ganado.")
        return False
    if (estado.t1_games == 7 and estado.t2_games == 5) or (estado.t2_games == 7 and estado.t1_games == 5):
        print("⚠️ Error: ¡Conteo de juegos no válido! El set ya está ganado (7-5).")
        return False

    # Validación de tie-break: solo ocurre cuando ambos tienen 6 juegos
    if estado.t1_games == 6 and estado.t2_games == 6:
        if abs(estado.t1_points - estado.t2_points) >= 2 and (estado.t1_points >= 7 or estado.t2_points >= 7):
            print("⚠️ Error: ¡Tie-break ya ganado!")
            return False

    # Validación de puntos: si alguien tiene "Adv", el otro debe tener "40"
    if (estado.t1_points == 4 and estado.t2_points != 3) or (estado.t2_points == 4 and estado.t1_points != 3):
        print("⚠️ Error: ¡Puntos no válidos! Si alguien tiene 'Adv', el otro debe tener '40'.")
        return False

    # Validación de puntos normales
    valid_points = [0, 1, 2, 3, 4]  # (0, 15, 30, 40, Adv)
    if (estado.t1_points not in valid_points) or (estado.t2_points not in valid_points):
        print("⚠️ Error: ¡Puntos no válidos! Solo se permiten 0, 15, 30, 40, Adv.")
        return False

    return True


def leer_probabilidad_final(file_path):
    """
    Lee la fila con 'Iteración' = 'Total' del archivo de probabilidades
    y devuelve la probabilidad final.
    """
    try:
        logging.info(f"📂 Intentando leer el archivo: {file_path}")
        df = pd.read_csv(file_path, delimiter=';', encoding='utf-8', on_bad_lines='skip')

        # Log para ver las primeras filas del archivo leído
        logging.info(f"🔍 Contenido del archivo {file_path}:")
        logging.info(f"\n{df.head(10)}")

        # Log para ver las columnas del DataFrame
        logging.info(f"🔑 Columnas del archivo {file_path}: {list(df.columns)}")

        # Buscar la fila donde la columna 'Iteración' tenga el valor 'Total'
        df_total = df[df['Iteración'] == 'Total']

        if df_total.empty:
            logging.warning(f"⚠️ Advertencia: No se encontró la fila 'Total' en {file_path}.")
            return "N/A"

        # Log para ver el contenido de la fila 'Total'
        logging.info(f"🔍 Fila 'Total' encontrada en {file_path}: {df_total}")

        return df_total['Calculated_Probability'].values[0]

    except Exception as e:
        logging.error(f"❌ Error al leer {file_path}: {e}")
        return "N/A"

def obtener_estado_partido():
    """
    Solicita al usuario el estado actual del partido, con los puntos en formato
    de tenis (0, 15, 30, 40, Adv) y devuelve un objeto MatchState con los valores convertidos.
    """
    print("\n--- Configuración inicial del partido ---")
    # Leer puntos en formato de tenis:
    t1_input = input("Introduce los puntos de T1 (0,15,30,40,Adv): ")
    t2_input = input("Introduce los puntos de T2 (0,15,30,40,Adv): ")

    try:
        t1_points = score_map[t1_input]
        t2_points = score_map[t2_input]
    except KeyError:
        print("❌ Error: Ingresa valores válidos para los puntos (0,15,30,40,Adv).")
        return None

    t1_games = int(input("Introduce los juegos ganados por T1: "))
    t2_games = int(input("Introduce los juegos ganados por T2: "))
    t1_sets = int(input("Introduce los sets ganados por T1: "))
    t2_sets = int(input("Introduce los sets ganados por T2: "))
    serve = int(input("¿Quién sirve? (1 para T1, 2 para T2): "))

    estado_actual = MatchState(t1_points, t2_points, t1_games, t2_games, t1_sets, t2_sets, serve)

    # Validar el estado inicial del partido
    while not validar_resultado(estado_actual):
        print("❌ Error en el estado del partido. Por favor, introduce los datos correctamente.")
        estado_actual = obtener_estado_partido()

    return estado_actual

def main():
    """
    Menú principal del programa que permite calcular probabilidades del juego, set 
    y actualizar el estado del partido.
    """
    estado_actual = obtener_estado_partido()  # Se obtiene el estado del partido al inicio

    # 🚀 Preguntar datos clave al inicio
    p_serve = float(input("\nIntroduce la probabilidad de ganar un **punto** al saque (0-1): "))
    p_games_won_on_serve = float(input("Introduce el porcentaje de **juegos** ganados al servicio (0-1): "))

    # Variable para almacenar la prob. de ganar el set (calculada en la opción 2)
    probabilidad_ganar_set = None

    while True:
        print("\n--- Prediction Call Menu ---")
        print("1. Calcular probabilidad de ganar el juego")
        print("2. Calcular probabilidad de ganar el set")
        print("3. Actualizar el resultado del partido")
        print("4. Calcular probabilidad de ganar el partido (depende de la prob. de ganar el set)")
        print("5. Calcular todas las probabilidades (juego, set y partido)")
        print("6. Salir")

        choice = input("Selecciona una opción (1-5): ")

        if choice == "1":
            # Si el marcador de juegos está 6-6, entonces calculamos tiebreak en lugar de un juego normal
            if estado_actual.t1_games == 6 and estado_actual.t2_games == 6:
                print("\n🎾 **Tiebreak detectado. Calculando probabilidades...**")
                estado_tiebreak = MatchState(
                    t1_points=estado_actual.t1_points,
                    t2_points=estado_actual.t2_points,
                    t1_games=6,
                    t2_games=6,
                    t1_sets=estado_actual.t1_sets,
                    t2_sets=estado_actual.t2_sets,
                    serve=estado_actual.serve
                )
                tiebreak_calculator = TiebreakCalculator(estado_tiebreak)
                df_tiebreak = tiebreak_calculator.calculate_probabilities()

                print("\n🔹 **Probabilidades del Tiebreak:**")
                print(df_tiebreak)
            else:
                # Llamar a la función para calcular probabilidades del juego usando p_serve
                resultado = calculate_game_probabilities(estado_actual, p_serve)
                print_game_probabilities(resultado)

        elif choice == "2":
            print("\n--- 2. Calcular probabilidad de ganar el set ---")

            # 📌 Si es un tiebreak (6-6 en juegos), llamar a TiebreakCalculator
            if estado_actual.t1_games == 6 and estado_actual.t2_games == 6:
                print("\n🎾 **Tiebreak detectado. Calculando probabilidades...**")
                estado_tiebreak = MatchState(
                    t1_points=estado_actual.t1_points,
                    t2_points=estado_actual.t2_points,
                    t1_games=6,
                    t2_games=6,
                    t1_sets=estado_actual.t1_sets,
                    t2_sets=estado_actual.t2_sets,
                    serve=estado_actual.serve
                )
                tiebreak_calculator = TiebreakCalculator(estado_tiebreak)
                df_tiebreak = tiebreak_calculator.calculate_probabilities()

                print("\n🔹 **Probabilidades del Tiebreak:**")
                print(df_tiebreak)
            
            else:
                # 📌 Generar secuencias de juego
                analysis_file_path = r"CSVFiles/Data/Set_Analysis_with_T1_and_T2_Wins.csv"
                output_csv_ifwin = r"CSVFiles/Exports/Updated_Set_Analysis_IfWin.csv"
                output_csv_ifloss = r"CSVFiles/Exports/Updated_Set_Analysis_IfLoss.csv"

                generate_game_sequence(estado_actual, analysis_file_path, output_csv_ifwin, output_csv_ifloss, win=True)
                generate_game_sequence(estado_actual, analysis_file_path, output_csv_ifwin, output_csv_ifloss, win=False)

                # 📌 Generar Set_Probabilities.csv con SetProbabilitiesGenerator
                probabilities_file = r"CSVFiles/Exports/Set_Probabilities.csv"

                generator = SetProbabilitiesGenerator(
                    analysis_file=analysis_file_path,
                    probabilities_file=probabilities_file,
                    p_games_won_on_serve=p_games_won_on_serve,
                    match_state=estado_actual
                )
                
                # 📌 Después, calcular probabilidades de IfWin y IfLoss con SetProbabilityCalculator
                output_file_ifwin = r"CSVFiles/Exports/Final_Probabilities_IfWin.csv"
                output_file_ifloss = r"CSVFiles/Exports/Final_Probabilities_IfLoss.csv"

                calculator = SetProbabilityCalculator(
                    analysis_file_ifwin=output_csv_ifwin,
                    analysis_file_ifloss=output_csv_ifloss,
                    probabilities_file=probabilities_file,
                    output_file_ifwin=output_file_ifwin,
                    output_file_ifloss=output_file_ifloss,
                    estado_actual=estado_actual
                )

                # 📌 Leer probabilidades finales
                prob_if_win = leer_probabilidad_final(output_file_ifwin)
                prob_if_loss = leer_probabilidad_final(output_file_ifloss)

                # 📌 Mostrar resultados
                print("\n🔹 **Resultados del cálculo de probabilidades del set:**")
                print(f"   ➡️ Si T1 gana el siguiente juego, su probabilidad de ganar el set: {prob_if_win}")
                print(f"   ➡️ Si T1 pierde el siguiente juego, su probabilidad de ganar el set: {prob_if_loss}")
                probabilidad_ganar_juego = calc_total_game_probability(p_serve, 1-p_serve, estado_actual)

                # Convertir a float las cadenas con '%'
                prob_if_win = float(prob_if_win.strip('%')) / 100
                prob_if_loss = float(prob_if_loss.strip('%')) / 100

                # Si probabilidad_ganar_juego > 1, se asume que está en %
                if probabilidad_ganar_juego > 1:
                    probabilidad_ganar_juego /= 100

                # Calcular la prob. de ganar el set combinando
                probabilidad_ganar_set = (probabilidad_ganar_juego * prob_if_win) + ((1 - probabilidad_ganar_juego) * prob_if_loss)
                probabilidad_ganar_set_percent = probabilidad_ganar_set * 100

                print(f"🔹 Probabilidad de ganar el set: {probabilidad_ganar_set_percent:.2f}%")

                # Guardamos en la variable su valor decimal
                probabilidad_ganar_set = probabilidad_ganar_set

        elif choice == "3":
            print("\n🔄 **Actualizar resultado del partido**")
            estado_actual = obtener_estado_partido()
            # 🔔 Reseteamos la prob. de ganar el set (pues ha cambiado el estado)
            probabilidad_ganar_set = None  
            print("\n✅ ¡Estado del partido actualizado!")

        elif choice == "4":
            # Queremos usar probabilidad_ganar_set
            if probabilidad_ganar_set is None:
                print("⚠️ Debes calcular primero la probabilidad de ganar el set (opción 2) antes de usar esta opción.")
            else:
                ifwin, ifloss = probability_match(estado_actual)
                # prob. ganar el partido = prob. ganar set * ifwin + (1 - prob. ganar set) * ifloss
                prob_ganar_partido = (probabilidad_ganar_set * ifwin) + ((1 - probabilidad_ganar_set) * ifloss)
                prob_ganar_partido_percent = prob_ganar_partido * 100
                print(f"🔹 Probabilidad de ganar el partido: {prob_ganar_partido_percent:.2f}%")
        elif choice == "5":
            # ---------------------------------
            # ---------- JUEGO -----------------
            # ----------------------------------
            # Si el marcador de juegos está 6-6, entonces calculamos tiebreak en lugar de un juego normal
            if estado_actual.t1_games == 6 and estado_actual.t2_games == 6:
                print("\n🎾 **Tiebreak detectado. Calculando probabilidades...**")
                estado_tiebreak = MatchState(
                    t1_points=estado_actual.t1_points,
                    t2_points=estado_actual.t2_points,
                    t1_games=6,
                    t2_games=6,
                    t1_sets=estado_actual.t1_sets,
                    t2_sets=estado_actual.t2_sets,
                    serve=estado_actual.serve
                )
                tiebreak_calculator = TiebreakCalculator(estado_tiebreak)
                df_tiebreak = tiebreak_calculator.calculate_probabilities()

                print("\n🔹 **Probabilidades del Tiebreak:**")
                print(df_tiebreak)
            else:
                # Llamar a la función para calcular probabilidades del juego usando p_serve
                resultado = calculate_game_probabilities(estado_actual, p_serve)
                print_game_probabilities(resultado)           
            # -------------------------------------
            # --------------- SET -----------------
            # -------------------------------------
            # 📌 Si es un tiebreak (6-6 en juegos), llamar a TiebreakCalculator
            if estado_actual.t1_games == 6 and estado_actual.t2_games == 6:
                print("\n🎾 **Tiebreak detectado. Calculando probabilidades...**")
                estado_tiebreak = MatchState(
                    t1_points=estado_actual.t1_points,
                    t2_points=estado_actual.t2_points,
                    t1_games=6,
                    t2_games=6,
                    t1_sets=estado_actual.t1_sets,
                    t2_sets=estado_actual.t2_sets,
                    serve=estado_actual.serve
                )
                tiebreak_calculator = TiebreakCalculator(estado_tiebreak)
                df_tiebreak = tiebreak_calculator.calculate_probabilities()

                print("\n🔹 **Probabilidades del Tiebreak:**")
                print(df_tiebreak)
            
            else:
                # 📌 Generar secuencias de juego
                analysis_file_path = r"CSVFiles/Data/Set_Analysis_with_T1_and_T2_Wins.csv"
                output_csv_ifwin = r"CSVFiles/Exports/Updated_Set_Analysis_IfWin.csv"
                output_csv_ifloss = r"CSVFiles/Exports/Updated_Set_Analysis_IfLoss.csv"

                generate_game_sequence(estado_actual, analysis_file_path, output_csv_ifwin, output_csv_ifloss, win=True)
                generate_game_sequence(estado_actual, analysis_file_path, output_csv_ifwin, output_csv_ifloss, win=False)

                # 📌 Generar Set_Probabilities.csv con SetProbabilitiesGenerator
                probabilities_file = r"CSVFiles/Exports/Set_Probabilities.csv"

                generator = SetProbabilitiesGenerator(
                    analysis_file=analysis_file_path,
                    probabilities_file=probabilities_file,
                    p_games_won_on_serve=p_games_won_on_serve,
                    match_state=estado_actual
                )
                
                # 📌 Después, calcular probabilidades de IfWin y IfLoss con SetProbabilityCalculator
                output_file_ifwin = r"CSVFiles/Exports/Final_Probabilities_IfWin.csv"
                output_file_ifloss = r"CSVFiles/Exports/Final_Probabilities_IfLoss.csv"

                calculator = SetProbabilityCalculator(
                    analysis_file_ifwin=output_csv_ifwin,
                    analysis_file_ifloss=output_csv_ifloss,
                    probabilities_file=probabilities_file,
                    output_file_ifwin=output_file_ifwin,
                    output_file_ifloss=output_file_ifloss,
                    estado_actual=estado_actual
                )

                # 📌 Leer probabilidades finales
                prob_if_win = leer_probabilidad_final(output_file_ifwin)
                prob_if_loss = leer_probabilidad_final(output_file_ifloss)

                # 📌 Mostrar resultados
                print("\n🔹 **Resultados del cálculo de probabilidades del set:**")
                print(f"   ➡️ Si T1 gana el siguiente juego, su probabilidad de ganar el set: {prob_if_win}")
                print(f"   ➡️ Si T1 pierde el siguiente juego, su probabilidad de ganar el set: {prob_if_loss}")
                probabilidad_ganar_juego = calc_total_game_probability(p_serve, 1-p_serve, estado_actual)

                # Convertir a float las cadenas con '%'
                prob_if_win = float(prob_if_win.strip('%')) / 100
                prob_if_loss = float(prob_if_loss.strip('%')) / 100

                # Si probabilidad_ganar_juego > 1, se asume que está en %
                if probabilidad_ganar_juego > 1:
                    probabilidad_ganar_juego /= 100

                # Calcular la prob. de ganar el set combinando
                probabilidad_ganar_set = (probabilidad_ganar_juego * prob_if_win) + ((1 - probabilidad_ganar_juego) * prob_if_loss)
                probabilidad_ganar_set_percent = probabilidad_ganar_set * 100

                print(f"🔹 Probabilidad de ganar el set: {probabilidad_ganar_set_percent:.2f}%")

                # Guardamos en la variable su valor decimal
                probabilidad_ganar_set = probabilidad_ganar_set
            # -------------------------------------
            # --------------- PARTIDO -------------
            # -------------------------------------
                        # Queremos usar probabilidad_ganar_set
            if probabilidad_ganar_set is None:
                print("⚠️ Debes calcular primero la probabilidad de ganar el set (opción 2) antes de usar esta opción.")
            else:
                ifwin, ifloss = probability_match(estado_actual)
                # prob. ganar el partido = prob. ganar set * ifwin + (1 - prob. ganar set) * ifloss
                prob_ganar_partido = (probabilidad_ganar_set * ifwin) + ((1 - probabilidad_ganar_set) * ifloss)
                prob_ganar_partido_percent = prob_ganar_partido * 100
                print(f"🔹 Probabilidad de ganar el partido: {prob_ganar_partido_percent:.2f}%")

        elif choice == "6":
            print("Saliendo del programa. ¡Hasta luego! 👋")
            break

        else:
            print("❌ Opción no válida. Por favor, selecciona una opción entre 1 y 5.")

if __name__ == "__main__":
    main()
