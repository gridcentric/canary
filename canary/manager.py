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

LOG = logging.getLogger(__name__)
FLAGS = flags.FLAGS

canary_opts = [
               cfg.StrOpt('canary_rrdpath',
               default='/var/lib/collectd/rrd/',
               help='The path for available RRD files.'),
              ]
FLAGS.register_opts(canary_opts)

class CanaryManager(manager.SchedulerDependentManager):

    def __init__(self, *args, **kwargs):
        super(CanaryManager, self).__init__(service_name="canary", *args, **kwargs)

    def query(self, context, metric, target=None, cf='AVERAGE', from_time=None, to_time=None, resolution=None):
        m = re.match("^([^\.\[]+)(\[([^\[]+)\])?\.(.+)$", metric)
        if not m:
            raise NotImplementedError()

        # Figure out the target.
        if target == None:
            target = socket.getfqdn()
        rrdpath = os.path.join(FLAGS.canary_rrdpath, target)

        # Find our RRD file.
        # NOTE: The deconstruction above is symmetric with the construction
        # below (in info()). There is no real special meaning behind these
        # constructions, but they should be in sync with each other.
        plugin = m.group(1)
        unit = m.group(3)
        key = m.group(4)
        if unit:
            filename = os.path.join(rrdpath, '%s-%s' % (plugin, unit), '%s.rrd' % key)
        else:
            filename = os.path.join(rrdpath, plugin, '%s.rrd' % key)

        cmd = [filename, cf]
        if from_time:
            cmd.extend(['--start', str(from_time)])
        if to_time:
            cmd.extend(['--end', str(to_time)])
        if resolution:
            cmd.extend(['--resolution', str(resolution)])

        # Pull our data.
        data = rrdtool.fetch(map(str, cmd))

        # Format and return.
        timestamps = range(data[0][0], data[0][1], data[0][2])
        values = [x[0] for x in data[2]]
        return zip(timestamps, values)

    def info(self, context, target=None):
        # Figure out the target.
        if target == None:
            target = socket.getfqdn()
        rrdpath = os.path.join(FLAGS.canary_rrdpath, target)

        # Grab available metrics.
        available = glob.glob(os.path.join(rrdpath, '*/*.rrd'))
        metrics = { }

        for filename in available:
            # NOTE: Not sure quite why, but it seems like 
            # the rrdtool commands below barf unless they 
            # this happens -- maybe barfing on unicode?
            filename = str(filename)

            m = re.match("^%s/([^\/-]+)(-([^\/]+))?/([^\.]+)\.rrd$" % rrdpath, filename)
            if m:
                plugin = m.group(1)
                unit = m.group(3)
                key = m.group(4)

                # NOTE: At this point we construct a metric name that is
                # equivilant to how we deconstruct the name above. It's 
                # important that these two operations are symmetric for
                # the sake of a user's sanity.
                if unit:
                    metric = "%s[%s].%s" % (plugin, unit, key)
                else:
                    metric = "%s.%s" % (plugin, key)
                if not(metric in metrics):
                    metrics[metric] = {}

                metrics[metric]["from_time"] = rrdtool.first(filename)
                metrics[metric]["to_time"] = rrdtool.last(filename)

                step = 1
                pdps = []
                cfs = []
                for (k, v) in rrdtool.info(filename).items():
                    if re.match("^step$",k):
                        step = int(v)
                        continue
                    elif re.match("^rra\[\d+\]\.pdp_per_row$", k):
                        pdps.append(int(v))
                        continue
                    elif re.match("^rra\[\d+\]\.cf", k):
                        cfs.append(v)
                        continue

                pdps = list(set(pdps))
                cfs = list(set(cfs))
                cfs.sort()
                resolutions = map(lambda x: step * x, pdps)
                resolutions.sort()

                metrics[metric]["cfs"] = cfs
                metrics[metric]["resolutions"] = resolutions

        return metrics
