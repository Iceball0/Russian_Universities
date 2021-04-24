import click
from flask.cli import with_appcontext

from flask_sqlalchemy import SQLAlchemy

@click.command(name='create_tables')
@with_appcontext
def create_tables():
    SQLAlchemy.create_all()