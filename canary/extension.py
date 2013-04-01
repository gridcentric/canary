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

        hosts = {}

        services = db.service_get_all(context, False)
        for service in services:
            if service['topic'] == FLAGS.canary_topic:
                if service['host'] not in hosts:
                    instances = db.instance_get_all_by_host(context, service['host'])
                    instance_uuids = map(lambda x: x['uuid'], instances)
                    hosts[service['host']] = instance_uuids

        return webob.Response(status_int=200, body=json.dumps(hosts))

    def query(self, req, id, body):
        if not(id):
            raise webob.exc.HTTPNotFound()

        context = req.environ["nova.context"]
        authorize(context)

        # Extract the query arguments.
        args = body.get('args', {})

        # Construct the query.
        kwargs = { 'method' : 'query', 'args' : args }
        parts = id.split(':', 1)
        if len(parts) == 2:
            instance = db.instance_get_by_uuid(context, parts[1])
            kwargs['args']['target'] = instance['name']
            queue = rpc.queue_get_for(context, FLAGS.canary_topic, parts[0])
        else:
            queue = rpc.queue_get_for(context, FLAGS.canary_topic, id)

        try:
            # Send it along.
            result = rpc.call(context, queue, kwargs)
        except Exception, e:
            raise webob.exc.HTTPBadRequest(explanation=unicode(e))

        # Send the result.
        return webob.Response(status_int=200, body=json.dumps(result))

    def info(self, req, id):
        if not(id):
            raise webob.exc.HTTPNotFound()

        context = req.environ["nova.context"]
        authorize(context)

        # Construct the query.
        kwargs = { 'method' : 'info', 'args' : {} }
        parts = id.split(':', 1)
        if len(parts) == 2:
            instance = db.instance_get_by_uuid(context, parts[1])
            kwargs['args']['target'] = instance['name']
            queue = rpc.queue_get_for(context, FLAGS.canary_topic, parts[0])
        else:
            queue = rpc.queue_get_for(context, FLAGS.canary_topic, id)

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
    updated = '2013-02-08T12:00:00-05:00' ## TIMESTAMP ##

    def get_resources(self):
        resources = [extensions.ResourceExtension('canary',
                CanaryController(),
                collection_actions={},
                member_actions={"query": "POST", "info": "GET"})]
        return resources
