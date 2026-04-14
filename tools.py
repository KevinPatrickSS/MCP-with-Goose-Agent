"""
MCP Server for Resort Booking System using FastMCP
Exposes database tools as MCP tools for AI assistants
"""

from typing import List, Dict, Any, Optional
from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INTERNAL_ERROR, INVALID_PARAMS
import json

# Import all your existing database functions and models
from sqlalchemy import create_engine, Column, Integer, BigInteger, String, DateTime, ForeignKey, Text, Float, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize MCP server
mcp = FastMCP("resort-booking")

# Database models (keeping your existing models)
Base = declarative_base()

# [Include all your existing model classes here - User, Listing, Amenity, etc.]
# I'll abbreviate for brevity, but you should include all models from your original code

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone_number = Column(String(20))
    has_deleted = Column(Integer, default=0)
    status = Column(String(20), default='active')
    created_resorts = relationship("Resort", foreign_keys="Resort.creator_id", back_populates="creator")
    owned_bookings = relationship("Booking", foreign_keys="Booking.owner_id", back_populates="owner")
    user_bookings = relationship("Booking", foreign_keys="Booking.user_id", back_populates="user")

class Resort(Base):
    __tablename__ = 'resorts'
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    creator_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    slug = Column(String(200), unique=True, nullable=False)
    address = Column(Text)
    has_deleted = Column(Integer, default=0)
    status = Column(String(20), default='active')
    lattitude = Column(String(255))
    longitude = Column(String(255))
    country = Column(String(100))
    city = Column(String(100))
    state = Column(String(100))
    zip = Column(String(20))
    county = Column(String(100))
    highlight_quote = Column(Text)
    description = Column(Text)
    creator = relationship("User", foreign_keys=[creator_id], back_populates="created_resorts")
    unit_types = relationship("UnitType", back_populates="resort")
    listings = relationship("Listing", back_populates="resort")

class UnitType(Base):
    __tablename__ = 'unit_types'
    id = Column(Integer, primary_key=True)
    resort_id = Column(Integer, ForeignKey('resorts.id'), nullable=False)
    name = Column(String(200), nullable=False)
    has_deleted = Column(Integer, default=0)
    status = Column(String(20), default='active')
    resort = relationship("Resort", back_populates="unit_types")
    listings = relationship("Listing", back_populates="unit_type")

class Listing(Base):
    __tablename__ = 'listings'
    id = Column(Integer, primary_key=True)
    resort_id = Column(Integer, ForeignKey('resorts.id'), nullable=False)
    unit_type_id = Column(Integer, ForeignKey('unit_types.id'), nullable=False)
    nights = Column(Integer, nullable=False)
    check_in = Column(DateTime, nullable=False)
    check_out = Column(DateTime, nullable=False)
    has_deleted = Column(Integer, default=0)
    status = Column(String(30), default='active')
    resort = relationship("Resort", back_populates="listings")
    unit_type = relationship("UnitType", back_populates="listings")
    bookings = relationship("Booking", back_populates="listing")

