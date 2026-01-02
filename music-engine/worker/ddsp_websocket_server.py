"""
StaticWaves DDSP WebSocket Audio Server
Real-time instrument synthesis with low-latency streaming
"""

import asyncio
import websockets
import numpy as np
import json
import sys
import os
from typing import Dict, Optional

# Try to import DDSP (gracefully fallback to mock)
try:
    import ddsp
    import ddsp.training
    HAS_DDSP = True
    print("✓ DDSP library loaded")
except ImportError:
    HAS_DDSP = False
    print("⚠ DDSP not available - using mock synthesis")

SAMPLE_RATE = 32000
BUFFER_SIZE = 1024  # Small buffer for low latency
HOST = "0.0.0.0"
PORT = 8765


class InstrumentSynthesizer:
    """
    Manages DDSP instrument models and synthesis
    """

    def __init__(self):
        self.models = {}
        self.current_instrument = "violin"
        self.load_models()

    def load_models(self):
        """Load available instrument models"""
        if not HAS_DDSP:
            print("Using mock instruments")
            return

        # Try to load pre-trained models
        model_dir = os.getenv("DDSP_MODELS_DIR", "models/ddsp")
        instruments = ["violin", "cello", "trumpet", "flute"]

        for instrument in instruments:
            model_path = os.path.join(model_dir, instrument)
            if os.path.exists(model_path):
                try:
                    model = ddsp.training.models.Autoencoder()
                    model.restore(model_path)
                    self.models[instrument] = model
                    print(f"✓ Loaded {instrument} model")
                except Exception as e:
                    print(f"✗ Failed to load {instrument}: {e}")
            else:
                print(f"⚠ Model not found: {model_path}")

        if not self.models:
            print("⚠ No DDSP models loaded - using fallback synthesis")

    def synthesize(
        self,
        pitch: float,
        energy: float,
        tension: float = 0.5,
        instrument: Optional[str] = None
    ) -> np.ndarray:
        """
        Generate audio buffer for given parameters

        Args:
            pitch: MIDI note number (0-127)
            energy: Loudness/amplitude (0-1)
            tension: Harmonic tension/brightness (0-1)
            instrument: Instrument name (optional)

        Returns:
            Audio buffer as numpy array
        """
        if instrument and instrument in self.models:
            return self._synthesize_ddsp(pitch, energy, tension, instrument)
        else:
            return self._synthesize_fallback(pitch, energy, tension)

    def _synthesize_ddsp(
        self,
        pitch: float,
        energy: float,
        tension: float,
        instrument: str
    ) -> np.ndarray:
        """Synthesize using DDSP model"""
        model = self.models[instrument]

        # Convert MIDI to frequency
        f0_hz = 440.0 * (2.0 ** ((pitch - 69) / 12.0))
        f0 = np.ones(BUFFER_SIZE) * f0_hz

        # Convert energy to loudness (dB)
        loudness_db = (energy * 60.0) - 60.0  # Range: -60dB to 0dB
        loudness = np.ones(BUFFER_SIZE) * loudness_db

        # Apply tension to harmonic brightness (optional enhancement)
        # Could modify model parameters here

        # Run inference
        audio = model.decode(f0_hz=f0, loudness_db=loudness)

        return audio

    def _synthesize_fallback(
        self,
        pitch: float,
        energy: float,
        tension: float
    ) -> np.ndarray:
        """
        Fallback synthesis using procedural oscillators
        Used when DDSP models aren't available
        """
        # Convert MIDI to frequency
        freq = 440.0 * (2.0 ** ((pitch - 69) / 12.0))

        # Generate time array
        t = np.arange(BUFFER_SIZE) / SAMPLE_RATE

        # Base oscillator (sawtooth for richer harmonics)
        audio = self._sawtooth(2 * np.pi * freq * t)

        # Add harmonics based on tension
        if tension > 0.3:
            audio += 0.3 * self._sawtooth(2 * np.pi * freq * 2 * t)
        if tension > 0.6:
            audio += 0.2 * self._sawtooth(2 * np.pi * freq * 3 * t)

        # Apply amplitude envelope
        audio *= energy

        # Simple low-pass filter based on tension
        cutoff = 0.3 + (tension * 0.7)
        audio = self._simple_lowpass(audio, cutoff)

        return audio.astype(np.float32)

    @staticmethod
    def _sawtooth(phase):
        """Generate sawtooth wave"""
        return 2 * (phase / (2 * np.pi) - np.floor(phase / (2 * np.pi) + 0.5))

    @staticmethod
    def _simple_lowpass(audio, cutoff):
        """Simple one-pole lowpass filter"""
        output = np.zeros_like(audio)
        output[0] = audio[0]
        for i in range(1, len(audio)):
            output[i] = output[i-1] + cutoff * (audio[i] - output[i-1])
        return output


