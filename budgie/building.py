from shutil import rmtree
from .app import app
from .config import settings
import os


def build_site():
    os.makedirs(settings.BUILD_DIR, exist_ok=True)
    rmtree(settings.BUILD_DIR)
    app.emit('build')


def build_page(path, content):
    path_parts = path.split('/')
    while any(path_parts) and not path_parts[-1]:
        path_parts.pop()

    dirname = os.path.join(settings.BUILD_DIR, *path_parts)
    filename = os.path.join(dirname, 'index.html')
    os.makedirs(dirname, exist_ok=True)

    with open(filename, 'w') as f:
        f.write(content)

    app.emit(
        'built',
        path=os.path.join(*path_parts),
        filename=filename
    )
