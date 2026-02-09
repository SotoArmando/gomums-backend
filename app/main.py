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
