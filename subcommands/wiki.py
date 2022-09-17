import click
import pathlib
from tabulate import tabulate
from utils.loader import load_oprt
from utils.colorize import colorize

package_path = pathlib.Path(__file__).parents[1]
data_path = package_path.joinpath('data')


@click.command(no_args_is_help=True)
@click.option('-P', '--pager', 'pager', is_flag=True, help='分页显示查询结果')
@click.option('-g', '--general', 'general', is_flag=True, help='查询干员基本信息')
@click.option('-a', '--attr', 'attr', is_flag=True, help='查询干员属性')
@click.option('-t', '--talent', 'talent', is_flag=True, help='查询干员天赋')
@click.option('-p', '--potential', 'potential', is_flag=True, help='查询干员潜能')
@click.option('-s', '--skill', 'skill', is_flag=False, flag_value=0, multiple=True, type=int, help='查询干员技能')
@click.option('-r', '--rank', 'rank', default=(0,), multiple=True, type=int, help='查询特定等级的技能')
@click.option('-u', '--upgrade', 'upgrade', flag_value='upgrade', help='显示技能升级/精英化所需材料')
@click.option('-U', '--upgrade-only', 'upgrade', flag_value='upgrade_only', help='仅显示技能升级/精英化所需材料')
@click.option('-e', '--elite', 'elite', type=click.IntRange(0, 2),
              prompt='请指定要查询的精英等级', prompt_required=False,
              help='查询干员精英化之后的属性数据')
@click.option('-m', '--module', 'module', is_flag=True, help='查询干员模组')
@click.argument('operator', nargs=1, required=False)
def wiki(pager, general, attr, talent, potential, skill, rank, upgrade, elite, module, operator):
    """查询干员信息"""

    # Options were provided but no operator found
    if not operator:
        click.echo('请添加需要查询的干员名称或别名之后重试')
        return

    try:
        oprt = load_oprt(operator)
        oprt['干员信息']['稀有度'] = int(oprt['干员信息']['稀有度']) + 1
    except KeyError:
        click.echo(f'未找到名叫或别名为{operator}的干员')
        return

    output = []

    # If user only provides the operator argument
    everything = not (general or attr or talent or skill or potential
                      or (elite in range(3))
                      or module)
    if everything:
        output.append(tabulate_general(oprt))
        output.append(tabulate_attr(oprt))
        output.append(tabulate_talent(oprt))
        output.append(tabulate_skill(oprt, (0,), rank, upgrade))
        if '模组' in oprt:
            output.append(tabulate_module(oprt, upgrade))

    else:
        if general:
            output.append(tabulate_general(oprt))

        if attr:
            output.append(tabulate_attr(oprt))

        if talent:
            output.append(tabulate_talent(oprt))

        if potential:
            output.append(tabulate_potential(oprt))

        if elite in range(3):
            output.append(tabulate_elite(oprt, elite, upgrade))

        if skill:
            output.append(tabulate_skill(oprt, skill, rank, upgrade))

        if module:
            if '模组' in oprt:
                output.append(tabulate_module(oprt, upgrade))
            else:
                click.echo('该干员未开放模组系统')

    if pager:
        click.echo_via_pager('\n\n'.join(output))
    else:
        click.echo('\n\n'.join(output))


def tabulate_general(oprt: dict):
    general = []
    for key, value in oprt['干员信息'].items():
        general.append([key, value])
    return tabulate(general, tablefmt='pretty')


def tabulate_attr(oprt: dict):
    attr1 = []
    for key in ('再部署', '部署费用', '阻挡数', '攻击速度'):
        value = oprt['属性'][key]
        attr1.append([key, value])
    attr1 = tabulate(attr1, tablefmt='pretty')

    attr2 = []
    attr2_header = ['属性', '精英0 1级', '精英0 满级', '信赖加成']
    rarity = oprt['干员信息']['稀有度']
    if rarity > 2:
        attr2_header.insert(-1, '精英1 满级')
    if rarity > 3:
        attr2_header.insert(-1, '精英2 满级')
    for attr in ('生命上限', '攻击', '防御', '法术抗性'):
        row = [attr]
        for col in attr2_header[1:]:
            key = col.replace(' ', '_') + '_' + attr
            value = oprt['属性'].get(key, None)
            row.append(value)
        attr2.append(row)
    attr2 = tabulate(attr2, headers=attr2_header, tablefmt='github')

    return f'{attr1}\n\n{attr2}'


