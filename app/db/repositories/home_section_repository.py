"""
Home Sections Repository
Database operations for managing home screen sections
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
from app.core.database import db
from app.models.home_section import SECTION_TEMPLATES, get_default_user_sections


class HomeSectionRepository:
    """Repository for home sections"""
    
    db = db
    
    # ==================== CRUD Operations ====================
    
    @staticmethod
    def create_section(user_id: Optional[str], section_data: dict) -> Optional[dict]:
        """Create a home section (user-specific or global)"""
        try:
            with HomeSectionRepository.db.get_cursor(commit=True) as cursor:
                # Prepare params with defaults for optional fields
                params = {
                    'user_id': user_id,
                    'type': section_data['type'],
                    'title': section_data['title'],
                    'subtitle': section_data.get('subtitle', ''),
                    'visible': section_data.get('visible', True),
                    'order_index': section_data.get('order_index', 0),
                    'data': json.dumps(section_data.get('data', {}))
                }
                
                cursor.execute("""
                    INSERT INTO home_sections 
                        (user_id, type, title, subtitle, visible, order_index, data)
                    VALUES 
                        (%(user_id)s, %(type)s, %(title)s, %(subtitle)s, 
                         %(visible)s, %(order_index)s, %(data)s)
                    RETURNING id, user_id, type, title, subtitle, visible, 
                              order_index, data, created_at, updated_at
                """, params)
                
                row = cursor.fetchone()
                if row:
                    result = dict(row)
                    # Convert data from JSON if needed
                    if result.get('data') and isinstance(result['data'], str):
                        result['data'] = json.loads(result['data'])
                    return result
                return None
        except Exception as e:
            print(f"Error creating section: {e}")
            return None
    
    @staticmethod
    def get_section(section_id: str, user_id: Optional[str] = None) -> Optional[dict]:
        """Get a single section by ID"""
        try:
            with HomeSectionRepository.db.get_cursor() as cursor:
                # If user_id provided, ensure section belongs to user or is global
                user_filter = ""
                if user_id:
                    user_filter = "AND (user_id = %(user_id)s OR user_id IS NULL)"
                
                query = f"""
                    SELECT id, user_id, type, title, subtitle, visible,
                           order_index, data, created_at, updated_at
                    FROM home_sections
                    WHERE id = %(section_id)s {user_filter}
                """
                
                cursor.execute(query, {"section_id": section_id, "user_id": user_id})
                
                row = cursor.fetchone()
                if row:
                    result = dict(row)
                    if result.get('data') and isinstance(result['data'], str):
                        import json
                        result['data'] = json.loads(result['data'])
                    return result
                return None
        except Exception as e:
            print(f"Error fetching section: {e}")
            return None
    
    @staticmethod
    def get_user_sections(user_id: str, include_global: bool = True,
                         visible_only: bool = False) -> List[dict]:
        """
        Get all sections for a user
        
        Args:
            user_id: User ID
            include_global: Include global sections (user_id IS NULL)
            visible_only: Only return visible sections
        """
        try:
            with HomeSectionRepository.db.get_cursor() as cursor:
                # Build query conditions
                conditions = []
                
                if include_global:
                    conditions.append("(user_id = %(user_id)s OR user_id IS NULL)")
                else:
                    conditions.append("user_id = %(user_id)s")
                
                if visible_only:
                    conditions.append("visible = true")
                
                where_clause = " AND ".join(conditions)
                
                query = f"""
                    SELECT id, user_id, type, title, subtitle, visible,
                           order_index, data, created_at, updated_at
                    FROM home_sections
                    WHERE {where_clause}
                    ORDER BY order_index ASC, created_at ASC
                """
                
                cursor.execute(query, {"user_id": user_id})
                
                rows = cursor.fetchall()
                results = []
                for row in rows:
                    result = dict(row)
                    if result.get('data') and isinstance(result['data'], str):
                        import json
                        result['data'] = json.loads(result['data'])
                    results.append(result)
                return results
        except Exception as e:
            print(f"Error fetching user sections: {e}")
            return []
    
    @staticmethod
    def get_global_sections(visible_only: bool = False) -> List[dict]:
        """Get all global sections (user_id IS NULL)"""
        try:
            with HomeSectionRepository.db.get_cursor() as cursor:
                visible_filter = "AND visible = true" if visible_only else ""
                
                query = f"""
                    SELECT id, user_id, type, title, subtitle, visible,
                           order_index, data, created_at, updated_at
                    FROM home_sections
                    WHERE user_id IS NULL {visible_filter}
                    ORDER BY order_index ASC, created_at ASC
                """
                
                cursor.execute(query)
                
                rows = cursor.fetchall()
                results = []
                for row in rows:
                    result = dict(row)
                    if result.get('data') and isinstance(result['data'], str):
                        import json
                        result['data'] = json.loads(result['data'])
                    results.append(result)
                return results
        except Exception as e:
            print(f"Error fetching global sections: {e}")
            return []
    
    @staticmethod
    def update_section(section_id: str, user_id: Optional[str], updates: dict) -> Optional[dict]:
        """Update a home section"""
        try:
            allowed_fields = ['type', 'title', 'subtitle', 'visible', 'order_index', 'data']
            set_parts = []
            values = {}
            
            for field in allowed_fields:
                if field in updates and updates[field] is not None:
                    set_parts.append(f"{field} = %({field})s")
                    # JSON serialize data field if it's a dict
                    if field == 'data' and isinstance(updates[field], dict):
                        values[field] = json.dumps(updates[field])
                    else:
                        values[field] = updates[field]
            
            if not set_parts:
                return None
            
            set_parts.append("updated_at = NOW()")
            set_clause = ", ".join(set_parts)
            values['section_id'] = section_id
            
            # Permission check
            if user_id:
                # User can only update their own sections
                user_check = "AND user_id = %(user_id)s"
                values['user_id'] = user_id
            else:
                # Admin updating global sections
                user_check = "AND user_id IS NULL"
            
            with HomeSectionRepository.db.get_cursor(commit=True) as cursor:
                query = f"""
                    UPDATE home_sections
                    SET {set_clause}
                    WHERE id = %(section_id)s {user_check}
                    RETURNING id, user_id, type, title, subtitle, visible,
                              order_index, data, created_at, updated_at
                """
                
                cursor.execute(query, values)
                
                row = cursor.fetchone()
                if row:
                    result = dict(row)
                    if result.get('data') and isinstance(result['data'], str):
                        result['data'] = json.loads(result['data'])
                    return result
                return None
        except Exception as e:
            print(f"Error updating section: {e}")
            return None
    
    @staticmethod
    def delete_section(section_id: str, user_id: Optional[str]) -> bool:
        """Delete a home section"""
        try:
            # Permission check
            if user_id:
                user_check = "AND user_id = %s"
                params = (section_id, user_id)
            else:
                user_check = "AND user_id IS NULL"
                params = (section_id,)
            
            with HomeSectionRepository.db.get_cursor(commit=True) as cursor:
                cursor.execute(f"""
                    DELETE FROM home_sections
                    WHERE id = %s {user_check}
                """, params)
                
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting section: {e}")
            return False
    
    @staticmethod
    def toggle_visibility(section_id: str, user_id: str) -> Optional[dict]:
        """Toggle section visibility"""
        try:
            with HomeSectionRepository.db.get_cursor(commit=True) as cursor:
                cursor.execute("""
                    UPDATE home_sections
                    SET visible = NOT visible, updated_at = NOW()
                    WHERE id = %s AND user_id = %s
                    RETURNING id, user_id, type, title, subtitle, visible,
                              order_index, data, created_at, updated_at
                """, (section_id, user_id))
                
                row = cursor.fetchone()
                if row:
                    result = dict(row)
                    if result.get('data') and isinstance(result['data'], str):
                        import json
                        result['data'] = json.loads(result['data'])
                    return result
                return None
        except Exception as e:
            print(f"Error toggling visibility: {e}")
            return None
    
    @staticmethod
    def reorder_sections(user_id: str, section_orders: List[Dict[str, Any]]) -> bool:
        """
        Bulk reorder sections
        
        Args:
            user_id: User ID
            section_orders: List of {"section_id": str, "new_order_index": int}
        """
        try:
            with HomeSectionRepository.db.get_cursor(commit=True) as cursor:
                for order_update in section_orders:
                    section_id = order_update.get('section_id')
                    new_order = order_update.get('new_order_index')
                    
                    if section_id is not None and new_order is not None:
                        cursor.execute("""
                            UPDATE home_sections
                            SET order_index = %s, updated_at = NOW()
                            WHERE id = %s AND user_id = %s
                        """, (new_order, section_id, user_id))
                
                return True
        except Exception as e:
            print(f"Error reordering sections: {e}")
            return False
    
    # ==================== Section Initialization ====================
    
    @staticmethod
    def initialize_user_sections(user_id: str) -> List[dict]:
        """Create default sections for a new user"""
        try:
            default_sections = get_default_user_sections()
            created_sections = []
            
            for section_template in default_sections:
                section = HomeSectionRepository.create_section(
                    user_id=user_id,
                    section_data=section_template
                )
                if section:
                    created_sections.append(section)
            
            return created_sections
        except Exception as e:
            print(f"Error initializing user sections: {e}")
            return []
    
    @staticmethod
    def reset_to_defaults(user_id: str) -> List[dict]:
        """Delete all user sections and recreate defaults"""
        try:
            with HomeSectionRepository.db.get_cursor(commit=True) as cursor:
                # Delete existing user sections
                cursor.execute("""
                    DELETE FROM home_sections
                    WHERE user_id = %s
                """, (user_id,))
            
            # Create defaults
            return HomeSectionRepository.initialize_user_sections(user_id)
        except Exception as e:
            print(f"Error resetting sections: {e}")
            return []
    
    @staticmethod
    def create_section_from_template(user_id: str, template_key: str) -> Optional[dict]:
        """Create a section from a template"""
        try:
            if template_key not in SECTION_TEMPLATES:
                print(f"Template '{template_key}' not found")
                return None
            
            template = SECTION_TEMPLATES[template_key].copy()
            
            # Get max order_index for user and add 1
            with HomeSectionRepository.db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT COALESCE(MAX(order_index), -1) + 1 as next_order
                    FROM home_sections
                    WHERE user_id = %s
                """, (user_id,))
                
                row = cursor.fetchone()
                next_order = row['next_order'] if row else 0
            
            # Override order_index
            template['order_index'] = next_order
            
            return HomeSectionRepository.create_section(
                user_id=user_id,
                section_data=template
            )
        except Exception as e:
            print(f"Error creating section from template: {e}")
            return None
    
    @staticmethod
    def get_available_templates() -> List[Dict[str, Any]]:
        """Get list of available section templates"""
        return [
            {
                "key": key,
                "type": template["type"],
                "title": template["title"],
                "subtitle": template.get("subtitle", ""),
                "default_data": template.get("data", {})
            }
            for key, template in SECTION_TEMPLATES.items()
        ]
