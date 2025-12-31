"""
MusicGen Engine - Base music generation using Meta's MusicGen

This module handles text-to-music generation using MusicGen
"""

import torch
import numpy as np
import os


# Check if audiocraft is available
try:
    from audiocraft.models import MusicGen
    MUSICGEN_AVAILABLE = True
except ImportError:
    MUSICGEN_AVAILABLE = False
    print("⚠️  Warning: audiocraft not installed. Using mock generation.")


class MusicGenEngine:
    """MusicGen model wrapper"""

    def __init__(self, model_name="facebook/musicgen-medium"):
        """
        Initialize MusicGen model

        Models:
        - facebook/musicgen-small (300M params, faster)
        - facebook/musicgen-medium (1.5B params, better quality)
        - facebook/musicgen-large (3.3B params, best quality)
        """
        if not MUSICGEN_AVAILABLE:
            self.model = None
            return

        print(f"Loading MusicGen model: {model_name}...")
        self.model = MusicGen.get_pretrained(model_name)
        print("✅ MusicGen model loaded")

    def generate(self, prompt: str, duration: int, temperature: float = 1.0, cfg_coef: float = 3.0):
        """
        Generate music from text prompt

        Args:
            prompt: Text description of music
            duration: Duration in seconds
            temperature: Sampling temperature (higher = more random)
            cfg_coef: Classifier-free guidance coefficient (higher = stronger prompt adherence)

        Returns:
            numpy array of audio (mono, 32kHz)
        """
        if not MUSICGEN_AVAILABLE or self.model is None:
            # Return mock audio for testing
            print(f"[MOCK] Generating {duration}s of audio for: {prompt}")
            sample_rate = 32000
            return self._generate_mock_audio(duration, sample_rate)

        # Set generation parameters
        self.model.set_generation_params(
            duration=duration,
            temperature=temperature,
            cfg_coef=cfg_coef
        )

        # Generate
        print(f"Generating: {prompt}")
        with torch.no_grad():
            wav = self.model.generate([prompt])

        # Convert to numpy (mono)
        audio = wav[0].cpu().numpy()

        # If stereo, convert to mono
        if len(audio.shape) > 1:
            audio = audio.mean(axis=0)

        return audio

    def _generate_mock_audio(self, duration: int, sample_rate: int = 32000):
        """Generate mock audio for testing (simple sine wave)"""
        t = np.linspace(0, duration, duration * sample_rate)

        # Create a simple musical pattern
        freq_bass = 110  # A2
        freq_mid = 220   # A3
        freq_high = 440  # A4

        audio = (
            0.3 * np.sin(2 * np.pi * freq_bass * t) +
            0.2 * np.sin(2 * np.pi * freq_mid * t) +
            0.1 * np.sin(2 * np.pi * freq_high * t)
        )

        # Add some variation
        envelope = np.exp(-t / duration)
        audio = audio * (0.3 + 0.7 * envelope)

        return audio


# Global model instance (loaded once)
_model_instance = None


def get_model():
    """Get or create global MusicGen model instance"""
    global _model_instance
    if _model_instance is None:
        model_name = os.getenv("MUSICGEN_MODEL", "facebook/musicgen-medium")
        _model_instance = MusicGenEngine(model_name)
    return _model_instance


def generate_base_audio(spec: dict):
    """
    Generate base audio from MusicSpec

    This is the entry point called by the worker
    """
    from shared.utils import spec_to_prompt

    # Convert spec to prompt
    prompt = spec_to_prompt(spec)
    duration = spec.get("duration", 30)

    # Get model and generate
    model = get_model()
    audio = model.generate(prompt, duration)

    return audio
