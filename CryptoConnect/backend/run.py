#!/usr/bin/env python3
"""
CryptoConnect FastAPI Backend Runner
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import uvicorn
from app.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )