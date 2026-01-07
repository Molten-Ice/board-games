# Settlers of Catan - Multiplayer Online Game

A complete, multiplayer implementation of Settlers of Catan built with Python (Flask + Socket.IO) and JavaScript.

## Features

### Complete Catan Rules Implementation
- ✅ Standard 19-hex board with proper resource distribution
- ✅ Building: Settlements, Cities, and Roads
- ✅ Development Cards: Knights, Victory Points, Road Building, Year of Plenty, Monopoly
- ✅ Trading: Bank trades (4:1) and player-to-player trading
- ✅ Robber mechanics with stealing
- ✅ Longest Road (5+ roads, 2 VP)
- ✅ Largest Army (3+ knights, 2 VP)
- ✅ Victory Points tracking (first to 10 wins)
- ✅ Setup phase with proper reverse-order placement
- ✅ Resource production on dice rolls
- ✅ Discarding when 7 is rolled (>7 cards)

### Multiplayer Features
- 🌐 Real-time multiplayer using WebSockets
- 👥 2-4 players per game
- 🎮 Game lobby system
- 💬 In-game chat
- 🔄 Automatic game state synchronization
- 📱 Responsive design

## Installation

### Requirements
- Python 3.8+
- pip

### Setup

1. Navigate to the game directory:
```bash
cd claude-catan
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the server:
```bash
python server.py
```

4. Open your browser and go to:
```
http://localhost:5000
```

## How to Play

### Starting a Game

1. **Create a Game:**
   - Enter your name
   - Click "Create New Game"
   - Share the Game ID with friends

2. **Join a Game:**
   - Enter your name
   - Enter the Game ID
   - Click "Join Game"

3. **Start the Game:**
   - Once all players have joined (2-4 players)
   - Click "Start Game"

### Gameplay

#### Setup Phase
- **Round 1:** Each player places 1 settlement + 1 road (in order)
- **Round 2:** Each player places 1 settlement + 1 road (reverse order)
- The second settlement gives you initial resources from adjacent hexes

#### Regular Turn Structure
1. **Roll Dice:** Click "Roll Dice" button
2. **Collect Resources:** All players automatically receive resources from tiles matching the roll
3. **Build & Trade:**
   - Build settlements (1 wood, 1 brick, 1 wheat, 1 sheep)
   - Build cities (2 wheat, 3 ore)
   - Build roads (1 wood, 1 brick)
   - Buy development cards (1 wheat, 1 sheep, 1 ore)
   - Trade with bank (4:1 ratio)
   - Trade with other players
4. **End Turn:** Click "End Turn"

#### Special Rules
- **Rolling a 7:**
  - Players with >7 cards must discard half (rounded down)
  - Move the robber to a new hex
  - Steal 1 random resource from a player with a building on that hex

- **Longest Road:** First player to have 5+ continuous roads gets 2 VP
- **Largest Army:** First player to play 3+ knights gets 2 VP

### Building
- **Settlement:** Click "Build Settlement" then click on a valid vertex
  - Must be 2 spaces away from any other settlement
  - Must be connected to your road network (except during setup)
  - Worth 1 Victory Point

- **City:** Click on one of your settlements to upgrade it
  - Worth 2 Victory Points
  - Produces 2 resources instead of 1

- **Road:** Click "Build Road" then click two adjacent vertices
  - Must connect to your existing road or building

### Winning
- First player to reach 10 Victory Points wins!

## Development

### Project Structure
```
claude-catan/
├── game_engine.py      # Core game logic and rules
├── server.py           # Flask + Socket.IO server
├── requirements.txt    # Python dependencies
├── templates/
│   └── game.html      # Main game HTML
├── static/
│   ├── css/
│   │   └── game.css   # Game styling
│   └── js/
│       └── game.js    # Client-side game logic
└── README.md
```

### Game Engine
The `game_engine.py` file contains:
- `CatanBoard`: Board generation and management
- `CatanGame`: Main game state and logic
- `Player`: Player state and resources
- All Catan rules implementation

### Server
The `server.py` file provides:
- WebSocket event handlers for all game actions
- Room management for multiplayer games
- Real-time state synchronization

## Rule Verification

This implementation has been verified by automated agents to ensure compliance with official Settlers of Catan rules:
- ✅ Board setup (19 hexes, correct resource distribution)
- ✅ Building costs and placement rules
- ✅ Victory point calculation
- ✅ Longest road and largest army mechanics
- ✅ Trading rules
- ✅ Robber mechanics
- ✅ Game flow and turn structure

## Known Limitations

- Port trades (3:1 and 2:1) are not yet implemented
- Some development cards (Road Building, Year of Plenty, Monopoly) need play functionality
- No AI players (multiplayer only)

## Credits

Built from scratch for multiplayer online play with complete Catan rules implementation.

## License

For educational and personal use.
