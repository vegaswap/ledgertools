"""
transact wrapper to isolate the network
"""

import requests
from web3 import Web3
import json
from web3.middleware import geth_poa_middleware

import os

URL = "https://mainnet.infura.io/v3/" + os.getenv("INFURA_KEY")


class Transactor:
    def __init__(self) -> None:
        self.pushactive = False
        self.w3 = self.get_w3()
        self.chainId = 1
        self.gasPrice = 25000 * 10 ** 6
        self.USDT = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
        self.USDT_DECIMALS = 6
        self.name_currency = "ETH"
        self.bnb_dec = 18

    def get_w3(self):
        w3 = Web3(Web3.HTTPProvider(URL))
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        return w3

    def write_abi(self, name, contract_address):
        raise Exception("not supported")

    def get_contract_json(self, ctr_name):
        """load w3 contract from brownie json format"""
        wdir = "./build"
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
        wdir = "./build"
        p = "%s/%s.abi" % (wdir, name)
        with open(p, "r") as f:
            return f.read()

    def load_bin(self, name):
        wdir = "./build"
        p = "%s/%s.bin" % (wdir, name)
        with open(p, "r") as f:
            return f.read()

    def load_contract(self, address, abi):
        return self.w3.eth.contract(address=address, abi=abi)

    def get_deploy_tx(self, address, w3_contract):
        raise Exception("not supported")

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
