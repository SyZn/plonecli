# -*- coding: utf-8 -*-
"""Console script for plonecli."""

import click
import subprocess
import os

from plonecli.registry import template_registry as reg


def get_templates(ctx, args, incomplete):
    """Return a list of available mr.bob templates."""
    templates = reg.get_templates()
    return templates


@click.group(chain=True)
@click.pass_context
def cli(context):
    """Plone Command Line Interface (CLI)"""
    context.obj = {}
    context.obj['target_dir'] = reg.root_folder


@cli.command()
@click.argument(
    'template',
    type=click.STRING,
    autocompletion=get_templates,
)
@click.argument('name')
@click.option('-v', '--verbose', is_flag=True)
@click.pass_context
def create(context, template, name, verbose):
    """Create a new Plone package"""
    template = reg.resolve_template_name(template)
    cur_dir = os.getcwd()
    context.obj['target_dir'] = '{0}/{1}'.format(cur_dir, name)
    if verbose:
        click.echo('RUN: mrbob {0} -O {1}'.format(template, name))
    subprocess.call(
        [
            'mrbob',
            template,
            '-O',
            name,
        ],
    )


@cli.command()
@click.argument(
    'template',
    type=click.STRING,
    autocompletion=get_templates,
)
@click.option('-v', '--verbose', is_flag=True)
@click.pass_context
def add(context, template, verbose):
    """Add features to your existing Plone package"""
    template = reg.resolve_template_name(template)
    if verbose:
        click.echo('RUN: mrbob {0}'.format(template))
    subprocess.call(
        [
            'mrbob',
            template,
        ],
    )


@cli.command('virtualenv')
@click.option('-v', '--verbose', is_flag=True)
@click.option('-c', '--clean', is_flag=True)
@click.pass_context
def create_virtualenv(context, verbose, clean):
    """Create/update the local virtual environment for the Plone package"""
    params = [
        'virtualenv',
        '.',
    ]
    if clean:
        params.append('--clear')
    if verbose:
        click.echo('RUN: {0}'.format(' '.join(params)))
    subprocess.call(
        params,
        cwd=context.obj['target_dir'],
    )


@cli.command('requirements')
@click.option('-v', '--verbose', is_flag=True)
@click.pass_context
def install_requirements(context, verbose):
    """Install the local package requirements"""
    if verbose:
        click.echo('RUN: pip install -r requirements.txt --upgrades')
    subprocess.call(
        [
            './bin/pip',
            'install',
            '-r',
            'requirements.txt',
            '--upgrade',
        ],
        cwd=context.obj['target_dir'],
    )


@cli.command('buildout')
@click.option('-v', '--verbose', count=True)
@click.option('-c', '--clean', count=True)
@click.pass_context
def run_buildout(context, verbose, clean):
    """Run the package buildout"""
    params = [
        './bin/buildout',
    ]
    if clean:
        params.append('-n')
    if verbose:
        click.echo('RUN: {0}'.format(' '.join(params)))
    subprocess.call(
        params,
        cwd=context.obj['target_dir'],
    )


@cli.command('serve')
@click.option('-v', '--verbose', count=True)
@click.pass_context
def run_serve(context, verbose):
    """Run the Plone client in foreground mode"""
    if verbose:
        click.echo('RUN: ./bin/instance fg')
    click.echo(
        '\nINFO: Open this in a Web Browser: http://localhost:8080')
    click.echo('INFO: You can stop it by pressing CTRL + c\n')
    subprocess.call(
        [
            './bin/instance',
            'fg',
        ],
        cwd=context.obj['target_dir'],
    )


@cli.command('debug')
@click.option('-v', '--verbose', count=True)
@click.pass_context
def run_debug(context, verbose):
    """Run the Plone client in debug mode"""
    if verbose:
        click.echo('RUN: ./bin/instance debug')
    click.echo('INFO: You can stop it by pressing STRG + c')
    subprocess.call(
        [
            './bin/instance',
            'debug',
        ],
        cwd=context.obj['target_dir'],
    )


@cli.command()
@click.option('-v', '--verbose', count=True)
@click.option('-c', '--clean', count=True)
@click.pass_context
def build(context, verbose, clean):
    """Bootstrap and build the package"""
    if clean:
        context.invoke(create_virtualenv, clean=True)
    else:
        context.invoke(create_virtualenv, clean=True)
    context.invoke(install_requirements)
    context.forward(run_buildout)


if __name__ == "__main__":
    cli()
