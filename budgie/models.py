from glob import glob
from io import StringIO
from .app import app
from .config import settings
from .db import Comparer
from .exceptions import NotFoundError, ContentDefinitionError
import os
import re
import yaml


META_LINE_EX = re.compile(r'^(\w+): (.+)$')
SCHEMA = {
    'slug': '',
    'title': '',
    'seo_title': '',
    'seo_description': '',
    'robots': None,
    'heading': '',
    'lede': ''
}


class Collection(object):
    def __init__(self, path=None):
        self.path = path
        self.__custom_path = not not path
        self.__slugs = []
        self.__obj_cache = None

    def __set_name__(self, owner, name):
        self.model = owner

        if not self.path:
            self.path = owner.__name__.lower() + 's'

    def all(self):
        if self.__obj_cache is not None:
            return self.__obj_cache

        self.__obj_cache = []
        path = os.path.join(settings.CONTENT_DIR, self.path)

        for name in glob('*.md', root_dir=path):
            filename = os.path.join(path, name)
            obj = self.model(self, filename)

            if obj.slug in self.__slugs:
                raise ContentDefinitionError(
                    'Slug \'%s\' already in use' % obj.slug
                )

            self.__slugs.append(obj.slug)
            self.__obj_cache.append(obj)

        return self.__obj_cache

    def filter(self, **kwargs):
        for obj in self.all():
            ignore = False

            for key, criteria in kwargs.items():
                comparer = Comparer.infer(key)
                if not comparer.compare(obj, criteria):
                    ignore = True
                    break

            if not ignore:
                yield obj

    def get(self, **kwargs):
        for obj in self.filter(**kwargs):
            return obj

        raise NotFoundError(
            'Object not found in \'%s\' collection matching query' % (
                self.path
            )
        )

    def build_url(self, path):
        if self.__custom_path:
            return app.build_absolute_uri(
                '/%s/%s/' % (self.path, path)
            )

        return app.build_absolute_uri('/%s/' % path)


class ModelBase(object):
    def __init__(self, collection, filename):
        schema = app.transform('article_schema', dict(**SCHEMA))

        def parse():
            in_content = False
            body = ''

            for prop, default_value in schema.items():
                setattr(self, prop, None)

            meta_lines = []

            with open(filename, 'r') as f:
                for line in f.readlines():
                    if not in_content:
                        if META_LINE_EX.match(line):
                            meta_lines.append(line)
                        else:
                            in_content = True

                    if in_content:
                        if not line.strip() and not body:
                            continue

                        if line.startswith('# ') and not body:
                            self.heading = line[1:].strip()
                            continue

                        body += line

            if any(meta_lines):
                meta_stream = StringIO(''.join(meta_lines))
                meta = yaml.load(meta_stream, yaml.SafeLoader)

                for key, value in meta.items():
                    key = key.lower()

                    if key not in schema:
                        raise ContentDefinitionError(
                            'Invalid property: \'%s\'' % key
                        )

                    transformed = app.transform(
                        'article_property',
                        value,
                        prop=key
                    )

                    setattr(self, key, transformed)                        

            if not self.slug:
                self.slug = os.path.splitext(
                    os.path.split(filename)[-1]
                )[0]

            if not self.title:
                if self.heading:
                    self.title = self.heading
                else:
                    self.title = self.slug.replace('-', ' ').capitalize()

            if not self.heading:
                self.heading = self.title

            self.body = app.transform('article_body', body)
            self.collection = collection

        @app.on('reload')
        def clear(files_changed=[]):
            basename = filename[len(settings.CONTENT_DIR):]
            for fn in files_changed:
                if fn == basename:
                    parse()

        parse()

    def get_absolute_url(self):
        return self.collection.build_url(self.slug)
