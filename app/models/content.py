"""
Content System Models
Models for articles, videos, and authors
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from datetime import datetime
from enum import Enum


class ContentCategory(str, Enum):
    """Content categories"""
    COOKING = "cooking"
    NUTRITION = "nutrition"
    BUDGETING = "budgeting"
    MEAL_PREP = "meal_prep"
    TIPS = "tips"
    RECIPES = "recipes"
    FAMILY = "family"
    HEALTH = "health"
    SAVINGS = "savings"
    LIFESTYLE = "lifestyle"
    GENERAL = "general"


# ==================== Author Models ====================

class AuthorBase(BaseModel):
    """Base model for authors"""
    name: str = Field(..., max_length=255, description="Author name")
    avatar: Optional[str] = Field(None, description="Author avatar URL")
    bio: Optional[str] = Field(None, description="Author biography")


class AuthorCreate(AuthorBase):
    """Model for creating an author"""
    pass


class AuthorUpdate(BaseModel):
    """Model for updating an author"""
    name: Optional[str] = Field(None, max_length=255)
    avatar: Optional[str] = None
    bio: Optional[str] = None


class AuthorResponse(AuthorBase):
    """Model for author responses"""
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AuthorWithStats(AuthorResponse):
    """Author with article/video counts"""
    article_count: int = 0
    video_count: int = 0


# ==================== Article Models ====================

class ArticleBase(BaseModel):
    """Base model for articles"""
    title: str = Field(..., max_length=255, description="Article title")
    content: str = Field(..., description="Article content (Markdown supported)")
    image: Optional[str] = Field(None, description="Article cover image URL")
    category: Optional[ContentCategory] = Field(None, description="Article category")
    read_time: Optional[str] = Field(None, max_length=50, description="Estimated read time (e.g., '5 min')")
    author_id: Optional[str] = Field(None, description="Author ID")


class ArticleCreate(ArticleBase):
    """Model for creating an article"""
    published_date: Optional[datetime] = Field(None, description="Publication date (defaults to now)")


class ArticleUpdate(BaseModel):
    """Model for updating an article"""
    title: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = None
    image: Optional[str] = None
    category: Optional[ContentCategory] = None
    read_time: Optional[str] = Field(None, max_length=50)
    author_id: Optional[str] = None
    published_date: Optional[datetime] = None


class ArticleResponse(ArticleBase):
    """Model for article responses"""
    id: str
    published_date: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ArticleWithAuthor(ArticleResponse):
    """Article with author information"""
    author: Optional[AuthorResponse] = None


class ArticleSummary(BaseModel):
    """Summarized article for list views"""
    id: str
    title: str
    image: Optional[str]
    category: Optional[str]
    read_time: Optional[str]
    author_id: Optional[str]
    author_name: Optional[str]
    published_date: datetime
    
    class Config:
        from_attributes = True


# ==================== Video Models ====================

class VideoBase(BaseModel):
    """Base model for videos"""
    title: str = Field(..., max_length=255, description="Video title")
    url: str = Field(..., description="Video URL (YouTube, Vimeo, etc.)")
    thumbnail: Optional[str] = Field(None, description="Video thumbnail URL")
    duration: Optional[str] = Field(None, max_length=50, description="Video duration (e.g., '10:30')")
    category: Optional[ContentCategory] = Field(None, description="Video category")


class VideoCreate(VideoBase):
    """Model for creating a video"""
    published_date: Optional[datetime] = Field(None, description="Publication date (defaults to now)")


class VideoUpdate(BaseModel):
    """Model for updating a video"""
    title: Optional[str] = Field(None, max_length=255)
    url: Optional[str] = None
    thumbnail: Optional[str] = None
    duration: Optional[str] = Field(None, max_length=50)
    category: Optional[ContentCategory] = None
    published_date: Optional[datetime] = None


class VideoResponse(VideoBase):
    """Model for video responses"""
    id: str
    published_date: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class VideoSummary(BaseModel):
    """Summarized video for list views"""
    id: str
    title: str
    thumbnail: Optional[str]
    duration: Optional[str]
    category: Optional[str]
    url: str
    published_date: datetime
    
    class Config:
        from_attributes = True


# ==================== Filter/Search Models ====================

class ContentFilters(BaseModel):
    """Filters for content queries"""
    category: Optional[ContentCategory] = None
    search: Optional[str] = Field(None, description="Search in title/content")
    limit: int = Field(10, ge=1, le=100, description="Number of results")
    offset: int = Field(0, ge=0, description="Offset for pagination")


class ArticleFilters(ContentFilters):
    """Filters specific to articles"""
    author_id: Optional[str] = None


class ContentStats(BaseModel):
    """Statistics about content"""
    total_articles: int = 0
    total_videos: int = 0
    total_authors: int = 0
    articles_by_category: dict = {}
    videos_by_category: dict = {}
    most_recent_article: Optional[datetime] = None
    most_recent_video: Optional[datetime] = None
