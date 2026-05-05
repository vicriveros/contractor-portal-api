from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime
from models import UserRole, FileType

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    role: UserRole

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    password: Optional[str] = None

class User(UserBase):
    id: int
    created_at: datetime
    client_profile: Optional[Client] = None
    model_config = ConfigDict(from_attributes=True)

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Client Schemas
class ClientBase(BaseModel):
    company_name: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None

class ClientCreate(ClientBase):
    contact_name: str
    user_id: Optional[int] = None

class ClientUpdate(ClientBase):
    pass
    
class Client(ClientBase):
    id: int
    contractor_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# Project Schemas
class ProjectBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = "active"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    advisor: Optional[str] = None
    advisor_email: Optional[str] = None
    advisor_phone: Optional[str] = None
    project_manager: Optional[str] = None


class ProjectCreate(ProjectBase):
    client_id: int
    name: str

class ProjectUpdate(ProjectBase):
    client_id: Optional[int] = None
    pass

class Project(ProjectBase):
    id: int
    client_id: int
    # para que Pydantic muestre la info de cliente al listar proyectos
    client: Optional[ClientBase] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# File Schemas
class ProjectFileBase(BaseModel):
    file_name: str
    file_type: FileType
    description: Optional[str] = None

class ProjectFile(ProjectFileBase):
    id: int
    project_id: int
    file_size: Optional[int] = None
    storage_key: str
    created_at: datetime
    presigned_url: Optional[str] = None  # Generated dynamically
    model_config = ConfigDict(from_attributes=True)