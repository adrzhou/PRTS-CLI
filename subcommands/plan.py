import click
import tomli
import tomli_w
import pathlib
from tabulate import tabulate
from utils.load_dict import load_dict
from utils.formulae import formulae

package_path = pathlib.Path(__file__).parents[1]
config_path = package_path.joinpath('config.toml')
names_path = package_path.joinpath('names_cn.toml')
profile_path = package_path.joinpath('profile.toml')
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
@click.option('-i', '--inventory', 'inventory', is_flag=True, help='查询或更新仓库内材料数量')
def plan(args, synth, optimal, up, inventory):
    """查询干员升级所需材料"""

    with open(config_path, 'rb') as config_file:
        config = tomli.load(config_file)
    with open(profile_path, 'rb') as pro_file:
        profile = tomli.load(pro_file)

    if up:
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

    summary = {}
    for oprt, tracker in profile['tracker'].items():
        cur_op = summary[oprt] = {}
        status = tracker['目前']
        goal = tracker['目标']
        op_dict = load_dict(oprt)
        set_need(cur_op, status, goal, op_dict)

        for skill, req in cur_op.items():
            if not req:
                continue
            if synth:
                decompose(req, profile)
            header = [f'{oprt}.{skill}', '总需', '库存', '还需']
            rows = []
            for mtrl in req:
                need = req[mtrl]
                have = profile['inventory'][mtrl]['amount']
                farm = max(need - have, 0)
                rows.append([mtrl, need, have, farm])
            click.echo(tabulate(rows, headers=header, tablefmt='github'))
            click.echo('\n')


def set_need(cur_op: dict, status: dict, goal: dict, op_dict: dict):
    for skill, level in status.items():
        while level < goal[skill]:
            level += 1
            key, value = '', {}
            if skill == '精英':
                key = f'精{level}'
                value = op_dict['精英化材料'][key]
            elif skill.endswith('技能'):
                if level <= 7:
                    key = f'技能升级材料{level}'
                    value = op_dict['技能升级材料'][str(level)]
                else:
                    key = f'{skill[0]}技能{level}'
                    value = op_dict['技能升级材料'][f'{skill[0]}{level}']
            elif skill == '模组':
                key = f'模组阶段{level}'
                if level == 1:
                    value = op_dict['模组']['材料消耗']
                else:
                    value = op_dict['模组'][f'材料消耗{level}']
            cur_op[key] = {k: v for k, v in value.items()
                           if k not in exclude
                           and not k.endswith('芯片')}


def decompose(skill: dict, profile: dict):
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
