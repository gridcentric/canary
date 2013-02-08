# Copyright 2013 Gridcentric Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os
import signal
import subprocess

from . import config

def run_collectd(pidfile, config):
    # Kill any pid that's running.
    if os.path.exists(pidfile):
        f = open(pidfile, 'r')
        pid = f.read().strip()
        try:
            os.kill(int(pid), signal.SIGTERM)
        except:
            pass

    # Run the collectd instance.
    cmd = ["collectd", "-P", pidfile, "-C", config]
    subprocess.call(cmd)

def start(pidfile, config):
    # Load the configuration.
    config = config.load(config)

    # Start the collectd process.
    run_collectd(config.pidfile, config.config)
