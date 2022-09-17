import click
import tomli
import tomli_w
import pathlib
from tabulate import tabulate
from utils.loader import load_oprt
from utils.formulae import formulae
from utils.colorize import colorize

package_path = pathlib.Path(__file__).parents[1]
config_path = package_path.joinpath('usr', 'config.toml')
names_path = package_path.joinpath('usr', 'reserved_names.toml')
profile_path = package_path.joinpath('usr', 'profile.toml')
data_path = package_path.joinpath('data')

exclude = ('龙门币', '技巧概要·卷1', '技巧概要·卷2', '技巧概要·卷3',
           '模组数据块', '数据增补仪', '数据增补条')


@click.command()
@click.argument('args', nargs=-1, required=False)
@click.option('-s', '--synth', 'synth', is_flag=True,
              help='用合成所需材料代替蓝色品质以上的材料')
@click.option('-o', '--optimal', 'optimal', is_flag=True,
              help='将待升级项目按材料收集进度排序')
@click.option('-u', '--up', 'up', is_flag=True, help='设定当期活动概率UP的材料')
@click.option('--clear', 'clear', is_flag=True, help='重置当期活动概率UP的材料')
@click.option('-i', '--inventory', 'inventory', is_flag=True, help='查询或更新仓库内材料数量')
@click.option('-c', '--compact', 'compact', is_flag=True, help='将单个干员的所有项目合并')
def plan(args, synth, optimal, up, inventory, compact, clear):
    """查询干员升级所需材料"""

    with open(config_path, 'rb') as config_file:
        config = tomli.load(config_file)
    with open(profile_path, 'rb') as pro_file:
        profile = tomli.load(pro_file)

    if up:
        if clear:
            config['drop_rate_up'].clear()
            with open(config_path, 'wb') as config_file:
                tomli_w.dump(config, config_file)
            return
        if not args:
            for skill in config['drop_rate_up']:
                click.echo(skill)
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

    if inventory:
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

    if optimal:
        agg = {}
        for name, tracker in profile['tracker'].items():
            oprt = load_oprt(name)
            focused = ('等级6', '等级7', '技能8', '技能9', '技能10',
                       '阶段1', '阶段2', '阶段3', '精2')
            skills = collect(tracker, oprt)
            skills = {f'{name}.{k}': v for k, v in skills.items() if k.endswith(focused)}
            agg.update(skills)

        if config['drop_rate_up']:
            upped = config['drop_rate_up'].keys()
            comp_agg = compress(agg)
            convert(comp_agg, profile)
            comp_agg = {k: v for k, v in comp_agg.items() if k in upped}
            header = [f'材料', '总需', '库存', '还需']
            rows = []
            for mtrl, amount in comp_agg.items():
                need = amount
                have = profile['inventory'][mtrl]['amount']
                farm = max(need - have, 0)
                rows.append([mtrl, need, have, farm])
            table = tabulate(rows, headers=header, tablefmt='presto')
            table = colorize(table)
            click.echo(f'{table}\n')

        diffs = {}
        for k, v in agg.items():
            convert(v, profile)
            diffs[k] = diff(v, profile, config)

        def get_diff(k):
            return diffs[k]

        ascending = {k: agg[k] for k in sorted(agg.keys(), key=get_diff)}
        for skill, recipe in ascending.items():
            header = [skill, '总需', '库存', '还需']
            rows = []
            for mtrl in recipe:
                need = recipe[mtrl]
                have = profile['inventory'][mtrl]['amount']
                farm = max(need - have, 0)
                rows.append([mtrl, need, have, farm])
            table = tabulate(rows, headers=header, tablefmt='presto')
            table = colorize(table)
            click.echo(f'{table}\n')
        return

    for name, tracker in profile['tracker'].items():
        oprt = load_oprt(name)
        skills = collect(tracker, oprt)
        if compact:
            skills = compress(skills)
            if synth:
                convert(skills, profile)
            header = [f'{name}', '总需', '库存', '还需']
            rows = []
            for mtrl, amount in skills.items():
                need = amount
                have = profile['inventory'][mtrl]['amount']
                farm = max(need - have, 0)
                rows.append([mtrl, need, have, farm])
            table = tabulate(rows, headers=header, tablefmt='presto')
            table = colorize(table)
            click.echo(f'{table}\n')
        else:
            for skill, recipe in skills.items():
                if not recipe:
                    continue
                if synth:
                    convert(recipe, profile)
                header = [f'{name}\n{skill}', '总需', '库存', '还需']
                rows = []
                for mtrl in recipe:
                    need = recipe[mtrl]
                    have = profile['inventory'][mtrl]['amount']
                    farm = max(need - have, 0)
                    rows.append([mtrl, need, have, farm])
                table = tabulate(rows, headers=header, tablefmt='presto')
                table = colorize(table)
                click.echo(f'{table}\n')


def collect(tracker: dict, oprt: dict):
    status = tracker['目前']
    goal = tracker['目标']
    entries = {}

    for skill, level in status.items():
        while level < goal[skill]:
            level += 1
            if skill == '精英':
                key = f'精{level}'
                value = oprt['精英化材料'][key]
            elif skill.endswith('技能'):
                if level <= 7:
                    key = f'技能等级{level}'
                    value = oprt['技能升级材料'][str(level)]
                else:
                    key = f'{skill[0]}技能{level}'
                    value = oprt['技能升级材料'][f'{skill[0]}{level}']
            else:
                key = f'{skill}.阶段{level}'
                if level == 1:
                    value = oprt['模组'][skill]['材料消耗']
                else:
                    value = oprt['模组'][skill][f'材料消耗{level}']
            entries[key] = {k: v for k, v in value.items()
                            if k not in exclude
                            and not k.endswith('芯片')}
    return entries


def compress(skills: dict):
    agg = {}
    for recipe in skills.values():
        for mtrl, amount in recipe.items():
            if mtrl not in agg:
                agg[mtrl] = amount
            else:
                agg[mtrl] += amount
    return agg


def convert(skill: dict, profile: dict):
    # 金色材料分解为银色材料
    for mtrl in tuple(skill.keys()):
        if int(profile['inventory'][mtrl]['rarity']) > 4:
            need = int(skill[mtrl]) - int(profile['inventory'][mtrl]['amount'])
            for k, v in formulae[mtrl].items():
                if k in skill.keys():
                    skill[k] += v * need
                else:
                    skill[k] = v * need
            del skill[mtrl]

    # 银色材料分解为蓝色材料
    for mtrl in tuple(skill.keys()):
        if int(profile['inventory'][mtrl]['rarity']) > 3:
            need = int(skill[mtrl]) - int(profile['inventory'][mtrl]['amount'])
            for k, v in formulae[mtrl].items():
                if k in skill.keys():
                    skill[k] += v * need
                else:
                    skill[k] = v * need
            del skill[mtrl]


def diff(skill: dict, profile: dict, config: dict):
    need = 0
    for mtrl, amount in skill.items():
        if profile['inventory'][mtrl]['rarity'] < 3:
            continue
        if mtrl in config['drop_rate_up']:
            continue
        have = profile['inventory'][mtrl]['amount']
        need += max(0, amount - have)
    return need
