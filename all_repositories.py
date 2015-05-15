#!/usr/bin/env python
# encoding: utf-8
# vim: set et sw=4 ts=4 sts=4 fenc=utf-8
# Author: Yang Tong

import requests, logging, threading
from pymongo import MongoClient
import time, libxml2dom,re

class Github_Api_Repos(object):

    def __init__(self, url, database, collection, r_status_col):
        self.url = url if "?since=" in url else url+"?since="
        self.col, self.status_col = self.open_db(database, collection, r_status_col)
        self.start_id = self.continue_()
        self.logger = self.create_log(collection)

    def open_db(self, database, collection, r_status_col):
        client = MongoClient('localhost', 27017)
        col = client[database][collection]
        col1 = client[database][r_status_col]
        return col, col1

    def continue_(self):
        docs = list(self.col.find())
        ids = [doc["id"] for doc in docs]
        return max(ids) if ids else 0

    def request_repos(self):
        self.url = self.url.split("=")[0] + "=" + str(self.start_id)
        r = self.make_request(self.url)
        items = r.json()
        if type(items) == dict:
            self.logger.info(">>>>REPOSITORIES<<<<oopps~~~ the rate"
                    +" limit for requests-60 times per hour-is approached.")
            return True
        elif items:
            self.col.insert(items)
            self.logger.info("%d repositories whose ids are between %d and %d are captured"
                    % (len(items), items[0]["id"], items[-1]['id']))
            self.start_id = items[-1]["id"]
            return self.request_repos()
        else:
            return None

    def make_request(self, url):
        try:
            r = requests.get(url)
        except requests.exceptions.ConnectionError, e:
            self.logger.debug(e)
            s = raw_input(">"*80+
                    "\nPlease check your network and make sure it is available!(Y to continue and N to stop):"
                    ).strip()[0].capitalize()
            if s == 'N':
                assert 1==2, "Stop executing this code"
            self.make_request(url)
        self.logger.info("link: %s, status:%d"
                % (r.url, r.status_code))
        self.status_col.insert({"request_url":r.url, "status": r.status_code})
        return r

    def create_log(self, name):
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        return logger

    def run(self):
        result = self.request_repos()
        if result:
            self.logger.info("sleep for 1 hour")
            time.sleep(3600)
            return self.run()
        else:
            self.logger.info("DONE!")

