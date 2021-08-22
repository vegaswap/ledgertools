"""
ledgertools - the main console application

handle
ledger_usb.LedgerUsbException: Invalid status in reply: 0x6985 (User declined on device)
"""

import click
import sys
from loguru import logger
import yaml
import json
import hashlib
import logutils
from account import LedgerAccount
from ledger_usb import *
import transact_bsc
import transact_eth
import transact_bsctest

logger.configure(**logutils.logconfig)


# util functions until click logging is hooked up to file log
def log(s1):
    logger.info(f"{s1}")
    # click.secho(s1, fg="green")


def logcrit(s1):
    logger.warning(f"{s1}")
    # click.secho(s1, bg="black", fg="red")


def activate_push(txr):
    logcrit(f"ACTIVATE PUSH")
    logcrit(f"YES/NO (Y/N)")
    yesno = input()
    if yesno == "Y":
        logcrit(f"PROCEED")
        txr.pushactive = True
    elif yesno == "N":
        logcrit(f"dont proceed")
        sys.exit(0)
    else:
        logcrit(f"dont proceed")
        sys.exit(0)


def confirm_msg(msg):
    logcrit(f"confirm {msg}")
    logcrit(f"YES/NO (Y/N)")
    yesno = input()
    if yesno == "Y":
        logcrit(f"PROCEED")
    elif yesno == "N":
        logcrit(f"dont proceed")
        sys.exit(0)
    else:
        logcrit(f"dont proceed")
        sys.exit(0)


def sha256sum(filename):
    # h  = hashlib.sha256()
    h = hashlib.sha1()
    b = bytearray(128 * 1024)
    mv = memoryview(b)
    with open(filename, "rb", buffering=0) as f:
        for n in iter(lambda: f.readinto(mv), 0):
            h.update(mv[:n])
    return h.hexdigest()


def get_ledger(accountID):
    try:
        ledger_account = LedgerAccount(account_id=accountID)
        address = ledger_account.get_address(accountID)
        log(f"ledger loaded accountID {accountID}\taddress: {address}")
        return ledger_account
    except LedgerUsbException as e:
        if e.status == STATUS_APP_NOT:
            logcrit("app not ready")
            sys.exit(1)
        else:
            logcrit(f"ledger not active: {e}. {e.status}")
            sys.exit(1)


def check_critical():
    logcrit(f"PERFORMING CRITICAL TASKS")
    logcrit(f"YES/NO (Y/N)")
    yesno = input()
    if yesno == "Y":
        logcrit(f"PROCEED")
    elif yesno == "N":
        logcrit(f"dont proceed")
        sys.exit(0)
    else:
        logcrit(f"dont proceed")
        sys.exit(0)


def get_transactor(ntwk, myaddr, builddir, whitelist):
    #map dynamically
    if ntwk == "ETH":
        transactor = transact_eth.Transactor(myaddr, log, logcrit, builddir, whitelist)
    elif ntwk == "BSC":
        transactor = transact_bsc.Transactor(myaddr ,log, logcrit, builddir, whitelist)
    elif ntwk == "BSCTEST":
        print (whitelist)
        transactor = transact_bsctest.Transactor(myaddr, log, logcrit, builddir, whitelist)
    else:
        logcrit("unknown network")
    return transactor


@click.group()
@click.option("--aid", help="account ID", type=int)
@click.option("--chain", help="chain", type=str)
@click.pass_context
def ltools(ctx, aid: int, chain: str):

    with open("config.yaml") as f:
        cfg = yaml.load(f, Loader=yaml.FullLoader)

    try:
        aid = int(aid)
    except:
        aid = cfg["accountid"]
        # logcrit(f"account id has to be an integer")
        # sys.exit(0)

    builddir = cfg["builddir"]
    print ("builddir ", builddir)

    if chain == None:
        chain = cfg["network"]
        logcrit(f"selected chain {chain}")
        # logcrit("invalid chain passed")
        # sys.exit(1)

    wl = cfg["whitelist"]
    with open(wl, "r") as f:
        x = f.read()
        whitelist = json.loads(x)


    logger.debug(f"main {ctx} {aid}")
    ledger_account = get_ledger(aid)
    myaddr = ledger_account.address
    transactor = get_transactor(chain, myaddr, builddir, whitelist)

    ctx.obj["ledger_account"] = ledger_account
    ctx.obj["transactor"] = transactor
    ctx.obj["chain"] = chain
    ctx.obj["maxused"] = cfg["maxused"]


