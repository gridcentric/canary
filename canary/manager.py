# Copyright 2013 GridCentric Inc.
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

import socket
import re
import glob
import os
import rrdtool

from nova import flags
from nova.openstack.common import cfg
from nova.openstack.common import log as logging
from nova import manager

LOG = logging.getLogger('canary.manager')
FLAGS = flags.FLAGS

canary_opts = [
               cfg.StrOpt('canary_rrdpath',
               default='/var/lib/collectd/%s' % socket.gethostname(),
               help='The path for available RRD files.'),
              ]
FLAGS.register_opts(canary_opts)

class CanaryManager(manager.SchedulerDependentManager):

    def __init__(self, *args, **kwargs):
        super(CanaryManager, self).__init__(service_name="canary", *args, **kwargs)

    def query(self, context, metric, cf='AVERAGE', from_time=None, to_time=None, resolution=None):
        m = re.match("^([^\.\[]+)(\[([^\[]+)\])?\.(.+)$", metric)
        if not m:
            # Return an error to the user.
            raise Exception("Unknown metric: should be 'module.name' or 'module[unit].name'.")

        # File our RRD file.
        plugin = m.group(1)
        unit = m.group(3)
        key = m.group(4)
        if unit:
            filename = os.path.join(FLAGS.canary_rrdpath, '%s-%s' % (plugin, unit), '%s.rrd' % key)
        else:
            filename = os.path.join(FLAGS.canary_rrdpath, plugin, '%s.rrd' % key)

        cmd = [filename, cf]
        if from_time:
            cmd.extend(['--start', str(from_time)])
        if to_time:
            cmd.extend(['--stop', str(to_time)])
        if resolution:
            cmd.extend(['--resolution', str(resolution)])

        # Pull our data.
        data = rrdtool.fetch(cmd)

        # Format and return.
        trange = (data[0][0], data[0][1])
        values = [x[0] for x in data[2]]
        return { "from_time" : trange[0], "to_time" : trange[1], "values" : values }

    def show(self, context):
        metrics = {}
        available = glob.glob(os.path.join(FLAGS.canary_rrdpath, '*/*.rrd'))
        for filename in available:
            m = re.match("^%s/([^\/-]+)(-([^\/]+))?/([^\.]+)\.rrd$" % FLAGS.canary_rrdpath, filename)
            if m:
                plugin = m.group(1)
                unit = m.group(3)
                key = m.group(4)

                if not(plugin in metrics):
                    metrics[plugin] = { }
                if unit:
                    if not(unit in metrics[plugin]):
                        metrics[plugin][unit] = {}
                    if not(key in metrics[plugin][unit]):
                        metrics[plugin][unit][key] = {}
                    keyinfo = metrics[plugin][unit][key]
                else:
                    if not(key in metrics[plugin]):
                        metrics[plugin][key] = {}
                    keyinfo = metrics[plugin][key]

                # FIXME: At this point, we should be populating 'keyinfo', with
                # the appropriate information about available CFs, time ranges,
                # resolutions, etc.
                pass

        return metrics