class MusicState:
    """
    Tracks current musical state from client updates
    """

    def __init__(self):
        self.pitch = 60.0  # Middle C
        self.energy = 0.5
        self.tension = 0.5
        self.darkness = 0.5
        self.instrument = "violin"
        self.playing = True

    def update(self, data: Dict):
        """Update state from client message"""
        if "pitch" in data:
            self.pitch = float(data["pitch"])
        if "energy" in data:
            self.energy = float(data["energy"])
        if "tension" in data:
            self.tension = float(data["tension"])
        if "darkness" in data:
            self.darkness = float(data["darkness"])
        if "instrument" in data:
            self.instrument = data["instrument"]
        if "playing" in data:
            self.playing = bool(data["playing"])


async def audio_generator(state: MusicState, synth: InstrumentSynthesizer):
    """
    Continuously generate audio buffers based on current state
    """
    while True:
        if state.playing:
            # Generate audio chunk
            audio = synth.synthesize(
                pitch=state.pitch,
                energy=state.energy,
                tension=state.tension,
                instrument=state.instrument
            )

            # Convert to PCM Int16
            audio_int16 = (audio * 32767).astype(np.int16)
            yield audio_int16.tobytes()

        # Small delay to control generation rate
        await asyncio.sleep(BUFFER_SIZE / SAMPLE_RATE)


async def handle_client(websocket, path):
    """
    Handle WebSocket client connection
    """
    print(f"✓ Client connected from {websocket.remote_address}")

    state = MusicState()
    synth = InstrumentSynthesizer()

    # Create audio generator
    audio_gen = audio_generator(state, synth)

    try:
        # Handle messages and audio streaming concurrently
        async def receive_controls():
            """Receive control updates from client"""
            async for message in websocket:
                try:
                    data = json.loads(message)
                    state.update(data)
                    print(f"State updated: pitch={state.pitch:.1f}, energy={state.energy:.2f}, tension={state.tension:.2f}")
                except json.JSONDecodeError:
                    print(f"Invalid JSON received: {message}")

        async def send_audio():
            """Send audio stream to client"""
            async for audio_chunk in audio_gen:
                try:
                    await websocket.send(audio_chunk)
                except websockets.exceptions.ConnectionClosed:
                    break

        # Run both tasks concurrently
        await asyncio.gather(
            receive_controls(),
            send_audio()
        )

    except websockets.exceptions.ConnectionClosed:
        print(f"✗ Client disconnected")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Start WebSocket server"""
    print(f"""
    ╔════════════════════════════════════════════════╗
    ║   StaticWaves DDSP WebSocket Server            ║
    ║                                                ║
    ║   Real-time instrument synthesis               ║
    ║   Low-latency audio streaming                  ║
    ║                                                ║
    ║   Listening on ws://{HOST}:{PORT}    ║
    ╚════════════════════════════════════════════════╝
    """)

    # Start WebSocket server
    async with websockets.serve(handle_client, HOST, PORT):
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n✓ Server stopped")
