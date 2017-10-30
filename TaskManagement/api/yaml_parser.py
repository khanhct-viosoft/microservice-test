import yaml
import  logging

if hasattr(yaml, 'CSafeLoader'):
    # make a dynamic subclass so we don't override global yaml Loader
    yaml_loader = type('CustomLoader', (yaml.CSafeLoader,), {})
else:
    yaml_loader = type('CustomLoader', (yaml.SafeLoader,), {})

if hasattr(yaml, 'CSafeDumper'):
    yaml_dumper = yaml.CSafeDumper
else:
    yaml_dumper = yaml.SafeDumper

def yaml_load(tmpl_str):
    return yaml.load(tmpl_str, Loader=yaml_loader)

def read_desc_file(file_path):
    """Read from config file"""
    with open(file_path) as stream:
        desc = yaml_load(stream)
    return desc

def parse_yaml(desc, codition):
    return desc[codition]








