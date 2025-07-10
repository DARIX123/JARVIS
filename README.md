
# Proyecto JARVIS

Este es el asistente inteligente JARVIS que incluye reconocimiento de voz, respuestas habladas y control de música, construido en Python usando Kivy, gTTS, PyAudio y otros módulos.

## ✅ Requisitos Previos

### 1. Instalar herramientas necesarias

- [Python 3.11.x](https://www.python.org/downloads/)
- [Visual Studio Code (VSC)](https://code.visualstudio.com/)
- [Git](https://git-scm.com/downloads)

### 2. Instalar extensiones en Visual Studio Code

- Python Extension (by Microsoft)
- Git Extension

---

## 🚀 Pasos para correr el proyecto

### 1. Clonar el repositorio

Abre una terminal (CMD, PowerShell o terminal de VSC):

```
git clone https://github.com/DARIX123/JARVIS.git
cd JARVIS
```

### 2. Crear entorno virtual (opcional pero recomendado)

```
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar dependencias

**Primero instala pipwin para facilitar PyAudio:**

```
pip install pipwin
pipwin install pyaudio
```

**Luego instala el resto de las dependencias:**

```
pip install -r requirements.txt
```

Si no tienes `requirements.txt`, puedes instalar manualmente:

```
pip install kivy gtts pygame speechrecognition requests librosa soundfile numba
```

---

## 🎧 Recomendaciones importantes

- Usa la **misma versión de Python** que tu compañero (idealmente 3.11.x).
- Asegúrate de tener **Python 64 bits**.
- Algunos módulos como `pyaudio` dan error si se instalan directamente con pip. Usa `pipwin` como se explicó.

---

## 🛠️ Ejecución del proyecto

Una vez tengas todo instalado, corre el proyecto con:

```
python main.py
```

---

## 📁 Estructura recomendada

Asegúrate de mantener esta estructura para que funcione bien:

```
JARVIS/
│
├── main.py
├── requirements.txt
├── perfiles/
├── usuarios_nuevos/
├── ...otros archivos .py y recursos
```

---

## 💬 ¿Problemas?

Si tienes errores con librerías de audio o ejecución, asegúrate de:

- Tener Python 64 bits.
- Haber usado pipwin para instalar PyAudio.
- Haber activado el entorno virtual antes de instalar.

---

## 👥 Créditos

Proyecto desarrollado por Uriel y colaboradores.
