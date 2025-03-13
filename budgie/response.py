from jinja2.exceptions import TemplateNotFound
from mimetypes import guess_type
from .app import app
from .templates import Template
import json
import os
import shutil


def error_page(title, extra=''):
    css = (
        'display: flex;',
        'flex-direction: column;',
        'align-items: center;',
        'justify-content: center;',
        'height: 100vh;',
        'font-family: sans-serif;'
    )

    return '<div style="%s"><h1 style="margin-bottom: 0;">%s</h1>%s</div>' % (
        ' '.join(css),
        title,
        extra and ('<p style="margin-bottom: 0;">%s</p>' % extra) or ''
    )


class Response(object):
    def __init__(
        self,
        content: str,
        content_type: str = 'text/html',
        status_code: int = 200,
        headers: dict = {}
    ):
        self.content = content
        self.content_type = content_type
        self.status_code = status_code
        self.headers = {
            'Content-Type': self.content_type,
            **headers
        }

    @property
    def body(self):
        return self.content.encode('utf-8')

    def output(self, writer):
        writer.write(self.body)


class TemplateResponse(Response):
    def __init__(
        self,
        template_names: [str],
        context: dict = {},
        content_type: str = 'text/html',
        status_code: int = 200,
        headers: dict = {}
    ):
        super().__init__(
            '',
            content_type=content_type,
            status_code=status_code,
            headers=headers
        )

        self.template_names = template_names
        self.context = context

    @property
    def body(self):
        template = Template(self.template_names)
        html = template.render(self.context)
        return html.encode('utf-8')


class Response404(Response):
    def __init__(self):
        super().__init__(
            content=error_page('Page not found'),
            status_code=404
        )

    @property
    def body(self):
        try:
            template = Template(['404.html'])
            html = template.render(
                app.get_template_context(self.request)
            )
        except TemplateNotFound:
            return super().body
        else:
            return html.encode('utf-8')


class ResponseRedirect(Response):
    def __init__(self, url, permanent=False):
        super().__init__(
            content='<h1>%s</h1>' % (
                permanent and 'Moved Permanently' or 'Found'
            ),
            status_code=permanent and 301 or 302,
            headers={
                'Location': url
            }
        )


class FileResponse(Response):
    def __init__(
        self,
        filename: str,
        status_code: int = 200,
        headers: dict = {}
    ):
        content_type, encoding = guess_type(filename)
        content_type_header = content_type

        if encoding:
            content_type_header += '; encoding=%s' % encoding

        headers['Content-Length'] = os.path.getsize(filename)
        super().__init__(
            '',
            content_type=content_type_header,
            headers=headers
        )

        self.__filename = filename

    @property
    def body(self):
        return open(self.__filename, 'rb').read()

    def output(self, writer):
        with open(self.__filename, 'rb') as f:
            shutil.copyfileobj(f, writer)


class JsonResponse(Response):
    def __init__(
        self,
        data: any,
        status_code: int = 200,
        headers: dict = {}
    ):
        super().__init__(
            '',
            content_type='application/json',
            headers=headers
        )

        self.__data = data

    @property
    def body(self):
        return json.dumps(self.__data).encode('utf-8')
