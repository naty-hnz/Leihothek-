from mfrc522 import MFRC522
import utime
from boot2 import connection
import configure
from time import sleep
import urequests as requests

reader = MFRC522(spi_id=0,sck=6,miso=4,mosi=7,cs=5,rst=22)

print("Bring TAG closer...")
print("")


while connection.isconnected():
    reader.init()
    (stat, tag_type) = reader.request(reader.REQIDL)
    if stat == reader.OK:
        (stat, uid) = reader.SelectTagSN()
        if stat == reader.OK:
            card = int.from_bytes(bytes(uid),"little",False)
            print("CARD ID: "+str(card))
            url = f"http://{configure.SERVER}:{configure.PORT}{configure.ENDPOINT}"

            try:
                response = requests.post(url, json={"RFID-tag": card})
                answer = response.json()
                print("Server response:", answer)
            except Exception as e:
                print("Error sending data:", e)
                sleep(2)
                continue
    utime.sleep_ms(500) 


