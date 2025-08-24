"""
Unit tests for the random bribe generation functionality
"""

import unittest
from unittest.mock import patch, MagicMock

# Import only the modules we need directly to avoid circular dependencies
from src.web.utils import generate_random_bribe, load_random_bribes
# Import Game class directly with proper path
from src.game.game import Game


class TestRandomBribeGeneration(unittest.TestCase):
    """Test the random bribe generation functionality"""

    def test_load_random_bribes(self):
        """Test that random bribes can be loaded from the file"""
        nouns, activities = load_random_bribes()
        
        # Verify we have content in both categories
        self.assertTrue(len(nouns) > 0, "Should load nouns from random_bribes.txt")
        self.assertTrue(len(activities) > 0, "Should load activities from random_bribes.txt")
        
        # Verify the content looks right (these are expected to be strings)
        for noun in nouns[:5]:  # Check just a few to save time
            self.assertIsInstance(noun, str)
            self.assertTrue(len(noun) > 0)
            
        for activity in activities[:5]:
            self.assertIsInstance(activity, str)
            self.assertTrue(len(activity) > 0)

    def test_generate_random_bribe(self):
        """Test that a random bribe can be generated"""
        bribe, is_random = generate_random_bribe()
        
        # Verify the return values
        self.assertIsInstance(bribe, str)
        self.assertTrue(len(bribe) > 0)
        self.assertTrue(is_random)  # Should always be True

    @patch('src.web.utils.load_random_bribes')
    def test_generate_random_bribe_content(self, mock_load):
        """Test that random bribes are selected from both nouns and activities"""
        # Mock the load_random_bribes function to return predictable test data
        mock_load.return_value = (
            ["Test noun 1", "Test noun 2"], 
            ["Test activity 1", "Test activity 2"]
        )
        
        # Generate multiple bribes and check they come from our test data
        for _ in range(10):  # Try multiple times to ensure we get both types
            bribe, is_random = generate_random_bribe()
            self.assertTrue(
                bribe in ["Test noun 1", "Test noun 2", "Test activity 1", "Test activity 2"],
                f"Generated bribe '{bribe}' not in expected test data"
            )
            self.assertTrue(is_random)


