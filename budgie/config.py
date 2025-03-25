from .exceptions import ConfigError
import yaml
import os


class Configuration(object):
    def __init__(self):
        self.BASE_DIR = os.path.dirname(os.path.dirname(__file__))
        self.CONTENT_DIR = os.path.join(self.BASE_DIR, 'content')
        self.BUILD_DIR = os.path.join(self.BASE_DIR, 'build')
        self.THEME_DIR = os.path.join(self.BASE_DIR, 'theme')
        self.PLUGINS = []
        self.DOMAIN = ''
        self.FRONTEND_PACKAGES = []
        self.BLOG_HEADING = 'Blog'
        self.BLOG_DESCRIPTION = ''
        self.MENUS = {
            'main': [
                {
                    'path': '/',
                    'text': 'Home'
                }
            ]
        }

        filename = os.path.join(self.BASE_DIR, 'settings.yaml')
        if not os.path.exists(filename):
            filename = os.path.join(self.BASE_DIR, 'settings.yml')

        if os.path.exists(filename):
            with open(filename, 'r') as f:
                settings = yaml.load(f, yaml.SafeLoader)

            if not isinstance(settings, dict):
                raise ConfigError('settings.yaml contents must be an object.')

            plugins = settings.pop('budgie_plugins', [])
            self.PLUGINS = list(
                sorted(set(self.PLUGINS + plugins))
            )

            for plugin in plugins:
                basename = plugin.split('.')[-1]
                plugin_settings = settings.pop(basename.lower(), {})

                if not isinstance(plugin_settings, dict):
                    raise ConfigError(
                        '%s must be an object.' % basename.lower()
                    )

                settings_dict = {}
                for key, value in plugin_settings.items():
                    settings_dict[key.upper()] = value

                if any(settings_dict):
                    setattr(self, basename.upper(), settings_dict)

            packages = settings.pop('frontend_packages', [])
            self.FRONTEND_PACKAGES = list(
                sorted(set(self.FRONTEND_PACKAGES + packages))
            )

            self.DOMAIN = settings.pop('domain', '')

            menus = settings.pop('menus', {})
            if not isinstance(menus, dict):
                raise ConfigError('menus must be an object.')

            if any(menus):
                for menu_name, menu_options in menus.items():
                    if not isinstance(menu_options, list):
                        raise ConfigError('menus.%s must be a list.' % menu_name)

                    for i, option in enumerate(menu_options):
                        if not isinstance(option, dict):
                            raise ConfigError(
                                'menus.%s.%d must be an object.' % (
                                    menu_name,
                                    i
                                )
                            )

                        for k in ('path', 'text'):
                            if k not in option:
                                raise ConfigError(
                                    'menus.%s.%d must contain a \'%s\' item.' % (
                                        menu_name,
                                        i,
                                        k
                                    )
                                )

                        for k in option.keys():
                            if k not in ('path', 'text', 'classes'):
                                raise ConfigError(
                                    'Unrecognised setting: \'menus.%s.%d.%s\'.' % (
                                        menu_name,
                                        i,
                                        k
                                    )
                                )

                self.MENUS.update(menus)

            for plugin in (
                'budgie.content.pages',
                'budgie.content.blog'
            ):
                basename = plugin.split('.')[-1]
                plugin_settings = settings.pop(basename.lower(), {})

                if not isinstance(plugin_settings, dict):
                    raise ConfigError(
                        '%s must be an object.' % basename.lower()
                    )

                settings_dict = {}
                for key, value in plugin_settings.items():
                    settings_dict[key.upper()] = value

                if any(plugin_settings):
                    setattr(self, basename.upper(), settings_dict)

            for key in settings.keys():
                raise ConfigError('Unrecognised setting: \'%s\'.' % key)

        if os.getenv('DOMAIN'):
            self.DOMAIN = os.getenv('DOMAIN')


settings = Configuration()
