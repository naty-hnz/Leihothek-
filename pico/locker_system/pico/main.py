import network
import urequests as requests
import utime
import ujson
from machine import Pin
from hx711driver import HX711
from mfrc522 import MFRC522
import configure




# ─── Wi-Fi ───────────────────────────────────────────────────────────────────
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(configure.WIFI_SSID, configure.WIFI_PASSWORD)
    retries = 0
    while not wlan.isconnected():
        if retries >= 15:
            print("Wi-Fi failed — check configure.py")
            return False
        retries += 1
        print(f"  Connecting ({retries}/15)...")
        utime.sleep(1)
    print("Wi-Fi connected:", wlan.ifconfig()[0])
    return True

# ─── Hardware ────────────────────────────────────────────────────────────────
green_led  = Pin(configure.GREEN_LED_PIN, Pin.OUT, value=0)
red_led    = Pin(configure.RED_LED_PIN,   Pin.OUT, value=0)
locker_pin = Pin(configure.LOCKER_PIN,    Pin.OUT, value=0)

rfid = MFRC522(
    spi_id=configure.RFID_SPI_ID,
    sck=configure.RFID_SCK,
    miso=configure.RFID_MISO,
    mosi=configure.RFID_MOSI,
    cs=configure.RFID_CS,
    rst=configure.RFID_RST,
)

hx = HX711(data_pin=configure.HX711_DT, clock_pin=configure.HX711_SCK)

# ─── LED helpers ─────────────────────────────────────────────────────────────
def leds_off():
    green_led.value(0)
    red_led.value(0)

def led_green():
    red_led.value(0)
    green_led.value(1)

def led_red():
    green_led.value(0)
    red_led.value(1)

def blink_green(times=3):
    for _ in range(times):
        green_led.value(1); utime.sleep_ms(200)
        green_led.value(0); utime.sleep_ms(200)

def blink_red(times=3):
    for _ in range(times):
        red_led.value(1); utime.sleep_ms(200)
        red_led.value(0); utime.sleep_ms(200)

# ─── Scale ───────────────────────────────────────────────────────────────────
def get_weight():
    return hx.get_units(times=10)

# ─── Locker control ──────────────────────────────────────────────────────────
def open_locker(duration_ms=3000):
    locker_pin.value(1)
    print("  Locker opened")
    utime.sleep_ms(duration_ms)
    locker_pin.value(0)
    print("  Locker locked")

# ─── Server communication ─────────────────────────────────────────────────────
BASE_URL = f"http://{configure.PC_SERVER}:{configure.PC_PORT}/api"

def post(endpoint, payload):
    try:
        r = requests.post(f"{BASE_URL}{endpoint}", json=payload)
        data = r.json()
        r.close()
        return data
    except Exception as e:
        print("  Network error:", e)
        return None

def send_event(event, tag_id=None, weight=None):
    payload = {"event": event}
    if tag_id  is not None: payload["tag_id"] = tag_id
    if weight  is not None: payload["weight"]  = round(weight, 1)
    return post("/locker_event", payload)

def send_weight(weight):
    return post("/weight_update", {"weight": round(weight, 1)})

# ─── Startup ─────────────────────────────────────────────────────────────────
print("\n=== Locker system starting ===")
leds_off()

print("Taring scale — keep it empty...")
utime.sleep(2)
hx.tare(times=configure.TARE_SAMPLES)
hx.set_scale(configure.SCALE_FACTOR)
print("Scale ready.")

if not connect_wifi():
    blink_red(10)
    raise SystemExit

print("Ready — scan a tag.\n")
blink_green(2)

# ─── State ───────────────────────────────────────────────────────────────────
last_weight    = 0.0
weight_poll_ms = 1000
last_poll      = utime.ticks_ms()

# ─── Main loop ───────────────────────────────────────────────────────────────
while True:
    now = utime.ticks_ms()

    # Poll weight every second and send to server
    if utime.ticks_diff(now, last_poll) >= weight_poll_ms:
        weight = get_weight()
        last_weight = weight
        send_weight(weight)

        # Detect item removed
        if weight < configure.WEIGHT_THRESHOLD:
            leds_off()

        last_poll = now

    # Check for RFID scan
    rfid.init()
    stat, _ = rfid.request(rfid.REQIDL)
    if stat == rfid.OK:
        stat, uid = rfid.SelectTagSN()
        if stat == rfid.OK:
            tag_id = int.from_bytes(bytes(uid), "little", False)
            weight = last_weight
            print(f"Tag scanned: {tag_id}  weight: {weight:.1f}g")

            response = send_event("rfid_scan", tag_id=tag_id, weight=weight)

            if response:
                action   = response.get("action")
                expected = response.get("expected", 0)

                if action == "open_checkout":
                    # Taking item out
                    blink_green(2)
                    open_locker()
                    leds_off()

                elif action == "open_return_ok":
                    # Returning item — weight correct
                    led_green()
                    print(f"  Item successfully returned ({weight:.1f}g)")
                    open_locker()
                    utime.sleep(2)
                    leds_off()

                elif action == "return_wrong_weight":
                    # Returning item — weight wrong
                    led_red()
                    print(f"  Wrong weight! Got {weight:.1f}g, expected ~{expected:.1f}g")
                    utime.sleep(5)
                    leds_off()

                elif action == "unknown_tag":
                    blink_red(3)
                    print("  Unknown tag — denied")

                else:
                    blink_red(2)

            utime.sleep_ms(1500)  # debounce

    utime.sleep_ms(100)
