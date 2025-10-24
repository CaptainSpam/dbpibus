#!/usr/bin/env python3

from dataclasses import dataclass
from threading import Thread, Lock
import time
from desertbus import fetcher, vst_data

@dataclass()
class SharedData:
    """The data shared between FetcherThread and whatever calls
    FetcherThread."""

    # The lock.  Don't change this.
    lock: Lock = Lock()

    # The fetched VstData object.  Will be defined if something's waiting to be
    # processed, None otherwise.  This should be set to something non-None by
    # the FetcherThread and reset to None after it's read by whatever's reading
    # it.
    #
    # It's not a queue because, while that does have its own locking mechanism,
    # there's no need to process any potentially missed fetches.  Plus, it's
    # phenomenally unlikely any fetches will be missed; this should be polled
    # far more frequently than the fetch occurs.
    pending_stats: vst_data.VstData = None

class FetcherThread(Thread):
    """The main VST data-fetching thread.  This is intended to be kicked off as
    soon as there's a network connection and kept up for the duration of the
    program (which, in general, will be until someone pulls the plug on the
    physical device)."""
    def __init__(self, name):
        Thread.__init__(self, daemon=True, name=name)
        self.name = name
        self._shared_data = SharedData()

    @property
    def shared_data(self):
        """The shared reference for both the lock and the fetched data."""
        return self._shared_data

    def run(self):
        while True:
            try:
                results = fetcher.get_current_stats()

                if results is not None:
                    # Since we're the only ones writing to this, we really,
                    # REALLY shouldn't need the timeout, but...
                    self._shared_data.lock.acquire(timeout=30)
                    self._shared_data.pending_stats = results
                    self._shared_data.lock.release()
            except Exception as e:
                # Wuh oh.
                # TODO: Maybe swap this for some proper logging sort of thing?
                print(f'fetcher_thread: FETCHING EXCEPTION!  {type(e)}: {e.args}')

            time.sleep(30)

