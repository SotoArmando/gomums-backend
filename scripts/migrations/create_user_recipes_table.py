"""
Create User Recipes Table
Creates the user_recipes table for private user-created recipes
"""
import psycopg2
from app.core.config import settings


def create_user_recipes_table():
    """Create user_recipes table for private user recipes"""
    conn = psycopg2.connect(
        host=settings.DATABASE_HOST,
        port=settings.DATABASE_PORT,
        database=settings.DATABASE_NAME,
        user=settings.DATABASE_USER,
        password=settings.DATABASE_PASSWORD
    )
    cursor = conn.cursor()
    
    try:
        # Create user_recipes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_recipes (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                image TEXT,
                prep_time VARCHAR(50),
                cook_time VARCHAR(50),
                total_time VARCHAR(50),
                servings INTEGER DEFAULT 1 CHECK (servings > 0),
                difficulty VARCHAR(50) CHECK (difficulty IN ('easy', 'medium', 'hard')),
                
                -- Recipe content as JSONB for flexibility
                ingredients JSONB DEFAULT '[]'::jsonb,
                instructions JSONB DEFAULT '[]'::jsonb,
                
                -- Nutrition info
                calories INTEGER,
                protein VARCHAR(50),
                carbs VARCHAR(50),
                fat VARCHAR(50),
                fiber VARCHAR(50),
                
                -- Organization
                category VARCHAR(100),
                tags TEXT[] DEFAULT '{}',
                
                -- Source info (if adapted from another recipe)
                source_url TEXT,
                source_name VARCHAR(255),
                original_recipe_id UUID REFERENCES recipes(id) ON DELETE SET NULL,
                
                -- Private notes
                notes TEXT,
                
                -- Favorites/Status
                is_favorite BOOLEAN DEFAULT FALSE,
                
                -- Timestamps
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✓ user_recipes table created/verified")
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_recipes_user_id 
            ON user_recipes(user_id);
        """)
        print("✓ user_recipes user_id index created")
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_recipes_category 
            ON user_recipes(category);
        """)
        print("✓ user_recipes category index created")
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_recipes_is_favorite 
            ON user_recipes(user_id, is_favorite) WHERE is_favorite = TRUE;
        """)
        print("✓ user_recipes favorites index created")
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_recipes_name_search 
            ON user_recipes USING gin(to_tsvector('english', name));
        """)
        print("✓ user_recipes name search index created")
        
        conn.commit()
        print("\n✅ User recipes table created successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error creating user_recipes table: {e}")
        raise e
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    print("\n" + "="*50)
    print("Creating User Recipes Table")
    print("="*50 + "\n")
    create_user_recipes_table()
