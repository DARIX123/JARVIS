import os
import uuid
import threading
import tempfile
import wave
import time
import audioop
import json

import speech_recognition as sr
import requests
from gtts import gTTS
import pygame
import librosa
import encoder
import numpy as np
<<<<<<< HEAD
import pyaudio

from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label                  # ← para ChatBubble
from kivy.uix.widget import Widget                # ← para WaveIndicator
from kivy.clock import Clock
from kivy.properties import ListProperty, NumericProperty
from kivy.factory import Factory
from kivy.metrics import dp
from kivy.core.window import Window

# ── Variables globales ───────────────────────────────────────────────────────
perfil_activo    = {"usuario": None, "inicio": None}
=======
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')





>>>>>>> 258b7ac0aea909bb7f133cc793a30c7d01eaa939
microfono_activo = False
should_record    = False
recording_frames = []
<<<<<<< HEAD
conversacion     = []
estado_actual    = {"ultima_cancion": None}
=======

memoria_usuarios = {}
perfil_activo = {"usuario": None, "inicio": None}

>>>>>>> 258b7ac0aea909bb7f133cc793a30c7d01eaa939

# Constantes de audio
RATE, CHUNK = 16000, 1024
FORMAT      = pyaudio.paInt16
CHANNELS    = 1

# ── Helpers ───────────────────────────────────────────────────────────────────
def sesion_valida():
    if perfil_activo["usuario"] and perfil_activo["inicio"]:
        return (datetime.now() - perfil_activo["inicio"]).total_seconds() < 300
    return False

def guardar_nuevo_usuario(audio_bytes, nombre):
    carpeta = os.path.join("usuarios_nuevos")
    os.makedirs(carpeta, exist_ok=True)
    ruta = os.path.join(carpeta, f"{nombre}_{uuid.uuid4().hex}.wav")
    with wave.open(ruta, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(RATE)
        wf.writeframes(audio_bytes)
    return ruta

# ── Widgets personalizados ───────────────────────────────────────────────────
class ChatBubble(Label):
    bg_color = ListProperty([0.1, 0.2, 0.3, 0.8])

class WaveIndicator(Widget):
    current_level = NumericProperty(0)

# ── Layout principal ─────────────────────────────────────────────────────────
class JarvisLayout(BoxLayout):
    # propiedades enlazadas con el KV
    bg_color      = ListProperty([0.1, 0.1, 0.15, 1])
    fg_color      = ListProperty([0.3, 0.8, 1, 1])
    current_level = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_key_down=self.on_key_down, on_key_up=self.on_key_up)
        Clock.schedule_interval(self.actualizar_fecha_hora, 1)
        Clock.schedule_once(self.saludo_inicial, 1)

    # ── Funciones de UI ──────────────────────────────────────────────────────
    def add_bubble(self, user, text, is_jarvis):
        Bubble = Factory.ChatBubble
        bubble = Bubble(
            text=f"[b]{user}:[/b] {text}",
            markup=True,
            size_hint_y=None,
            bg_color=self.fg_color if is_jarvis else [0.2,0.2,0.2,0.8]
        )
        bubble.bind(texture_size=lambda inst, size: setattr(inst, 'height', size[1] + dp(20)))
        self.ids.chat_box.add_widget(bubble)
        self.ids.chat_box.parent.scroll_y = 0

    def actualizar_fecha_hora(self, dt):
        if "fecha_hora" in self.ids:
            ahora = datetime.now().strftime("%A %d/%m/%Y %H:%M:%S")
            self.ids.fecha_hora.text = ahora

    # ── Saludo e identificación ───────────────────────────────────────────────
    def saludo_inicial(self, dt):
        self.add_bubble("JARVIS", "Hola, ¿quién eres? ¿En qué puedo ayudarte?", True)
        self.reproducir_audio("Hola, ¿quién eres? ¿En qué puedo ayudarte?")
        threading.Thread(target=self.identificar_usuario, args=(True,), daemon=True).start()

    def identificar_usuario(self, mostrar_bienvenida=True):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            audio = r.listen(source)
        wav_bytes = audio.get_wav_data()
        ruta = guardar_nuevo_usuario(wav_bytes, "temp")
        try:
            with open(ruta, 'rb') as f:
                resp = requests.post("http://127.0.0.1:5001/reconocer_voz", files={"audio": f})
            usuario = resp.json().get("usuario")
            if usuario and usuario != "desconocido":
                perfil_activo["usuario"] = usuario
                perfil_activo["inicio"] = datetime.now()
                if usuario not in memoria_usuarios:
                    memoria_usuarios[usuario] = {
                        "estado_actual": {
                            "ultima_cancion": None,
                            "ultima_pregunta": None
                        },
                        "conversacion": []
                    }
                if mostrar_bienvenida:
                    msg = f"Hola {usuario}, bienvenido. ¿En qué puedo ayudarte?"
                    Clock.schedule_once(lambda dt: self.add_bubble("JARVIS", msg, True), 0)
                    self.reproducir_audio(msg)
                return
        except Exception as e:
            Clock.schedule_once(lambda dt: self.add_bubble("JARVIS", f"Error identificación: {e}", True), 0)
            return
