import random

class HexTile:
    def __init__(self, resource_type, number_token, q=0, r=0):
        self.resource_type = resource_type
        self.number_token = number_token
        self.adjacent_tiles = []
        self.vertices = []
        self.q = q
        self.r = r

class Edge:
    def __init__(self, vertex1, vertex2):
        self.vertices = (vertex1, vertex2)  # Store as tuple for immutability
        self.owner = None
        self.connected_tiles = []  # Tiles this edge borders

    def __repr__(self):
        return f"Edge(vertices={self.vertices}, owner={self.owner}, connected_tiles={self.connected_tiles})"

class Vertex:
    """
    Revised Vertex class that can represent multiple (q, r, corner_index)
    references (corners) for the same physical spot.
    """
    def __init__(self, q, r, corner_index):
        # Start corners as a list containing the first corner
        self.corners = [(q, r, corner_index)]

        self.q = q
        self.r = r
        self.corner_index = corner_index

        self.connected_tiles = []
        self.connected_vertices = []
        self.owner = None
        self.building = None

    def __repr__(self):
        return f"Vertex(corners={self.corners}, owner={self.owner}, building={self.building})"

class Road:
    """
    A Road connects two adjacent vertices. It must be owned by exactly one player.
    """
    def __init__(self, edge, owner=None):
        self.edge = edge
        self.owner = owner

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

