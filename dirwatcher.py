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
import argparse
import os


__author__ = "Nikal Morgan"

logger = logging.getLogger(__name__)

exit_flag = False


def magic_word_finder(dirname, magic_word, ext):
    """Goes through each file of a given type in the given directory
    and searches for given text."""
    pass


def scan_single_file(f, magic_word):
    """Checks each line of a given file and searches for a given string"""
    pass


def watch_directory(dirname):
    """Watches given directory for added files and deleted files,
    if directory doesn't exist creates directory.
    """
    pass


def detect_added_files(dirname):
    """Checks give directory if new file was added"""
    pass


def detect_removed_files(dirname):
    """Checks give directory if a file was deleted"""
    pass


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


def create_parser():
    """Create an argument parser object"""
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', help='directory to monitor')
    parser.add_argument('magic_word', help='The magic word/words to watch for')
    parser.add_argument('-i',
                        '--interval',
                        help='Sets the interval in seconds to check the '
                             'directory for magic words',
                        type=float,
                        default=1.0)
    parser.add_argument('-x', '--extension', help='Sets the type of file to '
                                                  'watch for', default='.txt')
    return parser


def main(args):
    """Main function is declared as standalone, for testability"""
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    # Hook into these two signals from the OS
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    logger.info(parsed_args)
    logger.info("Starting Dirwatcher")
    start_time = time.time()
    polling_interval = parsed_args.interval

    while not exit_flag:
        try:
            magic_word_finder(
                parsed_args.directory,
                parsed_args.magic_word,
                parsed_args.extension,
            )
        except OSError as e:
            logger.warning(e)
            time.sleep(10)
        except Exception as e:
            logger.exception(e)
            time.sleep(10)
        time.sleep(polling_interval)

    logger.info("\nExiting.\n"
                "Process ran for {} seconds".format(time.time() - start_time))

    if __name__ == "__main__":
        """Runs the main loop until an interrupt like control+c are input."""
        logger.info("My Pid is {}".format(os.getpid()))
        logger.info("Command line arguments: {}".format(sys.argv))
        main(sys.argv[1:])
