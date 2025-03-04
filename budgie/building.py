from shutil import rmtree
from . import settings
from .app import app
from .models import ModelBase, Page, Post
from .request import Request
from .templates import Template
import os


def build_obj(obj: ModelBase, template_name: str = None):
    slug = obj.slug

    if template_name is None:
        template_name = [type(obj).__name__.lower() + '_detail.html']

        if isinstance(obj, Page) and obj.slug == 'index':
            template_name.insert(0, 'index.html')
            slug = ''

    template = Template(template_name)
    context = {
        'object': obj,
        'request': Request('/%s/' % slug)
    }

    html = template.render(context)
    os.makedirs(settings.BUILD_DIR, exist_ok=True)

    if isinstance(obj, Page) and obj.slug == 'index':
        filename = os.path.join(settings.BUILD_DIR, 'index.html')
    elif obj.collection.path != 'pages':
        dirname = os.path.join(settings.BUILD_DIR, obj.slug)
        filename = os.path.join(dirname, 'index.html')
    else:
        dirname = os.path.join(
            settings.BUILD_DIR,
            obj.collection.path,
            obj.slug
        )

        filename = os.path.join(dirname, 'index.html')

    with open(filename, 'w') as f:
        f.write(html)
        print('.', os.path.split(filename)[-1])


def build():
    os.makedirs(settings.BUILD_DIR, exist_ok=True)
    rmtree(settings.BUILD_DIR)

    for Model in (Page, Post):
        for obj in Model.objects.all():
            build_obj(obj)

    app.emit('build')
