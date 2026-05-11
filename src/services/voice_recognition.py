"""
Reconhecimento de voz com wake-word.
Fluxo: ouve continuamente → detecta "jarvis" → ouve o comando → dispara callback.
Requer: SpeechRecognition + python3-pyaudio
"""
from __future__ import annotations
import os
import threading
from typing import Callable


class VoiceRecognitionService:
    def __init__(self, wake_word: str = "jarvis", on_command: Callable[[str], None] | None = None):
        self._wake_word  = wake_word.lower()
        self._on_command = on_command
        self._running    = False
        self._thread: threading.Thread | None = None
        self._available  = self._check_deps()

    @property
    def available(self) -> bool:
        return self._available

    def start(self) -> None:
        if not self._available or self._running:
            return
        self._running = True
        self._thread  = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()
        print("[VoiceRec] Iniciado — diga 'Jarvis' para ativar")

    def stop(self) -> None:
        self._running = False

    # ------------------------------------------------------------------ #
    def _listen_loop(self) -> None:
        import speech_recognition as sr

        # Suprimir mensagens ALSA/JACK que poluem o terminal
        _silence_alsa()

        recognizer = sr.Recognizer()
        recognizer.energy_threshold        = 300
        recognizer.dynamic_energy_threshold = True
        recognizer.pause_threshold          = 0.8

        mic = sr.Microphone()

        # Calibrar ruído ambiente uma vez
        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=1.5)

        print("[VoiceRec] Pronto — aguardando wake-word")

        while self._running:
            try:
                # 1. Ouvir até detectar a wake-word
                with mic as source:
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=4)

                text = recognizer.recognize_google(audio, language="pt-BR").lower()

                if self._wake_word not in text:
                    continue

                print(f"[VoiceRec] Wake-word detectada: '{text}'")

                # Extrair comando junto à wake-word (ex: "jarvis fechar")
                inline_cmd = text.replace(self._wake_word, "").strip()

                if inline_cmd:
                    # Comando veio junto com a wake-word
                    if self._on_command:
                        self._on_command(inline_cmd)
                else:
                    # Aguardar o comando após a wake-word
                    if self._on_command:
                        self._on_command("")   # feedback imediato ("sim?")
                    try:
                        with mic as source:
                            audio2 = recognizer.listen(source, timeout=5, phrase_time_limit=6)
                        cmd = recognizer.recognize_google(audio2, language="pt-BR").lower()
                        print(f"[VoiceRec] Comando: '{cmd}'")
                        if self._on_command:
                            self._on_command(cmd)
                    except Exception:
                        pass

            except Exception:
                pass

    @staticmethod
    def _check_deps() -> bool:
        try:
            import speech_recognition  # noqa
            import pyaudio             # noqa
            return True
        except ImportError:
            return False


def _silence_alsa():
    """Redirecionar stderr do ALSA/JACK para /dev/null."""
    try:
        import ctypes
        asound = ctypes.cdll.LoadLibrary("libasound.so.2")
        asound.snd_lib_error_set_handler(None)
    except Exception:
        pass
    # Suprimir via fd redirect
    try:
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, 2)
        os.close(devnull)
    except Exception:
        pass
