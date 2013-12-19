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

import json
import re

from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse
from django.shortcuts import render
from horizon import exceptions
from horizon import tables
from horizon import conf

from .. import api
from ..api import novaclient
from .tables import HostsTable

DEFAULT_VM_METRICS = [
    'libvirt*',
]

DEFAULT_HOST_METRICS = [
    'load.load',
    'memory.memory-used',
    'df.df-root',
    'interface.if_octets-br100',
]

class HostListView(tables.DataTableView):
    table_class = HostsTable
    template_name = 'canary/host-list.html'

    def has_more_data(self, table):
        return False

    def get_data(self):
        try:
            return api.host_list(self.request)
        except:
            msg = _('Unable to retrieve host list.')
            exceptions.handle(self.request, msg)

def host_view(request, host):
    metrics = []
    # check for metrics in the query string, format ?graph1=a.a&graph2=b.b,c.c&
    metrics = [str(request.GET[x]) for x in request.GET if x.startswith("graph")]

    if ':' in host:
        title = novaclient(request).servers.get(host.split(':')[-1]).name
        if not metrics:
            metrics = conf.HORIZON_CONFIG.get('canary_default_vm_metrics',
                                              DEFAULT_VM_METRICS)
    else:
        title = host
        if not metrics:
            metrics = conf.HORIZON_CONFIG.get('canary_default_host_metrics',
                                              DEFAULT_HOST_METRICS)
    tf = conf.HORIZON_CONFIG.get('canary_default_timeframe', 2)
    update = conf.HORIZON_CONFIG.get('canary_default_update', 2)
    return render(request, 'canary/graphs.html', {'title': title,
                                                  'initial_metrics': metrics,
                                                  'timeframe': tf,
                                                  'update': update})

def host_data(request, host):
    # Separate the metrics from the query.
    if request.GET.get('metrics'):
        metrics = [x for x in str(request.GET['metrics']).split(',')]
    else:
        msg = "Please provide a query string appended to the url, \
               e.g. ?metrics=foo.bar"
        return HttpResponse(msg, content_type='text/plain')

    # Parse the rest of the query.
    params = {'from_time': int, 'to_time': int, 'cf': str, 'resolution': int}
    kwargs = {}
    for param, func in params.items():
        if param in request.GET:
            kwargs[param] = func(request.GET[param])

    metric_data = {}
    for metric in metrics:
        data = api.host_data(request, host, metric, **kwargs)
        metric_data[metric] = data

    return HttpResponse(json.dumps(metric_data),
                        content_type='application/json')

def host_metrics(request, host):
    info = api.novaclient(request).canary.info(host)
    metrics = [[metric.metric, metric.to_time, metric.cfs] for metric in info]
    return HttpResponse(json.dumps({'metrics': metrics}),
                        content_type='application/json')
