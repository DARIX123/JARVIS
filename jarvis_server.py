from flask import Flask, request, jsonify
import openai
import os
from dotenv import load_dotenv
from scipy.io.wavfile import write  # para guardar el audio en WAV
import os
from datetime import datetime
from pathlib import Path

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/comando", methods=["POST"])
def recibir_comando():
    try:
        datos = request.get_json(force=True)

        if not datos or "mensaje" not in datos:
            return jsonify({"respuesta": "⚠️ Error: no se recibió ningún mensaje."}), 400

        mensaje = datos["mensaje"].strip()
        usuario = datos.get("usuario", "usuario")
        print(f"[Cliente dijo] {mensaje}")

        # SYSTEM PROMPT mejorado
        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                "content": (
                            f"Eres JARVIS, un asistente útil y con voz amigable. "
                            f"Estás hablando con un usuario llamado {usuario}. "
                            "Si el usuario te pregunta cómo se llama, responde con su nombre. "
                            "Si te pide que pongas una canción (por ejemplo, 'pon Diciembre de Fuerza Regida' o 'pon Fuerza Regida'), "
                            "devuelve una respuesta JSON **válida** con este formato: "
                            "{ \"accion\": \"reproducir_musica\", \"titulo\": \"nombre de la canción\", \"artista\": \"nombre del artista\" }. "
                            "Si el usuario sólo menciona el artista, el campo \"titulo\" debe estar vacío. "
                            "Si sólo menciona la canción, el campo \"artista\" debe estar vacío. "
                            "Si no es un comando musical, responde normalmente con texto natural."
                        )

                },
                {
                    "role": "user",
                    "content": mensaje
                }
            ]
        )

        texto_respuesta = respuesta["choices"][0]["message"]["content"]
        return jsonify({"respuesta": texto_respuesta})

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return jsonify({"respuesta": f"Ocurrió un error: {str(e)}"}), 500
    
def guardar_nuevo_usuario(audio_data, nombre):
    # Crear carpeta si no existe
    Path("usuarios_nuevos").mkdir(parents=True, exist_ok=True)
    
    # Guardar archivo de voz
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"usuarios_nuevos/{nombre}_{timestamp}.wav"
    write(filename, 16000, audio_data)

    # Guardar .txt provisional
    txt_path = f"usuarios_nuevos/{nombre}.txt"
    if not os.path.exists(txt_path):
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("# Frases del usuario\n")

    return filename

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
