# PURPOSE: Entry point for production deployment (Railway, etc.)
# Sets up paths and runs uvicorn with correct imports

import os
import sys

# Add backend to path so imports work
backend_dir = os.path.join(os.path.dirname(__file__), "backend")
sys.path.insert(0, backend_dir)

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
