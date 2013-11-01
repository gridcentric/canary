var bytes = [
    [1, ' B'],
    [1024, ' KB'],
    [1048576, ' MB'],
    [1073741824, ' GB'],
];

var count = [
    [1, ' '],
    [1000, ' x10<sup>3</sup>'],
    [1000000, ' x10<sup>6</sup>'],
    [1000000000, ' x10<sup>9</sup>'],
];

// List of unit formatters: If the first item is a substring of a metric, the
// units defined in the second item are used.
units = [
    ['cpu[', [[1, '%']]],
    ['df', bytes],
    ['disk_octets', bytes],
    ['disk_ops', count],
    ['disk_time', [[1, ' s']]],
    ['if_dropped', count],
    ['if_errors', count],
    ['if_octets', bytes],
    ['if_packets', count],
    ['irq', count],
    ['memory', bytes],
    ['processes', count],
    ['swap', bytes],
    ['users', count],
    ['virt_cpu', count],
];

// List of regex that match metrics to proper names.
// This is an inclusive list of all collectd metrics used by canary.
var name_map = [

[/cpu(.*]).cpu-(.*)/,           "CPU $1 usage - $2"],
[/df.df-(.*)/,                  "Disk usage ($1)"],
[/disk(.*]).disk_merged/,       "Merged disk operations $1"],
[/disk(.*]).disk_octets/,       "Disk bytes $1"],
[/disk(.*]).disk_ops/,          "Disk operations $1"],
[/disk(.*]).disk_time/,         "Average I/O completion time $1"],
[/entropy.entropy/,             "Entropy"],
[/interface.if_errors-(.*)/,    "Network errors ($1)"],
[/interface.if_octets-(.*)/,    "Network bytes ($1)"],
[/interface.if_packets-(.*)/,   "Network packets ($1)"],
[/irq.irq-(.*)/,                "Requests on interrupt ($1)"],
[/libvirt.virt_cpu_total/,      "CPU utilization"],
[/libvirt.if_packets-(.*)/,     "Network packets ($1)"],
[/libvirt.if_octets-(.*)/,      "Network bytes ($1)"],
[/libvirt.if_errors-(.*)/,      "Network errors ($1)"],
[/libvirt.if_dropped-(.*)/,     "Network dropped ($1)"],
[/libvirt.disk_ops-(.*)/,       "Disk operations ($1)"],
[/libvirt.disk_octets-(.*)/,    "Disk bytes ($1)"],
[/load.load/,                   "System load"],
[/memory.memory-buffered/,      "Registered memory"],
[/memory.memory-cached/,        "Cached memory"],
[/memory.memory-free/,          "Free memory"],
[/memory.memory-used/,          "Memory usage"],
[/processes.fork_rate/,         "Fork Rate"],
[/processes.ps_state-(.*)/,     "Processes ($1)"],
[/users.users/,                 "Number of users"],
[/vms.absolute-domains/,        "Absolute Domains"],
[/vms.memory-limit/,            "VMS Memory Limit"],
[/vms.memory-target/,           "VMS Memory Target"],
[/vms.memory-(.*)/,             "VMS $1 memory"],
[/vmsfs.memory-allocated/,      "VMSFS Allocated Memory"],
[/vmsfs.memory-resident/,       "VMSFS Resident Memory"],

];
