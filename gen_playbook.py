#!/usr/bin/python

import os
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

tests=[]
wd=os.getcwd()
for directory, dirnames, filenames in os.walk(wd):
    if 'runtest.sh' in filenames:
        tests.append(os.path.relpath(directory))

playbook = [UnsortableOrderedDict([
    ('hosts', 'localhost'),
    ('tags', ['classic', 'container', 'atomic']),
    ('roles', [UnsortableOrderedDict([
        ('role', 'standard-test-beakerlib'),
        ('tests', sorted(tests)),
        ('required_packages', [])
    ])])
])]

#print playbook
print yaml.dump(playbook,default_flow_style=False)
