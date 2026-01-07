// Catan Multiplayer Game Client
let socket;
let gameState = null;
let myPlayerId = null;
let myGameId = null;
let buildMode = null; // 'settlement', 'city', 'road'
let selectedRoadStart = null;

// Resource colors
const RESOURCE_COLORS = {
    wood: '#2d5016',
    brick: '#9c4221',
    wheat: '#f1c40f',
    sheep: '#95a5a6',
    ore: '#566573',
    desert: '#c19a6b'
};

// Player colors
const PLAYER_COLORS = ['#FF0000', '#0000FF', '#FFFFFF', '#FFA500'];

// Initialize socket connection
function initSocket() {
    socket = io();

    socket.on('connected', (data) => {
        console.log('Connected to server:', data.session_id);
    });

    socket.on('join_success', (data) => {
        myPlayerId = data.player_id;
        myGameId = data.game_id;
        gameState = data.state;
        showGameLobby();
        updateLobby();
    });

    socket.on('player_joined', (data) => {
        gameState = data.state;
        updateLobby();
        showNotification(`${data.player_name} joined the game`, 'info');
    });

    socket.on('player_left', (data) => {
        gameState = data.state;
        updateLobby();
    });

    socket.on('game_started', (data) => {
        gameState = data.state;
        switchToGameScreen();
        updateUI();
        showNotification('Game started!', 'success');
    });

    socket.on('dice_rolled', (data) => {
        gameState = data.state;
        updateDiceDisplay(data.dice);
        updateUI();
        showNotification(`Rolled ${data.dice[0]} + ${data.dice[1]} = ${data.total}`, 'info');
    });

    socket.on('settlement_built', (data) => {
        gameState = data.state;
        updateUI();
        buildMode = null;
    });

    socket.on('city_built', (data) => {
        gameState = data.state;
        updateUI();
    });

    socket.on('road_built', (data) => {
        gameState = data.state;
        updateUI();
        buildMode = null;
        selectedRoadStart = null;
    });

    socket.on('dev_card_bought', (data) => {
        gameState = data.state;
        updateUI();
        showNotification(`You bought a ${data.card_type} card!`, 'success');
    });

    socket.on('player_bought_dev_card', (data) => {
        gameState = data.state;
        updateUI();
    });

    socket.on('knight_played', (data) => {
        gameState = data.state;
        updateUI();
        if (data.player_id === myPlayerId) {
            showRobberModal();
        }
    });

    socket.on('robber_moved', (data) => {
        gameState = data.state;
        updateUI();
        hideRobberModal();
    });

    socket.on('resources_discarded', (data) => {
        gameState = data.state;
        updateUI();
        hideDiscardModal();
    });

    socket.on('bank_trade_completed', (data) => {
        gameState = data.state;
        updateUI();
        hideTradeModal();
    });

    socket.on('trade_proposed', (data) => {
        gameState = data.state;
        updateUI();
        if (data.state.active_trade && data.state.active_trade.proposer !== myPlayerId) {
            showIncomingTrade();
        }
    });

    socket.on('trade_response_received', (data) => {
        gameState = data.state;
        updateUI();
        updateTradeResponses();
    });

    socket.on('trade_completed', (data) => {
        gameState = data.state;
        updateUI();
        hideTradeModal();
    });

    socket.on('trade_cancelled', (data) => {
        gameState = data.state;
        updateUI();
        hideIncomingTrade();
    });

    socket.on('turn_ended', (data) => {
        gameState = data.state;
        updateUI();
        buildMode = null;
        selectedRoadStart = null;
    });

    socket.on('game_finished', (data) => {
        gameState = data.state;
        updateUI();
        showNotification(`${data.winner_name} wins with ${gameState.players[data.winner_id].victory_points} victory points!`, 'success');
    });

    socket.on('chat_message', (data) => {
        addChatMessage(data.player_name, data.message);
    });

    socket.on('error', (data) => {
        showNotification(data.message, 'error');
    });
}

// Lobby functions
function createGame() {
    const playerName = document.getElementById('player-name-input').value || 'Player';

    fetch('/api/create-game', {
        method: 'POST'
    })
    .then(res => res.json())
    .then(data => {
        myGameId = data.game_id;
        socket.emit('join_game', {
            game_id: myGameId,
            player_name: playerName
        });
    });
}

