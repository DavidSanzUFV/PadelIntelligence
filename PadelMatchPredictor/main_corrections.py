@app.post("/run_prediction/")
def run_prediction(match: MatchInput):
    try:
        estado_actual = MatchState(
            t1_points=match.t1_points,
            t2_points=match.t2_points,
            t1_games=match.t1_games,
            t2_games=match.t2_games,
            t1_sets=match.t1_sets,
            t2_sets=match.t2_sets,
            serve=match.serve
        )

        # Validar el estado del partido
        validar_resultado(estado_actual)

        # Calcular probabilidades del juego
        if estado_actual.t1_games == 6 and estado_actual.t2_games == 6:
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
            game_probability = df_tiebreak.to_dict()
        else:
            game_probability = calculate_game_probabilities(estado_actual, match.p_serve)

        # Calcular probabilidades del set
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

        probabilidad_ganar_juego = calc_total_game_probability(match.p_serve, 1 - match.p_serve, estado_actual)
        prob_if_win = float(prob_if_win.strip('%')) / 100
        prob_if_loss = float(prob_if_loss.strip('%')) / 100

        if probabilidad_ganar_juego > 1:
            probabilidad_ganar_juego /= 100

        probabilidad_ganar_set = (probabilidad_ganar_juego * prob_if_win) + ((1 - probabilidad_ganar_juego) * prob_if_loss)
        probabilidad_ganar_set_percent = probabilidad_ganar_set * 100

        # Calcular probabilidades del partido
        ifwin, ifloss = probability_match(estado_actual)
        prob_ganar_partido = (probabilidad_ganar_set * ifwin) + ((1 - probabilidad_ganar_set) * ifloss)
        prob_ganar_partido_percent = prob_ganar_partido * 100

        return {
            "game_probability": f"{game_probability:.2f}%",
            "set_probability": f"{probabilidad_ganar_set_percent:.2f}%",
            "match_probability": f"{prob_ganar_partido_percent:.2f}%"
        }

    except HTTPException as e:
        return {"error": [True, str(e.detail)]}
    except Exception as e:
        # Capturar cualquier otra excepción no manejada
        return {"error": [True, f"Error inesperado: {str(e)}"]}



-----------------------------------


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

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from typing import Union
from pydantic import BaseModel, Field


class MatchInput(BaseModel):
    t1_points: Union[str, int] = Field(..., ge=0)
    t2_points: Union[str, int] = Field(..., ge=0)
    t1_games: int
    t2_games: int
    t1_sets: int
    t2_sets: int
    serve: int
    p_serve: float
    p_games_won_on_serve: float

import logging
import pandas as pd
import os

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
            return "N/A"
        else:
            logging.info(f"✅ El archivo existe: {absolute_path}")

        # Intentar leer el archivo
        logging.info(f"📂 Intentando leer el archivo: {file_path}")
        df = pd.read_csv(file_path, delimiter=';', encoding='utf-8', on_bad_lines='skip')

        # Verificar el número de filas leídas
        logging.info(f"📊 Número de filas leídas: {len(df)}")

        # Verificar el contenido completo del archivo
        logging.info(f"📝 Contenido completo del archivo:\n{df}")

        # Log para ver las columnas del DataFrame
        logging.info(f"🔑 Columnas del archivo {file_path}: {list(df.columns)}")

        # Verificar si el archivo está vacío
        if df.empty:
            logging.warning(f"⚠️ El archivo {file_path} está vacío.")
            return "N/A"

        # Filtrar las filas donde 'Iteración' tenga el valor 'Total'
        df_total = df[df['Iteración'].astype(str).str.strip() == 'Total']

        # Verificar si encontramos alguna fila con 'Total'
        if df_total.empty:
            logging.warning(f"⚠️ No se encontró la fila 'Total' en {file_path}.")
            return "N/A"

        # Verificar la última fila en el archivo leído
        last_row = df.tail(1)
        logging.info(f"🔍 Última fila del archivo leído:\n{last_row}")

        # Log para ver la(s) fila(s) encontradas
        logging.info(f"🔍 Fila(s) 'Total' encontrada(s) en {file_path}:\n{df_total}")

        # Tomar la última fila con 'Total'
        last_total_row = df_total.iloc[-1]

        # Extraer la probabilidad calculada
        calculated_probability = last_total_row['Calculated_Probability']
        logging.info(f"📊 Probabilidad encontrada: {calculated_probability}")

        # Verificar si el valor está en formato de porcentaje como cadena
        if isinstance(calculated_probability, str):
            # Eliminar espacios y caracteres no numéricos
            calculated_probability = calculated_probability.strip().replace('%', '')
            logging.info(f"🔧 Probabilidad después de limpiar caracteres: {calculated_probability}")

        # Intentar convertir a flotante
        try:
            calculated_probability = float(calculated_probability)
            logging.info(f"✅ Probabilidad convertida a número: {calculated_probability}%")
        except ValueError:
            logging.error(f"❌ Error al convertir la probabilidad: {calculated_probability}")
            return "N/A"

        return calculated_probability

    except Exception as e:
        logging.error(f"❌ Error al leer {file_path}: {e}")
        return "N/A"


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging

