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

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from horizon import tables
from openstack_dashboard.dashboards.project.instances import tables as proj_tables
from openstack_dashboard.dashboards.admin.instances import tables as adm_tables

class ViewStats(tables.LinkAction):
    name = "view_memory"
    verbose_name = _("View Stats")
    url = "horizon:admin:canary_instances:show"

    # We are not interested in instances in the BLESSED or BUILD states.
    # Note: proj_tables.ACTIVE_STATES was not used because users may want
    # statistics for instances in ERROR states too.
    DISALLOWED_STATES = ("BLESSED", "BUILD", )

    def get_link_url(self, instance):
        return reverse(self.url, args=["%s:%s" %
            (getattr(instance,'OS-EXT-SRV-ATTR:host'), instance.id)])

    def allowed(self, request, instance):
        return request.user.is_superuser \
                and instance.status not in self.DISALLOWED_STATES \
                and not proj_tables.is_deleting(instance)

def patch():
    proj_tables.InstancesTable.Meta.row_actions += (ViewStats,)
    adm_tables.AdminInstancesTable.Meta.row_actions += (ViewStats,)