function joinGame() {
    const gameId = document.getElementById('game-id-input').value;
    const playerName = document.getElementById('player-name-input').value || 'Player';

    if (!gameId) {
        showNotification('Please enter a game ID', 'error');
        return;
    }

    socket.emit('join_game', {
        game_id: gameId,
        player_name: playerName
    });
}

function showGameLobby() {
    document.getElementById('lobby-game-id').textContent = myGameId;
    document.getElementById('game-lobby').style.display = 'block';
}

function updateLobby() {
    const lobbyPlayers = document.getElementById('lobby-players');
    lobbyPlayers.innerHTML = '<h3>Players:</h3>';

    Object.values(gameState.players).forEach(player => {
        const playerDiv = document.createElement('div');
        playerDiv.className = 'player-item';
        playerDiv.innerHTML = `
            <div class="player-color" style="background: ${player.color}"></div>
            <span>${player.name}</span>
        `;
        lobbyPlayers.appendChild(playerDiv);
    });
}

function startGame() {
    socket.emit('start_game', {
        game_id: myGameId
    });
}

function switchToGameScreen() {
    document.getElementById('lobby-screen').classList.remove('active');
    document.getElementById('game-screen').classList.add('active');

    // Initialize canvas
    drawBoard();
}

// UI Update functions
function updateUI() {
    if (!gameState) return;

    updateTopBar();
    updatePlayersList();
    updateResourceCards();
    updateDevCards();
    updateActionButtons();
    drawBoard();
}

function updateTopBar() {
    document.getElementById('game-id-display').textContent = `Game: ${myGameId}`;
    document.getElementById('current-phase').textContent = `Phase: ${gameState.game_phase}`;

    const currentPlayer = gameState.players[gameState.current_player];
    if (currentPlayer) {
        document.getElementById('current-turn').textContent = `Turn: ${currentPlayer.name}`;
    }

    // Update dice button
    const rollBtn = document.getElementById('roll-dice-btn');
    const isMyTurn = gameState.current_player === myPlayerId;
    const canRoll = gameState.turn_phase === 'waiting_for_roll';
    rollBtn.disabled = !(isMyTurn && canRoll);
}

function updateDiceDisplay(dice) {
    if (dice) {
        document.getElementById('die1').textContent = dice[0];
        document.getElementById('die2').textContent = dice[1];
    }
}

function updatePlayersList() {
    const playersList = document.getElementById('players-list');
    playersList.innerHTML = '';

    gameState.player_order.forEach(playerId => {
        const player = gameState.players[playerId];
        const isCurrentTurn = playerId === gameState.current_player;

        const playerCard = document.createElement('div');
        playerCard.className = 'player-card' + (isCurrentTurn ? ' current-turn' : '');
        playerCard.innerHTML = `
            <div class="player-name" style="color: ${player.color}">
                ${player.name} ${playerId === myPlayerId ? '(You)' : ''}
            </div>
            <div class="player-stats">
                <span>VP: ${player.victory_points}</span>
                <span>Cards: ${player.resource_count}</span>
                <span>Knights: ${player.knights_played}</span>
            </div>
            <div class="player-stats">
                <span>Roads: ${15 - player.roads_remaining}</span>
                <span>Settlements: ${5 - player.settlements_remaining}</span>
                <span>Cities: ${4 - player.cities_remaining}</span>
            </div>
        `;
        playersList.appendChild(playerCard);
    });
}

function updateResourceCards() {
    const resourceCards = document.getElementById('resource-cards');
    const myPlayer = gameState.players[myPlayerId];

    if (!myPlayer) return;

    resourceCards.innerHTML = '';
    const resources = ['wood', 'brick', 'wheat', 'sheep', 'ore'];

    resources.forEach(resource => {
        const count = myPlayer.resources[resource];
        const card = document.createElement('div');
        card.className = `resource-card ${resource}`;
        card.innerHTML = `
            <div>${resource.toUpperCase()}</div>
            <div style="font-size: 1.5em">${count}</div>
        `;
        resourceCards.appendChild(card);
    });
}

function updateDevCards() {
    const devCardsDiv = document.getElementById('dev-cards');
    const myPlayer = gameState.players[myPlayerId];

    if (!myPlayer) return;

    document.getElementById('dev-card-count').textContent = myPlayer.dev_card_count;

    devCardsDiv.innerHTML = '';
    // Note: We don't have access to the actual dev card types in the state
    // In a real implementation, you'd track which cards the player has
}

function updateActionButtons() {
    const isMyTurn = gameState.current_player === myPlayerId;
    const isMainPhase = gameState.turn_phase === 'main_phase';
    const isSetup = gameState.game_phase.includes('setup');

    const myPlayer = gameState.players[myPlayerId];
    if (!myPlayer) return;

    // Build settlement
    const canBuildSettlement = isSetup || (
        myPlayer.resources.wood >= 1 &&
        myPlayer.resources.brick >= 1 &&
        myPlayer.resources.wheat >= 1 &&
        myPlayer.resources.sheep >= 1 &&
        myPlayer.settlements_remaining > 0
    );
    document.getElementById('build-settlement-btn').disabled = !(isMyTurn && canBuildSettlement);

    // Build city
    const canBuildCity = !isSetup && (
        myPlayer.resources.wheat >= 2 &&
        myPlayer.resources.ore >= 3 &&
        myPlayer.cities_remaining > 0
    );
    document.getElementById('build-city-btn').disabled = !(isMyTurn && canBuildCity);

    // Build road
    const canBuildRoad = isSetup || (
        myPlayer.resources.wood >= 1 &&
        myPlayer.resources.brick >= 1 &&
        myPlayer.roads_remaining > 0
    );
    document.getElementById('build-road-btn').disabled = !(isMyTurn && canBuildRoad);

    // Buy dev card
    const canBuyDevCard = !isSetup && (
        myPlayer.resources.wheat >= 1 &&
        myPlayer.resources.sheep >= 1 &&
        myPlayer.resources.ore >= 1 &&
        gameState.dev_cards_remaining > 0
    );
    document.getElementById('buy-dev-card-btn').disabled = !(isMyTurn && isMainPhase && canBuyDevCard);

    // Trade
    document.getElementById('trade-btn').disabled = !(isMyTurn && isMainPhase);

    // End turn
    document.getElementById('end-turn-btn').disabled = !isMyTurn || isSetup;
}

// Board rendering
function drawBoard() {
    const canvas = document.getElementById('game-board');
    const ctx = canvas.getContext('2d');

    // Clear canvas
    ctx.fillStyle = '#4a90a4';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    if (!gameState || !gameState.board) return;

    const scale = 35;
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;

    // Draw hexes
    gameState.board.hexes.forEach(hex => {
        const [x, y] = axialToPixel(hex.q, hex.r, scale, centerX, centerY);
        drawHex(ctx, x, y, scale, hex);
    });

    // Draw roads
    gameState.board.roads.forEach(road => {
        const v1 = gameState.board.vertices.find(v => v.id === road.v1);
        const v2 = gameState.board.vertices.find(v => v.id === road.v2);
        if (v1 && v2) {
            const [x1, y1] = axialToPixel(v1.q, v1.r, scale, centerX, centerY);
            const [x2, y2] = axialToPixel(v2.q, v2.r, scale, centerX, centerY);

            const player = gameState.players[road.owner];
            ctx.strokeStyle = player ? player.color : '#333';
            ctx.lineWidth = 6;
            ctx.beginPath();
            ctx.moveTo(x1, y1);
            ctx.lineTo(x2, y2);
            ctx.stroke();
        }
    });

    // Draw buildings
    gameState.board.vertices.forEach(vertex => {
        if (vertex.building) {
            const [x, y] = axialToPixel(vertex.q, vertex.r, scale, centerX, centerY);
            const player = gameState.players[vertex.owner_id];

            ctx.fillStyle = player ? player.color : '#333';

            if (vertex.building === 'settlement') {
                // Draw triangle
                ctx.beginPath();
                ctx.moveTo(x, y - 10);
                ctx.lineTo(x - 8, y + 8);
                ctx.lineTo(x + 8, y + 8);
                ctx.closePath();
                ctx.fill();
                ctx.strokeStyle = '#000';
                ctx.lineWidth = 2;
                ctx.stroke();
            } else if (vertex.building === 'city') {
                // Draw square
                ctx.fillRect(x - 10, y - 10, 20, 20);
                ctx.strokeStyle = '#000';
                ctx.lineWidth = 2;
                ctx.strokeRect(x - 10, y - 10, 20, 20);
            }
        }
    });

    // Highlight valid build locations if in build mode
    if (buildMode === 'settlement') {
        highlightValidSettlements(ctx, scale, centerX, centerY);
    } else if (buildMode === 'road') {
        highlightValidRoads(ctx, scale, centerX, centerY);
    }
}

