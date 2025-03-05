from collections import defaultdict
from importlib import import_module
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from . import settings
from .exceptions import ConfigError, NotFoundError


class WatchdogHandler(FileSystemEventHandler):
    def on_modified(self, event):
        filename = event.src_path[len(settings.CONTENT_DIR):]
        app.emit('reload', [filename])


class BudgieApp(object):
    def __init__(self):
        self.__tags = {}
        self.__filters = {}
        self.__routes = []
        self.__callbacks = defaultdict(list)
        self.__transformers = defaultdict(list)
        self.domain = settings.DOMAIN
        self.cache = {}

    def start(self, context: str):
        import_module('budgie.content.pages')

        if not self.domain:
            raise RuntimeError('Unable to determine website domain.')

        for plugin_name in settings.PLUGINS:
            import_module(plugin_name)

        try:
            assert context in ('build', 'serve')
        except AssertionError:
            raise ConfigError('Invalid app context')

        self.context = context

        event_handler = WatchdogHandler()
        observer = Observer()
        observer.schedule(
            event_handler,
            path=settings.CONTENT_DIR,
            recursive=True
        )

        observer.start()

    def tag(self, name: str = ''):
        def decorator(func):
            if name:
                tag_name = name
            elif func.__name__.endswith('_tag'):
                tag_name = func.__name__[:-7]
            else:
                tag_name = func.__name__

            self.__tags[tag_name] = func
            return func

        return decorator

    def filter(self, name: str = ''):
        def decorator(func):
            if name:
                filter_name = name
            elif func.__name__.endswith('_filter'):
                filter_name = func.__name__[:-7]
            else:
                filter_name = func.__name__

            self.__filters[filter_name] = func
            return func

        return decorator

    def route(
        self,
        path: str,
        name: str = '',
        priority: int = 1
    ):
        def decorator(func):
            from .routing import Route

            self.__routes.append(
                Route(path, func, name, priority)
            )

            return func

        return decorator

    def on(self, event_name: str):
        def decorator(func):
            self.__callbacks[event_name].append(func)
            return func

        return decorator

    def emit(self, event_name: str, *args, **kwargs):
        for callback in self.__callbacks[event_name]:
            callback(*args, **kwargs)

    def transformer(self, transformer_name: str, ordering: int = 10):
        def decorator(func):
            self.__transformers[transformer_name].append(
                (func, ordering)
            )

            return func

        return decorator

    def get_template_tags(self):
        return self.__tags

    def get_template_filters(self):
        return self.__filters

    def match_route(self, request):
        from .response import Response404, ResponseRedirect

        routes = sorted(
            self.__routes,
            key=lambda r: r.priority
        )

        try:
            for route in routes:
                if match := route.match(request.path):
                    args = match.groups()
                    return route(request, *args)

            raise NotFoundError()

        except NotFoundError:
            if not request.path.endswith('/'):
                return ResponseRedirect(request.path + '/')

            return Response404()

    def build_absolute_uri(self, path: str):
        if not path.startswith('/'):
            path = '/' + path

        return '//%s%s' % (self.domain, path)

    def build_menu(self, menu_name: str, request):
        options = settings.MENUS.get(menu_name, [])
        menu = []
        request_path = '/%s' % request.path

        for option in options:
            classes = option.get('classes', [])
            item = {
                'url': self.build_absolute_uri(option['path']),
                'text': option['text'],
                'classes': tuple(set(classes)),
                'active': request_path == option['path']
            }

            menu.append(item)

        return menu

    def build_menus(self, request):
        menus = {}
        for menu_name in settings.MENUS.keys():
            menus[menu_name] = self.build_menu(menu_name, request)

        return menus

    def get_template_context(self, request):
        context = {}
        menus = self.build_menus(request)

        if any(menus):
            context['MENUS'] = menus

        return context

    def transform(self, transformer_name, value):
        transformers = self.__transformers[transformer_name]
        transformers = [
            t[0]
            for t in sorted(transformers, key=lambda t: t[1])
        ]

        for transformer in transformers:
            value = transformer(value)

        return value


app = BudgieApp()
