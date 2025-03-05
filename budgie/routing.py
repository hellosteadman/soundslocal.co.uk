from inspect import isfunction
from .views import View
import re


class Route(object):
    def __init__(
        self,
        path: str,
        view: View,
        name: str = '',
        priority: int = 1
    ):
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
        self.priority = priority

    def __call__(self, request, *args):
        if isfunction(self.view):
            return self.view(request, *args)

        if issubclass(self.view, View):
            view = self.view()
            return view.dispatch(request, *args)

        raise RuntimeError('Unsupported response type', type(response))

    def match(self, path):
        return self.path_ex.match(path)
