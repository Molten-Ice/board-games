import requests
import json
from pprint import pprint

BASE_URL = 'http://localhost:5000/api'

def test_api():
    # Test reset board with settlement cutoff
    print("\n=== Testing /reset-board with settlement cutoff ===")
    data = {'board_type': 'settlement_cutoff'}
    response = requests.post(f'{BASE_URL}/reset-board', json=data)
    assert response.status_code == 200, "Reset board failed"
    board_state = response.json()
    print("Game reset successfully with settlement cutoff board")
    
    # Test get board s
    # Test get board state
    print("\n=== Testing /board-state ===")
    response = requests.get(f'{BASE_URL}/board-state')
    assert response.status_code == 200, "Get board state failed"
    board_state = response.json()['board']
    print("Board state retrieved successfully")
    print(board_state)
    
    # Get possible actions for player 1
    for key in board_state['next_actions']:
        next_actions = board_state['next_actions'].get(key, {})
        print(f"\nAvailable actions for player {key}:")
        pprint(next_actions)
 
    print(f'current player: {board_state["current_player"]}')
    # Convert current_player to string when accessing next_actions
    print(f'type of current player: {type(board_state["current_player"])}')
    next_actions = board_state['next_actions'][board_state['current_player']]
    print(f'----- Next actions to act on -----\n')
    pprint(next_actions)
    
    # Test build city
    print("\n=== Testing /build-city ===")
    if 'city' in next_actions and len(next_actions['city']) > 0:
        city_location = next_actions['city'][0]  # Take first available city location
        data = {
            'vertex_id': city_location,
            'player_id': '1'
        }
        print(f"Attempting to upgrade settlement to city at vertex {city_location}")
        response = requests.post(f'{BASE_URL}/build-city', json=data)
        assert response.status_code == 200, "Build city failed"
        print(f"City built successfully at vertex {city_location}")
        board_state = response.json()['board']
        # Update next_actions from the current player's perspective
        next_actions = board_state['next_actions'][board_state['current_player']]
    else:
        print("No valid city locations available")

    # Test place settlement
    print("\n=== Testing /place-settlement ===")
    if 'settlement' in next_actions and len(next_actions['settlement']) > 0:
        vertex_id = next_actions['settlement'][0]  # Should be vertex 44
        data = {
            'vertex_id': vertex_id,
            'player_id': '1'
        }
        print(f"Attempting to place settlement at vertex {vertex_id}")
        response = requests.post(f'{BASE_URL}/place-settlement', json=data)
        assert response.status_code == 200, "Place settlement failed"
        print(f"Settlement placed successfully at vertex {vertex_id}")
        board_state = response.json()['board']
        next_actions = board_state['next_actions'].get('1', {})
    else:
        print("No valid settlement locations available")

    # Test place road
    print("\n=== Testing /place-road ===")
    start_vertex, end_vertex = next_actions['roads'][0]  # Take first available road location
    data = {
        'start_vertex': start_vertex,
        'end_vertex': end_vertex,
        'player_id': '1'
    }
    print(f"Attempting to place road between vertices {start_vertex} and {end_vertex}")
    response = requests.post(f'{BASE_URL}/place-road', json=data)
    assert response.status_code == 200, "Place road failed"
    print(f"Road placed successfully between vertices {start_vertex} and {end_vertex}")
    board_state = response.json()['board']

    # Print final game state
    print("\n=== Final Game State ===")
    print("Players:")
    for player_id, resources in board_state['players'].items():
        print(f"Player {player_id}: {resources}")
    
    print("\nNext possible actions:")
    pprint(board_state['next_actions'])

if __name__ == "__main__":
    try:
        test_api()
        print("\n✅ All tests passed successfully!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the server. Make sure the Flask app is running on http://localhost:5000")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Debug info:")
        import traceback
        traceback.print_exc() 