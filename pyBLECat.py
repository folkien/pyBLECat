#!/usr/bin/python2.7
import argparse, os, sys
import time, binascii
from bluepy import btle

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--inputFile", type=str, required=False, help="input file")
parser.add_argument("-o", "--outputFile", type=str, required=False, help="output file")
parser.add_argument("-d", "--device", type=str, required=True, help="BLE device MAC address")
args = parser.parse_args()

print "Connecting..."
dev = btle.Peripheral(args.device)

# Function to Get BLE device info
def GetDeviceInfo(dev):
    sys.stdout.write("Device %s services :\n" % (dev.addr))
    for service in dev.services:
        sys.stdout.write(" %s :\n" % (str(service)))
        for characteristics in service.getCharacteristics():
            sys.stdout.write("  %s - " % (characteristics.uuid))
            sys.stdout.write("%s\n" % (characteristics.propertiesToString()))

GetDeviceInfo(dev)
