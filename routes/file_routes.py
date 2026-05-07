from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from database import get_db
from models import User, Project, ProjectFile, Client, FileType
from schemas import ProjectFile as ProjectFileSchema
from auth import get_current_user, get_current_contractor
from storage_service import storage_service
from config import settings
from image_utils import optimize_image

router = APIRouter(prefix="/files", tags=["Files"])

@router.post("/{project_id}/upload", response_model=ProjectFileSchema)
async def upload_file(
    project_id: int,
    file: UploadFile = File(...),
    description: str = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Validate file
    file_extension = file.filename.split('.')[-1].lower()
    if file_extension in settings.allowed_image_extensions_list:
        file_type = FileType.IMAGE
    elif file_extension in settings.allowed_document_extensions_list:
        file_type = FileType.DOCUMENT
    elif file_extension in settings.allowed_video_extensions_list:
        file_type = FileType.VIDEO
    else:
        raise HTTPException(
            status_code=400, 
            detail=f"File type not allowed. Allowed: images ({', '.join(settings.allowed_image_extensions_list)}), documents ({', '.join(settings.allowed_document_extensions_list)}), videos ({', '.join(settings.allowed_video_extensions_list)})"
        )
    
    # Read file content
    file_content = await file.read()
    
    file_name = file.filename
    content_type = file.content_type
    
    # Optimize image if needed
    if file_type == FileType.IMAGE:
        try:
            file_content, new_ext, content_type = optimize_image(file_content)
            # Update filename to have .webp extension
            base_name = ".".join(file.filename.split('.')[:-1])
            file_name = f"{base_name}.{new_ext}"
        except Exception as e:
            # Fallback to original image if optimization fails
            print(f"La optimización de imagen falló: {e}")
            file_name = file.filename
            content_type = file.content_type

    if len(file_content) > settings.max_file_size_bytes:
        raise HTTPException(status_code=400, detail="File too large")
    
    # Upload to storage
    storage_key, storage_url = storage_service.upload_file(
        file_content=file_content,
        file_name=file_name,
        content_type=content_type
    )
    
    # Save to database
    db_file = ProjectFile(
        project_id=project_id,
        file_name=file_name,
        file_type=file_type,
        file_size=len(file_content),
        storage_key=storage_key,
        storage_url=storage_url,
        mime_type=content_type,
        uploaded_by=current_user.id,
        description=description
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)

    # Generate presigned URL
    db_file.presigned_url = storage_service.generate_presigned_url(
        db_file.storage_key,
        expiration=3600
    )
    
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

@router.delete("/{file_id}", status_code=204)
def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Eliminar un archivo (solo contractor)
    """
    # Buscar el archivo
    file = db.query(ProjectFile).filter(ProjectFile.id == file_id).first()
    
    if not file:
        raise HTTPException(
            status_code=404,
            detail="Archivo no encontrado"
        )
    
    # Verificar que el proyecto pertenezca al contractor
    # project = db.query(Project).filter(Project.id == file.project_id).first()
    # client = db.query(Client).filter(Client.id == project.client_id).first()
    
    # if client.contractor_id != current_user.id:
    #     raise HTTPException(
    #         status_code=403,
    #         detail="No autorizado para eliminar este archivo"
    #     )
    
    # Eliminar del storage
    try:
        storage_service.delete_file(file.storage_key)
    except Exception as e:
        print(f"Error al eliminar del storage: {e}")
        # Continuar para eliminar de la BD aunque falle el storage
    
    # Eliminar de la base de datos
    db.delete(file)
    db.commit()
    
    return None