import pathlib
import tomli

package_path = pathlib.Path(__file__).parents[1]
config_path = package_path.joinpath('config.toml')
names_path = package_path.joinpath('reserved_names.toml')
data_path = package_path.joinpath('data')

with open(config_path, 'rb') as config_file:
    config = tomli.load(config_file)
with open(names_path, 'rb') as names_file:
    names = tomli.load(names_file)


def load_dict(op: str) -> dict:
    if data_path.joinpath(f'{op}.toml') in data_path.iterdir():
        op_path = f'{op}.toml'
    elif op in names:
        op_path = f'{names[op]}.toml'
    elif op in config['alias']:
        op_path = f'{config["alias"][op]}.toml'
    else:
        raise KeyError
    with open(data_path.joinpath(op_path), 'rb') as op_file:
        return tomli.load(op_file)
