import time
import random
import tkinter as tk
from copy import deepcopy

class Game2048:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("2048")
        self.grid_size = 4
        self.cell_size = 100
        self.grid = [[0] * self.grid_size for _ in range(self.grid_size)]
        
        # Add ESC binding
        self.root.bind("<Escape>", lambda e: self.root.destroy())
        
        # Create button frame
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack()
        
        # Add score label
        self.score_label = tk.Label(self.button_frame, text="Score: 0", font=("Arial", 16, "bold"))
        self.score_label.pack(side=tk.LEFT, padx=10)
        
        # Add AI Move button
        self.ai_button = tk.Button(self.button_frame, text="AI Move", command=self.make_ai_move)
        self.ai_button.pack(side=tk.LEFT)
        
        # Colors for different numbers
        self.colors = {
            0: "#cdc1b4",
            2: "#eee4da",
            4: "#ede0c8",
            8: "#f2b179",
            16: "#f59563",
            32: "#f67c5f",
            64: "#f65e3b",
            128: "#edcf72",
            256: "#edcc61",
            512: "#edc850",
            1024: "#edc53f",
            2048: "#edc22e"
        }

        # Create canvas
        self.canvas = tk.Canvas(
            self.root,
            width=self.cell_size * self.grid_size,
            height=self.cell_size * self.grid_size,
            bg='#bbada0'
        )
        self.canvas.pack()

        # Bind arrow keys
        self.root.bind("<Left>", lambda e: self.move("left"))
        self.root.bind("<Right>", lambda e: self.move("right"))
        self.root.bind("<Up>", lambda e: self.move("up"))
        self.root.bind("<Down>", lambda e: self.move("down"))

        # Initialize game
        self.add_new_tile()
        self.add_new_tile()
        self.draw_grid()

    def add_new_tile(self):
        empty_cells = [
            (i, j) for i in range(self.grid_size) 
            for j in range(self.grid_size) if self.grid[i][j] == 0
        ]
        if empty_cells:
            i, j = random.choice(empty_cells)
            self.grid[i][j] = 2 if random.random() < 0.9 else 4

    def draw_grid(self):
        self.canvas.delete("all")
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                x1 = j * self.cell_size + 5
                y1 = i * self.cell_size + 5
                x2 = x1 + self.cell_size - 10
                y2 = y1 + self.cell_size - 10
                
                value = self.grid[i][j]
                color = self.colors.get(value, "#ff0000")
                
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, width=0)
                if value != 0:
                    self.canvas.create_text(
                        (x1 + x2) / 2,
                        (y1 + y2) / 2,
                        text=str(value),
                        font=("Arial", 24, "bold")
                    )

    def _merge_line(self, line, direction):
        """Helper function to merge a single line in the given direction"""
        if direction in ["right", "down"]:
            line.reverse()
        
        # Merge
        new_line = [0] * self.grid_size
        index = 0
        prev = None
        for num in (x for x in line if x != 0):
            if prev is None:
                prev = num
            elif prev == num:
                new_line[index] = prev * 2
                index += 1
                prev = None
            else:
                new_line[index] = prev
                index += 1
                prev = num
        if prev is not None:
            new_line[index] = prev
        
        if direction in ["right", "down"]:
            new_line.reverse()
        return new_line

    def is_valid_move(self, direction, grid):
        test_grid = [row[:] for row in grid]
        
        if direction in ["left", "right"]:
            for i in range(self.grid_size):
                line = test_grid[i][:]
                test_grid[i] = self._merge_line(line, direction)
        else:  # up or down
            for j in range(self.grid_size):
                line = [test_grid[i][j] for i in range(self.grid_size)]
                new_line = self._merge_line(line, direction)
                for i in range(self.grid_size):
                    test_grid[i][j] = new_line[i]

        return test_grid != grid

    def update_score(self):
        """Update the score display"""
        score = sum(sum(row) for row in self.grid)
        self.score_label.config(text=f"Score: {score}")

    def move(self, direction):
        if not self.is_valid_move(direction, self.grid):
            print(f"Invalid move: {direction}")  # Add warning for invalid moves
            # Check if any moves are possible
            possible_moves = ["up", "down", "left", "right"]
            if not any(self.is_valid_move(move, self.grid) for move in possible_moves):
                print("\n" + "="*50)
                print("GAME OVER - NO MORE VALID MOVES POSSIBLE!")
                print("="*50 + "\n")
            return False
            
        original_grid = [row[:] for row in self.grid]
        
        if direction in ["left", "right"]:
            for i in range(self.grid_size):
                line = self.grid[i][:]
                self.grid[i] = self._merge_line(line, direction)
        else:  # up or down
            for j in range(self.grid_size):
                line = [self.grid[i][j] for i in range(self.grid_size)]
                new_line = self._merge_line(line, direction)
                for i in range(self.grid_size):
                    self.grid[i][j] = new_line[i]

        # If grid changed, add new tile after delay
        if self.grid != original_grid:
            self.draw_grid()
            self.update_score()  # Update score after successful move
            self.root.after(100, self.add_new_tile)  # 100ms delay
            self.root.after(101, self.draw_grid)     # Redraw after new tile
            return True
        
        return False

    def run(self):
        self.root.mainloop()

    def __str__(self):
        """Returns a string representation of the game board"""
        # Calculate the width needed for each cell based on the largest number
        max_num = max(max(row) for row in self.grid)
        cell_width = len(str(max_num))
        
        # Create the string representation
        board_str = ""
        for row in self.grid:
            # Create a row string with proper spacing
            row_str = " | ".join(str(num).center(cell_width) if num != 0 else " " * cell_width for num in row)
            board_str += f"|{row_str}|\n"
            board_str += "-" * (len(row_str) + 2) + "\n"  # Add separator line
        
        return board_str[:-1]  # Remove the last newline

    def make_ai_move(self):
        """Handler for AI Move button"""
        ai = Game2048AI(self)
        if not ai.is_game_over():
            ai.play_best_move()

