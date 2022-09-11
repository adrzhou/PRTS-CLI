import click
import pathlib


package_path = pathlib.Path(__file__).parents[1]
config_path = package_path.joinpath('config.toml')
names_path = package_path.joinpath('names_cn.toml')
profile_path = package_path.joinpath('profile.toml')
data_path = package_path.joinpath('data')


@click.command()
@click.argument('operator', nargs=-1, required=False)
@click.option('-s', '--synth', 'synth', is_flag=True,
              help='用合成所需材料代替蓝色品质以上的材料')
@click.option('-o', '--optimal', 'optimal', is_flag=True,
              help='将待升级项目按材料收集进度排序')
@click.option('-u', '--up', 'up', help='设定当期活动概率UP的材料')
@click.option('-i', '--inventory', 'inventory', help='查询或更新仓库内材料数量')
def plan(operator, synth, optimal, up, inventory):
    """查询干员升级所需材料"""


