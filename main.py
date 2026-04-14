"""
Main application for resort booking system with OpenAI function calling.
Updated to properly handle dictionary returns from tools.
"""
import os
import json
from typing import Dict, Any, List
from openai import OpenAI
from schemas import ALL_FUNCTION_SCHEMAS
from tools import call_tool
import re
from dotenv import load_dotenv
from assistant_thread import AssistantThread

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

# Initialize OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here")
)

def process_function_call(function_call) -> str:
    """
    Process a function call from OpenAI and return the result.
    
    Args:
        function_call: The function call object from OpenAI
        
    Returns:
        JSON string result of the function call
    """
    function_name = function_call.name
    
    # Parse arguments
    try:
        arguments = json.loads(function_call.arguments)
    except json.JSONDecodeError:
        return json.dumps({"error": "Invalid JSON arguments"})
    
    # Call the tool function - this returns a dict
    result = call_tool(function_name, **arguments)
    
    # Ensure result is serializable and return as JSON string
    if isinstance(result, dict):
        return json.dumps(result, indent=2, default=str)
    else:
        # Handle edge case where result might not be a dict
        return json.dumps({"result": result}, indent=2, default=str)


def chat_with_functions(user_message: str, max_iterations: int = 5) -> str:
    """
    Chat with OpenAI using function calling for resort booking queries.
    
    Args:
        user_message: The user's message/query
        max_iterations: Maximum number of function call iterations
        
    Returns:
        The assistant's final response
    """
    total_tokens = 0
    total_prompt_tokens = 0
    total_completion_tokens = 0
    
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful and friendly assistant for a resort booking system. "
                "When responding to users, always format your responses in a clear, human-readable way with:\n"
                "- Use emojis and formatting to make responses visually appealing\n"
                "- Structure information with bullet points, numbered lists, or sections\n"
                "- Use bold text (**text**) for important information like resort names, dates, prices\n"
                "- Present booking information in an organized, easy-to-read format\n"
                "- Be conversational and helpful in your tone\n"
                "- When showing multiple items, use clear numbering or bullet points\n"
                "- Include relevant details but keep responses concise and scannable\n"
                "Use the available functions to fetch real-time data from the database and always "
                "present the information in a beautiful, formatted way that's easy for humans to read."
            )
        },
        {
            "role": "user",
            "content": user_message
        }
    ]
    
    for iteration in range(max_iterations):
        try:
            # Make API call with function definitions
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages,
                tools=ALL_FUNCTION_SCHEMAS,
                tool_choice="auto"
            )
            
            assistant_message = response.choices[0].message
            
            # Add assistant message to conversation
            messages.append({
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": assistant_message.tool_calls
            })
            
            # Display token usage information
            if hasattr(response, 'usage') and response.usage:
                total_prompt_tokens += response.usage.prompt_tokens
                total_completion_tokens += response.usage.completion_tokens
                total_tokens += response.usage.total_tokens
                call_cost = calculate_cost(response.usage.prompt_tokens, response.usage.completion_tokens)
                print(f"📊 Token Usage - Prompt: {response.usage.prompt_tokens}, Completion: {response.usage.completion_tokens}, Total: {response.usage.total_tokens}, Cost: ${call_cost:.4f}")
            
            # Check if assistant wants to call functions
            if assistant_message.tool_calls:
                # Process each function call
                for tool_call in assistant_message.tool_calls:
                    function_result = process_function_call(tool_call.function)
                    print("🔧 Called function:", tool_call.function.name, "with args:", tool_call.function.arguments)
                    # Add function result to conversation
                    messages.append({
                        "role": "tool",
                        "content": function_result,
                        "tool_call_id": tool_call.id
                    })
                
                # Continue the conversation to get final response
                continue
            else:
                # No function calls, return the assistant's response
                final_response = assistant_message.content or "I'm sorry, I couldn't process your request."
                total_cost = calculate_cost(total_prompt_tokens, total_completion_tokens)
                print(f"💰 Total Session Usage - Prompt: {total_prompt_tokens}, Completion: {total_completion_tokens}, Total: {total_tokens} tokens, Cost: ${total_cost:.4f}")
                return final_response
                
        except Exception as e:
            if total_tokens > 0:
                total_cost = calculate_cost(total_prompt_tokens, total_completion_tokens)
                print(f"💰 Total Session Usage - Prompt: {total_prompt_tokens}, Completion: {total_completion_tokens}, Total: {total_tokens} tokens, Cost: ${total_cost:.4f}")
            return f"Error: {str(e)}"
    
    if total_tokens > 0:
        total_cost = calculate_cost(total_prompt_tokens, total_completion_tokens)
        print(f"💰 Total Session Usage - Prompt: {total_prompt_tokens}, Completion: {total_completion_tokens}, Total: {total_tokens} tokens, Cost: ${total_cost:.4f}")
    return "Maximum iterations reached. Please try again with a simpler query."

