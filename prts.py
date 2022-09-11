import click
from subcommands.alias import alias, unalias
from subcommands.sync import sync
from subcommands.wiki import wiki
from subcommands.track import track, untrack
from subcommands.plan import plan


@click.group()
def prts():
    pass


prts.add_command(alias)
prts.add_command(unalias)
prts.add_command(sync)
prts.add_command(wiki)
prts.add_command(track)
prts.add_command(untrack)
prts.add_command(plan)


if __name__ == '__main__':
    prts()
