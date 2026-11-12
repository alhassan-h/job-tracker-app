import os
import sys

# Ensure project root is included in sys.path for serverless imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

# Vercel Serverless Function entry point
app = app