class Board:
    def __init__(self):
        self.tiles = []
        # We will store each physical vertex in a dictionary keyed by
        # a consistent corner-key so we don’t create duplicates.
        self.vertices = []
        self.edges = {}
        self.bank = {
            'wood': 19,
            'brick': 19,
            'sheep': 19,
            'wheat': 19,
            'ore': 19
        }
        self.players = [Player(i) for i in range(1, 5)]
        self.current_player_index = 0
        self.setup_phase = False
        self.setup_round = 0
        # Kick off board setup
        self.setup_board()

    def setup_board(self):
        """Setup board in distinct phases"""
        self.setup_resources()         # 1) Create tiles with resources
        self.connect_adjacent_tiles()  # 2) Connect neighboring tiles
        self.assign_valid_number_tokens()  # 3) Assign dice numbers
        
        self.create_vertices()         # 4) Create vertices (with corner reps)
        # self.create_edges()            # 5) Create edges between vertices


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

        # Proper axial coordinates for a standard Catan layout
        grid_positions = [
            [(-2,0), (-1,-1), (0,-2)],              
            [(-2,1), (-1,0), (0,-1), (1,-2)],       
            [(-2,2), (-1,1), (0,0), (1,-1), (2,-2)],
            [(-1,2), (0,1), (1,0), (2,-1)],         
            [(0,2), (1,1), (2,0)]
        ]

        tile_index = 0
        for row in grid_positions:
            for q, r in row:
                resource = resources[tile_index]
                tile = HexTile(resource, 0, q, r)
                self.tiles.append(tile)
                tile_index += 1

    def connect_adjacent_tiles(self):
        """
        Phase 2: Set the adjacency relationships among tiles 
        (this helps us detect adjacent 6/8 tiles, among other things).
        """
        directions = [(1,0), (1,-1), (0,-1), (-1,0), (-1,1), (0,1)]
        for tile1 in self.tiles:
            for dq, dr in directions:
                q2 = tile1.q + dq
                r2 = tile1.r + dr
                for tile2 in self.tiles:
                    if tile2.q == q2 and tile2.r == r2:
                        if tile2 not in tile1.adjacent_tiles:
                            tile1.adjacent_tiles.append(tile2)
                        if tile1 not in tile2.adjacent_tiles:
                            tile2.adjacent_tiles.append(tile1)

    def equivalent_vertex(self, tuple1, tuple2):
        """Input two (q, r, corner_index) tuples and return True if they are equivalent."""
        if tuple1 == tuple2:
            return True
      
        q1, r1, c1 = tuple1
        q2, r2, c2 = tuple2

        #    0
        # 5     1
        # 4     2
        #    3

        # if c1 == 1:
        #     return False

        # diff to go from tuple1 to tuple2
        diff = (q2 - q1, r2 - r1)
        if diff == (-1, 0): # top left
            if (c1 == 0 and c2 == 2) or (c1 == 5 and c2 == 3):
                return True
        elif diff == (0, -1): # top right
            if (c1 == 0 and c2 == 4) or (c1 == 1 and c2 == 3):
                return True
        elif diff == (1, -1): # right
            if (c1 == 1 and c2 == 5) or (c1 == 2 and c2 == 4):
                return True
        elif diff == (1, 0): # bottom right
            if (c1 == 2 and c2 == 0) or (c1 == 3 and c2 == 5):
                return True
        elif diff == (0, 1): # bottom left
            if (c1 == 3 and c2 == 1) or (c1 == 4 and c2 == 0):
                return True
        elif diff == (-1, 1): # left
            if (c1 == 4 and c2 == 2) or (c1 == 5 and c2 == 1):
                return True
        return False

    def create_vertices(self):
        """
        1) For each tile, for each of its 6 corners, generate a consistent identifier.
        2) If that identifier is not already in self.vertices, create a new Vertex.
        3) Otherwise reuse the existing Vertex.
        4) Add this corner representation (q, r, corner_index) to the vertex.
        5) Link tile <-> vertex if needed.
        """
        self.vertices = []  # reset any existing list
        for tile in self.tiles:
            # Make sure tile.vertices starts empty so we can populate it fresh
            tile.vertices = []

            q, r = tile.q, tile.r
            for corner_index in range(6):
                matching_vertex = None
                for v in self.vertices:
                    if self.equivalent_vertex((q, r, corner_index), (v.q, v.r, v.corner_index)):
                        matching_vertex = v
                        break

                if not matching_vertex:
                    new_v = Vertex(q, r, corner_index)
                    self.vertices.append(new_v)
                    # Attach tile <--> vertex
                    tile.vertices.append(new_v)
                    new_v.connected_tiles.append(tile)
                else:
                    # Add this (q, r, corner_index) to the matching vertex's corners
                    matching_vertex.corners.append((q, r, corner_index))
                    # Attach tile <--> matching vertex
                    tile.vertices.append(matching_vertex)
                    matching_vertex.connected_tiles.append(tile)

    def create_edges(self):
        """
        1) For each tile, for each of its 6 edges, get the two vertices that define it.
        2) If that edge doesn't exist, create it.
        3) Store in self.edges dictionary with a consistent key for the vertex pair.
        4) Also link vertex.connected_vertices for adjacency checks.
        """
        self.edges = {}

        for tile in self.tiles:
            # The tile.vertices should have 6 Vertex objects in order
            # but we can't rely on their order in a set; they might not be in corner order.
            # So let's gather the correct Vertex objects by corner index:
            corner_vertices = [None]*6
            for corner_index in range(6):
                key = self._get_vertex_key(tile.q, tile.r, corner_index)
                corner_vertices[corner_index] = self.vertices[key]

            # For each edge of the hex (i, i+1)
            for i in range(6):
                v1 = corner_vertices[i]
                v2 = corner_vertices[(i + 1) % 6]

                # Build a stable edge key
                # We'll just store them sorted by Python's built-in id, or you could store references
                v1_id, v2_id = sorted([id(v1), id(v2)])
                edge_key = (v1_id, v2_id)

                if edge_key not in self.edges:
                    e = Edge(v1, v2)
                    # Link to tiles that share this edge
                    e.connected_tiles.append(tile)
                    self.edges[edge_key] = e
                else:
                    # Already created by an adjacent tile
                    existing_edge = self.edges[edge_key]
                    # Make sure we register this tile to the edge's tile list
                    if tile not in existing_edge.connected_tiles:
                        existing_edge.connected_tiles.append(tile)

                # For adjacency among vertices
                if v2 not in v1.connected_vertices:
                    v1.connected_vertices.append(v2)
                if v1 not in v2.connected_vertices:
                    v2.connected_vertices.append(v1)

        # Convert self.edges from dict to a more standard structure
        # or keep it as-is with the (id(v1), id(v2)) keys.

    def assign_valid_number_tokens(self, max_attempts=1000):
        """
        Phase 5: Assign dice roll values to non-desert tiles 
        so that no two '6' or '8' are adjacent.
        """
        number_tokens = [2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12]
        non_desert_tiles = [t for t in self.tiles if t.resource_type != 'desert']

        for attempt in range(max_attempts):
            random.shuffle(number_tokens)
            for i, tile in enumerate(non_desert_tiles):
                tile.number_token = number_tokens[i]

            if not self.has_adjacent_high_probability():
                return  # Valid distribution found

            # Otherwise reset and try again
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
        2) For each tile whose number matches dice_sum, distribute resources
           to any adjacent settlements/cities.
        """
        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6)
        dice_sum = dice1 + dice2
        
        for tile in self.tiles:
            if tile.number_token == dice_sum and tile.resource_type != 'desert':
                resource = tile.resource_type
                for vertex in tile.vertices:
                    if vertex.owner is not None and vertex.building:
                        owner_player = self.players[vertex.owner - 1]
                        amount = 2 if vertex.building == 'city' else 1
                        if self.bank[resource] >= amount:
                            self.bank[resource] -= amount
                            owner_player.resources[resource] += amount

        return dice1, dice2

    def next_player_turn(self):
        """
        Moves to the next player's turn (1->2->3->4->1->...).
        Returns the player object whose turn it now is.
        """
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        return self.players[self.current_player_index]

    def prev_player_turn(self):
        """
        Moves to the previous player's turn (1->4->3->2->1->...).
        Returns the player object whose turn it now is.
        """
        self.current_player_index = (self.current_player_index - 1) % len(self.players)
        return self.players[self.current_player_index]


    def get_valid_settlement_spots(self, player):
        """
        Return a list of vertices where the given player *could* place a new settlement.
        Rules:
         - Vertex must not be occupied
         - Must be at least 2 edges away from any other settlement
         - Must be connected to at least one tile (not off-board)
        """
        valid_spots = []
        for v in self.vertices:
            if (v.owner is None
                and not self._has_nearby_settlement(v)
                and len(v.connected_tiles) > 0):
                valid_spots.append(v)

        print(f"Found {len(valid_spots)} valid settlement spots")
        return valid_spots

    def _has_nearby_settlement(self, vertex):
        """Check if there's any settlement within 2 edges of this vertex."""
        for adjacent in vertex.connected_vertices:
            if adjacent.owner is not None:
                return True
            for second_adjacent in adjacent.connected_vertices:
                if second_adjacent.owner is not None:
                    return True
        return False

    def get_valid_city_spots(self, player):
        """
        Return a list of vertices that the given player owns (with a 'settlement')
        which can be upgraded to a city.
        """
        valid_spots = []
        for v in self.vertices:
            if v.owner == player.pid and v.building == 'settlement':
                valid_spots.append(v)
        return valid_spots

    def get_valid_road_spots(self, player):
        """
        Return all valid edges where the player could build a road.
        (Edge must not already have a road, and must connect to the player's
        existing road or settlement.)
        """
        valid_edges = []

        for edge in self.edges.values():
            # Check if edge already has a road
            if any(road.edge == edge for p in self.players for road in p.roads):
                continue

            # Check adjacency to the player's stuff
            has_connection = False
            for vertex in edge.vertices:
                if vertex.owner == player.pid:  # adjacency to a settlement
                    has_connection = True
                    break

                # check adjacency to an existing road
                for adj_edge in self.get_adjacent_edges(vertex):
                    if any(road.edge == adj_edge and road.owner == player.pid
                           for p in self.players for road in p.roads):
                        has_connection = True
                        break

            if has_connection:
                valid_edges.append(edge)

        return valid_edges
    
    def get_adjacent_edges(self, vertex):
        """Get all edges connected to a vertex."""
        corners = vertex.corners
        adjacent = []
        for edge in self.edges.values():
            v1, v2 = edge.vertices
            for corner in corners:
                if corner in v1.corners or corner in v2.corners:
                    adjacent.append(edge)
                    break
        print(f'adjacent_edges ({len(adjacent)}/{len(self.edges)})')
        return adjacent


    def _edge_has_road(self, v1, v2):
        """
        If any player's roads occupy this edge, return True.
        """
        for p in self.players:
            for road in p.roads:
                if (road.edge.vertices[0] == v1 and road.edge.vertices[1] == v2) \
                   or (road.edge.vertices[0] == v2 and road.edge.vertices[1] == v1):
                    return True
        return False

    def get_board_state(self):
        """
        Return a dict that describes all necessary board info.
        """
        state = {
            "tiles": [
                {
                    "q": t.q,
                    "r": t.r,
                    "resource_type": t.resource_type,
                    "number_token": t.number_token
                }
                for t in self.tiles
            ],
            "bank": self.bank,
            "players": [
                {
                    "pid": p.pid,
                    "resources": p.resources,
                }
                for p in self.players
            ],
            "current_player": self.get_current_player().pid
        }

        vertex_list = []
        for v in self.vertices:
            q0, r0, c0 = v.q, v.r, v.corner_index

            vertex_list.append({
                "q": q0,
                "r": r0,
                "corner_index": c0,
                "owner": v.owner,
                "building": v.building
            })

        state["vertices"] = vertex_list

        # Serialize edges
        edge_list = []
        for e in self.edges.values():
            v1, v2 = e.vertices
            # For stable display, pick the first corner from each vertex
            if v1.corners:
                q1, r1, c1 = v1.corners[0]
            else:
                q1, r1, c1 = (None, None, None)
            if v2.corners:
                q2, r2, c2 = v2.corners[0]
            else:
                q2, r2, c2 = (None, None, None)

            # Check if there's a road
            has_road = any(road.edge == e for p in self.players for road in p.roads)
            edge_list.append({
                "v1": {"q": q1, "r": r1, "corner": c1},
                "v2": {"q": q2, "r": r2, "corner": c2},
                "owner": e.owner,
                "has_road": has_road
            })
        state["edges"] = edge_list

        return state

    def get_current_player(self):
        """Helper method to get current player"""
        return self.players[self.current_player_index]


