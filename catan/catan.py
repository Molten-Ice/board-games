import json
import math
import random
import tkinter as tk
from enum import Enum
from itertools import pairwise

def visualization_catan_board(board_state, sf=30.0):
    width, height = 800, 800

    def visualization_get_hex_coordinates(q, r):
        # Convert axial coordinates to pixel coordinates
        x = (3/2 * q)
        y = (math.sqrt(3)/2 * q + math.sqrt(3) * r)
        # Add offset to center the pattern
        x *= sf
        y *= sf

        x += width / 2  # Half of canvas width
        y += height / 2
        return x, y
    
    root = tk.Tk()
    root.title("Centered Hexagonal Pattern")
    
    # Bind the Escape key to close the window
    root.bind('<Escape>', lambda event: root.destroy())
    
    canvas = tk.Canvas(root, bg='black', width=width, height=height)
    canvas.pack()

    # Define colors for each player
    player_colors = {
        1: '#FF0000',  # Red
        2: '#00FF00',  # Green
        3: '#0000FF',  # Blue
        4: '#FFFF00'   # Yellow
    }

    # Draw hex cells
    color, point_size = '#9B6400', 5
    for hex_data in board_state['hexes']:
        q, r = hex_data['q'], hex_data['r']
        x, y = visualization_get_hex_coordinates(q, r)
        canvas.create_oval(
            x-point_size, y-point_size, 
            x+point_size, y+point_size,
            fill=color, outline=color
        )
        canvas.create_text(x, y + 15, text=f"({q},{r})", fill='white', font=('Arial', 8))

    # Draw vertex cells
    for vertex_data in board_state['vertex_cells']:
        q, r = vertex_data['q'], vertex_data['r']
        unique_id = vertex_data['unique_id']
        x, y = visualization_get_hex_coordinates(q, r)
        
        # Check if the vertex has a building
        if vertex_data['building']:
            # Use a larger circle for settlements
            point_size = 7 if vertex_data['building'] == 'settlement' else 5
            color = player_colors.get(vertex_data['owner_id'], '#FFFFFF')
        else:
            point_size = 3
            color = '#FFFFFF'

        canvas.create_oval(
            x-point_size, y-point_size, 
            x+point_size, y+point_size,
            fill=color, outline=color
        )
        canvas.create_text(x, y + 15, text=f"({q},{r}: {unique_id})", fill='white', font=('Arial', 8))

    # Draw roads
    vertex_coords = {v['unique_id']: (v['q'], v['r']) for v in board_state['vertex_cells']}
    for v1_id, v2_id, owner_id in board_state['roads']:
        q1, r1 = vertex_coords[v1_id]
        q2, r2 = vertex_coords[v2_id]
        x1, y1 = visualization_get_hex_coordinates(q1, r1)
        x2, y2 = visualization_get_hex_coordinates(q2, r2)
        
        color = player_colors.get(owner_id, '#FFFFFF')
        canvas.create_line(x1, y1, x2, y2, fill=color, width=3)

    root.mainloop()

def generate_hex_grid():
    hex_cells = []
    vertex_cells = []

    hex_radius = 5
    for q in range(-hex_radius, hex_radius+1):
        for r in range(max(-hex_radius, -q - hex_radius), min(hex_radius, -q + hex_radius)+1):
            if (q-r) % 3 == 0 and (2*q + r) % 3 == 0: # hex point
                hex_cells.append(HexCell(q, r))
            else:
                vertex_cells.append(VertexCell(q, r))

    hex_cells = [h for h in hex_cells if len([v for v in vertex_cells if v.is_neighbor(h)]) == 6]
    vertex_cells = [v for v in vertex_cells if len([h for h in hex_cells if h.is_neighbor(v)]) != 0]
    for i, node in enumerate(vertex_cells + hex_cells):
        node.unique_id = i

    for i, vertex in enumerate(vertex_cells): # calculating these once at board creation.
        vertex.neighbor_vertexes = sorted([v.unique_id for v in vertex_cells if is_neighbor(vertex, v)])
        vertex.neighbor_hexes = sorted([h.unique_id for h in hex_cells if h.is_neighbor(vertex)])

    for hex_cell in hex_cells:
        neighbor_hexes = []
        vertex_neighbors = [v for v in vertex_cells if v.is_neighbor(hex_cell)]
        for vertex_neighbor in vertex_neighbors:
            neighbour_hexes = [h for h in hex_cells if h.is_neighbor(vertex_neighbor)]
            neighbor_hexes.extend(neighbour_hexes)
        hex_cell.neighbor_hexes = sorted(list(set([h.unique_id for h in neighbor_hexes if h.unique_id != hex_cell.unique_id])))
        hex_cell.neighbor_vertexes = sorted(list(set([v.unique_id for v in vertex_cells if v.is_neighbor(hex_cell)])))

    hex_cells_dict = {h.unique_id: h for h in hex_cells}
    vertex_cells_dict = {v.unique_id: v for v in vertex_cells}
    return hex_cells_dict, vertex_cells_dict


