#!/usr/bin/env python3
import click

@click.group()
def run():
    pass

@run.command()
def initdb():
    from garrent import models, database
    models.Base.metadata.bind = database.engine
    models.Base.metadata.create_all(database.engine)
    click.echo("Database inited")

@run.command()
def updatestock():
    click.echo('Updating Hong Kong stock list')
    from garrent.tasks import insert_stock
    insert_stock()

if __name__ == '__main__':
    run()

"""

"""
