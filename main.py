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
microfono_activo = False
should_record    = False
recording_frames = []
conversacion     = []
estado_actual    = {"ultima_cancion": None}

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
                if mostrar_bienvenida:
                    msg = f"Hola {usuario}, bienvenido. ¿En qué puedo ayudarte?"
                    Clock.schedule_once(lambda dt: self.add_bubble("JARVIS", msg, True), 0)
                    self.reproducir_audio(msg)
                return
        except Exception as e:
            Clock.schedule_once(lambda dt: self.add_bubble("JARVIS", f"Error identificación: {e}", True), 0)
            return
        Clock.schedule_once(lambda dt: self.add_bubble("JARVIS", "No te reconozco. ¿Cómo te llamas?", True), 0)
        self.reproducir_audio("No te reconozco. ¿Cómo te llamas?")

    # ── Control por tecla ─────────────────────────────────────────────────────
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
        if not sesion_valida():
            self.identificar_usuario()
            return
        # ... aquí tu lógica de API de ChatGPT u otros comandos ...
        respuesta = f"He recibido: '{comando}'"
        Clock.schedule_once(lambda dt: self.add_bubble("JARVIS", respuesta, True), 0)
        self.reproducir_audio(respuesta)

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

    def reset_estado(self, dt):
        self.add_bubble("JARVIS", "Esperando comandos...", True)

    def toggle_theme(self):
        if self.bg_color == [0.1, 0.1, 0.15, 1]:
            self.bg_color = [1, 1, 1, 1]
            self.fg_color = [0, 0, 0, 1]
        else:
            self.bg_color = [0.1, 0.1, 0.15, 1]
            self.fg_color = [0.3, 0.8, 1, 1]

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

# ── App ─────────────────────────────────────────────────────────────────────
class JarvisApp(App):
    def build(self):
        return JarvisLayout()

if __name__ == "__main__":
    JarvisApp().run()
