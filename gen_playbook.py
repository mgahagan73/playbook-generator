#!/usr/bin/python

import os
import sys
import yaml
from collections import OrderedDict

# Add hooks so YAML dictionaries can be dumped in the order of our choosing
# https://stackoverflow.com/questions/16782112/can-pyyaml-dump-dict-items-in-non-alphabetical-order


class UnsortableList(list):

    def sort(self, *args, **kwargs):
        pass


class UnsortableOrderedDict(OrderedDict):

    def items(self, *args, **kwargs):
        return UnsortableList(OrderedDict.items(self, *args, **kwargs))

yaml.add_representer(UnsortableOrderedDict,
                     yaml.representer.SafeRepresenter.represent_dict)

def GetRequires(makefile=None):
    if not makefile:
        raise IOError("/path/to/Makefile is required for GetRequires")
    with open(makefile) as f:
        for line in f:
            if "Requires:" in line:
                key, sep, value = line.partition(":")
                if '$(PACK' in value:
                    pass
                else:
                    packages.extend(value.split('"')[0].lstrip().split(" "))
    return packages

def GetAtomicPackages():
    basedir = os.path.abspath(os.path.dirname(sys.argv[0]))
    with open(os.path.join(basedir, "atomic.yaml"), "r") as fh:
        return yaml.load(fh)['data']['components']['rpms'].keys()

atomic_packages=GetAtomicPackages()
tests=[]
packages=[]
wd=os.getcwd()
for directory, dirnames, filenames in os.walk(wd):
    if 'runtest.sh' in filenames:
        tests.append(os.path.relpath(directory))
    if 'Makefile' in filenames:
        GetRequires(os.path.relpath(directory) + "/Makefile")


playbook = [UnsortableOrderedDict([
    ('hosts', 'localhost'),
    ('tags', ['classic', 'container', 'atomic']),
    ('roles', [UnsortableOrderedDict([
        ('role', 'standard-test-beakerlib'),
        ('tests', sorted(tests)),
        ('required_packages', sorted(list(set(packages))))
    ])])
])]

print yaml.dump(playbook,default_flow_style=False)
