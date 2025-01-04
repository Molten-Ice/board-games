## Building the game of Catan in python ##
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
        self.owner = None
        self.connected_vertices = []
        self.q = q  # q coordinate of the associated hex
        self.r = r  # r coordinate of the associated hex
        self.vertex_position = vertex_position  # 0-5 for the six corners
        self.building = None  # 'settlement' or 'city'

class Board:
    def __init__(self):
        self.tiles = []
        self.vertices = {}
        self.setup_board()
    
    def setup_board(self):
        """Setup board in distinct phases"""
        # Phase 1: Place resources and create board structure
        self.setup_resources()
        # Phase 2: Connect tiles
        self.connect_adjacent_tiles()
        # Phase 3: Assign and validate number tokens
        self.assign_valid_number_tokens()

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
        
        import random
        random.shuffle(resources)
        
        grid_positions = [
            [(0,0), (1,0), (2,0)],              # Top row
            [(0,1), (1,1), (2,1), (3,1)],       # Second row
            [(0,2), (1,2), (2,2), (3,2), (4,2)],# Middle row
            [(0,3), (1,3), (2,3), (3,3)],       # Fourth row
            [(0,4), (1,4), (2,4)]               # Bottom row
        ]

        # Create tiles with resources but no numbers yet
        tile_index = 0
        for row in grid_positions:
            for q, r in row:
                resource = resources[tile_index]
                tile = HexTile(resource, 0, q, r)  # Initialize with 0 as number
                self.tiles.append(tile)
                tile_index += 1

    def assign_valid_number_tokens(self, max_attempts=1000):
        """Phase 3: Assign and validate number tokens"""
        number_tokens = [2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12]
        non_desert_tiles = [t for t in self.tiles if t.resource_type != 'desert']
        
        for attempt in range(max_attempts):
            # Reset all number tokens

            tokens_to_assign = number_tokens.copy()
            random.shuffle(tokens_to_assign)
        
            for i, tile in enumerate(non_desert_tiles):
                tile.number_token = tokens_to_assign[i]
            
            if not self.has_adjacent_high_probability():
                print(f"Valid number distribution found after {attempt + 1} attempts")
                return

            for tile in non_desert_tiles:
                tile.number_token = -1
        
        raise Exception(f"Could not create valid number distribution after {max_attempts} attempts")

    def has_adjacent_high_probability(self):
        """Check if any 6s or 8s are adjacent to each other"""
        high_prob = [6, 8]
        for tile in self.tiles:
            if tile.number_token in high_prob:
                for adj_tile in tile.adjacent_tiles:
                    if adj_tile.number_token in high_prob:
                        return True
        return False

    def connect_adjacent_tiles(self):
        # In axial coordinates, the six neighboring hexes are at these offsets
        directions = [(1,0), (1,-1), (0,-1), (-1,0), (-1,1), (0,1)]
        
        for tile1 in self.tiles:
            for direction in directions:
                q = tile1.q + direction[0]
                r = tile1.r + direction[1]
                # Find if there's a tile at this position
                neighbor = next((t for t in self.tiles if t.q == q and t.r == r), None)
                if neighbor and neighbor not in tile1.adjacent_tiles:
                    tile1.adjacent_tiles.append(neighbor)

    def print_board(self):
        """Print a visual representation of the board in hexagonal shape"""
        def format_tile(tile):
            # Get first letter of resource (W=Wood, B=Brick, O=Ore, S=Sheep, H=wHeat, D=Desert)
            resource = tile.resource_type[0].upper()
            if resource == 'W' and tile.resource_type == 'wood':
                resource = 'T'  # Use 'T' (Tree) for wheat to avoid confusion with wheat 
            padding = "" if len(str(tile.number_token)) == 2 else " "
            return f"{resource}{tile.number_token}{padding}" 

        rows = [
            [(0,0), (1,0), (2,0)],
            [(0,1), (1,1), (2,1), (3,1)],
            [(0,2), (1,2), (2,2), (3,2), (4,2)],
            [(0,3), (1,3), (2,3), (3,3)],
            [(0,4), (1,4), (2,4)]
        ]

        board_str = ""
        for i, row in enumerate(rows):
            indent = "  " * (5 - len(row))
            board_str += indent

            for q, r in row:
                tile = next((t for t in self.tiles if t.q == q and t.r == r), None)
                board_str += f"{format_tile(tile)} "
            board_str += "\n"
        board_str = board_str.rstrip()
            
        print(board_str)
# Create and initialize the board
board = Board()
board.print_board()