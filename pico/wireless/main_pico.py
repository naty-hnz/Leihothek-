from boot import connection

while connection.isconnected():
    # read temperature
    from machine import ADC

    sensor = ADC(26)

    prop = 3.3 / 65535
    v_out = sensor.read_u16() * prop

    temp = (100 * v_out) - 50

    # send temperature to server
    import config
    import urequests as requests
    
    url = f"http://{config.SERVER}:{config.PORT}:{config.ENDPOINT}"
    
    response = requests.post(url, json=temp)

    # flash internal LED indicating temperature was sent
    from time import sleep
    from machine import Pin

    led = Pin(15, Pin.OUT)  # gewijzigd pinnummer

    for _ in range(5):
        led.on()
        sleep(1)
        led.off()
        sleep(1)
    # read server response
    answer = response.json()

    # set or unset warning LED if server tells us to do so
    if answer == "warning":
        led.on()
        sleep(2)
        led.off()

    # sleep a little until next temperature reading
    sleep(1)
