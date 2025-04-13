from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Union
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
from Modules.Games.match_result import MatchState
from Modules.Games.games_format_results import calculate_game_probabilities, print_game_probabilities
from Modules.Sets.GenerateSecuences import generate_game_sequence
from Modules.Sets.SetProbabilitiesGenerator import SetProbabilitiesGenerator
from Modules.Sets.ProbabilityCalculator import SetProbabilityCalculator
from Modules.TieBreak.TieBreak import TiebreakCalculator
from Modules.Games.games_calculations import calc_total_game_probability
from Modules.Match.Algo_match import probability_match
from typing import Union
from pydantic import BaseModel
import os

import io
import sys
from contextlib import redirect_stdout
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import pandas as pd
import psycopg2
from psycopg2 import sql
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
from typing import Union
from pydantic import BaseModel, Field
import logging
import pandas as pd
import os


# Import your algorithm modules
from Modules.Games.match_result import MatchState
from Modules.Games.games_format_results import calculate_game_probabilities, print_game_probabilities
from Modules.Sets.GenerateSecuences import generate_game_sequence
from Modules.Sets.SetProbabilitiesGenerator import SetProbabilitiesGenerator
from Modules.Sets.ProbabilityCalculator import SetProbabilityCalculator
from Modules.TieBreak.TieBreak import TiebreakCalculator
from Modules.Games.games_calculations import calc_total_game_probability
from Modules.Match.Algo_match import probability_match

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Permitir todos los encabezados
)


import os

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "postgres"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "options": "-c client_encoding=UTF8"
}

class MatchInput(BaseModel):
    t1_points: str
    t2_points: str
    t1_games: int
    t2_games: int
    t1_sets: int
    t2_sets: int
    serve: int
    p_serve: float
    p_games_won_on_serve: float

# Mapeo de puntos en formato tenis
score_map = {
    "0": 0,
    "15": 1,
    "30": 2,
    "40": 3,
    "Adv": 4
}

def leer_probabilidad_final(file_path):
    """
    Lee la última fila con 'Iteración' = 'Total' del archivo de probabilidades
    y devuelve la probabilidad final.
    """
    try:
        # Ruta absoluta
        absolute_path = os.path.abspath(file_path)
        logging.info(f"🌐 Ruta absoluta del archivo: {absolute_path}")

        # Verificar existencia del archivo
        if not os.path.exists(absolute_path):
            logging.error(f"❌ El archivo no existe en la ruta: {absolute_path}")
            return 0.0

        # Intentar leer el archivo
        logging.info(f"📂 Intentando leer el archivo: {file_path}")
        df = pd.read_csv(file_path, delimiter=';', encoding='utf-8', on_bad_lines='skip')

        # Filtrar las filas donde 'Iteración' tenga el valor 'Total'
        df_total = df[df['Iteración'].astype(str).str.strip() == 'Total']

        # Verificar si encontramos alguna fila con 'Total'
        if df_total.empty:
            logging.warning(f"⚠️ No se encontró la fila 'Total' en {file_path}.")
            return 0.0

        # Tomar la última fila con 'Total'
        last_total_row = df_total.iloc[-1]

        # Extraer la probabilidad calculada
        calculated_probability = str(last_total_row['Calculated_Probability']).strip()

        # Verificar si el valor contiene '%' y eliminarlo
        if isinstance(calculated_probability, str) and '%' in calculated_probability:
            calculated_probability = calculated_probability.replace('%', '').strip()
            logging.info(f"🔧 Probabilidad después de limpiar caracteres: {calculated_probability}")

        # Intentar convertir a flotante después de limpiar
        try:
            calculated_probability = float(calculated_probability)
            logging.info(f"✅ Probabilidad convertida a número: {calculated_probability}")
        except ValueError:
            logging.error(f"❌ Error al convertir la probabilidad: {calculated_probability}")
            return 0.0

        # Dividir por 100 si es un valor mayor a 1 (representando un porcentaje)
        if calculated_probability > 1:
            calculated_probability /= 100

        return calculated_probability

    except Exception as e:
        logging.error(f"❌ Error al leer {file_path}: {e}")
        return 0.0


def validar_resultado(estado):
    """ Valida el estado del partido. """
    try:
        # Validación de sets ganados (partido terminado o inválido)
        if (estado.t1_sets == 2 and estado.t2_sets >= 1) or (estado.t2_sets == 2 and estado.t1_sets >= 1):
            raise HTTPException(status_code=400, detail="⚠️ El partido ya está terminado!")
        if estado.t1_sets == 2 and estado.t2_sets == 2:
            raise HTTPException(status_code=400, detail="⚠️ Marcador de sets inválido: 2-2 no es posible!")

        # Validación de juegos (set ganado)
        if (estado.t1_games == 6 and estado.t2_games <= 4) or (estado.t2_games == 6 and estado.t1_games <= 4):
            raise HTTPException(status_code=400, detail="⚠️ Conteo de juegos no válido! El set ya está ganado.")
        if (estado.t1_games == 7 and estado.t2_games == 5) or (estado.t2_games == 7 and estado.t1_games == 5):
            raise HTTPException(status_code=400, detail="⚠️ Conteo de juegos no válido! El set ya está ganado (7-5).")

        # Validación de puntos: si alguien tiene "Adv", el otro debe tener "40"
        if (estado.t1_points == 4 and estado.t2_points != 3) or (estado.t2_points == 4 and estado.t1_points != 3):
            raise HTTPException(status_code=400, detail="⚠️ Puntos no válidos! Si alguien tiene 'Adv', el otro debe tener '40'.")

        # Validación de tie-break: solo ocurre cuando ambos tienen 6 juegos
        if estado.t1_games == 6 and estado.t2_games == 6:
            if abs(estado.t1_points - estado.t2_points) >= 2 and (estado.t1_points >= 7 or estado.t2_points >= 7):
                raise HTTPException(status_code=400, detail="⚠️ Tie-break ya ganado!")
        return True

    except HTTPException as e:
        logging.error(f"❌ Validación fallida: {e.detail}")
        raise
# Configuración del logging
logging.basicConfig(level=logging.INFO)

from fastapi import FastAPI
import logging

app = FastAPI()

@app.get("/test")
async def test():
    return {"message": "CORS funcionando correctamente"}
@app.options("/run_prediction/")
async def options_run_prediction():
    return {
        "Allow": "POST, OPTIONS",
        "Content-Length": "0",
        "Content-Type": "text/plain"
    }

@app.post("/run_prediction/")
async def run_prediction(match: MatchInput):
    try:
        # Detectar si el partido está en tiebreak (6-6 en juegos)
        is_tiebreak = (match.t1_games == 6 and match.t2_games == 6)

        # Inicializar variables de puntos
        if is_tiebreak:
            # Si es tiebreak, los puntos son números directamente
            try:
                t1_points = int(match.t1_points)
                t2_points = int(match.t2_points)
                if t1_points < 0 or t2_points < 0:
                    raise ValueError("Puntos no válidos en tiebreak.")
            except ValueError:
                raise ValueError("Puntos no válidos. Solo se permiten números enteros positivos en tiebreak.")
        else:
            # Para juegos normales, usar el mapeo tradicional
            t1_points = score_map.get(match.t1_points, -1)
            t2_points = score_map.get(match.t2_points, -1)

            if t1_points == -1 or t2_points == -1:
                raise ValueError("Puntos no válidos. Solo se permiten 0, 15, 30, 40, Adv en juegos normales.")

        logging.info(f"✅ Puntos convertidos: T1: {t1_points}, T2: {t2_points}")

        # Crear el estado del partido
        estado_actual = MatchState(
            t1_points=t1_points,
            t2_points=t2_points,
            t1_games=match.t1_games,
            t2_games=match.t2_games,
            t1_sets=match.t1_sets,
            t2_sets=match.t2_sets,
            serve=match.serve
        )
        logging.info(f"✅ Estado actual creado: {estado_actual}")

        if is_tiebreak:
            tiebreak_calculator = TiebreakCalculator(estado_actual)
            tie_break_probs = tiebreak_calculator.calculate_probabilities()

            if tie_break_probs is None:
                raise ValueError("El cálculo del tie-break devolvió un valor nulo.")

            # Obtener las probabilidades del tiebreak correctamente
            prob_tiebreak_t1 = float(tie_break_probs.get("tiebreak_probability_t1", "0").replace('%', '').strip()) / 100
            prob_tiebreak_t2 = float(tie_break_probs.get("tiebreak_probability_t2", "0").replace('%', '').strip()) / 100

            game_probability = {
                "tiebreak_probability_t1": f"{prob_tiebreak_t1 * 100:.2f}%",
                "tiebreak_probability_t2": f"{prob_tiebreak_t2 * 100:.2f}%",
                "if_win_next_point": tie_break_probs.get("if_win_next_point", "0"),
                "if_lose_next_point": tie_break_probs.get("if_lose_next_point", "0")
            }

            # Calcular la probabilidad de ganar el set como el resultado del tiebreak
            probabilidad_ganar_set = prob_tiebreak_t1
            prob_if_win = probabilidad_ganar_set
            prob_if_loss = 1 - probabilidad_ganar_set

            # Calcular la probabilidad de ganar el partido después del set
            ifwin, ifloss = probability_match(estado_actual)
            prob_ganar_partido = (prob_if_win * ifwin) + (prob_if_loss * ifloss)

            # Inicializar correctamente set_probability para el caso de tiebreak
            set_probability = {
                "if_win": f"{prob_if_win * 100:.2f}%",
                "if_loss": f"{prob_if_loss * 100:.2f}%",
                "calculated": f"{probabilidad_ganar_set:.2f}%"
            }

            # Calcular la probabilidad de ganar el partido usando el resultado del tiebreak
            match_probability = {
                "if_win_tiebreak": f"{ifwin * 100:.2f}%",
                "if_loss_tiebreak": f"{ifloss * 100:.2f}%",
                "match_total": f"{prob_ganar_partido * 100:.2f}%"
            }

            logging.info(f"✅ Probabilidades formateadas correctamente (tiebreak): {match_probability}")


        else:
            game_probability = calculate_game_probabilities(estado_actual, match.p_serve)

            analysis_file_path = "CSVFiles/Data/Set_Analysis_with_T1_and_T2_Wins.csv"
            output_csv_ifwin = "CSVFiles/Exports/Updated_Set_Analysis_IfWin.csv"
            output_csv_ifloss = "CSVFiles/Exports/Updated_Set_Analysis_IfLoss.csv"

            generate_game_sequence(estado_actual, analysis_file_path, output_csv_ifwin, output_csv_ifloss, win=True)
            generate_game_sequence(estado_actual, analysis_file_path, output_csv_ifwin, output_csv_ifloss, win=False)

            probabilities_file = "CSVFiles/Exports/Set_Probabilities.csv"
            output_file_ifwin = "CSVFiles/Exports/Final_Probabilities_IfWin.csv"
            output_file_ifloss = "CSVFiles/Exports/Final_Probabilities_IfLoss.csv"

            generator = SetProbabilitiesGenerator(
                analysis_file=analysis_file_path,
                probabilities_file=probabilities_file,
                p_games_won_on_serve=match.p_games_won_on_serve,
                match_state=estado_actual
            )

            calculator = SetProbabilityCalculator(
                analysis_file_ifwin=output_csv_ifwin,
                analysis_file_ifloss=output_csv_ifloss,
                probabilities_file=probabilities_file,
                output_file_ifwin=output_file_ifwin,
                output_file_ifloss=output_file_ifloss,
                estado_actual=estado_actual
            )

            # Leer probabilidades finales correctamente
            prob_if_win = leer_probabilidad_final(output_file_ifwin)
            prob_if_loss = leer_probabilidad_final(output_file_ifloss)

            # Calcular probabilidad de ganar el juego
            probabilidad_ganar_juego = calc_total_game_probability(match.p_serve, 1 - match.p_serve, estado_actual)

            if probabilidad_ganar_juego > 1:
                probabilidad_ganar_juego = probabilidad_ganar_juego / 100

            # Calcular probabilidad de ganar el set
            prob_if_win = prob_if_win / 100 if prob_if_win > 1 else prob_if_win
            prob_if_loss = prob_if_loss / 100 if prob_if_loss > 1 else prob_if_loss

            probabilidad_ganar_set = (probabilidad_ganar_juego * prob_if_win) + ((1 - probabilidad_ganar_juego) * prob_if_loss)
            print("➕ [DEBUG] prob_if_win:", prob_if_win)
            print("➕ [DEBUG] prob_if_loss:", prob_if_loss)
            print("➕ [DEBUG] probabilidad_ganar_juego:", probabilidad_ganar_juego)
            print("➕ [DEBUG] Resultado set:", probabilidad_ganar_set)

            # Calcular probabilidad de ganar el partido
            ifwin, ifloss = probability_match(estado_actual)
            prob_ganar_partido = (probabilidad_ganar_set * ifwin) + ((1 - probabilidad_ganar_set) * ifloss)

            set_probability = {
                "if_win": f"{prob_if_win * 100:.2f}%",
                "if_loss": f"{prob_if_loss * 100:.2f}%",
                "calculated": f"{probabilidad_ganar_set* 100:.2f}%"
            }

            match_probability = {
                "if_win_set": f"{ifwin * 100:.2f}%",
                "if_loss_set": f"{ifloss * 100:.2f}%",
                "match_total": f"{prob_ganar_partido* 100:.2f}%"
            }

        response = {
            "game_probability": game_probability,
            "set_probability": set_probability,
            "match_probability": match_probability,
            "set_win_probability": f"{probabilidad_ganar_set* 100:.2f}%"
        }

        logging.info(f"✅ Respuesta generada: {response}")
        return response

    except Exception as e:
        # Obtener el tipo de excepción y el mensaje de error
        error_type = type(e).__name__
        error_message = str(e)

        # Obtener información adicional del contexto si es posible
        logging.error(f"❗ Error en el endpoint: {error_type} - {error_message}")

        # Intentar capturar el contexto del error si es posible
        try:
            error_context = sys.exc_info()[2]
            logging.error(f"📝 Contexto del error: {error_context}")
        except Exception as context_error:
            logging.error(f"⚠️ No se pudo obtener el contexto del error: {str(context_error)}")

        # Devolver una respuesta de error con detalles
        return {
            "error": [True, f"Unexpected error of type {error_type}: {error_message}"],
            "traceback": repr(e)
        }
