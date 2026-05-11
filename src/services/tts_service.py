"""
TTS Service — tenta Piper → espeak-ng → gtts → silêncio.
Roda em thread separada para não bloquear a UI.
"""
import os
import shutil
import subprocess
import threading
import tempfile
from typing import Callable


class TTSService:
    def __init__(self, engine: str = "auto", speed: float = 1.0):
        self._engine   = engine
        self._speed    = speed
        self._lock     = threading.Lock()
        self._current  : subprocess.Popen | None = None
        self._resolved = self._resolve_engine()

    # ------------------------------------------------------------------ #
    def speak(self, text: str, callback: Callable | None = None) -> None:
        """Fala de forma assíncrona."""
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
    def _speak_sync(self, text: str, callback: Callable | None) -> None:
        self.stop()
        try:
            if self._resolved == "piper":
                self._speak_piper(text)
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
        piper_bin   = shutil.which("piper") or shutil.which("piper-tts")
        model_path  = self._find_piper_model()
        if not piper_bin or not model_path:
            self._resolved = "espeak"
            self._speak_espeak(text)
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

    def _speak_espeak(self, text: str) -> None:
        bin_name = "espeak-ng" if shutil.which("espeak-ng") else "espeak"
        speed_wpm = int(130 * self._speed)
        cmd = [
            bin_name, "-v", "pt+f3",
            "-s", str(speed_wpm),
            "-p", "40",
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
            gTTS(text=text, lang="pt", slow=False).save(tmp)
            player = shutil.which("mpg123") or shutil.which("ffplay") or shutil.which("aplay")
            if player:
                with self._lock:
                    self._current = subprocess.Popen(
                        [player, tmp], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL
                    )
                self._current.wait()
            os.unlink(tmp)
        except Exception as e:
            print(f"[TTS/gTTS] {e}")

    # ------------------------------------------------------------------ #
    def _resolve_engine(self) -> str:
        if self._engine != "auto" and self._engine != "piper":
            return self._engine

        if (shutil.which("piper") or shutil.which("piper-tts")) and self._find_piper_model():
            return "piper"
        if shutil.which("espeak-ng") or shutil.which("espeak"):
            return "espeak"
        try:
            import gtts   # noqa
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
