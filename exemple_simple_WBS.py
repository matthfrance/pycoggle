# -*- coding: utf-8 -*-

import os
import imp
from pycoggle.pycoggle import *


config_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "exemple_simple_WBS_config.py")
config = imp.load_source('exempleWBS', config_file_path)

diagram_name = "test"
access_token = 'xxx'

coggle = CoggleApi(access_token)

mindmap = coggle.diagrams[diagram_name]
mindmap.clear()


tree_start_level = 1
tree_nodes_startswith = "2"

for code, node in config.tree_data.items():
    text = code + ' ' + node["name"]
    if code.count('.') < tree_start_level or not code.startswith(tree_nodes_startswith):
        continue
    if code.count('.') == tree_start_level:
        parent = None
    else:
        aa = code.rindex('.')
        parent = config.tree_data[code[0:aa]]["object"]
    node["object"] = mindmap.create_node(text, parent)

for code, node in config.tree_data.items():
    if code.count('.') < tree_start_level or not code.startswith(tree_nodes_startswith):
        continue
    if node['dependencies'] == "":
        node['dependencies'] = None
        continue
    else:
        dependencies_list = node['dependencies'].split(',')
        node['dependencies'] = []
        for dependency in dependencies_list:
            if 'object' in config.tree_data[dependency.strip()]:
                node['dependencies'].append( config.tree_data[dependency.strip()]['object'].id )
            else:
                print('Dependency not found')

    for dependency in node['dependencies']:
        if not dependency:
            print('dependency not found')
            continue
        text = code + ' ' + node["name"] + ' [#](#{0})'.format(dependency)
        node["object"].text = text

mindmap.arrange()

exit(0)
