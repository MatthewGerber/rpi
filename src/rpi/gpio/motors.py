from rpi.gpio import Component
import RPi.GPIO as gpio


class DcMotor(Component):

    class State(Component.State):

        def __init__(
                self,
                speed: int
        ):
            self.speed = speed

        def __eq__(
                self,
                other: object
        ) -> bool:

            if not isinstance(other, DcMotor.State):
                raise ValueError(f'Expected a {DcMotor.State}')

            return self.speed == other.speed

        def __str__(
                self
        ) -> str:

            return f'Speed:  {self.speed}'

    def set_state(
            self,
            state: Component.State
    ):
        if not isinstance(state, DcMotor.State):
            raise ValueError(f'Expected a {DcMotor.State}')

        super().set_state(state)

        state: DcMotor.State

        if state.speed < 0:
            gpio.output(self.in_1_pin, gpio.HIGH)
            gpio.output(self.in_2_pin, gpio.LOW)
        elif state.speed > 0:
            gpio.output(self.in_1_pin, gpio.LOW)
            gpio.output(self.in_2_pin, gpio.HIGH)

        self.pwm_enable.ChangeDutyCycle(state.speed)

    def start(
            self
    ):
        self.state: DcMotor.State

        self.pwm_enable.start(self.state.speed)

    def stop(
            self
    ):
        self.pwm_enable.stop()

    def set_speed(
            self,
            speed: int
    ):
        self.set_state(DcMotor.State(speed))

    def __init__(
            self,
            enable_pin: int,
            in_1_pin: int,
            in_2_pin: int
    ):
        super().__init__(DcMotor.State(0))

        self.enable_pin = enable_pin
        self.in_1_pin = in_1_pin
        self.in_2_pin = in_2_pin

        self.pwm_enable = gpio.PWM(self.enable_pin, 1000)
        gpio.setup(self.in_1_pin, gpio.OUT)
        gpio.setup(self.in_2_pin, gpio.OUT)
