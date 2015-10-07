#!/usr/bin/env python3
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Last modified: 2015-10-08 01:25:22 +0200
#
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to tiff2pdf.py. This work is published from
# the Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

"""Convert TIFF files to PDF format using the utilities tiffinfo and tiff2pdf
from the libtiff package."""

__version__ = '1.1.0'

from concurrent.futures import ThreadPoolExecutor
import argparse
import logging
import os
import re
import subprocess
import sys


def main(argv):
    """
    Entry point for tifftopdf.

    Arguments:
        argv: command line arguments
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--log', default='warning',
                        choices=['debug', 'info', 'warning', 'error'],
                        help="logging level (defaults to 'warning')")
    parser.add_argument('-v', '--version',
                        action='version',
                        version=__version__)
    parser.add_argument("files", metavar='file', nargs='+',
                        help="one or more files to process")
    args = parser.parse_args(argv)
    logging.basicConfig(level=getattr(logging, args.log.upper(), None),
                        format='%(levelname)s: %(message)s')
    logging.debug('command line arguments = {}'.format(argv))
    logging.debug('parsed arguments = {}'.format(args))
    checkfor('tiffinfo', 255)
    checkfor(['tiff2pdf', '-v'])
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as tp:
        convs = tp.map(tiffconv, args.files)
    convs = [(fn, rv) for fn, rv in convs if rv != 0]
    for fn, rv in convs:
        print('Conversion of {} failed, return code {}'.format(fn, rv))


def checkfor(args, rv=0):
    """
    Make sure that a program necessary for using this script is available.
    Exits the program is the requirement cannot be found.

    Arguments:
        args: String or list of strings of commands. A single string may
            not contain spaces.
        rv: Expected return value from evoking the command.
    """
    if isinstance(args, str):
        if ' ' in args:
            raise ValueError('no spaces in single command allowed')
        args = [args]
    try:
        rc = subprocess.call(args, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
        if rc != rv:
            raise OSError
        logging.info('found required program "{}"'.format(args[0]))
    except OSError as oops:
        outs = 'required program "{}" not found: {}.'
        logging.error(outs.format(args[0], oops.strerror))
        sys.exit(1)


def tiffconv(fname):
    """
    Start a tiff2pdf process for the file fname.

    Arguments:
        name: Name of the tiff file to convert.

    Returns:
        A 2-tuple (input filename, tiff2pdf return value).
    """
    try:
        args = ['tiffinfo', fname]
        txt = subprocess.check_output(args, stderr=subprocess.DEVNULL)
        txt = txt.decode('utf-8').split()
        if 'Width:' not in txt:
            raise ValueError('no width in TIF')
        index = txt.index('Width:')
        width = float(txt[index + 1])
        length = float(txt[index + 4])
        try:
            index = txt.index('Resolution:')
            xres = float(txt[index + 1][:-1])
            yres = float(txt[index + 2])
        except ValueError:
            xres, yres = None, None
        outname = re.sub('\.tif{1,2}?$', '', fname,
                         flags=re.IGNORECASE) + '.pdf'
        if xres:
            args = ['tiff2pdf', '-w', str(width / xres), '-l',
                    str(length / xres), '-x', str(xres), '-y', str(yres), '-o',
                    outname, fname]
        else:
            args = ['tiff2pdf', '-o', outname, '-z', '-p', 'A4', '-F', fname]
            ls = "no resolution in {}. Fitting to A4"
            logging.warning(ls.format(fname))
        ls = 'starting conversion of "{}" to "{}"'
        logging.info(ls.format(fname, outname))
        rv = subprocess.call(args, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
        logging.info('finished "{}"'.format(outname))
        return (fname, rv)
    except Exception as e:
        ls = 'starting conversion of "{}" failed: {}'
        logging.error(ls.format(fname, str(e)))
        return (fname, 0)


if __name__ == '__main__':
    main(sys.argv[1:])
