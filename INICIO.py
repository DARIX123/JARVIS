import subprocess
import time
import os
import sys

# Ruta base relativa donde están los scripts
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Lista de scripts a ejecutar
scripts = [
    "jarvis_server.py",
    "voz_server.py",
    "spotify_server.py",
    # "boss_server.py",  # ← Descomenta si tienes este script
    "main.py"  # Al final, lanza la interfaz gráfica
]

# Ejecutar cada script
procesos = []
for script in scripts[:-1]:  # Ejecuta todos MENOS el último (main.py)
    ruta = os.path.join(BASE_DIR, script)
    print(f"Iniciando: {script}")
    p = subprocess.Popen([sys.executable, ruta], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    procesos.append(p)
    time.sleep(1.5)  # Espera para evitar conflictos al abrir puertos

# Ejecuta el último script en modo bloqueante (ej. main.py)
ruta_main = os.path.join(BASE_DIR, scripts[-1])
print(f"Iniciando interfaz gráfica: {scripts[-1]}")
subprocess.call([sys.executable, ruta_main])
