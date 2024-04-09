from time import sleep_ms as sleep

import network
import ntptime
import webrepl
from machine import RTC, Pin

webrepl.start()

led = Pin(15, Pin.OUT)


def blink(pin, count=1, delay=1000):
    for _ in range(count):
        pin.on()
        sleep(delay)
        pin.off()
        sleep(delay)


def do_connect(ssid, key):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print("connecting to network...")
        wlan.connect(ssid, key)

        while not wlan.isconnected():
            pass

    print("network config:", wlan.ifconfig())

    ntptime.settime()
    print(RTC().datetime())

    ip, _, _, _ = wlan.ifconfig()
    last = ip.split(".")[-1]
    for _ in range(2):
        for i in [int(n) for n in last]:
            blink(led, i, 150)
            sleep(500)
        sleep(2000)


with open("config.txt") as f:
    content = f.readlines()

    config = {k.strip(): v.strip() for k, v in [line.split(":") for line in content]}
    del content


blink(led, 3, 100)
do_connect(config["SSID"], config["KEY"])
