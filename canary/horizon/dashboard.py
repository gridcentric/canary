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

import horizon

from django.utils.translation import ugettext_lazy as _
from hosts.panel import Hosts
from instances.panel import Instances
from openstack_dashboard.dashboards.admin import dashboard

from . import tables

class CanaryPanels(horizon.PanelGroup):
    slug = "canary"
    name = _("Canary Statistics")
    panels = ('canary_hosts', 'canary_instances',)

# Must be listed explicitly; autodiscovery of panels only works for dashboards
dashboard.Admin.panels += (CanaryPanels,)
dashboard.Admin.register(Instances)
dashboard.Admin.register(Hosts)
tables.patch()
