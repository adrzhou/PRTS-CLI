import re


def parse(source: str) -> dict:
    oprt = {}

    # Curtail source length to reduce workload of re.sub
    source = source[:source.index('==相关道具==')]

    # Substitute HTML line breaks with colons
    source = re.sub(re.compile(r'<br/>'), ' ', source)

    # Remove HTML tags and other annotations from source
    tags = ('<ref.*?ref>', '<.*?>', '&lt;', '&gt;', '{{±.*?}}', r'\[\[关卡一览.*?\]\]',
            '{{攻击范围.*?}}', r'{{fa\|plus-circle\|color.*?}}')
    for tag in tags:
        source = re.sub(re.compile(tag), '', source)

    # Remove style notations from source
    # DO NOT ATTEMPT TO OPTIMIZE THIS PART OF CODE
    # IT WILL STOP WORKING IF REFACTORED AS AN OUTER FUNCTION
    def extract(match):
        pattern = match.re.pattern
        if pattern in (r'{{color\|.*?}}', r'{{color\|.*?}}', r'{{\*\|.*?}}', r'{{\*\*\|.*?}}',
                       r'{{\+\|.*?}}', r'{{术语\|.*?}}', r'{{\+\+\|.*?}}'):
            return re.search(r'\|.*?\|(.*?)}}', match.group(0)).group(1)
        elif pattern == r'{{变动数值lite\|.*?\|蓝\|.*?}}':
            return re.search(r'\|蓝\|(.*?)}}', match.group(0)).group(1)
        elif pattern == r'{{变动数值lite\|\|橙\|.*?}}':
            return re.search(r'\|橙\|(.*?)}}', match.group(0)).group(1)
        elif pattern == '{{修正.*?}}':
            return re.search(r'{{修正\|(.*?)\|.*?}}', match.group(0)).group(1)

    notations = (r'{{color\|.*?}}',
                 r'{{color\|.*?}}',
                 r'{{\*\|.*?}}',
                 r'{{\*\*\|.*?}}',
                 r'{{\+\|.*?}}',
                 r'{{术语\|.*?}}',
                 r'{{\+\+\|.*?}}',
                 r'{{变动数值lite\|.*?\|蓝\|.*?}}',
                 r'{{变动数值lite\|\|橙\|.*?}}', '{{修正.*?}}')

    for notation in notations:
        source = re.sub(notation, extract, source)

    parse_general(source, oprt)
    parse_attr(source, oprt)
    parse_talent(source, oprt)
    parse_potential(source, oprt)

    rarity = oprt['干员信息']['稀有度']
    if rarity in '01':
        return oprt

    oprt['精英化材料'] = {}
    parse_skill(source, '一技能', oprt)
    parse_rank_mtrl(source, oprt)
    parse_elite_mtrl(source, '精1', oprt)

    if rarity == '2':
        return oprt

    parse_elite_mtrl(source, '精2', oprt)
    parse_skill(source, '二技能', oprt)

    # 解析干员模组信息
    def parse_module():
        begin = source.index('{{模组')
        begin = source.index('{{模组', begin + 4)
        end = source.index('\n}}', begin)
        module_text = source[begin:end]
        oprt['模组'] = {}
        for attr in module_text.split('\n'):
            pair = attr.split('=')
            try:
                v = try_int(pair[1])
            except IndexError:
                continue
            k = pair[0].lstrip('|')
            oprt['模组'][k] = v
        for attr in ('类型颜色', '特性追加', '基础信息'):
            try:
                del oprt['模组'][attr]
            except KeyError:
                continue
        for level in ("材料消耗", "材料消耗2", "材料消耗3"):
            materials = oprt['模组'][level].split(' ')
            oprt['模组'][level] = {}
            for item in materials:
                k = item.split('|')[1]
                v = item.split('|')[2].rstrip('}')
                oprt['模组'][level][k] = try_int(v)

    try:
        parse_module()
    except ValueError:
        pass

    # TODO: Parse operators with multiple modules

    if rarity in '34':
        return oprt

    parse_skill(source, '三技能', oprt)
    return oprt


