#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: noah
# @Date:   2018-01-27 22:07:47
# @Last Modified by:   Noah Huetter
# @Last Modified time: 2018-01-31 11:37:19
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
# 


import csv
import argparse
import re
import os

from collections import Counter

lst_files = []
lst_files_uniq = []
lst_users = []
fd = []
rdr = []

# Setup command line parser
parser = argparse.ArgumentParser(description='Process Synology File Transfer Logs')
parser.add_argument('infile', metavar='CSV', type=str, nargs='+',
                   help='CSV Export of the File Transfer Log')
parser.add_argument('-u', dest='user', type=str,
                   help='User to analyze')
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

def printUsers (lst_users):
    print("- Users ----------------------------")
    for usr in lst_users:
        print("|  %s" % usr)
    print("------------------------------------")


##
## @brief      Parses the CSV
##
## @param      fname  The filename
##
## @return     { description_of_the_return_value }
##
def parseCSV (fname):
    global lst_files
    global lst_files_uniq
    global lst_users
    global fd
    global rdr

    print("Parsing file " + fname)

    # Open CSV
    fd = open(fname, 'r')
    rdr = csv.reader(fd, delimiter=',')

    # Get accessed 
    for row in rdr:
        if len(row) == 8:
            # Only files with size larger than 0
            if (row[5] == "File" and 
                humanToBytes(row[6]) > 0):
                    lst_files.append(os.path.basename(row[7]))
    
    # List of all users
    fd.seek(0)
    for row in rdr:
        if len(row) == 8:
            usr = row[3]
            if usr not in lst_users:
                lst_users.append(usr)

    # List with every file only once without path
    for f in lst_files:
        if f not in lst_files_uniq:
            lst_files_uniq.append(f)

    # c = Counter(lst_files)
    # print(c.most_common(10))

def userAnalytics(user):
    global lst_files
    global lst_files_uniq
    global lst_users
    global fd
    global rdr

    # Open CSV
    fd.seek(0)

    # User accessed files
    lst_user_files = []
    for row in rdr:
        if len(row) == 8:
            # Only files with size larger than 0
            if (row[5] == "File" and
                row[3] == user and 
                humanToBytes(row[6]) > 0):
                    lst_user_files.append(row[7])

    # Number of total files accessed
    n_files_accessed = len(set(lst_user_files))

    # unique list of accessed files
    lst_user_files_unique = []
    for f in lst_user_files:
        if f not in lst_user_files_unique:
            lst_user_files_unique.append(f)

    # Count file accesses
    c = Counter(lst_user_files)
    most_c = c.most_common()

    # Print user global information
    print("- User stats ----------------------------")
    print("| For User: %s" % user)
    print("|     Total accessed files: %d" % n_files_accessed)
    print("---------------------------------------------")

    # Print ranking of file accesses
    i = 1
    print("- Accessed Files ----------------------------")
    print("|  No   Cnt File")
    print("---------------------------------------------")
    for entry in most_c:
        print("| %3d %5d %s" % (i, entry[1], os.path.basename(entry[0])))
        i = i + 1
    print("---------------------------------------------")


############################################################
#
# Program Entry
# 
############################################################
# parse all files
for f in args.infile:
    parseCSV(f)

# Print user statistics
# printUsers(lst_users)

# If specified, analyze user statistics
if args.user:
    userAnalytics(args.user)
    




