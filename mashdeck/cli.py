#!/usr/bin/env python3
"""
MashDeck CLI - Command-line interface for MashDeck
"""

import argparse
import sys
import os

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mashdeck.song_engine.pipeline import generate_full_song
from mashdeck.vocals.pipeline import generate_vocals
from mashdeck.live.freestyle import LiveFreestyleEngine
from mashdeck.live.battle.engine import BattleEngine
from mashdeck.release.pipeline import AutoReleaser


def cmd_generate(args):
    """Generate a full song"""
    print(f"Generating {args.style} song...")

    output = generate_full_song(
        style=args.style,
        bpm=args.bpm,
        key=args.key,
        title=args.title,
        out_dir=args.output,
        create_variants=args.variants
    )

    print(f"\n✓ Song generated successfully!")
    print(f"Output: {output['song_final']}")


def cmd_vocal(args):
    """Generate vocals for existing instrumental"""
    print("Generating vocals...")

    from mashdeck.song_engine.planner import load_song_plan

    # Load song plan
    plan_path = os.path.join(args.song_dir, "song_plan.json")
    song_plan = load_song_plan(plan_path)

    # Get section files
    sections_dir = os.path.join(args.song_dir, "sections")
    section_files = {}

    for filename in os.listdir(sections_dir):
        if filename.endswith(".wav"):
            section_name = filename.replace(".wav", "")
            section_files[section_name] = os.path.join(sections_dir, filename)

    # Generate vocals
    vocal_output = generate_vocals(
        song_plan,
        section_files,
        args.song_dir,
        enable_harmonies=not args.no_harmonies,
        enable_midi_export=args.midi
    )

    print(f"\n✓ Vocals generated!")
    print(f"Vocals dir: {vocal_output['vocals_dir']}")


def cmd_freestyle(args):
    """Run live freestyle mode"""
    print("🎤 Live Freestyle Mode")
    print("Type messages as if they're chat, or 'freestyle' to generate\n")

    engine = LiveFreestyleEngine(output_dir=args.output)

    while True:
        try:
            msg = input("> ")

            if msg.lower() == "freestyle":
                result = engine.generate_from_chat(bars=args.bars, force=True)
                if result:
                    print(f"✓ Generated: {result}")
            elif msg.lower() == "quit":
                break
            else:
                # Simulate chat message
                engine.add_chat_message("user", msg)
                print("  (added to chat)")

        except KeyboardInterrupt:
            break

    print("\nFreestyle session ended")


def cmd_battle(args):
    """Run AI rapper battle"""
    print("\n🥊 AI RAPPER BATTLE MODE 🥊\n")

    engine = BattleEngine(output_dir=args.output)
    engine.start_battle()

    # Simulate some chat for demo
    print("Adding simulated chat messages...\n")

    # Side A messages
    for msg in ["fire", "let's go", "energy", "sick beat"]:
        engine.add_message_a("user_a", msg)

    # Side B messages
    for msg in ["yeah", "intense", "vibe", "amazing"]:
        engine.add_message_b("user_b", msg)

    # Execute rounds
    for i in range(args.rounds):
        engine.execute_round(bars=args.bars)
        print()

    # End battle
    winner = engine.end_battle()


def cmd_release(args):
    """Auto-release track to platforms"""
    print("🚀 Auto-Release Pipeline\n")

    releaser = AutoReleaser()

    metadata = {
        "title": args.title or "MashDeck Track",
        "artist": args.artist or "MashDeck AI",
        "genre": args.genre or "Electronic"
    }

    results = releaser.release_everywhere(
        args.audio,
        metadata,
        platforms=args.platforms.split(",") if args.platforms else None
    )

    print("\n✓ Release initiated!")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="MashDeck - AI Music Production System"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate a full song")
    gen_parser.add_argument("--style", default="edm", help="Music style")
    gen_parser.add_argument("--bpm", type=int, help="BPM")
    gen_parser.add_argument("--key", help="Musical key")
    gen_parser.add_argument("--title", help="Song title")
    gen_parser.add_argument("--output", default="output", help="Output directory")
    gen_parser.add_argument("--variants", action="store_true", help="Create platform variants")
    gen_parser.set_defaults(func=cmd_generate)

    # Vocal command
    vocal_parser = subparsers.add_parser("vocal", help="Generate vocals")
    vocal_parser.add_argument("song_dir", help="Song directory (with song_plan.json)")
    vocal_parser.add_argument("--no-harmonies", action="store_true", help="Skip harmonies")
    vocal_parser.add_argument("--midi", action="store_true", help="Export MIDI")
    vocal_parser.set_defaults(func=cmd_vocal)

    # Freestyle command
    free_parser = subparsers.add_parser("freestyle", help="Live freestyle mode")
    free_parser.add_argument("--bars", type=int, default=4, help="Bars per freestyle")
    free_parser.add_argument("--output", default="freestyle_output", help="Output dir")
    free_parser.set_defaults(func=cmd_freestyle)

    # Battle command
    battle_parser = subparsers.add_parser("battle", help="AI rapper battle")
    battle_parser.add_argument("--rounds", type=int, default=3, help="Number of rounds")
    battle_parser.add_argument("--bars", type=int, default=4, help="Bars per round")
    battle_parser.add_argument("--output", default="battles", help="Output dir")
    battle_parser.set_defaults(func=cmd_battle)

    # Release command
    release_parser = subparsers.add_parser("release", help="Auto-release track")
    release_parser.add_argument("audio", help="Audio file path")
    release_parser.add_argument("--title", help="Track title")
    release_parser.add_argument("--artist", help="Artist name")
    release_parser.add_argument("--genre", help="Genre")
    release_parser.add_argument("--platforms", help="Platforms (comma-separated)")
    release_parser.set_defaults(func=cmd_release)

    # Parse and execute
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
