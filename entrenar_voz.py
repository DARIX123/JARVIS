import os
import numpy as np
import soundfile as sf
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from encoder import inference as encoder

# Inicializar el modelo de voz
directorio_actual = os.path.dirname(os.path.abspath(__file__))
encoder.load_model(os.path.join(directorio_actual, "encoder_model", "encoder.pt"))

# Directorio de usuarios
directorio_usuarios = os.path.join(directorio_actual, "usuarios")
os.makedirs(directorio_usuarios, exist_ok=True)

def preprocess_wav(wav, source_sr):
    return encoder.preprocess_wav(wav, source_sr=source_sr)

def entrenar_usuario():
    root = tk.Tk()
    root.withdraw()

    # Selección de archivos
    messagebox.showinfo("Seleccionar archivos", "Selecciona los archivos de voz (.wav) del nuevo usuario.")
    archivos = filedialog.askopenfilenames(title="Selecciona archivos de voz", filetypes=[("WAV files", "*.wav")])

    if not archivos:
        messagebox.showwarning("Sin archivos", "No seleccionaste ningún archivo.")
        return

    # Solicita nombre del usuario
    nombre = simpledialog.askstring("Nombre del usuario", "Escribe el nombre del usuario (sin espacios ni acentos):")
    if not nombre:
        messagebox.showwarning("Nombre vacío", "No ingresaste un nombre de usuario.")
        return

    nombre = nombre.strip().lower()
    ruta_usuario = os.path.join(directorio_usuarios, f"{nombre}.npy")

    embeddings = []
    for archivo in archivos:
        try:
            wav, sr = sf.read(archivo)
            wav = encoder.preprocess_wav(wav)
            emb = encoder.embed_utterance(wav)
            embeddings.append(emb)
            print(f"Agregado: {archivo}")
        except Exception as e:
            print(f"Error al procesar {archivo}: {e}")

    if not embeddings:
        messagebox.showerror("Error", "No se pudo procesar ningún archivo de audio.")
        return

    # Si ya existe, cargar y combinar
    if os.path.exists(ruta_usuario):
        try:
            emb_existente = np.load(ruta_usuario)
            embeddings.append(emb_existente)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo existente: {e}")
            return

    # Guardar embeddings combinados
    emb_total = np.vstack(embeddings)
    np.save(ruta_usuario, emb_total)

    messagebox.showinfo("Éxito", f"Voz de {nombre} registrada con éxito. Total de muestras: {emb_total.shape[0]}")

if __name__ == "__main__":
    entrenar_usuario()
