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


if __name__ == "__main__":
    # For testing without API, you could call main() here,
    # but typically this module would be run via uvicorn.
    uvicorn.run("main-connected:app", host="0.0.0.0", port=8000, reload=True)