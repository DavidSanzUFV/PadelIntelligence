class MatchState:
    def __init__(self, t1_points, t2_points, t1_games, t2_games, t1_sets, t2_sets,serve):
        self.t1_points = t1_points  
        self.t2_points = t2_points  
        self.t1_games = t1_games    
        self.t2_games = t2_games    
        self.t1_sets = t1_sets      
        self.t2_sets = t2_sets 
        self.serve = serve     
        self.evaluate_match()
        self.imprimir_resultado()

    # 1. Verifica si el partido ha terminado
    def is_match_over(self):
        return self.t1_sets == 2 or self.t2_sets == 2

    # 2. Verifica si el set ha terminado (6 juegos y 2 de diferencia)
    def is_set_over(self):
        return (self.t1_games >= 6 and self.t1_games >= self.t2_games + 2) or \
               (self.t2_games >= 6 and self.t2_games >= self.t1_games + 2)
    
    # 3. Verifica si el juego actual ha terminado (40-40 o ventaja)
    def is_game_over(self):
        return (self.t1_points >= 4 and self.t1_points >= self.t2_points + 2) or \
               (self.t2_points >= 4 and self.t2_points >= self.t1_points + 2)
    
    # 4. Verifica si el tiebreak ha terminado (mínimo 7 puntos y 2 de diferencia)
    def is_tiebreak_over(self):
        return (self.t1_points >= 7 and self.t1_points >= self.t2_points + 2) or \
               (self.t2_points >= 7 and self.t2_points >= self.t1_points + 2)

    # 5. Evalúa el estado general del partido
    def evaluate_match(self):
        if self.is_match_over():
            print("Partido terminado.")
        elif self.t1_games == 6 and self.t2_games == 6:
            if self.is_tiebreak_over():
                print("Tiebreak terminado.")
            else:
                print("Tiebreak en curso.")
        elif self.is_set_over():
            print("Set terminado.")
        elif self.is_game_over():
            print("Juego terminado.")
        else:
            print("Partido en curso.")

# 6. Formatea los puntos al estilo de un marcador de tenis
    def format_points(self, t1_points, t2_points):
        point_map = {0: "0", 1: "15", 2: "30", 3: "40"}
        if t1_points >= 4 or t2_points >= 4:
            if t1_points == t2_points:
                return "Deuce", "Deuce"
            elif t1_points > t2_points:
                return "Adv", "40"
            else:
                return "40", "Adv"
        return point_map.get(t1_points, "0"), point_map.get(t2_points, "0")

    # 7. Imprime el resultado actual del partido
    def imprimir_resultado(self):
        t1_score, t2_score = self.format_points(self.t1_points, self.t2_points)
        print("\n--- Resultado del Partido ---")
        print(f"Sets:    T1 {self.t1_sets} - {self.t2_sets} T2")
        print(f"Juegos:  T1 {self.t1_games} - {self.t2_games} T2")
        print(f"Puntos:  T1 {t1_score} - {t2_score} T2")
        print(f"Sirve:   {self.serve}")
        print("----------------------------")