<<<<<<< HEAD
        Clock.schedule_once(lambda dt: self.add_bubble("JARVIS", "No te reconozco. ¿Cómo te llamas?", True), 0)
        self.reproducir_audio("No te reconozco. ¿Cómo te llamas?")

    # ── Control por tecla ─────────────────────────────────────────────────────
=======
        
        self.ids.output.text += "\nJARVIS: No te reconozco. ¿Tienes una palabra secreta?"
        self.reproducir_audio("No te reconozco. ¿Tienes una palabra secreta?")

        with sr.Microphone() as source:
            audio_secreto = r.listen(source)

        try:
            palabra = r.recognize_google(audio_secreto, language="es-MX").lower().strip()
            if "luz" in palabra:
                self.ids.output.text += "\nJARVIS: Acceso concedido. ¿A qué perfil deseas acceder?"
                self.reproducir_audio("Acceso concedido. ¿A qué perfil deseas acceder?")

                with sr.Microphone() as source:
                    audio_nombre = r.listen(source)

                nombre = r.recognize_google(audio_nombre, language="es-MX").lower().strip()
                nombre = nombre.split()[0]
                BASE_DIR = os.path.dirname(os.path.abspath(__file__))
                ruta_perfil = os.path.join(BASE_DIR, "usuarios", f"{nombre}.npy")

                print("[DEBUG] Ruta completa del perfil:", ruta_perfil)
                print("[DEBUG] ¿Existe el archivo?:", os.path.exists(ruta_perfil))

                if os.path.exists(ruta_perfil):
                    try:
                        embed = np.load(ruta_perfil)
                        usuario = nombre
                        perfil_activo["usuario"] = usuario
                        perfil_activo["inicio"] = datetime.now()
                        print(perfil_activo)
                        if nombre not in memoria_usuarios:
                            memoria_usuarios[usuario] = {
                                "estado_actual": {
                                    "ultima_cancion": None,
                                    "ultima_pregunta": None
                                },
                                "conversacion": []
                            }
        # Opcional: podrías guardar el embedding si lo necesitas más adelante
                        mensaje = f"Bienvenido {nombre}. Ya puedes hablar conmigo normalmente."
                        self.ids.output.text += f"\nJARVIS: {mensaje}"
                        self.reproducir_audio(mensaje)
                        if usuario not in memoria_usuarios:
                            memoria_usuarios[usuario] = {
                            "estado_actual": {
                            "ultima_cancion": None,
                            "ultima_pregunta": None
                            },
                            "conversacion": []
                            }
                        return
                    except Exception as e:
                        self.ids.output.text += f"\nJARVIS: Error al cargar el perfil {nombre}: {e}"
                        self.reproducir_audio("Hubo un error al cargar tu perfil.")
                        return
         

                
              
            else:
                self.ids.output.text += "\nJARVIS: Palabra secreta incorrecta."
                self.reproducir_audio("Palabra secreta incorrecta.")
                return

        except:
            self.ids.output.text += "\nJARVIS: No entendí la palabra. Intenta otra vez."
            self.reproducir_audio("No entendí la palabra. Intenta otra vez.")

            


        self.ids.output.text += "\nJARVIS: No puedo reconocerte ni tienes acceso. Intenta más tarde."
        self.reproducir_audio("No puedo reconocerte ni tienes acceso. Intenta más tarde.")
        return


    

