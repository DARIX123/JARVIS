from flask import Flask, request, jsonify
import numpy as np
import os
from encoder import inference as encoder
import numpy as np
arr = np.load("usuarios/uriel.npy")
print(arr.shape)  # debería ser algo como (10,256), no (256,)


UMBRAL_SIMILITUD = 0.75  # baja a 0.6–0.65 si quieres más tolerancia

app = Flask(__name__)

# Carga el modelo una sola vez
modelo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "encoder_model", "encoder.pt")
encoder.load_model(modelo_path)

# Siempre relativo a este script
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
perfiles_dir = os.path.join(BASE_DIR, "usuarios")

def obtener_embedding(audio_path):
    reprocessed_wav = encoder.preprocess_wav(audio_path)
    return encoder.embed_utterance(reprocessed_wav)

@app.route("/reconocer_voz", methods=["POST"])
def reconocer_voz():
    if "audio" not in request.files:
        return jsonify({"error": "No se proporcionó el archivo de audio."}), 400

    # Guarda el wav recibido
    audio = request.files["audio"]
    audio_path = os.path.join(BASE_DIR, "temp_audio.wav")
    audio.save(audio_path)

    # Depuración de directorio
    print("[DEBUG] Buscando perfiles en:", perfiles_dir)
    print("[DEBUG] Archivos encontrados:", os.listdir(perfiles_dir))

    try:
        embed = obtener_embedding(audio_path)
        max_similitud   = 0.0
        usuario_detectado = "desconocido"

        for archivo in os.listdir(perfiles_dir):
            if not archivo.endswith(".npy"):
                continue
            usuario = archivo[:-4]
            emb_perfil = np.load(os.path.join(perfiles_dir, archivo))  # array (N,256) o (256,) 

            # Si emb_perfil es 1D conviértelo a 2D para iterar uniformemente:
            vectores = emb_perfil if emb_perfil.ndim == 2 else emb_perfil[np.newaxis, :]

            for vector in vectores:
                sim = np.dot(embed, vector) / (np.linalg.norm(embed) * np.linalg.norm(vector))
                if sim > max_similitud:
                    max_similitud    = sim
                    usuario_detectado = usuario

        if max_similitud < UMBRAL_SIMILITUD:
            usuario_detectado = "desconocido"

        print(f"[RESULT] Usuario detectado: {usuario_detectado} (Similitud: {max_similitud:.2f})")
        return jsonify({"usuario": usuario_detectado, "similitud": float(max_similitud)})

    except Exception as e:
        print("[ERROR]", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)

