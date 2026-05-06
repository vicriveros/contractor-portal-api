from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User, Client
from schemas import ClientCreate, ClientUpdate, Client as ClientSchema
from auth import get_current_contractor, get_current_user

router = APIRouter(prefix="/clients", tags=["Clients"])

@router.post("/", response_model=ClientSchema, status_code=201)
def create_client(
    client_data: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_contractor)
):
    db_client = Client(
        contractor_id=current_user.id,
        **client_data.model_dump()
    )
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

@router.get("/", response_model=List[ClientSchema])
def list_clients(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Client).all()

@router.get("/{client_id}", response_model=ClientSchema)
def get_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@router.patch("/{client_id}", response_model=ClientSchema, status_code=201)
def update_client(
    client_id: int,
    client_data: ClientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    update_data = client_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(client, key, value)

    db.add(client)
    db.commit()
    db.refresh(client)
    return client

@router.delete("/{client_id}", status_code=204)
def delete_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    db.delete(client)
    db.commit()
    return {"message": "Client deleted successfully"}