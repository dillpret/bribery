#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Game mechanics test package - common imports
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'src'))

from game.game import Game
from game.game_manager import GameManager

# Import test classes for re-export
from .test_round_flow import TestRoundFlowLogic
from .test_scoring import TestScoringSystem
from .test_state_management import TestGameStateManagement
from .test_edge_cases import TestEdgeCasesAndTolerances
from .test_multi_round import TestMultiRoundLogic

# Custom prompts isn't exported since we don't have that test class yet
# from .test_custom_prompts import TestCustomPrompts

__all__ = [
    'TestRoundFlowLogic',
    'TestScoringSystem',
    'TestGameStateManagement', 
    'TestEdgeCasesAndTolerances',
    'TestMultiRoundLogic',
    # 'TestCustomPrompts'
]
