#!/usr/bin/env python3

import logging
from threading import Thread, Lock
import time
from desertbus import fetcher

logger = logging.getLogger(__name__)

class FetcherThread(Thread):
    """The main VST data-fetching thread.  This is intended to be kicked off as
    soon as there's a network connection and kept up for the duration of the
    program (which, in general, will be until someone pulls the plug on the
    physical device)."""
    def __init__(self, name):
        Thread.__init__(self, daemon=True, name=name)
        self.name = name
        self._latest_stats = None
        self._lock = Lock()

    @property
    def latest_stats(self):
        """Gets the latest stats fetched on this thread.  Does all the locking
        and such as need be, too.  Returns None if nothing's been fetched
        yet."""
        self._lock.acquire(timeout=30)
        to_return = self._latest_stats
        self._lock.release()
        return to_return

    def run(self):
        logger.info('The fetcher thread is going live!')
        while True:
            try:
                results = fetcher.get_current_stats()
                logger.debug(f'Fetched stats: {results}')

                if results is not None:
                    # Since we're the only ones writing to this, we really,
                    # REALLY shouldn't need the timeout, but...
                    self._lock.acquire(timeout=30)
                    self._latest_stats = results
                    self._lock.release()
            except Exception as e:
                # Wuh oh.
                logger.exception('Fetching exception!')

            logger.debug('Sleeping for 30 seconds...')
            time.sleep(30)

