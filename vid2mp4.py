#!/usr/bin/env python3
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Last modified: 2015-05-03 22:44:18 +0200
#
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to vid2mp4.py. This work is published from the
# Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

"""Convert all video files given on the command line to H.264/AAC streams in
an MP4 container."""

__version__ = '1.0.0'

from multiprocessing import cpu_count
from time import sleep
import os
import subprocess
import sys


def warn(s):
    """Print a warning message.

    :param s: Message string
    """
    s = ' '.join(['Warning:', s])
    print(s, file=sys.stderr)


def checkfor(args, rv=0):
    """Make sure that a program necessary for using this script is
    available.

    :param args: String or list of strings of commands. A single string may
    not contain spaces.
    :param rv: Expected return value from evoking the command.
    """
    if isinstance(args, str):
        if ' ' in args:
            raise ValueError('no spaces in single command allowed')
        args = [args]
    try:
        with open(os.devnull, 'w') as bb:
            rc = subprocess.call(args, stdout=bb, stderr=bb)
        if rc != rv:
            raise OSError
    except OSError as oops:
        outs = "Required program '{}' not found: {}."
        print(outs.format(args[0], oops.strerror))
        sys.exit(1)


def startencoder(fname):
    """Use ffmpeg to convert a video file to H.264/AAC
    streams in an MP4 container.

    :param fname: Name of the file to convert.
    :returns: a 3-tuple of a Process, input path and output path
    """
    basename, ext = os.path.splitext(fname)
    known = ['.mp4', '.avi', '.wmv', '.flv', '.mpg', '.mpeg', '.mov', '.ogv']
    if ext.lower() not in known:
        warn("File {} has unknown extension, ignoring it.".format(fname))
        return (None, fname, None)
    ofn = basename + '.mp4'
    args = ['ffmpeg', '-i', fname, '-c:v', 'libx264', '-crf', '29', '-flags',
            '+aic+mv4', '-c:a', 'libfaac', '-sn', ofn]
    with open(os.devnull, 'w') as bitbucket:
        try:
            p = subprocess.Popen(args, stdout=bitbucket, stderr=bitbucket)
            print("Conversion of {} to {} started.".format(fname, ofn))
        except:
            warn("Starting conversion of {} failed.".format(fname))
    return (p, fname, ofn)


def manageprocs(proclist):
    """Check a list of subprocesses tuples for processes that have ended and
    remove them from the list.

    :param proclist: a list of (process, input filename, output filename)
    tuples.
    """
    print('# of conversions running: {}\r'.format(len(proclist)), end='')
    sys.stdout.flush()
    for p in proclist:
        pr, ifn, ofn = p
        if pr is None:
            proclist.remove(p)
        elif pr.poll() is not None:
            print('Conversion of {} to {} finished.'.format(ifn, ofn))
            proclist.remove(p)
    sleep(0.5)


def main(argv):
    """Main program.

    :param argv: command line arguments
    """
    if len(argv) == 1:
        binary = os.path.basename(argv[0])
        print("{} version {}".format(binary, __version__), file=sys.stderr)
        print("Usage: {} [file ...]".format(binary), file=sys.stderr)
        sys.exit(0)
    checkfor(['ffmpeg', '-version'])
    avis = argv[1:]
    procs = []
    maxprocs = cpu_count()
    for ifile in avis:
        while len(procs) == maxprocs:
            manageprocs(procs)
        procs.append(startencoder(ifile))
    while len(procs) > 0:
        manageprocs(procs)


if __name__ == '__main__':
    main(sys.argv)
