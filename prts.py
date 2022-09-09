import click
from subcommands.alias import alias, unalias
from subcommands.sync import sync


@click.group()
def prts():
    pass


prts.add_command(alias)
prts.add_command(unalias)
prts.add_command(sync)

if __name__ == '__main__':
    prts()
