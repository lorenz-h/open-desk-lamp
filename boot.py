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

from networking import setup_network


print("Welcome to Open-Desk-Lamp")
setup_network()



