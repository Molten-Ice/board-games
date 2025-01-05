import json
import math
import tkinter as tk
from PIL import Image, ImageDraw


class Board:
    def __init__(self):
        self.hex_cells = []
        self.vertex_cells = []

    
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
                'owner': vertex_cell.owner,
                'building': vertex_cell.building
            } for vertex_cell in self.vertex_cells]
        }
    
    def get_neighbors(self, cell):
        def is_neighbor(spot1, spot2):
            return abs(spot1.q - spot2.q) <= 1 and abs(spot1.r - spot2.r) <= 1

        cells = self.hex_cells if isinstance(cell, HexCell) else self.vertex_cells
        return [c for c in cells if is_neighbor(c, cell)]

class Cell:
    def __init__(self, q, r):
        self.q = q
        self.r = r

    def is_neighbor(self, cell):
        return abs(self.q - cell.q) <= 1 and abs(self.r - cell.r) <= 1


class HexCell(Cell):
    def __init__(self, q, r, resource_type=None, resource_number=None):
        super().__init__(q, r)
        self.resource_type = resource_type
        self.resource_number = resource_number


class VertexCell(Cell):
    def __init__(self, q, r, owner=None, building=None):
        super().__init__(q, r)
        self.owner = owner
        self.building = building


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

    color, point_size = '#9B6400', 5
    for hex_cell in board.hex_cells:
        q, r = hex_cell.q, hex_cell.r
        x, y = visualization_get_hex_coordinates(q, r)
        canvas.create_oval(
            x-point_size, y-point_size, 
            x+point_size, y+point_size,
            fill=color, outline=color
        )

    color, point_size = '#FFFFFF', 3
    for vertex_cell in board.vertex_cells:
        q, r = vertex_cell.q, vertex_cell.r
        x, y = visualization_get_hex_coordinates(q, r)
        canvas.create_oval(
            x-point_size, y-point_size, 
            x+point_size, y+point_size,
            fill=color, outline=color
        )

    # Save the canvas to an image
    def save_canvas_to_image():
        canvas.postscript(file='canvas.ps', colormode='color')
        img = Image.open('canvas.ps')
        img.save('canvas_image.png', 'png')

    save_canvas_to_image()

    root.mainloop()

if __name__ == "__main__":

    board = Board()
    board.hex_cells, board.vertex_cells = generate_hex_grid()
    with open('board.json', 'w') as f:
        json.dump(board.get_board_state(), f, indent=2)

    visualization_hex_coordinates(board)