"""
transact wrapper to isolate the network
"""

from web3 import Web3
import json
from web3.middleware import geth_poa_middleware

import os


from transact import ATransactor

class Transactor(ATransactor):
    def __init__(self, myaddr, log, logcrit, builddir, whitelist):
        self.pushactive = False
        self.chainId = 1
        self.gasPrice = 25000 * 10 ** 6
        try:
            INFURA_KEY = os.getenv("INFURA_KEY")
        except:
            print("infura key not set")        
        self.URL = "https://mainnet.infura.io/v3/" + INFURA_KEY
        self.w3 = self.get_w3()

        self.USDT = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
        self.USDT_DECIMALS = 6
        self.name_currency = "ETH"
        self.bnb_dec = 18
        self.builddir = builddir
        

    def get_w3(self):
        w3 = Web3(Web3.HTTPProvider(self.URL))
        # w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        return w3

    def write_abi(self, name, contract_address):
        raise Exception("not supported")

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
