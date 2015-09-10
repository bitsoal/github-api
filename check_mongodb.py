#!/usr/bin/env python
# coding: utf-8
# vim: set et sw=4 ts=4 sts=4 fenc=utf-8
# Author: qfscu-bitsoal
# Created: 2015-06-08 15:53 CST

from pymongo import MongoClient
from sys import argv

def check_data(db, col, *fields):

    """
    this code is applied for mongodb to check the number of docs with given fields
    in the fixed col of given db.
    e.g. check the amounts of docs with field _id and languages and watch_count respectively
        in collection all_repositories of github_api database
    >>python check_data.py github_api all_repositories _id languages watch_count
    """

    client = MongoClient()
    col = client[db][col]

    counts = dict(([field, 0] for field in fields))

    cur = col.find()
    for doc in cur:
        for field in fields:
            if field in doc.keys():
                counts[field] += 1

    for field, count in counts.items():
        print "The number of docs with field %r is : %d" % (field, count)

if __name__ == "__main__":
    check_data("github_api", "all_repositories", "watch_count", "languages", "_id")
    #check_data(argv[1], argv[2], *argv[3:])
