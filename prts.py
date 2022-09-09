import click
from subcommands.alias import alias, unalias
from subcommands.sync import sync
from subcommands.wiki import wiki


@click.group()
def prts():
    pass


prts.add_command(alias)
prts.add_command(unalias)
prts.add_command(sync)
prts.add_command(wiki)

if __name__ == '__main__':
    prts()
