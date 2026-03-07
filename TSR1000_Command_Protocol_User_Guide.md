# TSR-1000 Sonar Command Protocol User Guide

This document describes the command protocol used to control and
communicate with the TSR‑1000 sonar module.

## 1. Command Format

Commands begin with the letter \'C\' followed by a numeric command
identifier. If parameters are required a comma (,) and additional data
follows. The command string is terminated by either \<CR\>, \<LF\>, or
both.

The parser ignores any characters until it encounters the \'C\' command
prefix.

Any ill formed commands will reset the parser to looking for a new
command.

For Blue Robotics PingViewer support see the 'TSR1000 Blue Robotics Ping
Protocol User Guide'

### Example:

-   C3\<CR\>\<LF\>
-   C2,{"FrameSize":"32768"}\<CR\>\<LF\>

## 2. Command Summary

-   C0 -- Check ready
-   C1 -- Initialize I/O do default baud rate
-   C2 -- Set parameters
-   C3 -- Get parameters
-   C4 -- Acquire frame
-   C5 -- Change I/O port (debug only)
-   C6 -- Firmware update
-   C7 -- Depth sounder mode (NEMA‑0183)
-   C8 -- Switch to Blue Robotics 'Ping' protocol mode

## 3. C0 -- Initialize

Mostly used to check if the device is ready. Send C0\<CR\>\<LF\> and get
back \<CR\>\<LF\>+.

It will also return the TSR1000 back to TSR command protocol mode if it
was switch to an alternate like the Blue Robotics PingViewer protocol.

### Command:

> C0\<CR\>\<LF\>

### Returns:

> \<CR\>\<LF\>+

## 4. C1 -- Unused

No operation.

## 5. C2 -- Set Parameters

Sets configuration parameters using a JSON formatted list of parameters
and values.

See *Appendix A* for a list of parameters.

### Command:

> C2,{\...}\<CR\>\<LF\>

### Returns:

> \<CR\>\<LF\>+

### Example: 

