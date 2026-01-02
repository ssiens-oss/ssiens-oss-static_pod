"""
StaticWaves Polyphonic Ensemble Mixer
Multi-layered composition with independent instrument control
"""

import numpy as np
from typing import Dict, List, Optional
import json


class MusicLayer:
    """
    Represents a single layer in the ensemble (rhythm, bass, harmony, melody, texture)
    """
    def __init__(self, name: str, instrument: str, role: str):
        self.name = name
        self.instrument = instrument
        self.role = role  # rhythm, bass, harmony, melody, texture
        self.intensity = 1.0
        self.pan = 0.0  # -1.0 (left) to 1.0 (right)
        self.notes = []  # List of active notes [(pitch, velocity, duration)]
        self.effects = {
            "reverb": 0.0,
            "delay": 0.0,
            "distortion": 0.0,
            "chorus": 0.0
        }

    def set_intensity(self, value: float):
        """Set layer intensity/volume (0.0 to 1.0)"""
        self.intensity = max(0.0, min(1.0, value))

    def add_note(self, pitch: int, velocity: float = 0.8, duration: float = 1.0):
        """Add a note to this layer"""
        self.notes.append({
            "pitch": pitch,
            "velocity": velocity,
            "duration": duration,
            "time": 0  # Will be set by mixer
        })

    def clear_notes(self):
        """Clear all notes"""
        self.notes = []

    def set_effect(self, effect_name: str, amount: float):
        """Set effect amount (0.0 to 1.0)"""
        if effect_name in self.effects:
            self.effects[effect_name] = max(0.0, min(1.0, amount))

    def to_dict(self):
        """Serialize to dict"""
        return {
            "name": self.name,
            "instrument": self.instrument,
            "role": self.role,
            "intensity": self.intensity,
            "pan": self.pan,
            "notes": self.notes,
            "effects": self.effects
        }


