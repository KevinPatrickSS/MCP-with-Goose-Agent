"""
Configuration and setup to connect Goose with MCP Server
"""
import os
import sys
import json
import yaml
import subprocess
from pathlib import Path
from typing import Dict, Any

class GooseMCPConfig:
    """Setup and manage Goose configuration to connect to MCP server."""
    
    def __init__(self):
        self.config_dir = Path.home() / ".config" / "goose"
        self.profiles_file = self.config_dir / "profiles.yaml"
        
    def setup_profile(self, mcp_server_path: str, profile_name: str = "resort-booking"):
        """
        Create a Goose profile that connects to your MCP server.
        
        Args:
            mcp_server_path: Full path to your MCP server script
            profile_name: Name for this profile
        """
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing profiles or create new
        if self.profiles_file.exists():
            with open(self.profiles_file, 'r') as f:
                profiles = yaml.safe_load(f) or {}
        else:
            profiles = {}
        
        # Convert to absolute path
        mcp_server_path = str(Path(mcp_server_path).resolve())
        
        # Get Python executable path
        python_exe = sys.executable
        
        print(f"   Python: {python_exe}")
        print(f"   MCP Server: {mcp_server_path}")
        
        # Add/update the profile with MCP server configuration
        profiles[profile_name] = {
            "provider": "anthropic",  # or "openai" 
            "processor": "claude-sonnet-4-20250514",  # LLM model to use
            "accelerator": "claude-sonnet-4-20250514",
            "moderator": "truncate",
            "toolkits": [
                {
                    "mcp": {
                        # This tells Goose how to start your MCP server
                        "command": python_exe,  # Use full path to Python
                        "args": [mcp_server_path],  # Full path to script
                        "env": {
                            # Pass any environment variables your MCP server needs
                            "PYTHONPATH": str(Path(mcp_server_path).parent),
                        }
                    }
                }
            ]
        }
        
        # Save the configuration
        with open(self.profiles_file, 'w') as f:
            yaml.dump(profiles, f, default_flow_style=False)
        
        print(f"✅ Goose profile '{profile_name}' configured!")
        print(f"   Config file: {self.profiles_file}")
        print(f"   MCP Server: {mcp_server_path}")
        print(f"   Python: {python_exe}")
        
        return profile_name
    
    def verify_setup(self, profile_name: str = "resort-booking"):
        """Verify that Goose and profile are properly configured."""
        print("\n🔍 Verifying Goose + MCP setup...")
        
        # Check if Goose is installed
        try:
            result = subprocess.run(
                ["goose", "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"✅ Goose installed: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Goose not found. Install it with: pip install goose-ai")
            return False
        
        # Check if profile exists
        if not self.profiles_file.exists():
            print("❌ No Goose profiles configured")
            return False
        
        with open(self.profiles_file, 'r') as f:
            profiles = yaml.safe_load(f) or {}
        
        if profile_name not in profiles:
            print(f"❌ Profile '{profile_name}' not found")
            return False
        
        print(f"✅ Profile '{profile_name}' configured")
        print(f"   Toolkits: {len(profiles[profile_name].get('toolkits', []))}")
        
        return True


class GooseSessionManager:
    """Manages Goose sessions with MCP server integration."""
    
    def __init__(self, profile: str = "resort-booking"):
        self.profile = profile
        self.process = None
        
    def start_interactive(self):
        """
        Start Goose in interactive mode.
        Goose will automatically connect to the MCP server defined in the profile.
        """
        print(f"\n🦆 Starting Goose with profile: {self.profile}")
        print("   Goose will connect to your MCP server automatically...")
        
        try:
            # Start Goose session - it will launch your MCP server as a subprocess
            cmd = ["goose", "session", "start", "--profile", self.profile]
            
            # Run interactively - this blocks and handles I/O
            subprocess.run(cmd)
            
        except KeyboardInterrupt:
            print("\n👋 Session ended")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def send_message_programmatically(self, message: str) -> str:
        """
        Send a message to Goose programmatically (non-interactive).
        Useful for chatbot integration.
        """
        try:
            cmd = [
                "goose", "session", "run",
                "--profile", self.profile,
                "--message", message
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                check=True
            )
            
            return result.stdout.strip()
            
        except subprocess.TimeoutExpired:
            return "Error: Request timed out"
        except subprocess.CalledProcessError as e:
            return f"Error: {e.stderr}"
        except Exception as e:
            return f"Error: {str(e)}"


def setup_and_run():
    """Setup Goose configuration and start interactive session."""
    
    print("🏖️  Resort Booking System - Goose + MCP Setup")
    print("=" * 60)
    
    # Step 1: Configure Goose to use your MCP server
    config = GooseMCPConfig()
    
    # Get the path to your MCP server script
    mcp_server_path = Path(__file__).parent / "mcp_server.py"
    
    if not mcp_server_path.exists():
        print(f"❌ MCP server not found at: {mcp_server_path}")
        print("   Make sure mcp_server.py is in the same directory")
        return
    
    # Setup the profile
    profile_name = config.setup_profile(
        mcp_server_path=str(mcp_server_path),
        profile_name="resort-booking"
    )
    
    # Step 2: Verify setup
    if not config.verify_setup(profile_name):
        print("\n❌ Setup verification failed")
        return
    
    print("\n✅ Setup complete!")
    print("\n📋 How it works:")
    print("   1. You type a message in Goose")
    print("   2. Goose (LLM) analyzes your message")
    print("   3. Goose discovers tools from your MCP server")
    print("   4. Goose decides which tools to call")
    print("   5. Goose executes tools via MCP server")
    print("   6. Goose formats and returns the result")
    
    print("\n💡 Example queries:")
    print("   • 'Show me all available resorts'")
    print("   • 'Get details for Paradise Bay Resort'")
    print("   • 'What bookings does John Doe have?'")
    
    # Step 3: Start interactive session
    input("\n Press Enter to start Goose session...")
    
    session = GooseSessionManager(profile=profile_name)
    session.start_interactive()


def test_mcp_server_standalone():
    """Test that MCP server works standalone (for debugging)."""
    print("\n🧪 Testing MCP Server Standalone")
    print("=" * 60)
    
    mcp_server_path = Path(__file__).parent / "mcp_server.py"
    
    if not mcp_server_path.exists():
        print(f"❌ MCP server not found: {mcp_server_path}")
        return
    
    print("Starting MCP server for 5 seconds...")
    print("(It should start without errors)\n")
    
    try:
        # Start MCP server as subprocess
        process = subprocess.Popen(
            ["python", str(mcp_server_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Let it run briefly
        import time
        time.sleep(2)
        
        # Check if still running
        if process.poll() is None:
            print("✅ MCP server started successfully")
            process.terminate()
            process.wait()
        else:
            stdout, stderr = process.communicate()
            print(f"❌ MCP server exited unexpectedly")
            if stderr:
                print(f"Error: {stderr}")
            
    except Exception as e:
        print(f"❌ Error starting MCP server: {e}")


def create_chatbot_integration():
    """
    Example of how to integrate this with your chatbot.
    Your chatbot can call Goose programmatically.
    """
    print("\n🤖 Chatbot Integration Example")
    print("=" * 60)
    
    session = GooseSessionManager(profile="resort-booking")
    
    # Simulate chatbot receiving user messages
    test_messages = [
        "Show me all available resorts",
        "Tell me about Paradise Bay Resort",
        "What bookings does John Doe have?"
    ]
    
    for msg in test_messages:
        print(f"\n👤 User: {msg}")
        print("🤖 Processing...")
        
        response = session.send_message_programmatically(msg)
        print(f"🤖 Bot: {response}")
        print("-" * 40)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test-mcp":
            test_mcp_server_standalone()
        elif sys.argv[1] == "--test-chatbot":
            create_chatbot_integration()
        else:
            print("Usage:")
            print("  python connect_goose_mcp.py           # Setup and run interactive")
            print("  python connect_goose_mcp.py --test-mcp      # Test MCP server")
            print("  python connect_goose_mcp.py --test-chatbot  # Test chatbot integration")
    else:
        setup_and_run()