import click
import pathlib
import tomli
import tomli_w
from utils.loader import load_dict

package_path = pathlib.Path(__file__).parents[1]
config_path = package_path.joinpath('config.toml')
names_path = package_path.joinpath('reserved_names.toml')
profile_path = package_path.joinpath('profile.toml')
data_path = package_path.joinpath('data')
kanji = {1: '一', 2: '二', 3: '三'}


@click.command()
@click.argument('operator', nargs=-1, required=False)
@click.option('-e', '--elite', 'elite', type=click.IntRange(0, 2), help='设置干员精英等级')
@click.option('-r', '--rank', 'rank', type=click.IntRange(1, 10), help='设置干员技能等级')
@click.option('-s', '--skill', 'skill', type=click.IntRange(1, 3), help='设置干员特定技能的专精等级')
@click.option('-m', '--module', 'module', type=click.IntRange(0, 3), help='设置干员模组阶段')
@click.option('-g', '--goal', 'goal', is_flag=True, help='设定干员练度目标')
def track(operator, elite, rank, skill, module, goal):
    """追踪干员练度与仓库材料"""

    with open(profile_path, 'rb') as pro_file:
        profile = tomli.load(pro_file)

    # No arguments provided
    if not operator:
        click.echo(tomli_w.dumps(profile['tracker']).replace('"', ''))
    else:
        for op in operator:
            try:
                op_dict = load_dict(op)
            except KeyError:
                click.echo(f'未找到名叫或别名为{op}的干员')
                continue
            op_name = op_dict['干员信息']['干员名']
            rarity = int(op_dict['干员信息']['稀有度'])

            # Operator already tracked
            if op_name in profile['tracker'].keys():
                output = profile['tracker'][op_name]

            # Add new operator to tracking list
            else:
                output = profile['tracker'][op_name] = {'目前': {}, '目标': {}}
                set_init(op_dict, output, rarity)

            # No options provided
            if not (elite in (0, 1, 2) or rank or module in (0, 1, 2, 3)):
                click.echo(op_name)
                click.echo(tomli_w.dumps(output).replace('"', ''))

            # At least one option provided
            else:
                if elite in range(3):
                    set_elite(goal, elite, rarity, op_name, output)
                if rank:
                    set_rank(goal, rank, skill, rarity, op_name, output)
                if module in range(4):
                    set_module(goal, output, module)
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
        profile['tracker'].clear()
    else:
        for op in operator:
            try:
                op_dict = load_dict(op)
            except KeyError:
                click.echo(f'未找到名叫或别名为{op}的干员')
                continue
            op_name = op_dict['干员信息']['干员名']
            del profile['tracker'][op_name]
    with open(profile_path, 'wb') as pro_file:
        tomli_w.dump(profile, pro_file)


def set_init(op_dict: dict, output: dict, rarity: int) -> None:
    """Helper for initializing a tracked operator"""

    if rarity > 1:
        output['目前']['精英'] = 0
        output['目前']['一技能'] = 1
        output['目标']['精英'] = 1
        output['目标']['一技能'] = 7
    if rarity > 2:
        output['目前']['二技能'] = 1
        output['目标']['精英'] = 2
        output['目标']['二技能'] = 7
    if rarity == 5:
        output['目前']['三技能'] = 1
        output['目标']['三技能'] = 7
    if '模组' in op_dict.keys():
        output['目前']['模组'] = 0
        output['目标']['模组'] = 3


def set_elite(goal: bool, elite: int, rarity: int, op_name: str, output: dict) -> None:
    """Helper for setting an operator's elite level"""

    if rarity < 2 or (rarity < 3 and elite == 2):
        click.echo(f'干员{op_name}无法晋升至精英{elite}')
        return

    if goal:
        output['目标']['精英'] = elite
        # 精英0的干员技能等级不大于4且未解锁模组
        if elite == 0:
            for k, v in output['目标'].items():
                if k.endswith('技能') and v > 4:
                    output['目标'][k] = 4
            if '模组' in output['目标'].keys():
                output['目标']['模组'] = 0
        # 精英1的干员技能等级不大于7且未解锁模组
        elif elite == 1:
            for k, v in output['目标'].items():
                if k.endswith('技能') and v > 7:
                    output['目标'][k] = 7
            if '模组' in output['目标'].keys():
                output['目标']['模组'] = 0
        return

    output['目前']['精英'] = elite
    # 精英0的干员技能等级不大于4且未解锁模组
    if elite == 0:
        for k, v in output['目前'].items():
            if k.endswith('技能') and v > 4:
                output['目前'][k] = 4
        if '模组' in output['目前'].keys():
            output['目前']['模组'] = 0
    # 精英1的干员技能等级不大于7且未解锁模组
    elif elite == 1:
        for k, v in output['目前'].items():
            if k.endswith('技能') and v > 7:
                output['目前'][k] = 7
        if '模组' in output['目前'].keys():
            output['模组'] = 0


def set_rank(goal: bool, rank: int, skill: int, rarity: int, op_name: str, output: dict) -> None:
    """Helper for setting an operator's skill rank"""

    if rarity < 2:
        click.echo(f'干员{op_name}无法提升技能等级')
        return
    if rank and skill:
        if rarity == 2 and rank > 7:
            click.echo(f'干员{op_name}无法专精技能')
            return
        if rarity == skill == 2:
            click.echo(f'干员{op_name}没有二技能')
            return
        if rarity < 5 and skill == 3:
            click.echo(f'干员{op_name}没有三技能')
            return
        skill = f'{kanji[skill]}技能'
        if rank in range(1, 8):
            if goal:
                for k, v in output['目标'].items():
                    if k.endswith('技能'):
                        output['目标'][k] = rank
                if rank > 4:
                    output['目标']['精英'] = 1
                return
            for k, v in output['目前'].items():
                if k.endswith('技能'):
                    output['目前'][k] = rank
            if rank > 4:
                output['目前']['精英'] = 1
            return
        if goal:
            output['目标'][skill] = rank
            if rank > 7:
                output['目标']['精英'] = 2
            return
        output['目前'][skill] = rank
        if rank > 7:
            output['目前']['精英'] = 1
    elif rank:
        if rarity == 2 and rank > 7:
            click.echo(f'干员{op_name}无法专精技能')
            return
        if goal:
            for k, v in output['目标'].items():
                if k.endswith('技能'):
                    output['目标'][k] = rank
            if rank > 4:
                output['目标']['精英'] = 1
            if rank > 7:
                output['目标']['精英'] = 2
            return
        for k, v in output['目前'].items():
            if k.endswith('技能'):
                output['目前'][k] = rank
        if rank > 4:
            output['目前']['精英'] = 1
        if rank > 7:
            output['目前']['精英'] = 2
        return


def set_module(goal: bool, output: dict, module: int) -> None:
    """Helper for setting an operator's module phase"""

    if '模组' in output['目标'].keys():
        if goal:
            output['目标']['模组'] = module
            if module in range(1, 4):
                output['目标']['精英'] = 2
        else:
            output['目前']['模组'] = module
            if module in range(1, 4):
                output['目前']['精英'] = 2
