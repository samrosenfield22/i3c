# I3C -- a better i2c scanner

## About
Most i2c scanner code just iterates through the range of 7-bit i2c addresses and prints device addresses. This leaves you with plenty of work -- writing and rewriting code to read who-am-i registers, other registers, and initialize the device. I3C aims to automate this work, accelerating the bringup and debugging of embedded hardware.


<img src="elegant.jpg" width="400">

## Features
* Reads the registers of each device on the bus, dumps them
* Checks if the bus has pullups, or if any devices are pulling the bus low, before scanning
* Checks the bus logic level is 5V or 3V3

## How to use I3C
* Connect SDA, SCL and GND between the Arduino and the device under test
* Open the serial monitor (Ctrl+Shift+M)
* Run the code

That's it!
