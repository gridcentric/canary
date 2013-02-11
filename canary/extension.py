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

class CanaryController(wsgi.Controller):

    @wsgi.action('canary-query')
    def query(self, req, id, body):
        context = req.environ["nova.context"]
        authorize(context)

        # Extract the host.
        host = body.get('canary', {}).get('host', None)

        # Extract the query arguments.
        args = body.get('canary', {}).get('args', {})

        # Construct the query.
        kwargs = { 'method' : 'query', 'args' : args }
        queue = self.db.queue_get_for(context, FLAGS.canary_topic, host)
        if not(host) or not(queue):
            raise webob.exc.HTTPNotFound(explanation=unicode(e))

        try:
            # Send it along.
            result = rpc.call(context, FLAGS.canary_topic, kwargs)
        except Exception, e:
            raise webob.exc.HTTPBadRequest(explanation=unicode(e))

        # Send the result.
        return webob.Response(status_int=200, body=json.dumps(result))

    @wsgi.action('canary-show')
    def show(self, req, id, body):
        context = req.environ["nova.context"]
        authorize(context)

        # Extract the host.
        host = body.get('canary', {}).get('host', None)

        # Construct the query.
        kwargs = { 'method' : 'show', 'args' : {} }
        queue = self.db.queue_get_for(context, FLAGS.canary_topic, host)
        if not(host) or not(queue):
            raise webob.exc.HTTPNotFound(explanation=unicode(e))

        try:
            # Send it along.
            result = rpc.call(context, FLAGS.canary_topic, kwargs)
        except Exception, e:
            raise webob.exc.HTTPBadRequest(explanation=unicode(e))

        # Send the result.
        return webob.Response(status_int=200, body=json.dumps(result))

    def get_actions(self):
        """ Return the actions the extension adds. """
        return \
            [
                extensions.ActionExtension("os-hosts", "canary-query", self.query),
                extensions.ActionExtension("os-hosts", "canary-show", self.show)
            ]

class Canary_extension(object):
    """
    Extension for monitoring hosts.
    """

    name = "canary"
    alias = "canary"
    namespace = "http://docs.gridcentric.com/openstack/canary/api/v0"
    updated = '2013-02-08T12:00:00-05:00'

    def __init__(self, ext_mgr):
        ext_mgr.register(self)

    def get_controller_extensions(self):
        controller = CanaryController()
        extension = extensions.ControllerExtension(self, 'os-hosts', controller)
