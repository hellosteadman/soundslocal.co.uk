from budgie import app, settings
from budgie.contrib import nodejs
from budgie.response import Response, FileResponse
from glob import glob
from tempfile import mkstemp
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import os
import shutil
import sys


STATIC_DIR = os.path.join(settings.THEME_DIR, 'static')


cache = {}


def compile_js(start_file):
    if 'js' not in cache:
        cache['js'] = {}

    if start_file not in cache['js']:
        output_filename = os.path.join(
            settings.BUILD_DIR,
            'static',
            'js',
            'site.{hash}.js'
        )

        output_basename = nodejs.compile_js(
            start_file,
            output_filename,
            source_map=True
        )

        print('.', 'static/js/%s' % output_basename)
        cache['js'][start_file] = '/static/js/%s' % output_basename

    return cache['js'][start_file]


def compile_scss(start_file):
    if 'css' not in cache:
        cache['css'] = {}

    if start_file not in cache['css']:
        output_filename = os.path.join(
            settings.BUILD_DIR,
            'static',
            'css',
            'site.{hash}.css'
        )

        output_basename = nodejs.compile_scss(
            start_file,
            output_filename,
            source_map=True
        )

        print('.', 'static/css/%s' % output_basename)
        cache['css'][start_file] = '/static/css/%s' % output_basename

    return cache['css'][start_file]


def cache_file(filename):
    files = app.cache.get('staticfiles', [])
    if filename not in files:
        files.append(filename)
        app.cache['staticfiles'] = files


@app.tag()
def static(path):
    if app.context == 'serve':
        if path.startswith('scss/'):
            path = 'css/' + path[5:]

        if path.endswith('.scss'):
            path = path[:-5] + '.css'

        return '/static/%s' % path

    path_parts = path.split('/')
    filename = os.path.join(STATIC_DIR, *path_parts)

    if filename.endswith('.js'):
        cache_file(filename)
        return app.build_absolute_uri(compile_js(filename))

    if filename.endswith('.scss'):
        cache_file(filename)
        return app.build_absolute_uri(compile_scss(filename))

    return app.build_absolute_uri('/static/%s' % path)


@app.route('static/js/*.js')
def serve_js(request, path):
    if 'js' not in cache:
        cache['js'] = {}

    if path not in cache['js']:
        handle, filename = mkstemp('.js')
        os.close(handle)

        path_parts = (path + '.js').split('/')
        nodejs.compile_js(
            os.path.join(STATIC_DIR, 'js', *path_parts),
            filename
        )

        cache['js'][path] = filename

    return Response(
        open(cache['js'][path], 'r').read(),
        content_type='text/javascript'
    )


@app.route('static/css/*.css')
def serve_css(request, path):
    if 'css' not in cache:
        cache['css'] = {}

    if path not in cache['css']:
        handle, filename = mkstemp('.css')
        os.close(handle)

        path_parts = (path + '.scss').split('/')
        nodejs.compile_scss(
            os.path.join(STATIC_DIR, 'scss', *path_parts),
            filename
        )

        cache['css'][path] = filename

    return Response(
        open(cache['css'][path], 'r').read(),
        content_type='text/css'
    )


@app.route('static/**')
def serve_static(request, path):
    path_parts = path.split('/')
    filename = os.path.join(STATIC_DIR, *path_parts)
    return FileResponse(filename)


@app.on('build')
def copy_assets(root_dir=STATIC_DIR):
    cached_files = app.cache.get('staticfiles', [])

    for filename in glob('*', root_dir=root_dir):
        fullpath = os.path.join(root_dir, filename)
        if os.path.isdir(fullpath):
            copy_assets(fullpath)
            continue

        if filename.startswith('.') or filename.startswith('_'):
            continue

        if fullpath in cached_files:
            continue

        basepath = fullpath[len(STATIC_DIR) + 1:]
        copydir = os.path.join(
            settings.BUILD_DIR,
            'static',
            os.path.split(basepath)[0]
        )

        os.makedirs(copydir, exist_ok=True)

        copypath = os.path.join(
            settings.BUILD_DIR,
            'static',
            basepath
        )

        shutil.copyfile(fullpath, copypath)
        print('.', 'static/%s' % basepath)


class WatchdogHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('.js'):
            if 'start' in cache.get('js', {}):
                sys.stdout.write('Recompiling start.js...')
                sys.stdout.flush()

                handle, filename = mkstemp('.js')
                os.close(handle)

                nodejs.compile_js(
                    os.path.join(STATIC_DIR, 'js', 'start.js'),
                    filename
                )

                cache['js']['start'] = filename
                sys.stdout.write(' Done\n')
                app.emit('reload', ['/static/js/start.js'])
                return

        if event.src_path.endswith('.scss'):
            if 'start' in cache.get('css', {}):
                sys.stdout.write('Recompiling start.scss...')
                sys.stdout.flush()

                handle, filename = mkstemp('.js')
                os.close(handle)

                nodejs.compile_scss(
                    os.path.join(STATIC_DIR, 'scss', 'start.scss'),
                    filename
                )

                cache['css']['start'] = filename
                sys.stdout.write(' Done\n')
                app.emit('reload', ['/static/scss/start.scss'])
                return


event_handler = WatchdogHandler()
observer = Observer()
observer.schedule(event_handler, path=STATIC_DIR, recursive=True)
observer.start()
