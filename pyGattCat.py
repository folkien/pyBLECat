#!/usr/bin/python2.7
import pygatt
import argparse, os, sys
import time, binascii
from binascii import hexlify

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

# Start Adapter and connect to device
adapter.start()
sys.stdout.write("Connecting to %s.\n" % args.device)
device = adapter.connect(args.device)

# Get device info
GetDeviceInfo(device)

#device.subscribe("00001011-1212-efde-1523-785feabcd123",
#                    callback=handle_data)

# If text command should be sent
if (args.command is not None):
    if (defaultWriteChar is not None):
        TransmitData(device,char,args.command+"\n",args.frameSize)



startTime=time.time()
while ((time.time()-startTime) < defaultTimeout):
    time.sleep(1)
    # do nothing

adapter.stop()
