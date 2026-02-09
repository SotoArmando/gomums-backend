"""
Content Repository
Database operations for articles, videos, and authors
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.core.database import db


class ContentRepository:
    """Repository for content (articles, videos, authors)"""
    
    db = db
    
    # ==================== Author Operations ====================
    
    @staticmethod
    def create_author(author_data: dict) -> Optional[dict]:
        """Create a new author"""
        try:
            with ContentRepository.db.get_cursor(commit=True) as cursor:
                cursor.execute("""
                    INSERT INTO authors (name, avatar, bio)
                    VALUES (%(name)s, %(avatar)s, %(bio)s)
                    RETURNING id, name, avatar, bio, created_at, updated_at
                """, author_data)
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
        except Exception as e:
            print(f"Error creating author: {e}")
            return None
    
    @staticmethod
    def get_author(author_id: str, include_stats: bool = False) -> Optional[dict]:
        """Get an author by ID"""
        try:
            with ContentRepository.db.get_cursor() as cursor:
                if include_stats:
                    cursor.execute("""
                        SELECT a.id, a.name, a.avatar, a.bio, a.created_at, a.updated_at,
                               COUNT(DISTINCT ar.id) as article_count,
                               COUNT(DISTINCT v.id) as video_count
                        FROM authors a
                        LEFT JOIN articles ar ON ar.author_id = a.id
                        LEFT JOIN videos v ON v.category = (
                            SELECT DISTINCT category FROM articles WHERE author_id = a.id LIMIT 1
                        )
                        WHERE a.id = %s
                        GROUP BY a.id
                    """, (author_id,))
                else:
                    cursor.execute("""
                        SELECT id, name, avatar, bio, created_at, updated_at
                        FROM authors
                        WHERE id = %s
                    """, (author_id,))
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
        except Exception as e:
            print(f"Error fetching author: {e}")
            return None
    
    @staticmethod
    def get_authors(limit: int = 50, offset: int = 0) -> List[dict]:
        """Get all authors"""
        try:
            with ContentRepository.db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT a.id, a.name, a.avatar, a.bio, a.created_at, a.updated_at,
                           COUNT(DISTINCT ar.id) as article_count
                    FROM authors a
                    LEFT JOIN articles ar ON ar.author_id = a.id
                    GROUP BY a.id
                    ORDER BY a.name ASC
                    LIMIT %s OFFSET %s
                """, (limit, offset))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error fetching authors: {e}")
            return []
    
    @staticmethod
    def update_author(author_id: str, updates: dict) -> Optional[dict]:
        """Update an author"""
        try:
            allowed_fields = ['name', 'avatar', 'bio']
            set_parts = []
            values = {}
            
            for field in allowed_fields:
                if field in updates and updates[field] is not None:
                    set_parts.append(f"{field} = %({field})s")
                    values[field] = updates[field]
            
            if not set_parts:
                return None
            
            set_parts.append("updated_at = NOW()")
            set_clause = ", ".join(set_parts)
            values['author_id'] = author_id
            
            with ContentRepository.db.get_cursor(commit=True) as cursor:
                query = f"""
                    UPDATE authors
                    SET {set_clause}
                    WHERE id = %(author_id)s
                    RETURNING id, name, avatar, bio, created_at, updated_at
                """
                
                cursor.execute(query, values)
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
        except Exception as e:
            print(f"Error updating author: {e}")
            return None
    
    @staticmethod
    def delete_author(author_id: str) -> bool:
        """Delete an author"""
        try:
            with ContentRepository.db.get_cursor(commit=True) as cursor:
                cursor.execute("DELETE FROM authors WHERE id = %s", (author_id,))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting author: {e}")
            return False
    
    # ==================== Article Operations ====================
    
    @staticmethod
    def create_article(article_data: dict) -> Optional[dict]:
        """Create a new article"""
        try:
            with ContentRepository.db.get_cursor(commit=True) as cursor:
                # Handle published_date default
                if 'published_date' not in article_data or article_data['published_date'] is None:
                    article_data['published_date'] = datetime.now()
                
                cursor.execute("""
                    INSERT INTO articles 
                        (title, content, image, category, read_time, author_id, published_date)
                    VALUES 
                        (%(title)s, %(content)s, %(image)s, %(category)s, 
                         %(read_time)s, %(author_id)s, %(published_date)s)
                    RETURNING id, title, content, image, category, read_time, author_id,
                              published_date, created_at, updated_at
                """, article_data)
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
        except Exception as e:
            print(f"Error creating article: {e}")
            return None
    
    @staticmethod
    def get_article(article_id: str, include_author: bool = False) -> Optional[dict]:
        """Get an article by ID"""
        try:
            with ContentRepository.db.get_cursor() as cursor:
                if include_author:
                    cursor.execute("""
                        SELECT a.id, a.title, a.content, a.image, a.category, 
                               a.read_time, a.author_id, a.published_date, 
                               a.created_at, a.updated_at,
                               au.id as author_id_nested, au.name as author_name, 
                               au.avatar as author_avatar, au.bio as author_bio,
                               au.created_at as author_created_at, au.updated_at as author_updated_at
                        FROM articles a
                        LEFT JOIN authors au ON au.id = a.author_id
                        WHERE a.id = %s
                    """, (article_id,))
                else:
                    cursor.execute("""
                        SELECT id, title, content, image, category, read_time, author_id,
                               published_date, created_at, updated_at
                        FROM articles
                        WHERE id = %s
                    """, (article_id,))
                
                row = cursor.fetchone()
                if row:
                    result = dict(row)
                    if include_author and result.get('author_name'):
                        result['author'] = {
                            'id': result['author_id'],
                            'name': result['author_name'],
                            'avatar': result.get('author_avatar'),
                            'bio': result.get('author_bio'),
                            'created_at': result.get('author_created_at'),
                            'updated_at': result.get('author_updated_at')
                        }
                        # Clean up nested fields
                        for key in ['author_id_nested', 'author_name', 'author_avatar', 'author_bio', 
                                    'author_created_at', 'author_updated_at']:
                            result.pop(key, None)
                    return result
                return None
        except Exception as e:
            print(f"Error fetching article: {e}")
            return None
    
    @staticmethod
    def get_articles(category: Optional[str] = None, 
                    author_id: Optional[str] = None,
                    search: Optional[str] = None,
                    limit: int = 10, 
                    offset: int = 0) -> List[dict]:
        """Get articles with filters"""
        try:
            with ContentRepository.db.get_cursor() as cursor:
                conditions = []
                values = {"limit": limit, "offset": offset}
                
                if category:
                    conditions.append("a.category = %(category)s")
                    values["category"] = category
                
                if author_id:
                    conditions.append("a.author_id = %(author_id)s")
                    values["author_id"] = author_id
                
                if search:
                    conditions.append("(a.title ILIKE %(search)s OR a.content ILIKE %(search)s)")
                    values["search"] = f"%{search}%"
                
                where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
                
                query = f"""
                    SELECT a.id, a.title, a.image, a.category, a.read_time, a.author_id,
                           a.published_date, au.name as author_name
                    FROM articles a
                    LEFT JOIN authors au ON au.id = a.author_id
                    {where_clause}
                    ORDER BY a.published_date DESC
                    LIMIT %(limit)s OFFSET %(offset)s
                """
                
                cursor.execute(query, values)
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error fetching articles: {e}")
            return []
    
    @staticmethod
    def update_article(article_id: str, updates: dict) -> Optional[dict]:
        """Update an article"""
        try:
            allowed_fields = ['title', 'content', 'image', 'category', 'read_time', 
                            'author_id', 'published_date']
            set_parts = []
            values = {}
            
            for field in allowed_fields:
                if field in updates and updates[field] is not None:
                    set_parts.append(f"{field} = %({field})s")
                    values[field] = updates[field]
            
            if not set_parts:
                return None
            
            set_parts.append("updated_at = NOW()")
            set_clause = ", ".join(set_parts)
            values['article_id'] = article_id
            
            with ContentRepository.db.get_cursor(commit=True) as cursor:
                query = f"""
                    UPDATE articles
                    SET {set_clause}
                    WHERE id = %(article_id)s
                    RETURNING id, title, content, image, category, read_time, author_id,
                              published_date, created_at, updated_at
                """
                
                cursor.execute(query, values)
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
        except Exception as e:
            print(f"Error updating article: {e}")
            return None
    
    @staticmethod
    def delete_article(article_id: str) -> bool:
        """Delete an article"""
        try:
            with ContentRepository.db.get_cursor(commit=True) as cursor:
                cursor.execute("DELETE FROM articles WHERE id = %s", (article_id,))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting article: {e}")
            return False
    
    # ==================== Video Operations ====================
    
    @staticmethod
    def create_video(video_data: dict) -> Optional[dict]:
        """Create a new video"""
        try:
            with ContentRepository.db.get_cursor(commit=True) as cursor:
                # Handle published_date default
                if 'published_date' not in video_data or video_data['published_date'] is None:
                    video_data['published_date'] = datetime.now()
                
                cursor.execute("""
                    INSERT INTO videos 
                        (title, url, thumbnail, duration, category, published_date)
                    VALUES 
                        (%(title)s, %(url)s, %(thumbnail)s, %(duration)s, 
                         %(category)s, %(published_date)s)
                    RETURNING id, title, url, thumbnail, duration, category,
                              published_date, created_at, updated_at
                """, video_data)
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
        except Exception as e:
            print(f"Error creating video: {e}")
            return None
    
    @staticmethod
    def get_video(video_id: str) -> Optional[dict]:
        """Get a video by ID"""
        try:
            with ContentRepository.db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT id, title, url, thumbnail, duration, category,
                           published_date, created_at, updated_at
                    FROM videos
                    WHERE id = %s
                """, (video_id,))
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
        except Exception as e:
            print(f"Error fetching video: {e}")
            return None
    
    @staticmethod
    def get_videos(category: Optional[str] = None,
                  search: Optional[str] = None,
                  limit: int = 10,
                  offset: int = 0) -> List[dict]:
        """Get videos with filters"""
        try:
            with ContentRepository.db.get_cursor() as cursor:
                conditions = []
                values = {"limit": limit, "offset": offset}
                
                if category:
                    conditions.append("category = %(category)s")
                    values["category"] = category
                
                if search:
                    conditions.append("title ILIKE %(search)s")
                    values["search"] = f"%{search}%"
                
                where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
                
                query = f"""
                    SELECT id, title, thumbnail, duration, category, url, published_date
                    FROM videos
                    {where_clause}
                    ORDER BY published_date DESC
                    LIMIT %(limit)s OFFSET %(offset)s
                """
                
                cursor.execute(query, values)
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error fetching videos: {e}")
            return []
    
    @staticmethod
    def update_video(video_id: str, updates: dict) -> Optional[dict]:
        """Update a video"""
        try:
            allowed_fields = ['title', 'url', 'thumbnail', 'duration', 'category', 'published_date']
            set_parts = []
            values = {}
            
            for field in allowed_fields:
                if field in updates and updates[field] is not None:
                    set_parts.append(f"{field} = %({field})s")
                    values[field] = updates[field]
            
            if not set_parts:
                return None
            
            set_parts.append("updated_at = NOW()")
            set_clause = ", ".join(set_parts)
            values['video_id'] = video_id
            
            with ContentRepository.db.get_cursor(commit=True) as cursor:
                query = f"""
                    UPDATE videos
                    SET {set_clause}
                    WHERE id = %(video_id)s
                    RETURNING id, title, url, thumbnail, duration, category,
                              published_date, created_at, updated_at
                """
                
                cursor.execute(query, values)
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
        except Exception as e:
            print(f"Error updating video: {e}")
            return None
    
    @staticmethod
    def delete_video(video_id: str) -> bool:
        """Delete a video"""
        try:
            with ContentRepository.db.get_cursor(commit=True) as cursor:
                cursor.execute("DELETE FROM videos WHERE id = %s", (video_id,))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting video: {e}")
            return False
    
    # ==================== Statistics ====================
    
    @staticmethod
    def get_content_stats() -> Optional[dict]:
        """Get content statistics"""
        try:
            with ContentRepository.db.get_cursor() as cursor:
                # Overall counts
                cursor.execute("""
                    SELECT 
                        COUNT(DISTINCT a.id) as total_articles,
                        COUNT(DISTINCT v.id) as total_videos,
                        COUNT(DISTINCT au.id) as total_authors,
                        MAX(a.published_date) as most_recent_article,
                        MAX(v.published_date) as most_recent_video
                    FROM authors au
                    LEFT JOIN articles a ON a.author_id = au.id
                    LEFT JOIN videos v ON true
                """)
                
                stats = dict(cursor.fetchone())
                
                # Articles by category
                cursor.execute("""
                    SELECT category, COUNT(*) as count
                    FROM articles
                    WHERE category IS NOT NULL
                    GROUP BY category
                """)
                
                articles_by_category = {}
                for row in cursor.fetchall():
                    articles_by_category[row['category']] = row['count']
                
                stats['articles_by_category'] = articles_by_category
                
                # Videos by category
                cursor.execute("""
                    SELECT category, COUNT(*) as count
                    FROM videos
                    WHERE category IS NOT NULL
                    GROUP BY category
                """)
                
                videos_by_category = {}
                for row in cursor.fetchall():
                    videos_by_category[row['category']] = row['count']
                
                stats['videos_by_category'] = videos_by_category
                
                return stats
        except Exception as e:
            print(f"Error fetching content stats: {e}")
            return None
