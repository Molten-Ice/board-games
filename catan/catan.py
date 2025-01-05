import time
import random
import tkinter as tk
from math import cos, sin, pi

def corner_pixel_coords(q, r, corner_index, 
                       tile_size=1.0, 
                       board_offset_q=2, 
                       board_offset_r=2):
    """
    Return a 'pixel-like' (x, y) for the corner corner_index of tile (q, r).
    This uses the same hex spacing logic from draw_board but in a normalized way.
    """
    # Approx offsets used in draw_board
    horizontal_offset = 1.732 * tile_size  # sqrt(3)
    vertical_offset   = 1.5   * tile_size

    # row_offset replicates logic in draw_board
    row_offset = 0
    if r == 0:
        row_offset = horizontal_offset
    elif r == 1:
        row_offset = horizontal_offset * 0.5
    elif r == 3:
        row_offset = horizontal_offset * 0.5
    elif r == 4:
        row_offset = horizontal_offset

    center_x = (q - board_offset_q) * horizontal_offset + row_offset
    center_y = (r - board_offset_r) * vertical_offset

    # Corner angles, same as draw_hex
    angle = (corner_index * pi / 3) + pi / 6
    corner_x = center_x + cos(angle) * tile_size
    corner_y = center_y + sin(angle) * tile_size

    # Round to mitigate floating-point mismatch
    return (round(corner_x, 3), round(corner_y, 3))

class HexTile:
    def __init__(self, resource_type, number_token, q=0, r=0):
        self.resource_type = resource_type
        self.number_token = number_token
        self.adjacent_tiles = []
        self.vertices = []
        self.q = q  # q coordinate in axial system
        self.r = r  # r coordinate in axial system

