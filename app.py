from fastapi import FastAPI
from backend.routes import router

app = FastAPI(title="ResolveAI Backend")

# Plug in all the endpoints defined in backend/routes.py
app.include_router(router)

@app.get("/")
def health_check():
    return {"status": "ResolveAI backend is running"}