function drawHex(ctx, x, y, size, hex) {
    // Draw hexagon
    ctx.beginPath();
    for (let i = 0; i < 6; i++) {
        const angle = (Math.PI / 3) * i + Math.PI / 6;
        const hx = x + size * Math.cos(angle);
        const hy = y + size * Math.sin(angle);
        if (i === 0) {
            ctx.moveTo(hx, hy);
        } else {
            ctx.lineTo(hx, hy);
        }
    }
    ctx.closePath();

    // Fill with resource color
    ctx.fillStyle = RESOURCE_COLORS[hex.resource_type] || '#c19a6b';
    ctx.fill();
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 2;
    ctx.stroke();

    // Draw number token
    if (hex.number_token > 0) {
        ctx.fillStyle = '#fff';
        ctx.beginPath();
        ctx.arc(x, y, size * 0.4, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = '#333';
        ctx.stroke();

        ctx.fillStyle = hex.number_token === 6 || hex.number_token === 8 ? '#e74c3c' : '#000';
        ctx.font = 'bold 20px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(hex.number_token, x, y);

        // Draw pips
        const pips = getPipCount(hex.number_token);
        if (pips > 0) {
            ctx.fillStyle = hex.number_token === 6 || hex.number_token === 8 ? '#e74c3c' : '#000';
            for (let i = 0; i < pips; i++) {
                ctx.beginPath();
                ctx.arc(x - (pips - 1) * 4 + i * 8, y + 15, 2, 0, Math.PI * 2);
                ctx.fill();
            }
        }
    }

    // Draw robber
    if (hex.has_robber) {
        ctx.fillStyle = '#000';
        ctx.font = 'bold 24px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('🛡️', x, y - 20);
    }
}

function getPipCount(number) {
    const pips = {
        2: 1, 12: 1,
        3: 2, 11: 2,
        4: 3, 10: 3,
        5: 4, 9: 4,
        6: 5, 8: 5
    };
    return pips[number] || 0;
}

function axialToPixel(q, r, size, centerX, centerY) {
    const x = size * (3/2 * q) + centerX;
    const y = size * (Math.sqrt(3)/2 * q + Math.sqrt(3) * r) + centerY;
    return [x, y];
}

function highlightValidSettlements(ctx, scale, centerX, centerY) {
    // This would need to get valid settlement locations from the game state
    // For now, just highlight all empty vertices
    gameState.board.vertices.forEach(vertex => {
        if (!vertex.building) {
            const [x, y] = axialToPixel(vertex.q, vertex.r, scale, centerX, centerY);
            ctx.strokeStyle = '#48bb78';
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.arc(x, y, 12, 0, Math.PI * 2);
            ctx.stroke();
        }
    });
}

function highlightValidRoads(ctx, scale, centerX, centerY) {
    // Highlight valid road locations
    // This would need proper validation from game state
}

// Game actions
function rollDice() {
    socket.emit('roll_dice', {
        game_id: myGameId,
        player_id: myPlayerId
    });
}

function buildSettlement() {
    if (buildMode === 'settlement') {
        buildMode = null;
        drawBoard();
    } else {
        buildMode = 'settlement';
        selectedRoadStart = null;
        drawBoard();
    }
}

function buildCity() {
    // Cities are built by clicking on existing settlements
    showNotification('Click on one of your settlements to upgrade it', 'info');
}

function buildRoad() {
    if (buildMode === 'road') {
        buildMode = null;
        selectedRoadStart = null;
        drawBoard();
    } else {
        buildMode = 'road';
        drawBoard();
    }
}

function buyDevCard() {
    socket.emit('buy_dev_card', {
        game_id: myGameId,
        player_id: myPlayerId
    });
}

function endTurn() {
    socket.emit('end_turn', {
        game_id: myGameId,
        player_id: myPlayerId
    });
}

// Canvas click handler
document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('game-board');

    canvas.addEventListener('click', (event) => {
        if (!gameState || gameState.current_player !== myPlayerId) return;

        const rect = canvas.getBoundingClientRect();
        const clickX = event.clientX - rect.left;
        const clickY = event.clientY - rect.top;

        const scale = 35;
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;

        // Find closest vertex
        let closestVertex = null;
        let minDist = Infinity;

        gameState.board.vertices.forEach(vertex => {
            const [x, y] = axialToPixel(vertex.q, vertex.r, scale, centerX, centerY);
            const dist = Math.sqrt((clickX - x) ** 2 + (clickY - y) ** 2);
            if (dist < minDist && dist < 20) {
                minDist = dist;
                closestVertex = vertex;
            }
        });

        if (closestVertex) {
            if (buildMode === 'settlement') {
                socket.emit('build_settlement', {
                    game_id: myGameId,
                    player_id: myPlayerId,
                    vertex_id: closestVertex.id
                });
            } else if (buildMode === 'road') {
                if (!selectedRoadStart) {
                    selectedRoadStart = closestVertex.id;
                    drawBoard();
                } else {
                    socket.emit('build_road', {
                        game_id: myGameId,
                        player_id: myPlayerId,
                        vertex1_id: selectedRoadStart,
                        vertex2_id: closestVertex.id
                    });
                }
            } else if (closestVertex.building === 'settlement' && closestVertex.owner_id === myPlayerId) {
                // Upgrade to city
                socket.emit('build_city', {
                    game_id: myGameId,
                    player_id: myPlayerId,
                    vertex_id: closestVertex.id
                });
            }
        }

        // Find closest hex (for robber)
        if (gameState.turn_phase === 'moving_robber') {
            let closestHex = null;
            let minDist = Infinity;

            gameState.board.hexes.forEach(hex => {
                const [x, y] = axialToPixel(hex.q, hex.r, scale, centerX, centerY);
                const dist = Math.sqrt((clickX - x) ** 2 + (clickY - y) ** 2);
                if (dist < minDist && dist < scale) {
                    minDist = dist;
                    closestHex = hex;
                }
            });

            if (closestHex && !closestHex.has_robber) {
                socket.emit('move_robber', {
                    game_id: myGameId,
                    player_id: myPlayerId,
                    hex_id: closestHex.id,
                    steal_from_player_id: null // TODO: Implement steal selection
                });
            }
        }
    });
});

