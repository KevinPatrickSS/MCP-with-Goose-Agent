"""
Main application for resort booking system using Goose AI agent with MCP
"""
import os
import json
import subprocess
import sys
from pathlib import Path
from typing import Optional

class GooseSession:
    """Manages interaction with Goose AI agent."""
    
    def __init__(self, profile: str = "default"):
        self.profile = profile
        self.session_dir = None
        self.session_id = None
        
    def start_session(self):
        """Start a new Goose session."""
        print("🚀 Starting Goose session...")
        
        # Start Goose in interactive mode
        try:
            # Check if goose is available
            result = subprocess.run(
                ["goose", "--version"],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                raise Exception("Goose not found. Is it installed and in PATH?")
                
            print("✅ Goose is ready!")
            return True
            
        except FileNotFoundError:
            print("❌ Goose not found. Please install Goose first.")
            print("   Visit: https://github.com/square/goose")
            return False
    
    def send_message(self, message: str) -> str:
        """
        Send a message to Goose and get response.
        Goose will use MCP tools automatically when needed.
        """
        try:
            # Use goose CLI to send message
            cmd = ["goose", "run", "--profile", self.profile]
            
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input=message + "\n")
            
            if process.returncode != 0:
                return f"Error: {stderr}"
            
            return stdout.strip()
            
        except Exception as e:
            return f"Error communicating with Goose: {str(e)}"

class GooseInteractiveSession:
    """
    Interactive session with Goose using subprocess for real-time communication.
    """
    
    def __init__(self, profile: str = "default"):
        self.profile = profile
        self.process = None
        
    def start(self):
        """Start Goose in interactive mode."""
        try:
            self.process = subprocess.Popen(
                ["goose", "session", "--profile", self.profile],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            print("✅ Goose interactive session started!")
            return True
        except Exception as e:
            print(f"❌ Failed to start Goose: {e}")
            return False
    
    def send(self, message: str):
        """Send message to Goose."""
        if self.process and self.process.stdin:
            self.process.stdin.write(message + "\n")
            self.process.stdin.flush()
    
    def stop(self):
        """Stop the Goose session."""
        if self.process:
            self.send("exit")
            self.process.terminate()
            self.process.wait()

def verify_mcp_server():
    """Verify that MCP server can be started."""
    print("\n🔍 Verifying MCP server...")
    try:
        # Try to import required modules
        from tools import call_tool
        from schemas import ALL_FUNCTION_SCHEMAS
        print("✅ Tools and schemas imported successfully")
        
        # Test a simple tool call
        result = call_tool("get_available_resorts")
        print(f"✅ MCP server tools are working (found {len(result.get('resorts', []))} resorts)")
        return True
    except Exception as e:
        print(f"❌ MCP server verification failed: {e}")
        return False

def main():
    """Main application loop."""
    print("🏖️  Resort Booking System with Goose AI + MCP")
    print("=" * 60)
    
    # Verify MCP server is ready
    if not verify_mcp_server():
        print("\n⚠️  MCP server verification failed.")
        print("   Make sure tools.py and schemas.py are properly configured.")
        return
    
    print("\n📋 Available Commands:")
    print("  - Type your booking queries naturally")
    print("  - 'help' - Show example queries")
    print("  - 'quit' - Exit the application")
    print("=" * 60)
    
    # Start Goose session
    goose = GooseSession()
    if not goose.start_session():
        return
    
    print("\n💡 Tip: Goose will automatically use MCP tools to answer your queries!")
    print("   Try: 'Show me all available resorts' or 'What are my bookings?'\n")
    
    while True:
        try:
            user_input = input("\n🗣️  You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if user_input.lower() == 'help':
                print("\n📖 Example Queries:")
                print("  • 'Show me all available resorts'")
                print("  • 'Get details for Paradise Bay Resort'")
                print("  • 'What are my bookings?' (for user: John Doe)")
                print("  • 'Check availability for Mountain View Lodge'")
                print("  • 'Book a room at Paradise Bay for 3 nights'")
                continue
            
            print("\n🤖 Goose: Processing your request...")
            print("-" * 40)
            
            response = goose.send_message(user_input)
            print(f"\n🤖 Goose: {response}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

def test_mcp_tools_directly():
    """Test MCP tools directly without Goose (for debugging)."""
    print("\n🧪 Testing MCP Tools Directly")
    print("=" * 40)
    
    from tools import call_tool
    
    tests = [
        ("get_available_resorts", {}),
        ("get_resort_details", {"resort_name": "Paradise Bay Resort"}),
        ("get_user_bookings", {"user_name": "John Doe"}),
    ]
    
    for tool_name, args in tests:
        print(f"\n🔧 Testing: {tool_name}")
        try:
            result = call_tool(tool_name, **args)
            print(f"✅ Success:")
            print(json.dumps(result, indent=2, default=str)[:500])
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_mcp_tools_directly()
    else:
        main()