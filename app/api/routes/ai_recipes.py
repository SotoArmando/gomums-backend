"""
AI Recipe Generation Routes
Endpoints for AI-powered recipe suggestions based on available ingredients
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel, Field
from openai import OpenAI
import json
import os

from app.core.security import get_current_user
from app.db.repositories.recipe_repository import RecipeRepository
from app.db.repositories.user_profile_repository import UserProfileRepository
from app.db.repositories.journal_repository import JournalRepository
from app.db.repositories.challenge_repository import ChallengeRepository
from app.db.repositories.mission_repository import MissionRepository
from uuid import UUID

router = APIRouter(prefix="/ai-recipes", tags=["AI Recipes"])
user_profile_repo = UserProfileRepository()


# Static fallback recipes (used when OpenAI is unavailable)
STATIC_RECIPES = [
    {
        "name": "Classic Spaghetti Carbonara",
        "description": "Creamy Italian pasta with eggs, cheese, and pancetta",
        "prep_time": "20 minutes",
        "servings": 4,
        "difficulty": "easy",
        "ingredients": ["spaghetti", "eggs", "parmesan cheese", "pancetta", "black pepper", "salt"],
        "instructions": ["Cook spaghetti according to package", "Fry pancetta until crispy", "Mix eggs and cheese", "Combine hot pasta with egg mixture", "Add pancetta and serve"],
        "steps": [
            {"order": 1, "phase": "prep", "text": "Mix eggs and grated parmesan cheese in a bowl", "items": ["eggs", "parmesan cheese"]},
            {"order": 2, "phase": "prep", "text": "Dice the pancetta into small cubes", "items": ["pancetta"]},
            {"order": 3, "phase": "cooking", "text": "Cook spaghetti in salted boiling water", "items": ["spaghetti", "salt"], "time_minutes": 10},
            {"order": 4, "phase": "cooking", "text": "Fry pancetta until crispy", "items": ["pancetta"], "time_minutes": 5},
            {"order": 5, "phase": "cooking", "text": "Toss hot drained pasta with the pancetta", "items": ["spaghetti", "pancetta"]},
            {"order": 6, "phase": "cooking", "text": "Remove from heat and stir in egg mixture quickly", "items": ["eggs", "parmesan cheese"], "tip": "Off the heat so eggs don't scramble"},
            {"order": 7, "phase": "serve", "text": "Plate and top with black pepper and extra parmesan", "items": ["black pepper", "parmesan cheese"]}
        ],
        "calories": 450,
        "protein": "18g",
        "carbs": "55g",
        "fat": "16g",
        "tags": ["italian", "pasta", "quick"],
        "uses_leftovers": False,
        "leftover_items_used": None
    },
    {
        "name": "Vegetable Stir Fry",
        "description": "Quick and healthy mixed vegetable stir fry",
        "prep_time": "15 minutes",
        "servings": 4,
        "difficulty": "easy",
        "ingredients": ["mixed vegetables", "soy sauce", "garlic", "ginger", "oil", "rice"],
        "instructions": ["Heat oil in wok", "Add garlic and ginger", "Stir fry vegetables", "Add soy sauce", "Serve over rice"],
        "steps": [
            {"order": 1, "phase": "prep", "text": "Mince garlic and grate ginger", "items": ["garlic", "ginger"]},
            {"order": 2, "phase": "prep", "text": "Wash and chop all vegetables", "items": ["mixed vegetables"]},
            {"order": 3, "phase": "cooking", "text": "Cook rice according to package", "items": ["rice"], "time_minutes": 15},
            {"order": 4, "phase": "cooking", "text": "Heat oil in wok over high heat", "items": ["oil"]},
            {"order": 5, "phase": "cooking", "text": "Add garlic and ginger, stir 30 seconds", "items": ["garlic", "ginger"]},
            {"order": 6, "phase": "cooking", "text": "Add vegetables and stir fry 3-4 minutes", "items": ["mixed vegetables"], "time_minutes": 4},
            {"order": 7, "phase": "cooking", "text": "Add soy sauce and toss to coat", "items": ["soy sauce"]},
            {"order": 8, "phase": "serve", "text": "Serve stir fry over rice", "items": ["rice"]}
        ],
        "calories": 280,
        "protein": "8g",
        "carbs": "45g",
        "fat": "8g",
        "tags": ["vegetarian", "healthy", "quick", "asian"],
        "uses_leftovers": False,
        "leftover_items_used": None
    },
    {
        "name": "Chicken Tacos",
        "description": "Mexican-style chicken tacos with fresh toppings",
        "prep_time": "25 minutes",
        "servings": 4,
        "difficulty": "easy",
        "ingredients": ["chicken breast", "taco shells", "lettuce", "tomatoes", "cheese", "sour cream", "taco seasoning"],
        "instructions": ["Season and cook chicken", "Shred chicken", "Warm taco shells", "Assemble tacos with toppings"],
        "steps": [
            {"order": 1, "phase": "prep", "text": "Season chicken breast with taco seasoning", "items": ["chicken breast", "taco seasoning"]},
            {"order": 2, "phase": "prep", "text": "Shred lettuce and dice tomatoes", "items": ["lettuce", "tomatoes"]},
            {"order": 3, "phase": "cooking", "text": "Cook chicken in a pan until done, then shred", "items": ["chicken breast"], "time_minutes": 12},
            {"order": 4, "phase": "cooking", "text": "Warm taco shells according to package", "items": ["taco shells"]},
            {"order": 5, "phase": "serve", "text": "Fill shells with shredded chicken", "items": ["taco shells", "chicken breast"]},
            {"order": 6, "phase": "serve", "text": "Top with lettuce, tomatoes, cheese, and sour cream", "items": ["lettuce", "tomatoes", "cheese", "sour cream"]}
        ],
        "calories": 380,
        "protein": "28g",
        "carbs": "32g",
        "fat": "14g",
        "tags": ["mexican", "quick", "family-friendly"],
        "uses_leftovers": False,
        "leftover_items_used": None
    },
    {
        "name": "Caprese Salad",
        "description": "Fresh Italian salad with tomatoes, mozzarella, and basil",
        "prep_time": "10 minutes",
        "servings": 4,
        "difficulty": "easy",
        "ingredients": ["tomatoes", "mozzarella", "basil", "olive oil", "balsamic vinegar", "salt", "pepper"],
        "instructions": ["Slice tomatoes and mozzarella", "Arrange on plate", "Add basil leaves", "Drizzle with oil and vinegar", "Season and serve"],
        "calories": 220,
        "protein": "12g",
        "carbs": "8g",
        "fat": "16g",
        "tags": ["italian", "vegetarian", "salad", "no-cook"],
        "uses_leftovers": False,
        "leftover_items_used": None
    },
    {
        "name": "Beef Fried Rice",
        "description": "Classic fried rice with beef and vegetables",
        "prep_time": "20 minutes",
        "servings": 4,
        "difficulty": "easy",
        "ingredients": ["cooked rice", "beef", "eggs", "mixed vegetables", "soy sauce", "garlic", "oil"],
        "instructions": ["Cook beef in wok", "Push aside and scramble eggs", "Add rice and vegetables", "Season with soy sauce", "Stir and serve"],
        "calories": 420,
        "protein": "24g",
        "carbs": "48g",
        "fat": "14g",
        "tags": ["asian", "rice", "quick"],
        "uses_leftovers": True,
        "leftover_items_used": ["cooked rice"]
    },
    {
        "name": "Greek Salad",
        "description": "Mediterranean salad with feta and olives",
        "prep_time": "15 minutes",
        "servings": 4,
        "difficulty": "easy",
        "ingredients": ["cucumber", "tomatoes", "red onion", "feta cheese", "olives", "olive oil", "lemon juice", "oregano"],
        "instructions": ["Chop vegetables", "Combine in bowl", "Add feta and olives", "Dress with oil and lemon", "Season with oregano"],
        "calories": 180,
        "protein": "6g",
        "carbs": "12g",
        "fat": "12g",
        "tags": ["greek", "vegetarian", "salad", "healthy"],
        "uses_leftovers": False,
        "leftover_items_used": None
    },
    {
        "name": "Grilled Cheese Sandwich",
        "description": "Classic comfort food sandwich",
        "prep_time": "10 minutes",
        "servings": 2,
        "difficulty": "easy",
        "ingredients": ["bread", "cheese", "butter"],
        "instructions": ["Butter bread slices", "Add cheese between slices", "Grill until golden on both sides", "Serve hot"],
        "calories": 350,
        "protein": "14g",
        "carbs": "32g",
        "fat": "18g",
        "tags": ["sandwich", "quick", "comfort-food", "vegetarian"],
        "uses_leftovers": False,
        "leftover_items_used": None
    },
    {
        "name": "Chicken Caesar Salad",
        "description": "Classic salad with grilled chicken and Caesar dressing",
        "prep_time": "20 minutes",
        "servings": 4,
        "difficulty": "easy",
        "ingredients": ["chicken breast", "romaine lettuce", "parmesan cheese", "croutons", "caesar dressing"],
        "instructions": ["Grill and slice chicken", "Chop lettuce", "Toss with dressing", "Add chicken and croutons", "Top with parmesan"],
        "calories": 320,
        "protein": "32g",
        "carbs": "18g",
        "fat": "14g",
        "tags": ["salad", "healthy", "protein-rich"],
        "uses_leftovers": False,
        "leftover_items_used": None
    },
    {
        "name": "Vegetable Soup",
        "description": "Hearty and healthy vegetable soup",
        "prep_time": "30 minutes",
        "servings": 6,
        "difficulty": "easy",
        "ingredients": ["mixed vegetables", "vegetable broth", "onion", "garlic", "tomatoes", "herbs", "salt", "pepper"],
        "instructions": ["Sauté onion and garlic", "Add vegetables and broth", "Simmer until tender", "Season with herbs", "Serve hot"],
        "calories": 120,
        "protein": "4g",
        "carbs": "22g",
        "fat": "2g",
        "tags": ["soup", "vegetarian", "healthy", "comfort-food"],
        "uses_leftovers": False,
        "leftover_items_used": None
    },
    {
        "name": "Teriyaki Chicken Bowl",
        "description": "Asian-inspired bowl with teriyaki chicken and rice",
        "prep_time": "25 minutes",
        "servings": 4,
        "difficulty": "easy",
        "ingredients": ["chicken thighs", "teriyaki sauce", "rice", "broccoli", "sesame seeds", "green onions"],
        "instructions": ["Cook rice", "Marinate chicken in teriyaki", "Pan fry chicken", "Steam broccoli", "Assemble bowls and garnish"],
        "calories": 480,
        "protein": "36g",
        "carbs": "52g",
        "fat": "12g",
        "tags": ["asian", "rice-bowl", "protein-rich"],
        "uses_leftovers": False,
        "leftover_items_used": None
    },
    {
        "name": "Margherita Pizza",
        "description": "Classic Italian pizza with tomato, mozzarella, and basil",
        "prep_time": "40 minutes",
        "servings": 4,
        "difficulty": "medium",
        "ingredients": ["pizza dough", "tomato sauce", "mozzarella", "basil", "olive oil", "salt"],
        "instructions": ["Roll out dough", "Spread sauce", "Add mozzarella", "Bake at 450°F", "Top with basil and serve"],
        "calories": 380,
        "protein": "16g",
        "carbs": "48g",
        "fat": "14g",
        "tags": ["italian", "pizza", "vegetarian"],
        "uses_leftovers": False,
        "leftover_items_used": None
    },
    {
        "name": "Egg Fried Rice",
        "description": "Simple fried rice with eggs and vegetables",
        "prep_time": "15 minutes",
        "servings": 4,
        "difficulty": "easy",
        "ingredients": ["cooked rice", "eggs", "peas", "carrots", "soy sauce", "green onions", "oil"],
        "instructions": ["Heat oil in wok", "Scramble eggs", "Add rice and vegetables", "Season with soy sauce", "Garnish with green onions"],
        "calories": 320,
        "protein": "12g",
        "carbs": "48g",
        "fat": "8g",
        "tags": ["asian", "vegetarian", "quick", "budget-friendly"],
        "uses_leftovers": True,
        "leftover_items_used": ["cooked rice"]
    },
    {
        "name": "Pasta Primavera",
        "description": "Light pasta with fresh spring vegetables",
        "prep_time": "25 minutes",
        "servings": 4,
        "difficulty": "easy",
        "ingredients": ["pasta", "mixed vegetables", "garlic", "olive oil", "parmesan", "herbs"],
        "instructions": ["Cook pasta", "Sauté vegetables with garlic", "Toss pasta with vegetables", "Add parmesan and herbs", "Serve immediately"],
        "calories": 380,
        "protein": "14g",
        "carbs": "58g",
        "fat": "10g",
        "tags": ["italian", "pasta", "vegetarian", "healthy"],
        "uses_leftovers": False,
        "leftover_items_used": None
    },
    {
        "name": "Quesadillas",
        "description": "Cheesy Mexican tortillas with optional fillings",
        "prep_time": "15 minutes",
        "servings": 4,
        "difficulty": "easy",
        "ingredients": ["tortillas", "cheese", "beans", "peppers", "sour cream", "salsa"],
        "instructions": ["Place cheese on tortilla", "Add desired fillings", "Fold and grill until crispy", "Cut into wedges", "Serve with toppings"],
        "calories": 340,
        "protein": "16g",
        "carbs": "36g",
        "fat": "14g",
        "tags": ["mexican", "quick", "vegetarian", "family-friendly"],
        "uses_leftovers": False,
        "leftover_items_used": None
    },
    {
        "name": "Chicken Noodle Soup",
        "description": "Comforting soup with chicken and noodles",
        "prep_time": "35 minutes",
        "servings": 6,
        "difficulty": "easy",
        "ingredients": ["chicken breast", "egg noodles", "carrots", "celery", "onion", "chicken broth", "herbs"],
        "instructions": ["Cook chicken in broth", "Remove and shred chicken", "Add vegetables and noodles", "Return chicken to pot", "Season and serve"],
        "calories": 280,
        "protein": "24g",
        "carbs": "32g",
        "fat": "6g",
        "tags": ["soup", "comfort-food", "healthy"],
        "uses_leftovers": True,
        "leftover_items_used": ["cooked chicken"]
    },
    {
        "name": "Avocado Toast",
        "description": "Simple and nutritious breakfast or snack",
        "prep_time": "5 minutes",
        "servings": 2,
        "difficulty": "easy",
        "ingredients": ["bread", "avocado", "lemon juice", "salt", "pepper", "red pepper flakes"],
        "instructions": ["Toast bread", "Mash avocado with lemon", "Spread on toast", "Season with salt and pepper", "Add toppings if desired"],
        "calories": 240,
        "protein": "6g",
        "carbs": "28g",
        "fat": "12g",
        "tags": ["breakfast", "vegetarian", "quick", "healthy"],
        "uses_leftovers": False,
        "leftover_items_used": None
    },
    {
        "name": "Beef Tacos",
        "description": "Seasoned ground beef tacos with fresh toppings",
        "prep_time": "20 minutes",
        "servings": 4,
        "difficulty": "easy",
        "ingredients": ["ground beef", "taco shells", "lettuce", "tomatoes", "cheese", "sour cream", "taco seasoning"],
        "instructions": ["Brown beef with seasoning", "Warm taco shells", "Fill shells with beef", "Add fresh toppings", "Serve immediately"],
        "calories": 390,
        "protein": "26g",
        "carbs": "32g",
        "fat": "16g",
        "tags": ["mexican", "quick", "family-friendly"],
        "uses_leftovers": False,
        "leftover_items_used": None
    },
    {
        "name": "Omelette",
        "description": "Classic egg omelette with cheese and vegetables",
        "prep_time": "10 minutes",
        "servings": 2,
        "difficulty": "easy",
        "ingredients": ["eggs", "cheese", "bell peppers", "onions", "butter", "salt", "pepper"],
        "instructions": ["Beat eggs with seasoning", "Sauté vegetables", "Pour eggs in pan", "Add cheese and fold", "Cook until set"],
        "calories": 280,
        "protein": "18g",
        "carbs": "6g",
        "fat": "20g",
        "tags": ["breakfast", "vegetarian", "quick", "protein-rich"],
        "uses_leftovers": False,
        "leftover_items_used": None
    },
    {
        "name": "Pasta with Marinara",
        "description": "Simple pasta with classic tomato sauce",
        "prep_time": "20 minutes",
        "servings": 4,
        "difficulty": "easy",
        "ingredients": ["pasta", "tomato sauce", "garlic", "olive oil", "basil", "parmesan"],
        "instructions": ["Cook pasta", "Heat sauce with garlic", "Toss pasta with sauce", "Add basil and parmesan", "Serve hot"],
        "calories": 360,
        "protein": "12g",
        "carbs": "62g",
        "fat": "8g",
        "tags": ["italian", "pasta", "vegetarian", "budget-friendly"],
        "uses_leftovers": False,
        "leftover_items_used": None
    },
    {
        "name": "Chicken Sandwich",
        "description": "Grilled chicken sandwich with lettuce and tomato",
        "prep_time": "20 minutes",
        "servings": 4,
        "difficulty": "easy",
        "ingredients": ["chicken breast", "bread", "lettuce", "tomato", "mayo", "cheese"],
        "instructions": ["Grill chicken", "Toast bread", "Spread mayo on bread", "Layer chicken and vegetables", "Assemble and serve"],
        "calories": 380,
        "protein": "32g",
        "carbs": "34g",
        "fat": "12g",
        "tags": ["sandwich", "quick", "protein-rich"],
        "uses_leftovers": True,
        "leftover_items_used": ["grilled chicken"]
    }
]


class IngredientInput(BaseModel):
    """Input model for ingredients"""
    name: str
    quantity: Optional[str] = None
    category: Optional[str] = None


class RecipeGenerationRequest(BaseModel):
    """Request model for AI recipe generation"""
    available_ingredients: Optional[List[str]] = Field(default=None, description="List of available ingredients (uses recent purchases if not provided)")
    leftovers: Optional[List[str]] = Field(default=None, description="List of leftover items to use (auto-fetched if not provided)")
    dietary_restrictions: Optional[List[str]] = Field(default=None, description="Dietary restrictions (vegetarian, vegan, gluten-free, etc.)")
    cuisine_preference: Optional[str] = Field(default=None, description="Preferred cuisine type")
    servings: Optional[int] = Field(default=4, ge=1, le=12, description="Number of servings")
    difficulty: Optional[str] = Field(default=None, description="Difficulty level: easy, medium, or hard")
    max_recipes: int = Field(default=5, ge=1, le=20, description="Maximum number of recipes to generate")
    save_to_database: bool = Field(default=False, description="Whether to save generated recipes to database")
    use_stored_data: bool = Field(default=True, description="Whether to auto-fetch ingredients and leftovers from journal")
    minimize_shopping: bool = Field(default=False, description="Recipes should only use available ingredients or common pantry staples (no shopping needed)")


class GeneratedRecipeStep(BaseModel):
    """A single step in a generated recipe"""
    order: int
    phase: str  # "prep", "cooking", "serve"
    text: str
    items: List[str] = Field(default_factory=list)
    time_minutes: Optional[int] = None
    tip: Optional[str] = None


class GeneratedRecipe(BaseModel):
    """Model for a generated recipe"""
    name: str
    description: Optional[str]
    prep_time: str
    servings: int
    difficulty: str
    ingredients: List[str]
    instructions: List[str]
    steps: List[GeneratedRecipeStep] = Field(default_factory=list)
    calories: Optional[int]
    protein: Optional[str]
    carbs: Optional[str]
    fat: Optional[str]
    tags: List[str]
    uses_leftovers: bool = False
    leftover_items_used: Optional[List[str]] = None


class RecipeGenerationResponse(BaseModel):
    """Response model for recipe generation"""
    recipes: List[GeneratedRecipe]
    count: int
    saved_to_database: bool = False


def get_openai_client():
    """Initialize OpenAI client, returns None if not configured"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    try:
        return OpenAI(api_key=api_key)
    except Exception:
        return None


