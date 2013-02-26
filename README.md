OpenStack Canary
================

Overview
--------

Canary is a simple OpenStack Nova service which can be used to expose
system-level monitoring information via the API and a Horizon dashboard for
administrators.

It depends on python-rrdtool, collectd, and python-nova.

Installation
------------

To install Canary, clone the repository and run:

    python setup.py install

Setting up API extensions
-------------------------

You should add the Canary extension to your nova.conf in order to expose the API:

    osapi_compute_extension=nova.api.openstack.compute.contrib.standard_extensions
    osapi_compute_extension=canary.extension.Canary_extension

Next, you should restart the API server.

    restart nova-api

Setting up collectd
-------------------

Canary relies on collectd running locally to gather system statistics. You will
need to enable the rrd plugin in `/etc/collectd/collectd.conf` by appending or
uncommenting the following lines:

    LoadPlugin rrdtool

    <Plugin rrdtool>
        DataDir "/var/lib/collectd/rrd"
    </Plugin>

Setting up the service
----------------------

Canary comes with an upstart script for automatically starting on upstart-based
systems. To start canary manually, use:

    start canary

If you use a non-standard RRD path for collectd, you can change the path by the
config option `canary_rrdpath` in `/etc/nova/nova.conf`. It will default to the
path `/var/lib/collectd/rrd/{fqdn}`, where {fqdn} is the hostname.domainname
of the host.

    [DEFAULT]
    canary_rrdpath=/var/lib/collectd/rrd/{fqdn}

Similarly, you may change the Canary topic, although it's unlikely you will need
to.

    [DEFAULT]
    canary_topic=canary

Setting up the dashboard
-------------------

To enable the Canary dashboard in Horizon, modify
`/etc/openstack-dashboard/local_settings.py` and add the following lines:

    import sys
    mod = sys.modules['openstack_dashboard.settings']
    mod.INSTALLED_APPS += ('canary.horizon',)

Then, restart the web server with `service apache2 restart` and navigate to
Horizon. There will be a new dashboard labeled "Canary".
