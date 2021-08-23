from account import LedgerAccount
from ledger_usb import *
import sys
from loguru import logger
import logutils
import transact
import yaml
logger.configure(**logutils.logconfig)

accountID = 4

def log(s1):
    logger.info(f"{s1}")

def logcrit(s1):
    logger.warning(f"{s1}")

global myaddr
# global ledger_account

def load_ledger():
    try:
        ledger_account = LedgerAccount(account_id=accountID)
        myaddr = ledger_account.get_address(accountID)
        logger.info(f"acccount address {myaddr}")
        return ledger_account
        # log(f"ledger loaded accountID {accountID}\taddress: {address}")
        # return ledger_account
    except LedgerUsbException as e:
        if e.status == STATUS_APP_NOT:
            print(e,type(e))
            logger.warning(f"{e} {e.status}")
            # logcrit("app not ready")
            sys.exit(1)
        elif e.status == STATUS_APP_NOT:
            logger.warning(f"{e} {e.status}")
            # logcrit(f"ledger not active: {e}. {e.status}")
            sys.exit(1)
        else:
            logger.warning(f"{e} {e.status}")
            sys.exit(1)




ledger_account = load_ledger()

with open("config.yaml") as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)

myaddr = "0x3dd34225F14423Fd3592c52634c1fC974E04f5C0"
transactor = transact.get_transactor("BSCTEST", myaddr, cfg["builddir"], '', log, logcrit)

ctr_addr = "0xFD8C90D6eb9AF117732340aAa7C5F4a58A8CD838"

abi = transactor.load_abi("NRT")

ctr = transactor.load_contract(ctr_addr, abi)
print (dir(ctr.functions))
print (ctr.functions.owners().call())
txp = transactor.buildTx()
btx =  ctr.functions.issue(myaddr, 100).buildTransaction(txp)
print(btx)

try:
    signedtx = ledger_account.signTransaction(btx)
    log(signedtx)
    transactor.activate_push()
    transactor.pushtx(signedtx)
except LedgerUsbException:
    logcrit(f"LedgerUsbException {LedgerUsbException}")
# ctr.functions.issue(myaddr, )
            
# btx = ctr.functions.transfer(to_address, amountDEC)