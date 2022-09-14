import pathlib
import click
import tomli
import tomli_w

package_path = pathlib.Path(__file__).parents[1]
config_path = package_path.joinpath('config.toml')
profile_path = package_path.joinpath('profile.toml')
names_path = package_path.joinpath('reserved_names.toml')
data_path = package_path.joinpath('data')


@click.command()
@click.argument('args', nargs=-1)
@click.option('-m', '--material', 'material', is_flag=True, help='设置养成材料别名')
def alias(args, material):
    """设置或查询干员或材料别名"""

    with open(config_path, 'rb') as config_file:
        config: dict = tomli.load(config_file)

    if material:
        aliases: dict = config['material_alias']
        if not args:
            for mtrl_alias, mtrl_name in aliases.items():
                click.echo(f'alias {mtrl_alias}={mtrl_name}')
        else:
            with open(profile_path, 'rb') as pro_file:
                inventory: dict = tomli.load(pro_file)['inventory']
            for arg in args:
                split_arg = [s for s in arg.split('=') if s]
                if len(split_arg) > 2:
                    click.echo(f'无法用{arg}创建材料别名')
                    click.echo('请使用以下格式创建材料别名')
                    click.echo('材料别名=材料原名')
                elif len(split_arg) == 2:
                    new_alias, mtrl_name = tuple(split_arg)
                    if new_alias in inventory:
                        click.echo(f'{new_alias}无法作为材料别名使用')
                        continue
                    if mtrl_name in inventory:
                        aliases[new_alias] = mtrl_name
                        with open(config_path, 'wb') as config_file:
                            tomli_w.dump(config, config_file)
                    else:
                        click.echo(f'材料**{mtrl_name}**不存在')
                else:
                    if mtrl_name := aliases.get(arg, False):
                        click.echo(f'alias {arg}={mtrl_name}')
                    else:
                        click.echo(f'材料别名**{arg}**不存在')
        return

    aliases: dict = config['alias']
    if not args:
        for oprt_alias, oprt_name in aliases.items():
            click.echo(f'alias {oprt_alias}={oprt_name}')
    else:
        with open(names_path, 'rb') as names_file:
            names: dict = tomli.load(names_file)
        for arg in args:
            split_arg = [s for s in arg.split('=') if s]
            if len(split_arg) > 2:
                click.echo(f'无法用{arg}创建干员别名')
                click.echo('请使用以下格式')
                click.echo('干员别名=干员名(或已存在的干员别名)')
            elif len(split_arg) == 2:
                new_alias, oprt_name = tuple(split_arg)
                if new_alias.upper() in names:
                    click.echo(f'"{new_alias}"无法作为干员别名使用')
                    continue
                if oprt_name.upper() in names:
                    aliases[new_alias] = oprt_name.upper()
                elif existing_name := aliases.get(oprt_name, False):
                    aliases[new_alias] = existing_name
                else:
                    click.echo(f'未找到名为{oprt_name}的干员')
                    continue
            else:
                if oprt_name := aliases.get(arg, False):
                    click.echo(f'alias {arg}={oprt_name}')
                else:
                    click.echo(f'干员别名{arg}不存在')
        with open(config_path, 'wb') as config_file:
            tomli_w.dump(config, config_file)


@click.command(no_args_is_help=True)
@click.option('-a', '--all', 'all_', is_flag=True, help='清除所有干员或材料别名')
@click.option('-m', '--material', 'material', is_flag=True, help='清除材料别名')
@click.argument('aliases', nargs=-1)
def unalias(all_, aliases, material):
    """删除干员或材料别名"""

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
