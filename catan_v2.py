import random

class HexTile:
    def __init__(self, resource_type, number_token, q=0, r=0):
        self.resource_type = resource_type
        self.number_token = number_token
        self.adjacent_tiles = []
        self.vertices = []
        self.q = q  # q coordinate in axial system
        self.r = r  # r coordinate in axial system

class Vertex:
    def __init__(self, q, r, vertex_position):
        self.connected_tiles = []
        self.owner = None   # Which player (1-4) owns this vertex, if any
        self.connected_vertices = []
        self.q = q   # q coordinate of associated hex
        self.r = r   # r coordinate of associated hex
        self.vertex_position = vertex_position  # integer 0-5 for corners
        self.building = None  # 'settlement' or 'city'

class Road:
    """
    A Road connects two adjacent vertices. It must be owned by exactly one player.
    """
    def __init__(self, vertex1, vertex2, owner=None):
        self.vertex1 = vertex1
        self.vertex2 = vertex2
        self.owner = owner  # which player (1-4), or None if unowned

class Player:
    """
    Each player holds resources, roads, etc.
    """
    def __init__(self, pid):
        self.pid = pid  # player id, e.g. 1, 2, 3, 4
        self.resources = {
            'wood': 0,
            'brick': 0,
            'wheat': 0,
            'sheep': 0,
            'ore': 0
        }
        self.roads = []        # list of Road objects owned by this player
        self.settlements = 0   # simple count, or store references to Vertex
        self.cities = 0        # simple count, or store references to Vertex
        # You could add more as needed (development cards, etc.)

