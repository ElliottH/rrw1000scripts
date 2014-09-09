#! /usr/bin/env python
#

"""
So, python's mailbox implementation tries to load the whole mailbox.
This ends badly when your mailbox is very big and your mail server is
very small.
So, this is a program which tries to split big mailboxes into lots of
 small ones. 

Syntax: split_mail.py <infile> <approx#bytes> <outstem>

 We detect new messages with r'^From '.
"""

import sys
import os

class GiveUp(Exception):
    pass

def out_file_name(stem, idx):
    return "%s.%d"%(stem, idx)

def go(args):
    if (len(args) != 3):
        print __doc__
        sys.exit(1)
    
    (infile, sbytes, outstem) = args
    nr_bytes = int(sbytes)
    print("+ Open %s .. "%(infile))
    in_f = open(infile, "r")
    b_in_file = 0
    p = 0
    current_idx = 0
    out_f = open(out_file_name(outstem, current_idx), "w")
    print " + Writing %s .. "%(out_file_name(outstem, current_idx))

    while True:
        l = in_f.readline()
        # All done
        if (len(l) == 0):
            break
        if (l.find("From ") == 0):
            # Start of a new message.
            if (b_in_file > nr_bytes):
                print " + Finished writing %s"%(out_file_name(outstem, current_idx))
                out_f.close()
                current_idx = current_idx + 1
                b_in_file = 0
                out_f = open(out_file_name(outstem, current_idx), "w")
                print " + Writing %s .. "%(out_file_name(outstem, current_idx))
        out_f.write(l)
        b_in_file = b_in_file + len(l)
        p = p + len(l)
        if (p > (1024*1024)):
            print"  > .. another %d bytes .. "%(p)
            p = 0
    out_f.close()
    print "All done. \n"


if __name__ == "__main__":
    go(sys.argv[1:])
