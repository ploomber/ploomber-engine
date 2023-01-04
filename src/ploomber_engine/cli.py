"""
Command-line interface
"""

import click

from ploomber_engine import execute_notebook


@click.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.argument("output_path", type=click.Path(exists=False))
@click.option(
    "--log-output",
    is_flag=True,
    default=False,
    help="Display notebook's stdout",
)
@click.option(
    "--profile-runtime",
    is_flag=True,
    default=False,
    help="Profile cell's runtime",
)
@click.option(
    "--profile-memory",
    is_flag=True,
    default=False,
    help="Profile cell's memory usage",
)
def cli(input_path, output_path, log_output, profile_runtime, profile_memory):
    """
    Execute my-notebook.ipynb, store results in output.ipynb:

    $ ploomber-engine my-notebook.ipynb output.ipynb

    Display print statements:

    $ ploomber-engine my-notebook.ipynb output.ipynb --log-output

    Store a plot with cell's runtime:

    $ ploomber-engine my-notebook.ipynb output.ipynb --profile-runtime

    Store a plot with cell's memory usage:

    $ ploomber-engine my-notebook.ipynb output.ipynb --profile-memory
    """
    execute_notebook(
        input_path,
        output_path,
        log_output=log_output,
        profile_memory=profile_memory,
        profile_runtime=profile_runtime,
    )
