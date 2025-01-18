import json
from flask import Flask, jsonify, render_template
from catan import Board, auto_place_initial_settlements

app = Flask(__name__)

board = Board()
auto_place_initial_settlements(board)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/getBoardState")
def get_board_state():
    with open("board_state.json", "w") as f:
        json.dump(board.get_board_state(), f, indent=2)
    return jsonify(board.get_board_state())

@app.route("/api/rollDice", methods=['POST'])
def roll_dice():
    dice1, dice2 = board.roll_dice_and_distribute()
    return jsonify({"dice1": dice1, "dice2": dice2, "dice_sum": dice1 + dice2})

@app.route("/api/nextPlayer", methods=['POST'])
def next_player():
    p = board.next_player_turn()
    return jsonify({"current_player": p.pid})

@app.route("/api/prevPlayer", methods=['POST'])
def prev_player():
    p = board.prev_player_turn()
    return jsonify({"current_player": p.pid})

@app.route("/api/resetBoard", methods=['POST'])
def reset_board():
    global board
    board = Board()
    auto_place_initial_settlements(board)
    return jsonify({"status": "success", "message": "Board reset successfully"})

if __name__ == "__main__":
    app.run(debug=True) 