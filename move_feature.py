#!/usr/bin/env python
# coding: utf-8
# vim: set et sw=4 ts=4 sts=4 fenc=utf-8
# Author: qfscu-bitsoal
# Created: 2015-06-05 20:57 CST

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError as DupError
from sys import argv

def move(collection0, collection1, *features):
    client = MongoClient()
    col0 = client["github_api"][collection0]
    col1 = client["github_api"][collection1]

    cur = col0.find()
    for doc in cur:
        items = {}
        keys = doc.keys()
        for feature in features:
            if feature in keys:
                items[feature] = doc.pop(feature)
        items["_id"] =  doc["_id"]
        col0.replace_one({"_id": items["_id"]}, doc)
        try:
            col1.insert(items)
        except DupError, e:
            _id = items.pop("_id")
            col1.update({"_id":_id}, {"$set":items})
    print "Done!"

if __name__ == "__main__":
    collection0, collection1 = argv[1], argv[2]
    move(collection0, collection1, *argv[3:])
