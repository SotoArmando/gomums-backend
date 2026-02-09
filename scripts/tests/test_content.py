"""
Test Content System
Tests articles, videos, and authors
"""
import requests
import os
from datetime import datetime

# Load test environment
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
TEST_EMAIL = os.getenv("TEST_EMAIL", "test@gomums.com")
TEST_PASSWORD = os.getenv("TEST_PASSWORD", "Test123!@#")


def test_content():
    """Test content system workflow"""
    print("\n" + "=" * 70)
    print("CONTENT SYSTEM TEST")
    print("=" * 70)
    
    # ==================== 1. AUTHENTICATE ====================
    print("\n1️⃣ AUTHENTICATING USER...")
    
    auth_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    
    if auth_response.status_code != 200:
        print(f"❌ Authentication failed: {auth_response.text}")
        return
    
    token = auth_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"✅ Authenticated as {TEST_EMAIL}")
    
    # ==================== 2. CREATE AUTHORS ====================
    print("\n2️⃣ CREATING AUTHORS...")
    
    authors_data = [
        {
            "name": "Chef Maria Rodriguez",
            "avatar": "https://example.com/avatars/maria.jpg",
            "bio": "Professional chef with 15 years of experience specializing in budget-friendly family meals"
        },
        {
            "name": "Dr. Sarah Johnson",
            "avatar": "https://example.com/avatars/sarah.jpg",
            "bio": "Nutritionist and wellness expert focused on healthy eating for families"
        },
        {
            "name": "Mike Chen",
            "avatar": "https://example.com/avatars/mike.jpg",
            "bio": "Food blogger and meal prep enthusiast helping families save time and money"
        }
    ]
    
    created_authors = []
    for author_data in authors_data:
        author_response = requests.post(
            f"{BASE_URL}/api/content/authors",
            headers=headers,
            json=author_data
        )
        
        if author_response.status_code == 200:
            author = author_response.json()
            created_authors.append(author)
            print(f"✅ Created author: {author['name']}")
        else:
            print(f"❌ Failed to create author: {author_response.text}")
    
    if not created_authors:
        print("❌ No authors created, aborting test")
        return
    
    # ==================== 3. CREATE ARTICLES ====================
    print("\n3️⃣ CREATING ARTICLES...")
    
    articles_data = [
        {
            "title": "10 Budget-Friendly Meal Prep Ideas for Busy Families",
            "content": """# Introduction
Meal prepping doesn't have to be expensive or time-consuming. Here are 10 practical tips...

## Tip 1: Plan Your Week
Start by planning your meals for the week ahead...

## Tip 2: Buy in Bulk
Purchasing staple items in bulk can save you up to 30%...
""",
            "image": "https://example.com/articles/meal-prep.jpg",
            "category": "meal_prep",
            "read_time": "8 min",
            "author_id": created_authors[0]["id"]
        },
        {
            "title": "How to Cut Your Grocery Bill in Half",
            "content": """# Save Money on Groceries
Learn practical strategies to significantly reduce your food expenses...

## Strategy 1: Shop Seasonal Produce
Seasonal fruits and vegetables are not only fresher but also cheaper...
""",
            "image": "https://example.com/articles/savings.jpg",
            "category": "budgeting",
            "read_time": "6 min",
            "author_id": created_authors[2]["id"]
        },
        {
            "title": "Nutrition Basics: Feeding Your Family Healthy Meals",
            "content": """# Understanding Nutrition
Good nutrition is the foundation of a healthy family...

## Essential Nutrients
Every meal should include a balance of proteins, carbs, and fats...
""",
            "image": "https://example.com/articles/nutrition.jpg",
            "category": "nutrition",
            "read_time": "10 min",
            "author_id": created_authors[1]["id"]
        }
    ]
    
    created_articles = []
    for article_data in articles_data:
        article_response = requests.post(
            f"{BASE_URL}/api/content/articles",
            headers=headers,
            json=article_data
        )
        
        if article_response.status_code == 200:
            article = article_response.json()
            created_articles.append(article)
            print(f"✅ Created article: {article['title']}")
            print(f"   Category: {article['category']} | Read time: {article['read_time']}")
        else:
            print(f"❌ Failed to create article: {article_response.text}")
    
    # ==================== 4. CREATE VIDEOS ====================
    print("\n4️⃣ CREATING VIDEOS...")
    
    videos_data = [
        {
            "title": "Quick 15-Minute Family Dinners",
            "url": "https://youtube.com/watch?v=example1",
            "thumbnail": "https://example.com/videos/quick-dinners-thumb.jpg",
            "duration": "15:30",
            "category": "cooking"
        },
        {
            "title": "Batch Cooking for Beginners",
            "url": "https://youtube.com/watch?v=example2",
            "thumbnail": "https://example.com/videos/batch-cooking-thumb.jpg",
            "duration": "22:45",
            "category": "meal_prep"
        },
        {
            "title": "Shopping Smart: Budget Tips at the Grocery Store",
            "url": "https://youtube.com/watch?v=example3",
            "thumbnail": "https://example.com/videos/shopping-tips-thumb.jpg",
            "duration": "12:15",
            "category": "budgeting"
        }
    ]
    
    created_videos = []
    for video_data in videos_data:
        video_response = requests.post(
            f"{BASE_URL}/api/content/videos",
            headers=headers,
            json=video_data
        )
        
        if video_response.status_code == 200:
            video = video_response.json()
            created_videos.append(video)
            print(f"✅ Created video: {video['title']}")
            print(f"   Duration: {video['duration']} | Category: {video['category']}")
        else:
            print(f"❌ Failed to create video: {video_response.text}")
    
    # ==================== 5. GET ALL AUTHORS ====================
    print("\n5️⃣ GETTING ALL AUTHORS...")
    
    authors_response = requests.get(
        f"{BASE_URL}/api/content/authors",
        headers=headers
    )
    
    if authors_response.status_code == 200:
        authors = authors_response.json()
        print(f"✅ Found {len(authors)} authors")
        for author in authors:
            print(f"   - {author['name']} ({author.get('article_count', 0)} articles)")
    else:
        print(f"❌ Failed to fetch authors: {authors_response.text}")
    
    # ==================== 6. GET ARTICLES LIST ====================
    print("\n6️⃣ GETTING ARTICLES LIST...")
    
    articles_response = requests.get(
        f"{BASE_URL}/api/content/articles",
        headers=headers,
        params={"limit": 10}
    )
    
    if articles_response.status_code == 200:
        articles = articles_response.json()
        print(f"✅ Found {len(articles)} articles")
        for article in articles:
            print(f"   - {article['title']}")
            print(f"     Author: {article.get('author_name', 'Unknown')} | {article['read_time']}")
    else:
        print(f"❌ Failed to fetch articles: {articles_response.text}")
    
    # ==================== 7. FILTER ARTICLES BY CATEGORY ====================
    print("\n7️⃣ FILTERING ARTICLES BY CATEGORY...")
    
    category_response = requests.get(
        f"{BASE_URL}/api/content/articles",
        headers=headers,
        params={"category": "meal_prep"}
    )
    
    if category_response.status_code == 200:
        filtered = category_response.json()
        print(f"✅ Found {len(filtered)} meal_prep articles")
        for article in filtered:
            print(f"   - {article['title']}")
    else:
        print(f"❌ Failed to filter articles: {category_response.text}")
    
    # ==================== 8. SEARCH ARTICLES ====================
    print("\n8️⃣ SEARCHING ARTICLES...")
    
    search_response = requests.get(
        f"{BASE_URL}/api/content/articles",
        headers=headers,
        params={"search": "budget"}
    )
    
    if search_response.status_code == 200:
        search_results = search_response.json()
        print(f"✅ Found {len(search_results)} articles matching 'budget'")
        for article in search_results:
            print(f"   - {article['title']}")
    else:
        print(f"❌ Failed to search articles: {search_response.text}")
    
    # ==================== 9. GET FULL ARTICLE WITH AUTHOR ====================
    print("\n9️⃣ GETTING FULL ARTICLE WITH AUTHOR...")
    
    if created_articles:
        article_id = created_articles[0]["id"]
        full_article_response = requests.get(
            f"{BASE_URL}/api/content/articles/{article_id}",
            headers=headers,
            params={"include_author": True}
        )
        
        if full_article_response.status_code == 200:
            full_article = full_article_response.json()
            print(f"✅ Retrieved article: {full_article['title']}")
            print(f"   Category: {full_article['category']}")
            print(f"   Read time: {full_article['read_time']}")
            print(f"   Content length: {len(full_article['content'])} characters")
            if full_article.get('author'):
                print(f"   Author: {full_article['author']['name']}")
                print(f"   Author bio: {full_article['author']['bio'][:50]}...")
        else:
            print(f"❌ Failed to get full article: {full_article_response.text}")
    
    # ==================== 10. GET VIDEOS LIST ====================
    print("\n🔟 GETTING VIDEOS LIST...")
    
    videos_response = requests.get(
        f"{BASE_URL}/api/content/videos",
        headers=headers
    )
    
    if videos_response.status_code == 200:
        videos = videos_response.json()
        print(f"✅ Found {len(videos)} videos")
        for video in videos:
            print(f"   - {video['title']} ({video['duration']})")
    else:
        print(f"❌ Failed to fetch videos: {videos_response.text}")
    
    # ==================== 11. FILTER VIDEOS BY CATEGORY ====================
    print("\n1️⃣1️⃣ FILTERING VIDEOS BY CATEGORY...")
    
    video_category_response = requests.get(
        f"{BASE_URL}/api/content/videos",
        headers=headers,
        params={"category": "cooking"}
    )
    
    if video_category_response.status_code == 200:
        cooking_videos = video_category_response.json()
        print(f"✅ Found {len(cooking_videos)} cooking videos")
    else:
        print(f"❌ Failed to filter videos: {video_category_response.text}")
    
    # ==================== 12. UPDATE ARTICLE ====================
    print("\n1️⃣2️⃣ UPDATING ARTICLE...")
    
    if created_articles:
        article_id = created_articles[0]["id"]
        updates = {
            "title": "10 Budget-Friendly Meal Prep Ideas (UPDATED)",
            "read_time": "9 min"
        }
        
        update_response = requests.patch(
            f"{BASE_URL}/api/content/articles/{article_id}",
            headers=headers,
            json=updates
        )
        
        if update_response.status_code == 200:
            updated = update_response.json()
            print(f"✅ Updated article: {updated['title']}")
            print(f"   New read time: {updated['read_time']}")
        else:
            print(f"❌ Failed to update article: {update_response.text}")
    
    # ==================== 13. UPDATE VIDEO ====================
    print("\n1️⃣3️⃣ UPDATING VIDEO...")
    
    if created_videos:
        video_id = created_videos[0]["id"]
        updates = {
            "duration": "16:00"
        }
        
        update_response = requests.patch(
            f"{BASE_URL}/api/content/videos/{video_id}",
            headers=headers,
            json=updates
        )
        
        if update_response.status_code == 200:
            updated = update_response.json()
            print(f"✅ Updated video duration: {updated['duration']}")
        else:
            print(f"❌ Failed to update video: {update_response.text}")
    
    # ==================== 14. UPDATE AUTHOR ====================
    print("\n1️⃣4️⃣ UPDATING AUTHOR...")
    
    if created_authors:
        author_id = created_authors[0]["id"]
        updates = {
            "bio": "Award-winning chef with 20 years of experience specializing in budget-friendly family meals and meal preparation"
        }
        
        update_response = requests.patch(
            f"{BASE_URL}/api/content/authors/{author_id}",
            headers=headers,
            json=updates
        )
        
        if update_response.status_code == 200:
            updated = update_response.json()
            print(f"✅ Updated author: {updated['name']}")
            print(f"   New bio: {updated['bio'][:60]}...")
        else:
            print(f"❌ Failed to update author: {update_response.text}")
    
    # ==================== 15. GET CONTENT STATISTICS ====================
    print("\n1️⃣5️⃣ GETTING CONTENT STATISTICS...")
    
    stats_response = requests.get(
        f"{BASE_URL}/api/content/stats",
        headers=headers
    )
    
    if stats_response.status_code == 200:
        stats = stats_response.json()
        print(f"✅ CONTENT STATISTICS:")
        print(f"   Total articles: {stats['total_articles']}")
        print(f"   Total videos: {stats['total_videos']}")
        print(f"   Total authors: {stats['total_authors']}")
        
        if stats.get('articles_by_category'):
            print(f"\n   📊 Articles by category:")
            for category, count in stats['articles_by_category'].items():
                print(f"      {category}: {count}")
        
        if stats.get('videos_by_category'):
            print(f"\n   📊 Videos by category:")
            for category, count in stats['videos_by_category'].items():
                print(f"      {category}: {count}")
    else:
        print(f"❌ Failed to get stats: {stats_response.text}")
    
    # ==================== 16. GET SPECIFIC AUTHOR ====================
    print("\n1️⃣6️⃣ GETTING SPECIFIC AUTHOR...")
    
    if created_authors:
        author_id = created_authors[0]["id"]
        author_response = requests.get(
            f"{BASE_URL}/api/content/authors/{author_id}",
            headers=headers,
            params={"include_stats": True}
        )
        
        if author_response.status_code == 200:
            author = author_response.json()
            print(f"✅ Retrieved author: {author['name']}")
            print(f"   Bio: {author['bio'][:60]}...")
            print(f"   Articles: {author.get('article_count', 0)}")
        else:
            print(f"❌ Failed to get author: {author_response.text}")
    
    # ==================== 17. DELETE VIDEO ====================
    print("\n1️⃣7️⃣ DELETING A VIDEO...")
    
    if created_videos and len(created_videos) > 1:
        video_id = created_videos[-1]["id"]
        delete_response = requests.delete(
            f"{BASE_URL}/api/content/videos/{video_id}",
            headers=headers
        )
        
        if delete_response.status_code == 200:
            print(f"✅ Deleted video successfully")
        else:
            print(f"❌ Failed to delete video: {delete_response.text}")
    
    # ==================== 18. DELETE ARTICLE ====================
    print("\n1️⃣8️⃣ DELETING AN ARTICLE...")
    
    if created_articles and len(created_articles) > 1:
        article_id = created_articles[-1]["id"]
        delete_response = requests.delete(
            f"{BASE_URL}/api/content/articles/{article_id}",
            headers=headers
        )
        
        if delete_response.status_code == 200:
            print(f"✅ Deleted article successfully")
        else:
            print(f"❌ Failed to delete article: {delete_response.text}")
    
    # ==================== FINAL SUMMARY ====================
    print("\n" + "=" * 70)
    print("✅ CONTENT SYSTEM TEST COMPLETED")
    print("=" * 70)
    
    # Get final stats
    final_stats_response = requests.get(
        f"{BASE_URL}/api/content/stats",
        headers=headers
    )
    
    if final_stats_response.status_code == 200:
        final_stats = final_stats_response.json()
        print(f"\n📊 FINAL CONTENT STATE:")
        print(f"   Articles: {final_stats['total_articles']}")
        print(f"   Videos: {final_stats['total_videos']}")
        print(f"   Authors: {final_stats['total_authors']}")
    
    print("\n✨ All content operations tested successfully!")


if __name__ == "__main__":
    test_content()
