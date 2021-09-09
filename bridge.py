# POST api.binance.org/bridge/api/v2/swaps
# {
#     "amount": 0.2,
#     "direction": "IN",
#     "fromNetwork": "ETH",
#     "source":"",
#     "symbol":"ETH",
#     "toAddress":"my wallet address",
#     "toAddressLabel":"",
#     "toNetwork":"BSC",
#     "walletAddress": "my wallet address",
#     "walletNetwork": "ETH"
#  }


# direction	query	direction	No	string
# endTime	query	endTime	No	long
# limit	query	limit	No	long
# offset	query	offset	No	long
# startTime	query	startTime	No	long
# status	query	status	No	[ string ]
# symbol	query	symbol	No	string
# walletAddress	query	walletAddress	Yes	string

import requests
import json

base = "https://api.binance.org/bridge/"

# tp = "api/v2/tokens"
tp = "api/v2/swaps"
url = base + tp


params = {"walletAddress": "0xF55BB51Cfab743EEef69D529eA6EbD8Be72163c9"}
# params = {'walletAddress': '0x0BB097042d12aF8A7cb2878B30a6b04A33D4cE6B'}


def get_tx():
    rt = requests.get(url, params=params)  # .json()
    swaps = json.loads(rt.content)["data"]["swaps"]
    print(swaps)
    for x in swaps:
        st = x["status"]
        if st == "Completed":
            print(st, x["toAddress"], x["actualToAmount"])
        else:
            print(x["status"])


# def make_swap():
#     myaddr = "0xe537ce8a0C8bB913A97EA18b148752bc84c67F5d"
#     payload = {
#         "amount": 0.01,
#         "direction": "IN",
#         "fromNetwork": "ETH",
#         "source": "",
#         "symbol": "ETH",
#         "toAddress": myaddr,
#         "toAddressLabel": "",
#         "toNetwork": "BSC",
#         "walletAddress": myaddr,
#         "walletNetwork": "ETH",
#     }
#     p = {"payload": payload}

#     print(url)
#     # rt = requests.post(url, params=p)  # .json()
#     # rt = requests.post(url, body=payload)  # .json()
#     import http.client
#     base = "api.binance.org"
#     # tp = "api/v2/tokens"
#     tp = "bridge/api/v2/swaps"
#     conn = http.client.HTTPConnection(base)
#     conn.request("GET", tp)
#     r1 = conn.getresponse()
#     print(r1)
#     print(r1.status, r1.reason)
#     data1 = r1.read()
#     print(data1)
#     # print(rt.content)
#     # print(rt.raw)
#     # print(rt.reason)
#     # print(dir(rt))


make_swap()
