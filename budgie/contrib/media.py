from budgie import app, settings
from budgie.exceptions import ContentDefinitionError
from budgie.response import FileResponse
import os
import regex
import shutil


IMG_TAG_EX = regex.compile(r'''
    !\[
        (?P<alt>(?:[^\]\\]|\\.)*)
    \]                      # End alt text
    \(                      # Opening parenthesis for URL and optional title
        \s*
        (?P<url>
            (?:
                <(?P<angle_url>[^>]+)>         # URL in angle brackets
                |
                (?P<plain_url>
                    (?:
                        [^()\s\\]+              # URL characters (no spaces, no parentheses)
                        |\\.
                        | \( (?P>plain_url) \)   # Recursively match nested parentheses
                    )+
                )
            )
        )
        (?:\s+                                  # Optional whitespace before title
            (?P<title>
                (?:
                    " (?: [^"\\] | \\.)* "       # Title in double quotes
                    |
                    ' (?: [^'\\] | \\.)* '       # Title in single quotes
                    |
                    \( (?: [^)\\] | \\.)* \)      # Title in parentheses
                )
            )
        )?
        \s*
    \)
''', regex.VERBOSE)

MEDIA_DIR = os.path.join(settings.CONTENT_DIR, 'media')


def cache_file(filename):
    files = app.cache.get('media', [])
    if filename not in files:
        files.append(filename)
        app.cache['media'] = files


class File(object):
    def __init__(self, filename):
        self.__filename = filename

    def url(self):
        fullpath = os.path.join(MEDIA_DIR, self.__filename)
        if not os.path.exists(fullpath):
            raise ContentDefinitionError(
                'Media file \'%s\' not found' % self.__filename
            )

        if app.context == 'build':
            basepath = fullpath[len(MEDIA_DIR) + 1:]
            copydir = os.path.join(
                settings.BUILD_DIR,
                'media',
                os.path.split(basepath)[0]
            )

            os.makedirs(copydir, exist_ok=True)

            copypath = os.path.join(
                settings.BUILD_DIR,
                'media',
                basepath
            )

            if not os.path.exists(copypath):
                shutil.copyfile(fullpath, copypath)
                print('-', 'media/%s' % basepath)

        return '/media/%s' % self.__filename


@app.transformer('article_schema')
def transform_schema(schema):
    schema['banner'] = None
    schema['featured_image'] = None
    schema['thumbnail'] = None

    return schema


@app.transformer('article_property', prop=('banner', 'featured_image', 'thumbnail'))  # NOQA
def transform_property(value, prop):
    return File(value)


@app.route('media/**')
def serve_media(request, path):
    path_parts = path.split('/')
    filename = os.path.join(MEDIA_DIR, *path_parts)
    return FileResponse(filename)


@app.transformer('article_body', 100)
def transform_img(value):
    if not value:
        return ''

    def replace(match):
        alt = match.group('alt')
        path = match.group('url')
        title = match.group('title')
        media = File(path)

        if title:
            return '![%s](%s "%s")' % (alt, media.url(), title)

        return '![%s](%s)' % (alt, media.url())

    return IMG_TAG_EX.sub(replace, value)


@app.tag()
def media_tag(path):
    return File(path).url()