def tabulate_talent(oprt: dict):
    output = []
    talent = oprt['天赋']
    talents = {}

    for key, value in talent.items():
        if len(key) == 5:
            if value not in talents:
                talents[value] = []
            condition = talent[key + '条件']
            effect = talent[key + '效果']
            talents[value].append([condition, effect])

    for t, rows in talents.items():
        header = ['条件', '效果']
        table = tabulate(rows, headers=header, tablefmt='github')
        output.append(f'{t}\n{table}')

    return '\n\n'.join(output)


def tabulate_potential(oprt: dict):
    header = ['潜能提升', '']
    rows = []
    for key, value in oprt['潜能提升'].items():
        rows.append([key, value])
    return tabulate(rows, headers=header, tablefmt='github')


def tabulate_elite(oprt: dict, elite: int, upgrade: bool):
    rarity = oprt['干员信息']['稀有度']
    if rarity < 3 and elite > 0:
        click.echo('一星和二星干员无法精英化')
        return ''
    if rarity == 3 and elite > 1:
        click.echo('三星干员无法晋升至精英2')
        return ''

    attr = oprt['属性']
    header = [f'精英{elite}_满级', '']
    rows = []

    for key in ('部署费用', '阻挡数'):
        rows.append([key, attr[key]])
    for key in ('生命上限', '攻击', '防御', '法术抗性'):
        f_key = f'精英{elite}_满级_{key}'
        rows.append([key, attr[f_key]])
    table = tabulate(rows, headers=header, tablefmt='github')

    talent = oprt['天赋']
    header = ['天赋', '条件', '效果']
    rows = []
    for key, value in talent.items():
        if f'精英{elite}' in value:
            effect = talent[f'{key[:-2]}效果']
            row = [key[:4], value, effect]
            rows.append(row)
    talent_table = tabulate(rows, headers=header, tablefmt='github')

    if upgrade:
        upgrade_table = ''
        if elite == 0:
            click.echo('晋升至精英0不需要精英化材料')
        else:
            header = [f'精{elite}材料', '数量']
            try:
                require = oprt['精英化材料'][f'精{elite}']
                rows = [[mtrl, amount] for mtrl, amount in require.items()]
                upgrade_table = tabulate(rows, headers=header, tablefmt='github')
                upgrade_table = colorize(upgrade_table)
            except KeyError:
                click.echo(f'该干员无法晋升至精英{elite}')

        if upgrade == 'upgrade_only':
            return upgrade_table
        return f'{table}\n\n{talent_table}\n\n{upgrade_table}'

    return f'{table}\n\n{talent_table}'


