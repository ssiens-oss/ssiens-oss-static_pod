"""
Vocal Synthesis Engine
XTTS-based text-to-speech for rap and singing
Supports voice cloning and multilingual output
"""

import os
from typing import Optional

try:
    from TTS.api import TTS
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("Warning: TTS library not available, vocal synthesis will be mocked")


class VocalSynthesizer:
    """Main vocal synthesis class"""

    def __init__(self, model_name: str = "tts_models/multilingual/multi-dataset/xtts_v2"):
        self.model_name = model_name
        self.tts = None

        if TTS_AVAILABLE:
            try:
                self.tts = TTS(model_name)
                print(f"✓ Loaded TTS model: {model_name}")
            except Exception as e:
                print(f"Warning: Could not load TTS model: {e}")
                self.tts = None

    def synthesize(
        self,
        text: str,
        out_path: str,
        speaker_wav: Optional[str] = None,
        language: str = "en"
    ) -> str:
        """
        Synthesize speech from text

        Args:
            text: Text to synthesize
            out_path: Output WAV path
            speaker_wav: Optional voice clone reference
            language: Language code

        Returns:
            Path to generated audio
        """
        if self.tts is None:
            print(f"Mock synthesis: {text[:50]}...")
            self._create_mock_audio(out_path, len(text) * 0.1)
            return out_path

        try:
            self.tts.tts_to_file(
                text=text,
                file_path=out_path,
                speaker_wav=speaker_wav,
                language=language
            )
            print(f"✓ Generated vocal: {out_path}")

        except Exception as e:
            print(f"Synthesis error: {e}, creating mock audio")
            self._create_mock_audio(out_path, len(text) * 0.1)

        return out_path

    def _create_mock_audio(self, path: str, duration: float):
        """Create mock audio for testing"""
        import numpy as np
        import soundfile as sf

        sample_rate = 22050
        samples = int(sample_rate * duration)
        audio = np.zeros(samples, dtype=np.float32)

        sf.write(path, audio, sample_rate)


# Global synthesizer instance
_global_synthesizer = None


def get_synthesizer() -> VocalSynthesizer:
    """Get or create global synthesizer instance"""
    global _global_synthesizer

    if _global_synthesizer is None:
        _global_synthesizer = VocalSynthesizer()

    return _global_synthesizer


def synthesize(
    text: str,
    out_path: str,
    speaker_wav: Optional[str] = None,
    language: str = "en"
) -> str:
    """
    Convenience function for vocal synthesis

    Args:
        text: Text to synthesize
        out_path: Output path
        speaker_wav: Voice clone reference
        language: Language code

    Returns:
        Path to generated audio
    """
    synth = get_synthesizer()
    return synth.synthesize(text, out_path, speaker_wav, language)


def rap_synthesize(
    text: str,
    out_path: str,
    speaker_wav: Optional[str] = None,
    style: str = "aggressive"
) -> str:
    """
    Synthesize rap vocals with appropriate style

    Args:
        text: Rap lyrics
        out_path: Output path
        speaker_wav: Voice clone reference
        style: Rap style (aggressive, smooth, hype)

    Returns:
        Path to generated audio
    """
    # For rap, use speech-rhythm synthesis
    # TODO: Add rhythm/flow control
    return synthesize(text, out_path, speaker_wav, "en")


def sing_synthesize(
    text: str,
    out_path: str,
    melody: list,
    speaker_wav: Optional[str] = None
) -> str:
    """
    Synthesize sung vocals with melody

    Args:
        text: Lyrics
        out_path: Output path
        melody: MIDI note sequence
        speaker_wav: Voice clone reference

    Returns:
        Path to generated audio
    """
    # First synthesize speech
    temp_path = out_path.replace(".wav", "_temp.wav")
    synthesize(text, temp_path, speaker_wav, "en")

    # Apply melody (pitch shifting)
    # This would use the melody to pitch-shift the audio
    # For now, just copy the file
    import shutil
    shutil.copy(temp_path, out_path)

    if os.path.exists(temp_path):
        os.remove(temp_path)

    return out_path


def multilingual_synthesize(
    text: str,
    languages: list,
    out_dir: str,
    base_name: str = "vocal"
) -> dict:
    """
    Synthesize vocals in multiple languages

    Args:
        text: Base text
        languages: List of language codes (en, es, fr, de, jp, etc.)
        out_dir: Output directory
        base_name: Base filename

    Returns:
        Dict mapping language to output path
    """
    os.makedirs(out_dir, exist_ok=True)

    outputs = {}

    for lang in languages:
        out_path = os.path.join(out_dir, f"{base_name}_{lang}.wav")

        # TODO: Add translation if text is not in target language
        # For now, synthesize in target language directly
        synthesize(text, out_path, language=lang)

        outputs[lang] = out_path

    return outputs


def clone_voice(
    reference_wav: str,
    text: str,
    out_path: str
) -> str:
    """
    Clone a voice and synthesize new text

    Args:
        reference_wav: Reference audio for voice cloning
        text: New text to speak
        out_path: Output path

    Returns:
        Path to cloned vocal
    """
    return synthesize(text, out_path, speaker_wav=reference_wav)
