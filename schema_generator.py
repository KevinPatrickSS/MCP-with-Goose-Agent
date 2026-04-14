"""
Utility to automatically generate OpenAI function tool schemas from Python function signatures.
"""
import inspect
import json
import re
from typing import Dict, Any, List, get_type_hints, Union, Optional
from types import GenericAlias
from tools import get_user_bookings, get_available_resorts, get_resort_details


def python_type_to_json_schema(python_type: Any) -> Dict[str, Any]:
    """
    Convert Python type annotations to JSON schema format.
    
    Args:
        python_type: The Python type to convert
        
    Returns:
        JSON schema representation of the type
    """
    # Handle basic types
    if python_type == str:
        return {"type": "string"}
    elif python_type == int:
        return {"type": "integer"}
    elif python_type == float:
        return {"type": "number"}
    elif python_type == bool:
        return {"type": "boolean"}
    elif python_type == list or python_type == List:
        return {"type": "array"}
    elif python_type == dict or python_type == Dict:
        return {"type": "object"}
    
    # Handle generic types (List[str], Dict[str, int], etc.)
    if hasattr(python_type, '__origin__'):
        origin = python_type.__origin__
        args = python_type.__args__
        
        if origin == list or origin == List:
            if args:
                return {
                    "type": "array",
                    "items": python_type_to_json_schema(args[0])
                }
            return {"type": "array"}
        
        elif origin == dict or origin == Dict:
            schema = {"type": "object"}
            if len(args) >= 2:
                schema["additionalProperties"] = python_type_to_json_schema(args[1])
            return schema
        
        elif origin == Union:
            # Handle Optional types (Union[X, None])
            if len(args) == 2 and type(None) in args:
                non_none_type = args[0] if args[1] is type(None) else args[1]
                return python_type_to_json_schema(non_none_type)
            # For other unions, default to string
            return {"type": "string"}
    
    # Handle Optional types
    if hasattr(python_type, '__class__') and python_type.__class__.__name__ == '_GenericAlias':
        if python_type._name == 'Optional':
            return python_type_to_json_schema(python_type.__args__[0])
    
    # Default to string for unknown types
    return {"type": "string"}


def generate_function_schema(func: callable, description: str = None) -> Dict[str, Any]:
    """
    Generate OpenAI function schema from a Python function.
    
    Args:
        func: The Python function to generate schema for
        description: Optional description for the function
        
    Returns:
        OpenAI-compatible function schema
    """
    # Get function signature
    sig = inspect.signature(func)
    
    # Get type hints, handling forward references safely
    try:
        type_hints = get_type_hints(func)
    except (NameError, AttributeError):
        # Fallback to raw annotations if type hints evaluation fails
        type_hints = getattr(func, '__annotations__', {})
    
    # Get docstring if description not provided
    if description is None:
        description = func.__doc__ or f"Function {func.__name__}"
        # Clean up docstring
        description = description.strip().split('\n')[0] if description else f"Function {func.__name__}"
    
    # Build parameters schema
    properties = {}
    required = []
    
    for param_name, param in sig.parameters.items():
        # Skip 'self' parameter
        if param_name == 'self':
            continue
            
        # Get type from type hints
        param_type = type_hints.get(param_name, str)
        
        # Convert to JSON schema
        param_schema = python_type_to_json_schema(param_type)
        
        # Add description if available from docstring
        param_schema["description"] = f"The {param_name} parameter"
        
        properties[param_name] = param_schema
        
        # Check if parameter is required (no default value)
        if param.default == inspect.Parameter.empty:
            required.append(param_name)
    
    # Build the complete schema
    schema = {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
                "additionalProperties": False
            }
        }
    }
    
    return schema


def generate_schemas_from_module(module, function_descriptions: Dict[str, str] = None) -> List[Dict[str, Any]]:
    """
    Generate OpenAI function schemas from all functions in a module.
    
    Args:
        module: The module to extract functions from
        function_descriptions: Optional dictionary of function descriptions
        
    Returns:
        List of OpenAI-compatible function schemas
    """
    schemas = []
    function_descriptions = function_descriptions or {}
    
    # Get all functions from the module
    for name, obj in inspect.getmembers(module):
        if inspect.isfunction(obj) and not name.startswith('_'):
            # Skip internal functions and imported functions
            if name in ['init_database', 'call_tool'] or not hasattr(obj, '__module__'):
                continue
            
            # Only include functions defined in the target module
            if obj.__module__ != module.__name__:
                continue
                
            description = function_descriptions.get(name)
            schema = generate_function_schema(obj, description)
            schemas.append(schema)
    
    return schemas


def demonstrate_schema_generation():
    """
    Demonstrate automatic schema generation with example functions.
    """
    from tools import get_user_bookings, get_available_resorts, get_resort_details
    
    print("🔧 Automatic Schema Generation Demo")
    print("=" * 50)
    
    # Custom descriptions for better function documentation
    descriptions = {
        "get_user_bookings": "Fetch all bookings for a user by name",
        "get_available_resorts": "List all available resorts with their basic information",
        "get_resort_details": "Get detailed information about a specific resort"
    }
    
    # Generate schemas for individual functions
    functions = [
        (get_user_bookings, descriptions["get_user_bookings"]),
        (get_available_resorts, descriptions["get_available_resorts"]),
        (get_resort_details, descriptions["get_resort_details"])
    ]
    
    for func, desc in functions:
        print(f"\n📌 Schema for {func.__name__}:")
        schema = generate_function_schema(func, desc)
        print(json.dumps(schema, indent=2))
        print("-" * 40)


def generate_schemas_file():
    """
    Generate a new schemas.py file with automatically generated schemas.
    """
    import tools
    
    # Generate schemas from tools module
    descriptions = {
        "get_user_bookings": "Fetch all bookings for a user by name",
        "get_available_resorts": "List all available resorts with their basic information",
        "get_resort_details": "Get detailed information about a specific resort"
    }
    
    schemas = generate_schemas_from_module(tools, descriptions)
    
    # Generate Python code for the schemas file
    code = '''"""
Auto-generated OpenAI function tool schemas.
Generated using schema_generator.py
"""
from typing import List, Dict, Any

'''
    
    for i, schema in enumerate(schemas):
        func_name = schema['function']['name']
        code += f'''
def {func_name}_schema() -> Dict[str, Any]:
    """Auto-generated schema for {func_name} function."""
    return {json.dumps(schema, indent=4)}

'''
    
    code += '''
def get_all_function_schemas() -> List[Dict[str, Any]]:
    """Get all auto-generated OpenAI-compatible function schemas."""
    return [
'''
    
    for schema in schemas:
        func_name = schema['function']['name']
        code += f'        {func_name}_schema(),\n'
    
    code += '''    ]

# Export all schemas as a list
ALL_FUNCTION_SCHEMAS = get_all_function_schemas()
'''
    
    return code


if __name__ == "__main__":
    print("🤖 OpenAI Function Schema Generator")
    print("=" * 50)
    
    # Demonstrate the schema generation
    demonstrate_schema_generation()
    
    print("\n🔄 Generating new schemas.py file...")
    new_schemas_code = generate_schemas_file()
    
    print("\n📝 Generated schemas.py content:")
    print("=" * 50)
    print(new_schemas_code)
    
    # Optionally write to file
    with open("auto_schemas.py", "w") as f:
        f.write(new_schemas_code)
    
    print("\n✅ Auto-generated schemas saved to 'auto_schemas.py'")
    print("   You can replace the manual schemas.py with this auto-generated version!") 