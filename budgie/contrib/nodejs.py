from budgie import settings
from hashlib import md5
import json
import os
import subprocess


PACKAGE_FILENAME = os.path.join(settings.BASE_DIR, 'package.json')


def setup_environment():
    if not os.path.exists(PACKAGE_FILENAME):
        package = {
            'name': 'soundslocal',
            'version': '1.0.0',
            'description': '',
            'author': 'Mark Steadman'
        }

        with open(PACKAGE_FILENAME, 'w') as f:
            json.dump(package, f, indent=4)
    else:
        with open(PACKAGE_FILENAME, 'r') as f:
            package = json.load(f)

    dev_dependencies = package.get('devDependencies', {})
    unmet_dev_dependencies = ['esbuild', 'sass']
    dependencies = package.get('dependencies', {})
    unmet_dependencies = list(sorted(set(settings.FRONTEND_PACKAGES)))

    for dep in dev_dependencies:
        try:
            index = unmet_dev_dependencies.index(dep)
        except ValueError:
            pass
        else:
            unmet_dev_dependencies.pop(index)

    if any(unmet_dev_dependencies):
        os.chdir(settings.BASE_DIR)
        subprocess.run(
            [
                'npm',
                'install',
                '--save-dev',
                *unmet_dev_dependencies
            ]
        )

    for dep in dependencies:
        try:
            index = unmet_dependencies.index(dep)
        except ValueError:
            pass
        else:
            unmet_dependencies.pop(index)

    if any(unmet_dependencies):
        os.chdir(settings.BASE_DIR)
        subprocess.run(
            [
                'npm',
                'install',
                '--save',
                *unmet_dependencies
            ]
        )

    os.chdir(settings.BASE_DIR)
    subprocess.run(
        [
            'npx',
            'esbuild',
            '--version'
        ],
        check=True,
        capture_output=True
    )

    subprocess.run(
        [
            'npx',
            'sass',
            '--version'
        ],
        check=True,
        capture_output=True
    )


def format_filename(output_filename, input_filename):
    if '{hash}' in output_filename:
        with open(input_filename, 'rb') as f:
            digest = md5(f.read()).hexdigest()
            return output_filename.replace('{hash}', digest)

    return output_filename


def compile_js(input_filename, output_filename, source_map=False):
    if not os.path.exists(input_filename):
        raise FileNotFoundError('Input file not found')

    output_basename = format_filename(output_filename, input_filename)
    setup_environment()
    os.chdir(settings.BASE_DIR)

    args = [
        'npx',
        'esbuild',
        input_filename,
        '--bundle',
        '--outfile=%s' % output_basename,
        '--minify',
        '--log-level=silent'
    ]

    if source_map:
        args.append('--sourcemap')

    subprocess.run(args, check=True)
    return os.path.split(output_basename)[-1]


def compile_scss(input_filename, output_filename, source_map=False):
    if not os.path.exists(input_filename):
        raise FileNotFoundError('Input file not found')

    output_basename = format_filename(output_filename, input_filename)
    setup_environment()
    os.chdir(settings.BASE_DIR)

    args = [
        'npx',
        'sass',
        input_filename,
        output_basename,
        '--quiet',
        '--load-path=node_modules'
    ]

    if not source_map:
        args.append('--no-source-map')

    subprocess.run(args, check=True)
    return os.path.split(output_basename)[-1]
