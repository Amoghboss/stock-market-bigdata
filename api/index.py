import os
import sys
from pathlib import Path

# Resolve project root (parent directory of api/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Tell backend it's running in Vercel serverless environment
os.environ["VERCEL"] = "1"
os.environ["FLASK_DEBUG"] = "False"

from backend.app import app

# Export WSGI application for Vercel
# Vercel's Python runtime requires 'app'
