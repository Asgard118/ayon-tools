import click
import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))


@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    if debug:
        click.echo(f"Debug mode is enabled")
        logging.basicConfig(level=logging.DEBUG)


@cli.command('deploy')
@click.argument('studio_name')
@click.argument('project_name')
def start_deploy(studio_name, project_name):
    click.echo(f'Start deploy project {studio_name}/{project_name}')


@cli.command('list-projects')
@click.argument('studio_name')
def show_projects(studio_name):
    click.echo(f'Show projects for {studio_name}')


@cli.command('list-studios')
def show_projects():
    click.echo(f'Show all studios')


@cli.command('diff')
@click.argument('studio_name')
@click.argument('project_name')
def show_difference(studio_name, project_name):
    click.echo(f'Show diff local and server for {studio_name}/{project_name}')


@cli.command('add-addon')
@click.argument('addon_url')
def show_difference(addon_url):
    click.echo(f'Add addon to main addon list: {addon_url}')


@cli.command('dump-addon')
@click.argument('studio_name')
@click.argument('addon_name')
@click.argument('project_name', required=False)
def show_difference(studio_name, addon_name, project_name):
    click.echo(f'Dump addon settings to storage and replace existing: {studio_name}/{project_name or "[studio]"}/{addon_name}')


if __name__ == '__main__':
    cli()