def create_recipe_prompt(request: RecipeGenerationRequest, user_allergies: list = None) -> str:
    """Create the prompt for recipe generation"""
    prompt = f"""Generate {request.max_recipes} unique, practical recipes using the following criteria:

AVAILABLE INGREDIENTS:
{', '.join(request.available_ingredients)}
"""

    if request.leftovers:
        prompt += f"""
LEFTOVER ITEMS TO USE (PRIORITY):
{', '.join(request.leftovers)}
"""

    if request.dietary_restrictions:
        prompt += f"""
DIETARY RESTRICTIONS:
{', '.join(request.dietary_restrictions)}
"""

    # Add allergies as critical safety constraint
    if user_allergies:
        prompt += f"""
ALLERGIES (MUST AVOID - CRITICAL):
{', '.join(user_allergies)}
DO NOT include these ingredients or their derivatives in any recipe.
"""

    if request.cuisine_preference:
        prompt += f"""
CUISINE PREFERENCE: {request.cuisine_preference}
"""

    prompt += f"""
SERVINGS: {request.servings}
"""

    if request.difficulty:
        prompt += f"""
DIFFICULTY: {request.difficulty}
"""

    # Add shopping constraint if specified
    if request.minimize_shopping:
        prompt += """

SHOPPING CONSTRAINT (CRITICAL):
- You MUST primarily use ONLY the ingredients listed in AVAILABLE INGREDIENTS
- If additional ingredients are absolutely necessary, they MUST be common pantry staples like:
  * Salt, pepper, basic spices (cumin, paprika, oregano)
  * Cooking oil, butter
  * Flour, sugar
  * Stock/broth
- DO NOT suggest recipes requiring fresh ingredients not in the available list
- DO NOT require any specialty or uncommon ingredients
- Goal: User should NOT need to go shopping
"""

    prompt += """
IMPORTANT REQUIREMENTS:
1. Prioritize using leftover items if provided
2. Use as many of the available ingredients as possible
3. Suggest reasonable substitutions if needed
4. Keep recipes practical and achievable
5. Include accurate prep times
6. Provide clear, step-by-step instructions
7. Include estimated nutritional information

Return ONLY a valid JSON array with this exact structure:
[
  {
    "name": "Recipe Name",
    "description": "Brief description",
    "prep_time": "30 minutes",
    "servings": 4,
    "difficulty": "easy|medium|hard",
    "ingredients": ["ingredient 1", "ingredient 2"],
    "instructions": ["step 1", "step 2"],
    "steps": [
      {"order": 1, "phase": "prep", "text": "Dice the onion", "items": ["1 onion"], "time_minutes": 5},
      {"order": 2, "phase": "cooking", "text": "Sauté the onion", "items": ["1 onion", "2 tbsp oil"], "time_minutes": 3},
      {"order": 3, "phase": "serve", "text": "Plate and garnish", "items": ["fresh herbs"]}
    ],
    "calories": 350,
    "protein": "25g",
    "carbs": "40g",
    "fat": "10g",
    "tags": ["tag1", "tag2"],
    "uses_leftovers": true|false,
    "leftover_items_used": ["item1", "item2"] or null
  }
]

IMPORTANT for "steps":
- Each step must have a "phase": either "prep", "cooking", or "serve"
- "items" lists the specific ingredients or tools used in that step (matching entries from the ingredients list)
- Steps must be in chronological order (prep first, cooking next, serve last)
- All prep steps come before all cooking steps, and all cooking steps come before serve steps
- The "instructions" field should still contain a flat list of all steps for backward compatibility

Do not include any text before or after the JSON array.
"""

    return prompt