def calculate_pip_value(vertex):
    """
    Calculate total pip value for a vertex based on adjacent tiles.
    Returns a tuple of (total_value, num_tiles).
    """
    pip_values = {
        2: 1, 12: 1,
        3: 2, 11: 2,
        4: 3, 10: 3,
        5: 4, 9: 4,
        6: 5, 8: 5
    }
    valid_tiles = [t for t in vertex.connected_tiles if t.resource_type != 'desert' and t.number_token > 0]
    num_tiles = len(valid_tiles)
    raw_pips = sum(pip_values.get(tile.number_token, 0) for tile in valid_tiles)
    return (raw_pips, num_tiles)

def auto_place_settlement(board, player):
    valid_spots = board.get_valid_settlement_spots(player)
    if not valid_spots:
        print(f"No valid spots for player {player.pid}")
        return None

    spot = random.choice(valid_spots)
    print(f"auto_place_settlement: spot: {spot} | connected_tiles: {len(spot.connected_tiles)}")

    spot.owner = player.pid
    spot.building = 'settlement'

    adjacent_edges = board.get_adjacent_edges(spot)
    if adjacent_edges:
        edge = random.choice(adjacent_edges)
        edge.owner = player.pid
        road = Road(edge, player.pid)
        player.roads.append(road)

    # Give initial resources for second settlement
    if board.setup_phase and board.setup_round == 2:
        for tile in spot.connected_tiles:
            if tile.resource_type != 'desert':
                player.resources[tile.resource_type] += 1

    return spot

def auto_place_initial_settlements(board):
    print("-" * 30 + " auto_place_initial_settlements " + "-" * 30)
    print(f'len(board.edges): {len(board.edges)}')
    print(f'len(board.vertices): {len(board.vertices)}')

    player = board.players[0]
    for v in board.vertices:
        v.owner = player.pid
        v.building = 'settlement'

  
    # player = board.players[3]
    # for edge in board.edges.values():
    #     edge.owner = player.pid
    #     road = Road(edge, player.pid)
    #     player.roads.append(road)

    print(f'placed {len(board.vertices)} settlements')
    print(f'placed {len(board.edges)} roads')


    # for player in board.players[:1]:
    #     auto_place_settlement(board, player)

    # Example of second round if desired:
    # board.setup_round = 2
    # for player in reversed(board.players):
    #     auto_place_settlement(board, player)
        