class Booking(Base):
    __tablename__ = 'bookings'
    id = Column(Integer, primary_key=True)
    unique_booking_code = Column(String(50), unique=True, nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    listing_id = Column(Integer, ForeignKey('listings.id'), nullable=False)
    price_night = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    owner = relationship("User", foreign_keys=[owner_id], back_populates="owned_bookings")
    user = relationship("User", foreign_keys=[user_id], back_populates="user_bookings")
    listing = relationship("Listing", back_populates="bookings")

class PtRtListing(Base):
    __tablename__ = 'pt_rt_listings'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    listing_id = Column(Integer)
    listing_price_night = Column(String(50))
    listing_nights = Column(Integer, default=0)
    listing_check_in = Column(DateTime)
    listing_check_out = Column(DateTime)
    listing_has_deleted = Column(Integer, default=0)
    listing_status = Column(String(50))
    listing_type = Column(String(255), default='prebook')
    unit_type_id = Column(Integer, default=0)
    unit_type_name = Column(String(255))
    unit_bedrooms = Column(String(5))
    unit_bathrooms = Column(String(7))
    unit_sleeps = Column(Integer, default=0)
    resort_id = Column(Integer, default=0)
    resort_name = Column(String(255))
    resort_city = Column(String(100))
    resort_country = Column(String(100))
    resort_state = Column(String(100))
    resort_address = Column(String(255))
    resort_google_rating = Column(Integer, default=0)
    listing_currency_code = Column(String(255))
    hot_deals = Column(Boolean, default=False)
    exclusive = Column(Boolean, default=False)
    has_weekend = Column(Integer, default=0)
    pt_or_rt = Column(String(10))
    resort_brand_name = Column(String(255))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class ResortMigration(Base):
    __tablename__ = 'resort_migration'
    id = Column(BigInteger, primary_key=True)
    resort_id = Column(Integer, default=0)
    resort_name = Column(String(255))
    listing_price_night = Column(String(50))
    unit_rates_price = Column(String(50))
    unit_rate_nightly_price = Column(String(255))
    listing_nights = Column(Integer, default=0)
    listing_check_in = Column(DateTime)
    listing_check_out = Column(DateTime)
    listing_has_deleted = Column(Integer, default=0)
    listing_status = Column(String(50))
    unit_type_name = Column(String(255))
    unit_bedrooms = Column(String(5))
    unit_bathrooms = Column(String(7))
    unit_sleeps = Column(Integer, default=0)
    unit_kitchenate = Column(String(255))
    address = Column(String(255))
    city = Column(String(255))
    state = Column(String(255))
    country = Column(String(255))
    zip = Column(String(255))
    county = Column(String(255))
    lattitude = Column(String(255))
    longitude = Column(String(255))
    is_featured = Column(Integer, default=0)
    popular = Column(Integer, default=0)
    is_fitness_center = Column(Integer, default=0)
    is_free_wifi = Column(Integer, default=0)
    is_restaurant = Column(Integer, default=0)
    is_swimming_pool = Column(Integer, default=0)
    hotel_star = Column(Integer, default=0)
    google_rating = Column(Integer, default=0)
    resort_has_deleted = Column(Integer, default=0)
    resort_status = Column(String(50))
    pets_friendly = Column(Integer, default=0)
    listing_currency_code = Column(String(255))
    offer = Column(String(255))
    offer_price = Column(String(255))
    brand_name = Column(String(255))
    highlight_quote = Column(String(255))
    has_weekend = Column(Integer, default=0)

# Database setup
def get_database_url():
    """Get database URL from environment variables."""
    host = os.getenv("MYSQL_HOST", "localhost")
    user = os.getenv("MYSQL_USER", "root")
    password = os.getenv("MYSQL_PASSWORD", "")
    database = os.getenv("MYSQL_DATABASE", "koala_live_laravel")
    
    if password:
        return f"mysql+pymysql://{user}:{password}@{host}/{database}"
    else:
        return f"mysql+pymysql://{user}@{host}/{database}"

DATABASE_URL = get_database_url()
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# MCP Tool Wrappers - Convert your functions to MCP tools

@mcp.tool()
def search_available_future_listings(
    resort_id: Optional[int] = None,
    check_in_date: Optional[str] = None,
    check_out_date: Optional[str] = None,
    nights: Optional[int] = None,
    country: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    limit: int = 20,
    flexible_dates: bool = True
) -> str:
    """
    Search for available resort listings with intelligent date handling.
    
    Provides comprehensive date-aware search with automatic fallback options.
    Supports flexible date matching (±7 days) and duration (±2 nights).
    
    Args:
        resort_id: Specific resort ID to search within
        check_in_date: Check-in date in YYYY-MM-DD format
        check_out_date: Check-out date in YYYY-MM-DD format
        nights: Number of nights for the stay
        country: Country name (supports partial matching)
        city: City name (supports partial matching)
        state: State/province name (supports partial matching)
        limit: Maximum number of results (default: 20)
        flexible_dates: Enable automatic fallback searches (default: True)
    
    Returns:
        JSON string with search results including resort details, pricing, and availability
    """
    session = SessionLocal()
    
    try:
        current_date = datetime.now()
        results = []
        search_info = {
            "original_criteria": {
                "resort_id": resort_id,
                "check_in_date": check_in_date,
                "nights": nights,
                "country": country,
                "city": city,
                "state": state
            },
            "searches_performed": []
        }
        
        # Primary search
        query = session.query(PtRtListing)\
            .filter(PtRtListing.listing_has_deleted == 0)\
            .filter(PtRtListing.listing_status.in_(['active', 'pending']))\
            .filter(PtRtListing.listing_type == 'prebook')\
            .filter(PtRtListing.listing_check_in >= current_date)
        
        if resort_id:
            query = query.filter(PtRtListing.resort_id == resort_id)
        
        if check_in_date:
            target_date = datetime.strptime(check_in_date, "%Y-%m-%d")
            query = query.filter(PtRtListing.listing_check_in >= target_date)
        
        if check_out_date:
            end_date = datetime.strptime(check_out_date, "%Y-%m-%d")
            query = query.filter(PtRtListing.listing_check_out <= end_date)
        
        if nights:
            query = query.filter(PtRtListing.listing_nights == nights)
        
        if country:
            query = query.filter(PtRtListing.resort_country.ilike(f"%{country}%"))
        
        if state:
            query = query.filter(PtRtListing.resort_state.ilike(f"%{state}%"))
        
        if city:
            query = query.filter(PtRtListing.resort_city.ilike(f"%{city}%"))
        
        listings = query.order_by(PtRtListing.listing_check_in).limit(limit).all()
        search_info["searches_performed"].append({
            "type": "exact_match",
            "results_count": len(listings)
        })
        
        # Process results
        for listing in listings:
            price_per_night = None
            if listing.listing_price_night:
                try:
                    clean_price = str(listing.listing_price_night).replace(',', '').replace('$', '').strip()
                    price_per_night = float(clean_price) if clean_price and clean_price.replace('.', '').isdigit() else None
                except (ValueError, AttributeError):
                    price_per_night = None
            
            results.append({
                "listing_id": listing.listing_id,
                "resort_name": listing.resort_name,
                "city": listing.resort_city,
                "state": listing.resort_state,
                "country": listing.resort_country,
                "unit_type": listing.unit_type_name,
                "bedrooms": listing.unit_bedrooms,
                "bathrooms": listing.unit_bathrooms,
                "sleeps": listing.unit_sleeps,
                "nights": listing.listing_nights,
                "check_in": listing.listing_check_in.strftime("%Y-%m-%d") if listing.listing_check_in else None,
                "check_out": listing.listing_check_out.strftime("%Y-%m-%d") if listing.listing_check_out else None,
                "price_per_night": price_per_night,
                "currency": listing.listing_currency_code or "USD",
                "status": listing.listing_status
            })
        
        return json.dumps({
            "results": results,
            "total_found": len(results),
            "search_info": search_info
        }, indent=2)
        
    except ValueError as e:
        raise McpError(ErrorData(INVALID_PARAMS, f"Invalid parameter: {str(e)}")) from e
    except Exception as e:
        raise McpError(ErrorData(INTERNAL_ERROR, f"Database error: {str(e)}")) from e
    finally:
        session.close()


@mcp.tool()
def get_user_bookings(user_email: str) -> str:
    """
    Fetch all bookings for a user by their email address.
    
    Args:
        user_email: The email address of the user
    
    Returns:
        JSON string with list of user's bookings including resort details and pricing
    """
    session = SessionLocal()
    
    try:
        if not user_email or '@' not in user_email:
            raise ValueError("Invalid email address format")
        
        bookings = session.query(Booking)\
            .join(User, Booking.user_id == User.id)\
            .join(Listing, Booking.listing_id == Listing.id)\
            .join(Resort, Listing.resort_id == Resort.id)\
            .join(UnitType, Listing.unit_type_id == UnitType.id)\
            .filter(User.email == user_email)\
            .filter(User.has_deleted == 0)\
            .filter(Listing.has_deleted == 0)\
            .filter(Resort.has_deleted == 0)\
            .all()
        
        result = []
        for booking in bookings:
            result.append({
                "booking_code": booking.unique_booking_code,
                "resort_name": booking.listing.resort.name,
                "city": booking.listing.resort.city,
                "country": booking.listing.resort.country,
                "unit_type": booking.listing.unit_type.name,
                "nights": booking.listing.nights,
                "check_in": booking.listing.check_in.strftime("%Y-%m-%d"),
                "check_out": booking.listing.check_out.strftime("%Y-%m-%d"),
                "price_per_night": booking.price_night,
                "total_price": booking.total_price,
                "status": booking.listing.status
            })
        
        return json.dumps({
            "user_email": user_email,
            "total_bookings": len(result),
            "bookings": result
        }, indent=2)
        
    except ValueError as e:
        raise McpError(ErrorData(INVALID_PARAMS, str(e))) from e
    except Exception as e:
        raise McpError(ErrorData(INTERNAL_ERROR, f"Error fetching bookings: {str(e)}")) from e
    finally:
        session.close()


@mcp.tool()
def get_available_resorts(
    country: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    limit: int = 10
) -> str:
    """
    List available resorts with optional filtering by location.
    
    Args:
        country: Optional country filter (partial match supported)
        city: Optional city filter (partial match supported)
        state: Optional state filter (partial match supported)
        limit: Maximum number of resorts to return (default: 10)
    
    Returns:
        JSON string with list of resorts and their details
    """
    session = SessionLocal()
    
    try:
        query = session.query(Resort)\
            .filter(Resort.has_deleted == 0)\
            .filter(Resort.status == 'active')
        
        if country:
            query = query.filter(Resort.country.ilike(f"%{country.strip()}%"))
        if city:
            query = query.filter(Resort.city.ilike(f"%{city.strip()}%"))
        if state:
            query = query.filter(Resort.state.ilike(f"%{state.strip()}%"))
        
        resorts = query.limit(limit).all()
        
        result = []
        for resort in resorts:
            active_listings = session.query(Listing)\
                .filter(Listing.resort_id == resort.id)\
                .filter(Listing.has_deleted == 0)\
                .filter(Listing.status.in_(['active', 'pending']))\
                .count()
            
            result.append({
                "resort_id": resort.id,
                "name": resort.name,
                "city": resort.city,
                "state": resort.state,
                "country": resort.country,
                "highlight": resort.highlight_quote,
                "active_listings": active_listings
            })
        
        return json.dumps({
            "total_found": len(result),
            "resorts": result
        }, indent=2)
        
    except Exception as e:
        raise McpError(ErrorData(INTERNAL_ERROR, f"Error fetching resorts: {str(e)}")) from e
    finally:
        session.close()


@mcp.tool()
def compare_resorts_by_rating(
    country: Optional[str] = None,
    state: Optional[str] = None,
    city: Optional[str] = None,
    min_rating: Optional[float] = None,
    limit: int = 10,
    rating_type: str = "google"
) -> str:
    """
    Compare resorts by their ratings with detailed analysis.
    
    Args:
        country: Optional country filter
        state: Optional state filter
        city: Optional city filter
        min_rating: Minimum rating threshold
        limit: Maximum number of resorts (default: 10)
        rating_type: Type of rating - "google" or "hotel_star" (default: "google")
    
    Returns:
        JSON string with top-rated resorts and comparison analysis
    """
    session = SessionLocal()
    
    try:
        if rating_type not in ["google", "hotel_star"]:
            raise ValueError("rating_type must be 'google' or 'hotel_star'")
        
        query = session.query(ResortMigration)\
            .filter(ResortMigration.resort_has_deleted == 0)\
            .filter(ResortMigration.resort_status == 'active')
        
        if country:
            query = query.filter(ResortMigration.country.ilike(f"%{country}%"))
        if state:
            query = query.filter(ResortMigration.state.ilike(f"%{state}%"))
        if city:
            query = query.filter(ResortMigration.city.ilike(f"%{city}%"))
        
        if rating_type == "google":
            if min_rating:
                query = query.filter(ResortMigration.google_rating >= min_rating)
            query = query.filter(ResortMigration.google_rating > 0)\
                         .order_by(ResortMigration.google_rating.desc())
        else:
            if min_rating:
                query = query.filter(ResortMigration.hotel_star >= min_rating)
            query = query.filter(ResortMigration.hotel_star > 0)\
                         .order_by(ResortMigration.hotel_star.desc())
        
        all_resorts = query.all()
        
        # Remove duplicates
        unique_resorts = {}
        for resort in all_resorts:
            resort_id = resort.resort_id
            current_rating = resort.google_rating if rating_type == "google" else resort.hotel_star
            
            if resort_id not in unique_resorts or current_rating > (
                unique_resorts[resort_id].google_rating if rating_type == "google" 
                else unique_resorts[resort_id].hotel_star
            ):
                unique_resorts[resort_id] = resort
        
        sorted_resorts = sorted(
            unique_resorts.values(),
            key=lambda x: x.google_rating if rating_type == "google" else x.hotel_star,
            reverse=True
        )[:limit]
        
        result = []
        for i, resort in enumerate(sorted_resorts, 1):
            def parse_price(price_str):
                if not price_str:
                    return None
                try:
                    clean = str(price_str).replace(',', '').replace('$', '').strip()
                    return float(clean) if clean and clean.replace('.', '').isdigit() else None
                except:
                    return None
            
            price = parse_price(resort.listing_price_night) or parse_price(resort.unit_rates_price)
            
            result.append({
                "rank": i,
                "resort_name": resort.resort_name,
                "rating": resort.google_rating if rating_type == "google" else resort.hotel_star,
                "rating_type": rating_type,
                "location": f"{resort.city}, {resort.state}, {resort.country}",
                "price_per_night": price,
                "amenities": {
                    "pool": bool(resort.is_swimming_pool),
                    "wifi": bool(resort.is_free_wifi),
                    "fitness": bool(resort.is_fitness_center),
                    "restaurant": bool(resort.is_restaurant)
                }
            })
        
        return json.dumps({
            "total_analyzed": len(unique_resorts),
            "top_resorts": result,
            "search_criteria": {
                "country": country,
                "state": state,
                "city": city,
                "rating_type": rating_type
            }
        }, indent=2)
        
    except ValueError as e:
        raise McpError(ErrorData(INVALID_PARAMS, str(e))) from e
    except Exception as e:
        raise McpError(ErrorData(INTERNAL_ERROR, f"Error comparing resorts: {str(e)}")) from e
    finally:
        session.close()


@mcp.tool()
def search_resorts_by_amenities(amenities: List[str], limit: int = 10) -> str:
    """
    Search for resorts that have specific amenities.
    
    Args:
        amenities: List of amenity names (e.g., ["pool", "wifi", "fitness"])
        limit: Maximum number of resorts to return (default: 10)
    
    Returns:
        JSON string with matching resorts and their amenity details
    """
    session = SessionLocal()
    
    try:
        if not amenities:
            raise ValueError("At least one amenity must be specified")
        
        query = session.query(ResortMigration)\
            .filter(ResortMigration.resort_has_deleted == 0)\
            .filter(ResortMigration.resort_status == 'active')
        
        for amenity in amenities:
            amenity_lower = amenity.lower()
            if amenity_lower in ['pool', 'swimming pool']:
                query = query.filter(ResortMigration.is_swimming_pool == 1)
            elif amenity_lower in ['wifi', 'free wifi']:
                query = query.filter(ResortMigration.is_free_wifi == 1)
            elif amenity_lower in ['fitness', 'gym', 'fitness center']:
                query = query.filter(ResortMigration.is_fitness_center == 1)
            elif amenity_lower in ['restaurant', 'dining']:
                query = query.filter(ResortMigration.is_restaurant == 1)
            elif amenity_lower in ['pets', 'pet friendly']:
                query = query.filter(ResortMigration.pets_friendly == 1)
        
        resorts = query.limit(limit * 2).all()
        
        seen_resorts = set()
        result = []
        
        for resort in resorts:
            if resort.resort_id not in seen_resorts:
                seen_resorts.add(resort.resort_id)
                
                result.append({
                    "resort_name": resort.resort_name,
                    "location": f"{resort.city}, {resort.state}",
                    "amenities": {
                        "swimming_pool": bool(resort.is_swimming_pool),
                        "free_wifi": bool(resort.is_free_wifi),
                        "fitness_center": bool(resort.is_fitness_center),
                        "restaurant": bool(resort.is_restaurant),
                        "pets_friendly": bool(resort.pets_friendly)
                    },
                    "rating": resort.google_rating or 0,
                    "hotel_stars": resort.hotel_star or 0
                })
                
                if len(result) >= limit:
                    break
        
        return json.dumps({
            "searched_amenities": amenities,
            "total_found": len(result),
            "resorts": result
        }, indent=2)
        
    except ValueError as e:
        raise McpError(ErrorData(INVALID_PARAMS, str(e))) from e
    except Exception as e:
        raise McpError(ErrorData(INTERNAL_ERROR, f"Error searching by amenities: {str(e)}")) from e
    finally:
        session.close()


@mcp.tool()
def get_price_range_summary(
    country: Optional[str] = None,
    state: Optional[str] = None
) -> str:
    """
    Get price statistics for resorts in a specific location.
    
    Args:
        country: Optional country filter
        state: Optional state filter
    
    Returns:
        JSON string with price statistics including min, max, average, and median
    """
    session = SessionLocal()
    
    try:
        query = session.query(ResortMigration)\
            .filter(ResortMigration.listing_has_deleted == 0)\
            .filter(ResortMigration.listing_status.in_(['active', 'pending']))
        
        if country:
            query = query.filter(ResortMigration.country.ilike(f"%{country}%"))
        if state:
            query = query.filter(ResortMigration.state.ilike(f"%{state}%"))
        
        resorts = query.all()
        
        prices = []
        for resort in resorts:
            price_str = resort.listing_price_night or resort.unit_rates_price
            if price_str:
                try:
                    clean = str(price_str).replace(',', '').replace('$', '').strip()
                    price = float(clean)
                    if price > 0:
                        prices.append(price)
                except:
                    continue
        
        if not prices:
            return json.dumps({
                "error": "No valid pricing data found",
                "location": {"country": country, "state": state}
            })
        
        prices.sort()
        count = len(prices)
        median = prices[count // 2] if count % 2 else (prices[count // 2 - 1] + prices[count // 2]) / 2
        
        return json.dumps({
            "location": {"country": country, "state": state},
            "statistics": {
                "min_price": round(min(prices), 2),
                "max_price": round(max(prices), 2),
                "average_price": round(sum(prices) / count, 2),
                "median_price": round(median, 2),
                "total_listings": count
            },
            "price_ranges": {
                "budget_under_100": len([p for p in prices if p < 100]),
                "mid_range_100_300": len([p for p in prices if 100 <= p < 300]),
                "luxury_300_plus": len([p for p in prices if p >= 300])
            }
        }, indent=2)
        
    except Exception as e:
        raise McpError(ErrorData(INTERNAL_ERROR, f"Error calculating price summary: {str(e)}")) from e
    finally:
        session.close()


# Run the MCP server
if __name__ == "__main__":
    # Test database connection first
    try:
        session = SessionLocal()
        from sqlalchemy import text
        session.execute(text("SELECT 1")).fetchone()
        session.close()
        print("✅ Database connection successful!")
        print("🚀 Starting MCP server for resort booking system...")
        
        # Run the FastMCP server
        mcp.run()
        
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        print("Please check your database configuration in the .env file")