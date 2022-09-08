import re


def parse(source: str) -> dict:
    operator = {}
    source = source[:source.index('==干员档案==')]

    def try_int(string):
        try:
            return int(string)
        except ValueError:
            return string

    def parse_section(section: str) -> None:
        operator[f'{section}'] = {}
        for attr in source[:source.index('\n}}')].split('\n')[1:]:
            pair = attr.split('=')
            try:
                v = try_int(pair[1])
            except IndexError:
                continue
            k = pair[0].lstrip('|')
            operator[f'{section}'][k] = v

    def parse_skill(skill: str, start: int) -> None:
        end = source.index('\n}}', start)
        text = source[start:end + 1]
        operator[skill] = {}
        attrs = ('技能名', '技能类型1', '技能类型2')
        for attr in attrs:
            try:
                operator[skill][attr] = re.search(rf'\|{attr}=(.*)\n', text).group(1)
            except AttributeError:
                continue
        for level in '1234567':
            operator[skill][level] = {}
            for attr in ('描述', '初始', '消耗', '持续'):
                value = re.search(rf'\|技能{level}{attr}=(.*)\n', text).group(1)
                operator[skill][level][attr] = try_int(value)
        if rarity in '345':
            for level in ('8', '9', '10'):
                operator[skill][level] = {}
                for attr in ('描述', '初始', '消耗', '持续'):
                    value = re.search(rf'\|技能专精{int(level) - 7}{attr}=(.*)\n', text).group(1)
                    operator[skill][level][attr] = try_int(value)

    # Remove HTML tags from source
    tags = ('<ref.*?ref>', '<.*?>')
    for tag in tags:
        source = re.sub(re.compile(tag), '', source)

    # Remove style notations from source
    def extract(match):
        return re.search(r'\|.*?\|(.*?)}}', match.group(0)).group(1)

    notations = (r'{{color\|.*?}}', r'{{\*\|.*?}}', r'{{\*\*\|.*?}}',
                 r'{{\+\|.*?}}', r'{{术语\|.*?}}')
    for notation in notations:
        source = re.sub(notation, extract, source)
        # TODO
        # source = re.sub('{{修正\|.*?}}', extract, source)

    keys = ('干员名', '干员外文名', '情报编号', '特性', '稀有度', '职业', '分支', '位置', '标签',
            '画师', '日文配音')
    operator['干员信息'] = {}
    for key in keys:
        if result := re.search(rf'\|{key}=(.*)\n', source):
            operator['干员信息'][key] = result.group(1)

    rarity = operator['干员信息']['稀有度']

    source = source[source.index('{{属性'):]
    parse_section('属性')
    for key in ('潜能', '潜能类型', "初始模组名", "模组1名", "模组1数据",
                "模组2名", "模组2数据"):
        try:
            del operator['属性'][key]
        except KeyError:
            continue

    source = source[source.index('{{天赋'):]
    parse_section('天赋')

    try:
        source = source[source.index('{{潜能提升'):]
        parse_section('潜能提升')
    except ValueError:
        pass

    if rarity in '01':
        return operator

    source = source[source.index('==技能=='):]
    skill1 = source.index('技能1（精英0开放）')
    parse_skill('一技能', skill1)

    operator['技能升级材料'] = {}

    def parse_rank(levels):
        for level in levels:
            operator['技能升级材料'][level] = {}
            items = re.search(rf'\|{level}=(.*)\n', source).group(1).split()
            for item in items:
                k = item.split('|')[1]
                v = item.split('|')[2].rstrip('}')
                operator['技能升级材料'][level][k] = try_int(v)

    parse_rank('234567')
    if rarity in '345':
        parse_rank(('一8', '一9', '一10', '二8', '二9', '二10'))
    if rarity == '5':
        parse_rank(('三8', '三9', '三10'))

    operator['精英化材料'] = {}

    def parse_elite(stage: str) -> None:
        operator['精英化材料'][f'{stage}'] = {}
        items = re.search(rf'\|{stage}=(.*)\n', source).group(1).split(' ')
        for item in items:
            k = item.split('|')[1]
            v = item.split('|')[2].rstrip('}')
            operator['精英化材料'][f'{stage}'][k] = try_int(v)

    parse_elite('精1')
    if rarity == '2':
        return operator

    parse_elite('精2')

    skill2 = source.index('技能2（精英1开放）')
    parse_skill('二技能', skill2)

    if rarity in '34':
        return operator

    skill3 = source.index('技能3（精英2开放）')
    parse_skill('三技能', skill3)

    return operator