def get_static_recipes(request: RecipeGenerationRequest, user_allergies: list = None) -> List[GeneratedRecipe]:
    """Get static recipes as fallback when OpenAI is unavailable"""
    import random
    
    # Filter recipes based on request
    filtered = STATIC_RECIPES.copy()
    
    # Filter by dietary restrictions
    if request.dietary_restrictions:
        restrictions_lower = [r.lower() for r in request.dietary_restrictions]
        if 'vegetarian' in restrictions_lower or 'vegan' in restrictions_lower:
            filtered = [r for r in filtered if 'vegetarian' in r['tags'] or not any(meat in ' '.join(r['ingredients']).lower() for meat in ['chicken', 'beef', 'pork', 'fish', 'meat'])]
    
    # Filter by allergies (exclude recipes with allergens)
    if user_allergies:
        for allergy in user_allergies:
            allergy_lower = allergy.lower()
            filtered = [r for r in filtered if allergy_lower not in ' '.join(r['ingredients']).lower()]
    
    # Prioritize leftover recipes if leftovers are provided
    if request.leftovers:
        leftover_recipes = [r for r in filtered if r['uses_leftovers']]
        non_leftover_recipes = [r for r in filtered if not r['uses_leftovers']]
        # Mix: priority to leftover recipes but include some regular ones
        filtered = leftover_recipes + non_leftover_recipes
    
    # Shuffle and limit to requested count
    random.shuffle(filtered)
    selected = filtered[:min(request.max_recipes, len(filtered))]
    
    # Convert to GeneratedRecipe objects and adjust servings
    recipes = []
    for recipe in selected:
        recipe_copy = recipe.copy()
        # Adjust servings if needed
        if request.servings and request.servings != recipe['servings']:
            recipe_copy['servings'] = request.servings
        recipes.append(GeneratedRecipe(**recipe_copy))
    
    return recipes


