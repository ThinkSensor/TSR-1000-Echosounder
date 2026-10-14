// TSR-1000 parameter presentation definitions, Version 1.
//
// Parameter presentation:
//   order: number  -> controls display order within a category (lower first).
//   suggestions: [] -> suggested numeric values while retaining free-form entry.
//   minFrom: "OtherParameter" -> dynamic minimum using its effective value.
//
// Visibility:
//   advanced: true -> shown only when "Show advanced settings" is enabled.
//   hidden: true   -> never displayed.
//
// editable: false -> displayed read-only.
// Parameters returned by C3 but not listed here are automatically shown
// read-only under "Unknown / Firmware Parameters" in Advanced mode.
//
// NOTE: The current firmware C3 response spells SpeedOfSound as "SpeendOfSound".
// Keep this key until the firmware spelling is corrected.

// Category presentation definitions.
// order controls screen position; title controls the displayed section heading.
const categoryDefinitions = {
    "Sonar / Transducer": {
        order: 10,
        title: "Sonar / Transducer"
    },
    "Environmental": {
        order: 20,
        title: "Environmental"
    },
    "Ping / Range": {
        order: 30,
        title: "Ping / Range"
    },
    "Gain / Processing": {
        order: 40,
        title: "Gain / Processing"
    },
    "Data Processing": {
        order: 45,
        title: "Data Processing"
    },
    "Rotator": {
        order: 50,
        title: "Rotator"
    },
    "Communications": {
        order: 60,
        title: "Communications"
    },
    "Operating Mode": {
        order: 70,
        title: "Operating Mode"
    },
    "Device": {
        order: 80,
        title: "Device"
    },
    "Status": {
        order: 90,
        title: "Status"
    },
    "System / Advanced": {
        order: 100,
        title: "System / Advanced"
    },
    "Unknown / Firmware Parameters": {
        order: 1000,
        title: "Unknown / Firmware Parameters"
    }
};

