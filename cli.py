"""
todo
handle
ledger_usb.LedgerUsbException: Invalid status in reply: 0x6985 (User declined on device)
"""

import click
from ledger_usb import *
import sys

from account import LedgerAccount
from web3 import Web3
import utils
# import logging

from loguru import logger

logger.add("ltools.log", rotation="500 MB") 
logger.add(sys.stdout, format="{time} {level} {message}", filter="my_module", level="INFO")

BSC_USDT = "0x55d398326f99059fF775485246999027B3197955"

whitelist = {"vcorp": "0xe537ce8a0C8bB913A97EA18b148752bc84c67F5d",
"funding": "0x0BB097042d12aF8A7cb2878B30a6b04A33D4cE6B",
"main": "0x3dd34225F14423Fd3592c52634c1fC974E04f5C0"}

def get_ledger(accountID):
    try:
        ledger_account = LedgerAccount(account_id=accountID)
        address = ledger_account.get_address(accountID)
        click.secho(f"ledger loaded accountID {accountID}\taddress: {address}", bg='black', fg='green')

        return ledger_account
    except LedgerUsbException:
        click.secho(f"ledger not active", bg='black', fg='blue')
        sys.exit(1)

def check_critical():
    click.secho(f"PERFORMING CRITICAL TASKS", bg='black', fg='red')
    click.secho(f"YES/NO (Y/N)", bg='black', fg='red')
    yesno = input()
    if yesno == "Y":
        click.secho(f"PROCEED", bg='black', fg='red')
    elif yesno == "N":
        click.secho(f"dont proceed", bg='black', fg='red')
        sys.exit(0)
    else:
        click.secho(f"dont proceed", bg='black', fg='red')
        sys.exit(0)

@click.group()
@click.option('--aid', help='account ID', type=int)
@click.pass_context
def ltools(ctx, aid: int):
    logger.debug("main")
    aid = int(aid)
    print ("main ",ctx, aid, type(aid))

    ledger_account = get_ledger(aid)

    ctx.obj['ledger_account'] = ledger_account

    URL = "https://bsc-dataseed.binance.org"
    w3 = Web3(Web3.HTTPProvider(URL))
    ctx.obj['w3'] = w3

    critical_accounts = [0 , 1]
    #critical
    # if aid in critical_accounts:

def show_balance(w3, addr):
    ercabi = utils.load_abi("./", "erc20")
    ctr = utils.load_contract(w3, BSC_USDT, ercabi)
    name = ctr.functions.name().call()
    sym = ctr.functions.symbol().call()
    b = ctr.functions.balanceOf(addr).call()
    click.secho(f"{name}: {b/10**18} ({sym})", fg="green")

def pushtx(w3, signedtx):
    logger.debug(f"push tx {signedtx.rawTransaction}")
    result = w3.eth.sendRawTransaction(signedtx.rawTransaction)
    rh = result.hex()
    logger.debug(f"txhash {rh}")

    tx_receipt = w3.eth.waitForTransactionReceipt(rh)
    s1 = f"status: {tx_receipt['status']}"
    s2 = f"blockNumber: {tx_receipt['blockNumber']}"
    s3 = f"gasUsed: {tx_receipt['gasUsed']}"

    logger.debug(f"{s1}")
    logger.debug(f"{s2}")
    logger.debug(f"{s3}")
    click.secho(s1, fg="green")
    click.secho(s2, fg="green")
    click.secho(s3, fg="green")

    # contractAddress
    # cumulativeGasUsed

# @ltools.command()
# @click.pass_context
# def send(ctx):
#     myaddr = ctx.obj['ledger_account'].address
#     check_critical()
#     # show_balance(myaddr)


@ltools.command()
@click.pass_context
def balanceusdt(ctx):
    myaddr = ctx.obj['ledger_account'].address
    show_balance(myaddr)


@ltools.command()
@click.pass_context
def balancebnb(ctx):
    ledger_account = ctx.obj['ledger_account']
    myaddr = ledger_account.address
    bnb_bal = ctx.obj['w3'].eth.getBalance(myaddr)

    click.secho(f"BNB {bnb_bal/10**18}", fg="green")

@ltools.command()
@click.pass_context
def listaccounts(ctx):
    logger.debug(f"list accounts")
    ledger_account = ctx.obj['ledger_account']
    for i in range(3):
        addr = ledger_account.get_address(i)
        click.secho(f"addr:  {addr}", fg="green")


@ltools.command()
@click.pass_context
def listall(ctx):
    logger.debug(f"listall")
    ledger_account = ctx.obj['ledger_account']
    for i in range(3):
        addr = ledger_account.get_address(i)
        s1 = f"addr:\t{addr}"
        logger.debug(s1)
        click.secho(s1, fg="green")
        bnb_bal = ctx.obj['w3'].eth.getBalance(addr)
        s2 = f"BNB {bnb_bal/10**18}"
        click.secho(s2, fg="green")
        logger.debug(s2)
        show_balance(ctx.obj['w3'], addr)
        click.secho(f"---------", fg="white")


def send_tx(ledger_account, w3, sendamount, to_address):
    logger.debug(f"send_tx {sendamount} {to_address}")

    myaddr = ledger_account.address
    nonce = w3.eth.getTransactionCount(myaddr)

    txd = {
        "chainId": 56,
        "to": to_address,
        "value": sendamount,
        "gas": 21000,
        "gasPrice": 5000 * 10 ** 6,
        "nonce": nonce,
    }

    signedtx = ledger_account.signTransaction(txd)
    print(signedtx)
    pushtx(w3, signedtx)


@ltools.command()
@click.pass_context
@click.option('--amount', help='amount', type=int)
@click.option('--to', help='address')
def sendbnb(ctx, amount, to):
    logger.debug(f"sendbnb {amount} {to}")
    ledger_account = ctx.obj['ledger_account']
    print("send ", amount)
    print("to ", to)
    #TODO check high amounts
    w3 = ctx.obj['w3']
    #TODO whitelist addresses
    if to in whitelist.keys():
        addr = whitelist[to]
        send_tx(ledger_account, w3, amount, addr)
    else:
        print("address not whitelisted")



@ltools.command()
@click.option('--name', help='full name')
@click.pass_context
def version(ctx, name):
    logger.debug("version")
    click.secho(f"{ctx.obj['ledger_account'].get_version()}", fg="green")



if __name__ == '__main__':
    ltools(obj={})