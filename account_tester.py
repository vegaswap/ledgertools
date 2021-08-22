"""
testing with private key on disk
"""
from eth_account import Account
from web3 import Web3
import toml
from pathlib import Path

from web3.types import SignedTx
import transact
from loguru import logger
import sys
import toml

logger.add("account_tester.log", rotation="500 MB")
logger.add(
    sys.stdout, format="{time} {level} {message}", filter="my_module", level="INFO"
)

if __name__ == "__main__":

    home = str(Path.home())
    f = "bsc_mainnet.toml"
    p = Path(home, ".chaindev", f)
    secrets = toml.load(p)
    pk = secrets["PRIVATEKEY"]

    account = Account()
    acct = account.privateKeyToAccount(pk)
    myaddr = acct.address
    print(myaddr)

    w3 = transact.get_w3()

    abi = transact.load_abi("VegaToken")
    bin = transact.load_bin("VegaToken")
    w3_contract = w3.eth.contract(abi=abi, bytecode=bin)

    deploytx = transact.get_deploy_tx(w3, myaddr, w3_contract)
    print(deploytx)

    signedtx = w3.eth.account.signTransaction(deploytx, pk)
    print(signedtx)

    bnb_bal = w3.eth.getBalance(myaddr)
    print(myaddr, bnb_bal)

    transact.pushtx(w3, signedtx, logger.debug)

    # print (abi, bin)

    # tx = get_deploy_tx(addr)

    #
    # print(signedtx)
    # w3.eth.sendRawTransaction(signedtx.rawTransaction)
    # pushtx(signedtx)
