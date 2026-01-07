"""
Settlers of Catan Game Engine
Complete implementation of Catan rules for multiplayer online play
"""

import random
import math
from enum import Enum
from typing import Dict, List, Tuple, Optional, Set
from collections import defaultdict
from dataclasses import dataclass, field


class ResourceType(Enum):
    """Resource types in Catan"""
    WOOD = "wood"
    BRICK = "brick"
    WHEAT = "wheat"
    SHEEP = "sheep"
    ORE = "ore"
    DESERT = "desert"


class BuildingType(Enum):
    """Building types"""
    SETTLEMENT = "settlement"
    CITY = "city"


class DevelopmentCardType(Enum):
    """Development card types"""
    KNIGHT = "knight"
    VICTORY_POINT = "victory_point"
    ROAD_BUILDING = "road_building"
    YEAR_OF_PLENTY = "year_of_plenty"
    MONOPOLY = "monopoly"


class GamePhase(Enum):
    """Game phases"""
    LOBBY = "lobby"
    SETUP_FORWARD = "setup_forward"  # Players 1-4 place first settlement+road
    SETUP_BACKWARD = "setup_backward"  # Players 4-1 place second settlement+road
    REGULAR_PLAY = "regular_play"
    FINISHED = "finished"


class TurnPhase(Enum):
    """Phases within a player's turn"""
    WAITING_FOR_ROLL = "waiting_for_roll"
    ROLLING = "rolling"
    DISCARDING = "discarding"  # When 7 is rolled and players have >7 cards
    MOVING_ROBBER = "moving_robber"
    STEALING = "stealing"
    MAIN_PHASE = "main_phase"  # Build, trade, play dev cards
    ENDED = "ended"


@dataclass
class HexTile:
    """Represents a hex tile on the board"""
    q: int  # Axial coordinate
    r: int  # Axial coordinate
    resource_type: ResourceType
    number_token: int  # 2-12, -1 for desert
    has_robber: bool = False
    unique_id: Optional[int] = None
    neighbor_hexes: List[int] = field(default_factory=list)
    neighbor_vertices: List[int] = field(default_factory=list)

    def __hash__(self):
        return hash((self.q, self.r))


@dataclass
class Vertex:
    """Represents a vertex (intersection) where buildings can be placed"""
    q: int  # Axial coordinate
    r: int  # Axial coordinate
    unique_id: Optional[int] = None
    owner_id: Optional[str] = None
    building: Optional[BuildingType] = None
    neighbor_vertices: List[int] = field(default_factory=list)
    neighbor_hexes: List[int] = field(default_factory=list)
    roads: Dict[int, str] = field(default_factory=dict)  # {other_vertex_id: owner_id}

    def __hash__(self):
        return hash((self.q, self.r))


@dataclass
class Player:
    """Represents a player in the game"""
    player_id: str
    name: str
    color: str
    resources: Dict[ResourceType, int] = field(default_factory=lambda: {
        ResourceType.WOOD: 0,
        ResourceType.BRICK: 0,
        ResourceType.WHEAT: 0,
        ResourceType.SHEEP: 0,
        ResourceType.ORE: 0
    })
    development_cards: List[DevelopmentCardType] = field(default_factory=list)
    development_cards_played: List[DevelopmentCardType] = field(default_factory=list)
    knights_played: int = 0
    roads_remaining: int = 15
    settlements_remaining: int = 5
    cities_remaining: int = 4
    victory_points: int = 0
    longest_road_length: int = 0
    has_longest_road: bool = False
    has_largest_army: bool = False
    ready: bool = False

    def get_total_resource_count(self) -> int:
        """Get total number of resource cards"""
        return sum(count for rt, count in self.resources.items()
                  if rt != ResourceType.DESERT)

    def get_development_card_count(self) -> int:
        """Get number of development cards (excluding played ones)"""
        return len(self.development_cards)

    def calculate_victory_points(self) -> int:
        """Calculate total victory points"""
        points = 0
        # Buildings
        points += (5 - self.settlements_remaining)  # Each settlement = 1 VP
        points += (4 - self.cities_remaining) * 2  # Each city = 2 VP
        # Development cards - VP cards count from hand (never played)
        points += sum(1 for card in self.development_cards
                     if card == DevelopmentCardType.VICTORY_POINT)
        # Special cards
        if self.has_longest_road:
            points += 2
        if self.has_largest_army:
            points += 2
        return points


