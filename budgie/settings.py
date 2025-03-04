from .exceptions import ConfigError
import yaml
import os


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CONTENT_DIR = os.path.join(BASE_DIR, 'content')
BUILD_DIR = os.path.join(BASE_DIR, 'build')
THEME_DIR = os.path.join(BASE_DIR, 'theme')
PLUGINS = []
DOMAIN = ''
FRONTEND_PACKAGES = []
MENUS = {
    'main': [
        {
            'path': '/',
            'text': 'Home'
        }
    ]
}


filename = os.path.join(BASE_DIR, 'settings.yaml')
if not os.path.exists(filename):
    filename = os.path.join(BASE_DIR, 'settings.yml')

if os.path.exists(filename):
    with open(filename, 'r') as f:
        settings = yaml.load(f, yaml.SafeLoader)
    
    del f

    if not isinstance(settings, dict):
        raise ConfigError('settings.yaml contents must be an object.')

    plugins = settings.pop('budgie_plugins', [])
    PLUGINS = list(sorted(set(PLUGINS + plugins)))
    del plugins

    packages = settings.pop('frontend_packages', [])
    FRONTEND_PACKAGES = list(sorted(set(FRONTEND_PACKAGES + packages)))
    del packages

    DOMAIN = settings.pop('domain', '')

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

                del k

            del i
            del option
        
        del menu_name
        del menu_options

        MENUS.update(menus)

    del menus

    for key in settings.keys():
        raise ConfigError('Unrecognised setting: \'%s\'.' % key)

    del settings

if os.getenv('DOMAIN'):
    DOMAIN = os.getenv('DOMAIN')

del filename
