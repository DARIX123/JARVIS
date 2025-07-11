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

# Crear carpeta de logs si no existe
log_dir = os.path.join(BASE_DIR, "logs")
os.makedirs(log_dir, exist_ok=True)

# Limpiar logs anteriores (opcional)
for f in os.listdir(log_dir):
    os.remove(os.path.join(log_dir, f))

# Ejecutar scripts en segundo plano (excepto main.py)
procesos = []
for script in scripts[:-1]:
    ruta = os.path.join(BASE_DIR, script)
    log_file = os.path.join(log_dir, f"{os.path.splitext(script)[0]}.log")
    print(f"Iniciando: {script} → guardando log en {log_file}")
    with open(log_file, "w") as f:
        p = subprocess.Popen([sys.executable, ruta], stdout=f, stderr=subprocess.STDOUT)
        procesos.append(p)
    time.sleep(1.5)

# Ejecutar el script principal (main.py) de forma bloqueante
ruta_main = os.path.join(BASE_DIR, scripts[-1])
print(f"Iniciando interfaz gráfica: {scripts[-1]}")
subprocess.call([sys.executable, ruta_main])
