# -*- coding: utf-8 -*-
"""
TSR-1000 Echosounder Pyton code example V2

"""
import math
import serial
import struct
import numpy as np
import matplotlib.pyplot as plt
import json
import sys
from time import sleep
import argparse
import pdb
# Cribbed from Eryk Sun on Stackoverflow.com
# Finds all the common factors of a given number
def factors(n):
    result = set()
    for i in range(1, int(n ** 0.5) + 1):
        div, mod = divmod(n, i)
        if mod == 0:
            result |= {i, div}
    return result

# Find two numbers that work as the prescaler and pulse length
# We try to use the bigest even number for the pulse length and the other for the prescale value
def GetClockParameters( MasterFrequency, Frequency ):
    MaxEvenFactor = 0
    ReqDivisor    = MasterFrequency // Frequency
    cf = factors( ReqDivisor )
    for factor in cf:
        if ( factor != ReqDivisor ) and ( factor % 2 == 0 ) and ( factor > MaxEvenFactor ) :
            if ( factor ) < 65536:
                MaxEvenFactor = factor
    return math.trunc(MaxEvenFactor), math.trunc( ReqDivisor // MaxEvenFactor )

def CheckReady():
    retry1 = 0
    retry2 = 0
    cmd = 'C0\n'
    notready = True
    while ( notready and ( retry1 < 4 ) ):
        retry1 += 1;
        ser.write( cmd.encode() )
        while ( notready and ( retry2 < 4 ) ):
            retry2 += 1
            if ( ( ser.inWaiting() > 0 ) and ( ser.read( 1 ) == b'+' ) ):
                notready = False
            else:
                sleep(0.05)
    if ( notready ):
        print('Communications Failed')
    else:
        print('OK')
    return


# Setup the timing parameters
#    MasterClock           Fixed in firmware at 240MHz
#    TransducerFrequency   Transducers native resonant frequency, fixed by hardware used
#    TransmitCycles        Number of pulses transmitted before sampling return data
#    FrameCount            Number of frames to collect (1..n), max n is set in firmware to 6
#    FrameSize             Number of samples / frame, max frame size in firmare is 32768
#    FrameFrequency        Number of frames / second (Frames are initiated at fixd intervals of time)
class CSonarParams:
    def __init__(self, MasterClock, TransducerFrequency, TransmitCycles, FrameCount, FrameSize,  FrameFrequency, PulseInterval, PulseCount,
                       PowerLevel, DoFilter, RunMode, RangeStart, RangeEnd, SpeedOfSound,
                       CommandMode, SimulateMode, GainPreampLevel, DecimationFactor ):
        self.ClockFrequency        = MasterClock                   # Master clock frequency (Defined in firmware)
        self.NumberOfFrames        = FrameCount                    # Number of frames to collect
        if ( FrameSize > 0 ):
            self.FrameSize         = FrameSize                     # Number of samples / frame (Should be a multiple of 32)
        self.PingClockFrequency    = TransducerFrequency*1000      # The transducer's resonant frequency (Defined by the transducer spec.)
        self.SamplingFrequency     = TransducerFrequency*4000      # 4 x the transducer's frequency is the ADC sample frequency
        self.FrameFrequency        = FrameFrequency                # Frames / second
        self.PingRepeatsInterval   = PulseInterval                 # Ping repeat frequency (kHz)
        
        self.PingClockPulseTrain   = TransmitCycles
        
        self.PingRepeats           = PulseCount          # Number of pulses per frame (zero does one pulse)
        
        # Serial port baud rate
        self.DebugBaudRate         = 230400
        self.DataBaudRate          = 230400
        self.PowerLevel            = PowerLevel
        self.Flags                 = 0
        self.DoFilter              = DoFilter
        self.RunMode               = RunMode             # 0 = return samples, 1 = return depth
        self.RangeStart            = RangeStart*1000     # range in mm
        if ( RangeEnd > 0 ):
            self.RangeEnd          = RangeEnd*1000       # range in mm
        self.SpeedOfSound          = SpeedOfSound        # in m/s
        self.CommandMode           = CommandMode         # 0 = TSR mode, 1 = Ping Viewer Mode
        self.SimulateMode          = SimulateMode        # 0 = off, 1 = raw, 2 = Filtered and Decimated
        self.Version               = ''
        self.GainPreampLevel       = GainPreampLevel     #gain = 0, 1, 2, 3
        self.DecimationFactor      = DecimationFactor    # default is 1
        

parser = argparse.ArgumentParser( description = 'Trigger and read back sonar data points' )
parser.add_argument( '-framecount',          '-fc',      default = 1,      type=int )
parser.add_argument( '-framesize',           '-fs',      default = 20480,      type=int )
parser.add_argument( '-framefrequency',      '-ff',      default = 5,      type=int )
parser.add_argument( '-transducerfrequency', '-tf',      default = 200,    type=int, choices=[40, 50, 200, 500, 505, 508, 515, 522, 542, 600, 610, 612, 620, 625, 632, 635, 675] )
parser.add_argument( '-log',                 '-l',       default = 1,   type=int )
parser.add_argument( '-baud',                '-b',       default = 230400, type=int, choices=[9600, 19200, 115200, 230400, 460800] )
parser.add_argument( '-port',                '-p',       default = 'COM13' )
parser.add_argument( '-outfile',             '-o',       default = 'rawdata2' )
parser.add_argument( '-transmitcycles',      '-tc',      default = 20,     type=int )
parser.add_argument( '-powerlevel',          '-pl',      default = 1024,   type=int )
parser.add_argument( '-dofilter',            '-df',      default = 0,      type=int )
parser.add_argument( '-runmode',             '-rmode',   default = 0,      type=int )
parser.add_argument( '-rangeend',            '-re',      default = 0,     type=int )
parser.add_argument( '-rangestart',          '-rs',      default = 0,      type=int )
parser.add_argument( '-speedofsound',        '-sos',     default = 1475,   type=int )
parser.add_argument( '-pingcommandmode',     '-cmode',   default = 0,      type=int ) # 0 is TSR, 1 is Ping Viewer
parser.add_argument( '-simulatemode',        '-smode',   default = 0,      type=int, choices=[0,1,2] )
parser.add_argument( '-initonly',            '-init',    default = 0 )
parser.add_argument( '-pulseinterval',       '-pint',    default = 40,     type=int )
parser.add_argument( '-pulsecount',          '-pcnt',    default = 1,      type=int )
parser.add_argument( '-gainpreamplevel',     '-gain',    default = 3,      type=int )
parser.add_argument( '-decimationfactor',    '-dec',     default = 0,      type=int )
parser.add_argument( '-report',              '-rep',     default = 'R',   type=str.upper, choices=['R','F','M'], help="Must be R, F or M" )

args = parser.parse_args()

#exit()
if ( args.framesize == 0 ) and ( args.rangeend == 0 ):
    print( 'Must supply EITHER the frame size or the range end')
    exit()
if ( args.framesize != 0 ) and ( args.rangeend != 0 ):
    print ( 'Can only supply the frame size OR the range end, not both' )
    exit()
if ( args.framesize % 1024 != 0 ):
    print( 'Frame size must be a multiple of 1024' )
    exit()
if ( (args.framecount > 6 ) or ( args.framecount < 1 ) ):
    print( 'Frame count must be between 1 and 6' )
    exit()
if ( args.log ) and ( args.outfile == ''):
    print( 'Must specify the -outfile parameter if logging is enabled' )
    exit()
if ( args.powerlevel < 0 ) or (args.powerlevel > 4095):
	print( 'Power level must be between 0 and 4095.' )
	exit()

print( vars( args ) )

# Allow for command line override
SonarParams    = CSonarParams( 240000000,
                              args.transducerfrequency,
                              args.transmitcycles,
                              args.framecount, args.framesize, args.framefrequency,
                              args.pulseinterval, args.pulsecount, 
                              args.powerlevel, args.dofilter, args.runmode, args.rangestart, args.rangeend,
                              args.speedofsound, args.pingcommandmode, args.simulatemode,
                              args.gainpreamplevel, args.decimationfactor )
print( vars( SonarParams ) )
#exit()
SerialPort     = args.port
SerialBaudRate = args.baud

print( vars( args ) )
print( vars( SonarParams ) )
print( "Serial Port: " + SerialPort )
print( "Serial Baud: " + str(SerialBaudRate) )

# How long to wait for data x 4 to give some wiggle room
#ReadTimeout = ( ( ( SonarParams.FrameSize * 2 * 10 ) // SerialBaudRate ) * 2 )
ReadTimeout = 100
if ( ReadTimeout < 10 ):
    ReadTimeout = 10
print( 'Read Timeout = ', ReadTimeout, ' seconds.' )

ser = serial.Serial( port=SerialPort, baudrate=SerialBaudRate, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=ReadTimeout )

# Windows-only: enlarge kernel driver buffers (pyserial exposes it)
try:
    ser.set_buffer_size(rx_size=262144, tx_size=65536)   # 256 KB RX
except (AttributeError, OSError):
    pass  # not supported by some drivers

# Configure Sonar
CheckReady()
cmd = 'C2,'+ json.dumps( SonarParams.__dict__ ) + '\n'
print('Size of command string: ' + str(len(cmd)))
ser.write( cmd.encode() )
print( cmd, end='' )

if ( args.initonly == 1 ):
    exit()
# Initiate a data collection cycle
CheckReady()
cmd = 'C4,' + args.report + '\n'
ser.write( cmd.encode() )
print( cmd, end='' )

# Wait for report

while ( 1 ):
    bytesToRead = ser.inWaiting()
    if ( bytesToRead < 1 ):
        continue
    reportType = ser.read( 1 )

    if ( reportType == b'R' ) or ( reportType == b'F' ) or ( reportType == b'M' ):
        break
# Read back the number of frames collected
if ( reportType == b'R' ):
    print('Record type = ', reportType )
    while (1):
        bytesToRead = ser.inWaiting()
        if ( bytesToRead >= 6 ):
            break
    tmpStr = ser.read( 6 )
    if len(tmpStr)<6:
        print('Failed to read back frame count')
        exit()
    FrameSize  = (tmpStr[3]*16777216) + (tmpStr[2]*65536) + (tmpStr[1]*256) + tmpStr[0]
    FrameCount = (tmpStr[5]*256) + tmpStr[4]

    ReadCount = FrameSize * 2 * FrameCount
    CurCount  = 0
    InputData = bytearray()

    print( 'Frames returned = ', FrameCount, ', Frame size = ', FrameSize, ', ReadCount = ', ReadCount )

    while ( CurCount < ReadCount ):
        TempData = ser.read( 1024 )
        CurCount = CurCount + len( TempData )
        InputData = InputData + TempData
        ser.write(b'G')

    #  Confirm the data read is the size we expected
    #print( 'Data read = ', len( InputData ), ' Bytes ')
    if ( len( InputData ) != ReadCount ):
        print('Read failed')
        exit()
elif ( reportType == b'F' ) or ( reportType == b'M' ):
    print( 'Record type = ', reportType )
    while (1):
        bytesToRead = ser.inWaiting()
        if ( bytesToRead >= 3 ):
            break
    tmpStr = ser.read( 3 )
    if len(tmpStr)<3:
        print('Failed to read header length')
        exit()
    headerLength = (tmpStr[1]*256) + tmpStr[0]
    dataType = tmpStr[2]

    print(f"Header Length = {headerLength}")

    while (1):
        bytesToRead = ser.inWaiting()
        if bytesToRead >= (headerLength-4):
            break
    tmpStr = ser.read(headerLength-4)
    if len(tmpStr)<(headerLength-4):
        print('Failed to read all the header')

    Decimation = (tmpStr[34]*256) + tmpStr[33]
    PacketSize = (tmpStr[36]*256) + tmpStr[35]
    FrameSize  = (tmpStr[40]*16777216) + (tmpStr[39]*65536) + (tmpStr[38]*256) + tmpStr[37]
    FrameCount = (tmpStr[42]*256) + tmpStr[41]
    if ( Decimation == 0 ):
        ReadCount = FrameSize * FrameCount * 4
    else:
        #ReadCount = ( FrameSize * 4 * FrameCount ) / ( Decimation * 4 / 2 )
        if ( reportType == b'F' ):
            ReadCount = ( ( FrameSize * FrameCount ) / ( Decimation * 4 ) ) * 8 # times 8 since we get I/Q each is a 4 byte float
        else:
            ReadCount = ( ( FrameSize * FrameCount ) * 4 )
    print( 'Decimation = ', Decimation, ', PacketSize = ', PacketSize, ', FrameSize = ', FrameSize, ', FrameCount = ', FrameCount, ', ReadCount = ', ReadCount )

    CurCount  = 0
    InputData = bytearray()

    while ( CurCount < ReadCount ):
        tmpStr = ser.read( 4 )
        if ( len(tmpStr) ==  0 ):
            print( 'Read Timeout' )
            continue
        CurCount = CurCount + len( tmpStr )
        InputData = InputData + tmpStr
        #print(f"Read len = {len(tmpStr)}, count = {CurCount}")
        if (CurCount >= PacketSize):
            ser.write(b'G')
            #print('Go')
    #
    #  Confirm the data read is the size we expected
    print( 'Data read = ', len( InputData ), ' Bytes ')
    if ( len( InputData ) != ReadCount ):
        print('Read failed')
        exit()

# Convert raw data into array of data points in InputData[ points ] [ framesize ]

Ping  = 0
Point = 0

RawData = [ [ 0 for x in range( FrameSize ) ] for y in range( FrameCount ) ]
if ( reportType == b'R' ):
    dataSize = 2
else:
    dataSize = 4

if ( reportType == b'R' ):
    RawData[ Ping ]  = [struct.unpack('<H', InputData[i:i+2])[0] for i in range(0, len(InputData), 2)]
elif ( reportType == b'F' ):
    RawData[ Ping ]  = [struct.unpack('f', InputData[i:i+4])[0] for i in range(0, len(InputData), 4)]
elif ( reportType == b'M' ):
    RawData[ Ping ]  = [struct.unpack('f', InputData[i:i+4])[0] for i in range(0, len(InputData), 4)]
else:
    raise(f"Unexpected report type: {reportType}")

fullfile = args.outfile+"_"+reportType.decode("utf-8")+"_"+str(args.decimationfactor)+".txt"
if ( args.log ):
    with open(fullfile, "w") as f:
        for i,v in enumerate(RawData[Ping]):
            f.write(f"{i},{v}\n")

new1 = RawData[0][:]
    
print('Ready to plot')
plt.figure()
plt.plot(new1, 'b*-')
plt.xlabel('Sample Number' )
plt.ylabel('Level')
plt.title("Odd")

if ( reportType == b'R' ):
    plt.title(f"Raw Sonar Data")
elif ( reportType == b'F' ):
    plt.title(f"Filtered Data - Decimation {Decimation}")
elif ( reportType == b'M' ):
    plt.title(f"Magnitude - Decimation {Decimation}")
plt.show()
ser.close()

print( 'Done' )
#exit()
