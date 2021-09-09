"""
ledgertools - the main console application

handle
ledger_usb.LedgerUsbException: Invalid status in reply: 0x6985 (User declined on device)
"""
import sys

from settings import ddir, tdir, ldir
# sys.path.insert(0, "/Users/ben/projects/vegaswap/repos/transactor")


import click
import sys
import yaml
import json
import hashlib

# from loguru import logger
import lgs
# import log
from ledgeraccount import LedgerAccount
from ledger_usb import *
sys.path.append(ddir)
sys.path.append(tdir)
sys.path.append(ldir)

import transact


def confirm_msg(msg):
    log.warning(f"confirm {msg}")
    log.warning(f"YES/NO (Y/N)")
    yesno = input()
    if yesno == "Y":
        log.warning(f"PROCEED")
    elif yesno == "N":
        log.warning(f"dont proceed")
        sys.exit(0)
    else:
        log.warning(f"dont proceed")
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


def check_critical():
    log.warning(f"PERFORMING CRITICAL TASKS")
    log.warning(f"YES/NO (Y/N)")
    yesno = input()
    if yesno == "Y":
        log.warning(f"PROCEED")
    elif yesno == "N":
        log.warning(f"dont proceed")
        sys.exit(0)
    else:
        log.warning(f"dont proceed")
        sys.exit(0)


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
        aid = cfg["accountID"]
        # log.warning(f"account id has to be an integer")
        # sys.exit(0)

    builddir = cfg["builddir"]
    print("builddir ", builddir)

    if chain == None:
        chain = cfg["network"]
        # log.warning("invalid chain passed")
        # sys.exit(1)

    # il = lgs.get_config(chain)
    # log.info = logger.info
    # log.warn = logger.warning
    # lgs.addlevel(chain)

    ctx.obj["log"] = lgs.setup_logger(chain)
    ctx.obj["log"].warning(f"selected chain {chain}")

    wl = cfg["whitelist"]
    with open(wl, "r") as f:
        x = f.read()
        whitelist = json.loads(x)

    ctx.obj["log"].info(f"main {ctx} {aid}")
    # ledger_account = get_ledger(aid)
    ledger_account = LedgerAccount(aid, ctx.obj["log"])
    myaddr = ledger_account.address
    transactor = transact.get_transactor(chain, myaddr, builddir, whitelist, ctx.obj["log"])

    ctx.obj["ledger_account"] = ledger_account
    ctx.obj["transactor"] = transactor
    ctx.obj["chain"] = chain
    ctx.obj["maxused"] = cfg["maxused"]


def load_erc20():
    with open("erc20.abi","r") as f:
        return f.read()

def show_balance_token(ctx, transactor, addr, token_address):
    # ercabi = transactor.load_abi("erc20")
    ercabi = load_erc20()
    ctr = transactor.load_contract(token_address, ercabi)
    name = ctr.functions.name().call()
    sym = ctr.functions.symbol().call()
    b = ctr.functions.balanceOf(addr).call()
    DEC = transactor.USDT_DECIMALS
    bd = b / 10 ** DEC
    s1 = f"{name}: {bd} ({sym})"
    ctx.obj["log"].info(s1)
    return bd


@ltools.command()
@click.pass_context
def balanceusdt(ctx):
    myaddr = ctx.obj["ledger_account"].address
    txr = ctx.obj["transactor"]
    show_balance_token(ctx, txr, myaddr, txr.USDT)


@ltools.command()
@click.pass_context
def balance(ctx):
    ledger_account = ctx.obj["ledger_account"]
    myaddr = ledger_account.address
    txr = ctx.obj["transactor"]
    bnb_bal = txr.ethbal(myaddr)

    ctx.obj["log"].info(f"BNB {bnb_bal/10**18}")


@ltools.command()
@click.pass_context
def showwhitelist(ctx):
    ctx.obj["log"].info("whitelist")
    txr = ctx.obj["transactor"]
    for k, v in txr.whitelist.items():
        ctx.obj["log"].info(f"{k}: {v}")


@ltools.command()
@click.pass_context
def listaccounts(ctx):
    ctx.obj["log"].info(f"list accounts")
    ledger_account = ctx.obj["ledger_account"]
    for i in range(3):
        addr = ledger_account.get_address(i)
        ctx.obj["log"].info(f"addr:  {addr}")


@ltools.command()
@click.pass_context
def listall(ctx):
    ctx.obj["log"].info(f"listall")
    ledger_account = ctx.obj["ledger_account"]
    txr = ctx.obj["transactor"]
    # with open("balances_%s.csv"%ctx.obj["chain"], "w") as f:
    for i in range(ctx.obj["maxused"]):
        addr = ledger_account.get_address(i)
        ctx.obj["log"].info(f"addr:\t{addr} (accountID: {i})")
        txr = ctx.obj["transactor"]
        bnb_bal = txr.ethbal(addr)
        bnb_bal_dec = bnb_bal / 10 ** txr.bnb_dec
        s2 = f"{txr.name_currency} {bnb_bal_dec}"
        ctx.obj["log"].info(s2)
        b = show_balance_token(ctx, txr, addr, txr.USDT)
        ctx.obj["log"].info(f"---------")
        # f.write(f"{addr},{txr.name_currency},{str(bnb_bal_dec)}\n")
        # f.write(f"{addr},USDT,{str(b)}\n")


