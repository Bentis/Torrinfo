#!/usr/bin/python

import sys
import os

from BitTorrent.bencode import bdecode_strict, bdecode_sloppy

if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help'):
    print "USAGE: torrinfo <torrent_file>"
    sys.exit()

filename = sys.argv[1]

if not os.path.isfile(filename):
    print "ERROR: %s is not a file." % filename
    sys.exit()

file = open(filename, 'r')
data = file.read()
file.close()
try:
    torrent = bdecode_strict(data)
except ValueError:
    try:
        torrent = bdecode_sloppy(data)
    except:
        torrent = None

del data

if torrent is None:
    print "ERROR: %s is not a valid torrent file." % os.path.basename(filename)
    sys.exit()

print "Torrent: %s" % os.path.basename(filename)
print "Infohash: %s"
# if print_full_announce:
#else
# TODO: mask passkey / remove all opts
if 'announce' in torrent:
    print "Announce url: %s" % torrent['announce']

# if print_files
# TODO: print files
if 'files' in torrent['info']:
    total_size = 0L
    num_files = 0
    for file in torrent['info']['files']:
        # TOOD: print files"
        #if print_files
        #   print "\t%s - %.2f%s" % (<joined_path>, <filesize>, <fielsize_mod(MB/GB)>)
        total_size += file['length']
        num_files += 1
    print "Files: %d" % num_files
    print "Size: %.2f %s" % (total_size/(float)(1024**2), 'MiB') # FIXME dynamic
    
else:
    print "File: %s" % os.path.basename(torrent['info']['file']) # FIXME: path?
    print "Size: %.2f %s" % (torrent['info']['length']/(float)(1024**2), 'MiB') # FIXME: dynamic size

#print "dict: %s" % torrent

del torrent
