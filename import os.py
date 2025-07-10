import os
import numpy as np

directorio_usuarios = os.path.join(os.getcwd(), "usuarios")

for archivo in os.listdir(directorio_usuarios):
    if archivo.endswith(".npy"):
        ruta = os.path.join(directorio_usuarios, archivo)
        try:
            datos = np.load(ruta)
            print(f"{archivo} → shape: {datos.shape}")
            if len(datos.shape) == 1 and datos.shape[0] != 256:
                print(f"❌ Embedding inválido en {archivo}. Debería tener shape (256,).")
            elif len(datos.shape) == 2 and datos.shape[1] != 256:
                print(f"❌ Embeddings inválidos en {archivo}. Cada fila debe tener 256 columnas.")
        except Exception as e:
            print(f"❌ Error al leer {archivo}: {e}")
