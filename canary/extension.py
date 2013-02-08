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

import json
import webob

from nova import flags
from nova.exception import NovaException
from nova.openstack.common import cfg
from nova.openstack.common import log as logging
from nova.openstack.common import rpc
from nova.api.openstack import extensions
from nova.api.openstack import wsgi

LOG = logging.getLogger('canary.api')
FLAGS = flags.FLAGS

canary_api_opts = [
               cfg.StrOpt('canary_topic',
               default='canary',
               help='the topic canary nodes listen on') ]
FLAGS.register_opts(canary_api_opts)

def convert_exception(action):
    def fn(self, *args, **kwargs):
        try:
            return action(self, *args, **kwargs)
        except NovaException as error:
            raise exc.HTTPBadRequest(explanation=unicode(error))
    fn.__name__ = action.__name__
    fn.__doc__ = action.__doc__
    return fn

class CanaryController(object):

    @convert_exception
    def query(self, req, body):
        context = req.environ["nova.context"]

        # Extract the host.
        host = body.get('canary', {}).get('host', None)

        # Extract the query arguments.
        args = body.get('canary', {}).get('args', {})

        # Construct the query.
        kwargs = { 'method' : 'query', 'args' : args }
        queue = self.db.queue_get_for(context, FLAGS.canary_topic, host)
        if not(host) or not(queue):
            return webob.Response(status_int=404)

        # Send it along.
        result = rpc.call(context, FLAGS.canary_topic, kwargs)
        return webob.Response(status_int=200, body=json.dumps(result))

class Canary_extension(object):
    """
    Extension for monitoring hosts.
    """

    name = "canary"
    alias = "canary"
    namespace = "http://www.gridcentric.com"
    updated = '2012-07-17T13:52:50-07:00' ##TIMESTAMP##

    def __init__(self, ext_mgr):
        ext_mgr.register(self)

    def get_resources(self):
        return [extensions.ResourceExtension('canary', CanaryController())]

    def get_controller_extensions(self):
        return []
