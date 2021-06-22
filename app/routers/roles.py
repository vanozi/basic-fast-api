from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.services.auth import RoleChecker
from app.sql_app import crud, schemas
from app.sql_app.database import get_db

router = APIRouter(
    prefix="/roles",
    tags=["roles"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=schemas.Role, dependencies=[Depends(RoleChecker(['admin']))])
def create_user_role(role: schemas.RoleCreate, db: Session = Depends(get_db)):
    return crud.create_user_role(db=db, role=role)
