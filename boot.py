from machine import Pin
from time import sleep_ms as sleep

import gc, network, ntptime, webrepl

CONNECTION_TIMEOUT = 30  # seconds


# Blink the LED on the board
def blink(pin, count=1, delay=1000):
    for _ in range(count):
        pin.on()
        sleep(delay)
        pin.off()
        sleep(delay)


# Blink the LED on the board in a sequence
def seq_blink(pin, seq, duration, delay):
    if isinstance(seq, str):
        seq = [int(n) for n in seq]

    for i in seq:
        blink(pin, i, duration)
        sleep(delay)


# Connect to a network from the known list
def start_network(connections):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    available = wlan.scan()
    ssids = {ap[0].decode() for ap in available}

    for connection in connections:
        if connection["SSID"] in ssids:
            print("Connecting to", connection["SSID"])
            wlan.connect(connection["SSID"], connection["KEY"])

            i = 0
            while not wlan.isconnected():
                if i >= CONNECTION_TIMEOUT * 2:
                    return None

                sleep(500)
                i += 1

            print("(IP, NM, GW, DNS):", wlan.ifconfig())

            ntptime.settime()
            # print(RTC().datetime())

            ip = wlan.ifconfig()[0]
            last = ip.split(".")[-1]
            seq_blink(led, last, 200, 500)
            # sleep(5000)
            # seq_blink(led, last, 200, 500)

            return wlan

    return None


if __name__ == "__main__":
    import json

    with open("config.json") as f:
        config = json.load(f)

    webrepl.start()

    led = Pin(15, Pin.OUT)
    blink(led, 3, 80)

    wlan = start_network(config["Connections"])

    if wlan is None:
        print("Failed to connect to any network")
        seq_blink(led, "404", 200, 500)
        # sleep(5000)
        # seq_blink(led, "404", 200, 500)

    gc.collect()
    print(f"Python//Free: {gc.mem_alloc()/1000:.3f}kB//{gc.mem_free()/1000:.3f}kB")
