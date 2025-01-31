from games_format_results import calculate_game_probabilities, print_game_probabilities
from match_result import MatchState

def main():
    while True:
        print("\n--- Prediction Call Menu ---")
        print("1. Calcular probabilidad de ganar el juego")
        print("2. Probabilidad de ganar el set")
        print("3. Salir")
        
        choice = input("Selecciona una opción (1-3): ")
        
        if choice == "1":
            # Solicitar datos para calcular probabilidades del set
            print("\n--- 1. Calcular probabilidad de ganar el juego ---")
            t1_points = int(input("Introduce los puntos de T1: "))
            t2_points = int(input("Introduce los puntos de T2: "))
            t1_games = int(input("Introduce los juegos ganados por T1: "))
            t2_games = int(input("Introduce los juegos ganados por T2: "))
            t1_sets = int(input("Introduce los sets ganados por T1: "))
            t2_sets = int(input("Introduce los sets ganados por T2: "))
            serve = int(input("¿Quién sirve? (1 para T1, 2 para T2): "))
            p_serve = float(input("Introduce la probabilidad de ganar un punto al saque (0-1): "))
            
            estado_actual = MatchState(t1_points, t2_points, t1_games, t2_games, t1_sets, t2_sets, serve)
            
            # Llamar a la función para calcular probabilidades
            resultado = calculate_game_probabilities(estado_actual, p_serve)
            
            print_game_probabilities(resultado)
        
        elif choice == "2":
            print("\n--- Próximamente ---")
        
        elif choice == "3":
            print("Saliendo del programa. ¡Hasta luego!")
            break
        
        else:
            print("Opción no válida. Por favor, selecciona una opción entre 1 y 3.")

if __name__ == "__main__":
    main()