@app.get("/pairs")
def get_pairs():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        query = """
            SELECT DISTINCT ON (LEAST(p1.player_id, p2.player_id), GREATEST(p1.player_id, p2.player_id))
                p1.player_id AS player1_id,
                p1.player AS player1,
                p2.player_id AS player2_id,
                p2.player AS player2,
                p1.photo AS photo1,
                p2.photo AS photo2,
                p1.gender AS gender1,
                p2.gender AS gender2,
                p1.nationality AS nationality1,
                p2.nationality AS nationality2
            FROM player_stats p1
            JOIN player_stats p2 
                ON p1.partner_id = p2.player_id
                AND p1.player_id < p2.player_id
            WHERE p1.player IS NOT NULL 
            AND p2.player IS NOT NULL
            ORDER BY LEAST(p1.player_id, p2.player_id), GREATEST(p1.player_id, p2.player_id);
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

        return [
            {
                "player1_id": pair[0],
                "player1": pair[1],
                "player2_id": pair[2],
                "player2": pair[3],
                "photo1": pair[4],
                "photo2": pair[5],
                "gender": determine_gender(pair[6], pair[7]),
                "nationality1": pair[8],
                "nationality2": pair[9],
            }
            for pair in pairs
        ]

    except Exception as e:
        print(f"⚠️ ERROR en la consulta SQL: {e}")
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/pairs_name")
def get_pairs_name():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        query = """
            SELECT DISTINCT ON (LEAST(p1.player_id, p2.player_id), GREATEST(p1.player_id, p2.player_id))
                p1.player AS player1,
                p2.player AS player2
            FROM player_stats p1
            JOIN player_stats p2 
                ON p1.partner_id = p2.player_id
                AND p1.player_id < p2.player_id
            WHERE p1.player IS NOT NULL 
            AND p2.player IS NOT NULL
            ORDER BY LEAST(p1.player_id, p2.player_id), GREATEST(p1.player_id, p2.player_id);
        """

        cursor.execute(query)
        pairs = cursor.fetchall()
        cursor.close()
        conn.close()

        # Formatear los nombres como "player1 / player2"
        formatted_pairs = [f"{pair[0]} / {pair[1]}" for pair in pairs]

        return {"pairs": formatted_pairs}

    except Exception as e:
        print(f"⚠️ ERROR en la consulta SQL: {e}")
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
                ROUND(AVG(num_Unforced_Errors)::numeric, 2) AS unforced_errors_per_match,
                
                -- Variables Radar Chart
                AVG(ci_per_point) AS ci_per_point,
                ROUND(COALESCE(AVG(num_direct_points_on_serve)::numeric, 0), 2) AS num_direct_points_on_serve,
                ROUND(COALESCE((AVG(percentage_points_won_on_serve_team) * 100)::numeric, 0), 2) AS percentage_points_won_on_serve_team,
                ROUND(COALESCE((AVG(percentage_points_won_return_team) * 100)::numeric, 0), 2) AS percentage_points_won_return_team,
                ROUND(COALESCE((AVG(percentage_shots_smash) * 100)::numeric, 0), 2) AS percentage_shots_smash,
                ROUND(COALESCE(AVG(num_bajadas)::numeric, 0), 2) AS num_bajadas,
                ROUND(COALESCE((AVG(percentage_viborejas_winners) * 100)::numeric, 0), 2) AS percentage_viborejas_winners,
                ROUND(COALESCE((AVG(percentage_winners) * 100)::numeric, 0), 2) AS percentage_winners,
                ROUND(COALESCE((AVG(percentage_assists_shots) * 100)::numeric, 0), 2) AS percentage_assists_shots,
                ROUND(COALESCE((AVG(percentage_error_setups) * 100)::numeric, 0), 2) AS percentage_error_setups,
                ROUND(COALESCE((AVG(percentage_ue) * 100)::numeric, 0), 2) AS percentage_ue,
                ROUND(COALESCE((AVG(percentage_pe) * 100)::numeric, 0), 2) AS percentage_pe,
                ROUND(COALESCE((AVG(percentage_winner_setups) * 100)::numeric, 0), 2) AS percentage_winner_setups,
                ROUND(COALESCE(AVG(num_smash_defenses)::numeric, 0), 2) AS num_smash_defenses


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
            "unforced_errors_per_match": float(result[18]) if result[18] is not None else 0.0,
            "ci_per_point": float(result[19]) if result[19] is not None else 0.0,
            "num_direct_points_on_serve": float(result[20]) if result[20] is not None else 0.0,
            "percentage_points_won_on_serve_team": float(result[21]) if result[21] is not None else 0.0,
            "percentage_points_won_return_team": float(result[22]) if result[22] is not None else 0.0,
            "percentage_shots_smash": float(result[23]) if result[23] is not None else 0.0,
            "num_bajadas": float(result[24]) if result[24] is not None else 0.0,
            "percentage_viborejas_winners": float(result[25]) if result[25] is not None else 0.0,
            "percentage_winners": float(result[26]) if result[26] is not None else 0.0,
            "percentage_assists_shots": float(result[27]) if result[27] is not None else 0.0,
            "percentage_error_setups": float(result[28]) if result[28] is not None else 0.0,
            "percentage_ue": float(result[29]) if result[29] is not None else 0.0,
            "percentage_pe": float(result[30]) if result[30] is not None else 0.0,
            "percentage_winner_setups": float(result[31]) if result[31] is not None else 0.0,
            "num_smash_defenses": float(result[32]) if result[32] is not None else 0.0,

        }

    except Exception as e:
        print(f"❌ Error en player_stats para {player_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/curiosities")
def get_curiosities():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        curiosities = {}

        # 1. Nationality Ranking
        cursor.execute("""
            SELECT nationality, COUNT(*) AS count
            FROM (
                SELECT DISTINCT player_id, nationality
                FROM player_stats
                WHERE nationality IS NOT NULL
            ) AS unique_players
            GROUP BY nationality
            ORDER BY count DESC
            LIMIT 3;
        """)
        nationalities = cursor.fetchall()
        curiosities["Nationality Ranking"] = [f"{row[0]} ({row[1]})" for row in nationalities]

        # 2. Racket Brand Usage
        cursor.execute("""
            SELECT brand, COUNT(*) AS count
            FROM (
                SELECT DISTINCT player_id, brand
                FROM player_stats
                WHERE brand IS NOT NULL AND brand != 'Default' 
            ) AS unique_players
            GROUP BY brand
            ORDER BY count DESC
            LIMIT 3;
        """)
        brands = cursor.fetchall()
        curiosities["Racket Brand Usage"] = [f"{row[0]} ({row[1]})" for row in brands]

        # 3. Most Wins
        cursor.execute("""
            SELECT player, COUNT(*) as wins
            FROM player_stats
            WHERE result = 'W'
            GROUP BY player
            ORDER BY wins DESC
            LIMIT 3;
        """)
        wins = cursor.fetchall()
        curiosities["Most Wins"] = [f"{row[0]} ({row[1]} wins)" for row in wins]

        # 4. Most Partner Changes
        cursor.execute("""
            SELECT player, COUNT(DISTINCT partner) as num_partners
            FROM player_stats
            WHERE partner IS NOT NULL
            GROUP BY player
            ORDER BY num_partners DESC
            LIMIT 3;
        """)

        partner_changes = cursor.fetchall()
        curiosities["Most Partner Changes"] = [
            f"{row[0]} ({row[1]} partners)" for row in partner_changes
        ]


        # 5. Main Draw Gender Ratio
        cursor.execute("""
            SELECT gender, COUNT(*) 
            FROM (
                SELECT DISTINCT player_id, gender
                FROM player_stats
                WHERE gender IS NOT NULL
            ) AS unique_players
            GROUP BY gender;
        """)
        gender_counts = dict(cursor.fetchall())
        total = sum(gender_counts.values())
        men = gender_counts.get("M", 0)
        women = gender_counts.get("W", 0)
        ratio = f"{round(men / total * 100)}% Men / {round(women / total * 100)}% Women"
        curiosities["Main Draw Gender Ratio"] = [ratio]
    #6  Cross vs Parallel — Top 3 jugadores con mayor % de bolas cruzadas:
        cursor.execute("""
                WITH player_sides AS (
                    SELECT player_id, MAX(side) AS side
                    FROM player_stats
                    WHERE side IN ('Left', 'Right')
                    GROUP BY player_id
                ),
                player_cross_stats AS (
                    SELECT 
                        ps.player_id,
                        CASE 
                            WHEN ps.side = 'Left' THEN AVG(shot_to_l::float / NULLIF(num_shots_wo_returns, 0)) 
                            WHEN ps.side = 'Right' THEN AVG(shot_to_r::float / NULLIF(num_shots_wo_returns, 0)) 
                        END AS avg_cross_percentage
                    FROM player_stats ps
                    JOIN player_sides USING (player_id)
                    GROUP BY ps.player_id, ps.side
                )
                SELECT ps.player AS player_name, 
                    ROUND((pcs.avg_cross_percentage * 100)::numeric, 2) AS cross_percentage
                FROM player_cross_stats pcs
                JOIN player_stats ps ON ps.player_id = pcs.player_id
                GROUP BY ps.player, pcs.avg_cross_percentage
                ORDER BY cross_percentage DESC
                LIMIT 3;
            """)
        cross_top3 = cursor.fetchall()

        cross_results = [
                {"player": row[0], "cross_percentage": float(row[1])}
                for row in cross_top3
            ]

# 7 Top 3 jugadores en net recovery después de lob (% promedio):
        cursor.execute("""
            SELECT ps.player AS player_name, 
                ROUND(AVG(ps.percentage_net_regains_after_lob) * 100, 2) AS avg_net_recovery_lob
            FROM player_stats ps
            WHERE ps.percentage_net_regains_after_lob IS NOT NULL
            GROUP BY ps.player
            HAVING COUNT(*) >= 5
            ORDER BY avg_net_recovery_lob DESC
            LIMIT 3;
        """)
        lob_net_recovery_top3 = cursor.fetchall()

        lob_recovery_results = [
            {"player": row[0], "net_recovery_lob": float(row[1])}
            for row in lob_net_recovery_top3
        ]
# 8 Top 3 jugadores con mayor % de smashes por globo recibido:
        cursor.execute("""
            SELECT ps.player AS player_name,
                ROUND((SUM(ps.num_smashes)::numeric / NULLIF(SUM(ps.num_lobs_received), 0)) * 100, 2) AS smash_percentage
            FROM player_stats ps
            WHERE ps.num_smashes IS NOT NULL AND ps.num_lobs_received > 0
            GROUP BY ps.player
            HAVING COUNT(*) >= 5
            ORDER BY smash_percentage DESC
            LIMIT 3;
        """)

        smash_lobs_top3 = cursor.fetchall()

        smash_lobs_results = [
            {"player": row[0], "smash_percentage": float(row[1])}
            for row in smash_lobs_top3
        ]

#9 - Top 3 jugadores con más lobs jugados por partido (AVG(num_lobs)):
        cursor.execute("""
            SELECT ps.player AS player_name,
                ROUND(AVG(ps.num_lobs)::numeric, 2) AS avg_lobs_per_match
            FROM player_stats ps
            WHERE ps.num_lobs IS NOT NULL
            GROUP BY ps.player
            HAVING COUNT(*) >= 5
            ORDER BY avg_lobs_per_match DESC
            LIMIT 3;
        """)

        top3_avg_lobs = cursor.fetchall()
        avg_lobs_results = [
            {"player": row[0], "avg_lobs_per_match": float(row[1])}
            for row in top3_avg_lobs
        ]

#10 - Total de globos jugados en toda la temporada (SUM(num_lobs)):
        cursor.execute("""
            SELECT SUM(num_lobs)
            FROM player_stats
            WHERE num_lobs IS NOT NULL;
        """)

        total_lobs = cursor.fetchone()[0] or 0

#11 - Top 3 jugadores con mayor % de globos en sus partidos
        cursor.execute("""
            SELECT ps.player AS player_name,
                ROUND(AVG(ps.percentage_lobs)::numeric, 2) AS avg_lob_percentage
            FROM player_stats ps
            WHERE ps.percentage_lobs IS NOT NULL
            GROUP BY ps.player
            HAVING COUNT(*) >= 5
            ORDER BY avg_lob_percentage DESC
            LIMIT 3;
        """)

        top3_lob_percentage = cursor.fetchall()
        lob_percentage_results = [
            {"player": row[0], "avg_lob_percentage": float(row[1])}
            for row in top3_lob_percentage
        ]
#12 - Top 3 jugadores con más winners de viborejas por partido (AVG(viborejas_winners)):

        cursor.execute("""
            SELECT ps.player AS player_name,
                ROUND(AVG(ps.viborejas_winners)::numeric, 2) AS avg_viborejas_winners
            FROM player_stats ps
            WHERE ps.viborejas_winners IS NOT NULL
            GROUP BY ps.player
            HAVING COUNT(*) >= 5
            ORDER BY avg_viborejas_winners DESC
            LIMIT 3;
        """)

        top3_viborejas = cursor.fetchall()
        viborejas_results = [
            {"player": row[0], "avg_viborejas_winners": float(row[1])}
            for row in top3_viborejas
        ]

#13 - Porcentaje de remates defendidos (Total remates ganados en defensa / Total remates intentados):
        cursor.execute("""
            SELECT 
                SUM(num_smash_defense_winners_salida) AS total_defended,
                SUM(num_points_won_after_smash) AS total_attacking_points
            FROM player_stats;
        """)

        total_defense_data = cursor.fetchone()
        total_defended = total_defense_data[0] or 0
        total_remates = total_defense_data[1] or 1  # Para evitar división por 0
        percentage_defended = round((total_defended / total_remates) * 100, 2)

#14 - Top 3 jugadores con más salidas defensivas (smash_defense_winners_salida):
        cursor.execute("""
            SELECT ps.player AS player_name,
                SUM(ps.num_smash_defense_winners_salida) AS total_exits
            FROM player_stats ps
            WHERE ps.num_smash_defense_winners_salida IS NOT NULL
            GROUP BY ps.player
            ORDER BY total_exits DESC
            LIMIT 3;
        """)

        top3_exits = cursor.fetchall()
        exits_results = [
            {"player": row[0], "total_exits": int(row[1])}
            for row in top3_exits
        ]            

#15 - Top 3 jugadores con mayor porcentaje de primeros saques
        cursor.execute("""
            SELECT ps.player AS player_name,
                ROUND(AVG(
                    CASE 
                        WHEN ps.num_serves > 0 THEN ps.num_1st_serves::numeric / ps.num_serves
                        ELSE NULL
                    END
                ) * 100, 2) AS first_serve_percentage
            FROM player_stats ps
            WHERE ps.num_serves > 0
            GROUP BY ps.player
            HAVING COUNT(*) >= 5
            ORDER BY first_serve_percentage DESC
            LIMIT 3;
        """)

        top3_first_serves = cursor.fetchall()
        first_serves_results = [
            {"player": row[0], "first_serve_percentage": float(row[1])}
            for row in top3_first_serves
        ]

 #16 - Top 3 jugadores con mayor media de percentage_lobbed_returns:
        cursor.execute("""
            SELECT ps.player AS player_name,
                ROUND(AVG(ps.percentage_lobbed_returns)::numeric, 2) AS avg_lobbed_returns
            FROM player_stats ps
            WHERE ps.percentage_lobbed_returns IS NOT NULL
            GROUP BY ps.player
            HAVING COUNT(*) >= 5
            ORDER BY avg_lobbed_returns DESC
            LIMIT 3;
        """)

        top3_lobbed_returns = cursor.fetchall()
        lobbed_returns_results = [
            {"player": row[0], "avg_lobbed_returns": float(row[1])}
            for row in top3_lobbed_returns
        ]
 #17 - Top 3 jugadores con mayor ratio de errores al resto (num_return_errors / num_returns):
        cursor.execute("""
            SELECT ps.player AS player_name,
                ROUND(AVG(
                    CASE 
                        WHEN ps.num_returns > 0 THEN ps.num_return_errors::numeric / ps.num_returns
                        ELSE NULL
                    END
                ) * 100, 2) AS return_error_percentage
            FROM player_stats ps
            GROUP BY ps.player
            HAVING COUNT(*) >= 5  -- al menos 5 partidos jugados
            ORDER BY return_error_percentage DESC
            LIMIT 3;
        """)

        top3_return_errors = cursor.fetchall()
        return_errors_results = [
            {"player": row[0], "return_error_percentage": float(row[1])}
            for row in top3_return_errors
        ]
        cursor.close()
        conn.close()

        cursor.close()
        conn.close()

        return {
            "Rankings & Player Profiles": {
                "Nationality Ranking": curiosities["Nationality Ranking"],
                "Racket Brand Usage": curiosities["Racket Brand Usage"],
                "Most Wins": curiosities["Most Wins"],
                "Most Partner Changes": curiosities["Most Partner Changes"],
                "Main Draw Gender Ratio": curiosities["Main Draw Gender Ratio"]
            },
            "Playing Style & Tactics": {
                "Cross vs Parallel": cross_results,
                "Lob to Net Gain %": lob_recovery_results,
                "Smash Percentage": smash_lobs_results
            },
            "Shot Frequency": {
                "Lobs per Match": avg_lobs_results,
                "Total Lobs This Season": [f"{total_lobs:,}"],
                "Lob Usage %": lob_percentage_results
            },
            "Effectiveness": {
                "Avg of Winners of Viborejas per match": viborejas_results,
                "Smash Defenses": [f"{percentage_defended}%"],
                "Court Exits": exits_results
            },
            "Serve & Return": {
                "1st vs 2nd Serve": first_serves_results,
                "Returns: Lob vs Low": lobbed_returns_results,
                "Return Errors": return_errors_results
            }
        }

    except Exception as e:
        print(f"❌ Error in /curiosities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/highlights")
def get_highlights():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        highlights = []

        # 🧊 QUERY 1 - Biggest Nevera
        cursor.execute("""          WITH lowest_stat AS (
                SELECT 
                    player_id,
                    partner_id,
                    match_id,
                    player,
                    date,
                    tournament_id,
                    percentage_balls
                FROM 
                    player_stats
                ORDER BY 
                    percentage_balls ASC
                LIMIT 1
            ),
            players_in_match AS (
                SELECT 
                    ps.player AS opponent_name
                FROM 
                    player_stats ps
                JOIN lowest_stat ls ON ps.match_id = ls.match_id
                WHERE 
                    ps.player_id NOT IN (ls.player_id, ls.partner_id)
            ),
            partner AS (
                SELECT player AS partner_name
                FROM player_stats
                WHERE player_id = (SELECT partner_id FROM lowest_stat)
                LIMIT 1
            ),
            tournament AS (
                SELECT tournament_name
                FROM tournaments
                WHERE tournament_id = (SELECT tournament_id FROM lowest_stat)
            )
            SELECT 
                ls.player,
                p.partner_name,
                ls.percentage_balls,
                t.tournament_name,
                ARRAY_AGG(pim.opponent_name) AS opponents
            FROM lowest_stat ls
            JOIN players_in_match pim ON TRUE
            JOIN partner p ON TRUE
            JOIN tournament t ON TRUE
            GROUP BY ls.player, p.partner_name, ls.percentage_balls, t.tournament_name;""")  
        row = cursor.fetchone()
        player, partner_name, percentage_balls, tournament_name, opponents = row

        value_short = f"{player} hit only {round(percentage_balls * 100, 1)}% of the balls"

        value_long = (
            f"The biggest nevera of the year happened at {tournament_name}, "
            f"in a match featuring {player}, {partner_name}, {opponents[0]} and {opponents[1]}. "
            f"{player} hit only {round(percentage_balls * 100, 1)}% of the balls."
        )

        highlights.append({
            "title": "Biggest Nevera of the Year",
            "player": f"{player} & {partner_name} vs {opponents[0]} & {opponents[1]}",
            "valueShort": value_short,
            "valueLong": value_long,
            "location": tournament_name
        })

        # 🔁 QUERY 2 - Most Shots
        cursor.execute("""WITH total_shots_per_match AS (
    SELECT 
        match_id,
        SUM(num_shots) AS total_shots
    FROM 
        player_stats
    GROUP BY 
        match_id
),
top_match AS (
    SELECT 
        match_id,
        total_shots
    FROM 
        total_shots_per_match
    ORDER BY 
        total_shots DESC
    LIMIT 1
),
players_in_match AS (
    SELECT 
        player,
        match_id,
        ROW_NUMBER() OVER () AS rn
    FROM 
        player_stats
    WHERE 
        match_id = (SELECT match_id FROM top_match)
),
tournament AS (
    SELECT 
        tournament_name
    FROM 
        tournaments
    WHERE 
        tournament_id = (
            SELECT tournament_id FROM player_stats
            WHERE match_id = (SELECT match_id FROM top_match)
            LIMIT 1
        )
)
SELECT 
    (SELECT total_shots FROM top_match) AS total_shots,
    (SELECT tournament_name FROM tournament) AS tournament_name,
    MAX(CASE WHEN rn = 1 THEN player END) AS player1,
    MAX(CASE WHEN rn = 2 THEN player END) AS player2,
    MAX(CASE WHEN rn = 3 THEN player END) AS player3,
    MAX(CASE WHEN rn = 4 THEN player END) AS player4
