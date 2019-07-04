import sys, time,os
import re
from bs4 import BeautifulSoup as BS
import requests
from dotenv import load_dotenv
from daemon import Daemon
load_dotenv()

url = ''
last_commentary = ''
TAG_RE = "<[^>]+>"
COMPILED_TAG_RE = re.compile(TAG_RE)

def notification(title, message):
    slack_url = os.getenv("SLACK_URL")
    if slack_url:
        requests.post(slack_url,headers={'Content-type' :"application/json"}, json={"text": "{0}\n{1}".format(title,message)})
    print(title)
    print(message)

def should_notify(comm):
    searchResult = re.search(TAG_RE,comm)
    if searchResult and searchResult.group():
        return True
    else:
        return False

def remove_tags(text):
    return COMPILED_TAG_RE.sub('*', text)


class MyDaemon(Daemon):
    def __init__(self, *args, **kwargs):
        super(MyDaemon, self).__init__(*args, **kwargs)

    def run(self):
        global last_commentary
        global match_id
        while True:
            r = requests.get(url)
            soup = BS(r.text, "html.parser")

            summary = soup.find('div', {'class': 'cb-scrs-wrp'}).text
            commentary_tag = soup.find('p', {'class': 'cb-com-ln'})
            commentary = "".join(map(str, commentary_tag.contents))
            if last_commentary != commentary:
                last_commentary = commentary
                if should_notify(commentary):
                    notification(remove_tags(commentary), summary)
                    time.sleep(60)
            time.sleep(10)


if __name__ == "__main__":
    arg = sys.argv[1]
    if sys.argv[1] == "start":
        url = input("Provide cricbuzz commentary url")
    daemon = MyDaemon('app.pid', verbose=0)
    getattr(daemon, arg)()