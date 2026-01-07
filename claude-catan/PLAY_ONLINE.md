# How to Play Catan Online with Friends

This guide shows you how to set up Catan so your friends can play with you online from anywhere!

## Quick Start (Easiest Method)

### 1. Install ngrok (One-time setup)

**macOS:**
```bash
brew install ngrok
```

**Linux:**
```bash
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok
```

**Windows:**
Download from: https://ngrok.com/download

**Sign up for ngrok (free):**
1. Visit: https://dashboard.ngrok.com/signup
2. Get your auth token from: https://dashboard.ngrok.com/get-started/your-authtoken
3. Run: `ngrok config add-authtoken YOUR_AUTH_TOKEN`

### 2. Start the Online Game

```bash
cd claude-catan
python3 deploy_online.py
```

This will:
- Start the Catan server
- Create a public URL using ngrok
- Show you a link to share with friends

### 3. Share the Link

The script will display something like:
```
📱 Share this link with your friends:
   https://abc123.ngrok.io
```

Send that link to your friends!

### 4. Create a Game

1. Open the link in your browser
2. Enter your name
3. Click "Create New Game"
4. You'll get a Game ID (like "a1b2c3d4")
5. Share this Game ID with your friends

### 5. Friends Join

Your friends:
1. Open the same link you sent them
2. Enter their name
3. Enter the Game ID you shared
4. Click "Join Game"

### 6. Start Playing!

Once 2-4 players have joined:
1. Click "Start Game"
2. Enjoy Catan with your friends!

---

## Alternative: Deploy to a Cloud Service

For a more permanent solution, you can deploy to a cloud service:

### Option 1: Heroku (Free Tier Available)

1. Create a Heroku account: https://signup.heroku.com/
2. Install Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli
3. Deploy:

```bash
cd claude-catan

# Login to Heroku
heroku login

# Create app
heroku create your-catan-game

# Add Procfile
echo "web: python server.py" > Procfile

# Deploy
git init
git add .
git commit -m "Deploy Catan"
git push heroku main

# Open your game
heroku open
```

Your game will be at: `https://your-catan-game.herokuapp.com`

### Option 2: Railway (Free Tier Available)

1. Visit: https://railway.app/
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repo
5. Railway will auto-detect and deploy

### Option 3: Render (Free Tier Available)

1. Visit: https://render.com/
2. Sign up
3. Click "New" → "Web Service"
4. Connect your GitHub repo
5. Configure:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python server.py`
6. Deploy!

---

## Troubleshooting

### "ngrok not found"
- Make sure you installed ngrok using the instructions above
- Try running `ngrok version` to verify installation

### "Failed to get public URL"
- Make sure you've authenticated ngrok with your auth token
- Visit: https://dashboard.ngrok.com/get-started/your-authtoken
- Run: `ngrok config add-authtoken YOUR_TOKEN`

### Friends can't connect
- Make sure your server is still running (don't close the terminal)
- Share the exact URL shown (including https://)
- Make sure they use the Game ID correctly (case-sensitive)

### Game is slow
- ngrok free tier has some bandwidth limits
- Consider deploying to a cloud service for better performance
- Make sure all players have stable internet

### Port already in use
- Kill any process using port 5000: `lsof -ti:5000 | xargs kill -9`
- Or change the port in `server.py` and `deploy_online.py`

---

## Tips for Best Experience

1. **Use Voice Chat**: Use Discord, Zoom, or similar while playing
2. **Stable Internet**: Make sure all players have good connections
3. **Desktop Browser**: Works best on Chrome, Firefox, or Safari on desktop
4. **Keep Terminal Open**: Don't close the terminal running the server

---

## Security Notes

- ngrok URLs are public but hard to guess
- Only share the Game ID with people you want to play with
- For private games, consider password protection (can be added to code)
- The free ngrok tier has bandwidth limits

---

## Advanced: Add Password Protection

If you want to add password protection to games:

1. Edit `server.py`
2. Add password check in `handle_join_game`
3. Add password input field in HTML

Example code snippet:
```python
@socketio.on('join_game')
def handle_join_game(data):
    game_id = data.get('game_id')
    password = data.get('password')

    # Check password
    if game_id in game_passwords:
        if game_passwords[game_id] != password:
            emit('error', {'message': 'Incorrect password'})
            return
    # ... rest of function
```

---

## Questions?

- Check the main README.md for game rules
- Run `python tests/test_game_engine.py` to verify everything works
- Report issues at: [your repo]/issues

Happy gaming! 🎲🏡🌾
