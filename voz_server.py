from flask import Flask, request, jsonify
import torch
import numpy as np
import os
from encoder import inference as encoder
from pathlib import Path
import soundfile as sf

# Inicializar Flask
app = Flask(__name__)

# Cargar el modelo encoder
encoder.load_model("C:/Users/PC RAPTOR/Desktop/JARVIS/encoder_model/encoder.pt")

# Ruta de los perfiles de voz
perfiles_dir = "C:/Users/PC RAPTOR/Desktop/JARVIS/usuarios"  # Asegúrate de que esta ruta sea correcta y contenga .npy

# Función para preprocesar el audio y obtener el embedding
def obtener_embedding(audio_path):
    reprocessed_wav = encoder.preprocess_wav(audio_path)
    embed = encoder.embed_utterance(reprocessed_wav)
    return embed

@app.route("/reconocer_voz", methods=["POST"])
def reconocer_voz():
    if "audio" not in request.files:
        return jsonify({"error": "No se proporcionó el archivo de audio."}), 400

    audio = request.files["audio"]
    audio_path = os.path.join("temp_audio.wav")
    audio.save(audio_path)

    try:
        embed = obtener_embedding(audio_path)
        max_similitud = 0.0
        usuario_detectado = "desconocido"

        for archivo in os.listdir(perfiles_dir):
            if archivo.endswith(".npy"):
                usuario = archivo.replace(".npy", "")
                emb = np.load(os.path.join(perfiles_dir, archivo))  # (10, 256)

                similitudes = [
                    np.dot(embed, vector) / (np.linalg.norm(embed) * np.linalg.norm(vector))
                    for vector in emb
                ]

                max_sim = max(similitudes)
                if max_sim > max_similitud:
                    max_similitud = max_sim
                    usuario_detectado = usuario

        print(f"Usuario detectado: {usuario_detectado} (Similitud: {float(max_similitud):.2f})")
        return jsonify({"usuario": usuario_detectado, "similitud": float(max_similitud)})

    except Exception as e:
        print("[ERROR]", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
