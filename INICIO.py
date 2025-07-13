import subprocess
import time
import os
import sys

# Ruta base
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Scripts a ejecutar
scripts = [
    "jarvis_server.py",
    "voz_server.py",
    "spotify_server.py",
    "main.py"
]



# Limpiar logs anteriores (opcional)

# Ejecutar scripts en segundo plano (excepto main.py)
procesos = []
for script in scripts[:-1]:
    ruta = os.path.join(BASE_DIR, script)
    print(f"Iniciando: {script}")
    p = subprocess.Popen([sys.executable, ruta])
    procesos.append(p)

    time.sleep(1.5)

# Ejecutar el script principal (main.py) de forma bloqueante
ruta_main = os.path.join(BASE_DIR, scripts[-1])
print(f"Iniciando interfaz gráfica: {scripts[-1]}")
subprocess.call([sys.executable, ruta_main])
