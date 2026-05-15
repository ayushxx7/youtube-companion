import os
import subprocess
import sys

def run_command(command, description):
    print(f"==> {description}...")
    try:
        subprocess.check_call(command, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        sys.exit(1)

def setup():
    # 1. Install dependencies
    run_command("pip install -r requirements.txt", "Installing dependencies")

    # 2. Seed database
    # Ensure we are in the right directory for relative imports in seed.py
    run_command("PYTHONPATH=. python scripts/seed.py", "Seeding database with demo data")

    print("\n" + "="*50)
    print("VibeIntelligence Setup Complete!")
    print("="*50)
    print("\nTo run the Dashboard:")
    print("  streamlit run dashboard/app.py")
    print("\nTo run the FastMCP 3.2 Server:")
    print("  python mcp_server.py")
    print("\nNote: For real YouTube data, populate .env with your Google Cloud Credentials.")
    print("="*50)

if __name__ == "__main__":
    setup()
