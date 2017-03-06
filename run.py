#!/usr/bin/env python3
import click

@click.command()
def hello():
    click.echo('Hi Henry')

if __name__ == '__main__':
    hello()


"""
from garrent import models, database
models.Base.metadata.bind = database.engine
models.Base.metadata.create_all(database.engine)
"""
