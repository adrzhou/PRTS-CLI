import click
import pathlib
import tomli
import tomli_w


package_path = pathlib.Path(__file__).parents[1]
config_path = package_path.joinpath('config.toml')
data_path = package_path.joinpath('data')
names_path = package_path.joinpath('names_cn.toml')


@click.command(no_args_is_help=True)
@click.option('-p', '--pager', 'pager', is_flag=True, help='分页显示查询结果')
@click.argument('operator', nargs=1, required=False)
def wiki(operator, pager):
    """查询干员信息"""

    if data_path.joinpath(f'{operator}.toml') in data_path.iterdir():
        operator_path = f'{operator}.toml'
    else:
        with open(config_path, 'rb') as config_file:
            config: dict = tomli.load(config_file)
        with open(names_path, 'rb') as names_file:
            names: dict = tomli.load(names_file)
        if operator in names:
            operator_path = f'{names[operator]}.toml'
        elif operator in config['alias']:
            operator_path = f'{config["alias"][operator]}.toml'
        else:
            click.echo(f'未找到名叫或别名为{operator}的干员')
            return
    with open(data_path.joinpath(operator_path), 'rb') as operator_file:
        operator_dict = tomli.load(operator_file)
    if pager:
        click.echo_via_pager(tomli_w.dumps(operator_dict).replace('"', ''))
    else:
        click.echo(tomli_w.dumps(operator_dict).replace('"', ''))