def main():
    print("🏖️  Resort Booking System with OpenAI Function Calling")
    print("=" * 60)
    thread = AssistantThread()
    print(f"Thread ID: {thread.thread_id}")

    while True:
        print("\nEnter your query (or 'quit' to exit):")
        user_input = input("> ").strip()
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Goodbye! 👋")
            break
        if not user_input:
            continue

        thread.add_user_message(user_input)
        print("\n🤖 Processing your request...")
        print("-" * 40)

        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=thread.get_history(),
            tools=ALL_FUNCTION_SCHEMAS,
            tool_choice="auto"
        )
        assistant_message = response.choices[0].message
        thread.add_assistant_message({
            "role": "assistant",
            "content": assistant_message.content,
            "tool_calls": assistant_message.tool_calls
        })
        
        # Only print content if it exists and isn't just function calls
        if assistant_message.content and assistant_message.content.strip():
            print("Assistant:", assistant_message.content)
            print("-" * 40)
        elif assistant_message.tool_calls:
            print("🔄 Processing function calls...")
            print("-" * 40)

        # Handle tool calls
        if assistant_message.tool_calls:
            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                
                # Call your Python function - returns a dict
                tool_result = call_tool(function_name, **arguments)
                
                # Convert dict to JSON string for OpenAI
                if isinstance(tool_result, dict):
                    tool_result_str = json.dumps(tool_result, indent=2, default=str)
                else:
                    tool_result_str = json.dumps({"result": tool_result}, indent=2, default=str)
                
                # Add tool response message
                thread.add_assistant_message({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result_str
                })
                print(f"✅ Function '{function_name}' executed successfully")
                
            # Now, send the updated history to OpenAI to get the final assistant reply
            print("🧠 Generating final response...")
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=thread.get_history(),
                tools=ALL_FUNCTION_SCHEMAS,
                tool_choice="auto"
            )
            assistant_message = response.choices[0].message
            thread.add_assistant_message({
                "role": "assistant",
                "content": assistant_message.content
            })
            if assistant_message.content:
                print("Assistant:", assistant_message.content)
            else:
                print("Assistant: I apologize, but I couldn't generate a response.")
            print("-" * 40)

def demo_function_schemas():
    """
    Demonstrate the function schemas that are available.
    """
    print("\n📋 Available Function Schemas:")
    print("=" * 50)
    
    for schema in ALL_FUNCTION_SCHEMAS:
        function_info = schema["function"]
        print(f"\n📌 {function_info['name']}")
        print(f"   Description: {function_info['description']}")
        
        if function_info["parameters"]["properties"]:
            print("   Parameters:")
            for param_name, param_info in function_info["parameters"]["properties"].items():
                required = param_name in function_info["parameters"].get("required", [])
                print(f"     - {param_name} ({param_info['type']}){' *required' if required else ''}")
                print(f"       {param_info['description']}")
        else:
            print("   Parameters: None")


def test_tools_directly():
    """
    Test the tools directly without OpenAI API.
    """
    print("\n🔧 Testing Tools Directly:")
    print("=" * 40)
    
    # Test get_user_bookings
    print("\n1. Testing get_user_bookings('John Doe'):")
    result = call_tool("get_user_bookings", user_name="John Doe")
    # Since result is a dict, we can print it nicely
    print("Result type:", type(result))
    print("Result content:")
    print(json.dumps(result, indent=2, default=str))
    
    # Test get_available_resorts
    print("\n2. Testing get_available_resorts():")
    result = call_tool("get_available_resorts")
    print("Result type:", type(result))
    print("Result content:")
    print(json.dumps(result, indent=2, default=str))
    
    # Test get_resort_details
    print("\n3. Testing get_resort_details('Paradise Bay Resort'):")
    result = call_tool("get_resort_details", resort_name="Paradise Bay Resort")
    print("Result type:", type(result))
    print("Result content:")
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY environment variable not set!")
        print("   Set it with: export OPENAI_API_KEY='your-api-key-here'")
        print("   For now, running in demo mode...\n")
        
        # Run demos without OpenAI API
        demo_function_schemas()
        test_tools_directly()
    else:
        # Run full application with OpenAI API
        main()