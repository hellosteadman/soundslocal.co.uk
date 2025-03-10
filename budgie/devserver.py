from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
from urllib.parse import urlparse
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from . import logging
from .app import app
from .request import Request
from .response import JsonResponse
import click
import os
import sys


HOT_RELOAD_JS = open(
    os.path.join(
        os.path.dirname(__file__),
        'fixtures',
        'hot-reload.js'
    ),
    'r'
).read()


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, *args, **kwargs):
        pass

    def do_GET(self):
        path = urlparse(self.path).path

        if not path.startswith('/'):
            path = '/%s' % path

        request = Request(path)

        try:
            response = app.match_route(request)
            if response is None:
                raise RuntimeError('View returned None instead of a Response')

            self.send_response(response.status_code)
            inject_reload = False

            for header, value in response.headers.items():
                if header.lower() == 'content-type':
                    if 'text/html' in value:
                        inject_reload = True
                self.send_header(header, value)

            self.end_headers()

            if inject_reload:
                body = response.body.decode('utf-8')
                end_body = body.lower().find('</body>')

                if end_body > -1:
                    before_endbody = body[:end_body]
                    after_endbody = body[end_body:]
                    inject = '<script>%s</script>' % HOT_RELOAD_JS
                    body = before_endbody + inject + after_endbody

                self.wfile.write(body.encode('utf-8'))
            else:
                response.output(self.wfile)
        except Exception as ex:
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(
                ('<p>%s</p>' % str(ex.args[0])).encode('utf-8')
            )

            logging.error(ex)


class WatchdogHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('.py'):
            click.echo('\nPython file changed. Restarting server...')
            os.execv(sys.executable, ['python'] + sys.argv)


class DevServer(TCPServer):
    allow_reuse_address = True  # Ensures the port is freed immediately


def post_message(**message):
    messages = app.cache.get('reload_messages', [])
    messages.append(message)
    app.cache['reload_messages'] = messages


@app.route('.well-known/reload-messages/')
def reload_messages(request):
    messages = reversed(
        app.cache.get('reload_messages', [])
    )

    app.cache['reload_messages'] = []
    return JsonResponse(list(messages))


@app.on('reload')
def hot_reload(files_changed=[]):
    for filename in files_changed:
        if filename.endswith('.js'):
            post_message(action='reload', full=True)
            continue

        if filename.endswith('.scss'):
            post_message(action='reload', css='/static/css/start.css')
            continue

        if filename.endswith('.md'):
            post_message(action='reload', full=True)
            continue

        if filename.startswith('/templates/'):
            post_message(action='reload', full=True)


def run(host: str = 'localhost', port: int = 8000):
    server = ('0.0.0.0', port)

    with DevServer(server, Handler) as httpd:
        click.echo('Starting development server...')
        event_handler = WatchdogHandler()
        observer = Observer()
        observer.schedule(event_handler, path='.', recursive=True)
        observer.start()

        try:
            click.echo('Serving at http://%s:%d/' % server)
            httpd.serve_forever()
        except KeyboardInterrupt:
            click.echo('\nShutting down server...')
            httpd.shutdown()
            httpd.server_close()
            observer.stop()
            observer.join()
