// Canvas references
let canvas, ctx;

// Some constants for drawing
const HEX_SIZE = 40;     
const CENTER_X = 450;    
const CENTER_Y = 300;    
const PIP_VALUES = {
  2: 1, 12: 1,    // One pip
  3: 2, 11: 2,    // Two pips
  4: 3, 10: 3,    // Three pips
  5: 4, 9: 4,     // Four pips
  6: 5, 8: 5      // Five pips
};

// On page load:
window.addEventListener("DOMContentLoaded", () => {
  canvas = document.getElementById("catanCanvas");
  ctx = canvas.getContext("2d");

  // Set up button event listeners
  document.getElementById("rollDiceBtn").addEventListener("click", rollDice);
  document.getElementById("nextPlayerBtn").addEventListener("click", nextPlayer);
  document.getElementById("prevPlayerBtn").addEventListener("click", prevPlayer);
  document.getElementById("resetBoardBtn").addEventListener("click", resetBoard);

  // Initial fetch and draw
  refreshBoardState();
});

async function refreshBoardState() {
  const response = await fetch("/api/getBoardState");
  const data = await response.json();
  drawBoard(data);
  updateUI(data);
}

async function rollDice() {
  const response = await fetch("/api/rollDice", {
    method: "POST"
  });
  const result = await response.json();
  document.getElementById("diceResult").textContent =
    `Rolled: ${result.dice1} + ${result.dice2} = ${result.dice_sum}`;
  refreshBoardState();
}

async function nextPlayer() {
  const response = await fetch("/api/nextPlayer", {
    method: "POST"
  });
  await response.json();
  refreshBoardState();
}

async function prevPlayer() {
  const response = await fetch("/api/prevPlayer", {
    method: "POST"
  });
  await response.json();
  refreshBoardState();
}

async function resetBoard() {
  const response = await fetch("/api/resetBoard", {
    method: "POST"
  });
  await response.json();
  refreshBoardState();
}

function drawBoard(data) {
  // Clear canvas
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Draw tiles
  data.tiles.forEach(tile => drawHexTile(tile));
  
  // Draw edges/roads
  data.edges.forEach(edge => {
    if (edge.owner) {
      drawRoad(edge);
    }
  });
  
  // Draw settlements/cities last (on top)
  data.vertices.forEach(v => {
    if (v.owner && v.building) {
      drawSettlement(v);
    }
  });
}

function drawHexTile(tile) {
  // Get the center point
  const center = axialToPixel(tile.q, tile.r);
  
  // Draw the hex using corner points
  ctx.beginPath();
  for (let i = 0; i < 6; i++) {
    const corner = axialToPixel(tile.q, tile.r, i);
    if (i === 0) ctx.moveTo(corner.x, corner.y);
    else ctx.lineTo(corner.x, corner.y);
  }
  ctx.closePath();

  const colorMap = {
    "wood":  "#2d4c1e",
    "brick": "#8b4513",
    "ore":   "#808080",
    "wheat": "#ffd700",
    "sheep": "#90ee90",
    "desert":"#f4a460"
  };
  
  ctx.fillStyle = colorMap[tile.resource_type] || "white";
  ctx.fill();
  ctx.strokeStyle = "black";
  ctx.stroke();

  if (tile.resource_type !== "desert" && tile.number_token > 0) {
    // Draw the number
    ctx.fillStyle = (tile.number_token === 6 || tile.number_token === 8) ? "red" : "black";
    ctx.font = "14px Arial";
    ctx.textAlign = "center";
    ctx.fillText(`${tile.number_token}`, center.x, center.y);
    
    // Draw the pips with smaller size and tighter spacing
    const pips = PIP_VALUES[tile.number_token];
    const pipRadius = 1.4;  // Reduced from 1.5
    const pipSpacing = 5; // Reduced from 4
    const pipStartX = center.x - ((pips - 1) * pipSpacing) / 2;
    
    for (let i = 0; i < pips; i++) {
      ctx.beginPath();
      ctx.arc(pipStartX + (i * pipSpacing), center.y + 8, pipRadius, 0, Math.PI * 2);
      ctx.fill();
    }
  }
}

function axialToPixel(q, r, cornerIndex = null) {
  // Constants for hex geometry
  const size = HEX_SIZE;
  // Use exact measurements for perfect tiling
  const width = size * Math.sqrt(3);
  const height = size * 2;
  
  // Convert axial coordinates to pixel coordinates (hex center)
  const x = CENTER_X + width * (q + r/2);
  const y = CENTER_Y + height * (r * 3/4);
  
  // If no cornerIndex provided, return hex center
  if (cornerIndex === null) {
    return { x, y };
  }
  
  // Use exact 60-degree angles for corners
  const cornerAngles = [
    Math.PI/6,      // 0 (top-right)
    Math.PI/2,      // 1 (right)
    5*Math.PI/6,    // 2 (bottom-right)
    7*Math.PI/6,    // 3 (bottom-left)
    3*Math.PI/2,    // 4 (left)
    11*Math.PI/6    // 5 (top-left)
  ];
  
  // Calculate corner position with exact size
  const angle = cornerAngles[cornerIndex];
  return {
    x: x + size * Math.cos(angle),
    y: y + size * Math.sin(angle)
  };
}

function drawSettlement(vertex) {
  const pos = axialToPixel(vertex.q, vertex.r, vertex.corner_index);
  
  const size = 8;
  const colorMap = {
      1: "red",
      2: "blue",
      3: "green",
      4: "yellow"
  };
  
  ctx.fillStyle = colorMap[vertex.owner] || "gray";
  ctx.fillRect(pos.x - size/2, pos.y - size/2, size, size);
  ctx.strokeStyle = "black";
  ctx.strokeRect(pos.x - size/2, pos.y - size/2, size, size);
}

function drawRoad(edge) {
    const colorMap = {
        1: "red",
        2: "blue",
        3: "green",
        4: "yellow"
    };
    
    // Calculate start and end points using axialToPixel
    const start = axialToPixel(edge.v1.q, edge.v1.r, edge.v1.corner);
    const end = axialToPixel(edge.v2.q, edge.v2.r, edge.v2.corner);
    
    ctx.beginPath();
    ctx.moveTo(start.x, start.y);
    ctx.lineTo(end.x, end.y);
    ctx.strokeStyle = colorMap[edge.owner];
    ctx.lineWidth = 4;
    ctx.stroke();
    ctx.lineWidth = 1;
}

function updateUI(data) {
  document.getElementById("currentPlayerLabel").textContent = 
    `Player ${data.current_player}`;

  let bankDiv = document.getElementById("bankInfo");
  bankDiv.innerHTML = "<h3>Bank</h3>";
  for (let resource in data.bank) {
    let p = document.createElement("p");
    p.textContent = `${resource}: ${data.bank[resource]}`;
    bankDiv.appendChild(p);
  }

  let playersDiv = document.getElementById("playersInfo");
  playersDiv.innerHTML = "<h3>Players</h3>";
  data.players.forEach(p => {
    let totalCards = Object.values(p.resources).reduce((a,b)=>a+b,0);
    let line = document.createElement("p");
    line.textContent = `Player ${p.pid} - total cards: ${totalCards}`;
    if (p.pid === data.current_player) {
      line.style.fontWeight = "bold";
    }
    playersDiv.appendChild(line);
  });
} 