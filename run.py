#!/usr/bin/python
import threading
import requests
from random import randint
from core import util
from core.api_runner import api_runner
import random

if __name__ == "__main__":

    host = "ltau-app.br-site.me"
    numberOfThreads = 100

    threads = []
    for num in range(0,numberOfThreads):
        t = api_runner(host, num)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    