# !/usr/bin/env python
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
# import logging.handlers
import sys
import signal
import time
import argparse
import os
import errno

__author__ = "Nikal Morgan"

logger = logging.getLogger(__name__)

files = {}
exit_flag = False


def magic_word_finder(path, start_line, magic_word):
    """Goes a file of a given type plus where to start
    and searches for given text."""
    line_number = 0
    with open(path) as f:
        for line_number, line in enumerate(f):
            if line_number >= start_line:
                if magic_word in line:
                    logger.info(
                        f"Match found for {magic_word} "
                        f"found on line {line_number+1} in {path}"
                                )
    return line_number + 1


def watch_directory(args):
    """Watches given directory for added files and deleted files,
    calls another function to find magic word in files.
    """
    file_list = os.listdir(args.directory)
    detect_added_files(file_list, args.extension)
    detect_removed_files(file_list)
    for f in files:
        path = os.path.join(args.directory, f)
        files[f] = magic_word_finder(
            path,
            files[f],
            args.magic_word
        )
    return files


def detect_added_files(file_list, ext):
    """Checks the directory if a new file was added"""
    global files
    for f in file_list:
        if f.endswith(ext) and f not in files:
            files[f] = 0
            logger.info(f"{f} added to watchlist.")
    return file_list


def detect_removed_files(file_list):
    """Checks the directory if a given file was deleted"""
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
    logger.warning('Received ' + signal.Signals(sig_num).name)
    global exit_flag
    exit_flag = True


def create_parser():
    """Create an argument parser object"""
    parser = argparse.ArgumentParser(
        description="Watches a directory of text files for a magic string"
    )
    parser.add_argument('directory', help='directory to monitor')
    parser.add_argument('magic_word', help='The magic word/words to watch for')
    parser.add_argument('-i',
                        '--interval',
                        help='Sets the interval in seconds to check the '
                             'directory for magic words',
                        type=float,
                        default=1.0)
    parser.add_argument('-x', '--extension',
                        help='Sets the type of file to watch for',
                        type=str,
                        default='.txt')
    return parser


def main(args):
    """Main function is declared as standalone, for testability"""
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    polling_interval = parsed_args.interval
    logging.basicConfig(
        format='%(asctime)s.%(msecs)03d %(name)-12s '
               '%(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d &%H:%M:%S'
    )
    logger.setLevel(logging.DEBUG)
    start_time = time.time()
    logger.info(
        '\n'
        '-------------------------------------------------\n'
        f'   Running {__file__}\n'
        f'   PID is {os.getpid()}\n'
        f'   Started on {start_time:.1f}\n'
        '-------------------------------------------------\n'
    )
    logger.info(
        f'Watching directory:{parsed_args.directory}, '
        f'File Extension:{parsed_args.extension}, '
        f'Polling Interval:{parsed_args.interval}, '
        f', Magic Text: {parsed_args.magic_word}'
    )
    # Hook into these two signals from the OS
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)
    signal.signal(signal.SIGUSR1, signal_handler)
    signal.signal(signal.SIGUSR2, signal_handler)
    while not exit_flag:
        try:
            watch_directory(parsed_args)
        except OSError as e:
            if e.errno == errno.ENOENT:
                logger.error(f"{parsed_args.directory} directory not found")
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
        f'   Stopped {__file__}\n'
        f'   Uptime was {full_time:.1f}\n'
        '-------------------------------------------------\n'
    )
    logging.shutdown()


if __name__ == "__main__":
    """Runs the main loop until an interrupt like control+c are input."""
    main(sys.argv[1:])
