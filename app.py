"""
Hugging Face Spaces entry point
"""
from main import app

# HF Spaces Docker looks for 'app' variable in app.py
__all__ = ['app']

