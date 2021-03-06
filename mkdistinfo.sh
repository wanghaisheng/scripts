#!/bin/sh
# Create a distinfo file for a FreeBSD port.
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2014-11-30 22:20:56 +0100
# Last modified: 2016-03-20 18:52:00 +0100
#
# To the extent possible under law, R.F. Smith has waived all copyright and
# related or neighboring rights to mkdistinfo.sh. This work is published
# from the Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

set -e
if [ ! -f "$1" ]; then
    echo "Usage: $0 file [>distinfo]";
    exit 1;
fi

# Gather the necessary data
FN=$(basename $1)
CHSUM=$(sha256 -q $1)
SZ=$(ls -l $1|awk '{print $5};')

# Print the distinfo
echo "SHA256 (${FN}) = ${CHSUM}"
echo "SIZE (${FN}) = ${SZ}"
