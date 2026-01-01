"""
MIDI Export System
Export vocal melodies and harmonies as MIDI files for DAW integration
"""

import os
from typing import List, Dict, Optional

try:
    import mido
    from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo
    MIDO_AVAILABLE = True
except ImportError:
    MIDO_AVAILABLE = False
    print("Warning: mido not available, MIDI export disabled")


def export_melody_midi(
    melody: List[int],
    bpm: int,
    out_path: str,
    root_note: int = 60,
    velocity: int = 80
) -> str:
    """
    Export melody as MIDI file

    Args:
        melody: List of semitone offsets from root
        bpm: Beats per minute
        out_path: Output MIDI file path
        root_note: MIDI root note (60 = middle C)
        velocity: Note velocity

    Returns:
        Path to MIDI file
    """
    if not MIDO_AVAILABLE:
        print("Warning: MIDI export unavailable (mido not installed)")
        return ""

    # Create MIDI file
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    # Set tempo
    track.append(MetaMessage('set_tempo', tempo=bpm2tempo(bpm)))
    track.append(MetaMessage('track_name', name='Vocal Melody'))

    # Add notes
    ticks_per_quarter = 480
    note_duration = ticks_per_quarter  # Quarter note

    for i, offset in enumerate(melody):
        note = root_note + offset

        # Note on
        track.append(Message(
            'note_on',
            note=note,
            velocity=velocity,
            time=0 if i == 0 else note_duration
        ))

        # Note off (after duration)
        track.append(Message(
            'note_off',
            note=note,
            velocity=0,
            time=note_duration
        ))

    # Save
    mid.save(out_path)
    print(f"✓ Exported melody MIDI: {out_path}")

    return out_path


def export_harmony_midi(
    melody: List[int],
    harmony_intervals: List[int],
    bpm: int,
    out_path: str,
    root_note: int = 60
) -> str:
    """
    Export harmony parts as separate MIDI tracks

    Args:
        melody: Base melody
        harmony_intervals: List of harmony intervals (e.g., [3, 7])
        bpm: BPM
        out_path: Output path
        root_note: Root MIDI note

    Returns:
        Path to MIDI file
    """
    if not MIDO_AVAILABLE:
        return ""

    mid = MidiFile()

    # Tempo track
    tempo_track = MidiTrack()
    mid.tracks.append(tempo_track)
    tempo_track.append(MetaMessage('set_tempo', tempo=bpm2tempo(bpm)))

    # Lead melody track
    lead_track = MidiTrack()
    mid.tracks.append(lead_track)
    lead_track.append(MetaMessage('track_name', name='Lead Vocal'))

    _add_melody_to_track(lead_track, melody, root_note)

    # Harmony tracks
    for i, interval in enumerate(harmony_intervals):
        harmony_track = MidiTrack()
        mid.tracks.append(harmony_track)
        harmony_track.append(MetaMessage('track_name', name=f'Harmony +{interval}'))

        # Transpose melody by interval
        harmony_melody = [note + interval for note in melody]
        _add_melody_to_track(harmony_track, harmony_melody, root_note, velocity=70)

    mid.save(out_path)
    print(f"✓ Exported harmony MIDI: {out_path}")

    return out_path


def _add_melody_to_track(
    track: 'MidiTrack',
    melody: List[int],
    root_note: int,
    velocity: int = 80
):
    """Add melody notes to MIDI track"""
    ticks_per_quarter = 480
    note_duration = ticks_per_quarter

    for i, offset in enumerate(melody):
        note = root_note + offset

        track.append(Message(
            'note_on',
            note=note,
            velocity=velocity,
            time=0 if i == 0 else note_duration
        ))

        track.append(Message(
            'note_off',
            note=note,
            velocity=0,
            time=note_duration
        ))


def export_full_song_midi(
    song_plan: Dict,
    vocal_melodies: Dict[str, List[int]],
    out_path: str
) -> str:
    """
    Export complete song with all vocal melodies as MIDI

    Args:
        song_plan: Song plan dict
        vocal_melodies: Dict mapping section names to melodies
        out_path: Output path

    Returns:
        Path to MIDI file
    """
    if not MIDO_AVAILABLE:
        return ""

    mid = MidiFile()
    bpm = song_plan.get("bpm", 120)

    # Tempo track
    tempo_track = MidiTrack()
    mid.tracks.append(tempo_track)
    tempo_track.append(MetaMessage('set_tempo', tempo=bpm2tempo(bpm)))

    # Track for each section
    for section_name, melody in vocal_melodies.items():
        track = MidiTrack()
        mid.tracks.append(track)
        track.append(MetaMessage('track_name', name=section_name))

        _add_melody_to_track(track, melody, root_note=60)

    mid.save(out_path)
    print(f"✓ Exported full song MIDI: {out_path}")

    return out_path


def import_midi_as_melody(midi_path: str) -> List[int]:
    """
    Import MIDI file and extract melody as note offsets

    Args:
        midi_path: Path to MIDI file

    Returns:
        List of semitone offsets
    """
    if not MIDO_AVAILABLE:
        return []

    mid = MidiFile(midi_path)
    melody = []

    for track in mid.tracks:
        for msg in track:
            if msg.type == 'note_on' and msg.velocity > 0:
                # Convert absolute note to offset from C4 (60)
                offset = msg.note - 60
                melody.append(offset)

    return melody
