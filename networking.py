import network
import os
import time


def setup_access_point():
    print("Creating access point.")
    ap_if = network.WLAN(network.AP_IF)
    ap_if.config(essid='open-desk-lamp', password="open-desk-lamp")


def setup_network(attempts=1):
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
                    if attempts > 1:
                        return setup_network(attempts-1)
                    setup_access_point()
                    break
        if sta_if.isconnected():
            print('network config:', sta_if.ifconfig())