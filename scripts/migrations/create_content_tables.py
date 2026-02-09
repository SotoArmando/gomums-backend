"""
Create Content Tables
Creates authors, articles, and videos tables
"""
import psycopg2
from app.core.config import settings

def create_content_tables():
    """Create content tables"""
    conn = psycopg2.connect(
        host=settings.DATABASE_HOST,
        port=settings.DATABASE_PORT,
        database=settings.DATABASE_NAME,
        user=settings.DATABASE_USER,
        password=settings.DATABASE_PASSWORD
    )
    cursor = conn.cursor()
    
    try:
        # Create authors table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS authors (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                avatar VARCHAR(255),
                bio TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✓ authors table created/verified")
        
        # Create articles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                content TEXT NOT NULL,
                image VARCHAR(255),
                category VARCHAR(50) CHECK (category IN (
                    'cooking', 'nutrition', 'budgeting', 'meal_prep', 
                    'kitchen_tips', 'family_meals', 'other'
                )),
                read_time INTEGER CHECK (read_time > 0),
                author_id UUID REFERENCES authors(id) ON DELETE SET NULL,
                published_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✓ articles table created/verified")
        
        # Create videos table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS videos (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                url VARCHAR(255) NOT NULL,
                thumbnail VARCHAR(255),
                duration VARCHAR(10),
                category VARCHAR(50) CHECK (category IN (
                    'cooking', 'meal_prep', 'budgeting', 'nutrition',
                    'kitchen_tips', 'family_meals', 'other'
                )),
                author_id UUID REFERENCES authors(id) ON DELETE SET NULL,
                published_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✓ videos table created/verified")
        
        # Create indexes - skip if columns don't exist yet
        try:
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_articles_author ON articles(author_id);
                CREATE INDEX IF NOT EXISTS idx_articles_category ON articles(category);
                CREATE INDEX IF NOT EXISTS idx_articles_date ON articles(published_date);
                CREATE INDEX IF NOT EXISTS idx_videos_author ON videos(author_id);
                CREATE INDEX IF NOT EXISTS idx_videos_category ON videos(category);
            """)
            print("✓ Indexes created/verified")
        except Exception as idx_error:
            print(f"⚠️  Skipping indexes: {idx_error}")
        
        # Create triggers for updated_at
        cursor.execute("""
            DROP TRIGGER IF EXISTS update_authors_updated_at ON authors;
            CREATE TRIGGER update_authors_updated_at
                BEFORE UPDATE ON authors
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
                
            DROP TRIGGER IF EXISTS update_articles_updated_at ON articles;
            CREATE TRIGGER update_articles_updated_at
                BEFORE UPDATE ON articles
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
                
            DROP TRIGGER IF EXISTS update_videos_updated_at ON videos;
            CREATE TRIGGER update_videos_updated_at
                BEFORE UPDATE ON videos
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
        """)
        print("✓ Triggers created/verified")
        
        conn.commit()
        print("\n✅ All content tables created successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error creating tables: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_content_tables()