class Vertex:
    def __init__(self, q, r, vertex_position, pixel_x=0, pixel_y=0):
        # Axial coords for reference (you can keep them or remove them)
        self.q = q
        self.r = r
        self.vertex_position = vertex_position
        
        # Pixel coordinates used as the true key for unifying corners
        self.pixel_x = pixel_x
        self.pixel_y = pixel_y

        self.connected_tiles = []
        self.owner = None   # Which player (1-4) owns this vertex, if any
        self.connected_vertices = []
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
        # Key change: self.vertices is now keyed by (pixel_x, pixel_y)
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
        self.create_vertices()         # 3) Create and connect vertices
        self.assign_valid_number_tokens()  # 4) Assign dice numbers
    
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
        # These are the 6 directions in axial coordinates
        directions = [(1,0), (1,-1), (0,-1), (-1,0), (-1,1), (0,1)]
        
        for tile1 in self.tiles:
            for direction in directions:
                q = tile1.q + direction[0]
                r = tile1.r + direction[1]
                # Find if there's a tile at (q, r)
                for tile2 in self.tiles:
                    if tile2.q == q and tile2.r == r:
                        if tile2 not in tile1.adjacent_tiles:
                            tile1.adjacent_tiles.append(tile2)
                        if tile1 not in tile2.adjacent_tiles:
                            tile2.adjacent_tiles.append(tile1)

    def create_vertices(self):
        """
        Create or retrieve a single Vertex object for each of the 6 corners on each tile. 
        Then link corners around each tile so connected_vertices is populated.
        """
        for tile in self.tiles:
            corner_vertices = []
            # 6 corners
            for i in range(6):
                px, py = corner_pixel_coords(tile.q, tile.r, i, tile_size=1.0)
                
                # Use (px, py) as the dictionary key
                if (px, py) not in self.vertices:
                    # Create the vertex (store q, r, i for reference only if desired)
                    self.vertices[(px, py)] = Vertex(
                        q=tile.q,
                        r=tile.r,
                        vertex_position=i,
                        pixel_x=px,
                        pixel_y=py
                    )

                vertex = self.vertices[(px, py)]
                # Connect tile <-> vertex
                if tile not in vertex.connected_tiles:
                    vertex.connected_tiles.append(tile)
                if vertex not in tile.vertices:
                    tile.vertices.append(vertex)

                corner_vertices.append(vertex)

            # Now link adjacent corners around this tile 
            # so that vertex.connected_vertices is populated
            for i in range(6):
                v1 = corner_vertices[i]
                v2 = corner_vertices[(i + 1) % 6]
                if v2 not in v1.connected_vertices:
                    v1.connected_vertices.append(v2)
                if v1 not in v2.connected_vertices:
                    v2.connected_vertices.append(v1)

    def _collect_all_vertices(self):
        """
        Return a list of unique vertices. We can use the values from self.vertices
        directly since we're already ensuring uniqueness through pixel coordinates.
        """
        # Debug print to verify vertex count
        vertices = list(self.vertices.values())
        return vertices

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
        """
        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6)
        dice_sum = dice1 + dice2
        
        # For each tile with matching number
        for tile in self.tiles:
            if tile.number_token == dice_sum and tile.resource_type != 'desert':
                resource = tile.resource_type
                
                # For each vertex that touches this tile
                for vertex in tile.vertices:
                    if vertex.owner is not None and vertex.building:  # Must have both owner AND building
                        owner_player = self.players[vertex.owner - 1]
                        # Settlement => +1 resource, City => +2
                        amount = 2 if vertex.building == 'city' else 1
                        
                        # Only distribute if the bank has enough
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
    
    def get_valid_settlement_spots(self, player: Player):
        """
        Return a list of vertices where the given player *could* place a new settlement.
        Rules:
        - Vertex must not be occupied
        - Must be at least 2 edges away from any other settlement
        - Must be connected to at least one land tile (not off-board)
        """
        valid_spots = []
        all_vertices = self._collect_all_vertices()
        
        for v in all_vertices:
            # Add check for connected tiles to ensure vertex is on the board
            if (v.owner is None and 
                not self._has_nearby_settlement(v) and 
                len(v.connected_tiles) > 0):  # Must be connected to at least one tile
                valid_spots.append(v)
        
        # Debug print
        print(f"Found {len(valid_spots)} valid settlement spots")
        return valid_spots

    def _has_nearby_settlement(self, vertex):
        """Check if there's any settlement within 2 edges of this vertex."""
        # Check immediate neighbors
        for adjacent in vertex.connected_vertices:
            if adjacent.owner is not None:
                return True
            # Check neighbors of neighbors
            for second_adjacent in adjacent.connected_vertices:
                if second_adjacent.owner is not None:
                    return True
        return False

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
        Return all possible edges (v1, v2) that the player could build on. 
        Now we rely on vertex.connected_vertices rather than trying to 
        deduce adjacency manually.
        """
        edges = []
        all_vertices = self._collect_all_vertices()
        
        # We can track an edge in a set to avoid duplicates 
        # (since v1<->v2 is same as v2<->v1).
        seen_edges = set()
        
        for v in all_vertices:
            for adj in v.connected_vertices:
                # Sort the two vertices by their pixel coords to get a consistent ordering
                key = tuple(sorted([(v.pixel_x, v.pixel_y), (adj.pixel_x, adj.pixel_y)]))
                if key not in seen_edges:
                    seen_edges.add(key)
                    
                    # Check if there's already a road on this edge
                    if not self._edge_has_road(v, adj):
                        edges.append((v, adj))
        
        return edges

    def _edge_has_road(self, v1, v2):
        """
        If any player's roads occupy this edge, return True.
        """
        for p in self.players:
            for road in p.roads:
                if (road.vertex1 == v1 and road.vertex2 == v2) \
                   or (road.vertex1 == v2 and road.vertex2 == v1):
                    return True
        return False


class CatanGUI:
    def __init__(self, board):
        self.board = board
        self.root = tk.Tk()
        self.root.title("Catan Board")
        
        # Add key binding for Escape
        self.root.bind('<Escape>', lambda e: self.root.destroy())
        
        # Create main frame
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(expand=True, fill='both')
        
        # Create left frame for game board
        self.board_frame = tk.Frame(self.main_frame)
        self.board_frame.pack(side='left', expand=True, fill='both')
        
        # Create right frame for bank info
        self.bank_frame = tk.Frame(self.main_frame)
        self.bank_frame.pack(side='right', fill='y')
        
        # Create bottom frame for player resources
        self.player_frame = tk.Frame(self.root)
        self.player_frame.pack(side='bottom', fill='x')
        
        # Canvas setup
        self.canvas_width = 800
        self.canvas_height = 600
        self.canvas = tk.Canvas(self.board_frame, width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack()
        
        # Hex dimensions
        self.hex_size = 40
        self.center_x = self.canvas_width // 2
        self.center_y = self.canvas_height // 2
        
        self.player_colors = {
            1: '#ff0000',  # Red
            2: '#0000ff',  # Blue
            3: '#00ff00',  # Green
            4: '#ffff00'   # Yellow
        }
        
        # Create top-left frame for player navigation
        self.nav_frame = tk.Frame(self.main_frame)
        self.nav_frame.pack(side='top', anchor='nw', padx=10, pady=10)
        
        # Create bottom-right frame for player summary
        self.summary_frame = tk.Frame(self.main_frame)
        self.summary_frame.pack(side='right', anchor='se', padx=10, pady=10)
        
        # Create dice roll frame between nav_frame and summary_frame
        self.dice_frame = tk.Frame(self.main_frame)
        self.dice_frame.pack(side='top', pady=10)
        
        # Create dice roll button and label
        self.roll_button = tk.Button(self.dice_frame, 
                                   text="Roll Dice", 
                                   command=self.roll_dice,
                                   font=('Arial', 12))
        self.roll_button.pack()
        
        self.dice_result = tk.Label(self.dice_frame, 
                                  text="", 
                                  font=('Arial', 12))
        self.dice_result.pack(pady=5)
        
        # Create all UI elements in the correct order
        self.create_bank_display()
        self.create_player_navigation()
        self.create_player_summary()
        self.create_player_resources_display()  # This creates self.resource_header
        
        self.draw_board()
        self.update_displays()  # Now all UI elements exist when this is called
    
    def create_bank_display(self):
        """Create labels for bank resources"""
        tk.Label(self.bank_frame, text="Bank Resources", font=('Arial', 12, 'bold')).pack(pady=5)
        self.bank_labels = {}
        for resource in self.board.bank:
            self.bank_labels[resource] = tk.Label(self.bank_frame, text=f"{resource}: {self.board.bank[resource]}")
            self.bank_labels[resource].pack(pady=2)
    
    def create_player_navigation(self):
        """Create navigation arrows to switch between players"""
        prev_btn = tk.Button(self.nav_frame, 
                            text="←", 
                            command=self.prev_player,
                            font=('Arial', 16, 'bold'))
        prev_btn.pack(side='left', padx=5)
        
        self.current_player_label = tk.Label(self.nav_frame, 
                                           text=f"Player {self.board.current_player_index + 1}",
                                           font=('Arial', 12, 'bold'))
        self.current_player_label.pack(side='left', padx=10)
        
        next_btn = tk.Button(self.nav_frame, 
                            text="→", 
                            command=self.next_player,
                            font=('Arial', 16, 'bold'))
        next_btn.pack(side='left', padx=5)
    
    def create_player_summary(self):
        """Create summary of all players' card counts"""
        tk.Label(self.summary_frame, 
                text="Players Summary", 
                font=('Arial', 12, 'bold')).pack(pady=5)
        
        self.summary_labels = {}
        for player in self.board.players:
            frame = tk.Frame(self.summary_frame)
            frame.pack(fill='x', pady=2)
            
            # Create indicator for current player
            self.summary_labels[player.pid] = {
                'indicator': tk.Label(frame, text="►", width=2),
                'label': tk.Label(frame, 
                                text=f"Player {player.pid}: 0 cards",
                                fg=self.player_colors[player.pid])
            }
            self.summary_labels[player.pid]['indicator'].pack(side='left')
            self.summary_labels[player.pid]['label'].pack(side='left')
    
    def create_player_resources_display(self):
        """Modified to only show current player's resources"""
        self.player_labels = {}
        frame = tk.Frame(self.player_frame)
        frame.pack(padx=20, pady=5)
        
        # Header for current player
        self.resource_header = tk.Label(frame, 
                                      text=f"Player {self.board.current_player_index + 1} Resources",
                                      font=('Arial', 12, 'bold'))
        self.resource_header.pack()
        
        # Resource labels
        self.resource_labels = {}
        current_player = self.board.players[self.board.current_player_index]
        for resource in current_player.resources:
            label = tk.Label(frame, text=f"{resource}: {current_player.resources[resource]}")
            label.pack()
            self.resource_labels[resource] = label
    
    def next_player(self):
        """Switch to next player"""
        self.board.next_player_turn()
        self.update_displays()
    
    def prev_player(self):
        """Switch to previous player"""
        self.board.current_player_index = (self.board.current_player_index - 1) % len(self.board.players)
        self.update_displays()
    
    def update_displays(self):
        """Updated to handle all new displays"""
        # Update bank display
        for resource, label in self.bank_labels.items():
            label.config(text=f"{resource}: {self.board.bank[resource]}")
        
        # Update current player's resources
        current_player = self.board.players[self.board.current_player_index]
        self.resource_header.config(
            text=f"Player {current_player.pid} Resources",
            fg=self.player_colors[current_player.pid]
        )
        
        for resource, label in self.resource_labels.items():
            label.config(text=f"{resource}: {current_player.resources[resource]}")
        
        # Update player navigation
        self.current_player_label.config(
            text=f"Player {current_player.pid}",
            fg=self.player_colors[current_player.pid]
        )
        
        # Update summary and indicators
        for player in self.board.players:
            total_cards = sum(player.resources.values())
            self.summary_labels[player.pid]['label'].config(
                text=f"Player {player.pid}: {total_cards} cards"
            )
            # Show/hide current player indicator
            if player.pid == current_player.pid:
                self.summary_labels[player.pid]['indicator'].config(text="►")
            else:
                self.summary_labels[player.pid]['indicator'].config(text="")
    
    def draw_hex(self, x, y, resource_type, number):
        # Calculate hex corners - start at 30° (pi/6) to get vertical edges
        corners = []
        for i in range(6):
            angle = (i * pi / 3) + pi / 6  # Start at 30° (pi/6)
            corner_x = x + self.hex_size * cos(angle)
            corner_y = y + self.hex_size * sin(angle)
            corners.extend([corner_x, corner_y])
        
        # Color mapping
        colors = {
            'wood': '#2d4c1e',    # Dark green
            'brick': '#8b4513',   # Saddle brown
            'ore': '#808080',     # Gray
            'wheat': '#ffd700',   # Gold
            'sheep': '#90ee90',   # Light green
            'desert': '#f4a460'   # Sandy brown
        }
        
        # Draw hexagon
        self.canvas.create_polygon(corners, fill=colors.get(resource_type, 'white'), outline='black')
        
        # Draw number token and pips (if not desert)
        if resource_type != 'desert' and number > 0:
            # Red for 6 and 8, black for others
            text_color = 'red' if number in [6, 8] else 'black'
            
            # Draw the number
            self.canvas.create_text(x, y - 5, text=str(number), 
                                  fill=text_color, font=('Arial', 12, 'bold'))
            
            # Draw probability pips
            pip_counts = {
                2: 1, 12: 1,          # One pip
                3: 2, 11: 2,          # Two pips
                4: 3, 10: 3,          # Three pips
                5: 4, 9: 4,           # Four pips
                6: 5, 8: 5            # Five pips
            }
            
            # Get number of pips for this number
            num_pips = pip_counts.get(number, 0)
            
            # Draw pips
            pip_radius = 1
            pip_spacing = 4
            total_width = (num_pips - 1) * pip_spacing
            start_x = x - total_width/2
            
            for i in range(num_pips):
                pip_x = start_x + (i * pip_spacing)
                self.canvas.create_oval(pip_x - pip_radius, y + 5 - pip_radius,
                                      pip_x + pip_radius, y + 5 + pip_radius,
                                      fill=text_color, outline=text_color)
    
    def draw_settlement(self, x, y, player_id):
        size = 8
        color = self.player_colors.get(player_id, 'gray')
        self.canvas.create_rectangle(x - size, y - size, 
                                   x + size, y + size, 
                                   fill=color, outline='black')
    
    def draw_road(self, x1, y1, x2, y2, player_id):
        color = self.player_colors.get(player_id, 'gray')
        self.canvas.create_line(x1, y1, x2, y2, 
                              fill=color, width=3)

    def get_vertex_pixels(self, vertex):
        """
        Scale the normalized vertex coordinates to match the hex size and center them on screen.
        """
        horizontal_spacing = 1.732 * self.hex_size  # sqrt(3)
        vertical_spacing = 1.5 * self.hex_size
        
        # Apply the same row-specific offsets as the hexes
        row_offset = 0
        r = vertex.r
        if r == 0:
            row_offset = horizontal_spacing
        elif r == 1:
            row_offset = horizontal_spacing * 0.5
        elif r == 3:
            row_offset = horizontal_spacing * 0.5
        elif r == 4:
            row_offset = horizontal_spacing
        
        # Scale and offset the coordinates
        scaled_x = (vertex.pixel_x * horizontal_spacing) + row_offset
        scaled_y = vertex.pixel_y * vertical_spacing
        
        # Center on screen and adjust for board offset
        screen_x = self.center_x + scaled_x - (2 * horizontal_spacing)  # Subtract 2 tiles worth to match board centering
        screen_y = self.center_y + scaled_y - (2 * vertical_spacing)   # Subtract 2 tiles worth to match board centering
        
        return screen_x, screen_y

    def draw_board(self):
        # Clear the canvas first
        self.canvas.delete("all")
        
        # For hexagons to touch, the horizontal spacing should be 2 * hex_size * cos(30°)
        # and vertical spacing should be hex_size * (1 + sin(60°))
        horizontal_offset = self.hex_size * 1.732  # 2 * cos(30°) ≈ 1.732
        vertical_offset = self.hex_size * 1.5      # 1 + sin(60°) = 1.5
        
        for tile in self.board.tiles:
            # Convert axial coordinates to pixel coordinates
            # Add row-specific horizontal shifts
            row_offset = 0
            if tile.r == 0:  # First row
                row_offset = horizontal_offset
            elif tile.r == 1:  # Second row
                row_offset = horizontal_offset * 0.5
            elif tile.r == 3:  # Fourth row
                row_offset = horizontal_offset * 0.5
            elif tile.r == 4:  # Fifth row
                row_offset = horizontal_offset
            
            pixel_x = self.center_x + (tile.q - 2) * horizontal_offset + row_offset
            pixel_y = self.center_y + (tile.r - 2) * vertical_offset
            
            self.draw_hex(pixel_x, pixel_y, tile.resource_type, tile.number_token)
        
        # Draw settlements and roads
        for tile in self.board.tiles:
            for vertex in tile.vertices:
                if vertex.building:
                    x, y = self.get_vertex_pixels(vertex)
                    self.draw_settlement(x, y, vertex.owner)
        
        # Draw roads
        for player in self.board.players:
            for road in player.roads:
                x1, y1 = self.get_vertex_pixels(road.vertex1)
                x2, y2 = self.get_vertex_pixels(road.vertex2)
                self.draw_road(x1, y1, x2, y2, player.pid)

    def roll_dice(self):
        """Handle dice roll and resource distribution"""
        # Roll dice and distribute resources
        dice1, dice2 = self.board.roll_dice_and_distribute()
        dice_sum = dice1 + dice2
        
        # Update dice result label
        self.dice_result.config(text=f"Rolled: {dice1} + {dice2} = {dice_sum}")
        
        # Update all displays
        self.update_displays()

