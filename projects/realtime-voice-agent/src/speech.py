import base64
from typing import Dict, Any, Tuple

class AudioProcessor:
    """Audio frame processing utility for PCM/WAV streams and Voice Activity Detection (VAD)."""

    @staticmethod
    def decode_chunk(b64_audio: str) -> bytes:
        """Decode base64 encoded audio chunk."""
        return base64.b64decode(b64_audio)

    @staticmethod
    def encode_chunk(raw_bytes: bytes) -> str:
        """Encode raw bytes to base64 string."""
        return base64.b64encode(raw_bytes).decode("utf-8")

    @staticmethod
    def detect_vad(raw_bytes: bytes, threshold: int = 500) -> Tuple[bool, float]:
        """Simple energy-based Voice Activity Detection on 16-bit PCM frames."""
        if not raw_bytes:
            return False, 0.0
        # Calculate rough energy / amplitude
        total_energy = sum(abs(int.from_bytes(raw_bytes[i:i+2], byteorder='little', signed=True)) for i in range(0, len(raw_bytes)-1, 2))
        avg_energy = total_energy / (len(raw_bytes) / 2.0)
        is_speech = avg_energy > threshold
        return is_speech, round(avg_energy, 2)
