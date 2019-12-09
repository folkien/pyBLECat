# pyBleCat - Bluetooth Low Energy cat tool.


```shell
usage: pyBleCat [-h] [-i INPUTFILE] [-o OUTPUTFILE] [-a] [-g COMMAND] -d
                DEVICE [-f FRAMESIZE] [-fd FRAMEDELAY] [-rd RECEIVEDELAY]
                [-rx RXSIZE] [-tx TXSIZE] [-t TIMEOUT] [-c] [-p]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUTFILE, --inputFile INPUTFILE
                        input file
  -o OUTPUTFILE, --outputFile OUTPUTFILE
                        output file
  -a, --appendOutputFile
                        Append output file instead of create and write
  -g COMMAND, --command COMMAND
                        Send raw text command instead of input file
  -d DEVICE, --device DEVICE
                        BLE device MAC address
  -f FRAMESIZE, --frameSize FRAMESIZE
                        Size of transmited frame
  -fd FRAMEDELAY, --frameDelay FRAMEDELAY
                        Delay of transmited frame in seconds (float)
  -rd RECEIVEDELAY, --receiveDelay RECEIVEDELAY
                        Extra receive delay of transmited frame in seconds
                        (float)
  -rx RXSIZE, --rxSize RXSIZE
                        Size of received total data
  -tx TXSIZE, --txSize TXSIZE
                        Size of transmitted total data
  -t TIMEOUT, --timeout TIMEOUT
                        Timeout during transmission/receiving
  -c, --check           Checks if input file is equal to output file.
  -p, --preview         Preview data
```

# Examples

