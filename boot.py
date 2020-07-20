# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#uos.dupterm(None, 1) # disable REPL on UART(0)
import gc
import webrepl
import utime as time
import network
import os
webrepl.start()
gc.collect()


def setup_access_point():
    print("Creating access point.")
    ap_if = network.WLAN(network.AP_IF)
    ap_if.config(essid='open-desk-lamp', password="open-desk-lamp")


def setup_network():
    CREDS_FNAME = "creds"
    CONN_TIMEOUT = 10000 #in ms
    if CREDS_FNAME not in os.listdir("/"):
        print("No credentials found")
        setup_access_point()
    else:
        with open(CREDS_FNAME, "r") as fp:
            user, passwd = fp.read().replace("\r", "").split("\n")

        sta_if = network.WLAN(network.STA_IF)
        if not sta_if.isconnected():
            print('connecting to network...')
            sta_if.active(True)
            sta_if.connect(user, passwd)
            start_time = time.ticks_ms()
            while not sta_if.isconnected():
                time.sleep(0.5)
                if time.ticks_diff(time.ticks_ms(), start_time) > CONN_TIMEOUT:
                    setup_access_point()
                    break
        if sta_if.isconnected():
            print('network config:', sta_if.ifconfig())


print("Welcome to Open-Desk-Lamp")
setup_network()



