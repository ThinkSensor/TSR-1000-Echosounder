# -*- coding: utf-8 -*-
"""
TSR-1000 Echosounder Pyton code example V2

"""
import serial
import struct
import matplotlib.pyplot as plt
import json
import sys
import time
import argparse

def read_exact(ser, size, timeout, description="data"):
    """Read exactly *size* bytes using one overall deadline."""
    if size < 0:
        raise ValueError(f"Invalid {description} size: {size}")

    data = bytearray(size)
    view = memoryview(data)
    received = 0
    deadline = time.monotonic() + timeout

    while received < size:
        remaining_time = deadline - time.monotonic()
        if remaining_time <= 0:
            raise TimeoutError(
                f"Timed out reading packet {packet_number}: "
                f"{packet_received}/{packet_length} bytes in this packet, "
                f"{total_received}/{read_count} bytes total"
            )

        # Keep individual reads short so the overall deadline remains meaningful.
        ser.timeout = min(0.25, remaining_time)
        chunk = ser.read(size - received)
        if chunk:
            view[received:received + len(chunk)] = chunk
            received += len(chunk)

    return data


def wait_for_report_type(ser, timeout=10.0):
    """Ignore command/debug text until a valid binary report marker arrives."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        ser.timeout = min(0.25, max(0.01, deadline - time.monotonic()))
        value = ser.read(1)
        if value in (b'R', b'F', b'M'):
            return value
    raise TimeoutError("Timed out waiting for report type R, F, or M")


def CheckReady(timeout=2.0, retries=4):
    """Send C0 and wait for '+' without indefinite busy-waiting."""
    cmd = b'C0\n'

    for _ in range(retries):
        ser.write(cmd)
        ser.flush()
        deadline = time.monotonic() + timeout

        while time.monotonic() < deadline:
            ser.timeout = min(0.1, max(0.01, deadline - time.monotonic()))
            value = ser.read(1)
            if value == b'+':
                print('OK')
                return True

    print('Communications Failed')
    return False


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
                       CommandMode, SimulateMode, GainPreampLevel, DecimationFactor, BaudRate, ActiveTransducers ):
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
        self.DebugBaudRate         = BaudRate
        self.DataBaudRate          = BaudRate
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
        self.ActiveTransducers = ActiveTransducers # default is 1
        

parser = argparse.ArgumentParser( description = 'Trigger and read back sonar data points' )
parser.add_argument( '-framecount',          '-fc',      default = 1,      type=int )
parser.add_argument( '-framesize',           '-fs',      default = 0,      type=int )
parser.add_argument( '-framefrequency',      '-ff',      default = 5,      type=int )
parser.add_argument( '-transducerfrequency', '-tf',      default = 675,    type=int, choices=[40, 50, 200, 500, 505, 508, 515, 522, 542, 600, 610, 612, 620, 625, 632, 635, 675] )
parser.add_argument( '-log',                 '-l',       default = 1,   type=int )
parser.add_argument( '-baud',                '-b',       default = 115200, type=int, choices=[9600, 19200, 115200, 230400, 460800] )
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
parser.add_argument( '-decimationfactor',    '-dec',     default = 1,      type=int )
parser.add_argument( '-report',              '-rep',     default = 'M',   type=str.upper, choices=['R','F','M'], help="Must be R, F or M" )
parser.add_argument('-activetransducers', '-at', default=1, type=int, choices=[1, 2, 3], help='Number of active transducers')
parser.add_argument('--packet-timeout', default=5.0, type=float, help='Maximum seconds allowed for each data packet')
parser.add_argument('--report-timeout', default=10.0, type=float, help='Maximum seconds to wait for the report header')

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
                              args.gainpreamplevel, args.decimationfactor, args.baud , args.activetransducers )
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
ReadTimeout = 0.25
print('Serial read slice timeout =', ReadTimeout, 'seconds')
print('Packet timeout =', args.packet_timeout, 'seconds')

ser = serial.Serial(port=SerialPort, baudrate=SerialBaudRate,
                    bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE, timeout=ReadTimeout,
                    write_timeout=2.0)

# Windows-only: enlarge kernel driver buffers (pyserial exposes it)
try:
    ser.set_buffer_size(rx_size=1048576, tx_size=65536)   # 1 MB RX
except (AttributeError, OSError):
    pass  # not supported by some drivers

# Configure Sonar
if not CheckReady():
    ser.close()
    sys.exit(2)
cmd = 'C2,'+ json.dumps( SonarParams.__dict__ ) + '\n'
print('Size of command string: ' + str(len(cmd)))
ser.write( cmd.encode() )
print( cmd, end='' )

if ( args.initonly == 1 ):
    exit()
# Initiate a data collection cycle
if not CheckReady():
    ser.close()
    sys.exit(2)
cmd = 'C4,' + args.report + '\n'
ser.write( cmd.encode() )
print( cmd, end='' )

# Wait for and receive report
try:
    reportType = wait_for_report_type(ser, args.report_timeout)

    first_header = read_exact(ser, 3, args.report_timeout, "report header prefix")
    headerLength = struct.unpack_from('<H', first_header, 0)[0]

    if headerLength < 4:
        raise ValueError(f"Invalid header length: {headerLength}")

    # Firmware currently sends the datatype as an ASCII digit. Accept a binary
    # value too, which makes this tolerant of a future protocol cleanup.
    raw_data_type = first_header[2]
    if ord('1') <= raw_data_type <= ord('3'):
        dataType = raw_data_type - ord('0')
    else:
        dataType = raw_data_type

    if dataType not in (1, 2, 3):
        raise ValueError(f"Invalid data type byte: 0x{raw_data_type:02X}")

    # 1 = float32, 2 = int16, 3 = int32
    typeToSize = {1: 4, 2: 2, 3: 4}
    dataSize = typeToSize[dataType]

    header_rest_size = headerLength - 4
    header = read_exact(ser, header_rest_size, args.report_timeout, "report header")
    if len(header) < 43:
        raise ValueError(
            f"Report header is too short for required fields: {len(header)} bytes"
        )

    Decimation = struct.unpack_from('<H', header, 33)[0]
    PacketSize = struct.unpack_from('<H', header, 35)[0]
    FrameSize = struct.unpack_from('<I', header, 37)[0]
    FrameCount = struct.unpack_from('<H', header, 41)[0]

    if PacketSize <= 0:
        raise ValueError(f"Invalid packet size: {PacketSize}")

    if Decimation == 0:
        ReadCount = FrameSize * FrameCount * dataSize
    elif reportType == b'F':
        numerator = FrameSize * FrameCount * 8
        denominator = Decimation * 4
        if numerator % denominator:
            raise ValueError(
                f"Filtered byte count is not integral: {numerator}/{denominator}"
            )
        ReadCount = numerator // denominator
    else:
        ReadCount = FrameSize * FrameCount * dataSize

    print(
        f"Record type={reportType.decode()}, datatype={dataType}, "
        f"decimation={Decimation}, packet size={PacketSize}, "
        f"frame size={FrameSize}, frame count={FrameCount}, "
        f"read count={ReadCount}"
    )

    # Read exactly one firmware packet, then send exactly one 'G'. The old
    # CurCount >= PacketSize test stayed true after the first packet and sent
    # a 'G' after every subsequent 4-byte read.
    InputData = bytearray(ReadCount)
    write_offset = 0
    packet_number = 0

    while write_offset < ReadCount:
        bytes_this_packet = min(PacketSize, ReadCount - write_offset)
        packet = read_exact(
            ser, bytes_this_packet, args.packet_timeout,
            f"data packet {packet_number + 1}"
        )
        InputData[write_offset:write_offset + bytes_this_packet] = packet
        write_offset += bytes_this_packet
        packet_number += 1

        ser.write(b'G')
        ser.flush()

        if packet_number == 1 or packet_number % 32 == 0 or write_offset == ReadCount:
            print(
                f"Received {write_offset}/{ReadCount} bytes "
                f"({packet_number} packets)"
            )

    print('Data read =', len(InputData), 'bytes')

except (TimeoutError, ValueError, serial.SerialException) as exc:
    print(f"Read failed: {exc}", file=sys.stderr)
    ser.close()
    sys.exit(3)

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
    RawData[ Ping ]  = [struct.unpack('<f', InputData[i:i+4])[0] for i in range(0, len(InputData), 4)]
elif ( reportType == b'M' ):
    RawData[ Ping ]  = [struct.unpack('<f', InputData[i:i+4])[0] for i in range(0, len(InputData), 4)]
else:
    raise RuntimeError(f"Unexpected report type: {reportType!r}")

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
    plt.title("Raw Sonar Data")
elif ( reportType == b'F' ):
    plt.title(f"Filtered Data - Decimation {Decimation}")
elif ( reportType == b'M' ):
    plt.title(f"Magnitude - Decimation {Decimation}")
plt.show()
ser.close()

print( 'Done' )
#exit()
