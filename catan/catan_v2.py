import json
import math
import random
import tkinter as tk
from enum import Enum


"""
TODO:
Place stuff on a vertex (settlements, cities)
Player resources
bank resources (total)
Collect resources from a hex.
dice -> hexes -> adjacent players settlements/cities -> no wheat = Defeat

# roads, dict(a, b) - > player_id


# Last
robber
dev cards - largest army, longest road, victory point
trading
"""


class Board:
    def __init__(self):
        self.hex_cells = []
        self.vertex_cells = []
        self.road_edges = {}
        self.bank = Bank()
        self.players = [Player(pid) for pid in range(1, 5)]

    def get_board_state(self):
        return {
            'hexes': [{
                'q': hex_cell.q,
                'r': hex_cell.r,
                'resource_type': hex_cell.resource_type,
                'resource_number': hex_cell.resource_number
            } for hex_cell in self.hex_cells],
            'vertex_cells': [{
                'q': vertex_cell.q,
                'r': vertex_cell.r,
                'owner_id': vertex_cell.owner_id,
                'building': vertex_cell.building.name if vertex_cell.building else None
            } for vertex_cell in self.vertex_cells],
            'road_edges': self.road_edges
        }


CellType = Enum('CellType', ['hex', 'vertex'])
BuildingType = Enum('BuildingType', ['settlement', 'city'])
ResourceType = Enum('ResourceType', ['wood', 'brick', 'wheat', 'sheep', 'ore'])
    
class Player:
    def __init__(self, pid):
        self.pid = pid # 1-4
        self.resources = {
            ResourceType.wood: 0,
            ResourceType.brick: 0,
            ResourceType.wheat: 0,
            ResourceType.sheep: 0,
            ResourceType.ore: 0
        }

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


class VertexCell(Cell):
    def __init__(self, q, r, owner_id=None, building=None):
        super().__init__(q, r, CellType.vertex)
        self.owner_id = owner_id
        self.building = building


def is_neighbor(spot1, spot2):
    diffs = [(1, 0), (0, 1), (-1, 0), (0, -1), (1, -1), (-1, 1)]
    diff = (spot1.q - spot2.q, spot1.r - spot2.r)
    return diff in diffs

# def valid_settlements(board):
    # Find settlement spots


def collect_resources(board):
    dice = random.randint(1, 6) + random.randint(1, 6)
    for hex_cell in board.hex_cells:
        if hex_cell.number_token != dice or hex_cell.robber:
            continue
        adjacent_vertex_cells = [c for c in board.vertex_cells if is_neighbor(c, hex_cell)]
        for vertex_cell in adjacent_vertex_cells:
            if not vertex_cell.building:
                continue
            factor = 1 if vertex_cell.building == BuildingType.settlement else 2
            print(f'Collecting {factor} {hex_cell.resource_type} from {vertex_cell.owner_id}')
            board.bank.resources[hex_cell.resource_type] += factor


def generate_hex_grid():
    hex_cells = []
    vertex_cells = []
    
    hex_radius = 5
    for q in range(-hex_radius, hex_radius+1):
        valid_q_hex_points = q != -hex_radius and q != hex_radius
        r1 = max(-hex_radius, -q - hex_radius)
        r2 = min(hex_radius, -q + hex_radius)
        for r in range(r1, r2+1):
            valid_r_hex_points = r != r1 and r != r2
            hex_point = (q-r) % 3 == 0 and (2*q + r) % 3 == 0
            if hex_point:
                if valid_q_hex_points and valid_r_hex_points: # Skips hexes on outer rim
                    hex_cells.append(HexCell(q, r, hex_point))
            else:
                vertex_cells.append(VertexCell(q, r))

    print(f'len(vertex_cells) (before filtering): {len(vertex_cells)}')
    filtered_vertex_cells = list(filter(
        lambda c: any(c.is_neighbor(h) for h in hex_cells),
        vertex_cells
    ))
    print(f'len(vertex_cells) (after filtering): {len(filtered_vertex_cells)}')
    return hex_cells, filtered_vertex_cells

def visualization_hex_coordinates(board, sf=30.0):
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

    color, point_size = '#9B6400', 5
    for hex_cell in board.hex_cells:
        q, r = hex_cell.q, hex_cell.r
        x, y = visualization_get_hex_coordinates(q, r)
        canvas.create_oval(
            x-point_size, y-point_size, 
            x+point_size, y+point_size,
            fill=color, outline=color
        )

    for vertex_cell in board.vertex_cells:
        q, r = vertex_cell.q, vertex_cell.r
        x, y = visualization_get_hex_coordinates(q, r)
        
        # Check if the vertex has a building
        if vertex_cell.building:
            # Use a larger circle for settlements
            point_size = 7 if vertex_cell.building == BuildingType.settlement else 5
            color = player_colors.get(vertex_cell.owner_id, '#FFFFFF')  # Default to white if no owner
        else:
            point_size = 3
            color = '#FFFFFF'  # Default color for unoccupied vertices

        canvas.create_oval(
            x-point_size, y-point_size, 
            x+point_size, y+point_size,
            fill=color, outline=color
        )

    root.mainloop()

if __name__ == "__main__":

    board = Board()
    board.hex_cells, board.vertex_cells = generate_hex_grid()

   
    for i in range(2):
        vertex_cell = [v for v in board.vertex_cells if v.building is None][0]
        vertex_cell.owner_id = 1
        vertex_cell.building = BuildingType.settlement

    print(f'len(board.vertex_cells): {len(board.vertex_cells)}')
    with open('board.json', 'w') as f:
        json.dump(board.get_board_state(), f, indent=2)

    visualization_hex_coordinates(board)