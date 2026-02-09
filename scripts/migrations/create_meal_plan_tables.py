"""
Create Meal Planning Tables
Creates meal_plans, planned_meals, and shopping_list_items tables
"""
import psycopg2
from app.core.config import settings

def create_meal_plan_tables():
    """Create meal planning tables"""
    conn = psycopg2.connect(
        host=settings.DATABASE_HOST,
        port=settings.DATABASE_PORT,
        database=settings.DATABASE_NAME,
        user=settings.DATABASE_USER,
        password=settings.DATABASE_PASSWORD
    )
    cursor = conn.cursor()
    
    try:
        # Create meal_plans table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS meal_plans (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                name VARCHAR(255) NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                total_cost DECIMAL(10, 2) DEFAULT 0.00,
                status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'completed')),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT valid_date_range CHECK (end_date >= start_date)
            );
        """)
        print("✓ meal_plans table created/verified")
        
        # Create planned_meals table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS planned_meals (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                meal_plan_id UUID NOT NULL REFERENCES meal_plans(id) ON DELETE CASCADE,
                date DATE NOT NULL,
                meal_type VARCHAR(20) NOT NULL CHECK (meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')),
                recipe_id UUID REFERENCES recipes(id) ON DELETE SET NULL,
                recipe_name VARCHAR(255) NOT NULL,
                servings INTEGER DEFAULT 1 CHECK (servings > 0),
                is_batch BOOLEAN DEFAULT false,
                is_leftovers BOOLEAN DEFAULT false,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✓ planned_meals table created/verified")
        
        # Create shopping_list_items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS shopping_list_items (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                meal_plan_id UUID NOT NULL REFERENCES meal_plans(id) ON DELETE CASCADE,
                name VARCHAR(255) NOT NULL,
                quantity VARCHAR(100),
                category VARCHAR(100),
                purchased BOOLEAN DEFAULT false,
                estimated_cost DECIMAL(10, 2),
                related_recipes TEXT[] DEFAULT '{}',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✓ shopping_list_items table created/verified")
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_meal_plans_user_id ON meal_plans(user_id);
            CREATE INDEX IF NOT EXISTS idx_meal_plans_dates ON meal_plans(start_date, end_date);
            CREATE INDEX IF NOT EXISTS idx_planned_meals_meal_plan ON planned_meals(meal_plan_id);
            CREATE INDEX IF NOT EXISTS idx_shopping_items_meal_plan ON shopping_list_items(meal_plan_id);
        """)
        print("✓ Indexes created/verified")
        
        # Create triggers for updated_at
        cursor.execute("""
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ language 'plpgsql';
        """)
        
        cursor.execute("""
            DROP TRIGGER IF EXISTS update_meal_plans_updated_at ON meal_plans;
            CREATE TRIGGER update_meal_plans_updated_at
                BEFORE UPDATE ON meal_plans
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
        """)
        
        cursor.execute("""
            DROP TRIGGER IF EXISTS update_planned_meals_updated_at ON planned_meals;
            CREATE TRIGGER update_planned_meals_updated_at
                BEFORE UPDATE ON planned_meals
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
        """)
        
        cursor.execute("""
            DROP TRIGGER IF EXISTS update_shopping_items_updated_at ON shopping_list_items;
            CREATE TRIGGER update_shopping_items_updated_at
                BEFORE UPDATE ON shopping_list_items
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
        """)
        print("✓ Triggers created/verified")
        
        conn.commit()
        print("\n✅ All meal planning tables created successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error creating tables: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_meal_plan_tables()