class Game2048AI:
    def __init__(self, game):
        self.game = game
        
    def get_state(self):
        """Returns current grid state"""
        return deepcopy(self.game.grid)
    
    def get_score(self):
        """Calculate current score (sum of all tiles)"""
        return sum(sum(row) for row in self.game.grid)
    
    def get_empty_cells(self):
        """Returns number of empty cells"""
        return sum(row.count(0) for row in self.game.grid)
    
    def make_move(self, direction):
        """
        Make a move and return if it was valid
        direction: "up", "down", "left", "right"
        Returns: True if move was valid, False otherwise
        """
        return self.game.move(direction)
    
    def get_possible_moves(self):
        """Returns list of valid moves"""
        moves = []
        for direction in ["up", "down", "left", "right"]:
            if self.game.is_valid_move(direction, self.game.grid):
                moves.append(direction)
        return moves
    
    def is_game_over(self):
        """Check if game is over"""
        return len(self.get_possible_moves()) == 0

    def get_best_move(self, depth=0, max_depth=5):
        """
        Recursively find the best move by looking ahead up to max_depth moves
        Returns: (best_move, best_score) tuple
        """
        # Base cases
        if depth >= max_depth:
            return None, self.get_score()
        
        possible_moves = self.get_possible_moves()
        if not possible_moves:
            return None, self.get_score()

        # Try each possible move
        best_move = None
        best_score = float('-inf')
        
        for move in possible_moves:
            # Save current state
            current_state = deepcopy(self.game.grid)
            
            # Make move
            self.make_move(move)
            
            # Recursively evaluate this path
            _, score = self.get_best_move(depth + 1, max_depth)
            
            # Restore state
            self.game.grid = current_state
            
            # Update best move if this score is higher
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move, best_score

    def play_best_move(self):
        """Makes the best move according to the recursive search"""
        t0 = time.time()
        print('Getting best move')
        print(f'Previous board:\n{str(self.game)}')
        # Check if game is already over
        if self.is_game_over():
            print("\n" + "="*50)
            print("GAME OVER - NO MORE VALID MOVES POSSIBLE!")
            print("="*50 + "\n")
            return
        
        # best_move, _ = self.get_best_move()
        best_move = self.get_possible_moves()[0]
        print(f'get_possible_moves: {self.get_possible_moves()}')
        print(f'Board after get_best_move:\n{str(self.game)}')
        print(f'Best move: "{best_move}" found in {time.time() - t0:.2f}s ')
        if best_move:

            self.make_move(best_move)
            print(f'New board:\n{str(self.game)}')
        else:
            print('WARNING, no best move found.')

# Remove the ai_player function and the automatic AI setup
if __name__ == "__main__":
    game = Game2048()
    game.run()