class Board:
    def __init__(self):
        self.tiles = []
        self.vertices = {}
        # The “bank” has limited resource cards, e.g. 19 each for basic 5 resources
        self.bank = {
            'wood': 19,
            'brick': 19,
            'sheep': 19,
            'wheat': 19,
            'ore': 19
        }
        
        # Create four players
        self.players = [Player(i) for i in range(1, 5)]
        
        # Keep track of current player
        self.current_player_index = 0  # points to self.players
        
        # Setup the board
        self.setup_board()
    
    def setup_board(self):
        """Setup board in distinct phases"""
        self.setup_resources()         # 1) Create tiles with resources
        self.connect_adjacent_tiles()  # 2) Connect neighboring tiles
        self.assign_valid_number_tokens()  # 3) Assign dice numbers
    
    def setup_resources(self):
        """Phase 1: Setup resources only"""
        resources = [
            'wood', 'wood', 'wood', 'wood',
            'brick', 'brick', 'brick',
            'ore', 'ore', 'ore',
            'wheat', 'wheat', 'wheat', 'wheat',
            'sheep', 'sheep', 'sheep', 'sheep',
            'desert'
        ]
        
        random.shuffle(resources)
        
        grid_positions = [
            [(0,0), (1,0), (2,0)],              # Top row
            [(0,1), (1,1), (2,1), (3,1)],       # Second row
            [(0,2), (1,2), (2,2), (3,2), (4,2)],# Middle row
            [(0,3), (1,3), (2,3), (3,3)],       # Fourth row
            [(0,4), (1,4), (2,4)]               # Bottom row
        ]

        tile_index = 0
        for row in grid_positions:
            for q, r in row:
                resource = resources[tile_index]
                tile = HexTile(resource, 0, q, r)  # Initialize with 0 as number
                self.tiles.append(tile)
                tile_index += 1

    def connect_adjacent_tiles(self):
        """
        Phase 2: Set the adjacency relationships among tiles 
        (this helps us detect adjacent 6/8 tiles, among other things).
        """
        directions = [(1,0), (1,-1), (0,-1), (-1,0), (-1,1), (0,1)]
        
        for tile1 in self.tiles:
            for direction in directions:
                q = tile1.q + direction[0]
                r = tile1.r + direction[1]
                # Find if there's a tile at (q, r)
                neighbor = next((t for t in self.tiles if t.q == q and t.r == r), None)
                if neighbor and neighbor not in tile1.adjacent_tiles:
                    tile1.adjacent_tiles.append(neighbor)

    def assign_valid_number_tokens(self, max_attempts=1000):
        """
        Phase 3: Assign dice roll values to non-desert tiles 
        in a way that no two '6' or '8' are adjacent.
        """
        number_tokens = [2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12]
        non_desert_tiles = [t for t in self.tiles if t.resource_type != 'desert']
        
        for attempt in range(max_attempts):
            # Shuffle new distribution
            random.shuffle(number_tokens)
            
            # Assign
            for i, tile in enumerate(non_desert_tiles):
                tile.number_token = number_tokens[i]
            
            # Check adjacency constraint
            if not self.has_adjacent_high_probability():
                # Found a valid distribution
                return
            
            # Otherwise reset (optional) and try again
            for tile in non_desert_tiles:
                tile.number_token = -1
        
        raise Exception(f"Could not create valid number distribution after {max_attempts} attempts")

    def has_adjacent_high_probability(self):
        """Check if any 6s or 8s are adjacent to each other."""
        high_prob = [6, 8]
        for tile in self.tiles:
            if tile.number_token in high_prob:
                for adj_tile in tile.adjacent_tiles:
                    if adj_tile.number_token in high_prob:
                        return True
        return False

    def roll_dice_and_distribute(self):
        """
        1) Roll 2 dice (1-6 each).
        2) For each tile whose number matches dice_sum, 
           give resources to any adjacent settlements/cities.
        3) If not enough resources in the bank, skip/partial distribution 
           (this example just *skips* if the bank runs out).
        """
        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6)
        dice_sum = dice1 + dice2
        print(f"\nDice roll is {dice1} + {dice2} = {dice_sum}")
        
        # For each tile with matching number
        for tile in self.tiles:
            if tile.number_token == dice_sum and tile.resource_type != 'desert':
                resource = tile.resource_type
                
                # For each vertex that touches this tile
                for v in tile.vertices:
                    if v.owner is not None:  # somebody owns this corner
                        owner_player = self.players[v.owner - 1]
                        # Settlement => +1 resource, City => +2
                        amount = 1 if v.building == 'settlement' else 2 if v.building == 'city' else 0
                        
                        # Only distribute if the bank has enough
                        if self.bank[resource] >= amount and amount > 0:
                            self.bank[resource] -= amount
                            owner_player.resources[resource] += amount
                        # If the bank doesn't have enough, we skip (or partially fill, etc.)

    def next_player_turn(self):
        """
        Moves to the next player's turn (1->2->3->4->1->...).
        Returns the player object whose turn it now is.
        """
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        return self.players[self.current_player_index]
    
    def get_valid_settlement_spots(self, player: Player):
        """
        Return a list of vertices where the given player *could* place a new settlement.
        For example:
          - Vertex must not be occupied
          - Typically must connect to that player's existing road or be free, 
            (we’ll keep it simple here and just say unoccupied)
        """
        valid_spots = []
        all_vertices = self._collect_all_vertices()
        for v in all_vertices:
            if v.owner is None:
                # (Optional) Add more logic like distance rule 
                # or checking adjacency to that player's road
                valid_spots.append(v)
        return valid_spots

    def get_valid_city_spots(self, player: Player):
        """
        Return a list of vertices that the given player owns (settlement) 
        which can be upgraded to city.
        """
        valid_spots = []
        all_vertices = self._collect_all_vertices()
        for v in all_vertices:
            if v.owner == player.pid and v.building == 'settlement':
                valid_spots.append(v)
        return valid_spots

    def get_valid_road_spots(self, player: Player):
        """
        Return a list of all possible roads (pairs of connected vertices)
        that the player could build on. 
        Basic rule: The edge is not already occupied by any road.
        """
        # Collect all possible edges by scanning adjacency among vertices
        edges = []
        all_vertices = self._collect_all_vertices()
        
        for v in all_vertices:
            for adj in v.connected_vertices:
                # Avoid double counting (v->adj vs adj->v)
                if v.vertex_position < adj.vertex_position or v.q < adj.q or v.r < adj.r:
                    # Check if already has a road
                    if not self._edge_has_road(v, adj):
                        # (Optional) Check connectivity to player's existing roads or settlement 
                        edges.append((v, adj))
        
        return edges

    def _edge_has_road(self, v1, v2):
        """Helper to see if there is any road occupying this edge."""
        # If you kept a global list of all roads on the Board, 
        # you’d check that list here. For demo, we just check each player's roads
        for p in self.players:
            for road in p.roads:
                # This means the road is the same if it has the same 2 endpoints 
                # (in either order).
                if (road.vertex1 == v1 and road.vertex2 == v2) or \
                   (road.vertex1 == v2 and road.vertex2 == v1):
                    return True
        return False

    def _collect_all_vertices(self):
        """
        For convenience, gather all Vertex objects from self.tiles 
        (once they're fully assigned).
        """
        # If each tile has 6 unique Vertex objects, you might be double counting.
        # In a standard approach, you’d be re-using Vertex references for adjacent 
        # tiles. For simplicity, assume you store them consistently in tile.vertices. 
        # This is left partly abstract, but you can unify them in a data structure.
        all_vertices = []
        for t in self.tiles:
            for v in t.vertices:
                if v not in all_vertices:
                    all_vertices.append(v)
        return all_vertices

    def print_board(self):
        """Print a visual representation of the board in hexagonal shape"""
        def format_tile(tile):
            # Get first letter of resource (W=Wood, B=Brick, O=Ore, S=Sheep, H=wHeat, D=Desert)
            # We'll do T for wood to avoid confusion with wheat:
            resource_char = 'T' if tile.resource_type == 'wood' else tile.resource_type[0].upper()
            if resource_char == 'W' and tile.resource_type == 'wheat':
                resource_char = 'H'  # H for wHeat
            padding = "" if len(str(tile.number_token)) == 2 else " "
            return f"{resource_char}{tile.number_token}{padding}"

        rows = [
            [(0,0), (1,0), (2,0)],
            [(0,1), (1,1), (2,1), (3,1)],
            [(0,2), (1,2), (2,2), (3,2), (4,2)],
            [(0,3), (1,3), (2,3), (3,3)],
            [(0,4), (1,4), (2,4)]
        ]

        board_str = ""
        for row in rows:
            indent = "  " * (5 - len(row))
            board_str += indent
            for q, r in row:
                tile = next((t for t in self.tiles if t.q == q and t.r == r), None)
                board_str += f"{format_tile(tile)} "
            board_str += "\n"
        board_str = board_str.rstrip()
            
        print(board_str)