def show_balance_token(transactor, addr, token_address):
    ercabi = transactor.load_abi("erc20")
    ctr = transactor.load_contract(token_address, ercabi)
    name = ctr.functions.name().call()
    sym = ctr.functions.symbol().call()
    b = ctr.functions.balanceOf(addr).call()
    DEC = transactor.USDT_DECIMALS
    bd = b / 10 ** DEC
    s1 = f"{name}: {bd} ({sym})"
    log(s1)
    return bd


@ltools.command()
@click.pass_context
def balanceusdt(ctx):
    myaddr = ctx.obj["ledger_account"].address
    txr = ctx.obj["transactor"]
    show_balance_token(txr, myaddr, txr.USDT)


@ltools.command()
@click.pass_context
def balance(ctx):
    ledger_account = ctx.obj["ledger_account"]
    myaddr = ledger_account.address
    txr = ctx.obj["transactor"]
    bnb_bal = txr.ethbal(myaddr)

    log(f"BNB {bnb_bal/10**18}")


@ltools.command()
@click.pass_context
def showwhitelist(ctx):
    log("whitelist")
    txr = ctx.obj["transactor"]
    for k, v in txr.whitelist.items():
        log(f"{k}: {v}")


@ltools.command()
@click.pass_context
def listaccounts(ctx):
    logger.debug(f"list accounts")
    ledger_account = ctx.obj["ledger_account"]
    for i in range(3):
        addr = ledger_account.get_address(i)
        log(f"addr:  {addr}")


@ltools.command()
@click.pass_context
def listall(ctx):
    logger.debug(f"listall")
    ledger_account = ctx.obj["ledger_account"]
    txr = ctx.obj["transactor"]
    # with open("balances_%s.csv"%ctx.obj["chain"], "w") as f:
    for i in range(ctx.obj["maxused"]):
        addr = ledger_account.get_address(i)
        log(f"addr:\t{addr} (accountID: {i})")
        txr = ctx.obj["transactor"]
        bnb_bal = txr.ethbal(addr)
        bnb_bal_dec = bnb_bal / 10 ** txr.bnb_dec
        s2 = f"{txr.name_currency} {bnb_bal_dec}"
        log(s2)
        b = show_balance_token(txr, addr, txr.USDT)
        log(f"---------")
        # f.write(f"{addr},{txr.name_currency},{str(bnb_bal_dec)}\n")
        # f.write(f"{addr},USDT,{str(b)}\n")


def send_tx(ledger_account, transactor, sendamount, to_address):
    logger.debug(f"send_tx {sendamount} {to_address}")

    myaddr = ledger_account.address
    txd = transactor.get_send_tx(myaddr, to_address, sendamount)

    try:
        signedtx = ledger_account.signTransaction(txd)
        log(signedtx)
        transactor.pushtx(signedtx, log)
    except LedgerUsbException:
        # if LedgerUsbException.status == "User declined on device":
        #     logcrit("you declined")
        # else:
        logcrit(f"LedgerUsbException {LedgerUsbException}")


@ltools.command()
@click.pass_context
@click.option("--amount", help="amount", type=float)
@click.option("--to", help="address")
def sendmoney(ctx, amount, to):
    if amount > 1:
        logcrit("amount too large")
        sys.exit(1)

    txr = ctx.obj["transactor"]
    ledger_account = ctx.obj["ledger_account"]
    amountDEC = int(amount * 10 ** txr.bnb_dec)

    log(f"send {txr.name_currency} amount: {amount} amountDEC: {amountDEC} to: {to}")
    activate_push(txr)

    # TODO check high amounts
    if to in txr.whitelist.keys():
        addr = txr.whitelist[to]
        send_tx(ledger_account, txr, amountDEC, addr)
    else:
        logcrit("address not whitelisted")


