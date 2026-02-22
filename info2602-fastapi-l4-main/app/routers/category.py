from fastapi import APIRouter, HTTPException
from sqlmodel import select
from app.database import SessionDep
from app.models import *
from app.auth import AuthDep
from fastapi import status

category_router = APIRouter(tags=["Category Management"])

@category_router.post('/category', status_code=status.HTTP_201_CREATED)
def create_category(db: SessionDep, user: AuthDep, category_data: dict):
    """Creates a category for the CURRENT LOGGED IN user"""
    try:
        category = Category(text=category_data['text'], user_id=user.id)
        db.add(category)
        db.commit()
        db.refresh(category)
        return category
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Could not create category"
        )

@category_router.post('/todo/{todo_id}/category/{cat_id}')
def add_category_to_todo(todo_id: int, cat_id: int, db: SessionDep, user: AuthDep):
    """Assigns the category cat_id to the todo todo_id if the user is authorized to access it"""
    # Verify todo exists and belongs to user
    todo = db.exec(select(Todo).where(Todo.id == todo_id, Todo.user_id == user.id)).one_or_none()
    if not todo:
        raise HTTPException(
            status_code=404,
            detail="Todo not found"
        )
    
    # Verify category exists and belongs to user
    category = db.exec(select(Category).where(Category.id == cat_id, Category.user_id == user.id)).one_or_none()
    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )
    
    # Check if association already exists
    existing = db.exec(
        select(TodoCategory).where(
            TodoCategory.todo_id == todo_id, 
            TodoCategory.category_id == cat_id
        )
    ).one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Category already assigned to this todo"
        )
    
    # Create the association
    try:
        todo_category = TodoCategory(todo_id=todo_id, category_id=cat_id)
        db.add(todo_category)
        db.commit()
        return {"message": "Category added to todo"}
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=503,
            detail="An error occurred"
        )

@category_router.delete('/todo/{todo_id}/category/{cat_id}')
def remove_category_from_todo(todo_id: int, cat_id: int, db: SessionDep, user: AuthDep):
    """Removes the category cat_id from the todo todo_id"""
    # Verify todo exists and belongs to user
    todo = db.exec(select(Todo).where(Todo.id == todo_id, Todo.user_id == user.id)).one_or_none()
    if not todo:
        raise HTTPException(
            status_code=404,
            detail="Todo not found"
        )
    
    # Find and delete the association
    todo_category = db.exec(
        select(TodoCategory).where(
            TodoCategory.todo_id == todo_id, 
            TodoCategory.category_id == cat_id
        )
    ).one_or_none()
    
    if not todo_category:
        raise HTTPException(
            status_code=404,
            detail="Category not assigned to this todo"
        )
    
    try:
        db.delete(todo_category)
        db.commit()
        return {"message": "Category removed from todo"}
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=503,
            detail="An error occurred"
        )

@category_router.get('/category/{cat_id}/todos')
def get_todos_for_category(cat_id: int, db: SessionDep, user: AuthDep):
    """Retrieves ALL todos for the category cat_id for the CURRENT LOGGED IN user"""
    # Verify category exists and belongs to user
    category = db.exec(
        select(Category).where(Category.id == cat_id, Category.user_id == user.id)
    ).one_or_none()
    
    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )
    
    return category