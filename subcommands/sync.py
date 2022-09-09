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
names_path = package_path.joinpath('names_cn.toml')


@click.command(no_args_is_help=True)
@click.option('-s', '--subclass', 'subclass', is_flag=True, help='同步特定分支的所有干员')
@click.argument('operators', nargs=-1, required=False)
def sync(subclass, operators):
    """将本地数据与prts.wiki同步"""

    with open(catalog_path, 'rb') as catalog_file:
        catalog: dict = tomli.load(catalog_file)
    if subclass:
        for sc in operators:
            ops = []
            for cls in catalog.values():
                if sc in cls.keys():
                    ops = cls[sc].keys()
                    break
            for op in ops:
                response = requests.get(rf'https://prts.wiki/index.php?title={op}&action=edit')
                soup = BeautifulSoup(response.text, features='html.parser')
                source = soup.find(id='wpTextbox1')
                if source:
                    op_dict = parse(source.text)
                    op_filename = op_dict['干员信息']['干员外文名'].replace(' ', '_')
                    output_path = data_path.joinpath(f"{op_filename}.toml")
                    with open(output_path, 'wb') as output_file:
                        tomli_w.dump(op_dict, output_file)
                    click.echo(f'成功更新**{op}**的干员信息')
                else:
                    click.echo(f'ERROR: 未找到干员**{op}**的wiki页面')
    else:
        with open(config_path, 'rb') as config_file:
            config: dict = tomli.load(config_file)
        with open(names_path, 'rb') as names_file:
            names: dict = tomli.load(names_file)
        for op in operators:
            op = config['alias'].get(op, op)
            response = requests.get(rf'https://prts.wiki/index.php?title={op}&action=edit')
            soup = BeautifulSoup(response.text, features='html.parser')
            source = soup.find(id='wpTextbox1')
            if source:
                op_dict = parse(source.text)
                op_filename = op_dict['干员信息']['干员外文名'].replace(' ', '_')
                output_path = data_path.joinpath(f"{op_filename}.toml")
                with open(output_path, 'wb') as output_file:
                    tomli_w.dump(op_dict, output_file)
                op_class = op_dict['干员信息']['职业']
                op_subclass = op_dict['干员信息']['分支']
                if op_subclass not in catalog[op_class]:
                    catalog[op_class][op_subclass] = {}
                names[f"{op_dict['干员信息']['干员名']}"] = op_filename
                catalog[op_class][op_subclass][f"{op_dict['干员信息']['干员名']}"] = op_filename

                click.echo(f'成功更新**{op}**的干员信息')
            else:
                click.echo(f'ERROR: 未找到干员**{op}**的wiki页面')
        with open(catalog_path, 'wb') as catalog_file:
            tomli_w.dump(catalog, catalog_file)
        with open(names_path, 'wb') as names_file:
            tomli_w.dump(names, names_file)
