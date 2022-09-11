import click
import tomli
import tomli_w
import pathlib


package_path = pathlib.Path(__file__).parents[1]
config_path = package_path.joinpath('config.toml')
names_path = package_path.joinpath('names_cn.toml')
profile_path = package_path.joinpath('profile.toml')
data_path = package_path.joinpath('data')


@click.command()
@click.argument('args', nargs=-1, required=False)
@click.option('-s', '--synth', 'synth', is_flag=True,
              help='用合成所需材料代替蓝色品质以上的材料')
@click.option('-o', '--optimal', 'optimal', is_flag=True,
              help='将待升级项目按材料收集进度排序')
@click.option('-u', '--up', 'up', is_flag=True, help='设定当期活动概率UP的材料')
@click.option('-i', '--inventory', 'inventory', is_flag=True, help='查询或更新仓库内材料数量')
def plan(args, synth, optimal, up, inventory):
    """查询干员升级所需材料"""

    with open(config_path, 'rb') as config_file:
        config = tomli.load(config_file)
    with open(profile_path, 'rb') as pro_file:
        profile = tomli.load(pro_file)

    if up:
        if not args:
            for item in config['drop_rate_up']:
                click.echo(item)
        else:
            config['drop_rate_up'].clear()
            for arg in args:
                if arg in profile['inventory']:
                    config['drop_rate_up'][arg] = True
                elif arg in config['material_alias']:
                    arg = config['material_aliases'][arg]
                    config['drop_rate_up'][arg] = True
                else:
                    click.echo(f'不存在名或别名为{arg}的材料')
        with open(config_path, 'wb') as config_file:
            tomli_w.dump(config, config_file)
        return

    if inventory and args:
        for arg in args:
            split_arg = [s for s in arg.split('=') if s]
            if len(split_arg) > 2:
                click.echo(f'无法用{arg}更新库存数量')
                click.echo('请使用以下格式更新库存数量')
                click.echo('材料原名(或别名)=库存数量')
            elif len(split_arg) == 2:
                material, amount = tuple(split_arg)
                try:
                    amount = int(amount)
                except ValueError:
                    click.echo('库存数量必须为正整数')
                if amount >= 0:
                    if material in profile['inventory']:
                        profile['inventory'][material]['amount'] = amount
                    elif material in config['material_alias']:
                        material = config['material_alias'][material]
                        profile['inventory'][material]['amount'] = amount
                    else:
                        click.echo(f'不存在名或别名为{material}的材料')
                else:
                    click.echo('库存数量必须为正整数')
            else:
                if arg in config['material_alias']:
                    arg = config['material_alias'][arg]
                try:
                    amount = profile['inventory'][arg]['amount']
                    click.echo(f'{arg} = {amount}')
                except KeyError:
                    click.echo(f'不存在名或别名为{arg}的材料')
        with open(profile_path, 'wb') as pro_file:
            tomli_w.dump(profile, pro_file)
        return

    if not args:
