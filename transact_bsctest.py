"""
transact wrapper to isolate the network
"""

import requests
from web3 import Web3
import json
from web3.middleware import geth_poa_middleware
import sys

from transact import ATransactor


class Transactor(ATransactor):
    def __init__(self, myaddr, builddir, whitelist):
        super().__init__()
        self.pushactive = False
        self.chainId = 97
        self.name = "BSCTEST"
        self.URL = "https://data-seed-prebsc-1-s1.binance.org:8545"
        self.w3 = self.get_w3()
        # self.gasPrice = 5000 * 10 ** 6
        self.gasPrice = self.w3.toWei("10", "gwei")
        # self.USDT = "0x55d398326f99059fF775485246999027B3197955"
        # BUSD = "0x8301F2213c0eeD49a7E28Ae4c3e91722919B8B47"
        self.USDT = "0xA11c8D9DC9b66E209Ef60F0C8D969D3CD988782c"

        self.USDT_DECIMALS = 6
        self.name_currency = "BNB"
        self.bnb_dec = 18
        self.builddir = builddir
        self.mingas = 21000
        self.whitelist = whitelist
        self.myaddr = myaddr

    def get_w3(self):
        w3 = Web3(Web3.HTTPProvider(self.URL))
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        return w3

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

    def buildTx(self):
        nonce = self.get_nonce(self.myaddr)

        tx_params = {
            "chainId": self.chainId,
            "value": 0,
            "gas": 200000,
            "gasPrice": self.gasPrice,
            "nonce": nonce,
        }
        return tx_params

    def send_erc20(self, USD_amount, to_address, nonce):
        # self.log(f"send_erc20 {USD_amount} {to_address}")
        amountDEC = int(USD_amount * 10 ** self.USDT_DECIMALS)
        # self.log(f"send_erc20 dec: {amountDEC} {to_address}")

        ercabi = self.load_abi("erc20")
        ctr = self.load_contract(self.USDT, ercabi)
        # self.log(f"contract {self.USDT}")
        # self.log(f"erc contract {ctr.functions.name().call()}")
        # self.log(f"erc Decimals {ctr.functions.decimals().call()}")

        bnbvalue = 0

        tx_params = {
            "chainId": self.chainId,
            # "to": to_address,
            "value": bnbvalue,
            "gas": 70000,
            "gasPrice": self.gasPrice,
            "nonce": nonce,
        }

        # self.log(f"tx_params {tx_params}")
        # self.log(f"to_address {to_address}")
        # self.log(f"amountDEC {amountDEC}")

        btx = ctr.functions.transfer(to_address, amountDEC).buildTransaction(tx_params)
        return btx

    def get_deploy_tx(self, w3_contract, *constructargs):
        print(constructargs)

        nonce = self.get_nonce(self.myaddr)
        # print(acct.address, nonce)

        txparams = {
            # 'from': myadress,
            # 'to': '',
            # "gas": 999000,
            "nonce": nonce,
            "gasPrice": self.gasPrice,
        }
        cargs = "NRTSeed", "NRTS", "Seed"
        tx = w3_contract.constructor(*cargs).buildTransaction(txparams)
        # print(tx)

        est = self.w3.eth.estimate_gas(tx)
        # log(f"estimated gas {est}")
        # add some gas just in case
        use_gas = int(est * 1.2)
        txparams["gas"] = use_gas
        tx = w3_contract.constructor(*cargs).buildTransaction(txparams)
        # print(tx)

        return tx
