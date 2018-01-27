#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: noah
# @Date:   2018-01-27 22:07:47
# @Last Modified by:   noah
# @Last Modified time: 2018-01-27 23:13:41
# 
# CSV Columns:
# 0 Log
# 1 Date & Time
# 2 IP address
# 3 User
# 4 Event
# 5 File/Folder
# 6 File size
# 7 File name

import csv
import argparse
import re
import ntpath
from collections import Counter

# Setup command line parser
parser = argparse.ArgumentParser(description='Process Synology File Transfer Logs')
parser.add_argument('infile', metavar='CSV', type=str, nargs='+',
                   help='CSV Export of the File Transfer Log')
args = parser.parse_args()

##
## @brief      Convert a human readable string to filesize in bytes
##
## @param      hum   a string
##
## @return     file size in bytes
##
def humanToBytes (hum):
    mult = 1
    if "Bytes" in hum:
        mult = 1
    if "KB" in hum:
        mult = pow(1024,1)
    if "MB" in hum:
        mult = pow(1024,2)
    if "GB" in hum:
        mult = pow(1024,3)
    if "TB" in hum:
        mult = pow(1024,4)
    # for s in hum.split(" "):
    #     if s.isdigit():
    snum = re.findall(r"[-+]?\d*\.\d+|\d+", hum)
    try:
        num = float(snum[0])
    except ValueError:
        return 0
    return num * mult

##
## @brief      Parses the CSV
##
## @param      fname  The filename
##
## @return     { description_of_the_return_value }
##
def parseCSV (fname):
    print("Parsing file " + fname)

    # Open CSV
    rdr = csv.reader(open(fname, 'r'), delimiter=',')

    # Get accessed Files
    lst_files = []
    for row in rdr:
        if len(row) == 8:
            # Only files with size larger than 0 and user moviefriend
            if (row[5] == "File" and 
                row[3] == "moviefriend" and 
                humanToBytes(row[6]) > 0):
                    lst_files.append(ntpath.basename(row[7]))
    
    # List with every file only once without path
    lst_files_uniq = []
    for f in lst_files:
        if f not in lst_files_uniq:
            lst_files_uniq.append(f)

    c = Counter(lst_files);
    print(c.most_common(10))
        

# Program Entry
for f in args.infile:
    parseCSV(f)