FROM 
    players_in_match;

""")  
        row = cursor.fetchone()
        total_shots, tournament_name, p1, p2, p3, p4 = row

        value_short = f"{total_shots} shots played"

        value_long = (
            f"The match with the most shots was played at {tournament_name}, "
            f"featuring {p1}, {p2}, {p3} and {p4}, with a total of {total_shots} shots."
        )

        highlights.append({
            "title": "Most Shots in a Match",
            "player": f"{p1} & {p2} vs {p3} & {p4}",
            "valueShort": value_short,
            "valueLong": value_long,
            "location": tournament_name
        })

# 🟣 QUERY 3 - Most Points in a Match
        cursor.execute("""
            WITH top_match AS (
                SELECT 
                    match_id,
                    points_played
                FROM 
                    player_stats
                ORDER BY 
                    points_played DESC
                LIMIT 1
            ),
            players_in_match AS (
                SELECT 
                    player,
                    ROW_NUMBER() OVER () AS rn
                FROM 
                    player_stats
                WHERE 
                    match_id = (SELECT match_id FROM top_match)
            ),
            tournament AS (
                SELECT tournament_name
                FROM tournaments
                WHERE tournament_id = (
                    SELECT tournament_id FROM player_stats
                    WHERE match_id = (SELECT match_id FROM top_match)
                    LIMIT 1
                )
            )
            SELECT 
                (SELECT points_played FROM top_match) AS points_played,
                (SELECT tournament_name FROM tournament),
                MAX(CASE WHEN rn = 1 THEN player END),
                MAX(CASE WHEN rn = 2 THEN player END),
                MAX(CASE WHEN rn = 3 THEN player END),
                MAX(CASE WHEN rn = 4 THEN player END)
            FROM players_in_match;
        """)

        row = cursor.fetchone()
        points, tournament_name, p1, p2, p3, p4 = row

        value_short = f"{points} points played"

        value_long = (
            f"The match with the most points was played at {tournament_name}, "
            f"featuring {p1}, {p2}, {p3}, and {p4}, with a total of {points} points."
        )

        highlights.append({
            "title": "Most Points in a Match",
            "player": f"{p1} & {p2} vs {p3} & {p4}",
            "valueShort": value_short,
            "valueLong": value_long,
            "location": tournament_name
        })

# 🌫️ QUERY 4 - Most Lobs in a Match
        cursor.execute("""
            WITH total_lobs_per_match AS (
                SELECT 
                    match_id,
                    SUM(num_lobs) AS total_lobs
                FROM 
                    player_stats
                GROUP BY 
                    match_id
            ),
            top_match AS (
                SELECT 
                    match_id,
                    total_lobs
                FROM 
                    total_lobs_per_match
                ORDER BY 
                    total_lobs DESC
                LIMIT 1
            ),
            players_in_match AS (
                SELECT 
                    player,
                    ROW_NUMBER() OVER () AS rn
                FROM 
                    player_stats
                WHERE 
                    match_id = (SELECT match_id FROM top_match)
            ),
            tournament AS (
                SELECT tournament_name
                FROM tournaments
                WHERE tournament_id = (
                    SELECT tournament_id FROM player_stats
                    WHERE match_id = (SELECT match_id FROM top_match)
                    LIMIT 1
                )
            )
            SELECT 
                (SELECT total_lobs FROM top_match) AS total_lobs,
                (SELECT tournament_name FROM tournament),
                MAX(CASE WHEN rn = 1 THEN player END),
                MAX(CASE WHEN rn = 2 THEN player END),
                MAX(CASE WHEN rn = 3 THEN player END),
                MAX(CASE WHEN rn = 4 THEN player END)
            FROM players_in_match;
        """)

        row = cursor.fetchone()
        total_lobs, tournament_name, p1, p2, p3, p4 = row

        value_short = f"{total_lobs} lobs played"

        value_long = (
            f"The match with the most lobs was played at {tournament_name}, "
            f"featuring {p1}, {p2}, {p3}, and {p4}, with a total of {total_lobs} lobs."
        )

        highlights.append({
            "title": "Most Lobs in a Match",
            "player": f"{p1} & {p2} vs {p3} & {p4}",
            "valueShort": value_short,
            "valueLong": value_long,
            "location": tournament_name
        })

        # 🚪 QUERY 5 - Most Door Exits in a Match
        cursor.execute("""
            WITH total_door_exits_per_match AS (
                SELECT 
                    match_id,
                    SUM(num_Smash_Defense_winners_Salida) AS total_door_exits
                FROM 
                    player_stats
                GROUP BY 
                    match_id
            ),
            top_match AS (
                SELECT 
                    match_id,
                    total_door_exits
                FROM 
                    total_door_exits_per_match
                ORDER BY 
                    total_door_exits DESC
                LIMIT 1
            ),
            players_in_match AS (
                SELECT 
                    player,
                    ROW_NUMBER() OVER () AS rn
                FROM 
                    player_stats
                WHERE 
                    match_id = (SELECT match_id FROM top_match)
            ),
            tournament AS (
                SELECT tournament_name
                FROM tournaments
                WHERE tournament_id = (
                    SELECT tournament_id FROM player_stats
                    WHERE match_id = (SELECT match_id FROM top_match)
                    LIMIT 1
                )
            )
            SELECT 
                (SELECT total_door_exits FROM top_match) AS total_door_exits,
                (SELECT tournament_name FROM tournament),
                MAX(CASE WHEN rn = 1 THEN player END),
                MAX(CASE WHEN rn = 2 THEN player END),
                MAX(CASE WHEN rn = 3 THEN player END),
                MAX(CASE WHEN rn = 4 THEN player END)
            FROM players_in_match;
        """)

        row = cursor.fetchone()
        door_exits, tournament_name, p1, p2, p3, p4 = row

        value_short = f"{door_exits} door exits"
        value_long = (
            f"The match with the most door exits was played at {tournament_name}, "
            f"featuring {p1}, {p2}, {p3}, and {p4}, with a total of {door_exits} exits."
        )

        highlights.append({
            "title": "Most Door Exits per Match",
            "player": f"{p1} & {p2} vs {p3} & {p4}",
            "valueShort": value_short,
            "valueLong": value_long,
            "location": tournament_name
        })

        # 💥 QUERY 6 - Most Smashes in a Match
        cursor.execute("""
            WITH total_smashes_per_match AS (
                SELECT 
                    match_id,
                    SUM(num_smashes) AS total_smashes
                FROM 
                    player_stats
                GROUP BY 
                    match_id
            ),
            top_match AS (
                SELECT 
                    match_id,
                    total_smashes
                FROM 
                    total_smashes_per_match
                ORDER BY 
                    total_smashes DESC
                LIMIT 1
            ),
            players_in_match AS (
                SELECT 
                    player,
                    ROW_NUMBER() OVER () AS rn
                FROM 
                    player_stats
                WHERE 
                    match_id = (SELECT match_id FROM top_match)
            ),
            tournament AS (
                SELECT tournament_name
                FROM tournaments
                WHERE tournament_id = (
                    SELECT tournament_id FROM player_stats
                    WHERE match_id = (SELECT match_id FROM top_match)
                    LIMIT 1
                )
            )
            SELECT 
                (SELECT total_smashes FROM top_match) AS total_smashes,
                (SELECT tournament_name FROM tournament),
                MAX(CASE WHEN rn = 1 THEN player END),
                MAX(CASE WHEN rn = 2 THEN player END),
                MAX(CASE WHEN rn = 3 THEN player END),
                MAX(CASE WHEN rn = 4 THEN player END)
            FROM players_in_match;
        """)

        row = cursor.fetchone()
        smashes, tournament_name, p1, p2, p3, p4 = row

        value_short = f"{smashes} smashes"
        value_long = (
            f"The match with the most smashes was played at {tournament_name}, "
            f"featuring {p1}, {p2}, {p3}, and {p4}, with a total of {smashes} smashes."
        )

        highlights.append({
            "title": "Most Smashes in a Match",
            "player": f"{p1} & {p2} vs {p3} & {p4}",
            "valueShort": value_short,
            "valueLong": value_long,
            "location": tournament_name
        })

        # ❄️ QUERY 7 - Fewest Smashes in a Match
        cursor.execute("""
            WITH total_smashes_per_match AS (
                SELECT 
                    match_id,
                    SUM(num_smashes) AS total_smashes
                FROM 
                    player_stats
                GROUP BY 
                    match_id
            ),
            bottom_match AS (
                SELECT 
                    match_id,
                    total_smashes
                FROM 
                    total_smashes_per_match
                ORDER BY 
                    total_smashes ASC
                LIMIT 1
            ),
            players_in_match AS (
                SELECT 
                    player,
                    ROW_NUMBER() OVER () AS rn
                FROM 
                    player_stats
                WHERE 
                    match_id = (SELECT match_id FROM bottom_match)
            ),
            tournament AS (
                SELECT tournament_name
                FROM tournaments
                WHERE tournament_id = (
                    SELECT tournament_id FROM player_stats
                    WHERE match_id = (SELECT match_id FROM bottom_match)
                    LIMIT 1
                )
            )
            SELECT 
                (SELECT total_smashes FROM bottom_match) AS total_smashes,
                (SELECT tournament_name FROM tournament),
                MAX(CASE WHEN rn = 1 THEN player END),
                MAX(CASE WHEN rn = 2 THEN player END),
                MAX(CASE WHEN rn = 3 THEN player END),
                MAX(CASE WHEN rn = 4 THEN player END)
            FROM players_in_match;
        """)

        row = cursor.fetchone()
        smashes, tournament_name, p1, p2, p3, p4 = row

        value_short = f"{smashes} smashes"
        value_long = (
            f"The match with the fewest smashes was played at {tournament_name}, "
            f"featuring {p1}, {p2}, {p3}, and {p4}, with only {smashes} smashes."
        )

        highlights.append({
            "title": "Fewest Smashes in a Match",
            "player": f"{p1} & {p2} vs {p3} & {p4}",
            "valueShort": value_short,
            "valueLong": value_long,
            "location": tournament_name
        })

        # 🧼 QUERY 8 - Fewest Unforced Errors in a Match
        cursor.execute("""
            WITH total_errors_per_match AS (
                SELECT 
                    match_id,
                    SUM(num_Unforced_Errors) AS total_errors
                FROM 
                    player_stats
                GROUP BY 
                    match_id
            ),
            bottom_match AS (
                SELECT 
                    match_id,
                    total_errors
                FROM 
                    total_errors_per_match
                ORDER BY 
                    total_errors ASC
                LIMIT 1
            ),
            players_in_match AS (
                SELECT 
                    player,
                    ROW_NUMBER() OVER () AS rn
                FROM 
                    player_stats
                WHERE 
                    match_id = (SELECT match_id FROM bottom_match)
            ),
            tournament AS (
                SELECT tournament_name
                FROM tournaments
                WHERE tournament_id = (
                    SELECT tournament_id FROM player_stats
                    WHERE match_id = (SELECT match_id FROM bottom_match)
                    LIMIT 1
                )
            )
            SELECT 
                (SELECT total_errors FROM bottom_match) AS total_unforced_errors,
                (SELECT tournament_name FROM tournament),
                MAX(CASE WHEN rn = 1 THEN player END),
                MAX(CASE WHEN rn = 2 THEN player END),
                MAX(CASE WHEN rn = 3 THEN player END),
                MAX(CASE WHEN rn = 4 THEN player END)
            FROM players_in_match;
        """)

        row = cursor.fetchone()
        errors, tournament_name, p1, p2, p3, p4 = row

        value_short = f"{errors} unforced errors"
        value_long = (
            f"The match with the fewest unforced errors was played at {tournament_name}, "
            f"featuring {p1}, {p2}, {p3}, and {p4}, with only {errors} unforced errors."
        )

        highlights.append({
            "title": "Fewest Unforced Errors",
            "player": f"{p1} & {p2} vs {p3} & {p4}",
            "valueShort": value_short,
            "valueLong": value_long,
            "location": tournament_name
        })

        # 🔁 QUERY 9 - Most Repeated Matchup of the Year
        cursor.execute("""
            WITH player_pairs AS (
                SELECT
                    match_id,
                    LEAST(player_id, partner_id) AS p1,
                    GREATEST(player_id, partner_id) AS p2
                FROM player_stats
            ),
            matchups_ordered AS (
                SELECT
                    match_id,
                    MIN(p1) AS teamA_player1,
                    MIN(p2) AS teamA_player2,
                    MAX(p1) AS teamB_player1,
                    MAX(p2) AS teamB_player2
                FROM player_pairs
                GROUP BY match_id
            ),
            matchup_counts AS (
                SELECT
                    LEAST(teamA_player1, teamB_player1) AS a1,
                    LEAST(teamA_player2, teamB_player2) AS a2,
                    GREATEST(teamA_player1, teamB_player1) AS b1,
                    GREATEST(teamA_player2, teamB_player2) AS b2,
                    COUNT(*) AS times_played,
                    MAX(match_id) AS sample_match
                FROM matchups_ordered
                GROUP BY
                    LEAST(teamA_player1, teamB_player1),
                    LEAST(teamA_player2, teamB_player2),
                    GREATEST(teamA_player1, teamB_player1),
                    GREATEST(teamA_player2, teamB_player2)
                ORDER BY times_played DESC
                LIMIT 1
            ),
            players_in_match AS (
                SELECT
                    player_id,
                    player
                FROM player_stats
                WHERE match_id = (SELECT sample_match FROM matchup_counts)
            )
            SELECT
                mc.times_played,
                MAX(CASE WHEN pim.player_id = mc.a1 THEN pim.player END),
                MAX(CASE WHEN pim.player_id = mc.a2 THEN pim.player END),
                MAX(CASE WHEN pim.player_id = mc.b1 THEN pim.player END),
                MAX(CASE WHEN pim.player_id = mc.b2 THEN pim.player END)
            FROM matchup_counts mc
            JOIN players_in_match pim
            ON pim.player_id IN (mc.a1, mc.a2, mc.b1, mc.b2)
            GROUP BY mc.a1, mc.a2, mc.b1, mc.b2, mc.times_played;
        """)

        row = cursor.fetchone()
        times_played, p1, p2, p3, p4 = row

        value_short = f"Played {times_played} times"
        value_long = (
            f"The most repeated matchup of the year was played {times_played} times "
            f"between {p1} & {p2} vs {p3} & {p4}."
        )

        highlights.append({
            "title": "Most Repeated Matchup",
            "player": f"{p1} & {p2} vs {p3} & {p4}",
            "valueShort": value_short,
            "valueLong": value_long,
            "location": "Premier Padel"
        })

        # 🔥 QUERY 10 - Most Long Points in a Match
        cursor.execute("""
            WITH long_point_totals AS (
                SELECT
                    match_id,
                    tournament_id,
                    SUM(num_long_points_winners + num_long_points_ue + num_long_points_pe) AS total_long_points
                FROM player_stats
                GROUP BY match_id, tournament_id
            ),
            top_match AS (
                SELECT 
                    match_id,
                    tournament_id,
                    total_long_points
                FROM long_point_totals
                ORDER BY total_long_points DESC
                LIMIT 1
            ),
            players_in_top_match AS (
                SELECT 
                    player,
                    ROW_NUMBER() OVER () AS rn
                FROM player_stats
                WHERE match_id = (SELECT match_id FROM top_match)
            ),
            tournament AS (
                SELECT tournament_name
                FROM tournaments
                WHERE tournament_id = (SELECT tournament_id FROM top_match)
            )
            SELECT 
                tm.total_long_points,
                (SELECT tournament_name FROM tournament),
                MAX(CASE WHEN pitm.rn = 1 THEN pitm.player END),
                MAX(CASE WHEN pitm.rn = 2 THEN pitm.player END),
                MAX(CASE WHEN pitm.rn = 3 THEN pitm.player END),
                MAX(CASE WHEN pitm.rn = 4 THEN pitm.player END)
            FROM top_match tm
            JOIN players_in_top_match pitm ON TRUE
            GROUP BY tm.total_long_points;
        """)

        row = cursor.fetchone()
        long_points, tournament_name, p1, p2, p3, p4 = row

        value_short = f"{long_points} long rallies"
        value_long = (
            f"The match with the most long points was played at {tournament_name}, "
            f"featuring {p1}, {p2}, {p3}, and {p4}, with a total of {long_points} long rallies."
        )

        highlights.append({
            "title": "Most Long Points Played",
            "player": f"{p1} & {p2} vs {p3} & {p4}",
            "valueShort": value_short,
            "valueLong": value_long,
            "location": tournament_name
        })

        # 🎯 QUERY 11 - Most Winners in a Match
        cursor.execute("""
            WITH total_winners_per_match AS (
                SELECT
                    match_id,
                    tournament_id,
                    SUM(num_winners) AS total_winners
                FROM player_stats
                GROUP BY match_id, tournament_id
            ),
            top_match AS (
                SELECT 
                    match_id,
                    tournament_id,
                    total_winners
                FROM total_winners_per_match
                ORDER BY total_winners DESC
                LIMIT 1
            ),
            players_in_match AS (
                SELECT 
                    player,
                    ROW_NUMBER() OVER () AS rn
                FROM player_stats
                WHERE match_id = (SELECT match_id FROM top_match)
            ),
            tournament AS (
                SELECT tournament_name
                FROM tournaments
                WHERE tournament_id = (SELECT tournament_id FROM top_match)
            )
            SELECT 
                tm.total_winners,
                (SELECT tournament_name FROM tournament),
                MAX(CASE WHEN pim.rn = 1 THEN pim.player END),
                MAX(CASE WHEN pim.rn = 2 THEN pim.player END),
                MAX(CASE WHEN pim.rn = 3 THEN pim.player END),
                MAX(CASE WHEN pim.rn = 4 THEN pim.player END)
            FROM top_match tm
            JOIN players_in_match pim ON TRUE
            GROUP BY tm.total_winners;
        """)

        row = cursor.fetchone()
        winners, tournament_name, p1, p2, p3, p4 = row
        value_short = f"{winners} winners"
        value_long = (
            f"The match with the most winners was played at {tournament_name}, "
            f"featuring {p1}, {p2}, {p3}, and {p4}, with a total of {winners} winners."
        )

        highlights.append({
            "title": "Most Winners in a Match",
            "player": f"{p1} & {p2} vs {p3} & {p4}",
            "valueShort": value_short,
            "valueLong": value_long,
            "location": tournament_name
        })

        # 💣 QUERY 12 - Most Forced Errors in a Match
        cursor.execute("""
            WITH total_forced_errors_per_match AS (
                SELECT
                    match_id,
                    tournament_id,
                    SUM(num_pressured_errors) AS total_forced_errors
                FROM player_stats
                GROUP BY match_id, tournament_id
            ),
            top_match AS (
                SELECT 
                    match_id,
                    tournament_id,
                    total_forced_errors
                FROM total_forced_errors_per_match
                ORDER BY total_forced_errors DESC
                LIMIT 1
            ),
            players_in_match AS (
                SELECT 
                    player,
                    ROW_NUMBER() OVER () AS rn
                FROM player_stats
                WHERE match_id = (SELECT match_id FROM top_match)
            ),
            tournament AS (
                SELECT tournament_name
                FROM tournaments
                WHERE tournament_id = (SELECT tournament_id FROM top_match)
            )
            SELECT 
                tm.total_forced_errors,
                (SELECT tournament_name FROM tournament),
                MAX(CASE WHEN pim.rn = 1 THEN pim.player END),
                MAX(CASE WHEN pim.rn = 2 THEN pim.player END),
                MAX(CASE WHEN pim.rn = 3 THEN pim.player END),
                MAX(CASE WHEN pim.rn = 4 THEN pim.player END)
            FROM top_match tm
            JOIN players_in_match pim ON TRUE
            GROUP BY tm.total_forced_errors;
        """)

        row = cursor.fetchone()
        forced_errors, tournament_name, p1, p2, p3, p4 = row

        value_short = f"{forced_errors} forced errors"
        value_long = (
            f"The match with the most forced errors was played at {tournament_name}, "
            f"featuring {p1}, {p2}, {p3}, and {p4}, with a total of {forced_errors} forced errors."
        )

        highlights.append({
            "title": "Most Forced Errors in a Match",
            "player": f"{p1} & {p2} vs {p3} & {p4}",
            "valueShort": value_short,
            "valueLong": value_long,
            "location": tournament_name
        })


#TERMINAR
        cursor.close()
        conn.close()

        return highlights

    except Exception as e:
        print(f"❌ ERROR en /highlights: {e}")
        raise HTTPException(status_code=500, detail=str(e))


from fastapi import HTTPException

@app.get("/pair_stats/{player1_id}/{player2_id}")
def get_pair_stats(player1_id: int, player2_id: int):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Validar que haya al menos una fila con esa pareja
        cursor.execute("""
            SELECT COUNT(*) 
            FROM player_stats 
            WHERE (player_id = %s AND partner_id = %s) 
               OR (player_id = %s AND partner_id = %s);
        """, (player1_id, player2_id, player2_id, player1_id))

        count_result = cursor.fetchone()
        if count_result[0] == 0:
            raise HTTPException(status_code=404, detail="No data found for this pair")

        # Obtener sides de cada jugador
        cursor.execute("""
            SELECT player_id, side 
            FROM player_stats 
            WHERE player_id IN (%s, %s)
            GROUP BY player_id, side;
        """, (player1_id, player2_id))
        sides_raw = dict(cursor.fetchall())

        side1 = sides_raw.get(player1_id)
        side2 = sides_raw.get(player2_id)

        if not side1 or not side2:
            raise HTTPException(status_code=400, detail="Missing side for one of the players")

        # Columna cruzada
        cross_col = sql.Identifier("shot_to_l" if side1 == "Left" else "shot_to_r")

        query = sql.SQL("""
            SELECT 
                COUNT(DISTINCT tournament_id),
                COUNT(DISTINCT match_id),
                ROUND(
                        COUNT(DISTINCT CASE WHEN result = 'W' THEN match_id END)::numeric / 
                        NULLIF(COUNT(DISTINCT match_id), 0) * 100, 2),
                ROUND(AVG(CASE WHEN num_serves > 0 THEN num_1st_serves::numeric / num_serves ELSE NULL END) * 100, 2),
                ROUND(AVG(CASE WHEN num_games_served > 0 THEN num_games_served_won::numeric / num_games_served ELSE NULL END) * 100, 2),
                ROUND(SUM({cross_col})::numeric / NULLIF(SUM(num_shots_wo_returns), 0) * 100, 2),
                ROUND(SUM(num_flat_returns)::numeric / NULLIF(SUM(num_returns), 0) * 100, 2),
                ROUND(SUM(num_lobbed_returns)::numeric / NULLIF(SUM(num_returns), 0) * 100, 2),
                ROUND(SUM(num_return_errors)::numeric / NULLIF(SUM(num_returns), 0) * 100, 2),

                ROUND(AVG(num_lobs_received)::numeric, 2),
                ROUND(SUM(num_smashes)::numeric / NULLIF(SUM(num_lobs_received), 0) * 100, 2),
                ROUND(SUM(num_rulos)::numeric / NULLIF(SUM(num_lobs_received), 0) * 100, 2),
                ROUND(SUM(viborejas)::numeric / NULLIF(SUM(num_lobs_received), 0) * 100, 2),
                ROUND(SUM(num_bajadas)::numeric / NULLIF(SUM(num_lobs_received), 0) * 100, 2),
                ROUND(SUM(num_points_won_after_smash + rulos_winners + bajadas_winners + viborejas_winners)::numeric 
                      / NULLIF(SUM(num_lobs_received), 0) * 100, 2),

                SUM(num_smash_defense_winners_salida),
                ROUND(AVG(num_lobs)::numeric, 2),
                ROUND(AVG(percentage_net_regains_after_lob) * 100, 2),
                ROUND(AVG(num_Unforced_Errors)::numeric, 2),
                -- Variables Radar Chart para Parejas
                AVG(ci_per_point) AS ci_per_point,
                ROUND(COALESCE(AVG(num_direct_points_on_serve)::numeric, 0), 2) AS num_direct_points_on_serve,
                ROUND(COALESCE((AVG(percentage_points_won_on_serve_team) * 100)::numeric, 0), 2) AS percentage_points_won_on_serve_team,
                ROUND(COALESCE((AVG(percentage_points_won_return_team) * 100)::numeric, 0), 2) AS percentage_points_won_return_team,
                ROUND(COALESCE((AVG(percentage_shots_smash) * 100)::numeric, 0), 2) AS percentage_shots_smash,
                ROUND(COALESCE(AVG(num_bajadas)::numeric, 0), 2) AS num_bajadas,
                ROUND(COALESCE((AVG(percentage_viborejas_winners) * 100)::numeric, 0), 2) AS percentage_viborejas_winners,
                ROUND(COALESCE((AVG(percentage_winners) * 100)::numeric, 0), 2) AS percentage_winners,
                ROUND(COALESCE((AVG(percentage_assists_shots) * 100)::numeric, 0), 2) AS percentage_assists_shots,
                ROUND(COALESCE((AVG(percentage_error_setups) * 100)::numeric, 0), 2) AS percentage_error_setups,
                ROUND(COALESCE((AVG(percentage_ue) * 100)::numeric, 0), 2) AS percentage_ue,
                ROUND(COALESCE((AVG(percentage_pe) * 100)::numeric, 0), 2) AS percentage_pe,
                ROUND(COALESCE((AVG(percentage_winner_setups) * 100)::numeric, 0), 2) AS percentage_winner_setups,
                ROUND(COALESCE(AVG(num_smash_defenses)::numeric, 0), 2) AS num_smash_defenses

            FROM player_stats
            WHERE 
                (player_id = %s AND partner_id = %s) 
                OR (player_id = %s AND partner_id = %s);
        """).format(cross_col=cross_col)

        cursor.execute(query, (player1_id, player2_id, player2_id, player1_id))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        return {
            "pair_ids": f"{player1_id} & {player2_id}",
            "tournaments_played": result[0],
            "matches_played": result[1],
            "win_rate": float(result[2]) if result[2] is not None else 0.0,
            "percentage_1st_serves": float(result[3]) or 0.0,
            "percentage_service_games_won": float(result[4]) or 0.0,
            "percentage_cross": float(result[5]) or 0.0,
            "percentage_parallel": 100 - float(result[5]) if result[5] is not None else 0.0,
            "percentage_flat_returns": float(result[6]) or 0.0,
            "percentage_lobbed_returns": float(result[7]) or 0.0,
            "percentage_return_errors": float(result[8]) or 0.0,
            "lobs_received_per_match": float(result[9]) or 0.0,
            "percentage_smashes_from_lobs": float(result[10]) or 0.0,
            "percentage_rulos_from_lobs": float(result[11]) or 0.0,
            "percentage_viborejas_from_lobs": float(result[12]) or 0.0,
            "percentage_bajadas_from_lobs": float(result[13]) or 0.0,
            "winners_from_lobs": float(result[14]) or 0.0,
            "outside_recoveries": int(result[15]) or 0,
            "lobs_played_per_match": float(result[16]) or 0.0,
            "net_recovery_with_lob": float(result[17]) or 0.0,
            "unforced_errors_per_match": float(result[18]) or 0.0,
            "ci_per_point": float(result[19]) if result[19] is not None else 0.0,
            "num_direct_points_on_serve": float(result[20]) if result[20] is not None else 0.0,
            "percentage_points_won_on_serve_team": float(result[21]) if result[21] is not None else 0.0,
            "percentage_points_won_return_team": float(result[22]) if result[22] is not None else 0.0,
            "percentage_shots_smash": float(result[23]) if result[23] is not None else 0.0,
            "num_bajadas": float(result[24]) if result[24] is not None else 0.0,
            "percentage_viborejas_winners": float(result[25]) if result[25] is not None else 0.0,
            "percentage_winners": float(result[26]) if result[26] is not None else 0.0,
            "percentage_assists_shots": float(result[27]) if result[27] is not None else 0.0,
            "percentage_error_setups": float(result[28]) if result[28] is not None else 0.0,
            "percentage_ue": float(result[29]) if result[29] is not None else 0.0,
            "percentage_pe": float(result[30]) if result[30] is not None else 0.0,
            "percentage_winner_setups": float(result[31]) if result[31] is not None else 0.0,
            "num_smash_defenses": float(result[32]) if result[32] is not None else 0.0
        }

    except Exception as e:
        print(f"❌ Error en pair_stats para {player1_id} & {player2_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/benchmark")
def get_benchmark():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Consulta para el benchmark agrupado por género
        query = """
            SELECT gender,
                -- Promedio de torneos jugados y partidos jugados
                ROUND(AVG(tournaments_played), 2) AS tournaments_played,
                ROUND(AVG(matches_played), 2) AS matches_played,
                ROUND(AVG(win_rate), 2) AS win_rate,

                -- Servicios
                ROUND(AVG(percentage_1st_serves), 2) AS percentage_1st_serves,
                ROUND(AVG(percentage_service_games_won), 2) AS percentage_service_games_won,

                -- Táctica
                ROUND(AVG(percentage_cross), 2) AS percentage_cross,

                -- Resto
                ROUND(AVG(percentage_flat_returns), 2) AS percentage_flat_returns,
                ROUND(AVG(percentage_lobbed_returns), 2) AS percentage_lobbed_returns,
                ROUND(AVG(percentage_return_errors), 2) AS percentage_return_errors,

                -- Juego aéreo
                ROUND(AVG(lobs_received_per_match), 2) AS lobs_received_per_match,
                ROUND(AVG(percentage_smashes_from_lobs), 2) AS percentage_smashes_from_lobs,
                ROUND(AVG(percentage_rulos_from_lobs), 2) AS percentage_rulos_from_lobs,
                ROUND(AVG(percentage_viborejas_from_lobs), 2) AS percentage_viborejas_from_lobs,
                ROUND(AVG(percentage_bajadas_from_lobs), 2) AS percentage_bajadas_from_lobs,
                ROUND(AVG(winners_from_lobs), 2) AS winners_from_lobs,

                -- Defensa y globos
                ROUND(AVG(outside_recoveries), 2) AS outside_recoveries,
                ROUND(AVG(lobs_played_per_match), 2) AS lobs_played_per_match,
                ROUND(AVG(net_recovery_with_lob), 2) AS net_recovery_with_lob,
                ROUND(AVG(unforced_errors_per_match), 2) AS unforced_errors_per_match,

                -- Variables Radar Chart
                AVG(ci_per_point) AS ci_per_point,
                ROUND(CAST(AVG(num_direct_points_on_serve) AS numeric), 2) AS num_direct_points_on_serve,
                ROUND(CAST(AVG(percentage_points_won_on_serve_team) AS numeric), 2) AS percentage_points_won_on_serve_team,
                ROUND(CAST(AVG(percentage_points_won_return_team) AS numeric), 2) AS percentage_points_won_return_team,
                ROUND(CAST(AVG(percentage_shots_smash) AS numeric), 2) AS percentage_shots_smash,
                ROUND(CAST(AVG(num_bajadas) AS numeric), 2) AS num_bajadas,
                ROUND(CAST(AVG(percentage_viborejas_winners) AS numeric), 2) AS percentage_viborejas_winners,
                ROUND(CAST(AVG(percentage_winners) AS numeric), 2) AS percentage_winners,
                ROUND(CAST(AVG(percentage_assists_shots) AS numeric), 2) AS percentage_assists_shots,
                ROUND(CAST(AVG(percentage_error_setups) AS numeric), 2) AS percentage_error_setups,
                ROUND(CAST(AVG(percentage_ue) AS numeric), 2) AS percentage_ue,
                ROUND(CAST(AVG(percentage_pe) AS numeric), 2) AS percentage_pe,
                ROUND(CAST(AVG(percentage_winner_setups) AS numeric), 2) AS percentage_winner_setups,
                ROUND(CAST(AVG(num_smash_defenses) AS numeric), 2) AS num_smash_defenses


            FROM (
                SELECT gender,
                    -- Calcular torneos, partidos y win rate por jugador
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
                    ROUND(SUM(shot_to_l)::numeric / NULLIF(SUM(num_shots_wo_returns), 0) * 100, 2) AS percentage_cross,

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
                    ROUND(AVG(percentage_net_regains_after_lob), 2) * 100 AS net_recovery_with_lob,
                    ROUND(AVG(num_Unforced_Errors)::numeric, 2) AS unforced_errors_per_match,

                    -- Variables Radar Chart
                    AVG(ci_per_point) AS ci_per_point,
                    ROUND(CAST(AVG(num_direct_points_on_serve) AS numeric), 2) AS num_direct_points_on_serve,
                    ROUND(CAST(AVG(percentage_points_won_on_serve_team) AS numeric), 2) AS percentage_points_won_on_serve_team,
                    ROUND(CAST(AVG(percentage_points_won_return_team) AS numeric), 2) AS percentage_points_won_return_team,
                    ROUND(CAST(AVG(percentage_shots_smash) AS numeric), 2) AS percentage_shots_smash,
                    ROUND(CAST(AVG(num_bajadas) AS numeric), 2) AS num_bajadas,
                    ROUND(CAST(AVG(percentage_viborejas_winners) AS numeric), 2) AS percentage_viborejas_winners,
                    ROUND(CAST(AVG(percentage_winners) AS numeric), 2) AS percentage_winners,
                    ROUND(CAST(AVG(percentage_assists_shots) AS numeric), 2) AS percentage_assists_shots,
                    ROUND(CAST(AVG(percentage_error_setups) AS numeric), 2) AS percentage_error_setups,
                    ROUND(CAST(AVG(percentage_ue) AS numeric), 2) AS percentage_ue,
                    ROUND(CAST(AVG(percentage_pe) AS numeric), 2) AS percentage_pe,
                    ROUND(CAST(AVG(percentage_winner_setups) AS numeric), 2) AS percentage_winner_setups,
                    ROUND(CAST(AVG(num_smash_defenses) AS numeric), 2) AS num_smash_defenses


                FROM player_stats
                GROUP BY gender, player
            ) AS subquery
            GROUP BY gender;

        """
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        conn.close()

        benchmark = {}
        for row in results:
            gender = row[0]
            benchmark[gender] = {
                "tournaments_played": float(row[1]),
                "matches_played": float(row[2]),
                "win_rate": float(row[3]),
                "percentage_1st_serves": float(row[4]),
                "percentage_service_games_won": float(row[5]),
                "percentage_cross": float(row[6]),
                "percentage_parallel": float(100 - row[6]) if row[6] is not None else 0.0,
                "percentage_flat_returns": float(row[7]),
                "percentage_lobbed_returns": float(row[8]),
                "percentage_return_errors": float(row[9]),
                "lobs_received_per_match": float(row[10]),
                "percentage_smashes_from_lobs": float(row[11]),
                "percentage_rulos_from_lobs": float(row[12]),
                "percentage_viborejas_from_lobs": float(row[13]),
                "percentage_bajadas_from_lobs": float(row[14]),
                "winners_from_lobs": float(row[15]),
                "outside_recoveries": int(row[16]),
                "lobs_played_per_match": float(row[17]),
                "net_recovery_with_lob": float(row[18]),
                "unforced_errors_per_match": float(row[19]),
                "ci_per_point": float(row[20]),
                "num_direct_points_on_serve": float(row[21]),
                "percentage_points_won_on_serve_team": float(row[22]*100),
                "percentage_points_won_return_team": float(row[23]*100),
                "percentage_shots_smash": float(row[24]*100),
                "num_bajadas": float(row[25]),
                "percentage_viborejas_winners": float(row[26]*100),
                "percentage_winners": float(row[27]*100),
                "percentage_assists_shots": float(row[28]*100),
                "percentage_error_setups": float(row[29]*100),
                "percentage_ue": float(row[30]*100),
                "percentage_pe": float(row[31]*100),
                "percentage_winner_setups": float(row[32]*100),
                "num_smash_defenses": float(row[33])
            }

        return benchmark

    except Exception as e:
        print(f"❌ Error al obtener el benchmark: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/benchmark_couples")
def get_benchmark_couples():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        query = """
SELECT gender,
    ROUND(AVG(tournaments_played), 2),
    ROUND(AVG(matches_played), 2),
    ROUND(AVG(win_rate), 2),
    ROUND(AVG(percentage_1st_serves), 2),
    ROUND(AVG(percentage_service_games_won), 2),
    ROUND(AVG(percentage_cross), 2),
    ROUND(AVG(percentage_flat_returns), 2),
    ROUND(AVG(percentage_lobbed_returns), 2),
    ROUND(AVG(percentage_return_errors), 2),
    ROUND(AVG(lobs_received_per_match), 2),
    ROUND(AVG(percentage_smashes_from_lobs), 2),
    ROUND(AVG(percentage_rulos_from_lobs), 2),
    ROUND(AVG(percentage_viborejas_from_lobs), 2),
    ROUND(AVG(percentage_bajadas_from_lobs), 2),
    ROUND(AVG(winners_from_lobs), 2),
    ROUND(AVG(outside_recoveries), 2),
    ROUND(AVG(lobs_played_per_match), 2),
    ROUND(AVG(net_recovery_with_lob), 2),
    ROUND(AVG(unforced_errors_per_match), 2),
    ROUND(AVG(ci_per_point), 2),
    ROUND(AVG(num_direct_points_on_serve), 2),
    ROUND(CAST(AVG(percentage_points_won_on_serve_team) * 100 AS numeric), 2),
    ROUND(CAST(AVG(percentage_points_won_return_team) * 100 AS numeric), 2),
    ROUND(CAST(AVG(percentage_shots_smash) * 100 AS numeric), 2),
    ROUND(AVG(num_bajadas), 2),
    ROUND(CAST(AVG(percentage_viborejas_winners) * 100 AS numeric), 2),
    ROUND(CAST(AVG(percentage_winners) * 100 AS numeric), 2),
    ROUND(CAST(AVG(percentage_assists_shots) * 100 AS numeric), 2),
    ROUND(CAST(AVG(percentage_error_setups) * 100 AS numeric), 2),
    ROUND(CAST(AVG(percentage_ue) * 100 AS numeric), 2),
    ROUND(CAST(AVG(percentage_pe) * 100 AS numeric), 2),
    ROUND(CAST(AVG(percentage_winner_setups) * 100 AS numeric), 2),
    ROUND(AVG(num_smash_defenses), 2)
