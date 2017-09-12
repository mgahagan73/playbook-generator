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
    packages = []
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

# https://github.com/fedora-modularity/baseruntime-package-lists/blob/master/data/Fedora/devel/atomic/atomic.yaml
def GetAtomicPackages():
    basedir = os.path.abspath(os.path.dirname(sys.argv[0]))
    with open(os.path.join(basedir, "atomic.yaml"), "r") as fh:
        return yaml.load(fh)['data']['components']['rpms'].keys()

def FilterPackages(pkgs=[], pkg_list=[]):
    """ Return true iff all items in pkgs are found in pkg_list """
    for p in pkgs:
        if p not in pkg_list:
            return False
    return True

packages = []
atomic_packages=GetAtomicPackages()
test = {}
tests_classic=[]
tests_container=[]
tests_atomic=[]
wd=os.getcwd()
for directory, dirnames, filenames in os.walk(wd):
    if 'runtest.sh' in filenames:
        test[os.path.relpath(directory)] = []
    if 'Makefile' in filenames:
        test[os.path.relpath(directory)] = GetRequires(os.path.relpath(directory) + "/Makefile")

for k in test.keys():
    if FilterPackages(test[k], atomic_packages):
        tests_atomic.append(k)
    tests_classic.append(k)
    tests_container.append(k)
    packages.extend(test[k])

tagged_tests = {}

tagged_tests['classic'] = list(tests_classic)

tagged_tests['container'] = list(tests_container)

tagged_tests['atomic'] = list(tests_atomic)

test_tags = ['classic', 'container', 'atomic']
if not tagged_tests['atomic']:
    test_tags.remove('atomic')
if not tagged_tests['container']:
    test_tags.remove('container')

playbook = []
for tag in test_tags:
    role = [('role', 'standard-test-beakerlib'),
            ('tests', sorted(tagged_tests[tag]))]
    if tag != 'atomic':
        role.append(('required_packages', sorted(list(set(packages)))))

    playbook.append(UnsortableOrderedDict([
        ('hosts', 'localhost'),
        ('tags', [tag]),
        ('roles', [UnsortableOrderedDict(role)])
    ]))

print yaml.dump(playbook, default_flow_style=False)
