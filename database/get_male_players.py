import psycopg2

DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "PadelIntelligence1",
    "host": "localhost",
    "port": "5432"
}

def get_unique_male_players():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        query = "SELECT DISTINCT player FROM player_stats WHERE gender = 'M' ORDER BY player;"
        cursor.execute(query)
        players = cursor.fetchall()
        
        print("Lista de jugadores masculinos únicos (ordenados alfabéticamente):")
        for player in players:
            print(player[0])  # Solo imprimir el nombre
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")


def get_unique_pairs():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        query = """
        SELECT DISTINCT 
            LEAST(player, partner) AS player1,
            GREATEST(player, partner) AS player2
        FROM player_stats
        WHERE player IS NOT NULL AND partner IS NOT NULL
        ORDER BY player1, player2;
        """
        
        cursor.execute(query)
        pairs = cursor.fetchall()
        
        print("Lista de parejas únicas ordenadas alfabéticamente:")
        for pair in pairs:
            print(f"{pair[0]} - {pair[1]}")  # Imprimir la pareja
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")        

if __name__ == "__main__":
    #get_unique_male_players()
    get_unique_pairs()
