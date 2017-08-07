#!/usr/bin/python

import os
import yaml

playbook={}
tests=[]
wd=os.getcwd()
for directory, dirnames, filenames in os.walk(wd):
    if 'runtest.sh' in filenames:
        tests.append(os.path.relpath(directory))
playbook['tests'] = tests

#print playbook
print yaml.dump(playbook,default_flow_style=False)
