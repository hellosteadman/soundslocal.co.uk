from shutil import rmtree
from . import settings
from .app import app
import os


def build():
    os.makedirs(settings.BUILD_DIR, exist_ok=True)
    rmtree(settings.BUILD_DIR)
    app.emit('build')