def tabulate_skill(oprt: dict, skill: tuple, rank: tuple, upgrade: str):
    kanji = {1: '一', 2: '二', 3: '三'}
    rarity = oprt['干员信息']['稀有度']

    # If user does not specify skill
    if 0 in skill:
        if rarity < 3:
            click.echo('一星和二星干员无技能')
            return ''

        output = []
        for sk in kanji.values():
            try:
                sk = oprt[f'{sk}技能']
                name = sk['技能名']
                type1 = sk['技能类型1']
                type2 = sk.get('技能类型2', '被动触发')
                header = ['等级', '描述', '初始', '消耗', '持续']
                rows = []
                value = sk['7']
                row = [value[k] for k in header[1:]]
                row = [7] + row
                rows.append(row)
                if rarity > 3:
                    rows.clear()
                    value = sk['10']
                    row = [value[k] for k in header[1:]]
                    row = [10] + row
                    rows.append(row)
                table = tabulate(rows, headers=header, tablefmt='github')
                output.append(f'{name}  [{type1}]  [{type2}]\n{table}')
            except KeyError:
                continue

        if upgrade:
            output.append('技能升级材料')
            if upgrade == 'upgrade_only':
                output.clear()
            for rk, value in oprt['技能升级材料'].items():
                rows = [[k, v] for k, v in value.items()]
                table = tabulate(rows, tablefmt='github')
                table = colorize(table)
                output.append(f'{rk}\n{table}')

        return '\n\n'.join(output)

    # If user does specify skill
    else:
        output = []
        for sk in set(skill).intersection({1, 2, 3}):
            try:
                sk = oprt[f'{kanji[sk]}技能']
            except KeyError:
                click.echo(f'该干员没有{kanji[sk]}技能')
                continue

            name = sk['技能名']
            type1 = sk['技能类型1']
            type2 = sk.get('技能类型2', '')
            header = ['等级', '描述', '初始', '消耗', '持续']
            rows = []

            # If user does not specify rank
            if 0 in rank:
                for rk in range(1, 8):
                    value = sk[str(rk)]
                    row = [value[k] for k in header[1:]]
                    row = [rk] + row
                    rows.append(row)
                if rarity > 3:
                    for rk in (8, 9, 10):
                        value = sk[str(rk)]
                        row = [value[k] for k in header[1:]]
                        row = [rk] + row
                        rows.append(row)

            # If user does specify rank
            else:
                for rk in set(rank).intersection(set(range(1, 11))):
                    if rk < 1:
                        continue
                    if rk > 10:
                        break
                    try:
                        value = sk[str(rk)]
                    except KeyError:
                        click.echo('该干员技能等级最高为7')
                        break
                    row = [value[k] for k in header[1:]]
                    row = [rk] + row
                    rows.append(row)

            table = tabulate(rows, headers=header, tablefmt='github')
            output.append(f'{name}  [{type1}]  [{type2}]\n{table}')

        if upgrade:
            if 0 in rank:
                rank = range(2, 8)
            if upgrade == 'upgrade_only':
                output.clear()
            for rk in set(rank).intersection(set(range(2, 8))):
                req = oprt['技能升级材料'][str(rk)]
                rows = [[k, v] for k, v in req.items()]
                table = tabulate(rows, tablefmt='github')
                table = colorize(table)
                output.append(f'{rk}\n{table}')
            for sk in set(skill).intersection({1, 2, 3}):
                for rk in set(rank).intersection({8, 9, 10}):
                    req = oprt['技能升级材料'][f'{kanji[sk]}{rk}']
                    rows = [[k, v] for k, v in req.items()]
                    table = tabulate(rows, tablefmt='github')
                    table = colorize(table)
                    output.append(f'{kanji[sk]}{rk}\n{table}')

        return '\n\n'.join(output)


def tabulate_module(oprt: dict, upgrade: str):
    output = []
    module = oprt['模组']
    for name, mdl in module.items():
        mdl.pop('解锁等级', None)
        mdl.pop('解锁信赖', None)
        rows = []
        for key in ('名称', '类型', '任务1', '任务2'):
            rows.append([key, mdl.pop(key)])
        table = tabulate(rows, tablefmt='pretty')
        output.append(table)

        attrs = [key for key, value in mdl.items() if type(value) is int]
        cols = {}
        keys = [key for key in attrs if not (key.endswith('2') or key.endswith('3'))]
        cols['属性'] = keys
        cols['等级1'] = [mdl.pop(key, None) for key in keys]
        cols['等级2'] = [mdl.pop(f'{key}2', None) for key in keys]
        cols['等级3'] = [mdl.pop(f'{key}3', None) for key in keys]
        table = tabulate(cols, headers='keys', tablefmt='pretty')
        output.append(table)

        keys = [key for key in mdl if not key.startswith('材料消耗')]
        rows = [[key, mdl.pop(key)] for key in keys]
        table = tabulate(rows, tablefmt='pretty')
        output.append(table)

        if upgrade:
            if upgrade == 'upgrade_only':
                output.clear()
            for key, req in mdl.items():
                header = ('材料', '数量')
                rows = [[k, v] for k, v in req.items()]
                table = tabulate(rows, headers=header, tablefmt='pretty')
                table = colorize(table)
                output.append(f'{key}\n{table}')

    return '\n\n'.join(output)