class CatanBoard:
    """Manages the Catan game board"""

    def __init__(self):
        self.hexes: Dict[int, HexTile] = {}
        self.vertices: Dict[int, Vertex] = {}
        self.robber_hex_id: Optional[int] = None
        self._generate_board()

    def _generate_board(self):
        """Generate the standard Catan board layout"""
        # Generate hex grid
        hex_cells = []
        vertex_cells = []

        hex_radius = 5
        for q in range(-hex_radius, hex_radius + 1):
            for r in range(max(-hex_radius, -q - hex_radius),
                          min(hex_radius, -q + hex_radius) + 1):
                if (q - r) % 3 == 0 and (2 * q + r) % 3 == 0:  # Hex point
                    hex_cells.append(HexTile(q, r, ResourceType.DESERT, -1))
                else:
                    vertex_cells.append(Vertex(q, r))

        # Filter to get proper board shape (19 hexes for standard Catan)
        hex_cells = [h for h in hex_cells
                    if len([v for v in vertex_cells if self._is_neighbor(h, v)]) == 6]
        vertex_cells = [v for v in vertex_cells
                       if len([h for h in hex_cells if self._is_neighbor(h, v)]) > 0]

        # Verify we have exactly 19 hexes
        assert len(hex_cells) == 19, f"Expected 19 hex tiles, got {len(hex_cells)}"

        # Assign unique IDs
        for i, node in enumerate(vertex_cells + hex_cells):
            node.unique_id = i

        # Calculate neighbors
        for vertex in vertex_cells:
            vertex.neighbor_vertices = sorted([v.unique_id for v in vertex_cells
                                              if self._is_direct_neighbor(vertex, v)])
            vertex.neighbor_hexes = sorted([h.unique_id for h in hex_cells
                                           if self._is_neighbor(vertex, h)])

        for hex_cell in hex_cells:
            vertex_neighbors = [v for v in vertex_cells if self._is_neighbor(hex_cell, v)]
            neighbor_hexes = []
            for vn in vertex_neighbors:
                neighbor_hexes.extend([h for h in hex_cells if self._is_neighbor(vn, h)])
            hex_cell.neighbor_hexes = sorted(list(set([h.unique_id for h in neighbor_hexes
                                                       if h.unique_id != hex_cell.unique_id])))
            hex_cell.neighbor_vertices = sorted([v.unique_id for v in vertex_neighbors])

        # Convert to dicts
        self.hexes = {h.unique_id: h for h in hex_cells}
        self.vertices = {v.unique_id: v for v in vertex_cells}

        # Assign resources and number tokens
        self._setup_resources()
        self._assign_number_tokens()

    def _is_neighbor(self, cell1, cell2) -> bool:
        """Check if two cells are neighbors"""
        return abs(cell1.q - cell2.q) <= 1 and abs(cell1.r - cell2.r) <= 1

    def _is_direct_neighbor(self, v1: Vertex, v2: Vertex) -> bool:
        """Check if two vertices are direct neighbors (share an edge)"""
        diffs = [(1, 0), (0, 1), (-1, 0), (0, -1), (1, -1), (-1, 1)]
        diff = (v1.q - v2.q, v1.r - v2.r)
        return diff in diffs

    def _setup_resources(self):
        """Assign resources to hex tiles"""
        resources = [
            ResourceType.WOOD, ResourceType.WOOD, ResourceType.WOOD, ResourceType.WOOD,
            ResourceType.BRICK, ResourceType.BRICK, ResourceType.BRICK,
            ResourceType.ORE, ResourceType.ORE, ResourceType.ORE,
            ResourceType.WHEAT, ResourceType.WHEAT, ResourceType.WHEAT, ResourceType.WHEAT,
            ResourceType.SHEEP, ResourceType.SHEEP, ResourceType.SHEEP, ResourceType.SHEEP,
            ResourceType.DESERT
        ]
        random.shuffle(resources)

        for hex_tile, resource in zip(self.hexes.values(), resources):
            hex_tile.resource_type = resource
            if resource == ResourceType.DESERT:
                hex_tile.has_robber = True
                self.robber_hex_id = hex_tile.unique_id

    def _assign_number_tokens(self):
        """Assign number tokens ensuring no adjacent 6s or 8s"""
        number_tokens = [2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12]
        non_desert_hexes = [h for h in self.hexes.values()
                           if h.resource_type != ResourceType.DESERT]

        max_attempts = 1000
        for attempt in range(max_attempts):
            random.shuffle(number_tokens)

            # Assign numbers
            for hex_tile, number in zip(non_desert_hexes, number_tokens):
                hex_tile.number_token = number

            # Check if valid (no adjacent 6s or 8s)
            if self._is_valid_number_distribution():
                print(f"Valid number distribution found after {attempt + 1} attempts")
                return

        raise Exception(f"Could not create valid number distribution after {max_attempts} attempts")

    def _is_valid_number_distribution(self) -> bool:
        """Check if no 6s or 8s are adjacent"""
        for hex_tile in self.hexes.values():
            if hex_tile.number_token in [6, 8]:
                for neighbor_id in hex_tile.neighbor_hexes:
                    if self.hexes[neighbor_id].number_token in [6, 8]:
                        return False
        return True

    def get_hex_coordinates(self, q: int, r: int) -> Tuple[float, float]:
        """Convert axial coordinates to pixel coordinates for rendering"""
        sf = 30.0  # Scale factor
        x = (3/2 * q) * sf
        y = (math.sqrt(3)/2 * q + math.sqrt(3) * r) * sf
        return x, y


