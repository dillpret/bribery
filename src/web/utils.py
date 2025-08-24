"""
Utility functions for the web application
"""

import random
from typing import List, Optional, Tuple

# Cache prompts to avoid repeated file I/O
_cached_prompts = None
_cached_random_bribes = None


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
            "Your favourite meme",
            "A gif that describes your mood",
            "Something that would make them laugh",
            "A random fact",
            "A terrible dad joke",
            "An inspirational quote",
            "A picture of something cute"
        ]
        return _cached_prompts


def load_random_bribes() -> Tuple[List[str], List[str]]:
    """Load random nouns and activities for generating random bribes (cached)"""
    global _cached_random_bribes

    if _cached_random_bribes is not None:
        return _cached_random_bribes

    nouns = []
    activities = []
    in_nouns_section = True

    try:
        with open('data/random_bribes.txt', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if line.startswith('#'):
                    if 'Activities' in line:
                        in_nouns_section = False
                    continue
                
                if in_nouns_section:
                    nouns.append(line)
                else:
                    activities.append(line)
        
        _cached_random_bribes = (nouns, activities)
        return _cached_random_bribes
    except FileNotFoundError:
        # Default random bribes if file doesn't exist
        nouns = [
            "A talking rubber duck",
            "A teapot that tells jokes",
            "A hat that compliments you",
            "A magical pencil",
            "A self-inflating whoopee cushion"
        ]
        activities = [
            "Teaching ducks to dance",
            "Knitting jumpers for garden gnomes",
            "Writing haikus about traffic jams",
            "Building a castle out of biscuits",
            "Training snails for underground racing"
        ]
        _cached_random_bribes = (nouns, activities)
        return _cached_random_bribes


def generate_random_bribe() -> Tuple[str, bool]:
    """Generate a random silly bribe and flag it as randomly generated"""
    nouns, activities = load_random_bribes()
    
    if random.random() < 0.5:
        return random.choice(nouns), True
    else:
        return random.choice(activities), True


def get_player_room(game_manager, game_id: str, player_id: str) -> Optional[str]:
    """Get the socket room for a specific player"""
    for sid, session in game_manager.player_sessions.items():
        if session.player_id == player_id and session.game_id == game_id:
            return sid
    return None