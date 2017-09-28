#!/usr/bin/python2.7

import os
import httplib
import re
import shutil
import argparse
import ConfigParser
import json
import sys
import time
import requests
import urlparse
import urllib
from jinja2 import Environment, FileSystemLoader

def jinja_render(job):
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('lava-build/single-defconfig-build.jinja2')
    return template.render(job)

def parse_prop(prop):
    data = {}
    with open(prop) as f:
        content = f.readlines()
    for line in content:
        bits = line.rstrip().split('=', 1)
        data[bits[0].lower()] = bits[1]
    data['defconfig_list'] = data['defconfig_list'].split(' ')
    return data

def main(args):
    data = parse_prop(args.get('properties'))
    job_dir = '%s-%s-%s-%s' % (data['tree_name'], data['branch'], data['git_describe'], data['arch'])
    if not os.path.exists(job_dir):
        os.mkdir(job_dir)
    for defconfig in data['defconfig_list']:
        job = {}
        defconfig_name = defconfig
        if 'kselftest' in defconfig:
            defconfig_name = defconfig.replace('/','_')
        job['name'] = "kci-%s-%s" % (job_dir, defconfig_name)
        job_file = job_dir + '/' + job['name'] + '.yaml'
        job['defconfig'] = defconfig
        job['api'] = args.get('api')
        job['token'] = args.get('token')
        job.update(data)
        with open(job_file, 'w') as f:
            f.write(jinja_render(job))
        print "Job written: %s" % job_file


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--properties", help="Defconfig builder properties file", required=True)
    parser.add_argument("--api", help="KernelCI API", required=True)
    parser.add_argument("--token", help="KernelCI API token", required=True)
    parser.add_argument("--priority", choices=['high', 'medium', 'low', 'HIGH', 'MEDIUM', 'LOW'],
                        help="priority for LAVA jobs", default='high')
    args = vars(parser.parse_args())
    if args:
        main(args)
    else:
        exit(1)