>>>>>>> 258b7ac0aea909bb7f133cc793a30c7d01eaa939
    def on_key_down(self, window, key, scancode, codepoint, modifiers):
        global microfono_activo, should_record
        if key == 32 and not microfono_activo:
            microfono_activo = True
            should_record = True
            threading.Thread(target=self.grabar_audio, daemon=True).start()

    def on_key_up(self, window, key, *args):
        global microfono_activo, should_record
        if key == 32:
            should_record = False
            microfono_activo = False

    # ── Grabación y procesado ─────────────────────────────────────────────────
    def grabar_audio(self):
        global recording_frames
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
        frames = []
        while should_record:
            data = stream.read(CHUNK)
            frames.append(data)
            nivel = audioop.rms(data, 2) / 10000.0
            self.current_level = min(1, max(0, nivel))
        stream.stop_stream()
        stream.close()
        p.terminate()
        self.procesar_audio(frames)

    def procesar_audio(self, frames):
        ruta = os.path.join(tempfile.gettempdir(), f"audio_{uuid.uuid4().hex}.wav")
        with wave.open(ruta, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(pyaudio.PyAudio().get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
        r = sr.Recognizer()
        with sr.AudioFile(ruta) as source:
            audio = r.record(source)
        try:
            comando = r.recognize_google(audio, language="es-MX")
            Clock.schedule_once(lambda dt: self.add_bubble("Tú", comando, False), 0)
            self.ejecutar_comando(comando.lower())
        except Exception as e:
            Clock.schedule_once(lambda dt: self.add_bubble("JARVIS", f"Error: {e}", True), 0)

    # ── Ejecución de comandos ─────────────────────────────────────────────────
    def ejecutar_comando(self, comando):
<<<<<<< HEAD
        if not sesion_valida():
=======
        usuario = perfil_activo["usuario"]
        if not any(comando.lower().startswith(p) for p in ["que", "como", "cual", "quien", "donde", "por que", "para que"]):
            memoria_usuarios[usuario]["conversacion"].append({
            "rol": perfil_activo["usuario"],
            "contenido": comando,
            "hora": datetime.now().strftime("%H:%M:%S")
            })

        nombre = perfil_activo["usuario"] if sesion_valida() else None
        if not nombre:
            self.ids.output.text += "\nJARVIS: ¿Quién eres? No te escuché bien."
            self.reproducir_audio("¿Quién eres? No te escuché bien.")
>>>>>>> 258b7ac0aea909bb7f133cc793a30c7d01eaa939
            self.identificar_usuario()
            return
        # ... aquí tu lógica de API de ChatGPT u otros comandos ...
        respuesta = f"He recibido: '{comando}'"
        Clock.schedule_once(lambda dt: self.add_bubble("JARVIS", respuesta, True), 0)
        self.reproducir_audio(respuesta)

<<<<<<< HEAD
    # ── Entrada manual ────────────────────────────────────────────────────────
    def enviar_texto(self):
        texto = self.ids.entrada_usuario.text.strip()
        if texto:
            self.add_bubble("Tú", texto, False)
            self.ids.entrada_usuario.text = ""
            self.ejecutar_comando(texto.lower())

    # ── Controles UI adicionales ─────────────────────────────────────────────
    def hablar_con_jarvis(self):
        self.add_bubble("JARVIS", "Escuchando...", True)
        Clock.schedule_once(lambda dt: self.reset_estado(), 3)
=======
        if "cómo me llamo" in comando:
            self.ids.output.text += "\nHaber habla un segundo, para ver quien eres jeje..."
            self.reproducir_audio("Haber habla un segundo, para ver quien eres jeje...")
            self.identificar_usuario(mostrar_bienvenida=False)
            if perfil_activo["usuario"]:
                mensaje = f"Claro, conozco tu nombre. Eres {perfil_activo['usuario']}. ¿En qué más puedo ayudarte?"
            else:
                mensaje = "Lo siento, no logré reconocerte."
            self.ids.output.text += f"\nJARVIS: {mensaje}"
            self.reproducir_audio(mensaje)
            return
        
        if any(frase in comando for frase in [
            "qué canción", "qué música", "cuál canción",
            "qué canción es esta", "cómo se llama esta canción",
            "cuál era la canción", "qué puse", "qué canción puse"
        ]):

            if memoria_usuarios[perfil_activo["usuario"]]["estado_actual"]["ultima_cancion"]:

                respuesta = f"La canción actual es:{memoria_usuarios[perfil_activo['usuario']]['estado_actual']['ultima_cancion']}."
            else:
                respuesta = "No recuerdo que hayas puesto alguna canción."
            self.ids.output.text += f"\nJARVIS: {respuesta}"
            self.reproducir_audio(respuesta)
            return

        
        if "qué te dije hace rato" in comando or "qué te conté" in comando or "qué te dije" in comando:
            for mensaje in reversed(memoria_usuarios[perfil_activo["usuario"]]["conversacion"]):
                if (
                    mensaje["rol"] == perfil_activo["usuario"]
                    and not mensaje["contenido"].startswith(("cómo", "qué", "quién", "enciende", "apaga", "reproduce", "pausa", "siguiente"))
                    and len(mensaje["contenido"].split()) > 3
                ):
                    recordatorio = mensaje["contenido"]
                    respuesta = f"Me dijiste: \"{recordatorio}\""
                    self.ids.output.text += f"\nJARVIS: {respuesta}"
                    self.reproducir_audio(respuesta)
                    return
            self.ids.output.text += "\nJARVIS: No recuerdo que me hayas dicho nada importante."
            self.reproducir_audio("No recuerdo que me hayas dicho nada importante.")
            return
        
        if any(comando.lower().startswith(p) for p in ["qué", "cuánto", "cuál", "cómo", "quién", "dónde", "por qué", "para qué"]):
            if not any(esp in comando for esp in [
                "qué canción", "cuál canción", "cómo se llama esta canción",
                "qué puse", "qué canción puse", "qué música"
            ]):
                if len(comando.split()) > 3:
                    usuario = perfil_activo.get("usuario")
                    if usuario and usuario in memoria_usuarios:
                        memoria_usuarios[usuario]["estado_actual"]["ultima_pregunta"] = comando

        if any(frase in comando for frase in [
            "qué te pregunté", "cuál fue mi última pregunta", "última pregunta", "te dije hace rato una pregunta"
        ]):
            usuario = perfil_activo.get("usuario")
            if usuario and usuario in memoria_usuarios:

                ultima = memoria_usuarios[usuario]["estado_actual"].get("ultima_pregunta")
                if ultima:
                    respuesta = f"La ultima pregunta que me hiciste fue: {ultima}"
                else:
                    respuesta = "No recuerdo la ultima pregunta"
            else:
                respuesta = "No se quien eres, no puedo acceder a tu historial"
            self.ids.output.text += f"\nJARVIS: {respuesta}"
            self.reproducir_audio(respuesta)
            return
>>>>>>> 258b7ac0aea909bb7f133cc793a30c7d01eaa939

    def reset_estado(self, dt):
        self.add_bubble("JARVIS", "Esperando comandos...", True)

<<<<<<< HEAD
    def toggle_theme(self):
        if self.bg_color == [0.1, 0.1, 0.15, 1]:
            self.bg_color = [1, 1, 1, 1]
            self.fg_color = [0, 0, 0, 1]
        else:
            self.bg_color = [0.1, 0.1, 0.15, 1]
            self.fg_color = [0.3, 0.8, 1, 1]
=======

        # Resto del flujo de comandos normales
        texto_respuesta = ""
        try:
            respuesta = requests.post("http://127.0.0.1:5000/comando", json={"mensaje": comando,
                                                                             "usuario": perfil_activo["usuario"]})
            texto_respuesta = respuesta.json()["respuesta"]
            print("[ TEXTO RECIBIDO DEL SERVIDOR]:", texto_respuesta)

            usuario = perfil_activo.get("usuario")
            if usuario and usuario in memoria_usuarios:
                memoria_usuarios[usuario]["conversacion"].append({
                "rol": "jarvis",
                "contenido": texto_respuesta,
                "hora": datetime.now().strftime("%H:%M:%S")
                })
        # Guardar última pregunta importante
       

            try:
                print("Intentando decodificar:", texto_respuesta)
                data = json.loads(texto_respuesta)
                if isinstance(data, dict) and data.get("accion") == "reproducir_musica":
                    titulo = data.get("titulo", "")
                    artista = data.get("artista", "")
                    usuario = perfil_activo.get("usuario")
                    if usuario and usuario in memoria_usuarios:
                        memoria_usuarios[usuario]["estado_actual"]["ultima_cancion"] = f"{titulo} de {artista if artista else 'desconocido'}"

                    if not titulo:
                        texto_respuesta = "¿Cómo se llama la canción que quieres escuchar?"
                    else:
                        try:
                            time.sleep(1)
                            requests.post("http://127.0.0.1:5002/reproducir", json={
                                "titulo": titulo,
                                "artista": artista
                            })
                            texto_respuesta = f"Reproduciendo {titulo} de {artista if artista else 'Spotify'}."
                        except:
                            texto_respuesta = "No pude encontrar la canción."
            except json.JSONDecodeError:
                print("No es un JSON válido. El texto fue:", texto_respuesta)
                pass

            texto_lower = texto_respuesta.lower()
            if "enciende" in texto_lower and "luz" in texto_lower:
                texto_respuesta += f"\n(Comando ejecutado: encender luz)"
            elif "apaga" in texto_lower and "luz" in texto_lower:
                texto_respuesta += f"\n(Comando ejecutado: apagar luz)"
            elif "pausa" in texto_lower and "música" in texto_lower:
                try:
                    requests.post("http://127.0.0.1:5002/control", json={"accion": "pausar"})
                except:
                    texto_respuesta += "\n(No se pudo pausar la música)"
            elif "reproduce" in texto_lower and "música" in texto_lower:
                try:
                    requests.post("http://127.0.0.1:5002/control", json={"accion": "reproducir"})
                except:
                    texto_respuesta += "\n(No se pudo reanudar la música)"
            elif "siguiente" in texto_lower and "canción" in texto_lower:
                try:
                    requests.post("http://127.0.0.1:5002/control", json={"accion": "siguiente"})
                except:
                    texto_respuesta += "\n(No se pudo cambiar la canción)"

        except requests.exceptions.ConnectionError:
            texto_respuesta = "No se pudo conectar con el servidor de ChatGPT. Verifica que esté en ejecución."

        self.ids.output.text += f"\nJARVIS: {texto_respuesta}"
        self.reproducir_audio(texto_respuesta)
>>>>>>> 258b7ac0aea909bb7f133cc793a30c7d01eaa939

    def reproducir_audio(self, texto):
        nombre = f"tts_{uuid.uuid4().hex}.mp3"
        tts = gTTS(text=texto, lang='es')
        tts.save(nombre)
        pygame.mixer.init()
        pygame.mixer.music.load(nombre)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pass
        pygame.mixer.quit()
        os.remove(nombre)

<<<<<<< HEAD
# ── App ─────────────────────────────────────────────────────────────────────
=======


>>>>>>> 258b7ac0aea909bb7f133cc793a30c7d01eaa939
class JarvisApp(App):
    def build(self):
        return JarvisLayout()

if __name__ == "__main__":
    JarvisApp().run()
