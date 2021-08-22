"""
transact wrapper to isolate the network
"""

import requests
from web3 import Web3
import json
from web3.middleware import geth_poa_middleware
import sys


URL = "https://bsc-dataseed.binance.org"


class Transactor:
    def __init__(self, log, logcrit, builddir, whitelist) -> None:
        self.pushactive = False
        self.w3 = self.get_w3()
        self.chainId = 56
        self.gasPrice = 5000 * 10 ** 6
        self.USDT = "0x55d398326f99059fF775485246999027B3197955"
        self.USDT_DECIMALS = 18
        self.name_currency = "BNB"
        self.bnb_dec = 18
        self.log = log
        self.logcrit = logcrit
        self.builddir = builddir
        self.mingas = 21000
        self.whitelist = whitelist

    def get_w3(self):
        w3 = Web3(Web3.HTTPProvider(URL))
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        return w3

    def get_send_tx(self, myaddr, to_address, sendamount):
        nonce = self.get_nonce(myaddr)
        # dont add from field
        txd = {
            "chainId": self.chainId,
            "to": to_address,
            "value": sendamount,
            "gas": self.mingas,
            "gasPrice": self.gasPrice,
            "nonce": nonce,
        }
        return txd

    def write_abi(self, name, contract_address):
        response = requests.get(
            f"https://api.bscscan.com/api?"
            f"module=contract&"
            f"action=getabi&"
            f"address={contract_address}"
        )

        abi = response.json()["result"]
        with open("%s.abi" % name, "w") as f:
            f.write(abi)

    def get_contract_json(self, ctr_name):
        """load w3 contract from brownie json format"""
        # wdir = "./build"
        wdir = self.builddir
        with open("%s/%s.json" % (wdir, ctr_name), "r") as f:
            b = json.loads(f.read())
            print(b.keys())
            abi = b["abi"]
            bin = b["bytecode"]

        contract = self.w3.eth.contract(abi=abi, bytecode=bin)
        return contract

    def get_contract(self, ctr):
        abi = self.load_abi(ctr)
        bin = self.load_bin(ctr)
        print("abi ", abi)
        print("bin ", bin)
        contract = self.w3.eth.contract(abi=abi, bytecode=bin)
        return contract

    def load_abi(self, name):
        """load an abi file"""
        # wdir = "./build"
        wdir = self.builddir
        p = "%s/%s.abi" % (wdir, name)
        with open(p, "r") as f:
            return f.read()

    def load_bin(self, name):
        # wdir = "./build"
        wdir = self.builddir
        p = "%s/%s.bin" % (wdir, name)
        with open(p, "r") as f:
            return f.read()

    def load_contract(self, address, abi):
        return self.w3.eth.contract(address=address, abi=abi)

    def send_erc20(self, USD_amount, to_address, nonce):
        self.log(f"send_erc20 {USD_amount} {to_address}")
        amountDEC = USD_amount * 10 ** self.USDT_DECIMALS
        self.log(f"send_erc20 dec: {amountDEC} {to_address}")

        ercabi = self.load_abi("erc20")
        ctr = self.load_contract(self.USDT, ercabi)
        self.log(f"erc contract {ctr.functions.name().call()}")
        self.log(f"erc Decimals {ctr.functions.decimals().call()}")

        bnbvalue = 0

        tx_params = {
            "chainId": self.chainId,
            # "to": to_address,
            "value": bnbvalue,
            "gas": 50000,
            "gasPrice": self.gasPrice,
            "nonce": nonce,
        }

        btx = ctr.functions.transfer(to_address, amountDEC).buildTransaction(tx_params)
        return btx

    def get_deploy_tx(self, address, w3_contract):

        nonce = self.w3.eth.getTransactionCount(address)  # , 'pending')
        # print(acct.address, nonce)

        txparams = {
            # 'from': myadress,
            # 'to': '',
            # "gas": 999000,
            "nonce": nonce,
            "gasPrice": self.w3.toWei("5", "gwei"),
        }
        tx = w3_contract.constructor().buildTransaction(txparams)
        # print(tx)

        est = self.w3.eth.estimate_gas(tx)
        # log(f"estimated gas {est}")
        # add some gas just in case
        use_gas = int(est * 1.2)
        txparams["gas"] = use_gas
        tx = w3_contract.constructor().buildTransaction(txparams)
        # print(tx)

        return tx

    def ethbal(self, addr):
        return self.w3.eth.getBalance(addr)

    def get_nonce(self, myaddr):
        nonce = self.w3.eth.getTransactionCount(myaddr)
        return nonce

    def pushtx(self, signedtx, log):
        if self.pushactive:
            log(f"push tx {signedtx.rawTransaction}")
            result = self.w3.eth.sendRawTransaction(signedtx.rawTransaction)
            rh = result.hex()
            log(f"txhash {rh}")

            tx_receipt = self.w3.eth.waitForTransactionReceipt(rh)
            log(f"status: {tx_receipt['status']}")
            log(f"blockNumber: {tx_receipt['blockNumber']}")
            log(f"gasUsed: {tx_receipt['gasUsed']}")

            return tx_receipt
        else:
            log("push not activated")

        # contractAddress
        # cumulativeGasUsed
