#!/usr/bin/env python3
"""
Setup validation script for Foody Menu App
Checks if all dependencies and requirements are met
"""
import sys
import subprocess
import os

def check_command(command, name, install_hint):
    """Check if a command is available"""
    try:
        result = subprocess.run(
            [command, '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print(f"✅ {name}: {version}")
            return True
        else:
            print(f"❌ {name}: Not found")
            print(f"   Install: {install_hint}")
            return False
    except FileNotFoundError:
        print(f"❌ {name}: Not found")
        print(f"   Install: {install_hint}")
        return False
    except Exception as e:
        print(f"⚠️  {name}: Error checking ({e})")
        return False

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python: {version.major}.{version.minor}.{version.micro} (requires 3.8+)")
        return False

def check_python_packages():
    """Check if Python packages are installed"""
    packages = [
        'flask',
        'flask_cors',
        'pytesseract',
        'cv2',
        'PIL',
        'sqlalchemy'
    ]

    all_good = True
    for package in packages:
        try:
            __import__(package)
            print(f"✅ Python package: {package}")
        except ImportError:
            print(f"❌ Python package: {package} not found")
            all_good = False

    if not all_good:
        print(f"\n   Install with: cd backend && pip install -r requirements.txt")

    return all_good

def check_node_version():
    """Check Node.js version"""
    try:
        result = subprocess.run(
            ['node', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            # Parse version number
            version_num = int(version.lstrip('v').split('.')[0])
            if version_num >= 14:
                print(f"✅ Node.js: {version}")
                return True
            else:
                print(f"⚠️  Node.js: {version} (recommends 14+)")
                return True  # Still works, just warning
        return False
    except:
        print(f"❌ Node.js: Not found")
        print(f"   Install from: https://nodejs.org/")
        return False

def check_directory_structure():
    """Check if directory structure is correct"""
    required_dirs = [
        'backend',
        'frontend',
        'backend/uploads'
    ]

    required_files = [
        'backend/app.py',
        'backend/requirements.txt',
        'frontend/package.json',
        'frontend/src/App.js'
    ]

    all_good = True

    # Check directories
    for dir_path in required_dirs:
        full_path = os.path.join(os.path.dirname(__file__), dir_path)
        if os.path.isdir(full_path):
            print(f"✅ Directory: {dir_path}/")
        else:
            print(f"❌ Directory: {dir_path}/ not found")
            all_good = False

    # Check files
    for file_path in required_files:
        full_path = os.path.join(os.path.dirname(__file__), file_path)
        if os.path.isfile(full_path):
            print(f"✅ File: {file_path}")
        else:
            print(f"❌ File: {file_path} not found")
            all_good = False

    return all_good

def check_env_files():
    """Check for environment files"""
    backend_env = os.path.join(os.path.dirname(__file__), 'backend', '.env')
    frontend_env = os.path.join(os.path.dirname(__file__), 'frontend', '.env')

    backend_exists = os.path.isfile(backend_env)
    frontend_exists = os.path.isfile(frontend_env)

    if backend_exists:
        print("✅ Backend .env file exists")
    else:
        print("⚠️  Backend .env file not found (optional)")
        print("   Copy from: backend/.env.example")

    if frontend_exists:
        print("✅ Frontend .env file exists")
    else:
        print("⚠️  Frontend .env file not found (optional)")
        print("   Copy from: frontend/.env.example")

    return True  # These are optional

def main():
    """Run all checks"""
    print("🔍 Foody Menu App - Setup Validation")
    print("=" * 60)

    results = []

    # Check Python
    print("\n📦 Checking Python...")
    results.append(check_python_version())

    # Check Tesseract
    print("\n🔤 Checking Tesseract OCR...")
    results.append(check_command(
        'tesseract',
        'Tesseract OCR',
        'macOS: brew install tesseract | Ubuntu: sudo apt-get install tesseract-ocr'
    ))

    # Check Node.js
    print("\n📦 Checking Node.js...")
    results.append(check_node_version())

    # Check npm
    print("\n📦 Checking npm...")
    results.append(check_command(
        'npm',
        'npm',
        'Comes with Node.js - install from https://nodejs.org/'
    ))

    # Check directory structure
    print("\n📁 Checking directory structure...")
    results.append(check_directory_structure())

    # Check environment files
    print("\n⚙️  Checking environment files...")
    check_env_files()

    # Check Python packages (only if in venv or packages might be installed)
    print("\n📚 Checking Python packages...")
    if os.path.exists(os.path.join(os.path.dirname(__file__), 'backend', 'venv')):
        print("   (Run after activating virtual environment)")
    else:
        results.append(check_python_packages())

    # Summary
    print("\n" + "=" * 60)
    if all(results):
        print("✅ All checks passed!")
        print("\nYou're ready to run the app:")
        print("  ./start.sh (Unix/Mac) or start.bat (Windows)")
        print("\nOr manually:")
        print("  Terminal 1: cd backend && python app.py")
        print("  Terminal 2: cd frontend && npm start")
    else:
        print("❌ Some checks failed")
        print("\nPlease install missing dependencies and run this script again")
        print("\nFor detailed setup instructions, see:")
        print("  - README.md")
        print("  - QUICKSTART.md")

    print("=" * 60)

    return 0 if all(results) else 1

if __name__ == '__main__':
    sys.exit(main())
