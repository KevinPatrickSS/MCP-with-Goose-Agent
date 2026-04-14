"""
Streamlit application for resort booking system with OpenAI function calling.
Beautiful web interface replicating the terminal functionality.
"""
import os
import json
import streamlit as st
from typing import Dict, Any, List
from openai import OpenAI
from schemas import ALL_FUNCTION_SCHEMAS
from tools import call_tool
from dotenv import load_dotenv
from assistant_thread import AssistantThread
import time

# Load environment variables
load_dotenv()

# OpenAI pricing (as of 2024) - prices per 1K tokens
GPT4_TURBO_PROMPT_PRICE = 0.01  # $0.01 per 1K prompt tokens
GPT4_TURBO_COMPLETION_PRICE = 0.03  # $0.03 per 1K completion tokens

def calculate_cost(prompt_tokens: int, completion_tokens: int) -> float:
    """Calculate the cost of OpenAI API usage."""
    prompt_cost = (prompt_tokens / 1000) * GPT4_TURBO_PROMPT_PRICE
    completion_cost = (completion_tokens / 1000) * GPT4_TURBO_COMPLETION_PRICE
    return prompt_cost + completion_cost

# Page configuration
st.set_page_config(
    page_title="🏖️ Resort Booking Assistant",
    page_icon="🏖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #FF6B6B 0%, #4ECDC4 50%, #45B7D1 100%);
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #4ECDC4;
    }
    
    .user-message {
        background-color: #f0f2f6;
        border-left-color: #FF6B6B;
    }
    
    .assistant-message {
        background-color: #e8f4fd;
        border-left-color: #4ECDC4;
    }
    
    .function-call {
        background-color: #fff3cd;
        border-left-color: #ffc107;
        font-family: monospace;
        font-size: 0.9em;
    }
    
    .function-call pre {
        background-color: #f8f9fa;
        padding: 0.5rem;
        border-radius: 5px;
        white-space: pre-wrap;
        word-wrap: break-word;
        max-height: 300px;
        overflow-y: auto;
    }
    
    .function-call details {
        margin-top: 0.5rem;
    }
    
    .function-call summary {
        cursor: pointer;
        font-weight: bold;
        color: #28a745;
    }
    
    .metrics-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #FF6B6B 0%, #4ECDC4 100%);
        color: white;
        border: none;
        border-radius: 20px;
        padding: 0.5rem 2rem;
        font-weight: bold;
    }
    
    .sidebar-content {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'thread' not in st.session_state:
    st.session_state.thread = AssistantThread()

if 'total_tokens' not in st.session_state:
    st.session_state.total_tokens = 0

if 'total_cost' not in st.session_state:
    st.session_state.total_cost = 0.0

if 'client' not in st.session_state:
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        st.session_state.client = OpenAI(api_key=api_key)
    else:
        st.session_state.client = None

def display_function_schemas():
    """Display available function schemas in the sidebar."""
    st.sidebar.markdown("### 📋 Available Functions")
    
    for schema in ALL_FUNCTION_SCHEMAS:
        function_info = schema["function"]
        with st.sidebar.expander(f"📌 {function_info['name']}", expanded=False):
            st.write(f"**Description:** {function_info['description']}")
            
            if function_info["parameters"]["properties"]:
                st.write("**Parameters:**")
                for param_name, param_info in function_info["parameters"]["properties"].items():
                    required = param_name in function_info["parameters"].get("required", [])
                    param_type = param_info.get('type', 'unknown')
                    if param_type == 'array' and 'items' in param_info:
                        param_type = f"array[{param_info['items']['type']}]"
                    req_text = " *(required)*" if required else ""
                    st.write(f"• **{param_name}** ({param_type}){req_text}")
                    st.write(f"  {param_info['description']}")
            else:
                st.write("**Parameters:** None")

def test_tools_demo():
    """Display tools testing demo."""
    st.sidebar.markdown("### 🔧 Test Tools Directly")
    
    if st.sidebar.button("Test get_available_resorts"):
        with st.spinner("Testing get_available_resorts..."):
            result = call_tool("get_available_resorts")
            st.sidebar.success("✅ Function executed!")
            st.sidebar.json(result)
    
    if st.sidebar.button("Test get_resort_details"):
        with st.spinner("Testing get_resort_details..."):
            result = call_tool("get_resort_details", resort_id=1)
            st.sidebar.success("✅ Function executed!")
            st.sidebar.json(result)
    
    if st.sidebar.button("Test get_featured_listings"):
        with st.spinner("Testing get_featured_listings..."):
            result = call_tool("get_featured_listings", limit=5)
            st.sidebar.success("✅ Function executed!")
            st.sidebar.json(result)
    
    user_email = st.sidebar.text_input("User email for booking test:", "john.doe@example.com")
    if st.sidebar.button("Test get_user_bookings"):
        with st.spinner(f"Testing get_user_bookings for {user_email}..."):
            result = call_tool("get_user_bookings", user_email=user_email)
            st.sidebar.success("✅ Function executed!")
            st.sidebar.json(result)

def process_function_call(function_call) -> str:
    """Process a function call from OpenAI and return the result."""
    function_name = function_call.name
    
    try:
        arguments = json.loads(function_call.arguments)
    except json.JSONDecodeError:
        return json.dumps({"error": "Invalid JSON arguments"})
    
    result = call_tool(function_name, **arguments)
    
    if isinstance(result, dict):
        return json.dumps(result, indent=2, default=str)
    else:
        return json.dumps({"result": result}, indent=2, default=str)

def display_message(message, is_user=True):
    """Display a chat message with appropriate styling."""
    if is_user:
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>🧑‍💻 You:</strong><br>
            {message}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message assistant-message">
            <strong>🤖 Resort Assistant:</strong><br>
            {message}
        </div>
        """, unsafe_allow_html=True)

def display_function_call(function_name, arguments, result=None):
    """Display function call information."""
    result_display = ""
    if result:
        if isinstance(result, str) and len(result) > 200:
            # Truncate long results but show they exist
            result_display = f'<br><strong>✅ Result:</strong> <details><summary>Function executed successfully (click to view result)</summary><pre>{result}</pre></details>'
        elif result:
            result_display = f'<br><strong>✅ Result:</strong> <pre>{result}</pre>'
        else:
            result_display = '<br><strong>✅ Result:</strong> Function executed successfully'
    
    st.markdown(f"""
    <div class="chat-message function-call">
        <strong>🔧 Function Call:</strong> {function_name}<br>
        <strong>Arguments:</strong> {arguments}
        {result_display}
    </div>
    """, unsafe_allow_html=True)

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🏖️ Resort Booking Assistant</h1>
        <p>Your AI-powered resort booking companion with real-time data access</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check API key
    if not st.session_state.client:
        st.error("⚠️ OpenAI API key not found! Please set OPENAI_API_KEY environment variable.")
        st.info("💡 For demonstration purposes, you can test the tools directly using the sidebar.")
        
        # Show demo content
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🎯 Available Features")
            st.write("• Search available resorts by location")
            st.write("• Get detailed resort information")
            st.write("• Check user bookings and profiles") 
            st.write("• Browse featured and weekend listings")
            st.write("• Search by amenities and listing types")
            st.write("• Get price range summaries")
        
        with col2:
            st.subheader("🚀 Example Queries")
            st.write("• 'Show me resorts in Mexico'")
            st.write("• 'Get details for resort ID 5'")
            st.write("• 'Find resorts with pool and spa'")
            st.write("• 'Check bookings for user@email.com'")
            st.write("• 'Show featured listings'")
            st.write("• 'Get weekend available listings'")
        
        # Display function schemas and tools
        display_function_schemas()
        test_tools_demo()
        return
    
    # Main chat interface
    col1, col2 = st.columns([3, 1])
    
    with col2:
        # Metrics
        st.markdown("""
        <div class="metrics-container">
            <h4>📊 Session Metrics</h4>
        </div>
        """, unsafe_allow_html=True)
        
        st.metric("Total Tokens", st.session_state.total_tokens)
        st.metric("Total Cost", f"${st.session_state.total_cost:.4f}")
        st.metric("Thread ID", st.session_state.thread.thread_id[:8] + "...")
        
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.session_state.thread = AssistantThread()
            st.session_state.total_tokens = 0
            st.session_state.total_cost = 0.0
            st.rerun()
        
        # Display function schemas and tools
        display_function_schemas()
        test_tools_demo()
    
    with col1:
        # Chat history
        st.subheader("💬 Chat History")
        
        # Display chat messages
        for message in st.session_state.messages:
            if message["type"] == "user":
                display_message(message["content"], is_user=True)
            elif message["type"] == "assistant":
                display_message(message["content"], is_user=False)
            elif message["type"] == "function_call":
                display_function_call(
                    message["function_name"], 
                    message["arguments"], 
                    message.get("result")
                )
        
        # Chat input
        st.subheader("✍️ Ask me anything about resort bookings!")
        
        # Example queries
        example_queries = [
            "Show me all available resorts",
            "List resorts in Mexico", 
            "Get details for resort ID 1",
            "Show featured listings",
            "Find resorts with pool and spa amenities",
            "Check my bookings for john.doe@example.com",
            "Get weekend available listings",
            "Search listings by type: villa"
        ]
        
        selected_example = st.selectbox(
            "Quick examples:", 
            [""] + example_queries,
            key="example_selector"
        )
        
        user_input = st.text_area(
            "Your message:",
            value=selected_example if selected_example else "",
            height=100,
            key="user_input"
        )
        
        col_send, col_clear_input = st.columns([1, 1])
        
        with col_send:
            send_button = st.button("🚀 Send Message", use_container_width=True)
        
        with col_clear_input:
            if st.button("🧹 Clear Input", use_container_width=True):
                st.session_state.user_input = ""
                st.rerun()
        
        if send_button and user_input.strip():
            # Add user message to chat history
            st.session_state.messages.append({
                "type": "user",
                "content": user_input
            })
            
            # Add to thread
            st.session_state.thread.add_user_message(user_input)
            
            # Process with OpenAI
            with st.spinner("🤖 Processing your request..."):
                try:
                    # First API call
                    response = st.session_state.client.chat.completions.create(
                        model="gpt-4-turbo-preview",
                        messages=st.session_state.thread.get_history(),
                        tools=ALL_FUNCTION_SCHEMAS,
                        tool_choice="auto"
                    )
                    
                    assistant_message = response.choices[0].message
                    
                    # Track tokens and cost
                    if hasattr(response, 'usage') and response.usage:
                        st.session_state.total_tokens += response.usage.total_tokens
                        call_cost = calculate_cost(response.usage.prompt_tokens, response.usage.completion_tokens)
                        st.session_state.total_cost += call_cost
                    
                    # Add assistant message to thread
                    st.session_state.thread.add_assistant_message({
                        "role": "assistant",
                        "content": assistant_message.content,
                        "tool_calls": assistant_message.tool_calls
                    })
                    
                    # Handle tool calls
                    if assistant_message.tool_calls:
                        for tool_call in assistant_message.tool_calls:
                            function_name = tool_call.function.name
                            arguments = tool_call.function.arguments
                            
                            # Execute function
                            parsed_args = json.loads(arguments)
                            tool_result = call_tool(function_name, **parsed_args)
                            
                            # Convert result to JSON string
                            if isinstance(tool_result, dict):
                                tool_result_str = json.dumps(tool_result, indent=2, default=str)
                            else:
                                tool_result_str = json.dumps({"result": tool_result}, indent=2, default=str)
                            
                            # Add function call to chat history with actual result
                            st.session_state.messages.append({
                                "type": "function_call",
                                "function_name": function_name,
                                "arguments": arguments,
                                "result": tool_result_str
                            })
                            
                            # Add tool response to thread
                            st.session_state.thread.add_assistant_message({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": tool_result_str
                            })
                        
                        # Get final response
                        final_response = st.session_state.client.chat.completions.create(
                            model="gpt-4-turbo-preview",
                            messages=st.session_state.thread.get_history(),
                            tools=ALL_FUNCTION_SCHEMAS,
                            tool_choice="auto"
                        )
                        
                        final_message = final_response.choices[0].message
                        
                        # Track tokens for final response
                        if hasattr(final_response, 'usage') and final_response.usage:
                            st.session_state.total_tokens += final_response.usage.total_tokens
                            final_cost = calculate_cost(final_response.usage.prompt_tokens, final_response.usage.completion_tokens)
                            st.session_state.total_cost += final_cost
                        
                        # Add final assistant message
                        st.session_state.thread.add_assistant_message({
                            "role": "assistant",
                            "content": final_message.content
                        })
                        
                        # Add to chat history
                        if final_message.content:
                            st.session_state.messages.append({
                                "type": "assistant",
                                "content": final_message.content
                            })
                    else:
                        # No function calls, just add the response
                        if assistant_message.content:
                            st.session_state.messages.append({
                                "type": "assistant",
                                "content": assistant_message.content
                            })
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()