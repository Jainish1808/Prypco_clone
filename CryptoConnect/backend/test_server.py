#!/usr/bin/env python3
"""
Very simple test server
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/user")
def get_user():
    return {"id": "1", "username": "testuser", "email": "test@example.com"}

@app.post("/api/login")
def login():
    return {"message": "Login successful", "user": {"id": "1", "username": "testuser"}}

@app.post("/api/register")
def register():
    return {"message": "Registration successful", "user": {"id": "1", "username": "testuser"}}

@app.get("/api/properties")
def get_properties():
    return [{"id": "1", "name": "Test Property", "status": "approved"}]

if __name__ == "__main__":
    import uvicorn
    print("Starting test server on http://127.0.0.1:8002")
    uvicorn.run(app, host="127.0.0.1", port=8002)