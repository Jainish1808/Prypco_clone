#!/usr/bin/env python3
"""
Simple FastAPI Backend Runner for CryptoConnect
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="CryptoConnect API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "CryptoConnect API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/user")
async def get_user():
    return {"message": "User endpoint working"}

@app.post("/api/register")
async def register():
    return {"message": "Register endpoint working"}

@app.post("/api/login")
async def login():
    return {"message": "Login endpoint working"}

@app.post("/api/logout")
async def logout():
    return {"message": "Logout endpoint working"}

@app.get("/api/properties")
async def get_properties():
    return [
        {
            "id": "1",
            "name": "Sample Property",
            "description": "A sample property for testing",
            "address": "123 Test St",
            "propertyType": "residential",
            "propertyValue": 1000000,
            "propertySize": 100,
            "expectedYield": 5.0,
            "totalTokens": 1000000,
            "tokenPrice": 1.0,
            "tokensAvailable": 1000000,
            "tokensSold": 0,
            "status": "approved",
            "images": [],
            "documents": [],
            "createdAt": "2024-01-01T00:00:00Z"
        }
    ]

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting CryptoConnect Backend on http://127.0.0.1:8001")
    print("Press Ctrl+C to stop")
    try:
        uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")
    except KeyboardInterrupt:
        print("👋 Backend stopped")