class Board:
    def __init__(self):
        self.hex_cells = {}
        self.vertex_cells = {}
        self.bank = Bank()
        # Convert player IDs to strings
        self.players = {str(id): Player(str(id)) for id in range(1, 5)}
        self.current_player = '1'

    def get_board_state(self, get_next_actions=True):
        roads = []
        for vertex_cell in self.vertex_cells.values():
            for other_vertex_id, owner_id in vertex_cell.roads.items():
                roads.append((min(vertex_cell.unique_id, other_vertex_id), max(vertex_cell.unique_id, other_vertex_id), owner_id))
        roads = list(set(roads))

        if get_next_actions:
            # next_actions = {self.current_player: BoardUtils.possible_next_actions(self, self.current_player)}
            next_actions = {id: BoardUtils.possible_next_actions(self, id) for id in self.players.keys()}
        else:
            next_actions = {}

        return {
            'current_player': self.current_player,
            'hexes': [{
                'q': hex_cell.q,
                'r': hex_cell.r,
                'resource_type': hex_cell.resource_type.name,
                'resource_number': hex_cell.resource_number,
                'robber': hex_cell.robber
            } for hex_cell in self.hex_cells.values()],
            'vertex_cells': [{
                'q': vertex_cell.q,
                'r': vertex_cell.r,
                'unique_id': vertex_cell.unique_id,
                'owner_id': vertex_cell.owner_id,
                'building': vertex_cell.building.name if vertex_cell.building else None
            } for vertex_cell in self.vertex_cells.values()],
            'roads': roads,
            'bank': {k.name: v for k, v in self.bank.resources.items()},
            'players': {id: {k.name: v for k, v in player.resources.items()} for id, player in self.players.items()},
            'next_actions': next_actions
        }
    





CellType = Enum('CellType', ['hex', 'vertex'])
BuildingType = Enum('BuildingType', ['settlement', 'city'])
ResourceType = Enum('ResourceType', ['wood', 'brick', 'wheat', 'sheep', 'ore', 'desert'])
    
class Player:
    def __init__(self, pid):
        self.pid = pid  # Now a string "1"-"4"
        self.resources = {
            ResourceType.wood: 0,
            ResourceType.brick: 0,
            ResourceType.wheat: 0,
            ResourceType.sheep: 0,
            ResourceType.ore: 0
        }
        for k in self.resources.keys():
            self.resources[k] += 5


class Bank:
    def __init__(self):
        self.resources = {
            ResourceType.wood: 19,
            ResourceType.brick: 19,
            ResourceType.wheat: 19,
            ResourceType.sheep: 19,
            ResourceType.ore: 19
        }


class Cell:
    def __init__(self, q, r, cell_type):
        self.q = q
        self.r = r
        self.cell_type = cell_type

    def is_neighbor(self, cell):
        return abs(self.q - cell.q) <= 1 and abs(self.r - cell.r) <= 1


class HexCell(Cell):
    def __init__(self, q, r, resource_type=None, resource_number=None):
        super().__init__(q, r, CellType.hex)
        self.resource_type = resource_type
        self.resource_number = resource_number
        self.robber = False
        self.unique_id = None
        self.neighbor_hexes = [] # really 2 nodes away on graph.

    def __repr__(self):
        return f'[{self.unique_id}] ({self.q}, {self.r}), resource_type: {self.resource_type}, resource_number: {self.resource_number}, robber: {self.robber}'


