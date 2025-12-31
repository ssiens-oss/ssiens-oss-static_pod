"""
AI Lyrics Generation using Claude

Generates song lyrics based on genre, mood, and theme
"""

import os
from typing import Dict, Optional, List
import json


def generate_lyrics_prompt(
    genre: str,
    mood: str,
    theme: Optional[str] = None,
    song_structure: Optional[List[str]] = None,
    style: str = "catchy"
) -> str:
    """
    Generate a prompt for Claude to create lyrics

    Args:
        genre: Music genre
        mood: Emotional mood
        theme: Optional theme/topic
        song_structure: List of section types (verse, chorus, etc.)
        style: Lyrical style (catchy, poetic, narrative, abstract)
    """
    structure_str = ", ".join(song_structure) if song_structure else "verse, chorus, verse, chorus, bridge, chorus"

    theme_str = f"Theme: {theme}\n" if theme else ""

    prompt = f"""Generate song lyrics for a {genre} track with a {mood} mood.

{theme_str}Style: {style}
Structure: {structure_str}

Requirements:
- Write complete lyrics for each section
- Make the chorus catchy and memorable
- Match the emotional tone to the {mood} mood
- Fit the {genre} genre conventions
- Be creative and original
- Use vivid imagery

Format the output as JSON with this structure:
{{
  "title": "Song Title",
  "sections": [
    {{"type": "verse", "lyrics": ["line 1", "line 2", ...]}},
    {{"type": "chorus", "lyrics": ["line 1", "line 2", ...]}}
  ],
  "theme": "brief theme description",
  "mood_tags": ["tag1", "tag2", "tag3"]
}}

Generate the lyrics now:"""

    return prompt


def parse_lyrics_response(response: str) -> Dict:
    """Parse Claude's response into structured lyrics"""
    try:
        # Try to extract JSON from response
        start = response.find("{")
        end = response.rfind("}") + 1

        if start >= 0 and end > start:
            json_str = response[start:end]
            lyrics_data = json.loads(json_str)
            return lyrics_data
    except:
        pass

    # Fallback: simple parsing
    return {
        "title": "Generated Song",
        "sections": [
            {"type": "verse", "lyrics": ["AI-generated lyrics"]},
            {"type": "chorus", "lyrics": ["Coming soon"]}
        ],
        "theme": "auto-generated",
        "mood_tags": ["electronic"]
    }


async def generate_lyrics_with_claude(
    genre: str,
    mood: str,
    theme: Optional[str] = None,
    structure: Optional[List[str]] = None
) -> Dict:
    """
    Generate lyrics using Claude API

    Returns structured lyrics data
    """
    # Check if Anthropic API key is available
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        print("⚠️  ANTHROPIC_API_KEY not set, using placeholder lyrics")
        return generate_placeholder_lyrics(genre, mood, structure)

    try:
        # Try to use Anthropic API
        try:
            from anthropic import AsyncAnthropic
        except ImportError:
            print("⚠️  anthropic package not installed, using placeholder lyrics")
            return generate_placeholder_lyrics(genre, mood, structure)

        client = AsyncAnthropic(api_key=api_key)

        prompt = generate_lyrics_prompt(genre, mood, theme, structure)

        response = await client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        lyrics_text = response.content[0].text
        lyrics_data = parse_lyrics_response(lyrics_text)

        return lyrics_data

    except Exception as e:
        print(f"Error generating lyrics with Claude: {e}")
        return generate_placeholder_lyrics(genre, mood, structure)


def generate_placeholder_lyrics(
    genre: str,
    mood: str,
    structure: Optional[List[str]] = None
) -> Dict:
    """Generate placeholder lyrics when Claude API is unavailable"""

    if not structure:
        structure = ["verse", "chorus", "verse", "chorus", "bridge", "chorus"]

    sections = []

    for i, section_type in enumerate(structure):
        if section_type == "verse":
            lyrics = [
                f"In the {mood} of the {genre} night",
                "Where melodies take flight",
                "Every beat, every sound",
                "Magic can be found"
            ]
        elif section_type == "chorus":
            lyrics = [
                f"This is the {genre} way",
                "Dancing through the day",
                "Feel the rhythm, feel the vibe",
                "Come alive, come alive"
            ]
        elif section_type == "bridge":
            lyrics = [
                "Instrumental break",
                f"Let the {genre} speak",
                "No words needed here",
                "Just feel the atmosphere"
            ]
        else:
            lyrics = [
                f"[{section_type}]",
                "Instrumental section"
            ]

        sections.append({
            "type": section_type,
            "lyrics": lyrics
        })

    return {
        "title": f"{mood.title()} {genre.replace('_', ' ').title()} Track",
        "sections": sections,
        "theme": f"{mood} {genre} vibes",
        "mood_tags": [mood, genre, "electronic", "instrumental"]
    }


def lyrics_to_text(lyrics_data: Dict) -> str:
    """Convert lyrics data to readable text format"""
    lines = []

    lines.append(f"# {lyrics_data.get('title', 'Untitled')}\n")

    for section in lyrics_data.get("sections", []):
        section_type = section.get("type", "").upper()
        section_lyrics = section.get("lyrics", [])

        lines.append(f"\n[{section_type}]")
        for line in section_lyrics:
            lines.append(line)

    if "theme" in lyrics_data:
        lines.append(f"\n---\nTheme: {lyrics_data['theme']}")

    if "mood_tags" in lyrics_data:
        lines.append(f"Tags: {', '.join(lyrics_data['mood_tags'])}")

    return "\n".join(lines)
