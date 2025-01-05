import random

class HexCell:
    def __init__(self, x, y, resource_type=None, number_token=None):
        self.x = x
        self.y = y
        self.resource_type = resource_type
        self.number_token = number_token
        self.adjacent_tiles = []  # Keep this for compatibility with number token assignment

    def __repr__(self):
        return f"HexCell(x={self.x}, y={self.y}, res={self.resource_type}, num={self.number_token})"

class EdgeCell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.owner = None
        self.connected_tiles = []  # Keep for compatibility

    def __repr__(self):
        return f"EdgeCell(x={self.x}, y={self.y}, owner={self.owner})"

class VertexCell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.owner = None
        self.building = None
        self.connected_tiles = []  # Keep for compatibility
        self.connected_vertices = []  # Keep for adjacency checks

    def __repr__(self):
        return f"VertexCell(x={self.x}, y={self.y}, owner={self.owner}, building={self.building})"

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
        self.HEX_W = 5  # Width of the hex grid
        self.HEX_H = 5  # Height of the hex grid
        self.ARR_W = 2 * self.HEX_W + 2  # Width of edge/vertex arrays
        self.ARR_H = 2 * self.HEX_H + 2  # Height of edge/vertex arrays

        # Initialize empty matrices
        self.hexes = [[None for _ in range(self.HEX_H)] for _ in range(self.HEX_W)]
        self.edges = [[None for _ in range(self.ARR_H)] for _ in range(self.ARR_W)]
        self.vertices = [[None for _ in range(self.ARR_H)] for _ in range(self.ARR_W)]

        # Initialize other board properties
        self.bank = {
            'wood': 19, 'brick': 19, 'sheep': 19,
            'wheat': 19, 'ore': 19
        }
        self.players = [Player(i) for i in range(1, 5)]
        self.current_player_index = 0
        self.setup_phase = False
        self.setup_round = 0

        # Setup the board
        self.setup_board()

    def setup_board(self):
        """Setup board in distinct phases"""
        self.setup_resources()
        self.connect_adjacent_tiles()
        self.assign_valid_number_tokens()
        self.create_vertices()
        self.create_edges()

    def setup_resources(self):
        """Convert the old coordinate system to the new matrix-based one"""
        resources = [
            'wood', 'wood', 'wood', 'wood',
            'brick', 'brick', 'brick',
            'ore', 'ore', 'ore',
            'wheat', 'wheat', 'wheat', 'wheat',
            'sheep', 'sheep', 'sheep', 'sheep',
            'desert'
        ]
        random.shuffle(resources)

        # Define the valid hex positions in the matrix
        valid_positions = [
            [(1,1), (2,1), (3,1)],              
            [(1,2), (2,2), (3,2), (4,2)],       
            [(0,3), (1,3), (2,3), (3,3), (4,3)],
            [(1,4), (2,4), (3,4), (4,4)],         
            [(2,5), (3,5), (4,5)]
        ]

        resource_index = 0
        for row in valid_positions:
            for x, y in row:
                if resource_index < len(resources):
                    self.hexes[x][y] = HexCell(x, y, resources[resource_index])
                    resource_index += 1

    def connect_adjacent_tiles(self):
        """Set adjacency relationships among tiles in the matrix."""
        for x in range(self.HEX_W):
            for y in range(self.HEX_H):
                if self.hexes[x][y]:
                    # Get neighbors using matrix offsets
                    offset = 1 if (x % 2 == 0) else -1
                    neighbor_coords = [
                        (x, y+1), (x, y-1),      # above/below
                        (x+1, y), (x-1, y),      # right/left
                        (x+1, y+offset),         # diagonal right
                        (x-1, y+offset)          # diagonal left
                    ]
                    
                    for nx, ny in neighbor_coords:
                        if (0 <= nx < self.HEX_W and 
                            0 <= ny < self.HEX_H and 
                            self.hexes[nx][ny]):
                            self.hexes[x][y].adjacent_tiles.append(self.hexes[nx][ny])

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
        """Create vertices at valid intersections in the matrix."""
        for x in range(self.ARR_W):
            for y in range(self.ARR_H):
                self.vertices[x][y] = VertexCell(x, y)
                
                # Connect vertices to adjacent hexes
                hex_coords = self._get_adjacent_hexes(x, y)
                for hx, hy in hex_coords:
                    if (0 <= hx < self.HEX_W and 
                        0 <= hy < self.HEX_H and 
                        self.hexes[hx][hy]):
                        self.vertices[x][y].connected_tiles.append(self.hexes[hx][hy])

    def create_edges(self):
        """Create edges between valid vertices in the matrix."""
        for x in range(self.ARR_W):
            for y in range(self.ARR_H):
                self.edges[x][y] = EdgeCell(x, y)
                
                # Connect edges to adjacent hexes
                hex_coords = self._get_adjacent_hexes_for_edge(x, y)
                for hx, hy in hex_coords:
                    if (0 <= hx < self.HEX_W and 
                        0 <= hy < self.HEX_H and 
                        self.hexes[hx][hy]):
                        self.edges[x][y].connected_tiles.append(self.hexes[hx][hy])

    def _get_adjacent_hexes(self, vx, vy):
        """Helper to get hex coordinates adjacent to a vertex position."""
        offset = vx % 2
        return [
            ((vx-1) // 2, (vy // 2) - offset),
            (vx // 2, (vy // 2)),
            ((vx-1) // 2, (vy // 2))
        ]

    def _get_adjacent_hexes_for_edge(self, ex, ey):
        """Helper to get hex coordinates adjacent to an edge position."""
        offset = ex % 2
        return [
            (ex // 2, ey // 2),
            ((ex-1) // 2, (ey // 2) - offset)
        ]

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
        """Roll dice and distribute resources using matrix positions."""
        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6)
        dice_sum = dice1 + dice2
        
        for x in range(self.HEX_W):
            for y in range(self.HEX_H):
                hex_cell = self.hexes[x][y]
                if (hex_cell and 
                    hex_cell.number_token == dice_sum and 
                    hex_cell.resource_type != 'desert'):
                    
                    # Find connected vertices with settlements/cities
                    vertex_coords = self._get_hex_vertices(x, y)
                    for vx, vy in vertex_coords:
                        if (0 <= vx < self.ARR_W and 
                            0 <= vy < self.ARR_H and 
                            self.vertices[vx][vy] and 
                            self.vertices[vx][vy].owner is not None):
                            
                            vertex = self.vertices[vx][vy]
                            amount = 2 if vertex.building == 'city' else 1
                            resource = hex_cell.resource_type
                            
                            if self.bank[resource] >= amount:
                                self.bank[resource] -= amount
                                self.players[vertex.owner - 1].resources[resource] += amount
                                
        return dice1, dice2

    def _get_hex_vertices(self, hx, hy):
        """Get vertex coordinates for a hex position."""
        offset = hx % 2
        return [
            (2*hx, 2*hy + offset),
            (2*hx, 2*hy + 1 + offset),
            (2*hx, 2*hy + 2 + offset),
            (2*hx+1, 2*hy + offset),
            (2*hx+1, 2*hy + 1 + offset),
            (2*hx+1, 2*hy + 2 + offset)
        ]

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
        """Return valid vertex positions for settlements."""
        valid_spots = []
        for x in range(self.ARR_W):
            for y in range(self.ARR_H):
                vertex = self.vertices[x][y]
                if (vertex and 
                    vertex.owner is None and 
                    not self._has_nearby_settlement(vertex) and 
                    len(vertex.connected_tiles) > 0):
                    valid_spots.append(vertex)
        return valid_spots

    def _has_nearby_settlement(self, vertex):
        """Check for settlements within 2 edges using matrix positions."""
        x, y = vertex.x, vertex.y
        nearby_coords = [
            (x-2, y), (x+2, y),     # left/right
            (x-1, y-1), (x+1, y-1), # diagonals up
            (x-1, y+1), (x+1, y+1)  # diagonals down
        ]
        
        for nx, ny in nearby_coords:
            if (0 <= nx < self.ARR_W and 
                0 <= ny < self.ARR_H and 
                self.vertices[nx][ny] and 
                self.vertices[nx][ny].owner is not None):
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
        """Return valid edge positions for roads."""
        valid_edges = []
        for x in range(self.ARR_W):
            for y in range(self.ARR_H):
                edge = self.edges[x][y]
                if edge and not edge.owner:
                    # Check connection to player's existing roads/settlements
                    if self._is_valid_road_spot(edge, player):
                        valid_edges.append(edge)
        return valid_edges

    def _is_valid_road_spot(self, edge, player):
        """Check if edge connects to player's existing infrastructure."""
        x, y = edge.x, edge.y
        
        # Check adjacent vertices
        vertex_coords = [
            (x, y), (x+1, y),   # horizontal edge
            (x, y+1), (x, y-1)  # vertical edge
        ]
        
        for vx, vy in vertex_coords:
            if (0 <= vx < self.ARR_W and 
                0 <= vy < self.ARR_H and 
                self.vertices[vx][vy] and 
                self.vertices[vx][vy].owner == player.pid):
                return True
            
        # Check adjacent edges
        edge_coords = [
            (x-1, y), (x+1, y),
            (x, y-1), (x, y+1)
        ]
        
        for ex, ey in edge_coords:
            if (0 <= ex < self.ARR_W and 
                0 <= ey < self.ARR_H and 
                self.edges[ex][ey] and 
                self.edges[ex][ey].owner == player.pid):
                return True
            
        return False
    
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
        

