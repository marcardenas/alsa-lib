#!/usr/bin/env python3
"""
Setup script for Trump Monitor WhatsApp Client
Helps with initial installation and configuration
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_banner():
    """Print setup banner"""
    print("=" * 60)
    print("🇺🇸 TRUMP MONITOR WHATSAPP CLIENT SETUP 🇺🇸")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_environment_file():
    """Set up environment file"""
    print("\n⚙️ Setting up environment configuration...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("⚠️  .env file already exists")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("Keeping existing .env file")
            return True
    
    if env_example.exists():
        shutil.copy(env_example, env_file)
        print("✅ Created .env file from template")
        print("📝 Please edit .env file with your credentials")
        return True
    else:
        print("❌ .env.example file not found")
        return False

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = ["logs", "data"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created {directory}/ directory")

def test_installation():
    """Test the installation"""
    print("\n🧪 Testing installation...")
    
    try:
        # Try importing main modules
        from config import Config
        from database import DatabaseManager
        print("✅ Core modules imported successfully")
        
        # Test database creation
        db = DatabaseManager()
        print("✅ Database initialized successfully")
        
        return True
    except Exception as e:
        print(f"❌ Installation test failed: {e}")
        return False

def print_next_steps():
    """Print next steps for the user"""
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit the .env file with your credentials:")
    print("   - Twilio Account SID and Auth Token (required)")
    print("   - Your WhatsApp number (required)")
    print("   - Truth Social API key (optional)")
    print("   - Twitter Bearer Token (optional)")
    print()
    print("2. Test your configuration:")
    print("   python main.py --test")
    print()
    print("3. Run the monitoring service:")
    print("   python main.py")
    print()
    print("4. Or run with web interface:")
    print("   python main.py --api")
    print()
    print("📖 For detailed instructions, see README.md")

def main():
    """Main setup function"""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed during dependency installation")
        sys.exit(1)
    
    # Set up environment file
    if not setup_environment_file():
        print("\n❌ Setup failed during environment configuration")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Test installation
    if not test_installation():
        print("\n⚠️  Setup completed but installation test failed")
        print("   You may need to manually configure your environment")
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    main()