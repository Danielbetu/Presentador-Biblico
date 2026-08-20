import os
import threading
import subprocess

# Mapeo de idiomas de la app a los códigos del motor TTS
MAPA_IDIOMAS_TTS = {
    "es": "es",
    "en": "en",
    "fr": "fr",
    "it": "it",
    "por": "pt"
}

def reproducir_versiculo_async(texto, idioma='es'):
    """
    Lee el versículo en voz alta en un hilo separado (no congela la app).
    Intenta primero gTTS (Audio natural HD) y si falla usas fallback local.
    """
    def _proceso_reproduccion():
        codigo_idioma = MAPA_IDIOMAS_TTS.get(idioma.lower(), "es")
        
        # 1. INTENTO ONLINE (gTTS - Calidad de voz excelente)
        try:
            from gtts import gTTS
            from tempfile import NamedTemporaryFile

            tts = gTTS(text=texto, lang=codigo_idioma, slow=False)
            with NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                temp_path = fp.name
            
            tts.save(temp_path)

            # Reproducción silenciosa por terminal con ffplay o paplay
            cmd = ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", temp_path]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            if os.path.exists(temp_path):
                os.remove(temp_path)
            return

        except Exception as e:
            print(f"[⚠️ TTS Online no disponible, usando voz local]: {e}")

        # 2. INTENTO OFFLINE (espeak-ng - Fallback si no hay internet)
        try:
            mapa_espeak = {"es": "es", "en": "en-us", "fr": "fr", "it": "it", "pt": "pt-pt"}
            voz_local = mapa_espeak.get(codigo_idioma, "es")
            subprocess.run(["espeak-ng", "-v", voz_local, "-s", "140", texto], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e_local:
            print(f"[❌ ERROR TTS Local]: {e_local}")

    # Lanzar hilo secundario inmediatamente
    hilo = threading.Thread(target=_proceso_reproduccion, daemon=True)
    hilo.start()
