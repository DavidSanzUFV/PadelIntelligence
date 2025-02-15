class MatchState:
    def __init__(self, t1_points, t2_points, t1_games, t2_games, t1_sets, t2_sets, serve):
        self.t1_points = t1_points  
        self.t2_points = t2_points  
        self.t1_games = t1_games    
        self.t2_games = t2_games    
        self.t1_sets = t1_sets      
        self.t2_sets = t2_sets 
        self.serve = serve     

        self.evaluate_match()    # Evalúa el estado (partido en curso, set terminado, etc.)
        self.imprimir_resultado()# Imprime el marcador formateado

    # 1. Verifica si el partido ha terminado (2 sets ganados por algún jugador)
    def is_match_over(self):
        return self.t1_sets == 2 or self.t2_sets == 2

    # 2. Verifica si el set ha terminado (6 juegos y 2 de diferencia, sin tiebreak, etc.)
    def is_set_over(self):
        return ((self.t1_games >= 6 or self.t2_games >= 6) and 
               abs(self.t1_games - self.t2_games) >= 2 and 
               not self.is_tiebreak_in_progress())

    # 3. Verifica si el juego actual ha terminado (40-40 o ventaja)
    def is_game_over(self):
        return (self.t1_points >= 4 and self.t1_points >= self.t2_points + 2) or \
               (self.t2_points >= 4 and self.t2_points >= self.t1_points + 2)

    # 4. Verifica si hay un tiebreak en curso (6-6 en juegos, sin que nadie lo haya ganado aún)
    def is_tiebreak_in_progress(self):
        if self.t1_games == 6 and self.t2_games == 6 and not self.is_tiebreak_over():
            return True
        return False

    # 5. Verifica si el tiebreak ha terminado (mínimo 7 puntos y 2 de diferencia)
    def is_tiebreak_over(self):
        return (self.t1_games == 6 and self.t2_games == 6) and \
               ((self.t1_points >= 7 and self.t1_points >= self.t2_points + 2) or
                (self.t2_points >= 7 and self.t2_points >= self.t1_points + 2))

    # 6. Evalúa el estado general del partido
    def evaluate_match(self):
        if self.is_match_over():
            print("Partido terminado.")
        elif self.is_tiebreak_in_progress():
            print("Tiebreak en curso.")
        elif self.is_tiebreak_over():
            print("Tiebreak terminado.")
        elif self.is_set_over():
            print("Set terminado.")
        elif self.is_game_over():
            print("Juego terminado.")
        else:
            print("Partido en curso.")

    # 7. Formatea los puntos en un juego normal (no tiebreak)
    def format_points_game(self, t1_points, t2_points):
        """
        Lógica estándar de 0,15,30,40,Deuce,Adv 
        """
        point_map = {0: "0", 1: "15", 2: "30", 3: "40"}
        # A partir de 4, hay posibilidad de Deuce/Adv
        if t1_points >= 4 or t2_points >= 4:
            if t1_points == t2_points:
                return "Deuce", "Deuce"
            elif t1_points == t2_points + 1:
                return "Adv", "40"
            elif t2_points == t1_points + 1:
                return "40", "Adv"
            elif t1_points >= t2_points + 2:
                # Juego ganado T1, pero eso se evalúa en is_game_over
                return "Game", " "
            elif t2_points >= t1_points + 2:
                return " ", "Game"
        return point_map.get(t1_points, "0"), point_map.get(t2_points, "0")

    # 8. Formatea los puntos cuando estamos en un tiebreak
    def format_points_tiebreak(self, t1_points, t2_points):
        """
        En un tiebreak, simplemente se muestran los puntos como números 
        (0,1,2,3,...) sin Deuce ni Advantage.
        """
        return str(t1_points), str(t2_points)

    # 9. Imprime el resultado actual del partido
    def imprimir_resultado(self):
        # Si hay tiebreak en curso, formateamos los puntos del tiebreak.
        if self.is_tiebreak_in_progress():
            t1_score, t2_score = self.format_points_tiebreak(self.t1_points, self.t2_points)
        else:
            # Caso normal: se formatean los puntos como 0,15,30,40,Adv...
            t1_score, t2_score = self.format_points_game(self.t1_points, self.t2_points)

        print("\n--- Resultado del Partido ---")
        print(f"Sets:    T1 {self.t1_sets} - {self.t2_sets} T2")
        print(f"Juegos:  T1 {self.t1_games} - {self.t2_games} T2")

        # Si ya es Tiebreak pero aun no hay ganador => mostramos "Tiebreak points"
        # Si no, puntos normales del juego
        if self.is_tiebreak_in_progress():
            print(f"Tiebreak: T1 {t1_score} - {t2_score} T2")
        else:
            print(f"Puntos:   T1 {t1_score} - {t2_score} T2")

        print(f"Sirve:   {self.serve}")
        print("----------------------------")
