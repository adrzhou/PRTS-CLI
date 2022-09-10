import click
import pathlib
import tomli
import tomli_w
from utils.load_dict import load_dict

package_path = pathlib.Path(__file__).parents[1]
config_path = package_path.joinpath('config.toml')
names_path = package_path.joinpath('names_cn.toml')
profile_path = package_path.joinpath('profile.toml')
data_path = package_path.joinpath('data')


@click.command()
@click.argument('operator', nargs=-1, required=False)
@click.option('-e', '--elite', 'elite', type=click.IntRange(0, 2), help='设置干员精英等级')
@click.option('-r', '--rank', 'rank', type=click.IntRange(1, 10), help='设置干员技能等级')
@click.option('-s', '--skill', 'skill', type=click.IntRange(1, 3), help='设置干员特定技能的专精等级')
@click.option('-m', '--module', 'module', type=click.IntRange(0, 3), help='设置干员模组阶段')
def track(operator, elite, rank, skill, module):
    """追踪干员练度与仓库材料"""

    with open(profile_path, 'rb') as pro_file:
        profile = tomli.load(pro_file)
    if not operator:
        click.echo(tomli_w.dumps(profile['tracking']).replace('"', ''))
    else:
        kanji = {1: '一', 2: '二', 3: '三'}
        for op in operator:
            try:
                op_dict = load_dict(op)
            except KeyError:
                click.echo(f'未找到名叫或别名为{op}的干员')
                continue
            op_name = op_dict['干员信息']['干员名']
            rarity = int(op_dict['干员信息']['稀有度'])
            if op_name in profile['tracking'].keys():
                output = profile['tracking'][op_name]
            else:
                output = profile['tracking'][op_name] = {'精英': 0}
                if rarity > 1:
                    output['一技能'] = 1
                if rarity > 2:
                    output['二技能'] = 1
                if rarity == 5:
                    output['三技能'] = 1
                if '模组' in op_dict.keys():
                    output['模组'] = 0
            if not (elite in (0, 1, 2) or rank or skill or module in (0, 1, 2, 3)):
                click.echo(op_name)
                click.echo(tomli_w.dumps(output).replace('"', ''))
            else:
                if elite in (0, 1, 2):
                    if rarity < 2 or (rarity < 3 and elite == 2):
                        click.echo(f'干员{op_name}无法晋升至精英{elite}')
                    else:
                        output['精英'] = elite
                if rank:
                    if rarity < 2:
                        click.echo(f'干员{op_name}无法提升技能等级')
                    elif 0 < rank < 8:
                        output['一技能'] = rank
                        if rarity > 2:
                            output['二技能'] = rank
                        if rarity == 5:
                            output['三技能'] = rank
                        if rank > 4 and output['精英'] == 0:
                            output['精英'] = 1
                    else:
                        if output['精英'] < 2:
                            output['精英'] = 2
                        if skill:
                            if rarity == 2:
                                click.echo(f'干员{op_name}无法专精技能')
                            elif skill == 3 and rarity < 5:
                                click.echo(f'干员{op_name}没有三技能')
                            else:
                                output[f'{kanji[skill]}技能'] = rank
                                for i in kanji.values():
                                    if output[f'{i}技能'] < 7:
                                        output[f'{i}技能'] = 7
                        else:
                            output['一技能'] = rank
                            if rarity > 2:
                                output['二技能'] = rank
                            if rarity == 5:
                                output['三技能'] = rank
                if module in (0, 1, 2, 3):
                    if '模组' in op_dict.keys():
                        output['模组'] = module
            with open(profile_path, 'wb') as pro_file:
                tomli_w.dump(profile, pro_file)


@click.command(no_args_is_help=True)
@click.argument('operator', nargs=-1, required=False)
@click.option('-a', '--all', 'all_', is_flag=True, help='停止追踪所有干员')
def untrack(operator, all_):
    """停止追踪干员练度"""

    with open(profile_path, 'rb') as pro_file:
        profile = tomli.load(pro_file)
    if all_:
        profile['tracking'].clear()
    else:
        for op in operator:
            try:
                op_dict = load_dict(op)
            except KeyError:
                click.echo(f'未找到名叫或别名为{op}的干员')
                continue
            op_name = op_dict['干员信息']['干员名']
            del profile['tracking'][op_name]
    with open(profile_path, 'wb') as pro_file:
        tomli_w.dump(profile, pro_file)
