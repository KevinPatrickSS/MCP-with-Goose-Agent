"""
Auto-generated OpenAI function tool schemas.
Generated using schema_generator.py
"""
from typing import List, Dict, Any


def compare_resorts_by_highest_rating_schema() -> Dict[str, Any]:
    """Auto-generated schema for compare_resorts_by_highest_rating function."""
    return {
    "type": "function",
    "function": {
        "name": "compare_resorts_by_highest_rating",
        "description": "Compare resorts by their highest ratings and provide detailed comparison analysis.",
        "parameters": {
            "type": "object",
            "properties": {
                "country": {
                    "type": "string",
                    "description": "The country parameter"
                },
                "state": {
                    "type": "string",
                    "description": "The state parameter"
                },
                "city": {
                    "type": "string",
                    "description": "The city parameter"
                },
                "min_rating": {
                    "type": "number",
                    "description": "The min_rating parameter"
                },
                "limit": {
                    "type": "integer",
                    "description": "The limit parameter"
                },
                "rating_type": {
                    "type": "string",
                    "description": "The rating_type parameter"
                },
                "debug": {
                    "type": "boolean",
                    "description": "The debug parameter"
                }
            },
            "required": [],
            "additionalProperties": False
        }
    }
}


def get_amenity_details_schema() -> Dict[str, Any]:
    """Auto-generated schema for get_amenity_details function."""
    return {
    "type": "function",
    "function": {
        "name": "get_amenity_details",
        "description": "Get all details for a specific amenity by its ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "amenity_id": {
                    "type": "integer",
                    "description": "The amenity_id parameter"
                }
            },
            "required": [
                "amenity_id"
            ],
            "additionalProperties": False
        }
    }
}


def get_available_resorts_schema() -> Dict[str, Any]:
    """Auto-generated schema for get_available_resorts function."""
    return {
    "type": "function",
    "function": {
        "name": "get_available_resorts",
        "description": "List all available resorts with their basic information",
        "parameters": {
            "type": "object",
            "properties": {
                "country": {
                    "type": "string",
                    "description": "The country parameter"
                },
                "city": {
                    "type": "string",
                    "description": "The city parameter"
                },
                "state": {
                    "type": "string",
                    "description": "The state parameter"
                },
                "status": {
                    "type": "string",
                    "description": "The status parameter"
                },
                "limit": {
                    "type": "integer",
                    "description": "The limit parameter"
                }
            },
            "required": [],
            "additionalProperties": False
        }
    }
}


def get_booking_details_schema() -> Dict[str, Any]:
    """Auto-generated schema for get_booking_details function."""
    return {
    "type": "function",
    "function": {
        "name": "get_booking_details",
        "description": "Get detailed information about a specific booking by its ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "booking_id": {
                    "type": "integer",
                    "description": "The booking_id parameter"
                },
                "fields": {
                    "type": "string",
                    "description": "The fields parameter"
                }
            },
            "required": [
                "booking_id"
            ],
            "additionalProperties": False
        }
    }
}


def get_database_url_schema() -> Dict[str, Any]:
    """Auto-generated schema for get_database_url function."""
    return {
    "type": "function",
    "function": {
        "name": "get_database_url",
        "description": "Get database URL from environment variables.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False
        }
    }
}


def get_featured_listings_schema() -> Dict[str, Any]:
    """Auto-generated schema for get_featured_listings function."""
    return {
    "type": "function",
    "function": {
        "name": "get_featured_listings",
        "description": "Get featured listings.",
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "The limit parameter"
                }
            },
            "required": [],
            "additionalProperties": False
        }
    }
}


def get_listing_details_schema() -> Dict[str, Any]:
    """Auto-generated schema for get_listing_details function."""
    return {
    "type": "function",
    "function": {
        "name": "get_listing_details",
        "description": "Get all details for a specific listing by its ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "listing_id": {
                    "type": "integer",
                    "description": "The listing_id parameter"
                }
            },
            "required": [
                "listing_id"
            ],
            "additionalProperties": False
        }
    }
}


def get_price_range_summary_schema() -> Dict[str, Any]:
    """Auto-generated schema for get_price_range_summary function."""
    return {
    "type": "function",
    "function": {
        "name": "get_price_range_summary",
        "description": "Get price range summary for resorts in a specific location.",
        "parameters": {
            "type": "object",
            "properties": {
                "country": {
                    "type": "string",
                    "description": "The country parameter"
                },
                "state": {
                    "type": "string",
                    "description": "The state parameter"
                }
            },
            "required": [],
            "additionalProperties": False
        }
    }
}


def get_resort_details_schema() -> Dict[str, Any]:
    """Auto-generated schema for get_resort_details function."""
    return {
    "type": "function",
    "function": {
        "name": "get_resort_details",
        "description": "Get detailed information about a specific resort",
        "parameters": {
            "type": "object",
            "properties": {
                "resort_id": {
                    "type": "integer",
                    "description": "The resort_id parameter"
                }
            },
            "required": [
                "resort_id"
            ],
            "additionalProperties": False
        }
    }
}


def get_resort_price_schema() -> Dict[str, Any]:
    """Auto-generated schema for get_resort_price function."""
    return {
    "type": "function",
    "function": {
        "name": "get_resort_price",
        "description": "Enhanced version of get_resort_price with better debugging and flexible matching.",
        "parameters": {
            "type": "object",
            "properties": {
                "resort_name": {
                    "type": "string",
                    "description": "The resort_name parameter"
                },
                "country": {
                    "type": "string",
                    "description": "The country parameter"
                },
                "city": {
                    "type": "string",
                    "description": "The city parameter"
                },
                "state": {
                    "type": "string",
                    "description": "The state parameter"
                },
                "min_price": {
                    "type": "number",
                    "description": "The min_price parameter"
                },
                "max_price": {
                    "type": "number",
                    "description": "The max_price parameter"
                },
                "unit_type": {
                    "type": "string",
                    "description": "The unit_type parameter"
                },
                "nights": {
                    "type": "integer",
                    "description": "The nights parameter"
                },
                "currency_code": {
                    "type": "string",
                    "description": "The currency_code parameter"
                },
                "limit": {
                    "type": "integer",
                    "description": "The limit parameter"
                },
                "debug": {
                    "type": "boolean",
                    "description": "The debug parameter"
                }
            },
            "required": [],
            "additionalProperties": False
        }
    }
}


def get_user_bookings_schema() -> Dict[str, Any]:
    """Auto-generated schema for get_user_bookings function."""
    return {
    "type": "function",
    "function": {
        "name": "get_user_bookings",
        "description": "Fetch all bookings for a user by name",
        "parameters": {
            "type": "object",
            "properties": {
                "user_email": {
                    "type": "string",
                    "description": "The user_email parameter"
                }
            },
            "required": [
                "user_email"
            ],
            "additionalProperties": False
        }
    }
}


def get_user_profile_schema() -> Dict[str, Any]:
    """Auto-generated schema for get_user_profile function."""
    return {
    "type": "function",
    "function": {
        "name": "get_user_profile",
        "description": "Get user profile information.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_email": {
                    "type": "string",
                    "description": "The user_email parameter"
                }
            },
            "required": [
                "user_email"
            ],
            "additionalProperties": False
        }
    }
}


def get_weekend_listings_schema() -> Dict[str, Any]:
    """Auto-generated schema for get_weekend_listings function."""
    return {
    "type": "function",
    "function": {
        "name": "get_weekend_listings",
        "description": "Get listings with weekend availability.",
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "The limit parameter"
                }
            },
            "required": [],
            "additionalProperties": False
        }
    }
}


def search_available_future_listings_enhanced_schema() -> Dict[str, Any]:
    """Auto-generated schema for search_available_future_listings_enhanced function."""
    return {
    "type": "function",
    "function": {
        "name": "search_available_future_listings_enhanced",
        "description": "Search for available resort listings with intelligent date handling and flexible search options.",
        "parameters": {
            "type": "object",
            "properties": {
                "resort_id": {
                    "type": "integer",
                    "description": "The resort_id parameter"
                },
                "check_in_date": {
                    "type": "string",
                    "description": "The check_in_date parameter"
                },
                "check_out_date": {
                    "type": "string",
                    "description": "The check_out_date parameter"
                },
                "nights": {
                    "type": "integer",
                    "description": "The nights parameter"
                },
                "country": {
                    "type": "string",
                    "description": "The country parameter"
                },
                "city": {
                    "type": "string",
                    "description": "The city parameter"
                },
                "state": {
                    "type": "string",
                    "description": "The state parameter"
                },
                "limit": {
                    "type": "integer",
                    "description": "The limit parameter"
                },
                "flexible_dates": {
                    "type": "boolean",
                    "description": "The flexible_dates parameter"
                },
                "debug": {
                    "type": "boolean",
                    "description": "The debug parameter"
                }
            },
            "required": [],
            "additionalProperties": False
        }
    }
}


def search_available_listings_schema() -> Dict[str, Any]:
    """Auto-generated schema for search_available_listings function."""
    return {
    "type": "function",
    "function": {
        "name": "search_available_listings",
        "description": "Search for available listings with various filters.",
        "parameters": {
            "type": "object",
            "properties": {
                "resort_id": {
                    "type": "integer",
                    "description": "The resort_id parameter"
                },
                "check_in_date": {
                    "type": "string",
                    "description": "The check_in_date parameter"
                },
                "check_out_date": {
                    "type": "string",
                    "description": "The check_out_date parameter"
                },
                "nights": {
                    "type": "integer",
                    "description": "The nights parameter"
                },
                "country": {
                    "type": "string",
                    "description": "The country parameter"
                },
                "limit": {
                    "type": "integer",
                    "description": "The limit parameter"
                }
            },
            "required": [],
            "additionalProperties": False
        }
    }
}


def search_listings_by_type_schema() -> Dict[str, Any]:
    """Auto-generated schema for search_listings_by_type function."""
    return {
    "type": "function",
    "function": {
        "name": "search_listings_by_type",
        "description": "Get listings by type.",
        "parameters": {
            "type": "object",
            "properties": {
                "listing_type": {
                    "type": "string",
                    "description": "The listing_type parameter"
                },
                "limit": {
                    "type": "integer",
                    "description": "The limit parameter"
                }
            },
            "required": [
                "listing_type"
            ],
            "additionalProperties": False
        }
    }
}


def search_resorts_by_amenities_schema() -> Dict[str, Any]:
    """Auto-generated schema for search_resorts_by_amenities function."""
    return {
    "type": "function",
    "function": {
        "name": "search_resorts_by_amenities",
        "description": "Search for resorts that have specific amenities.",
        "parameters": {
            "type": "object",
            "properties": {
                "amenities": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "The amenities parameter"
                },
                "limit": {
                    "type": "integer",
                    "description": "The limit parameter"
                }
            },
            "required": [
                "amenities"
            ],
            "additionalProperties": False
        }
    }
}


def test_database_connection_schema() -> Dict[str, Any]:
    """Auto-generated schema for test_database_connection function."""
    return {
    "type": "function",
    "function": {
        "name": "test_database_connection",
        "description": "Test if the database connection works.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False
        }
    }
}


def get_all_function_schemas() -> List[Dict[str, Any]]:
    """Get all auto-generated OpenAI-compatible function schemas."""
    return [
        compare_resorts_by_highest_rating_schema(),
        get_amenity_details_schema(),
        get_available_resorts_schema(),
        get_booking_details_schema(),
        get_database_url_schema(),
        get_featured_listings_schema(),
        get_listing_details_schema(),
        get_price_range_summary_schema(),
        get_resort_details_schema(),
        get_resort_price_schema(),
        get_user_bookings_schema(),
        get_user_profile_schema(),
        get_weekend_listings_schema(),
        search_available_future_listings_enhanced_schema(),
        search_available_listings_schema(),
        search_listings_by_type_schema(),
        search_resorts_by_amenities_schema(),
        test_database_connection_schema(),
    ]

# Export all schemas as a list
ALL_FUNCTION_SCHEMAS = get_all_function_schemas()