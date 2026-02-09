"""
Create Smart Suggestions and Home Sections Tables
"""
import psycopg2
from app.core.config import settings

def create_tables():
    """Create smart suggestions and home sections tables"""
    conn = psycopg2.connect(
        host=settings.DATABASE_HOST,
        port=settings.DATABASE_PORT,
        database=settings.DATABASE_NAME,
        user=settings.DATABASE_USER,
        password=settings.DATABASE_PASSWORD
    )
    cursor = conn.cursor()
    
    try:
        # Create smart_suggestions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS smart_suggestions (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                type VARCHAR(50) NOT NULL CHECK (type IN (
                    'streak', 'meal_plan', 'budget', 'recipe', 'challenge',
                    'leftover', 'achievement', 'mission', 'batch_cooking', 'shopping'
                )),
                priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
                title VARCHAR(255) NOT NULL,
                message TEXT NOT NULL,
                action_text VARCHAR(100),
                action_link VARCHAR(255),
                dismissed BOOLEAN DEFAULT false,
                metadata JSONB DEFAULT '{}',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✓ smart_suggestions table created/verified")
        
        # Create home_sections table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS home_sections (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                type VARCHAR(50) NOT NULL CHECK (type IN (
                    'stats', 'achievements', 'suggestions', 'challenges', 'missions',
                    'meal_plans', 'recipes', 'journal', 'leaderboard', 'tips',
                    'articles', 'videos', 'streak', 'budget', 'shopping', 'custom'
                )),
                title VARCHAR(255) NOT NULL,
                subtitle VARCHAR(255),
                icon VARCHAR(50),
                order_index INTEGER NOT NULL DEFAULT 0,
                is_visible BOOLEAN DEFAULT true,
                is_global BOOLEAN DEFAULT false,
                data JSONB DEFAULT '{}',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT unique_user_section UNIQUE (user_id, type, title)
            );
        """)
        print("✓ home_sections table created/verified")
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_suggestions_user_id ON smart_suggestions(user_id);
            CREATE INDEX IF NOT EXISTS idx_suggestions_dismissed ON smart_suggestions(dismissed);
            CREATE INDEX IF NOT EXISTS idx_sections_user_id ON home_sections(user_id);
            CREATE INDEX IF NOT EXISTS idx_sections_order ON home_sections(order_index);
        """)
        print("✓ Indexes created/verified")
        
        # Create triggers for updated_at
        cursor.execute("""
            DROP TRIGGER IF EXISTS update_smart_suggestions_updated_at ON smart_suggestions;
            CREATE TRIGGER update_smart_suggestions_updated_at
                BEFORE UPDATE ON smart_suggestions
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
                
            DROP TRIGGER IF EXISTS update_home_sections_updated_at ON home_sections;
            CREATE TRIGGER update_home_sections_updated_at
                BEFORE UPDATE ON home_sections
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
        """)
        print("✓ Triggers created/verified")
        
        conn.commit()
        print("\n✅ All smart features tables created successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error creating tables: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_tables()
