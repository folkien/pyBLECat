#!/usr/bin/python2.7
import pygatt
import argparse, os, sys
import time, binascii
from binascii import hexlify
from bluepy import btle

# default variables
adapter = pygatt.GATTToolBackend()
defaultReadChar = None
defaultWriteChar = None
defaultNotifyChar = None
defaultFrameSize=256
defaultTimeout=1

# Parsing and configuration
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--inputFile", type=str, required=False, help="input file")
parser.add_argument("-o", "--outputFile", type=str, required=False, help="output file")
parser.add_argument("-c", "--command", type=str, required=False, help="Send raw text command instead of input file")
parser.add_argument("-f", "--frameSize", type=int, required=False, help="Size of transmited frame")
parser.add_argument("-t", "--timeout", type=int, required=False, help="Timeout during transmission/receiving")
parser.add_argument("-d", "--device", type=str, required=True, help="BLE device MAC address")
args = parser.parse_args()

# Args - set default frameSize
if (args.frameSize is not None):
    defaultFrameSize=args.frameSize

if (args.timeout is not None):
    defaultTimeout=args.timeout

# Function to Get BLE device info
def Bluepy_GetDeviceInfo(address):
    global defaultWriteChar
    global defaultReadChar
    global defaultNotifyChar

    sys.stdout.write("Connecting to %s and reading...\n" % args.device)
    dev = btle.Peripheral()
    dev.connect(address)

    # Descriptors list
    sys.stdout.write("Device %s descriptors :\n" % (dev.addr))
    for desc in dev.getDescriptors():
        sys.stdout.write(" %s :\n" % (str(desc)))

    # Services list
    sys.stdout.write("Device %s services :\n" % (dev.addr))
    for service in dev.getServices():
        sys.stdout.write(" %s :\n" % (str(service)))
        for characteristics in service.getCharacteristics():
            sys.stdout.write("  %s - " % (characteristics.uuid))
            sys.stdout.write("%04x %s\n" % (characteristics.properties, characteristics.propertiesToString()))
            # If WRITE property
            if (characteristics.properties & btle.Characteristic.props["WRITE"]):
                defaultWriteChar=characteristics.uuid.getCommonName()
            # If NOTIFY property
            if (characteristics.properties & btle.Characteristic.props["NOTIFY"]):
                defaultNotifyChar=characteristics.uuid.getCommonName()
            # If READ property
            if (characteristics.properties & btle.Characteristic.props["READ"]):
                defaultReadChar = characteristics.uuid.getCommonName()
                value = characteristics.read()
                print "  Value", binascii.b2a_hex(value)

    dev.disconnect()

# Function to Get BLE device info
def GetDeviceInfo(dev):
    global defaultWriteChar
    global defaultReadChar
    global defaultNotifyChar

    # Descriptors list
    sys.stdout.write("Device %s :\n" % (dev._address))

    # Characteristics list
    for uuid in device.discover_characteristics():
        charObject = device._characteristics[uuid]
        print  "<uuid=%s handle=0x%04x>" % (charObject.uuid, charObject.handle)


# Transmit data to device characteristics
def TransmitData(dev,uuid,data,limit):
    handle = dev.get_handle(uuid)
    DataLength=len(data)
    position=0
    while (position < DataLength):
        tmpBuffer=data[position:position+limit]
        tmpBuffer+="".join(["\0"]*(limit-len(tmpBuffer)))
        sys.stdout.write("Write %s to characteristic %s.\n" % (repr(tmpBuffer), uuid))
        dev.char_write_handle(handle,bytearray(tmpBuffer,'utf-8'))
        position+=len(tmpBuffer)


def handle_data(handle, value):
    """
    handle -- integer, characteristic read handle the data was received on
    value -- bytearray, the data returned in the notification
    """
    print("Received data: %s" % hexlify(value))

# main()
# ------------------------------------------------------------

# Get device info through Bluepy
Bluepy_GetDeviceInfo(args.device)


# Start Adapter, connect to device and callback notifications
adapter.start()
sys.stdout.write("Connecting to %s.\n" % args.device)
device = adapter.connect(args.device)
device.subscribe(defaultNotifyChar, callback=handle_data)

# If text command should be sent
if (args.command is not None):
    if (defaultWriteChar is not None):
        TransmitData(device,defaultWriteChar,args.command+"\n",defaultFrameSize)


#startTime=time.time()
#while ((time.time()-startTime) < defaultTimeout):
    time.sleep(1)
    # do nothing

sys.stdout.write("Disconnecting from %s.\n" % args.device)
adapter.stop()
