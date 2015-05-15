#!/usr/bin/env python
# encoding: utf-8
# vim: set et sw=4 ts=4 sts=4 fenc=utf-8
# Author: Yang Tong


import time, libxml2dom, re

from all_repositories import Github_Api_Repos

class More_For_Repos(Github_Api_Repos):

    def __init__(self, url, database, collection,r_status_col):
        super(More_For_Repos, self).__init__(url, database, collection, r_status_col)

    def get_more(self):
        docs = list(self.col.find())
        more_features = ["watch_count", "fork_count", "star_count", "commit_times"]
        candidate_ids = [self.least_id(feature, docs) for feature in more_features if self.least_id != 0]
        return min(candidate_ids) if candidate_ids else 0

    def least_id(self, feature, docs):
        ids = (doc["id"] for doc in docs if feature not in doc.keys())
        return min(ids) if ids else 0

    def Extract_more_data(self,t0=None, how_long=3600):
        """
        extract fork, watch, star, commit and issue
        """
        t0 = t0 if t0 else time.time()
        get_more_id = self.get_more()
        if get_more_id == 0:
            self.logger.info("*"*20
                    +"\nExtractions of fork, watch, star and commit for all repositories are DONE!\n"
                    +"*"*20)
            return None
        cur = self.col.find({"id":{"$gte":get_more_id}})
        for doc in cur:
            self.extract_more_data(doc)
            if (time.time()-t0) > 3600:
                return True


    def extract_more_data(self, doc):
        url, _id = doc["html_url"], doc["_id"]
        url = url if "www" in url else "//www.".join(url.split("//"))
        r = self.make_request(url)
        text = libxml2dom.parseString(r.text.encode("utf-8"), html=1)
        items = text.xpath("//ul[@class='pagehead-actions']/li/a[2]/text()")
        string = reduce(lambda x,y: x+y, [item.textContent for item in items])
        values = re.findall("[0-9]+", string)
        dic = {"watch_count":int(values[0]), "star_count":int(values[1]), "fork_count":int(values[2])}
        commits_url = text.xpath("//li[@class='commits']/a/@href")
        if commits_url:
            commits_url = "https://www.github.com/" + commits_url[0].textContent
            dic["commit_times"] = self.commits_time(commits_url)
        else:
            dic["commit_times"] = "failed to get this feature"
        result = self.col.update({"_id":_id}, {"$set": dic})
        result.update(dic)
        self.logger.info(result)

    def commits_time(self, commits_url):
        page=1
        commits_url += "?page=%d"
        r = self.make_request(commits_url % page)
        times = []
        while r.status_code == 200:
            lines = [line.strip() for line in r.text.split('\n')]
            commit_times = [line.split(" on ")[-1] for line in lines if "Commits on" in line]
            times.extend(commit_times)
            page += 1
            r = self.make_request(commits_url % page)
        return times

    def extract_language(self):
        language_urls = [[doc["_id"],doc["languages_url"]] for doc in self.col.find()
                if "languages" not in doc.keys()]
        if len(language_urls) == 0:
            return None
        for _id, url in language_urls:
            r = self.make_request(url).json()
            if "message" in r.keys():
                self.logger.info(">>>>LANGUAGE<<<<oopps~~~ the rate limit"
                        +" for requests-60 times per hour-is approached.")
                return True
            result = self.col.update({"_id":_id}, {"$set":{"languages": r}})
            result.update({"languages":r})
            self.logger.info(result)
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
    r2 = repos_api.extract_language()
    r3 = repos_api.Extract_more_data()
    while r1 or r2 or r3:
        r1 = repos_api.request_repos()
        r2 = repos_api.extract_language()
        r3 = repos_api.Extract_more_data()

if __name__ == "__main__":
    main()
 #   repos_api = More_For_Repos("https://api.github.com/repositories", "github_api", "all_repositories")
 #   repos_api.run()
 #   repos_api.request_repos()
