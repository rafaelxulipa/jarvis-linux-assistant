"""
TTS Service — cascata: sons pré-gravados → Piper → edge-tts → espeak-ng → gtts → silêncio.
Roda em thread separada para não bloquear a UI.

Vozes padrão (edge-tts, Microsoft Neural):
  male:   pt-BR-AntonioNeural
  female: pt-BR-FranciscaNeural
"""
from __future__ import annotations
import asyncio
import os
import shutil
import subprocess
import threading
import tempfile
from typing import Callable

from src.config.settings import SOUNDS_DIR

_EDGE_VOICES = {
    "male":   "pt-BR-AntonioNeural",
    "female": "pt-BR-FranciscaNeural",
}


class TTSService:
    def __init__(self, engine: str = "auto", speed: float = 1.0, voice_gender: str = "male"):
        self._engine       = engine
        self._speed        = speed
        self._voice_gender = voice_gender  # "male" | "female"
        self._lock         = threading.Lock()
        self._current      : subprocess.Popen | None = None
        self._resolved     = self._resolve_engine()

    # ------------------------------------------------------------------ #
    def play_sound(self, sound_name: str) -> None:
        """Toca arquivo pré-gravado de sounds/ (ex: 'morning', 'boot', 'shutdown').
        Adiciona sufixo _male/_female automaticamente.
        """
        path = os.path.join(SOUNDS_DIR, f"{sound_name}_{self._voice_gender}.mp3")
        if not os.path.exists(path):
            return
        threading.Thread(target=self._play_mp3, args=(path,), daemon=True).start()

    def speak(self, text: str, callback: Callable | None = None) -> None:
        """Sintetiza texto em voz de forma assíncrona."""
        t = threading.Thread(target=self._speak_sync, args=(text, callback), daemon=True)
        t.start()

    def stop(self) -> None:
        with self._lock:
            if self._current:
                try:
                    self._current.terminate()
                except Exception:
                    pass
                self._current = None

    @property
    def available(self) -> bool:
        return self._resolved != "none"

    @property
    def engine_name(self) -> str:
        return self._resolved

    # ------------------------------------------------------------------ #
    def _play_mp3(self, path: str) -> None:
        player = shutil.which("mpg123") or shutil.which("ffplay") or shutil.which("aplay")
        if not player:
            return
        with self._lock:
            self._current = subprocess.Popen(
                [player, path], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL
            )
        self._current.wait()

    def _speak_sync(self, text: str, callback: Callable | None) -> None:
        self.stop()
        try:
            if self._resolved == "piper":
                self._speak_piper(text)
            elif self._resolved == "edge":
                self._speak_edge(text)
            elif self._resolved == "espeak":
                self._speak_espeak(text)
            elif self._resolved == "gtts":
                self._speak_gtts(text)
        except Exception as e:
            print(f"[TTS] Erro: {e}")
        finally:
            if callback:
                callback()

    def _speak_piper(self, text: str) -> None:
        piper_bin  = shutil.which("piper") or shutil.which("piper-tts")
        model_path = self._find_piper_model()
        if not piper_bin or not model_path:
            self._resolved = "edge"
            self._speak_edge(text)
            return

        cmd = [piper_bin, "--model", model_path, "--output-raw"]
        with self._lock:
            p1 = subprocess.Popen(
                cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
            )
            p2 = subprocess.Popen(
                ["aplay", "-r", "22050", "-f", "S16_LE", "-t", "raw", "-"],
                stdin=p1.stdout, stderr=subprocess.DEVNULL
            )
            self._current = p2

        p1.communicate(input=text.encode())
        p2.wait()

    def _speak_edge(self, text: str) -> None:
        try:
            import edge_tts
            voice = _EDGE_VOICES.get(self._voice_gender, _EDGE_VOICES["male"])
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                tmp = f.name

            async def _synth():
                await edge_tts.Communicate(text, voice).save(tmp)

            asyncio.run(_synth())
            self._play_mp3(tmp)
            os.unlink(tmp)
        except Exception as e:
            print(f"[TTS/edge] {e}")
            self._speak_espeak(text)

    def _speak_espeak(self, text: str) -> None:
        bin_name  = "espeak-ng" if shutil.which("espeak-ng") else "espeak"
        speed_wpm = int(130 * self._speed)
        voice     = "pt+m3" if self._voice_gender == "male" else "pt+f3"
        pitch     = "35"    if self._voice_gender == "male" else "55"
        cmd = [
            bin_name, "-v", voice,
            "-s", str(speed_wpm),
            "-p", pitch,
            "-a", "180",
            "--ipa=0",
            text,
        ]
        with self._lock:
            self._current = subprocess.Popen(cmd, stderr=subprocess.DEVNULL)
        self._current.wait()

    def _speak_gtts(self, text: str) -> None:
        try:
            from gtts import gTTS
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                tmp = f.name
            GTS_TLD = "com" if self._voice_gender == "male" else "com.br"
            gTTS(text=text, lang="pt", tld=GTS_TLD, slow=False).save(tmp)
            self._play_mp3(tmp)
            os.unlink(tmp)
        except Exception as e:
            print(f"[TTS/gTTS] {e}")

    # ------------------------------------------------------------------ #
    def _resolve_engine(self) -> str:
        if self._engine not in ("auto", "piper"):
            return self._engine

        if (shutil.which("piper") or shutil.which("piper-tts")) and self._find_piper_model():
            return "piper"
        try:
            import edge_tts  # noqa
            if shutil.which("mpg123") or shutil.which("ffplay"):
                return "edge"
        except ImportError:
            pass
        if shutil.which("espeak-ng") or shutil.which("espeak"):
            return "espeak"
        try:
            import gtts  # noqa
            if shutil.which("mpg123") or shutil.which("ffplay"):
                return "gtts"
        except ImportError:
            pass
        return "none"

    @staticmethod
    def _find_piper_model() -> str | None:
        search_dirs = [
            os.path.expanduser("~/.local/share/piper"),
            os.path.expanduser("~/piper-models"),
            "/usr/share/piper",
            "/usr/local/share/piper",
        ]
        for d in search_dirs:
            if os.path.isdir(d):
                for f in os.listdir(d):
                    if f.endswith(".onnx"):
                        return os.path.join(d, f)
        return None
