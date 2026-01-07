"""
Catan Multiplayer Server
Flask + Socket.IO server for real-time multiplayer Catan
"""

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
import uuid
from typing import Dict
from game_engine import CatanGame

app = Flask(__name__)
app.config['SECRET_KEY'] = 'catan-secret-key-' + str(uuid.uuid4())
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Store active games
games: Dict[str, CatanGame] = {}

# Store player connections
player_sessions: Dict[str, dict] = {}  # {session_id: {game_id, player_id}}

# Player colors
PLAYER_COLORS = ['#FF0000', '#0000FF', '#FFFFFF', '#FFA500']  # Red, Blue, White, Orange


@app.route('/')
def index():
    """Serve the main game page"""
    return render_template('game.html')


@app.route('/api/create-game', methods=['POST'])
def create_game():
    """Create a new game"""
    game_id = str(uuid.uuid4())[:8]
    games[game_id] = CatanGame(game_id)
    return jsonify({'game_id': game_id})


@app.route('/api/games', methods=['GET'])
def list_games():
    """List all available games"""
    game_list = []
    for game_id, game in games.items():
        game_list.append({
            'game_id': game_id,
            'player_count': len(game.players),
            'max_players': game.max_players,
            'phase': game.game_phase.value
        })
    return jsonify({'games': game_list})


@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"Client connected: {request.sid}")
    emit('connected', {'session_id': request.sid})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"Client disconnected: {request.sid}")

    # Remove player from game if they were in one
    if request.sid in player_sessions:
        session_info = player_sessions[request.sid]
        game_id = session_info['game_id']
        player_id = session_info['player_id']

        if game_id in games:
            game = games[game_id]
            game.remove_player(player_id)

            # Notify other players
            socketio.emit('player_left', {
                'player_id': player_id,
                'state': game.get_state()
            }, room=game_id)

            # Clean up empty games
            if len(game.players) == 0:
                del games[game_id]

        del player_sessions[request.sid]


@socketio.on('join_game')
def handle_join_game(data):
    """Handle player joining a game"""
    game_id = data.get('game_id')
    player_name = data.get('player_name', f'Player {len(games[game_id].players) + 1}')

    if game_id not in games:
        emit('error', {'message': 'Game not found'})
        return

    game = games[game_id]

    # Assign player color
    color = PLAYER_COLORS[len(game.players) % len(PLAYER_COLORS)]

    # Generate player ID
    player_id = str(uuid.uuid4())[:8]

    # Add player to game
    if game.add_player(player_id, player_name, color):
        # Join Socket.IO room
        join_room(game_id)

        # Store session info
        player_sessions[request.sid] = {
            'game_id': game_id,
            'player_id': player_id
        }

        # Notify all players
        socketio.emit('player_joined', {
            'player_id': player_id,
            'player_name': player_name,
            'state': game.get_state()
        }, room=game_id)

        # Send join confirmation to the joining player
        emit('join_success', {
            'player_id': player_id,
            'game_id': game_id,
            'state': game.get_state()
        })
    else:
        emit('error', {'message': 'Game is full or already started'})


@socketio.on('start_game')
def handle_start_game(data):
    """Handle game start"""
    game_id = data.get('game_id')

    if game_id not in games:
        emit('error', {'message': 'Game not found'})
        return

    game = games[game_id]

    if game.start_game():
        socketio.emit('game_started', {
            'state': game.get_state()
        }, room=game_id)
    else:
        emit('error', {'message': 'Cannot start game (need at least 2 players)'})


@socketio.on('roll_dice')
def handle_roll_dice(data):
    """Handle dice roll"""
    game_id = data.get('game_id')
    player_id = data.get('player_id')

    if game_id not in games:
        emit('error', {'message': 'Game not found'})
        return

    game = games[game_id]
    result = game.roll_dice(player_id)

    if result:
        socketio.emit('dice_rolled', {
            'dice': result,
            'total': sum(result),
            'state': game.get_state()
        }, room=game_id)
    else:
        emit('error', {'message': 'Cannot roll dice now'})


