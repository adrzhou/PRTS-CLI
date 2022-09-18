import subprocess
import click
import pathlib
import tomli
import tomli_w


package_path = pathlib.Path(__file__).parents[1]
job_path = package_path.joinpath('usr', 'job.toml')


@click.command(no_args_is_help=True)
@click.argument('sanity', nargs=1, type=int, required=False)
@click.option('-m', '--max', 'max_', type=int, help='设定理智上限')
def remind(sanity, max_):
    with open(job_path, 'rb') as job_file:
        job = tomli.load(job_file)

    if max_:
        if max_ <= 0:
            click.echo('理智上限必须大于0')
            return
        job['max_sanity'] = max_
        with open(job_path, 'wb') as job_file:
            tomli_w.dump(job, job_file)
    if 'max_sanity' not in job:
        click.echo('请设定理智上限')
        click.echo('命令格式: prts remind -m 理智上限')
        return
    else:
        max_ = job['max_sanity']
    if not sanity:
        return
    if (diff := max_ - sanity) > 0:
        after = diff * 6
        if last_jobid := job.get('last_id', None):
            hide = subprocess.getoutput(f'atrm {last_jobid}')
        schedule = subprocess.getoutput(f'at -f utils/alert.sh now +{after} minutes')
        job['last_id'] = schedule.split('\n')[1].split()[1]
        click.echo(f'PRTS将在{diff // 10}小时后推送通知')

    with open(job_path, 'wb') as job_file:
        tomli_w.dump(job, job_file)
