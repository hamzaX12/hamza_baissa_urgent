"""
Setup script to register agent accounts on the XMPP server
Run this after the server is up: docker-compose exec ejabberd python setup_server.py
"""
import subprocess
import sys

def register_user(username, password):
    """Register a user on the ejabberd server"""
    try:
        cmd = f"ejabberdctl register {username} localhost {password}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Successfully registered {username}@localhost")
        else:
            if "already registered" in result.stderr:
                print(f"ℹ User {username}@localhost already exists")
            else:
                print(f"✗ Failed to register {username}@localhost: {result.stderr}")
    except Exception as e:
        print(f"✗ Error registering {username}: {e}")

def main():
    print("Setting up XMPP agent accounts...\n")
    
    # Register both agents
    register_user("ambulance", "ambulancepass")
    register_user("aospital", "hospitalpass")
    
    print("\n✓ Setup complete! Agents can now communicate.")

if __name__ == "__main__":
    main()
