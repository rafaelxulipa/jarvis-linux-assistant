"""
Reconhecimento de voz com wake-word opcional.
Requer: SpeechRecognition + PyAudio (opcionais).
"""
from __future__ import annotations
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

    def stop(self) -> None:
        self._running = False

    # ------------------------------------------------------------------ #
    def _listen_loop(self) -> None:
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        mic        = sr.Microphone()

        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)

        while self._running:
            try:
                with mic as source:
                    audio = recognizer.listen(source, timeout=3, phrase_time_limit=6)
                text = recognizer.recognize_google(audio, language="pt-BR").lower()
                print(f"[VoiceRec] Reconhecido: {text}")

                if self._wake_word in text:
                    command = text.replace(self._wake_word, "").strip()
                    if self._on_command:
                        self._on_command(command or "ativado")
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
