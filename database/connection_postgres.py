import psycopg2

# Configuración de la conexión
DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "PadelIntelligence1",
    "host": "localhost",
    "port": "5432"
}

# Conectar a la base de datos
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    print("Conectado a PostgreSQL ✅")

    # Ejecutar una consulta (ejemplo: obtener las primeras 5 filas de player_stats)
    #cursor.execute("SELECT * FROM player_stats LIMIT 5;")
    
    # Obtener resultados
    #rows = cursor.fetchall()
    
    # Mostrar los datos
    #for row in rows:
        #print(row)
    
    # Cerrar conexión
    cursor.close()
    conn.close()
    print("Conexión cerrada ✅")

except Exception as e:
    print(f"Error al conectar con PostgreSQL ❌: {e}")
