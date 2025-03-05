from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
from urllib.parse import urlparse
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from . import logging
from .app import app
from .request import Request
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
                self.wfile.write(response.body)
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


def run(host: str = 'localhost', port: int = 8000):
    server = (host, port)

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