class EnsembleMixer:
    """
    Manages multiple instrument layers and mixes them into final audio
    Supports polyphony and independent layer control
    """

    def __init__(self, sample_rate: int = 32000):
        self.sample_rate = sample_rate
        self.layers: Dict[str, MusicLayer] = {}
        self.master_volume = 1.0
        self.tempo = 120  # BPM
        self.key = "C"
        self.scale = "minor"

    def add_layer(self, name: str, instrument: str, role: str):
        """Add a new layer to the ensemble"""
        layer = MusicLayer(name, instrument, role)
        self.layers[name] = layer
        return layer

    def get_layer(self, name: str) -> Optional[MusicLayer]:
        """Get a layer by name"""
        return self.layers.get(name)

    def remove_layer(self, name: str):
        """Remove a layer"""
        if name in self.layers:
            del self.layers[name]

    def update_from_context(self, context: Dict):
        """
        Update ensemble based on music context

        Context example:
        {
            "energy": 0.8,
            "tension": 0.6,
            "darkness": 0.5,
            "complexity": 0.4
        }
        """
        energy = context.get("energy", 0.5)
        tension = context.get("tension", 0.5)
        darkness = context.get("darkness", 0.5)
        complexity = context.get("complexity", 0.5)

        # Update rhythm layer
        if "rhythm" in self.layers:
            # More energy = louder rhythm
            self.layers["rhythm"].set_intensity(0.6 + (energy * 0.4))
            # More complexity = more reverb on drums
            self.layers["rhythm"].set_effect("reverb", complexity * 0.3)

        # Update bass layer
        if "bass" in self.layers:
            # Energy affects bass drive
            self.layers["bass"].set_intensity(0.7 + (energy * 0.3))
            # Darkness affects bass tone
            distortion = max(0, darkness - 0.5) * 0.6
            self.layers["bass"].set_effect("distortion", distortion)

        # Update harmony layer
        if "harmony" in self.layers:
            # Tension affects harmony intensity
            self.layers["harmony"].set_intensity(0.5 + (tension * 0.5))
            # Darkness affects chorus
            self.layers["harmony"].set_effect("chorus", darkness * 0.4)
            # Complexity affects reverb
            self.layers["harmony"].set_effect("reverb", complexity * 0.6)

        # Update melody layer
        if "melody" in self.layers:
            # Energy affects melody presence
            self.layers["melody"].set_intensity(0.4 + (energy * 0.6))
            # Complexity affects delay
            self.layers["melody"].set_effect("delay", complexity * 0.5)

        # Update texture layer
        if "texture" in self.layers:
            # Darkness affects texture prominence
            self.layers["texture"].set_intensity(darkness * 0.8)
            # Always spacious
            self.layers["texture"].set_effect("reverb", 0.7)

    def generate_chords_for_context(self, context: Dict):
        """
        Generate appropriate chord progression based on context
        """
        tension = context.get("tension", 0.5)
        darkness = context.get("darkness", 0.5)

        # Base note (C in C minor)
        base_note = 60

        # Chord progression based on tension/darkness
        if tension < 0.3 and darkness < 0.3:
            # Bright and calm: I - IV - V
            chords = [[60, 64, 67], [65, 69, 72], [67, 71, 74]]
        elif tension < 0.3 and darkness >= 0.3:
            # Dark and calm: i - iv - v (minor)
            chords = [[60, 63, 67], [65, 68, 72], [67, 70, 74]]
        elif tension >= 0.3 and darkness < 0.3:
            # Bright and tense: I - vi - IV - V
            chords = [[60, 64, 67], [69, 72, 76], [65, 69, 72], [67, 71, 74]]
        else:
            # Dark and tense: i - VI - III - VII (dramatic minor)
            chords = [[60, 63, 67], [68, 72, 75], [63, 67, 70], [70, 74, 77]]

        return chords

    def auto_compose(self, context: Dict, duration_bars: int = 4):
        """
        Automatically compose music for all layers based on context
        """
        energy = context.get("energy", 0.5)
        complexity = context.get("complexity", 0.5)

        # Get chord progression
        chords = self.generate_chords_for_context(context)

        # Clear existing notes
        for layer in self.layers.values():
            layer.clear_notes()

        # Rhythm layer - drums
        if "rhythm" in self.layers:
            note_density = int(4 + (complexity * 8))  # 4-12 hits per bar
            for bar in range(duration_bars):
                for beat in range(note_density):
                    # Kick and snare pattern
                    time = bar + (beat / note_density)
                    pitch = 36 if beat % 2 == 0 else 38  # Kick / Snare
                    velocity = 0.7 + (energy * 0.3)
                    self.layers["rhythm"].add_note(pitch, velocity, 0.1)

        # Bass layer
        if "bass" in self.layers:
            for bar in range(duration_bars):
                chord = chords[bar % len(chords)]
                bass_note = chord[0] - 12  # Root note, one octave down
                self.layers["bass"].add_note(bass_note, 0.8, 1.0)

        # Harmony layer - pads
        if "harmony" in self.layers:
            for bar in range(duration_bars):
                chord = chords[bar % len(chords)]
                for note in chord:
                    self.layers["harmony"].add_note(note, 0.6, 2.0)

        # Melody layer
        if "melody" in self.layers:
            notes_per_bar = int(2 + (complexity * 6))
            for bar in range(duration_bars):
                chord = chords[bar % len(chords)]
                for i in range(notes_per_bar):
                    # Melody from chord tones + passing notes
                    note = chord[i % len(chord)] + 12  # Octave up
                    if complexity > 0.5:
                        note += np.random.choice([-1, 0, 1])  # Add variety
                    self.layers["melody"].add_note(note, 0.7, 0.25)

        # Texture layer - ambient
        if "texture" in self.layers:
            for bar in range(duration_bars):
                chord = chords[bar % len(chords)]
                # High sustained notes
                for note in chord:
                    self.layers["texture"].add_note(note + 24, 0.4, 4.0)

    def mix_layers(self, ddsp_synth=None) -> np.ndarray:
        """
        Mix all layers into final audio output

        Args:
            ddsp_synth: Optional DDSP synthesizer for rendering

        Returns:
            Mixed audio as numpy array
        """
        # Calculate total duration
        max_duration = 0
        for layer in self.layers.values():
            for note in layer.notes:
                duration = note["time"] + note["duration"]
                max_duration = max(max_duration, duration)

        # Generate silence
        samples = int(max_duration * self.sample_rate)
        mixed_audio = np.zeros(samples, dtype=np.float32)

        # Render each layer
        for layer_name, layer in self.layers.items():
            if layer.intensity == 0:
                continue

            layer_audio = np.zeros(samples, dtype=np.float32)

            # Render each note
            for note in layer.notes:
                start_sample = int(note["time"] * self.sample_rate)
                duration_samples = int(note["duration"] * self.sample_rate)

                if ddsp_synth:
                    # Use DDSP for realistic synthesis
                    note_audio = ddsp_synth.synthesize(
                        pitch=note["pitch"],
                        energy=note["velocity"],
                        duration=duration_samples,
                        instrument=layer.instrument
                    )
                else:
                    # Fallback: simple sine wave
                    t = np.arange(duration_samples) / self.sample_rate
                    freq = 440 * (2 ** ((note["pitch"] - 69) / 12))
                    note_audio = np.sin(2 * np.pi * freq * t) * note["velocity"]

                # Add to layer audio
                end_sample = start_sample + len(note_audio)
                if end_sample <= samples:
                    layer_audio[start_sample:end_sample] += note_audio[:duration_samples]

            # Apply effects
            layer_audio = self._apply_effects(layer_audio, layer.effects)

            # Apply panning
            # (Simplified - in stereo version would pan left/right)

            # Mix into final output
            mixed_audio += layer_audio * layer.intensity

        # Apply master volume
        mixed_audio *= self.master_volume

        # Normalize to prevent clipping
        max_val = np.abs(mixed_audio).max()
        if max_val > 1.0:
            mixed_audio /= max_val

        return mixed_audio

    def _apply_effects(self, audio: np.ndarray, effects: Dict) -> np.ndarray:
        """
        Apply effects to audio
        Simplified implementation - production would use proper DSP
        """
        result = audio.copy()

        # Reverb (simple delay)
        if effects["reverb"] > 0:
            delay_samples = int(0.05 * self.sample_rate)  # 50ms delay
            delayed = np.zeros_like(result)
            delayed[delay_samples:] = result[:-delay_samples]
            result = result + (delayed * effects["reverb"] * 0.5)

        # Distortion (soft clipping)
        if effects["distortion"] > 0:
            drive = 1 + (effects["distortion"] * 10)
            result = np.tanh(result * drive) / drive

        # Chorus (pitch modulation)
        if effects["chorus"] > 0:
            # Simplified - would normally use modulated delay
            pass

        # Delay (echo)
        if effects["delay"] > 0:
            delay_samples = int(0.25 * self.sample_rate)  # 250ms
            delayed = np.zeros_like(result)
            delayed[delay_samples:] = result[:-delay_samples] * effects["delay"] * 0.6
            result = result + delayed

        return result

    def to_dict(self):
        """Serialize ensemble state"""
        return {
            "master_volume": self.master_volume,
            "tempo": self.tempo,
            "key": self.key,
            "scale": self.scale,
            "layers": {name: layer.to_dict() for name, layer in self.layers.items()}
        }

    def from_dict(self, data: Dict):
        """Load ensemble state from dict"""
        self.master_volume = data.get("master_volume", 1.0)
        self.tempo = data.get("tempo", 120)
        self.key = data.get("key", "C")
        self.scale = data.get("scale", "minor")

        self.layers = {}
        for name, layer_data in data.get("layers", {}).items():
            layer = MusicLayer(
                layer_data["name"],
                layer_data["instrument"],
                layer_data["role"]
            )
            layer.intensity = layer_data.get("intensity", 1.0)
            layer.pan = layer_data.get("pan", 0.0)
            layer.notes = layer_data.get("notes", [])
            layer.effects = layer_data.get("effects", {})
            self.layers[name] = layer


def create_default_ensemble() -> EnsembleMixer:
    """
    Create a default 5-layer ensemble
    """
    mixer = EnsembleMixer()

    mixer.add_layer("rhythm", "808_drums", "rhythm")
    mixer.add_layer("bass", "analog_bass", "bass")
    mixer.add_layer("harmony", "warm_pad", "harmony")
    mixer.add_layer("melody", "supersaw_lead", "melody")
    mixer.add_layer("texture", "granular_fx", "texture")

    return mixer


# Example usage
if __name__ == "__main__":
    # Create ensemble
    ensemble = create_default_ensemble()

    # Set context
    context = {
        "energy": 0.8,
        "tension": 0.6,
        "darkness": 0.5,
        "complexity": 0.7
    }

    # Update ensemble from context
    ensemble.update_from_context(context)

    # Auto-compose
    ensemble.auto_compose(context, duration_bars=4)

    # Mix (would need DDSP synth in production)
    # audio = ensemble.mix_layers()

    # Export state
    state = ensemble.to_dict()
    print(json.dumps(state, indent=2))
