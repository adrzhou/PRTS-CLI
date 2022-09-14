import os
import pathlib
import click
import tomli
import tomli_w

package_path = pathlib.Path(__file__).parents[1]
config_path = package_path.joinpath('config.toml')
profile_path = package_path.joinpath('profile.toml')
data_path = package_path.joinpath('data')


@click.command()
@click.argument('args', nargs=-1)
@click.option('-m', '--material', 'material', is_flag=True, help='设置养成材料别名')
def alias(args, material):
    """设置或查询干员别名"""

    if material:
        if not args:
            with open(config_path, 'rb') as config_file:
                aliases: dict = tomli.load(config_file)['material_alias']
            for mat_alias, mat_name in aliases.items():
                click.echo(f'alias {mat_alias}={mat_name}')
        else:
            with open(profile_path, 'rb') as pro_file:
                inventory: dict = tomli.load(pro_file)['inventory']
            with open(config_path, 'rb') as config_file:
                config: dict = tomli.load(config_file)
            for arg in args:
                split_arg = [s for s in arg.split('=') if s]
                if len(split_arg) > 2:
                    click.echo(f'无法用{arg}创建材料别名')
                    click.echo('请使用以下格式创建材料别名')
                    click.echo('材料别名=材料原名')
                elif len(split_arg) == 2:
                    new_alias, mat_name = tuple(split_arg)
                    if new_alias in inventory:
                        click.echo(f'{new_alias}无法作为材料别名使用')
                        continue
                    if mat_name in inventory:
                        config['material_alias'][new_alias] = mat_name
                        with open(config_path, 'wb') as config_file:
                            tomli_w.dump(config, config_file)
                    else:
                        click.echo(f'材料**{mat_name}**不存在')
                else:
                    if mat_name := config['material_alias'].get(arg, False):
                        click.echo(f'alias {arg}={mat_name}')
                    else:
                        click.echo(f'材料别名{arg}不存在')
        return

    if not args:
        with open(config_path, 'rb') as config_file:
            aliases: dict = tomli.load(config_file)['alias']
        for op_alias, op_name in aliases.items():
            click.echo(f'alias {op_alias}={op_name}')
    else:
        for arg in args:
            split_arg = [s for s in arg.split('=') if s]
            if len(split_arg) > 2:
                click.echo(f'无法用{arg}创建干员别名')
                click.echo('请使用以下格式创建干员别名')
                click.echo('干员别名=干员名(或已存在的干员别名)')
            elif len(split_arg) == 2:
                new_alias, op_name = tuple(split_arg)
                if f'{new_alias}.toml' in os.listdir(data_path):
                    click.echo(f'{new_alias}无法作为干员别名使用')
                    continue
                names_path = package_path.joinpath('reserved_names.toml')
                with open(names_path, 'rb') as names_file:
                    names_cn: dict = tomli.load(names_file)
                with open(config_path, 'rb') as config_file:
                    config: dict = tomli.load(config_file)
                if f'{op_name}.toml' in os.listdir(data_path):
                    config['alias'][new_alias] = op_name
                elif existing_name := names_cn.get(op_name, False):
                    config['alias'][new_alias] = existing_name
                elif existing_name := config['alias'].get(op_name, False):
                    config['alias'][new_alias] = existing_name
                else:
                    click.echo(f'未找到名为{op_name}的干员')
                    continue
                with open(config_path, 'wb') as config_file:
                    tomli_w.dump(config, config_file)
            else:
                with open(config_path, 'rb') as config_file:
                    aliases = tomli.load(config_file)['alias']
                    if op_name := aliases.get(arg, False):
                        click.echo(f'alias {arg}={op_name}')
                    else:
                        click.echo(f'干员别名{arg}不存在')


@click.command(no_args_is_help=True)
@click.option('-a', '--all', 'all_', is_flag=True, help='清除所有干员别名')
@click.option('-m', '--material', 'material', is_flag=True, help='清除材料别名')
@click.argument('aliases', nargs=-1)
def unalias(all_, aliases, material):
    """删除干员别名"""
    with open(config_path, 'rb') as config_file:
        config = tomli.load(config_file)
    if all_:
        if material:
            config['material_alias'].clear()
        else:
            config['alias'].clear()
    else:
        for a in aliases:
            if material:
                try:
                    del config['material_alias'][a]
                except KeyError:
                    continue
            else:
                try:
                    del config['alias'][a]
                except KeyError:
                    continue
    with open(config_path, 'wb') as config_file:
        tomli_w.dump(config, config_file)
