import RPi.GPIO as gpio

from rpi.gpio import Component


class LED(Component):
    """
    LED.
    """

    class State(Component.State):
        """
        LED state.
        """

        def __init__(
                self,
                on: bool
        ):
            """
            Initialize the LED state.

            :param on: Whether or not the LED is on.
            """

            self.on = on

        def __eq__(
                self,
                other: 'LED.State'
        ) -> bool:
            """
            Check equality with another state.

            :param other: State.
            :return: True if equal and False otherwise.
            """

            return self.on == other.on

    def get(
            self
    ) -> 'LED.State':
        """
        Get the state.

        :return: State.
        """

        return self.state

    def set(
            self,
            state: 'LED.State'
    ):
        """
        Set the state and trigger any listeners.

        :param state: State.
        """

        super().set(state)

        self.state: 'LED.State'

        if self.state.on:
            gpio.output(self.output_pin, gpio.HIGH)
        else:
            gpio.output(self.output_pin, gpio.LOW)

    def __init__(
            self,
            output_pin: int
    ):
        """
        Initialize the LED.

        :param output_pin: Output pin that connects to the LED.
        """

        super().__init__(
            state=LED.State(on=False)
        )

        self.output_pin = output_pin

        gpio.setup(self.output_pin, gpio.OUT)

        self.set(self.state)
