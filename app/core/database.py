import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from typing import Generator, Any
from app.core.config import settings


class Database:
    """Database connection pool manager"""
    
    def __init__(self):
        """Initialize database connection pool"""
        self.connection_pool = None
    
    def initialize(self):
        """Create the connection pool"""
        try:
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                1,  # Minimum connections
                20,  # Maximum connections
                host=settings.DATABASE_HOST,
                port=settings.DATABASE_PORT,
                database=settings.DATABASE_NAME,
                user=settings.DATABASE_USER,
                password=settings.DATABASE_PASSWORD
            )
            print("✓ Database connection pool created successfully")
        except psycopg2.Error as e:
            print(f"✗ Failed to create database connection pool: {e}")
            raise
    
    def close(self):
        """Close all connections in the pool"""
        if self.connection_pool:
            self.connection_pool.closeall()
            print("✓ Database connection pool closed")
    
    @contextmanager
    def get_connection(self) -> Generator[Any, None, None]:
        """
        Context manager to get a connection from the pool
        
        Usage:
            with db.get_connection() as conn:
                # Use connection
                pass
        """
        if not self.connection_pool:
            raise Exception("Database pool not initialized. Call initialize() first.")
        
        conn = self.connection_pool.getconn()
        try:
            yield conn
        finally:
            self.connection_pool.putconn(conn)
    
    @contextmanager
    def get_cursor(self, commit: bool = False, dict_cursor: bool = True) -> Generator[Any, None, None]:
        """
        Context manager to get a cursor from a connection
        
        Args:
            commit: Whether to commit the transaction after cursor operations
            dict_cursor: Whether to return results as dictionaries (default: True)
        
        Usage:
            with db.get_cursor(commit=True) as cursor:
                cursor.execute("INSERT INTO users ...")
        """
        with self.get_connection() as conn:
            cursor_factory = RealDictCursor if dict_cursor else None
            cursor = conn.cursor(cursor_factory=cursor_factory)
            try:
                yield cursor
                if commit:
                    conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                cursor.close()
    
    def test_connection(self) -> bool:
        """Test if database connection is working"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT NOW(), version()")
                result = cursor.fetchone()
                print(f"✓ Database connection successful")
                print(f"  Server time: {result['now']}")
                print(f"  PostgreSQL version: {result['version'][:50]}...")
                return True
        except Exception as e:
            print(f"✗ Database connection test failed: {e}")
            return False


# Create a global database instance
db = Database()
