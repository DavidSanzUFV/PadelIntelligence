import io
import sys
from contextlib import redirect_stdout
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import pandas as pd
import psycopg2
from fastapi.middleware.cors import CORSMiddleware

# Import your algorithm modules
from Modules.Games.match_result import MatchState
from Modules.Games.games_format_results import calculate_game_probabilities, print_game_probabilities
from Modules.Sets.GenerateSecuences import generate_game_sequence
from Modules.Sets.SetProbabilitiesGenerator import SetProbabilitiesGenerator
from Modules.Sets.ProbabilityCalculator import SetProbabilityCalculator
from Modules.TieBreak.TieBreak import TiebreakCalculator
from Modules.Games.games_calculations import calc_total_game_probability
from Modules.Match.Algo_match import probability_match

DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "PadelIntelligence1",
    "host": "localhost",
    "port": "5432"
}

def leer_probabilidad_final(file_path):
    """
    Lee la fila con 'Iteración' = 'Total' del archivo de probabilidades
    y devuelve la probabilidad final.
    """
    try:
        df = pd.read_csv(file_path, delimiter=';', encoding='utf-8', on_bad_lines='skip')
        df_total = df[df['Iteración'] == 'Total']

        if df_total.empty:
            print(f"⚠️ Advertencia: No se encontró la fila 'Total' en {file_path}.")
            return "N/A"

        return df_total['Calculated_Probability'].values[0]

    except Exception as e:
        print(f"❌ Error al leer {file_path}: {e}")
        return "N/A"

# Define an input model for match state and parameters
class MatchInput(BaseModel):
    t1_points: int
    t2_points: int
    t1_games: int
    t2_games: int
    t1_sets: int
    t2_sets: int
    serve: int
    p_serve: float
    p_games_won_on_serve: float

app = FastAPI(title="Padel Intelligence API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello from main-connected.py!"}

@app.post("/run_prediction/")
def run_prediction(match: MatchInput):
    # Create the MatchState object from the input
    estado_actual = MatchState(
        t1_points=match.t1_points,
        t2_points=match.t2_points,
        t1_games=match.t1_games,
        t2_games=match.t2_games,
        t1_sets=match.t1_sets,
        t2_sets=match.t2_sets,
        serve=match.serve
    )

    # Prepare to capture all printed output
    buffer = io.StringIO()
    try:
        with redirect_stdout(buffer):
            # Game probability calculation
            if estado_actual.t1_games == 6 and estado_actual.t2_games == 6:
                print("\n🎾 Tiebreak detected. Calculating game probabilities...")
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
                print("\n🔹 Tiebreak Probabilities:")
                print(df_tiebreak)
            else:
                resultado = calculate_game_probabilities(estado_actual, match.p_serve)
                print_game_probabilities(resultado)
            
            # Set probability calculation
            if estado_actual.t1_games == 6 and estado_actual.t2_games == 6:
                print("\n🎾 Tiebreak detected. Calculating set probabilities...")
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
                print("\n🔹 Tiebreak Probabilities:")
                print(df_tiebreak)
            else:
                analysis_file_path = r"CSVFiles/Data/Set_Analysis_with_T1_and_T2_Wins.csv"
                output_csv_ifwin = r"CSVFiles/Exports/Updated_Set_Analysis_IfWin.csv"
                output_csv_ifloss = r"CSVFiles/Exports/Updated_Set_Analysis_IfLoss.csv"
                generate_game_sequence(estado_actual, analysis_file_path, output_csv_ifwin, output_csv_ifloss, win=True)
                generate_game_sequence(estado_actual, analysis_file_path, output_csv_ifwin, output_csv_ifloss, win=False)
                probabilities_file = r"CSVFiles/Exports/Set_Probabilities.csv"
                generator = SetProbabilitiesGenerator(
                    analysis_file=analysis_file_path,
                    probabilities_file=probabilities_file,
                    p_games_won_on_serve=match.p_games_won_on_serve,
                    match_state=estado_actual
                )
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
                prob_if_win = leer_probabilidad_final(output_file_ifwin)
                prob_if_loss = leer_probabilidad_final(output_file_ifloss)
                print("\n🔹 Set Winning Probability Results:")
                print(f"   ➡️ If T1 wins the next game, probability of winning the set: {prob_if_win}")
                print(f"   ➡️ If T1 loses the next game, probability of winning the set: {prob_if_loss}")
                probabilidad_ganar_juego = calc_total_game_probability(match.p_serve, 1-match.p_serve, estado_actual)
                prob_if_win = float(prob_if_win.strip('%')) / 100
                prob_if_loss = float(prob_if_loss.strip('%')) / 100
                if probabilidad_ganar_juego > 1:
                    probabilidad_ganar_juego /= 100
                probabilidad_ganar_set = (probabilidad_ganar_juego * prob_if_win) + ((1 - probabilidad_ganar_juego) * prob_if_loss)
                probabilidad_ganar_set_percent = probabilidad_ganar_set * 100
                print(f"🔹 Probability of winning the set: {probabilidad_ganar_set_percent:.2f}%")
            
            # Match winning probability
            print("\n--- Calculating Match Winning Probability ---")
            if 'probabilidad_ganar_set' not in locals() or probabilidad_ganar_set is None:
                print("⚠️ You must calculate the set winning probability first!")
            else:
                ifwin, ifloss = probability_match(estado_actual)
                prob_ganar_partido = (probabilidad_ganar_set * ifwin) + ((1 - probabilidad_ganar_set) * ifloss)
                prob_ganar_partido_percent = prob_ganar_partido * 100
                print(f"🔹 Probability of winning the match: {prob_ganar_partido_percent:.2f}%")
            
    except Exception as e:
        return {"error": str(e)}

    # Return the captured output as a string
    output = buffer.getvalue()
    return {"prediction_output": output}

