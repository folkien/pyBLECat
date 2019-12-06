#!/usr/bin/python2.7
import argparse, os, sys
import time, binascii
from bluepy import btle

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--inputFile", type=str, required=False, help="input file")
parser.add_argument("-o", "--outputFile", type=str, required=False, help="output file")
parser.add_argument("-c", "--command", type=str, required=False, help="Send raw text command instead of input file")
parser.add_argument("-f", "--frameSize", type=int, required=False, help="Size of transmited frame")
parser.add_argument("-d", "--device", type=str, required=True, help="BLE device MAC address")
args = parser.parse_args()

defaultReadChar = None
defaultWriteChar = None
defaultNotifyChar = None
defaultFrameSize=256

# Args - set default frameSize
if (args.frameSize is not None):
    defaultFrameSize=args.frameSize

sys.stdout.write("Connecting to %s.\n" % args.device)
dev = btle.Peripheral(args.device)

# Function to Get BLE device info
def GetDeviceInfo(dev):
    global defaultWriteChar
    global defaultReadChar
    global defaultNotifyChar
    sys.stdout.write("Device %s services :\n" % (dev.addr))
    for service in dev.services:
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
                print "Value", binascii.b2a_hex(value)

# Transmit data to device characteristics
def TransmittData(char,data,limit):
    DataFill=" "
    DataLength=len(data)
    position=0
    while (position < DataLength):
        tmpBuffer=data[position:position+limit]
        tmpBuffer+="".join([" "]*(limit-len(tmpBuffer)))
        sys.stdout.write("Write '%s' to characteristic %s.\n" % (tmpBuffer, char.uuid))
        char.write(tmpBuffer,withResponse=True)
        position+=len(tmpBuffer)


# Always get device info and read
GetDeviceInfo(dev)

# If text command should be sent
if (args.command is not None):
    if (defaultWriteChar is not None):
        TransmittData(defaultWriteChar,args.command, defaultFrameSize)