# Configuración del logging
logging.basicConfig(level=logging.INFO)

app = FastAPI()

# Mapeo de puntos en formato tenis
score_map = {
    "0": 0,
    "15": 1,
    "30": 2,
    "40": 3,
    "Adv": 4
}

# Modelo actualizado para aceptar puntos como cadena
class MatchInput(BaseModel):
    t1_points: str  # Acepta "0", "15", "30", "40", "Adv"
    t2_points: str  # Acepta "0", "15", "30", "40", "Adv"
    t1_games: int
    t2_games: int
    t1_sets: int
    t2_sets: int
    serve: int
    p_serve: float
    p_games_won_on_serve: float

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

@app.post("/run_prediction/")
async def run_prediction(match: MatchInput):
    try:
        # Inicializar variables de puntos para evitar problemas de referencia
        t1_points = -1
        t2_points = -1

        # Conversión de puntos
        try:
            # Verificar si es un tie-break (juegos 6-6)
            if match.t1_games == 6 and match.t2_games == 6:
                t1_points = int(match.t1_points)
                t2_points = int(match.t2_points)
                logging.info(f"🎾 Tie-break detectado: T1 Points: {t1_points}, T2 Points: {t2_points}")
            else:
                t1_points = score_map.get(match.t1_points, -1)
                t2_points = score_map.get(match.t2_points, -1)

            if t1_points == -1 or t2_points == -1:
                raise ValueError("Puntos no válidos. Solo se permiten 0, 15, 30, 40, Adv en juegos normales.")
            logging.info(f"✅ Puntos convertidos: T1: {t1_points}, T2: {t2_points}")

        except Exception as e:
            logging.error(f"❌ Error al procesar los puntos: {str(e)}")
            return {"error": [True, f"Error al procesar los puntos: {str(e)}"]}

        # Crear el estado del partido
        try:
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
        except Exception as e:
            logging.error(f"❌ Error al crear el estado: {str(e)}")
            return {"error": [True, f"Error al crear el estado: {str(e)}"]}

        # Validar el estado del partido
        try:
            validar_resultado(estado_actual)
            logging.info("✅ Estado del partido validado correctamente")
        except Exception as e:
            logging.error(f"❌ Error al validar el estado: {str(e)}")
            return {"error": [True, str(e)]}

        # Calcular probabilidades del juego
        try:
            if estado_actual.t1_games == 6 and estado_actual.t2_games == 6:
                # Caso Tie-break
                tiebreak_calculator = TiebreakCalculator(estado_actual)
                tie_break_probs = tiebreak_calculator.calculate_probabilities()

                if tie_break_probs is None:
                    logging.error("❌ El cálculo del tie-break devolvió un valor nulo.")
                    raise ValueError("El cálculo del tie-break devolvió un valor nulo.")
                
                # Formatear correctamente las probabilidades del tie-break
                tiebreak_probability_t1 = float(tie_break_probs.get("tiebreak_probability_t1", "0").replace("%", "").strip())
                tiebreak_probability_t2 = float(tie_break_probs.get("tiebreak_probability_t2", "0").replace("%", "").strip())
                if_win_next_point = float(tie_break_probs.get("if_win_next_point", "0").replace("%", "").strip())
                if_lose_next_point = float(tie_break_probs.get("if_lose_next_point", "0").replace("%", "").strip())

                game_probability = {
                    "tiebreak_probability_t1": f"{tiebreak_probability_t1:.2f}%",
                    "tiebreak_probability_t2": f"{tiebreak_probability_t2:.2f}%",
                    "if_win_next_point": f"{if_win_next_point:.2f}%",
                    "if_lose_next_point": f"{if_lose_next_point:.2f}%"
                }

                # En tie-break, las probabilidades de juego, set y partido son las mismas
                set_probability = game_probability
                match_probability = game_probability

                logging.info(f"🎾 Probabilidad de tie-break calculada: {game_probability}")

            else:
                # Juego normal: calcular probabilidades del juego
                game_probability = calculate_game_probabilities(estado_actual, match.p_serve)
                logging.info(f"🎾 Probabilidad de juego calculada: {game_probability}")

                # Calcular probabilidades del set
                analysis_file_path = r"CSVFiles/Data/Set_Analysis_with_T1_and_T2_Wins.csv"
                output_csv_ifwin = r"CSVFiles/Exports/Updated_Set_Analysis_IfWin.csv"
                output_csv_ifloss = r"CSVFiles/Exports/Updated_Set_Analysis_IfLoss.csv"

                generate_game_sequence(estado_actual, analysis_file_path, output_csv_ifwin, output_csv_ifloss, win=True)
                generate_game_sequence(estado_actual, analysis_file_path, output_csv_ifwin, output_csv_ifloss, win=False)

                prob_if_win = leer_probabilidad_final(output_csv_ifwin)
                prob_if_loss = leer_probabilidad_final(output_csv_ifloss)

                # Conversión robusta de probabilidades
                prob_if_win = float(prob_if_win.strip('%')) / 100 if isinstance(prob_if_win, str) and prob_if_win != "N/A" else 0.0
                prob_if_loss = float(prob_if_loss.strip('%')) / 100 if isinstance(prob_if_loss, str) and prob_if_loss != "N/A" else 0.0

                probabilidad_ganar_juego = calc_total_game_probability(match.p_serve, 1 - match.p_serve, estado_actual)
                if probabilidad_ganar_juego > 1:
                    probabilidad_ganar_juego /= 100

                probabilidad_ganar_set = (probabilidad_ganar_juego * prob_if_win) + ((1 - probabilidad_ganar_juego) * prob_if_loss)
                probabilidad_ganar_set_percent = probabilidad_ganar_set * 100

                ifwin, ifloss = probability_match(estado_actual)
                prob_ganar_partido = (probabilidad_ganar_set * ifwin) + ((1 - probabilidad_ganar_set) * ifloss)
                prob_ganar_partido_percent = prob_ganar_partido * 100

                set_probability = {
                    "if_win": f"{prob_if_win * 100:.2f}%",
                    "if_loss": f"{prob_if_loss * 100:.2f}%",
                    "calculated": f"{probabilidad_ganar_set_percent:.2f}%"
                }

                match_probability = f"{prob_ganar_partido_percent:.2f}%"

            response = {
                "game_probability": game_probability,
                "set_probability": set_probability,
                "match_probability": match_probability
            }

            logging.info(f"✅ Respuesta generada: {response}")
            return response

        except Exception as e:
            logging.error(f"❌ Error al calcular la probabilidad del partido: {str(e)}")
            return {"error": [True, f"Error en la probabilidad del partido: {str(e)}"]}

    except Exception as e:
        logging.error(f"❗ Error inesperado en el endpoint: {str(e)}")
        return {"error": [True, f"Error inesperado: {str(e)}"]}