@router.post("/generate", response_model=RecipeGenerationResponse)
async def generate_recipes(
    request: RecipeGenerationRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate custom recipes using AI based on available ingredients and leftovers
    
    This endpoint uses OpenAI's GPT model to generate practical recipes that:
    - Use your available ingredients (from recent purchases if not specified)
    - Prioritize using leftovers (auto-fetched from your journal)
    - Respect dietary restrictions
    - Match your preferred cuisine and difficulty level
    - Automatically uses your saved preferences (dietary restrictions, allergies, household size)
    
    The recipes can optionally be saved to your recipe collection.
    
    Smart Data Integration:
    - If no ingredients provided, uses items from your recent purchases (last 7 days)
    - If no leftovers provided, fetches your active leftover meals
    - Set use_stored_data=false to disable automatic fetching
    """
    try:
        # Fetch user's actual data from journal if requested
        if request.use_stored_data:
            # Get recent purchased ingredients if not provided
            if not request.available_ingredients:
                purchased_ingredients = JournalRepository.get_recent_purchased_ingredients(
                    user_id=current_user["id"],
                    days=7
                )
                request.available_ingredients = purchased_ingredients
            
            # Get active leftovers if not provided
            if not request.leftovers:
                active_leftovers = JournalRepository.get_active_leftovers(
                    user_id=current_user["id"]
                )
                if active_leftovers:
                    request.leftovers = active_leftovers
        
        # Validate we have ingredients to work with
        if not request.available_ingredients or len(request.available_ingredients) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No ingredients available. Please provide ingredients or make sure you have recent purchases recorded."
            )
        
        # Fetch user preferences to use as defaults
        user_preferences = await user_profile_repo.get_preferences(current_user["id"])
        
        # Apply user preferences as defaults if not explicitly provided
        if user_preferences:
            # Use user's dietary restrictions if not provided
            if not request.dietary_restrictions and user_preferences.get('dietary_restrictions'):
                request.dietary_restrictions = user_preferences['dietary_restrictions']
            
            # Use user's household size as servings if not provided
            if request.servings == 4 and user_preferences.get('household_size'):
                request.servings = user_preferences['household_size']
            
            # Use user's skill level as difficulty if not provided
            if not request.difficulty and user_preferences.get('skill_level'):
                skill_mapping = {
                    'beginner': 'easy',
                    'intermediate': 'medium',
                    'advanced': 'hard'
                }
                request.difficulty = skill_mapping.get(user_preferences['skill_level'], 'medium')
        
        # Initialize OpenAI
        client = get_openai_client()
        
        # Create the prompt with user allergies
        user_allergies = user_preferences.get('allergies', []) if user_preferences else []
        
        # Use static recipes as fallback if OpenAI is not available
        if client is None:
            print("OpenAI not available, using static recipes")
            generated_recipes = get_static_recipes(request, user_allergies)
        else:
            try:
                prompt = create_recipe_prompt(request, user_allergies)
                
                # Call OpenAI API
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a professional chef and meal planning expert. You create practical, delicious recipes that help people use their available ingredients efficiently and reduce food waste."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.8,
                    max_tokens=4000
                )
                
                # Parse the response
                content = response.choices[0].message.content.strip()
                
                # Try to extract JSON if it's wrapped in markdown code blocks
                if content.startswith("```json"):
                    content = content.split("```json")[1].split("```")[0].strip()
                elif content.startswith("```"):
                    content = content.split("```")[1].split("```")[0].strip()
                
                # Parse JSON
                try:
                    recipes_data = json.loads(content)
                    if not isinstance(recipes_data, list):
                        # If the response is an object with a recipes key
                        if isinstance(recipes_data, dict) and 'recipes' in recipes_data:
                            recipes_data = recipes_data['recipes']
                        else:
                            raise ValueError("Expected a list of recipes")
                except json.JSONDecodeError as e:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Failed to parse AI response: {str(e)}"
                    )
                
                # Convert to GeneratedRecipe models
                generated_recipes = []
                for recipe_data in recipes_data[:request.max_recipes]:
                    try:
                        recipe = GeneratedRecipe(**recipe_data)
                        generated_recipes.append(recipe)
                    except Exception as e:
                        print(f"Error parsing recipe: {e}")
                        continue
                
                if not generated_recipes:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="No valid recipes were generated"
                    )
            
            except Exception as e:
                # If OpenAI fails, fallback to static recipes
                print(f"OpenAI error: {e}, using static recipes as fallback")
                generated_recipes = get_static_recipes(request, user_allergies)
        
        # Save to database if requested
        saved = False
        if request.save_to_database:
            for recipe in generated_recipes:
                try:
                    RecipeRepository.create_recipe({
                        "name": recipe.name,
                        "image": None,
                        "prep_time": recipe.prep_time,
                        "servings": recipe.servings,
                        "difficulty": recipe.difficulty,
                        "ingredients": recipe.ingredients,
                        "instructions": recipe.instructions,
                        "steps": [s.model_dump() for s in recipe.steps] if recipe.steps else [],
                        "calories": recipe.calories,
                        "protein": recipe.protein,
                        "carbs": recipe.carbs,
                        "fat": recipe.fat,
                        "featured": False,
                        "category": request.cuisine_preference or "AI Generated",
                        "tags": recipe.tags + (["uses-leftovers"] if recipe.uses_leftovers else [])
                    })
                except Exception as e:
                    print(f"Error saving recipe {recipe.name}: {e}")
            saved = True
        
        return RecipeGenerationResponse(
            recipes=generated_recipes,
            count=len(generated_recipes),
            saved_to_database=saved
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Fallback to static recipes for any other error
        print(f"Unexpected error, using static recipes: {e}")
        user_allergies = []
        if 'user_preferences' in locals() and user_preferences:
            user_allergies = user_preferences.get('allergies', [])
        generated_recipes = get_static_recipes(request, user_allergies)
        
        return RecipeGenerationResponse(
            recipes=generated_recipes,
            count=len(generated_recipes),
            saved_to_database=False
        )


@router.post("/quick-generate")
async def quick_generate_recipes(
    request_body: dict,
    current_user: dict = Depends(get_current_user)
):
    """
    Quick recipe generation with minimal parameters (just ingredients list)
    
    Request body:
    - ingredients: List[str] - List of available ingredients
    - max_recipes: int (optional, default: 5) - Number of recipes to generate
    - minimize_shopping: bool (optional, default: false) - Only use available ingredients
    """
    ingredients = request_body.get("ingredients", [])
    max_recipes = request_body.get("max_recipes", 5)
    minimize_shopping = request_body.get("minimize_shopping", False)
    
    if not ingredients:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ingredients field is required"
        )
    
    request = RecipeGenerationRequest(
        available_ingredients=ingredients,
        max_recipes=max_recipes,
        save_to_database=False,
        minimize_shopping=minimize_shopping
    )
    return await generate_recipes(request, current_user)


@router.post("/leftover-recipes")
async def generate_leftover_recipes(
    request_body: dict,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate recipes specifically focused on using leftovers
    
    Request body:
    - leftovers: List[str] - List of leftover items to use
    - pantry_items: List[str] (optional) - Additional pantry items available
    - max_recipes: int (optional, default: 5) - Number of recipes to generate
    - minimize_shopping: bool (optional, default: false) - Avoid requiring fresh ingredients
    """
    leftovers = request_body.get("leftovers", [])
    pantry_items = request_body.get("pantry_items")
    max_recipes = request_body.get("max_recipes", 5)
    minimize_shopping = request_body.get("minimize_shopping", False)
    
    if not leftovers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="leftovers field is required"
        )
    
    request = RecipeGenerationRequest(
        available_ingredients=pantry_items or ["common pantry staples"],
        leftovers=leftovers,
        max_recipes=max_recipes,
        save_to_database=False,
        minimize_shopping=minimize_shopping
    )
    return await generate_recipes(request, current_user)


