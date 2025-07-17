from encoder import inference as encoder
from encoder.audio import preprocess_wav
import numpy as np
import os
from pathlib import Path

# Ruta exacta del modelo
encoder.load_model("C:/Users/PC RAPTOR/Desktop/JARVIS/encoder_model/encoder.pt")

# Ruta exacta de tus audios
audio_dir = Path("C:/Users/PC RAPTOR/Downloads/uriel")
audio_filenames = [f"uriel-{i}.wav" for i in range(1, 17)]

# Ruta exacta donde se guardará el archivo final
directorio_salida = Path("C:/Users/PC RAPTOR/Desktop/JARVIS/usuarios")
directorio_salida.mkdir(parents=True, exist_ok=True)  # Crea carpeta si no existe

# Generar embeddings
embeddings = []
for filename in audio_filenames:
    wav_path = audio_dir / filename
    if not wav_path.exists():
        print(f"❌ No se encontró el archivo: {wav_path}")
        continue
    wav = preprocess_wav(wav_path)
    emb = encoder.embed_utterance(wav)
    embeddings.append(emb)
    print(f"✅ Embedding generado para: {filename}")

# Guardar archivo .npy con nombre 'uriel.npy'
output_file = directorio_salida / "uriel.npy"
np.save(output_file, embeddings)
print(f"✅ Archivo guardado exitosamente en: {output_file}")
