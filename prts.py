import click
from subcommands.alias import alias, unalias


@click.group()
def prts():
    pass


prts.add_command(alias)
prts.add_command(unalias)

if __name__ == '__main__':
    prts()
