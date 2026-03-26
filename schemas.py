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

class User(UserBase):
    id: int
    created_at: datetime
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
    contact_name: str
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None

class ClientCreate(ClientBase):
    user_id: Optional[int] = None

class Client(ClientBase):
    id: int
    contractor_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# Project Schemas
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: Optional[str] = "active"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class ProjectCreate(ProjectBase):
    client_id: int

class Project(ProjectBase):
    id: int
    client_id: int
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