class VertexCell(Cell):
    def __init__(self, q, r, owner_id=None, building=None):
        super().__init__(q, r, CellType.vertex)
        self.owner_id = owner_id
        self.building = building
        self.unique_id = None
        self.neighbor_vertexes = [] # neighbor vertex ids
        self.neighbor_hexes = []
        self.roads = {} # dict of {other_vertex_id: owner_id, ...} # Note: this is duplicated for both vertices.

    def __repr__(self):
        return f'[{self.unique_id}] ({self.q}, {self.r}), building: {self.building}, owner_id: {self.owner_id}, roads: {self.roads}'

def is_neighbor(spot1, spot2):
    diffs = [(1, 0), (0, 1), (-1, 0), (0, -1), (1, -1), (-1, 1)]
    diff = (spot1.q - spot2.q, spot1.r - spot2.r)
    return diff in diffs


class BoardUtils:
    @staticmethod
    def setup_board():
        board = Board()
        board.hex_cells, board.vertex_cells = generate_hex_grid()

        BoardUtils.setup_resources(board)
        BoardUtils.assign_valid_resource_numbers(board)
        return board

    @staticmethod
    def setup_resources(board):
        """Convert the old coordinate system to the new matrix-based one"""
        resources = [
            ResourceType.wood, ResourceType.wood, ResourceType.wood, ResourceType.wood,
            ResourceType.brick, ResourceType.brick, ResourceType.brick,
            ResourceType.ore, ResourceType.ore, ResourceType.ore,
            ResourceType.wheat, ResourceType.wheat, ResourceType.wheat, ResourceType.wheat,
            ResourceType.sheep, ResourceType.sheep, ResourceType.sheep, ResourceType.sheep,
            ResourceType.desert
        ]
        random.shuffle(resources)

        assert len(board.hex_cells) == len(resources), f'{len(board.hex_cells)} != {len(resources)}'

        for hex_cell, resource in zip(board.hex_cells.values(), resources):
            hex_cell.resource_type = resource
            if resource == ResourceType.desert:
                hex_cell.robber = True


    @staticmethod
    def assign_valid_resource_numbers(board, max_attempts=1000):
        """
        Phase 5: Assign dice roll values to non-desert tiles 
        so that no two '6' or '8' are adjacent.
        """
        resource_numbers = [2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12]
        non_desert_hexes = [h for h in board.hex_cells.values() if h.resource_type != ResourceType.desert]
        assert len(non_desert_hexes) == len(resource_numbers), f'{len(non_desert_hexes)} != {len(resource_numbers)}'

        def invalid_distribution(board):
            for h in board.hex_cells.values():
                if h.resource_number in [6, 8]:
                    for neighbor_id in h.neighbor_hexes:
                        if board.hex_cells[neighbor_id].resource_number in [6, 8]:
                            return True
            return False
        
        for tile in board.hex_cells.values(): # Deals with the edge case where the desert is left as None instead of -1
            tile.resource_number = -1

        for attempt in range(1, max_attempts+1):
            random.shuffle(resource_numbers)
            for i, tile in enumerate(non_desert_hexes):
                tile.resource_number = resource_numbers[i]
            if not invalid_distribution(board):
                print(f'Setting up resource numbers successfully after {attempt} attempts.')
                return

            print(f'Setting up resource numbers attempt {attempt} invalid, reseting and trying again.')
            for tile in board.hex_cells.values(): # Otherwise reset and try again
                tile.resource_number = -1
        raise Exception(f"Could not create valid number distribution after {max_attempts} attempts")
    
    @staticmethod
    def valid_settlements(board):
        starting_nodes = [v for v in board.vertex_cells.values() if v.building is None]

        def is_valid_spot(possible_spot):
            for neighbour_id in possible_spot.neighbor_vertexes:
                neighbour = board.vertex_cells[neighbour_id]
                if neighbour.building is not None:
                    # print(f'{possible_spot.unique_id} ({possible_spot.q}, {possible_spot.r}) is not a valid spot because {neighbour_id} ({neighbour.q}, {neighbour.r}) is occupied.')
                    return False
            return True

        valid_spots = []
        for possible_spot in starting_nodes:
            if is_valid_spot(possible_spot):
                valid_spots.append(possible_spot.unique_id)
        return valid_spots

    @staticmethod
    def valid_cities(board, owner_id):
        """Check user has resources before calling this function."""
        buildings = [v for v in board.vertex_cells.values() if v.owner_id == owner_id]
        settlements = [b for b in buildings if b.building == BuildingType.settlement]
        if len(settlements) == 5:
            print(f'{owner_id} has 5 settlements, so cannot build any more cities.')
            return []
        else:
            return [b.unique_id for b in buildings if b.building == BuildingType.city]

    @staticmethod
    def highest_production_spot(board):
        pip_values = {
            -1 : 0, # 'desert'
            2: 1, 12: 1,
            3: 2, 11: 2,
            4: 3, 10: 3,
            5: 4, 9: 4,
            6: 5, 8: 5
        }
        available_spots  = BoardUtils.valid_settlements(board)

        vertex_pips = []
        for vertex_id in available_spots:
            vertex = board.vertex_cells[vertex_id]
            neighbour_hexes =[board.hex_cells[hex_id] for hex_id in vertex.neighbor_hexes]
            neighbour_pips = [pip_values[hex.resource_number] for hex in neighbour_hexes]
            vertex_pips.append((sum(neighbour_pips), vertex_id))
        vertex_pips.sort(key=lambda x: x[0], reverse=True)
        return vertex_pips[0][1]
    
    @staticmethod
    def collect_resources(board, dice_roll, current_player_id="3"):
        player_order = []  # Wraps e.g. ["3", "4", "1", "2"]
        current = int(current_player_id)
        for i in range(4):  # 4 players total
            player_id = str(((current - 1 + i) % 4) + 1)
            player_order.append(player_id)

        for player_id in player_order:
            player_buildings = [v for v in board.vertex_cells.values() if v.owner_id == player_id]
            for building in player_buildings:
                for hex_id in building.neighbor_hexes:
                    hex = board.hex_cells[hex_id]
                    if hex.resource_number == dice_roll and not hex.robber:
                        factor = 1 if building.building == BuildingType.settlement else 2
                        if board.bank.resources[hex.resource_type] >= factor:
                            board.players[player_id].resources[hex.resource_type] += factor
                            board.bank.resources[hex.resource_type] -= factor
                            print(f'Collected {factor} {hex.resource_type.name} from {hex_id} for player {player_id}')
                        else:
                            print(f'Player {player_id} does not have enough resources to collect {factor} {hex.resource_type}')
                            if board.bank.resources[hex.resource_type] == 1:
                                print(f'Given 1 out of 2 of {hex.resource_type} to {player_id}')
                                board.players[player_id].resources[hex.resource_type] += 1
        return board

    @staticmethod
    def valid_origin_vertices(board, player_id):
        """
        Finds all valid vertices where a player could build their next road from.
        Uses BFS to explore all reachable vertices from each building.
        
        Returns:
            set: Vertex IDs that are valid starting points for new roads
        """
        from collections import deque
        
        # Start with all building locations as valid origins
        buildings = {v.unique_id for v in board.vertex_cells.values() 
                    if v.owner_id == player_id and v.building is not None}
        valid_origins = buildings.copy()
        
        # For each building, explore all connected paths
        for building_id in buildings:
            visited = {building_id}
            queue = deque([building_id])
            
            while queue:
                current_vertex_id = queue.popleft()
                current_vertex = board.vertex_cells[current_vertex_id]
                
                # Check all roads from this vertex
                for neighbor_id in current_vertex.roads:
                    # Skip if we've already visited this vertex
                    if neighbor_id in visited:
                        continue
                        
                    neighbor = board.vertex_cells[neighbor_id]
                    # Skip if blocked by opponent's building
                    if neighbor.building is not None and neighbor.owner_id != player_id:
                        continue
                        
                    # If this road belongs to the player, we can traverse it
                    if current_vertex.roads[neighbor_id] == player_id:
                        visited.add(neighbor_id)
                        queue.append(neighbor_id)
                        valid_origins.add(neighbor_id)
        
        return sorted(list(valid_origins))
    
    @staticmethod
    def possible_next_actions(board, player_id):
        actions = {'player_id' : player_id}
        player_buildings = [v for v in board.vertex_cells.values() if v.owner_id == player_id]
        cities = [b for b in player_buildings if b.building == BuildingType.city]
        settlements = [b for b in player_buildings if b.building == BuildingType.settlement]
        resources = board.players[player_id].resources
        if len(cities) < 5 and resources[ResourceType.ore] >= 3 and resources[ResourceType.wheat] >= 5:
            actions[BuildingType.city.name] = [v.unique_id for v in settlements]

        valid_vertices = BoardUtils.valid_origin_vertices(board, player_id)

        if len(settlements) < 5 and (resources[ResourceType.wood] > 0 and resources[ResourceType.brick] > 0 
                        and resources[ResourceType.wheat] > 0 and resources[ResourceType.sheep] > 0):
            all_valid_settlements = BoardUtils.valid_settlements(board)
        
            valid_settlement_spots = [v for v in all_valid_settlements if v in valid_vertices]
            actions[BuildingType.settlement.name] = valid_settlement_spots

        if resources[ResourceType.wood] > 0 and resources[ResourceType.brick] > 0:
            possible_roads = []
            for id in valid_vertices:
                vertex = board.vertex_cells[id]

                current_roads =  list(vertex.roads.keys())
                for road_id in vertex.neighbor_vertexes:
                    if road_id not in current_roads:
                        possible_roads.append((min(id, road_id), max(id, road_id)))
            possible_roads = sorted(list(set(possible_roads)))
            actions['roads'] = possible_roads
        return actions

