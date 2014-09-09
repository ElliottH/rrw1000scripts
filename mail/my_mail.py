#! /usr/bin/env python

import os
import mailbox
import sys
import subprocess
import re
import datetime
import time
from mailbox import mbox

"""
Given an archive of all the messages delivered to a host,
this script finds all those that would have been delivered
to the filename [addr] since [date-from] and copies them
from [box] to [dst], where [box] and [dst] are mbox files.

Syntax: my_mail [box] [dst] [addr] [date-from]

This script brought to you by thunderbird, dovecot,
exim and quite a lot of swearing.
"""

# Contains a cache of email address -> { True, False } based
# on the results of deliver_to_me
g_my_addresses = { }
    


class GiveUp(Exception):
    pass

def deliver_to_me(address, mailbox):
    try:
        op = subprocess.check_output([ "exim", "-bt", address ])
    except subprocess.CalledProcessError, c:
        return False
    return (op.find("-> %s"%mailbox) != -1)

def is_mine(address, mailbox):
    if (not (address in g_my_addresses)):
        g_my_addresses[address] = deliver_to_me(address, mailbox)
    return g_my_addresses[address]

def parse_date(dstr):
    return  datetime.datetime(*(time.strptime(dstr, 
                                                  "%a %b %d %H:%M:%S %Y")[0:6]))


def go(args):
    if (len(args) != 4):
        raise GiveUp("Syntax: my_mail [box] [dst] [addr] [date-from]")

    addr = args[2]
    print " - Scanning from mailbox %s"%(args[0])
    box = mbox(args[0])
    date_re = re.compile(r'^\s*([^\s]+)\s*(.*)$')
    if (args[3] == "0"):
        since = datetime.datetime(datetime.MINYEAR, 1, 1, tzinfo =None)
    else:
        since = parse_date(args[3])
    nr_msgs= 0
    nr_total = 0
    print " - Sending matching mail to %s"%(args[1])
    new_box = mbox(args[1], create = True)
    print " - Scanning .. "
    # Scan the whole mailbox ..
    for msg in box.values():
        to = msg['envelope-to']
        if (to is None):
             to = msg['to']
        minep = is_mine(to,addr)
        nr_total = nr_total + 1
        if (nr_total % 256)== 0:
            print " = scanned %d msgs"%nr_total

        # Now extract the date on which this message was delivered.
        if (minep):
            from_line = msg.get_from()
            m = date_re.match(from_line)
            if (m is not None):
                #print "Match!"
                #print "Date: %s"%(m.group(2))
                # One of our mailservers has too load a datetime to have
                # datetime.strptime, so .. 
                a_date = parse_date(m.group(2))
                if (a_date > since):
                    # Yay.
                    print "+ %s"%(from_line)
                    nr_msgs = nr_msgs + 1
                    new_box.add(msg)
    print("Flush %d messages and close .. "%nr_msgs)
    new_box.flush()
    new_box.close()

if __name__ == "__main__":
        go(sys.argv[1:])
    
