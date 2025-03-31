#!/usr/bin/env python

import budgie
import click


@click.group()
def cli():
    """
    Management commands for the static site builder.
    """

    click.echo()


@click.command()
@click.option('--domain', default=None, help='Website domain.')
def build(domain: str = None):
    """
    Build the static site.
    """

    if domain:
        budgie.app.domain = domain

    budgie.app.start('build')
    click.echo('Building the static site...')
    budgie.build_site()
    click.echo('\nBuild complete.\n')


@click.command()
@click.option('--host', default='localhost', help='Hostname to serve files on.')
@click.option('--port', type=int, default=8000, help='Port to serve files on.')
def serve(host: str = 'localhost', port: int = 8000):
    """
    Run the development server.
    """

    budgie.app.domain = '%s:%s' % (host, port)
    budgie.app.start('serve')
    budgie.runserver(host=host, port=port)
    click.echo()


cli.add_command(build)
cli.add_command(serve)

if __name__ == '__main__':
    cli()
