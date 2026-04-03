Hardware Needed
Raspberry Pi Pico W
Load cell (usually 4-wire)
HX711 load cell amplifier/ADC module
Jumper wires
Breadboard (optional)

Wiring the Components
a. Connect the Load Cell to HX711
Most load cells have four wires: Red, Black, White, Green (colors may differ, check your load cell's datasheet)

Red: Excitation+ (E+)
Black: Excitation- (E-)
White: Output- (A-)
Green: Output+ (A+)
Connect as follows:

Red → E+ on HX711
Black → E- on HX711
White → A- on HX711
Green → A+ on HX711
b. Connect the HX711 to Raspberry Pi Pico W
The HX711 typically has these pins:

VCC (Power, 3.3V-5V)
GND (Ground)
DT (Data)
SCK (Clock)
Connect:

VCC (HX711)     3.3V (Pin 36 or 39 on Pico)
GND (HX711) → GND (Pico, any ground pin)
DT (HX711) → Pico GPIO pin (e.g., GP1)
SCK (HX711) → Pico GPIO pin (e.g., GP0)
Note: You can choose any available GPIO pins, just note which ones for the code.

Connection Table
HX711	Pico Pin	Pin Number
VCC	3V3	36, 39
GND	GND	Any GND
DT	GP1	2
SCK	GP0	1

Python code 

from machine import Pin
from hx711 import HX711
import time

dt = Pin(1, Pin.IN, pull=None)   # DT to GP1
sck = Pin(0, Pin.OUT)            # SCK to GP0

hx = HX711(d_out=dt, pd_sck=sck)
hx.tare()  # tare the scale (do this with no weight on the sensor!)

while True:
    print('Weight:', hx.read())
    time.sleep(1)