class EndpointHelpers:

    @staticmethod
    def handle_roll_dice(board, current_player):
        """Handle dice rolling and resource collection logic"""
        dice1, dice2 = random.randint(1, 6), random.randint(1, 6)
        print(f'handle_roll_dice | Rolled dice: {dice1}, {dice2}')
        dice_sum = dice1 + dice2
        BoardUtils.collect_resources(board, dice_sum, current_player)
        return {
            'dice1': dice1,
            'dice2': dice2,
            'board': board.get_board_state()
        }

    @staticmethod
    def handle_place_road(board, raw_start_vertex, raw_end_vertex, player_id):
        """Handle road placement logic"""


        print(f'handle_place_road called with start_vertex: {raw_start_vertex}, end_vertex: {raw_end_vertex}, and player_id: {player_id}')
        start_vertex = min(raw_start_vertex, raw_end_vertex)
        end_vertex = max(raw_start_vertex, raw_end_vertex)
        print(f'start_vertex: {start_vertex}, end_vertex: {end_vertex}')
        
        
        possible_actions = BoardUtils.possible_next_actions(board, player_id)
        if 'roads' not in possible_actions or (start_vertex, end_vertex) not in possible_actions['roads']:
            raise ValueError('Invalid road placement')
        
        board.vertex_cells[start_vertex].roads[end_vertex] = player_id
        board.vertex_cells[end_vertex].roads[start_vertex] = player_id
        
        player = board.players[player_id]
        player.resources[ResourceType.wood] -= 1
        player.resources[ResourceType.brick] -= 1
        board.bank.resources[ResourceType.wood] += 1
        board.bank.resources[ResourceType.brick] += 1

        return board

    @staticmethod
    def handle_end_turn(board):
        """Handle end turn logic"""
        # Convert to int for calculation, then back to string
        current = int(board.current_player)
        new_player = str((current % 4) + 1)
        print(f'handle_end_turn called, old player: {board.current_player}, new player: {new_player}')
        board.current_player = new_player
        return board

    @staticmethod
    def handle_build_city(board, vertex_id, player_id):
        """Handle city building logic"""
        print(f'handle_build_city called with vertex_id: {vertex_id} and player_id: {player_id}')
        possible_actions = BoardUtils.possible_next_actions(board, player_id)
        if BuildingType.city.name not in possible_actions or vertex_id not in possible_actions[BuildingType.city.name]:
            print(f'No city placement possible for player {player_id}')
            return board
        vertex = board.vertex_cells[vertex_id]
        vertex.building = BuildingType.city
        
        player = board.players[player_id]
        player.resources[ResourceType.wheat] -= 2
        player.resources[ResourceType.ore] -= 3
        board.bank.resources[ResourceType.wheat] += 2
        board.bank.resources[ResourceType.ore] += 3
        return board
  

    @staticmethod
    def handle_place_settlement(board, vertex_id, player_id):
        """Handle settlement placement logic"""
        print(f'handle_place_settlement called with vertex_id: {vertex_id} and player_id: {player_id}')
        possible_actions = BoardUtils.possible_next_actions(board, player_id)
        if BuildingType.settlement.name not in possible_actions or vertex_id not in possible_actions[BuildingType.settlement.name]:
            print(f'No settlement placement possible for player {player_id}')
            return board
        
        vertex = board.vertex_cells[vertex_id]
        vertex.owner_id = player_id
        vertex.building = BuildingType.settlement
        
        player = board.players[player_id]
        for resource_type in [ResourceType.wood, ResourceType.brick, ResourceType.wheat, ResourceType.sheep]:
            player.resources[resource_type] -= 1
            board.bank.resources[resource_type] += 1
        return board

