import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import models
from app.database import init_db

init_db()