# ------------------------------------------------------------------------------
# Example usage / flow
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    # Create and initialize the board
    board = Board()
    board.print_board()
    
    # Fake hooking up the tile vertices with some shared references, 
    # so resources can be distributed. 
    # In a real game, you'd share Vertex objects across adjacent tiles 
    # and set up adjacency between them. 
    # (This step is typically more intricate, but here’s a minimal approach.)
    
    # Example: Let’s forcibly assign 6 vertices to each tile.
    # Real code would unify them among tiles so they share the same vertex object 
    # at shared corners.
    for tile in board.tiles:
        for pos in range(6):
            tile.vertices.append(Vertex(tile.q, tile.r, pos))
    
    # Now connect each tile’s 6 vertices. 
    # (Again, in a real code base you’d unify these among adjacent tiles.)
    # For demonstration, we’ll just connect them in a ring, ignoring cross-tile adjacency:
    for tile in board.tiles:
        for i in range(6):
            v1 = tile.vertices[i]
            v2 = tile.vertices[(i+1) % 6]
            if v2 not in v1.connected_vertices:
                v1.connected_vertices.append(v2)
            if v1 not in v2.connected_vertices:
                v2.connected_vertices.append(v1)
    
    # Simulate a round of turns
    for turn in range(1, 5):
        current_player = board.players[board.current_player_index]
        print(f"\n=== Player {current_player.pid}'s turn ===")
        
        # 1) Roll dice and distribute
        board.roll_dice_and_distribute()
        
        # 2) Get valid placements for player
        valid_settlements = board.get_valid_settlement_spots(current_player)
        valid_cities = board.get_valid_city_spots(current_player)
        valid_roads = board.get_valid_road_spots(current_player)
        
        # 3) Print them (in a real game, you’d choose among them)
        print(f"Valid settlement spots: {len(valid_settlements)}")
        print(f"Valid city spots:       {len(valid_cities)}")
        print(f"Valid road placements: {len(valid_roads)}")
        
        # 4) Move to next player
        board.next_player_turn()
    
    # After the loop, we can see players' resource counts, etc.
    for p in board.players:
        print(f"\nPlayer {p.pid} resources: {p.resources}")
    print(f"\nBank left: {board.bank}")