@socketio.on('build_settlement')
def handle_build_settlement(data):
    """Handle settlement building"""
    game_id = data.get('game_id')
    player_id = data.get('player_id')
    vertex_id = data.get('vertex_id')

    if game_id not in games:
        emit('error', {'message': 'Game not found'})
        return

    game = games[game_id]

    if game.build_settlement(player_id, vertex_id):
        socketio.emit('settlement_built', {
            'player_id': player_id,
            'vertex_id': vertex_id,
            'state': game.get_state()
        }, room=game_id)
    else:
        emit('error', {'message': 'Cannot build settlement there'})


@socketio.on('build_city')
def handle_build_city(data):
    """Handle city building"""
    game_id = data.get('game_id')
    player_id = data.get('player_id')
    vertex_id = data.get('vertex_id')

    if game_id not in games:
        emit('error', {'message': 'Game not found'})
        return

    game = games[game_id]

    if game.build_city(player_id, vertex_id):
        socketio.emit('city_built', {
            'player_id': player_id,
            'vertex_id': vertex_id,
            'state': game.get_state()
        }, room=game_id)
    else:
        emit('error', {'message': 'Cannot build city there'})


@socketio.on('build_road')
def handle_build_road(data):
    """Handle road building"""
    game_id = data.get('game_id')
    player_id = data.get('player_id')
    vertex1_id = data.get('vertex1_id')
    vertex2_id = data.get('vertex2_id')

    if game_id not in games:
        emit('error', {'message': 'Game not found'})
        return

    game = games[game_id]

    if game.build_road(player_id, vertex1_id, vertex2_id):
        socketio.emit('road_built', {
            'player_id': player_id,
            'vertex1_id': vertex1_id,
            'vertex2_id': vertex2_id,
            'state': game.get_state()
        }, room=game_id)
    else:
        emit('error', {'message': 'Cannot build road there'})


@socketio.on('buy_dev_card')
def handle_buy_dev_card(data):
    """Handle development card purchase"""
    game_id = data.get('game_id')
    player_id = data.get('player_id')

    if game_id not in games:
        emit('error', {'message': 'Game not found'})
        return

    game = games[game_id]
    card = game.buy_development_card(player_id)

    if card:
        # Send card type only to the player who bought it
        emit('dev_card_bought', {
            'card_type': card.value,
            'state': game.get_state()
        })

        # Notify others (without revealing card type)
        socketio.emit('player_bought_dev_card', {
            'player_id': player_id,
            'state': game.get_state()
        }, room=game_id, skip_sid=request.sid)
    else:
        emit('error', {'message': 'Cannot buy development card'})


@socketio.on('play_knight')
def handle_play_knight(data):
    """Handle playing a knight card"""
    game_id = data.get('game_id')
    player_id = data.get('player_id')

    if game_id not in games:
        emit('error', {'message': 'Game not found'})
        return

    game = games[game_id]

    if game.play_knight_card(player_id):
        socketio.emit('knight_played', {
            'player_id': player_id,
            'state': game.get_state()
        }, room=game_id)
    else:
        emit('error', {'message': 'Cannot play knight card'})


@socketio.on('move_robber')
def handle_move_robber(data):
    """Handle moving the robber"""
    game_id = data.get('game_id')
    player_id = data.get('player_id')
    hex_id = data.get('hex_id')
    steal_from = data.get('steal_from_player_id')

    if game_id not in games:
        emit('error', {'message': 'Game not found'})
        return

    game = games[game_id]

    if game.move_robber(player_id, hex_id, steal_from):
        socketio.emit('robber_moved', {
            'player_id': player_id,
            'hex_id': hex_id,
            'stolen_from': steal_from,
            'state': game.get_state()
        }, room=game_id)
    else:
        emit('error', {'message': 'Cannot move robber there'})


@socketio.on('discard_resources')
def handle_discard_resources(data):
    """Handle resource discarding"""
    game_id = data.get('game_id')
    player_id = data.get('player_id')
    resources = data.get('resources', {})

    if game_id not in games:
        emit('error', {'message': 'Game not found'})
        return

    game = games[game_id]

    if game.discard_resources(player_id, resources):
        socketio.emit('resources_discarded', {
            'player_id': player_id,
            'state': game.get_state()
        }, room=game_id)
    else:
        emit('error', {'message': 'Invalid discard'})


