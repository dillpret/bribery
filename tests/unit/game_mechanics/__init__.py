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
