import re
import click

palette = {'化合切削液': 'blue', '切削原液': 'bright_white', '半自然溶剂': 'blue', '精炼溶剂': 'bright_white',
           '晶体元件': 'blue', '晶体电路': 'bright_white', '晶体电子单元': 'bright_yellow', '炽合金': 'blue',
           '炽合金块': 'bright_white', '凝胶': 'blue', '聚合凝胶': 'bright_white', '双酮': 'white',
           '酮凝集': 'bright_green', '酮凝集组': 'blue', '酮阵列': 'bright_white', '异铁碎片': 'white',
           '异铁': 'bright_green', '异铁组': 'blue', '异铁块': 'bright_white', '代糖': 'white',
           '糖': 'bright_green', '糖组': 'blue', '糖聚块': 'bright_white', '酯原料': 'white',
           '聚酸酯': 'bright_green', '聚酸酯组': 'blue', '聚酸酯块': 'bright_white', '破损装置': 'white',
           '装置': 'bright_green', '全新装置': 'blue', '改量装置': 'bright_white', '源岩': 'white',
           '固源岩': 'bright_green', '固源岩组': 'blue', '提纯源岩': 'bright_white', 'RMA70-12': 'blue',
           'RMA70-24': 'bright_white', '研磨石': 'blue', '五水研磨石': 'bright_white', '轻锰矿': 'blue',
           '三水锰矿': 'bright_white', '扭转醇': 'blue', '白马醇': 'bright_white', '聚合剂': 'bright_yellow',
           '双极纳米片': 'bright_yellow', 'D32钢': 'bright_yellow', '龙门币': 'bright_blue',
           '技巧概要·卷1': 'bright_yellow', '技巧概要·卷2': 'green', '技巧概要·卷3': 'blue'}


def colorize(source: str):
    source = source.split('\n')
    for i in range(len(source)):
        for mtrl, color in palette.items():
            mtrl = f' {mtrl} '

            def style(match):
                return click.style(match.group(0), fg=color)

            source[i] = re.sub(mtrl, style, source[i])
    return '\n'.join(source)
