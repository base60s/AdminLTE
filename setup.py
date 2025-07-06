#!/usr/bin/env python3
"""
Setup script for Polymarket Price Monitoring Agent
This script helps users set up the agent with basic checks and guidance.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def print_banner():
    """Print a welcome banner"""
    print("=" * 60)
    print("🔥 Polymarket Price Monitoring Agent Setup")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    print("📋 Checking Python version...")
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    else:
        print(f"✅ Python version OK: {sys.version.split()[0]}")
        return True

def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Error installing dependencies")
        return False

def create_env_file():
    """Create .env file from example if it doesn't exist"""
    print("\n⚙️  Setting up configuration...")
    
    if os.path.exists('.env'):
        print("✅ .env file already exists")
        return True
    
    if os.path.exists('.env.example'):
        try:
            with open('.env.example', 'r') as src:
                content = src.read()
            
            with open('.env', 'w') as dst:
                dst.write(content)
            
            print("✅ Created .env file from example")
            print("⚠️  Please edit .env file with your actual configuration")
            return True
        except Exception as e:
            print(f"❌ Error creating .env file: {e}")
            return False
    else:
        print("❌ .env.example file not found")
        return False

def check_credentials_file():
    """Check if Google credentials file exists"""
    print("\n🔑 Checking Google credentials...")
    
    if os.path.exists('credentials.json'):
        try:
            with open('credentials.json', 'r') as f:
                creds = json.load(f)
            
            if 'client_email' in creds:
                print("✅ Google credentials file found")
                print(f"   Service account email: {creds['client_email']}")
                return True
            else:
                print("❌ Invalid credentials file format")
                return False
        except json.JSONDecodeError:
            print("❌ Invalid JSON in credentials file")
            return False
    else:
        print("⚠️  Google credentials file (credentials.json) not found")
        print("   Please download it from Google Cloud Console")
        return False

def check_env_configuration():
    """Check if .env file has required configuration"""
    print("\n🔧 Checking configuration...")
    
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        return False
    
    required_vars = ['GOOGLE_SHEET_ID']
    polymarket_vars = ['POLYMARKET_EVENT_SLUG', 'POLYMARKET_MARKET_SLUG']
    missing_vars = []
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        for var in required_vars:
            value = os.getenv(var)
            if not value or value.startswith('your_'):
                missing_vars.append(var)
        
        # Check that at least one Polymarket variable is set
        polymarket_set = False
        for var in polymarket_vars:
            value = os.getenv(var)
            if value and not value.startswith('your_'):
                polymarket_set = True
                break
        
        if not polymarket_set:
            missing_vars.append('POLYMARKET_EVENT_SLUG or POLYMARKET_MARKET_SLUG')
        
        if missing_vars:
            print("⚠️  The following required variables need to be configured:")
            for var in missing_vars:
                print(f"   - {var}")
            print("   Please edit your .env file with actual values")
            return False
        else:
            print("✅ Required configuration variables are set")
            return True
            
    except ImportError:
        print("⚠️  Cannot check configuration (python-dotenv not installed)")
        return False

def run_test():
    """Run a quick test to validate the setup"""
    print("\n🧪 Running setup validation test...")
    
    try:
        from config import Config
        Config.validate_config()
        print("✅ Configuration validation passed")
        
        # Try importing main modules
        from polymarket_client import PolymarketClient
        from google_sheets_client import GoogleSheetsClient
        print("✅ All modules imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Setup validation failed: {e}")
        return False

def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "=" * 60)
    print("🎉 Setup Complete! Next Steps:")
    print("=" * 60)
    print()
    print("1. 📝 Edit the .env file with your actual configuration:")
    print("   - POLYMARKET_EVENT_SLUG or POLYMARKET_MARKET_SLUG: Get from Polymarket URL")
    print("   - GOOGLE_SHEET_ID: Get from Google Sheets URL")
    print()
    print("2. 📁 Download Google credentials:")
    print("   - Save as 'credentials.json' in this directory")
    print("   - Make sure it's from a service account")
    print()
    print("3. 📊 Set up Google Sheet:")
    print("   - Create a new Google Sheet")
    print("   - Share it with your service account email")
    print("   - Give 'Editor' permissions")
    print()
    print("4. 🚀 Run the agent:")
    print("   python polymarket_agent.py")
    print()
    print("📖 For detailed instructions, see README_POLYMARKET_AGENT.md")
    print()

def main():
    """Main setup function"""
    print_banner()
    
    success = True
    
    # Check Python version
    if not check_python_version():
        success = False
    
    # Install dependencies
    if success and not install_dependencies():
        success = False
    
    # Create .env file
    if success:
        create_env_file()
    
    # Check credentials
    creds_ok = check_credentials_file()
    
    # Check configuration
    config_ok = check_env_configuration()
    
    # Run validation test
    if success and creds_ok and config_ok:
        test_ok = run_test()
    else:
        test_ok = False
    
    # Print results
    print("\n" + "=" * 60)
    print("🔍 Setup Summary:")
    print("=" * 60)
    print(f"✅ Python & Dependencies: {'OK' if success else 'NEEDS ATTENTION'}")
    print(f"✅ Google Credentials: {'OK' if creds_ok else 'NEEDS SETUP'}")
    print(f"✅ Configuration: {'OK' if config_ok else 'NEEDS COMPLETION'}")
    print(f"✅ Validation Test: {'PASSED' if test_ok else 'NEEDS FIXING'}")
    
    if success and creds_ok and config_ok and test_ok:
        print("\n🎉 Everything looks good! You're ready to run the agent.")
    else:
        print("\n⚠️  Some steps need attention. Please review the messages above.")
    
    print_next_steps()

if __name__ == "__main__":
    main()