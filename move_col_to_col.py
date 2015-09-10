#!/usr/bin/env python
# coding: utf-8
# vim: set et sw=4 ts=4 sts=4 fenc=utf-8
# Author: qfscu-bitsoal
# Created: 2015-06-06 16:54 CST

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError as DupError
from sys import argv

def move_repos(db0, col0, db1, col1, all_repos=True):
    client = MongoClient()
    col0 = client[db0][col0]
    col1 = client[db1][col1]

    cur0 = col0.find()
    if all_repos:
        for doc in cur0:
            try:
                col1.insert(doc)
                col0.remove({"_id": doc["_id"]})
            except DupError, e:
                print e
                _id = doc.pop("_id")
                col1.update({"_id": _id}, {"$set":doc})
    else:
        col1.insert(doc)
    print "Done!"

if __name__ == "__main__":
    db0, col0, db1, col1 = argv[1], argv[2], argv[3], argv[4]
    move_repos(db0, col0, db1, col1, all_repos=True)
    #move_repos("github_api", "all_repositories1", "github_api", "all_repositories")
