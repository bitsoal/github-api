#!/usr/bin/env python
# coding: utf-8
# vim: set et sw=4 ts=4 sts=4 fenc=utf-8
# Author: qfscu-bitsoal
# Created: 2015-06-08 14:33 CST

import time
from pymongo.errors import CursorNotFound
from pymongo.errors import DuplicateKeyError as DupError
from pymongo import MongoClient

from all_repositories import Github_Api_Repos

class More_For_Repos(Github_Api_Repos):

    def __init__(self, url, database, collection, r_status_col):
        super(More_For_Repos, self).__init__(url, database, collection, r_status_col)

    def to_be_extracted(self, feature, feature_link, length):
        cur = self.col.find({"_id":{"$gte":1}}, {"_id":1, feature:1, feature_link:1})
        docs = []
        for doc in cur:
            if feature not in doc.keys():
                docs.append(doc)
            if len(docs) >= length:
                break
        return docs


    def Extract_more_data(self,t0=None, how_long=4000):
        """
        extract fork, watch, star
        """
        t0 = t0 if t0 else time.time()
        docs = self.to_be_extracted("watch_count", "html_url", 150)
        if len(docs) == 0:
            self.logger.info(">>>>>all watch, star, fork of extracted repos have been extracted<<<<<<<<<<<< ")
            return None
        for doc in docs:
            self.extract_more_data(doc)
            if (time.time()-t0) > how_long:
                self.logger.info(">>>Time over for extracting features!<<<")
                return True
        self.logger.info(">>>>>>The for loop for fork, watch, star is done. check whether anoter for loop is needed<<<<<<<")
        return self.Extract_more_data(t0=t0)

    def extract_more_data(self, doc):
        url, _id = doc["html_url"], doc["_id"]
        url = url if "www" in url else "//www.".join(url.split("//"))
        r = self.make_request(url)
        if r.status_code == 404:
            result = self.col.update({"_id": _id}, {"$set":{"watch_count":None, "star_count":None, "fork_count":None}})
            result.update({"_id":_id})
            self.logger.info(result)
            return
        lines = [l.strip() for l in r.text.split("\n") if l.strip()]
        inds = [ind_ for ind_, l in enumerate(lines) if "pagehead-actions" in l]
        if len(inds) != 1:
            if r.status_code == 404:
                self.col.remove({"_id":_id})
                self.logger.info("The repos with id = %d and html_url = %s is unvalid, remove it from mongodb"
                        % (_id, url))
                return
            else:
                assert 1==2, "there are some problems once requesting %s" % url
        lines = [l.lower() for l in lines[inds[0]:inds[0]+50] if not l.startswith("<") and "=" not in l]
        values = [lines[i] for i in [1,3,5]]
        for ind, value in enumerate(values):
            if "," in value:
                values[ind] = reduce(lambda x, y: x+y, value.split(","))
            values[ind] = int(values[ind])
        dic = {"watch_count":values[0], "star_count":values[1], "fork_count":values[2]}
        result = self.col.update({"_id":_id}, {"$set":dic})
        dic["html_url"], dic["_id"] = url, _id
        result.update(dic)
        self.logger.info(result)

    def extract_language(self):
        docs = self.to_be_extracted("languages", "languages_url", 70)
        language_urls = [[doc["_id"],doc["languages_url"]] for doc in docs]
        self.logger.info(">>>>>>>have got to-be-extracted urls of languages<<<<<<<")
        if len(language_urls) == 0:
            self.logger.info(">>>>>all languages of extracted repos have been extracted<<<<<<<<<<<")
            return None
        for _id, url in language_urls:
            r = self.make_request(url).json()
            if "message" in r.keys() and "documentation_url" in r.keys():
                self.logger.info(">>>>LANGUAGE<<<<oopps~~~ the rate limit"
                        +" for requests-60 times per hour-is approached.")
                return True
            result = self.col.update({"_id":_id}, {"$set":{"languages": r}})
            result.update({"languages":r, "_id":_id})
            self.logger.info(result)
        self.logger.info(">>>>>>>The for loop for the extraction of languages is done!<<<<<<<<<<")
        return self.extract_language()

    def run(self):
        language_result = self.extract_language()
        if language_result:
            self.Extract_more_data()
            return self.run()
        else:
            r = self.Extract_more_data()
            if r:
                self.run()
            else:
                self.logger.info("Extractions for more features are DONE!")
                return True

def main():
    repos_api = More_For_Repos("https://api.github.com/repositories",
            "github_api", "all_repositories", "request_status")
    r1 = repos_api.request_repos()
    r2 = repos_api.Extract_more_data()
    r3 = repos_api.extract_language()
    while r1 or r2 or r3:
        repos_api.logger.info(">>>>>>before the first loop<<<<<<<")
        r1 = repos_api.request_repos()
        repos_api.logger.info(">>>>>>before the second loop<<<<<<<<")
        r2 = repos_api.Extract_more_data()
        repos_api.logger.info(">>>>>>before the third loop<<<<<<<<")
        r3 = repos_api.extract_language()
        repos_api.logger.info(">>>>>>before the fourth loop<<<<<<<<")
        r2 = repos_api.Extract_more_data()
        repos_api.logger.info(">>>>>>One while loop is done<<<<<<<<<")
    repos_api.logger.info("Congratulations! The extraction of all github repos & their features"
            +" (watch_count, star_count, fork_count and languages) is DONE!")

if __name__ == "__main__":
    main()
