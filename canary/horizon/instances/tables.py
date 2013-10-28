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
from horizon import tables

class InstanceTable(tables.DataTable):
    tenant_name = tables.Column("tenant_name",
                            verbose_name=_("Project Name"))

    host = tables.Column("host",
                         verbose_name=_("Host"))

    name = tables.Column("name",
                         link="horizon:admin:canary_instances:show",
                         verbose_name=_("Name"))

    class Meta:
        name = "instances"
        verbose_name = _("Instances")