// Chat
function sendChat() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();

    if (message) {
        socket.emit('chat_message', {
            game_id: myGameId,
            player_id: myPlayerId,
            message: message
        });
        input.value = '';
    }
}

function addChatMessage(playerName, message) {
    const chatMessages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message';
    messageDiv.innerHTML = `<span class="player-name">${playerName}:</span> ${message}`;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Notifications
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Modal functions
function showTradeModal() {
    document.getElementById('trade-modal').classList.add('active');
}

function hideTradeModal() {
    document.getElementById('trade-modal').classList.remove('active');
}

function showRobberModal() {
    document.getElementById('robber-modal').classList.add('active');
}

function hideRobberModal() {
    document.getElementById('robber-modal').classList.remove('active');
}

function showDiscardModal() {
    document.getElementById('discard-modal').classList.add('active');
}

function hideDiscardModal() {
    document.getElementById('discard-modal').classList.remove('active');
}

function showIncomingTrade() {
    document.getElementById('incoming-trade').style.display = 'block';
}

function hideIncomingTrade() {
    document.getElementById('incoming-trade').style.display = 'none';
}

function updateTradeResponses() {
    // Update trade response UI
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    initSocket();

    // Lobby
    document.getElementById('create-game-btn').addEventListener('click', createGame);
    document.getElementById('join-game-btn').addEventListener('click', joinGame);
    document.getElementById('start-game-btn').addEventListener('click', startGame);

    // Actions
    document.getElementById('roll-dice-btn').addEventListener('click', rollDice);
    document.getElementById('build-settlement-btn').addEventListener('click', buildSettlement);
    document.getElementById('build-city-btn').addEventListener('click', buildCity);
    document.getElementById('build-road-btn').addEventListener('click', buildRoad);
    document.getElementById('buy-dev-card-btn').addEventListener('click', buyDevCard);
    document.getElementById('trade-btn').addEventListener('click', showTradeModal);
    document.getElementById('end-turn-btn').addEventListener('click', endTurn);

    // Chat
    document.getElementById('send-chat-btn').addEventListener('click', sendChat);
    document.getElementById('chat-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendChat();
    });

    // Modal close buttons
    document.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.target.closest('.modal').classList.remove('active');
        });
    });
});
