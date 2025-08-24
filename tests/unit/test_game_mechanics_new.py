#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for core game mechanics and business logic
Tests the actual game flow, scoring, and edge cases

NOTICE: This file is now a compatibility layer that imports tests
from the game_mechanics package. New tests should be added to the
appropriate module in the game_mechanics package.
"""

# Import all test classes from the game_mechanics package
from tests.unit.game_mechanics import (
    TestRoundFlowLogic,
    TestScoringSystem,
    TestGameStateManagement,
    TestEdgeCasesAndTolerances,
    TestMultiRoundLogic,
    TestCustomPrompts
)

# This file now serves as a compatibility layer
# All tests are now maintained in the game_mechanics package
