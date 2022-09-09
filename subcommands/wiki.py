import click


@click.command(no_args_is_help=True)
@click.argument('operator', nargs=1, required=False)
def wiki(operator):
    """查询干员信息"""
    pass
