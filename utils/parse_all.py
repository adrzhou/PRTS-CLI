import pathlib
import tomli
import tomli_w
from parser import parse


package_path = pathlib.Path(__file__).parents[1]
source_path = package_path.joinpath('temp')
data_path = package_path.joinpath('data')
catalog_path = package_path.joinpath('catalog.toml')
names_path = package_path.joinpath('names_cn.toml')

with open(catalog_path, 'rb') as catalog_file:
    catalog: dict = tomli.load(catalog_file)

with open(names_path, 'rb') as names_file:
    names: dict = tomli.load(names_file)

for source in source_path.iterdir():
    with open(source) as source_file:
        source_text = source_file.read()
    try:
        operator: dict = parse(source_text)
    except ValueError:
        print(f'{source.stem} 解析失败')
        continue
    op_filename = operator['干员信息']['干员外文名'].replace(' ', '_')
    output_path = data_path.joinpath(f"{op_filename}.toml")
    with open(output_path, 'wb') as file:
        tomli_w.dump(operator, file)
    names[f"{operator['干员信息']['干员名']}"] = op_filename
    op_class = operator['干员信息']['职业']
    op_subclass = operator['干员信息']['分支']
    if op_class not in catalog:
        catalog[op_class] = {}
    if op_subclass not in catalog[op_class]:
        catalog[op_class][op_subclass] = {}
    catalog[op_class][op_subclass][f"{operator['干员信息']['干员名']}"] = op_filename

with open(catalog_path, 'wb') as catalog_file:
    tomli_w.dump(catalog, catalog_file)
with open(names_path, 'wb') as names_file:
    tomli_w.dump(names, names_file)
