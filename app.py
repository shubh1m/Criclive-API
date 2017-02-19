from slackclient import SlackClient
from flask import Flask, request
from bs4 import BeautifulSoup
import requests
import json
import os
import time
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
sched = BackgroundScheduler()

URL = "http://www.espncricinfo.com/ci/engine/match/index.html?view=live"
BASE_URL = "http://www.espncricinfo.com"


def getHTML(url):
    html_doc = requests.get(url).text
    soup = BeautifulSoup(html_doc, 'html.parser')
    return soup


def getCategories(soup):
    categories = soup.find_all("div", "match-section-head")
    categories = [x.string for x in categories]
    return categories

def getMatches(soup):
    matches = {
            "data": []
            }
    categories = getCategories(soup)
    soup = soup.find(id="live-match-data")
    i=0
    for match_block in soup.find_all("section", "matches-day-block"):
        details = {}
        details = {
                "category": categories[i],
                "matches": []
                }
        i+=1
        for match in match_block.find_all("section", "default-match-block "):
            det = {
                "date": match.find("div", "match-info").find("span", "bold").string,
                "team1": {
                    "name": match.find("div", "innings-info-1").contents[0].strip(),
                    "score": match.find("div", "innings-info-1").contents[1].string
                    },
                "team2": {
                    "name": match.find("div", "innings-info-2").contents[0].strip(),
                    "score": match.find("div", "innings-info-2").contents[1].string
                    },
                "status": match.find("div", "match-status").find("span", "bold").string,
                "url": BASE_URL + match.find("span", "match-no").find("a").get("href")
                }
            details["matches"].append(det)
        matches["data"].append(details)
    #matches = json.dumps(matches)
    return matches


@sched.scheduled_job('interval', minutes=1)
@app.route('/', methods=['GET', 'POST'])
def main():
    soup = getHTML(URL)
    matches = getMatches(soup)
    results = json.dumps(matches, indent=4, sort_keys=True)
    return results


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    sched.start()
    app.run(host='0.0.0.0', port=port)
