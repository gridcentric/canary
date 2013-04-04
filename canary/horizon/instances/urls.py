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

from django.conf.urls.defaults import patterns, url
from .views import InstanceListView
from ..hosts.views import host_view, host_data, host_metrics

urlpatterns = patterns('canary.horizon.hosts.views',
    url(r'^$', InstanceListView.as_view(), name='index'),
    url(r'^(?P<host>[^/]+)/$', host_view, name='show'),
    url(r'^(?P<host>[^/]+)/metrics/(?P<metric>[^/]+)/$', host_data, name='data'),
    url(r'^(?P<host>[^/]+)/metrics/$', host_metrics, name='metrics'),
)
