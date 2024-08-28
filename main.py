from fastapi import FastAPI
import models
from database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware
from routes import user, category, consume_hist, budget,total, mail
from auth import login
from scheduler import start_scheduler, stop_scheduler
from contextlib import asynccontextmanager
import uvicorn


models.Base.metadata.create_all(bind=engine)


origins = [
    "http://localhost:44103",
]

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    stop_scheduler()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"], 
    
)

app.include_router(user.router, prefix="/users", tags=["users"])
app.include_router(category.router, prefix="/category", tags=["category"])
app.include_router(consume_hist.router, prefix="/consume.history", tags=["consume.history"])
app.include_router(budget.router, prefix="/budgets", tags=["budget"])
app.include_router(total.router, prefix="/total", tags=["total"])
app.include_router(login.router, tags=["login"])
app.include_router(mail.router, prefix="/mail", tags=["mail"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the API"}

if __name__ == "__main__" :
	uvicorn.run("main:app", reload=True)