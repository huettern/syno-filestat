#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: noah
# @Date:   2018-01-27 22:07:47
# @Last Modified by:   Noah Huetter
# @Last Modified time: 2018-02-05 12:33:23
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
parser.add_argument('-m', dest='month', type=int,
                   help='Month to analyze of current year [1-12]')
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
## @brief      Checks if the date is in the given month [1-12]
##             Date Format: 2018/01/23 22:41:13
##
## @param      date  The date
## param[in]   month Month [1-12]
##
## @return     True if in month, False otherwise.
##
def isInMonth (date, month):
    dat = date.split("/")
    m = int(dat[1])
    if m == month:
        return True
    else:
        return False

def printUsers (lst_users):
    print("- Users ----------------------------")
    for usr in lst_users:
        print("|  %s" % usr)
    print("------------------------------------")

##
## @brief      Convert numver to month string value
##
## @param      num   The number
##
## @return     Month
##
def num2month(num):
    return {
        1 : 'January',
        2 : 'February',
        3 : 'March',
        4 : 'April',
        5 : 'May',
        6 : 'June',
        7 : 'July',
        8 : 'August',
        9 : 'September',
        10 : 'October',
        11 : 'November',
        12 : 'December',
        99 : 'None',
    }.get(num, "")

##
## @brief      Converts byte size to human readable string
##
## @param      bts   number of bytes
##
## @return     human readable size
##
def bytes2human(bts):
    bytes_old = bts;
    exp = 0;

    d = {
        0 : 'B',
        3 : 'KB',
        6 : 'MB',
        9 : 'GB',
        12 : 'TB',
        15 : 'GB',
        }
    
    while bytes_old > 1000:
        exp = exp + 3
        bytes_old = bytes_old / 1024

    return "%.3f %s" % (bytes_old, d.get(exp, "B"))


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

def userAnalytics(month, user):
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
                humanToBytes(row[6]) > 0 and
                isInMonth(row[1], month) ):
                    lst_user_files.append(row[7])

    # Number of total files accessed
    n_files_accessed = len(lst_user_files)

    # unique list of accessed files
    lst_user_files_unique = []
    for f in lst_user_files:
        if f not in lst_user_files_unique:
            lst_user_files_unique.append(f)

    # Count file accesses
    c = Counter(lst_user_files)
    most_c = c.most_common()

    # Print user global information
    print("- User stats -------------------------------------------------------------------")
    print("| For User: %s" % user)
    print("|     Total accessed files: %d" % n_files_accessed)
    print("--------------------------------------------------------------------------------")

    # Print ranking of file accesses
    i = 1
    print("- Accessed Files ---------------------------------------------------------------")
    print("|  No   Cnt File")
    print("--------------------------------------------------------------------------------")
    for entry in most_c:
        print("| %3d %5d %s" % (i, entry[1], os.path.basename(entry[0])))
        i = i + 1
    print("--------------------------------------------------------------------------------")

def monthAnalytics(month, user):
    global lst_files
    global lst_files_uniq
    global lst_users
    global fd
    global rdr

    # Open CSV
    fd.seek(0)

    # Get logs in given month
    lst_user_month_files = []
    lst_user_month_sizes = []
    for row in rdr:
        if len(row) == 8:
            # Only files with size larger than 0, given user and month
            if (row[5] == "File" and
                row[3] == user and 
                humanToBytes(row[6]) > 0 and
                isInMonth(row[1], month) ):
                    lst_user_month_files.append(row[7])
                    lst_user_month_sizes.append(humanToBytes(row[6]))

    n_files = len(lst_user_month_files)
    n_bytes = 0
    n_unique = 0
    i = 0
    # unique list of accessed files
    lst_user_files_unique = []
    for f in lst_user_month_files:
        # count total bytes
        n_bytes = n_bytes + lst_user_month_sizes[i]
        # count unique files
        if f not in lst_user_files_unique:
            lst_user_files_unique.append(f)
            n_unique = n_unique + 1
        i = i + 1

    # report
    print("- Monthly stats ----------------------------------------------------------------")
    print("| For month %s and user %s" % (num2month(month), user))
    print("|     Total accessed files: %d" % n_files)
    print("|     Uniquely accessed files: %d" % n_unique)
    print("|     Total Bytes downloaded: %s" % bytes2human(n_bytes))
    print("--------------------------------------------------------------------------------")





############################################################
#
# Program Entry
# 
############################################################
# parse all files

for f in args.infile:
    parseCSV(f)

if args.month:
    if args.month < 13 and args.month > 0:
        userAnalytics(args.month, args.user)
        monthAnalytics(args.month, args.user)

    