class CatanGame:
    """Main game state and logic"""

    def __init__(self, game_id: str, max_players: int = 4):
        self.game_id = game_id
        self.max_players = max_players
        self.players: Dict[str, Player] = {}
        self.player_order: List[str] = []
        self.current_player_index: int = 0
        self.board = CatanBoard()

        # Game state
        self.game_phase = GamePhase.LOBBY
        self.turn_phase = TurnPhase.WAITING_FOR_ROLL
        self.setup_placements: int = 0  # Track setup phase progress

        # Development cards deck
        self.dev_card_deck: List[DevelopmentCardType] = self._create_dev_card_deck()
        random.shuffle(self.dev_card_deck)

        # Bank resources
        self.bank_resources: Dict[ResourceType, int] = {
            ResourceType.WOOD: 19,
            ResourceType.BRICK: 19,
            ResourceType.WHEAT: 19,
            ResourceType.SHEEP: 19,
            ResourceType.ORE: 19
        }

        # Special cards
        self.longest_road_owner: Optional[str] = None
        self.largest_army_owner: Optional[str] = None

        # Trade state
        self.active_trade: Optional[Dict] = None

        # Last dice roll
        self.last_dice_roll: Optional[Tuple[int, int]] = None

    def _create_dev_card_deck(self) -> List[DevelopmentCardType]:
        """Create the development card deck"""
        deck = []
        deck.extend([DevelopmentCardType.KNIGHT] * 14)
        deck.extend([DevelopmentCardType.VICTORY_POINT] * 5)
        deck.extend([DevelopmentCardType.ROAD_BUILDING] * 2)
        deck.extend([DevelopmentCardType.YEAR_OF_PLENTY] * 2)
        deck.extend([DevelopmentCardType.MONOPOLY] * 2)
        return deck

    def add_player(self, player_id: str, name: str, color: str) -> bool:
        """Add a player to the game"""
        if len(self.players) >= self.max_players:
            return False
        if player_id in self.players:
            return False

        self.players[player_id] = Player(player_id, name, color)
        return True

    def remove_player(self, player_id: str) -> bool:
        """Remove a player from the game"""
        if player_id in self.players:
            del self.players[player_id]
            if player_id in self.player_order:
                self.player_order.remove(player_id)
            return True
        return False

    def start_game(self) -> bool:
        """Start the game (move from lobby to setup phase)"""
        if len(self.players) < 2:
            return False

        self.player_order = list(self.players.keys())
        random.shuffle(self.player_order)
        self.current_player_index = 0
        self.game_phase = GamePhase.SETUP_FORWARD
        self.turn_phase = TurnPhase.MAIN_PHASE
        return True

    def get_current_player_id(self) -> Optional[str]:
        """Get the current player's ID"""
        if not self.player_order:
            return None
        return self.player_order[self.current_player_index]

    def get_current_player(self) -> Optional[Player]:
        """Get the current player"""
        player_id = self.get_current_player_id()
        return self.players.get(player_id) if player_id else None

    def roll_dice(self, player_id: str) -> Optional[Tuple[int, int]]:
        """Roll the dice"""
        if self.get_current_player_id() != player_id:
            return None
        if self.turn_phase != TurnPhase.WAITING_FOR_ROLL:
            return None

        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6)
        total = dice1 + dice2
        self.last_dice_roll = (dice1, dice2)

        if total == 7:
            # Check if anyone needs to discard
            needs_discard = any(p.get_total_resource_count() > 7
                              for p in self.players.values())
            if needs_discard:
                self.turn_phase = TurnPhase.DISCARDING
            else:
                self.turn_phase = TurnPhase.MOVING_ROBBER
        else:
            # Distribute resources
            self._distribute_resources(total)
            self.turn_phase = TurnPhase.MAIN_PHASE

        return (dice1, dice2)

    def _distribute_resources(self, dice_value: int):
        """Distribute resources based on dice roll"""
        # Find all hexes with the rolled number
        for hex_tile in self.board.hexes.values():
            if hex_tile.number_token == dice_value and not hex_tile.has_robber:
                resource_type = hex_tile.resource_type
                if resource_type == ResourceType.DESERT:
                    continue

                # Find all settlements/cities on this hex
                for vertex_id in hex_tile.neighbor_vertices:
                    vertex = self.board.vertices[vertex_id]
                    if vertex.building and vertex.owner_id:
                        player = self.players[vertex.owner_id]

                        # Determine resource amount (1 for settlement, 2 for city)
                        amount = 1 if vertex.building == BuildingType.SETTLEMENT else 2

                        # Check if bank has enough resources
                        if self.bank_resources[resource_type] >= amount:
                            player.resources[resource_type] += amount
                            self.bank_resources[resource_type] -= amount
                        else:
                            # Give what's available
                            available = self.bank_resources[resource_type]
                            player.resources[resource_type] += available
                            self.bank_resources[resource_type] = 0

    def can_build_settlement(self, player_id: str, vertex_id: int) -> bool:
        """Check if player can build a settlement at the given vertex"""
        player = self.players.get(player_id)
        if not player:
            return False

        vertex = self.board.vertices.get(vertex_id)
        if not vertex:
            return False

        # Check if vertex is already occupied
        if vertex.building is not None:
            return False

        # Check distance rule (no settlements on adjacent vertices)
        for neighbor_id in vertex.neighbor_vertices:
            neighbor = self.board.vertices[neighbor_id]
            if neighbor.building is not None:
                return False

        # During setup, can build anywhere that's valid
        if self.game_phase in [GamePhase.SETUP_FORWARD, GamePhase.SETUP_BACKWARD]:
            return True

        # During regular play, must be connected to player's road network
        if not self._is_connected_to_road(player_id, vertex_id):
            return False

        # Check resources
        if (player.resources[ResourceType.WOOD] >= 1 and
            player.resources[ResourceType.BRICK] >= 1 and
            player.resources[ResourceType.WHEAT] >= 1 and
            player.resources[ResourceType.SHEEP] >= 1 and
            player.settlements_remaining > 0):
            return True

        return False

    def build_settlement(self, player_id: str, vertex_id: int) -> bool:
        """Build a settlement"""
        if not self.can_build_settlement(player_id, vertex_id):
            return False

        player = self.players[player_id]
        vertex = self.board.vertices[vertex_id]

        # Place settlement
        vertex.building = BuildingType.SETTLEMENT
        vertex.owner_id = player_id
        player.settlements_remaining -= 1

        # Deduct resources (not during setup)
        if self.game_phase == GamePhase.REGULAR_PLAY:
            player.resources[ResourceType.WOOD] -= 1
            player.resources[ResourceType.BRICK] -= 1
            player.resources[ResourceType.WHEAT] -= 1
            player.resources[ResourceType.SHEEP] -= 1

            self.bank_resources[ResourceType.WOOD] += 1
            self.bank_resources[ResourceType.BRICK] += 1
            self.bank_resources[ResourceType.WHEAT] += 1
            self.bank_resources[ResourceType.SHEEP] += 1

        # During setup backward, collect resources from adjacent hexes
        if self.game_phase == GamePhase.SETUP_BACKWARD:
            for hex_id in vertex.neighbor_hexes:
                hex_tile = self.board.hexes[hex_id]
                if hex_tile.resource_type != ResourceType.DESERT:
                    if self.bank_resources[hex_tile.resource_type] > 0:
                        player.resources[hex_tile.resource_type] += 1
                        self.bank_resources[hex_tile.resource_type] -= 1

        # Update victory points
        player.victory_points = player.calculate_victory_points()

        return True

    def can_build_city(self, player_id: str, vertex_id: int) -> bool:
        """Check if player can upgrade to a city"""
        player = self.players.get(player_id)
        if not player:
            return False

        vertex = self.board.vertices.get(vertex_id)
        if not vertex:
            return False

        # Must have a settlement owned by this player
        if vertex.building != BuildingType.SETTLEMENT or vertex.owner_id != player_id:
            return False

        # Check resources
        if (player.resources[ResourceType.WHEAT] >= 2 and
            player.resources[ResourceType.ORE] >= 3 and
            player.cities_remaining > 0):
            return True

        return False

    def build_city(self, player_id: str, vertex_id: int) -> bool:
        """Upgrade a settlement to a city"""
        if not self.can_build_city(player_id, vertex_id):
            return False

        player = self.players[player_id]
        vertex = self.board.vertices[vertex_id]

        # Upgrade to city
        vertex.building = BuildingType.CITY
        player.cities_remaining -= 1
        player.settlements_remaining += 1  # Settlement piece goes back

        # Deduct resources
        player.resources[ResourceType.WHEAT] -= 2
        player.resources[ResourceType.ORE] -= 3

        self.bank_resources[ResourceType.WHEAT] += 2
        self.bank_resources[ResourceType.ORE] += 3

        # Update victory points
        player.victory_points = player.calculate_victory_points()

        return True

    def can_build_road(self, player_id: str, vertex1_id: int, vertex2_id: int) -> bool:
        """Check if player can build a road"""
        player = self.players.get(player_id)
        if not player:
            return False

        vertex1 = self.board.vertices.get(vertex1_id)
        vertex2 = self.board.vertices.get(vertex2_id)

        if not vertex1 or not vertex2:
            return False

        # Check if vertices are neighbors
        if vertex2_id not in vertex1.neighbor_vertices:
            return False

        # Check if road already exists
        if vertex2_id in vertex1.roads:
            return False

        # During setup or regular play, must connect to player's network
        if self.game_phase != GamePhase.REGULAR_PLAY:
            # During setup, must connect to the settlement just placed
            # (This is handled by the caller)
            return True

        # Must connect to player's road or building
        connects_to_network = False

        # Check if either vertex has player's building
        if vertex1.owner_id == player_id or vertex2.owner_id == player_id:
            connects_to_network = True

        # Check if either vertex has player's road
        for v_id in [vertex1_id, vertex2_id]:
            vertex = self.board.vertices[v_id]
            for road_owner in vertex.roads.values():
                if road_owner == player_id:
                    connects_to_network = True
                    break

        if not connects_to_network:
            return False

        # Check resources (not during setup)
        if self.game_phase == GamePhase.REGULAR_PLAY:
            if (player.resources[ResourceType.WOOD] >= 1 and
                player.resources[ResourceType.BRICK] >= 1 and
                player.roads_remaining > 0):
                return True
            return False

        return player.roads_remaining > 0

    def build_road(self, player_id: str, vertex1_id: int, vertex2_id: int) -> bool:
        """Build a road between two vertices"""
        if not self.can_build_road(player_id, vertex1_id, vertex2_id):
            return False

        player = self.players[player_id]
        vertex1 = self.board.vertices[vertex1_id]
        vertex2 = self.board.vertices[vertex2_id]

        # Build road
        vertex1.roads[vertex2_id] = player_id
        vertex2.roads[vertex1_id] = player_id
        player.roads_remaining -= 1

        # Deduct resources (not during setup)
        if self.game_phase == GamePhase.REGULAR_PLAY:
            player.resources[ResourceType.WOOD] -= 1
            player.resources[ResourceType.BRICK] -= 1

            self.bank_resources[ResourceType.WOOD] += 1
            self.bank_resources[ResourceType.BRICK] += 1

        # Update longest road
        self._update_longest_road()

        return True

    def _is_connected_to_road(self, player_id: str, vertex_id: int) -> bool:
        """Check if vertex is connected to player's road network"""
        vertex = self.board.vertices[vertex_id]

        # Check adjacent roads
        for neighbor_id in vertex.neighbor_vertices:
            if neighbor_id in vertex.roads and vertex.roads[neighbor_id] == player_id:
                return True

        return False

    def _calculate_longest_road_for_player(self, player_id: str) -> int:
        """Calculate the longest road for a specific player using DFS"""
        # Find all vertices with player's roads
        road_graph = defaultdict(list)

        for vertex_id, vertex in self.board.vertices.items():
            for neighbor_id, owner_id in vertex.roads.items():
                if owner_id == player_id:
                    road_graph[vertex_id].append(neighbor_id)

        if not road_graph:
            return 0

        def dfs(node: int, visited: Set[Tuple[int, int]]) -> int:
            """DFS to find longest path"""
            max_length = 0

            for neighbor in road_graph[node]:
                edge = tuple(sorted([node, neighbor]))
                if edge not in visited:
                    new_visited = visited.copy()
                    new_visited.add(edge)
                    length = 1 + dfs(neighbor, new_visited)
                    max_length = max(max_length, length)

            return max_length

        # Try starting from each vertex
        longest = 0
        for start_vertex in road_graph.keys():
            length = dfs(start_vertex, set())
            longest = max(longest, length)

        return longest

    def _update_longest_road(self):
        """Update longest road achievement"""
        # Calculate longest road for all players
        road_lengths = {}
        for player_id in self.players.keys():
            length = self._calculate_longest_road_for_player(player_id)
            road_lengths[player_id] = length
            self.players[player_id].longest_road_length = length

        # Find player with longest road (must be at least 5)
        max_length = max(road_lengths.values()) if road_lengths else 0

        if max_length >= 5:
            # Find all players with max length
            players_with_max = [pid for pid, length in road_lengths.items()
                               if length == max_length]

            # If current holder still has it, they keep it (tie goes to current holder)
            if self.longest_road_owner and self.longest_road_owner in players_with_max:
                new_owner = self.longest_road_owner
            else:
                # Otherwise, first player with longest road gets it
                new_owner = players_with_max[0]

            # Update ownership
            if self.longest_road_owner != new_owner:
                if self.longest_road_owner:
                    self.players[self.longest_road_owner].has_longest_road = False
                self.longest_road_owner = new_owner
                self.players[new_owner].has_longest_road = True
        else:
            # Remove longest road if no one has >= 5 roads
            if self.longest_road_owner:
                self.players[self.longest_road_owner].has_longest_road = False
                self.longest_road_owner = None

        # Update victory points
        for player in self.players.values():
            player.victory_points = player.calculate_victory_points()

    def buy_development_card(self, player_id: str) -> Optional[DevelopmentCardType]:
        """Buy a development card"""
        player = self.players.get(player_id)
        if not player:
            return None

        # Check resources
        if (player.resources[ResourceType.WHEAT] < 1 or
            player.resources[ResourceType.SHEEP] < 1 or
            player.resources[ResourceType.ORE] < 1):
            return None

        # Check if deck has cards
        if not self.dev_card_deck:
            return None

        # Draw card
        card = self.dev_card_deck.pop()
        player.development_cards.append(card)

        # Deduct resources
        player.resources[ResourceType.WHEAT] -= 1
        player.resources[ResourceType.SHEEP] -= 1
        player.resources[ResourceType.ORE] -= 1

        self.bank_resources[ResourceType.WHEAT] += 1
        self.bank_resources[ResourceType.SHEEP] += 1
        self.bank_resources[ResourceType.ORE] += 1

        return card

    def end_turn(self, player_id: str) -> bool:
        """End the current player's turn"""
        if self.get_current_player_id() != player_id:
            return False

        # Handle setup phase
        if self.game_phase == GamePhase.SETUP_FORWARD:
            self.setup_placements += 1
            if self.setup_placements >= len(self.players):
                self.game_phase = GamePhase.SETUP_BACKWARD
                # Don't change player, they go again
            else:
                self.current_player_index = (self.current_player_index + 1) % len(self.player_order)

        elif self.game_phase == GamePhase.SETUP_BACKWARD:
            self.setup_placements += 1
            if self.setup_placements >= len(self.players) * 2:
                self.game_phase = GamePhase.REGULAR_PLAY
                self.turn_phase = TurnPhase.WAITING_FOR_ROLL
            else:
                # Go backwards
                self.current_player_index = (self.current_player_index - 1) % len(self.player_order)

        else:  # Regular play
            self.current_player_index = (self.current_player_index + 1) % len(self.player_order)
            self.turn_phase = TurnPhase.WAITING_FOR_ROLL
            self.last_dice_roll = None

        # Check for winner
        current_player = self.get_current_player()
        if current_player and current_player.victory_points >= 10:
            self.game_phase = GamePhase.FINISHED

        return True

    def move_robber(self, player_id: str, hex_id: int, steal_from_player_id: Optional[str] = None) -> bool:
        """Move the robber to a new hex and optionally steal from a player"""
        if self.turn_phase != TurnPhase.MOVING_ROBBER:
            return False

        hex_tile = self.board.hexes.get(hex_id)
        if not hex_tile:
            return False

        # Can't place robber on same hex
        if hex_tile.has_robber:
            return False

        # Remove robber from old location
        if self.board.robber_hex_id is not None:
            self.board.hexes[self.board.robber_hex_id].has_robber = False

        # Place robber on new location
        hex_tile.has_robber = True
        self.board.robber_hex_id = hex_id

        # If stealing, validate and steal
        if steal_from_player_id:
            victim = self.players.get(steal_from_player_id)
            thief = self.players.get(player_id)

            if not victim or not thief:
                return False

            # Validate victim has building on robber hex
            victim_on_hex = False
            for vertex_id in hex_tile.neighbor_vertices:
                vertex = self.board.vertices[vertex_id]
                if vertex.owner_id == steal_from_player_id and vertex.building:
                    victim_on_hex = True
                    break

            if not victim_on_hex:
                return False

            # Steal random resource if victim has any
            if victim.get_total_resource_count() > 0:
                available_resources = [rt for rt, count in victim.resources.items()
                                      if rt != ResourceType.DESERT and count > 0]
                if available_resources:
                    stolen_resource = random.choice(available_resources)
                    victim.resources[stolen_resource] -= 1
                    thief.resources[stolen_resource] += 1

        self.turn_phase = TurnPhase.MAIN_PHASE
        return True

    def discard_resources(self, player_id: str, resources: Dict[str, int]) -> bool:
        """Discard resources when 7 is rolled"""
        player = self.players.get(player_id)
        if not player:
            return False

        # Validate discard amount (must discard half, rounded down)
        total_cards = player.get_total_resource_count()
        if total_cards <= 7:
            return False

        discard_amount = total_cards // 2
        total_discarded = sum(resources.values())

        if total_discarded != discard_amount:
            return False

        # Validate resources
        for resource_name, amount in resources.items():
            try:
                resource_type = ResourceType(resource_name)
                if player.resources[resource_type] < amount:
                    return False
            except ValueError:
                return False

        # Discard resources
        for resource_name, amount in resources.items():
            resource_type = ResourceType(resource_name)
            player.resources[resource_type] -= amount
            self.bank_resources[resource_type] += amount

        # Check if all players have discarded
        all_discarded = all(p.get_total_resource_count() <= 7 or p.player_id == player_id
                           for p in self.players.values())

        if all_discarded:
            self.turn_phase = TurnPhase.MOVING_ROBBER

        return True

    def trade_with_bank(self, player_id: str, give: Dict[str, int], receive: Dict[str, int]) -> bool:
        """Trade with the bank (4:1 or port trades)"""
        player = self.players.get(player_id)
        if not player:
            return False

        # Validate trade amounts
        give_total = sum(give.values())
        receive_total = sum(receive.values())

        # Must give exactly 4 of one resource for 1 of another (basic 4:1 trade)
        # TODO: Add port trade logic for 3:1 and 2:1
        if give_total != 4 or receive_total != 1:
            return False

        # Must be 4 of the SAME resource (can't mix resources in 4:1 trade)
        if len(give) != 1:
            return False

        # Check player has resources
        for resource_name, amount in give.items():
            try:
                resource_type = ResourceType(resource_name)
                if player.resources[resource_type] < amount:
                    return False
            except ValueError:
                return False

        # Check bank has resources
        for resource_name, amount in receive.items():
            try:
                resource_type = ResourceType(resource_name)
                if self.bank_resources[resource_type] < amount:
                    return False
            except ValueError:
                return False

        # Execute trade
        for resource_name, amount in give.items():
            resource_type = ResourceType(resource_name)
            player.resources[resource_type] -= amount
            self.bank_resources[resource_type] += amount

        for resource_name, amount in receive.items():
            resource_type = ResourceType(resource_name)
            player.resources[resource_type] += amount
            self.bank_resources[resource_type] -= amount

        return True

    def propose_player_trade(self, player_id: str, offer: Dict[str, int], request: Dict[str, int]) -> bool:
        """Propose a trade to other players"""
        if self.get_current_player_id() != player_id:
            return False

        player = self.players.get(player_id)
        if not player:
            return False

        # Validate player has resources to offer
        for resource_name, amount in offer.items():
            try:
                resource_type = ResourceType(resource_name)
                if player.resources[resource_type] < amount:
                    return False
            except ValueError:
                return False

        self.active_trade = {
            'proposer': player_id,
            'offer': offer,
            'request': request,
            'responses': {}
        }

        return True

    def respond_to_trade(self, player_id: str, accept: bool) -> bool:
        """Respond to an active trade proposal"""
        if not self.active_trade:
            return False

        if player_id == self.active_trade['proposer']:
            return False

        self.active_trade['responses'][player_id] = accept
        return True

    def execute_trade(self, player_id: str, trade_with_player_id: str) -> bool:
        """Execute a trade with a specific player who accepted"""
        if not self.active_trade:
            return False

        if player_id != self.active_trade['proposer']:
            return False

        if trade_with_player_id not in self.active_trade['responses']:
            return False

        if not self.active_trade['responses'][trade_with_player_id]:
            return False

        proposer = self.players[player_id]
        acceptor = self.players[trade_with_player_id]

        offer = self.active_trade['offer']
        request = self.active_trade['request']

        # Validate both players have resources
        for resource_name, amount in offer.items():
            resource_type = ResourceType(resource_name)
            if proposer.resources[resource_type] < amount:
                return False

        for resource_name, amount in request.items():
            resource_type = ResourceType(resource_name)
            if acceptor.resources[resource_type] < amount:
                return False

        # Execute trade
        for resource_name, amount in offer.items():
            resource_type = ResourceType(resource_name)
            proposer.resources[resource_type] -= amount
            acceptor.resources[resource_type] += amount

        for resource_name, amount in request.items():
            resource_type = ResourceType(resource_name)
            acceptor.resources[resource_type] -= amount
            proposer.resources[resource_type] += amount

        # Clear active trade
        self.active_trade = None

        return True

    def cancel_trade(self, player_id: str) -> bool:
        """Cancel the active trade"""
        if not self.active_trade:
            return False

        if player_id != self.active_trade['proposer']:
            return False

        self.active_trade = None
        return True

    def play_knight_card(self, player_id: str) -> bool:
        """Play a knight development card"""
        player = self.players.get(player_id)
        if not player:
            return False

        if DevelopmentCardType.KNIGHT not in player.development_cards:
            return False

        # Remove card from hand
        player.development_cards.remove(DevelopmentCardType.KNIGHT)
        player.development_cards_played.append(DevelopmentCardType.KNIGHT)
        player.knights_played += 1

        # Update largest army
        self._update_largest_army()

        # Move robber
        self.turn_phase = TurnPhase.MOVING_ROBBER

        return True

    def _update_largest_army(self):
        """Update largest army achievement"""
        # Find player with most knights (must be at least 3)
        max_knights = max((p.knights_played for p in self.players.values()), default=0)

        if max_knights >= 3:
            players_with_max = [pid for pid, p in self.players.items()
                               if p.knights_played == max_knights]

            # If current holder still has it, they keep it
            if self.largest_army_owner and self.largest_army_owner in players_with_max:
                new_owner = self.largest_army_owner
            else:
                new_owner = players_with_max[0]

            # Update ownership
            if self.largest_army_owner != new_owner:
                if self.largest_army_owner:
                    self.players[self.largest_army_owner].has_largest_army = False
                self.largest_army_owner = new_owner
                self.players[new_owner].has_largest_army = True

        # Update victory points
        for player in self.players.values():
            player.victory_points = player.calculate_victory_points()

    def get_state(self) -> Dict:
        """Get the current game state as a dictionary"""
        return {
            'game_id': self.game_id,
            'game_phase': self.game_phase.value,
            'turn_phase': self.turn_phase.value,
            'current_player': self.get_current_player_id(),
            'player_order': self.player_order,
            'last_dice_roll': self.last_dice_roll,
            'active_trade': self.active_trade,
            'players': {
                pid: {
                    'player_id': p.player_id,
                    'name': p.name,
                    'color': p.color,
                    'resources': {rt.value: count for rt, count in p.resources.items()},
                    'resource_count': p.get_total_resource_count(),
                    'dev_card_count': p.get_development_card_count(),
                    'knights_played': p.knights_played,
                    'roads_remaining': p.roads_remaining,
                    'settlements_remaining': p.settlements_remaining,
                    'cities_remaining': p.cities_remaining,
                    'victory_points': p.victory_points,
                    'longest_road_length': p.longest_road_length,
                    'has_longest_road': p.has_longest_road,
                    'has_largest_army': p.has_largest_army,
                    'ready': p.ready
                }
                for pid, p in self.players.items()
            },
            'board': {
                'hexes': [
                    {
                        'id': h.unique_id,
                        'q': h.q,
                        'r': h.r,
                        'resource_type': h.resource_type.value,
                        'number_token': h.number_token,
                        'has_robber': h.has_robber
                    }
                    for h in self.board.hexes.values()
                ],
                'vertices': [
                    {
                        'id': v.unique_id,
                        'q': v.q,
                        'r': v.r,
                        'owner_id': v.owner_id,
                        'building': v.building.value if v.building else None,
                        'neighbor_vertices': v.neighbor_vertices
                    }
                    for v in self.board.vertices.values()
                ],
                'roads': [
                    {
                        'v1': v1_id,
                        'v2': v2_id,
                        'owner': owner_id
                    }
                    for vertex in self.board.vertices.values()
                    for v1_id in [vertex.unique_id]
                    for v2_id, owner_id in vertex.roads.items()
                    if v1_id < v2_id  # Avoid duplicates
                ]
            },
            'bank_resources': {rt.value: count for rt, count in self.bank_resources.items()},
            'dev_cards_remaining': len(self.dev_card_deck)
        }
