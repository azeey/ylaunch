#!/usr/bin/env python
# encoding: utf-8

# Copyright (c) 2014  Addisu Z. Taddese
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import argparse
import yaml
import copy
import shlex
import subprocess
import os

def create_config(ydict):
    """Populates a new dict using data and inheritance in the yaml config file

    :ydict: Parsed yaml dictionary
    :returns: Populated dict

    """
    proc_config = []
    for key, yconf_items in ydict.items():
        #print key
        #print yconf_items
        # Check if inheriting
        has_inheritance = False
        config = None
        if 'base' in yconf_items:
            config = copy.deepcopy(ydict[yconf_items['base']])
            has_inheritance = True
        else:
            config = copy.deepcopy(yconf_items)

        config['name'] = key

        # We need the keys to be present so we don't throw an unnecessary exception
        if 'cmd' not in config:
            config['cmd'] = yconf_items['cmd']

        if 'args' not in config:
            config['args'] = yconf_items.get('args',[])

        config['display'] = yconf_items.get('display', True)

        if has_inheritance:
            # Go through the args of the instance and override whatever it
            # inherited from the base
            for arg_obj in yconf_items.get('args',[]):
                if isinstance(arg_obj, dict):
                    for arg_key in arg_obj:
                        # Search for the key in config['args']. Not the most
                        # effient way to do this.
                        arg_key_found = False
                        for elem in config['args']:
                            if arg_key in elem:
                                arg_key_found = True
                                # Replace value
                                elem[arg_key] = arg_obj[arg_key]
                                break
                        if not arg_key_found:
                            config['args'].append(arg_obj)
                else:
                    # If not a dict, search for the element in the base args array
                    if not arg_obj in config['args']:
                        config['args'].append(arg_obj)

        proc_config.append(config)
        #print "Config", config
        #print "Proc Config", proc_config

    return proc_config

def create_cmds(config, extra_args):
    """Takes a populated config file and generates a command for each entry

    :config: @todo
    :returns: @todo

    """

    cmds = []
    for item in config:
        if item['display']:
            cmdline = item['cmd']
            for arg_obj in item['args']:
                if isinstance(arg_obj, dict):
                    for arg_key,arg_item in arg_obj.items():
                        cmdline += " {} {}".format(arg_key, arg_item)
                else:
                    cmdline += " {}".format(arg_obj)

            #print key, cmdline

            # Add extra args
            cmdline += " " + " ".join(extra_args)
            cmds.append((item['name'], cmdline))

    return cmds

def cmd_ui(cmds, ylaunch_args):
    """UI for selecting command

    :cmds: @todo
    :returns: @todo

    """
    if ylaunch_args.run is None:
        for i,item in enumerate(cmds):
            name, cmd = item
            print i, name, cmd

    try:
        if ylaunch_args.run is not None:
            which_cmd = ylaunch_args.run
        else:
            which_cmd = int(raw_input("Select command:"))
        #cmd = shlex.split(cmds[i])
        name, cmd = cmds[which_cmd]

        print
        print name, cmd
        os.system(cmd)
    except Exception as e:
        print "Can't run command"
        print e


def main():
    parser = argparse.ArgumentParser(description='YAML based command launcher')
    parser.add_argument('file', metavar='FILE', help='YAML file')
    parser.add_argument('-r', '--run', type=int, help='Run command without selection prompt')
    ylaunch_args, extra_args = parser.parse_known_args()
    ydict = yaml.load(open(ylaunch_args.file,'r'))

    proc_config = create_config(ydict)
    #print proc_config
    cmds = create_cmds(proc_config, extra_args)
    cmd_ui(cmds, ylaunch_args)


if __name__ == '__main__':
    main()