def calculate_pip_value(vertex):
    """
    Calculate total pip value for a vertex based on adjacent tiles.
    Returns a tuple of (total_value, num_tiles) where:
    - total_value = raw_pips * resource_importance
    - num_tiles is used as a tiebreaker
    """
    pip_values = {
        2: 1, 12: 1,    # One pip
        3: 2, 11: 2,    # Two pips
        4: 3, 10: 3,    # Three pips
        5: 4, 9: 4,     # Four pips
        6: 5, 8: 5      # Five pips
    }
    
    valid_tiles = [t for t in vertex.connected_tiles 
                    if t.resource_type != 'desert' and t.number_token > 0]
    num_tiles = len(valid_tiles)
    raw_pips = sum(pip_values.get(tile.number_token, 0) for tile in valid_tiles)
    return (raw_pips, num_tiles)

def auto_place_initial_settlements(board):
    """Auto-place initial settlements and roads for testing purposes."""
    for player in board.players:  # Currently just first player
        valid_spots = board.get_valid_settlement_spots(player)
        
        if valid_spots:
            # Calculate values and sort by both pip value and number of tiles
            spot_values = [(spot, calculate_pip_value(spot)) for spot in valid_spots]
            spot_values.sort(key=lambda x: (x[1][0], x[1][1]), reverse=True)

            # Print top 3 spots for verification
            print(f"\nPlayer {player.pid} top spots:")
            for spot, (pip_value, num_tiles) in spot_values[:1]:
                print(f"Spot at ({spot.q},{spot.r}) pos {spot.vertex_position}: "
                      f"{pip_value:.1f} pips, {num_tiles} tiles")
                print(f"  Adjacent resources: {[t.resource_type for t in spot.connected_tiles]}")
                # print(f"  Adjacent numbers: {[t.number_token for t in spot.connected_tiles]}")
            
            # Place at best spot
            best_spot = spot_values[0][0]
            best_spot.owner = player.pid
            best_spot.building = 'settlement'
            player.settlements += 1
            print(f'settlement for {player.pid} placed at {best_spot.vertex_position}')
            
            # Place road from settlement
            if best_spot.connected_vertices:
                road_end = random.choice(best_spot.connected_vertices)
                new_road = Road(best_spot, road_end, owner=player.pid)
                player.roads.append(new_road)

# ------------------------------------------------------------------------------
# Example usage / flow
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    board = Board()
    auto_place_initial_settlements(board)
    gui = CatanGUI(board)
    gui.root.mainloop()
    print('finished.')