@router.post("/for-challenge")
async def generate_recipes_for_challenge(
    request_body: dict,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate recipes specifically tailored for a challenge or mission
    
    Request body:
    - challenge_id: str (optional) - Challenge ID to generate recipes for
    - mission_id: str (optional) - Mission ID to generate recipes for
    - max_recipes: int (optional, default: 5) - Number of recipes to generate
    - save_to_database: bool (optional, default: false) - Save generated recipes
    
    The endpoint will:
    - Fetch challenge/mission details and goals
    - Analyze constraints (budget, difficulty, goals)
    - Generate recipes that help complete the challenge/mission
    - Use user's available ingredients and preferences
    """
    challenge_id = request_body.get("challenge_id")
    mission_id = request_body.get("mission_id")
    max_recipes = request_body.get("max_recipes", 5)
    save_to_database = request_body.get("save_to_database", False)
    
    if not challenge_id and not mission_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either challenge_id or mission_id is required"
        )
    
    try:
        # Fetch user preferences and available ingredients
        user_preferences = await user_profile_repo.get_preferences(current_user["id"])
        purchased_ingredients = JournalRepository.get_recent_purchased_ingredients(
            user_id=current_user["id"],
            days=7
        )
        active_leftovers = JournalRepository.get_active_leftovers(
            user_id=current_user["id"]
        )
        
        # Fetch challenge or mission details
        challenge_context = ""
        difficulty_constraint = None
        cuisine_hint = None
        
        if challenge_id:
            challenge = ChallengeRepository.get_challenge_by_id(UUID(challenge_id))
            if not challenge:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Challenge not found"
                )
            
            challenge_type = challenge.get('type', '')
            challenge_goals = challenge.get('goals', [])
            
            challenge_context = f"Challenge: {challenge['title']}\n"
            challenge_context += f"Type: {challenge_type}\n"
            challenge_context += f"Description: {challenge.get('description', '')}\n"
            challenge_context += "Goals:\n"
            for goal in challenge_goals:
                challenge_context += f"- {goal['description']}\n"
            
            # Determine difficulty based on challenge type
            if 'budget' in challenge_type.lower():
                difficulty_constraint = 'easy'
                cuisine_hint = "budget-friendly, affordable"
            elif 'zero_waste' in challenge_type.lower() or 'leftover' in challenge_type.lower():
                cuisine_hint = "leftover-focused, waste-reduction"
            elif 'batch' in challenge_type.lower():
                cuisine_hint = "meal-prep friendly, freezer-friendly"
            
        elif mission_id:
            mission_repo = MissionRepository()
            # Fetch mission from active missions
            active_missions = await mission_repo.get_active_missions(current_user["id"])
            mission = next((m for m in active_missions if m['mission_id'] == mission_id), None)
            
            if not mission:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Mission not found or not active"
                )
            
            mission_data = mission['mission']
            mission_type = mission_data.get('type', '')
            mission_category = mission_data.get('category', '')
            mission_difficulty = mission_data.get('difficulty', '')
            mission_goals = mission_data.get('goals', [])
            
            challenge_context = f"Mission: {mission_data['title']}\n"
            challenge_context += f"Type: {mission_type}\n"
            challenge_context += f"Category: {mission_category}\n"
            challenge_context += f"Description: {mission_data.get('description', '')}\n"
            challenge_context += "Goals:\n"
            for goal in mission_goals:
                challenge_context += f"- {goal['description']}\n"
            
            difficulty_constraint = mission_difficulty
            
            if 'new_recipe' in mission_category.lower():
                cuisine_hint = "adventurous, try new cuisines"
            elif 'budget' in mission_category.lower():
                cuisine_hint = "budget-friendly, affordable"
            elif 'leftover' in mission_category.lower():
                cuisine_hint = "leftover-focused"
        
        # Build recipe generation request
        request = RecipeGenerationRequest(
            available_ingredients=purchased_ingredients if purchased_ingredients else None,
            leftovers=active_leftovers if active_leftovers else None,
            dietary_restrictions=user_preferences.get('dietary_restrictions') if user_preferences else None,
            cuisine_preference=cuisine_hint,
            servings=user_preferences.get('household_size', 4) if user_preferences else 4,
            difficulty=difficulty_constraint,
            max_recipes=max_recipes,
            save_to_database=save_to_database,
            use_stored_data=True,
            minimize_shopping='budget' in challenge_context.lower()
        )
        
        # Generate recipes with challenge/mission context
        # Add the context to the prompt by temporarily modifying the request
        original_prompt = create_recipe_prompt(request, user_preferences.get('allergies', []) if user_preferences else [])
        enhanced_prompt = f"""
{challenge_context}

IMPORTANT: Generate recipes that will help the user complete the above challenge/mission goals.
Consider the challenge type and goals when selecting recipes.

{original_prompt}
"""
        
        # Initialize OpenAI
        client = get_openai_client()
        user_allergies = user_preferences.get('allergies', []) if user_preferences else []
        
        # Use static recipes as fallback if OpenAI is not available
        if client is None:
            print("OpenAI not available, using static recipes")
            generated_recipes = get_static_recipes(request, user_allergies)
        else:
            try:
                # Call OpenAI API with enhanced prompt
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a professional chef and meal planning expert. You help users complete their food challenges and missions by creating recipes that align with their goals."
                        },
                        {
                            "role": "user",
                            "content": enhanced_prompt
                        }
                    ],
                    temperature=0.8,
                    max_tokens=4000
                )
                
                # Parse the response
                content = response.choices[0].message.content.strip()
                
                # Try to extract JSON if it's wrapped in markdown code blocks
                if content.startswith("```json"):
                    content = content.split("```json")[1].split("```")[0].strip()
                elif content.startswith("```"):
                    content = content.split("```")[1].split("```")[0].strip()
                
                # Parse JSON
                try:
                    recipes_data = json.loads(content)
                    if not isinstance(recipes_data, list):
                        if isinstance(recipes_data, dict) and 'recipes' in recipes_data:
                            recipes_data = recipes_data['recipes']
                        else:
                            raise ValueError("Expected a list of recipes")
                except json.JSONDecodeError as e:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Failed to parse AI response: {str(e)}"
                    )
                
                # Convert to GeneratedRecipe models
                generated_recipes = []
                for recipe_data in recipes_data[:request.max_recipes]:
                    try:
                        recipe = GeneratedRecipe(**recipe_data)
                        generated_recipes.append(recipe)
                    except Exception as e:
                        print(f"Error parsing recipe: {e}")
                        continue
                
                if not generated_recipes:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="No valid recipes were generated"
                    )
            
            except Exception as e:
                # If OpenAI fails, fallback to static recipes
                print(f"OpenAI error: {e}, using static recipes as fallback")
                generated_recipes = get_static_recipes(request, user_allergies)
        
        # Save to database if requested
        saved = False
        if save_to_database:
            for recipe in generated_recipes:
                try:
                    RecipeRepository.create_recipe({
                        "name": recipe.name,
                        "image": None,
                        "prep_time": recipe.prep_time,
                        "servings": recipe.servings,
                        "difficulty": recipe.difficulty,
                        "ingredients": recipe.ingredients,
                        "instructions": recipe.instructions,
                        "calories": recipe.calories,
                        "protein": recipe.protein,
                        "carbs": recipe.carbs,
                        "fat": recipe.fat,
                        "featured": False,
                        "category": cuisine_hint or "Challenge Recipe",
                        "tags": recipe.tags + (["challenge"] if challenge_id else ["mission"])
                    })
                except Exception as e:
                    print(f"Error saving recipe {recipe.name}: {e}")
            saved = True
        
        return RecipeGenerationResponse(
            recipes=generated_recipes,
            count=len(generated_recipes),
            saved_to_database=saved
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating recipes for challenge/mission: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recipes: {str(e)}"
        )

