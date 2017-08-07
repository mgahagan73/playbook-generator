#!/usr/bin/python

import os
import yaml

playbook = [{'hosts': 'localhost',
             'tags': ['classic', 'container', 'atomic'],
             'roles': [{'role': 'standard-test-beakerlib',
                        'tests': [],
                        'required_packages': []}]
           }]
tests=[]
wd=os.getcwd()
for directory, dirnames, filenames in os.walk(wd):
    if 'runtest.sh' in filenames:
        tests.append(os.path.relpath(directory))
playbook[0]['roles'][0]['tests'] = tests

#print playbook
print yaml.dump(playbook,default_flow_style=False)
