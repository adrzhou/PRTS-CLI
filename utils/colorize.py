import re
import click


palette = {'龙门币': 'bright_blue', 'D32钢': 'bright_yellow', 'RMA70-24': 'bright_white'}


def colorize(source: str):
    source = source.split('\n')
    for i in range(len(source)):
        for mtrl, color in palette.items():
            def style(match):
                return click.style(match.group(0), fg=color)
            source[i] = re.sub(mtrl, style, source[i])
    return '\n'.join(source)
