import click
import pathlib
from tabulate import tabulate
from utils.loader import load_oprt

package_path = pathlib.Path(__file__).parents[1]
config_path = package_path.joinpath('config.toml')
data_path = package_path.joinpath('data')
names_path = package_path.joinpath('reserved_names.toml')


@click.command(no_args_is_help=True)
@click.option('-P', '--pager', 'pager', is_flag=True, help='分页显示查询结果')
@click.option('-g', '--general', 'general', is_flag=True, help='查询干员基本信息')
@click.option('-a', '--attr', 'attr', is_flag=True, help='查询干员属性')
@click.option('-t', '--talent', 'talent', is_flag=True, help='查询干员天赋')
@click.option('-p', '--potential', 'potential', is_flag=True, help='查询干员潜能')
@click.option('-s', '--skill', 'skill', is_flag=False, flag_value=0, multiple=True, type=int, help='查询干员技能')
@click.option('-r', '--rank', 'rank', default=[0], multiple=True, type=int, help='查询特定等级的技能')
@click.option('-u', '--upgrade', 'upgrade', flag_value='upgrade', help='显示技能升级/精英化所需材料')
@click.option('-U', '--upgrade-only', 'upgrade', flag_value='upgrade_only', help='仅显示技能升级/精英化所需材料')
@click.option('-e', '--elite', 'elite', is_flag=False, flag_value=2, type=click.IntRange(0, 2),
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

    # If user only provides the operator argument
    everything = not (general or attr or talent or skill or elite or module)
    if everything:
        # TODO: print everything
        pass

    output = []

    if general:
        output.append(tabulate_general(oprt))

    if attr:
        output.append(tabulate_attr(oprt))

    if talent:
        output.append(tabulate_talent(oprt))

    if potential:
        output.append(tabulate_potential(oprt))

    if elite in (0, 1, 2):
        section = output[f'精英{elite}'] = {}
        section['部署费用'] = oprt['属性']['部署费用']
        section['阻挡数'] = oprt['属性']['阻挡数']
        for key, value in oprt['属性'].items():
            if key.startswith(f'精英{elite}'):
                section[key] = value
        if upgrade:
            if upgrade == 'upgrade_only':
                section.clear()
            if elite == 0:
                click.echo('晋升至精英0不需要精英化材料')
            else:
                try:
                    section['精英化材料'] = oprt['精英化材料'][f'精{elite}']
                except KeyError:
                    click.echo(f'该干员无法晋升至精英{elite}')

    if skill:
        kanji = {1: '一', 2: '二', 3: '三'}
        section = output['技能'] = {}
        if 0 in skill:
            if oprt['干员信息']['稀有度'] in '01':
                click.echo('一星和二星干员无技能')
                del output['技能']
            for sk in kanji.values():
                try:
                    section[f'{sk}'] = oprt[f'{sk}技能']
                except KeyError:
                    continue
        else:
            for sk in set(skill):
                if sk < 1:
                    continue
                if sk > 3:
                    break
                if 0 in rank:
                    try:
                        section[f'{kanji[sk]}技能'] = oprt[f'{kanji[sk]}技能']
                    except KeyError:
                        click.echo(f'该干员没有{kanji[sk]}技能')
                        break
                else:
                    section[f'{kanji[sk]}'] = {}
                    for r in set(rank):
                        if r < 1:
                            continue
                        if r > 10:
                            break
                        try:
                            section[f'{kanji[sk]}'][str(r)] = oprt[f'{kanji[sk]}技能'][str(r)]
                        except KeyError:
                            click.echo('该干员技能等级最高为7')
                            rank = [i for i in rank if 0 < i < 8]
                            break
        if upgrade:
            for sk, ranks in section.items():
                if upgrade == 'upgrade_only':
                    try:
                        del section[sk]['1']
                    except KeyError:
                        pass
                for r in tuple(ranks):
                    if upgrade == 'upgrade_only':
                        try:
                            section[sk][r].clear()
                        except AttributeError:
                            del section[sk][r]
                            continue
                    try:
                        int(r)
                    except ValueError:
                        continue
                    if 1 < int(r) < 8:
                        section[sk][r]['升级材料'] = oprt['技能升级材料'][str(r)]
                    elif int(r) > 7:
                        section[sk][r]['升级材料'] = oprt['技能升级材料'][f'{sk[0]}{r}']
                    else:
                        pass

    if module:
        output['模组'] = {k: v for k, v in oprt['模组'].items() if not k.startswith('材料消耗')}
        if upgrade:
            if upgrade == 'upgrade_only':
                output['模组'].clear()
            output['模组'].update({k: v for k, v in oprt['模组'].items() if k.startswith('材料消耗')})

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
            condition = talent[key+'条件']
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
