"""
Mission Repository - Database operations for missions
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.core.database import db


class MissionRepository:
    """Repository for mission-related database operations"""
    
    async def get_active_missions(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all active missions for a user
        Auto-expires missions that have passed their deadline
        
        Args:
            user_id: UUID of the user
        
        Returns:
            List of user missions with embedded mission details
        """
        # First, mark expired missions as 'expired'
        expire_query = """
            UPDATE user_missions
            SET status = 'expired', updated_at = NOW()
            WHERE user_id = %s 
            AND status = 'active'
            AND expires_at IS NOT NULL 
            AND expires_at < NOW()
        """
        
        # Then fetch active missions (excluding newly expired ones)
        query = """
            SELECT 
                um.id, um.user_id, um.mission_id, um.status, um.progress,
                um.started_at, um.completed_at, um.expires_at,
                um.created_at, um.updated_at,
                m.id as m_id, m.title, m.description, m.type, m.category,
                m.difficulty, m.target, m.reward_points, m.reward_achievement_id,
                m.kind,
                m.created_at as m_created_at, m.updated_at as m_updated_at
            FROM user_missions um
            JOIN missions m ON um.mission_id = m.id
            WHERE um.user_id = %s 
            AND um.status = 'active'
            AND (um.expires_at IS NULL OR um.expires_at > NOW())
            ORDER BY um.started_at DESC
        """
        
        try:
            with db.get_cursor(commit=True) as cursor:
                # First, mark expired missions
                cursor.execute(expire_query, (user_id,))
                
                # Then fetch active (non-expired) missions
                cursor.execute(query, (user_id,))
                rows = cursor.fetchall()
                
                missions = []
                for row in rows:
                    user_mission_id = str(row['id'])
                    mission_id = str(row['mission_id'])
                    
                    # Get mission goals
                    mission_goals = await self.get_mission_goals(mission_id)
                    
                    # Get goal progress for this user_mission
                    goal_progress = await self.get_user_mission_goal_progress(user_mission_id)
                    
                    missions.append({
                        'id': user_mission_id,
                        'user_id': str(row['user_id']),
                        'mission_id': mission_id,
                        'status': row['status'],
                        'progress': row['progress'],
                        'started_at': row['started_at'],
                        'completed_at': row['completed_at'],
                        'expires_at': row['expires_at'],
                        'created_at': row['created_at'],
                        'updated_at': row['updated_at'],
                        'goal_progress': goal_progress,
                        'mission': {
                            'id': mission_id,
                            'title': row['title'],
                            'description': row['description'],
                            'type': row['type'],
                            'category': row['category'],
                            'difficulty': row['difficulty'],
                            'target': row['target'],
                            'reward_points': row['reward_points'],
                            'reward_achievement_id': str(row['reward_achievement_id']) if row['reward_achievement_id'] else None,
                            'kind': row.get('kind', 'mission'),
                            'goals': mission_goals,
                            'created_at': row['m_created_at'],
                            'updated_at': row['m_updated_at']
                        }
                    })
                
                return missions
        except Exception as e:
            print(f"Error getting active missions: {e}")
            return []
    
    async def get_mission_goals(self, mission_id: str) -> List[Dict[str, Any]]:
        """
        Get all goals for a mission
        
        Args:
            mission_id: UUID of the mission
        
        Returns:
            List of mission goals
        """
        query = """
            SELECT id, mission_id, description, target, order_index,
                   created_at, updated_at
            FROM mission_goals
            WHERE mission_id = %s
            ORDER BY order_index
        """
        
        try:
            with db.get_cursor() as cursor:
                cursor.execute(query, (mission_id,))
                rows = cursor.fetchall()
                
                goals = []
                for row in rows:
                    goals.append({
                        'id': str(row['id']),
                        'mission_id': str(row['mission_id']),
                        'description': row['description'],
                        'target': row['target'],
                        'order_index': row['order_index'],
                        'created_at': row['created_at'],
                        'updated_at': row['updated_at']
                    })
                
                return goals
        except Exception as e:
            print(f"Error getting mission goals: {e}")
            return []
    
    async def get_user_mission_goal_progress(self, user_mission_id: str) -> List[Dict[str, Any]]:
        """
        Get goal progress for a user's mission
        
        Args:
            user_mission_id: UUID of the user_mission
        
        Returns:
            List of goal progress with goal details
        """
        query = """
            SELECT 
                umg.id, umg.user_mission_id, umg.goal_id,
                umg.completed, umg.progress, umg.completed_at,
                umg.created_at, umg.updated_at,
                mg.description as goal_description,
                mg.target as goal_target,
                mg.order_index
            FROM user_mission_goals umg
            JOIN mission_goals mg ON umg.goal_id = mg.id
            WHERE umg.user_mission_id = %s
            ORDER BY mg.order_index
        """
        
        try:
            with db.get_cursor() as cursor:
                cursor.execute(query, (user_mission_id,))
                rows = cursor.fetchall()
                
                goal_progress = []
                for row in rows:
                    goal_progress.append({
                        'id': str(row['id']),
                        'user_mission_id': str(row['user_mission_id']),
                        'goal_id': str(row['goal_id']),
                        'completed': row['completed'],
                        'progress': row['progress'],
                        'completed_at': row['completed_at'],
                        'created_at': row['created_at'],
                        'updated_at': row['updated_at'],
                        'goal': {
                            'id': str(row['goal_id']),
                            'description': row['goal_description'],
                            'target': row['goal_target'],
                            'order_index': row['order_index']
                        }
                    })
                
                return goal_progress
        except Exception as e:
            print(f"Error getting user mission goal progress: {e}")
            return []
    
    async def update_mission_goal_progress(
        self,
        user_mission_id: str,
        goal_id: str,
        progress_increment: int = 1
    ) -> Optional[Dict[str, Any]]:
        """
        Update progress for a specific mission goal
        
        Args:
            user_mission_id: UUID of the user_mission
            goal_id: UUID of the goal
            progress_increment: Amount to increment progress by
        
        Returns:
            Updated goal data or None if failed
        """
        try:
            with db.get_cursor(commit=True) as cursor:
                # Get goal target and current progress
                cursor.execute("""
                    SELECT mg.target, umg.progress, umg.completed
                    FROM user_mission_goals umg
                    JOIN mission_goals mg ON umg.goal_id = mg.id
                    WHERE umg.user_mission_id = %s AND umg.goal_id = %s
                """, (user_mission_id, goal_id))
                
                goal_data = cursor.fetchone()
                if not goal_data:
                    return None
                
                # Calculate new progress
                new_progress = goal_data['progress'] + progress_increment
                goal_completed = new_progress >= goal_data['target']
                
                # Update goal progress
                cursor.execute("""
                    UPDATE user_mission_goals
                    SET progress = %s,
                        completed = %s,
                        completed_at = CASE WHEN %s THEN NOW() ELSE completed_at END,
                        updated_at = NOW()
                    WHERE user_mission_id = %s AND goal_id = %s
                    RETURNING id, completed, progress, completed_at
                """, (new_progress, goal_completed, goal_completed, user_mission_id, goal_id))
                
                updated_goal = cursor.fetchone()
                
                # Check if all goals are completed
                cursor.execute("""
                    SELECT COUNT(*) as total,
                           SUM(CASE WHEN completed THEN 1 ELSE 0 END) as completed_count
                    FROM user_mission_goals
                    WHERE user_mission_id = %s
                """, (user_mission_id,))
                
                goal_stats = cursor.fetchone()
                
                # If all goals completed, mark mission as completed and award points
                if goal_stats['total'] == goal_stats['completed_count'] and goal_stats['total'] > 0:
                    cursor.execute("""
                        SELECT um.user_id, m.reward_points
                        FROM user_missions um
                        JOIN missions m ON um.mission_id = m.id
                        WHERE um.id = %s
                    """, (user_mission_id,))
                    
                    mission_info = cursor.fetchone()
                    
                    # Mark mission as completed
                    cursor.execute("""
                        UPDATE user_missions
                        SET status = 'completed',
                            progress = %s,
                            completed_at = NOW(),
                            updated_at = NOW()
                        WHERE id = %s
                    """, (goal_data['target'], user_mission_id))
                    
                    # Award points
                    if mission_info and mission_info['reward_points'] > 0:
                        cursor.execute("""
                            UPDATE user_stats
                            SET points = points + %s,
                                updated_at = NOW()
                            WHERE user_id = %s
                        """, (mission_info['reward_points'], str(mission_info['user_id'])))
                    
                    return {
                        'id': str(updated_goal['id']),
                        'completed': updated_goal['completed'],
                        'progress': updated_goal['progress'],
                        'completed_at': updated_goal['completed_at'],
                        'mission_completed': True,
                        'points_awarded': mission_info['reward_points'] if mission_info else 0
                    }
                
                return {
                    'id': str(updated_goal['id']),
                    'completed': updated_goal['completed'],
                    'progress': updated_goal['progress'],
                    'completed_at': updated_goal['completed_at'],
                    'mission_completed': False
                }
                
        except Exception as e:
            print(f"Error updating mission goal progress: {e}")
            return None
    
    async def check_mission_availability(self, user_id: str, mission_id: str) -> Dict[str, Any]:
        """
        Check if a mission is available for assignment (cooldown has passed)
        
        Args:
            user_id: UUID of the user
            mission_id: UUID of the mission to check
        
        Returns:
            Dictionary with availability status and cooldown info
        """
        try:
            with db.get_cursor() as cursor:
                # Get mission type
                cursor.execute("SELECT type FROM missions WHERE id = %s", (mission_id,))
                mission = cursor.fetchone()
                
                if not mission:
                    return {'available': False, 'reason': 'Mission not found'}
                
                # Determine cooldown based on mission type
                if mission['type'] == 'daily':
                    cooldown_interval = "INTERVAL '24 hours'"
                elif mission['type'] == 'weekly':
                    cooldown_interval = "INTERVAL '7 days'"
                elif mission['type'] == 'monthly':
                    cooldown_interval = "INTERVAL '30 days'"
                else:
                    cooldown_interval = "INTERVAL '1 hour'"
                
                # Check most recent assignment
                cursor.execute(f"""
                    SELECT 
                        id, 
                        started_at,
                        started_at + {cooldown_interval} as available_at
                    FROM user_missions
                    WHERE user_id = %s 
                    AND mission_id = %s
                    ORDER BY started_at DESC
                    LIMIT 1
                """, (user_id, mission_id))
                
                last_assignment = cursor.fetchone()
                
                if not last_assignment:
                    return {
                        'available': True,
                        'reason': 'Never assigned before',
                        'cooldown_hours': None
                    }
                
                # Check if cooldown has passed
                cursor.execute(f"""
                    SELECT 
                        CASE WHEN NOW() >= %s + {cooldown_interval}
                            THEN TRUE 
                            ELSE FALSE 
                        END as is_available,
                        EXTRACT(EPOCH FROM (%s + {cooldown_interval} - NOW())) / 3600 as hours_remaining
                """, (last_assignment['started_at'], last_assignment['started_at']))
                
                availability = cursor.fetchone()
                
                if availability['is_available']:
                    return {
                        'available': True,
                        'reason': 'Cooldown period has passed',
                        'last_assigned': last_assignment['started_at']
                    }
                else:
                    hours_remaining = max(0, availability['hours_remaining'])
                    return {
                        'available': False,
                        'reason': 'Mission is in cooldown period',
                        'last_assigned': last_assignment['started_at'],
                        'available_at': last_assignment['available_at'],
                        'hours_remaining': round(hours_remaining, 1)
                    }
                    
        except Exception as e:
            print(f"Error checking mission availability: {e}")
            return {'available': False, 'reason': f'Error: {str(e)}'}
    
    async def get_all_missions(self, mission_type: Optional[str] = None, kind: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all available missions from the missions table
        
        Args:
            mission_type: Optional filter by mission type (daily/weekly/monthly)
            kind: Optional filter by mission kind (mission/challenge/event)
        
        Returns:
            List of mission definitions
        """
        # Build query with optional filters
        where_clauses = []
        params = []
        
        if mission_type:
            where_clauses.append("type = %s")
            params.append(mission_type)
        
        if kind:
            where_clauses.append("kind = %s")
            params.append(kind)
        
        where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        
        query = f"""
            SELECT 
                id, title, description, type, category, difficulty, 
                target, reward_points, reward_achievement_id, kind,
                created_at, updated_at
            FROM missions
            {where_sql}
            ORDER BY kind, type, category, difficulty
        """
        
        try:
            with db.get_cursor() as cursor:
                cursor.execute(query, tuple(params))
                rows = cursor.fetchall()
                
                missions = []
                for row in rows:
                    mission_id = str(row['id'])
                    
                    # Get mission goals
                    mission_goals = await self.get_mission_goals(mission_id)
                    
                    missions.append({
                        'id': mission_id,
                        'title': row['title'],
                        'description': row['description'],
                        'type': row['type'],
                        'category': row['category'],
                        'difficulty': row['difficulty'],
                        'target': row['target'],
                        'reward_points': row['reward_points'],
                        'reward_achievement_id': str(row['reward_achievement_id']) if row['reward_achievement_id'] else None,
                        'kind': row.get('kind', 'mission'),
                        'goals': mission_goals,
                        'created_at': row['created_at'],
                        'updated_at': row['updated_at']
                    })
                
                return missions
        except Exception as e:
            print(f"Error getting all missions: {e}")
            return []
    
    async def update_mission_progress(
        self, 
        user_mission_id: str, 
        user_id: str, 
        progress: int
    ) -> Optional[Dict[str, Any]]:
        """
        Update progress on a mission and auto-complete if target reached
        
        Args:
            user_mission_id: UUID of the user_mission record
            user_id: UUID of the user (for security)
            progress: New progress value
        
        Returns:
            Updated user mission dictionary or None if not found
        """
        query = """
            UPDATE user_missions
            SET 
                progress = %s,
                status = CASE 
                    WHEN %s >= (SELECT target FROM missions WHERE id = mission_id) THEN 'completed'
                    ELSE status
                END,
                completed_at = CASE
                    WHEN %s >= (SELECT target FROM missions WHERE id = mission_id) THEN NOW()
                    ELSE completed_at
                END,
                updated_at = NOW()
            WHERE id = %s AND user_id = %s
            RETURNING 
                id, user_id, mission_id, status, progress,
                started_at, completed_at, expires_at,
                created_at, updated_at
        """
        
        try:
            with db.get_cursor(commit=True) as cursor:
                cursor.execute(query, (progress, progress, progress, user_mission_id, user_id))
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                # Get mission details
                mission_query = """
                    SELECT id, title, description, type, category, difficulty,
                           target, reward_points, reward_achievement_id,
                           created_at, updated_at
                    FROM missions
                    WHERE id = %s
                """
                cursor.execute(mission_query, (row['mission_id'],))
                mission_row = cursor.fetchone()
                
                # If completed, award points
                if row['status'] == 'completed' and mission_row:
                    points_query = """
                        UPDATE user_stats
                        SET points = points + %s, updated_at = NOW()
                        WHERE user_id = %s
                    """
                    cursor.execute(points_query, (mission_row['reward_points'], user_id))
                
                return {
                    'id': str(row['id']),
                    'user_id': str(row['user_id']),
                    'mission_id': str(row['mission_id']),
                    'status': row['status'],
                    'progress': row['progress'],
                    'started_at': row['started_at'],
                    'completed_at': row['completed_at'],
                    'expires_at': row['expires_at'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at'],
                    'mission': {
                        'id': str(mission_row['id']),
                        'title': mission_row['title'],
                        'description': mission_row['description'],
                        'type': mission_row['type'],
                        'category': mission_row['category'],
                        'difficulty': mission_row['difficulty'],
                        'target': mission_row['target'],
                        'reward_points': mission_row['reward_points'],
                        'reward_achievement_id': str(mission_row['reward_achievement_id']) if mission_row['reward_achievement_id'] else None,
                        'created_at': mission_row['created_at'],
                        'updated_at': mission_row['updated_at']
                    }
                } if mission_row else None
        except Exception as e:
            print(f"Error updating mission progress: {e}")
            return None
    
    async def get_mission_stats(self, user_id: str) -> Dict[str, int]:
        """
        Get mission statistics for a user
        
        Args:
            user_id: UUID of the user
        
        Returns:
            Dictionary with mission stats
        """
        query = """
            SELECT 
                COUNT(*) FILTER (WHERE status = 'active') as total_active,
                COUNT(*) FILTER (WHERE status = 'completed') as total_completed,
                COUNT(*) FILTER (WHERE status = 'expired') as total_expired
            FROM user_missions
            WHERE user_id = %s
        """
        
        points_query = """
            SELECT 
                COALESCE(SUM(m.reward_points) FILTER (
                    WHERE um.completed_at::date = CURRENT_DATE
                ), 0) as points_today,
                COALESCE(SUM(m.reward_points) FILTER (
                    WHERE um.completed_at >= CURRENT_DATE - INTERVAL '7 days'
                ), 0) as points_week,
                COALESCE(SUM(m.reward_points), 0) as points_total
            FROM user_missions um
            JOIN missions m ON um.mission_id = m.id
            WHERE um.user_id = %s AND um.status = 'completed'
        """
        
        try:
            with db.get_cursor() as cursor:
                # Get counts
                cursor.execute(query, (user_id,))
                counts = cursor.fetchone()
                
                # Get points
                cursor.execute(points_query, (user_id,))
                points = cursor.fetchone()
                
                return {
                    'total_active': counts['total_active'] if counts else 0,
                    'total_completed': counts['total_completed'] if counts else 0,
                    'total_expired': counts['total_expired'] if counts else 0,
                    'points_earned_today': int(points['points_today']) if points else 0,
                    'points_earned_week': int(points['points_week']) if points else 0,
                    'points_earned_total': int(points['points_total']) if points else 0
                }
        except Exception as e:
            print(f"Error getting mission stats: {e}")
            return {
                'total_active': 0,
                'total_completed': 0,
                'total_expired': 0,
                'points_earned_today': 0,
                'points_earned_week': 0,
                'points_earned_total': 0
            }
    
    async def assign_daily_missions(self, user_id: str) -> List[str]:
        """
        Auto-assign daily missions to a user
        Helper method to be called periodically or on user login
        
        Args:
            user_id: UUID of the user
        
        Returns:
            List of assigned mission IDs
        """
        # Get available daily missions that have passed their cooldown period
        # Cooldown is based on mission type: daily = 24 hours
        query = """
            INSERT INTO user_missions (user_id, mission_id, expires_at)
            SELECT %s, m.id, NOW() + INTERVAL '1 day'
            FROM missions m
            WHERE m.type = 'daily'
            AND NOT EXISTS (
                SELECT 1 FROM user_missions um
                WHERE um.user_id = %s 
                AND um.mission_id = m.id
                AND um.started_at > NOW() - INTERVAL '24 hours'
            )
            LIMIT 3
            RETURNING id
        """
        
        try:
            with db.get_cursor(commit=True) as cursor:
                cursor.execute(query, (user_id, user_id))
                rows = cursor.fetchall()
                return [str(row['id']) for row in rows]
        except Exception as e:
            print(f"Error assigning daily missions: {e}")
            return []
    
    async def assign_specific_mission(self, user_id: str, mission_id: str) -> Optional[Dict[str, Any]]:
        """
        Manually assign a specific mission to a user
        Missions become available again after their cooldown period:
        - daily: 24 hours
        - weekly: 7 days
        - monthly: 30 days
        
        Args:
            user_id: UUID of the user
            mission_id: UUID of the mission to assign
        
        Returns:
            The assigned user_mission record or None if failed
        """
        try:
            with db.get_cursor(commit=True) as cursor:
                # Check if mission exists and get its type
                cursor.execute("SELECT type FROM missions WHERE id = %s", (mission_id,))
                mission = cursor.fetchone()
                
                if not mission:
                    return None
                
                # Calculate expiration and cooldown based on mission type
                if mission['type'] == 'daily':
                    expires_interval = "INTERVAL '1 day'"
                    cooldown_interval = "INTERVAL '24 hours'"
                elif mission['type'] == 'weekly':
                    expires_interval = "INTERVAL '7 days'"
                    cooldown_interval = "INTERVAL '7 days'"
                elif mission['type'] == 'monthly':
                    expires_interval = "INTERVAL '30 days'"
                    cooldown_interval = "INTERVAL '30 days'"
                else:
                    expires_interval = "NULL"
                    cooldown_interval = "INTERVAL '1 hour'"  # Default 1 hour cooldown
                
                # Check if mission is still in cooldown period
                cursor.execute(f"""
                    SELECT id, started_at FROM user_missions
                    WHERE user_id = %s 
                    AND mission_id = %s
                    AND started_at > NOW() - {cooldown_interval}
                    ORDER BY started_at DESC
                    LIMIT 1
                """, (user_id, mission_id))
                
                existing = cursor.fetchone()
                if existing:
                    # Mission still in cooldown, calculate time remaining
                    return None
                
                # Insert new user_mission
                cursor.execute(f"""
                    INSERT INTO user_missions (user_id, mission_id, expires_at)
                    VALUES (%s, %s, NOW() + {expires_interval})
                    RETURNING id
                """, (user_id, mission_id))
                
                result = cursor.fetchone()
                
                if result:
                    user_mission_id = str(result['id'])
                    
                    # Check if mission has goals
                    cursor.execute("""
                        SELECT id, description, target, order_index
                        FROM mission_goals
                        WHERE mission_id = %s
                        ORDER BY order_index
                    """, (mission_id,))
                    
                    goals = cursor.fetchall()
                    
                    # Create user_mission_goals entries for each goal
                    for goal in goals:
                        cursor.execute("""
                            INSERT INTO user_mission_goals
                            (user_mission_id, goal_id, completed, progress)
                            VALUES (%s, %s, FALSE, 0)
                        """, (user_mission_id, str(goal['id'])))
                    
                    return {'id': user_mission_id, 'mission_id': mission_id, 'goals_count': len(goals)}
                
                return None
                
        except Exception as e:
            print(f"Error assigning specific mission: {e}")
            return None
