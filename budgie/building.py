from shutil import rmtree
from .app import app
from .config import settings
import os


def build():
    os.makedirs(settings.BUILD_DIR, exist_ok=True)
    rmtree(settings.BUILD_DIR)
    app.emit('build')
