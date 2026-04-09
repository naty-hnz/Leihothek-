from machine import Pin
from utime import sleep_us

class HX711:
    def __init__(self, data_pin, clock_pin, gain=128):
        self.pdat = Pin(data_pin, Pin.IN)
        self.psck = Pin(clock_pin, Pin.OUT)
        self.psck.value(0)
        self.gain = 0
        self.offset = 0
        self.scale = 1
        self.set_gain(gain)

    def set_gain(self, gain):
        if gain == 128:
            self.gain = 1
        elif gain == 64:
            self.gain = 3
        elif gain == 32:
            self.gain = 2
        self.read()

    def is_ready(self):
        return self.pdat.value() == 0

    def read(self):
        while not self.is_ready():
            pass
        result = 0
        for _ in range(24):
            self.psck.value(1)
            sleep_us(1)
            result = (result << 1) | self.pdat.value()
            self.psck.value(0)
            sleep_us(1)
        for _ in range(self.gain):
            self.psck.value(1)
            sleep_us(1)
            self.psck.value(0)
            sleep_us(1)
        if result & 0x800000:
            result -= 0x1000000
        return result

    def read_average(self, times=10):
        total = 0
        for _ in range(times):
            total += self.read()
        return total / times

    def tare(self, times=15):
        self.offset = self.read_average(times)
        print("Tare done. Offset:", self.offset)

    def set_scale(self, scale):
        self.scale = scale

    def get_units(self, times=5):
        return (self.read_average(times) - self.offset) / self.scale