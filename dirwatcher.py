#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Thi program monitors a given directory for text files that are created within
the monitored directory. It will continually search within all files in the
directory for a given "magic string" (implemented with a timed polling loop).
If the magic string is found in a file, the program will log a message
indicating which file, and the line number within the file where the magic
text was found; it will not be logged again unless it appears in the file as
another subsequent line entry later on.
"""


import logging
import sys
import signal
import time

__author__ = "Nikal Morgan"

logger = logging.getLogger(__name__)


exit_flag = False


def signal_handler(sig_num, frame):
    """
    This is a handler for SIGTERM and SIGINT.
    Other signals can be mapped here as well (SIGHUP?)
    Basically, it just sets a global flag, and main() will exit its loop
    if the signal is trapped.
    :param sig_num: The integer signal number that was trapped from the OS.
    :param frame: Not used
    :return None
    """
    # log the associated signal name
    logger.warn('Received ' + signal.Signals(sig_num).name)
    global exit_flag
    exit_flag = True


def main():
    # Hook into these two signals from the OS
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    # Now my signal_handler will get called if OS sends
    # either of these to my process.
    start_time = time.time()

    while not exit_flag:
        try:
            # call my directory watching function
            # put a sleep inside my while loop
            # so I don't peg the cpu usage at 100%
            time.sleep(polling_interval)
            pass
        except Exception as e:
            logger.exception(e)
            time.sleep(10)
    
    logger.info("\nExiting.\n"
                "Process ran for {} seconds".format(time.time() - start_time))

    if __name__ == "__main__":
        """Runs the main loop until an interrupt like control+c are input."""
        main(sys.argv[1:])
