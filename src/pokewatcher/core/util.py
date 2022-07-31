# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

###############################################################################
# Interface
###############################################################################


def noop(*args, **kwargs):
    pass


class SleepLoop:
    """Context manager for a timed sleep loop.
    Use `n <= 0` for an infinite loop.
    Use `delay` to specify the sleep time (in seconds) between iterations.
    Includes `delta` (seconds) - time spent since the previous iteration.
    Includes the `timestamp` at which the current iteration is starting.
    Usage:

    ```
    # should run three times, with 1 second pauses between iterations
    with SleepLoop(n=3, delay=1.0) as loop:
        while loop.iterate():
            print('Iteration number:', loop.iteration)
            print('Elapsed time since the previous iteration:', loop.delta)
            print('This iteration is starting at:', loop.timestamp)
        assert loop.i == loop.n
        print('Iterated', loop.i, 'times.')
    ```
    """

    def __init__(self, n=0, delay=1.0):
        self.n = n
        self.delay = delay
        self.iterate = self._no_loop
        self.i = -1
        self.delta = 0.0
        self.timestamp = 0

    @property
    def iteration(self):
        return self.i + 1

    def _first_iteration(self):
        self.i = 0
        self.delta = 0.0
        self.timestamp = time.time()
        self.iterate = self._other_iterations
        return True

    def _other_iterations(self):
        time.sleep(self.delay)
        now = time.time()
        self.delta = now - self.timestamp
        self.timestamp = now
        self.i += 1
        if self.n <= 0 or self.i < self.n:
            return True
        self.iterate = self._no_loop
        return False

    def _no_loop(self):
        return False

    def __enter__(self):
        self.iterate = self._first_iteration
        return self

    def __exit__(self, type, value, traceback):
        self.i = -1
        self.iterate = self._no_loop