def try_int(string):
    try:
        return int(string)
    except ValueError:
        return string


def parse_general(source: str, oprt: dict) -> None:
    general = oprt['干员信息'] = {}

    keys = ('干员名', '干员外文名', '情报编号', '特性',
            '稀有度', '职业', '分支', '位置', '标签',
            '画师', '日文配音')

    for key in keys:
        if result := re.search(rf'\|{key}=(.*)\n', source):
            general[key] = result.group(1)


def parse_attr(source: str, oprt: dict) -> None:
    attr = oprt['属性'] = {}

    start = source.index('{{属性')
    end = source.index('\n}}', start)
    section = source[start:end]

    for line in section.split('\n')[1:]:
        pair = line.split('=')
        try:
            v = try_int(pair[1])
        except IndexError:
            continue
        k = pair[0].lstrip('|')
        attr[k] = v

    for k in ('潜能', '潜能类型', '初始模组名', '模组1名',
              '模组1数据', '模组2名', '模组2数据'):
        attr.pop(k, None)


def parse_talent(source: str, oprt: dict) -> None:
    talent = oprt['天赋'] = {}

    start = source.index('{{天赋')
    end = source.index('\n}}', start)
    section = source[start:end]

    for line in section.split('\n')[1:]:
        pair = line.split('=')
        try:
            v = try_int(pair[1])
        except IndexError:
            continue
        k = pair[0].lstrip('|')
        talent[k] = v

    talent.pop('备注', None)


def parse_potential(source: str, oprt: dict) -> None:
    potential = oprt['潜能提升'] = {}

    try:
        start = source.index('{{潜能提升')
    except ValueError:
        return
    end = source.index('\n}}', start)
    section = source[start:end]

    for line in section.split('\n')[1:]:
        pair = line.split('=')
        try:
            v = try_int(pair[1])
        except IndexError:
            continue
        k = pair[0].lstrip('|')
        potential[k] = v


def parse_skill(source: str, skill: str, oprt: dict) -> None:
    if skill == '一技能':
        start = source.index('技能1（精英0开放）')
    elif skill == '二技能':
        start = source.index('技能2（精英1开放）')
    else:
        start = source.index('技能3（精英2开放）')

    end = source.index('\n}}', start)
    section = source[start:end + 1]

    rarity = oprt['干员信息']['稀有度']
    data = oprt[skill] = {}
    keys = ('技能名', '技能类型1', '技能类型2')
    for key in keys:
        try:
            data[key] = re.search(rf'\|{key}=(.*)\n', section).group(1)
        except AttributeError:
            continue
    for level in '1234567':
        data[level] = {}
        for key in ('描述', '初始', '消耗', '持续'):
            value = re.search(rf'\|技能{level}{key}=(.*)\n', section).group(1)
            data[level][key] = try_int(value)
    if rarity in '345':
        for level in ('8', '9', '10'):
            data[level] = {}
            for key in ('描述', '初始', '消耗', '持续'):
                value = re.search(rf'\|技能专精{int(level) - 7}{key}=(.*)\n', section).group(1)
                data[level][key] = try_int(value)


def parse_rank_mtrl(source: str, oprt: dict):
    rank_mtrl = oprt['技能升级材料'] = {}
    rarity = oprt['干员信息']['稀有度']
    levels = '2 3 4 5 6 7'.split()
    if rarity in '345':
        levels.extend(('一8', '一9', '一10', '二8', '二9', '二10'))
    if rarity == '5':
        levels.extend(('三8', '三9', '三10'))
    for level in levels:
        data = rank_mtrl[level] = {}
        items = re.search(rf'\|{level}=(.*)\n', source).group(1).split()
        for item in items:
            k = item.split('|')[1]
            v = item.split('|')[2].rstrip('}')
            data[k] = try_int(v)


def parse_elite_mtrl(source: str, stage: str, oprt: dict):
    data = oprt['精英化材料'][stage] = {}
    items = re.search(rf'\|{stage}=(.*)\n', source).group(1).split(' ')
    for item in items:
        k = item.split('|')[1]
        v = item.split('|')[2].rstrip('}')
        data[k] = try_int(v)
