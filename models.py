from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum

class UserRole(str, enum.Enum):
    CONTRACTOR = "contractor"
    CLIENT = "client"

class FileType(str, enum.Enum):
    IMAGE = "image"
    DOCUMENT = "document"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(SQLEnum(UserRole), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    clients = relationship("Client", back_populates="contractor", foreign_keys="Client.contractor_id")
    client_profile = relationship("Client", back_populates="user", foreign_keys="Client.user_id", uselist=False)

class Client(Base):
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    contractor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # If client has login
    company_name = Column(String)
    contact_name = Column(String, nullable=False)
    contact_email = Column(String)
    contact_phone = Column(String)
    address = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    contractor = relationship("User", back_populates="clients", foreign_keys=[contractor_id])
    user = relationship("User", back_populates="client_profile", foreign_keys=[user_id])
    projects = relationship("Project", back_populates="client", cascade="all, delete-orphan")

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    status = Column(String, default="active")
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    client = relationship("Client", back_populates="projects")
    files = relationship("ProjectFile", back_populates="project", cascade="all, delete-orphan")

class ProjectFile(Base):
    __tablename__ = "project_files"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    file_name = Column(String, nullable=False)
    file_type = Column(SQLEnum(FileType), nullable=False)
    file_size = Column(Integer)  # bytes
    storage_key = Column(String, nullable=False)  # S3 key
    storage_url = Column(String)
    mime_type = Column(String)
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    project = relationship("Project", back_populates="files")
    uploader = relationship("User")