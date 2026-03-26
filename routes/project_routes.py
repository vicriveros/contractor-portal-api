from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, Client, Project
from schemas import ProjectCreate, Project as ProjectSchema
from auth import get_current_contractor

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.post("/", response_model=ProjectSchema, status_code=201)
def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_contractor)
):
    # Verify client belongs to contractor
    client = db.query(Client).filter(
        Client.id == project_data.client_id,
        Client.contractor_id == current_user.id
    ).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    db_project = Project(**project_data.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.get("/", response_model=List[ProjectSchema])
def list_projects(
    client_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_contractor)
):
    query = db.query(Project).join(Client).filter(Client.contractor_id == current_user.id)
    if client_id:
        query = query.filter(Project.client_id == client_id)
    return query.all()