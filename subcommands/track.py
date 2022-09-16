import click
import pathlib
import tomli
import tomli_w
from tabulate import tabulate
from utils.loader import load_oprt

package_path = pathlib.Path(__file__).parents[1]
config_path = package_path.joinpath('usr', 'config.toml')
names_path = package_path.joinpath('usr', 'reserved_names.toml')
profile_path = package_path.joinpath('usr', 'profile.toml')
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
        for oprt, tracker in profile['tracker'].items():
            status = tracker['目前']
            goal = tracker['目标']
            header = [oprt, '目前', '目标']
            rows = [[key, status[key], goal[key]] for key in status]
            table = tabulate(rows, headers=header, tablefmt='github')
            click.echo(table)
            click.echo('\n')
        return

    # At least one operator provided
    for op in operator:
        try:
            oprt = load_oprt(op)
        except KeyError:
            click.echo(f'未找到名叫或别名为{op}的干员')
            continue
        name = oprt['干员信息']['干员名']
        rarity = int(oprt['干员信息']['稀有度'])

        if name not in profile['tracker']:
            tracker = profile['tracker'][name] = {'目前': {}, '目标': {}, '模组': {}}
            set_init(oprt, tracker, rarity)
        else:
            tracker = profile['tracker'][name]

        if elite in range(3):
            set_elite(goal, elite, rarity, name, tracker)
        if rank:
            set_rank(goal, rank, skill, rarity, name, tracker)
        if module in range(4):
            set_module(goal, tracker, module)

        status = tracker['目前']
        goal = tracker['目标']
        header = [name, '目前', '目标']
        rows = [[key, status[key], goal[key]] for key in status]
        table = tabulate(rows, headers=header, tablefmt='github')
        click.echo(table)
        click.echo('\n')

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
                oprt = load_oprt(op)
            except KeyError:
                click.echo(f'未找到名叫或别名为{op}的干员')
                continue
            op_name = oprt['干员信息']['干员名']
            del profile['tracker'][op_name]
    with open(profile_path, 'wb') as pro_file:
        tomli_w.dump(profile, pro_file)


def set_init(oprt: dict, tracker: dict, rarity: int) -> None:
    """Helper for initializing a tracked operator"""

    status = tracker['目前']
    goal = tracker['目标']
    module = tracker['模组']

    if rarity > 1:
        status['精英'] = 0
        status['一技能'] = 1
        goal['精英'] = 1
        goal['一技能'] = 7
    if rarity > 2:
        status['二技能'] = 1
        goal['精英'] = 2
        goal['二技能'] = 7
    if rarity == 5:
        status['三技能'] = 1
        goal['三技能'] = 7
    if '模组' in oprt:
        idx = 1
        for mdl in oprt['模组']:
            status[mdl] = 0
            goal[mdl] = 3
            module[str(idx)] = mdl
            idx += 1


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
            output['目前']['精英'] = 2
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
