from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn

from app.core.config import settings
from app.core.database import db
from app.api.routes import auth, journal, budget, recipe, mission, user_profile, challenge, ai_recipes, user_stats, achievements, meal_plans, smart_suggestions, home_sections
from app.api.routes import content
from app.api.routes import user_recipes
from app.api.routes import saved_prices
from app.api.routes import ingredient_catalog


# ==================== Create FastAPI App ====================

app = FastAPI(
    title="GoMums API",
    description="Backend API for GoMums - Smart budget and meal planning for families",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# ==================== CORS Middleware ====================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Startup & Shutdown Events ====================

@app.on_event("startup")
async def startup_event():
    """Initialize database connection pool and test connection"""
    print("\n" + "="*50)
    print("🚀 Starting GoMums Backend API")
    print("="*50)
    
    # Initialize database connection pool
    db.initialize()
    
    # Test database connection
    if db.test_connection():
        print("✓ All systems operational")
    else:
        print("✗ Database connection failed - please check your configuration")
        print("  Make sure PostgreSQL is running and .env file is properly configured")
    
    print(f"📝 API Documentation: http://localhost:{settings.PORT}/docs")
    print("="*50 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connections"""
    print("\n" + "="*50)
    print("👋 Shutting down GoMums Backend API")
    db.close()
    print("="*50 + "\n")


# ==================== Health Check Endpoint ====================

@app.get("/health", tags=["Health"])
def health_check():
    """
    Health check endpoint to verify the API is running
    
    Returns:
        Status information including timestamp and environment
    """
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "environment": settings.ENVIRONMENT,
        "service": "GoMums API",
        "version": "1.0.0"
    }


@app.get("/", tags=["Root"])
def root():
    """
    Root endpoint with API information
    """
    return {
        "message": "Welcome to GoMums API",
        "documentation": f"http://localhost:{settings.PORT}/docs",
        "health": f"http://localhost:{settings.PORT}/health"
    }


def get_response_schema(route) -> dict:
    """Extract response schema from route's response model"""
    response_info = {}
    
    # Get response model if defined
    if hasattr(route, "response_model") and route.response_model:
        model = route.response_model
        model_name = getattr(model, "__name__", str(model))
        response_info["response_model"] = model_name
        
        # Try to get the schema from pydantic model
        if hasattr(model, "model_json_schema"):
            try:
                schema = model.model_json_schema()
                response_info["response_schema"] = schema
            except Exception:
                pass
        elif hasattr(model, "schema"):
            try:
                schema = model.schema()
                response_info["response_schema"] = schema
            except Exception:
                pass
    
    # Get responses defined in the route
    if hasattr(route, "responses") and route.responses:
        response_info["responses"] = route.responses
    
    return response_info


def get_request_body_schema(route) -> dict:
    """Extract request body schema from route"""
    request_info = {}
    
    if hasattr(route, "body_field") and route.body_field:
        body = route.body_field
        if hasattr(body, "type_") and body.type_:
            model = body.type_
            model_name = getattr(model, "__name__", str(model))
            request_info["request_model"] = model_name
            
            if hasattr(model, "model_json_schema"):
                try:
                    schema = model.model_json_schema()
                    request_info["request_schema"] = schema
                except Exception:
                    pass
    
    return request_info


@app.get("/api/routes", tags=["Meta"])
def list_routes(include_schemas: bool = False):
    """
    List all available API routes - useful for AI agents to discover endpoints
    
    Returns a structured list of all routes with their methods, paths, and descriptions.
    
    - **include_schemas**: If true, includes full request/response JSON schemas (larger response)
    """
    routes = []
    for route in app.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            route_info = {
                "path": route.path,
                "methods": list(route.methods),
                "name": route.name,
                "description": route.description if hasattr(route, "description") else None,
                "tags": route.tags if hasattr(route, "tags") else []
            }
            
            # Add response model name (always include)
            if hasattr(route, "response_model") and route.response_model:
                model = route.response_model
                route_info["response_model"] = getattr(model, "__name__", str(model))
            
            # Add full schemas if requested
            if include_schemas:
                response_schema = get_response_schema(route)
                if response_schema:
                    route_info.update(response_schema)
                
                request_schema = get_request_body_schema(route)
                if request_schema:
                    route_info.update(request_schema)
            
            routes.append(route_info)
    
    return {
        "service": "GoMums API",
        "version": "1.0.0",
        "total_routes": len(routes),
        "openapi_schema": f"http://localhost:{settings.PORT}/openapi.json",
        "interactive_docs": f"http://localhost:{settings.PORT}/docs",
        "routes": sorted(routes, key=lambda x: x["path"])
    }


# ==================== Include Routers ====================

# Authentication routes
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])

# Journal routes
app.include_router(journal.router, prefix="/api/journal", tags=["Journal"])

# Budget routes
app.include_router(budget.router, prefix="/api/budget", tags=["Budget"])

# Recipe routes
app.include_router(recipe.router, prefix="/api/recipes", tags=["Recipes"])

# Mission routes
app.include_router(mission.router, prefix="/api/missions", tags=["Missions"])

# Challenge routes
app.include_router(challenge.router, prefix="/api/challenges", tags=["Challenges"])

# User Profile routes
app.include_router(user_profile.router, prefix="/api/user", tags=["User Profile"])

# User Stats routes
app.include_router(user_stats.router, prefix="/api", tags=["User Stats"])

# Achievements routes
app.include_router(achievements.router, prefix="/api", tags=["Achievements"])

# Meal Planning routes
app.include_router(meal_plans.router, prefix="/api", tags=["Meal Planning"])

# Smart Suggestions routes
app.include_router(smart_suggestions.router)

# Home Sections routes
app.include_router(home_sections.router)

# Content routes (Articles & Videos)
app.include_router(content.router)

# AI Recipe Generation routes
app.include_router(ai_recipes.router, prefix="/api", tags=["AI Recipes"])

# User Recipes routes (private user-created recipes)
app.include_router(user_recipes.router)

# Saved Ingredient Prices routes (Price Compare)
app.include_router(saved_prices.router, prefix="/api/saved-prices", tags=["Saved Prices"])

# Ingredient Catalog routes (master reference prices by region)
app.include_router(ingredient_catalog.router, prefix="/api/ingredients", tags=["Ingredient Catalog"])

# TODO: Add more routers as they are implemented


# ==================== Run Server ====================

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=True if settings.ENVIRONMENT == "development" else False
    )
