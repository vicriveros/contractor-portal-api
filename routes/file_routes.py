from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from database import get_db
from models import User, Project, ProjectFile, Client, FileType
from schemas import ProjectFile as ProjectFileSchema
from auth import get_current_user, get_current_contractor
from storage_service import storage_service
from config import settings

router = APIRouter(prefix="/files", tags=["Files"])

@router.post("/{project_id}/upload", response_model=ProjectFileSchema)
async def upload_file(
    project_id: int,
    file: UploadFile = File(...),
    description: str = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_contractor)
):
    # Verify project exists and belongs to contractor
    project = db.query(Project).join(Client).filter(
        Project.id == project_id,
        Client.contractor_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Validate file
    file_extension = file.filename.split('.')[-1].lower()
    if file_extension in settings.allowed_image_extensions_list:
        file_type = FileType.IMAGE
    elif file_extension in settings.allowed_document_extensions_list:
        file_type = FileType.DOCUMENT
    else:
        raise HTTPException(status_code=400, detail="File type not allowed")
    
    # Read file content
    file_content = await file.read()
    if len(file_content) > settings.max_file_size_bytes:
        raise HTTPException(status_code=400, detail="File too large")
    
    # Upload to storage
    storage_key, storage_url = storage_service.upload_file(
        file_content=file_content,
        file_name=file.filename,
        content_type=file.content_type
    )
    
    # Save to database
    db_file = ProjectFile(
        project_id=project_id,
        file_name=file.filename,
        file_type=file_type,
        file_size=len(file_content),
        storage_key=storage_key,
        storage_url=storage_url,
        mime_type=file.content_type,
        uploaded_by=current_user.id,
        description=description
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    
    return db_file

@router.get("/{project_id}/files", response_model=List[ProjectFileSchema])
def list_files(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get files and generate presigned URLs
    files = db.query(ProjectFile).filter(ProjectFile.project_id == project_id).all()
    
    # Add presigned URLs
    for file in files:
        file.presigned_url = storage_service.generate_presigned_url(file.storage_key)
    
    return files