FROM (
    SELECT 
        LEAST(player_id, partner_id) AS player1_id,
        GREATEST(player_id, partner_id) AS player2_id,
        MAX(gender) AS gender,

        COUNT(DISTINCT tournament_id) AS tournaments_played,
        COUNT(DISTINCT match_id) AS matches_played,
        ROUND(SUM(CASE WHEN result = 'W' THEN 1 ELSE 0 END)::numeric / NULLIF(COUNT(DISTINCT match_id), 0) * 100, 2) AS win_rate,

        ROUND(AVG(CASE WHEN num_serves > 0 THEN num_1st_serves::numeric / num_serves ELSE NULL END) * 100, 2) AS percentage_1st_serves,
        ROUND(AVG(CASE WHEN num_games_served > 0 THEN num_games_served_won::numeric / num_games_served ELSE NULL END) * 100, 2) AS percentage_service_games_won,
        ROUND(SUM(shot_to_l)::numeric / NULLIF(SUM(num_shots_wo_returns), 0) * 100, 2) AS percentage_cross,

        ROUND(SUM(num_flat_returns)::numeric / NULLIF(SUM(num_returns), 0) * 100, 2) AS percentage_flat_returns,
        ROUND(SUM(num_lobbed_returns)::numeric / NULLIF(SUM(num_returns), 0) * 100, 2) AS percentage_lobbed_returns,
        ROUND(SUM(num_return_errors)::numeric / NULLIF(SUM(num_returns), 0) * 100, 2) AS percentage_return_errors,

        ROUND(AVG(num_lobs_received)::numeric, 2) AS lobs_received_per_match,
        ROUND(SUM(num_smashes)::numeric / NULLIF(SUM(num_lobs_received), 0) * 100, 2) AS percentage_smashes_from_lobs,
        ROUND(SUM(num_rulos)::numeric / NULLIF(SUM(num_lobs_received), 0) * 100, 2) AS percentage_rulos_from_lobs,
        ROUND(SUM(viborejas)::numeric / NULLIF(SUM(num_lobs_received), 0) * 100, 2) AS percentage_viborejas_from_lobs,
        ROUND(SUM(num_bajadas)::numeric / NULLIF(SUM(num_lobs_received), 0) * 100, 2) AS percentage_bajadas_from_lobs,
        ROUND(SUM(num_points_won_after_smash + rulos_winners + bajadas_winners + viborejas_winners)::numeric / NULLIF(SUM(num_lobs_received), 0) * 100, 2) AS winners_from_lobs,

        SUM(num_smash_defense_winners_salida) AS outside_recoveries,
        ROUND(AVG(num_lobs)::numeric, 2) AS lobs_played_per_match,
        ROUND(CAST(AVG(percentage_net_regains_after_lob) * 100 AS numeric), 2) AS net_recovery_with_lob,
        ROUND(AVG(num_Unforced_Errors)::numeric, 2) AS unforced_errors_per_match,

        ROUND(AVG(ci_per_point), 2) AS ci_per_point,
        ROUND(AVG(num_direct_points_on_serve), 2) AS num_direct_points_on_serve,
        AVG(percentage_points_won_on_serve_team) AS percentage_points_won_on_serve_team,
        AVG(percentage_points_won_return_team) AS percentage_points_won_return_team,
        AVG(percentage_shots_smash) AS percentage_shots_smash,
        ROUND(AVG(num_bajadas), 2) AS num_bajadas,
        AVG(percentage_viborejas_winners) AS percentage_viborejas_winners,
        AVG(percentage_winners) AS percentage_winners,
        AVG(percentage_assists_shots) AS percentage_assists_shots,
        AVG(percentage_error_setups) AS percentage_error_setups,
        AVG(percentage_ue) AS percentage_ue,
        AVG(percentage_pe) AS percentage_pe,
        AVG(percentage_winner_setups) AS percentage_winner_setups,
        ROUND(AVG(num_smash_defenses), 2) AS num_smash_defenses

    FROM player_stats
    GROUP BY player1_id, player2_id
) AS grouped_pairs
GROUP BY gender;

        """

        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        conn.close()

        keys = [
            "tournaments_played", "matches_played", "win_rate",
            "percentage_1st_serves", "percentage_service_games_won",
            "percentage_cross", "percentage_flat_returns", "percentage_lobbed_returns", "percentage_return_errors",
            "lobs_received_per_match", "percentage_smashes_from_lobs", "percentage_rulos_from_lobs", "percentage_viborejas_from_lobs",
            "percentage_bajadas_from_lobs", "winners_from_lobs", "outside_recoveries", "lobs_played_per_match", "net_recovery_with_lob",
            "unforced_errors_per_match", "ci_per_point", "num_direct_points_on_serve", "percentage_points_won_on_serve_team",
            "percentage_points_won_return_team", "percentage_shots_smash", "num_bajadas", "percentage_viborejas_winners",
            "percentage_winners", "percentage_assists_shots", "percentage_error_setups", "percentage_ue", "percentage_pe",
            "percentage_winner_setups", "num_smash_defenses"
        ]

        benchmark_by_gender = {}
        for row in results:
            gender = row[0]
            benchmark_by_gender[gender] = {
                k: float(v) if v is not None else 0.0 for k, v in zip(keys, row[1:])
            }

        return benchmark_by_gender

    except Exception as e:
        print(f"❌ Error en benchmark_couples: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/benchmark_max")
def get_benchmark_max():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Consulta SQL ajustada por género
        query = """
            SELECT gender,
                MAX(avg_ci_per_point) AS max_ci_per_point,
                MAX(avg_num_direct_points_on_serve) AS max_direct_points_on_serve,
                MAX(avg_percentage_points_won_on_serve_team) AS max_points_won_on_serve_team,
                MAX(avg_percentage_return_errors) AS max_percentage_return_errors,
                MAX(avg_percentage_points_won_return_team) AS max_points_won_return_team,
                MAX(avg_percentage_shots_smash) AS max_shots_smash,
                MAX(avg_num_bajadas) AS max_bajadas,
                MAX(avg_percentage_viborejas_winners) AS max_viborejas_winners,
                MAX(avg_percentage_winners) AS max_winners,
                MAX(avg_percentage_assists_shots) AS max_assists_shots,
                MAX(avg_percentage_error_setups) AS max_error_setups,
                MAX(avg_percentage_ue) AS max_ue,
                MAX(avg_percentage_pe) AS max_pe,
                MAX(avg_percentage_winner_setups) AS max_winner_setups,
                MAX(avg_num_smash_defenses) AS max_smash_defenses
            FROM (
                SELECT 
                    gender,
                    player,
                    AVG(ci_per_point) AS avg_ci_per_point,
                    AVG(num_direct_points_on_serve) AS avg_num_direct_points_on_serve,
                    AVG(percentage_points_won_on_serve_team) * 100 AS avg_percentage_points_won_on_serve_team,
                    
                    -- Calcular el porcentaje de errores de resto previamente
                    ROUND(SUM(num_return_errors)::numeric / NULLIF(SUM(num_returns), 0) * 100, 2) AS avg_percentage_return_errors,

                    AVG(percentage_points_won_return_team) * 100 AS avg_percentage_points_won_return_team,
                    AVG(percentage_shots_smash) * 100 AS avg_percentage_shots_smash,
                    AVG(num_bajadas) AS avg_num_bajadas,
                    AVG(percentage_viborejas_winners) * 100 AS avg_percentage_viborejas_winners,
                    AVG(percentage_winners) * 100 AS avg_percentage_winners,
                    AVG(percentage_assists_shots) * 100 AS avg_percentage_assists_shots,
                    AVG(percentage_error_setups) * 100 AS avg_percentage_error_setups,
                    AVG(percentage_ue) * 100 AS avg_percentage_ue,
                    AVG(percentage_pe) * 100 AS avg_percentage_pe,
                    AVG(percentage_winner_setups) * 100 AS avg_percentage_winner_setups,
                    AVG(num_smash_defenses) AS avg_num_smash_defenses
                FROM player_stats
                GROUP BY gender, player
            ) AS player_averages
            GROUP BY gender;
        """

        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        conn.close()

        # Formatear el resultado en un diccionario diferenciado por género
        benchmark_max = {}
        for row in results:
            gender = row[0]
            benchmark_max[gender] = {
                "ci_per_point": float(row[1]) if row[1] is not None else 0.0,
                "num_direct_points_on_serve": float(row[2]) if row[2] is not None else 0.0,
                "percentage_points_won_on_serve_team": float(row[3]) if row[3] is not None else 0.0,
                "percentage_return_errors": float(row[4]) if row[4] is not None else 0.0,
                "percentage_points_won_return_team": float(row[5]) if row[5] is not None else 0.0,
                "percentage_shots_smash": float(row[6]) if row[6] is not None else 0.0,
                "num_bajadas": float(row[7]) if row[7] is not None else 0.0,
                "percentage_viborejas_winners": float(row[8]) if row[8] is not None else 0.0,
                "percentage_winners": float(row[9]) if row[9] is not None else 0.0,
                "percentage_assists_shots": float(row[10]) if row[10] is not None else 0.0,
                "percentage_error_setups": float(row[11]) if row[11] is not None else 0.0,
                "percentage_ue": float(row[12]) if row[12] is not None else 0.0,
                "percentage_pe": float(row[13]) if row[13] is not None else 0.0,
                "percentage_winner_setups": float(row[14]) if row[14] is not None else 0.0,
                "num_smash_defenses": float(row[15]) if row[15] is not None else 0.0
            }

        return benchmark_max
    except Exception as e:
        return {"error": str(e)}

@app.get("/benchmark_max_couples")
def get_benchmark_max_couples():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute("""
            -- 💡 Query corregida dividida por género
            SELECT gender,
                MAX(win_rate),
                MAX(percentage_1st_serves),
                MAX(percentage_service_games_won),
                MAX(percentage_cross),
                MAX(percentage_flat_returns),
                MAX(percentage_lobbed_returns),
                MAX(percentage_return_errors),
                MAX(lobs_received_per_match),
                MAX(percentage_smashes_from_lobs),
                MAX(percentage_rulos_from_lobs),
                MAX(percentage_viborejas_from_lobs),
                MAX(percentage_bajadas_from_lobs),
                MAX(winners_from_lobs),
                MAX(outside_recoveries),
                MAX(lobs_played_per_match),
                MAX(net_recovery_with_lob),
                MAX(unforced_errors_per_match),
                MAX(ci_per_point),
                MAX(num_direct_points_on_serve),
                MAX(percentage_points_won_on_serve_team),
                MAX(percentage_points_won_return_team),
                MAX(percentage_shots_smash),
                MAX(num_bajadas),
                MAX(percentage_viborejas_winners),
                MAX(percentage_winners),
                MAX(percentage_assists_shots),
                MAX(percentage_error_setups),
                MAX(percentage_ue),
                MAX(percentage_pe),
                MAX(percentage_winner_setups),
                MAX(num_smash_defenses)
            FROM (
                SELECT 
                    LEAST(player_id, partner_id) AS player1_id,
                    GREATEST(player_id, partner_id) AS player2_id,
                    MAX(gender) AS gender,

                    -- Cálculos (como en query anterior corregida)
                    ROUND(COUNT(DISTINCT CASE WHEN result = 'W' THEN match_id END)::numeric /
                    NULLIF(COUNT(DISTINCT match_id), 0) * 100, 2) AS win_rate,
                    ROUND(AVG(CASE WHEN num_serves > 0 THEN num_1st_serves::numeric / num_serves ELSE NULL END) * 100, 2) AS percentage_1st_serves,
                    ROUND(AVG(CASE WHEN num_games_served > 0 THEN num_games_served_won::numeric / num_games_served ELSE NULL END) * 100, 2) AS percentage_service_games_won,
                    ROUND(SUM(shot_to_l)::numeric / NULLIF(SUM(num_shots_wo_returns), 0) * 100, 2) AS percentage_cross,
                    ROUND(SUM(num_flat_returns)::numeric / NULLIF(SUM(num_returns), 0) * 100, 2) AS percentage_flat_returns,
                    ROUND(SUM(num_lobbed_returns)::numeric / NULLIF(SUM(num_returns), 0) * 100, 2) AS percentage_lobbed_returns,
                    ROUND(SUM(num_return_errors)::numeric / NULLIF(SUM(num_returns), 0) * 100, 2) AS percentage_return_errors,
                    ROUND(AVG(num_lobs_received)::numeric, 2) AS lobs_received_per_match,
                    ROUND(SUM(num_smashes)::numeric / NULLIF(SUM(num_lobs_received), 0) * 100, 2) AS percentage_smashes_from_lobs,
                    ROUND(SUM(num_rulos)::numeric / NULLIF(SUM(num_lobs_received), 0) * 100, 2) AS percentage_rulos_from_lobs,
                    ROUND(SUM(viborejas)::numeric / NULLIF(SUM(num_lobs_received), 0) * 100, 2) AS percentage_viborejas_from_lobs,
                    ROUND(SUM(num_bajadas)::numeric / NULLIF(SUM(num_lobs_received), 0) * 100, 2) AS percentage_bajadas_from_lobs,
                    ROUND(SUM(num_points_won_after_smash + rulos_winners + bajadas_winners + viborejas_winners)::numeric / NULLIF(SUM(num_lobs_received), 0) * 100, 2) AS winners_from_lobs,
                    SUM(num_smash_defense_winners_salida) AS outside_recoveries,
                    ROUND(AVG(num_lobs)::numeric, 2) AS lobs_played_per_match,
                    ROUND(CAST(AVG(percentage_net_regains_after_lob) * 100 AS numeric), 2) AS net_recovery_with_lob,
                    ROUND(AVG(num_Unforced_Errors)::numeric, 2) AS unforced_errors_per_match,
                    ROUND(AVG(ci_per_point)::numeric, 2) AS ci_per_point,
                    ROUND(AVG(num_direct_points_on_serve)::numeric, 2) AS num_direct_points_on_serve,
                    ROUND(CAST(AVG(percentage_points_won_on_serve_team) * 100 AS numeric), 2) AS percentage_points_won_on_serve_team,
                    ROUND(CAST(AVG(percentage_points_won_return_team) * 100 AS numeric), 2) AS percentage_points_won_return_team,
                    ROUND(CAST(AVG(percentage_shots_smash) * 100 AS numeric), 2) AS percentage_shots_smash,
                    ROUND(AVG(num_bajadas)::numeric, 2) AS num_bajadas,
                    ROUND(CAST(AVG(percentage_viborejas_winners) * 100 AS numeric), 2) AS percentage_viborejas_winners,
                    ROUND(CAST(AVG(percentage_winners) * 100 AS numeric), 2) AS percentage_winners,
                    ROUND(CAST(AVG(percentage_assists_shots) * 100 AS numeric), 2) AS percentage_assists_shots,
                    ROUND(CAST(AVG(percentage_error_setups) * 100 AS numeric), 2) AS percentage_error_setups,
                    ROUND(CAST(AVG(percentage_ue) * 100 AS numeric), 2) AS percentage_ue,
                    ROUND(CAST(AVG(percentage_pe) * 100 AS numeric), 2) AS percentage_pe,
                    ROUND(CAST(AVG(percentage_winner_setups) * 100 AS numeric), 2) AS percentage_winner_setups,
                    ROUND(AVG(num_smash_defenses)::numeric, 2) AS num_smash_defenses

                FROM player_stats
                GROUP BY LEAST(player_id, partner_id), GREATEST(player_id, partner_id)
            ) AS pairs
            GROUP BY gender;
        """)

        results = cursor.fetchall()
        cursor.close()
        conn.close()

        keys = [
            "win_rate", "percentage_1st_serves", "percentage_service_games_won", "percentage_cross",
            "percentage_flat_returns", "percentage_lobbed_returns", "percentage_return_errors",
            "lobs_received_per_match", "percentage_smashes_from_lobs", "percentage_rulos_from_lobs",
            "percentage_viborejas_from_lobs", "percentage_bajadas_from_lobs", "winners_from_lobs",
            "outside_recoveries", "lobs_played_per_match", "net_recovery_with_lob",
            "unforced_errors_per_match", "ci_per_point", "num_direct_points_on_serve",
            "percentage_points_won_on_serve_team", "percentage_points_won_return_team",
            "percentage_shots_smash", "num_bajadas", "percentage_viborejas_winners",
            "percentage_winners", "percentage_assists_shots", "percentage_error_setups",
            "percentage_ue", "percentage_pe", "percentage_winner_setups", "num_smash_defenses"
        ]

        result_dict = {}
        for row in results:
            gender = row[0]
            values = row[1:]
            result_dict[gender] = {k: float(v) if v is not None else 0.0 for k, v in zip(keys, values)}

        return result_dict

    except Exception as e:
        return {"error": str(e)}

@app.get("/summary_season")
def get_summary_season():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SET client_encoding TO 'UTF8';")  # Esto lo refuerza por si options no basta

        query = """
        WITH max_sets AS (
            SELECT match_id, MAX(set_num) AS max_set
            FROM score_evolution
            GROUP BY match_id
        ),
        max_points AS (
            SELECT match_id, MAX(point_num) AS max_point
            FROM score_evolution
            GROUP BY match_id
        )
        SELECT
            COUNT(DISTINCT ms.match_id) AS matches_played,
            SUM(ms.max_set) AS sets_played,
            SUM(mp.max_point) AS points_played
        FROM max_sets ms
        JOIN max_points mp ON ms.match_id = mp.match_id;
        """

        cursor.execute(query)
        result = cursor.fetchone()

        summary = {
            "matches_played": result[0],
            "sets_played": result[1],
            "points_played": result[2]
        }

        cursor.close()
        conn.close()

        return summary

    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # For testing without API, you could call main() here,
    # but typically this module would be run via uvicorn.
    uvicorn.run("main-connected:app", host="0.0.0.0", port=8000, reload=True)