const parameterDefinitions = {
    PingClockFrequency: {
        label: "Transducer Frequency",
        category: "Sonar / Transducer",
        order: 10,
        type: "integer",
        units: "kHz",
        editable: true,
        min: 20,
        max: 675,
        step: 10,
        displayScale: 1000,
        decimals: 0,
        suggestions: [50, 100, 200, 300, 400, 500, 600, 675, 800],
        help: "Operating frequency of the sonar transducer."
    },
    PowerLevel: {
        label: "Transmit Power Level",
        category: "Sonar / Transducer",
        order: 20,
        type: "select",
        editable: true,
        options: {
            0: "178VDC (-7.03dB)",
            512: "190VDC (-6.47dB)",
            1024: "206VDC (-5,77dB)",
            2048: "246VDC (-4.22dB)",
            3072: "306VDC (-2.33dB)",
            4095: "400VDC (0.00dB)"
        },
        help: "Sets the sonar transmit power level from 0 to 4095.<br>P_dB = 20*log10(VDC/V_norm)<br>Where V_norm = 400VDC."
    },
    MaximumTransducers: {
        label: "Maximum Transducers",
        category: "Sonar / Transducer",
        order: 30,
		visibleWhen: { parameter: "MaximumTransducers", gt: 1 },
        type: "integer",
        editable: false,
        help: "Shows the maximum number of transducers that can be supported by this hardware."
    },
    ActiveTransducers: {
        label: "Active Transducers",
        category: "Sonar / Transducer",
        order: 40,
        visibleWhen: { parameter: "MaximumTransducers", gt: 1 },
        maxFrom: "MaximumTransducers",
        type: "integer",
        editable: true,
        min: 1,
        max: 3,
        help: "In a version with more than one transducer sets the number to use on the next ping.  Must be less than 'Maximum Transducers'."
    },
    EnableTransmitter: {
        label: "Enable Transmitter",
        category: "Sonar / Transducer",
        type: "boolean",
        editable: true,
        help: "If enabled then the transducer will send an initial 'Transmit Pulse Count', if not it will sample only."
    },
    SpeedOfSound: {
        label: "Speed of Sound",
        category: "Environmental",
        order: 10,
        type: "integer",
        units: "m/s",
        editable: true,
        min: 1450,
        max: 1550,
        help: "Speed of sound used to convert sonar echo travel time into distance. Set this for the medium and conditions in which the sonar is operating.\nRange: 1450..1550"
    },
    PingNumber: {
        label: "Ping Number",
        category: "Environmental",
        order: 20,
        type: "integer",
        editable: true,
        min: 0,
        advanced: true,
        help: "Displays the current ping count and allows setting the counter for the next ping value.\nRange: 0..n"
    },
    RangeStart: {
        label: "Range Start",
        category: "Ping / Range",
        order: 10,
        type: "integer",
        units: "m",
        editable: true,
        min: 0,
        step: 0.1,
        displayScale: 1000,
        decimals: 1,
        help: "Start of the sonar range window. The configurator displays this value in metres; the firmware stores and receives it in millimetres."
    },
    RangeEnd: {
        label: "Range End",
        category: "Ping / Range",
        order: 20,
        type: "integer",
        units: "m",
        editable: true,
        min: 0,
        step: 0.1,
        displayScale: 1000,
        decimals: 1,
        help: "End of the sonar range window. The configurator displays this value in metres; the firmware stores and receives it in millimetres."
    },
    AutoPingMode: {
        label: "Automatic Ping",
        category: "Ping / Range",
        order: 30,
        type: "boolean",
        editable: true,
        help: "If enabled then new a new ping will be initiated every 'Ping Interval' milliseconds."
    },
    PingInterval: {
        label: "Ping Interval",
        category: "Ping / Range",
        order: 40,
        type: "integer",
        units: "ms",
        editable: true,
        min: 0,
        max: 65535,
        help: "The time in milliseconds between automatically initiaing a new ping."
    },
    PingClockPulseTrain: {
        label: "Transmit Pulse Count",
        category: "Ping / Range",
        order: 50,
        type: "integer",
		units: "cycles",
        editable: true,
        min: 10,
        help: "Number of pulses transmitted on each ping.\nRange: 10..n"
    },
    PingRepeats: {
        label: "Ping Repeats",
        category: "Ping / Range",
        order: 60,
        type: "integer",
        editable: true,
        min: 0,
        max: 65535,
        advanced: true,
        help: "The number of pulse transmit sequences to initiate during one ping."
    },
    PingRepeatsInterval: {
        label: "Ping Repeat Interval",
        category: "Ping / Range",
        order: 70,
        type: "integer",
        units: "sample clocks",
        editable: true,
        advanced: true,
        min: 10,
        minFrom: "PingClockPulseTrain",
        help: "The number of samples collected during one ping between 'Ping Repeats'."
    },

    AutoGainMode: {
        label: "Automatic Gain",
        category: "Gain / Processing",
        order: 10,
        type: "boolean",
        editable: true,
        help: "If enabled the sample data will be normalized to +/32768."
    },
    ScaleFactor: {
        label: "Digital Gain",
        category: "Gain / Processing",
        order: 20,
        type: "number",
        editable: true,
        min: 0.01,
        step: 0.01,
        advanced: true,
        help: "Reports the digital scale factor calculated by the 'Automatic Gain'.  The value is retained if 'Automatic Gain' is disabled and may be set to have fixed scaling."
    },
    GainPreampLevel: {
        label: "Preamp Gain Level",
        category: "Gain / Processing",
        order: 30,
        type: "select",
        editable: true,
        options: {
            0: "0",
            1: "1",
            2: "2",
            3: "3"
        },
        help: "Selects the sonar receiver preamplifier gain level. Higher values apply more front-end gain before digital processing."
    },
    DoFilter: {
        label: "Enable Filter",
        category: "Data Processing",
        order: 10,
        type: "boolean",
        editable: true,
        help: "When enabled the band pass filter will be applied to the data before further processing or reporting"
    },
    DecimationFactor: {
        label: "Decimation Factor",
        category: "Data Processing",
        order: 20,
        type: "select",
        editable: true,
        options: {
			1: "1",
			2: "2",
			4: "4",
			8: "8",
			16: "16",
			32: "32",
			64: "64"
		},
        help: "Reduces the number of processed/output samples. Higher decimation values return fewer data points. Magnitude mode currently requires a minimum decimation factor of 8 because of the allocated magnitude buffer size."
    },
    DepthAlgorithm: {
        label: "Depth Algorithm",
        category: "Data Processing",
        order: 30,
        type: "select",
        editable: false,
        advanced: true,
        options: {
            3: "Largest magnitude above threshold"
        },
        help: "Returns the depth of the largest magnitude return."
    },

    RotatorStartPosition: {
        label: "Rotator Start Position",
        category: "Rotator",
        type: "number",
        units: "%",
        editable: true,
        hidden: true,
        displayScale: 10,
        min: 0,
        max: 100,
        step: 0.1
    },
    RotatorPosition: {
        label: "Rotator Position",
        category: "Rotator",
        type: "number",
        units: "%",
        editable: true,
        hidden: true,
        displayScale: 10,
        min: 0,
        max: 100,
        step: 0.1
    },
    RotatorStepSize: {
        label: "Rotator Step Size",
        category: "Rotator",
        type: "integer",
        editable: true,
        hidden: true,
        advanced: true
    },
    RotatorDelay: {
        label: "Rotator Delay",
        category: "Rotator",
        type: "integer",
        units: "ms",
        editable: true,
        hidden: true,
        advanced: true,
        min: 0,
        max: 65535
    },
    RotatorSweepMode: {
        label: "Rotator Sweep Mode",
        category: "Rotator",
        type: "integer",
        editable: true,
        hidden: true,
        advanced: true,
        min: 0,
        max: 4
    },

    DataBaudRate: {
        label: "Data Baud Rate",
        category: "Communications",
        type: "select",
        units: "baud",
        editable: true,
        help: "Baud rate used by the sonar data serial port. The connected host must use the same baud rate.",
        options: {
            9600: "9600",
            19200: "19200",
            38400: "38400",
            57600: "57600",
            115200: "115200",
            230400: "230400",
            460800: "460800",
            921600: "921600"
        }
    },
    DebugBaudRate: {
        label: "Debug Baud Rate",
        category: "Communications",
        type: "select",
        units: "baud",
        editable: true,
        advanced: true,
        hidden: true,
        help: "Baud rate used by the firmware debug serial interface.",
        options: {
            9600: "9600",
            19200: "19200",
            38400: "38400",
            57600: "57600",
            115200: "115200",
            230400: "230400",
            460800: "460800",
            921600: "921600"
        }
    },
    DataPortMode: {
        label: "Data Port Mode",
        category: "Communications",
        type: "select",
        editable: true,
        help: "Selects the electrical/duplex mode used by the sonar data serial port.",
        options: {
            0: "RS-232 Full Duplex",
            1: "RS-422 Full Duplex",
            3: "RS-485 Half Duplex"
        }
    },
    AutobaudEnable: {
        label: "Enable Autobaud",
        category: "Communications",
        type: "boolean",
        editable: true,
        advanced: true
    },
    CommandMode: {
        label: "Command Protocol",
        category: "Communications",
        type: "select",
        editable: false,
        hidden: true,
        options: {
            0: "C Protocol",
            1: "Ping Protocol"
        }
    },
    EmulatePing1D: {
        label: "Emulate Ping1D",
        category: "Communications",
        type: "boolean",
        editable: true,
        advanced: true,
        help: "When selected the ECHO will emulate the Blue Robotics Ping1D 8-bit magnitude vector. Leaving it unselected will send an modified 16bit magnitude vector when responding to the Blue Robotics Profile commands."
    },

    RunMode: {
        label: "Run Mode",
        category: "Operating Mode",
        type: "select",
        editable: true,
        options: {
            0: "Return Samples",
            1: "Return Depth",
            2: "Return Magnitude"
        },
        help: "Selects the sonar processing/output mode. Return Samples is used for raw or filtered sample data; Return Magnitude filters the signal and calculates magnitude data."
    },
    SimulateMode: {
        label: "Simulation Mode",
        category: "Operating Mode",
        type: "boolean",
        editable: false,
        hidden: true,
        advanced: true
    },

    DeviceId: {
        label: "Device ID",
        category: "Device",
        type: "integer",
        editable: true,
        advanced: true,
        min: 0,
        max: 255,
        help: "Identifieds the device ID when using the Blue Robotics Ping1D protocols."
    },
    Version: {
        label: "Firmware Version",
        category: "Device",
        type: "string",
        editable: false,
        hidden: true
    },

    Distance: {
        label: "Last Distance",
        category: "Status",
        type: "integer",
        units: "mm",
        editable: false
    },
    Voltage: {
        label: "Supply Voltage",
        category: "Status",
        type: "integer",
        units: "mV",
        editable: false,
        hidden: true
    },
    PCBTemperature: {
        label: "PCB Temperature",
        category: "Status",
        type: "number",
        units: "°C",
        editable: false,
        displayScale: 100,
        decimals: 2,
        hidden: true
    },
    CPUTemperature: {
        label: "CPU Temperature",
        category: "Status",
        type: "number",
        units: "°C",
        editable: false,
        displayScale: 100,
        decimals: 2,
        hidden: true
    },
    LastPingTime: {
        label: "Last Ping Time",
        category: "Status",
        type: "integer",
        units: "ms",
        editable: false,
        advanced: true
    },
    CommErrors: {
        label: "Communication Errors",
        category: "Status",
        type: "integer",
        editable: false,
        advanced: true
    },

    // Firmware-derived/internal timing values. These are deliberately hidden
    // in V1 because changing the intent-level settings causes firmware to
    // recalculate them.
    ClockFrequency: {
        label: "Master Clock Frequency",
        category: "System / Advanced",
        type: "integer",
        units: "Hz",
        editable: false,
        hidden: true
    },
    SamplingFrequency: {
        label: "Sampling Frequency",
        category: "System / Advanced",
        type: "integer",
        units: "Hz",
        editable: false,
        hidden: true
    },
    SamplingPrescaler: {
        label: "Sampling Prescaler",
        category: "System / Advanced",
        type: "integer",
        editable: false,
        hidden: true
    },
    SamplingPulseLength: {
        label: "Sampling Pulse Length",
        category: "System / Advanced",
        type: "integer",
        editable: false,
        hidden: true
    },
    SamplingDutyCycle: {
        label: "Sampling Duty Cycle",
        category: "System / Advanced",
        type: "integer",
        editable: false,
        hidden: true
    },
    PingClockPulseLength: {
        label: "Ping Clock Pulse Length",
        category: "System / Advanced",
        type: "integer",
        editable: false,
        hidden: true
    },
    PingClockDutyCycle: {
        label: "Ping Clock Duty Cycle",
        category: "System / Advanced",
        type: "integer",
        editable: false,
        hidden: true
    },
    OverSampleFactor: {
        label: "Oversample Factor",
        category: "System / Advanced",
        type: "integer",
        editable: false,
        hidden: true
    },
    MaxFrameSize: {
        label: "Maximum Frame Size",
        category: "System / Advanced",
        type: "integer",
        editable: false,
        hidden: true
    },
    FrameSize: {
        label: "Frame Size",
        category: "System / Advanced",
        type: "integer",
        editable: false,
        advanced: true,
        help: "Shows the number of raw samples that will be collected give the current frequency and range settings."
    },

    RotatorZeroCount: {
        label: "Rotator Zero Count",
        category: "System / Advanced",
        type: "integer",
        editable: false,
        hidden: true
    },
    RotatorFullCount: {
        label: "Rotator Full Count",
        category: "System / Advanced",
        type: "integer",
        editable: false,
        hidden: true
    },
    RotatorDeltaCount: {
        label: "Rotator Delta Count",
        category: "System / Advanced",
        type: "number",
        editable: false,
        hidden: true
    },

    AutoBaudStartTime: {
        label: "Autobaud Start Time",
        category: "System / Advanced",
        type: "integer",
        editable: false,
        hidden: true
    },
    AutoBaudWaitTime: {
        label: "Autobaud Wait Time",
        category: "System / Advanced",
        type: "integer",
        units: "ms",
        editable: false,
        hidden: true
    },
    AutoBaudTimeout: {
        label: "Autobaud Timeout",
        category: "System / Advanced",
        type: "integer",
        units: "ms",
        editable: false,
        hidden: true
    },
    AutoBaudStallTimeout: {
        label: "Autobaud Stall Timeout",
        category: "System / Advanced",
        type: "integer",
        units: "ms",
        editable: false,
        hidden: true
    },

    Flags: {
        label: "Configuration Flags",
        category: "System / Advanced",
        type: "select",
        editable: true,
        advanced: true,
        options: {
            0: "0 x00 - Factory Default (read only)",
            1: "0x01 - Save Settings",
            3: "0x03 - Restore to Factory Defaults",
            128: "0x80 - Using Saved Settings"
        },
        help: "Displaying 0 means its using the factory defaults, 128 means its using stored defaults.  Setting to 1 will save the current settings as user defaults, 3 will restore to factory defaults."
    },
    SoftReset: {
        label: "Soft Reset",
        category: "System / Advanced",
        type: "boolean",
        editable: true,
        advanced: true,
        help: "Setting this to 1 requests a firmware soft reset."
    }
};