@socketio.on('trade_with_bank')
def handle_trade_with_bank(data):
    """Handle trading with the bank"""
    game_id = data.get('game_id')
    player_id = data.get('player_id')
    give = data.get('give', {})
    receive = data.get('receive', {})

    if game_id not in games:
        emit('error', {'message': 'Game not found'})
        return

    game = games[game_id]

    if game.trade_with_bank(player_id, give, receive):
        socketio.emit('bank_trade_completed', {
            'player_id': player_id,
            'state': game.get_state()
        }, room=game_id)
    else:
        emit('error', {'message': 'Invalid bank trade'})


@socketio.on('propose_trade')
def handle_propose_trade(data):
    """Handle trade proposal"""
    game_id = data.get('game_id')
    player_id = data.get('player_id')
    offer = data.get('offer', {})
    request = data.get('request', {})

    if game_id not in games:
        emit('error', {'message': 'Game not found'})
        return

    game = games[game_id]

    if game.propose_player_trade(player_id, offer, request):
        socketio.emit('trade_proposed', {
            'state': game.get_state()
        }, room=game_id)
    else:
        emit('error', {'message': 'Cannot propose trade'})


@socketio.on('respond_to_trade')
def handle_respond_to_trade(data):
    """Handle trade response"""
    game_id = data.get('game_id')
    player_id = data.get('player_id')
    accept = data.get('accept', False)

    if game_id not in games:
        emit('error', {'message': 'Game not found'})
        return

    game = games[game_id]

    if game.respond_to_trade(player_id, accept):
        socketio.emit('trade_response_received', {
            'player_id': player_id,
            'accept': accept,
            'state': game.get_state()
        }, room=game_id)
    else:
        emit('error', {'message': 'Cannot respond to trade'})


@socketio.on('execute_trade')
def handle_execute_trade(data):
    """Handle trade execution"""
    game_id = data.get('game_id')
    player_id = data.get('player_id')
    trade_with = data.get('trade_with_player_id')

    if game_id not in games:
        emit('error', {'message': 'Game not found'})
        return

    game = games[game_id]

    if game.execute_trade(player_id, trade_with):
        socketio.emit('trade_completed', {
            'state': game.get_state()
        }, room=game_id)
    else:
        emit('error', {'message': 'Cannot execute trade'})


@socketio.on('cancel_trade')
def handle_cancel_trade(data):
    """Handle trade cancellation"""
    game_id = data.get('game_id')
    player_id = data.get('player_id')

    if game_id not in games:
        emit('error', {'message': 'Game not found'})
        return

    game = games[game_id]

    if game.cancel_trade(player_id):
        socketio.emit('trade_cancelled', {
            'state': game.get_state()
        }, room=game_id)
    else:
        emit('error', {'message': 'Cannot cancel trade'})


@socketio.on('end_turn')
def handle_end_turn(data):
    """Handle end of turn"""
    game_id = data.get('game_id')
    player_id = data.get('player_id')

    if game_id not in games:
        emit('error', {'message': 'Game not found'})
        return

    game = games[game_id]

    if game.end_turn(player_id):
        socketio.emit('turn_ended', {
            'state': game.get_state()
        }, room=game_id)

        # Check for winner
        if game.game_phase.value == 'finished':
            winner = max(game.players.values(), key=lambda p: p.victory_points)
            socketio.emit('game_finished', {
                'winner_id': winner.player_id,
                'winner_name': winner.name,
                'state': game.get_state()
            }, room=game_id)
    else:
        emit('error', {'message': 'Cannot end turn'})


@socketio.on('chat_message')
def handle_chat_message(data):
    """Handle chat messages"""
    game_id = data.get('game_id')
    player_id = data.get('player_id')
    message = data.get('message')

    if game_id not in games:
        return

    game = games[game_id]
    player = game.players.get(player_id)

    if player:
        socketio.emit('chat_message', {
            'player_id': player_id,
            'player_name': player.name,
            'message': message
        }, room=game_id)


if __name__ == '__main__':
    print("Starting Catan Multiplayer Server...")
    print("Access the game at: http://localhost:5000")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
