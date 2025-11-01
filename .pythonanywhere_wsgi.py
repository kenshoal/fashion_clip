# PythonAnywhere WSGI configuration
import sys
import os

# Add your project directory to the path
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.insert(0, path)

# Import your FastAPI app
from main import app

# PythonAnywhere expects 'application'
application = app