class TestRandomBribeGameIntegration(unittest.TestCase):
    """Test how random bribes integrate with the game mechanics"""
    
    def setUp(self):
        """Set up a test game instance"""
        self.game = Game("TEST_GAME", "HOST_ID", {
            'rounds': 3,
            'submission_time': 60,
            'voting_time': 30,
            'results_time': 5
        })
        
        # Add players
        self.game.add_player("player1", "Alice")
        self.game.add_player("player2", "Bob")
        self.game.add_player("player3", "Charlie")
        
        # Set up a round with pairings
        self.game.current_round = 1
        self.game.bribes[1] = {}
        self.game.round_pairings[1] = {
            "player1": ["player2", "player3"],
            "player2": ["player1", "player3"],
            "player3": ["player1", "player2"]
        }

    def test_random_bribe_generation(self):
        """Test that a random bribe is properly flagged"""
        bribe_text, is_random = generate_random_bribe()
        self.assertTrue(is_random)
        self.assertTrue(len(bribe_text) > 0)

    def test_voting_phase_doesnt_show_random_indicator(self):
        """Test that random bribes don't show the 'randomly generated' text during voting"""
        # Set up bribes including a random one
        self.game.bribes[1] = {
            "player1": {
                "player2": {"content": "Regular bribe", "type": "text", "is_random": False}
            },
            "player2": {
                "player1": {"content": "Random bribe", "type": "text", "is_random": True}
            }
        }
        
        # Simulate the voting phase code
        player_id = "player1"
        bribes_for_player = []
        
        # This mimics the code in the voting phase
        for submitter_id, submissions in self.game.bribes[1].items():
            if submitter_id == player_id:
                continue
            
            for target_id, bribe in submissions.items():
                if target_id == player_id:
                    bribes_for_player.append({
                        'id': f"{submitter_id}_{target_id}",
                        'content': bribe['content'],
                        'type': bribe['type'],
                        'is_random': bribe.get('is_random', False)
                    })
        
        # Check that the bribe content doesn't contain "(randomly generated)"
        self.assertEqual(len(bribes_for_player), 1)
        self.assertEqual(bribes_for_player[0]['content'], "Random bribe")
        self.assertTrue(bribes_for_player[0]['is_random'])
        self.assertNotIn("(randomly generated)", bribes_for_player[0]['content'])

    def test_results_phase_shows_random_indicator(self):
        """Test that random bribes show the 'randomly generated' text during results"""
        # Set up a random bribe
        bribe = {"content": "Random bribe", "type": "text", "is_random": True}
        
        # Simulate the results phase code
        bribe_content = bribe['content']
        if bribe.get('is_random', False):
            bribe_content += " (randomly generated)"
        
        # Check that the indicator was added
        self.assertEqual(bribe_content, "Random bribe (randomly generated)")

    def test_scoring_with_random_bribes(self):
        """Test that random bribes receive half points"""
        # Initialize the scores
        self.game.scores = {"player1": 0, "player2": 0, "player3": 0}
        
        # Test the scoring logic directly
        round_scores = {}
        
        # Simulate a vote for a regular bribe
        submitter_id = "player1"
        is_random = False
        
        if submitter_id not in round_scores:
            round_scores[submitter_id] = 0
            
        if is_random:
            round_scores[submitter_id] += 0.5  # Half point for random bribes
        else:
            round_scores[submitter_id] += 1    # Full point for player submissions
            
        # Simulate a vote for a random bribe
        submitter_id = "player2"
        is_random = True
        
        if submitter_id not in round_scores:
            round_scores[submitter_id] = 0
            
        if is_random:
            round_scores[submitter_id] += 0.5  # Half point for random bribes
        else:
            round_scores[submitter_id] += 1    # Full point for player submissions
            
        # Apply the round scores to the game scores
        for player_id, points in round_scores.items():
            self.game.scores[player_id] += points
            
        # Check the scores
        self.assertEqual(self.game.scores["player1"], 1, "Regular bribes should get 1 point")
        self.assertEqual(self.game.scores["player2"], 0.5, "Random bribes should get 0.5 points")
        self.assertEqual(self.game.scores["player3"], 0, "Player3 should have no points")
        
        # Add players
        self.game.add_player("player1", "Alice")
        self.game.add_player("player2", "Bob")
        self.game.add_player("player3", "Charlie")
        
        # Set up a round with pairings
        self.game.current_round = 1
        self.game.bribes[1] = {}
        self.game.round_pairings[1] = {
            "player1": ["player2", "player3"],
            "player2": ["player1", "player3"],
            "player3": ["player1", "player2"]
        }

    def test_missing_submissions_get_random_bribes(self):
        """Test that missing submissions are filled with random bribes"""
        # This test verifies the logic that would generate random bribes for missing submissions
        
        # Create empty bribes dict for the current round
        self.game.bribes[1] = {}
        
        # Initialize player1's bribes dict 
        self.game.bribes[1]["player1"] = {}
        
        # Add one manual submission
        self.game.bribes[1]["player1"]["player2"] = {
            'content': "Player submitted bribe",
            'type': 'text',
            'is_random': False
        }
        
        # Get player1's targets from the round pairings
        targets = self.game.round_pairings[1].get("player1", [])
        
        # Find missing submissions
        missing_submissions = []
        for target_id in targets:
            if target_id not in self.game.bribes[1]["player1"]:
                missing_submissions.append(target_id)
        
        # Verify player3 is in the missing submissions
        self.assertIn("player3", missing_submissions)
        
        # Generate random bribes for missing submissions
        for target_id in missing_submissions:
            # Generate a random bribe
            random_bribe, is_random = generate_random_bribe()
            
            # Add it to the game state
            self.game.bribes[1]["player1"][target_id] = {
                'content': random_bribe,
                'type': 'text',
                'is_random': True  # Flag it as randomly generated
            }
        
        # Verify all submissions now exist
        for target_id in targets:
            self.assertIn(target_id, self.game.bribes[1]["player1"])
        
        # Verify the original submission remains unchanged
        self.assertEqual(self.game.bribes[1]["player1"]["player2"]["content"], "Player submitted bribe")
        self.assertFalse(self.game.bribes[1]["player1"]["player2"]["is_random"])
        
        # Verify the random submission was added
        self.assertTrue(self.game.bribes[1]["player1"]["player3"]["is_random"])

    def test_scoring_with_random_bribes(self):
        """Test that random bribes receive half points"""
        # Set up bribes including random ones
        self.game.bribes[1] = {
            "player1": {
                "player2": {"content": "Regular bribe", "type": "text", "is_random": False},
                "player3": {"content": "Regular bribe", "type": "text", "is_random": False}
            },
            "player2": {
                "player1": {"content": "Random bribe", "type": "text", "is_random": True},
                "player3": {"content": "Regular bribe", "type": "text", "is_random": False}
            },
            "player3": {
                "player1": {"content": "Regular bribe", "type": "text", "is_random": False},
                "player2": {"content": "Random bribe", "type": "text", "is_random": True}
            }
        }
        
        # Set up votes
        self.game.votes[1] = {
            "player1": "player2_player1",  # player1 votes for player2's random bribe
            "player2": "player1_player2",  # player2 votes for player1's regular bribe
            "player3": "player2_player3"   # player3 votes for player2's regular bribe
        }
        
        # Initialize scores
        self.game.scores = {"player1": 0, "player2": 0, "player3": 0}
        
        # Import and call the end_voting_phase function
        from src.web.socket_handlers.game_flow import end_voting_phase
        
        # Create a mock socketio to prevent errors when emitting events
        mock_socketio = MagicMock()
        with patch('src.web.socket_handlers.game_flow.socketio', mock_socketio):
            end_voting_phase(self.game)
        
        # Check the scores - player1 should get 1 point, player2 should get 1.5 points (0.5 for random + 1 for regular)
        self.assertEqual(self.game.scores["player1"], 1, "Regular bribes should get 1 point")
        self.assertEqual(self.game.scores["player2"], 1.5, "Player2 should get 0.5 points for random bribe and 1 for regular bribe")
        self.assertEqual(self.game.scores["player3"], 0, "Player3 should have no points")

    def test_display_of_random_bribes_in_voting_phase(self):
        """Test that random bribes are not marked during voting phase but are marked during results"""
        # This test verifies that the UI doesn't show "(randomly generated)" during voting
        # Create a bribe display for voting phase
        bribe = {
            'id': 'player2_player1',
            'content': 'Random bribe',
            'type': 'text',
            'is_random': True
        }
        
        # Verify the content doesn't contain the random indicator
        self.assertNotIn('(randomly generated)', bribe['content'])
        
        # Now simulate what happens in results phase
        bribe_content = bribe['content']
        if bribe.get('is_random', False):
            bribe_content += " (randomly generated)"
        
        # Verify the content now contains the random indicator
        self.assertEqual(bribe_content, 'Random bribe (randomly generated)')
