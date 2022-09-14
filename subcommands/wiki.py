import click
import pathlib
import tomli
import tomli_w

package_path = pathlib.Path(__file__).parents[1]
config_path = package_path.joinpath('config.toml')
data_path = package_path.joinpath('data')
names_path = package_path.joinpath('reserved_names.toml')


@click.command(no_args_is_help=True)
@click.option('-P', '--pager', 'pager', is_flag=True, help='分页显示查询结果')
@click.option('-g', '--general', 'general', is_flag=False, flag_value='all', multiple=True, help='查询干员基本信息')
@click.option('-a', '--attr', 'attr', is_flag=True, help='查询干员属性')
@click.option('-t', '--talent', 'talent', is_flag=True, help='查询干员天赋')
@click.option('-s', '--skill', 'skill', is_flag=False, flag_value=0, multiple=True, type=int, help='查询干员技能')
@click.option('-r', '--rank', 'rank', default=[0], multiple=True, type=int, help='查询特定等级的技能')
@click.option('-u', '--upgrade', 'upgrade', flag_value='upgrade', help='显示技能升级/精英化所需材料')
@click.option('-U', '--upgrade-only', 'upgrade', flag_value='upgrade_only', help='仅显示技能升级/精英化所需材料')
@click.option('-e', '--elite', 'elite', is_flag=False, flag_value=2, type=click.IntRange(0, 2),
              help='查询干员精英化之后的属性数据')
@click.option('-m', '--module', 'module', is_flag=True, help='查询干员模组')
@click.argument('operator', nargs=1, required=False)
def wiki(pager, general, attr, talent, skill, rank, upgrade, elite, module, operator):
    """查询干员信息"""

    if not operator:
        click.echo('请添加需要查询的干员名称或别名之后重试')
        return
    if data_path.joinpath(f'{operator}.toml') in data_path.iterdir():
        operator_path = f'{operator}.toml'
    else:
        with open(config_path, 'rb') as config_file:
            config: dict = tomli.load(config_file)
        with open(names_path, 'rb') as names_file:
            names: dict = tomli.load(names_file)
        if operator in names:
            operator_path = f'{names[operator]}.toml'
        elif operator in config['alias']:
            operator_path = f'{config["alias"][operator]}.toml'
        else:
            click.echo(f'未找到名叫或别名为{operator}的干员')
            return
    with open(data_path.joinpath(operator_path), 'rb') as operator_file:
        operator_dict = tomli.load(operator_file)

    output = {}

    if 'all' in general:
        output['干员信息'] = operator_dict['干员信息']
    elif general:
        output['干员信息'] = {}
        for query in set(general):
            try:
                output['干员信息'][query] = operator_dict['干员信息'][query]
            except KeyError:
                click.echo(f'未找到干员的**{query}**属性')
                continue
    else:
        pass

    if attr:
        output['属性'] = operator_dict['属性']
    if talent:
        output['天赋'] = operator_dict['天赋']

    if elite in (0, 1, 2):
        section = output[f'精英{elite}'] = {}
        section['部署费用'] = operator_dict['属性']['部署费用']
        section['阻挡数'] = operator_dict['属性']['阻挡数']
        for key, value in operator_dict['属性'].items():
            if key.startswith(f'精英{elite}'):
                section[key] = value
        if upgrade:
            if upgrade == 'upgrade_only':
                section.clear()
            if elite == 0:
                click.echo('晋升至精英0不需要精英化材料')
            else:
                try:
                    section['精英化材料'] = operator_dict['精英化材料'][f'精{elite}']
                except KeyError:
                    click.echo(f'该干员无法晋升至精英{elite}')

    if skill:
        kanji = {1: '一', 2: '二', 3: '三'}
        section = output['技能'] = {}
        if 0 in skill:
            if operator_dict['干员信息']['稀有度'] in '01':
                click.echo('一星和二星干员无技能')
                del output['技能']
            for sk in kanji.values():
                try:
                    section[f'{sk}'] = operator_dict[f'{sk}技能']
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
                        section[f'{kanji[sk]}技能'] = operator_dict[f'{kanji[sk]}技能']
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
                            section[f'{kanji[sk]}'][str(r)] = operator_dict[f'{kanji[sk]}技能'][str(r)]
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
                        section[sk][r]['升级材料'] = operator_dict['技能升级材料'][str(r)]
                    elif int(r) > 7:
                        section[sk][r]['升级材料'] = operator_dict['技能升级材料'][f'{sk[0]}{r}']
                    else:
                        pass

    if module:
        output['模组'] = {k: v for k, v in operator_dict['模组'].items() if not k.startswith('材料消耗')}
        if upgrade:
            if upgrade == 'upgrade_only':
                output['模组'].clear()
            output['模组'].update({k: v for k, v in operator_dict['模组'].items() if k.startswith('材料消耗')})

    if pager:
        click.echo_via_pager(tomli_w.dumps(output).replace('"', ''))
    else:
        click.echo(tomli_w.dumps(output).replace('"', ''))