@app.get("/pairs")
def get_pairs():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        query = """
            SELECT DISTINCT ON (LEAST(p1.player, p2.player), GREATEST(p1.player, p2.player))
                p1.player AS player1,
                p2.player AS player2,
                p1.photo AS photo1,
                p2.photo AS photo2,
                p1.gender AS gender1,
                p2.gender AS gender2,
                p1.nationality AS nationality1,
                p2.nationality AS nationality2
            FROM player_stats p1
            JOIN player_stats p2 
                ON p1.partner = p2.player
                AND p1.player < p2.player  -- 🔹 Evita duplicados invirtiendo parejas
            WHERE p1.player IS NOT NULL 
            AND p2.player IS NOT NULL
            ORDER BY LEAST(p1.player, p2.player), GREATEST(p1.player, p2.player);
        """

        cursor.execute(query)
        pairs = cursor.fetchall()

        cursor.close()
        conn.close()

        def determine_gender(g1, g2):
            if g1 == "W" and g2 == "W":
                return "W"
            elif g1 == "M" and g2 == "M":
                return "M"
            else:
                return "Mixed"

        return [  # Convertir datos a JSON
            {
                "player1": pair[0], 
                "player2": pair[1], 
                "photo1": pair[2], 
                "photo2": pair[3],
                "gender": determine_gender(pair[4], pair[5]),
                "nationality1": pair[6],  
                "nationality2": pair[7]   
            } 
            for pair in pairs
        ]

    except Exception as e:
        print(f"⚠️ ERROR en la consulta SQL: {e}")  # Mostrará el error en la consola
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/players")
def get_players():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        query = """
            SELECT DISTINCT 
                player, 
                photo, 
                gender, 
                nationality,
                brand,
                hand,
                side 
            FROM player_stats 
            ORDER BY player;
        """

        cursor.execute(query)
        players = cursor.fetchall()
        cursor.close()
        conn.close()
        return [  # Convertir datos a JSON
            {
                "player": player[0], 
                "photo": player[1], 
                "gender": player[2], 
                "nationality": player[3],
                "brand": player[4],
                "hand": player[5],
                "side": player[6]
            } 
            for player in players
        ]

    except Exception as e:
        print(f"⚠️ ERROR en la consulta SQL: {e}")  
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/player_stats/{player_name}")
def get_basic_player_stats(player_name: str):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Obtener el side del jugador (para calcular el % cruzado)
        cursor.execute("SELECT side FROM player_stats WHERE player = %s LIMIT 1;", (player_name,))
        side_result = cursor.fetchone()
        side = side_result[0] if side_result else None

        if not side or side not in ['Left', 'Right']:
            raise HTTPException(status_code=400, detail=f"Invalid or missing side for player {player_name}")

        # columna cruzada según el lado
        cross_col = "shot_to_l" if side == "Left" else "shot_to_r"

        query = f"""
            SELECT 
                COUNT(DISTINCT tournament_id) AS tournaments_played,
                COUNT(DISTINCT match_id) AS matches_played,
                ROUND(SUM(CASE WHEN result = 'W' THEN 1 ELSE 0 END)::numeric / 
                    NULLIF(COUNT(DISTINCT match_id), 0) * 100, 2) AS win_rate,

                -- Servicios
                ROUND(AVG(
                    CASE 
                        WHEN num_serves > 0 THEN num_1st_serves::numeric / num_serves
                        ELSE NULL 
                    END
                ) * 100, 2) AS percentage_1st_serves,

                ROUND(AVG(
                    CASE 
                        WHEN num_games_served > 0 THEN num_games_served_won::numeric / num_games_served
                        ELSE NULL 
                    END
                ) * 100, 2) AS percentage_service_games_won,

                -- Táctica
                ROUND(SUM({cross_col})::numeric / NULLIF(SUM(num_shots_wo_returns), 0) * 100, 2) AS percentage_cross,

                -- Resto
                ROUND(SUM(num_flat_returns)::numeric / NULLIF(SUM(num_returns), 0) * 100, 2) AS percentage_flat_returns,
                ROUND(SUM(num_lobbed_returns)::numeric / NULLIF(SUM(num_returns), 0) * 100, 2) AS percentage_lobbed_returns,
                ROUND(SUM(num_return_errors)::numeric / NULLIF(SUM(num_returns), 0) * 100, 2) AS percentage_return_errors,

                -- Juego aéreo
                ROUND(AVG(num_lobs_received)::numeric, 2) AS lobs_received_per_match,
                ROUND(SUM(num_smashes)::numeric / NULLIF(SUM(num_lobs_received), 0) * 100, 2) AS percentage_smashes_from_lobs,
                ROUND(SUM(num_rulos)::numeric / NULLIF(SUM(num_lobs_received), 0) * 100, 2) AS percentage_rulos_from_lobs,
                ROUND(SUM(viborejas)::numeric / NULLIF(SUM(num_lobs_received), 0) * 100, 2) AS percentage_viborejas_from_lobs,
                ROUND(SUM(num_bajadas)::numeric / NULLIF(SUM(num_lobs_received), 0) * 100, 2) AS percentage_bajadas_from_lobs,
                ROUND(SUM(num_points_won_after_smash + rulos_winners + bajadas_winners + viborejas_winners)::numeric 
                      / NULLIF(SUM(num_lobs_received), 0) * 100, 2) AS winners_from_lobs,

                -- Defensa y globos
                SUM(num_smash_defense_winners_salida) AS outside_recoveries,
                ROUND(AVG(num_lobs)::numeric, 2) AS lobs_played_per_match,
                ROUND(AVG(percentage_net_regains_after_lob), 2)*100 AS percentage_net_regains_with_lob,
                ROUND(AVG(num_Unforced_Errors)::numeric, 2) AS unforced_errors_per_match

            FROM player_stats
            WHERE player = %s;
        """

        cursor.execute(query, (player_name,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        return {
            "player": player_name,
            "tournaments_played": result[0],
            "matches_played": result[1],
            "win_rate": float(result[2]) if result[2] is not None else 0.0,
            "percentage_1st_serves": float(result[3]) if result[3] is not None else 0.0,
            "percentage_service_games_won": float(result[4]) if result[4] is not None else 0.0,
            "percentage_cross": float(result[5]) if result[5] is not None else 0.0,
            "percentage_parallel": float(100 - result[5]) if result[5] is not None else 0.0,
            "percentage_flat_returns": float(result[6]) if result[6] is not None else 0.0,
            "percentage_lobbed_returns": float(result[7]) if result[7] is not None else 0.0,
            "percentage_return_errors": float(result[8]) if result[8] is not None else 0.0,
            "lobs_received_per_match": float(result[9]) if result[9] is not None else 0.0,
            "percentage_smashes_from_lobs": float(result[10]) if result[10] is not None else 0.0,
            "percentage_rulos_from_lobs": float(result[11]) if result[11] is not None else 0.0,
            "percentage_viborejas_from_lobs": float(result[12]) if result[12] is not None else 0.0,
            "percentage_bajadas_from_lobs": float(result[13]) if result[13] is not None else 0.0,
            "winners_from_lobs": float(result[14]) if result[14] is not None else 0.0,
            "outside_recoveries": int(result[15]) if result[15] is not None else 0,
            "lobs_played_per_match": float(result[16]) if result[16] is not None else 0.0,
            "net_recovery_with_lob": float(result[17]) if result[17] is not None else 0.0,
            "unforced_errors_per_match": float(result[18]) if result[18] is not None else 0.0
        }

    except Exception as e:
        print(f"❌ Error en player_stats para {player_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # For testing without API, you could call main() here,
    # but typically this module would be run via uvicorn.
    uvicorn.run("main-connected:app", host="0.0.0.0", port=8000, reload=True)