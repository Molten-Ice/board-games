#!/usr/bin/env python3
"""
Deploy Catan online using ngrok for easy friend access
Allows you to share a link with friends to play together
"""

import os
import sys
import subprocess
import time
import requests
from threading import Thread

def check_ngrok_installed():
    """Check if ngrok is installed"""
    try:
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ ngrok is installed: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass

    print("\n❌ ngrok is not installed!")
    print("\nTo install ngrok:")
    print("1. Visit: https://ngrok.com/download")
    print("2. Download for your system")
    print("3. Follow installation instructions")
    print("\nOr use one of these quick install methods:")
    print("  - macOS: brew install ngrok")
    print("  - Linux: snap install ngrok")
    print("  - Or download from: https://ngrok.com/download")
    return False

def start_flask_server():
    """Start the Flask server in background"""
    print("\n🚀 Starting Catan server...")
    server_process = subprocess.Popen(
        [sys.executable, 'server.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(3)  # Give server time to start
    return server_process

def start_ngrok():
    """Start ngrok tunnel"""
    print("🌐 Creating public URL with ngrok...")
    ngrok_process = subprocess.Popen(
        ['ngrok', 'http', '5000', '--log=stdout'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(3)  # Give ngrok time to establish tunnel
    return ngrok_process

def get_public_url():
    """Get the public URL from ngrok API"""
    try:
        response = requests.get('http://localhost:4040/api/tunnels')
        if response.status_code == 200:
            data = response.json()
            for tunnel in data['tunnels']:
                if tunnel['proto'] == 'https':
                    return tunnel['public_url']
    except:
        pass
    return None

def main():
    print("="*60)
    print("  Settlers of Catan - Online Multiplayer Setup")
    print("="*60)

    # Check ngrok
    if not check_ngrok_installed():
        sys.exit(1)

    # Start Flask server
    server = start_flask_server()

    # Start ngrok
    ngrok = start_ngrok()

    # Get public URL
    public_url = None
    for i in range(10):
        public_url = get_public_url()
        if public_url:
            break
        time.sleep(1)

    if not public_url:
        print("\n❌ Failed to get public URL from ngrok")
        print("Make sure ngrok is properly installed and authenticated")
        print("Visit: https://dashboard.ngrok.com/get-started/setup")
        server.terminate()
        ngrok.terminate()
        sys.exit(1)

    print("\n" + "="*60)
    print("✅ Catan is now available online!")
    print("="*60)
    print(f"\n📱 Share this link with your friends:")
    print(f"\n   {public_url}")
    print(f"\n")
    print("="*60)
    print("\nInstructions for your friends:")
    print("1. Open the link above in their web browser")
    print("2. Enter their name")
    print("3. Enter the Game ID you share with them")
    print("4. Click 'Join Game'")
    print("\nTo create a game:")
    print("1. Open the link yourself")
    print("2. Enter your name")
    print("3. Click 'Create New Game'")
    print("4. Share the Game ID with your friends")
    print("5. Once 2-4 players join, click 'Start Game'")
    print("\n" + "="*60)
    print("\n⚠️  Important:")
    print("- Keep this terminal window open while playing")
    print("- If you close this, the game will stop")
    print("- Press Ctrl+C to stop the server")
    print("\n" + "="*60)

    try:
        # Keep running
        print("\n🎮 Server is running... waiting for players...\n")
        server.wait()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down servers...")
        server.terminate()
        ngrok.terminate()
        print("✓ Servers stopped")

if __name__ == '__main__':
    main()
