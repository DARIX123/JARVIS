from flask import Flask, request, jsonify
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

app = Flask(__name__)

# Configura tus credenciales de Spotify Developer
SPOTIPY_CLIENT_ID = '81dc301ce4d44e4f8644fb75e2375473'
SPOTIPY_CLIENT_SECRET = '6a32b7584dad4f4382402ed4ccbc04ed'
SPOTIPY_REDIRECT_URI = 'http://127.0.0.1:5000/callback'

scope = 'user-read-playback-state user-modify-playback-state user-read-currently-playing'

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope=scope
))

@app.route("/reproducir", methods=["POST"])
def reproducir_cancion():
    data = request.json
    titulo = data.get("titulo", "")
    artista = data.get("artista", "")

    try:
        # Construir consulta
        query = f"track:{titulo}"
        if artista:
            query += f" artist:{artista}"

        results = sp.search(q=query, type="track", limit=1)
        tracks = results['tracks']['items']
        if tracks:
            track_uri = tracks[0]['uri']
            sp.start_playback(uris=[track_uri])
            return jsonify({"status": "ok", "cancion": tracks[0]['name']})
        else:
            return jsonify({"error": "No se encontró la canción"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/control", methods=["POST"])
def controlar_musica():
    data = request.json
    accion = data.get("accion")

    try:
        if accion == "pausar":
            sp.pause_playback()
        elif accion == "reproducir":
            sp.start_playback()
        elif accion == "siguiente":
            sp.next_track()
        else:
            return jsonify({"error": "Acción no reconocida"}), 400

        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


  

if __name__ == '__main__':
    app.run(port=5002)
