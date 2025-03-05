from inspect import isfunction
from .app import app
from .exceptions import NotFoundError
from .response import Response404
from .views import View, IndexView
import re


class Route(object):
    def __init__(self, path: str, view: View, name: str = ''):
        self.path_ex = re.compile(
            '^/' + path.replace(
                '.', '\\.'
            ).replace(
                '**', '<\\WILDCARD>'
            ).replace(
                '*', '([^/]+)'
            ).replace(
                '<\\WILDCARD>',
                '(.*)'
            ) + '$'
        )

        self.view = view
        self.name = name

    def __call__(self, request, *args):
        if isfunction(self.view):
            return self.view(request, *args)

        if issubclass(self.view, View):
            view = self.view()
            return view.dispatch(request, *args)

        raise RuntimeError('Unsupported response type', type(response))

    def match(self, path):
        return self.path_ex.match(path)


routes = [
    Route('', IndexView, 'index')
]


def match(request):
    try:
        for route in routes + app.get_routes():
            if match := route.match(request.path):
                args = match.groups()
                return route(request, *args)

        raise NotFoundError()

    except NotFoundError:
        return Response404()
