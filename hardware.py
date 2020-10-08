import machine
import utime as time


class RotaryEncoder:
    def __init__(self, clk_pin, dt_pin, button_pin):
        self.clk = machine.Pin(clk_pin, machine.Pin.IN)
        self.dt = machine.Pin(dt_pin, machine.Pin.IN)

        self.button = machine.Pin(button_pin, machine.Pin.IN)
        self.delta = 0
        self.clk_state = self.clk.value()
        self.pressed = False
        self.press_start = 0

    def update(self):
        # returns 0 if button went down, 1 if button is released, 2 if button in released after being pressed shortly
        clkState = self.clk.value()
        dtState = self.dt.value()
        if clkState != self.clk_state:
            if dtState != clkState:
                self.delta += 1
            else:
                self.delta -= 1
        self.clk_state = clkState

        if not bool(self.button.value()) and not self.pressed:
            print("Encoder button pressed")
            self.delta = 0
            self.press_start = time.ticks_ms()
            self.pressed = True
            return 0

        if self.pressed and bool(self.button.value()):
            print("Encoder button released")
            press_duration = time.ticks_diff(time.ticks_ms(), self.press_start)
            self.pressed = False
            self.delta = 0
            if press_duration < 600:
                return 2
            else:
                return 1

        return None


class CappedValue:
    def __init__(self, val, min_val, max_val):
        self.value = val
        assert min_val <= val <= max_val, "minimum value for capped value mast be smaller than maximum value"
        self.min_val = min_val
        self.max_val = max_val

    def update(self, value):
        if value < self.min_val:
            self.value = self.min_val
        elif value > self.max_val:
            self.value = self.max_val
        else:
            self.value = value

    def __call__(self, value=None):
        if value is not None:
            self.update(value)

        return self.value

    def __iadd__(self, other):
        self.update(self.value + other)
        return self

    def __isub__(self, other):
        self.update(self.value - other)
        return self


class LampHardware:

    max_duty_cycle = 200

    def __init__(self):
        self.pwm1 = machine.PWM(machine.Pin(4), freq=1000, duty=0)
        self.pwm2 = machine.PWM(machine.Pin(5), freq=1000, duty=0)
        self.rotary_encoder = RotaryEncoder(12, 13, 2)

        self.brightness = CappedValue(0.7, 0.0, 1.0)
        self.color = CappedValue(0.5, 0.0, 1.0)
        self.on = False

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.fade_down(duration=1)
        self.update_leds()

    def update_leds(self, ignore_off=False):
        if self.on or ignore_off:
            total_duty = self.max_duty_cycle * self.brightness()
            self.pwm1.duty(int(total_duty*self.color()))
            self.pwm2.duty(int(total_duty * (1-self.color())))
        else:
            self.pwm1.duty(0)
            self.pwm2.duty(0)

    def fade_up(self, duration: float = 3, steps=20, target=1.0):
        self.brightness.update(0.0)

        for i in range(steps):
            self.brightness += target / steps
            time.sleep(duration / steps)
            self.update_leds()
        self.brightness.update(target)
        self.update_leds()

    def fade_down(self, duration: float = 3, steps=20):
        start_val = self.brightness()
        for i in range(steps):
            self.brightness -= start_val / steps
            time.sleep(duration / steps)
            self.update_leds(ignore_off=True)
        self.brightness.update(0.0)
        self.update_leds()

    def pulse(self, duration=1.0, n=2):
        self.on = True
        for _ in range(n):
            self.fade_up(duration=0.5*duration, steps=int(10*duration))
            self.fade_down(duration=0.5*duration, steps=int(10*duration))
        self.on = False

    def update(self):
        for i in range(10):
            event = self.rotary_encoder.update()
            time.sleep_ms(1)
            if event is not None:
                print("Encountered event" + str(event))

            if event == 2:
                self.on = not self.on
                if self.on and self.brightness() == 0.0:
                    self.brightness(0.5)
                if self.on:
                    self.fade_up(1, 10, self.brightness() + 0)
                else:
                    self.fade_down(1, 10)
                print("Lamp is now on: " + str(self.on) + ". Brightness: " + str(self.brightness()))

        if self.on:
            if not self.rotary_encoder.pressed:
                self.brightness += -1 * self.rotary_encoder.delta / 25
                self.rotary_encoder.delta = 0
            else:
                self.color += -1 * self.rotary_encoder.delta / 25
                self.rotary_encoder.delta = 0

        self.update_leds()

    async def loop(self):
        while True:
            self.update()

