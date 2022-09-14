import pathlib
import tomli

package_path = pathlib.Path(__file__).parents[1]
config_path = package_path.joinpath('config.toml')
names_path = package_path.joinpath('reserved_names.toml')
data_path = package_path.joinpath('data')

with open(config_path, 'rb') as config_file:
    aliases = tomli.load(config_file)['alias']
with open(names_path, 'rb') as names_file:
    names = tomli.load(names_file)


def load_oprt(name: str) -> dict:
    """Helper function to load an operator's dictionary from a given name"""

    if stem := names.get(name, False):
        name = f'{stem}.toml'
    elif stem := aliases.get(name, False):
        stem = names[stem]
        name = f'{stem}.toml'
    elif stem := names.get(name.replace(' ', '_').lower(), False):
        name = f'{stem}.toml'
    else:
        raise KeyError
    with open(data_path.joinpath(name), 'rb') as op_file:
        return tomli.load(op_file)
