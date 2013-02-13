OpenStack Canary
================

Overview
--------

Canary is a simple OpenStack nova service which can be used to expose
system-level monitoring information via the API for administrators.

It depends on python-rrdtool, collectd, and python-nova.

Setting up API extensions
-------------------------

You should add the Canary extension to your nova.conf in order to expose the API:

    osapi_compute_extension=nova.api.openstack.compute.contrib.standard_extensions
    osapi_compute_extension=canary.extension.Canary_extension

Next, you should restart the API server.

    restart nova-api

Setting up the service
----------------------

Canary comes with an upstart script for automatically starting on upstart-based
systems. To start canary manually, use:

    start canary

If you use a non-standard RRD path for collectd, you can change the path by the
config option `canary_rrdpath` in `/etc/nova/nova.conf`. It will default to the
path `/var/lib/collectd/rrd/{fqdn}`.

    [DEFAULT]
    canary_rrdpath=/var/lib/collectd/rrd/{fqdn}

Similarly, you may change the Canary topic, although it's unlikely you will need.

    [DEFAULT]
    canary_topic=canary

Setting up collectd
-------------------

Canary relies on collectd running locally to gather system statistics.