> C2,{\"FrameSize\":\"32768\",\"DataBaudRate\":\"460800\"}\<CR\>\<LF\>

> FrameSize -- Number of samples collected per ping

> DataBaudRate -- Communication port baud rate

## 6. C3 -- Get Parameters

Returns all configuration parameters formatted as a JSON object
containing all the parameters and values.

See *Appendix A* for a list of parameters.

### Command:

> C3\<CR\>\<LF\>

### Returns:

> \<JSON Object\>\<CR\>\<LF\>\<CR\>\<LF\>+

## 7. C4 -- Get Frame

Triggers an acquisition cycle and returns data based on the mode.

See *Appendix B* for the report types and format.

### Command:

> C4\<CR\>\<LF\>

### Returns:

> \<format\>\<data\>

## 8. C5 -- Change I/O Port

Debug command. Currently not used in normal operation. May be removed.

## 9. C6 -- Firmware Update

Places the device into firmware update mode.

### Command:

> C6,1\<CR\>\<LF\>

## 10. C7 -- Report depth as a NEMA 0813 string

Simple depth response in NEMA 0813 formatting.

### Command:

> C7\<CR\>\<LF\>

### Returns:

> \$\<talker\>\<type\>,\<feet\>,f,\<meters\>,M,\<fathoms\>f\<checksum\>

### Example:

> C7\<CR\>\<LF\>

> \$SDDBT,0.17,f,0.05,M,0.03,F\*36\<CR\>\<LF\>+

## 

## Appendix A -- Parameters

Parameters can be retrieved using the **C3 command** and modified (when
permitted) using the **C2 command**.

### Example:

> C2,{\"FrameSize\":\"32768\",\"DataBaudRate\":\"460800\"}\<CR\>\<LF\>

### Notes on the parameters:

1.  *SamplingFrequency = PingClockFrequency × OverSampleFactor*\
    These values are intrinsically related and altering the
    *SamplingFrequency* will update the *PingClockFrequency* and vice
    versa. You should not change both, the result will not be guaranteed
    over firmware updates.
2.  FrameSize = function(RangeEnd, SamplingFrequency, SpeedOfSound)\
    Changing the RangeStart, RangeEnd, SamplingFrequency or SpeedOfSound
    will trigger a change in the FrameSize to accommodate. Changing the
    FrameSize will change the RangeEnd appropriately.
3.  Parameters marked R/O are for information and diagnostic purposes.
    Attempts to change them will be ignored.

### A.1 Sonar Timing and Sampling

  --------------------- -------- -------- ----- ------------ ----------------------------------------------------------
  ClockFrequency        uint64   Hz       R/O   240000000    MCU master clock frequency
  PingClockFrequency    uint64   Hz       R/W   675000       Transducer operating frequency
  SamplingFrequency     uint64   Hz       R/W   2700000      ADC sampling frequency (normally 4 × PingClockFrequency)
  PingClockPulseTrain   uint64   pulses   R/W   20           Number of transmit pulses per ping
  SamplingPrescaler     uint16   --       R/O   calculated   Timer prescaler for sampling clock
  SamplingPulseLength   uint32   ticks    R/O   calculated   Sample clock pulse width
  SamplingDutyCycle     uint32   ticks    R/O   calculated   Sampling clock duty cycle
  OverSampleFactor      uint16   --       R/W   4            Oversampling factor
  DecimationFactor      uint16   --       R/W   8            Decimation applied after filtering
  --------------------- -------- -------- ----- ------------ ----------------------------------------------------------

### A.2 Range and Frame Control

  -------------- -------- --------- ----- ------- --------------------------------------
  RangeStart     uint32   mm        R/W   0       Minimum measurement distance
  RangeEnd       uint32   mm        R/W   10000   Maximum measurement distance
  FrameSize      uint32   samples   R/O           Number of samples collected per ping
  MaxFrameSize   uint32   samples   R/O           Maximum frame buffer capacity
  -------------- -------- --------- ----- ------- --------------------------------------

### A.3 Ping Operation

  ---------------------- -------- -------- ----- ----- ---------------------------------------
  PingNumber             uint32   --       R/O   0     Ping counter since boot
  LastPingTime           uint32   ms       R/O         Time of last ping
  PingRepeats            uint16   --       R/W   1     Number of pings per acquisition cycle
  PingRepeatsInterval    uint16   clocks   R/W   100   Sample clocks between transmit pulses
  PingInterval           uint16   ms       R/W   66    Interval between pings in auto mode
  PingClockPulseLength   uint16   ticks    R/W   4     Transducer pulse width
  PingClockDutyCycle     uint16   ticks    R/O   2     Transducer duty cycle
  ---------------------- -------- -------- ----- ----- ---------------------------------------

### A.4 Communication

  --------------- -------- ------ ----- ----------- -------------------------------
  DebugBaudRate   uint32   baud   R/W   230400      Debug serial port speed
  DataBaudRate    uint32   baud   R/W   230400      Data communication port speed
  DataPortMode    enum     --     R/W   RS485Full   Interface mode (RS232/RS485)
  CommErrors      uint32   --     R/O   0           Communication error counter
  --------------- -------- ------ ----- ----------- -------------------------------

### A.5 Environmental Monitoring

  ---------------- -------- ------- ----- ------ -------------------------
  Voltage          uint16   mV      R/O   5000   Measured supply voltage
  PCBTemperature   uint16   cdegC   R/O   2000   PCB temperature
  CPUTemperature   uint16   cdegC   R/O   3000   CPU temperature
  ---------------- -------- ------- ----- ------ -------------------------

### A.6 Signal Processing

  ----------------- --------- ---- ----- ------ -------------------------------------
  DoFilter          uint8     --   R/W   1      Enable digital filtering
  DepthAlgorithm    uint16    --   R/W   3      Depth detection algorithm
  ScaleFactor       float32   --   R/O   calc   Scaling used for PingViewer display
  AutoGainMode      uint8     --   R/W   Auto   Automatic gain control mode
  GainPreampLevel   uint8     --   R/W   0      Pre-amplifier gain level
  ----------------- --------- ---- ----- ------ -------------------------------------

### A.7 Transducer Configuration

  -------------------- -------- ---- ----- ------ -------------------------------
  PowerLevel           uint16   --   R/W   1024   Transmit power level
  EnableTransmitter    enum     --   R/W   On     Enable or disable transmitter
  MaximumTransducers   uint16   --   R/O   3      Maximum supported transducers
  ActiveTransducers    uint16   --   R/W   1      Number of active transducers
  -------------------- -------- ---- ----- ------ -------------------------------

### A.8 Rotator Control

  ---------------------- -------- -------- ----- ----------------- ---------------------------------
  RotatorStartPosition   uint16   \% ×10   R/W   500               Starting rotator position (50%)
  RotatorPosition        uint16   \% ×10   R/O   500               Current rotator position
  RotatorZeroCount       uint16   --       R/W   device specific   PWM value corresponding to 0%
  RotatorFullCount       uint16   --       R/W   device specific   PWM value corresponding to 100%
  RotatorStepSize        int16    --       R/W   0                 Rotator step change per ping
  RotatorDelay           uint16   ms       R/W   0                 Delay after rotator movement
  RotatorSweepMode       uint8    --       R/W   0                 Rotator sweep mode
  ---------------------- -------- -------- ----- ----------------- ---------------------------------

### A.9 System Control

  -------------- ------------ ---- ----- -------------- -------------------------
  Version        char\[32\]   --   R/O   build string   Firmware version
  DeviceId       uint8        --   R/W   1              Device identifier
  Flags          uint16       --   R/W   0x00           Configuration flags
  SoftReset      uint8        --   W/O   0              Force software reset
  CommandMode    enum         --   R/W   PingProtocol   Active command protocol
  SimulateMode   enum         --   R/W   Off            Simulation mode
  RunMode        enum         --   R/W   ReportData     Return samples or depth
  -------------- ------------ ---- ----- -------------- -------------------------

## 

## Appendix B -- Sample Data Return Formats

The *****C4*** command** starts an acquisition cycle and returns one of
three report formats depending on the requested report type:

-   *****R***** --- Raw samples
-   *****F***** --- Filtered data
-   *****M***** --- Magnitude data

The host requests the desired format by sending:

> C4,\<report\>\<CR\>\<LF\>

Examples:

> C4,R\<CR\>\<LF\>

> C4,F\<CR\>\<LF\>

> C4,M\<CR\>\<LF\>

### B.1 General Transfer Behaviour

After *C4* is sent, the TSR-1000 returns a report stream beginning with
a **single ASCII format character**:

-   *R* for raw
-   *F* for filtered
-   *M* for magnitude

For large transfers, the data is sent in chunks. After each chunk is
received, the host sends the single character:

All data is sent in little-endian form.

### B.2 Report Type *R* --- Raw Samples

#### Purpose

The *R* format returns the acquired sonar data as **raw 16-bit sample
values**. Each value is the number is the raw ADC value as a 16 bit
unsigned integer.

#### Command

> C4,R\<CR\>\<LF\>

#### Response Layout

> \'*R\'+\<uint32 FrameSize\>+\<uint16 FrameCount\>+\<raw sample data\>*

The host program reads the *R* byte first, then reads **6 additional
bytes.**

#### Data Payload

The raw payload size is: *FrameSize × FrameCount × 2 bytes*

#### Chunking

The host reads raw data in blocks of **1024 bytes** and sends *G* after
each block to request the next one.

### B.3 Report Type *F* --- Filtered Data

#### Purpose

The *F* format returns **filtered and decimated** data. The data is
returned as 32 bit floating point values.

#### Command

> C4,F\<CR\>\<LF\>

#### Response Layout

> \'F\'+\<uint16 HeaderLength\>+\<uint8 DataType\>+\<header
> data\>+\<float\[\] payload\>

#### Header Fields Used by the Host

  ------------------ ----------- ------ --------
  Field              Data Type   Size   Offset
  type               char        1      0
  headerSize         uint16_t    2      1
  type               uint8_t     1      3
  reserved           double      8      4
  reserved           double      8      12
  reserved           double      8      20
  reserved           double      8      28
  reserved           uint8_t     1      36
  decimationFactor   uint16_t    2      37
  sendPacketSize     uint16_t    2      39
  dataSetLength      uint32_t    4      41
  numberOfDataSets   uint16_t    2      45
  ------------------ ----------- ------ --------

#### Payload Size

For filtered data, the script computes payload length as:

> (FrameSize × FrameCount) / (Decimation × 4) × 8

When the decimation factor is not zero the data points represent I/Q
values.

When the decimation factor is zero the data represents the filtered
data.

#### Chunking

The host reads 4 bytes at a time and sends *G* whenever the number of
bytes accumulated reaches **sendPacketSize**.

### B.3 Report Type *M* --- Magnitude Data

#### Purpose

The *M* format returns ****magnitude data****. The data is returned as
32 bit floating point values.

#### Command

> C4,M\<CR\>\<LF\>

#### Response Layout

> \'M\'+\<uint16 HeaderLength\>+\<uint8 DataType\>+\<header
> data\>+\<float\[\] payload\>

#### Header Fields Used by the Host

  ------------------ ----------- ------ --------
  Field              Data Type   Size   Offset
  type               char        1      0
  headerSize         uint16_t    2      1
  type               uint8_t     1      3
  reserved           double      8      4
  reserved           double      8      12
  reserved           double      8      20
  reserved           double      8      28
  reserved           uint8_t     1      36
  decimationFactor   uint16_t    2      37
  sendPacketSize     uint16_t    2      39
  dataSetLength      uint32_t    4      41
  numberOfDataSets   uint16_t    2      45
  ------------------ ----------- ------ --------

#### Payload Size

For filtered data, the script computes payload length as:

> (FrameSize × FrameCount) / (Decimation × 4) × 8

When the decimation factor is not zero the data points represent I/Q
values.

When the decimation factor is zero the data represents the filtered
data.

#### Chunking

The host reads 4 bytes at a time and sends *G* whenever the number of
bytes accumulated reaches **sendPacketSize**.

## Appendix C -- Firmware Update Protocol

The host sends C6,1 to initiate firmware update mode.

The device responds with \'RDY\' when ready to receive firmware packets.

-   Host sends: C6,1
-   Device replies: RDY
-   Host sends firmware packets sequentially
-   Device acknowledges each packet
-   After the final packet the device programs flash and resets

## Appendix D --- Developer Information

This appendix provides additional information useful for developers
implementing host software or integrating the TSR-1000 into custom
systems.

### D.1 Command Parser Behaviour

The TSR-1000 command parser operates as a **stream parser**.

Key characteristics:

-   The parser ignores all characters until the *C* character is
    detected.
-   A command is considered complete when either:

<div>

\<CR\>

\<LF\>

\<CR\>\<LF\>

</div>

is received.

-   Any malformed command resets the parser and it begins searching for
    the next *C* command prefix.

This behaviour allows the device to recover from corrupted serial
streams without requiring a connection reset.

### D.2 Data Endianness

All binary values returned by the TSR-1000 are encoded in
**little-endian format**.

Examples:

  --------- ------------------------
  uint16    LSB first
  uint32    LSB first
  float32   IEEE-754 little-endian
  --------- ------------------------

This matches the native format of the STM32 processor.

### D.3 Chunked Data Transfer

Large data transfers (such as *C4* frame acquisition) are transmitted in
**chunks**.

After each block of data is received, the host must send the single
character:

<div>

[]{#anchor}G

</div>

to request the next block.

This mechanism prevents the device from overrunning slower host systems.

Typical sequence:

<div>

[]{#anchor-1}Host -\> TSR1000 : C4,R

TSR1000 -\> Host : first data chunk

Host -\> TSR1000 : G

TSR1000 -\> Host : next data chunk

Host -\> TSR1000 : G

\...

</div>

The internal firmware converts the *G* request into an internal
**NextChunk command**.

### D.4 Parameter Dependencies

Several configuration parameters are interdependent.

#### Sampling Frequency Relationship

<div>

[]{#anchor-2}SamplingFrequency = PingClockFrequency × OverSampleFactor

</div>

Changing either parameter will update the other automatically.

#### Frame Size Relationship

<div>

[]{#anchor-3}FrameSize = f(RangeEnd, SamplingFrequency, SpeedOfSound)

</div>

Changing any of the following parameters will trigger recalculation of
the frame size:

-   RangeStart
-   RangeEnd
-   SamplingFrequency
-   SpeedOfSound

Changing **FrameSize** directly will update **RangeEnd** accordingly.

### D.5 Filtered Data Interpretation

Filtered data (*F* report format) may represent either:

#### I/Q data pairs

If the **DecimationFactor** is non-zero, the returned values represent:

<div>

[]{#anchor-4}I0, Q0, I1, Q1, I2, Q2 \...

</div>

Each value is a **32-bit float**.

These represent the complex baseband signal after digital
down-conversion.

#### Real filtered samples

If **DecimationFactor = 0**, the returned data represents filtered real
samples.

### D.6 Magnitude Data Interpretation

Magnitude mode (*M* report) returns the magnitude of the complex signal.

Each sample is a **32-bit floating point value** representing:

<div>

[]{#anchor-5}sqrt(I² + Q²)

</div>

This format is typically used for:

-   waterfall displays
-   envelope detection
-   depth algorithms

### D.7 Firmware Update Notes

The firmware update protocol is designed to tolerate unreliable serial
links.

Features include:

-   CRC-16 packet protection
-   ACK / NAK retransmission
-   sequence numbers
-   image CRC-32 verification

Developers should normally use the **provided Python update utility**
rather than implementing the update protocol directly.

### D.8 Recommended Host Behaviour

For reliable operation, host software should:

1.  Wait for the *+* prompt before sending commands.
2.  Use timeouts when reading serial responses.
3.  Handle chunked transfers using the *G* mechanism.
4.  Flush any partial responses before sending a new command.

### D.9 Typical Host Session

Example interaction:

<div>

[]{#anchor-6}\<CR\>

\+

C3

{JSON parameters}

\+

C4,R

\<data\>

G

\<data\>

G

\...

</div>
