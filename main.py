from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routes import auth_routes, client_routes, project_routes, file_routes, user_routes

# Create database tables
#Base.metadata.create_all(bind=engine)

app = FastAPI(title="Contractor Portal API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_routes.router)
app.include_router(client_routes.router)
app.include_router(project_routes.router)
app.include_router(file_routes.router)
app.include_router(user_routes.router)

@app.get("/")
def root():
    return {"message": "Contractor Portal API"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)