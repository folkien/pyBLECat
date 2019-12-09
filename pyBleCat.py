#!/usr/bin/python2.7
import pygatt
import argparse, os, sys
import time, binascii
import hashlib
from binascii import hexlify
from bluepy import btle

# default variables
result=0 # Program result return at then end of main
adapter = None
defaultReadChar = None
defaultWriteChar = None
defaultNotifyChar = None
defaultFrameSize=256
defaultTimeout=1

# Variable with program states
outFile=None
inFile=None
inputSize=0
RxLastDataTime=time.time()
TxLastDataTime=time.time()
RxRunning=0
TxRunning=0
TotalRxBytes=0
TotalTxBytes=0

# Parsing and configuration
parser = argparse.ArgumentParser()
# File and input options
parser.add_argument("-i", "--inputFile", type=str, required=False, help="input file")
parser.add_argument("-o", "--outputFile", type=str, required=False, help="output file")
parser.add_argument("-a", "--appendOutputFile", action='store_true', required=False, help="Append output file instead of create and write")
parser.add_argument("-g", "--command", type=str, required=False, help="Send raw text command instead of input file")
# Bluetooth options
parser.add_argument("-d", "--device", type=str, required=True, help="BLE device MAC address")
# General communication options
parser.add_argument("-f", "--frameSize", type=int, required=False, help="Size of transmited frame")
parser.add_argument("-fd", "--frameDelay", type=float, required=False, help="Delay of transmited frame in seconds (float)")
parser.add_argument("-rd", "--receiveDelay", type=float, required=False, help="Extra receive delay of transmited frame in seconds (float)")
parser.add_argument("-rx", "--rxSize", type=int, required=False, help="Size of received total data")
parser.add_argument("-tx", "--txSize", type=int, required=False, help="Size of transmitted total data")
parser.add_argument("-t", "--timeout", type=int, required=False, help="Timeout during transmission/receiving")
# Extra options
parser.add_argument("-c", "--check", action='store_true', required=False, help="Checks if input file is equal to output file.")
parser.add_argument("-p", "--preview", action='store_true', required=False, help="Preview data")
args = parser.parse_args()

#Assert
if (not args.device):
    print "No device"
    sys.exit(1)

# Args - set default frameSize
if (args.frameSize is not None):
    defaultFrameSize=args.frameSize

# Config timeout check
if (args.timeout is not None):
    defaultTimeout=args.timeout

# Read input file size
if (args.inputFile is not None):
    inputSize = os.stat(args.inputFile).st_size
if (args.txSize is not None):
    inputSize=args.txSize
if (args.command is not None):
    inputSize=len(args.command)

#Config check
if (not args.rxSize is not None):
    rxSize=inputSize
else:
    rxSize=args.rxSize

# MD5 of file ( only path given as argument )
def FileMD5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


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
    global TotalTxBytes
    handle = dev.get_handle(uuid)
    DataLength=len(data)
    position=0
    while (position < DataLength):
        tmpBuffer=data[position:position+limit]
        tmpBuffer+="".join(["\0"]*(limit-len(tmpBuffer)))
        sys.stdout.write("> Write %s to %s.\n" % (repr(tmpBuffer), uuid))
        dev.char_write_handle(handle,bytearray(tmpBuffer,'utf-8'))
        position+=len(tmpBuffer)

    TotalTxBytes+=DataLength


# Receive data from notifications
def RxNotifications(handle, value):
    global outFile
    global TotalRxBytes
    global RxRunning
    global rxSize

    # Write data if RX enabled
    if ((RxRunning==1) and (outFile is not None)):
        outFile.write(value)
        RxLastDataTime=time.time()

    # Update total RX size and check if finished
    TotalRxBytes+=len(value)
    if (TotalRxBytes >= rxSize):
        RxRunning=0

# Wait on receiver to end job
def RxWait():
    global RxRunning
    global RxLastDataTime
    global defaultTimeout

    # Wait until receiving all data or receivng timeout happend
    while (RxRunning == 1):
        sys.stdout.write("\rTransmitted %d/%dB. Readed %d/%dB. Delta = %dB.  " % (TotalTxBytes,inputSize,TotalRxBytes,rxSize,TotalTxBytes-rxSize))
        time.sleep(0.1)
        if ((time.time()-RxLastDataTime)>defaultTimeout):
            print "\nRxData timeout %us happend!" % (defaultTimeout)
            break;
    sys.stdout.write("\n")


# Enable receiving
def RxEnable(device):
    global outFile
    global RxRunning
    global args

    # Open output file to append or write clear
    if (args.appendOutputFile):
        outFile = open(args.outputFile,'a+')
    else:
        outFile = open(args.outputFile,'w')
    print "Output to %s(%s)" % (args.outputFile,outFile.mode)
    device.subscribe(defaultNotifyChar, callback=RxNotifications)
    RxRunning=1


# main()
# ------------------------------------------------------------

# Get device info through Bluepy
Bluepy_GetDeviceInfo(args.device)

# Start Adapter, connect to device and callback notifications
adapter = pygatt.GATTToolBackend()
adapter.start()
sys.stdout.write("Connecting to %s.\n" % args.device)
device = adapter.connect(args.device)

# Enable Rx if needed
if (args.outputFile is not None):
    RxEnable(device)

# If text command should be sent
if (args.command is not None):
    if (defaultWriteChar is not None):
        TransmitData(device,defaultWriteChar,args.command+"\n",defaultFrameSize)
        time.sleep(defaultTimeout)

# If input file defined
if (args.inputFile is not None):
    # Open write file and send lines
    print "Input from ",args.inputFile,"(",inputSize,"Bytes)."
    inFile = open(args.inputFile,'r')
    for chunk in iter(lambda: inFile.read(min(defaultFrameSize,inputSize-TxTransmitted)), ''):
        writeSize       = TransmitData(device,defaultWriteChar,chunk,defaultFrameSize)
        TxTransmitted   += writeSize

        # Transmitted data preview if set
        if (args.preview):
            sys.stdout.write("Tx:%s\n" % (chunk))
        # Wait frame delay if set
        if (args.frameDelay is not None):
            time.sleep(args.frameDelay)
        if (RxRunning == 0):
            break;

# Wait on reading thread and close port
RxWait()

# Check files md5 sums if enabled
if ((args.check) and (args.inputFile is not None) and (args.outputFile is not None)):
    sumInput=FileMD5(args.inputFile)
    sumOutput=FileMD5(args.outputFile)
    sys.stdout.write("Input file MD5 %s\n" % sumInput)
    sys.stdout.write("Output file MD5 %s\n" % sumOutput)
    if (sumInput != sumOutput):
        sys.stdout.write("Checksum error!\n")
        result=-1


# Closing
if (inFile is not None):
    inFile.close()

if (outFile is not None):
    outFile.close()

if (adapter is not None):
    sys.stdout.write("Disconnecting from %s.\n" % args.device)
    adapter.stop()

sys.exit(result)
