OpenStack Canary
================

Overview
--------

Setting up API extensions
-------------------------

You should add the Canary extension to your nova.conf in order to expose the API:

    osapi_compute_extension=nova.api.openstack.compute.contrib.standard_extensions
    osapi_compute_extension=canary.extension.Canary_extension

Next, you should restart the API server.

    restart nova-api


Setting up the service
----------------------

    start canary

Setting up collectd
-------------------
