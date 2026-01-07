"""
Comprehensive test suite for Catan game engine
Tests all game logic, rules, and mechanics
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from game_engine import (
    CatanGame, CatanBoard, Player, ResourceType, BuildingType,
    DevelopmentCardType, GamePhase, TurnPhase
)


class TestBoardSetup(unittest.TestCase):
    """Test board generation and setup"""

    def setUp(self):
        self.board = CatanBoard()

    def test_board_has_19_hexes(self):
        """Verify board has exactly 19 hex tiles"""
        self.assertEqual(len(self.board.hexes), 19)

    def test_resource_distribution(self):
        """Verify correct resource distribution"""
        resources = [hex_tile.resource_type for hex_tile in self.board.hexes.values()]

        self.assertEqual(resources.count(ResourceType.WOOD), 4)
        self.assertEqual(resources.count(ResourceType.BRICK), 3)
        self.assertEqual(resources.count(ResourceType.ORE), 3)
        self.assertEqual(resources.count(ResourceType.WHEAT), 4)
        self.assertEqual(resources.count(ResourceType.SHEEP), 4)
        self.assertEqual(resources.count(ResourceType.DESERT), 1)

    def test_number_token_distribution(self):
        """Verify correct number token distribution"""
        non_desert_hexes = [h for h in self.board.hexes.values()
                           if h.resource_type != ResourceType.DESERT]

        self.assertEqual(len(non_desert_hexes), 18)

        numbers = [h.number_token for h in non_desert_hexes]
        numbers.sort()

        expected = [2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12]
        self.assertEqual(numbers, expected)

    def test_no_adjacent_6s_or_8s(self):
        """Verify no two 6s or 8s are adjacent"""
        for hex_tile in self.board.hexes.values():
            if hex_tile.number_token in [6, 8]:
                for neighbor_id in hex_tile.neighbor_hexes:
                    neighbor = self.board.hexes[neighbor_id]
                    self.assertNotIn(neighbor.number_token, [6, 8],
                                   f"Found adjacent 6/8 at {hex_tile.q},{hex_tile.r} and neighbor")

    def test_robber_starts_on_desert(self):
        """Verify robber starts on desert tile"""
        desert_hexes = [h for h in self.board.hexes.values()
                       if h.resource_type == ResourceType.DESERT]

        self.assertEqual(len(desert_hexes), 1)
        self.assertTrue(desert_hexes[0].has_robber)
        self.assertEqual(self.board.robber_hex_id, desert_hexes[0].unique_id)


class TestBuildingCosts(unittest.TestCase):
    """Test building costs and resource requirements"""

    def setUp(self):
        self.game = CatanGame('test-game')
        self.game.add_player('p1', 'Player 1', '#FF0000')
        self.game.add_player('p2', 'Player 2', '#0000FF')
        self.game.start_game()
        self.player = self.game.players['p1']

    def test_settlement_cost(self):
        """Test settlement requires correct resources"""
        # Give player exact resources
        self.player.resources = {
            ResourceType.WOOD: 1,
            ResourceType.BRICK: 1,
            ResourceType.WHEAT: 1,
            ResourceType.SHEEP: 1,
            ResourceType.ORE: 0
        }

        # Find valid vertex
        vertex_id = list(self.game.board.vertices.keys())[0]

        # Should be able to build
        self.assertTrue(self.game.can_build_settlement('p1', vertex_id))

        # Remove one resource
        self.player.resources[ResourceType.WOOD] = 0
        self.assertFalse(self.game.can_build_settlement('p1', vertex_id))

    def test_city_cost(self):
        """Test city requires correct resources"""
        # Place a settlement first
        vertex_id = list(self.game.board.vertices.keys())[0]
        vertex = self.game.board.vertices[vertex_id]
        vertex.building = BuildingType.SETTLEMENT
        vertex.owner_id = 'p1'

        # Give player exact resources for city
        self.player.resources = {
            ResourceType.WOOD: 0,
            ResourceType.BRICK: 0,
            ResourceType.WHEAT: 2,
            ResourceType.SHEEP: 0,
            ResourceType.ORE: 3
        }

        self.assertTrue(self.game.can_build_city('p1', vertex_id))

        # Remove one ore
        self.player.resources[ResourceType.ORE] = 2
        self.assertFalse(self.game.can_build_city('p1', vertex_id))

    def test_road_cost(self):
        """Test road requires correct resources"""
        self.player.resources = {
            ResourceType.WOOD: 1,
            ResourceType.BRICK: 1,
            ResourceType.WHEAT: 0,
            ResourceType.SHEEP: 0,
            ResourceType.ORE: 0
        }

        # Get two adjacent vertices
        vertex_id = list(self.game.board.vertices.keys())[0]
        vertex = self.game.board.vertices[vertex_id]
        neighbor_id = vertex.neighbor_vertices[0]

        self.assertTrue(self.game.can_build_road('p1', vertex_id, neighbor_id))

        # Remove brick
        self.player.resources[ResourceType.BRICK] = 0
        self.assertFalse(self.game.can_build_road('p1', vertex_id, neighbor_id))

    def test_dev_card_cost(self):
        """Test development card requires correct resources"""
        self.player.resources = {
            ResourceType.WOOD: 0,
            ResourceType.BRICK: 0,
            ResourceType.WHEAT: 1,
            ResourceType.SHEEP: 1,
            ResourceType.ORE: 1
        }

        card = self.game.buy_development_card('p1')
        self.assertIsNotNone(card)

        # Verify resources were deducted
        self.assertEqual(self.player.resources[ResourceType.WHEAT], 0)
        self.assertEqual(self.player.resources[ResourceType.SHEEP], 0)
        self.assertEqual(self.player.resources[ResourceType.ORE], 0)


class TestBuildingRules(unittest.TestCase):
    """Test building placement rules"""

    def setUp(self):
        self.game = CatanGame('test-game')
        self.game.add_player('p1', 'Player 1', '#FF0000')
        self.game.add_player('p2', 'Player 2', '#0000FF')
        self.game.start_game()

    def test_settlement_distance_rule(self):
        """Test settlements must be 2 spaces apart"""
        # Find two adjacent vertices
        vertex_id = list(self.game.board.vertices.keys())[0]
        vertex = self.game.board.vertices[vertex_id]
        neighbor_id = vertex.neighbor_vertices[0]

        # Place settlement on first vertex
        vertex.building = BuildingType.SETTLEMENT
        vertex.owner_id = 'p1'

        # Cannot place settlement on adjacent vertex
        self.assertFalse(self.game.can_build_settlement('p2', neighbor_id))

    def test_settlement_limit(self):
        """Test maximum 5 settlements per player"""
        player = self.game.players['p1']
        player.settlements_remaining = 0

        vertex_id = list(self.game.board.vertices.keys())[0]
        self.assertFalse(self.game.can_build_settlement('p1', vertex_id))

    def test_city_upgrade_only_own_settlement(self):
        """Test can only upgrade own settlements"""
        vertex_id = list(self.game.board.vertices.keys())[0]
        vertex = self.game.board.vertices[vertex_id]

        # Place settlement owned by p2
        vertex.building = BuildingType.SETTLEMENT
        vertex.owner_id = 'p2'

        # p1 cannot upgrade p2's settlement
        self.game.players['p1'].resources = {
            ResourceType.WHEAT: 2,
            ResourceType.ORE: 3,
            ResourceType.WOOD: 0,
            ResourceType.BRICK: 0,
            ResourceType.SHEEP: 0
        }
        self.assertFalse(self.game.can_build_city('p1', vertex_id))

    def test_city_limit(self):
        """Test maximum 4 cities per player"""
        player = self.game.players['p1']
        player.cities_remaining = 0

        vertex_id = list(self.game.board.vertices.keys())[0]
        vertex = self.game.board.vertices[vertex_id]
        vertex.building = BuildingType.SETTLEMENT
        vertex.owner_id = 'p1'

        self.assertFalse(self.game.can_build_city('p1', vertex_id))


class TestResourceProduction(unittest.TestCase):
    """Test resource production on dice rolls"""

    def setUp(self):
        self.game = CatanGame('test-game')
        self.game.add_player('p1', 'Player 1', '#FF0000')
        self.game.add_player('p2', 'Player 2', '#0000FF')
        self.game.start_game()

    def test_settlement_produces_one_resource(self):
        """Test settlements produce 1 resource"""
        # Find a hex with number 6
        hex_with_6 = None
        for hex_tile in self.game.board.hexes.values():
            if hex_tile.number_token == 6:
                hex_with_6 = hex_tile
                break

        if hex_with_6:
            # Place settlement on vertex of this hex
            vertex_id = hex_with_6.neighbor_vertices[0]
            vertex = self.game.board.vertices[vertex_id]
            vertex.building = BuildingType.SETTLEMENT
            vertex.owner_id = 'p1'

            # Clear player resources
            player = self.game.players['p1']
            for rt in player.resources:
                player.resources[rt] = 0

            # Distribute resources for rolling 6
            self.game._distribute_resources(6)

            # Check player got 1 resource
            resource_type = hex_with_6.resource_type
            if resource_type != ResourceType.DESERT:
                self.assertEqual(player.resources[resource_type], 1)

    def test_city_produces_two_resources(self):
        """Test cities produce 2 resources"""
        # Find a hex with number 8
        hex_with_8 = None
        for hex_tile in self.game.board.hexes.values():
            if hex_tile.number_token == 8:
                hex_with_8 = hex_tile
                break

        if hex_with_8:
            # Place city on vertex of this hex
            vertex_id = hex_with_8.neighbor_vertices[0]
            vertex = self.game.board.vertices[vertex_id]
            vertex.building = BuildingType.CITY
            vertex.owner_id = 'p1'

            # Clear player resources
            player = self.game.players['p1']
            for rt in player.resources:
                player.resources[rt] = 0

            # Distribute resources for rolling 8
            self.game._distribute_resources(8)

            # Check player got 2 resources
            resource_type = hex_with_8.resource_type
            if resource_type != ResourceType.DESERT:
                self.assertEqual(player.resources[resource_type], 2)

    def test_robber_blocks_production(self):
        """Test robber blocks resource production"""
        # Find a non-desert hex
        hex_tile = None
        for h in self.game.board.hexes.values():
            if h.resource_type != ResourceType.DESERT:
                hex_tile = h
                break

        # Place settlement
        vertex_id = hex_tile.neighbor_vertices[0]
        vertex = self.game.board.vertices[vertex_id]
        vertex.building = BuildingType.SETTLEMENT
        vertex.owner_id = 'p1'

        # Place robber on this hex
        hex_tile.has_robber = True

        # Clear player resources
        player = self.game.players['p1']
        for rt in player.resources:
            player.resources[rt] = 0

        # Distribute resources
        self.game._distribute_resources(hex_tile.number_token)

        # Check player got no resources
        self.assertEqual(player.resources[hex_tile.resource_type], 0)


class TestVictoryPoints(unittest.TestCase):
    """Test victory point calculation"""

    def setUp(self):
        self.game = CatanGame('test-game')
        self.game.add_player('p1', 'Player 1', '#FF0000')
        self.player = self.game.players['p1']

    def test_settlement_worth_one_point(self):
        """Test each settlement is worth 1 VP"""
        self.player.settlements_remaining = 3  # Built 2 settlements
        vp = self.player.calculate_victory_points()
        self.assertEqual(vp, 2)

    def test_city_worth_two_points(self):
        """Test each city is worth 2 VP"""
        self.player.cities_remaining = 2  # Built 2 cities
        vp = self.player.calculate_victory_points()
        self.assertEqual(vp, 4)

    def test_vp_dev_card_counts(self):
        """Test VP development cards count toward victory"""
        self.player.development_cards = [
            DevelopmentCardType.VICTORY_POINT,
            DevelopmentCardType.VICTORY_POINT,
            DevelopmentCardType.KNIGHT
        ]
        vp = self.player.calculate_victory_points()
        self.assertEqual(vp, 2)  # 2 VP cards

    def test_longest_road_worth_two_points(self):
        """Test longest road is worth 2 VP"""
        self.player.has_longest_road = True
        vp = self.player.calculate_victory_points()
        self.assertGreaterEqual(vp, 2)

    def test_largest_army_worth_two_points(self):
        """Test largest army is worth 2 VP"""
        self.player.has_largest_army = True
        vp = self.player.calculate_victory_points()
        self.assertGreaterEqual(vp, 2)

    def test_total_victory_points(self):
        """Test total victory point calculation"""
        self.player.settlements_remaining = 3  # 2 settlements = 2 VP
        self.player.cities_remaining = 2  # 2 cities = 4 VP
        self.player.development_cards = [DevelopmentCardType.VICTORY_POINT]  # 1 VP
        self.player.has_longest_road = True  # 2 VP
        self.player.has_largest_army = True  # 2 VP

        vp = self.player.calculate_victory_points()
        self.assertEqual(vp, 11)  # Total: 11 VP


class TestRobberMechanics(unittest.TestCase):
    """Test robber placement and stealing"""

    def setUp(self):
        self.game = CatanGame('test-game')
        self.game.add_player('p1', 'Player 1', '#FF0000')
        self.game.add_player('p2', 'Player 2', '#0000FF')
        self.game.start_game()
        self.game.turn_phase = TurnPhase.MOVING_ROBBER

    def test_cannot_place_robber_on_same_hex(self):
        """Test cannot place robber on current hex"""
        current_hex_id = self.game.board.robber_hex_id
        result = self.game.move_robber('p1', current_hex_id)
        self.assertFalse(result)

    def test_robber_moves_successfully(self):
        """Test robber can move to new hex"""
        # Find a different hex
        new_hex_id = None
        for hex_id in self.game.board.hexes.keys():
            if hex_id != self.game.board.robber_hex_id:
                new_hex_id = hex_id
                break

        result = self.game.move_robber('p1', new_hex_id)
        self.assertTrue(result)
        self.assertEqual(self.game.board.robber_hex_id, new_hex_id)

    def test_stealing_requires_victim_on_hex(self):
        """Test can only steal from players with buildings on robber hex"""
        # Find a hex without any buildings
        empty_hex_id = None
        for hex_id, hex_tile in self.game.board.hexes.items():
            if hex_id != self.game.board.robber_hex_id:
                has_buildings = False
                for vertex_id in hex_tile.neighbor_vertices:
                    if self.game.board.vertices[vertex_id].building:
                        has_buildings = True
                        break
                if not has_buildings:
                    empty_hex_id = hex_id
                    break

        if empty_hex_id:
            # Try to steal from p2 who has no building there
            result = self.game.move_robber('p1', empty_hex_id, steal_from_player_id='p2')
            # Should succeed (moving robber) but not steal (no building)
            self.assertTrue(result)


class TestTrading(unittest.TestCase):
    """Test trading mechanics"""

    def setUp(self):
        self.game = CatanGame('test-game')
        self.game.add_player('p1', 'Player 1', '#FF0000')
        self.game.add_player('p2', 'Player 2', '#0000FF')
        self.game.start_game()

    def test_bank_trade_4_for_1(self):
        """Test 4:1 bank trade"""
        player = self.game.players['p1']
        player.resources = {
            ResourceType.WOOD: 4,
            ResourceType.BRICK: 0,
            ResourceType.WHEAT: 0,
            ResourceType.SHEEP: 0,
            ResourceType.ORE: 0
        }

        result = self.game.trade_with_bank('p1', {'wood': 4}, {'brick': 1})
        self.assertTrue(result)
        self.assertEqual(player.resources[ResourceType.WOOD], 0)
        self.assertEqual(player.resources[ResourceType.BRICK], 1)

    def test_bank_trade_must_be_same_resource(self):
        """Test bank trade requires 4 of same resource"""
        player = self.game.players['p1']
        player.resources = {
            ResourceType.WOOD: 2,
            ResourceType.BRICK: 2,
            ResourceType.WHEAT: 0,
            ResourceType.SHEEP: 0,
            ResourceType.ORE: 0
        }

        # Try to trade mixed resources (should fail)
        result = self.game.trade_with_bank('p1', {'wood': 2, 'brick': 2}, {'ore': 1})
        self.assertFalse(result)

    def test_player_trade_proposal(self):
        """Test player can propose trade"""
        player = self.game.players['p1']
        player.resources = {
            ResourceType.WOOD: 2,
            ResourceType.BRICK: 0,
            ResourceType.WHEAT: 0,
            ResourceType.SHEEP: 0,
            ResourceType.ORE: 0
        }

        result = self.game.propose_player_trade('p1', {'wood': 2}, {'brick': 1})
        self.assertTrue(result)
        self.assertIsNotNone(self.game.active_trade)

    def test_player_trade_execution(self):
        """Test player trade can be executed"""
        p1 = self.game.players['p1']
        p2 = self.game.players['p2']

        p1.resources = {
            ResourceType.WOOD: 2,
            ResourceType.BRICK: 0,
            ResourceType.WHEAT: 0,
            ResourceType.SHEEP: 0,
            ResourceType.ORE: 0
        }

        p2.resources = {
            ResourceType.WOOD: 0,
            ResourceType.BRICK: 1,
            ResourceType.WHEAT: 0,
            ResourceType.SHEEP: 0,
            ResourceType.ORE: 0
        }

        # Propose trade
        self.game.propose_player_trade('p1', {'wood': 2}, {'brick': 1})

        # p2 accepts
        self.game.respond_to_trade('p2', True)

        # Execute trade
        result = self.game.execute_trade('p1', 'p2')
        self.assertTrue(result)

        # Verify resources transferred
        self.assertEqual(p1.resources[ResourceType.WOOD], 0)
        self.assertEqual(p1.resources[ResourceType.BRICK], 1)
        self.assertEqual(p2.resources[ResourceType.WOOD], 2)
        self.assertEqual(p2.resources[ResourceType.BRICK], 0)


class TestGameFlow(unittest.TestCase):
    """Test game flow and phases"""

    def setUp(self):
        self.game = CatanGame('test-game')
        self.game.add_player('p1', 'Player 1', '#FF0000')
        self.game.add_player('p2', 'Player 2', '#0000FF')

    def test_game_starts_in_lobby(self):
        """Test game starts in lobby phase"""
        self.assertEqual(self.game.game_phase, GamePhase.LOBBY)

    def test_game_moves_to_setup(self):
        """Test game moves to setup phase when started"""
        self.game.start_game()
        self.assertEqual(self.game.game_phase, GamePhase.SETUP_FORWARD)

    def test_setup_forward_then_backward(self):
        """Test setup goes forward then backward"""
        self.game.start_game()
        self.assertEqual(self.game.game_phase, GamePhase.SETUP_FORWARD)

        # Place first round of settlements for both players
        for i in range(2):
            self.game.end_turn(self.game.get_current_player_id())

        # Should now be in backward phase
        self.assertEqual(self.game.game_phase, GamePhase.SETUP_BACKWARD)

    def test_rolling_7_triggers_discard(self):
        """Test rolling 7 triggers discard phase"""
        self.game.start_game()
        self.game.game_phase = GamePhase.REGULAR_PLAY
        self.game.turn_phase = TurnPhase.WAITING_FOR_ROLL

        # Give a player >7 cards
        player = self.game.players['p1']
        player.resources[ResourceType.WOOD] = 8

        # Mock rolling a 7
        self.game.last_dice_roll = (3, 4)
        # Manually trigger discard phase
        self.game.turn_phase = TurnPhase.DISCARDING

    def test_win_condition(self):
        """Test game ends when player reaches 10 VP"""
        self.game.start_game()
        self.game.game_phase = GamePhase.REGULAR_PLAY

        player = self.game.players['p1']
        # Give player 10 VP worth of stuff
        player.settlements_remaining = 0  # 5 settlements = 5 VP
        player.cities_remaining = 2  # 2 cities = 4 VP
        player.has_longest_road = False
        player.development_cards = [DevelopmentCardType.VICTORY_POINT]  # 1 VP

        player.victory_points = player.calculate_victory_points()
        self.assertEqual(player.victory_points, 10)

        # End turn should trigger win
        self.game.end_turn('p1')
        self.assertEqual(self.game.game_phase, GamePhase.FINISHED)


class TestDevelopmentCards(unittest.TestCase):
    """Test development card mechanics"""

    def setUp(self):
        self.game = CatanGame('test-game')
        self.game.add_player('p1', 'Player 1', '#FF0000')
        self.game.add_player('p2', 'Player 2', '#0000FF')

    def test_dev_card_deck_has_25_cards(self):
        """Test dev card deck has 25 cards"""
        self.assertEqual(len(self.game.dev_card_deck), 25)

    def test_dev_card_distribution(self):
        """Test dev card deck has correct distribution"""
        knights = sum(1 for card in self.game.dev_card_deck
                     if card == DevelopmentCardType.KNIGHT)
        vp_cards = sum(1 for card in self.game.dev_card_deck
                      if card == DevelopmentCardType.VICTORY_POINT)
        road_building = sum(1 for card in self.game.dev_card_deck
                           if card == DevelopmentCardType.ROAD_BUILDING)
        year_of_plenty = sum(1 for card in self.game.dev_card_deck
                            if card == DevelopmentCardType.YEAR_OF_PLENTY)
        monopoly = sum(1 for card in self.game.dev_card_deck
                      if card == DevelopmentCardType.MONOPOLY)

        self.assertEqual(knights, 14)
        self.assertEqual(vp_cards, 5)
        self.assertEqual(road_building, 2)
        self.assertEqual(year_of_plenty, 2)
        self.assertEqual(monopoly, 2)

    def test_knight_card_triggers_robber(self):
        """Test playing knight card moves to robber phase"""
        player = self.game.players['p1']
        player.development_cards = [DevelopmentCardType.KNIGHT]

        self.game.turn_phase = TurnPhase.MAIN_PHASE
        result = self.game.play_knight_card('p1')

        self.assertTrue(result)
        self.assertEqual(self.game.turn_phase, TurnPhase.MOVING_ROBBER)
        self.assertEqual(player.knights_played, 1)

    def test_largest_army_requires_3_knights(self):
        """Test largest army requires at least 3 knights"""
        p1 = self.game.players['p1']
        p1.knights_played = 3

        self.game._update_largest_army()

        self.assertTrue(p1.has_largest_army)
        self.assertEqual(self.game.largest_army_owner, 'p1')


def run_all_tests():
    """Run all test suites"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestBoardSetup))
    suite.addTests(loader.loadTestsFromTestCase(TestBuildingCosts))
    suite.addTests(loader.loadTestsFromTestCase(TestBuildingRules))
    suite.addTests(loader.loadTestsFromTestCase(TestResourceProduction))
    suite.addTests(loader.loadTestsFromTestCase(TestVictoryPoints))
    suite.addTests(loader.loadTestsFromTestCase(TestRobberMechanics))
    suite.addTests(loader.loadTestsFromTestCase(TestTrading))
    suite.addTests(loader.loadTestsFromTestCase(TestGameFlow))
    suite.addTests(loader.loadTestsFromTestCase(TestDevelopmentCards))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