class ExampleBoards:
    @staticmethod
    def example_settlement_cutoff_board():
        board = BoardUtils.setup_board()

        ## Testing road length and settlment placement for road cut off
        # Player 1
        vertex_cell = board.vertex_cells[32]
        vertex_cell.owner_id = "1"
        vertex_cell.building = BuildingType.settlement
        vertex_cell.roads[38] = "1"
        board.vertex_cells[38].roads[32] = "1"

        board.vertex_cells[38].roads[37] = "1"
        board.vertex_cells[37].roads[38] = "1"

        board.vertex_cells[38].roads[44] = "1"
        board.vertex_cells[44].roads[38] = "1"

        vertex_cell = board.vertex_cells[37]
        vertex_cell.owner_id = "1"
        vertex_cell.building = BuildingType.settlement
        #Player 2
        vertex_cell = board.vertex_cells[25]
        vertex_cell.owner_id = "2"
        vertex_cell.building = BuildingType.settlement
        for start, end in pairwise([25, 31, 37, 43]):
            board.vertex_cells[start].roads[end] = "2"
            board.vertex_cells[end].roads[start] = "2"
        return board

    @staticmethod
    def example_highest_production_first_spots():
        def place_spot_for_owner_id(board, owner_id):
            vertex_id = BoardUtils.highest_production_spot(board)
            vertex_cell = board.vertex_cells[vertex_id]
            vertex_cell.owner_id = owner_id
            vertex_cell.building = BuildingType.settlement
            neighbour_id = random.choice(vertex_cell.neighbor_vertexes)
            vertex_cell.roads[neighbour_id] = owner_id
            board.vertex_cells[neighbour_id].roads[vertex_id] = owner_id
            for hex_id in vertex_cell.neighbor_hexes:
                resource_type = board.hex_cells[hex_id].resource_type
                if resource_type == ResourceType.desert:
                    continue
                board.players[owner_id].resources[resource_type] += 1
                board.bank.resources[resource_type] -= 1
            return board

        board = BoardUtils.setup_board()
        for owner_id in range(1, 5):
            board = place_spot_for_owner_id(board, str(owner_id))

        for owner_id in range(4, 0, -1):
            board = place_spot_for_owner_id(board, str(owner_id))
        return board



def print_resources(board):
    print(f'Bank resources: {[f"{k.name}: {v}" for k, v in board.bank.resources.items()]}')
    for id, player in board.players.items():
        print(f'Player {id} resources: {[f"{k.name}: {v}" for k, v in player.resources.items()]}')


"""
TODO:
ALlow users to interact with the board.

figure out where valid roads are allowed (need to do a tree search to check if it's connected to the road network - another players settlement could cut it off).
dev cards - largest army, longest road, victory point
trading
"""

"""
API:
actionable moves. Return a list of player ids with the thing each player can do

API interaction order:
a) roll dice 
-> backend picks up all resources. (frontend also given previous state so it can visualize)
-> player given option to place settlements, roads, cities, buy dev cards.
^ In the above the can also propose trades* (* leave to the later on to add in).

Next steps:
Allow the frontend to take the actions specificed in possible_next_actions, updating the resources store each time an action is taken.
"""



if __name__ == "__main__":
    import pickle
    with open('games/game_state1.pkl', 'rb') as f:
        board = pickle.load(f)

    visualization_catan_board(board.get_board_state())

# python -m http.server
# http://localhost:8000/catan_board.html