"""
Content API Routes
Endpoints for articles, videos, and authors
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from app.models.content import (
    AuthorCreate,
    AuthorUpdate,
    AuthorResponse,
    AuthorWithStats,
    ArticleCreate,
    ArticleUpdate,
    ArticleResponse,
    ArticleWithAuthor,
    ArticleSummary,
    VideoCreate,
    VideoUpdate,
    VideoResponse,
    VideoSummary,
    ContentStats,
    ContentCategory
)
from app.db.repositories.content_repository import ContentRepository
from app.core.security import get_current_user

router = APIRouter(prefix="/api/content", tags=["content"])


# ==================== Author Endpoints ====================

@router.get("/authors", response_model=List[AuthorWithStats])
def get_authors(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all authors
    
    Returns authors with their article counts.
    """
    authors = ContentRepository.get_authors(limit=limit, offset=offset)
    return authors


@router.get("/authors/{author_id}", response_model=AuthorWithStats)
def get_author(
    author_id: str,
    include_stats: bool = Query(True, description="Include article/video counts"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get an author by ID
    
    Returns author details with optional statistics.
    """
    author = ContentRepository.get_author(author_id=author_id, include_stats=include_stats)
    
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    
    return author


@router.post("/authors", response_model=AuthorResponse)
def create_author(
    author: AuthorCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new author
    
    Admin endpoint for creating content authors.
    """
    created_author = ContentRepository.create_author(author.model_dump())
    
    if not created_author:
        raise HTTPException(status_code=500, detail="Failed to create author")
    
    return created_author


@router.patch("/authors/{author_id}", response_model=AuthorResponse)
def update_author(
    author_id: str,
    updates: AuthorUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update an author
    
    Admin endpoint for updating author details.
    """
    author = ContentRepository.update_author(
        author_id=author_id,
        updates=updates.model_dump(exclude_unset=True)
    )
    
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    
    return author


@router.delete("/authors/{author_id}")
def delete_author(
    author_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete an author
    
    Admin endpoint. Articles by this author will have their author_id set to NULL.
    """
    success = ContentRepository.delete_author(author_id=author_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Author not found")
    
    return {"message": "Author deleted successfully"}


# ==================== Article Endpoints ====================

@router.get("/articles", response_model=List[ArticleSummary])
def get_articles(
    category: Optional[ContentCategory] = Query(None, description="Filter by category"),
    author_id: Optional[str] = Query(None, description="Filter by author"),
    search: Optional[str] = Query(None, description="Search in title/content"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """
    Get articles with filters
    
    Returns summarized articles for list views.
    Supports filtering by category, author, and text search.
    """
    articles = ContentRepository.get_articles(
        category=category.value if category else None,
        author_id=author_id,
        search=search,
        limit=limit,
        offset=offset
    )
    
    return articles


@router.get("/articles/{article_id}", response_model=ArticleWithAuthor)
def get_article(
    article_id: str,
    include_author: bool = Query(True, description="Include author details"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get a full article by ID
    
    Returns complete article content with optional author information.
    """
    article = ContentRepository.get_article(
        article_id=article_id,
        include_author=include_author
    )
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    return article


@router.post("/articles", response_model=ArticleResponse)
def create_article(
    article: ArticleCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new article
    
    Admin endpoint for creating articles.
    Content supports Markdown formatting.
    """
    article_data = article.model_dump()
    
    # Convert enum to string
    if article_data.get('category'):
        article_data['category'] = article_data['category'].value if hasattr(article_data['category'], 'value') else article_data['category']
    
    created_article = ContentRepository.create_article(article_data)
    
    if not created_article:
        raise HTTPException(status_code=500, detail="Failed to create article")
    
    return created_article


@router.patch("/articles/{article_id}", response_model=ArticleResponse)
def update_article(
    article_id: str,
    updates: ArticleUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update an article
    
    Admin endpoint for updating article content and metadata.
    """
    update_data = updates.model_dump(exclude_unset=True)
    
    # Convert enum to string
    if update_data.get('category'):
        update_data['category'] = update_data['category'].value if hasattr(update_data['category'], 'value') else update_data['category']
    
    article = ContentRepository.update_article(
        article_id=article_id,
        updates=update_data
    )
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    return article


@router.delete("/articles/{article_id}")
def delete_article(
    article_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete an article
    
    Admin endpoint for permanently removing articles.
    """
    success = ContentRepository.delete_article(article_id=article_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Article not found")
    
    return {"message": "Article deleted successfully"}


# ==================== Video Endpoints ====================

@router.get("/videos", response_model=List[VideoSummary])
def get_videos(
    category: Optional[ContentCategory] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in title"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """
    Get videos with filters
    
    Returns videos for list views.
    Supports filtering by category and text search.
    """
    videos = ContentRepository.get_videos(
        category=category.value if category else None,
        search=search,
        limit=limit,
        offset=offset
    )
    
    return videos


@router.get("/videos/{video_id}", response_model=VideoResponse)
def get_video(
    video_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get a video by ID
    
    Returns complete video information including URL and metadata.
    """
    video = ContentRepository.get_video(video_id=video_id)
    
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    return video


@router.post("/videos", response_model=VideoResponse)
def create_video(
    video: VideoCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new video
    
    Admin endpoint for adding video content.
    Supports YouTube, Vimeo, and other video platforms.
    """
    video_data = video.model_dump()
    
    # Convert enum to string
    if video_data.get('category'):
        video_data['category'] = video_data['category'].value if hasattr(video_data['category'], 'value') else video_data['category']
    
    created_video = ContentRepository.create_video(video_data)
    
    if not created_video:
        raise HTTPException(status_code=500, detail="Failed to create video")
    
    return created_video


@router.patch("/videos/{video_id}", response_model=VideoResponse)
def update_video(
    video_id: str,
    updates: VideoUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update a video
    
    Admin endpoint for updating video metadata.
    """
    update_data = updates.model_dump(exclude_unset=True)
    
    # Convert enum to string
    if update_data.get('category'):
        update_data['category'] = update_data['category'].value if hasattr(update_data['category'], 'value') else update_data['category']
    
    video = ContentRepository.update_video(
        video_id=video_id,
        updates=update_data
    )
    
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    return video


@router.delete("/videos/{video_id}")
def delete_video(
    video_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a video
    
    Admin endpoint for permanently removing videos.
    """
    success = ContentRepository.delete_video(video_id=video_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Video not found")
    
    return {"message": "Video deleted successfully"}


# ==================== Statistics ====================

@router.get("/stats", response_model=ContentStats)
def get_content_stats(current_user: dict = Depends(get_current_user)):
    """
    Get content statistics
    
    Returns counts and breakdowns of all content types.
    """
    stats = ContentRepository.get_content_stats()
    
    if not stats:
        return {
            "total_articles": 0,
            "total_videos": 0,
            "total_authors": 0,
            "articles_by_category": {},
            "videos_by_category": {},
            "most_recent_article": None,
            "most_recent_video": None
        }
    
    return stats
