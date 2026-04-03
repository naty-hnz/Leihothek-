from hx711 import HX711
from utime import sleep

# --- Setup ---
# DT = GP2 (pin 4), SCK = GP3 (pin 5)
hx = HX711(data_pin=2, clock_pin=3)

# --- Calibration ---
# Step 1: Tare (zero the scale with nothing on it)
print("Remove everything from the scale and press enter...")
input()
hx.tare()

# Step 2: Put a known weight on and enter its value
print("Place a known weight on the scale and enter its weight in grams:")
known_weight = float(input())
raw = hx.read_average(times=10)
scale_factor = (raw - hx.offset) / known_weight
hx.set_scale(scale_factor)
print(f"Calibration done. Scale factor: {scale_factor:.2f}")
print("You can hardcode this value next time to skip calibration.\n")

# --- Live reading ---
print("Reading weight... (Ctrl+C to stop)")
while True:
    weight = hx.get_units(times=5)
    print(f"Weight: {weight:.1f} g")
    sleep(1)