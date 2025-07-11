from flask import Flask, request, jsonify
import openai
import os
from dotenv import load_dotenv
from scipy.io.wavfile import write
from datetime import datetime
from pathlib import Path
import json  # Para validar JSON

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

        # SYSTEM PROMPT
        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                       "Tu nombre es JARVIS, un asistente útil y con voz amigable. "
                        "Estás hablando con un usuario llamado {usuario}. "
                        "Si el usuario pregunta “¿cómo me llamo?” o “quién soy?”, responde diciendo su nombre ('Eres {usuario}')."
                        "Si el usuario te pide que pongas una canción (por ejemplo, 'pon Diciembre de Fuerza Regida', 'reproduce algo de Peso Pluma', etc.), "
                        "responde SOLO con un JSON válido en este formato exacto: "
                        "{\"accion\": \"reproducir_musica\", \"titulo\": \"nombre de la canción\", \"artista\": \"nombre del artista\"}. "
                        "No pongas saludos, explicaciones ni texto adicional. Solo el JSON plano. "
                        "Si el usuario menciona solo el artista, deja 'titulo' vacío. "
                        "Si solo menciona la canción, deja 'artista' vacío. "
                        "Ejemplos válidos:\n"
                        "Usuario: pon Ojitos Lindos de Bad Bunny → {\"accion\": \"reproducir_musica\", \"titulo\": \"Ojitos Lindos\", \"artista\": \"Bad Bunny\"}\n"
                        "Usuario: pon algo de Peso Pluma → {\"accion\": \"reproducir_musica\", \"titulo\": \"\", \"artista\": \"Peso Pluma\"}\n"
                        "Usuario: reproduce Mi Ex tenía razón → {\"accion\": \"reproducir_musica\", \"titulo\": \"Mi Ex tenía razón\", \"artista\": \"\"}\n"
                        "Si el mensaje no es un comando musical, responde normalmente con texto natural y amigable."

                    )
                },
                {
                    "role": "user",
                    "content": mensaje
                }
            ]
        )

        texto_respuesta = respuesta["choices"][0]["message"]["content"]
        print("[🧪 TEXTO RECIBIDO DE OPENAI]:", texto_respuesta)

        try:
            data = json.loads(texto_respuesta)
            print("[✔️ JSON VÁLIDO] Se recibió correctamente:", data)
        except json.JSONDecodeError:
            print("[⚠️ ADVERTENCIA] La respuesta de OpenAI no fue JSON válido. Fue:", texto_respuesta)

        # ✅ FALTABA ESTO:
        return jsonify({"respuesta": texto_respuesta})

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return jsonify({"respuesta": f"Ocurrió un error: {str(e)}"}), 500

def guardar_nuevo_usuario(audio_data, nombre):
    Path("usuarios_nuevos").mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"usuarios_nuevos/{nombre}_{timestamp}.wav"
    write(filename, 16000, audio_data)
    txt_path = f"usuarios_nuevos/{nombre}.txt"
    if not os.path.exists(txt_path):
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("# Frases del usuario\n")
    return filename

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
