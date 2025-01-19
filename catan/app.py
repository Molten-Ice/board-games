import os
import pickle
from copy import deepcopy
from flask import Flask, jsonify, request
from flask_cors import CORS

from catan import BoardUtils, EndpointHelpers, ExampleBoards


app = Flask(__name__)
CORS(app)

os.makedirs('games', exist_ok=True)
GAME_STATE_FILE = 'games/game_state1.pkl'

def save_game_state(board):
    """Save game state to pickle file"""
    with open(GAME_STATE_FILE, 'wb') as f:
        pickle.dump(board, f)

def load_game_state():
    """Load game state from pickle file"""
    if os.path.exists(GAME_STATE_FILE):
        with open(GAME_STATE_FILE, 'rb') as f:
            return pickle.load(f)
    
    print('load_game_state | Setting up new game')
    # board = EndpointHelpers.handle_start_game()
    board = ExampleBoards.example_settlement_cutoff_board()
    return board
        

@app.route('/api/start-game', methods=['POST'])
def start_game():
    """Initialize a new game"""
    board = load_game_state()
    save_game_state(board)
    return jsonify({'board': board.get_board_state()})

@app.route('/api/board-state', methods=['GET'])
def get_board_state():
    board = load_game_state()
    return jsonify({'board': board.get_board_state()})

@app.route('/api/roll-dice', methods=['POST'])
def roll_dice():
    """Roll dice and collect resources"""
    board = load_game_state()
    output_board = EndpointHelpers.handle_roll_dice(board)
    save_game_state(output_board)
    return jsonify({'prev_board': board.get_board_state(get_next_actions=False), 'board': output_board.get_board_state()})


@app.route('/api/place-settlement', methods=['POST'])
def place_settlement():
    """Place a settlement at the specified vertex""" 
    data = request.get_json()
    vertex_id = data.get('vertex_id')
    player_id = data.get('player_id')
    
    board = load_game_state()
    output_board = EndpointHelpers.handle_place_settlement(board, vertex_id, player_id)
    save_game_state(output_board)
    return jsonify({'prev_board': board.get_board_state(get_next_actions=False), 'board': output_board.get_board_state()})

@app.route('/api/place-road', methods=['POST'])
def place_road():
    """Place a road between two vertices"""
    data = request.get_json()
    start_vertex = data.get('start_vertex')
    end_vertex = data.get('end_vertex')
    player_id = data.get('player_id')

    board = load_game_state()
    output_board = EndpointHelpers.handle_place_road(board, start_vertex, end_vertex, player_id)
    save_game_state(output_board)
    return jsonify({'prev_board': board.get_board_state(get_next_actions=False), 'board': output_board.get_board_state()})
    

@app.route('/api/end-turn', methods=['POST'])
def end_turn():
    """End current player's turn and move to next player"""
    board = load_game_state()
    output_board = EndpointHelpers.handle_end_turn(board)
    save_game_state(output_board)
    return jsonify({'prev_board': board.get_board_state(get_next_actions=False), 'board': output_board.get_board_state()})

@app.route("/api/build-city", methods=['POST'])
def build_city():
    """Upgrade a settlement to a city at the specified vertex"""
   
    data = request.get_json()
    vertex_id = data.get('vertex_id')
    player_id = data.get('player_id')

    board = load_game_state()
    output_board = EndpointHelpers.handle_build_city(board, vertex_id, player_id)
    save_game_state(output_board)
    return jsonify({'prev_board': board.get_board_state(get_next_actions=False), 'board': output_board.get_board_state()})

if __name__ == "__main__":
    app.run(debug=True) 
