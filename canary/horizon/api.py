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

from horizon import api

from novaclient import shell
from novaclient.v1_1 import client

# NOTE: We have to reimplement this function here (although it is
# impemented in the API module above). The base module does not currently
# support loading extensions. We will attempt to fix this upstream,
# but in the meantime it is necessary to have this functionality here.
def novaclient(request):
    insecure = getattr(api.settings, 'OPENSTACK_SSL_NO_VERIFY', False)
    api.LOG.debug('novaclient connection created using token "%s" and url "%s"' %
                  (request.user.token.id, api.url_for(request, 'compute')))
    extensions = shell.OpenStackComputeShell()._discover_extensions("1.1")
    c = client.Client(request.user.username,
                      request.user.token.id,
                      extensions=extensions,
                      project_id=request.user.tenant_id,
                      auth_url=api.url_for(request, 'compute'),
                      insecure=insecure)
    c.client.auth_token = request.user.token.id
    c.client.management_url = api.url_for(request, 'compute')
    return c

class Host(object):

    def __init__(self, name):
        self.id = name
        self.name = name

class Instance(object):

    def __init__(self, host, instance_id, name, tenant_name):
        self.id = '{}:{}'.format(host, instance_id)
        self.host = host
        self.instance_id = instance_id
        self.name = name
        self.tenant_name = tenant_name

def host_list(request):
    return [Host(host.host_name) for host in novaclient(request).canary.list()
            if not hasattr(host, 'instance_id') or host.instance_id is None]

def instance_list(request):
    client = novaclient(request)
    instances = dict([(server.id, server) for server in client.servers.list(True, {'all_tenants': True})])
    tenants = dict([(tenant.id, tenant) for tenant in api.keystone.tenant_list(request, admin=True)])
    return [Instance(instance.host_name, instance.instance_id,
                          instances[instance.instance_id].name,
                          tenants[instances[instance.instance_id].tenant_id].name)
            for instance in client.canary.list()
            if hasattr(instance, 'instance_id') and instance.instance_id is not None]

def host_data(request, host, metric, **kwargs):
    client = novaclient(request)
    return client.canary.query(host, metric, **kwargs)
