import logging
import time
from abc import ABC, abstractmethod
from copy import deepcopy
from threading import Thread, Lock
from typing import List, Tuple, Callable, Optional

import RPi.GPIO as gpio


def setup():
    """
    Set up the GPIO interface.
    """

    gpio.setmode(gpio.BOARD)


def cleanup():
    """
    Clean up the GPIO interface.
    """

    gpio.cleanup()


class Component(ABC):
    """
    Abstract base class for all components.
    """

    class State(ABC):
        """
        Abstract base class for all component states.
        """

        def __init__(
                self
        ):
            """
            Initialize the state.
            """

        @abstractmethod
        def __eq__(
                self,
                other: 'Component.State'
        ) -> bool:
            """
            Check equality with another state.

            :param other: State.
            :return: True if equal and False otherwise.
            """

        def __ne__(
                self,
                other: 'Component.State'
        ) -> bool:
            """
            Check inequality with another state.

            :param other: State.
            :return: True if not equal and False otherwise.
            """

            return not self.__eq__(other)

    def on(
            self,
            trigger: Optional[Callable[['Component.State'], bool]],
            event: Callable
    ):
        """
        Add an event trigger to the component.

        :param trigger: A function that takes the current state and returns True if event should be fired, or None to
        fire the event on every state change.
        :param event: Event to fire.
        """

        self.trigger_events.append((trigger, event))

    @abstractmethod
    def get_state(
            self
    ) -> 'Component.State':
        """
        Get the state.

        :return: State.
        """

    def set_state(
            self,
            state: 'Component.State'
    ):
        """
        Set the state and trigger events.

        :param state: State.
        """

        if state != self.state:
            self.state = state
            for trigger, event in self.trigger_events:
                if trigger is None or trigger(self.state):
                    event()

    def __init__(
            self,
            state: 'Component.State'
    ):
        """
        Initialize the component.

        :param state: Initial state.
        """

        self.state = state

        self.trigger_events: List[Tuple[Optional[Callable[['Component.State'], bool]], Callable]] = []


class Clock(Component):
    """
    A clock that ticks regularly.
    """

    class State(Component.State):
        """
        Clock state.
        """

        def __init__(
                self,
                running: bool,
                tick: int
        ):
            """
            Initialize the clock state.

            :param running: Whether the clock is running.
            :param tick: Clock tick.
            """

            self.running = running
            self.tick = tick

        def __eq__(
                self,
                other: 'Clock.State'
        ) -> bool:
            """
            Check equality with another state.

            :param other: State.
            :return: True if equal and False otherwise.
            """

            return self.running == other.running and self.tick == other.tick

    def get_state(
            self
    ) -> 'Clock.State':
        """
        Get the state.

        :return: State.
        """

        return self.state

    def start(
            self
    ):
        """
        Start the clock.
        """

        self.state: Clock.State

        with self.state_lock:
            if self.state.running:
                logging.warning('Attempted to start clock that is running.')
            else:
                self.run_thread = Thread(target=self.__run__)
                self.run_thread.start()

    def stop(
            self
    ):
        """
        Stop the clock.
        """

        self.state: Clock.State

        with self.state_lock:
            if self.state.running:
                self.state.running = False
            else:
                logging.warning('Attempted to stop clock that is not running.')

        self.run_thread.join()

        logging.info('Stopped clock.')

    def __init__(
            self,
            tick_interval_seconds: Optional[float]
    ):
        """
        Initialize the clock.

        :param tick_interval_seconds: Number of seconds to wait between clock ticks, or None to tick as quickly as
        possible.
        """

        super().__init__(
            Clock.State(
                running=False,
                tick=0
            )
        )

        self.tick_interval_seconds = tick_interval_seconds

        self.run_thread: Optional[Thread] = None
        self.state_lock = Lock()

    def __run__(
            self
    ):
        """
        Run the clock.
        """

        self.state: Clock.State

        # reset state
        with self.state_lock:
            new_state = deepcopy(self.state)
            new_state.running = True
            new_state.tick = 0
            self.set_state(new_state)

        # run until we should stop
        loop = True
        while loop:

            # sleep if we have a tick interval
            if self.tick_interval_seconds is not None:
                time.sleep(self.tick_interval_seconds)

            # watch out for race condition on the running value. only set state if we're still running.
            with self.state_lock:
                if self.state.running:
                    new_state = deepcopy(self.state)
                    new_state.tick += 1
                    self.set_state(new_state)
                else:
                    loop = False

        # set final state
        with self.state_lock:
            new_state = deepcopy(self.state)
            new_state.running = False
            self.set_state(new_state)
