import os
import numpy as np

directorio = os.path.join(os.getcwd(), "usuarios")

for archivo in os.listdir(directorio):
    if archivo.endswith(".npy"):
        ruta = os.path.join(directorio, archivo)
        try:
            datos = np.load(ruta, allow_pickle=True)
            if datos.ndim == 2 and datos.shape[1] == 256:
                print(f"✅ {archivo} válido ({datos.shape[0]} muestras)")
            else:
                print(f"❌ {archivo} inválido. Eliminando...")
                os.remove(ruta)
        except Exception as e:
            print(f"❌ {archivo} corrupto: {e}. Eliminando...")
            os.remove(ruta)
