"""
Vocal Role Planner - Decides rap vs sung vocals per section
"""

from typing import Dict, List


def assign_roles(song_plan: Dict) -> List[Dict]:
    """
    Assign vocal roles (rap/sing) to song sections

    Args:
        song_plan: Song plan with style and structure

    Returns:
        List of vocal role assignments
    """
    roles = []
    style = song_plan.get("style", "edm")

    for section in song_plan["structure"]:
        name = section["section"]
        bars = section["bars"]
        energy = section["energy"]

        # Verses -> Rap (for hip-hop/trap)
        if "verse" in name and style in ["hiphop", "trap"]:
            roles.append({
                "section": name,
                "role": "rap",
                "bars": bars,
                "energy": energy,
                "style": "rhythmic"
            })

        # Choruses/Hooks -> Sung
        elif "chorus" in name or "hook" in name:
            roles.append({
                "section": name,
                "role": "sing",
                "bars": min(8, bars),  # Hooks are usually shorter
                "energy": energy,
                "style": "melodic"
            })

        # Drops (EDM) -> Chants/Shouts
        elif "drop" in name:
            roles.append({
                "section": name,
                "role": "chant",
                "bars": 4,
                "energy": energy,
                "style": "hype"
            })

        # Bridges -> Ad-libs
        elif "bridge" in name:
            roles.append({
                "section": name,
                "role": "adlib",
                "bars": 4,
                "energy": energy,
                "style": "atmospheric"
            })

    return roles


def get_vocal_intensity(role: str, energy: float) -> str:
    """
    Determine vocal intensity based on role and energy

    Args:
        role: Vocal role (rap, sing, chant, adlib)
        energy: Energy level (0.0-1.0)

    Returns:
        Intensity descriptor
    """
    if energy > 0.8:
        return "high"
    elif energy > 0.5:
        return "medium"
    else:
        return "low"
