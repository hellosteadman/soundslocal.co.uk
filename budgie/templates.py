from bs4 import BeautifulSoup
from jinja2 import (
    Environment,
    BaseLoader,
    select_autoescape,
    TemplateNotFound,
    nodes
)

from jinja2.ext import Extension as ExtensionBase
from . import settings
from .app import app
import os


class ThemeLoader(BaseLoader):
    def get_source(self, environment: Environment, name: str):
        filename = os.path.join(
            settings.THEME_DIR,
            'templates',
            *os.path.split(name)
        )

        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return (f.read(), name, lambda: True)

        raise TemplateNotFound(name)


def TagExcension(tag_name, tag_func):
    class Extension(ExtensionBase):
        tags = {tag_name}

        def parse(self, parser):
            lineno = next(parser.stream).lineno
            args = [parser.parse_expression()]
            call_node = self.call_method(
                '_render',
                args,
                lineno=lineno,
            )

            output = nodes.Output([call_node])
            return output.set_lineno(lineno)

        def _render(self, *args, **kwargs):
            return tag_func(*args)

    return Extension


class Template(object):
    def __init__(self, name: (str, list, tuple)):
        if isinstance(name, str):
            self.names = [name]
        else:
            self.names = name

    def render(self, context: dict = {}):
        if 'engine' not in 'cache':
            engine = Environment(
                loader=ThemeLoader(),
                autoescape=select_autoescape(),
                extensions=[
                    TagExcension(*tag_pair)
                    for tag_pair in app.get_template_tags().items()
                ]
            )

            for name, filter_func in app.get_template_filters().items():
                engine.filters[name] = filter_func

            cache['engine'] = engine
        else:
            engine = cache['engine']

        ctx = {**context}
        if request := context.get('request'):
            ctx.update(app.get_template_context(request))

        names = list(self.names)
        template = None

        while template is None:
            template_name = names.pop(0)

            try:
                template = engine.get_template(template_name)
            except TemplateNotFound:
                if not any(names):
                    raise
            else:
                rendered = template.render(**ctx)

                if template_name.endswith('.html'):
                    soup = BeautifulSoup(rendered, 'html.parser')
                    rendered = str(soup)

                return rendered


cache = {}
