#!/usr/bin/python2.7
import argparse, os, sys
import time, binascii
from bluepy import btle

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--inputFile", type=str, required=False, help="input file")
parser.add_argument("-o", "--outputFile", type=str, required=False, help="output file")
parser.add_argument("-c", "--command", type=str, required=False, help="Send raw text command instead of input file")
parser.add_argument("-f", "--frameSize", type=int, required=False, help="Size of transmited frame")
parser.add_argument("-t", "--timeout", type=int, required=False, help="Timeout during transmission/receiving")
parser.add_argument("-d", "--device", type=str, required=True, help="BLE device MAC address")
args = parser.parse_args()

defaultReadChar = None
defaultWriteChar = None
defaultNotifyChar = None
defaultFrameSize=256
defaultTimeout=1

# Args - set default frameSize
if (args.frameSize is not None):
    defaultFrameSize=args.frameSize

if (args.timeout is not None):
    defaultTimeout=args.timeout

class ReadDelegate(btle.DefaultDelegate):
    def __init__(self, params = 0):
        btle.DefaultDelegate.__init__(self)
        # ... initialise here

    def handleNotification(self, cHandle, data):
        # ... perhaps check cHandle
        # ... process 'data'
        sys.stdout.write("Read %s from %s .\n" % (repr(rxData), cHandle))


# Function to Get BLE device info
def GetDeviceInfo(dev):
    global defaultWriteChar
    global defaultReadChar
    global defaultNotifyChar

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
                defaultWriteChar=characteristics
            # If NOTIFY property
            if (characteristics.properties & btle.Characteristic.props["NOTIFY"]):
                defaultNotifyChar=characteristics
            # If READ property
            if (characteristics.properties & btle.Characteristic.props["READ"]):
                defaultReadChar = characteristics
                value = characteristics.read()
                print "  Value", binascii.b2a_hex(value)

# Transmit data to device characteristics
def TransmittData(char,data,limit):
    DataLength=len(data)
    position=0
    while (position < DataLength):
        tmpBuffer=data[position:position+limit]
        tmpBuffer+="".join(["\0"]*(limit-len(tmpBuffer)))
        sys.stdout.write("Write %s to characteristic %s.\n" % (repr(tmpBuffer), char.uuid))
        char.write(tmpBuffer,withResponse=True)
        position+=len(tmpBuffer)

# Read data from device characteristics
# timeout given i seconds
def ReceiveData(dev,char,timeout=1):
    resp = dev.waitForNotifications(timeout)
    print "resp=",resp
    startTime=time.time()
    while ((time.time() - startTime) < timeout):
        rxData = char.read()
        sys.stdout.write("Read %s from characteristic %s.\n" % (repr(rxData), char.uuid))

def turn_on_notifications(per):
     print "hello"
     setup_data = b"\x01\x00"
     notify = per.getCharacteristics(uuid='00002902-0000-1000-8000-00805f9b34fb')[0]
     notify_handle = notify.getHandle() + 1
     per.writeCharacteristic(notify_handle, setup_data, withResponse=True)
#    svc = peripheral.getServiceByUUID("00002902-0000-1000-8000-00805f9b34fb")
#    ch = svc.getCharacteristics(read_uuid)[0]
#     ch = dev.getCharacteristics(uuid=0x0025)[0]
#     peripheral.writeCharacteristic(ch.getHandle() + 1, struct.pack('<bb', 0x01, 0x00), True)

# BLE connection
sys.stdout.write("Connecting to %s.\n" % args.device)
dev = btle.Peripheral(args.device)
dev.setDelegate( ReadDelegate() )

# Always get device info and read
GetDeviceInfo(dev)

# enable notifcations
turn_on_notifications(dev)

##srv = dev.getServiceByUUID(btle.UUID(0x2902))

#dev.writeCharacteristic(, "0x0100")

#notifyConf = dev.getCharacteristics(btle.UUID("00002902-0000-1000-8000-00805f9b34fb"))
#notifyConf.write(0x0101)
#dev.writeCharacteristic(0x2902,0x0100)


# If text command should be sent
if (args.command is not None):
    if (defaultWriteChar is not None):
        TransmittData(defaultWriteChar,args.command+"\n", defaultFrameSize)
        ReceiveData(dev,defaultWriteChar,defaultTimeout)

