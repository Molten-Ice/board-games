import time
import random
import tkinter as tk
from copy import deepcopy

class CoreGame2048:
    """Core game logic without any visualization"""
    def __init__(self):
        self.grid_size = 4
        self.grid = [[0] * self.grid_size for _ in range(self.grid_size)]
        self.score = 0
        
        # Initialize game
        self.add_new_tile()
        self.add_new_tile()

    def add_new_tile(self):
        empty_cells = [
            (i, j) for i in range(self.grid_size) 
            for j in range(self.grid_size) if self.grid[i][j] == 0
        ]
        if empty_cells:
            i, j = random.choice(empty_cells)
            self.grid[i][j] = 2 if random.random() < 0.9 else 4

    def _merge_line(self, line, direction):
        """Helper function to merge a single line in the given direction"""
        if direction in ["right", "down"]:
            line.reverse()
        
        # Merge
        new_line = [0] * self.grid_size
        index = 0
        prev = None
        score_increase = 0  # Track score increase
        for num in (x for x in line if x != 0):
            if prev is None:
                prev = num
            elif prev == num:
                merged_value = prev * 2
                new_line[index] = merged_value
                score_increase += merged_value  # Add to score increase instead of self.score
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
        return new_line, score_increase

    def is_valid_move(self, direction, grid=None):
        if grid is None:
            grid = self.grid
            
        test_grid = [row[:] for row in grid]
        
        if direction in ["left", "right"]:
            for i in range(self.grid_size):
                line = test_grid[i][:]
                test_grid[i] = self._merge_line(line, direction)[0]
        else:  # up or down
            for j in range(self.grid_size):
                line = [test_grid[i][j] for i in range(self.grid_size)]
                new_line, _ = self._merge_line(line, direction)
                for i in range(self.grid_size):
                    test_grid[i][j] = new_line[i]

        return test_grid != grid

    def move(self, direction):
        """Move all tiles in the given direction and merge if possible"""
        if direction not in ["up", "down", "left", "right"]:
            return False

        # Store the current grid state to check if it changes
        old_grid = [row[:] for row in self.grid]
        
        # Process each line based on direction
        score_increase = 0  # Track total score increase
        if direction in ["up", "down"]:
            for col in range(self.grid_size):
                line = [self.grid[row][col] for row in range(self.grid_size)]
                new_line, line_score = self._merge_line(line, direction)  # Get score from merge
                score_increase += line_score  # Add to total score increase
                for row in range(self.grid_size):
                    self.grid[row][col] = new_line[row]
        else:  # left or right
            for row in range(self.grid_size):
                line = self.grid[row][:]
                new_line, line_score = self._merge_line(line, direction)  # Get score from merge
                score_increase += line_score  # Add to total score increase
                self.grid[row] = new_line

        # Check if the grid changed
        if old_grid != self.grid:
            self.score += score_increase  # Add the total score increase here
            self.add_new_tile()
            return True
        return False

    def get_possible_moves(self):
        """Returns list of valid moves"""
        return [direction for direction in ["up", "down", "left", "right"]
                if self.is_valid_move(direction)]

    def is_game_over(self):
        """Check if game is over"""
        return len(self.get_possible_moves()) == 0

    def __str__(self):
        """Returns a string representation of the game board"""
        max_num = max(max(row) for row in self.grid)
        cell_width = len(str(max_num))
        
        board_str = ""
        for row in self.grid:
            row_str = " | ".join(str(num).center(cell_width) if num != 0 else " " * cell_width for num in row)
            board_str += f"|{row_str}|\n"
            board_str += "-" * (len(row_str) + 2) + "\n"
        
        return board_str[:-1]

