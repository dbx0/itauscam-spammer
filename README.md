# Attack against Itau Bank Scam 

On this project we will explore and try to difficult the life of these scammers. Here you'll see the steps taken during this process.

The website was introduced to me via SMS, with a poor url.

![SMS Received](images/sms.jpg?raw=true "SMS Received" )

You can see screenshots of the app in the `images` folder here in the repository.

## Analysing the website

Using the Developer Tools from my browser I could see that the data is being submitted at every step of the flow. So we are going to explore that later.

I also noticed that after you finish the flow every 2 seconds a ping is sent to the host so they can monitor the users.
The request to keep track of the user is a POST request sent to `https://ltau-app.br-site.me/api.php?hash=xxxxxxx` with the content `action=PING&idInfo=2278`, where `idInfo` is my user Id. 
I opened a new session and my id was now 2279.
This means that over 2000 users already has fallen to this scam.


### Cheking the website files and ports

The first thing to be done is scanning the website with `nmap` to see if we can get some information about the app. The result of the scan below can be found on the `scan` folder here.

```sh
$ nmap -sC -sV -oN scan/initial.txt XXX.XXX.XXX.XXX | tee scan/initial.txt
```

By checking the result I was able to identify an outdated Apache and an outdated OpenSSH, but we are not going to exploit them.

For this case I decided to check the files I could see with Apache using Wfuzz. The full scan can be found on the `scan` folder. I also used the tool `dirbuster` but I wasn`t able to find anything else.

```sh
$ wfuzz -w /usr/share/wordlists/wfuzz/general/big.txt --hc=403,404,500 https://ltau-app.xxxxx.xx/FUZZ | tee wfuzzresult.txt

********************************************************
* Wfuzz 2.4.5 - The Web Fuzzer                         *
********************************************************

Target: https://ltau-app.xxxxx.xx/FUZZ
Total requests: 3024

===================================================================
ID           Response   Lines    Word     Chars       Payload                                                                                                
===================================================================

000000740:   301        9 L      28 W     326 Ch      "css"                                                                                                  
000001337:   301        9 L      28 W     329 Ch      "images"                                                                                               
000001474:   301        9 L      28 W     325 Ch      "js"                                                                                                   

```
I opened the files in the `js` folder to check what could be useful, and found the files below:

![Files on js folder](images/jsindex.png?raw=true "Files on js folder")



## Creating a script

### Getting our info needed

On `confirmacao.js` I was able to see the request that is sent in the end of the flow. We are going to use this in our script as example.

```js
$.ajax({
    url: "api.php?hash="+hash,
    type:'POST',
    dataType : 'text',
    data: { action : 'SALVAR_INFO', celular: celular, senhaCartao : senhaCartao, agencia : agencia, conta : conta, cpf : cpf, nome : nome, senha : senha, senhaConfirmacao: senhaConfirmacao },
    cache: false,
    success: function(r){
        if(r == "ok"){
            window.location.href = "iToken.php?hash="+hash;
        } else {
            stopLoading();
            msg(r);
        }

    }
}
```

It's important to keep the flow that we send the data along, so we are going to send multiple requests and each one with one different data. Here they are in the order they are sent:

```
action=SALVAR_CPF&cpf=177.699.302-00
action=SALVAR_CONTA&agencia=7458&conta=96585-2
action=SALVAR_SENHA_NET&senha=565252&senhaConfirmacao=565252
action=SALVAR_INFO&celular=(94)+51515-1551&senhaCartao=565252&agencia=7458&conta=96585-2&cpf=177.699.302-00&nome=Cliente&senha=565252&senhaConfirmacao=565252
```

The `hash` field can be found when sending a GET request to the `/` url.
With the header below we can simulate we are using a mobile device and get the hash from the server.
```
Host: ltau-app.xxxxx.xx
User-Agent: Mozilla/5.0 (Linux; Android 7.0; SM-G892A Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/67.0.3396.87 Mobile Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
DNT: 1
Connection: keep-alive
Upgrade-Insecure-Requests: 1
```
Here is the response header we get with the hash value we needed.
```
HTTP/1.1 302 Found
Date: Wed, 10 Jun 2020 00:27:34 GMT
Server: Apache/2.4.29 (Ubuntu)
Set-Cookie: PHPSESSID=vr2kfj2vuqvijjqxxxx0v9u4; path=/
Expires: Thu, 19 Nov 1981 08:52:00 GMT
Cache-Control: no-store, no-cache, must-revalidate
Pragma: no-cache
Set-Cookie: clientHashId=4102194095ee1111650f8f9.38945622; expires=Wed, 17-Jun-2020 00:27:34 GMT; Max-Age=604800
Location: Convite.php?hash=4102194095111128f650f8f9.38945622
Content-Length: 0
Keep-Alive: timeout=5, max=100
Connection: Keep-Alive
Content-Type: text/html; charset=UTF-8
```

Here is the header we need to send at the end.
```
Host: ltau-app.xxxxx.xx
User-Agent: Mozilla/5.0 (Linux; Android 7.0; SM-G892A Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/67.0.3396.87 Mobile Safari/537.36
Accept: text/plain, */*; q=0.01
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
X-Requested-With: XMLHttpRequest
Content-Length: 157
Origin: https://ltau-app.xxxxx.xx
DNT: 1
Connection: keep-alive
Referer: https://ltau-app.xxxxx.xx/Confirmacao.php?hash=4102194095ee028f650f8f9.38945622
Cookie: PHPSESSID=vr2kfj2vuqvijjq5dbebr0v9u4; clientHashId=4102194095ee028f650f8f9.38945622
```

### The script

As I see that I don't have much time, as users are being infected now, this script is going to be simple.

First we get an open proxy list to realize our connections.

Then we start multiple threads each one with a proxy.

In each thread we do the following steps:
* do a GET request to / to get the user hash and the PHPSESSID;
* create random data for the requests and fill the headers;
* submit a request to the api.php api with the action SALVAR_CPF;
* submit a request to the api.php api with the action SALVAR_CONTA;
* submit a request to the api.php api with the action SALVAR_SENHA_NET;
* submit a request to the api.php api with the action SALVAR_INFO;

The output should be like this when the connections are finished, where each OK represents one of the APIs success:
```sh
$ python run.py
Starting thread
Starting thread
Starting thread
Thread results: OK      OK      OK      OK
Thread results: OK      OK      OK      OK
Thread results: OK      OK      OK      OK
```






