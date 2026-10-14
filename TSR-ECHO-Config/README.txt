TSR-ECHO Combined Configuration and Ping Viewer v16 (prototype)

Open TSR-ECHO-Config.html in a Chromium browser supporting Web Serial.

Configuration and Ping Viewer share one Web Serial port and one binary reader.
Click Ping Viewer to select Raw, Filtered or Magnitude and capture a single ping.
Pending configuration changes are applied before acquisition.
The viewer temporarily changes RunMode, DoFilter and DecimationFactor via C2.
After capture, C3 refreshes the configuration shown in the Configuration tab.

Requires parameters.js, serialports.js, tsr-echo-serial.js and TSR Logo_web.png
in the same folder. No network connection is needed.

This version has not been hardware-tested.


v17: Renamed main HTML and serial JS to TSR-ECHO family names.
Added titled ping plot with labelled axes, grid and automatic tick marks.
Magnitude can be displayed as linear or relative dB (0 dB at peak, -80 dB floor).
X axis uses SpeedOfSound and SamplingFrequency if available; otherwise sample index.
Raw stride=1 ADC sample; filtered/magnitude stride=4*DecimationFactor.
Current acquisition assumed to start at ADC sample zero (RangeStart not added).
Hardware validation still required.
