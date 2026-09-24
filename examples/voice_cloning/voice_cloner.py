"""Reusable voice cloning wrapper around Coqui XTTS-v2 (TTS.api.TTS).

Educational use only. Only clone voices you own or have explicit consent
to clone. See README.md for the full ethical-use notice.
"""

from pathlib import Path
from typing import List, Optional, Union

import torch

from TTS.api import TTS

MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"

SUPPORTED_LANGUAGES = [
    "en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru",
    "nl", "cs", "ar", "zh-cn", "hu", "ko", "ja", "hi",
]


class VoiceCloner:
    """Loads XTTS-v2 once and clones a voice from a reference clip on demand."""

    def __init__(self, device: Optional[str] = None, progress_bar: bool = True):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.progress_bar = progress_bar
        self._tts: Optional[TTS] = None

    @property
    def model(self) -> TTS:
        if self._tts is None:
            self._tts = TTS(MODEL_NAME, progress_bar=self.progress_bar).to(self.device)
        return self._tts

    def clone(
        self,
        text: str,
        speaker_wav: Union[str, List[str]],
        output_path: Union[str, Path],
        language: str = "en",
    ) -> Path:
        """Synthesize `text` in the voice of `speaker_wav`, writing a wav to `output_path`.

        Args:
            text: Text to speak.
            speaker_wav: Path (or list of paths) to reference audio of the target voice.
                6-30s of clean, single-speaker audio works best.
            output_path: Where to write the generated wav file.
            language: One of SUPPORTED_LANGUAGES. Defaults to "en".
        """
        if not text or not text.strip():
            raise ValueError("text must not be empty")

        if language not in SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Unsupported language '{language}'. Supported: {', '.join(SUPPORTED_LANGUAGES)}"
            )

        wav_paths = [speaker_wav] if isinstance(speaker_wav, str) else list(speaker_wav)
        if not wav_paths:
            raise ValueError("speaker_wav must be a path or non-empty list of paths")
        for wav_path in wav_paths:
            if not Path(wav_path).is_file():
                raise FileNotFoundError(f"Reference audio not found: {wav_path}")

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        self.model.tts_to_file(
            text=text,
            speaker_wav=wav_paths,
            language=language,
            file_path=str(output_path),
        )
        return output_path
