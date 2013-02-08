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

from eventlet.green import threading as gthreading

from nova import flags
from nova.openstack.common import cfg
from nova.openstack.common import log as logging
from nova import manager

LOG = logging.getLogger('canary.manager')
FLAGS = flags.FLAGS

canary_opts = [
               cfg.StrOpt('canary_config',
                default='/etc/nova/canary.conf',
                help='The configuration file for stats collection.'),
               ]
FLAGS.register_opts(canary_opts)

from . import collect

class CanaryManager(manager.SchedulerDependentManager):

    def __init__(self, *args, **kwargs):
        super(CanaryManager, self).__init__(service_name="canary", *args, **kwargs)

        # Use an eventlet green thread condition lock instead of the regular
        # threading module. This is required for eventlet threads because they
        # essentially run on a single system thread.  All of the green threads
        # will share the same base lock, defeating the point of using the it.
        # Since the main threading module is not monkey patched we cannot use
        # it directly.
        self.cond = gthreading.Condition()

        # Start up the data collection process.
        collect.start(FLAGS.canary_config)

    def query(self, context, *args):
        print args
