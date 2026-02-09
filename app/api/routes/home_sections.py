"""
Home Sections API Routes
Endpoints for managing dynamic home screen sections
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from app.models.home_section import (
    HomeSectionCreate,
    HomeSectionUpdate,
    HomeSectionResponse,
    BulkReorderSections
)
from app.db.repositories.home_section_repository import HomeSectionRepository
from app.core.security import get_current_user

router = APIRouter(prefix="/api/home-sections", tags=["home-sections"])


@router.get("/", response_model=List[HomeSectionResponse])
def get_home_sections(
    include_global: bool = Query(True, description="Include global sections"),
    visible_only: bool = Query(False, description="Only visible sections"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all home sections for the current user
    
    Returns both user-specific sections and global sections (if included).
    Sections are returned in display order (order_index ASC).
    """
    user_id = current_user.get("id") or current_user.get("user_id")
    
    sections = HomeSectionRepository.get_user_sections(
        user_id=user_id,
        include_global=include_global,
        visible_only=visible_only
    )
    
    return sections


@router.get("/global", response_model=List[HomeSectionResponse])
def get_global_sections(
    visible_only: bool = Query(False, description="Only visible sections"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all global sections (available to all users)
    
    Global sections have user_id = NULL and are typically admin-created.
    """
    sections = HomeSectionRepository.get_global_sections(visible_only=visible_only)
    return sections


@router.get("/templates")
def get_section_templates(current_user: dict = Depends(get_current_user)):
    """
    Get available section templates
    
    Returns a list of predefined section templates that can be added to the home screen.
    """
    templates = HomeSectionRepository.get_available_templates()
    return {"templates": templates}


@router.post("/from-template/{template_key}", response_model=HomeSectionResponse)
def create_section_from_template(
    template_key: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new section from a template
    
    - **template_key**: Key of the template (e.g., "stats", "achievements", "suggestions")
    
    The section will be added at the end of the user's section list.
    """
    user_id = current_user.get("id") or current_user.get("user_id")
    
    section = HomeSectionRepository.create_section_from_template(
        user_id=user_id,
        template_key=template_key
    )
    
    if not section:
        raise HTTPException(status_code=404, detail=f"Template '{template_key}' not found")
    
    return section


@router.post("/initialize", response_model=List[HomeSectionResponse])
def initialize_sections(current_user: dict = Depends(get_current_user)):
    """
    Initialize default home sections for the user
    
    Creates a set of default sections if the user doesn't have any.
    This is typically called once when a user first accesses the home screen.
    """
    user_id = current_user.get("id") or current_user.get("user_id")
    
    # Check if user already has sections
    existing = HomeSectionRepository.get_user_sections(
        user_id=user_id,
        include_global=False
    )
    
    if existing:
        return {"message": "User already has sections", "sections": existing}
    
    # Create defaults
    sections = HomeSectionRepository.initialize_user_sections(user_id=user_id)
    
    return sections


@router.post("/reset", response_model=List[HomeSectionResponse])
def reset_to_defaults(current_user: dict = Depends(get_current_user)):
    """
    Reset home sections to defaults
    
    Deletes all user-specific sections and recreates the default set.
    Global sections are not affected.
    """
    user_id = current_user.get("id") or current_user.get("user_id")
    
    sections = HomeSectionRepository.reset_to_defaults(user_id=user_id)
    
    return sections


@router.get("/{section_id}", response_model=HomeSectionResponse)
def get_section(
    section_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get a specific home section by ID
    
    Returns the section if it belongs to the user or is a global section.
    """
    user_id = current_user.get("id") or current_user.get("user_id")
    
    section = HomeSectionRepository.get_section(
        section_id=section_id,
        user_id=user_id
    )
    
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    
    return section


@router.post("/", response_model=HomeSectionResponse)
def create_section(
    section: HomeSectionCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new custom home section
    
    Creates a user-specific section with custom configuration.
    """
    user_id = current_user.get("id") or current_user.get("user_id")
    
    created_section = HomeSectionRepository.create_section(
        user_id=user_id,
        section_data=section.model_dump(exclude_unset=True)
    )
    
    if not created_section:
        raise HTTPException(status_code=500, detail="Failed to create section")
    
    return created_section


@router.patch("/{section_id}", response_model=HomeSectionResponse)
def update_section(
    section_id: str,
    updates: HomeSectionUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update a home section
    
    Allows updating section properties like title, visibility, order, and data.
    """
    user_id = current_user.get("id") or current_user.get("user_id")
    
    section = HomeSectionRepository.update_section(
        section_id=section_id,
        user_id=user_id,
        updates=updates.model_dump(exclude_unset=True)
    )
    
    if not section:
        raise HTTPException(status_code=404, detail="Section not found or access denied")
    
    return section


@router.patch("/{section_id}/toggle-visibility", response_model=HomeSectionResponse)
def toggle_section_visibility(
    section_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Toggle section visibility
    
    Quick toggle between visible and hidden states.
    """
    user_id = current_user.get("id") or current_user.get("user_id")
    
    section = HomeSectionRepository.toggle_visibility(
        section_id=section_id,
        user_id=user_id
    )
    
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    
    return section


@router.post("/reorder")
def reorder_sections(
    reorder_data: BulkReorderSections,
    current_user: dict = Depends(get_current_user)
):
    """
    Reorder multiple sections at once
    
    - **sections**: List of {section_id, new_order_index} objects
    
    This allows dragging sections to reorder them in the UI.
    All sections in the list will be updated with their new order_index values.
    """
    user_id = current_user.get("id") or current_user.get("user_id")
    
    section_orders = [
        {
            "section_id": item.section_id,
            "new_order_index": item.new_order_index
        }
        for item in reorder_data.sections
    ]
    
    success = HomeSectionRepository.reorder_sections(
        user_id=user_id,
        section_orders=section_orders
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to reorder sections")
    
    return {"message": f"Reordered {len(section_orders)} sections successfully"}


@router.delete("/{section_id}")
def delete_section(
    section_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a home section
    
    Permanently removes the section from the user's home screen.
    """
    user_id = current_user.get("id") or current_user.get("user_id")
    
    success = HomeSectionRepository.delete_section(
        section_id=section_id,
        user_id=user_id
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Section not found or access denied")
    
    return {"message": "Section deleted successfully"}
