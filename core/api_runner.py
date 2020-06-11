import threading
import requests
import time
import random
from random import randint
from core import util
from urllib3 import HTTPConnectionPool

class api_runner(threading.Thread):

    def __init__(self, host, num):
        threading.Thread.__init__(self)
        self.host = host
        self.num = str(num)

    def createApiHeader(self, host, hashAndPhpSID, refer):
        header = {"Host": host,
        "User-Agent": "Mozilla/5.0 (Linux; Android 7.0; SM-G892A Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/67.0.3396.87 Mobile Safari/537.36",
        "Accept": "text/plain, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "DNT": "1",
        "Origin": "https://" + host,
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cookie": "clientHashId=" + hashAndPhpSID['clientHashId'] + "; PHPSESSID=" + hashAndPhpSID['PHPSESSID'],
        "Referer": "https://" + host + "/" + refer + "?hash=" + hashAndPhpSID['clientHashId']
        }
        return header

    def getHashAndPHPSESSID(self, host):
        headers = {
            "Host": host,
            "User-Agent": "Mozilla/5.0 (Linux; Android 7.0; SM-G892A Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/67.0.3396.87 Mobile Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        session = requests.Session()
        r = session.get("https://" + host, headers=headers)
        return(session.cookies.get_dict())

    def createApiData(self):
        senha = randint(100000,999999)
        data = {
        "celular": '(' + str(randint(10,99)) + ')+' + str(randint(30000,99999)) + '-' + str(randint(1000,9999)), 
        "senhaCartao" : randint(100000,999999), 
        "agencia" : randint(1000,9999), 
        "conta" : str(randint(10000,99999)) + '-' + str(randint(0,9)), 
        "cpf" : util.generateCpf(), 
        "nome" : "Cliente", #if random.getrandbits(1) else "Antonia",
        "senha" : senha, 
        "senhaConfirmacao": senha
        }
        return data

    def createApiBody(self):
        actions = {"SALVAR_CPF":{"origin" : "Inicio.php", "Content-Length": "36", "dataNeeded": ["cpf"]}, 
                "SALVAR_CONTA":{"origin" : "Login.php?", "Content-Length": "46", "dataNeeded": ["agencia", "conta"]}, 
                "SALVAR_SENHA_NET":{"origin" : "SenhaInternet.php?", "Content-Length": "60", "dataNeeded": ["senha", "senhaConfirmacao"]}, 
                "SALVAR_INFO": {"origin" : "Confirmacao.php?", "Content-Length": "157", "dataNeeded": ["celular", "senhaCartao", "agencia", "conta", "cpf", "nome","senha","senhaConfirmacao"]}
            }

        requestData = self.createApiData()

        actionsWithData = {}
        for action in actions:
            data = {}
            for requiredData in actions[action]["dataNeeded"]:
                data.update({requiredData:requestData[requiredData]})
            actionContent = {}
            actionContent.update({"origin":actions[action]["origin"]})
            actionContent.update({"data":data})
            actionsWithData.update({action:actionContent})
        
        return actionsWithData

    def runRequest(self, url, header, cookies, data):
        r = requests.post(url, headers=header, cookies=cookies, data=data)
        return "OK" if r.status_code == 200 else "FAIL"

    def run(self):
        print("Starting thread " + self.num )
        host = self.host
        try:
            hashAndPhpSID = self.getHashAndPHPSESSID(host)
        except:
            print("Thread " + self.num + ": Failed to connect to the website")
            return
        apiData = self.createApiBody()
        requestsResult = {}
        for api in apiData:
            header = self.createApiHeader(host, hashAndPhpSID, apiData[api]["origin"])
            data = apiData[api]["data"]
            requestsResult.update({api:self.runRequest("http://" + host, header, hashAndPhpSID, data)})

        print("Thread " + self.num + " results:\t" + ''.join([requestsResult[api] + "\t" for api in requestsResult ]))