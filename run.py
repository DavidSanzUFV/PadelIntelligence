import subprocess
import sys
import os

# Ruta del entorno virtual
VENV_PYTHON = os.path.join(os.getcwd(), "venv", "Scripts", "python.exe")

# Si se pasa un argumento (nombre del script), usarlo. Si no, usar `connection_postgres.py` por defecto.
SCRIPT_NAME = sys.argv[1] if len(sys.argv) > 1 else "connection_postgres.py"
SCRIPT_PATH = os.path.join(os.getcwd(), "database", SCRIPT_NAME)

# Verificar si el script existe antes de ejecutarlo
if not os.path.exists(SCRIPT_PATH):
    print(f"❌ Error: El script '{SCRIPT_NAME}' no existe en 'database/'.")
    sys.exit(1)

# Ejecutar el script dentro del entorno virtual
try:
    subprocess.run([VENV_PYTHON, SCRIPT_PATH], check=True)
except Exception as e:
    print(f"❌ Error al ejecutar el script: {e}")
