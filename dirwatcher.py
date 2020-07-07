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
import errno

__author__ = "Nikal Morgan"

logger = logging.getLogger(__file__)

files = {}
exit_flag = False


def magic_word_finder(dirname, magic_word, start_line):
    """Goes a file of a given type plus where to start and searches for given text."""
    pass


def watch_directory(args):
    """Watches given directory for added files and deleted files,
    if directory doesn't exist creates directory.
    """
    logger.info('Watching directory:{}, File Extension:{}, Polling Interval:{}'
                ', Magic Text: {}'.format(args.directory, args.extension,
                                          args.interval, args.magic_word)
                )
    while not os.path.isdir(args.directory):
        # complain
        pass
    file_list = os.listdir(args.directory)
    detect_added_files(file_list, args.extension)
    detect_removed_files(file_list)
    for f in files:
        files[f] = magic_word_finder(
            os.path.join(args.directory, f),
            files[f],
            args.magic_word
        )


def detect_added_files(file_list, ext):
    """Checks give directory if new file was added"""
    global files
    for f in file_list:
        if f.endswith(ext) and f not in files:
            files[f] = 0
            logger.info(f"{f} added to watchlist.")
    return file_list


def detect_removed_files(file_list):
    """Checks give directory if a file was deleted"""
    global files
    for f in list(files):
        if f not in file_list:
            logger.info(f"{f} removed from watchlist.")
            del files[f]
    return file_list


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
    logging.basicConfig(
        format='%(asctime)s.%(msecs)03d %(name)-12s'
               '%(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d &%H:%M:%S'
    )
    logger.setLevel(logging.DEBUG)
    start_time = time.time()
    logger.info(
        '\n'
        '-------------------------------------------------\n'
        '   Running {}\n'
        '   Started on {}\n'
        '-------------------------------------------------\n'
        .format(__file__, start_time.isoformat())
    )
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    polling_interval = int(float(parsed_args.interval))
    # Hook into these two signals from the OS
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    while not exit_flag:
        try:
            watch_directory(args)
        except OSError as e:
            if e.errno == errno.ENOENT:
                logger.error(f"{args.path} directory not found")
                time.sleep(2)
            else:
                logger.error(e)
        except Exception as e:
            logger.error(f"UNHANDLED EXCEPTION:{e}")
        time.sleep(polling_interval)

    full_time = time.time() - start_time
    logger.info(
        '\n'
        '-------------------------------------------------\n'
        '   Stopped {}\n'
        '   Uptime was {}\n'
        '-------------------------------------------------\n'
        .format(__file__, full_time.isoformat())
    )
    logging.shutdown()

    if __name__ == "__main__":
        """Runs the main loop until an interrupt like control+c are input."""
        logger.info("My Pid is {}".format(os.getpid()))
        logger.info("Command line arguments: {}".format(sys.argv))
        main(sys.argv[1:])
