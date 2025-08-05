"""
Utility functions for the web application
"""

from typing import List, Optional

# Cache prompts to avoid repeated file I/O
_cached_prompts = None


def load_prompts() -> List[str]:
    """Load prompts from prompts.txt file (cached)"""
    global _cached_prompts

    if _cached_prompts is not None:
        return _cached_prompts

    try:
        with open('data/prompts.txt', 'r', encoding='utf-8') as f:
            prompts = [line.strip() for line in f if line.strip()]
        _cached_prompts = prompts
        return prompts
    except FileNotFoundError:
        # Default prompts if file doesn't exist
        _cached_prompts = [
            "A funny haiku",
            "Your favorite meme",
            "A gif that describes your mood",
            "Something that would make them laugh",
            "A random fact",
            "A terrible dad joke",
            "An inspirational quote",
            "A picture of something cute"
        ]
        return _cached_prompts


def get_player_room(game_manager, game_id: str, player_id: str) -> Optional[str]:
    """Get the socket room for a specific player"""
    for sid, session in game_manager.player_sessions.items():
        if session.player_id == player_id and session.game_id == game_id:
            return sid
    return None
