# Open Desk Lamp

<img src="/docs/lamp.jpg" width="40%" style="display: block; margin-left: auto; margin-right: auto;">

The Xiaomi Desklamp is an affordable connected Lamp that uses an ESP8266 Microcontroller internally. 
Unfortunately, users are required to register for the Xiaomi Home Service and the lamp communicates with Xiaomi servers. 
This project replaces the lamp's original firmware with privacy focussed firmware based on [Micropython](https://micropython.org/).
Pinouts for the custom ESP8266 board and other information was taken from fvollmers's 
[open-desk-lamp-firmware](https://github.com/fvollmer/open-desk-lamp-firmware) project, which is written in C and lacks IoT functionality.

## Hardware
The most difficult aspect of this project was soldering the connections onto the microprocessor to flash the new firmware.
TO open the lamp you need to peel back the rubber standoffs and remove three screws (indicated in orange below):

<img src="/docs/screws.png" width="70%" style="display: block; margin-left: auto; margin-right: auto;">

After opening the case you will find two PCBs. We are interested in the larger one, which holds the rotary encoder and the microprocessor.
First, you need to pull of the knob from the rotary encoder. This requires quite a bit of force. I wrapped the knob in tape and pulled it off using pliers.
After you have removed the knob you can remove the three screws holding the PCB in place. 
After turning the PCB over you should see the four pads that we need to solder to, as indicated below:

<img src="/docs/pins.png" width="70%" style="display: block; margin-left: auto; margin-right: auto;">

The soldering was by far the most nerve-wracking step of this project. The contacts are very close together and in proximity to small resistors on the board,
so it is important not to overheat the board and take things slow. After successfully attaching all four leads we can connect them to a serial adapter.

## Flashing Micropython
To put the ESP8266 into write mode you need to pull GPIO 0 to GND. Remember to remove the pulldown after you have completed the flashing, 
as no WiFi hotspot will be created if the pin is still pulled low. A complete installation guide can be found in the [Micropython Docs](https://docs.micropython.org/en/latest/esp8266/tutorial/intro.html).

## Setup

After installing Micropython, transfer all files in this repository (excluding README.md and the docs folder) onto the ESP. This can be done using the Micropython [webrepl tools](https://github.com/micropython/webrepl). 
If all files were successfully transferred the lamp should create a WiFi hotspot called open-desk-lamp with password open-desk-lamp after you power-cycle it. Connect to the hotspot using one of your other devices and enter `192.168.0.1` in your browser's address bar. 
At that point, you can enter the credentials that the lamp will use to connect to your home wifi.

## Usage
The lamps status can be read at `/status` using `GET`
