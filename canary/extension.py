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
from nova import db
from nova.exception import NovaException
from nova.openstack.common import cfg
from nova.openstack.common import log as logging
from nova.openstack.common import rpc
from nova.api.openstack import extensions
from nova.api.openstack import wsgi
from nova.api.openstack import xmlutil

LOG = logging.getLogger(__name__)
# NOTE: We use the same authorization as the standard os-hosts
# extension. This is because we need we same level of privelege.
authorize = extensions.extension_authorizer('compute', 'hosts')
FLAGS = flags.FLAGS

canary_api_opts = [
               cfg.StrOpt('canary_topic',
               default='canary',
               help='the topic canary nodes listen on') ]
FLAGS.register_opts(canary_api_opts)

class CanaryController(object):

    def index(self, req):
    	context = req.environ['nova.context']
        authorize(context)
    	services = db.service_get_all(context, False)
        hosts = []
        for host in services:
            if host["topic"] == FLAGS.canary_topic:
        	hosts.append(host['host'])

        return webob.Response(status_int=200, body=json.dumps(hosts))

    def query(self, req, id, body):
        context = req.environ["nova.context"]
        authorize(context)

        # Extract the query arguments.
        args = body.get('args', {})

        # Construct the query.
        kwargs = { 'method' : 'query', 'args' : args }
        queue = rpc.queue_get_for(context, FLAGS.canary_topic, id)
        if not(id) or not(queue):
            raise webob.exc.HTTPNotFound(explanation=unicode(e))

        try:
            # Send it along.
            result = rpc.call(context, FLAGS.canary_topic, kwargs)
        except Exception, e:
            raise webob.exc.HTTPBadRequest(explanation=unicode(e))

        # Send the result.
        return webob.Response(status_int=200, body=json.dumps(result))

    def info(self, req, id):
        context = req.environ["nova.context"]
        authorize(context)

        # Construct the query.
        kwargs = { 'method' : 'info', 'args' : {} }
        queue = rpc.queue_get_for(context, FLAGS.canary_topic, id)
        if not(id) or not(queue):
            raise webob.exc.HTTPNotFound(explanation=unicode(e))

        try:
            # Send it along.
            result = rpc.call(context, FLAGS.canary_topic, kwargs)
        except Exception, e:
            raise webob.exc.HTTPBadRequest(explanation=unicode(e))

        # Send the result.
        return webob.Response(status_int=200, body=json.dumps(result))

class Canary_extension(extensions.ExtensionDescriptor):
    """
    Extension for monitoring hosts.
    """

    name = "canary"
    alias = "canary"
    namespace = "http://docs.gridcentric.com/openstack/canary/api/v0"
    updated = '2013-02-08T12:00:00-05:00'

    def get_resources(self):
        resources = [extensions.ResourceExtension('canary',
                CanaryController(),
                collection_actions={},
                member_actions={"query": "POST", "info": "GET"})]
        return resources