@ltools.command()
@click.pass_context
@click.option("--amount", help="amount", type=int)
@click.option("--to", help="address")
def sendusdt(ctx, amount, toaddrLabel):
    # amounts are treated as nondecimals i.e. 1 = 1 USDT
    # decimals are handled on the transactor level
    logger.debug(f"send usdt {amount} {toaddrLabel}")
    ledger_account = ctx.obj["ledger_account"]
    transactor = ctx.obj["transactor"]
    logcrit(f"send {amount}")
    logcrit(f"to  {toaddrLabel}")
    maxAmount = 1000
    if amount > maxAmount:
        logcrit("higher than max amount")
        sys.exit(1)
    # can only send to whitelisted addresses
    if toaddrLabel in transactor.whitelist.keys():
        toaddr = transactor.whitelist[toaddrLabel]
        txr = ctx.obj["transactor"]
        myaddr = ledger_account.address
        nonce = txr.get_nonce(myaddr)
        btx = txr.send_erc20(amount, toaddr, nonce)
        signedtx = ledger_account.signTransaction(btx)
        log(f"signedtx {signedtx}")
        # activate_push(transactor)
        # pushtx(signedtx, log)

    else:
        logcrit("address not whitelisted")


# def append_deploymap(name, contractAddress):


@ltools.command()
@click.option("--contractname", help="the name of the contract to deploy")
@click.pass_context
def deploy(ctx, contractname):
    if contractname == "" or contractname == None:
        logcrit("no contract name provided")
        sys.exit(1)

    confirm_msg("deploying contract %s" % contractname)

    transactor = ctx.obj["transactor"]
    w3_contract = transactor.get_contract(contractname)
    wdir = "./build"
    p = "%s/%s.abi" % (wdir, contractname)
    msg = f"abi sha1 hash {sha256sum(p)}"
    confirm_msg(msg)
    p = "%s/%s.bin" % (wdir, contractname)
    msg = f"bin sha1 hash {sha256sum(p)}"
    confirm_msg(msg)
    print(w3_contract)
    # sys.exit(1)

    ledger_account = ctx.obj["ledger_account"]
    myaddr = ledger_account.address
    msg = f"deploytx {contractname} from {myaddr}"
    logcrit(msg)
    confirm_msg(msg)
    tx = transactor.get_deploy_tx(myaddr, w3_contract)
    log(tx)

    log("confirm hash of contract bin!")

    try:
        signedtx = ledger_account.signTransaction(tx)
    except LedgerExceptionDeclined as e:
        logcrit(f"user declined {e}")
        sys.exit(1)

    log(f"signedtx {signedtx}")
    activate_push(transactor)
    tx_receipt = transactor.pushtx(signedtx, log)
    # log(tx_receipt)
    if tx_receipt["status"] == 1:
        log(f"deploy success {tx_receipt}")
        contractAddress = tx_receipt["contractAddress"]
        log(f"deployed to {contractAddress}")
        # append to map of addresses
        # append_deploymap
    else:
        logcrit(f"deploy failed {tx_receipt}")


@ltools.command()
@click.pass_context
def balancevega(ctx):
    myaddr = ctx.obj["ledger_account"].address
    txr = ctx.obj["transactor"]

    vega = "0xdFA7b5aafb1AA5C2120939Bfa1413329878F340F"
    show_balance_token(txr, myaddr, vega)


@ltools.command()
@click.pass_context
def version(ctx):
    log("version")
    log(f"{ctx.obj['ledger_account'].get_version()}")

def cli():
    ltools(obj={})

if __name__ == "__main__":
    log("start")
    ltools(obj={})