def send_tx(ledger_account, transactor, sendamount, to_address):
    myaddr = ledger_account.address
    log.info(f"send_tx {sendamount} {to_address} from: {myaddr}")
    txd = transactor.get_send_tx(myaddr, to_address, sendamount)

    try:
        log.info("sign...")
        signedtx = ledger_account.signTransaction(txd)
        log.info(signedtx)
        transactor.pushtx(signedtx)
    except LedgerUsbException:
        # if LedgerUsbException.status == "User declined on device":
        #     log.warning("you declined")
        # else:
        log.warning(f"LedgerUsbException {LedgerUsbException}")


@ltools.command()
@click.pass_context
@click.option("--amount", help="amount", type=float)
@click.option("--to", help="address")
def sendmoney(ctx, amount, to):
    toaddrLabel = to
    if amount > 1:
        ctx.obj["log"].warning("amount too large")
        sys.exit(1)

    txr = ctx.obj["transactor"]
    ledger_account = ctx.obj["ledger_account"]
    amountDEC = int(amount * 10 ** txr.bnb_dec)
    myaddr = ledger_account.address
    ctx.obj["log"].info(
        f"send {txr.name_currency} amount: {amount} amountDEC: {amountDEC} to: {to} from: {myaddr}"
    )
    txr.activate_push()

    bnb_bal = txr.ethbal(myaddr)    
    if amountDEC > bnb_bal:
        ctx.obj["log"].warning(f"insufficient balance. current balance: {bnb_bal}")
        sys.exit(1)

    # TODO check high amounts
    if toaddrLabel in txr.whitelist.keys():
        addr = txr.whitelist[to]
        send_tx(ledger_account, txr, amountDEC, addr)
    else:
        ctx.obj["log"].warning(f"address not whitelisted {txr.whitelist}")


@ltools.command()
@click.pass_context
@click.option("--amount", help="amount", type=float)
@click.option("--to", help="address", type=str)
def sendusdt(ctx, amount, to):
    # amounts are treated as nondecimals i.e. 1 = 1 USDT
    # decimals are handled on the transactor level
    toaddrLabel = to
    ctx.obj["log"].info(f"send usdt {amount} {toaddrLabel}")
    ledger_account = ctx.obj["ledger_account"]
    transactor = ctx.obj["transactor"]
    ctx.obj["log"].warning(f"send {amount}")
    ctx.obj["log"].warning(f"to  {toaddrLabel}")
    maxAmount = 20000
    if amount > maxAmount:
        ctx.obj["log"].warning("higher than max amount")
        sys.exit(1)
    # can only send to whitelisted addresses
    if toaddrLabel in transactor.whitelist.keys():
        toaddr = transactor.whitelist[toaddrLabel]
        print(f"toaddr {toaddr}")
        txr = ctx.obj["transactor"]
        myaddr = ledger_account.address
        nonce = txr.get_nonce(myaddr)

        btx = txr.send_erc20(amount, toaddr, nonce)
        signedtx = ledger_account.signTransaction(btx)
        ctx.obj["log"].info(f"signedtx {signedtx}")
        transactor.activate_push()
        transactor.pushtx(signedtx)

    else:
        ctx.obj["log"].warning("address not whitelisted")


# def append_deploymap(name, contractAddress):


@ltools.command()
@click.option("--contractname", help="the name of the contract to deploy")
@click.pass_context
def deploy(ctx, contractname):
    if contractname == "" or contractname == None:
        ctx.obj["log"].warning("no contract name provided")
        sys.exit(1)

    confirm_msg("deploying contract %s" % contractname)

    transactor = ctx.obj["transactor"]
    w3_contract = transactor.get_contract(contractname)
    wdir = transactor.builddir
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
    ch = ctx.obj["chain"]
    msg = f"deploytx {contractname} from {myaddr} ({ch})"
    ctx.obj["log"].warning(msg)
    confirm_msg(msg)
    # TODO pass constructor args
    cargs = "NRTSeed", "NRTS", "Seed"
    tx = transactor.get_deploy_tx(w3_contract, cargs)
    ctx.obj["log"].info(tx)

    try:
        signedtx = ledger_account.signTransaction(tx)
    except LedgerExceptionDeclined as e:
        ctx.obj["log"].warning(f"user declined {e}")
        sys.exit(1)

    ctx.obj["log"].info(f"signedtx {signedtx}")
    transactor.activate_push()
    tx_receipt = transactor.pushtx(signedtx)
    # log.info(tx_receipt)
    if tx_receipt["status"] == 1:
        ctx.obj["log"].info(f"deploy success {tx_receipt}")
        contractAddress = tx_receipt["contractAddress"]
        ctx.obj["log"].info(f"deployed to {contractAddress}")
        # append to map of addresses
        # append_deploymap
    else:
        ctx.obj["log"].warning(f"deploy failed {tx_receipt}")


# @ltools.command()
# @click.option("--contractname", help="the name of the contract")
# @click.option("--function", help="the name of the function to call")
# @click.pass_context
# def transact(ctx, contractname, function):


@ltools.command()
@click.pass_context
def balancevega(ctx):
    myaddr = ctx.obj["ledger_account"].address
    txr = ctx.obj["transactor"]

    vega = "0xdFA7b5aafb1AA5C2120939Bfa1413329878F340F"
    show_balance_token(ctx, txr, myaddr, vega)


@ltools.command()
@click.pass_context
def version(ctx):
    ctx.obj["log"].info("version")
    ctx.obj["log"].info(f"{ctx.obj['ledger_account'].get_version()}")


def cli():
    ltools(obj={})


if __name__ == "__main__":
    ltools(obj={})