class Game2048(CoreGame2048):
    """Game with visualization layer"""
    def __init__(self):
        super().__init__()
        self.root = tk.Tk()
        self.root.title("2048")
        self.cell_size = 100
        
        # Setup visualization
        self.setup_visualization()
        self.draw_grid()

    def setup_visualization(self):
        """Setup all GUI elements"""
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
            0: "#cdc1b4", 2: "#eee4da", 4: "#ede0c8", 8: "#f2b179",
            16: "#f59563", 32: "#f67c5f", 64: "#f65e3b", 128: "#edcf72",
            256: "#edcc61", 512: "#edc850", 1024: "#edc53f", 2048: "#edc22e"
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
        self.root.bind("<Left>", lambda e: self.handle_move("left"))
        self.root.bind("<Right>", lambda e: self.handle_move("right"))
        self.root.bind("<Up>", lambda e: self.handle_move("up"))
        self.root.bind("<Down>", lambda e: self.handle_move("down"))

    def handle_move(self, direction):
        """Handle move and update visualization"""
        if self.move(direction):
            self.draw_grid()
            self.update_score()

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

    def update_score(self):
        """Update the score display"""
        self.score_label.config(text=f"Score: {self.score}")

    def make_ai_move(self):
        """Handler for AI Move button"""
        ai = Game2048AI(self)
        if not ai.is_game_over():
            ai.play_best_move()
            self.draw_grid()  # Update the visual grid
            self.update_score()  # Update the score display

    def run(self):
        self.root.mainloop()

class Game2048AI:
    def __init__(self, game):
        self.game = game
        self.max_depth = 8
        
    def get_state(self):
        """Returns current grid state and score"""
        return deepcopy(self.game.grid), deepcopy(self.game.score)
    
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

    def get_best_move(self):
        """Returns the best move and its evaluation score using minimax"""
        best_score = float('-inf')
        best_move = None
        
        # Add timeout protection
        start_time = time.time()
        timeout = 5  # 5 seconds maximum
        
        for move in self.get_possible_moves():
            if time.time() - start_time > timeout:
                print("Search timed out")
                break
                
            # Create a deep copy for simulation
            test_grid = deepcopy(self.game.grid)
            test_score = self.game.score
            
            # Try move on the copy
            self.game.grid = deepcopy(test_grid)
            if self.make_move(move):
                score = self.minimax(self.max_depth - 1, False, start_time, timeout)
                
                if score > best_score:
                    best_score = score
                    best_move = move
            
            # Restore original state
            self.game.grid = test_grid
            self.game.score = test_score
        
        return best_move, best_score
    
    def minimax(self, depth, is_maximizing, start_time, timeout):
        """Minimax algorithm with depth limit and timeout"""
        if time.time() - start_time > timeout:
            return self.evaluate_position()
            
        if depth == 0 or self.is_game_over():
            return self.evaluate_position()
        
        if is_maximizing:
            max_eval = float('-inf')
            for move in self.get_possible_moves():
                # Create a deep copy for simulation
                test_grid = deepcopy(self.game.grid)
                test_score = self.game.score
                
                # Try move on the copy
                self.game.grid = deepcopy(test_grid)
                if self.make_move(move):
                    eval = self.minimax(depth - 1, False, start_time, timeout)
                    max_eval = max(max_eval, eval)
                
                # Restore state
                self.game.grid = test_grid
                self.game.score = test_score
            
            return max_eval if max_eval != float('-inf') else self.evaluate_position()
        
        else:  # Simulating random tile placement
            min_eval = float('inf')
            empty_cells = [(i, j) for i in range(self.game.grid_size) 
                          for j in range(self.game.grid_size) 
                          if self.game.grid[i][j] == 0]
            
            if not empty_cells:
                return self.evaluate_position()
            
            # Sample a few random positions for efficiency
            sample_size = min(2, len(empty_cells))  # Reduced sample size
            for i, j in random.sample(empty_cells, sample_size):
                for new_tile in [2]:  # Only try value 2 for efficiency
                    # Create a deep copy for simulation
                    test_grid = deepcopy(self.game.grid)
                    
                    # Place new tile
                    self.game.grid = deepcopy(test_grid)
                    self.game.grid[i][j] = new_tile
                    eval = self.minimax(depth - 1, True, start_time, timeout)
                    min_eval = min(min_eval, eval)
                    
                    # Restore state
                    self.game.grid = test_grid
            
            return min_eval if min_eval != float('inf') else self.evaluate_position()
    
    def evaluate_position(self):
        """
        Evaluate the current position based on:
        1. Total sum of all tiles
        2. Number of empty cells (weighted)
        """
        total_sum = sum(sum(row) for row in self.game.grid)
        empty_cells = self.get_empty_cells()
        
        # Weight empty cells more heavily
        empty_cell_weight = 10.0
        
        return total_sum + (empty_cells * empty_cell_weight)

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
        
        best_move, _ = self.get_best_move()
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