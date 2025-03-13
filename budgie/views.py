from .exceptions import ConfigError
from .response import TemplateResponse


class View(object):
    def get(self, request, *args):
        raise RuntimeError('Method not implemented')

    def dispatch(self, request, *args):
        self.request = request
        self.args = args

        return self.get(request, *args)


class TemplateView(View):
    def get_template_names(self):
        if hasattr(self, 'template_names'):
            return self.template_names

        raise ConfigError('template_names not defined')

    def get_render_context(self):
        return {
            'request': self.request
        }

    def get(self, request, *args):
        return TemplateResponse(
            self.get_template_names(),
            self.get_render_context()
        )


class ListView(TemplateView):
    def get_query_args(self):
        return {}

    def get_object_list(self):
        if not hasattr(self, 'object_list'):
            if not hasattr(self, 'model'):
                raise ConfigError('model not defined')

            self.object_list = self.model.objects.filter(
                **self.get_query_args()
            )

        return self.object_list

    def get_template_names(self):
        template_names = [self.model.__name__.lower() + '_list.html']

        if hasattr(self, 'template_name'):
            template_names.insert(0, self.template_name)
        elif hasattr(self, 'template_names'):
            for name in reversed(self.template_names):
                template_names.insert(0, name)

        if not any(template_names):
            raise ConfigError('template_names not defined')

        return template_names

    def get_render_context(self):
        return {
            **super().get_render_context(),
            'object_list': self.get_object_list()
        }


class DetailView(TemplateView):
    def get_query_args(self):
        return {
            'slug': self.args[0]
        }

    def get_object(self):
        if not hasattr(self, 'object'):
            if not hasattr(self, 'model'):
                raise ConfigError('model not defined')

            self.object = self.model.objects.get(
                **self.get_query_args()
            )

        return self.object

    def get_template_names(self):
        template_names = [self.model.__name__.lower() + '_detail.html']

        if hasattr(self, 'template_name'):
            template_names.insert(0, self.template_name)
        elif hasattr(self, 'template_names'):
            for name in reversed(self.template_names):
                template_names.insert(0, name)

        if not any(template_names):
            raise ConfigError('template_names not defined')

        return template_names

    def get_render_context(self):
        return {
            **super().get_render_context(),
            'object': self.get_object()
        }
