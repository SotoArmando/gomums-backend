"""
Challenge Repository
Database operations for multi-goal challenges
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from app.core.database import db


class ChallengeRepository:
    """Repository for challenge operations"""

    # ==========================================
    # CHALLENGE CRUD
    # ==========================================

    @staticmethod
    def create_challenge(
        title: str,
        description: Optional[str],
        type: str,
        duration: int,
        reward_points: int,
        goals: List[Dict[str, Any]],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        reward_achievement_ids: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """Create a new challenge with goals"""
        try:
            with db.get_cursor(commit=True) as cursor:
                # Insert challenge
                cursor.execute("""
                    INSERT INTO challenges 
                    (title, description, type, duration, start_date, end_date, reward_points, reward_achievement_ids)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id, title, description, type, duration, start_date, end_date, 
                              reward_points, reward_achievement_ids, created_at, updated_at
                """, (title, description, type, duration, start_date, end_date, reward_points, reward_achievement_ids))
                
                challenge = dict(cursor.fetchone())
                challenge_id = challenge['id']
                
                # Insert goals
                challenge_goals = []
                for goal in goals:
                    cursor.execute("""
                        INSERT INTO challenge_goals 
                        (challenge_id, description, target, order_index)
                        VALUES (%s, %s, %s, %s)
                        RETURNING id, challenge_id, description, target, order_index, created_at, updated_at
                    """, (challenge_id, goal['description'], goal['target'], goal.get('order_index', 0)))
                    
                    challenge_goals.append(dict(cursor.fetchone()))
                
                challenge['goals'] = challenge_goals
                return challenge
                
        except Exception as e:
            print(f"Error creating challenge: {e}")
            return None

    @staticmethod
    def get_challenge_by_id(challenge_id: UUID) -> Optional[Dict[str, Any]]:
        """Get challenge by ID with goals"""
        try:
            with db.get_cursor() as cursor:
                # Get challenge
                cursor.execute("""
                    SELECT id, title, description, type, duration, start_date, end_date, 
                           reward_points, reward_achievement_ids, created_at, updated_at
                    FROM challenges
                    WHERE id = %s
                """, (str(challenge_id),))
                
                challenge = cursor.fetchone()
                if not challenge:
                    return None
                
                challenge = dict(challenge)
                
                # Get goals
                cursor.execute("""
                    SELECT id, challenge_id, description, target, order_index, created_at, updated_at
                    FROM challenge_goals
                    WHERE challenge_id = %s
                    ORDER BY order_index
                """, (str(challenge_id),))
                
                challenge['goals'] = [dict(row) for row in cursor.fetchall()]
                
                return challenge
                
        except Exception as e:
            print(f"Error fetching challenge: {e}")
            return None

    @staticmethod
    def get_all_challenges(
        challenge_type: Optional[str] = None,
        active_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Get all challenges with optional filtering"""
        try:
            with db.get_cursor() as cursor:
                query = """
                    SELECT id, title, description, type, duration, start_date, end_date, 
                           reward_points, reward_achievement_ids, created_at, updated_at
                    FROM challenges
                    WHERE 1=1
                """
                params = []
                
                if challenge_type:
                    query += " AND type = %s"
                    params.append(challenge_type)
                
                if active_only:
                    query += " AND (start_date IS NULL OR start_date <= CURRENT_DATE)"
                    query += " AND (end_date IS NULL OR end_date >= CURRENT_DATE)"
                
                query += " ORDER BY created_at DESC"
                
                cursor.execute(query, params)
                challenges = [dict(row) for row in cursor.fetchall()]
                
                # Get goals for each challenge
                for challenge in challenges:
                    cursor.execute("""
                        SELECT id, challenge_id, description, target, order_index, created_at, updated_at
                        FROM challenge_goals
                        WHERE challenge_id = %s
                        ORDER BY order_index
                    """, (str(challenge['id']),))
                    
                    challenge['goals'] = [dict(row) for row in cursor.fetchall()]
                
                return challenges
                
        except Exception as e:
            print(f"Error fetching challenges: {e}")
            return []

    # ==========================================
    # USER CHALLENGE ASSIGNMENT
    # ==========================================

    @staticmethod
    def assign_challenge(user_id: UUID, challenge_id: UUID) -> Optional[Dict[str, Any]]:
        """Assign a challenge to a user and create goal tracking entries"""
        try:
            with db.get_cursor(commit=True) as cursor:
                # Check if already assigned
                cursor.execute("""
                    SELECT id FROM user_challenges
                    WHERE user_id = %s AND challenge_id = %s AND status = 'active'
                """, (str(user_id), str(challenge_id)))
                
                if cursor.fetchone():
                    return None  # Already assigned
                
                # Get challenge details
                cursor.execute("""
                    SELECT id, duration FROM challenges WHERE id = %s
                """, (str(challenge_id),))
                
                challenge = cursor.fetchone()
                if not challenge:
                    return None
                
                # Insert user_challenge
                cursor.execute("""
                    INSERT INTO user_challenges 
                    (user_id, challenge_id, status, progress)
                    VALUES (%s, %s, 'active', 0)
                    RETURNING id, user_id, challenge_id, status, progress, started_at, completed_at, created_at, updated_at
                """, (str(user_id), str(challenge_id)))
                
                user_challenge = dict(cursor.fetchone())
                user_challenge_id = user_challenge['id']
                
                # Get challenge goals
                cursor.execute("""
                    SELECT id, description, target, order_index
                    FROM challenge_goals
                    WHERE challenge_id = %s
                    ORDER BY order_index
                """, (str(challenge_id),))
                
                goals = cursor.fetchall()
                
                # Create user_challenge_goal entries
                for goal in goals:
                    cursor.execute("""
                        INSERT INTO user_challenge_goals
                        (user_challenge_id, goal_id, completed, progress)
                        VALUES (%s, %s, FALSE, 0)
                    """, (str(user_challenge_id), str(goal['id'])))
                
                return user_challenge
                
        except Exception as e:
            print(f"Error assigning challenge: {e}")
            return None

    # ==========================================
    # USER CHALLENGE PROGRESS
    # ==========================================

    @staticmethod
    def get_active_user_challenges(user_id: UUID) -> List[Dict[str, Any]]:
        """Get all active challenges for a user with goal progress"""
        try:
            with db.get_cursor() as cursor:
                # Get active user challenges
                cursor.execute("""
                    SELECT 
                        uc.id,
                        uc.user_id,
                        uc.challenge_id,
                        c.title as challenge_title,
                        c.description as challenge_description,
                        c.type as challenge_type,
                        c.reward_points,
                        uc.status,
                        uc.progress,
                        uc.started_at,
                        uc.completed_at,
                        uc.created_at,
                        uc.updated_at
                    FROM user_challenges uc
                    JOIN challenges c ON uc.challenge_id = c.id
                    WHERE uc.user_id = %s AND uc.status = 'active'
                    ORDER BY uc.started_at DESC
                """, (str(user_id),))
                
                user_challenges = [dict(row) for row in cursor.fetchall()]
                
                # Get goal progress for each challenge
                for uc in user_challenges:
                    cursor.execute("""
                        SELECT 
                            ucg.id,
                            ucg.user_challenge_id,
                            ucg.goal_id,
                            ucg.completed,
                            ucg.progress,
                            ucg.completed_at,
                            cg.description as goal_description,
                            cg.target as goal_target,
                            cg.order_index
                        FROM user_challenge_goals ucg
                        JOIN challenge_goals cg ON ucg.goal_id = cg.id
                        WHERE ucg.user_challenge_id = %s
                        ORDER BY cg.order_index
                    """, (str(uc['id']),))
                    
                    uc['goal_progress'] = [dict(row) for row in cursor.fetchall()]
                    uc['total_goals'] = len(uc['goal_progress'])
                    uc['completed_goals'] = sum(1 for g in uc['goal_progress'] if g['completed'])
                
                return user_challenges
                
        except Exception as e:
            print(f"Error fetching user challenges: {e}")
            return []

    @staticmethod
    def get_completed_user_challenges(user_id: UUID) -> List[Dict[str, Any]]:
        """Get all completed challenges for a user with goal progress"""
        try:
            with db.get_cursor() as cursor:
                # Get completed user challenges
                cursor.execute("""
                    SELECT 
                        uc.id,
                        uc.user_id,
                        uc.challenge_id,
                        c.title as challenge_title,
                        c.description as challenge_description,
                        c.type as challenge_type,
                        c.reward_points,
                        uc.status,
                        uc.progress,
                        uc.started_at,
                        uc.completed_at,
                        uc.created_at,
                        uc.updated_at
                    FROM user_challenges uc
                    JOIN challenges c ON uc.challenge_id = c.id
                    WHERE uc.user_id = %s AND uc.status = 'completed'
                    ORDER BY uc.completed_at DESC
                """, (str(user_id),))
                
                user_challenges = [dict(row) for row in cursor.fetchall()]
                
                # Get goal progress for each challenge
                for uc in user_challenges:
                    cursor.execute("""
                        SELECT 
                            ucg.id,
                            ucg.user_challenge_id,
                            ucg.goal_id,
                            ucg.completed,
                            ucg.progress,
                            ucg.completed_at,
                            cg.description as goal_description,
                            cg.target as goal_target,
                            cg.order_index
                        FROM user_challenge_goals ucg
                        JOIN challenge_goals cg ON ucg.goal_id = cg.id
                        WHERE ucg.user_challenge_id = %s
                        ORDER BY cg.order_index
                    """, (str(uc['id']),))
                    
                    uc['goal_progress'] = [dict(row) for row in cursor.fetchall()]
                    uc['total_goals'] = len(uc['goal_progress'])
                    uc['completed_goals'] = sum(1 for g in uc['goal_progress'] if g['completed'])
                
                return user_challenges
                
        except Exception as e:
            print(f"Error fetching completed challenges: {e}")
            return []

    @staticmethod
    def update_goal_progress(
        user_challenge_id: UUID,
        goal_id: UUID,
        progress_increment: int = 1
    ) -> Optional[Dict[str, Any]]:
        """Update progress for a specific goal and check for completion"""
        try:
            with db.get_cursor(commit=True) as cursor:
                # Get goal target
                cursor.execute("""
                    SELECT cg.target, ucg.progress, ucg.completed
                    FROM user_challenge_goals ucg
                    JOIN challenge_goals cg ON ucg.goal_id = cg.id
                    WHERE ucg.user_challenge_id = %s AND ucg.goal_id = %s
                """, (str(user_challenge_id), str(goal_id)))
                
                goal_data = cursor.fetchone()
                if not goal_data:
                    return None
                
                # Calculate new progress
                new_progress = goal_data['progress'] + progress_increment
                goal_completed = new_progress >= goal_data['target']
                
                # Update goal progress
                cursor.execute("""
                    UPDATE user_challenge_goals
                    SET progress = %s,
                        completed = %s,
                        completed_at = CASE WHEN %s THEN NOW() ELSE completed_at END,
                        updated_at = NOW()
                    WHERE user_challenge_id = %s AND goal_id = %s
                    RETURNING id, user_challenge_id, goal_id, completed, progress, completed_at
                """, (new_progress, goal_completed, goal_completed, str(user_challenge_id), str(goal_id)))
                
                updated_goal = dict(cursor.fetchone())
                
                # Check if all goals are completed
                cursor.execute("""
                    SELECT COUNT(*) as total, 
                           SUM(CASE WHEN completed THEN 1 ELSE 0 END) as completed_count
                    FROM user_challenge_goals
                    WHERE user_challenge_id = %s
                """, (str(user_challenge_id),))
                
                goal_stats = cursor.fetchone()
                
                # Update user_challenge if all goals completed
                if goal_stats['total'] == goal_stats['completed_count']:
                    # Get challenge details for points
                    cursor.execute("""
                        SELECT c.reward_points, uc.user_id
                        FROM user_challenges uc
                        JOIN challenges c ON uc.challenge_id = c.id
                        WHERE uc.id = %s
                    """, (str(user_challenge_id),))
                    
                    challenge_info = cursor.fetchone()
                    
                    # Mark challenge as completed
                    cursor.execute("""
                        UPDATE user_challenges
                        SET status = 'completed',
                            progress = 100,
                            completed_at = NOW(),
                            updated_at = NOW()
                        WHERE id = %s
                    """, (str(user_challenge_id),))
                    
                    # Award points
                    if challenge_info and challenge_info['reward_points'] > 0:
                        cursor.execute("""
                            UPDATE user_stats
                            SET points = points + %s,
                                updated_at = NOW()
                            WHERE user_id = %s
                        """, (challenge_info['reward_points'], str(challenge_info['user_id'])))
                    
                    updated_goal['challenge_completed'] = True
                    updated_goal['points_awarded'] = challenge_info['reward_points']
                else:
                    updated_goal['challenge_completed'] = False
                
                return updated_goal
                
        except Exception as e:
            print(f"Error updating goal progress: {e}")
            return None

    @staticmethod
    def update_goal_progress_absolute(
        user_challenge_id: UUID,
        goal_id: UUID,
        progress_value: int
    ) -> Optional[Dict[str, Any]]:
        """Update progress for a goal with an absolute value (e.g., consecutive days count)"""
        try:
            with db.get_cursor(commit=True) as cursor:
                # Get goal target
                cursor.execute("""
                    SELECT cg.target, ucg.progress, ucg.completed
                    FROM user_challenge_goals ucg
                    JOIN challenge_goals cg ON ucg.goal_id = cg.id
                    WHERE ucg.user_challenge_id = %s AND ucg.goal_id = %s
                """, (str(user_challenge_id), str(goal_id)))
                
                goal_data = cursor.fetchone()
                if not goal_data:
                    return None
                
                # Use the provided absolute value
                goal_completed = progress_value >= goal_data['target']
                
                # Only update if progress changed
                if goal_data['progress'] == progress_value and goal_data['completed'] == goal_completed:
                    return None
                
                # Update goal progress with absolute value
                cursor.execute("""
                    UPDATE user_challenge_goals
                    SET progress = %s,
                        completed = %s,
                        completed_at = CASE WHEN %s AND completed_at IS NULL THEN NOW() ELSE completed_at END,
                        updated_at = NOW()
                    WHERE user_challenge_id = %s AND goal_id = %s
                    RETURNING id, user_challenge_id, goal_id, completed, progress, completed_at
                """, (progress_value, goal_completed, goal_completed, str(user_challenge_id), str(goal_id)))
                
                updated_goal = dict(cursor.fetchone())
                
                # Check if all goals are completed
                cursor.execute("""
                    SELECT COUNT(*) as total, 
                           SUM(CASE WHEN completed THEN 1 ELSE 0 END) as completed_count
                    FROM user_challenge_goals
                    WHERE user_challenge_id = %s
                """, (str(user_challenge_id),))
                
                goal_stats = cursor.fetchone()
                
                # Update user_challenge if all goals completed
                if goal_stats['total'] == goal_stats['completed_count']:
                    # Get challenge details for points
                    cursor.execute("""
                        SELECT c.reward_points, uc.user_id
                        FROM user_challenges uc
                        JOIN challenges c ON uc.challenge_id = c.id
                        WHERE uc.id = %s
                    """, (str(user_challenge_id),))
                    
                    challenge_info = cursor.fetchone()
                    
                    # Mark challenge as completed
                    cursor.execute("""
                        UPDATE user_challenges
                        SET status = 'completed',
                            progress = 100,
                            completed_at = NOW(),
                            updated_at = NOW()
                        WHERE id = %s
                    """, (str(user_challenge_id),))
                    
                    # Award points
                    if challenge_info and challenge_info['reward_points'] > 0:
                        cursor.execute("""
                            UPDATE user_stats
                            SET points = points + %s,
                                updated_at = NOW()
                            WHERE user_id = %s
                        """, (challenge_info['reward_points'], str(challenge_info['user_id'])))
                    
                    updated_goal['challenge_completed'] = True
                    updated_goal['points_awarded'] = challenge_info['reward_points']
                else:
                    updated_goal['challenge_completed'] = False
                
                return updated_goal
                
        except Exception as e:
            print(f"Error updating goal progress (absolute): {e}")
            return None

    @staticmethod
    def get_user_challenge_details(user_challenge_id: UUID) -> Optional[Dict[str, Any]]:
        """Get detailed information about a user's challenge"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        uc.id,
                        uc.user_id,
                        uc.challenge_id,
                        uc.status,
                        uc.progress,
                        uc.started_at,
                        uc.completed_at,
                        c.title,
                        c.description,
                        c.type,
                        c.duration,
                        c.reward_points
                    FROM user_challenges uc
                    JOIN challenges c ON uc.challenge_id = c.id
                    WHERE uc.id = %s
                """, (str(user_challenge_id),))
                
                user_challenge = cursor.fetchone()
                if not user_challenge:
                    return None
                
                user_challenge = dict(user_challenge)
                
                # Get goal progress
                cursor.execute("""
                    SELECT 
                        ucg.id,
                        ucg.completed,
                        ucg.progress,
                        ucg.completed_at,
                        cg.id as goal_id,
                        cg.description as goal_description,
                        cg.target as goal_target,
                        cg.order_index
                    FROM user_challenge_goals ucg
                    JOIN challenge_goals cg ON ucg.goal_id = cg.id
                    WHERE ucg.user_challenge_id = %s
                    ORDER BY cg.order_index
                """, (str(user_challenge_id),))
                
                user_challenge['goals'] = [dict(row) for row in cursor.fetchall()]
                
                return user_challenge
                
        except Exception as e:
            print(f"Error fetching user challenge details: {e}")
            return None
