"""
transact wrapper to isolate the network
"""

from web3 import Web3
import json
from web3.middleware import geth_poa_middleware

import os
import sys
from loguru import logger
import logutils

logger.configure(**logutils.logconfig)


class ATransactor:
    def __init__(self):
        self.pushactive = False
        # self.w3 = self.get_w3()
        # self.chainId = 1
        # self.gasPrice = 25000 * 10 ** 6
        # self.USDT = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
        # self.USDT_DECIMALS = 6
        # self.name_currency = "ETH"
        # self.bnb_dec = 18

    def activate_push(self):
        logger.warning(f"ACTIVATE PUSH")
        logger.warning(f"YES/NO (Y/N)")
        yesno = input()
        if yesno == "Y":
            logger.warning(f"PROCEED")
            self.pushactive = True
        elif yesno == "N":
            logger.warning(f"dont proceed")
            sys.exit(0)
        else:
            logger.warning(f"dont proceed")
            sys.exit(0)

    def get_contract_json(self, ctr_name):
        """load w3 contract from brownie json format"""
        with open("%s/%s.json" % (self.builddir, ctr_name), "r") as f:
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
        p = "%s/%s.abi" % (self.builddir, name)
        with open(p, "r") as f:
            return f.read()

    def load_bin(self, name):
        p = "%s/%s.bin" % (self.builddir, name)
        with open(p, "r") as f:
            return f.read()

    def load_contract(self, address, abi):
        return self.w3.eth.contract(address=address, abi=abi)

    def get_deploy_tx(self, address, w3_contract):
        raise Exception("not supported")

    def ethbal(self, addr):
        return self.w3.eth.getBalance(addr)

    def get_nonce(self, addr):
        nonce = self.w3.eth.getTransactionCount(addr)
        return nonce
        # nonce = self.w3.eth.getTransactionCount(address)  # , 'pending')

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
        logger.info(f"txd {txd}")
        return txd

    def pushtx(self, signedtx):
        if self.pushactive:
            logger.info(f"push tx {signedtx.rawTransaction}")
            try:
                result = self.w3.eth.sendRawTransaction(signedtx.rawTransaction)
            except Exception as e:
                # ValueError: {'code': -32000, 'message': 'transaction underpriced'}
                logger.warning(f"{e}")
                return

            rh = result.hex()
            logger.info(f"txhash {rh}")

            tx_receipt = self.w3.eth.waitForTransactionReceipt(rh)
            logger.info(f"status: {tx_receipt['status']}")
            logger.info(f"blockNumber: {tx_receipt['blockNumber']}")
            logger.info(f"gasUsed: {tx_receipt['gasUsed']}")
            # contractAddress
            # cumulativeGasUsed
            return tx_receipt
        else:
            logger.warning("push not activated")


import transact_bsc
import transact_eth
import transact_bsctest


def get_transactor(ntwk, myaddr, builddir, whitelist):
    # map dynamically
    if ntwk == "ETH":
        transactor = transact_eth.Transactor(myaddr, builddir, whitelist)
    elif ntwk == "BSC":
        transactor = transact_bsc.Transactor(myaddr, builddir, whitelist)
    elif ntwk == "BSCTEST":
        print(whitelist)
        transactor = transact_bsctest.Transactor(myaddr, builddir, whitelist)
    else:
        logger.warning("unknown network")
    return transactor
