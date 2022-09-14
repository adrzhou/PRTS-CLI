import click
import tomli
import tomli_w
import pathlib
import requests
from bs4 import BeautifulSoup
from utils.parser import parse

package_path = pathlib.Path(__file__).parents[1]
catalog_path = package_path.joinpath('catalog.toml')
config_path = package_path.joinpath('config.toml')
data_path = package_path.joinpath('data')
names_path = package_path.joinpath('reserved_names.toml')


@click.command(no_args_is_help=True)
@click.option('-s', '--subclass', 'subclass', is_flag=True, help='同步特定分支的所有干员')
@click.argument('operators', nargs=-1, required=False)
def sync(subclass, operators):
    """将本地数据与prts.wiki同步"""

    def get_source(name: str):
        response = requests.get(rf'https://prts.wiki/index.php?title={name}&action=edit')
        soup = BeautifulSoup(response.text, features='html.parser')
        return soup.find(id='wpTextbox1')

    with open(catalog_path, 'rb') as catalog_file:
        catalog: dict = tomli.load(catalog_file)

    if subclass:
        for subcls in operators:
            tasks = []
            for cls in catalog.values():
                if subcls in cls.keys():
                    tasks = cls[subcls].keys()
                    break
            for oprt in tasks:
                source = get_source(oprt)
                try:
                    oprt_data = parse(source.text)
                    stem = oprt_data['干员信息']['情报编号']
                    oprt_path = data_path.joinpath(f"{stem}.toml")
                    with open(oprt_path, 'wb') as oprt_file:
                        tomli_w.dump(oprt_data, oprt_file)
                    click.echo(f'成功更新**{oprt}**的干员信息')
                except ValueError:
                    click.echo(f'ERROR: 未找到干员**{oprt}**的wiki页面')
    else:
        with open(config_path, 'rb') as config_file:
            config: dict = tomli.load(config_file)
        with open(names_path, 'rb') as names_file:
            names: dict = tomli.load(names_file)
        for oprt in operators:
            oprt = config['alias'].get(oprt.upper(), oprt).lower()
            source = get_source(oprt)
            if not source:
                click.echo(f'ERROR: 未找到干员**{oprt}**的wiki页面')
                continue

            source = source.text
            if '#redirect' in source:
                start = source.index('[[')
                end = source.index(']]')
                redirect = source[start + 2:end]
                source = get_source(redirect)

            oprt_data = parse(source)
            stem = oprt_data['干员信息']['情报编号']
            oprt_path = data_path.joinpath(f"{stem}.toml")
            with open(oprt_path, 'wb') as oprt_file:
                tomli_w.dump(oprt_data, oprt_file)

            oprt_name = oprt_data['干员信息']['干员名']
            oprt_cls = oprt_data['干员信息']['职业']
            oprt_subcls = oprt_data['干员信息']['分支']
            if oprt_subcls not in catalog[oprt_cls]:
                catalog[oprt_cls][oprt_subcls] = {}
            names[f"{oprt_data['干员信息']['干员名']}"] = stem
            names[f"{oprt_data['干员信息']['干员外文名']}"] = stem
            catalog[oprt_cls][oprt_subcls][oprt_name] = stem

            click.echo(f'成功更新**{oprt_name}**的干员信息')

        with open(catalog_path, 'wb') as catalog_file:
            tomli_w.dump(catalog, catalog_file)
        with open(names_path, 'wb') as names_file:
            tomli_w.dump(names, names_file)
