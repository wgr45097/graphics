#!/usr/bin/python3

import os
import subprocess, resource
from subprocess import PIPE
import tempfile
from itertools import chain
from time import sleep
import requests
import time
import datetime


# scenes and integrator for rendering the reference image
# scenes = [('cbox', 'path'), ('veach_bidir', 'path')]
scenes = [('veach_bidir', 'path')]


integrators = ['path', 'volpath', 'bdpt', 'pssmlt', 'mlt', 'erpt', 'sppm']
# integrators = integrators[6:]
# integrators = ['sppm']
# good_integrators = ['path', 'volpath']

def print_and_run_command(cmd):
    print(cmd)
    return subprocess.run(cmd, shell=True, executable="/bin/bash")

def insert_time_usage_log(scene, integrator, n_steps, cpu_time, retcode):
    requests.post('http://localhost:3000/log', json = {
        'scene': scene,
        'integrator': integrator,
        'n_steps': n_steps,
        'duration_seconds': cpu_time,
        'datetime': time.ctime(),
        'retcode': retcode,
    })

# -1 means infinite steps
def run_once(scene, integrator, n_steps):
    config_filename = './{}/{}.xml'.format(scene, scene)

    print_and_run_command("sed 's/REPLACE_INTEGRATOR/{}/' {} > {}".format(integrator, config_filename+'.template', config_filename))

    print_and_run_command("sed -i 's/REPLACE_MAX_DEPTH/{}/' {}".format(n_steps, config_filename))

    if integrator in ['pssmlt', 'mlt']:
        sampler = "independent" 
    else:
        sampler = "ldsampler"
    print_and_run_command("sed -i 's/REPLACE_SAMPLER/{}/' {}".format(sampler, config_filename))

    print_and_run_command("cp {} ./output/{}_{}.{}.xml".format(config_filename, scene, integrator, n_steps))

    retcode = 1
    count = 0
    while retcode != 0 and count <= 10:
        # usage_start = resource.getrusage(resource.RUSAGE_CHILDREN)
        start_time = datetime.datetime.now()
        result = subprocess.run('docker run --memory=48g --cpus=24 --mount type=bind,source=./{},target=/app wgr/mitsuba-conda-clang-o2 mitsuba -p 24 -L error /app/{}.xml'.format(scene, scene), shell=True, executable="/bin/bash")
        end_time = datetime.datetime.now()
        # usage_end = resource.getrusage(resource.RUSAGE_CHILDREN)
        retcode = result.returncode 
        count = count + 1
    subprocess.run('mv -f ./{}/{}.exr ./output/{}_{}.{}.exr'.format(scene, scene, scene, integrator, n_steps), shell=True, executable="/bin/bash")
    # utime = usage_end.ru_utime - usage_start.ru_utime
    # stime = usage_end.ru_stime - usage_start.ru_stime
    insert_time_usage_log(scene, integrator, n_steps, (end_time - start_time).total_seconds(), retcode)


# run_once('cbox', 'path', 1)
for scene, ref_interator in scenes:
    # run_once(scene, ref_interator, -1)
    for integrator in integrators:
        # run_once(scene, integrator, -1)
        for i in range(0, 10):
            run_once(scene, integrator, 2**i)
