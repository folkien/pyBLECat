#!/usr/bin/env python
from __future__ import print_function

import binascii
import pygatt

YOUR_DEVICE_ADDRESS = "e0:7d:ea:50:1f:12"

adapter = pygatt.GATTToolBackend()
adapter.start()
device = adapter.connect(YOUR_DEVICE_ADDRESS)

for uuid in device.discover_characteristics().keys():
    print("Read UUID %s." % (uuid))
