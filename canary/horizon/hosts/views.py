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

from django.utils.translation import ugettext_lazy as _

from canary.horizon import api
from horizon import exceptions
from horizon import tables
from .tables import HostsTable

from django.views import generic
from django.http import HttpResponse
import json
from django.shortcuts import render

class HostListView(tables.DataTableView):
    table_class = HostsTable
    template_name = 'canary/hosts/index.html'

    def has_more_data(self, table):
        return False

    def get_data(self):
        try:
            return api.host_list(self.request)
        except:
            msg = _('Unable to retrieve host list.')
            exceptions.handle(self.request, msg)

class HostView(generic.TemplateView):
    template_name = 'canary/hosts/host.html'

def host_view(request, host):
    return render(request, 'canary/hosts/host.html', {'host': host})

def host_data(request, host, metric):
    params = {'from_time': int, 'to_time': int, 'cf': str, 'resolution': int}
    kwargs = {}
    for param, func in params.items():
        if param in request.GET:
            kwargs[param] = func(request.GET[param])
    data = api.host_data(request, host, metric, **kwargs)
    return HttpResponse(json.dumps({'data': data}),
                        content_type='application/json')

def host_metrics(request, host):
    info = api.novaclient(request).canary.info(host)
    metrics = [[metric.metric, metric.to_time, metric.cfs] for metric in info]
    return HttpResponse(json.dumps({'metrics': metrics}),
                        content_type='application/json')
