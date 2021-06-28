import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.routers import auth, users, roles
from app.sql_app import crud, schemas
from app.sql_app.database import get_db
from app.sql_app.models import User
from app.services.auth import Auth

app = FastAPI()

# CORS Orgigns allwed
origins = [
"http://localhost:3000",
    '*'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add routers
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(roles.router)


@app.on_event("startup")
async def startup_event():
    db = next(get_db())
    if crud.get_user_by_email(db=db, email="admin@admin.com"):
        return None
    crud.create_admin_user(db, email="admin@admin.com", hashed_password=Auth.get_password_hash(password="admin"))
    user = crud.get_user_by_email(db, email="admin@admin.com")
    crud.create_user_role(db, role=schemas.RoleCreate(owner_id=user.id, role="admin"))






if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
