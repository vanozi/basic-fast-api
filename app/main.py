from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from pathlib import Path
from app.routers import users, auth, roles

app = FastAPI()

# CORS Orgigns allwed
origins = [
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

if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=8000)